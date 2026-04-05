---
id: "ta-scalability"
concept: "画质可伸缩性"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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


# 画质可伸缩性

## 概述

画质可伸缩性（Scalable Quality）是指游戏引擎通过预设的画质分级档位，在不同硬件配置上自动调整渲染参数组合，以确保目标帧率与视觉效果之间取得最佳平衡的技术体系。以虚幻引擎的四档分级 Low / Medium / High / Epic 为例，每一档位实质上是数十个控制台变量（CVar）的快照集合，而非单一开关。

这一概念的工程化实现可追溯至2012年前后 PC 游戏面对显卡性能断层时期。彼时开发者发现，单纯依赖驱动程序的自动降级会产生不一致的视觉割裂感，因此引入了手动分级的预设组合思路。虚幻引擎4在此基础上形成了 `Scalability.ini` 配置文件驱动的完整框架，并沿用至虚幻引擎5。

画质可伸缩性的价值在于：同一份代码资产可以覆盖从移动端到高端 PC 的硬件谱系，而无需为每个平台单独维护渲染管线分支。这使得技术美术人员能够在单一项目内同时照顾到配置仅有 GTX 1060 的玩家和拥有 RTX 4090 的玩家，GPU 预算差距往往超过10倍。

---

## 核心原理

### 分级配置文件的结构

虚幻引擎的 `Scalability.ini` 将可伸缩性分为若干独立组（Group），常见组包括 `sg.ResolutionQuality`、`sg.ShadowQuality`、`sg.PostProcessQuality`、`sg.TextureQuality`、`sg.EffectsQuality` 等。每个组内部针对 0（Low）至 3（Epic）四个整数索引分别写入不同的 CVar 值。例如：

```ini
[ShadowQuality@2]
r.ShadowQuality=4
r.Shadow.CSM.MaxCascades=3
r.Shadow.RadiusThreshold=0.01
```

当玩家选择 High 档（索引2）时，引擎会批量 apply 该组下所有 CVar，单次调用的 CVar 数量在中型项目中通常达到 30～80 个。

### 分辨率伸缩与超分辨率的交叉

`sg.ResolutionQuality` 控制的是内部渲染分辨率相对于输出分辨率的百分比，取值范围为 `[10, 100]`。Low 档默认值为 50（即半分辨率渲染），Epic 档为 100。当项目集成 TSR 或 DLSS 后，Low 档的实际渲染像素数可以进一步降低至输出分辨率的 33%，但最终图像质量由超分算法补偿。这意味着分辨率伸缩组的数值含义在引入超分后发生了根本性转变——它从"渲染分辨率百分比"变成了"超分输入分辨率百分比"，技术美术在设置 Low 档数值时必须同步考量超分算法的最低可用输入比例。

### 档位与帧率目标的绑定方式

自动化画质伸缩（Auto Scalability）依赖帧率采样窗口决定是否降档或升档。虚幻引擎内置的 `FGameUserSettings::RunHardwareBenchmark()` 会在启动时执行约 5 秒的基准测试，根据 GPU 合成得分将玩家初始化至对应档位。运行时动态伸缩则通过 `UGameUserSettings` 中的 `FrameRateLowerBound`（默认 20fps）和 `FrameRateUpperBound`（默认 100fps）触发档位升降，采样窗口长度默认为 30 帧。这两个阈值在移动端项目中几乎必须覆写，因为移动端目标帧率通常锁定在 30fps 或 60fps。

---

## 实际应用

**主机游戏的"性能/画质"双模式**：以PlayStation 5上常见的实现为例，技术美术团队会在 `sg.ShadowQuality` 分组中将性能模式对应至索引1（Medium），画质模式对应至索引3（Epic），并在 `DefaultEngine.ini` 中禁用索引0和2，强制只暴露两个档位给玩家。这是通过重写 `GetRecommendedResolutionQuality()` 并锁定 `bUseVSync` 实现的。

**手游的热更新档位调整**：Unity 的 Quality Settings API（`QualitySettings.SetQualityLevel(int index)`）和虚幻的 CVar 体系均支持在运行时无缝切换档位，这使得手游运营团队可以在服务器端下发新的 `Scalability.ini` 补丁包，针对因系统更新导致性能下降的特定机型批量调低默认档位，整个过程无需更新客户端包体。

**帧预算感知的局部伸缩**：部分项目不采用全局档位切换，而是仅对单一高成本组启用动态伸缩。例如在战场场景特效密集时单独降低 `sg.EffectsQuality`，而保持 `sg.TextureQuality` 和 `sg.ShadowQuality` 不变。这种策略要求技术美术为每个 CVar 组标注其 GPU 成本权重，通常借助 `stat GPU` 和 `r.ProfileGPU` 数据建立成本表。

---

## 常见误区

**误区一：认为四档是固定的四个数值**
Low/Med/High/Epic 的对应索引 0/1/2/3 只是引擎默认命名，项目完全可以通过 `GScalabilityQualityLevels` 注册更多自定义档位（如增加"Ultra"作为索引4），也可以将某些组的高档和低档合并。错误地认为"四档是系统强制约束"会导致技术美术在面对特殊需求时放弃定制化的可能性。

**误区二：所有 CVar 降低都能线性降低 GPU 成本**
`sg.TextureQuality` 降至 Low 主要减少的是显存占用和纹理流送带宽，对 GPU 着色器计算成本的影响几乎为零。因此如果目标是提升帧率，优先降低纹理质量档位的策略是无效的；正确做法是先通过 `stat GPU` 确认瓶颈在 Shading 还是 Bandwidth，再选择对应的伸缩组进行降档。

**误区三：Epic 档就是"不做任何限制"**
Epic 档（索引3）仍然受到 `r.MaxAnisotropy`、`r.Shadow.MaxResolution` 等硬性上限 CVar 的约束，这些上限 CVar 独立于 Scalability 组之外。在项目质量评审中，有时会发现 Epic 档的阴影贴图分辨率比美术预期低，根本原因正是遗漏了对 `r.Shadow.MaxResolution`（默认值2048）的单独修改。

---

## 知识关联

画质可伸缩性建立在**性能预算分配**的量化结果之上：只有当技术美术已经明确了每个档位的 GPU 帧预算（如 Low 档目标8ms、High 档目标12ms），才能有依据地为每个 CVar 组的各档位赋值，否则档位参数的设定将缺乏可量化验证的标准。

掌握画质可伸缩性后，自然延伸至**渲染特性开关**的精细控制：分级配置只能批量操控预定义的 CVar 组，而渲染特性开关允许技术美术在代码层面为单个材质节点、单个 Pass 甚至单个 DrawCall 绑定档位条件判断（如 `#if QUALITY_LEVEL >= 2`），实现比 CVar 组更细粒度的按需启用逻辑。两者共同构成了从粗粒度到细粒度的完整画质控制层级。