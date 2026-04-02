---
id: "sfx-am-attenuation"
concept: "衰减曲线"
domain: "game-audio-sfx"
subdomain: "audio-middleware"
subdomain_name: "音频中间件"
difficulty: 4
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 衰减曲线

## 概述

衰减曲线（Attenuation Curve）是游戏音频中间件（如 Wwise、FMOD）用于描述声源音量随距离变化规律的可编辑函数图形。它将"监听者与声源之间的三维距离"映射为"音量增益（dB）或线性音量比（0.0–1.0）"，决定了玩家在何处开始听到某个声音、何处完全听不到，以及中间过渡的精确形状。

衰减的物理基础来自声学中的**平方反比定律**：自由空间中声强与距离的平方成反比，即每距离加倍，声压级下降约 6 dB。然而现实游戏场景远比理想空间复杂——室内混响、地形遮挡、材质吸收都会改变衰减行为——因此中间件提供了自定义曲线而非强制套用物理公式，允许设计师按游戏世界的风格与比例手动塑造衰减形状。

在 Wwise 中，衰减曲线编辑器以 ShareSet 形式存在，同一条衰减曲线可被多个声音对象共享复用，修改一次即全局生效，这对大型项目的维护效率至关重要。FMOD Studio 的对应功能则嵌入在事件的 3D 属性面板中，称为"Min/Max Distance"配合可绘制的自定义衰减形状。

---

## 核心原理

### 距离范围参数：MinDistance 与 MaxDistance

衰减曲线由两个距离锚点界定工作区间。**MinDistance**（最小距离，默认常见值为 1 m 或游戏单位 100 u）标记音量保持最大值（0 dB 增益）的内圆半径；在此范围内，无论声源与监听者多近，音量不再继续提升，防止极近距离时爆音。**MaxDistance**（最大距离）标记音量衰减至 −∞ dB（即完全静音）的外圆半径。超出 MaxDistance 后，Wwise 的 Virtual Voice 系统会将该声音设为虚拟（Virtual），暂停 CPU 处理，节省性能。两个参数共同确定曲线的 X 轴跨度，设计师需根据游戏世界比例（写实 vs 卡通夸张）仔细校准它们，而非使用默认值。

### 曲线形状与控制点

曲线 Y 轴表示音量（dB 或线性），X 轴表示归一化距离（0.0 = MinDistance，1.0 = MaxDistance）。Wwise 提供以下几种内置曲线插值类型，每种产生不同的感知结果：

- **Linear（线性）**：音量与距离成正比下降，数学上简单但听感突兀；
- **Logarithmic（对数）**：近距离衰减快、远距离趋缓，最接近物理平方反比规律的感知等效；
- **S-Curve（S 形）**：近距保持丰满，中段急速衰减，远段平缓拖尾，适合英雄武器等需要"大范围可感知"的音效；
- **Exponential（指数）**：衰减极陡，适合仅在极近处可闻的细节音效（如脚步）。

设计师还可在曲线上添加多个自定义控制点，拼接不同插值段，例如 0–0.3 段使用对数曲线模拟真实衰减，0.3–1.0 段切换为线性以人为延长可听范围。

### 多维度衰减：音量之外的曲线通道

衰减曲线并非只控制音量。Wwise 的 Attenuation ShareSet 包含多个独立可配置的曲线通道，每个通道均可绘制不同形状：

| 通道名称 | 作用 |
|---|---|
| Volume | 整体音量增益（dB） |
| Low-pass Filter | 随距离增加的低通截止频率（Hz），模拟高频空气吸收 |
| High-pass Filter | 随距离变化的高通截止 |
| Spread | 立体声/全景声扩展宽度（0–100%） |
| Focus | 3D 声像集中度（Wwise 2019.1 引入） |

其中 Low-pass Filter 通道尤为关键：真实世界中高频（>2 kHz）随距离衰减比低频快得多（空气吸收系数在 20°C、50% 湿度下约 0.5 dB/100 m@1 kHz，远大于低频），因此单独绘制一条随距离增强的低通曲线，能在不改变音量的情况下大幅提升距离感的真实性。

---

## 实际应用

**步枪射击音效**：近战（0–5 m）保持原始冲击感，使用 S 形曲线让枪声在 5–80 m 范围内仍清晰可辨，80 m 后使用指数段急速衰减至静音；同时配置 Low-pass 通道，在 MaxDistance（150 m）处将截止频率压至 800 Hz，模拟远距离枪声的闷响特征。

**环境循环音（瀑布）**：MinDistance 设为 3 m，MaxDistance 设为 40 m，采用对数曲线；同时将 Spread 通道配置为从 20%（近距，定向感强）逐渐增加到 100%（远距，声场包围感），让玩家靠近瀑布时声音从"背景氛围"变为"具体方向性声源"。

**NPC 对话**：使用 Linear 曲线配合极小的 MaxDistance（约 8–12 m），确保对话声音不会在嘈杂场景中传播过远干扰沉浸感；为不同 NPC 重用同一 Attenuation ShareSet，通过 Wwise 的 Override Attenuation 选项对特殊剧情 NPC 单独定制曲线。

---

## 常见误区

**误区一：MaxDistance 越大越好**
许多初学者将 MaxDistance 设置为极大值（如 500 m）以"保险"，但这会阻止 Virtual Voice 机制的触发，导致大量不可听声音仍占用 CPU 运算，在密集场景中可能引发性能瓶颈。正确做法是实测玩家能察觉声音的最远距离，将 MaxDistance 设为该值的约 110%，让引擎及时将超出范围的声音虚拟化。

**误区二：用单一音量曲线模拟所有距离感**
仅调整音量通道而忽略 Low-pass Filter 通道，会导致远处声音听起来像"安静但清晰"的声音，而不像真正遥远的声音。现实中距离感的 60% 以上来自高频损失而非纯粹音量降低，缺少频率衰减的设计会让游戏世界显得"扁平"。

**误区三：混淆衰减曲线与混响发送量**
衰减曲线控制直达声（Dry）的音量与频率，而混响（Wet 信号）的距离感知需要通过独立的 Auxiliary Send 配置实现——随距离增加 Wet/Dry 比例，让远处声音听起来"被空间淹没"。两套机制协同配置才能产生完整的距离感，单靠衰减曲线无法模拟混响包围感。

---

## 知识关联

**前置概念——混合容器（Blend Container）**：混合容器中的 Blend Tracks 可以按距离参数混合不同音频层，与衰减曲线形成互补——衰减曲线决定整体音量包络，而混合容器可在不同距离段切换不同的声音素材（如近距离使用 Close-mic 录音，远距离切换为 Room 录音），两者结合实现分层距离混音。

**后续概念——遮挡与阻隔（Obstruction & Occlusion）**：衰减曲线处理的是开放空间中纯距离引起的音量变化，遮挡与阻隔则在此基础上叠加几何体对声音传播路径的影响。Wwise 的 Obstruction 参数会额外施加一个 Low-pass 滤波器，与衰减曲线的 Low-pass 通道相加作用，设计师需避免两套系统的高频截止值叠加过度导致声音过度闷滞。

**后续概念——距离模型（Distance Model）**：距离模型是更底层的空间音频计算框架，定义了引擎如何将 3D 位置信息转换为衰减曲线的输入距离值（如是否考虑声源包围盒、是否使用自定义的距离计算函数），掌握衰减曲线后需进一步理解距离模型才能处理非点声源（如大型移动物体）的空间音频问题。