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
quality_tier: "pending-rescore"
quality_score: 43.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 分轨导出

## 概述

分轨导出（Stem Export）是指在DAW中将一首完整的游戏音乐作品按照乐器组、功能层或音效类别，分别渲染输出为多个独立音频文件的工作流程。与普通的立体声混音导出不同，分轨导出的每个输出文件（称为Stem）只包含特定的音轨内容，例如仅包含弦乐组的`strings.wav`或仅包含打击乐的`drums.wav`。游戏音频中间件（如Wwise、FMOD）在运行时可以单独控制每条Stem的音量和播放状态，从而实现音乐随玩家行为动态变化的自适应效果。

这一概念最早随着2000年代自适应音乐系统的普及而被游戏音频行业广泛采纳。早期的做法是手工在DAW中逐轨Solo后分别导出，效率极低；现代DAW（如Logic Pro、Cubase、Reaper）均已内置"导出多条通道（Export Multiple）"功能，Reaper甚至允许通过自定义渲染矩阵（Render Matrix）一次性指定数十条输出，将导出时间压缩到单次渲染即可完成。

分轨导出对游戏音乐的重要性在于它是连接作曲创作与交互运行时的物理桥梁：作曲师的分层编排能否在引擎中被正确还原，完全取决于分轨文件是否按约定格式、命名规则和对齐方式交付。错误的分轨导出会导致Wwise中的Music Segment无法正确同步，或FMOD中的多层混音时序错乱。

## 核心原理

### 轨道分组与Bus路由

分轨导出的前提是在DAW工程中为每个目标Stem建立独立的混音Bus（总线）。具体做法是将属于同一Stem的若干音轨的输出均路由到同一条子总线，例如将Violin 1、Violin 2、Viola三条MIDI轨的输出统一发送至名为`Bus_Strings`的总线，再从该总线输出到主输出。导出时对`Bus_Strings`进行离线渲染，所得文件即为弦乐Stem。需要注意的是，若音轨同时挂有发送到混响总线的Aux Send，必须决定是否将混响效果"烘焙"入该Stem，还是单独导出一条混响返回Stem，这一决策会影响引擎端混合时的空间感。

### 时间对齐与帧起始位置

所有Stem文件的长度必须完全一致，且起始点必须在同一时间帧（通常是小节1第1拍第1子位）开始录音。这是因为游戏引擎会以"同时触发多条Stem"的方式进行播放，任何一条Stem的样本偏移超过1个采样点（at 48000Hz约0.02毫秒）都会产生可察觉的音相问题。在DAW导出设置中，应将"导出区域"锁定为工程起始点到终止点，而不是"选中区域"，以防止不同轨道的修剪边界导致各Stem长度不一致。

### 采样率、位深与文件格式规范

游戏音频的Stem通常以**48000Hz、24-bit、WAV格式**交付，这是Wwise和FMOD的默认导入格式。44100Hz常见于音乐发行，但游戏引擎内部时钟普遍使用48kHz，若混用采样率会在引擎内触发实时重采样，引入轻微的音质损失并增加CPU负担。部分游戏项目（如主机平台高保真项目）会要求32-bit float以保留更大的动态余量，此时需在DAW的渲染设置中明确选择"32-bit float"而非"32-bit int"，两者在DAW下拉菜单中相邻但含义截然不同。

### 导出前的自动化检查

由于Stem导出与自动化曲线（Automation）密切相关，在执行导出前必须确认：作曲阶段写入的音量/Pan自动化是否属于应该保留在Stem内部的表情处理，还是属于应由游戏引擎在运行时控制的动态层次。例如，一段"渐强到高潮"的音量自动化如果被烘焙进Stem，引擎将无法再单独调节这条Stem的响度，导致自适应功能失效。业界惯例是：**表情性自动化（articulation automation）留在Stem内；响度与静音控制类自动化不烘焙**，而改由引擎参数驱动。

## 实际应用

在一款典型的角色扮演游戏战斗音乐制作中，作曲师可能将同一段64小节的战斗主题拆分为以下4条Stem导出：`combat_drums.wav`（打击乐组）、`combat_bass.wav`（低音线）、`combat_melody.wav`（主旋律铜管）、`combat_pad.wav`（弦乐铺垫）。在Wwise中，这4条文件被导入同一个Music Segment并设置为同步播放。当战斗强度参数（Combat Intensity）从低变高时，Wwise的RTPC曲线会将`combat_melody`的音量从0dB提升到0dB（默认）、将`combat_pad`的音量淡出，实现从"氛围感"到"激烈战斗"的动态过渡——这一切都依赖于4条Stem精确对齐且时长完全一致。

在Reaper的渲染矩阵工作流中，可以通过勾选矩阵中不同的行列交叉点，在单次离线渲染中同时输出全部4条Stem，总渲染时间约等于1次全曲渲染时间，比逐条Solo导出节省约75%的时间。

## 常见误区

**误区一：将Stem与多轨录音（Multitrack）混淆。** Stem是已经过子混音（Submix）处理的分组文件，一条Stem通常包含多个乐器；而Multitrack是每件乐器的单独录音。在游戏引擎中导入Multitrack是可行的，但会成倍增加内存占用和通道管理复杂度，绝大多数游戏项目并不需要。

**误区二：认为Stem数量越多，自适应效果越好。** 将音乐切分为8条甚至12条Stem在技术上可行，但每增加一条Stem，引擎需要额外维护一个播放实例，内存与流媒体带宽的压力线性增加。移动平台项目通常将Stem数量控制在2-4条；主机/PC项目可扩展至6-8条，但超过此范围需要进行专项内存预算评估。

**误区三：忽略Stem间的效果器相位一致性。** 如果多条Stem在DAW中共享同一个总线混响（通过Aux Send并行处理），导出时若仅对干声总线离线渲染，所得Stem将不包含混响尾音，在引擎中播放时会失去空间感。正确做法是同时导出一条`reverb_return.wav`的混响返回Stem，或将混响烘焙入各Stem并接受额外的磁盘空间开销。

## 知识关联

分轨导出建立在**自动化与表情**的基础之上：作曲师需要在完成所有自动化编写后才能执行导出，并且必须在导出前决定哪些自动化曲线烘焙进文件、哪些交由引擎处理。这一决策直接影响后续**Music Segment**的配置方式——Wwise的Music Segment以Stem文件为素材，其时间网格（Time Grid）和同步行为依赖于Stem的精确时长与小节信息元数据。

在项目规模扩大后，手动逐曲导出Stem的效率瓶颈催生了**批量处理（Batch Processing）**的需求：通过DAW脚本（如Reaper的EEL/Lua脚本或Nuendo的批量导出预设）可以对数十个工程文件执行统一的分轨导出参数，确保整个游戏OST的格式一致性。分轨导出的规范也直接约束**Music Event**的设计：Music Event触发时引擎需要知道加载哪些Stem文件，文件命名规范（如`{曲目名}_{层名}_{版本}.wav`）必须在分轨导出阶段就与音频设计师对齐。
