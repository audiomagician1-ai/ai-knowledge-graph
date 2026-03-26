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
quality_tier: "B"
quality_score: 49.1
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

# Lumen系统

## 概述

Lumen是Epic Games在虚幻引擎5（UE5，发布于2022年4月）中引入的全动态全局光照与反射系统，其核心设计目标是在无需预计算光照贴图的前提下，实现电影级别的间接光照效果。与UE4中的光照贴图烘焙方案不同，Lumen支持光源、几何体和材质属性的实时变化，使昼夜交替、动态遮蔽等效果得以在运行时自然呈现。

Lumen的技术路线来源于Epic在Samaritan（2011年）和Valley of the Ancient（2021年）等演示项目中对实时全局光照的长期探索。它的核心创新在于混合光线追踪策略：并非依赖完整的硬件光线追踪（Hardware Ray Tracing, HRT），而是将有符号距离场（Signed Distance Field, SDF）软件追踪与屏幕空间追踪（Screen Space Tracing）组合，在没有RTX显卡的硬件上也能运行。

Lumen对开发者的实际意义在于消除了"光照迭代地狱"——传统流程中美术人员每次调整灯光后需要等待数小时的光照烘焙。Lumen将这个反馈循环压缩到实时响应，并通过激进的缓存机制将性能开销控制在1080p下约2-3毫秒的合理范围内。

## 核心原理

### 屏幕空间追踪（Screen Space Tracing）

Lumen首先在屏幕空间对每条光线执行层级深度缓冲（Hierarchical Depth Buffer, HZB）步进。HZB以2的幂次逐级降采样深度图，使光线能够在粗糙分辨率下快速跳过无遮挡区域，仅在命中概率高的局部切换至全分辨率精确检测。屏幕追踪的成本与屏幕分辨率挂钩，在1080p下每像素通常执行4到16步。屏幕空间追踪只能命中当前帧可见的几何体，当光线走向屏幕外或被遮挡时，系统自动切换至下一阶段的SDF追踪，这一切换由追踪结果中的`bHit`标志控制。

### 网格SDF追踪（Mesh SDF Tracing）

当屏幕追踪未能命中时，Lumen调用每个网格的局部SDF（Per-Mesh SDF）。每个静态网格体在导入时预计算一张3D纹理，存储从采样点到最近表面的有符号距离值。光线步进公式为：

$$p_{i+1} = p_i + d \cdot \text{SDF}(p_i)$$

其中 $p_i$ 是当前步进位置，$d$ 是光线方向单位向量，$\text{SDF}(p_i)$ 是当前位置的距离场值。这种球形步进（Sphere Marching）保证了每步都不会穿越表面，同时步长自适应地由距离场数值决定，远离表面时步长大、接近表面时步长小。网格SDF的精度由`r.Lumen.SceneCapture.MeshSDFRadius`控制，默认覆盖摄像机周围180米范围内的网格。

### 全局SDF与Lumen场景（Global SDF & Lumen Scene）

超出网格SDF有效范围后，Lumen使用全局SDF（Global SDF）——一个覆盖整个可见场景的4级Clipmap体素距离场，分辨率通常为每级128³或256³体素。全局SDF以摄像机为中心以级联方式排列，内层精度高、外层精度低，最远覆盖距离由`r.Lumen.Scene.DistanceField.ClipmapExtent`指定，默认值约为4096个单位（约40米/级）。与此同时，Lumen维护一个称为"Lumen场景"的辐照度缓存结构，由表面缓存（Surface Cache）组成：系统从多个方向对场景中重要网格的表面进行捕获并存储辐照度，分辨率为64×64或128×128像素的图块（Card）。光线追踪命中全局SDF后，直接从表面缓存读取命中位置的辐照度，避免了递归追踪，这是Lumen在软件追踪模式下维持实时性能的关键。

### 时间复用与降噪

Lumen以1/4甚至1/16分辨率执行追踪，再通过时间超采样（TAAU）和空间滤波重建全分辨率结果。每帧仅对部分像素更新辐照度（Checkerboard采样），利用历史缓冲中的前帧结果补全其余像素，历史帧权重的衰减系数约为0.1，意味着约10帧后历史贡献降至原始值的35%（$0.9^{10} \approx 0.35$），在快速移动场景中通过运动向量校正防止鬼影。

## 实际应用

**洞穴与室内场景的间接光照**：在《黑神话：悟空》等基于UE5的项目中，Lumen使玩家手持火把进入洞穴时，红橙色火焰的间接光照会实时染色周围岩石，这类效果在传统烘焙流程中需要手动放置辅助灯才能模拟。

**天光遮蔽（Sky Occlusion）**：Lumen替代了UE4的距离场环境遮蔽（DFAO），天光通过全局SDF追踪计算接触阴影，使户外场景中植被的接触遮蔽自然响应时间变化，Fortnite在Chapter 4引入Lumen后移除了大量手动放置的点光源补光。

**硬件光线追踪模式**：在RTX系列GPU上启用`r.Lumen.HardwareRayTracing 1`后，网格SDF追踪阶段被替换为实际的BVH硬件遍历，追踪精度提升但性能开销增加约30-50%，适合主机端（PS5/XSX均支持DXR子集）的高画质模式。

## 常见误区

**误区一：Lumen等同于路径追踪**。Lumen是一种基于缓存辐照度的近似全局光照方案，不是每帧完整路径追踪。它的表面缓存存储的是上一帧计算的辐照度均值，因此无法精确表现焦散（Caustics）和高频镜面反射。UE5另有独立的"路径追踪器"（Path Tracer）用于离线渲染，两者是平行关系而非同一系统。

**误区二：关闭硬件光线追踪会大幅降质**。软件追踪模式（默认模式）使用SDF，对90%的场景内容质量接近硬件模式，主要差距在于薄壁几何体（如树叶）和高精度镜面反射。对于不含大量透明植被的架构场景，软件模式性能更优且视觉差异极小。

**误区三：Lumen完全无需任何预计算**。Lumen仍需在导入时为每个静态网格体生成距离场（Per-Mesh SDF），这一步骤在编辑器中离线完成，存储在Derived Data Cache中。完全动态的Skeletal Mesh默认不生成SDF，其追踪精度依赖屏幕空间阶段或全局SDF的低精度近似。

## 知识关联

**前置概念——体素全局光照（VXGI）**：Lumen的全局SDF Clipmap架构直接继承了体素全局光照中的Clipmap级联思想，VXGI将场景体素化并存储辐照度，Lumen将这一思路演进为SDF辅助的精确追踪加表面缓存读取组合，解决了VXGI在尖锐几何体和细小结构上的漏光问题。理解体素GI的Clipmap分辨率权衡有助于解读Lumen各级全局SDF精度参数的设计意图。

**横向对比——硬件RT路径**：Lumen的软件追踪模式与Nvidia RTX中的专用硬件BVH遍历单元形成互补关系。掌握SDF球形步进的原理，可以理解为何在距离场误差较大的场景（如Nanite虚拟几何体）中混合使用HRT能带来准确性提升，而在大型开放世界中SDF的近似误差反而小于HRT因BVH精度不足导致的偏差。