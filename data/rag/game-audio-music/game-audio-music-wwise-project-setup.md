---
id: "game-audio-music-wwise-project-setup"
concept: "Wwise项目搭建"
domain: "game-audio-music"
subdomain: "wwise-music"
subdomain_name: "Wwise音乐系统"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Wwise项目搭建

## 概述

Wwise项目搭建是指在Audiokinetic Wwise软件中创建一个新的音频工程文件（`.wproj`），并建立其内部层级结构与基本参数配置的完整过程。一个Wwise项目本质上是一个XML格式的工程描述文件，配合存放音频素材的`\.cache`文件夹和`SoundBanks`输出目录共同构成完整的工程体系。Wwise 2019.2版本之后引入了更稳定的工程文件版本控制机制，使多人协作时的合并冲突显著减少。

Wwise项目的概念最早随2006年Audiokinetic发布第一版Wwise时出现，其设计思路借鉴了数字音频工作站（DAW）的会话文件概念，但专为游戏引擎集成而优化。与DAW工程不同，Wwise项目不直接存储音频波形数据，而是存储对音频文件的引用关系、所有Audio Object的属性配置，以及与游戏引擎通过API通信的事件（Events）定义。这一设计使得同一个.wav源文件可以在项目中被多个不同的Sound对象引用，从而节省磁盘空间。

搭建一个结构清晰的Wwise项目对整个游戏音频开发流程至关重要，原因在于Wwise的SoundBank打包系统依赖项目内部的层级分组来决定哪些资源被打包到同一个Bank文件中。一旦前期层级混乱，后期重构的成本极高，因为Event名称和SoundBank名称会直接写入游戏代码，任何重命名都需要同步修改程序端的引用字符串。

## 核心原理

### 项目创建与文件结构

在Wwise中通过菜单`File > New Project`创建项目时，软件会要求指定项目名称、存储路径，以及目标平台（Platform）。平台选项直接影响编解码器的可用范围：例如选择Nintendo Switch平台后，才能使用`Vorbis`或`ADPCM`的Switch专用编码变体。创建完成后，工程根目录下自动生成以下结构：

- `<ProjectName>.wproj` — 工程主文件
- `<ProjectName>.wsources` — 音频源文件引用清单（Wwise 2021.1后从.wproj中分离）
- `\.cache\` — 转码后的音频缓存，不应纳入版本控制
- `SoundBanks\` — Bank输出目录，内含各平台子目录
- `Originals\` — Wwise内置的源文件管理目录，用于存放导入的原始音频

### Actor-Mixer层级与Work Unit

Wwise项目的组织核心是**Work Unit**系统。每个Work Unit是一个独立的`.wwu`文件，对应Project Explorer中的一个顶级节点。默认情况下，新建项目会在Actor-Mixer Hierarchy下创建名为`Default Work Unit`的单个`.wwu`文件。实际项目中推荐按功能模块分割Work Unit，例如将BGM、SFX、Voice各自对应一个独立`.wwu`文件，这样不同音频设计师可以同时编辑各自的Work Unit而不产生版本控制冲突。

Actor-Mixer Hierarchy是存放Sound SFX、Sound Voice等普通音频对象的容器；而交互式音乐系统（Interactive Music Hierarchy）则是存放Music Segment、Music Switch Container等音乐专用对象的独立分支。两套层级在Project Explorer的左侧以不同标签页展示，音乐内容必须创建在Interactive Music Hierarchy下，否则无法使用节拍同步、拍号设置等音乐专属功能。

### 基本属性配置

新项目搭建时必须在`Project > Project Settings`中完成以下关键配置：

**采样率（Sample Rate）**：Wwise默认工程采样率为48000 Hz，与绝大多数游戏引擎的音频子系统标准一致。若源文件为44100 Hz的音乐素材，建议在此处统一设为48000 Hz，让Wwise在转码时自动重采样，而非在SoundBank生成时产生多套缓存。

**SoundBank设置**：在`Project Settings > SoundBanks`标签下，需指定`SoundBank Path`的输出根目录，并勾选`Generate header file`选项以自动生成`Wwise_IDs.h`文件。这个头文件将所有Event和SwitchGroup的字符串名称转换为唯一的32位哈希ID（`AkUniqueID`类型），游戏程序员通过引用该文件中的宏定义来触发音频，避免在代码中硬编码字符串。

**平台与语言设置**：通过`Project > Platform Manager`可添加多个目标平台；通过`Project > Language Manager`可添加游戏所需的语言（如`Chinese`、`English`），语言列表直接影响Voice对象的本地化文件夹组织方式。

## 实际应用

以一个中型RPG游戏项目为例，典型的Wwise项目搭建流程如下：首先创建项目并添加PC、PS5、Xbox Series X三个平台；接着在Interactive Music Hierarchy下创建名为`BGM`的Work Unit，在Actor-Mixer Hierarchy下分别创建`SFX_Ambient`、`SFX_Combat`、`UI`三个Work Unit。在`SoundBanks`层级下，建立`Init.bnk`（存放全局设置）、`BGM_World1.bnk`、`BGM_World2.bnk`（按游戏章节分包）的Bank结构，使得玩家进入World2时才加载对应的音乐Bank，控制内存占用。

在Wwise与Unity集成的场景中，完成项目搭建后需要将Wwise Unity Integration包导入Unity工程，并在Unity的`WwiseGlobal`对象上指定`SoundBanksPath`为相对路径，该路径必须与Wwise Project Settings中配置的输出路径保持一致，否则游戏运行时会报`AK_BankNotFound`错误。

## 常见误区

**误区一：将`.cache`目录纳入Git版本控制。** `.cache`文件夹存放的是Wwise根据源文件和平台设置自动生成的转码缓存，体积可达数GB，且可由任何协作者在本地重新生成。正确做法是在`.gitignore`中添加`\.cache\`条目，只对`.wwu`文件、`.wproj`文件和`Originals\`目录进行版本管理。

**误区二：将音乐内容创建在Actor-Mixer Hierarchy下。** 初学者常在Actor-Mixer的Sound SFX对象中导入背景音乐文件，这样虽然能播放声音，但完全无法使用Wwise音乐系统的节拍感知（Beat/Bar同步）、音乐过渡（Music Transition）等功能。所有需要节拍同步的音乐内容必须在Interactive Music Hierarchy下以`Music Segment`为基本单元进行组织。

**误区三：使用中文或特殊字符命名项目和路径。** Wwise工程路径中若包含中文字符，在某些操作系统区域设置下会导致SoundBank生成失败或Wwise命令行工具（WAAPI）调用异常。项目名称和存储路径应严格使用字母、数字和下划线的组合。

## 知识关联

Wwise项目搭建以**Wwise概述**中介绍的Audio Object分类体系（Sound、Container、Bus等）为前提，项目搭建阶段建立的层级结构正是这些对象的组织框架。Interactive Music Hierarchy的创建是后续学习**Music Segment**的直接入口——Music Segment必须在已有Interactive Music Hierarchy Work Unit的项目中才能被创建，其拍号、BPM等属性的配置依赖于项目级别的采样率设置是否正确完成。正确搭建的SoundBank目录结构和`Wwise_IDs.h`头文件，则是后续与游戏引擎集成、触发音乐事件的技术基础。