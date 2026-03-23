---
id: "terrain-collision"
concept: "地形碰撞"
domain: "level-design"
subdomain: "terrain-design"
subdomain_name: "地形设计"
difficulty: 2
is_milestone: false
tags: ["物理"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 地形碰撞

## 概述

地形碰撞（Terrain Collision）是指游戏引擎在运行时判断角色、物体与地形网格之间是否发生接触的机制，具体通过为地形生成碰撞体（Collision Shape）并使用物理引擎进行交叉测试来实现。与普通静态网格碰撞不同，地形碰撞需要处理大面积、连续起伏的曲面，因此碰撞精度与运行性能之间的权衡是地形碰撞设计的核心问题。

地形碰撞的技术演进与高度图（Heightmap）的普及密不可分。早期3D游戏（1990年代中期）往往直接用可见的三角网格做碰撞，导致多边形数量极高时帧率崩溃。Unreal Engine 1在1998年引入专用的地形碰撞组件，将可见网格与碰撞网格分离，这一思路延续至今。现代引擎如Unity和Unreal Engine 5均为Terrain/Landscape提供独立的碰撞分辨率设置，允许开发者以低于渲染分辨率的1/4甚至1/8精度生成碰撞数据，从而大幅降低物理计算开销。

地形碰撞的精度直接影响玩家体验：碰撞过于粗糙会导致角色在斜坡上漂浮或穿模，而碰撞过于精细则会引发CPU物理线程瓶颈，特别是在同时有大量NPC在地形上移动的场景中。理解如何平衡这两者，是关卡设计师与技术美术都必须掌握的实用技能。

## 核心原理

### 高度场碰撞体（Heightfield Collider）

绝大多数引擎对地形碰撞使用高度场（Heightfield）而非通用三角网格（Triangle Mesh）作为碰撞形状。高度场将地形表示为一个二维网格，每个格点存储一个浮点高度值，物理引擎只需对给定XZ坐标查找相邻四个格点并插值，即可得到该位置的碰撞高度。这种结构的查询复杂度为O(1)，远优于三角网格的BVH遍历。PhysX（Unreal的默认物理引擎）要求高度场的分辨率必须是(2^n + 1) × (2^m + 1)的形式，例如513×513或1025×1025，这是开发者在设置Landscape大小时必须遵守的约束。

### 碰撞LOD与精度分级

Unreal Engine的Landscape组件支持独立于渲染LOD的碰撞LOD设置，包含两个关键参数：**Collision Mip Level**（简单碰撞分辨率）和**Simple Collision Mip Level**（用于角色移动的低精度版本）。例如将Collision Mip Level设为1，则碰撞网格分辨率降为渲染网格的1/2；设为2则降为1/4。Unity Terrain同样提供**Terrain Collider**组件，其内部使用PhysX Heightfield，分辨率直接由地形的heightmapResolution决定，默认513×513。过高的分辨率（如4097×4097）在生成PhysX碰撞体时可能消耗超过200MB内存。

### 碰撞精度与性能的量化关系

碰撞数据的内存占用可用以下公式估算：

**M = R × R × B**

其中M为内存字节数，R为高度场单边分辨率（格点数），B为每格点字节数（PhysX Heightfield通常为2字节的16位整数高度值加上1字节的材质索引，共约4字节对齐后为4字节）。以1025×1025分辨率为例：M = 1025 × 1025 × 4 ≈ 4.2MB，这仅是碰撞体本身的内存，不含渲染数据。当分辨率加倍至2049×2049时，内存增加约4倍至16.8MB，CPU每帧的碰撞查询数量也成比例上升。

### 物理材质与地形图层

地形碰撞不只判断"是否接触"，还需要传递物理材质信息（如摩擦系数、弹性系数）以驱动角色在草地、石头、冰面上的不同移动手感。Unreal的Landscape Layer通过为每个地形绘制图层关联一个Physical Material，碰撞系统在检测到接触时返回对应材质索引。Unity则通过Terrain Layer上绑定Physic Material实现相同功能。物理材质的划分粒度受碰撞分辨率限制——如果碰撞LOD过低，两种地表的材质边界会出现锯齿状的突变，导致角色在材质交界处瞬间改变速度。

## 实际应用

**陡坡穿透问题**：当角色以高速移动（如载具速度超过30m/s）时，单帧位移可能超过两个碰撞格点的间距，导致隧穿（Tunneling）。解决方案是对载具启用Continuous Collision Detection（CCD），或在关卡中对高速行驶区域提高局部碰撞分辨率。Unreal支持对Landscape局部区域使用Landscape Spline添加额外碰撞体来强化斜坡边缘。

**大世界地形流送**：在开放世界游戏中，地形以Chunk为单位动态加载。每个Chunk的PhysX Heightfield在加载时需要约100ms的Cook时间（在主机平台上）。为避免玩家走到Chunk边界时出现碰撞空洞，通常提前2个Chunk加载碰撞数据，而渲染LOD则可以晚一个Chunk加载，两者加载优先级不同。

**NPC寻路与碰撞的配合**：AI寻路系统（NavMesh）独立于地形碰撞，但NavMesh的烘焙精度应与地形碰撞精度匹配。若地形碰撞Mip Level设为2（1/4精度），而NavMesh以原始精度烘焙，NPC可能走向碰撞体认为不可通行的陡坡，产生NPC在平坦NavMesh区域被地形卡住的Bug。

## 常见误区

**误区一：渲染网格越精细，碰撞就越准确**。实际上渲染网格与碰撞网格是完全独立的数据。Unreal的Landscape可以用8192×8192的渲染分辨率展示精细地形细节，同时用512×512的碰撞高度场处理物理交互。两者同步提升只会浪费资源，应根据游戏玩法需求单独调节碰撞精度。

**误区二：碰撞精度越高越好**。新手开发者常把碰撞Mip Level保持在0（最高精度）不做修改。在一个包含512×512渲染顶点的地形块上，Mip Level 0会生成相同分辨率的碰撞体；若地图有16个这样的Chunk同时激活，碰撞数据总量将超过67MB，并在每帧产生大量物理查询。对于玩家步行速度（约6m/s）的游戏，Mip Level 1（精度减半）在绝大多数情况下肉眼无法察觉差异。

**误区三：地形碰撞可以用普通Static Mesh Collider代替**。部分开发者尝试将地形导出为FBX并作为静态网格添加碰撞，认为这样更灵活。但三角网格碰撞体在面数超过65000时，PhysX的BVH构建时间和每帧查询开销远高于等效分辨率的Heightfield，且无法享受高度场的材质索引功能。只有在需要悬崖、洞穴等高度场无法表达的地形结构时，才应补充使用静态网格碰撞。

## 知识关联

学习地形碰撞需要先掌握**地形设计概述**中的高度图原理——高度图的像素分辨率直接决定了碰撞高度场的最大精度上限，理解这一映射关系才能合理设置碰撞参数。在此基础上，地形碰撞与**物理材质系统**紧密相连，后者依赖碰撞体携带的材质索引来驱动角色控制器的摩擦和音效响应。对于开放世界关卡设计，地形碰撞的流送策略还需与**World Partition**或**Level Streaming**机制协同设计，确保碰撞数据的加载时序早于玩家到达的时机。
