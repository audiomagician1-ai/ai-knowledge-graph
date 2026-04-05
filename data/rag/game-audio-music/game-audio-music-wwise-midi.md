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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# Wwise MIDI

## 概述

Wwise MIDI 是 Audiokinetic Wwise 引擎中专门处理 MIDI 消息驱动的交互式音乐播放子系统。它允许游戏逻辑通过发送标准 MIDI 1.0 规范定义的消息（音符开/关 Note On/Off、控制器变化 CC、音高弯曲 Pitch Bend、通道压力 Aftertouch 等）来实时控制 Wwise 内部合成器或触发采样播放，从而在不预先录制完整音频的前提下动态生成音乐内容。

该功能自 **Wwise 2015.1** 版本起趋于成熟，并在 **Wwise 2019.2** 引入 Wwise Spatial Audio 扩展后，MIDI 驱动的程序化音乐可进一步与空间化混音流程结合（参见 Audiokinetic 官方文档 *Wwise SDK 2023.1 — MIDI API Reference*）。其核心价值在于：同一套 MIDI 序列数据可以驱动截然不同的音色方案，允许在运行时通过切换 Source Plugin 改变乐器，而无需重新导出大量 PCM 音频文件。

在架构层面，Wwise MIDI 分为两个独立方向：其一是作为 MIDI 消息的**接收端**（Input），游戏代码通过 `PostMIDIOnEvent()` 将 MIDI 数据推送给 Wwise Sound/Music 对象；其二是作为 MIDI 消息的**发送端**（Output），通过 Music Callbacks 机制将 Wwise 内部 MIDI Track 的播放数据反向传递给外部软件合成器或游戏逻辑。两个方向在 Wwise Authoring 工具配置和 API 调用上差异显著，本文将分别展开。

---

## 核心原理

### MIDI 消息在 Wwise 引擎中的传递路径

游戏代码调用的入口函数为：

```cpp
// 构造 MIDI 消息数组
AkMIDIPost midiPosts[2];

// 音符开启：通道0，音符60（中央C），力度100
midiPosts[0].byType      = AK_MIDI_EVENT_TYPE_NOTE_ON;  // 0x90
midiPosts[0].byChan      = 0;
midiPosts[0].byOnOffNote = 60;   // Middle C (MIDI note 60)
midiPosts[0].byVelocity  = 100;
midiPosts[0].uOffset     = 0;    // 相对于当前帧，以采样为单位的偏移量

// 音符关闭：500ms 后
midiPosts[1].byType      = AK_MIDI_EVENT_TYPE_NOTE_OFF; // 0x80
midiPosts[1].byChan      = 0;
midiPosts[1].byOnOffNote = 60;
midiPosts[1].byVelocity  = 0;
midiPosts[1].uOffset     = 22050; // 48000Hz 采样率下约 500ms

AK::SoundEngine::PostMIDIOnEvent(
    AK::EVENTS::PLAY_SYNTH_MELODY,  // Event ID
    gameObjectID,                    // 关联的 Game Object
    midiPosts,
    2                                // 消息数量
);
```

消息进入引擎后，Wwise 将其分发给与该 Event 绑定的所有启用了 **"MIDI Playback: Use note tracking"** 的 Sound 对象。`uOffset` 字段支持以**采样点（sample）**为单位的精确定时，在 48000 Hz 采样率下，1个采样点的时间精度约为 **20.8 微秒**，远优于基于帧率的游戏逻辑调度，适合需要严格节拍对齐的音乐场景。

### 能够响应 MIDI 的 Wwise 对象类型

并非所有 Wwise 对象都能消费 MIDI 数据，仅以下三类对象支持：

1. **Sound SFX 对象**：勾选 MIDI note tracking 后，接收到的 MIDI 音符编号将直接映射为音高偏移。音高偏移计算公式为：

$$\Delta_{semitone} = N_{received} - N_{base}$$

