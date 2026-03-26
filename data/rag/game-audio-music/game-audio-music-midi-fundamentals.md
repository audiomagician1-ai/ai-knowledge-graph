---
id: "game-audio-music-midi-fundamentals"
concept: "MIDI基础"
domain: "game-audio-music"
subdomain: "daw"
subdomain_name: "编曲软件(DAW)"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# MIDI基础

## 概述

MIDI（Musical Instrument Digital Interface，乐器数字接口）是1983年由Roland、Yamaha、Korg等日本乐器厂商联合制定的通信协议标准，版本号为MIDI 1.0。与音频文件不同，MIDI本质上不存储任何声音波形，而是存储"演奏指令"——记录哪个键在何时被按下、力度有多强、持续多长时间。一个完整的MIDI文件（.mid）即便包含数分钟的复杂编曲，体积也通常不超过100KB，而同等时长的WAV音频文件可能超过50MB。

MIDI协议在游戏音乐历史上扮演了决定性角色。早期游戏主机如SNES（1990年）和PC平台通过MIDI驱动内置的FM合成芯片或采样引擎发声，《最终幻想VI》《塞尔达传说：时之笛》等经典游戏的配乐均以MIDI格式存储。即使在当今使用高质量采样库的现代游戏音乐制作中，DAW内部的编曲层依然基于MIDI，作曲家在FL Studio、Cubase、Reaper等软件中写下的每一个音符，本质上仍是MIDI数据触发虚拟乐器发声。

MIDI对游戏音乐制作者的实际意义在于：它是连接作曲构思与最终音色的"乐谱语言"。掌握MIDI编辑意味着你可以精确控制每个音符的力度（Velocity）、时值、音高，以及通过CC控制器实现弦乐的颤音、管乐的气息感、打击乐的细腻过渡——这些都是让游戏音乐从"机械感"走向"生动感"的关键技术。

---

## 核心原理

### MIDI消息的数据结构

MIDI协议以字节（Byte）为单位传输数据，每条消息通常由1~3个字节组成。最核心的消息类型是**Note On**和**Note Off**：

- **Note On**：3字节 = `[状态字节: 1001nnnn] [音符编号: 0~127] [力度: 0~127]`
- **Note Off**：3字节 = `[状态字节: 1000nnnn] [音符编号: 0~127] [力度: 0~127]`

其中`nnnn`代表MIDI通道号（0~15，对应通道1~16）。MIDI标准规定第10通道（Channel 10）专门分配给打击乐器，这是MIDI 1.0规范中少数被硬性规定的惯例之一。音符编号60对应中央C（C4），每增减1代表半音。因此在DAW的Piano Roll中，你看到的每个方块都对应一条Note On + Note Off消息对。

### Velocity（力度）与表情控制

力度值范围为0~127，直接决定音符的响度和音色特征。在高质量采样库（如Spitfire Audio的弦乐库）中，力度分层（Velocity Layer）通常有4~8层甚至更多：力度1~30触发"柔弱演奏（pp）"采样，力度100~127触发"强奏（ff）"采样，完全不同的录音片段。这意味着在游戏音乐中为弦乐写旋律时，简单地将所有音符力度设为统一数值（如velocity=100）会让音乐听起来机械且不真实。

### CC控制器（Continuous Controller）

CC控制器是MIDI协议中用于发送连续变化参数的消息，格式为：`[0xBn] [控制器编号] [值: 0~127]`，其中`n`为通道号。MIDI 1.0标准定义了128个CC编号（0~127），其中多个有约定俗成的用途：

| CC编号 | 约定功能 | 游戏音乐常用场景 |
|--------|----------|-----------------|
| CC1 | 调制轮（Modulation Wheel） | 控制弦乐颤音深度、管乐气息波动 |
| CC7 | 主音量（Main Volume） | 实时调整乐器整体音量 |
| CC11 | 表情（Expression） | 配合CC7精细控制动态起伏 |
| CC64 | 延音踏板（Sustain Pedal） | 钢琴、合成器的音符延留 |

在游戏音乐制作中，CC11（Expression）与CC7（Volume）的配合使用是专业技巧：CC7设定乐器的基准音量上限，CC11在0~127之间自动化绘制动态曲线，实现从pp渐强至ff的自然过渡。许多游戏配乐师（如Austin Wintory在《风之旅人》的制作过程中）会在DAW的自动化轨道上逐帧绘制CC11曲线以实现弦乐的呼吸感。

