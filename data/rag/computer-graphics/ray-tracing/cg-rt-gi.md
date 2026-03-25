---
id: "cg-rt-gi"
concept: "光追全局光照"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 4
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.4
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


# 光追全局光照

## 概述

光追全局光照（Ray-Traced Global Illumination，RTGI）是指利用光线追踪技术模拟光线在场景中多次弹射、散射和折射的物理过程，从而在实时渲染管线中实现间接光照效果的技术方案。与传统的预烘焙光照贴图不同，RTGI能够响应场景中动态物体和动态光源的变化，在运行时重新计算间接照明结果。

该技术方向随着2018年NVIDIA发布Turing架构（RTX 20系列）和DirectX Raytracing（DXR）API而进入实时可行阶段。在此之前，全局光照几乎完全依赖静态烘焙（Lightmap）或屏幕空间近似（SSAO、SSGI），二者均无法处理完全动态的光照场景。Turing架构引入的专用RT Core硬件单元将BVH遍历加速约10倍，使得每帧发射数百万条光线成为可能。

RTGI的工程意义在于它打破了"动态场景不能有高质量间接照明"的长期限制。在影视级实时渲染、开放世界游戏和建筑可视化中，间接光照往往贡献了整体亮度的50%至80%，光追全局光照因此成为这些场景不可替代的技术手段。

---

## 核心原理

### 动态漫反射全局光照（DDGI）

DDGI（Dynamic Diffuse Global Illumination）由NVIDIA于2019年在论文《Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Probes》中提出，是目前工业界应用最广泛的实时RTGI方案之一。其核心思想是在场景中均匀或非均匀地放置**辐照度探针（Irradiance Probe）**网格，每帧对每个探针发射少量光线（通常为64至256条），将命中点的辐射值存储为球谐（Spherical Harmonics）系数或小分辨率的等距柱状投影（Octahedral Projection）纹理。

着色时，片元根据周围8个相邻探针的辐照度数据进行三线性插值，叠加可见性权重（Visibility Weight）以减少漏光伪影。每个探针维护两张纹理：一张8×8像素的辐照度图和一张16×16像素的距离矩（Mean Distance）图，后者用于实现切比雪夫可见性测试。整个方案将每帧的光线数量控制在可接受范围内，同时通过时序积累（Temporal Accumulation）平滑噪声。

### RTXGI SDK 与探针更新策略

NVIDIA官方发布的RTXGI SDK（基于DDGI思想）将探针组织为可配置的三维网格（Volume），支持在编辑器中动态调整探针密度和覆盖范围。SDK内置**探针分类（Probe Classification）**机制，将探针标记为Active、Inactive或Newly Active状态，避免对被几何体完全遮挡或位于墙体内部的探针进行无效光线投射，从而节省约20%-40%的GPU光线时间。

探针更新并非每帧全量刷新，而是采用**滚动更新（Rolling Update）**策略：每帧仅更新总探针数量的1/N（N通常为2到4），结合较大的时间混合系数（Hysteresis，默认0.97）保证视觉稳定性。这意味着完整的间接光照信息约需2至4帧才能完全收敛，因此RTXGI不适合极端快速变化的光源场景（如高频闪烁）。

### 与路径追踪的关系和区别

路径追踪通过蒙特卡洛积分无偏地估计渲染方程，每像素需要数百至数千条光线才能收敛。RTGI方案通过引入探针缓存层将问题从像素域转移到世界空间稀疏采样域，本质上是对路径追踪的**有偏近似（Biased Approximation）**：以牺牲低频细节的准确性换取每帧光线数量从数百万条/像素降低至固定数量（通常全局总计1M至8M条）。因此DDGI无法重现焦散（Caustics）等高频光传输现象，这是其结构性局限。

---

## 实际应用

**《堡垒之夜》（Fortnite）Chapter 4**是最早在商业AAA游戏中大规模启用RTXGI的案例。Epic Games在UE5的Lumen系统之外，为RTX显卡用户提供了基于DDGI的硬件光追路径，使室内区域的间接光照质量显著提升，尤其在有色光源附近的颜色渗透效果更接近物理真实。

**建筑可视化工具Enscape 3.x**集成了基于DXR的实时RTGI，允许设计师在修改材质或调整窗户尺寸后实时观察自然光在室内的漫射分布，将传统Lightmap烘焙从数小时缩短至秒级反馈。Enscape的实现针对建筑场景的特点，将探针密度集中于室内区域，室外区域退化为更稀疏的天光采样。

**NVIDIA Omniverse**平台使用RTXGI作为实时视口的GI方案，在数字孪生和工业仿真场景中，探针网格能够随机器人或车辆的运动实时更新遮挡关系，这是Lightmap方案完全无法覆盖的使用场景。

---

## 常见误区

**误区一：RTGI等同于完整的路径追踪**。DDGI等方案只计算漫反射间接光（Diffuse Indirect），通常仅追踪1至2次弹射。镜面反射间接光（Specular Indirect）需要单独的光线反射（Ray-Traced Reflections）模块处理，焦散则几乎所有实时RTGI方案都无法正确表现。将RTGI的视觉结果与离线渲染的路径追踪参考图对比，往往在光泽表面和阴影接触处仍存在明显差距。

**误区二：探针数量越多越好**。增加探针密度会线性增加光线投射数量，但间接照明信号本身是低频的，过密的探针网格并不能获得更多高频细节，反而导致帧预算超支。DDGI论文建议在室内场景中每1至2米放置一个探针，室外开放场景可降至每4至8米，比例失当反而引入更多插值伪影（Probe Bleeding）。

**误区三：RTXGI可以替代全部烘焙流程**。对于不支持RTX的硬件（DXR要求Shader Model 6.5及以上，实际上RTX 20系列以下基本不可用），仍需Lightmap作为回退方案。同时，RTXGI的时序积累会在相机快速移动时产生拖影，烘焙方案在静态场景下反而具有零运行时开销的优势。

---

## 知识关联

**前置知识——路径追踪**：DDGI探针更新本质是在探针视点执行单次弹射的路径追踪，理解蒙特卡洛积分和重要性采样有助于明白为何需要64条以上光线才能获得稳定的辐照度估计，以及为何时序混合系数0.97意味着理论上需要约33帧才能使旧信息权重降至50%以下（由 $0.97^{33} \approx 0.37$ 得出）。

**横向关联——屏幕空间全局光照（SSGI）**：SSGI依赖GBuffer中已有的屏幕空间深度和法线信息，计算开销极低（无需光线投射硬件），但受限于屏幕可见范围，屏幕边缘和背对相机的表面无法获得正确间接光。RTGI通过世界空间探针解决了这一本质缺陷，代价是更高的GPU内存占用（每个探针体积通常需要2MB至20MB的纹理图集）。

**延伸方向——硬件加速演进**：Ada Lovelace架构（RTX 40系列）的RT Core第三代吞吐量相比Turing提升约2倍，使DDGI可以在4K分辨率下维持60帧的光线预算。未来随着Shader Execution Reordering（SER）技术普及，非相干光线的GPU利用率有望进一步提升20%-30%，为更高探针密度或更多弹射次数提供硬件基础。