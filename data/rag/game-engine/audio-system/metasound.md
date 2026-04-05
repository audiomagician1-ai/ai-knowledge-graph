---
id: "metasound"
concept: "MetaSound(UE5)"
domain: "game-engine"
subdomain: "audio-system"
subdomain_name: "音频系统"
difficulty: 3
is_milestone: false
tags: ["UE5"]

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
updated_at: 2026-03-26
---



# MetaSound（UE5）

## 概述

MetaSound 是虚幻引擎 5（Unreal Engine 5）中引入的新一代程序化音频系统，于 UE5.0 正式发布，取代了 UE4 时代的 Sound Cue 系统。其核心设计思想是将音频处理建模为一张有向无环图（DAG），每个节点代表一个 DSP 运算单元（如振荡器、滤波器、混音器），边代表音频信号或控制参数的流向。开发者通过连接这些节点构造完整的音频信号链路，并在运行时由 MetaSound 引擎实时执行 DSP 图的计算。

MetaSound 脱胎于 Epic Games 内部对 Wwise、FMOD 等中间件的反思。传统中间件将音频资产与行为逻辑打包在外部工具中，UE 项目必须通过插件桥接。MetaSound 的目标是将"程序化声音合成"与"游戏逻辑驱动"统一到引擎内部，做到零外部依赖即可实现同等甚至更强的运行时音频行为。它的实际意义在于：声音设计师可以直接在 MetaSound Editor 中编写类似着色器的音频程序，声音的音高、节奏、音色都可以随游戏状态实时变化，而非仅靠预录音频片段的切换。

## 核心原理

### DSP 图执行模型

MetaSound 的运行时以"音频渲染块（Audio Render Block）"为单位推进，默认块大小为 **256 个采样点**，对应 44100 Hz 采样率下约 5.8 ms 的延迟窗口。每帧引擎调用一次图执行，按拓扑顺序依次计算各节点。节点之间传递的数据分为两种类型：**Audio 类型**（每块 256 个 float 样本的缓冲区）和**标量触发/参数类型**（单一值或 Trigger 事件）。这一设计使得音频计算与游戏线程解耦，DSP 图运行在专属音频线程上，避免了游戏帧率波动对声音输出造成卡顿。

### 节点类型与内置 DSP 算子

MetaSound 提供了丰富的内置节点，涵盖以下主要类别：
- **生成类**：Sine、Saw、Square、Noise 等波形振荡器，以及 Wave Player（播放音频资产）。
- **处理类**：Biquad Filter（双二阶滤波器，可配置为 LPF/HPF/BPF）、Delay、Reverb Send、Envelope Follower。
- **控制类**：ADSR Envelope（Attack/Decay/Sustain/Release）、LFO、Random Get、Trigger Compare。
- **数学类**：Add、Multiply、Map Range（将参数值从一个区间线性映射到另一区间）。

其中 Map Range 节点的公式为：

$$\text{Output} = \text{OutMin} + \frac{(\text{Input} - \text{InMin})}{(\text{InMax} - \text{InMin})} \times (\text{OutMax} - \text{OutMin})$$

这使得开发者可以将任意游戏变量（如角色速度 0–600）直接映射为滤波器截止频率（200 Hz–4000 Hz），无需在蓝图中额外转换。

### 输入/输出接口与蓝图通信

每个 MetaSound 资产都有显式声明的 **Input 引脚**和 **Output 引脚**，构成其对外的"接口协议"。Input 引脚支持的类型包括 Float、Int32、Bool、Trigger、Audio Buffer 等。游戏逻辑（蓝图或 C++）通过调用 `UAudioComponent::SetFloatParameter`、`SetTriggerParameter` 等函数在运行时向 MetaSound 推送参数值，MetaSound 在下一个渲染块开始时读取最新值。这与 Sound Cue 只能在播放前烘焙参数有本质区别——MetaSound 实现了**真正的逐帧动态调制**。

### MetaSound Patch 与复用机制

MetaSound 支持将子图封装为 **MetaSound Patch**（.metasoundpatch 资产），类似 HLSL 的函数库概念。一个"湿混响房间"效果链可以封装为 Patch，在多个 MetaSound Source 资产中作为单一节点复用，并暴露"混响时间"等参数供外部覆盖。这解决了 Sound Cue 系统中重复音频逻辑必须依赖蓝图函数库的痛点。

## 实际应用

**程序化脚步声系统**：根据角色移动速度（0–600 cm/s）和地面材质（枚举类型）实时合成脚步声，而非切换预录片段。速度值通过 Map Range 节点映射为 Envelope 释放时间，地面材质类型通过 Trigger Compare 节点路由到不同的 Wave Player，实现物理驱动的脚步节奏与音色变化。

**自适应引擎音效**：赛车游戏中，发动机 RPM（如 800–8000）作为 Float Input 传入 MetaSound，驱动 Saw 波振荡器的频率参数，同时调制 Biquad Filter 的截止频率，使高转速时音色更刺耳。整套合成逻辑在引擎内部完成，无需 Wwise 的 RTPC 系统。

**环境 Ambience 的程序化变奏**：雨声 MetaSound 接收"降雨强度"Float 参数，通过 LFO 对 Noise 节点的音量做周期性调制，Biquad Filter 的 Q 值随降雨强度线性增大，模拟暴雨时雨滴打击声的密度变化，且每次播放因 Random Get 节点而产生细微不同的节奏模式。

## 常见误区

**误区一：MetaSound 等同于 Sound Cue 的升级版**
Sound Cue 是一个基于随机/混音逻辑的**资产调度系统**，节点之间流动的是音频资产引用；MetaSound 的节点之间流动的是**实时 DSP 信号和参数值**，具备真正的信号合成能力。两者的根本差异不在 UI，而在于是否能生成原本不存在于任何音频文件中的声音。

**误区二：所有参数更新都是实时的**
游戏线程向 MetaSound 推送的参数更新不是零延迟的——它们在下一个 256 采样块的边界才生效，约有 5.8 ms 的延迟。在需要精确同步（如节拍对齐）的场景中，应使用 Trigger 类型配合 MetaSound 内部的时间节点（如 BPM To Seconds），而非依赖外部精确计时。

**误区三：MetaSound 可以完全替代 Wwise/FMOD**
MetaSound 擅长单一声音对象的程序化合成，但 UE5.0–5.3 版本中尚不具备 Wwise 的全局混音矩阵、跨平台音频总线管理和自适应音乐分段系统（Interactive Music）等企业级功能。大型项目仍可能需要 MetaSound 负责合成层，Wwise 负责混音路由层的分工架构。

## 知识关联

学习 MetaSound 前需要理解**音频中间件**（如 Wwise、FMOD）的核心概念：RTPC（实时参数控制）、Event 触发机制、音频总线路由。MetaSound 的 Input/Output 接口设计直接对标 RTPC 的参数绑定思路，理解 RTPC 后更容易理解为何 MetaSound 要将 Float/Trigger 分为不同数据类型。同时，DSP 基础知识（采样率、奈奎斯特频率、滤波器传递函数）能帮助开发者正确配置 Biquad Filter 等节点的参数范围，避免出现混叠或爆音。MetaSound 的 Patch 机制与 UE 材质系统的 Material Function 在设计哲学上高度一致，有 UE 材质开发经验的开发者能快速迁移模块化封装的思维方式。