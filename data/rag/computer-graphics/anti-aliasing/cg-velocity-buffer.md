---
id: "cg-velocity-buffer"
concept: "速度缓冲"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 2
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
  - type: "academic"
    author: "Yang, L., Nehab, D., Sander, P. V., Sitthi-amorn, P., Lawrence, J., & Seitz, S. M."
    year: 2009
    title: "Amortized Supersampling"
    venue: "ACM Transactions on Graphics (SIGGRAPH Asia 2009), 28(5)"
  - type: "technical"
    author: "Karis, B."
    year: 2014
    title: "High Quality Temporal Supersampling"
    venue: "SIGGRAPH 2014 Advances in Real-Time Rendering Course, Epic Games"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 速度缓冲

## 概述

速度缓冲（Velocity Buffer，也称 Motion Vector Buffer）是一种全屏幕纹理，存储场景中每个像素在屏幕空间的二维运动向量，单位通常为像素/帧或归一化屏幕坐标的位移量。它记录的是从上一帧到当前帧，某个表面点在屏幕上的位置偏移 $(\Delta u, \Delta v)$，而非三维世界中的速度。

该技术的广泛应用始于 2010 年代中期，随着 TAA（时序抗锯齿）成为主流而被纳入标准渲染管线。Karis（2014）在 SIGGRAPH 课程中系统阐述了 Velocity Buffer 作为 TAA 基础设施的核心地位，同年 Unreal Engine 4.4 将其作为 TAA 的标准组件正式引入并公开了实现细节。此后几乎所有主流实时渲染引擎都采用相同的 R16G16 半精度浮点格式存储运动向量，以平衡精度与带宽消耗。Unity HDRP 在 2018 年（Unity 2018.1）同样将 Velocity Buffer 纳入其延迟渲染管线的标准 G-Buffer 布局，并将其标记为 RT2 的第四个通道或独立渲染目标，取决于平台带宽预算。

速度缓冲的重要性在于它将"时间信息"以空间化的方式写入 G-Buffer，使得 TAA 的历史帧重投影和运动模糊（Motion Blur）的方向与长度计算都能从同一张纹理中读取数据，避免重复推导，降低 GPU 计算成本。Yang 等人（2009）在时序超采样的早期研究中已指出，逐像素运动向量是实现高质量时序累积的必要条件，这一结论为后续引擎实现提供了重要的理论依据。

---

## 核心数学原理

### Per-Pixel 速度的推导公式

速度向量通过比较当前帧与上一帧的裁剪空间坐标得出。对于静态几何体，只需考虑摄像机运动；对于蒙皮或刚体动画，还需将上一帧的骨骼变换矩阵传入顶点着色器。

具体公式为：

$$\mathbf{v} = \frac{\mathbf{p}_{\text{current}}.xy}{\mathbf{p}_{\text{current}}.w} - \frac{\mathbf{p}_{\text{prev}}.xy}{\mathbf{p}_{\text{prev}}.w}$$

其中 $\mathbf{p}_{\text{current}}$ 由当前帧的 MVP 矩阵变换顶点得到，$\mathbf{p}_{\text{prev}}$ 由上一帧的 MVP 矩阵（$M_{\text{prev}} \times VP_{\text{prev}}$）变换**同一顶点的世界空间位置**得到。结果从 NDC 的 $[-1, 1]$ 范围转换到 $[0, 1]$ 的 UV 空间后写入 Velocity Buffer：

$$\mathbf{v}_{\text{uv}} = \mathbf{v} \times 0.5$$

TAA 在历史帧重投影阶段利用该向量将采样坐标反推到上一帧位置：

$$\mathbf{uv}_{\text{history}} = \mathbf{uv}_{\text{current}} - \mathbf{v}_{\text{uv}}$$

运动模糊的采样步长则进一步由向量长度与曝光时间系数共同决定，步长为 $|\mathbf{v}_{\text{uv}}| \times k$，其中 $k = 0.5 \times t_{\text{shutter}} / t_{\text{frame}}$，通常在渲染设置中可按需配置。

### 精度分析

R16G16 半精度浮点格式每通道 16 位，可表示的最小 UV 偏移约为 $6 \times 10^{-5}$。以 1920×1080 分辨率为例，该精度对应约 $6 \times 10^{-5} \times 1920 \approx 0.115$ 像素，完全满足 TAA 和运动模糊的需求。相比之下，R32G32 全精度格式会使带宽从约 8 MB/帧（1080p，60fps）翻倍至 16 MB/帧，在移动平台上造成不可忽视的功耗与性能损耗，因此在 iOS/Android 的高质量渲染方案（如 ARM Mali GPU 优化指南）中明确不推荐使用全精度 Velocity Buffer。

---

## 静态像素的特殊处理

当场景中大多数像素属于静态物体且摄像机也静止时，运动向量全部为零向量。引擎通常在清除 Velocity Buffer 时写入一个"无效标记"（如 $(0.5, 0.5)$ 表示零偏移的 UV 编码），TAA 和运动模糊的采样着色器通过判断该标记跳过历史帧重投影，直接使用当前帧数据，节省带宽。

