---
id: "ta-texture-streaming"
concept: "纹理流送"
domain: "technical-art"
subdomain: "memory-budget"
subdomain_name: "内存与预算"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
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


# 纹理流送

## 概述

纹理流送（Texture Streaming）是一种按需动态加载纹理Mip层级的显存管理技术，其核心思想是：不将一张纹理的所有Mip层级同时驻留于GPU显存，而是根据摄像机距离、屏幕投影面积等实时参数，只加载当前帧实际需要的Mip层级。这项技术的现代实现以**虚拟纹理流送（Virtual Texture Streaming，VTS）**为代表，Unreal Engine 4.23起将其作为可选渲染特性正式引入，DirectX 11.2的Tiled Resources规范也对底层硬件提供了原生支持。

纹理流送的出现直接源于分辨率军备竞赛带来的显存压力。一张4096×4096的RGBA无压缩纹理需要占用64MB显存，若游戏场景中同时存在数百张此类纹理，显存需求将轻易突破主流GPU的预算上限。纹理流送通过将"完整加载"改为"按需加载"，使得理论上可管理的纹理总量远超物理显存容量——Unreal Engine的文档指出，启用Virtual Texture后，场景可寻址的纹理数据量可达物理显存的数十倍。

理解纹理流送的工程意义在于：它不是单纯的内存优化技巧，而是一套涉及CPU调度、IO带宽、GPU采样三者协作的完整管线。错误配置流送参数会导致明显的纹理"弹出"（Pop-in）瑕疵，这是玩家可直接感知的视觉劣化，因此技术美术必须深入掌握其运作机制。

---

## 核心原理

### Mip层级请求计算

纹理流送的决策中枢是**Mip偏差计算（Mip Bias Calculation）**。引擎每帧对场景中每个可见网格的UV投影面积进行估算，得到一个"所需Mip等级"值。Unreal Engine使用如下基本逻辑：

> **所需Mip = log₂(纹理分辨率 / 屏幕像素覆盖宽度)**

当一个512×512纹理在屏幕上仅投影为32×32像素时，所需Mip层级约为log₂(512/32) = 4，即只需加载Mip4（32×32）而非完整的Mip0。此计算结果会被提交给**Streaming Manager**，由其负责异步向磁盘或内存池发起加载请求。

### 虚拟纹理页表机制

虚拟纹理流送（VTS）引入了类似CPU虚拟内存的**页表（Page Table）**概念。整张虚拟纹理被划分为固定尺寸的**Tile**（Unreal中默认为128×128像素），每个Tile在物理纹理缓存（Physical Texture Cache）中有对应的物理页。GPU的着色器不直接采样原始纹理地址，而是先查询一张低分辨率的**间接纹理（Indirection Texture）**，其中记录了每个虚拟Tile对应的物理缓存位置。

这一结构使得系统能够实现**Tile粒度的精确加载**：若摄像机只看见一面墙的左半部分，只需将左半部分对应的Tile加载到物理缓存，右半部分的显存占用为零。相比传统流送每次必须加载整个Mip层级，VTS的显存利用率更高，但代价是每次纹理采样需要额外的间接纹理查找开销。

### 流送池与带宽预算

Unreal Engine通过`r.Streaming.PoolSize`（单位MB）配置全局纹理流送池大小，该数值直接限制了流送系统可使用的显存上限。流送池满载时，系统依据**Last Recently Used（LRU）**策略驱逐最久未访问的Mip数据。更关键的是**IO带宽预算**：若磁盘读取速度不足（如机械硬盘约100-200 MB/s，NVMe SSD可达3000+ MB/s），摄像机快速移动时流送请求会积压，导致低分辨率Mip持续显示——这正是"纹理糊"（Texture Blur）瑕疵的物理成因。

---

## 实际应用

**开放世界地形纹理**是纹理流送最典型的应用场景。《荒野大镖客：救赎2》的地形系统采用多层纹理混合，每个地形分块对应独立的流送优先级；靠近玩家的地块持续维持Mip0，远景地块自动降级至Mip3或更低，据Rockstar的GDC分享，此策略使地形纹理显存占用压缩了约60%。

**电影级场景的角色特写**则需要相反的策略：当镜头推进至角色面部时，面部纹理的Mip偏差值需要主动被锁定（Streaming Mip Bias = 0），防止流送系统错误降级。Unreal Engine提供了`Streaming Mip Bias`材质参数和`ForceMipLevelsToBeResident`节点来实现这一精确控制。

在移动端，由于带宽和显存更为受限，Unity的**Texture Streaming API**（Unity 2018.2正式引入）允许开发者为不同摄像机设置独立的`mipMapBias`，确保主摄像机视锥内的纹理享有最高优先级，而小地图摄像机所对应的纹理只加载低Mip层级。

---

## 常见误区

**误区一：纹理流送延迟只与磁盘速度有关。**  
实际上，纹理流送的延迟受三段管线共同制约：①IO读取时间（磁盘→内存）、②上传时间（内存→显存，受PCIe带宽限制，PCIe 3.0 x16理论峰值约16 GB/s）、③Streaming Manager的调度决策延迟。许多开发者将纹理弹出问题单纯归咎于SSD不够快，却忽略了Streaming Manager因帧预算不足导致的请求积压。

**误区二：提高`r.Streaming.PoolSize`就能解决一切流送问题。**  
流送池过大会直接挤占其他渲染资源（如渲染目标、网格缓冲区）的显存，在8GB显存的GPU上盲目将流送池设置为6GB会导致整体渲染稳定性下降。正确做法是使用Unreal的`Stat Streaming`命令实测`Wanted Pool Size`与`Currently Streaming`数据，以实测需求为依据设置池大小，通常预留10%-15%余量即可。

**误区三：虚拟纹理流送（VTS）在所有场景下优于传统Mip流送。**  
VTS的间接纹理查找会引入额外的ALU与带宽消耗，在纹理采样密集的移动端着色器中，这一开销可导致帧率下降3%-8%（视具体GPU架构而定）。对于重复平铺（Tiling）的小纹理（256×256以下），传统Mip流送的实现成本更低，VTS更适合大尺寸、不可平铺的独特贴图（如地形和建筑立面纹理集）。

---

## 知识关联

**前置概念——Mipmap策略**直接决定了纹理流送的操作对象：流送系统调度的最小单位正是Mipmap的各个层级，若Mipmap未正确生成（如缺少高层级Mip），流送系统将无法在远距离使用低分辨率替代，反而可能长时间占用Mip0的全量显存。技术美术在制作流程中需确保所有流送纹理均启用完整的Mip链（Full Mip Chain）。

**后续概念——加载优化**在纹理流送基础上进一步处理资源生命周期管理问题，包括预加载策略（Prestreaming）、关卡切换时的显存清空时机，以及与异步场景加载（Async Level Loading）的协调。掌握纹理流送的带宽模型和优先级队列机制，是正确设计关卡加载序列、避免加载屏幕期间产生IO峰值的必要基础。