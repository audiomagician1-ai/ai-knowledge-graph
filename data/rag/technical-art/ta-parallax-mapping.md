---
id: "ta-parallax-mapping"
concept: "视差贴图"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
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

# 视差贴图

## 概述

视差贴图（Parallax Occlusion Mapping，简称 POM）是一种基于高度图（Heightmap）在片段着色器中模拟表面凹凸深度感的实时渲染技术。与普通法线贴图只改变光照计算方向不同，POM 通过偏移纹理坐标（UV 偏移）来制造视觉上的几何位移错觉，使平坦多边形表面看起来拥有真实的凹凸起伏，例如砖墙的砖缝深度、石板地面的裂缝。

该技术的发展经历了三个主要阶段：最初的简单视差贴图（Simple Parallax Mapping，2001年由 Kaneko 等人提出）、中间的视差遮挡贴图改进版（Steep Parallax Mapping，2005年），以及真正将其推广普及的 Parallax Occlusion Mapping（2006年 Tatarchuk 在 GDC 上正式提出）。POM 在不增加任何实际几何体顶点的前提下，以每像素射线步进（Ray Marching）替代顶点位移，将性能开销控制在可接受范围内，是一种性价比极高的"廉价深度错觉"方案。

POM 的核心价值在于它的"欺骗成本极低"——一块砖墙如果用真实几何体表达每块砖的凹凸，需要数百万额外三角面；而 POM 只需一张高度图和几十次纹理采样循环，在中等距离下视觉效果与真实位移几乎相同，是游戏场景美术中大量静态环境材质的首选深度增强方案。

---

## 核心原理

### UV 偏移的数学基础

POM 的基本思想是：当摄像机以某个角度观察表面时，眼睛看到的"真实"纹素位置应该从当前视线方向做偏移。设视线向量在切线空间（Tangent Space）中的投影分量为 **V_xy**，高度图在当前 UV 采样点的高度值为 **h**（范围 0~1），则最简单的视差映射 UV 偏移公式为：

```
UV_offset = (V_xy / V_z) * h * heightScale
UV_new = UV_original + UV_offset
```

其中 `V_z` 是视线向量在法线方向上的分量，`heightScale` 是美术控制的深度强度参数，通常取 0.02~0.1 之间。这一步仅做一次采样，因此叫**简单视差贴图**，但在掠射角度（Grazing Angle）下会产生严重的"游泳"（Swimming）伪影。

### Steep Parallax Mapping 的分层步进

为解决掠射角伪影，Steep Parallax Mapping 将高度范围划分为若干等深层（通常 8~32 层），从表面最高层向下逐层步进，每步沿视线方向偏移一小段 UV，直到采样高度值大于当前层深度为止。步进次数 `numLayers` 的选择公式常用：

```
numLayers = mix(minLayers, maxLayers, 1.0 - dot(N, V))
```

即视线越接近掠射，层数越多（如最大 32 层），正面观察时层数可减少至 8 层，以此平衡质量与性能。

### 视差遮挡贴图的二分细化与自阴影

完整 POM 在找到步进交叉层之后，还会在相邻两层之间进行**线性插值细化**（或二分查找细化），将 UV 定位精度提升到亚层级别，消除层与层之间的台阶感。更重要的是，POM 还可以在同一着色器中沿**光线方向**再做一次步进，判断当前点是否被遮挡于更高的表面高度之下，从而生成**自阴影（Self-Shadowing）**，这是法线贴图完全无法做到的效果——砖缝底部会出现真实的接触阴影，而非仅依赖环境光遮蔽贴图（AO Map）来伪造。

---

## 实际应用

**游戏场景石材与砖墙**：《战地》系列（Frostbite 引擎）和《使命召唤》系列大量使用 POM 处理建筑外墙、地面石板。heightScale 参数设置约 0.05，配合 32 层步进，在中近景下可完全替代真实几何细节。

**UE5 中的材质节点使用**：Unreal Engine 5 的材质编辑器提供了 `Parallax Occlusion Mapping` 节点，输入参数包括 HeightmapChannel（通常打包进 Roughness 贴图的 Alpha 通道）、HeightRatio（即 heightScale）、MinSteps 和 MaxSteps。典型配置中 MinSteps = 8，MaxSteps = 64，并将结果 UV 输出连接到后续所有贴图的 UV 输入端。

**地面裂缝与泥土轮辙**：视线近乎垂直于地面时，POM 效果最佳；此类材质 heightScale 可设到 0.08~0.12，配合自阴影开关，使裂缝底部呈现真实遮蔽投影，不需要额外烘焙专用 AO。

**布料与皮革的细微织物感**：对于凹凸幅度极小的布纹（heightScale 约 0.01~0.02），POM 比置换贴图（Displacement Map）省去了细分曲面的 GPU 开销，适合次要道具材质使用。

---

## 常见误区

**误区一：POM 可以完全替代置换贴图**。POM 是屏幕空间的视觉欺骗，轮廓边缘（Silhouette）处依然是平坦多边形，摄像机贴近时或从侧面观察物体边缘时，凸起部分不会改变几何轮廓。置换贴图通过细分曲面（Tessellation）真正移动顶点，轮廓处有真实的几何凸起。POM 适用于中近景大面积平坦表面，不适合边缘轮廓需要精确凸起的物体（如岩石块的边缘）。

**误区二：heightScale 越大效果越真实**。当 heightScale 超过 0.1 时，视线角度偏斜的情况下 UV 偏移量会超过单个砖块纹素范围，导致采样到相邻砖块纹理区域，出现明显的纹理错位撕裂。最大安全值取决于高度图内容的空间频率，高频细节（砖缝窄）比低频内容（大石块）允许的 heightScale 更小。

**误区三：增加步进层数可无限提升质量**。步进层数超过 64 层后，在现代 GPU（如 NVIDIA RTX 4080）上每帧每像素超过 64 次纹理采样会显著增加带宽压力，通常在复杂场景中将反而成为填充率瓶颈，超过 64 层的额外质量提升在 1080P 下肉眼难以区分。真正需要高精度深度的场景，应改用 Tessellation + Displacement 方案。

---

## 知识关联

POM 的正确使用建立在 **PBR 材质基础**之上：高度图通常打包进 PBR 贴图集（如 Metal-Roughness 工作流中的 RGBA 贴图），POM 节点输出的偏移 UV 需要同时驱动 Albedo、Normal、Roughness 等所有 PBR 通道采样，否则会出现法线贴图与高度错觉不一致的"漂浮感"。

POM 与法线贴图是互补关系而非替代关系：POM 负责宏观的深度视差（视线移动时 UV 偏移），法线贴图负责微观高频光照细节。两者叠加才能获得最佳视觉效果——POM 提供砖缝的物理深度感，法线贴图提供砖块表面的细微纹理光照变化。在实际材质制作中，高度图（POM 输入）与法线贴图通常从同一套 ZBrush 或 Substance Designer 流程中同步生成，保证两者描述的是同一套几何信息。