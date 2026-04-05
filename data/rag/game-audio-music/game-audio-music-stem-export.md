---
id: "game-audio-music-stem-export"
concept: "分轨导出"
domain: "game-audio-music"
subdomain: "daw"
subdomain_name: "编曲软件(DAW)"
difficulty: 2
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 分轨导出

## 概述

分轨导出（Stem Export）是指将DAW工程中的多条音频轨道按照逻辑分组，单独渲染为独立音频文件的操作流程。与普通立体声混音导出不同，分轨导出产出的是若干个单独的.wav或.ogg文件，每个文件只包含工程中部分乐器或声部的声音，例如单独的鼓轨、弦乐轨或人声轨。

分轨导出的概念源自录音棚的多轨磁带工作流程，早在1960年代Beatles在Abbey Road录音时就已将各乐器录制在不同磁道上，以便后期混音。进入数字音频工作站时代后，Pro Tools、Cubase、Reaper等软件将这一概念标准化为"Export Stems"功能。游戏音频领域，Wwise和FMOD等自适应音频中间件在2005年前后开始广泛支持多分轨实时混合，使得向游戏引擎提供分轨文件成为游戏音乐制作的标准交付物。

在游戏音乐中，分轨导出的意义在于它是实现自适应音乐（Adaptive Music）的物质基础。游戏引擎无法实时拆分一段混音完成的立体声文件，只有在DAW阶段将各声部分别导出，才能让Wwise或FMOD在运行时根据游戏状态动态控制每条分轨的音量，例如战斗开始时渐入打击乐分轨、角色死亡时静音人声分轨。

---

## 核心原理

### 分轨的分组逻辑

分轨不等于"每条轨道单独导出"。标准游戏音频工作流中，通常将数十条MIDI或音频轨道汇总为4至8条逻辑分轨（Stem），例如：**打击乐（Percussion）**、**低频（Bass）**、**和声垫（Pad/Harmony）**、**旋律（Melody）**、**人声（Vocals）**。分组原则取决于哪些声部在游戏逻辑中需要被独立控制，而非按乐器类别机械分割。例如若游戏只需在战斗时切入打击乐，将鼓、贝斯、打击乐器全部合并到同一条分轨导出即可，反而比导出十余条单乐器轨更高效。

### 导出时的总线路由（Bus Routing）

在Cubase或Logic Pro中，正确的分轨导出需要先建立专属的总线架构。每组分轨对应一条独立的Group Bus或Aux Bus，所有属于该分组的轨道都发送到这条Bus，而不是发送到Master Bus。导出时选择"导出各Bus的独奏输出"而非主输出，确保每条分轨文件中不混入其他声部的信号。需要特别注意的是：**主混响和主压缩等主线效果器（Master FX）通常应用于Master Bus，在分轨导出时必须决定是否让每条分轨各自携带该效果，还是在游戏引擎内由主Bus统一施加**。两种方案在音色一致性上存在根本差异。

### 精确的时间对齐要求

所有分轨文件必须具有**完全相同的时间长度和采样精度**，才能在Wwise或FMOD中实现无缝同步播放。具体而言，每条分轨的开始时间戳、小节线位置、总采样数必须完全一致。在Reaper中，通过"File → Render → Render Matrix"可以一次性勾选多条轨道并以相同的起止点批量渲染，避免手动逐条导出时因起始位置偏移几个采样点而导致各分轨之间出现相位漂移（Phase Drift）。Wwise要求分轨文件必须同步至同一音频时钟，通常以44100 Hz或48000 Hz采样率、16-bit或24-bit位深交付，具体规格需与引擎端协商确定。

### 自动化数据的处理方式

DAW轨道上的音量自动化（Volume Automation）和声像自动化（Pan Automation）在分轨导出时有两种处理策略：**烘焙进文件（Bake into Audio）**或**剥离出文件（Strip Automation）**。若某条分轨的淡入淡出是由Wwise的RTPC参数在运行时控制的，则导出时必须将该轨道的DAW自动化曲线设为平直（0 dB无变化），否则运行时会出现双重音量控制，导致音量变化不可预测。反之，若某个渐强效果纯属音乐表达而不参与游戏逻辑，则可以烘焙进音频文件。

---

## 实际应用

**RPG战斗场景的四轨方案**：在一款JRPG战斗音乐中，作曲家将完整编曲拆分为四条分轨：`battle_percussion.wav`、`battle_bass.wav`、`battle_harmony.wav`、`battle_melody.wav`。在Wwise中，探索状态仅播放harmony和bass两轨，当战斗触发时通过Blend Track将percussion和melody的音量在2秒内从-96 dB拉至0 dB。四个文件总时长均为32秒（在44100 Hz下各为1,411,200个采样点），保证循环拼接时完美对齐。

**Reaper的Render Matrix实际操作**：在Reaper中，打开"File → Render"并切换至"Render Matrix"标签页，横轴为各条轨道，纵轴为渲染目标文件。勾选对应单元格后点击"Render X Files"，软件会以相同的时间范围一次性输出全部分轨，整个过程约比逐条手动导出节省70%的操作时间。

**Wwise中分轨的组织方式**：导出的分轨文件在Wwise中通常被组织在同一个Music Segment下，每条分轨文件对应一个独立的Music Track，通过Blend Track或Switch Track根据游戏变量决定各轨的混合权重。

---

## 常见误区

**误区一：认为分轨越多控制越精细**。初学者常将每件乐器单独导出为一条分轨，导致一首3分钟的游戏音乐产生20个以上的.wav文件，不仅占用大量内存（48000 Hz / 16-bit / 立体声的3分钟音频约为103 MB每轨），还使Wwise中的逻辑变得极为复杂。实际上应按游戏逻辑需求决定分组数量，而非按乐器数量决定。

**误区二：分轨导出后仍在DAW总线上保留动态效果器**。如果Master Bus上挂有限幅器（Limiter）或多段压缩，导出各独立分轨时这些效果器只处理当前分轨的信号，而非所有分轨叠加后的信号，导致每条分轨的动态处理结果与实际游戏中多轨叠加播放时完全不同。正确做法是在分轨导出时旁通（Bypass）所有Master Bus效果器，或将效果器插入每条分轨的Bus上。

**误区三：忽视循环点（Loop Point）的对齐**。分轨导出后在Wwise中设置循环时，若循环点不位于所有分轨共同的小节线上，各分轨的循环周期会逐渐错位，产生越来越明显的节奏偏差。分轨文件的总时长必须是该段音乐BPM对应的完整小节数，例如120 BPM的4小节片段在44100 Hz下精确长度为88200个采样点。

---

## 知识关联

分轨导出直接依赖**自动化与表情**阶段的工作成果，因为在DAW中为各轨道精心绘制的音量与声像自动化曲线，正是决定分轨导出时"烘焙"还是"剥离"自动化数据的判断依据。若自动化阶段未清晰区分"纯音乐表达性自动化"与"由游戏逻辑驱动的动态变化"，分轨导出时将面临两难选择。

完成分轨导出后，下一步是**批量处理**：当一首完整游戏原声需要导出数十组分轨时，需要借助Reaper的脚本或命令行工具对文件进行自动化重命名、格式转换和响度标准化（通常归一至-23 LUFS或游戏项目指定标准）。导出的分轨文件在Wwise中被封装为**Music Segment**的组成部分，并通过**Music Event**触发播放，这两个概念构成游戏引擎接收分轨文件并将其与游戏逻辑连接的完整闭环。