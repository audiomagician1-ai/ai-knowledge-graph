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
quality_tier: "B"
quality_score: 46.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
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

Unreal Engine 的 Sequencer 是引擎内置的非线性动画编辑器，负责过场动画、关卡序列和时间轴驱动的游戏事件。Sequencer扩展允许开发者通过 C++ 注册自定义的 Track（轨道）、Section（片段）和 Channel（通道），从而让 Sequencer 能够驱动任意游戏逻辑——不仅限于引擎内置的变换、骨骼动画或音频播放。

这套扩展机制在 Unreal Engine 4.15 版本前后逐步成熟，官方将 Sequencer 的内部架构向第三方开放，允许插件和项目以与原生 Track（如 `UMovieSceneTransformTrack`）完全相同的方式集成进编辑器。其核心价值在于：当项目需要在过场动画中精确控制自定义属性（例如技能冷却、UI 渐变、游戏流程触发）时，无需编写独立的时间轴系统，可直接复用 Sequencer 的关键帧编辑、混合、循环和预览基础设施。

对非线性叙事游戏、开放世界剧情演出或需要设计师可视化调试的项目而言，Sequencer扩展能显著降低技术美术与程序员之间的协作摩擦，所有可交互的参数都可在 Sequencer 编辑器内直接打关键帧。

---

## 核心原理

### Track、Section 与 Channel 的层级关系

三者构成严格的包含层次：一个 `UMovieSceneTrack` 可以包含多个 `UMovieSceneSection`，每个 Section 再包含若干 `FMovieSceneChannel`。Track 决定"这条轨道控制什么"，Section 表示时间轴上的一段区间（带起止时间），Channel 存储实际的关键帧数据曲线。

自定义时，至少需要同时实现三个 C++ 类型：继承 `UMovieSceneTrack` 的 Track 类、继承 `UMovieSceneSection` 的 Section 类，以及一个实现 `TMovieSceneChannelTraits` 特化的 Channel 结构体。Channel 通常直接复用引擎提供的 `FMovieSceneFloatChannel`、`FMovieSceneBoolChannel` 或 `FMovieSceneByteChannel`，也可从零实现满足 `FMovieSceneChannel` 接口要求的自定义类型。

### 求值管线与 EvalTemplate

Sequencer 在运行时通过 `FMovieSceneEvalTemplate` 执行轨道求值。每个自定义 Track 需要提供一个 `UMovieSceneSection::GenerateTemplate()` 的重写，返回对应的 `FMovieSceneEvalTemplate` 子类实例。该模板的 `Evaluate()` 方法在每一帧被调用，接收插值后的通道值并写入 `FMovieSceneExecutionTokens`，最终由 Token 在 Game Thread 上统一应用到目标对象。

这套两阶段设计（生成模板 → 求值 Token）允许 Sequencer 在编辑器预览和运行时使用同一套求值逻辑，同时保持线程安全。关键公式为：

```
ChannelValue(t) = Interpolate(KeyA, KeyB, (t - tA) / (tB - tA))
```

其中插值方式由每个关键帧的 `ERichCurveInterpMode` 枚举控制（`RCIM_Cubic`、`RCIM_Linear`、`RCIM_Constant`）。

### 编辑器侧的 TrackEditor 注册

运行时 Track 类需要配套一个仅存在于编辑器模块中的 `ISequencerTrackEditor` 子类，负责处理轨道在 Sequencer UI 中的外观、右键菜单和关键帧拖拽行为。注册语句写在编辑器模块的 `StartupModule()` 中：

```cpp
ISequencerModule& SequencerModule = FModuleManager::LoadModuleChecked<ISequencerModule>("Sequencer");
TrackEditorHandle = SequencerModule.RegisterTrackEditor(
    FOnCreateTrackEditor::CreateStatic(&FMyCustomTrackEditor::CreateTrackEditor)
);
```

