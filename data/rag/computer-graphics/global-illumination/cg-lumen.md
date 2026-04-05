---
id: "cg-lumen"
concept: "Lumen系统"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 4
is_milestone: false
tags: ["引擎"]

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
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Lumen系统

## 概述

Lumen是Epic Games在虚幻引擎5（UE5，2022年4月正式发布）中引入的全动态全局光照与反射系统，彻底取代了UE4时代依赖预计算光照贴图的静态GI方案。Lumen的核心技术创新在于将**有向距离场（Signed Distance Field, SDF）追踪**与**屏幕空间追踪（Screen Space Tracing）**混合使用，使开发者能够在无需任何离线烘焙的情况下实现实时间接光照、软阴影和高质量镜面反射。

Lumen的设计目标是在主机和高端PC上以30fps或60fps的帧率跑通完整GI管线，同时支持场景几何体、光源和材质的任意动态变化。相比体素全局光照（VXGI）方案需要将场景体素化并在三维网格上传播辐射，Lumen改用基于SDF的距离查询来避免昂贵的体素遍历，将单次可见性查询的复杂度从O(n)体素步进降低到对距离场的O(log n)球形步进（Sphere Marching）。

Lumen的重要性在于它代表了实时渲染从"预计算近似"向"真实动态光传输"迈进的工程里程碑。游戏中移动的太阳、打开的门洞、动态破坏物都能实时影响间接光照，这在UE4及之前的引擎工作流程中是不可能实时完成的任务。

---

## 核心原理

### 1. 屏幕空间追踪（Screen Space Tracing）

Lumen首先在当前帧的深度缓冲和GBuffer上做高精度的屏幕空间光线步进（Ray Marching）。屏幕追踪使用层次化深度（Hierarchical Z, Hi-Z）加速，将命中检测的步进次数从数十次减少到约4–8次。屏幕空间追踪仅限于摄像机可见区域的几何细节，精度极高但覆盖范围受限——当光线步出屏幕边界、打到屏幕外遮挡物或进入相机背后区域时，屏幕追踪直接"失败"，控制权交给SDF追踪阶段。两阶段之间通过一个命中置信度（Hit Confidence）标志位进行切换，置信度阈值默认为0.5，开发者可通过控制台变量`r.Lumen.ScreenProbeGather.ScreenTraces`调节。

### 2. Mesh SDF与全局SDF

Lumen为场景中每个Mesh预生成一份**Mesh SDF**（最高分辨率可达64³体素），以有符号距离值存储到最近表面的距离。在大范围追踪时，Lumen将所有Mesh SDF合并到一份低分辨率的**全局SDF（Global SDF）**，分辨率通常为4个级联层，每层256³体素，覆盖半径从数米到数百米递增（默认最远追踪距离约为200m，可由`r.Lumen.MaxTraceDistance`控制）。

球形步进（Sphere Marching）是SDF追踪的核心算法：从光线起点 $\mathbf{o}$ 出发，每步移动距离等于当前位置的SDF值 $d$，迭代公式为：

$$\mathbf{p}_{k+1} = \mathbf{p}_k + d(\mathbf{p}_k) \cdot \hat{\mathbf{r}}$$

当 $d(\mathbf{p}_k) < \epsilon$（默认约0.01cm）时判定命中。由于每步都保证不穿越任何表面，整个追踪过程无需BVH遍历，在GPU上可以高度并行化执行。

### 3. 表面缓存（Surface Cache）与辐照度存储

Lumen不直接在每条追踪光线上累积反弹，而是引入了**Surface Cache**：将每个Mesh的材质属性（反照率、法线、自发光）和当前帧的间接光照结果缓存在Atlas纹理中，分辨率按距离分为近/远两级（近级约16×16像素/卡片，远级4×4）。当SDF追踪命中一个表面时，直接查询该Mesh在Surface Cache中的辐照度，而非继续递归追踪。这种"延迟辐照度查询"将每帧实际需要跟踪的光线从理论上的数百万条降低到约每像素1条（通过时间积累）。

### 4. 屏幕探针聚集（Screen Probe Gather）

Lumen以稀疏的**屏幕探针（Screen Probe）**网格（默认每8×8像素一个探针）在屏幕空间布置采样点，每个探针发射若干半球方向的追踪光线（默认16条，时间滤波后等效64–128条），通过**自适应探针放置**在几何边缘处加密。最终以空间+时间联合重投影（Spatial+Temporal Reprojection）将探针辐照度插值到每个像素，抑制噪声的同时保持对动态变化的响应延迟在约4帧以内。

---

## 实际应用

**开放世界光照**：在《黑神话：悟空》等使用UE5的项目中，Lumen使得森林场景中树冠间隙漏下的间接光随时间动态变化成为可能。Global SDF的多级联设计确保远景山体也能接收到正确的天空遮蔽（Sky Occlusion）而无需额外的DFAO Pass。

**室内动态灯光**：玩家手持手电筒进入黑暗房间时，Lumen会通过Surface Cache更新墙面的间接辐照度，使远处角落出现正确的一次反弹漫反射颜色渗色（Color Bleeding），响应延迟约1–2帧，视觉上感知为即时。

**硬件光线追踪模式**：当目标平台支持DXR时，Lumen可将屏幕空间追踪失败后的后备路径从SDF替换为硬件RT（通过`r.Lumen.HardwareRayTracing=1`开启），此时Mesh SDF不再生成，追踪精度提升但GPU内存占用增加约200–400MB。

---

## 常见误区

**误区1："Lumen是路径追踪"**
Lumen采用的是基于SDF球形步进的近似可见性查询，并非蒙特卡洛路径追踪。Lumen默认只计算**一次漫反射间接反弹**（One Bounce Indirect Diffuse），更多反弹依靠Surface Cache的历史帧信息近似。真正的无偏路径追踪是UE5另一个独立功能——Path Tracer，二者共享部分基础设施但原理和用途完全不同。

**误区2："关闭Lumen可以提升所有平台性能"**
在不支持体积雾遮蔽（Volumetric Fog Shadowing）和动态天空光的场景中，关闭Lumen必须同时启用替代的SSAO和静态GI，否则画面质量会出现明显的漏光和黑面。Lumen系统在移动平台上（iOS/Android）目前默认关闭，需用`r.DynamicGlobalIlluminationMethod=0`并搭配烘焙贴图。

**误区3："Mesh SDF精度越高越好"**
Mesh SDF分辨率提升时，GPU内存消耗以立方关系增长（分辨率翻倍则体积增加8倍）。对于薄壁几何体（厚度 < 2个体素单元），高分辨率SDF反而会因采样误差产生漏光（Light Leak），正确做法是对薄壁使用`Two-Sided Distance Field`选项，而不是一味提升分辨率。

---

## 知识关联

**与体素全局光照的关系**：Lumen可视为对VXGI架构的直接工程改进。VXGI将场景离散为均匀体素锥追踪（Voxel Cone Tracing），追踪步长固定；Lumen用SDF将步长变为自适应，消除了VXGI在大空旷场景中浪费的空体素步进，同时Surface Cache的辐照度更新机制与VXGI的"辐射注入→传播→过滤"三阶段有直接对应关系，学习过VXGI的开发者能快速理解Lumen中辐照度存储与更新的设计动机。

**与实时阴影技术的关系**：Lumen的全局SDF同时用于生成软阴影的**Distance Field Soft Shadows**，与Ray Traced Shadow共享SDF数据结构但走不同的Shader路径，在场景编辑器中调整`Mesh Distance Field Resolution Scale`参数会同时影响GI追踪精度和软阴影精度。