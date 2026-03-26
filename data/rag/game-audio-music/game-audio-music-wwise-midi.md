---
id: "game-audio-music-wwise-midi"
concept: "Wwise MIDI"
domain: "game-audio-music"
subdomain: "wwise-music"
subdomain_name: "Wwise音乐系统"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Wwise MIDI

## 概述

Wwise MIDI 是 Audiokinetic Wwise 引擎中用于驱动交互式音乐播放的 MIDI 消息处理系统。它允许游戏逻辑通过发送标准 MIDI 消息（音符开/关、控制器变化、音高弯曲等）来实时控制 Wwise 内部合成器或触发采样播放，从而实现无需预先录制音频即可动态生成音乐内容的能力。

这一功能自 Wwise 2015.1 版本起逐渐成熟，主要面向需要程序化生成音乐或将 DAW 工作流直接移植到游戏引擎的音频设计师。其核心价值在于：同一段 MIDI 数据可以驱动截然不同的音色方案，允许在运行时切换乐器，而无需重新导出大量音频文件。

Wwise MIDI 在技术上分为两个独立方向：一是作为 MIDI 事件的**接收端**，由 Wwise Music 对象消费 MIDI 数据；二是作为 MIDI 消息的**发送端**，通过 Music Callbacks 将 Wwise 内部 MIDI 节点的播放数据传递给外部软件合成器。两个方向在 Wwise 项目配置和 API 调用上差异显著，混淆两者是初学者最常见的错误。

## 核心原理

### MIDI 消息的传递路径

在 Wwise 中，MIDI 消息的起点通常是游戏代码调用 `AK::SoundEngine::PostMIDIOnEvent()` 函数。该函数接受一个 `AkMIDIPost` 结构体数组，每条记录包含 `byType`（消息类型，如 `AK_MIDI_EVENT_TYPE_NOTE_ON = 0x90`）、`byChan`（0-15 的 MIDI 通道）、`byOnOffNote`（音符编号，中央 C 为 60）以及 `byVelocity`（力度 0-127）等字段。消息被投递到与指定 Event 绑定的 Wwise Sound 对象上，该对象必须在 Wwise 设计工具中勾选 **"MIDI Playback: Use note tracking"** 选项才能响应。

### Wwise 中 MIDI 驱动的对象类型

并非所有 Wwise 对象都能消费 MIDI 数据。能够响应 MIDI 的对象仅限于：**Sound SFX** 对象（启用 MIDI note tracking 后可根据音符编号改变音高）、**Music Track** 对象（可在 Sequence 或 Random 容器中直接内嵌 MIDI 剪辑），以及连接了第三方 VST 插件（如 Wwise Synth One 或 Tonal Freeze）的 **Source Plugin** 对象。每类对象在 Authoring 工具的 MIDI 标签页中有各自独立的音调映射配置，其中 Sound SFX 的音高偏移公式为：`semitone_shift = received_MIDI_note - 60`（以中央 C 为基准音）。

### MIDI 通道与 Wwise Bus 路由的关系

Wwise 的 MIDI 通道（0-15）不等同于 Wwise 的 Audio Bus 通道。一个 Wwise Event 可以同时接收多个 MIDI 通道的消息，而每个通道对应的 Sound 对象可以路由到完全不同的 Audio Bus 上。这意味着可以用单一 `PostMIDIOnEvent` 调用同时驱动鼓组（通道 9）和旋律线（通道 0），鼓组走 Dry Bus，旋律线走带混响的 Wet Bus，在 Wwise 内部完成混音分离，无需游戏代码进行任何额外分配操作。

### MIDI Tempo 与 Wwise Music System 的同步

当 MIDI 剪辑被嵌入 **Music Segment** 时，Wwise 会以 Music Segment 自身的 Tempo（单位 BPM）为主时钟驱动 MIDI 回放，忽略 MIDI 文件本身的 header tempo 信息。如果需要将 MIDI 剪辑的速度从原始的 120 BPM 改变为游戏中动态设置的 95 BPM，必须在 Wwise Authoring 的 Music Track Editor 中将剪辑的 **"Stretch Duration"** 选项关联到 Music Segment 的 Tempo 参数，否则 MIDI 音符时间轴将发生偏移，导致与其他音频层不同步。

