---
id: "mn-ch-storage-optimization"
concept: "存储优化"
domain: "multiplayer-network"
subdomain: "cdn-hotpatch"
subdomain_name: "CDN与热更新"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 存储优化

## 概述

存储优化是指在客户端安装包制作阶段，通过一系列压缩、合并和去重手段，将游戏资源文件的总体积降低到用户可接受的下载与安装范围内的技术策略。对于手机游戏而言，Google Play 商店要求初始 APK 不超过 150MB，App Store 的蜂窝网络直接下载上限为 200MB，这使得存储优化成为上线发布的硬性门槛，而非可选的性能改进。

存储优化技术随移动游戏兴起而演进。2010 年前后，受限于 App Store 早期 100MB 上限和 3G 网络速度，开发者开始探索将资源分包、延迟下载的工作流。Asset Bundle 系统成熟后，存储优化与热更新管道紧密结合：初始安装包只打入首屏必要资源，其余内容通过 CDN 按需拉取，使"安装包体积"与"游戏总资源量"彻底解耦。

体积控制的意义不仅限于商店规定。根据 Google 的统计数据，APK 每增加 6MB，转化率（用户点击安装的比例）下降约 1%；超过 100MB 后卸载率明显上升。因此存储优化直接影响用户留存与商业表现，是 CDN 热更新方案中资源管线设计的起点。

---

## 核心原理

### 纹理压缩格式选择

纹理通常占游戏包体积的 60%~80%，选择正确的 GPU 原生压缩格式是减小体积的最大单项收益。Android 平台主流使用 ETC2（OpenGL ES 3.0 强制支持，RGBA 8 位图像压缩比约为 8:1），iOS 平台使用 ASTC（Apple A8 芯片后全系支持，可在 4×4 到 12×12 之间调整块大小，压缩比范围 8:1 至 36:1）。与未压缩 RGBA32 相比，一张 1024×1024 的纹理从 4MB 降至 512KB（ETC2）或最低约 170KB（ASTC 12×12）。错误地将所有平台都保留 RGBA32 格式，是包体超标的最常见原因。

### 音频编码与采样率降级

PCM 原始音频占用极大，游戏中背景音乐应使用 Vorbis（OGG）或 AAC 有损压缩，压缩比通常在 10:1 左右。音效文件可降低采样率：人耳对游戏音效中 22050 Hz 与 44100 Hz 的差异几乎无感知，而体积直接减半。Unity 中对非循环短音效启用"Decompress On Load"+ "ADPCM"格式，可在低 CPU 开销下将音频包体再降 3.5 倍。

### 资源分包与 Streaming Assets 剥离

存储优化的结构性手段是将资源分为"首包必要资源"和"可延迟下载资源"两类。首包只打入主菜单、角色选择等首次启动流程所需的 Asset Bundle；其他关卡、高清贴图包等资源在安装后首次运行时从 CDN 下载，写入沙盒目录（Android 的 `/sdcard/Android/data/<package>/files/`，iOS 的 `Application.persistentDataPath`）。这要求资源加载层在 `AssetBundle.LoadFromFile` 路径上同时检查本地沙盒与 StreamingAssets，形成"本地优先、CDN 兜底"的加载逻辑。

### 代码与 Shader 裁剪

IL2CPP 编译后的原生代码在 ARM64 下本体约 20~40MB。开启 Unity 的"Managed Stripping Level: High"可移除未被反射引用的 .NET 类型，通常减少 3~8MB。Shader 变体是另一大隐患：一个未限制变体的 Uber Shader 可膨胀至数百 MB；通过 `ShaderVariantCollection` 预热并在 Player Settings 中剔除未用变体，可将 Shader 数据从数十 MB 降至个位 MB。

---

## 实际应用

**某 MMORPG 首包优化案例**：原始安装包 APK 达 680MB，远超商店限制。按以下步骤分阶段压缩：
1. 将所有纹理从 RGBA32 迁移至 ETC2/ASTC，纹理总量从 310MB 降至 78MB；
2. 音乐从 WAV 改为 128kbps OGG，音频从 95MB 降至 22MB；
3. 除主城和新手引导关卡外，其余 12 个副本的 Asset Bundle 移出首包；
4. 开启代码裁剪与 Shader 变体收集。
最终首包降至 89MB，其余约 500MB 资源在首次登录后台分批下载。

**分辨率分级下载**：针对低端机型，CDN 存储同一纹理的 512×512 低分辨率版和 2048×2048 高分辨率版。客户端在首次启动时检测 GPU 型号和 RAM 容量，低于 3GB RAM 设备下载低清包（约 120MB），高端机下载高清包（约 380MB），对首包体积无影响。

---

## 常见误区

**误区一：压缩格式一律使用 PNG**
PNG 是无损图像格式，可在磁盘上节省空间，但 GPU 无法直接读取 PNG，运行时必须解码为 RGBA32 再上传显存。把 PNG 打入 Asset Bundle 并不等于在 GPU 侧做了压缩；必须在 Texture Import Settings 中显式设置 ETC2/ASTC，PNG 仅作为源文件格式。

**误区二：首包越小越好**
将首包压至极小（如 10MB 以下）会导致用户首次启动时需要等待数百 MB 的后台下载才能进入游戏，在弱网环境下严重损害体验。合理的首包目标是覆盖"30 秒内让用户看到游戏内容"所需的最小资源集，而非一味追求零资源首包。

**误区三：相同内容重复打包进多个 Asset Bundle**
若 Asset Bundle A 和 B 都引用了同一张 512KB 的共享纹理，且未将该纹理单独抽成共用包，则该纹理会被复制进两个包，磁盘占用翻倍。Unity 的 Asset Bundle 系统不会自动去重跨包依赖，必须手动在依赖分析阶段（`AssetDatabase.GetDependencies`）找出共享资产，将其提取为单独的 Base Bundle 供其他包引用。

---

## 知识关联

本概念直接建立在 **Asset Bundle 系统**之上：Asset Bundle 的分包策略决定了哪些资源进入首包、哪些延迟下载，这是存储优化结构性方案的执行载体；纹理压缩格式的配置也在 Asset Bundle 构建流程（`BuildPipeline.BuildAssetBundles`）中统一生效。掌握 Asset Bundle 的依赖关系管理是避免"重复打包"误区的前提。

存储优化的成果直接服务于 CDN 分发效率：首包体积越小，CDN 边缘节点的冷启动分发压力越低；按平台/分辨率分级存储的资源方案需要 CDN 的多版本路径管理能力配合。在项目整体资源管线中，存储优化是连接本地构建与线上分发的关键卡口，在版本发布前必须通过自动化脚本校验各平台包体是否满足商店上限，防止回归超标。