在 `ShutdownModule()` 中必须调用 `SequencerModule.UnRegisterTrackEditor(TrackEditorHandle)` 释放句柄，否则引擎关闭时会触发断言。

---

## 实际应用

**自定义浮点属性动画**：假设项目中存在 `ASpellCaster` 角色，其 `ManaRegen` 属性需要在过场中随时间曲线变化。创建 `UManaRegenTrack`（继承 `UMovieSceneTrack`）和 `UManaRegenSection`（包含一个 `FMovieSceneFloatChannel ManaRegenChannel`），在 EvalTemplate 的 `Evaluate()` 内将求值结果调用 `SpellCaster->SetManaRegen(Value)` 即可让设计师直接在 Sequencer 中打曲线关键帧。

**事件触发式 Channel**：使用 `FMovieSceneBoolChannel` 搭配 Section 的 `Evaluate()` 检测从 `false` 到 `true` 的边沿跳变，可实现精确帧对齐的游戏事件触发，误差在 Sequencer 的子帧精度（默认 `EMovieScenePlayerStatus` 以 `1/DisplayRate` 为最小步长，通常为 1/24 秒或 1/30 秒）范围内。

**多 Channel 混合**：一个 `UColorGradingSection` 可在内部持有四个 `FMovieSceneFloatChannel`（分别对应 R、G、B、Intensity），在 TrackEditor 中为每条通道绘制不同颜色的曲线，让美术人员直观调整。

---

## 常见误区

**误区一：将 TrackEditor 代码放入运行时模块**
`ISequencerTrackEditor` 及所有 Sequencer 编辑器 API 只存在于 `SequencerModule`（编辑器模块），若在运行时模块（`Runtime` 或 `Developer` 类型）中引用，打包时会因模块不存在而链接失败。正确做法是在 `.uproject` 或插件的 `Build.cs` 中将 Sequencer 依赖加在 `Editor` 条件块内，并将 TrackEditor 类隔离在独立的编辑器模块中。

**误区二：忘记实现 `GetTrackName()` 和 `SupportsType()` 导致轨道无法出现在添加菜单**
`UMovieSceneTrack` 要求重写 `SupportsType(TSubclassOf<UMovieSceneSection> SectionClass)` 返回 `true` 才能被 Sequencer 识别为可添加的轨道类型；`FMyCustomTrackEditor::SupportsSequence()` 也必须明确返回支持的 Sequence 类型，否则右键菜单中始终不显示该轨道选项，初学者常误以为注册失败。

**误区三：Channel 数据不声明 `UPROPERTY` 导致序列化丢失**
`FMovieSceneFloatChannel` 等 Channel 结构体必须在其所属的 `UMovieSceneSection` 子类中以 `UPROPERTY()` 标记，且需通过 `FMovieSceneChannelProxyData` 正确注册到 Channel Proxy。若仅作为普通成员变量存储，保存关卡序列并重载后所有关键帧数据将全部丢失。

---

## 知识关联

**前置知识**：编辑器扩展概述中的模块系统（`IModuleInterface`、`StartupModule/ShutdownModule` 生命周期）和 Slate UI 框架是实现 TrackEditor 的直接基础；理解 `UObject` 的序列化机制是避免 Channel 数据丢失问题的必要条件。

**横向关联**：自定义 Sequencer Track 与蓝图可调用的 `Timeline` 节点解决同类问题，但 Sequencer Track 支持编辑器内非破坏性预览和多镜头混合，适合演出级精度需求；而 `FTimeline` 更轻量，适合纯运行时逻辑。自定义 Track 还可与 **Sequencer 的 Spawnables** 机制结合，在特定 Section 区间内动态生成并销毁被控制的 Actor。

**深化方向**：在掌握基础 Track/Section/Channel 实现后，可进一步研究 `FMovieSceneBlendingAccumulator` 实现多轨道混合权重叠加，以及 `IMovieScenePlayer` 接口以在自定义播放器（非 `ALevelSequenceActor`）中驱动序列求值。