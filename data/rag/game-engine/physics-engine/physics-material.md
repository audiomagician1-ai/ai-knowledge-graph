---
id: "physics-material"
concept: "物理材质"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["材质"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 物理材质

## 概述

物理材质（Physics Material）是游戏引擎物理系统中用于描述物体表面物理属性的数据资源，它通过定义摩擦系数、弹性系数（恢复系数）等参数，控制碰撞体之间相互作用时的实际物理表现。两个碰撞体接触时，物理引擎会取双方物理材质的参数进行计算，从而决定物体是在表面上滑行、滚动，还是弹起、停止。

物理材质的概念来源于现实物理学中的接触力学（Contact Mechanics）与摩擦学（Tribology）。Havok、PhysX 等主流游戏物理引擎均将其实现为独立的可复用资源文件。在 Unity 中它被称为 Physic Material（注意无字母 s），在 Unreal Engine 中则被称为 Physical Material，两者参数略有差异但概念一致。没有正确设置物理材质，冰面与混凝土地板的行走手感将完全相同，子弹打在橡胶上与打在金属上也不会有任何区别，游戏世界的真实感将大幅下降。

## 核心原理

### 摩擦系数（Friction Coefficient）

摩擦系数分为**静摩擦系数（Static Friction）**和**动摩擦系数（Dynamic Friction）**两类。静摩擦系数描述物体从静止状态开始运动所需克服的阻力比例，动摩擦系数描述物体已在运动时受到的摩擦阻力比例。在 PhysX 引擎中，摩擦力的计算公式为：

> **F_friction = μ × F_normal**

其中 μ 为摩擦系数，F_normal 为法向接触力。两个碰撞体之间的最终摩擦系数由引擎根据所选的**合并模式（Combine Mode）**决定，常见合并模式包括：Average（取平均值）、Minimum（取较小值）、Maximum（取较大值）、Multiply（相乘）。例如，Unity 中冰面材质动摩擦系数通常设为 0.01，而橡胶材质可设为 0.8，当两者接触时若模式为 Average，最终摩擦系数为 0.405。

### 弹性系数（Bounciness / Restitution）

弹性系数又称**恢复系数（Coefficient of Restitution，COR）**，取值范围为 0.0 到 1.0。0.0 表示完全非弹性碰撞（碰后物体不弹起，动能全部损失），1.0 表示完全弹性碰撞（碰后以相同速度弹回，理论上无能量损失）。公式为：

> **e = |v_after| / |v_before|**

其中 e 为恢复系数，v_before 与 v_after 分别为碰撞前后的法向速度大小。篮球材质的 COR 约为 0.76，网球约为 0.75，钢球落在钢板上约为 0.52。在 Unreal Engine 5 中，Physical Material 的 Restitution 参数默认值为 0.3，适合大多数普通地面。弹性系数同样支持上述四种合并模式，且弹性系数合并模式与摩擦系数合并模式可以独立设置。

### 物理表面类型（Physical Surface Type）

除数值参数外，物理材质还承载着**表面类型标签**功能，允许开发者为每种材质指定一个枚举类型标识符。在 Unreal Engine 中，Physical Material 中的 Surface Type 可在 Project Settings → Physics → Physical Surface 中最多定义 62 种自定义类型（SurfaceType1 至 SurfaceType62）。游戏逻辑通过射线检测（Raycast）或碰撞回调中返回的 Physical Material 引用，读取其 Surface Type，从而触发对应的音效、粒子特效或动画反馈——例如脚踩在沙地上播放沙沙声，踩在金属板上播放金属碰撞声。这使得物理材质不仅是物理模拟参数容器，也是游戏表现层与物理层之间的信息桥梁。

## 实际应用

**冰面滑行效果**：将冰面碰撞体的 Physic Material 设置为动摩擦系数 0.01、静摩擦系数 0.01、弹性 0.0，角色碰撞体保持默认摩擦系数 0.6，合并模式选 Minimum，最终摩擦系数接近 0.01，角色踩上冰面后几乎无法自主减速，从而还原溜冰感觉。

**弹球游戏**：弹球碰撞体赋予弹性系数为 0.9 的物理材质，墙壁使用弹性系数 0.9 的材质，合并模式选 Multiply，则每次碰撞保留约 81% 的速度，弹球会持续弹跳但逐渐衰减，符合真实弹球台的物理预期。

**脚步音效系统**：在 Unreal Engine 中，将石板地面 Physical Material 的 Surface Type 设为 SurfaceType2（Stone），泥土地面设为 SurfaceType3（Dirt）。角色 Anim Notify 触发脚步事件时，通过 LineTraceByChannel 从角色脚部向下检测，取命中结果中的 Physical Material，读取 Surface Type 后在蓝图 Switch 节点分支播放对应音效资产。

## 常见误区

**误区一：弹性系数设为 1.0 就能让物体永远弹跳。**  
实际上，即便 COR = 1.0，PhysX 引擎在极低速度时会启用睡眠机制（Sleep Threshold），当刚体速度低于阈值（PhysX 默认线速度睡眠阈值约为 0.005 m/s²）时，物体会被强制进入睡眠状态停止模拟，因此永动弹跳在物理引擎内无法实现。

**误区二：两个碰撞体只要有一方没有物理材质就不产生摩擦或弹性。**  
事实上，Unity 和 Unreal Engine 均为物理材质参数提供了默认值。Unity 中未赋予 Physic Material 的碰撞体默认摩擦系数为 0.6、弹性系数为 0.0；Unreal Engine 中 Physical Material 默认 Friction 为 0.7、Restitution 为 0.3。因此即使未显式指定材质，物体依然会有摩擦和恢复行为，只是使用引擎内置默认值。

**误区三：物理材质的合并模式只影响最终数值大小，与游戏感受关系不大。**  
合并模式的选择对游戏手感有决定性影响。同样是摩擦系数 0.8 的角色与 0.1 的冰面接触：Average 模式结果为 0.45（仍有明显摩擦感），Minimum 模式结果为 0.1（极度光滑），Multiply 模式结果为 0.08（比 Minimum 更滑）。三种设置下角色在冰面上的加速和制动手感差异极为显著。

## 知识关联

学习物理材质需要先了解**物理引擎概述**中的刚体（Rigidbody）与碰撞体（Collider）概念，因为物理材质必须附加在碰撞体组件上才能生效，脱离碰撞体的物理材质资源不参与任何物理计算。同时理解碰撞检测的回调机制（OnCollisionEnter / Hit Event）有助于在代码中动态读取和切换物理材质，实现如车辆驶过不同路面时实时改变轮胎摩擦系数的进阶效果。物理材质的表面类型系统也是实现**游戏音效与粒子特效**按地表类型分发的基础数据层，在角色控制器、载具系统以及武器伤害反馈系统中均有广泛应用。
