---
id: "audio-attenuation"
concept: "音频衰减模型"
domain: "game-engine"
subdomain: "audio-system"
subdomain_name: "音频系统"
difficulty: 2
is_milestone: false
tags: ["模型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 音频衰减模型

## 概述

音频衰减模型（Audio Attenuation Model）描述了游戏中声音随距离增加而减小音量的数学关系，以及声源方向对听者感知音量的影响规则。简单来说，距离越远，声音越小——但"如何变小"的曲线形状，决定了玩家对游戏世界真实感的直接体验。

物理世界中声音遵循平方反比定律（Inverse Square Law）：声音强度与距离的平方成反比，即 **I ∝ 1/r²**，其中 I 为声音强度，r 为距离。游戏引擎将这一物理原理转化为可调参数，并在此基础上引入了最小距离（MinDistance）、最大距离（MaxDistance）和多种曲线类型，让设计师能够超越纯物理模拟，制作出更符合游戏需求的声音体验。

衰减模型的意义不仅在于音量控制，它还直接影响音频系统的CPU性能。当声源超过最大衰减距离（即音量衰减为0）时，引擎可以完全跳过该声源的混音计算，从而节省运算资源。这使得衰减参数既是艺术决策，也是性能优化手段。

## 核心原理

### 距离衰减曲线类型

主流游戏引擎（如Unity和Unreal Engine）均内置了至少四种距离衰减曲线：

- **线性衰减（Linear）**：音量从 MinDistance 到 MaxDistance 均匀线性下降至0。公式为 `Volume = 1 - (distance - MinDistance) / (MaxDistance - MinDistance)`。这种曲线不符合物理规律，但在开阔关卡中常用于背景环境音，因为它变化均匀、易于预测。
- **对数衰减（Logarithmic / Inverse Distance）**：最接近现实的曲线，近处音量剧烈下降，远处趋于平缓。Unity中称为"Logarithmic Rolloff"。适合爆炸、枪声等需要强烈距离感的音效。
- **对数曲率衰减（Logarithmic Rolloff with Rolloff Factor）**：在对数衰减基础上引入滚降因子（Rolloff Factor），值为1时等同于标准对数，值越大衰减越急剧。FMOD Studio中此参数范围通常为0到10。
- **自定义曲线（Custom Curve）**：设计师手动绘制距离-音量曲线，完全打破物理约束，用于特殊叙事需求，例如某个魔法结界内部声音保持恒定，越过边界瞬间消失。

### MinDistance 与 MaxDistance 参数

**MinDistance** 定义了声音不再随距离增大而增大的起始半径。在小于MinDistance的范围内，音量保持为最大值（归一化为1.0）。这个参数非常重要——一个爆炸声的MinDistance可能设置为5米，而一只虫鸣的MinDistance仅为0.3米，两者差异直接影响玩家对声源"体量"的感知。

**MaxDistance** 是声音完全消失的距离阈值。超过此距离，引擎将音量视为0并停止处理该声源。错误地将MaxDistance设置过大（如将一声脚步声设为500米）不仅听感不真实，还会导致引擎在整个关卡范围内持续计算该声源，白白消耗CPU资源。

### 方向衰减（锥形衰减）

除距离外，声源的朝向也会影响音量，这通过**声锥（Sound Cone）**模型实现。声锥由三个参数定义：

- **内锥角（Inner Cone Angle）**：通常为角度值，例如60°，在此范围内声音以全音量播放。
- **外锥角（Outer Cone Angle）**：例如120°，超出此角度声音衰减至外锥音量。
- **外锥音量（Outer Cone Gain）**：例如设为0.1，即方向偏离声源正面时，最低音量为原始音量的10%。

声锥模型常用于模拟具有方向性的声源，如喇叭、角色的嘴部语音，或单向旋转的机器。

### 优先级系统

当场景中同时存在超过引擎最大同声道数（例如Unity默认的32个音频声道）的活跃声源时，引擎需要决定哪些声源被播放，哪些被裁剪（Voice Stealing）。优先级（Priority）参数（Unity中范围为0到256，0为最高优先级）配合衰减模型共同决定裁剪顺序。

实际裁剪逻辑通常为：**计算听者处的感知音量 = 声源原始音量 × 距离衰减系数**，然后按优先级分组，组内再按感知音量排序，从低到高裁剪直至声道数满足限制。因此即使一个声源优先级很高，若其在衰减后音量几乎为0，引擎仍可能将其裁剪。

## 实际应用

**FPS游戏枪声设计**：一把手枪的音效通常将MinDistance设为0.5米，MaxDistance设为80米，使用对数曲线，让枪声在近距离时极为响亮，15米外已明显变小，保证玩家能通过音量迅速判断威胁远近。

**开放世界环境音**：鸟鸣、流水等环境音往往使用自定义曲线，在20米内保持较高音量，20-50米缓慢线性下降，营造浸入感而非物理精确性。MaxDistance限制在60米，避免音频系统在玩家远处仍持续计算数百个环境音源。

**NPC语音**：NPC说话声通过声锥设置（内锥60°/外锥180°）模拟人嘴朝向，当玩家绕到NPC背后时，语音音量降低至40%，增加空间真实感。优先级设为高值（Unity中设为64），确保剧情对话不被裁剪。

## 常见误区

**误区一：将线性衰减视为"真实"选项**。很多初学者认为线性衰减最直观，因此最真实。实际上物理声音遵循平方反比定律，对应对数衰减曲线。线性衰减会让声音在近距离时感觉"太远"，在远距离时感觉"太近"，只适合特殊风格化场景。

**误区二：忽略MinDistance导致"巨型声源"问题**。将爆炸声或环境音的MinDistance留在默认值0.1米，会导致玩家进入该半径内（几乎只有贴近声源时）才能听到全音量，大多数情况下声音总是处于衰减状态，显得遥远而无力。正确做法是根据声源"物理尺寸"或叙事意图设置有意义的MinDistance。

**误区三：用高优先级"保护"所有声音**。将项目中大部分音效优先级都设为最高（Priority = 0），反而使优先级系统完全失效，引擎只能靠衰减后音量随机裁剪，可能导致重要的近处声音被遥远但优先级相同的声源挤掉。应当仅将少数关键音效（如玩家受伤音、剧情语音）设为最高优先级，其余按重要性梯度分配。

## 知识关联

音频衰减模型建立在**Audio Source与Listener**的基础概念之上：距离衰减的计算本质上是Audio Source位置与Listener位置之间的三维欧几里得距离运算，方向衰减依赖Audio Source的朝向向量与Listener方向向量的夹角计算。没有这两个空间实体，衰减模型无从计算。

在工程实现层面，衰减模型与**空间音频（Spatializer）**和**混响区域（Reverb Zone）**密切配合：衰减模型决定干声（Dry Signal）的音量，而混响系统则根据同一距离参数计算湿声（Wet Signal）比例，两者共同构成完整的三维音频空间感。熟悉衰减模型的参数逻辑，是进一步调整HRTF头部相关传递函数和环境混响的重要前提。