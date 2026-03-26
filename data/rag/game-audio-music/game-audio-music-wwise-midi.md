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

Wwise MIDI 是 Audiokinetic Wwise 引擎中用于驱动交互式音乐的 MIDI 协议实现层，允许开发者通过发送 MIDI 事件、音符、控制器信息来实时控制 Wwise 内部的音乐合成器（Synth One 插件）或外部虚拟乐器。与传统的音频文件播放不同，Wwise MIDI 播放的是参数化的音符指令（音高、力度、时长），而非预录制的 PCM 波形，这使得音乐在运行时可以根据游戏状态动态调整旋律、和声与节奏。

Wwise 对 MIDI 的支持从 2015 年的 2015.1 版本正式引入，与 Wwise Interactive Music 系统深度整合。在此之前，Wwise 只能播放静态音频片段，引入 MIDI 后，设计师可以在 Wwise 的 Music Segment 中直接嵌入 MIDI 轨道，并将 MIDI 数据与音频素材同步触发，实现真正意义上的程序化音乐生成。

Wwise MIDI 在游戏音乐领域的价值体现在其极低的内存占用与极高的动态可控性：一段 16 小节的 MIDI 数据通常只需几千字节，而同等时长的高质量 WAV 文件可达数兆字节。对于需要根据战斗强度、玩家位置或情绪状态实时改变音乐织体的 RPG 或开放世界游戏，MIDI 驱动方案具有不可替代的优势。

---

## 核心原理

### MIDI 消息类型与 Wwise 的处理方式

Wwise MIDI 支持三类核心消息：**Note On/Off**（音符开关，包含通道号 0–15、音高 0–127、力度 0–127）、**Control Change（CC）**（控制器编号 0–127，如 CC7 为主音量、CC10 为声像）、以及 **Pitch Bend**（音高弯曲，14位精度，范围 -8192 至 +8191）。这些消息在 Wwise 中既可来自内嵌于 Music Segment 的 MIDI 文件轨道，也可通过 Wwise SDK 的 `PostMIDIOnEvent()` API 在运行时由游戏代码动态发送。

Wwise 将每条 MIDI 通道映射到一个独立的 **MIDI Target**，即一个已挂载了 MIDI-capable 插件的 Sound SFX 对象。当 Note On 消息到达时，Wwise 内部会生成一个对应音高的合成声音实例，该实例的音高偏移量由公式 `Δsemitones = NoteNumber - 69`（以 A4=69 为参考）计算，并以 `Δcents = Δsemitones × 100` 转换后应用于 Synth One 的基频参数。

### Music Segment 中的 MIDI 轨道嵌入

在 Wwise Designer 的 Music Segment Editor 中，MIDI Track 与 Audio Track 并列存在。MIDI Track 直接引用 `.mid` 文件，Wwise 在播放 Segment 时会按节拍精度（tick resolution，默认 480 PPQ）解析 MIDI 事件并驱动挂载的插件。关键设计点在于：MIDI Track 的播放时序受 **Music Sync** 系统约束，保证与其他音频轨道在 Bar/Beat 边界严格对齐，误差通常在 ±1 毫秒以内。

设计师还可以在 MIDI Track 的属性面板中设置 **MIDI Target** 路由——将特定通道的 MIDI 数据路由至不同的 Sound 对象，实现一个 Segment 内多乐器的独立控制。例如，通道 1 路由至弦乐合成器，通道 10 路由至鼓机，通道 3 路由至钢琴 VST。

### 通过 SDK 实时发送 MIDI 事件

Wwise SDK 提供 `AK::SoundEngine::PostMIDIOnEvent()` 函数，其原型需要传入 Event ID、Game Object ID 以及一个 `AkMIDIPost` 结构数组，每个结构体包含 `byType`（消息类型）、`byChan`（通道）、`byOnOffNote`（音高）和 `byVelocity`（力度）四个字段。在 Unity 集成环境下，通过 `AkSoundEngine.PostMIDIOnEvent()` 包装函数调用，可在 C# 脚本中直接根据游戏逻辑（如玩家血量映射为力度值）驱动音乐变化。

