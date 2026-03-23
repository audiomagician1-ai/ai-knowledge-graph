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
quality_tier: "pending-rescore"
quality_score: 40.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 动画图（AnimGraph）

## 概述

动画图（AnimGraph）是虚幻引擎动画蓝图中专门用于处理骨骼网格体姿势计算的可视化节点图。它与动画蓝图中的事件图（EventGraph）严格分离：事件图负责逻辑驱动和变量赋值，而动画图的唯一职责是在每一帧将若干个姿势数据流（Pose）从左至右传递，最终将一个单一的姿势输出到"输出姿势"（Output Pose）节点，驱动角色骨骼做出相应动作。

动画图的设计起源于虚幻引擎4的早期版本（约2013年随UE4公测推出），借鉴了Houdini和Shader Graph等基于节点的可视化编程思想，将原本需要C++手写的姿势混合逻辑封装为可拖拽的节点。与UE3时代的AnimTree相比，AnimGraph引入了"编译为字节码"的执行模型，使得节点图在运行时并非逐个调用蓝图虚拟机，而是被编译为紧凑的动画节点更新序列，大幅降低了每帧的CPU开销。

动画图的重要性体现在它是连接状态机（State Machine）、混合空间（Blend Space）、IK解算器（如Two Bone IK、Full Body IK）、蒙太奇槽（Slot）等所有运行时姿势处理节点的唯一场所。任何无法在动画图中表达的姿势操作，都无法出现在最终骨骼动画结果中。

---

## 核心原理

### 姿势数据流与求值顺序

动画图中的每根连线传递的并非是一帧已经计算好的变换数组，而是一个"姿势求值请求"（Pose Evaluation Request）。当引擎调用`UAnimInstance::UpdateAnimation()`后，随即触发`EvaluateAnimation()`，从"输出姿势"节点出发，**向左**递归地向各上游节点请求数据。这种惰性求值（Lazy Evaluation）方式意味着，如果某条分支的混合权重为0，该分支的所有上游节点将被跳过，不消耗计算资源。这一机制是动画图性能优化的基础。

### 三类核心节点及其连接关系

动画图中的节点按功能分为三大类：

- **姿势来源节点**：包括序列播放器（Sequence Player）、混合空间播放器（Blend Space Player）、状态机节点。这些节点只有输出姿势引脚（白色骨骼图标），没有姿势输入，是整个图的数据源头。状态机节点内部又自含一个独立的状态机图层，各状态内部可再嵌套序列播放器或混合空间。

- **姿势变换节点**：包括分层混合（Layered Blend Per Bone）、叠加混合（Apply Additive）、两骨IK（Two Bone IK）、变换骨骼（Transform Bone）等。这类节点拥有一个或多个姿势输入和一个姿势输出，对输入姿势执行数学变换后传递给下游。例如Two Bone IK节点需要指定末端骨骼名称（如`hand_r`）和IK目标位置向量，才能正确完成FABRIK解算。

- **输出节点**：每个动画图有且仅有一个"输出姿势"节点（Output Pose），是整个图的终端。动画图不允许存在多个输出，所有姿势流必须汇聚于此。

### 编译与执行模型

动画图在保存时会触发编译，引擎将节点图转化为`FAnimNode_Base`派生结构体的线性执行序列，存储于`UAnimBlueprintGeneratedClass`中。每个节点对应一个C++动画节点结构体——例如状态机对应`FAnimNode_StateMachine`，两骨IK对应`FAnimNode_TwoBoneIK`。这意味着在动画图中添加的每一个节点，都会在编译后的类实例中占用相应的内存，因此无限制地堆砌节点会增加每个动画实例（AnimInstance）的内存占用。

---

## 实际应用

**角色武器持握IK**：在第三人称射击游戏中，常见做法是将角色上半身的动画状态机输出连接到Two Bone IK节点，该节点的"IK骨骼"设置为`hand_l`，"效果器目标"从姿势缓存或场景组件位置获取，再将IK结果通过分层混合（Layered Blend Per Bone）与下半身的移动姿势合并，最终输出完整姿势。整个流程在同一个动画图中通过不超过5个节点即可完成。

**ALS（Advanced Locomotion System）风格的多状态融合**：在动画图顶层放置一个主状态机，内部包含地面移动、空中、蹲伏等多个状态，各状态内嵌混合空间播放器。状态机输出后，接入"控制绑定输出姿势"（Control Rig Output）节点进行程序化骨骼修正，最后汇入Output Pose。这种结构体现了动画图作为"姿势流水线"的组织能力。

**子动画图（Sub-AnimGraph）**：当节点数量超过约30个时，可使用"折叠为函数"（Collapse to Function）将一组节点封装为可复用的子图，使顶层动画图保持清晰。这一功能在UE5.0之后得到显著改善，支持在多个动画蓝图之间共享子图逻辑。

---

## 常见误区

**误区一：认为动画图中可以执行游戏逻辑**
动画图的节点只能消费已有变量，不能修改动画蓝图的变量值，也不能调用带副作用的函数（如`SpawnActor`）。试图在动画图中通过"变换骨骼"节点直接读取Actor位置并触发事件是无效的——此类逻辑必须放在事件图的`BlueprintUpdateAnimation`中完成计算，再由动画图读取结果变量。

**误区二：将所有混合逻辑都堆叠在动画图根层**
初学者常将十余个状态机、混合节点直接铺在动画图的最顶层，导致图极难维护。正确做法是利用状态机的内部嵌套结构和Sub-Graph函数对逻辑分层：顶层动画图只应看到2~4个主要节点，复杂的局部混合放入各自的状态机状态内或子图中。

**误区三：认为动画图的求值方向是从左到右**
视觉上节点从左到右排列，给人数据"流向右边"的印象。但实际求值是从右端Output Pose节点向左递归拉取数据，权重为0的上游分支不会被执行。因此在性能分析时，不能仅凭节点数量判断开销，而需要关注实际执行路径上哪些节点的权重非零。

---

## 知识关联

动画图以**动画蓝图概述**中建立的"动画蓝图是状态机与混合的宿主"概念为前提——必须先理解动画蓝图的双图（EventGraph + AnimGraph）结构，才能正确区分何时在哪张图中操作。

在动画图基础上，**姿势缓存**（Pose Cache）允许在动画图内部将某个中间姿势结果保存为具名快照，供同一帧内的其他节点复用，避免重复计算，是优化复杂动画图的直接手段。**动画槽**（Animation Slot）节点作为动画图中蒙太奇插入点，必须放置在动画图中才能让蒙太奇覆盖对应骨骼层级的姿势。**链接动画蓝图**（Linked Anim Graph）节点则直接出现在动画图中，将另一个动画蓝图的输出姿势引入当前图，实现角色动画逻辑的模块化拆分。**Control Rig节点**作为动画图的特殊姿势变换节点，将程序化骨骼控制能力引入姿势流水线，是动画图节点体系在UE5时代的重要扩展方向。
