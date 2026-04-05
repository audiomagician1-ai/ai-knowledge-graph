---
id: "sfx-am-aux-send"
concept: "辅助发送"
domain: "game-audio-sfx"
subdomain: "audio-middleware"
subdomain_name: "音频中间件"
difficulty: 4
is_milestone: false
tags: []

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
updated_at: 2026-03-27
---


# 辅助发送

## 概述

辅助发送（Auxiliary Send）是音频中间件（如Wwise、FMOD）中的一种路由机制，允许将一个音频信号的副本发送到独立的Aux Bus（辅助总线）上进行并行处理，而不影响原始信号的主路径。与直接在声音对象上挂载效果器不同，辅助发送使多个声音源共享同一个混响或延迟效果器实例，从而在运行时大幅降低CPU开销。

这一概念源自硬件调音台时代的"Aux Send"旋钮设计——录音棚里工程师通过调节每个通道条上的Aux旋钮，决定有多少信号被送往公共效果器（例如Lexicon 480L混响单元）。Wwise在2010年代将此范式引入游戏音频领域，通过Game-Defined Auxiliary Sends和User-Defined Auxiliary Sends两套机制，让游戏引擎与设计师均可动态控制辅助发送量。

在游戏音频中辅助发送的核心价值在于**环境混响的空间一致性**：当玩家穿越不同房间时，房间内所有声音——脚步声、枪声、NPC对白——都应共享同一个代表"这个空间声学特征"的混响总线。若每个声音对象各自携带独立的混响效果器，不仅CPU消耗成倍增长，各声音之间的混响尾音也无法在时间轴上自然交叠融合。

---

## 核心原理

### Aux Bus的信号流架构

在Wwise的路由图中，辅助发送形成一条**旁路（Side Chain）**信号流：原声音对象的输出继续沿Actor-Mixer层级向上传至Master Audio Bus，同时按照设定的发送电平（Send Level，单位为dB或0~1的线性值）将一份拷贝路由至指定的Aux Bus。Aux Bus自身拥有独立的效果器插槽、音量推子和输出目标，其输出最终合并回主混音总线。这意味着混响效果的湿信号（Wet Signal）与干信号（Dry Signal）走的是完全独立的物理路径，设计师可以在Aux Bus端单独控制混响的总电平，而无需逐一修改每个声音对象。

### Game-Defined 与 User-Defined 发送

Wwise将辅助发送分为两类，两者在实现逻辑上有根本差异。**User-Defined Auxiliary Sends**由音频设计师在Wwise工程中静态指定：在某个声音对象的General Settings面板中，最多可添加4条辅助发送通道，每条指向一个特定Aux Bus并预设发送量。**Game-Defined Auxiliary Sends**则由引擎代码在运行时通过API（`AK::SoundEngine::SetGameObjectAuxSendValues()`）动态赋值，通常配合环境区域触发器使用——当角色进入石洞区域，引擎将该游戏对象的Aux Send目标切换至"Cave_Reverb"总线，发送量由距离或遮挡系数实时计算。两种方式可同时在一个声音对象上生效，最终发送电平为两者叠加结果。

### 发送量的衰减计算

辅助发送量通常不是固定值，而依赖于**基于距离和遮挡的衰减曲线**。在Wwise中，当启用"Use game-defined auxiliary sends"后，引擎可以将Auxiliary Send Level与Obstruction（遮挡）系数联动：遮挡值为0时直达声与混响均正常传播，遮挡值增大时直达声通过Low-pass Filter衰减，但辅助发送量（即混响比例）可配置为**反向增大**——被墙壁遮挡的声音，听起来更多是通过空气和结构传来的漫反射成分，混响比例自然更高。这正是前置知识"遮挡与阻隔"与辅助发送交汇的具体物理依据。公式上，若遮挡系数为O（0~1），一种常见设计方案是将Aux Send Level设为`L_aux = L_base + O × ΔL`，其中ΔL为遮挡带来的额外混响增益补偿量（通常取值范围3~6 dB）。

### Aux Bus上的效果器管理

