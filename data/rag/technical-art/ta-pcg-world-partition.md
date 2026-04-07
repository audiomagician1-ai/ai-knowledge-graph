---
id: "ta-pcg-world-partition"
concept: "世界分区与PCG"
domain: "technical-art"
subdomain: "pcg"
subdomain_name: "程序化生成"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 世界分区与PCG

## 概述

世界分区（World Partition）是虚幻引擎5引入的一套自动化关卡流送架构，取代了UE4中手动管理的World Composition系统。当PCG（Procedural Content Generation）框架在大型开放世界中运行时，World Partition负责将整个地图划分为若干2D网格单元（Cell），PCG生成的内容必须与这套单元加载/卸载机制深度协同，才能避免在玩家视野范围外进行无效的程序化运算。

传统的关卡流送方案要求美术人员手动切割子关卡，而World Partition + PCG的组合允许开发者在单一持久关卡（Persistent Level）内定义PCG图表（PCG Graph），系统自动决定哪些PCG Actor需要激活并产生输出。这一能力在《堡垒之夜》的超大地图迭代以及Epic内部的Valley of the Ancient演示关卡中得到了验证，证明即使在40平方公里以上的地形上，PCG结合World Partition也能将内存峰值控制在可接受范围内。

理解这一集成方案的核心价值在于：PCG组件上的**Generate on Load**属性与World Partition的Data Layer、Runtime Grid共同构成了一套生成时机控制链路。若不了解两者的触发顺序，开发者极易遭遇Actor在流送进来时重复执行生成逻辑或数据丢失的问题。

---

## 核心原理

### World Partition的网格划分与PCG的空间感知

World Partition将地图按照可配置的Cell Size（默认128m × 128m）分割，每个Cell拥有独立的加载状态。PCG的**`UPCGComponent`**在执行图表时，可通过**GetActorBounds**以及**PCG Landscape Data**节点读取当前已加载Cell的边界，从而将采样范围（Sample Surface或Get Spline Points节点的输出）限定在已流送入的几何体上。若PCG图表尝试访问尚未加载的Cell中的地形高度数据，则会返回空的Point Data，而非崩溃——这一"软失败"机制是PCG与World Partition安全协同的基础。

开发者可在PCG Graph的属性面板中开启**`bGenerateBoundsBasedOnPartition`**，启用后PCG系统会自动将整张图表的执行划分为多个Tile Job，每个Tile的范围对齐到World Partition的Cell边界，从而保证单次Tile生成不会跨越未加载区域采样数据。

### Data Layer与PCG的条件生成

World Partition的Data Layer可为场景内容打上逻辑标签（如"白天"/"战后"/"任务阶段3"），PCG图表通过**PCG Data Layer Filter**节点读取当前激活的Data Layer列表，并通过分支（Branch）节点选择不同的生成路径。例如，同一片草原在"战后"Data Layer激活时，PCG可以将稠密草地的Spawn权重降低80%、增加废弃物件的生成密度，而无需美术团队手动摆放任何Actor。

Data Layer的状态变更（`SetDataLayerRuntimeState`）会触发**`OnPCGGraphGenerated`**委托，若PCG组件的**`bActivateIfNotSet`**未正确配置，将导致Data Layer切换后PCG内容不刷新。这是UE5.1至5.3版本间最常见的World Partition + PCG联调Bug之一。

### 运行时流送触发时机与Generate on Load

PCG组件提供三种生成时机模式：
- **`GenerateOnLoad`**：Actor随World Partition流送进入时立即执行图表。
- **`GenerateOnDemand`**：仅响应蓝图或C++的显式`Generate()`调用。
- **`GenerateWithHLOD`**：配合World Partition的HLOD（Hierarchical LOD）层生成低精度代理几何，当玩家距离超过HLOD转换距离（通常800m以上）时由HLOD代理替代实际PCG输出。

当选用`GenerateOnLoad`时，PCG的执行发生在Actor的`BeginPlay`之前、`PostActorCreated`阶段，此时Landscape组件尚未完成全部碰撞Cook。因此在World Partition环境下，需要将**Landscape Projection**节点的**`Project Target`**设置为**`Height Field`**（基于高度场而非物理碰撞），以避免投影结果全部落回Y=0平面的问题。

---

## 实际应用

**开放世界森林生成案例**：在一个16km × 16km的地图中，开发者在PCG Graph里使用**Partition by Grid**节点将树木生成按512m × 512m分块，每块独立作为一个PCG Partition Actor注册到World Partition中。这样当玩家在地图某一角时，只有周边约9个Partition（约2.3平方公里）处于激活状态并持有树木实例数据，其余区域的Foliage Instance Buffer被完全释放。

**任务相关地物的动态替换**：在支持玩家破坏建筑的开放世界游戏中，PCG结合Data Layer可实现建筑从"完整"到"废墟"的无缝替换——"完整"Data Layer卸载时，PCG Graph自动清理建筑模块的Spawn结果；"废墟"Data Layer加载时，新的PCG图表分支执行碎石、墙体破口等程序化摆放，整个切换过程不依赖任何预烘焙的子关卡资产。

---

## 常见误区

**误区1：PCG生成的内容会自动参与World Partition的HLOD烘焙**
事实上，PCG在运行时动态生成的Static Mesh Instance默认**不会**被World Partition的HLOD构建系统收录。要让PCG产出的树木或建筑出现在HLOD代理中，必须在编辑器内执行**Build PCG（Preview）** 将结果固化为静态Actor，或者显式为PCG Spawner节点指定**HLOD Layer**属性，二者缺一不可。

**误区2：Cell Size越小，PCG性能越好**
减小World Partition的Cell Size会增加Cell总数和流送开销，同时导致PCG Partition Actor数量成平方级增长。对于覆盖范围超过1km²的植被PCG，Cell Size低于64m时，Partition Actor的序列化/反序列化成本往往超过PCG生成本身的计算成本，实测在UE5.2中该拐点约在48m。

**误区3：`GenerateOnLoad`模式下PCG内容在编辑器和Runtime行为一致**
编辑器中World Partition使用"Editor Cells"加载机制，其触发时机与PIE（Play In Editor）的Runtime流送时序存在差异。具体表现是：在编辑器视口中手动移动摄像机触发Cell加载时，PCG的`Generate`调用早于`LandscapeProxy`的`OnConstruction`完成，而在Runtime中顺序相反。这一差异在UE5.3的官方文档中有明确标注，需通过延迟一帧（`Delay 0`）或监听`OnLandscapeReady`事件来规避。

---

## 知识关联

本主题直接依赖**运行时PCG**中对`UPCGComponent`生命周期和`GenerateOnDemand`调用方式的理解——不熟悉PCG组件的激活状态机，就无法判断在World Partition流送回调中应使用哪种触发模式。

在技术路径上，本主题与**PCG + Nanite/ISM优化**紧密相关：World Partition管理的是Actor级别的加载粒度，而Nanite与Instanced Static Mesh（ISM）管理的是已加载Cell内的渲染批次。两套系统共同决定了大规模PCG内容的最终帧预算分配。若项目需要支持主机平台（如PS5的内存上限约16GB可用），必须同时对World Partition Cell Size、PCG Tile大小和ISM Instance上限进行联合调参，而非独立优化单一参数。