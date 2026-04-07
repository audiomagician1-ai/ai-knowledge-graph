---
id: "blueprint-scripting"
concept: "蓝图脚本(LD)"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 2
is_milestone: false
tags: ["脚本"]

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
updated_at: 2026-03-26
---



# 蓝图脚本（关卡设计应用）

## 概述

蓝图脚本（Blueprint Scripting）是虚幻引擎5提供的可视化编程系统，关卡设计师无需编写C++代码，通过连接节点的方式即可为关卡添加交互逻辑。在关卡设计语境下，蓝图脚本的主要载体是**关卡蓝图（Level Blueprint）**和各类**Actor蓝图**，前者是每个关卡独有的单例脚本，后者可在多个关卡中复用。关卡蓝图存储在`.umap`文件内部，直接引用场景中的具体Actor实例，适合处理一次性触发事件和关卡全局状态。

蓝图系统由Epic Games于虚幻引擎4（2014年发布）时以现代形态定型，其前身是UE3的Kismet系统。对关卡设计师而言，蓝图脚本的价值在于它将"触发陷阱开关"、"打开门"、"播放过场动画"等高频关卡设计需求转化为可视化节点，使设计师在不依赖程序员的情况下完成关卡原型的功能验证，大幅缩短迭代周期。

## 核心原理

### 执行流与数据流的区分

蓝图节点图中存在两种不同性质的连线：**白色执行线（Execution Wire）**控制逻辑的执行顺序，**彩色数据线（Data Wire）**传递数值、引用或布尔值等数据。关卡设计师最常犯的困惑就来自混淆这两条线——执行线从左到右决定"先做什么后做什么"，数据线则随时被读取而不占用执行槽位。例如，`Open Door`事件节点发出白色执行线连接到`Set Actor Rotation`，同时`Float`变量通过橙色数据线向`Set Actor Rotation`的角度输入端提供数值，两种线缺一不可。

### 事件驱动模型与常用事件节点

蓝图脚本以**事件（Event）**为入口，关卡设计中最常用的事件节点包括：
- **Event BeginPlay**：关卡载入完成时触发一次，适合初始化门的状态、灯光颜色等初始条件。
- **Event Tick**：每帧触发，帧率相关，关卡设计师应谨慎使用，避免在Tick中写逻辑密集的运算。
- **On Component Begin Overlap**：当角色进入触发体积（Trigger Volume）时调用，是制作机关触发的核心事件，需在`Box Collision`组件上勾选`Generate Overlap Events`才能激活。

关卡蓝图中还可通过右键场景中已选中的Actor直接生成`Add Event for [ActorName]`的快捷引用，这是关卡蓝图特有的工作流，Actor蓝图中无法使用。

### 变量、分支与时间轴节点

关卡设计师常用的三类逻辑构建块：

**变量（Variable）**：在蓝图中声明`Boolean`类型变量`bDoorIsOpen`，可跨多个事件共享状态，避免重复触发。变量类型在左侧`My Blueprint`面板中创建，点击`+`号新增后在`Details`面板设置类型和默认值。

**Branch节点**：等同于`if-else`，输入一个布尔值，从`True`或`False`执行引脚分叉执行不同逻辑。例如：玩家靠近机关时先用Branch判断`bDoorIsOpen`是否为真，若为假才执行开门动画，防止重复播放。

**Timeline节点**：关卡设计专用的动画曲线节点，可内嵌浮点、向量或颜色曲线，直接驱动Actor的位移或旋转，无需接入Sequencer即可实现0.5秒内平滑开门的效果。Timeline的`Play`、`Reverse`、`Stop`执行引脚使其成为制作可逆机关（如可开关的门、升降平台）的首选工具。

## 实际应用

**压力板开门机关**：在场景中放置`Trigger Box`，打开关卡蓝图，选中Trigger Box后右键节点图添加`OnActorBeginOverlap`事件。连接Branch节点判断`bDoorIsOpen`变量，若为False则调用门Actor上的`Play Timeline`节点，同时用`Set`节点将`bDoorIsOpen`置为True；`OnActorEndOverlap`事件连接`Reverse Timeline`实现玩家离开后门自动关闭。整个流程约12个节点即可完成。

**单次触发的剧情对话**：用`Do Once`节点（位于Flow Control分类）包裹对话触发逻辑，确保无论玩家多少次经过触发区域，对话只播放一次。`Do Once`有一个`Reset`执行引脚，可在存档读取时重置状态，适配存档系统的需求。

**多米诺机关链**：通过`Event Dispatcher`（事件分发器）让一个Actor蓝图在机关激活时广播信号，关卡蓝图中多个其他Actor分别绑定该分发器，实现一键触发连锁反应，比在关卡蓝图中直接引用多个Actor实例更易维护。

## 常见误区

**误区1：在关卡蓝图中写所有逻辑**
新手常把所有机关逻辑都写进关卡蓝图，导致该蓝图变得臃肿且逻辑无法复用。正确做法是将可复用的机关（如标准门、按钮）封装为独立Actor蓝图，关卡蓝图只负责协调关卡全局状态和各Actor之间的通信。关卡蓝图中的Actor引用是硬引用场景实例，一旦场景对象被删除或重命名，引用会立即失效并报错。

**误区2：用Event Tick实现延迟效果**
部分设计师会在Tick中用计数器实现"3秒后触发"的效果，实际上应使用`Set Timer by Event`节点（延迟指定秒数后调用自定义事件）或`Delay`节点，后者可直接在执行链中插入等待时间，不污染Tick逻辑，也不受帧率波动影响。

**误区3：混淆关卡蓝图与Actor蓝图的适用场景**
关卡蓝图只在当前关卡有效，换图即失效；Actor蓝图随资产跨关卡使用。若把关卡专属的剧情触发器做成Actor蓝图并在其内部用`Get All Actors Of Class`查找场景对象，会产生不必要的性能开销。关卡独有的一次性触发逻辑（如最终Boss房间的灯光演出）放在关卡蓝图中才是正确归属。

## 知识关联

掌握蓝图脚本的前提是熟悉**UE5关卡编辑器**的基本操作，尤其是Outliner面板中的Actor管理、Details面板中组件属性的修改方式，以及碰撞体积的放置方法——这些是蓝图事件能够正确引用场景对象的操作基础。

在此基础上，**Sequencer（关卡设计应用）**是蓝图脚本的自然延伸：当关卡设计师需要编排多个Actor、灯光、摄像机同步运动的复杂过场时，Sequencer提供了时间轴式的多轨道编辑能力，而蓝图中的`Play Movie Scene`节点正是触发Sequencer序列的标准接口，两者配合使用才能完成完整的过场动画触发流程。**Gameplay Ability（关卡设计应用）**则进一步扩展了蓝图脚本能够交互的角色能力系统，使关卡机关可以响应玩家特定技能的激活状态，构建更复杂的谜题条件判断。