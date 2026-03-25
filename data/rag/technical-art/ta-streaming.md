---
id: "ta-streaming"
concept: "资源流送"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 资源流送

## 概述

资源流送（Resource Streaming）是一种将游戏资产——包括纹理、网格和关卡几何体——按需异步加载进内存的技术策略。其核心思想是：游戏不必在启动时将所有资产一次性加载完毕，而是根据摄像机位置、视距和玩家行为预测，动态决定哪些资产需要被加载、哪些可以被卸载。这种机制使得大世界游戏（如《赛博朋克2077》或《荒野大镖客：救赎2》）得以在有限的显存与内存约束下运行，而不会产生明显的加载黑屏。

资源流送技术最早在PS2时代的赛车游戏中以"关卡流送"形式出现，彼时主要解决赛道分段加载问题。进入PS3/Xbox 360世代后，随着开放世界游戏兴起，纹理流送成为标配——虚幻引擎3在2006年随《战争机器》发布时已内置Texture Streaming系统。现代引擎（UE5、Unity HDRP）的流送系统已演进为统一的异步资产管理框架，可同时处理纹理MIP级别切换、网格LOD加载和世界分区（World Partition）单元的异步读取。

资源流送之所以重要，在于它直接决定了玩家体验到的卡顿频率。当流送系统失效时，最直接的症状是"纹理弹出"（Texture Pop-in）——物体从模糊低分辨率突然切换到清晰高分辨率——以及移动速度过快时关卡几何体尚未就绪导致的"穿地"或空洞。

## 核心原理

### 异步I/O与主线程解耦

流送的基础是将磁盘读取操作与游戏主线程完全分离。传统同步加载会在`LoadAsset()`调用期间阻塞主线程，导致帧率瞬间跌至0。异步流送则通过操作系统的异步I/O接口（Windows上为`OVERLAPPED`结构体，或DirectStorage API）在后台线程提交读取请求，主线程继续渲染。微软在2020年发布的DirectStorage API将GPU直接作为DMA传输目标，跳过CPU解压缩环节，理论上可将纹理加载带宽从约2 GB/s提升至NVMe SSD的全速7 GB/s。

### 纹理MIP流送与优先级预算

纹理流送的核心是MIP链管理。一张2048×2048的纹理包含从2048×2048（MIP0）到1×1（MIP11）共12个级别，完整链占用约2.73MB（DXT1压缩）。流送系统通常在内存中常驻MIP3或MIP4（分辨率为256×256或128×128）作为"常驻基础MIP"（Resident Base MIP），仅当物体进入预设的流送距离阈值时才异步加载更高级别MIP。

虚幻引擎的纹理流送预算由`r.Streaming.PoolSize`控制（默认值因平台而异，PS5上通常设为1500 MB），系统根据每帧计算出的`Wanted Mip`与`Resident Mip`之差决定优先级队列的调度顺序：距离摄像机越近、屏幕占比越大的纹理优先级越高。

### 世界分区与关卡流送单元

UE5的World Partition系统将整个地图按网格划分为流送单元格（Streaming Cell），默认尺寸为3200厘米×3200厘米（即32米×32米）。每个单元格对应一个子关卡（Sub-Level），由流送管理器根据玩家的`Streaming Source`组件（通常附加在玩家控制器上）的位置和设定的加载距离（Load Distance）决定激活或休眠。单元格的异步激活分为三个阶段：磁盘读取→反序列化→Actor注册，每个阶段可跨越多帧分摊，从而避免单帧CPU尖峰。

网格流送（Mesh Streaming）与纹理流送类似，采用LOD分级异步加载策略：远处物体持有LOD2或LOD3（面数仅为LOD0的1/8至1/64），当物体进入高细节距离阈值后，后台线程开始加载LOD0网格数据并在加载完成后无缝切换。

## 实际应用

**开放世界游戏的流送配置**：在UE5的开放世界项目中，技术美术通常需要设置三个关键参数：`Streaming Distance Multiplier`（控制全局流送距离的缩放系数，通常在0.5–2.0之间调整）、`LOD Bias`（正值强制使用更低LOD，在移动平台上常设为+1或+2）以及纹理组（Texture Group）的`MaxLODBias`，针对`World`和`WorldNormalMap`组分别设置内存预算。

**流送诊断工具**：在UE5中，执行控制台命令`stat streaming`可实时显示当前流送纹理池使用量、待加载纹理数量（Pending Textures）及每帧I/O带宽消耗。`r.Streaming.DropMips 1`可强制丢弃所有非常驻MIP以测试最低内存占用。Unity的Addressables系统提供`Addressables.LoadAssetAsync<T>()`接口配合`IResourceLocator`实现等效的异步纹理和预制体流送。

**主机平台的SSD利用**：PS5和Xbox Series X的定制SSD（顺序读取约5.5 GB/s和2.4 GB/s）允许极低的常驻基础MIP策略，部分开发商将常驻MIP下调至MIP5（64×64），在运行时依赖流送实时补充，从而大幅降低系统内存占用基线。

## 常见误区

**误区一：流送池越大越好**。增大`r.Streaming.PoolSize`并不能无限提升效果。当流送池超过GPU显存的70%–80%时，系统需要频繁与CPU内存之间搬运数据，反而引入额外带宽开销。正确做法是通过`stat streaming`监控实际峰值用量，将池大小设置为峰值的110%–120%留有余量即可。

**误区二：流送可以完全替代正确的资产规格控制**。流送系统本质上是内存调度机制，它无法将一张不合理的8K纹理变得"高效"——8K纹理的MIP0单张在RGBA16F格式下仍占128 MB，即使大多数时间只加载MIP4，一旦摄像机贴近，瞬时带宽需求仍会造成卡顿。流送需配合正确的纹理分辨率规划、压缩格式选择（BC7、ASTC）共同使用。

**误区三：异步加载意味着没有帧率影响**。磁盘读取虽在后台线程进行，但反序列化和GPU上传阶段仍可能产生CPU/GPU尖峰。UE5的`r.Streaming.MaxNumTexturesToStreamPerFrame`参数（默认值为0，即不限制）若不加以限制，在I/O密集区域每帧可能触发数十次纹理上传调用，导致渲染线程等待GPU完成上传而产生气泡（Bubble）。

## 知识关联

资源流送与**虚拟纹理**（Virtual Texture，VT）在设计目标上高度互补但机制不同：传统流送以整张纹理的MIP级别为调度单位，而虚拟纹理将单张纹理切分为128×128或256×256的页面（Page），以页面为最小调度单位，使得超大纹理（如地形的8K Blend纹理）只有摄像机实际覆盖的页面被加载进物理纹理缓存（Physical Texture Cache）。掌握了资源流送的MIP调度逻辑后，虚拟纹理的页面请求（Page Request）机制将更易理解——两者本质上都是"只加载当前可见细节所需的最小数据量"这一原则的不同粒度实现。

在技术美术工作流中，资源流送还与LOD系统、实例化渲染（GPU Instancing）和遮挡剔除（Occlusion Culling）共同构成大世界性能优化的完整链条：遮挡剔除决定哪些物体不需要渲染，流送决定哪些物体的高细节资产需要存在于内存，LOD决定实际渲染哪个精度级别，而实例化渲染则减少已加载网格的Draw Call开销。
