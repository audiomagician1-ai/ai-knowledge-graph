---
id: "anim-sequencer"
concept: "动画序列器"
domain: "animation"
subdomain: "animation-blueprint"
subdomain_name: "动画蓝图"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 动画序列器

## 概述

动画序列器（Sequencer）是虚幻引擎（Unreal Engine）中专门用于过场动画（Cinematics）和电影级序列编排的非线性编辑工具。它于UE4.8版本正式取代早期的Matinee系统，提供了基于轨道（Track）的时间轴（Timeline）编辑界面，允许动画师和电影导演在同一编辑器内协调摄像机运动、骨骼网格体动画、音频以及特效的时间关系。

Sequencer的设计目标是让游戏内电影级内容的制作流程向好莱坞后期制作靠拢。它采用关键帧插值方式记录属性变化，时间精度默认为1/24秒帧率，可调整为30fps、60fps等标准帧率。每个Sequencer文件保存为`.uasset`格式的Level Sequence资产，可在关卡中通过`Level Sequence Actor`播放，也可以由蓝图或C++代码触发。

在动画蓝图体系中，Sequencer负责处理那些预先编排好、不需要实时游戏逻辑干预的动画段落。与动画蓝图擅长的角色状态机驱动的实时动画不同，Sequencer更适合用于剧情过场、技能演出、结局动画等需要精确帧控制的场景。

## 核心原理

### 轨道系统与层级结构

Sequencer的所有内容均以轨道（Track）为单位组织，轨道挂载在绑定的Actor或组（Group）之下。常见的轨道类型包括：**动画轨道（Animation Track）**、**变换轨道（Transform Track）**、**摄像机剪切轨道（Camera Cut Track）**、**音频轨道（Audio Track）**和**事件轨道（Event Track）**。动画轨道专门用于播放骨骼网格体上的AnimSequence或BlendSpace片段，通过在时间轴上叠放多个片段可实现动画混合（Blend），默认混合曲线为线性插值，可在每个片段的属性面板中改为缓入缓出（Ease In/Out）曲线。

轨道按照父子层级排列：最顶层可以是`Possessable`（关卡中已存在的Actor）或`Spawnable`（由Sequencer在运行时临时生成的Actor）。Spawnable对象的生命周期由Sequence掌控，场景关闭后自动销毁，适合不污染关卡的过场专用角色。

### 关键帧与曲线编辑器

Sequencer支持在任意轨道上以`Ctrl+鼠标左键`方式逐帧打关键帧，或开启**自动关键帧模式（Auto-Key）**自动记录属性变化。关键帧数值可在内置的**曲线编辑器（Curve Editor）**中调整插值类型，包括：线性（Linear）、阶梯（Constant）、立方贝塞尔（Cubic Bezier）三种模式。变换轨道中位置、旋转、缩放各分量均可独立编辑切线，实现精准的摄像机运镜曲线。

时间轴的工作范围由**工作范围标记（Work Range）**和**播放范围标记（Playback Range）**共同决定，前者定义可见区域，后者定义实际播放的帧范围，两者可独立设置。序列支持子序列嵌套，即一个Master Sequence中可以包含多个Shot Sequence，每个Shot对应一段镜头，实现非线性叙事的分段管理。

### 与动画蓝图的协同机制

当Sequencer的动画轨道驱动一个角色时，它会暂时覆盖（Override）该角色上动画蓝图的输出。具体机制是：Sequencer通过`UAnimSequencerInstance`类将当前帧的动画姿态直接注入骨骼网格体组件，动画蓝图的状态机在此期间仍在后台运算，但其输出权重被Sequencer的动画姿态压制为0。当Sequence播放结束或被停止后，权重恢复，动画蓝图重新接管角色。

**事件轨道（Event Track）**是Sequencer向动画蓝图或游戏逻辑回传信号的桥梁。在事件轨道上放置关键帧，并在该关键帧属性中指定一个`Quick Binding`函数名，Sequence播放到该帧时会调用对应Actor上的蓝图事件或C++函数。这与动画通知（Animation Notify）的触发机制相似，但事件轨道的触发时间点由Sequence时间轴精确决定，而非依赖AnimSequence内嵌的通知。

## 实际应用

**过场动画制作**：在RPG游戏的剧情对话场景中，使用Master Sequence嵌套多个Shot Sequence，每个Shot绑定不同摄像机角度。摄像机使用`Cine Camera Actor`，其光圈（Aperture）、焦距（Focal Length）等电影参数均可在Sequencer中制作关键帧动画，实现景深变化效果。整段过场通过`Play Level Sequence`蓝图节点在玩家触发对话时启动。

**技能演出动画**：对于游戏内需要打断实时控制的技能必杀演出，可将角色短暂绑定为Spawnable的替身，在Sequence中播放高质量的预录制动画，结束后通过事件轨道调用`OnSkillSequenceEnd`事件重新激活玩家控制，整个切换过程在2帧（约0.083秒@24fps）内完成，玩家感知不到控制权的交接。

**UI与环境联动**：Sequencer的属性轨道（Property Track）可以绑定到UMG控件的透明度、位置等属性，实现与3D动画完全同步的UI淡入淡出效果，时间精度可控制到单帧级别，比蓝图时间轴（Timeline节点）更易于精确对齐。

## 常见误区

**误区一：Sequencer可以完全替代动画蓝图**。两者用途根本不同：动画蓝图处理基于游戏状态实时响应的动画混合，例如根据角色速度混合走跑动画；而Sequencer处理预先编排的固定时序动画。对于需要根据玩家输入实时打断的动作，使用Sequencer会导致无法即时响应，必须由动画蓝图处理。

**误区二：动画轨道中叠加的片段会自动完美混合**。实际上，两个动画片段在时间轴上重叠时，Sequencer仅对重叠区域按**线性权重**进行混合，如果两个动画的根骨骼位移方向冲突，会产生明显的位置跳变。正确做法是：在动画轨道的Blend属性中手动调整混合曲线，或在美术阶段确保衔接动画的首尾姿态接近。

**误区三：Sequence资产可以在多个关卡间通用**。`Possessable`绑定依赖关卡中特定的Actor引用，换关卡后绑定会失效显示为红色感叹号。跨关卡复用的正确方式是将角色改为`Spawnable`类型，让Sequence自带角色蓝图类的引用，在任何关卡中均可独立播放。

## 知识关联

**与动画通知的关系**：动画通知（Animation Notify）嵌入在AnimSequence资产内部，随动画片段本身在Sequencer动画轨道上播放时自然触发。当需要在过场动画中精确触发音效或粒子特效时，应优先使用Sequencer自身的**音频轨道**和**粒子系统轨道**，而非依赖AnimSequence内嵌的通知，因为Sequencer轨道的时间点在编辑时可视化调整，而AnimSequence内部通知只能在动画编辑器中修改。理解AnimNotify的触发机制，有助于开发者判断何时在动画资产内部埋通知、何时在Sequencer事件轨道上统一管理触发逻辑，避免同一效果被双重触发。
