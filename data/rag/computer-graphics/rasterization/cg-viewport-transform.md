---
id: "cg-viewport-transform"
concept: "视口变换"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 视口变换

## 概述

视口变换（Viewport Transform）是光栅化管线中将标准化设备坐标（NDC，Normalized Device Coordinates）映射到屏幕像素坐标的几何变换步骤。经过投影变换和透视除法后，场景中所有可见顶点的坐标均已被压缩至 NDC 空间的 $[-1, 1]^3$ 立方体内，而视口变换负责将这个抽象的单位立方体"拉伸"对齐到具体的帧缓冲区矩形区域。

视口变换的概念随着固定管线图形 API 的成熟而被明确规范化。OpenGL 1.0（1992年发布）中就已引入 `glViewport(x, y, width, height)` 函数，将 NDC 的 $[-1,1]$ 范围映射到用户指定的像素窗口区域。Direct3D 则定义了独立的 `D3D11_VIEWPORT` 结构体，并额外暴露 `MinDepth` 与 `MaxDepth` 两个深度范围参数，允许对深度值进行独立缩放。

视口变换在管线中处于顶点处理阶段的最末端，其输出直接决定了光栅化器扫描三角形时所使用的窗口坐标。若视口设置错误，整个场景会出现错位、拉伸或被裁剪到错误区域，因此正确理解视口变换的公式与约定对调试渲染错误至关重要。

---

## 核心原理

### NDC 到屏幕坐标的映射公式

视口变换本质上是一次线性映射，其 $x$ 和 $y$ 分量的计算公式如下：

$$
x_{screen} = \frac{width}{2} \cdot x_{ndc} + \left(x_0 + \frac{width}{2}\right)
$$

$$
y_{screen} = \frac{height}{2} \cdot y_{ndc} + \left(y_0 + \frac{height}{2}\right)
$$

其中 $(x_0, y_0)$ 是视口左下角的像素坐标，$width$ 和 $height$ 是视口的像素宽度和高度。公式将 NDC 的 $x \in [-1, 1]$ 线性映射到 $[x_0, x_0 + width]$，将 $y \in [-1, 1]$ 映射到 $[y_0, y_0 + height]$。注意 OpenGL 的 NDC 坐标系 $y$ 轴朝上，所以 $y_{ndc} = 1$ 对应屏幕顶部；而 Direct3D 的 NDC $y$ 轴同样朝上，但其屏幕坐标 $y$ 轴朝下，因此 Direct3D 的视口变换会引入一次 $y$ 轴翻转。

### 深度值的线性映射

视口变换还负责处理深度分量 $z$。OpenGL 通过 `glDepthRange(near, far)` 控制此映射，默认值为 $near=0$，$far=1$，公式为：

$$
z_{window} = \frac{far - near}{2} \cdot z_{ndc} + \frac{far + near}{2}
$$

当 $z_{ndc} \in [-1, 1]$ 时，$z_{window} \in [0, 1]$，即深度缓冲区中存储的归一化深度值。Direct3D 的 NDC 深度范围为 $[0, 1]$，因此其深度映射公式为 $z_{window} = (MaxDepth - MinDepth) \cdot z_{ndc} + MinDepth$，默认情况下恒等映射。两套 API 的深度约定差异是跨平台渲染中常见的错误来源。

### 像素中心约定

视口变换完成后，光栅化器需要判断三角形是否覆盖某个像素，而这依赖于**像素中心**的位置约定。OpenGL 规定像素中心位于半整数坐标，即第 $i$ 列第 $j$ 行的像素中心在 $(i + 0.5, j + 0.5)$。Direct3D 9 曾使用整数坐标作为像素中心（即中心在 $(i, j)$），这导致在 DirectX 9 应用中做全屏后处理时需要手动偏移 $0.5$ 个像素来对齐纹理采样与像素坐标。从 Direct3D 10 起，微软将像素中心统一改为半整数约定，与 OpenGL 保持一致，消除了这一历史包袱。

---

## 实际应用

**分屏渲染（Split-screen Rendering）**：多人游戏中，开发者调用两次 `glViewport`，分别将左半屏（`glViewport(0, 0, 960, 1080)`）和右半屏（`glViewport(960, 0, 960, 1080)`）设为视口，同一套 NDC 场景几何体就能分别投射到两个不同的屏幕区域，无需重复提交几何数据。

**UI 叠加层（HUD Rendering）**：游戏 HUD 通常使用全屏视口（`glViewport(0, 0, 1920, 1080)`），但将 NDC 坐标直接对应像素位置。此时开发者构造一个正交投影矩阵，使得 NDC 的 $[-1,1]^2$ 精确对应屏幕像素范围 $[0, 1920] \times [0, 1080]$，实现像素级精确的文字和图标渲染。

**Vulkan 中的翻转视口技巧**：Vulkan 的 NDC $y$ 轴朝下，但其裁剪坐标约定与 OpenGL 相反，导致渲染结果上下翻转。Vulkan 1.1 扩展 `VK_KHR_maintenance1` 允许在 `VkViewport` 中将 `height` 设为负值（如 `height = -1080`），等效于对视口变换引入 $y$ 轴翻转，从而无需修改着色器即可兼容 OpenGL 风格的坐标系。

---

## 常见误区

**误区一：视口变换改变了裁剪行为**。实际上裁剪（Clipping）发生在投影变换之后、透视除法之前的齐次裁剪空间（Clip Space）中，视口变换在裁剪之后执行，对已经位于 NDC 内的顶点进行纯线性重映射，不会剔除或修剪任何几何体。将场景渲染到一个小视口并非"裁剪"了场景，而是缩放了场景在帧缓冲中的占据区域。

**误区二：视口尺寸决定渲染分辨率**。视口变换的 $width \times height$ 仅定义了 NDC 坐标映射到的帧缓冲子区域，帧缓冲本身的分辨率是独立配置的。将视口设为 `glViewport(0, 0, 1920, 1080)` 但帧缓冲只有 $800 \times 600$，结果是视口超出帧缓冲边界，光栅化器会按帧缓冲边界隐式截断输出，不会自动升级帧缓冲分辨率。

**误区三：Direct3D 9 与 OpenGL 的坐标系完全对称**。许多开发者以为只需翻转 $y$ 轴即可兼容两套 API，但忽略了像素中心约定的差异——Direct3D 9 的整数像素中心导致纹理坐标与顶点坐标之间存在 $0.5$ 像素偏移，这在全分辨率渲染时几乎不可见，但在低分辨率或放大渲染时会造成明显的模糊或锯齿。

---

## 知识关联

视口变换的输入依赖**投影变换**的正确性：若投影矩阵的 NDC 深度范围约定（OpenGL 的 $[-1,1]$ 对比 Direct3D 的 $[0,1]$）与视口深度映射不匹配，深度缓冲将产生系统性错误，导致近处物体被错误遮挡。理解投影变换输出的 NDC 空间语义是正确配置视口变换的前提。

视口变换完成后，管线进入**三角形装配（Triangle Assembly）**阶段，光栅化器以视口变换输出的窗口坐标为基准，对三角形的三条边进行扫描线分析，判断哪些像素采样点落入三角形内部。此时的像素中心约定（半整数坐标）直接影响光栅化规则（如 OpenGL 的左上填充规则 top-left rule），理解视口变换中的坐标体系是正确实现三角形覆盖测试的基础。