其中 $N_{received}$ 是接收到的 MIDI 音符编号（0–127），$N_{base}$ 是在 Authoring 工具中设定的基准音（默认为 60，即中央 C）。例如，若游戏代码发送音符 64（E4），而基准音为 60，则 Sound 对象将被升高 **+4 个半音**播放。

2. **Music Track 对象**：可在其 Sequence 或 Random 容器中内嵌 MIDI 剪辑（.mid 文件），与音频剪辑混合排布在同一时间轴上，MIDI 剪辑中的音符事件将驱动挂载于同一 Music Track 的 Source Plugin。

3. **Source Plugin 对象**（如 Wwise 自带的 **Wwise Synth One** 或第三方 **Tonal Freeze**）：这类插件本身即为软件合成器，可直接消费 MIDI 数据产生音频，是实现完全程序化生成音乐的核心组件。

### MIDI 通道与 Audio Bus 路由的解耦关系

Wwise 的 MIDI 通道（0–15）与 Audio Bus 的声道（Mono/Stereo/5.1）在概念上完全无关。单个 Wwise Event 可同时接收全部 16 个 MIDI 通道的消息，每个通道对应的 Sound 对象可路由至独立的 Audio Bus。例如：

- 通道 **9**（General MIDI 打击乐专用通道）→ 鼓组 Sound → **Dry Bus**（无混响）
- 通道 **0** 旋律线 → Synth One Plugin → **Wet Bus**（带 Convolution Reverb）
- 通道 **1** 贝斯线 → Sampler Sound → **Sub Bus**（低频增强）

这三路信号在 Wwise Mixer 内部完成分离，Unity 侧的 C# 脚本**无需**对音频数据做任何处理，仅需正确填写 `byChan` 字段即可。

---

## 关键 API 与配置参数

### PostMIDIOnEvent 与 StopMIDIOnEvent 的配对使用

`AK::SoundEngine::PostMIDIOnEvent()` 将 MIDI 消息推入引擎的实时处理队列，但若游戏逻辑在音符持续期间需要中止播放（如玩家死亡打断音乐），必须显式调用：

```cpp
AK::SoundEngine::StopMIDIOnEvent(
    AK::EVENTS::PLAY_SYNTH_MELODY,
    gameObjectID
);
```

若仅调用通用的 `AK::SoundEngine::StopAll()`，**只会停止音频输出，不会发送隐式 Note Off**，可能导致 Synth One 等有状态合成器出现音符"卡住"（stuck note）现象——这是集成阶段最高频的运行时 bug 之一。

### MIDI Tempo 与 Wwise Music System 的节拍同步

当 MIDI 剪辑嵌入 Music Track 时，Wwise 内部维护一个以 **PPQ（Pulses Per Quarter Note）** 为单位的时间轴，默认分辨率为 **480 PPQ**。若外部 MIDI 序列的 Tempo 为 **120 BPM**，则每个 PPQ 对应的实际时间为：

$$t_{PPQ} = \frac{60}{BPM \times PPQ} = \frac{60}{120 \times 480} \approx 1.042 \text{ ms}$$

Wwise 会将此 Tempo 信息存入 Music Segment 的元数据，供 Music Callbacks 系统向外暴露节拍事件（Beat、Bar、Grid 三个粒度），从而使 Unity 的游戏逻辑可在严格节拍点执行操作，如在第 3 小节第 1 拍切换战斗状态。

---

## 在 Unity-Wwise 集成中的实际应用

### 通过 Wwise Unity Integration 发送 MIDI

在已完成 Wwise-Unity 集成（即安装了 Wwise Integration Package）的项目中，C# 侧封装了与 C++ API 等价的接口。发送一个持续四分音符长度（120BPM 下 500ms）的 MIDI 音符示例如下：

