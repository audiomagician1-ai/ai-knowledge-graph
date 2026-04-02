---
id: "vfx-destruct-hierarchy"
concept: "层级破碎"
domain: "vfx"
subdomain: "destruction"
subdomain_name: "破碎与销毁"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 层级破碎

## 概述

层级破碎（Hierarchical Fracture）是一种将物体按照"大块→中块→小块"多级结构预先分割，并在运行时按层级顺序触发碎裂的特效技术。与单次全碎不同，层级破碎会先将物体分解为数个较大的Chunk，当这些大块受到足够冲击力或满足触发条件时，再进一步碎裂为中块、最终破碎为细小碎片，形成视觉上更真实的渐进式破坏过程。

该技术最早随Houdini 16版本的Voronoi层级节点（Voronoi Fracture Configure Object）在电影特效领域普及，后被引入Unreal Engine的Chaos物理系统（UE 4.23正式版中首次集成）。传统单层Voronoi破碎会产生所有碎片同时飞散的"爆米花效应"，而层级破碎通过设置至少两个以上的细分层级，解决了这一视觉失真问题。

层级破碎的价值不仅在于视觉质量，更在于运行时的性能优化：未触发细碎层级的区域仍以大块刚体参与物理运算，只有受冲击区域才激活下一层级的碎片，大幅降低了同帧内活跃刚体的数量。

## 核心原理

### 层级树结构与Cluster组织

层级破碎的底层数据结构是一棵树形Cluster图。根节点代表完整物体，第一层子节点为Level 1大块（通常10至20个），每个大块下挂载若干Level 2中块（每组4至8个），最底层叶节点为Level 3细碎片（每组20至50个不等）。在Chaos物理引擎中，这一结构以**几何集合（Geometry Collection）**的形式存储，每个节点记录父子关系及对应网格体。

Cluster内部的节点通过**内部应变阈值（Internal Strain Threshold）**保持连接。只有当施加在Cluster连接面上的冲量超过该阈值，父节点才会"断开"并释放子节点参与独立物理计算。Level 1的阈值通常设置为Level 2阈值的5至10倍，确保大块先于中块分离，形成层级感。

### 破碎触发的传播逻辑

层级破碎采用**自顶向下**的触发顺序，而非全层级同时激活。当一颗子弹击中墙体，首先判断冲量是否超过Level 1阈值：若超过，大块脱离；脱离后的大块在运动或二次碰撞中如果冲量再次超过Level 2阈值，才会进一步裂解为中块。这种级联激活依赖Chaos的**Cluster Break Propagation**参数，其中`Propagation Multiplier`默认值为1.0，将其设为0.5至0.8可以限制裂解沿着Cluster向外蔓延的速度，产生更局部化的破坏效果。

冲量传递公式为：  
**F_child = F_impact × (V_parent / V_child) × Propagation_Multiplier**  
其中 `V_parent` 和 `V_child` 分别代表父块和子块的体积，体积比保证了小块受到相对更大的相对应变，模拟真实材料力学行为。

### 预破碎几何体的生成策略

Level 1大块通常使用**基于表面法线引导的Voronoi散点**，沿结构力学薄弱点（如窗框、砖缝）布置，生成20至30个种子点。Level 2在每个大块内部独立执行Voronoi细分，种子密度提升3至5倍。Level 3可采用**Radial或Brick Pattern**，模拟混凝土骨料或砖石纹理。Houdini中的节点链路为：`Voronoi Fracture → Assemble → Connectivity → 重复三次并以Transform Pieces组合成树`。关键参数是每层的`Random Seed`必须不同，否则相邻层级会产生对齐的裂缝面，视觉上呈现不自然的同心圆碎片。

## 实际应用

**建筑物倒塌场景**：在电影《变形金刚》CG制作管线中，楼体破坏正是采用三级层级破碎：外墙大板（Level 1，约15块）→混凝土块（Level 2，约60块）→砖石粉尘（Level 3，约300块）。Level 3的细碎片往往以**粒子系统**替代刚体以节省性能，Chaos中可通过勾选`Remove on Break`并触发Niagara粒子实现无缝替换。

**游戏环境中的可破坏墙体**：UE5项目中，一堵典型可破坏墙设置为Level 1阈值10 000 N·s、Level 2阈值2 000 N·s，玩家手枪无法击碎大块，但火箭筒可直接跳过Level 1激活Level 2，形成差异化武器破坏效果。通过`Damage Threshold`数组`[10000, 2000, 500]`对应三层，美术团队无需写代码即可独立调整每层破碎难度。

**局部破坏优化**：对于大型场景中大量同类型可破坏物（如一排柱子），可将层级破碎Geometry Collection设为**Field-Driven激活**：只有进入半径5米范围内的Field才能激活Level 2及以下层级，场景中同帧活跃刚体数量可从数千降至数百。

## 常见误区

**误区一：层级越多效果越好**  
初学者常将层级设置为4至5层，但每增加一层，Cluster连接数量呈指数增长，Level 4碎片数量可能达到数千个，导致Chaos物理在触发瞬间CPU耗时飙升。实际项目中3层已是性能与效果的平衡点，Level 3以下的视觉细节几乎完全依赖粒子和贴图噪声来补充，而不是继续增加刚体层级。

**误区二：子层级Voronoi种子可以在全局空间统一生成**  
如果在全物体范围内一次性生成所有层级的Voronoi点，中块和小块的裂缝面会穿越大块边界，造成破碎时碎片从错误位置弹出的"穿模碎裂"。正确做法是**每一层的Voronoi细分必须在其父级几何体的局部包围盒内独立执行**，Houdini的`Connectivity SOP`提供了`By Attribute`模式来保证这一点。

**误区三：内部应变阈值越低破碎越真实**  
将所有层级的阈值设置为极低值（如0.1 N·s）会导致物体在轻微碰撞甚至自身重力下自发碎裂。合理的阈值应参考现实材料数据：混凝土抗拉强度约2至5 MPa，换算到游戏单位后Level 1阈值通常在5 000至15 000 N·s范围，Level 2为Level 1的20%至30%，而非无依据地调低。

## 知识关联

**前置知识——Chaos物理**：层级破碎的运行时激活完全依赖Chaos的Cluster Break机制。理解Chaos中`Rigid Body Component`的冲量计算方式（特别是`Collision Impulse`如何累积到`Strain`上）是正确设置各层阈值的基础。没有Chaos物理知识，层级破碎的参数调节将完全依赖试错而无法预判结果。

**后续概念——伤害模型**：层级破碎完成了"什么时候碎、碎成什么形状"的几何与物理定义，而伤害模型解决的是"哪种攻击能触发哪个层级"的游戏逻辑层问题。具体而言，伤害模型会将武器伤害值映射到Chaos的`External Strain`输入，决定是直接破碎至Level 2还是只能触发Level 1，两者共同构成完整的可破坏物系统。