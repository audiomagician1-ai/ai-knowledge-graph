---
id: "ta-translucent-material"
concept: "半透明材质"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 半透明材质

## 概述

半透明材质（Translucent/Transparent Material）是指允许光线部分或全部穿透物体表面的材质类型，用于表现玻璃、水面、薄纱、烟雾、火焰等自然现象。与不透明材质不同，半透明材质的渲染管线需要知道当前像素"背后"是什么内容，因此无法像不透明物体那样依赖深度缓冲（Depth Buffer）进行早期剔除，这从根本上改变了渲染流程的组织方式。

半透明渲染的复杂性源于其对"顺序依赖"的物理本质。当光线依次穿过两层半透明物体时，先穿 A 再穿 B 与先穿 B 再穿 A，最终混合到屏幕上的颜色结果不同，这被称为**混合的非交换性**。这与加法混合（Additive Blend）形成对比——火焰和粒子特效常用加法混合，因为它天然满足交换律，无需排序。

在游戏引擎工业实践中，半透明材质是美术与程序之间冲突最高发的技术点之一。一个场景中半透明对象数量超过数十个时，DrawCall 的排序开销和透明度排序错误（Z-Fighting on Transparency）就会显著影响运行时性能与画面质量，因此理解其底层机制对技术美术师至关重要。

---

## 核心原理

### 1. Alpha 混合公式与混合模式

标准 Alpha 混合（Alpha Blending）遵循如下公式：

$$C_{out} = \alpha_s \cdot C_{src} + (1 - \alpha_s) \cdot C_{dst}$$

其中：
- $C_{src}$：当前半透明片元的颜色（Source Color）
- $C_{dst}$：帧缓冲中已有的颜色（Destination Color，即背景）
- $\alpha_s$：当前片元的透明度（0 = 完全透明，1 = 完全不透明）
- $C_{out}$：最终写入帧缓冲的颜色

除标准 Alpha 混合外，常见混合模式还包括：
- **Additive（加法）**：$C_{out} = C_{src} + C_{dst}$，常用于火焰、光效，亮度只增不减
- **Premultiplied Alpha（预乘 Alpha）**：$C_{out} = C_{src} + (1-\alpha_s) \cdot C_{dst}$，要求颜色通道在存储时已乘以 Alpha，能避免黑边伪影（Dark Fringe Artifact）
- **Multiply（正片叠底）**：$C_{out} = C_{src} \cdot C_{dst}$，常用于玻璃染色效果

### 2. 透明排序问题（Transparency Sorting）

由于 GPU 的深度测试在写入深度缓冲时会丢弃被遮挡的半透明片元，渲染引擎通常在渲染半透明物体时**关闭深度写入（Depth Write = false），但保留深度测试（Depth Test = true）**。这意味着半透明对象必须按照**从后到前（Back-to-Front）**的顺序手动排序，才能保证混合结果正确，这一算法被称为 **Painter's Algorithm（画家算法）**。

画家算法在 CPU 端对半透明对象按摄像机距离降序排列。然而当两个半透明网格相互穿插时（例如两块相交的玻璃），无法找到全局正确的排序顺序，这是该算法的根本局限。解决方法包括：
- **Order-Independent Transparency（OIT，顺序无关透明）**：在 GPU 上存储每个像素的多层片元并在片段着色器末尾排序，代表实现有 Intel 的 A-Buffer 和 Weighted Blended OIT（WBOIT，2013年由 Morgan McGuire 提出）
- **逐网格拆分**：将相交网格切割为不相交部分，强制可排序

### 3. 光照与阴影的特殊处理

半透明材质接收光照时，需要区分两种物理现象：

