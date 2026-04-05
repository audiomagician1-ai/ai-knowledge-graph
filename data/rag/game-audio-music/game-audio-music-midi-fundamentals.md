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



# MIDI基础

## 概述

MIDI（Musical Instrument Digital Interface，乐器数字接口）是1983年1月由Roland创始人梯郁三（Ikutaro Kakehashi）与Sequential Circuits公司Dave Smith联合主导，联合Roland、Yamaha、Korg、Kawai等日本及美国乐器厂商共同制定的通信协议标准，正式版本号为MIDI 1.0。该协议的诞生直接解决了不同品牌电子乐器之间无法互相通信的行业痛点——在MIDI之前，一台Roland合成器与一台Yamaha鼓机无法同步演奏。梯郁三因此贡献获得2013年格莱美技术奖（Grammy Technical Grammy Award）。

MIDI协议的核心设计哲学是：**传输演奏指令，而非传输声音本身**。一个包含4分钟复杂管弦编曲的.mid文件，体积通常在20KB～80KB之间；而同等时长的CD品质WAV文件（44100Hz、16bit、立体声）需要约40MB，压缩后的MP3也有4MB左右。这一数量级的差异解释了为什么早期游戏主机和PC游戏几乎全部采用MIDI格式存储音乐——1991年发售的SNES主机内置SPC700音频芯片，片内音频RAM仅有64KB，必须依靠MIDI数据驱动内置采样引擎实时合成音频，《最终幻想VI》（1994年）和《超级马里奥世界》（1990年）的全部配乐均以这种方式存储和播放。

即使在当今游戏音乐制作环境中，DAW内部的编曲层依然基于MIDI。作曲家在Reaper、Cubase、FL Studio、Logic Pro中写下的每一个音符，本质上仍是MIDI数据触发虚拟乐器（VST/AU插件）或硬件采样模块发声。掌握MIDI编辑，意味着可以精确控制每个音符的力度（Velocity）、时值（Duration）、音高（Pitch），以及通过CC控制器数据曲线实现弦乐的颤音渐入、管乐的气息强弱、钢琴的踏板延音——这些细节正是让游戏音乐从"机械感"走向"生动感"的底层技术基础。

参考资料：《MIDI 1.0 Detailed Specification》(MIDI Manufacturers Association, 1996, 第三版)；《The MIDI Manual: A Practical Guide to MIDI in the Project Studio》(Huber, David Miles, Focal Press, 2012)。

---

## 核心原理

### MIDI消息的数据结构

MIDI协议以字节（Byte）为单位传输数据，每条消息由1～3个字节组成。物理层传输速率固定为**31250 bps**（波特率），这是MIDI 1.0规范中被硬性规定的数值，由此可计算出每秒最多传输约3125字节，对应约1000条三字节消息——这个速率在1983年已足够，但在现代复杂编排中偶尔会出现"MIDI拥堵"（MIDI Choke）问题，尤其在同一时刻触发大量音符时。

最核心的消息类型是 **Note On** 与 **Note Off**：

- **Note On**：`[1001nnnn] [0kkkkkkk] [0vvvvvvv]`
- **Note Off**：`[1000nnnn] [0kkkkkkk] [0vvvvvvv]`

其中 `nnnn` 为MIDI通道号（二进制0000～1111，对应通道1～16）；`kkkkkkk` 为音符编号（0～127）；`vvvvvvv` 为力度（0～127）。音符编号与音高的对应关系为：

$$\text{音高（Hz）} = 440 \times 2^{\frac{n - 69}{12}}$$

其中 $n$ 为MIDI音符编号。例如中央C（C4）= 编号60，则其频率为 $440 \times 2^{(60-69)/12} = 440 \times 2^{-0.75} \approx 261.63\text{ Hz}$。A4 = 编号69，频率恰好为440 Hz。每增减1个编号代表一个半音，增减12个编号代表一个八度。

MIDI 1.0规范中有一项被硬性规定的惯例：**第10通道（Channel 10）专门分配给打击乐器**，通用MIDI（General MIDI，GM）标准进一步规定了第10通道上各音符编号对应的鼓件，例如编号36=低音鼓（Bass Drum 1）、编号38=小军鼓（Acoustic Snare）、编号42=踩镲关闭（Closed Hi-Hat）。

### Velocity（力度）与采样分层

力度值范围0～127，直接决定音符的响度，但在高质量采样库中其影响远不止于此。以Spitfire Audio的《BBC Symphony Orchestra》弦乐库为例，每个音符按力度分为**4～8个录音分层（Velocity Layer）**：

- 力度 1～25：对应 **ppp**（极弱）采样，录音来自真实演奏家以最轻柔的方式演奏
- 力度 26～60：对应 **mp**（中弱）采样
- 力度 61～90：对应 **mf**（中强）采样
- 力度 91～127：对应 **ff**（强）采样

这意味着不同力度范围触发的是完全不同的录音文件，音色质感截然不同。若在游戏音乐中为弦乐旋律统一设置 `velocity=100`，所有音符将始终触发同一层强奏采样，听感机械且缺乏呼吸感。正确做法是根据乐句走向手绘力度曲线（在DAW的Piano Roll中逐音符调整），或在录制后使用MIDI编辑工具批量施加人性化（Humanize）随机偏移，偏移幅度通常在 ±5～±15 之间为宜。

### CC控制器（Continuous Controller）

CC（Continuous Controller）消息是MIDI协议中用于传输连续变化参数的机制，消息格式为三字节：

```
[0xBn]  [控制器编号 0~127]  [参数值 0~127]
```

