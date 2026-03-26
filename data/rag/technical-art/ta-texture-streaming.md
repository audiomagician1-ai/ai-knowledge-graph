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

# 纹理流送

## 概述

纹理流送（Texture Streaming）是一种在运行时按需动态加载纹理Mip层级的内存管理技术，其核心思想是：摄像机远处物体只需要低分辨率的Mip层级，而近处物体才需要加载完整的高分辨率Mip0层级，通过这种空间相关性来削减纹理总驻留内存。与预先将所有纹理完整加载至显存的传统方式相比，纹理流送可将显存占用降低30%~70%，具体取决于场景的视距分布。

该技术最早以"MegaTexture"概念出现在id Software 2007年发布的《Quake Wars》中，后被Unreal Engine 4在2014年正式内置为标准的流送管理器（Texture Streaming Pool），Unity则在其HDRP/URP管线中通过Mipmap Streaming API提供类似支持。虚幻引擎5进一步演进出Virtual Shadow Maps和Nanite体系，但传统纹理流送在常规材质上依然是必不可少的运行时内存控制手段。

纹理流送解决的根本矛盾是：一款现代AAA游戏的原始纹理资产总量可达数十GB，而主机或PC的VRAM通常只有8~16GB。没有流送系统，任何超出VRAM预算的资产组合都会导致显存溢出或强制降质；有了流送系统，引擎可以在帧与帧之间异步交换Mip层级，让玩家无感知地维持视觉质量。

---

## 核心原理

### Mip层级优先级计算

流送系统的决策核心是为每张纹理计算一个"所需Mip层级"（Required Mip Level）。Unreal Engine使用的公式如下：

```
RequiredMip = log2(TextureSize / ScreenSize) + MipBias
```

其中 `TextureSize` 是纹理物理尺寸（像素），`ScreenSize` 是该物体在屏幕上的投影像素面积开方值，`MipBias` 是材质或项目级别的手动偏移量。该值向上取整后即为需要常驻的最高Mip索引——索引越大代表分辨率越低。每帧引擎会对场景中所有可见纹理重新计算此值，并将结果汇总到流送管理器的请求队列。

### 流送池（Streaming Pool）与预算管理

Unreal Engine维护一个固定大小的流送池，默认配置约为512MB（可通过 `r.Streaming.PoolSize` 调整）。流送管理器按优先级将纹理Mip块分配进池中：屏幕占比最大的纹理优先得到高分辨率Mip，超出预算的纹理被降级保留低Mip或完全逐出。当池满时，系统采用LRU（最近最少使用）策略淘汰已离开视野的纹理Mip数据。Unity的Mipmap Streaming同样依赖 `Texture.streamingMipmapUploadCount` 等API监控池的活跃状态。

### 异步IO与Mip加载管道

加载一个Mip层级的完整流程包括：①流送管理器将缺失Mip记录为IO请求；②后台线程从磁盘/包文件中读取对应Mip的压缩数据（通常为BC7/ASTC格式）；③解压后上传至GPU显存，替换旧Mip占位符。这个过程完全异步，不阻塞渲染线程，但存在1~3帧的延迟窗口。在摄像机快速拉近时，这段延迟会造成可见的"纹理弹入（Texture Pop-in）"现象，是流送调优的主要问题来源。

### Virtual Texture Streaming（虚拟纹理流送）

Virtual Texture（VT）是纹理流送的高级形态，灵感来自操作系统的虚拟内存分页机制。VT将超大纹理（如4K×4K地形纹理集）划分为固定大小的"页"（Page，通常128×128或256×256像素），物理显存只存放当前可见的页，由一张"间接表（Indirection Table）"负责虚拟地址到物理页的映射。Unreal Engine 5中Runtime Virtual Texture（RVT）还允许将地形颜色、法线、高度信息合并烘焙进VT，进一步减少采样次数。

---

## 实际应用

**开放世界地形纹理**：《荒野大镖客：救赎2》的地形系统使用VT将数百张4K地表纹理合并为连续虚拟地址空间，玩家骑马穿越时只有摄像机视锥体内的页面被物理加载，地形纹理总VRAM驻留量控制在约1GB以内，而逻辑纹理面积相当于数十GB。

**Unreal Engine项目实操**：在UE5项目中，选中纹理资产勾选"Stream"选项，并在`Project Settings > Engine > Streaming`中将`Texture Streaming Pool Size`设为与目标平台VRAM匹配的值（PS5建议4096~6144MB）。通过控制台命令 `Stat Streaming` 可实时查看Pool Used、Wanted Mips vs Resident Mips的差值，差值持续为正说明池预算不足，需要提升池大小或降低资产纹理分辨率。

**移动端ASTC与流送结合**：移动平台（iOS/Android）使用ASTC压缩格式，每像素仅占0.89~8 bits。结合Mipmap Streaming后，一张2048×2048 ASTC 6×6的纹理在最低Mip（Mip8，即8×8）时只占约0.1KB驻留，而Mip0完整加载才约256KB，流送节省比例极为显著。

---

## 常见误区

**误区一：流送池越大越好**
盲目增大流送池并不能解决所有纹理模糊问题。当池大小超过GPU实际可用VRAM时，系统会触发显存分页至系统内存，导致带宽骤降、帧时间飙升。正确做法是先用 `Stat Streaming` 定位哪些纹理Mip长期缺失，再针对性地优化资产尺寸或拆分场景分区加载。

**误区二：纹理流送可以替代LOD**
纹理流送只处理Mip层级的加载卸载，不影响网格体面数。一个近处的高模（100K面）即使其纹理Mip0已正确流入，仍然会消耗大量顶点处理资源。纹理流送与网格体LOD是相互独立的优化维度，必须配合使用才能同时控制显存和GPU算力预算。

**误区三：Texture Pop-in是无法避免的**
纹理弹入本质上是IO带宽不足或流送预测失败的表现。UE5提供了`r.Streaming.LookAheadTime`参数（默认0.5秒）来让系统提前预判摄像机运动方向并预加载Mip，配合将关键过场动画使用`ForceMipLevelsToBeResident`强制驻留高Mip，可以将过场中的Pop-in完全消除。

---

## 知识关联

**前置概念——Mipmap策略**：纹理流送的操作单元就是Mipmap的各个层级。没有Mipmap的纹理（如UI图集中的某些元素）无法参与流送，因为系统没有可降级的中间分辨率版本可供替换。Mipmap生成时选择的过滤算法（Box/Kaiser）直接影响流送降级后的视觉质量。

**后续概念——加载优化**：纹理流送是加载优化的基础组件之一。理解流送池的填充速率（受磁盘IO和解压速度限制）之后，才能进一步讨论异步场景加载、关卡分块（Level Streaming）与纹理流送的协同调度策略——例如在关卡切换的黑屏帧期间强制预热纹理池，避免玩家进入新区域后看到大面积模糊纹理。