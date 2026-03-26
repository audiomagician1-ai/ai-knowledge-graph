---
id: "ta-shadow-perf"
concept: "阴影性能"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 阴影性能

## 概述

阴影性能优化是实时渲染中最消耗GPU资源的领域之一。在现代游戏引擎中，一盏方向光（Directional Light）产生的阴影贴图渲染至少需要对场景进行一次额外的完整深度Pass，若使用4级级联阴影（4 Cascades CSM），则意味着该光源需要渲染4张独立的深度贴图，Draw Call数量可能翻4倍。这种开销在移动平台上尤为致命，因此理解并控制阴影渲染的各个参数是技术美术（TA）的核心日常工作。

阴影级联贴图（Cascaded Shadow Maps，CSM）由Engel在2006年提出，解决了单张阴影贴图在大场景中近处锯齿严重、远处浪费分辨率的问题。Virtual Shadow Maps（VSM）则是Unreal Engine 5引入的基于虚拟纹理的阴影方案，将整块阴影贴图拆分为16K×16K的虚拟页表，只有实际被相机看到的页才会被渲染和缓存，从而大幅降低内存和渲染带宽的浪费。理解这两类方案的工作机制，是优化阴影性能的前提。

## 核心原理

### 级联阴影贴图（CSM）的分割与权重

CSM将相机视锥体沿深度方向切割为N段（常见为2、4、8级），每段对应一张独立分辨率的阴影贴图。分割位置由对数公式与均匀分割的线性插值决定：

$$C_i = \lambda \cdot C_{log}(i) + (1-\lambda) \cdot C_{uni}(i)$$

其中 $\lambda$ 为分割系数（UE中称为 `Cascade Distribution Exponent`，默认值3.0），$C_{log}$ 为对数方案，$C_{uni}$ 为均匀方案。$\lambda$ 越大，靠近相机的级联范围越窄，近处精度越高但过渡越突兀。在Unity HDRP中，该参数对应 `Split 1/2/3` 的百分比手动配置。

每增加一级级联，GPU需要多渲染一遍场景的阴影深度Pass。因此在移动平台，建议将级联数量控制在2级以内；主机和PC平台通常使用4级。级联之间的混合区域（Blend Distance）若设置过大，会导致额外的采样开销，混合带宽建议控制在单级级联范围的5%~10%之间。

### 阴影分辨率对渲染开销的影响

阴影贴图分辨率直接决定阴影纹素密度（Texel Density）和内存占用。一张2048×2048的R32F深度贴图占用16MB显存（单面），若使用4级CSM，则共占用64MB；若升级至4096×4096，则暴涨至256MB。在UE5中，单个光源的 `Shadow Map Resolution` 通过 `r.Shadow.MaxResolution` 全局控制，默认值为2048。

软阴影（PCF/PCSS）会在采样时增加额外的Texel查找次数。标准3×3 PCF需要9次深度采样，5×5 PCF需要25次，而PCSS（Percentage Closer Soft Shadows）因需要动态调整采样核大小，开销更高，不建议在移动平台开启。阴影分辨率每翻倍，PCF的内存带宽压力随之倍增，因此高分辨率与软阴影质量不能同时无节制提升。

### 阴影距离与Fade的裁剪策略

阴影绘制距离（Shadow Distance）是控制阴影渲染范围最直接的手段。在UE4/5中，`r.Shadow.RadiusThreshold` 控制小型阴影在屏幕上的像素占比阈值（默认0.03，即3%），低于该阈值的投影物体将不产生阴影，直接减少Draw Call。Shadow Distance若从500m降至100m，方向光的CSM覆盖面积减少约96%，深度Pass中的几何体数量大幅削减。

阴影的Fade Out区域（Shadow Fade Distance）应与裁剪技术中的LOD距离配合，确保低多边形LOD模型恰好在阴影消失前切换完成，避免出现精细阴影由低模投出的画面穿帮。对于动态阴影，可为不重要的NPC设置独立的 `Max Draw Distance`，在距离超过30~50m后切换为Blob Shadow（圆形贴花阴影），GPU开销可下降70%以上。