- **透射（Transmission）**：光线穿过材质继续传播，折射率（IOR，Index of Refraction）决定偏转角度。玻璃的 IOR 约为 1.5，水为 1.33，钻石为 2.42。在实时渲染中，折射常通过采样一张已完成渲染的场景颜色贴图（Scene Color Texture / Grab Pass）并施加法线扰动来模拟。
- **次表面散射（Subsurface Scattering，SSS）**：光线进入材质后在内部散射再射出，用于皮肤、玉石、蜡等**半透明（Translucent）**而非透明材质。这与玻璃的纯透射在着色器实现上完全不同。

半透明对象通常**无法正确接收和投射阴影**，因为阴影贴图（Shadow Map）在生成时只记录最近表面的深度。Unreal Engine 对半透明材质提供了基于 Volumetric Shadow Map 的近似方案，但代价是一倍以上的阴影计算开销。

---

## 实际应用

**窗玻璃与瓶子**：使用标准 Alpha Blend 模式，Alpha 值设为 0.05～0.2，同时在着色器中叠加 Fresnel 反射项（边缘反射更强）。折射偏移量通过采样 SceneColor 并加上法线贴图驱动的 UV 偏移实现，偏移强度通常控制在 0.02～0.05 范围内以避免失真过大。

**薄纱布料**：通常不使用完整 Alpha Blend，而是改用 **Dithered Transparency（抖动透明）**——在不透明渲染通道中，通过屏幕空间 4×4 Bayer 矩阵对像素做阈值丢弃，使其在不关闭深度写入的情况下产生半透明视觉效果，完全规避排序问题，TAA 开启后效果更平滑。

**粒子与烟雾**：粒子系统大量使用 Additive 或 Premultiplied Alpha 混合模式。单个粒子系统内部可设置粒子按深度排序（Sort Mode = By Distance），但跨粒子系统间的排序需由引擎层统一处理。Niagara（UE5）和 VFX Graph（Unity）均提供了每系统级别的透明排序优先级参数。

---

## 常见误区

**误区一：Alpha = 0 的像素不需要渲染**
很多初学者认为将 Alpha 设为 0 就等同于该区域不存在。但在 Alpha Blend 模式下，即使 Alpha=0 的片元仍会参与深度测试，遮挡其后方的不透明物体写深度，导致出现"隐形墙"效果。正确做法是结合 `clip()` / `discard` 指令在着色器中丢弃低于阈值的片元，或改用 Alpha Test（Cutout）模式。

**误区二：半透明材质可以接收实时阴影且效果准确**
半透明材质在标准延迟渲染（Deferred Rendering）管线中完全无法参与 GBuffer 写入，因此不支持延迟阴影。在 Unreal Engine 中，将材质混合模式设为 Translucent 后，若不手动开启 `Cast Volumetric Translucent Shadow`，该材质不会向场景投射任何阴影，这是美术资产审查中的高频 Bug。

**误区三：透明度排序问题可以靠调整材质参数解决**
当两块相互穿插的半透明网格出现闪烁时，美术师常尝试调整 Opacity 值或混合模式，但这无法解决根本问题。闪烁的本质是帧与帧之间摄像机距离变化导致排序结果翻转，唯一正确解法是拆分网格或启用 OIT 方案。

---

## 知识关联

**前置概念**：PBR 材质基础中的金属度/粗糙度工作流为半透明材质的镜面反射计算提供参数基础；Fresnel 方程（$F_0 + (1-F_0)(1-\cos\theta)^5$）在玻璃边缘反射增强效果中直接复用。深度缓冲与深度测试的工作原理是理解透明排序问题的前提。

**横向关联**：半透明材质与粒子系统紧密耦合，粒子的混合模式选择直接决定特效的视觉风格；与后处理中的景深（DOF）效果也存在交互——半透明物体在 CoC（Circle of Confusion）计算中需特殊处理，否则会出现轮廓漏光。Weighted Blended OIT 作为当前主流的工程化 OIT 方案，其权重函数 $w(z, \alpha) = \alpha \cdot \max(0.01, \min(3000, 10/(10^{-5} + (z/5)^2 + (z/200)^6)))$ 在移动端和 PC 端高质量透明渲染项目中均有实装案例。