一个Aux Bus可承载多个串联效果器插件，最典型的配置是**Wwise Reflect**（基于图像源法的早期反射）或**SoundSeed Reverb**（算法混响）挂载于洞穴、大厅等专属Aux Bus上。由于所有共享这条总线的声音对象共用同一个效果器实例，该实例的CPU开销只被计算一次，而非随声音数量线性增长。在有40个同时发声对象的战斗场景中，若每个对象单独挂载混响效果器，CPU代价是Aux Bus方案的**近40倍**。

---

## 实际应用

**大型室内空间的环境建模**：在第一人称射击游戏中，设计师为"工厂车间"创建一条名为`AMB_Factory_LargeHall`的Aux Bus，并在其上挂载衰减时间（RT60）约2.8秒的算法混响。玩家在车间内开枪、脚步声、金属碰撞声均通过User-Defined Send以-6 dBFS的发送量路由至此总线。设计师只需在Aux Bus上调整一次RT60参数，全部声音的空间感同步更新，无需打开每个声音对象逐一修改。

**门缝过渡的混响渐变**：玩家从户外靠近建筑物内部时，引擎通过距离触发逐渐提高Game-Defined Send电平，将"Indoor_MediumRoom"Aux Bus的发送量从-∞ dB线性提升至-3 dB，同时降低"Outdoor_Plate"总线的发送量，实现户外干声向室内混响的自然过渡，全程由代码驱动，音频设计师无需制作任何过渡音效资产。

**多层次空间的并发发送**：地下城场景中，单一声音对象可同时向`Dungeon_Stone_Reverb`（模拟石墙反射，短混响0.9秒）和`Dungeon_Ambient_Tail`（模拟远距离回声，长混响3.5秒）两条Aux Bus分别发送，前者发送量-4 dB，后者发送量-14 dB，叠加形成复杂空间层次感，但仍只需两个效果器实例。

---

## 常见误区

**误区一：将发送量直接设为0 dB以获得"更强的混响效果"**
0 dB发送意味着将等量的原始信号复制至Aux Bus，但混响器的输入增益并不等同于湿/干比。很多初学者误以为发送量越高混响越明显，实际上过高的发送量会导致Aux Bus混响输出过载，产生失真，而非更自然的空间感。Wwise中建议的初始发送量通常在-6 dB至-12 dB之间，并结合Aux Bus上的效果器Wet Level参数共同调节。

**误区二：用User-Defined Send处理所有环境切换**
静态的User-Defined Send无法响应运行时环境变化。若关卡有10种不同声学空间，将每种空间的Aux Bus都静态绑定在每个声音对象上会造成路由混乱且无法动态切换。正确做法是将环境敏感的混响切换完全交给Game-Defined Send，由引擎在区域碰撞回调中调用`SetGameObjectAuxSendValues()`更新目标总线，而User-Defined Send仅保留用于角色自身固定音色特征（如声音角色自带的轻微预混响）。

**误区三：认为辅助发送会延迟原始声音的播放时机**
辅助发送是信号路由，不引入任何延迟（除非Aux Bus上的效果器本身有延迟，如早期反射算法带来的若干毫秒）。干路径上的原始声音与Aux Bus上的混响完全并行处理，不存在因发送操作本身导致声音起始时机推迟的情况。

---

## 知识关联

辅助发送直接建立在**遮挡与阻隔**概念之上：遮挡系数不仅影响直达声的频率响应，同样是Game-Defined Auxiliary Send电平计算的输入变量，两者通过同一套空间感知模型联动，使声音在物理遮挡时同步呈现更强的漫反射混响比例。

向后延伸，辅助发送机制是**对白系统**的重要基础设施。NPC对白需要根据说话角色所在的声学空间（室内/室外/载具内部）动态切换混响类型，同时对白的清晰度优先级又要求混响发送量低于音效类声音——这些差异化的参数控制均通过Game-Defined Auxiliary Sends在运行时按游戏对象类别分别设置，而不是在对白资产本身上硬编码效果器，保证了对白混音的灵活性与可维护性。