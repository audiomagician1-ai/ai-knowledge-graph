---
id: "sfx-sa-distance-model"
concept: "距离模型"
domain: "game-audio-sfx"
subdomain: "spatial-audio"
subdomain_name: "空间音频"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 距离模型

## 概述

距离模型（Distance Model）是空间音频系统中用于计算声源音量随距离变化的数学规则集合，其核心任务是将听者与声源之间的欧几里得距离转换为增益系数（0.0 到 1.0 之间的乘数），从而模拟声音在三维空间中的自然衰减。不同于混响或方向感等音色维度的处理，距离模型专注于"响度随距离减小"这一单一物理现象的仿真与游戏化适配。

物理学中声强与距离的关系遵循**平方反比定律（Inverse Square Law）**：声强 I 与距离 r 的平方成反比，即 `I ∝ 1/r²`。这一规律由17世纪声学研究确立，意味着距离翻倍时声压级下降约6 dB。然而，游戏环境的几何约束、性能预算以及玩法设计需求，使得直接套用物理公式往往并不合适，因此各大音频中间件和引擎都提供了多种可配置的距离模型变体。

在OpenAL、FMOD、Wwise等主流音频API与中间件中，距离模型是空间化声音的必选配置项之一。正确设置距离模型能让玩家凭借音量判断敌人远近、感知环境规模，是沉浸感构建的基础声学工具。

---

## 核心原理

### 平方反比模型与线性模型的数学差异

OpenAL规范定义了六种标准距离模型，其中最常用的两种公式对比如下：

**Inverse Distance（倒数距离）模型**：
```
Gain = ReferenceDistance / (ReferenceDistance + RolloffFactor × (distance - ReferenceDistance))
```

**Linear Distance（线性距离）模型**：
```
Gain = 1 - RolloffFactor × (distance - ReferenceDistance) / (MaxDistance - ReferenceDistance)
```

其中 `ReferenceDistance` 是增益为1.0的基准距离，`RolloffFactor` 是衰减速率系数，`MaxDistance` 是线性模型中增益归零的截止距离。线性模型在 `MaxDistance` 处强制将增益降至0，会产生突然消失的听感，但在需要精确控制声音消失点的游戏场景（如触发式音效范围）中更易管理。

### ReferenceDistance、MaxDistance 与 RolloffFactor 的交互关系

三个参数共同决定距离模型的形状，改变任意一个都会产生与其他两个的联动效果：

- **ReferenceDistance**（参考距离）：听者处于该距离以内时，增益固定为1.0，不再增大。FMOD中默认值通常为1米，Wwise中称为"Min Distance"，默认1米。
- **MaxDistance**：只在Clamped变体中生效，超出该距离后增益不再继续衰减（保留在某个最低值而非归零）。
- **RolloffFactor**：值为1.0时近似物理真实；值为0时完全不衰减；Wwise的"Attenuation Shape"曲线本质上是对该系数在不同距离区间的分段重写。

在大型开放世界游戏中，RolloffFactor通常设置为0.5甚至更低，目的是让远处的环境音（如远方炮声）在超出物理预期的距离内仍清晰可闻，服务玩法而非物理准确性。

### Clamped 变体与距离截断行为

OpenAL还定义了每种模型对应的"Clamped"版本（如Inverse Distance Clamped），当 `distance < ReferenceDistance` 时，距离值被夹持（Clamp）到ReferenceDistance，防止声源过于接近时音量爆表——这在第一人称射击游戏中尤为重要，因为枪口距离麦克风位置可能为零米。无Clamped保护的模型在 `distance → 0` 时增益趋于无穷大，会直接导致音频削波（Clipping）失真。

---

## 实际应用

### Wwise中的Attenuation编辑器与距离模型映射

Wwise将距离模型封装在**Attenuation（衰减）共享集**中，设计师通过图形化曲线编辑器绘制Volume随距离变化的关系，底层实际对应的是Linear或Logarithmic距离模型的变体。典型的步枪枪声配置：Min Distance = 0.5 m，Max Distance = 80 m，曲线在15–40 m区间使用对数斜率，在40–80 m区间改用更陡的线性斜率，模拟声音穿越开阔地的快速消衰。

### Unity AudioSource的距离模型设置

Unity的AudioSource组件提供"Logarithmic Rolloff"（对数衰减，接近物理真实）、"Linear Rolloff"（线性衰减）和"Custom Rolloff"（自定义曲线）三个选项，对应Max Distance参数默认值为500单位（Unity世界单位，通常等同于米）。使用Custom Rolloff时，Unity内部将设计师绘制的曲线转换为查找表（LUT），在运行时插值计算，计算开销低于实时公式求解。

### 2D俯视角游戏中的距离模型特殊处理

在俯视角游戏（如《哈迪斯》风格的ARPG）中，声源与听者的Y轴差异往往被人为压缩——引擎会将3D距离计算限制在XZ平面，或对Y轴距离乘以0.3的压缩系数，防止楼上楼下的声音因垂直距离过大而提前消失，这是距离模型在2.5D场景中最常见的定制化调整。

---

## 常见误区

### 误区1：RolloffFactor越大声音越"真实"

许多初学者认为将RolloffFactor设为1.0（对应物理平方反比）就是最正确的选择。但物理真实的衰减在大多数游戏场景中会使远处声音过早消失。《荒野大镖客：救赎2》的音频团队公开分享过其大量使用低于物理值的RolloffFactor来保持世界环境音的存在感。游戏音频的目标是**感知真实**而非**物理真实**。

### 误区2：距离模型等同于衰减曲线（Attenuation Curve）

距离模型是通用数学公式，输入距离、输出增益；衰减曲线是设计师手绘的自定义映射关系，是对距离模型的替代或覆写。Wwise中的Attenuation曲线会完全绕过引擎默认的距离模型公式，两者不是同一层次的概念，不能互换使用。

### 误区3：MaxDistance是声音完全听不见的距离

MaxDistance在Inverse Distance Clamped模型中是增益停止继续衰减的距离，不是增益归零的距离——超过MaxDistance后音量会保持在一个较低但非零的值。只有Linear Distance模型才能在MaxDistance处将增益精确归零。混淆这两种行为会导致"声音该消失却未消失"的Bug。

---

## 知识关联

距离模型建立在**衰减曲线**的概念之上——衰减曲线为距离模型提供了可视化的编辑界面和自定义覆盖机制，理解衰减曲线中的最小/最大距离参数是正确配置距离模型的前提。在Ambisonics空间音频系统中，距离模型负责增益维度，而Ambisonics编码负责方向维度，二者共同构成完整的三维声场定位，但各自独立运算互不干扰。

学习完距离模型后，下一个自然延伸的概念是**多普勒效应**：多普勒效应处理的是声源相对运动引起的音调变化，与距离模型处理的静态距离-音量关系形成互补——两者在移动声源场景中同时激活，多普勒公式中的相对速度参数需要引擎已知声源在每帧的距离变化量，这正是距离模型持续追踪的数据。