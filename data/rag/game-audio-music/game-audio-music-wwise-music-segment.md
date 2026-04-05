---
id: "game-audio-music-wwise-music-segment"
concept: "Music Segment"
domain: "game-audio-music"
subdomain: "wwise-music"
subdomain_name: "Wwise音乐系统"
difficulty: 2
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 83.0
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



# Music Segment（音乐片段）

## 概述

Music Segment 是 Wwise 互动音乐系统中承载实际音频内容的基本结构单元。它将一段音乐素材（WAV、OGG 或 Opus 等格式的音频文件）包裹起来，并附加 BPM、拍号、Entry/Exit Cue 等音乐时序元数据，使 Wwise 引擎能够以"懂音乐"的方式管理和播放该素材。与普通的 Sound SFX 对象相比，Music Segment 内部维护一条独立的音乐时间线，引擎在运行时以 BPM 和拍号为基准对齐、切换、循环音频，而不是依赖毫秒级偏移量进行盲目拼接。

Music Segment 作为独立对象类型随 Wwise 2009.1 对 Interactive Music Hierarchy 的正式引入而出现（Audiokinetic 官方文档 *Wwise Help: Music Segment*, 2023）。此后历次版本中，Audiokinetic 持续为其增加了 Custom Cue 编辑、Pre-Entry/Post-Exit 缓冲区、Stinger 触发点等功能。无论是 Music Playlist Container 的顺序播放还是 Music Switch Container 的实时切换，最终执行层都是若干个 Music Segment 的实际播放——这使得掌握 Music Segment 的属性设置成为所有 Wwise 互动音乐工作流的必要前提。

---

## 核心原理

### 音乐时间线与 BPM / 拍号的精确含义

每个 Music Segment 拥有独立的 **Tempo（BPM）** 和 **Time Signature（拍号）** 字段。当你在属性面板中填入 BPM = 120、拍号 = 4/4 后，Wwise 会自动计算每个四分音符时值，进而得出每小节的物理时长：

$$T_{\text{bar}} = \frac{60{,}000 \text{ ms}}{\text{BPM}} \times \text{beats per bar} = \frac{60{,}000}{120} \times 4 = 2{,}000 \text{ ms}$$

这张以 2000 ms 为单位的小节网格，直接决定了上层容器在"第 N 小节第 M 拍"处进行同步切换的精度。若将 BPM 误填为 60，同一段 120 BPM 的音频将被 Wwise 按 4000 ms/bar 对齐，导致切换点与音乐节拍偏移整整两倍，是实际项目中最常见的设置错误之一。

拍号分子影响每小节拍数，分母影响拍值单位。3/8 拍 BPM = 120 时，每小节时长为 $\frac{60{,}000}{120} \times 3 \times \frac{1}{2} \times 2 = 1{,}500 \text{ ms}$（分母 8 代表八分音符为一拍，相当于四分音符时值的一半）。Wwise 内部时间单位为 **音乐网格刻度（Music Grid Tick）**，1 tick = 1/48 拍，这使得 Wwise 在理论上能以约 10.4 ms（120 BPM 下）的粒度定位任意音乐事件。

### Entry Cue、Exit Cue 与 Pre-Entry / Post-Exit 缓冲区

Music Segment 时间线上至少存在两个不可删除的标记：**Entry Cue** 和 **Exit Cue**。

- **Entry Cue**：默认位于时间线第 0 拍（Position = 0 ms），标记外部跳入该片段时的"落脚点"。将 Entry Cue 后移到第 2 拍，则上层容器在切入时会从第 2 拍位置开始同步，第 0～2 拍之间的音频将在 **Pre-Entry** 区域内提前静默播放（可配置是否可听），用于音频硬件缓冲预热或引入前奏填充。
- **Exit Cue**：默认位于音频文件末尾，标记允许从该片段跳出的时刻。将 Exit Cue 提前到第 15 小节第 1 拍（共 16 小节的素材），则第 15 小节至结尾成为 **Post-Exit** 区域，上层容器在这段时间内已切换至下一 Segment，而当前 Segment 继续播放残响尾音，这是实现无缝淡变过渡（Crossfade Transition）的常见手段。

**Custom Cue** 可由音频设计师自定义名称（如 `"Drop"` 或 `"Verse_End"`），并在 Transition 规则或 Stinger 设置中被引用为触发点，从而在片段播放中途精确插入音效层或触发游戏逻辑回调。

### Music Track 的容纳结构与分轨工作流

Music Segment 内部可容纳一条或多条 **Music Track**，每条 Track 包含一个或多个 **Clip**（音频片段的时间轴实例）。其层级关系如下：

```
Music Segment
 ├── Music Track（鼓组）
 │    └── Clip: drums_loop.wav  [0 ms → 8000 ms]
 ├── Music Track（贝斯）
 │    └── Clip: bass_loop.wav   [0 ms → 8000 ms]
 └── Music Track（旋律）
      └── Clip: melody_loop.wav [0 ms → 8000 ms]
```

这一结构直接对应 DAW 中的"分轨导出"工作流：将鼓、贝斯、旋律分别导出为同起点、同时长的独立 WAV 文件，在 Wwise 中分别关联到对应的 Music Track Clip 上，即可通过对各 Track 绑定 RTPC 音量曲线来实现动态分层混音（Vertical Remixing）。

Music Track 自身还具有 **Track Type** 属性，可选：
- **Normal**：单层静态播放；
- **Random Step / Sequence Step**：多 Clip 随机或顺序轮换，常用于随机化副歌变奏；
- **Switch**：由 Game Parameter 或 State 实时切换 Clip，常见于根据玩家状态切换旋律层。

---

## 关键属性与参数速查