部分引擎（如 Unity HDRP 2020.2 及以后版本）采用 Stencil 标记静态物体像素，在 Velocity Pass 中仅绘制运动物体的覆盖区域，Velocity Buffer 的其余像素保持摄像机运动产生的统一背景向量，进一步减少不必要的绘制调用。实测数据显示，在静态场景占主体（约 80% 像素为静态）的城市场景中，该优化可将 Velocity Pass 的 GPU 耗时减少约 30%~40%。

---

## 实际应用场景

**蒙皮角色的运动向量**：角色骨骼动画在每帧顶点着色器中需要同时计算当前帧骨骼矩阵和上一帧骨骼矩阵对顶点的变换结果，分别用于输出当前裁剪坐标和历史裁剪坐标。例如，一个拥有 60 根骨骼的标准人形角色，顶点着色器需要额外传入 60 个 4×4 的上一帧骨骼变换矩阵（或以双四元数压缩传输），以完成逐顶点的历史坐标计算。UE5 的 Nanite 系统对此专门维护了一套"Previous Position Buffer"，以支持百万级几何体的逐像素速度写入，该方案在 2022 年 GDC 的 Nanite 技术分享中有详细说明。

**粒子系统**：粒子通常在 CPU 或 Compute Shader 上模拟，其上一帧世界坐标可存储在粒子属性中，顶点着色器读取该属性并完成历史裁剪坐标计算，写入 Velocity Buffer。例如，一个火焰粒子系统若以每帧平均 500 个活跃粒子、每粒子覆盖约 16×16 像素计算，在 1080p 下约有 4% 的屏幕像素受其影响；若粒子系统省略速度写入步骤，TAA 会在这些像素处产生明显的彩色重影，尤其在粒子运动速度超过 10 像素/帧时视觉效果极差。

**UI 与全屏效果**：HUD 元素不应写入 Velocity Buffer（或写入零向量），否则 TAA 会对 UI 边缘进行错误的历史混合，导致文字发虚。实现上通常将 UI 合成放置在 TAA 之后的独立 Pass 中，这也是 UE4/UE5 和 Unity HDRP 的默认渲染顺序约定。

**问题思考**：如果一个场景中存在一面完全透明的玻璃（Alpha = 0），但其背后有一个高速运动的物体，Velocity Buffer 应该记录玻璃表面的速度还是背后物体的速度？TAA 在此情形下会遇到什么挑战？

---

## 常见误区与澄清

**误区一：速度缓冲存储的是三维世界空间速度**。实际上 Velocity Buffer 存储的是二维屏幕空间偏移，单位是 UV 坐标差值，不含深度分量。同一个物体在屏幕边缘与屏幕中心产生的屏幕空间向量长度不同，即使其三维速度完全相同，这是透视投影的正常结果。例如，一辆以 10 m/s 匀速横穿屏幕的汽车，在距离摄像机 5 m 时屏幕空间速度约为 50 px/帧，而在距离 20 m 时仅约 12 px/帧（假设 90° FOV，1080p）。

**误区二：静态物体不需要写入 Velocity Buffer**。当摄像机发生平移或旋转时，静态物体同样有非零的屏幕空间运动向量，此时需要依据摄像机的当前帧与上一帧 ViewProjection 矩阵差异来计算背景运动向量，否则 TAA 会对静态背景产生严重的模糊或重影。通常的做法是全场景统一写入 Velocity Pass，或至少对静态物体写入摄像机运动产生的向量。

**误区三：Velocity Buffer 精度越高越好**。R16G16 半精度在绝大多数场景下已足够，使用 R32G32 全精度会使带宽翻倍，在移动平台上造成不可忽视的性能损耗，且对最终视觉质量的提升极为有限（肉眼难以区分）。

---

## 调试与可视化

在实际开发中，直接可视化 Velocity Buffer 是排查 TAA 重影问题的第一步。主流引擎均内置了 Motion Vector 覆盖层（Overlay）：

- **Unreal Engine 5**：在 Viewport 的 Buffer Visualization 菜单中选择 "Velocity"，运动向量的 X 分量映射到红色通道，Y 分量映射到绿色通道，静止像素呈现为纯黑色（零向量）。
- **Unity HDRP**：通过 Rendering Debugger（Window > Analysis > Rendering Debugger）选择 "Motion Vectors" 模式，可分别显示摄像机运动向量和物体运动向量的叠加结果。

例如，当调试一个蒙皮角色的 TAA 重影时，在 Motion Vector Overlay 下观察到角色区域呈现出与背景完全不同的颜色（非黑色），即可确认 Velocity Pass 已正确写入角色运动向量；若角色区域呈黑色或与背景颜色相同，则说明骨骼动画的上一帧矩阵未正确传递到顶点着色器，是导致重影的根本原因。

---

## 知识关联与学习路径

**前置概念 TAA** 是 Velocity Buffer 最主要的消费者。TAA 的核心算法——历史帧累积与重投影——必须依赖 Velocity Buffer 提供的逐像素运动信息才能正确处理动态物体，否则只能通过相机矩阵估算重投影，无法解决动画角色的重影问题。Karis（2014）的 SIGGRAPH 技术报告至今仍是理解 TAA 与 Velocity Buffer 协同工作机制的最重要参考文献之一。

Velocity Buffer 生成的 Velocity Pass 通常插入在 G-Buffer Pass 之后、光照计算之前，是延迟渲染管线中除深度缓冲和法线缓冲之外最早生成的全屏数据之一。理解 Velocity Buffer 的写入时机和格式