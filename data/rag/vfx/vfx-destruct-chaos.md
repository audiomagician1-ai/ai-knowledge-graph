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

Chaos物理是虚幻引擎5（UE5）内置的新一代物理模拟框架，完全取代了UE4时代的PhysX引擎，由Epic Games从UE4.23版本开始逐步引入，并在UE5中成为默认物理系统。Chaos的核心设计目标是支持大规模实时破碎与销毁效果（Chaos Destruction），能够在运行时动态模拟数百乃至数千个碎片的物理交互，而PhysX在同等规模下性能会显著崩溃。

Chaos系统的破碎功能依托于**几何体集合（Geometry Collection）**这一专属资产类型运作。与传统静态网格体不同，几何体集合将预先碎裂好的网格片段以树状层级结构存储，每个节点记录自身的变换、质量和连接关系。当外力超过设定的破碎阈值时，Chaos求解器会在单帧内断开对应连接键，释放碎片进入自由物理模拟状态，整个过程完全在CPU端的Chaos求解器线程中并行计算。

理解Chaos对于制作影视级破坏特效至关重要。《黑客帝国：矩阵重生》宣传素材及多款使用UE5制作的游戏如《堡垒之夜》Chapter 4均大量运用了Chaos Destruction来实现建筑倒塌、墙体穿透等实时破坏效果，展示了该系统在商业项目中的实际产出能力。

---

## 核心原理

### 几何体集合与连接图

几何体集合内部维护一张**连接图（Connectivity Graph）**，记录相邻碎片之间的"粘合键（Strain）"。每条粘合键拥有一个线性阈值（Linear Threshold）和角度阈值（Angular Threshold），单位均为牛顿（N）或牛顿·米（N·m）。当Chaos求解器计算出两碎片之间的接触冲量超过对应阈值时，该键被永久断开。断开操作不可逆，这与布料模拟中的弹簧恢复机制有本质区别。

在编辑器的**Fracture Mode（破碎模式）**下生成几何体集合后，可通过**Fix All（全部固定）**命令将所有根节点标记为锚定状态（Anchored），使结构在受到足够外力之前保持静止，这对于墙体、地板等建筑构件的默认状态设置至关重要。

### Chaos求解器参数配置

场景中的Chaos物理由**Physics Scene（物理场景）**中的Chaos求解器统一管理。关键参数包括：

- **Iterations（迭代次数）**：默认值为8，值越高模拟越稳定但CPU开销越大；对于大规模破碎场景建议降至4~6以维持帧率。
- **Cluster Breaking（集群破碎）**：控制子集群是否能从父集群中整体脱离，而非仅单个碎片脱落，这是实现"墙体整块崩落"效果的关键开关。
- **Collision Margin（碰撞边距）**：每个碎片的隐式碰撞形状会向内收缩该数值（默认0.0 cm），适当增大可减少碎片间的穿插抖动。

几何体集合组件（Geometry Collection Component）本身也暴露了**Damage Threshold（伤害阈值）**数组，数组索引对应层级深度，允许根层使用高阈值（如1000 N）而叶层使用低阈值（如100 N），实现"表面易碎、内部坚韧"的分层破碎效果。

### 场外休眠与激活机制

Chaos引入了**External Strain（外部应变）**的概念，通过`Apply Radial Damage`或`Apply External Strain`蓝图节点可以在运行时对指定位置施加球形范围内的破碎冲量，半径单位为厘米（cm），力度单位为内部Chaos力单位。未被外力影响的几何体集合处于**休眠（Sleep）**状态，Chaos求解器会完全跳过其计算，因此场景中存在大量静止破碎墙体时的性能开销接近于零，只有被激活的碎片集群才计入求解器负担。

---

## 实际应用

**爆炸破墙**：在墙体几何体集合的碰撞事件中调用`Apply Radial Damage`，将Damage参数设置为大于破碎阈值的值（如5000），Falloff类型选择`Linear`，即可模拟爆炸冲击波向外扩散导致中心碎裂、边缘完整的渐变效果。

**车辆碾压地面**：将地面几何体集合的根层阈值设为极高（50000 N），叶层设为车辆质量可触发的低值（800 N），配合`On Chaos Physics Collision`事件获取碰撞冲量，当车辆质量乘以加速度超过叶层阈值时仅产生表面裂纹碎片，不会整体崩塌。

**结构性倒塌**：将建筑柱体标记为锚定，柱体的线性阈值设置为2000 N，在关卡蓝图中对柱体执行`Release All Clusters`后所有锚定立即解除，配合重力即可实现建筑因支撑失效而整体坍塌的演算，这是影视过场动画中常见的预演（Previs）替代方案。

**与Niagara联动**：几何体集合提供`On Chaos Break`事件，可在碎片断裂瞬间触发Niagara粒子系统，在断裂位置生成烟尘、火花效果，实现物理与视觉特效的精确同步，延迟通常在同一帧内完成，不会产生明显视觉错位。

---

## 常见误区

**误区一：认为Chaos物理可以完全依赖运行时实时碎裂**
运行时碎裂（Runtime Fracture）虽然可行，但Chaos Destruction的主流工作流是**预烘焙碎裂**：在编辑器中通过Fracture Mode对静态网格体执行Voronoi、切片或集群破碎，生成好几何体集合后再放入场景。依赖运行时动态碎裂每帧生成新碎片会产生大量GC压力并显著拖慢求解器，在角色频繁触发破碎的战斗场景中尤为明显。预烘焙工作流的碎片几何已经存储在资产中，运行时仅需要断开连接键，性能差距可达5~10倍。

**误区二：直接将PhysX的Static Mesh碰撞体设置迁移给几何体集合**
几何体集合的碰撞形状由Chaos自动从网格体生成为**隐式曲面（Implicit Surface）**，而非PhysX使用的凸包（Convex Hull）复合体。直接在几何体集合组件上设置`Collision Profile`为PhysX预设往往无效，应在几何体集合资产的**Collision Type**属性中选择`Implicit`或`Sphere Simplified`，并调整Collision Margin而非在组件层面修改碰撞通道。

**误区三：破碎后碎片数量越多效果越好**
Chaos求解器的性能与活跃碎片数量成线性关系。在普通PC硬件上，单个求解器同时模拟超过2000个活跃刚体碎片时帧时间会超过16ms（即低于60 FPS）。实际项目中应将高密度碎裂（如1000+碎片的玻璃效果）与Niagara粒子混合使用：近处少量真实物理碎片（<100片）提供碰撞反馈，远处的视觉粉碎感由粒子系统承担。

---

## 知识关联

**前置：运行时碎裂**
运行时碎裂介绍了如何在UE5 Fracture Mode中对静态网格体执行Voronoi分割并生成几何体集合资产，理解碎片的层级节点结构和初始连接图的生成逻辑是配置Chaos求解器参数的前提——Damage Threshold数组的索引直接对应Fracture Mode中设置的层级深度数字。

**后续：层级破碎**
在掌握Chaos基础物理参数配置后，层级破碎（Hierarchical Fracture）进一步讲解如何在几何体集合中构建多层嵌套的集群结构，使破碎效果从"单层碎片散落"升级为"大块崩裂后二次碎裂"的连锁反应，涉及`Cluster Breaking`参数的精细化控制与各层独立阈值的调配策略，是制作影视级建筑倒塌的必要进阶技术。