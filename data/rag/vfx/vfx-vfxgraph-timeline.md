---
id: "vfx-vfxgraph-timeline"
concept: "Timeline集成"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Timeline集成

## 概述

Timeline集成是指将Unity VFX Graph特效系统与Timeline编辑器结合使用，通过PlayableDirector组件和VFX Binding Track实现对粒子系统的时间轴级精确控制。这项功能允许美术师和技术美术师在Timeline的剪辑片段（Clip）层面控制VFX Graph的播放、暂停、停止以及参数调制，使特效成为电影级过场动画（Cutscene）和游戏序列的精准组成部分。

Timeline集成功能在Unity 2018.3版本中随VFX Graph的早期预览包一同引入，正式稳定版本在Unity 2019.3 LTS中发布。在此之前，开发者只能通过脚本手动调用`visualEffect.Play()`和`visualEffect.Stop()`来控制特效时序，无法利用Timeline的非线性编辑能力对特效关键帧进行可视化调整。

Timeline集成对电影化游戏体验至关重要：一个爆炸特效可能需要在角色台词结束后第0.3秒触发，并在镜头切换前第0.5秒完全消散，这种精度要求单靠事件回调难以维持，而Timeline的帧级对齐能力正是为此而生。

## 核心原理

### VFX Binding Track与Clip结构

Timeline集成的核心机制依赖于`VisualEffectControlTrack`（VFX控制轨道）。在Timeline窗口中添加一条VFX Control Track后，将场景中的`VisualEffect`组件拖入轨道的绑定槽（Binding Slot），即建立了Timeline与VFX Graph实例之间的驱动关系。轨道上的每个Clip代表一段特效活跃时间窗口，Clip的起始帧触发`SendEvent("OnPlay")`，结束帧触发`SendEvent("OnStop")`，这两个事件名称与VFX Graph内部的On Start和On Stop上下文节点直接对应。

### Scrubbing与时间重映射

Timeline最重要的特性之一是Scrubbing（时间轴拖拽预览），但粒子系统的模拟本质上是时间累积的，无法像动画曲线那样随机访问任意时刻的状态。为解决这一问题，VFX Graph在Timeline集成中引入了Reinit-On-Scrub机制：当编辑器检测到时间轴被反向拖动超过1帧时，自动重置粒子模拟并从Clip起始点快速重播至目标时间点（称为"Catch-up simulation"），其内部使用`simulationStepCount`参数控制追赶模拟的精度与性能开销之间的平衡。

Clip属性面板中还提供`Start Seed`字段，固定随机种子可确保每次Scrubbing时粒子行为完全可复现，这对动画师校对关键帧位置极为重要。

### 通过Timeline驱动Exposed Property

VFX Binding Track不仅控制播放状态，还可通过Clip的`Attribute Track`子轨道对VFX Graph中的Exposed属性（暴露属性）进行关键帧动画。在Clip属性面板的`Attribute Binder`列表中添加目标属性绑定后，Timeline会在每帧调用`visualEffect.SetFloat()`、`visualEffect.SetVector3()`等API将曲线采样值写入VFX Graph。这意味着爆炸的半径、颜色强度、发射率均可跟随Timeline曲线精确变化，而无需任何运行时脚本。

属性绑定支持的类型包括：`float`、`int`、`bool`、`Vector2`、`Vector3`、`Vector4`、`Color`、`Texture2D`、`Mesh`，涵盖了VFX Graph中绝大多数可暴露的参数类型。

## 实际应用

**过场动画爆炸序列**：在一段30秒的CG过场动画中，策划需要在第18.5秒精确触发建筑倒塌特效。使用Timeline集成，美术师在第18秒30帧位置放置VFX Control Clip，Clip时长设为4秒。同时在Attribute Track中为`SpawnRate`属性设置从500渐变到0的曲线，使粒子在特效后期逐渐稀疏，避免硬切断的突兀感。

**天气系统与剧情联动**：角色进入洞窟的过场动画需要外部的暴风雪特效在门关闭时（第8秒）迅速减弱。开发者将`WindStrength`（Vector3类型的Exposed属性）绑定到Attribute Track，在第8秒到第9秒之间设置贝塞尔缓出曲线，Timeline每帧将计算值通过`SetVector3("WindStrength", value)`写入VFX Graph，配合VFX内部的湍流节点，实现物理自洽的风力衰减效果。

**运行时Timeline与VFX的动态组合**：通过`PlayableDirector.playableAsset`在运行时替换Timeline资产，同时保持VFX Binding Track的组件绑定不变，可实现同一VFX实例在不同剧情分支中呈现不同的特效时序，适用于程序化叙事游戏中的分支过场动画。

## 常见误区

**误区一：认为Clip结束后粒子会立即消失**。VFX Control Clip的结束时间触发Stop事件，但VFX Graph内粒子的实际消亡取决于粒子的`Lifetime`属性。若粒子寿命为3秒而Clip仅持续1秒，Stop事件后粒子仍会在场景中存活最多3秒。正确做法是在Graph内为On Stop上下文连接Kill Block，或将Clip时长设置为不短于`最大粒子Lifetime + 发射持续时间`之和。

**误区二：Scrubbing预览与运行时效果完全一致**。编辑器中的Catch-up simulation因为使用离散时间步推进模拟，当`simulationStepCount`值较低（默认为5）时，复杂的碰撞或湍流效果在Scrubbing预览中的表现可能与实际运行结果存在细微偏差。在需要精确对位的项目中，应在Game View的Play Mode下以实际帧率验证最终效果。

**误区三：直接在VFX Graph中使用Timeline时间驱动逻辑**。部分开发者尝试在VFX Graph内部通过`Get Attribute: Age`节点自行实现时间轴逻辑，替代Timeline集成。这种方法无法受益于Timeline的非破坏性编辑、轨道混合（Track Blending）以及与Animator、Audio Track的统一时序管理，维护成本高且无法在编辑器中可视化调整。

## 知识关联

**前置概念——Shader Graph集成**：学习Timeline集成前需掌握VFX Graph中Exposed Property的声明方式，因为Attribute Binder的绑定目标正是这些已暴露的属性。Shader Graph集成中理解的材质属性暴露逻辑与VFX Graph的属性暴露机制高度类似，可类比迁移。

**后续概念——Exposed Property**：Timeline集成引出了对Exposed Property系统更深层次的需求：哪些属性类型可被暴露、如何命名以确保绑定不因重命名而失效、以及属性的默认值如何与Timeline曲线的基准值协调。掌握Timeline集成后，深入学习Exposed Property将重点转向属性的跨系统复用与版本管理策略。

**横向关联——Signal Track**：除VFX Control Track外，Timeline的Signal Track可在特定帧发送`SignalAsset`事件，配合`SignalReceiver`组件调用`visualEffect.SendEvent()`，实现比VFX Control Clip更轻量的事件触发方案，适合不需要属性动画的单次触发特效（如UI粒子爆发）。