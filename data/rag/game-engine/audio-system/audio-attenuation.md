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
---
# 音频衰减模型

## 概述

音频衰减模型（Audio Attenuation Model）描述了游戏引擎中声音强度随距离和方向变化而减弱的数学规律。当一个 Audio Source 距离 Audio Listener 越远，玩家听到的音量就越小，这个"随距离降低音量"的过程并非随意为之，而是由具体的衰减曲线函数精确控制的。不同的衰减公式会产生截然不同的听觉体验——有些声音会突然消失，有些则平滑渐出。

音频衰减的概念源于物理声学中的**平方反比定律**（Inverse Square Law），该定律表明声音强度与距离的平方成反比：$I = \frac{P}{4\pi r^2}$，其中 $I$ 为声音强度、$P$ 为声源功率、$r$ 为距声源的距离。游戏引擎在此物理基础上进行了工程化简化与艺术化调整，引入了可配置的曲线编辑器，允许音频设计师脱离纯物理约束，为游戏世界中的声音定制专属的衰减行为。

在实时游戏场景中，一张地图上可能同时存在数十乃至数百个 Audio Source，衰减模型不仅决定玩家的沉浸感，还直接影响引擎的**声音优先级裁剪**（Voice Culling）——距离过远、音量衰减至阈值以下的声音将被系统自动停止计算，从而节省 CPU 和内存资源。

---

## 核心原理

### 距离衰减曲线类型

游戏引擎（以 Unity 和 Unreal Engine 为代表）通常提供以下几种标准衰减模型：

- **线性衰减（Linear）**：音量从 `MinDistance` 到 `MaxDistance` 之间按比例均匀下降，公式为 $V = 1 - \frac{r - r_{min}}{r_{max} - r_{min}}$。这种模式听起来不自然，但设计直观，常用于 UI 音效或背景音乐的淡出。

- **对数衰减（Logarithmic / Inverse）**：模拟真实物理的平方反比，近距离音量下降极快，远距离下降趋于平缓。Unreal Engine 将此模式称为 `Natural Sound`，是三维环境声效的默认选择。

- **自定义曲线（Custom Curve）**：Unity 的 `AudioSource` 组件允许在 Inspector 中直接绘制音量-距离曲线，设计师可以为特定声音（如远处炮声在 50 米时音量骤降）定制非标准衰减行为。

三种模型在 `MinDistance = 1m, MaxDistance = 50m` 的条件下，在 $r = 10m$ 处的相对音量差异可超过 40%，选型错误会让游戏声音显得"漂浮"或"突兀"。

### 方向性衰减（Directional Attenuation）

除距离外，声音的传播方向也影响音量。方向性衰减通过**内锥角（Inner Cone Angle）**和**外锥角（Outer Cone Angle）**两个参数定义：

- 在 Inner Cone 范围内（如 60°），声音以全音量播放；
- 在 Inner Cone 与 Outer Cone 之间的过渡区域，音量按 `Cone Outside Volume`（通常设为 0~0.3）平滑过渡；
- 超出 Outer Cone（如 120°）后，音量固定在 `Cone Outside Volume` 值。

这一机制常用于模拟有方向性的声源，例如：NPC 角色的嘴部发声、喇叭广播、单向的排气管声效。Unreal Engine 中对应参数位于 `Attenuation Shape` 设置内的 `Cone` 形状选项。

### 最小距离与最大距离

衰减模型中有两个关键边界参数：

- **MinDistance（最小距离）**：在此距离以内，音量保持最大值（即 1.0），不会因靠近声源而继续增大。这防止了玩家站在声源内部时出现"无限响"的问题。典型枪声的 MinDistance 设为 0.5~2 米。
- **MaxDistance（最大距离）**：超出此距离后，Audio Source 要么音量降为 0 并停止混音计算，要么在某些引擎中维持一个极小的背景音量下限。Unity 中该参数直接影响 Voice Culling 的触发。

---

## 实际应用

**开放世界中的远程炮击声**：在《原神》类开放世界游戏中，炮击或爆炸音效需要在数百米外依然可辨识，但不能压过近距离对话。设计师通常将爆炸声的 MinDistance 设为 5 米、MaxDistance 设为 300 米，并使用自定义曲线在 50~150 米区间内人为减缓衰减速率，制造"远处传来的厚重感"。

**室内 NPC 对话**：NPC 走廊对话通常将 MaxDistance 压缩至 8~12 米，使用线性衰减，确保玩家必须靠近才能触发语音，避免多个 NPC 同时广播造成混乱。

**Unreal Engine 的 Attenuation Asset**：Unreal 将衰减设置抽象为独立的 `Sound Attenuation` 资产，多个 `Sound Cue` 可以共享同一个衰减资产，修改一处即影响所有引用它的音效，大幅提升了大型项目中的声音管理效率。

---

## 常见误区

**误区一：MaxDistance 越大越好**
许多初学者认为 MaxDistance 设得越大，声音"覆盖范围"越广越真实。实际上，过大的 MaxDistance 会导致引擎同时混音大量远距离（但实际音量接近零）的 Audio Source，浪费混音通道资源。游戏中通常设定一个**Voice Budget**（如最多 32 或 64 个同时活跃声音），过大的 MaxDistance 会"占用名额"而不产生任何可感知的听觉贡献。

**误区二：对数衰减总是比线性衰减更真实**
对数衰减确实更符合物理定律，但在游戏设计中"真实"不等于"好听"。室内混响场景、魔法音效、UI 反馈等场景下，线性甚至自定义的非物理曲线能带来更舒适的玩家体验。衰减模型的选择应服务于**玩法感受**，而非单纯模拟物理。

**误区三：方向性衰减与空间声像（Panning）是同一件事**
空间声像（Stereo Panning）控制的是声音在左右耳之间的分布，是二维的平移效果。方向性衰减（Cone Attenuation）控制的是声源自身朝向与听者相对角度导致的**音量增减**，是三维的强度变化。两者在引擎中属于不同的处理阶段，可以独立调节。

---

## 知识关联

音频衰减模型直接建立在 **Audio Source 与 Audio Listener** 的位置关系之上——没有 Source 和 Listener 的空间坐标，衰减公式中的距离参数 $r$ 就无从计算。理解了 Source/Listener 的组件结构之后，衰减模型是让两者"发生关系"的数学桥梁：Source 的世界坐标与 Listener 的世界坐标相减，得到距离向量，再代入衰减曲线，输出最终的混音音量权重。

在引擎声音优先级系统中，衰减模型输出的瞬时音量值直接作为该 Audio Source 的**优先级打分依据**之一：一个衰减后音量为 0.02 的远距离声音，在 Voice Budget 不足时会优先被剔除。这使得衰减模型不仅是听觉效果的塑造者，也是引擎运行时资源调度的重要输入信号。
