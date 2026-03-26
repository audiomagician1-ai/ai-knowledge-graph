---
id: "vfx-destruct-chaos"
concept: "Chaos物理"
domain: "vfx"
subdomain: "destruction"
subdomain_name: "破碎与销毁"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Chaos物理

## 概述

Chaos物理是Unreal Engine 5内置的刚体物理与破碎销毁仿真框架，于UE 4.23版本作为实验性功能首次引入，并在UE 5.0正式成为默认物理引擎，完全取代了此前基于PhysX的物理系统。Chaos的核心架构采用位置基于动力学（Position-Based Dynamics，PBD）求解器，与PhysX的冲量基求解器不同，PBD能在每帧迭代中直接约束顶点位置，从而在高碎片数量场景中保持更好的稳定性。

Chaos Destruction系统专门针对实时游戏场景中的几何体破碎而设计。它将破碎数据存储在名为**Geometry Collection**的专用资产类型中，该资产在编辑器烘焙阶段就预先计算碎块的层级关系与连接图（Connectivity Graph），运行时只需查询连接状态即可触发断裂，而无需进行昂贵的实时几何切割。这一设计使大型场景中同时存在数百个破碎对象成为可能。

在特效制作流程中，Chaos物理的重要性体现在它与Niagara粒子系统、Level Sequence以及PCG程序化生成的深度整合上。美术人员可以通过Field System向碎块施加外力场，编写碎裂触发逻辑，而无需编写一行C++代码，这使得破碎特效的迭代周期大幅缩短。

## 核心原理

### Geometry Collection资产结构

Geometry Collection是Chaos Destruction的数据容器，其内部以树状层级组织所有碎块。每个碎块节点记录以下信息：局部变换（Local Transform）、连接至哪些相邻碎块（Adjacency List）以及各连接边的**应力阈值（Breaking Strain）**。当一条连接边承受的应力超过该阈值时，连接断裂，对应碎块从静态组转入动态模拟。

Breaking Strain的默认单位为kg·cm/s²，典型混凝土材质的Breaking Strain参考值约为**5000至15000**之间。在Fracture Editor中可针对每个层级单独设置该值：外层碎块通常设置较低阈值以优先破碎，内层骨料碎块设置较高阈值，形成符合物理直觉的由表及里的破碎感。

### 物理求解器配置

Chaos求解器位于World Settings > Chaos Physics面板中，关键参数包括：
- **Cluster Breaking（集群断裂）**：控制同一Geometry Collection内碎块分离的总开关
- **Iterations（求解迭代次数）**：默认值为1，增加至2-4可显著提升堆叠碎块的稳定性，但每增加1次迭代约带来15%的CPU开销
- **Collision Margin**：碎块凸包的收缩量，默认0.01 cm，过大会导致碎块悬浮感，过小会引发穿插
- **Damping（阻尼）**：线性阻尼默认0.01，角阻尼默认0.01，对粉碎性小碎块通常需调高至0.1以防止无限滚动

Chaos使用**分层集群（Cluster）**机制管理碎块的物理代理：在碎块尚未破碎时，多个子碎块合并为一个物理代理（Rigid Cluster），只消耗单个刚体的模拟成本；断裂后子碎块才各自激活独立物理代理。这一机制使初始状态下1000个碎块的Geometry Collection实际物理代价等同于1个刚体。

### Field System施力机制

Field System允许在世界空间中定义影响碎块行为的场，常用类型包括：
- **Radial Falloff Field**：以爆炸中心为原点，按距离平方衰减施加冲量，模拟爆炸冲击波
- **Uniform Field**：在指定Box范围内施加等量力，适合模拟定向风场或重力异常区域
- **Noise Field**：在场内叠加Perlin噪声扰动，为碎块运动添加有机感

通过蓝图调用`Apply Radial Break Field`节点，传入冲量强度（Magnitude，单位kg·cm/s²）和衰减半径，即可在运行时触发范围内所有Geometry Collection的连接断裂。

## 实际应用

**建筑物爆破场景**：在UE5的Lyra示例项目中，混凝土柱子使用Voronoi分裂（层级0约20块，层级1约80块）预先构建Geometry Collection。游戏中炸弹爆炸时，通过Field System在爆炸点发送一个Magnitude=50000的Radial Break Field，配合Niagara发射碎石烟尘粒子，整个爆炸特效的物理碎裂部分仅需约3ms GPU时间。

**玻璃窗破碎**：玻璃材质适合使用Planar切割而非Voronoi，将平面切割角度设置为30°交叉网格，Breaking Strain设为800，使玻璃在受到较小冲击时即大面积碎裂。启用`Enable Clustering`并设置Cluster Break Type为`Strain`，可实现玻璃从冲击点向外辐射式蔓延断裂的视觉效果。

**程序化城市破坏**：结合PCG图表批量生成建筑，每栋建筑的Geometry Collection可共享同一资产并通过`Geometry Collection Component`各自独立模拟，CPU端的Cluster激活是惰性的（Lazy Activation），未被触发的建筑不消耗物理预算。

## 常见误区

**误区一：认为Chaos碎块数量越多视觉越好**  
实际上，单个Geometry Collection建议碎块总数控制在500块以内。超过此数量后，每帧的Cluster状态评估和碰撞窄相（Narrow Phase）检测开销呈非线性增长。正确做法是通过层级破碎（Hierarchical Fracture）让远处保持大块碎片，仅近处碎块进入细碎层级，而非无差别增加碎块密度。

**误区二：混淆Chaos碎裂与运行时动态切割**  
Chaos Destruction所有的切割面都是编辑器预计算的，运行时无法产生新的切割几何，只能沿预设切割面断裂。如果场景需要根据子弹入射角度产生不同切割面的效果，必须额外使用Runtime Virtual Texture遮罩或Decal叠加视觉欺骗，而不能依赖Chaos本身生成新几何。

**误区三：在移动平台上直接使用默认参数**  
Chaos物理求解器的默认Solver Tick Rate为60Hz，在移动端（通常30Hz渲染）这会导致物理与渲染不同步，碎块出现抖动。需在Project Settings中将Physics > Async Scene > Max Substep Delta Time设置为0.0333（即30Hz），并将Chaos迭代次数降至1，否则移动端单帧物理计算可能超过8ms预算。

## 知识关联

**前置概念：运行时碎裂**  
理解运行时碎裂（Runtime Fracture）中Geometry Collection的创建流程是使用Chaos物理的前提——Fracture Mode工具栏中的Voronoi、Plane、Cluster Bond等操作直接决定了Chaos求解器能使用的连接图结构。没有正确预烘焙的Geometry Collection，Chaos求解器的Breaking Strain参数将无从作用。

**后续概念：层级破碎**  
掌握Chaos物理的单层破碎原理后，层级破碎（Hierarchical Fracture）在此基础上引入多层嵌套Cluster概念，允许同一Geometry Collection在不同冲击强度下逐级解体。层级破碎的LOD切换逻辑、各层Breaking Strain梯度设计，以及与Chaos求解器Cluster Depth参数的配合，都依赖于本页所述的Cluster激活机制与连接图概念。