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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

光追全局光照（Ray-Traced Global Illumination，RTGI）是指利用硬件加速光线追踪单元，在实时渲染管线中计算间接光照贡献的技术方案。与离线渲染中的完整路径追踪不同，实时RTGI的核心挑战在于每帧仅能发射极少量光线（通常每像素1条甚至更少），因此必须结合降噪、时序复用和探针缓存等手段才能产生视觉上可接受的间接光照效果。

该领域的两个主流工业实现分别是NVIDIA的**RTXGI**（RTX Global Illumination SDK）和Lumen启发下的**DDGI**（Dynamic Diffuse Global Illumination，由Morgan McGuire等人于2019年在论文"Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"中正式提出）。RTXGI本质上是DDGI思想的工业级封装，通过在场景中部署辐照度探针网格（Irradiance Probe Grid）来缓存和传播间接漫反射光照。

RTGI在实时渲染中的意义在于打破了传统预烘焙光照贴图只能处理静态场景的限制——当场景中的光源位置、强度或遮挡关系发生改变时，RTGI可以在数帧到十余帧的时间窗口内完成全局光照的动态更新，使游戏引擎首次能够以接近实时的速度响应动态间接光照变化。

---

## 核心原理

### DDGI探针网格与辐照度缓存

DDGI在世界空间中均匀分布一组辐照度探针（Irradiance Probe），每个探针以八面体映射（Octahedral Mapping）格式存储两张纹理：
- **辐照度图（Irradiance Atlas）**：分辨率通常为6×6或8×8像素/探针，存储RGB辐照度；
- **深度/可见性图（Visibility Atlas）**：分辨率通常为14×14或16×16像素/探针，存储到场景表面的平均深度及深度方差，用于切比雪夫可见性测试（Chebyshev Visibility Test）以抑制漏光。

每帧，系统从每个探针向随机分布的方向发射若干条光线（典型值为**128或256条/探针/帧**）。这些光线命中场景后获取该点的直接光照和自发光，并以指数移动平均（EMA）方式融入探针的历史辐照度累积结果，混合系数通常设定为0.97（历史权重）对0.03（新帧权重），从而实现时序稳定的间接光照收敛。

### 探针着色与遮挡处理

在实际着色阶段，像素点从周围最近的8个探针（三线性插值的立方体顶点）采样辐照度。为了避免光线穿透薄墙或地板产生的漏光伪影（Light Leaking），DDGI为每个探针方向存储深度矩（Mean and Variance of Depth），并对每个采样探针施加切比雪夫权重：

$$w_{chebyshev} = \begin{cases} 1 & d \leq \mu \\ \frac{\sigma^2}{\sigma^2 + (d - \mu)^2} & d > \mu \end{cases}$$

其中 $d$ 为像素到探针的距离，$\mu$ 为探针该方向的平均深度，$\sigma^2$ 为深度方差。这一权重会大幅削减被遮挡探针的贡献，从而减轻漏光现象，但并不能完全消除，这是DDGI相对于屏幕空间方法的主要工程代价之一。

### 探针更新调度与滚动分帧

由于场景中可能存在数百至数千个探针，逐帧全量更新在性能上不可承受。RTXGI/DDGI采用**滚动更新（Rolling Update）**策略，每帧仅更新探针总量的一个子集。在UE5 Lumen的实现中，屏幕近端探针（Screen-Space Probes）密度更高且更新更频繁，而远端世界探针则更新间隔更长，形成多级更新频率的层级结构。RTXGI SDK默认将探针按Morton码排序后循环更新，确保空间上均匀的更新分布。

---

## 实际应用

**UE5 Lumen的硬件光追路径**：当启用Hardware Ray Tracing模式时，Lumen利用DXR（DirectX Raytracing）从屏幕空间探针向场景发射长距离光线，获取远场辐照度。近场使用SDF（有向距离场）光锥追踪，远场使用BVH硬件加速，两者在约200单位距离处融合，共同构成完整的间接漫反射和间接高光。

**《赛博朋克2077》RTXGI集成**：CD Projekt RED将NVIDIA RTXGI SDK集成进Red Engine，将场景分层为室内探针网格（分辨率约0.5m间距）和室外探针网格（约4m间距），从而在霓虹灯色彩反弹高度复杂的室内环境中实现稳定的彩色间接光。对比烘焙方案，RTXGI使动态关灯/开灯场景中间接光响应延迟从完全没有更新降低至约8帧（约133ms，60fps下）。

**ReSTIR GI的结合应用**：2021年NVIDIA提出的ReSTIR GI（Reservoir-based Spatiotemporal Importance Resampling for GI）可与DDGI结合使用：DDGI负责低频漫反射GI，而ReSTIR GI通过空间和时序重采样大幅提升每像素间接光照的采样效率，每像素仅需1条光线即可达到等效数十条光线的降噪质量，两者分工协作以覆盖不同频率的间接光照信号。

---

## 常见误区

**误区一：DDGI可以替代阴影贴图处理所有遮挡**。DDGI的切比雪夫可见性测试只能减轻漏光，无法精确处理直接光阴影。直接光照部分仍需独立的阴影贴图或光线追踪阴影，DDGI仅负责间接漫反射光照的一次或多次弹射，不包含直接光贡献。

**误区二：探针分辨率越高越好**。辐照度探针存储的是方向上的低频漫反射信号（球谐函数的1-2阶已能描述绝大部分能量），6×6像素已足够捕捉漫反射方向分布，盲目增大探针分辨率只会增加显存带宽消耗和光线着色成本，对视觉质量的提升极为有限。真正影响质量的是探针的**空间密度**和**可见性测试精度**。

**误区三：RTGI完全等同于全局光照**。实时RTGI方案通常仅计算**一次间接漫反射弹射**（Single Bounce Indirect Diffuse），对于金属表面的多次高光弹射和焦散（Caustics）几乎没有处理能力。焦散的实时光追需要光子映射或专用的ReSTIR光子技术，尚未大规模商用。

---

## 知识关联

**与路径追踪的关系**：路径追踪是RTGI的理论基础——路径追踪通过蒙特卡洛方法对渲染方程进行无偏估计，而RTGI的所有方案本质上是路径追踪在实时预算约束下的**有偏近似**。DDGI以探针辐照度缓存替代每像素完整路径追踪，以EMA时序滤波替代帧间样本累积，从而将每帧光线需求压缩至路径追踪的百分之一以下。理解蒙特卡洛估计方差与样本数的 $1/\sqrt{N}$ 收敛关系，有助于直观理解为什么DDGI的探针更新需要时序稳定性策略。

**后续扩展方向**：掌握RTGI后，可进一步研究ReSTIR系列算法（针对直接光的ReSTIR DI和针对间接光的ReSTIR GI），以及Lumen的全层级GI架构（屏幕空间缓存 → SDF近场 → 硬件光追远场）。此外，神经辐照度缓存（Neural Radiance Cache，NRC）代表了将神经网络引入光追GI的新方向，用小型MLP网络在线学习场景辐照度分布，进一步降低光线预算需求。