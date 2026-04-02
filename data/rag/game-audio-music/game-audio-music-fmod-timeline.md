---
id: "game-audio-music-fmod-timeline"
concept: "Timeline编辑"
domain: "game-audio-music"
subdomain: "fmod-music"
subdomain_name: "FMOD音乐"
difficulty: 2
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 52.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Timeline编辑

## 概述

FMOD Studio的Timeline是一个基于时间轴的多轨编辑界面，允许音频设计师将音频片段、逻辑标记和自动化曲线排布在一条水平时间线上，通过精确的时间控制实现游戏音乐的播放与触发。Timeline以毫秒（ms）为最小时间单位，同时支持以小节/拍（Bars/Beats）为单位进行编辑，这对于需要节拍对齐的游戏音乐设计尤为关键。

Timeline编辑的概念源自传统DAW（数字音频工作站）软件的轨道式布局，FMOD Studio从2.0版本开始对Timeline界面进行了重大重构，引入了"Instrument"（乐器层）的概念，使每条轨道不仅能容纳音频片段，还能承载参数触发和过渡逻辑。与Cubase或Pro Tools等纯录音软件的时间线不同，FMOD Timeline的核心价值在于它是"实时可分叉"的——游戏运行时，Timeline的播放头位置会受到游戏参数影响，而不仅仅是线性推进。

在游戏音乐设计中，Timeline编辑解决了"固定时长音频与动态游戏进程"之间的矛盾。一段45秒的战斗音乐如果用传统方式播放，无法在第23秒时恰好配合玩家击败Boss的瞬间结束。通过在Timeline上放置Transition Region和Destination Marker，设计师可以定义音乐在特定条件下如何优雅地跳转至胜利主题，而不产生生硬的切断感。

## 核心原理

### 轨道类型与层级结构

FMOD Timeline中的轨道分为三个主要类型：**Audio Track**（音频轨道）、**Logic Track**（逻辑轨道）和**Automation Track**（自动化轨道）。Audio Track直接承载音频片段，可以叠加多个片段形成复音层次；Logic Track不包含音频，专门用于放置Marker、Loop Region、Transition Region等控制元素；Automation Track用于在时间轴上绘制参数值随时间变化的曲线，例如让Low-pass滤波器截止频率在16拍内从20kHz缓降至800Hz。

多条Audio Track可以同时激活，形成音乐的多层结构。例如，一个战斗音乐Event可以包含四条轨道：底鼓/打击乐层、贝斯层、弦乐层和铜管层，每层以独立轨道存在，方便后续通过参数控制各层的音量淡入淡出。

### Marker与Region的编辑机制

Timeline上最常用的逻辑元素有四种，各自具有不同的图标颜色和行为：

- **Destination Marker**（绿色旗帜）：标记播放头可以跳转到的目标位置，通常放在小节起始处，确保跳转后节拍对齐。
- **Loop Region**（蓝色区域块）：定义循环的起止范围。播放头到达Loop Region末端时会自动返回起点，是游戏音乐无缝循环的基础。
- **Transition Region**（橙色区域块）：当播放头进入此区域且预设的参数条件成立时，Timeline会在当前Loop Region完成后执行跳转，而非立即中断。
- **Tempo Marker**（节拍标记）：定义Timeline特定位置的BPM和拍号。一条Timeline上可以放置多个Tempo Marker，使音乐从120 BPM的段落平滑过渡到90 BPM的段落，FMOD会自动计算每个小节的像素宽度。

### 时间显示模式与卡尺系统

Timeline顶部的卡尺（Ruler）有两种显示模式可以切换：**时间模式**（显示分:秒:毫秒）和**音乐模式**（显示小节:拍:细分）。在音乐模式下，Timeline的网格对齐吸附功能会以当前Tempo Marker定义的BPM为基准，自动将音频片段的起点吸附到最近的小节线或拍点。这一功能确保音频素材与节拍完全对齐，误差不超过1个采样（在48000Hz采样率下约为0.02ms）。

拖拽音频片段至Timeline时，按住Ctrl键可暂时关闭网格吸附，允许非整拍位置的精确放置，适用于需要切分节奏或弱拍进入的乐句。

## 实际应用

**战斗音乐的层叠结构设计**：以一款RPG游戏为例，设计师在同一个Event的Timeline上创建6条平行Audio Track，分别对应鼓组、低频层、旋律层A、旋律层B、打击乐补充层和氛围层。每条轨道的音频片段时长均为32小节（约64秒，BPM=120），确保所有层完美对齐。通过将每条轨道连接到同一个"战斗激烈度"参数，可以让轨道的Volume Automation根据敌人数量动态调整，而这一切都在同一条Timeline上可视化管理。

**无缝循环点设置**：在Timeline音乐模式下，将Loop Region的起点设置在第1小节第1拍，终点设置在第32小节第4拍最后一个16分音符之后（即恰好在第33小节第1拍之前）。若音频素材的末尾存在混响尾音，可在Loop Region末端之后额外预留2小节的尾音区域，并勾选Audio Track的"Steal on loop"选项，避免混响被截断。

**过场动画的一次性播放**：对于不需要循环的过场音乐，在Timeline上不放置任何Loop Region，并在音频片段末尾放置一个Event End Marker。播放头到达End Marker后，Event将自动停止并从内存中释放引用，防止内存泄漏。

## 常见误区

**误区一：认为Timeline与Playlist可以互换使用**。Timeline适合有明确时间结构和节拍逻辑的音乐，例如需要精确卡点的战斗音乐。Playlist则适合需要随机或顺序播放一组独立片段的场景（如环境音效）。若将一首带有明确起承转合结构的RPG战斗曲放入Playlist，将失去Timeline提供的Transition Region和Tempo Marker等节拍对齐能力。

**误区二：认为Loop Region的结束点越靠近音频片段末尾越好**。实际上，Loop Region的结束点需要设置在音乐中"可以重复"的自然节点，通常是4小节或8小节的整数倍位置。若Loop Region过短（例如只有2拍），频繁的循环跳转可能导致节奏感割裂，而过长的Loop Region（例如64小节）则会使Transition Region的触发延迟过高，影响音乐对游戏事件的响应速度——一般推荐Loop Region长度控制在8至16小节之间。

**误区三：混淆Destination Marker与Transition Marker的功能**。Destination Marker仅定义"跳转目标"，本身不触发任何跳转动作；触发跳转的动作由Transition Region或游戏代码调用`EventInstance.setParameterByName()`实现。若只放置Destination Marker而不配置对应的Transition Region，音乐不会自动跳转，播放头将直接越过Destination Marker继续前行。

## 知识关联

Timeline编辑建立在**Music Event**概念之上：Music Event定义了整个音频事件的容器属性（如3D空间化、音量、距离衰减），而Timeline则是该容器内部的时间编排层，负责决定容器内的音频何时播放、如何循环。没有对Music Event的理解，无法判断Timeline中的轨道应当使用何种输出总线路由。

学习Timeline编辑之后，下一个核心主题是**参数化音乐**。参数化音乐利用Timeline中已建立的Transition Region和Destination Marker，通过FMOD参数系统在运行时动态控制播放头的跳转行为——本质上是将Timeline从一个线性播放序列升级为一个由游戏状态驱动的有限状态机。掌握Timeline编辑中Marker的放置逻辑，是实现参数化音乐跳转规则的必要前提。