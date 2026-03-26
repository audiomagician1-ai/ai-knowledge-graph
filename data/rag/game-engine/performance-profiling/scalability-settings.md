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
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
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

可扩展画质设置（Scalability Settings）是Unreal Engine中一套预定义的渲染质量分级系统，允许开发者和玩家在运行时动态调整画面质量以适配不同硬件性能。该系统将数十个底层渲染参数（如阴影分辨率、后处理质量、特效细节等）打包为五个离散档位：**Low（低）、Medium（中）、High（高）、Epic（超高）和Cinematic（电影级）**，每个档位对应一组经过UE官方调优的参数组合。

该系统最早在UE4时代以`sg.*`控制台变量族的形式成型，在UE5中得到进一步扩展，Cinematic档位正式被纳入标准配置。其设计动机在于解决PC平台硬件配置差异巨大的问题——同一款游戏需要在集成显卡到旗舰GPU上均能运行，而手动为每种硬件组合编写配置不现实。

在性能剖析工作流中，可扩展画质设置是快速定位性能瓶颈类型的第一道工具。当剖析某个帧时间过长的场景时，将画质从Epic一键切换到Low，若帧率立即达标，则可以断定瓶颈在GPU渲染负载而非CPU逻辑；若帧率提升有限，则应转向CPU侧剖析。这种粗粒度的二分排查节省了大量性能剖析前期的盲目尝试。

---

## 核心原理

### 档位参数映射机制

每个档位本质上是一批`sg.*`控制台变量的预设值集合，定义在`Scalability.ini`配置文件中。以阴影质量为例，`sg.ShadowQuality`取值范围为0（Low）到4（Cinematic），其背后实际驱动的是`r.Shadow.MaxResolution`等十余个子变量。Epic档位下`r.Shadow.MaxResolution`默认为2048，而Low档位下降至512，即分辨率降低为1/4，阴影图所占显存从约16MB骤降至约1MB。

五个档位对应的整数值分别为：Low=0、Medium=1、High=2、Epic=3、Cinematic=4。在C++或蓝图中可通过`UGameUserSettings::SetOverallScalabilityLevel(int32 Value)`统一设置所有子类别，或单独调用`SetShadowQuality`、`SetTextureQuality`等方法精细控制各分类。

### 六大画质分类

可扩展画质设置将渲染参数划分为六个独立可调的类别：

- **ResolutionQuality**：内部渲染分辨率百分比，Low档默认为50%，即以半分辨率渲染后上采样输出，这是降低GPU像素填充率负担最直接的手段
- **ViewDistanceQuality**：控制`r.SkeletalMeshLODBias`和`r.StaticMeshLODBias`等LOD偏移，影响远处物体切换到低模的距离
- **AntiAliasingQuality**：影响TAA采样数和FXAA/MSAA模式选择，Epic档下TAA Temporal Samples为8
- **ShadowQuality**：控制阴影贴图分辨率、级联阴影数量（CSM）和距离，对GPU帧时间影响权重最大
- **PostProcessQuality**：管理景深、环境光遮蔽（SSAO）、镜头光晕等屏幕空间效果的采样精度
- **EffectsQuality**：影响Niagara粒子系统的粒子数量上限和GPU模拟精度

### Cinematic档位的特殊性

Cinematic档位并非简单地将所有参数调至最高，而是启用了部分在实时游戏中通常禁用的渲染路径。例如，它会将`r.MotionBlurQuality`提升至4（Epic为3），并启用`r.AmbientOcclusion.Compute`的全精度计算路径。该档位本意用于过场动画录制或截图，在实时游戏逻辑运行时使用Cinematic档会导致大多数中端GPU帧时间超过33ms（跌破30FPS）。

---

## 实际应用

### 性能剖析中的快速分层测试

在使用Unreal Insights或`stat GPU`命令采集数据之前，剖析工程师通常先执行一次"档位阶梯测试"：在同一场景同一视角，依次以Epic、High、Medium、Low录制30秒GPU帧时间数据，绘制折线图观察帧时间随档位下降的曲线斜率。若从Epic到High帧时间下降超过40%，说明该场景的性能敏感点集中在ShadowQuality或PostProcessQuality管控的特效上；若曲线几乎平坦直到Low才显著下降，则ResolutionQuality（即填充率）是主要瓶颈。

### 为目标平台配置自动档位

UE提供了`Scalability.ini`中的硬件基准测试（Benchmark）机制，通过`UGameUserSettings::RunHardwareBenchmark()`自动检测GPU/CPU性能并映射到推荐档位。主机游戏开发中，PS5和Xbox Series X通常锁定在High到Epic之间的自定义档位，开发团队会直接在`BaseScalability.ini`中覆盖特定子参数，而非使用整档切换，以便在保持视觉一致性的同时精确命中33ms或16ms的帧预算。

### 控制台命令实时验证

在编辑器或开发版本中，可通过控制台命令`sg.ShadowQuality 0`将阴影质量单独降至Low，同时保持其他类别在Epic档，再用`stat SceneRendering`观察`Shadow Depths`一栏的耗时变化，从而量化阴影渲染对总帧时间的贡献比例。

---

## 常见误区

### 误区一：Cinematic档等于"最好看"且应在游戏中使用

许多初学者在开发阶段将编辑器中的可扩展档位设置为Cinematic，认为这样截图和测试效果最接近"最终品质"。实际上，Cinematic档的部分参数（如全精度光线步进）在PIE（Play In Editor）模式下会造成严重的帧率下降，掩盖真实的游戏性能数据。正确做法是在游戏设定的目标档位（通常为Epic或High）下进行性能剖析，Cinematic仅用于离线渲染录制。

### 误区二：统一使用`SetOverallScalabilityLevel`等于精确控制

`SetOverallScalabilityLevel(3)`（即Epic）会将全部六个类别统一设为Epic，但实际项目中美术和技术团队往往对各类别有不同的取舍——例如将TextureQuality保持在Epic（显存允许时纹理不需要降低）但将EffectsQuality设为High（粒子数量适当减少）。盲目使用整体档位切换会覆盖掉这些精细化配置，导致剖析数据与正式发布版本不一致。

### 误区三：档位切换对所有内容立即生效

部分渲染资源（尤其是流送纹理和预编译光照贴图）在档位切换后不会立即更新，需要等待流送系统的异步加载完成。在剖析时若切换档位后立即采集数据，可能捕获到过渡状态的异常帧时间。正确做法是切换档位后等待至少2-3秒，待`stat Streaming`中的`Texture Pool`数据稳定后再开始录制。

---

## 知识关联

可扩展画质设置建立在**性能剖析概述**中介绍的GPU/CPU时间分离概念之上——只有理解"帧时间由GPU侧渲染成本和CPU侧逻辑成本共同构成"，才能正确解读档位切换实验的结论。切换至Low档后帧时间不变，意味着GPU渲染耗时在总帧时间中占比极低，CPU绑定（CPU-Bound）的判断由此而来。

在实际剖析工作流中，可扩展画质设置通常作为**第一步粗筛工具**，随后才会使用RenderDoc、Unreal Insights中的GPU Insights轨道或`ProfileGPU`命令进行Draw Call级别的精细分析。掌握各档位的具体参数范围（尤其是`sg.ShadowQuality`和`sg.PostProcessQuality`对帧时间的典型影响幅度），能够帮助剖析工程师在进入精细工具之前就形成有效的性能假设，大幅缩短定位瓶颈所需的迭代周期。