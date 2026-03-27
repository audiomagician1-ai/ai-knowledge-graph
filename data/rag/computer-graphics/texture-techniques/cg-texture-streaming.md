---
id: "cg-texture-streaming"
concept: "纹理流式加载"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 3
is_milestone: false
tags: ["实践"]

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

# 纹理流式加载

## 概述

纹理流式加载（Texture Streaming，也称 Mip Streaming）是一种按需动态加载纹理 Mipmap 层级的内存管理技术。其核心思想是：渲染引擎不将一张纹理的所有 Mip 级别常驻于 GPU 显存，而是根据摄像机距离、屏幕占比等运行时信息，仅加载当前帧实际需要的 Mip 层级，从而将有限的显存预算分配给最影响画质的纹理区域。

该技术最早在 2005 年前后随大世界游戏的普及而受到重视。id Software 在《Quake》系列中使用的静态纹理方案无法应对开放世界的显存压力，促使后来的引擎（如 Unreal Engine 3 于 2006 年正式引入 Texture Streaming 系统）开始将流式加载作为标准渲染管线的组成部分。现代引擎如 Unreal Engine 5 和 Unity（自 2018.2 起支持 Mip Streaming API）均内置了完整的流式加载框架。

纹理流式加载的意义在于它打破了"显存容量 = 可用纹理总量"的硬性限制。一个典型的 AAA 游戏场景中，所有纹理的完整 Mipmap 集合可能高达 8–16 GB，远超主流显卡 8–12 GB 的显存上限，而流式加载使得系统只需在显存中维持 1–3 GB 的活跃纹理切片，其余部分按需从磁盘或内存中动态换入换出。

---

## 核心原理

### Mip 优先级计算

流式加载系统为场景中每张纹理计算一个"所需 Mip 层级"（Required Mip Level），其核心公式为：

$$\text{RequiredMip} = \log_2\left(\frac{TextureTexels}{ScreenPixels \times \text{MipBias}}\right)$$

其中 `TextureTexels` 是纹理在屏幕投影后的纹素密度，`ScreenPixels` 是该表面实际占用的像素数，`MipBias` 是可调节的质量偏移量。计算结果越小，说明该纹理需要越高分辨率的 Mip 层级（Mip 0 为最高分辨率）。引擎在每帧更新这一值，并将所有纹理按优先级排序，决定哪些纹理应当升档（Stream In）或降档（Stream Out）。

### 显存预算管理（Memory Budget）

流式加载系统维护一个全局显存预算池（Texture Pool），Unreal Engine 中默认通过 `r.Streaming.PoolSize`（单位 MB）配置，典型值在 512–2048 MB 之间。系统将预算切分为三个区域：**常驻区**（Resident，存放 Mip 尾部即最低分辨率层级，通常为 64×64 或 32×32，永不卸载）、**活跃区**（Active，存放当前帧需要的高 Mip 层级）、**预取区**（Prefetch，预加载摄像机移动方向上即将进入视野的纹理）。当活跃区 + 预取区超出预算时，系统强制将最低优先级纹理的高 Mip 层级卸载，退回到常驻区的低分辨率版本。

### 流式加载的异步 IO 管道

Mip 层级的实际数据传输通过异步 IO 完成，避免阻塞主渲染线程。典型管道分为四个阶段：
1. **优先级排序**（每帧，CPU）：计算所有可见纹理的 RequiredMip，生成升档/降档请求队列。
2. **IO 请求发出**（异步线程）：将待加载的 Mip 切片从磁盘读入系统内存（RAM），DXT/BC7 压缩数据原样传输。
3. **GPU 上传**（异步复制队列）：利用 DirectX 12 / Vulkan 的异步复制命令队列，将压缩数据上传至显存，不占用图形队列带宽。
4. **引用切换**（下一帧开始前）：原子性地将着色器采样引用从旧 Mip 切换到新 Mip，避免采样到未完成上传的数据。

---

## 实际应用

**Unreal Engine 5 的 Nanite 与流式加载协作**：在使用 Nanite 几何体的场景中，虚拟纹理（Virtual Texture）与 Mip Streaming 共同工作——Nanite 提供精确的屏幕覆盖率数据，使 Mip 优先级计算比传统方案精确约 30%，减少了因距离估算误差导致的低分辨率闪烁（Texture Pop-in）。

**Unity 中的 Mip Streaming 调试**：开发者可通过 `Texture.streamingTextureCount`、`Texture.desiredMipmapLevel` 等 API 实时查询每张纹理的目标 Mip 级别，配合 Memory Profiler 的 Texture Streaming 视图，定位哪些纹理持续占用高优先级槽位并触发预算溢出。

**移动平台的差异化配置**：在 iOS/Android 平台，由于 LPDDR5 带宽限制和 UFS 3.1 存储顺序读速约 2000 MB/s，流式加载的 IO 批量大小通常设置为 256 KB/次，而 PC 平台（NVMe SSD 顺序读速可达 7000 MB/s）可放宽至 1–4 MB/次，以平衡响应延迟与带宽效率。

---

## 常见误区

**误区一：Mip 0 永远不会被卸载**  
实际上，在严格的显存预算限制下，即使是摄像机正对的纹理，其 Mip 0（最高分辨率层级）也可能因预算耗尽而被降档。系统保证卸载的下限是常驻 Mip（通常为 Mip 6 或 Mip 7，即 64×64 或 32×32），而非 Mip 0。将 `r.Streaming.FullyLoadUsedTextures 1` 才能强制保留视野内纹理的最高分辨率，但这会绕过预算控制。

**误区二：流式加载会消除 Texture Pop-in**  
流式加载减少了显存溢出导致的强制降档，但并不能消除 Pop-in。当摄像机移动速度超过 IO 带宽能补充 Mip 层级的速度时（例如瞬间传送类能力或极速飞行），新进入视野的纹理仍会短暂以低分辨率 Mip 呈现。解决方案是配合**预取半径**（Prefetch Radius）参数和关卡流送设计来对抗这一问题，而非依赖流式加载本身。

**误区三：提高 PoolSize 总能改善画质**  
当显存预算已足以容纳所有活跃纹理的最优 Mip 层级时，继续增大 PoolSize 不会带来任何画质提升，反而会挤压帧缓冲、Shadow Map 等其他显存资源的空间。合理的做法是通过 `Stat Streaming` 命令观察 `Required Pool Size` 与当前 `Pool Size` 的差值，仅在 Required > Allocated 时才增加预算。

---

## 知识关联

纹理流式加载以 Mipmap 为前提：每个 Mip 层级（Mip 0 至 Mip N，分辨率以 2 的幂次递减）是流式加载的最小传输单元。没有预先生成的 Mipmap 链，流式系统就无法按层级独立管理内存。理解 Mipmap 的层级结构（1024×1024 纹理对应 Mip 0 至 Mip 10 共 11 个层级）直接决定了对流式系统优先级计算的理解深度。

流式加载技术进一步延伸出**虚拟纹理（Virtual Texture / VT）**体系——后者将纹理细分为固定尺寸（如 128×128）的 Page 进行流式管理，而非以完整 Mip 层级为单位，能更精细地利用显存，但实现复杂度显著更高。在学习流式加载的优先级与预算机制后，虚拟纹理中的 Page Table、Feedback Buffer 等概念会更加直观。