---
id: "anim-anim-graph"
concept: "动画图"
domain: "animation"
subdomain: "animation-blueprint"
subdomain_name: "动画蓝图"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 动画图（AnimGraph）

## 概述

动画图（AnimGraph）是动画蓝图中专门用于处理骨骼网格体姿势数据的可视化节点图。它与事件图（EventGraph）的根本区别在于：AnimGraph 每帧执行一次姿势求值，其最终输出必须连接到一个唯一的 **Output Pose** 节点，该节点代表角色在当前帧的最终骨骼变换结果。EventGraph 处理逻辑和变量，AnimGraph 处理骨骼姿势——两者协作但职责完全分离。

AnimGraph 于 Unreal Engine 4 早期随动画蓝图系统一同引入，取代了旧版的 AnimTree 资产方案。其设计目标是让程序员和动画师都能通过拖拽节点连线来构建复杂的动画混合逻辑，而无需编写 C++ 骨骼求值代码。每条连线传递的数据类型是 `Pose`（姿势），本质上是一组骨骼局部空间变换（位置、旋转、缩放）的快照。

AnimGraph 之所以在运行时效率上优于纯蓝图逻辑，是因为其节点在编译时会被转换为 `FAnimNode` 结构体的 C++ 求值链，而非逐帧解释执行的蓝图字节码。这意味着一个包含状态机、混合空间和 IK 的 AnimGraph，其运行开销远低于用 EventGraph 逐帧手动插值骨骼变换。

---

## 核心原理

### 姿势数据的单向流动

AnimGraph 中的数据流方向是从左到右、从源头流向 Output Pose。每个节点接收一个或多个输入姿势，执行变换后输出新姿势。例如，一个 **Blend Poses by Bool** 节点接收两个姿势输入（True Pose 和 False Pose），根据布尔条件输出其中一个，并支持 `Blend Time` 参数控制过渡时长（单位：秒）。节点之间的白色连线代表姿势数据流，不可与普通蓝图的执行引脚（白色箭头）混淆。

### 状态机节点的嵌入

状态机（State Machine）在 AnimGraph 中以单个节点的形式存在，双击可进入其内部编辑。AnimGraph 可同时包含多个状态机节点，并将它们的输出姿势进行进一步混合。例如，一个典型的第三人称角色 AnimGraph 可能包含：一个处理下半身移动的状态机、一个处理上半身射击动作的状态机，以及一个 **Layered Blend per Bone**节点将两者按骨骼层级叠加——混合点设置在 `spine_01` 骨骼，权重值 0 表示完全使用基础姿势，1 表示完全使用叠加姿势。

### IK 节点的后处理阶段

IK 节点（如 **Two Bone IK**、**FABRIK**、**Full Body IK**）通常放置在 AnimGraph 的末尾靠近 Output Pose 处，这是因为 IK 求解依赖于前序动画节点已经确定的骨骼位置。Two Bone IK 节点需要指定 `IKBone`（末端骨骼，如手腕）、`JointTarget`（极向量控制肘部弯曲方向），以及效应器的世界空间位置。将 IK 节点放在状态机之前会导致 IK 结果被动画覆盖，这是 AnimGraph 节点顺序的关键规则。

### 本地空间与组件空间的切换

AnimGraph 中的节点默认在**本地空间（Local Space）**运行，即每块骨骼的变换相对于其父骨骼。但 IK 和某些程序化动画节点需要在**组件空间（Component Space）**运行，即所有骨骼变换相对于骨骼网格体组件原点。AnimGraph 通过 **Local to Component** 和 **Component to Local** 节点进行显式转换，这两种节点在图中以蓝色连线（组件空间姿势）和白色连线（本地空间姿势）区分。频繁的空间转换会增加 CPU 开销，因此应将同类型节点集中在同一空间内连续处理。

---

## 实际应用

**第三人称射击游戏角色**：AnimGraph 的典型结构为：移动状态机（处理 Idle/Walk/Run/Jump）→ **Layered Blend per Bone**（在 `pelvis` 以上叠加射击动画）→ **Hand IK Retargeting** 节点（确保双手握持武器位置正确）→ **Two Bone IK**（左手 IK 修正）→ Output Pose。整个图从左到右不超过 6 个主要节点，但覆盖了移动、上半身动作和手部 IK 三个层次。

**程序化脚部 IK**：在 AnimGraph 末端添加两个 **Two Bone IK** 节点（分别处理左脚和右脚），其效应器位置由 EventGraph 中的射线检测（LineTrace）每帧更新并存入变量，AnimGraph 直接读取这些变量作为 IK 目标。这种拆分让 AnimGraph 专注姿势计算，EventGraph 专注世界查询。

**混合空间的嵌入**：将 **BlendSpace 1D** 或 **BlendSpace** 资产直接拖入 AnimGraph 即可生成对应的求值节点，节点上暴露 `Speed`、`Direction` 等驱动轴参数，直接连接来自 EventGraph 设置的变量引脚，实现基于速度和方向的八方向混合行走动画。

---

## 常见误区

**误区一：在 AnimGraph 中使用延迟或异步节点**。AnimGraph 每帧同步求值，不支持 `Delay`、`Timeline` 或任何异步蓝图节点。若需要随时间变化的混合权重，应在 EventGraph 中用 `FInterp To` 更新变量，再由 AnimGraph 读取该变量作为混合权重输入。

**误区二：认为 AnimGraph 可以有多个 Output Pose**。每个 AnimGraph 有且只有一个 Output Pose 节点，所有分支的姿势数据最终必须汇聚到这一个节点。若有多套动画逻辑，正确做法是使用混合节点在 AnimGraph 内合并，而非尝试连接多个 Output Pose（这在编辑器中本身就不被允许）。

**误区三：混淆 AnimGraph 与子动画蓝图的边界**。通过 **Sub-Anim Instance** 节点可以在 AnimGraph 中嵌入另一个动画蓝图的 AnimGraph 输出，但这是独立的动画蓝图实例，而非当前 AnimGraph 的内部状态机。两者共享骨骼资产但变量空间完全隔离，父级无法直接访问子实例的局部变量，必须通过暴露的接口属性传递数据。

---

## 知识关联

学习 AnimGraph 需要先理解**动画蓝图概述**中的角色动画管线，尤其是动画蓝图实例如何绑定到骨骼网格体组件这一前置关系。

掌握 AnimGraph 之后，可以继续深入以下方向：**姿势缓存（Pose Cache）**节点允许在 AnimGraph 中保存中间姿势并在多处复用，避免重复求值同一状态机；**动画槽（Animation Slot）**节点为 Montage 播放提供插入点，是实现技能动画叠加的关键；**链接动画蓝图（Linked Anim Blueprint）**将 AnimGraph 的模块化能力提升到跨资产复用的级别；**Control Rig 节点**则将程序化骨骼控制直接嵌入 AnimGraph 的求值链中，是替代传统 IK 节点的现代方案。