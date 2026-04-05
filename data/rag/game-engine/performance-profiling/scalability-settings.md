---
id: "scalability-settings"
concept: "可扩展画质设置"
domain: "game-engine"
subdomain: "performance-profiling"
subdomain_name: "性能剖析"
difficulty: 2
is_milestone: false
tags: ["配置"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 可扩展画质设置

## 概述

可扩展画质设置（Scalability Settings）是虚幻引擎（Unreal Engine）中一套预定义的渲染质量分级体系，允许开发者和玩家在 Low、Medium、High、Epic、Cinematic 五个档位之间切换，从而在视觉效果与运行性能之间取得平衡。每个档位本质上是一组 Console Variable（CVar）的批量赋值，单次切换可同时调整数十个底层渲染参数。

该系统最早在 UE4 时代以 `Engine Scalability Settings` 的名称正式落地，核心配置文件为 `BaseScalability.ini`，开发者可在项目的 `Config` 目录下覆盖默认值。Cinematic 档位是 UE4.15 之后才正式加入的第五档，专为过场动画和离线渲染场景设计，并不以实时 60fps 为目标。

在性能剖析工作流中，可扩展画质设置是定位帧率瓶颈的第一道筛查工具：若将画质从 Epic 降至 Low 后帧时（Frame Time）大幅下降，则瓶颈很可能在 GPU 渲染；若帧时几乎不变，则瓶颈更可能在 CPU 或游戏逻辑线程，而非渲染质量本身。

---

## 核心原理

### 五档位与 CVar 批量映射

五个档位对应的质量等级在内部用整数 0～4 表示（Low=0，Medium=1，High=2，Epic=3，Cinematic=4）。每个档位激活时，引擎会读取 `BaseScalability.ini` 中对应 `[TextureQuality@0]`、`[ShadowQuality@2]` 等节区，批量 `SET` 相关 CVar。例如，`sg.ShadowQuality` 从 0 切换到 3 时，会同时修改 `r.Shadow.MaxResolution`（从 512 提升至 2048）、`r.Shadow.RadiusThreshold` 等多个变量。整套系统使用约 7 个质量组（Texture、Shadow、AntiAliasing、PostProcess、Effects、Foliage、Shading），每组各自独立分级，互不耦合。

### 配置文件覆盖机制

项目级覆盖写入 `DefaultScalability.ini`，其优先级高于引擎默认的 `BaseScalability.ini`。若需要针对移动平台做额外限制，可在 `DefaultDeviceProfiles.ini` 中为特定设备型号绑定对应的 Scalability 档位。引擎启动时按 `Engine → Project → Platform → Device` 的顺序叠加读取，后者覆盖前者。

### 运行时切换与性能剖析配合

在运行时可通过控制台命令 `sg.OverallQuality 0`（切换至 Low）或 `sg.ShadowQuality 2`（单独调整阴影至 High）实时生效，无需重启编辑器或游戏。在 Unreal Insights 或 `stat GPU` 视图中，切换前后的 `Shadow Depths`、`BasePass`、`Translucency` 等 GPU Pass 耗时会立即反映变化，使剖析人员可以精确量化每个质量组对总帧时的贡献比例。

---

## 实际应用

**快速定位 GPU 瓶颈**：在目标机器上运行游戏，打开 `stat fps` 观察帧率，依次执行 `sg.OverallQuality 3`（Epic）、`sg.OverallQuality 0`（Low），若帧率从 24fps 跃升至 90fps，差距超过 3 倍，说明渲染负载极重，可进一步缩小到单组：先恢复 Epic，再单独执行 `sg.ShadowQuality 0` 观察阴影组是否是大头。

**移动端适配**：针对中端 Android 设备，开发者通常将 Foliage 固定在 Medium（`sg.FoliageQuality 1`），将 Shadow 固定在 Low（`sg.ShadowQuality 0`），而保留 Texture 在 High，以在视觉上优先保证贴图清晰度。这种"拆组"用法比整体档位切换更精细。

**Cinematic 渲染管线**：在 Movie Render Queue 中输出过场动画时，将 `sg.OverallQuality 4`（Cinematic）与 `r.MotionBlurQuality 4`、`r.DepthOfFieldQuality 4` 联用，可在离线渲染模式下解除实时帧率约束，输出用于宣传的高质量视频素材。

---

## 常见误区

**误区一：Epic 档等于"最高画质"**
Epic 是实时游戏场景的最高档，但 Cinematic 档在部分渲染特性（如光线追踪反弹次数、阴影贴图分辨率上限）上仍高于 Epic。将 Cinematic 当作游戏内正常运行档位会导致在主流 PC 上帧率跌破 10fps，因为该档位的 `r.Shadow.MaxResolution` 上限被放开至 4096 甚至更高。

**误区二：整体档位切换等于单个 CVar 的极值**
`sg.OverallQuality 3`（Epic）设置的 `r.Shadow.MaxResolution` 是 2048，而直接手写 `r.Shadow.MaxResolution 8192` 会超出 Scalability 系统的上限。两者并不等价，自定义 CVar 覆盖优先级高于 Scalability 分组，会在下次 Scalability 切换时被覆盖回去，导致配置失效。

**误区三：降低 Scalability 档位一定能解决卡顿**
如果瓶颈在游戏线程（例如每帧运行复杂 AI 寻路或大量 Tick 调用），将画质从 Epic 降至 Low 对帧时的改善幅度通常不超过 2ms，因为 `sg.OverallQuality` 仅控制渲染 CVar，不影响蓝图执行、物理模拟或动画计算开销。

---

## 知识关联

可扩展画质设置建立在**性能剖析概述**的基础上——只有理解帧时、GPU/CPU 瓶颈分类、`stat GPU` 与 `stat unit` 的含义，才能正确解读档位切换前后数据的变化意义。实践中，它通常是剖析流程的第一步：宏观确认瓶颈类别，再进入 RenderDoc 帧捕获或 Unreal Insights 的时间线视图做精细分析。

在项目发布阶段，可扩展画质设置与**设备画质分级（Device Profile）**系统深度联动，将 Scalability 档位绑定到具体硬件规格（如 GPU 基准分数阈值），实现自动适配，无需玩家手动调节。理解 `BaseScalability.ini` 的节区结构，也是后续自定义渲染管线（Custom Shading Model）时避免配置冲突的必要前提。