### Virtual Shadow Maps（VSM）的页缓存机制

UE5的VSM将一张16384×16384的虚拟阴影贴图划分为128×128个页（每页128×128像素），只有相机视锥体内可见物体覆盖的页才被实际分配和渲染。静态物体的阴影页会被缓存在一个持久化的Physical Page Pool中（默认大小16MB），下一帧若该页未失效则直接复用，无需重新渲染深度。

VSM的最大性能优势在于动静分离：静态几何体的阴影页每帧几乎不更新，而动态物体仅会使其运动轨迹覆盖的少量页失效（Invalidate）。因此在静态场景占比高的开放世界游戏中，VSM可将阴影渲染帧时从CSM的4~8ms降至1~2ms。但VSM对显存池大小敏感，若 `r.Shadow.Virtual.MaxPhysicalPages`（默认2048）设置过低，会频繁触发页的驱逐（Eviction），造成阴影闪烁。

## 实际应用

**开放世界地形阴影优化**：在一个典型的500m视距开放世界项目中，将方向光CSM从4级降为3级、每级分辨率从2048降至1024，并将 `Shadow Distance` 从500m降至300m，实测可在PS5上减少约2.3ms的GPU帧时。同时对超过80m的静态建筑启用Distance Field Shadow，完全替代CSM中第3/4级的深度渲染，视觉上几乎无差异。

**角色阴影的移动端策略**：在Unity URP移动端项目中，对主角使用1级CSM（分辨率512×512），对非关键NPC关闭动态阴影并使用 `Blob Shadow Projector`，整体阴影Draw Call从每帧80次降至12次，帧率在红米Note设备上提升约18%。

**VSM的Indoor场景局限**：在室内走廊类场景，VSM频繁的遮挡和阴影角落变化会导致大量Page Invalidation，反而比CSM慢。此时建议关闭VSM，改用2级CSM配合 `r.Shadow.CSM.MaxCascades 2`。

## 常见误区

**误区一：阴影分辨率越高视觉越好**。许多TA默认将阴影贴图调至4096以消除锯齿，但实际上近处阴影锯齿的根源往往是级联分割不合理（$\lambda$ 值过小导致近处级联覆盖范围过大），而非分辨率不足。正确做法是先调整 `Cascade Distribution Exponent`，再评估是否需要提升分辨率。

**误区二：VSM可以完全替代CSM**。VSM在大型开放世界和静态场景中表现优异，但其物理页池有最大容量限制，在密集动态场景（如粒子+骨骼动画角色密集）中会因频繁Page Invalidation产生阴影质量下降，而CSM在这类场景中反而更稳定可控。

**误区三：关闭阴影就能线性提升帧率**。阴影渲染在CPU侧同样有剔除和命令录制开销。仅将 `Cast Shadow` 关闭但不减少光源数量，CPU的阴影剔除逻辑仍会执行。应同时使用 `r.Shadow.RadiusThreshold` 从源头减少参与阴影计算的光源和物体数量。

## 知识关联

裁剪技术（视锥体剔除、遮挡剔除）是阴影性能优化的上游工序。在生成CSM深度Pass之前，引擎会对每一级级联分别执行一次视锥体剔除，剔除掉不在该级联正交相机视野内的物体。若场景的遮挡剔除配置不合理（如HZB的分辨率过低），进入阴影Pass的三角形数量会增加，直接导致阴影渲染时间延长。因此优化阴影性能应先确保裁剪阶段已充分减少待渲染物体，再针对阴影贴图本身的分辨率、级联数和距离参数进行调优。

距离场阴影（Distance Field Shadows）与VSM是阴影性能的两条并行演进方向，前者用有向距离场近似远处软阴影，后者用虚拟页表优化近处精确阴影，两者在同一项目中可根据距离范围分段使用，形成互补的阴影渲染管线。