```csharp
using UnityEngine;

public class MidiMelodyTrigger : MonoBehaviour
{
    public AK.Wwise.Event synthEvent;

    void TriggerNote(int midiNote, int velocity, int durationMs)
    {
        AkMIDIPost noteOn = new AkMIDIPost();
        noteOn.byType      = AkMIDIEventTypes.NOTE_ON;
        noteOn.byChan      = 0;
        noteOn.byOnOffNote = (byte)midiNote;
        noteOn.byVelocity  = (byte)velocity;
        noteOn.uOffset     = 0;

        AkMIDIPost noteOff = new AkMIDIPost();
        noteOff.byType      = AkMIDIEventTypes.NOTE_OFF;
        noteOff.byChan      = 0;
        noteOff.byOnOffNote = (byte)midiNote;
        noteOff.byVelocity  = 0;
        // 在 48000Hz 下，durationMs 毫秒对应的采样点数
        noteOff.uOffset     = (uint)(48000 * durationMs / 1000);

        AkMIDIPostArray posts = new AkMIDIPostArray(2);
        posts[0] = noteOn;
        posts[1] = noteOff;

        synthEvent.PostMIDI(gameObject, posts);
    }

    void Start()
    {
        // 触发中央C，力度90，持续500ms
        TriggerNote(60, 90, 500);
    }
}
```

### 案例：程序化生成战斗音乐和声

在某 RPG 战斗系统中，设计师将 Wwise Synth One 配置为弦乐 Pad 音色，并预先在 Wwise Authoring 中设置 7 个 Sound 对象分别映射至自然小调音阶的各级音。当战斗难度评分（0–100）超过 **70** 时，Unity 脚本将实时发送 Am 和弦（音符 57/60/64）的 Note On 消息，并将 MIDI CC#7（主音量控制器，0–127）值从 **40 提升至 110**，使弦乐 Pad 在保持和声不断的同时动态增强紧张感，整个过程不涉及任何音频文件的加载与解码，内存开销可忽略不计。

---

## 常见误区

### 误区一：认为 MIDI 通道 10 在 Wwise 中自动对应打击乐

在 General MIDI 标准（由 MIDI Manufacturers Association 于 1991 年制定）中，通道 10（程序编号，对应 `byChan = 9`）约定用于打击乐。但 Wwise **不会**自动对通道 9 做任何特殊处理——打击乐逻辑需要设计师在 Authoring 工具中手动将通道 9 的 Sound 对象配置为使用 **note-to-asset 映射表**，将不同音符编号（如 36=BassDrum、38=Snare、42=HiHat）映射至对应的采样文件。若忽略此配置，通道 9 的行为与其他通道完全相同，会对同一音频文件施加音高偏移而非触发不同采样。

### 误区二：混淆 MIDI Output（发送端）与 MIDI Input（接收端）的配置流程

**MIDI Input** 的配置路径：Sound 属性面板 → MIDI 标签页 → 勾选"Use note tracking"，并在 Wwise 工程的 Project Settings 中无需任何额外设置。

**MIDI Output** 的配置路径：需要在 Music Track 上启用"MIDI Metronome"或通过 `AK_MusicSyncMIDI` 类型的 Music Callback 回调，在 Unity 侧注册 `AkCallbackType.AK_MusicSyncMIDI` 才能接收 MIDI 事件流。两套流程完全独立，在 Authoring 工具中对应不同的属性面板页，将两者混淆会导致调试时耗费大量时间却找不到数据流向。

### 误区三：忽略采样率对 uOffset 计算的影响

`uOffset` 字段以**目标平台的实际音频采样率**为单位，而非固定的 48000 Hz。若项目在移动平台使用 **44100 Hz**，则 500ms 对应 `44100 × 0.5 = 22050` 个采样点；若 PC 平台使用 **48000 Hz**，则为 `48000 × 0.5 = 24000`。将平台采样率硬编码为 48000 是常见的跨平台 bug 根源，正确做法是在运行时调用 `AK::SoundEngine::GetAudioSettings()` 获取 `uNumSamplesPerFrame` 与实际采样率后再行换算。

---

## 知识关联

### 与 Music Callback 系统的衔接

Wwise MIDI 的