其中 `0xB` 表示这是CC消息类型，`n` 为通道号（十六进制0～F）。例如在通道1（n=0）上发送CC1（调制轮）值为64，实际字节序列为：`0xB0 0x01 0x40`。

MIDI 1.0标准定义了128个CC编号，以下为游戏音乐制作中最常用的几个：

| CC编号 | 约定功能 | 游戏音乐典型用途 |
|--------|----------|-----------------|
| CC1    | 调制轮（Modulation Wheel） | 控制弦乐/管乐颤音深度（Vibrato），从0到127渐进触发颤音效果 |
| CC7    | 音量（Channel Volume） | 整体通道音量包络，制作音乐的淡入淡出（fade in/out） |
| CC10   | 声像（Pan） | 左右声场定位，64为中央，0为最左，127为最右 |
| CC11   | 表情（Expression） | 乐句内的动态起伏，与CC7配合实现"音量×表情"的双层动态控制 |
| CC64   | 延音踏板（Sustain Pedal） | 值≥64为踏板踩下，<64为抬起；钢琴编曲必用 |
| CC74   | 明亮度/滤波截止（Brightness） | 控制合成音色的滤波器截止频率，制作音色渐亮/渐暗效果 |

**CC1与CC11的配合使用**是专业游戏音乐制作者的核心技巧：CC11（Expression）控制乐句级别的动态（如整个4小节短句的渐强渐弱），CC7控制整个段落的静态音量平衡。两者相乘决定最终输出音量，因此不应用CC7做乐句内的实时动态，这会破坏各乐器之间的混音平衡。

---

## 关键数据与规格速查

MIDI 1.0协议中几个需要牢记的关键数值：

| 参数 | 数值 | 实际意义 |
|------|------|----------|
| 传输波特率 | 31250 bps | 固定值，所有MIDI 1.0设备必须遵守 |
| 音符编号范围 | 0～127（共128个） | 0=C-2，60=C4（中央C），127=G9 |
| 力度范围 | 0～127 | 0在Note On中通常等同于Note Off |
| CC控制器数量 | 128个（编号0～127） | 其中14个为高精度14-bit控制器（MSB+LSB） |
| MIDI通道数 | 16个 | 第10通道（GM规范）保留给打击乐 |
| Pitch Bend范围 | -8192～+8191（14-bit） | 默认±2半音，可通过RPN 0重新设置范围 |
| PPQN默认精度 | 480 PPQN | 每个四分音符480个时钟脉冲，为DAW中最常见默认值 |

**PPQN（Pulses Per Quarter Note，每四分音符脉冲数）** 决定MIDI时序精度。480 PPQN意味着一个十六分音符被分为120个时钟步，这已足够应对绝大多数游戏音乐编曲需求。某些高精度DAW工程文件使用960 PPQN甚至1920 PPQN以支持更细腻的演奏时序偏移记录。

---

## 实际应用：游戏音乐中的MIDI工作流

### 典型Piano Roll编辑流程

以下是在Reaper中使用MIDI为游戏弦乐段落添加表情的典型步骤，以CC11控制乐句动态为例：

```
1. 在Piano Roll中完成音符布局（Note On/Off数据）
2. 切换至CC Lane视图，选择CC11（Expression）
3. 使用铅笔工具（Pencil Tool）手绘动态曲线：
   - 乐句起始：CC11 = 40（轻柔进入）
   - 乐句顶点（第3拍）：CC11 = 110（情绪高潮）
   - 乐句收尾：CC11 = 55（自然收声）
4. 同时在CC1（Modulation）曲线上：
   - 乐句前两拍：CC1 = 0（无颤音，长音起始）
   - 第3拍后渐增至：CC1 = 70（颤音渐入，增加歌唱感）
5. 检查CC64（Sustain）是否与钢琴声部的踏板逻辑一致
```

**案例**：《塞尔达传说：旷野之息》（2017年，作曲：梨本惠）的钢琴配乐以极度稀疏的MIDI力度曲线著称，同一主题每次重复时力度最大差异不超过20个单位（如55→70→60），刻意回避了标准化的"渐强→高潮→渐弱"模板，创造出独特的内敛张力。这种手法在MIDI编辑层面完全可见且可复现。

### 游戏音乐中的MIDI程序切换（Program Change）

通用MIDI（GM）标准定义了128种音色编号（Program 1～128），例如：Program 1=Acoustic Grand Piano，Program 41=Violin，Program 57=Trumpet。在早期PC游戏（如1990年代的AdLib/Sound Blaster平台）中，游戏引擎直接发送Program Change消息让OPL2/OPL3 FM合成芯片切换音色。现代游戏音乐制作中，Program Change消息可用于同一条MIDI轨道内切换采样库的演奏法（Articulation），例如在同一小节内从长弓奏法（Sustain）切换至拨弦奏法（Pizzicato），无需手动分轨。

---

## 常见误区

**误区一：认为更高的力度值等于更好的音乐表现**
许多初次使用专业采样库的制作者习惯将所有音符力度设置在90～110范围内（"够响但不爆"），但这使得弦乐库始终在 `mf` 至 `f` 层之间循环，完全丧失 `pp` 层独有的柔和泛音质感。正确做法是让力度范围覆盖20～120，根据乐句情绪决定分布重心。

**误区二：混淆CC7（Volume）与CC11（Expression）的用途**
CC7应在编曲开始前设定各轨静态音量平衡（如弦乐=100，铜管=85，打击乐=110），编曲过程中不再修改。CC11才是实时动态控制的正确工具。若用CC7做渐强渐弱，会导致每次修改混音平衡时之前画的动态曲