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


# Sequencer（关卡事件序列编辑器）

## 概述

Sequencer 是虚幻引擎（Unreal Engine）内置的非线性时间轴编辑器，专门用于在关卡中编排过场动画、摄像机运镜、Actor 属性动画以及游戏事件的触发顺序。它在 UE4.8 版本引入后逐步取代了旧版 Matinee 系统，并在 UE5 中成为驱动 Lumen 光影过渡动画和 Nanite 场景过场的标准工具。

Sequencer 的核心数据容器称为 **Level Sequence Asset**（关卡序列资产），保存在内容浏览器中，可被多个关卡引用。与纯粹的蓝图脚本相比，Sequencer 提供可视化时间轴，允许关卡设计师以帧为单位（默认 30fps 或 24fps，可自行调整）精确控制每个 Actor 的位置、旋转、材质参数和声音播放时机，而无需手写 Lerp 插值逻辑。

对关卡设计师而言，Sequencer 最重要的价值在于将"叙事节奏"直接嵌入关卡结构：一段 8 秒的开门过场、一次 BOSS 登场镜头切换、或是随玩家进入触发区而播放的环境动画，都可以在 Sequencer 时间轴上拖拽 Keyframe（关键帧）完成，而不必依赖程序员修改 C++ 代码。

---

## 核心原理

### 时间轴与轨道系统

Sequencer 界面由左侧的**轨道列表（Track List）**和右侧的**时间轴区域（Timeline Area）**构成。每个被编辑的对象（Actor、摄像机、音频等）以独立的 Track（轨道）形式存在。Track 下方可嵌套 Sub-Track，例如一个 StaticMesh Actor 的 Transform Track 可以同时包含 Location、Rotation、Scale 三条子轨道。

关键帧之间的插值模式直接影响动画手感：Sequencer 支持 **Cubic（三次贝塞尔）、Linear（线性）、Constant（阶跃）** 三种主要插值类型。右键单击关键帧可切换插值模式；若选择 Cubic，切线手柄会出现在关键帧两侧，设计师可拖拽手柄调整缓入缓出（Ease In/Out）弧度，而无需填写数学公式。

### 摄像机系统与 CineCameraActor

在 Sequencer 中添加摄像机动画时，应优先使用 **CineCameraActor** 而非普通 Camera Actor。CineCameraActor 提供了焦距（Focal Length，单位 mm）、光圈（Aperture，f-stop 值）和焦点距离（Focus Distance）的动画支持，可在时间轴上记录镜头从 35mm 推进到 85mm 的变焦过程。Sequencer 的 **Camera Cut Track**（摄像机切换轨道）负责控制在哪一帧切换到哪一台摄像机，每段摄像机区间称为一个 Camera Cut Section。

### 事件轨道与蓝图通信

**Event Track（事件轨道）**是 Sequencer 与关卡蓝图或 Actor 蓝图交互的桥梁。在指定帧位置添加 Event Keyframe 后，可绑定一个蓝图函数；当 Sequence 播放到该帧时，绑定函数被自动调用。例如，在第 90 帧（3 秒处，30fps 设定下）触发爆炸粒子特效，或在第 150 帧开启某扇门的物理碰撞。这一机制要求设计师具备基础的蓝图脚本知识，理解"函数绑定"的概念。

Event Track 有两种绑定模式：**Trigger（单次触发）**与 **Repeater（循环触发）**。Trigger 模式只在播放头经过该帧时触发一次，而 Repeater 模式会在每帧持续调用，适用于需要实时跟踪参数的场景。

### Sub-Sequence 与嵌套结构

大型关卡过场往往拆分为多个 Sub-Sequence，再由主 Level Sequence 通过 **Sub-Sequence Track** 统一编排。例如，一个 60 秒的 BOSS 入场动画可以拆解为：15 秒的环境镜头（Sub-A）、20 秒的 BOSS 动作展示（Sub-B）、25 秒的 UI 提示与音乐切换（Sub-C）。这种拆分方式允许多名关卡设计师并行编辑不同的 Sub-Sequence，最终合并到主序列而不产生资产冲突。

---

## 实际应用

**触发式过场动画（In-Engine Cinematic）**：在关卡中放置 Trigger Box，当玩家角色重叠时，关卡蓝图调用 `Play` 节点播放绑定的 Level Sequence。Sequencer 会接管摄像机控制权，播放完毕后通过 `OnStop` 委托归还控制权给玩家。整个流程无需 C++ 代码，纯蓝图即可实现。

**环境动画循环**：利用 Sequencer 的 **Loop（循环）播放模式**，可以驱动风车叶片旋转、旗帜飘动或瀑布粒子的强度变化。与直接在蓝图中写 Timeline 节点相比，Sequencer 的优势在于美术或关卡设计师可以直接在时间轴上调整曲线形状，而不需要修改节点参数。

**实时参数混合**：在 Sequencer 中为 Post Process Volume 的 Exposure Compensation 属性记录关键帧，可以在过场过程中平滑调整场景曝光值从 -2EV 过渡到 +1EV，配合 Lumen 全局光照实现昼夜交替的叙事演出效果。

---

## 常见误区

**误区一：将 Sequencer 当作游戏逻辑的替代品**。Sequencer 专为确定性时间轴播放设计，不适合处理玩家输入分支或条件判断。若在 Sequencer 的 Event Track 中塞入大量游戏逻辑判断，会导致序列在倒放（Reverse）或跳帧（Jump to Frame）时事件触发顺序混乱。需要条件分支的逻辑应放在蓝图中，Sequencer 只负责播放指令的发出。

**误区二：忽略"Possess"与"Spawnable"的区别**。Sequencer 中的 Actor 绑定有两种模式：**Possessable**（持有关卡中已存在的 Actor）和 **Spawnable**（由 Sequence 自行生成并在结束后销毁）。若设计师误将一个只应在过场期间存在的摄像机设为 Possessable，在序列未播放时该摄像机仍会持续存在于关卡中，占用资源并可能干扰其他逻辑。

**误区三：关键帧精度依赖默认帧率**。Sequencer 支持每秒帧数（fps）的全局设置，但许多设计师在制作过程中忘记统一项目帧率设定。若关卡序列以 30fps 创建，而项目后期改为 60fps，所有时间轴标注的帧号位置不变，但实际播放时长会减半，导致动画节奏完全错乱。正确做法是在项目初期的 Project Settings > General Settings 中锁定 Custom Time Step。

---

## 知识关联

Sequencer 的 Event Track 功能直接依赖于**蓝图脚本（LD）**中函数绑定、委托调用和 Actor 引用的基础知识——若不理解蓝图的函数结构，就无法在 Event Track 上正确设置触发回调。同时，Sequencer 中对 CineCameraActor 焦距和景深的调节，与关卡中灯光、后处理体积（Post Process Volume）的配合使用密切相关：摄像机的 f-stop 设定直接影响景深模糊范围，而景深效果的质量又取决于 Lumen 或光线追踪的渲染管线设置。掌握 Sequencer 后，设计师可以进一步学习 **MetaSound 音频序列**与时间轴同步、以及 **Control Rig** 骨骼动画驱动，将角色表演直接嵌入关卡过场而无需依赖预烘焙的动画资产。