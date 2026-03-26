---
id: "vfx-fluid-texture"
concept: "流体纹理"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.9
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

# 流体纹理

## 概述

流体纹理是指通过预烘焙或程序化纹理贴图来模拟流体运动视觉效果的一类技术，主要包括 Flowmap（流向图）、法线扰动贴图（Normal Perturbation Map）以及噪声混合动画贴图等手段。这些技术的核心思路是将流体的速度场、方向场或表面细节编码进纹理的 RGB 或 RG 通道，在运行时以极低的计算开销驱动 UV 动画或表面法线偏移，从而在视觉上还原水流、熔岩、烟雾等流动现象。

Flowmap 技术由 Valve 工程师 Alex Vlachos 在 2010 年 GDC 演讲《Water Flow in Portal 2》中系统化提出并公开了完整实现方案，该演讲奠定了实时游戏中 Flowmap 的标准工作流程。在此之前，开发者通常只能用简单的 UV 滚动（UV Scrolling）来表现流水，无法呈现绕过石头、汇聚于低洼处等具有真实感的流向变化。Flowmap 技术使得《传送门 2》的水面表现效果在当时的实时渲染水准中显著超出同期同类游戏。

流体纹理技术之所以在特效领域受到广泛采用，是因为它将离线模拟的复杂流体计算结果"固化"成一张纹理，运行时仅需一次纹理采样和若干向量运算，GPU 消耗可以控制在每帧 0.1ms 以下，这对于需要大量粒子与流体并存的移动端游戏场景尤为关键。

---

## 核心原理

### Flowmap 的编码与解码

Flowmap 是一张将二维速度场存储在 RG 两个通道中的纹理。其中 R 通道表示 X 方向的流速分量，G 通道表示 Y 方向的流速分量，数值范围为 [0, 1]，经过 `velocity = sample * 2.0 - 1.0` 的重映射后转换为 [-1, 1] 区间的有向速度向量。以 Unreal Engine 的 Flowmap 材质节点为例，最终 UV 偏移量的计算公式为：

```
UV_offset = FlowDir * Time * FlowSpeed
UV_A = UV + UV_offset * Phase_A
UV_B = UV + UV_offset * Phase_B
Result = lerp(TextureSample(UV_A), TextureSample(UV_B), BlendWeight)
```

其中 Phase_A 和 Phase_B 使用 `frac(Time + 0.0)` 与 `frac(Time + 0.5)` 实现两组相位差为 0.5 的 UV 动画，通过三角函数权重混合消除每半周期在相位归零时产生的"闪烁"跳变（Ghosting Artifact）。

### 法线扰动的频率叠加策略

单一法线贴图的流体表面在近景观察时会因纹理分辨率不足而显得模糊平坦。法线扰动技术通常采用两层甚至三层不同平铺频率和滚动速度的法线贴图叠加：第一层大尺度贴图（Tiling = 1×）负责整体波形结构，第二层小尺度贴图（Tiling = 4×~8×）提供水面高频细节涟漪，两层贴图分别以不同方向（例如夹角 30°~45°）滚动，通过法线混合公式 `BlendedNormal = normalize(N1 + N2)` 或 Unreal 的 "Whiteout" 混合方法合并，有效打破重复感并产生自然的互相干涉图案。

### 噪声纹理驱动的流体扭曲

在不需要精确流向控制的场景（如熔岩池、魔法光效）中，可以用 Simplex Noise 或 Perlin Noise 噪声纹理代替手绘 Flowmap 来驱动 UV 扭曲。Unity Shader Graph 中的 Simple Noise 节点生成的灰度值经过 `dir = noise * 2.0 - 1.0` 转换为扰动向量，再以扰动强度系数（通常 0.05~0.2 的 UV 单位）叠加到原始 UV 上进行纹理采样，可以在几乎零额外资产的情况下模拟低精度流体扭曲效果，但代价是流向不可精确控制。

---

## 实际应用

**河流与溪流场景**：在《塞尔达传说：旷野之息》的河流系统中，设计团队使用手绘 Flowmap 配合法线扰动来表现水流绕过岩石后形成的涡流与汇聚区，美术人员在 Photoshop 或 Houdini 中绘制流向场后导出为 16 位精度的 EXR 格式以保留方向精度。

**熔岩材质**：熔岩表面通常使用一张 Flowmap 驱动红橙色 Albedo 贴图 UV 缓慢蠕动（FlowSpeed ≈ 0.03~0.08），同时用另一张高频噪声纹理扰动法线贴图，配合自发光 Emissive 通道的亮度随流速变化的调制，实现熔岩在裂缝处温度更高、发光更亮的视觉层次。

**UI 特效中的流体纹理**：在移动游戏 UI 的技能冷却波纹或水晶球效果中，Flowmap 同样适用。将一张低分辨率（64×64 或 128×128）的圆形旋转流向 Flowmap 应用于 UI 材质，可以用不到 0.5KB 的纹理资产实现连续旋转流动效果，比使用帧序列动画节省 95% 以上的纹理内存。

---

## 常见误区

**误区一：Flowmap 流速越快越真实**
将 FlowSpeed 参数调高至 0.5 以上后，UV 采样区域会在半周期内偏移过大，导致纹理细节被拉伸模糊，同时两组相位动画之间的混合过渡变得剧烈，反而产生明显的闪烁感。实际工程中 FlowSpeed 通常控制在 0.05~0.2 之间，通过 Flowmap 本身的向量方向变化来传递流速差异感，而非单纯提高全局速度。

**误区二：法线扰动可以完全替代几何波形**
法线贴图扰动只改变光照计算中的表面朝向，不会改变实际几何形状。当视角接近水面掠射角（Grazing Angle）时，由于屏幕空间反射（SSR）或环境反射是基于真实几何位置采样的，法线扰动无法影响反射采样的实际坐标，会出现反射图像与法线扰动的涟漪错位的穿帮现象。此时需要配合顶点动画（Vertex Animation Shader）或曲面细分（Tessellation）提供低频几何波动。

**误区三：Flowmap 必须手绘才能达到高质量**
Houdini 的 Labs Flowmap 工具集（自 Houdini 17.5 起内置）可以根据几何体的坡度、障碍物分布和重力方向自动生成物理上合理的流向场，其输出结果在弯道处的加速效果和障碍物背后的尾流漩涡上往往比手绘更准确。手绘 Flowmap 更适合用于艺术化夸张的场景，如需精确物理流向应优先考虑工具自动化生成。

---

## 知识关联

流体纹理建立在**实时流体策略**中对"以纹理代替模拟"这一决策的基础上——正是因为实时流体策略明确了何时适合采用近似方案，才有了 Flowmap 等技术的应用场景定位。掌握 Flowmap 的 UV 相位混合原理需要理解 UV 坐标空间和基础 Shader 数学（向量重映射、frac 函数、lerp 插值）。

进入**流体交互**阶段后，静态预烘焙的 Flowmap 将不再满足需求：当玩家角色涉水或物体落入水面时，需要在运行时动态修改速度场纹理，即通过 Render Texture 将交互信号写入 Flowmap，使流体纹理从静态资产变为动态生成的驱动数据。这一升级要求掌握 GPU 端的 RenderTexture 写入、深度图差值碰撞检测以及波形传播的迭代 Shader 计算，是流体纹理技术向真正动态模拟演进的关键跨越。