### Piano Roll编辑基础

现代DAW中的Piano Roll是MIDI数据的可视化编辑界面。纵轴为音高（对应MIDI音符编号），横轴为时间轴（以小节:拍:格为单位）。量化（Quantize）功能将音符对齐到指定的节拍网格，如1/16音符网格。在游戏音乐的快速动作场景配乐中，常使用1/32甚至1/64的量化精度来安排鼓机滚奏或弦乐快速分解和弦。

---

## 实际应用

**为RPG游戏场景音乐制作弦乐垫音（Pad）**：在DAW中新建MIDI轨道，加载弦乐采样库。在Piano Roll中绘制持续8拍的和弦（如C-E-G三音叠置），将所有音符velocity统一设置为70左右作为基准，然后在自动化轨道中为CC11绘制从值20缓慢上升至100再回落的弧线曲线，即可得到富有呼吸感的弦乐渐强渐弱效果，适合用于RPG地图探索场景的背景音乐。

**游戏战斗音乐的鼓轨编程**：将鼓组MIDI写入第10通道，利用General MIDI（GM）标准中规定的打击乐音符映射（音符36=Bass Drum，音符38=Snare，音符42=Closed Hi-Hat）编写基础节奏型。通过在相邻小节间调整踩镲音符的velocity值（如奇数拍velocity=90，正拍间隙velocity=55），可模拟真实鼓手的力度变化，让战斗音乐节奏更具律动感而非过于机械。

**利用CC64延音踏板制作游戏钢琴场景**：在钢琴旋律MIDI轨道上，手动在自动化轨中绘制CC64的开关（值127=踏板踩下，值0=踏板抬起），时机对应和声变化节点，可避免音符混浊同时保留钢琴共鸣，这在游戏情感高潮场景（如BOSS战后的过场动画配乐）中尤为重要。

---

## 常见误区

**误区一：MIDI力度等于音量**  
许多初学者认为提高Velocity就是让音符"更响"。实际上，Velocity触发的是采样库中不同录音层次的切换，而音量由CC7和CC11控制。将所有音符Velocity拉到127不会让音乐更有力，反而会因为一直触发"最强奏"采样而丧失动态对比，使游戏配乐听起来没有层次感。

**误区二：CC1（调制轮）在所有乐器上效果相同**  
CC1的实际效果完全取决于虚拟乐器的内部映射设置。在弦乐库中CC1通常控制颤音（Vibrato）深度，但在某些合成器中CC1可能控制滤波器截止频率（Filter Cutoff）或LFO速率。游戏音乐制作者在使用新音色库前必须查阅其CC映射文档，否则盲目绘制CC1自动化曲线可能导致完全意外的音色变化。

**误区三：MIDI量化越精确音乐越好**  
将所有MIDI音符硬量化至1/16或1/32网格会消除人类演奏时自然存在的微小时间偏差（Groove/Swing感）。在游戏音乐的爵士场景、民族音乐场景或RPG古典场景中，刻意保留甚至手动引入±5~15毫秒的时值偏移（Humanize功能）能显著提升音乐的有机感。Cubase、Logic Pro等DAW均提供Humanize参数来随机化音符位置和力度。

---

## 知识关联

**前置概念——DAW对比选择**：不同DAW的MIDI编辑能力有所侧重。Reaper的MIDI编辑器功能基础但高度可定制，FL Studio的Piano Roll被广泛认为是节拍制作（Beat Making）最直观的MIDI界面，而Cubase的MIDI逻辑编辑器（Logical Editor）支持通过条件表达式批量处理CC值——了解这些差异有助于在实际游戏音乐项目中选择合适工具。

**后续概念——音频录制**：MIDI控制的是虚拟乐器输出的数字信号，当需要引入真实乐器演奏（如为游戏配乐录制真实小提琴独奏或人声）时，就需要进入音频录制的工作流程。实际制作中，专业游戏配乐常将MIDI编排的管弦乐背景层与录制的真实乐器旋律层混合使用，MIDI轨与音频轨在DAW中并行存在，通过混音路由统一输出。