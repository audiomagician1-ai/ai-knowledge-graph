---
id: "texture-streaming"
concept: "纹理流"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["资源"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
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


# 纹理流

## 概述

纹理流（Texture Streaming）是一种按需动态加载纹理数据的技术机制，其核心思想是：在任意给定帧中，只将摄像机实际可见且需要高分辨率的纹理 MIP 层级加载到 GPU 显存（VRAM）中，而非一次性将场景所有纹理的所有层级全部驻留显存。这一技术直接解决了现代游戏场景纹理总量远超 GPU 显存容量的根本矛盾——一张 4K 纹理（BC7 压缩后约 8 MB）在大型开放世界中可能有数千张，完整加载超过 GPU 典型的 8–16 GB 显存上限。

该技术的工程实践可追溯至 2000 年代初期。id Software 在《雷神之锤 III》之后开始探索 MegaTexture 概念，而 John Carmack 于 2007 年在《Enemy Territory: Quake Wars》中正式落地虚拟纹理（Virtual Texture）系统，将整个场景地形的纹理合并为一张逻辑上的巨型纹理（可达 128K×128K 像素），仅按视图需要流式加载对应区块。Unreal Engine 4 在 4.23 版本正式引入 Virtual Texture Streaming（VT），而 Unity 的 Adaptive Probe Volumes 与 Streaming Virtual Texturing（SVT）则在 Unity 2020 LTS 周期内逐步成熟。

纹理流对运行时显存占用的影响十分直接：Unreal Engine 的默认纹理预算（`r.Streaming.PoolSize`）可将显存用量压缩到不开启时的 30%–60%，使中低端设备也能呈现高质量纹理细节，同时避免因显存溢出导致的纹理降质或崩溃。

## 核心原理

### MIP 层级选择与 LOD 计算

纹理流的前提是 MIP 链（MIP Chain）：一张 2048×2048 基础纹理生成 MIP 0 至 MIP 10 共 11 个层级，层级每增加 1，分辨率减半，内存占用约为上一级的 25%。运行时，GPU 着色器使用公式

$$\lambda = \log_2\!\left(\frac{\partial(u,v)}{\partial(x,y)} \cdot \text{texelDensity}\right)$$

计算所需 MIP 层级 λ，其中 ∂(u,v)/∂(x,y) 是纹理坐标相对于屏幕坐标的偏导数，反映纹素密度。纹理流系统读取 GPU 反馈（Feedback Buffer）或预测摄像机距离，预先将该层级及其上下各一级缓存到显存，确保采样时不发生缺页（Texture Miss）。

### 虚拟纹理（Virtual Texture）分块机制

虚拟纹理将逻辑巨型纹理划分为固定大小的**页面（Page/Tile）**，通常为 128×128 或 256×256 纹素。每帧渲染一个"分析Pass"，使用低精度着色器将每个像素所需的虚拟纹理页面编号及 MIP 写入一张屏幕分辨率的 Feedback Texture（一般降采样至 1/8 分辨率以节省开销）。CPU 读取该纹理，对请求页面排优先级后异步从磁盘或内存池加载，并将已加载页面写入**物理纹理缓存（Physical Texture Cache）**——一张有限大小的 Atlas Texture。同时维护一张**页表纹理（Page Table Texture）**，着色器在采样时先查询页表，将虚拟地址重定向到物理缓存中的实际位置，整个过程对材质着色器几乎透明。

### 流式调度与优先级策略

纹理流管理器（Streaming Manager）维护一个优先级队列，综合以下因素为每张纹理/每个 Tile 计算优先级分数：
- **视角距离**：越近优先级越高，权重最大；
- **屏幕占用像素数**：大面积可见物体优先于边缘细小物体；
- **纹理请求时效性**：已请求但长时间未加载的页面优先级随时间上升（Aging 机制），防止饥饿（Starvation）；
- **I/O 带宽限制**：通常每帧最多提交 2–4 MB 的纹理上传请求（取决于平台总线带宽）。

当显存预算告急时，管理器执行驱逐（Eviction），优先卸载最久未访问（LRU, Least Recently Used）的高分辨率 MIP 层级，而保留低 MIP 层级作为 Fallback，避免出现全黑纹理的硬性错误。

## 实际应用

**Unreal Engine 开放世界场景**：在 UE5 的 World Partition 工作流下，地形（Landscape）使用 Runtime Virtual Texture（RVT）将混合材质结果缓存为虚拟纹理，减少重复材质求值开销。`r.VT.MaxUploadsPerFrame=8` 控制每帧最大页面上传数量，开发者在低端主机上通常将其降至 4 以避免帧率尖刺。

**移动平台纹理流**：iOS/Android 平台 GPU 显存与主存共享，纹理流预算需要更加保守。Unity 在移动端使用 `QualitySettings.streamingMipmapsMemoryBudget`（单位 MB）硬性限制流式显存占用，配合 Addressables 异步加载纹理 Asset Bundle，将 MIP 0（最低精度）常驻内存，按需拉取高 MIP 层级。

**过场动画纹理预热**：纹理流的主要负面表现之一是"纹理弹出"（Texture Pop-in）——摄像机切换后高 MIP 尚未加载完毕。Naughty Dog 在《最后生还者 Part I》的 PC 移植中专门设计了过场预加载阶段（Prestream Phase），在摄像机切换前 0.5–1 秒通过预测路径提前请求所需页面，将 Pop-in 发生率降低超过 80%。

## 常见误区

**误区一：纹理流等于低画质纹理**  
实际上纹理流的目标恰恰相反——它允许使用比传统方式更高分辨率的纹理，因为不需要同时将所有 MIP 全部驻留显存。关闭纹理流（如将 `r.Streaming.Enabled=0`）反而可能因显存超限导致引擎自动降级所有纹理到更低分辨率（UE 的 `r.Streaming.LimitPoolSizeToVRAM` 行为）。

**误区二：虚拟纹理与 MIP Streaming 是同一回事**  
MIP Streaming 仅选择性加载同一张纹理的不同 MIP 层级，纹理的逻辑尺寸和 UV 布局不变。虚拟纹理则更进一步，将多张纹理或超大纹理合并为统一逻辑地址空间，通过页表间接寻址，增加了分析 Pass 和页表查询的额外开销（约占帧时间 0.2–0.5 ms），需要材质着色器显式支持虚拟纹理采样接口。

**误区三：纹理流能完全消除加载卡顿**  
纹理流依赖 I/O 和总线带宽，HDD（约 100–200 MB/s 顺序读取）上的页面加载延迟远大于 NVMe SSD（约 3500 MB/s），因此 PS5 的 SSD 优先架构（带宽约 5.5 GB/s）是 UE5 Nanite+虚拟几何体与 Lumen+虚拟纹理实现无缝串流的硬件前提，在 HDD 平台上相同参数设置会产生明显的流式延迟。

## 知识关联

纹理流建立在**渲染管线概述**所讲的纹理采样阶段之上：理解 GPU 如何在片元着色器中执行 `texture2D(sampler, uv)` 采样，以及 MIP 过滤（Trilinear/Anisotropic）的工作方式，是理解纹理流为何需要预先将正确 MIP 层级驻留显存的必要基础。MIP 链的存储格式（DXT/BC 块压缩）决定了每次页面上传的字节数和 I/O 开销计算。

在渲染管线的更广背景下，纹理流与**遮挡剔除（Occlusion Culling）**紧密协作：被剔除的物体不产生纹理请求，可显著降低流式带宽压力。此外，纹理流的 Feedback Buffer 分析 Pass 与**延迟渲染（Deferred Rendering）**的 G-Buffer Pass 存在执行顺序依赖，引擎通常在 Depth PrePass 完成后立即执行虚拟纹理分析，以最早获得准确的可见性信息，减少一帧的页面请求延迟。