## 实际应用

**程序化弦乐伴奏系统**：在角色扮演游戏的战斗场景中，游戏代码可根据玩家血量实时计算和弦类型，然后调用 `PostMIDIOnEvent()` 发送对应的音符组合（如紧张时发送 Cm 小调和弦：音符 60、63、67），驱动 Wwise 中加载了弦乐采样的 Sound SFX 对象。血量恢复时切换为 C 大调（60、64、67），整个切换无需加载新的音频文件，内存占用仅为一套弦乐采样的大小。

**外部 MIDI 控制器的实时演奏**：通过 Unity 的 `InputSystem` 捕获物理 MIDI 键盘的输入，将其转化为 `AkMIDIPost` 结构体后传入 Wwise，玩家可以在游戏内实时"演奏"绑定了合成器插件的 Wwise Sound 对象。这一流程中需要注意 Unity 与 Wwise 的线程安全问题：`PostMIDIOnEvent` 必须在 Wwise 的音频线程或通过 `AkCallbackManager` 的主线程代理调用，在 `Update()` 中直接调用可能导致音符卡顿。

**自适应音乐层叠**：将一首多轨乐曲的各声部分别存为独立的 MIDI 剪辑，放置在同一个 Music Segment 的不同 Music Track 上，再为每条 Track 设置不同的 MIDI 通道（0=旋律，1=低音，2=打击乐）。游戏通过 RTPC（Real-Time Parameter Control）参数控制哪些通道静音，可在不重新触发 Event 的情况下动态增减音乐层次，比传统的多段音频切换响应延迟低约 20ms。

## 常见误区

**误区一：认为 Wwise MIDI 可以直接替代 General MIDI 音源**。Wwise 本身不内置 GM 音色库，`PostMIDIOnEvent` 发出的 Program Change 消息（0xC0）在没有外部插件的情况下会被静默忽略。要获得钢琴、铜管等标准音色，必须在 Wwise 项目中安装并配置支持 Program Change 响应的 Source Plugin（如 McDSP 或 Audiokinetic 官方示例中使用的 Wwise Synth One）。

**误区二：混淆 MIDI note 编号与 Wwise 音调参数的单位**。`PostMIDIOnEvent` 中的音符编号是 0-127 的整数，而 Wwise 中 Pitch 参数的单位是"百分音（cents）"，100 cents = 1 个半音。当通过 MIDI note tracking 自动计算音高偏移时，Wwise 内部会将音符差值转换为 cents（公式：`Δcents = (note - 60) × 100`），但如果同时叠加了手动设置的 Pitch RTPC，两者会相加，容易造成音高偏移双倍计算的问题。

**误区三：认为 Music Segment 内嵌的 MIDI 剪辑与 PostMIDIOnEvent 是同一套机制**。前者是 Wwise Authoring 工具中预编排的静态 MIDI 数据，随 Music Segment 自动播放；后者是运行时由游戏代码动态注入的 MIDI 消息流，两套机制的优先级和调度方式完全独立，无法互相覆盖或取消对方已发出的 Note On 消息。

## 知识关联

学习 Wwise MIDI 需要先掌握 **Wwise-Unity 集成**的 API 调用规范，具体是熟悉 `AkSoundEngine` 静态类的事件投递模式——`PostMIDIOnEvent` 与 `PostEvent` 共享同一套 GameObject 绑定逻辑，未挂载 `AkGameObj` 组件的对象无法接收 MIDI 消息，这一点在从 Unity 侧调试时尤为关键。

完成 Wwise MIDI 的学习后，自然过渡到 **Music Callback** 机制，后者允许游戏代码在 Wwise MIDI 序列播放的特定节拍（Bar/Beat/Grid）接收回调通知，从而实现游戏视觉效果与 MIDI 驱动的音乐节奏精确对齐。两者组合使用时，常见模式是：Music Callback 告知游戏"当前是第 3 拍"，游戏逻辑据此决定下一个 `PostMIDIOnEvent` 应发送何种和弦，形成一个实时的音乐生成闭环。