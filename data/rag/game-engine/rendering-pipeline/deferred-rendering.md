---
id: "deferred-rendering"
concept: "延迟渲染"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 2
is_milestone: false
tags: ["路径"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.367
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 延迟渲染

## 概述

延迟渲染（Deferred Rendering）是一种将几何体处理与光照计算分离为两个独立渲染阶段的技术。与传统前向渲染（Forward Rendering）不同，延迟渲染先将场景的几何信息（位置、法线、材质属性等）写入一组称为 G-Buffer（Geometry Buffer）的纹理缓冲区，再在后续阶段统一进行光照计算，从而避免对同一像素进行多次冗余的着色运算。

该技术由 Saito 和 Takahashi 于 1990 年在论文《Comprehensible Rendering of 3-D Shapes》中正式提出，但受制于当时 GPU 的多渲染目标（MRT，Multiple Render Targets）支持有限，直到 2004 年前后随着可编程着色器的普及才被游戏行业广泛采用。Killzone 2（2009年，Guerrilla Games）是最早将延迟渲染技术大规模应用于商业游戏的代表作之一，其场景中同时存在数十盏动态光源的效果震惊了业界。

延迟渲染的核心价值在于光照计算的复杂度从 O(几何体数量 × 光源数量) 降低为 O(屏幕像素数 × 光源数量)。当场景中存在大量动态光源（如数十至数百盏点光）时，这一差异极为显著，使得现代开放世界游戏的动态光照成为可能。

---

## 核心原理

### G-Buffer 的结构与内容

G-Buffer 并非单一纹理，而是由多张全屏纹理共同构成的缓冲区组合。一个典型的 G-Buffer 布局包含以下纹理槽：

- **RT0（RGBA8）**：漫反射颜色（Albedo），RGB三通道存储基础颜色，A通道可存储镜面反射强度
- **RT1（RGBA16F）**：世界空间法线（Normal），需要编码压缩以节省带宽，常用球面映射或八面体映射
- **RT2（RGBA8）**：材质属性，如粗糙度（Roughness）、金属度（Metallic）、环境光遮蔽（AO）
- **深度缓冲（Depth/Stencil）**：存储每像素深度值，用于重建世界空间位置

第一阶段（Geometry Pass）将所有不透明几何体渲染一遍，每个片元着色器仅负责将数据写入对应 G-Buffer 通道，不计算任何光照。第二阶段（Lighting Pass）遍历所有光源，以全屏四边形或光源体积（Light Volume）为单位，读取 G-Buffer 数据执行真正的着色运算。

### 从深度重建世界坐标

延迟渲染不直接存储世界空间位置（否则需要一张 RGBA16F 纹理，代价高昂），而是通过深度缓冲重建。重建公式为：

```
P_world = InvViewProj × vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0)
P_world /= P_world.w
```

其中 `uv` 为当前像素的屏幕UV坐标（0~1），`depth` 为深度缓冲中读取的值，`InvViewProj` 为投影矩阵与视图矩阵之积的逆矩阵。该逆矩阵每帧仅需计算一次并以 Uniform 形式传入着色器。

### 光源体积与光照剔除

在 Lighting Pass 中，点光源不使用全屏四边形，而是渲染一个包围该光源影响范围的球体网格（Light Volume Sphere）。球的半径 r 由光源衰减公式确定：当光照强度衰减至某个阈值（通常为 1/256）时的距离即为半径，例如对于强度 I、阈值 t，半径 `r = sqrt(I / t)`。GPU 只对球体覆盖的像素执行光照着色，实现了粗粒度的光源剔除，将大量像素排除在无关光源的计算之外。

---

## 实际应用

**《赛博朋克 2077》的霓虹灯场景**：夜城街道中同时存在数百盏各色霓虹灯，若使用前向渲染，每个不透明像素可能需要执行数百次光照计算。延迟渲染使每个像素只需读取一次 G-Buffer，再逐光源累加贡献，GPU 利用率大幅提升。

**Unity 的 URP 与 HDRP 对比**：Unity 的通用渲染管线（URP）默认使用前向渲染并加入了 Forward+（分块光源列表）优化，而高清渲染管线（HDRP）则强制使用延迟渲染，并将 G-Buffer 数量扩展至 4 张以支持次表面散射、各向异性高光等高级材质特性。

**Unreal Engine 的实现**：UE4/UE5 的默认渲染路径即为延迟渲染，其 G-Buffer 布局有 5 个渲染目标，其中 GBufferA 存储法线与感知线性粗糙度，GBufferB 存储金属度、高光度等 PBR 参数，GBufferC 存储基础颜色。UE 同时保留了一套 Forward Shading 选项，专门用于VR平台以避免 G-Buffer 的带宽开销。

---

## 常见误区

**误区一：延迟渲染对所有平台都更优**

延迟渲染的 G-Buffer 要求同时绑定多张全屏分辨率纹理，每帧在 Geometry Pass 结束后需要将这些纹理全部从显存写回，再在 Lighting Pass 中全部读取。在移动端 GPU（如 Adreno、Mali、PowerVR）上，这种"写入 → 从显存读回"的模式会导致严重的带宽压力，而移动端 GPU 普遍采用基于瓦片的延迟渲染架构（TBDR，Tile-Based Deferred Rendering），原生支持片上缓存，用传统延迟渲染反而浪费了 TBDR 的优势。因此 iOS 和 Android 游戏多使用 TBDR 兼容的变体，而非 PC 版延迟渲染的直接移植。

**误区二：延迟渲染原生支持半透明物体**

G-Buffer 只能存储每像素最前方的一个表面信息，半透明物体（如玻璃、粒子）无法正确写入 G-Buffer，因为它们需要同时保留背景的颜色信息进行混合。实际引擎中，半透明物体通常在延迟渲染完成后，单独使用前向渲染再绘制一遍，形成"延迟 + 前向混合"的双通道流程。这意味着延迟渲染管线本质上并不能完全取代前向渲染。

**误区三：G-Buffer 中直接存储世界空间法线精度足够**

将法线的 XYZ 分量直接存入 RGBA8 格式纹理时，每个分量只有 256 级精度，导致法线分布在球面上时出现明显的量化误差（法线块状分布），特别影响镜面高光的平滑度。工业实践中通常使用 RG16F 格式配合重建 Z 分量（`z = sqrt(1 - x² - y²)`），或采用八面体法线编码（Octahedron Normal Encoding）将 3D 法线压缩至两个通道同时保持均匀分布精度。

---

## 知识关联

学习延迟渲染需要先掌握渲染管线概述中的 G-Buffer 写入流程、MRT 绑定机制以及深度缓冲的工作原理，缺乏这些基础会导致无法理解 Geometry Pass 与 Lighting Pass 的职责划分。

延迟渲染为后续多个渲染技术提供了 G-Buffer 这一基础资源。**阴影映射**（Shadow Mapping）在 Lighting Pass 阶段需要从 G-Buffer 读取像素的世界坐标以判断其是否位于阴影中，延迟架构使得阴影查询可以集中在一个着色阶段完成。**全局光照**（Global Illumination）技术如屏幕空间环境光遮蔽（SSAO）直接依赖 G-Buffer 中的法线和深度信息重建三维结构。**后处理效果**（Post-Processing）同样以 G-Buffer 的深度与法线数据为输入，例如景深（DoF）需要深度图、屏幕空间反射（SSR）需要法线图，延迟渲染天然提供了这些数据，无需额外的渲染遍次。