| 属性名称 | 位置 | 典型取值 | 作用说明 |
|---|---|---|---|
| Tempo (BPM) | Segment 属性面板 | 60～200 | 决定小节网格时长 |
| Time Signature | Segment 属性面板 | 4/4、3/4、7/8 | 决定每小节拍数与拍值 |
| Entry Cue Position | 时间线标记 | 0 ms（默认） | 跳入落脚点 |
| Exit Cue Position | 时间线标记 | 音频末尾（默认） | 允许跳出的最早时刻 |
| Loop Count | Segment 属性 | 0 = 无限循环 | 控制 Segment 自身循环次数 |
| Look-ahead Time | 全局 Music Bus 设置 | 默认 500 ms | 引擎预计算切换点的提前量 |

其中 **Look-ahead Time** 尤为关键：Wwise 需要在实际切换发生前至少 500 ms 完成下一 Segment 的解码预热（Pre-fetch）。若游戏逻辑的状态切换延迟超过这一窗口，切换将被顺延至下一个合法 Sync 点，造成可感知的响应滞后。

---

## 实际应用案例

**案例：RPG 游戏战斗音乐的无缝切换**

某 RPG 游戏的探索场景使用一段 8 小节、BPM = 98、4/4 拍的环境音乐循环（`exploration_loop.wav`）。当玩家触发战斗时，需要在当前小节末尾无缝切换至战斗主题（`battle_intro.wav` + `battle_loop.wav`）。

配置方式如下：
1. 为 `exploration_loop.wav` 创建 Music Segment，BPM = 98，Exit Cue 置于第 8 小节第 1 拍（即循环末尾）；
2. 为 `battle_intro.wav` 创建 Music Segment，BPM = 98（与探索音乐同 BPM 保证节拍对齐），Entry Cue 位于第 1 拍；
3. 在 Music Switch Container 中，将探索→战斗的 Transition Rule 设置为 **Sync to: Exit Cue of source**，**Destination: Entry Cue**，Fade-out 时长 = 500 ms，Fade-in 时长 = 0 ms；
4. 结果：玩家触发战斗后，探索音乐最多再播放不足 8 小节（~4.9 秒，$8 \times 60000/98 \approx 4898 \text{ ms}$）便会在自然的节拍边界上淡出，战斗 Intro 无缝衔接。

这一配置完全依赖 Music Segment 的 BPM、Exit Cue 和时间线网格，普通 Sound SFX 对象无法实现等效效果。

---

## 常见误区

**误区 1：BPM 与实际音频不匹配**
将音频的 DAW 工程 BPM 填写为 Wwise Segment BPM 时，若 DAW 工程使用了 Tempo Map（多段变速），则 Wwise 中只能填写单一 BPM。此时应将变速区段分割为多个 Music Segment，每段填写对应的局部 BPM，而不是用一个 Segment 试图涵盖整段变速音频。

**误区 2：Loop Count = 1 与 Loop Count = 0 的混淆**
Loop Count = 1 表示"播放 1 次后停止"（即不循环），Loop Count = 0 表示"无限循环"。项目中曾有因将循环背景乐的 Loop Count 误设为 1 而导致音乐在第一次播放结束后静音的 bug，排查成本极高。

**误区 3：忽略 Pre-Entry 区域的可听性**
当 Entry Cue 后移时，Pre-Entry 区域内的音频默认设置为**可听（Audible = true）**。若 Entry Cue 被设置在第 2 小节，而第 1 小节是一段强力鼓击引入，玩家在切入该 Segment 时会听到这段引入被"提前"播放，从而产生混乱。应明确将 Pre-Entry 的音量包络设为静音（Volume = -96 dB），或选择将 Entry Cue 保留在第 0 拍。

**误区 4：Music Segment 直接挂载到 Actor-Mixer**
Music Segment 只能作为 Music Playlist Container 或 Music Switch Container 的子对象存在，不能像 Sound SFX 一样直接挂载到 Actor-Mixer Hierarchy 下并用 Post Event 播放。尝试这样操作时 Wwise 不会报错，但该 Segment 将永远不会被正确触发。

---

## 知识关联

- **前置概念——分轨导出**：Music Segment 的多 Track 结构要求音频素材以同起点、同时长的分轨形式提供。在 Logic Pro、Pro Tools 或 Reaper 中导出时须勾选"Export all tracks individually from the start of the timeline"，确保所有 WAV 文件的第 0 帧对齐，避免 Clip 在 Wwise 时间线上出现静默偏移。

- **后续概念——Music Playlist Container**：Music Playlist Container 将多个 Music Segment 按顺序或随机排列，其"连续播放"逻辑依赖各 Segment 的 Exit Cue 位置和相邻 Segment 之间的 Transition 规则。理解单个 Music Segment 的时间线属性，是正确配置 Playlist 过渡的必要基础（Audiokinetic, *Wwise SDK Documentation: Music Playlist Container*, 2023）。

- **Stinger 系统**：Stinger 是一种在任意 Music Segment 播放中途叠加的短促音效层，其触发时机以 Music Segment 时间线上的 Custom Cue 为锚点。例如，在 `Verse_End` Custom Cue 处触发一段 2 拍的过门 Stinger，可在不中断背景循环的前提下强化音乐层次变化，是互动音乐设计中常见的纵向分层手段。

- **RTPC 与动态混音**：各 Music Track 的音量可绑定到 RTPC（Real-Time Parameter Control），例如将"玩家血量"RTPC 映射到"旋律层音量曲线"，使旋律随玩家状态减弱消退。这一动态混音技术的物理承载层正是 Music Segment 内部的多条 Music Track，脱离 Segment 结构则无法实现逐 Track 的独立控制。

---

> **思考问题**：若一首歌曲存在 4 小节的拍号从 4/4 变为 7/8 的局部变拍段落，而 Wwise Music Segment 只允许填写