实时 MIDI 方案的时序精度受 Wwise 音频线程调度影响，通常延迟为 1–2 个音频缓冲区（约 10–20ms，默认缓冲区 512 samples @ 48kHz）。对于需要严格节奏同步的场景，应结合 **Music Callback** 机制在精确的节拍时间点触发 MIDI Post，而非在 Update() 帧循环中轮询。

---

## 实际应用

**战斗强度自适应旋律**：在一款 ARPG 游戏中，敌人数量从 0 增至 10 时，游戏代码将该数值线性映射为 MIDI 力度值（0→30，10→127），通过 `PostMIDIOnEvent()` 实时更新弦乐 Stab 的演奏力度，营造从平静到激烈的自然渐变，而无需预先制作多版本音频。

**程序化和弦生成**：根据游戏世界的昼夜系统，设计师在 Wwise 外部脚本中维护一张和弦表（如 C 大调音阶的 7 个三和弦），每逢游戏时间推进一小时，脚本遍历和弦音符并发送一组 Note On 消息至 Wwise Piano Sound，构成不同情绪色彩的和声背景。这套方案在《某独立游戏》实际部署时，全部和弦数据仅占用 2KB 运行时内存。

**教程关卡音效反馈**：玩家每成功完成一个操作步骤，系统发送音高依次升高半音的 Note On 消息（C4→D4→E4→...），形成音阶式正向反馈，整个设计不依赖任何预录制音效文件，完全由 Wwise Synth One 实时合成。

---

## 常见误区

**误区一：认为 MIDI Track 会自动选择乐器音色**
Wwise MIDI Track 本身不携带通用 MIDI（GM）的音色库，不像 DAW 软件那样内置 128 种乐器音色。MIDI Track 必须显式绑定一个挂载了 Synth One 或第三方 VST 插件的 Sound 对象作为 MIDI Target，如果忘记设置 MIDI Target，Wwise 会播放 MIDI 数据但完全无声输出，且 Designer 日志不会报错，这是新手最常遇到的静音陷阱。

**误区二：混淆 PostMIDIOnEvent 与普通 PostEvent 的作用域**
`PostMIDIOnEvent()` 发送的 MIDI 消息与 `PostEvent()` 触发的音频事件作用在同一 Game Object 上，但两者的生命周期管理不同：MIDI Note 若只发送 Note On 而不发送对应的 Note Off，合成器将持续发声直到 Game Object 被销毁，导致音符"卡住"。正确做法是在每个 Note On 后设置定时器，或在 Music Segment 结束时通过 `StopMIDI()` 全局清零。

**误区三：假设 MIDI 延迟可以忽略不计**
MIDI 数据体积小并不等于触发延迟为零。经过 Wwise 音频线程排队处理后，`PostMIDIOnEvent()` 的实际发声延迟与普通音频事件相同，约为 10–23ms（取决于缓冲区大小配置），在节奏游戏中若直接在视觉事件帧回调里触发 MIDI，会产生可感知的音画不同步，需预留补偿时间戳（`iOffset` 字段，单位为采样数）。

---

## 知识关联

Wwise MIDI 的使用以 **Wwise-Unity 集成**为前提，开发者需要已掌握在 Unity 场景中挂载 AkGameObj 组件、调用 `AkSoundEngine` 静态方法的基础操作，因为 `PostMIDIOnEvent()` 同样依赖 Game Object 作为声音空间定位和 RTPCs 作用域的锚点。若 Game Object 未正确注册到 Wwise 声音引擎，MIDI 消息会被静默丢弃。

掌握 Wwise MIDI 后，下一个关键主题是 **Music Callback**。Music Callback 机制允许 Wwise 在 Bar、Beat 或自定义 Cue 点触发回调函数，而 MIDI 发送的最佳时机正是在这些回调中执行——两者结合才能构建出节拍精准的程序化音乐系统。没有 Music Callback 提供的精确时间窗口，MIDI 实时发送将无法保证与 Segment 内置轨道的节拍对齐，导致和声或节奏错乱。