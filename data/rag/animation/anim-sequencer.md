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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 动画序列器

## 概述

动画序列器（Sequencer）是虚幻引擎（Unreal Engine）中专门用于过场动画（Cinematics）和线性动画编排的非线性编辑工具，于UE4.7版本正式引入并取代了早期的Matinee系统。它以多轨道时间线（Timeline）为核心界面，允许动画师将角色骨骼动画、摄像机运动、音频、特效、事件触发等内容编排在同一时间轴上，精确控制每一帧的表现。

与动画蓝图（Animation Blueprint）负责实时驱动角色状态机不同，序列器专注于**预先编排好的线性播放内容**，典型用途包括游戏开场CG、对话过场、关卡触发的剧情动画等。序列器输出的资产称为**关卡序列（Level Sequence）**，可以嵌入到关卡中由蓝图或触发器调用，也可以作为独立的**主序列（Master Sequence）**管理整段电影级过场。

序列器之所以重要，在于它将帧精度控制带入了引擎工作流：时间线精度可达到1/1000秒（子帧级别），支持SMPTE标准时间码（24fps、30fps、60fps等多种帧率），使得引擎内的过场动画可以与外部视频制作管线无缝对接。

## 核心原理

### 时间线轨道系统

序列器的界面由**轨道（Track）**和**片段（Section）**组成。每条轨道对应一类数据通道，常见轨道类型包括：
- **骨骼动画轨道（Animation Track）**：将AnimSequence片段拖入时间线，可对多个动画片段进行混合，相邻片段之间自动生成**混合区间（Blend Region）**，默认混合帧数为5帧。
- **变换轨道（Transform Track）**：记录Actor的位置、旋转、缩放关键帧，支持样条插值和线性插值切换。
- **摄像机截断轨道（Camera Cut Track）**：切换镜头所用的专属轨道，位于轨道列表顶部，每段Section代表一个摄像机的有效范围。
- **事件轨道（Event Track）**：在特定帧触发蓝图事件，与动画通知（Animation Notify）的区别在于事件轨道属于序列器级别，可跨多个Actor广播。

### 关键帧与曲线编辑

序列器使用**曲线编辑器（Curve Editor）**管理所有属性的插值。每个关键帧（Keyframe）可独立设置插值类型：`Cubic（Auto）`、`Linear`、`Constant`或`Cubic（User）`。属性值随时间的变化由贝塞尔曲线控制，调整切线手柄可精确塑造缓入（Ease In）和缓出（Ease Out）效果。

时间线的播放范围由**工作区范围（Working Range）**和**播放范围（Playback Range）**两层定义：工作区范围可超出播放范围，方便在不影响最终输出的情况下预览前后帧；播放范围的起终帧决定了导出或运行时的实际长度。

### 与动画蓝图的协作机制

当序列器控制一个拥有动画蓝图的角色时，二者存在**控制权争夺**问题。序列器提供了三种解决方式：
1. **复制并销毁（Spawnables）**：序列器在播放时生成一个临时副本，完全由序列器控制，不干扰原有蓝图逻辑，过场结束后自动销毁。
2. **可拥有对象（Possessables）**：序列器直接接管场景中已存在的Actor，过场期间覆盖动画蓝图输出，结束后归还控制权。
3. **自定义混合权重**：在骨骼动画轨道上，可调整序列器动画与动画蓝图姿势之间的**混合权重（Blend Weight）**，实现平滑过渡。

### 子序列与镜头分组

序列器支持**子序列轨道（Sub Sequence Track）**，将一个Level Sequence嵌套进另一个，实现模块化管理。例如，一段10分钟的开场动画可以拆分为"角色入场"、"对话场景A"、"对话场景B"等多个子序列分别制作，最后由主序列（Master Sequence）按时间顺序拼接。虚幻引擎还提供**镜头轨道（Shot Track）**专门用于电影级镜头管理，每个Shot本质上是一个独立的Level Sequence，拥有各自独立的时间偏移（Time Offset）。

## 实际应用

**游戏开场CG制作**：在第三人称游戏中，玩家触碰特定触发体积后，蓝图调用`Play`节点播放一段关卡序列。序列器中包含：摄像机截断轨道切换三个不同机位，骨骼动画轨道为NPC播放"伸手指路"动画（AnimSequence_PointDirection，共72帧@30fps），事件轨道在第48帧触发台词音频和字幕显示蓝图事件。整段过场时长2.4秒，结束后序列器通过`OnStop`委托通知蓝图归还角色控制权。

**实时渲染过场（In-Camera VFX）**：UE5的序列器支持**Movie Render Queue**集成，可将Timeline内容以每帧渲染（Offline Render）方式输出为EXR图像序列或ProRes视频，导出时帧率可独立设置为48fps或120fps用于慢动作素材。

**关卡过场触发流程**：在关卡蓝图中，`Get Sequence Player` → `Play`是最常见的调用链。若需要从特定时间点开始播放，使用`Play From Start`或`Set Playback Position`（传入以秒为单位的浮点数）。

## 常见误区

**误区一：认为动画通知和事件轨道功能相同**
动画通知（Animation Notify）附加在AnimSequence资产本身上，无论该动画在何处播放都会触发；而序列器的事件轨道是**序列级别**的，只在该Level Sequence播放时触发，且可以在不修改原始动画资产的情况下向任意蓝图发送事件。两者触发逻辑完全不同，混用会导致事件重复触发或漏触发。

**误区二：序列器可以替代动画蓝图处理所有角色动画**
序列器是线性工具，不具备状态机的条件判断能力，无法响应玩家实时输入。对于过场中需要根据玩家历史选择呈现不同动作的角色，正确做法是由动画蓝图保留状态判断逻辑，序列器通过混合权重平滑接管关键帧段落，而非完全替代动画蓝图。

**误区三：关卡序列资产与关卡直接绑定**
Level Sequence是独立资产，可以被多个关卡引用。但其中的Possessable对象（已拥有对象）通过软引用绑定到**特定关卡**中的特定Actor，若在其他关卡中播放同一序列，Possessable绑定会失效，此时应改用Spawnable方式让序列器自行生成临时Actor。

## 知识关联

**与动画通知的关系**：动画通知是序列器事件轨道的前置知识——理解通知的触发机制（附加在AnimSequence帧位置）有助于理解为何序列器事件轨道需要独立存在。在序列器的骨骼动画轨道播放AnimSequence时，该序列中原有的动画通知仍会正常触发，与事件轨道并行工作，因此需要明确区分二者的触发来源，避免逻辑冲突。

**与动画蓝图的关系**：动画蓝图定义了角色的实时运动逻辑，而序列器定义了过场期间的线性覆盖层。掌握Possessables与Spawnables的差异、理解混合权重的数值意义（0.0=完全由动画蓝图控制，1.0=完全由序列器控制），是两者协作的关键接口知识。

**后续拓展方向**：序列器的高级应用包括Control Rig集成（直接在时间线上进行FK/IK姿势编辑）、Movie Render Queue的渲染管线配置、以及Live Link结合动作捕捉实时录制到序列器时间线等专业影视制作工作流。