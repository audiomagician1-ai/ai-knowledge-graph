---
id: "sequencer-extension"
concept: "Sequencer扩展"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 3
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Sequencer扩展

## 概述

Sequencer扩展是Unreal Engine中针对Sequencer编辑器进行功能扩充的技术手段，允许开发者通过C++或Python创建自定义的Track（轨道）、Section（片段）和Channel（通道）类型，从而在原有动画、摄像机、事件等内置轨道之外添加专属的时间轴控制逻辑。这种扩展机制建立在UE4.12版本引入的新Sequencer架构之上，该架构将轨道数据（UMovieScene系列类）与编辑器表现层（FSequencer系列类）彻底分离，使得自定义扩展既可影响运行时行为，也可独立定制编辑器UI。

从历史上看，旧版Matinee系统不支持自定义轨道类型，开发者只能通过Event轨道变通实现。UE4重写Sequencer后，官方在`Engine/Source/Runtime/MovieScene/`目录下暴露了完整的基类体系，包括`UMovieSceneTrack`、`UMovieSceneSection`和`FMovieSceneChannel`三层核心结构。游戏项目中常见的需求——例如为布景道具定制材质参数轨道、为战斗系统添加技能触发轨道——都可以通过这套体系实现，最终结果会像内置轨道一样出现在Sequencer编辑器的"添加轨道"菜单中。

## 核心原理

### 三层数据结构

Sequencer扩展的数据模型遵循严格的三层继承体系。**Track层**继承`UMovieSceneTrack`，负责管理整条轨道的全局属性和Section集合；**Section层**继承`UMovieSceneSection`，代表轨道上某一时间范围内的一段数据块，可以被拖动、裁剪、混合；**Channel层**继承`FMovieSceneChannel`，存储Section内部的实际关键帧数据，例如浮点曲线使用`FMovieSceneFloatChannel`，布尔开关使用`FMovieSceneBoolChannel`。三者的关系可以简述为：一条Track包含多个Section，每个Section内部持有一个或多个Channel。

### 运行时求值系统

Sequencer的运行时求值通过**Evaluation Template**机制完成，而非直接在Track上执行逻辑。开发者需要为自定义Track实现`UMovieSceneTrack::CreateTrackInstance()`，返回一个继承自`FMovieSceneEvalTemplate`的模板对象，并在该模板的`Evaluate()`函数中编写每帧的逻辑。`Evaluate()`函数接收`FMovieSceneContext`参数，其中包含当前求值时间`FFrameTime`（UE5中以`FFrameNumber + SubFrame`表示，精度为1/24000帧）和求值方向（正向/反向播放）。运行时模板与编辑器代码物理分离，意味着打包后的游戏可以正常播放自定义轨道而无需编辑器模块。

### 编辑器层绑定

仅有数据层还不足以让自定义Track显示在编辑器中，还需要通过`ISequencerModule`的扩展接口注册编辑器行为。具体做法是在编辑器模块的`StartupModule()`中调用`ISequencerModule::RegisterTrackEditor<FMyCustomTrackEditor>()`，其中`FMyCustomTrackEditor`继承自`FMovieSceneTrackEditor`。该类需要重写`SupportsType()`来声明支持的Track类型，重写`BuildTrackContextMenu()`来添加右键菜单项，以及重写`BuildObjectBindingTrackMenu()`来决定轨道是否出现在某类Actor的绑定菜单中。对于Channel的可视化（即曲线编辑器中的显示方式），则需要通过`FMovieSceneChannelTraits`特化模板来声明Channel的UI属性，如颜色`FLinearColor(1.0f, 0.5f, 0.0f, 1.0f)`和显示名称。

### 自定义Section的时间混合

当同一轨道上的两个Section时间段发生重叠时，Sequencer会按照`EMovieSceneBlendType`枚举决定混合方式，可选值包括`Absolute`（绝对值覆盖）、`Additive`（叠加）、`Relative`（相对偏移）。自定义Section可以通过在构造函数中调用`SetBlendType(EMovieSceneBlendType::Additive)`来声明支持的混合模式，并在Evaluation Template中实现对应的混合逻辑，以实现类似多层动画权重叠加的效果。

## 实际应用

**材质参数控制轨道**是最常见的自定义Track案例。项目需要在过场动画中动态调整场景灯光材质的自发光强度，内置的MaterialParameter轨道只支持ScalarParameter，若要同时驱动一组相关参数，可以创建自定义Track，在Section内部放置多个`FMovieSceneFloatChannel`分别对应不同参数名，在`Evaluate()`中遍历绑定对象的材质实例并逐一赋值。

**技能触发轨道**适用于ARPG战斗系统，过场动画中需要精确到某一帧触发角色技能。自定义Track持有一个`TArray<FMySkillKeyframe>`，每个关键帧记录技能ID和触发时间。Section的`Evaluate()`在每帧检查当前时间是否跨越任何关键帧时间点，并调用角色技能组件的触发接口。由于Sequencer支持非线性编辑和倒放，`FMovieSceneContext`中的`GetDirection()`返回值决定了技能触发是否需要撤销逻辑。

**本地化字幕轨道**是另一个典型场景，轨道存储带时间码的字幕文本（`FText`类型），通过自定义Channel在编辑器中以文字标签而非曲线形式显示，实现类似NLE软件中字幕条的外观效果。

## 常见误区

**误区一：在Track类中直接编写游戏逻辑**。很多初学者习惯将`Evaluate()`逻辑写在`UMovieSceneTrack`的子类中，但Track类实际上是纯数据容器，不参与运行时求值循环。正确做法是实现单独的`FMovieSceneEvalTemplate`子类，否则打包后的运行时将无法执行任何逻辑，因为Track类的编辑器代码可能在运行时模块中被剥离。

**误区二：混淆Section时间范围与Channel关键帧时间**。Section的起止时间（`TRange<FFrameNumber>`）控制整个片段的激活区间，而Channel内部的关键帧时间是相对于Section起始点的局部时间偏移。当用户在编辑器中拖动Section位置时，Channel关键帧的世界时间随之整体平移，但局部偏移值不变。若在`Evaluate()`中使用绝对世界时间去查询Channel数据，将会得到错误的采样结果；应始终使用`FMovieSceneContext::GetTime()`减去Section的`GetInclusiveStartFrame()`来换算为局部时间。

**误区三：认为注册TrackEditor是可选步骤**。如果跳过`RegisterTrackEditor`，自定义Track的数据仍然可以被序列化和播放，但Sequencer编辑器无法显示该轨道的Section，用户也无法在UI中添加它，导致只能通过代码手动创建Track实例。对于需要美术或动画师使用的工具，编辑器注册是不可省略的环节。

## 知识关联

Sequencer扩展建立在**编辑器扩展概述**所讲述的模块分离原则和`IModuleInterface`注册机制之上：自定义TrackEditor必须放在`Editor`类型模块（`.uproject`中`"Type": "Editor"`）中，而数据类（Track/Section/Channel）放在`Runtime`模块，这与编辑器扩展概述中关于运行时/编辑器模块隔离的要求完全一致。理解`UCLASS()`宏和反射系统对于Track数据类的序列化同样至关重要，因为`UMovieSceneTrack`子类的属性依赖UObject反射才能被存入`.uasset`文件。

在Sequencer扩展的基础之上，项目可以进一步探索**Sequencer Binding与World Partition**的联动——即自定义Track如何通过`FMovieSceneObjectBindingID`引用流式关卡中的Actor，以及**Python脚本自动化**在Sequencer中批量创建自定义Track的工作流，这些属于Sequencer在大型开放世界项目中的高级应用方向。