---
id: "sequencer-ld"
concept: "Sequencer(LD)"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 2
is_milestone: false
tags: ["脚本"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Sequencer（关卡序列器）

## 概述

Sequencer 是虚幻引擎（Unreal Engine）内置的非线性动画与过场动画编辑工具，专门用于在关卡中编排事件序列、摄像机运镜、角色动画及灯光变化。它在 UE4.7 版本中正式取代了旧版的 Matinee 系统，并在 UE5 中得到了大幅增强，支持全局序列（Level Sequence）与子序列（Sub-Sequence）的嵌套管理。

在关卡设计工作流中，Sequencer 允许设计师以时间轴方式精确控制关卡内多个 Actor 的属性变化，无需编写复杂代码即可实现开场动画、剧情触发演出、环境事件等效果。与单纯使用蓝图脚本逐帧控制相比，Sequencer 提供了可视化的时间轴（Timeline）编辑界面，支持以秒或帧为单位精确设置关键帧（Keyframe），最小精度可达 0.001 秒。

Sequencer 对关卡设计师的意义在于：它将"时间"作为一个可编辑的维度引入关卡叙事，让设计师能够以电影剪辑的思维来设计玩家体验节奏，例如触发 BOSS 登场动画、控制场景爆炸时序、编排多段剧情过场，而无需依赖程序员实现每一个细节。

---

## 核心原理

### 时间轴与轨道系统

Sequencer 的编辑界面由**时间轴（Timeline）**和**轨道列表（Track List）**两部分组成。时间轴以帧率（默认 30fps，可调整为 24fps 或 60fps）为刻度，设计师在轨道上为目标 Actor 的各个属性（位置、旋转、可见性、材质参数等）添加关键帧。每两个关键帧之间的插值方式可选择**线性（Linear）、常量（Constant）或贝塞尔曲线（Cubic/Bezier）**，插值方式直接决定属性过渡的动画感受。

每个 Level Sequence 资产本质上是一个 UAsset 文件，保存了所有轨道数据与 Actor 绑定关系。当 Sequence 在关卡中被 Level Sequence Actor 引用并播放时，引擎会按时间轴逐帧读取关键帧数据并覆盖对应 Actor 的运行时属性值。

### 摄像机切换与 Cinematic Camera

Sequencer 内置了 **Camera Cut Track（摄像机切换轨道）**，允许设计师在时间轴上任意时间点切换不同的 Cine Camera Actor。Cine Camera Actor 具有焦距（Focal Length，默认 35mm）、光圈（Aperture，以 f-stop 表示）、焦距对焦距离（Focus Distance）等物理摄像机参数，可模拟真实的景深效果。多机位切换、推拉摇移等运镜技巧都通过在同一 Sequence 内排列多段摄像机轨道实现。

### 与蓝图的事件触发集成

Sequencer 通过 **Event Track（事件轨道）**在时间轴特定帧触发蓝图函数。事件轨道上的每个事件标记（Event Marker）可绑定到关卡蓝图或目标 Actor 的蓝图函数，实现"第 90 帧触发爆炸特效生成"或"第 150 帧播放音效"等时序精确的逻辑联动。这是 Sequencer 与蓝图脚本协作的主要接口，设计师在 Sequencer 中控制时序，蓝图负责具体逻辑执行。

### 子序列与复用

Level Sequence 支持嵌套 **Sub-Sequence Track**，将多个小序列（如单个角色的进场动画、单段爆炸演出）作为独立资产管理，然后在主序列的时间轴上拖入排列。这种分层结构使团队可以并行制作不同片段，再由关卡设计师在主序列中统一调整各段之间的时间偏移（Time Offset）和相对位置。

---

## 实际应用

**开场过场动画**：在玩家进入关卡区域时，通过触发器（Trigger Volume）调用蓝图，蓝图调用 `Play` 函数启动绑定的 Level Sequence。序列内包含 Camera Cut Track 实现多机位切换，配合角色骨骼动画轨道播放预制的动画蒙太奇（Animation Montage），实现无缝的剧情过场。典型序列时长为 8～30 秒。

**环境叙事事件**：设计师可在 Sequencer 中编排一段 10 秒的序列，依次控制关卡内吊灯的位置抖动（0～2 秒）、窗户玻璃材质的不透明度变化（2～4 秒）、门自动开启（4 秒关键帧设置旋转到 90°），形成一段连贯的环境叙事演出，无需为每个 Actor 单独编写蓝图动画逻辑。

**BOSS 登场演出**：利用 Sequencer 的 Fade Track（淡入淡出轨道）控制屏幕黑场时机，配合 Audio Track 精准对齐背景音乐起始点（精确到帧级别），再通过 Event Track 在特定帧通知 AI 控制器开始启用战斗行为树，实现视觉、听觉与gameplay逻辑的同步登场。

---

## 常见误区

**误区一：把 Sequencer 当成运行时动画系统**
部分初学者将 Sequencer 用于需要持续响应玩家输入的角色动画（如走路、跑步循环），这是错误用法。Sequencer 适合**预定义、不受玩家输入打断的演出序列**；受玩家控制的动画应使用动画蓝图（Animation Blueprint）+ 状态机实现。用 Sequencer 驱动玩家角色的实时运动会导致输入响应失效。

**误区二：忽略 Actor 绑定的"可拥有"与"可生成"区别**
Sequencer 中绑定 Actor 有两种模式：**Possessable（可拥有，引用关卡中已存在的 Actor）**和 **Spawnable（可生成，由 Sequence 自行生成和销毁）**。若将过场专用的角色设置为 Possessable，该 Actor 必须始终存在于关卡中，可能浪费内存；正确做法是将仅在演出期间需要的 Actor 设为 Spawnable，序列结束后自动清理。

**误区三：不设定序列结束后的"完成状态"**
每个被 Sequencer 控制的属性轨道都有 **When Finished** 选项，默认为 `Keep State`（保持最终关键帧状态）。若设计师不注意，一段移动摄像机的序列结束后摄像机会停留在最后位置，导致后续游戏摄像机异常。应根据需求将其设置为 `Restore State`（恢复序列播放前的原始状态）。

---

## 知识关联

**前置知识——蓝图脚本（LD）**：使用 Sequencer 之前必须了解蓝图，因为 Sequence 的播放（`Play`/`Stop`/`Set Playback Position`）全部通过蓝图节点调用，Event Track 触发的事件也在蓝图中实现具体逻辑。不了解蓝图就无法将 Sequencer 演出与关卡的游戏逻辑联动，序列将沦为孤立的动画片段。

**关联工具——虚幻引擎 Control Rig**：对于需要在 Sequencer 中进行自定义骨骼动画调整的场景，Control Rig 作为骨骼控制层可直接在 Sequencer 的 Control Rig 轨道中嵌入，允许设计师在时间轴上直接 K 帧调整角色姿势，无需返回 DCC 软件（如 Maya）重新导出动画资产，这是 UE5 引入的重要协作特性。

**关联概念——World Partition 与流送关卡**：在使用 World Partition 的大型开放世界关卡中，Sequencer 绑定的 Actor 必须确保在序列播放时已加载进内存，设计师需配合数据层（Data Layers）或手动流送控制来保证演出 Actor 的可用性，否则序列播放时会出现绑定目标缺失的运行时错误。