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
updated_at: 2026-03-27
---


# 纹理流式加载

## 概述

纹理流式加载（Texture Streaming，也称 Mip Streaming）是一种在运行时动态决定哪些 Mipmap 层级驻留在显存中的技术。其核心思想是：不将纹理的所有 Mip 级别同时加载到 GPU 显存，而是根据摄像机距离、屏幕像素覆盖面积等因素，仅加载当前帧真正需要的 Mip 层级，其余层级保留在系统内存或磁盘上待命。

该技术最早随第七代主机（PS3/Xbox 360 时代，约 2005 年前后）的显存容量限制（通常仅 256 MB）而广泛应用于商业引擎中。Unreal Engine 3 在 2006 年引入了完整的 Texture Streaming 系统，Unity 则在 2018 年的 Unity 2018.2 版本中正式内置 Mip Streaming 功能（通过 `QualitySettings.streamingMipmapsActive` 开关控制）。

纹理流式加载的价值在于它将显存占用与画质之间的矛盾转化为一个可量化的优先级调度问题。一张 4K（4096×4096）RGBA 未压缩纹理全量加载需要 64 MB 显存，若场景中有 200 张此类纹理，总需 12.8 GB——远超任何消费级 GPU 的显存容量。Mip Streaming 通过只保留必要层级，将实际驻留量压缩至预算范围内。

---

## 核心原理

### Mip 需求计算：所需 Mip 级别的确定

系统首先要为场景中每张纹理计算"所需 Mip 层级"（Required Mip Level）。计算依据是纹理在屏幕上的像素密度，通称 **Texel-to-Pixel 比值**。

若某个三角形在屏幕上占据 `P` 个像素，其 UV 展开对应纹理面积为 `T` 个 texel，则所需 Mip 级别为：

```
RequiredMip = log2(sqrt(T / P))
```

当该值为 0 时使用最高清 Mip（Mip 0）；值越大则使用越模糊的 Mip 层级，对应的内存占用越小（每降低一级，内存减少约 75%，因为分辨率减半而面积变为 1/4）。

实际引擎中这一计算发生在 GPU 端的遮挡剔除与渲染准备阶段，Unreal Engine 使用一张低分辨率的"流式纹理池反馈缓冲区"（Streaming Texture Feedback Buffer）来收集每帧中各纹理的最大所需 Mip。

### 优先级排序：哪些纹理先加载

当多张纹理同时需要更高分辨率的 Mip 级别，但显存预算不足以全部满足时，系统按优先级排队。优先级通常由以下因素加权计算：

1. **Mip 差距（Mip Delta）**：当前驻留 Mip 与所需 Mip 之差越大，画面模糊越严重，优先级越高。
2. **屏幕占比（Screen Proportion）**：纹理对应物体在屏幕上占据的归一化面积越大，优先级越高。
3. **强制驻留标记（Forced Resident Flag）**：UI、角色主体纹理等可被标记为强制常驻，不参与流式调度，始终保持 Mip 0。

Unity 的 Mip Streaming 系统中，可通过 `Texture2D.requestedMipmapLevel` 手动覆盖某张纹理的优先级，强制锁定到指定 Mip 层级。

### 内存预算管理：显存池的分配策略

纹理流式加载系统维护一个固定大小的**纹理流式内存池**（Streaming Texture Pool）。Unity 中通过 `QualitySettings.streamingMipmapsMemoryBudget` 设置预算（单位 MB，默认值为 512 MB）。Unreal Engine 通过 `r.Streaming.PoolSize` 控制，单位同为 MB。

内存池的工作机制分为三个阶段：

- **驱逐（Eviction）**：当新的高优先级 Mip 请求无法满足时，系统将当前最低优先级的纹理的高清 Mip 从显存中卸载，退回到系统内存或磁盘。
- **上传（Upload）**：将所需 Mip 数据从磁盘/系统内存通过 DMA 传输到显存，此操作通常是异步的，存在 1~3 帧的延迟，期间显示低清 Mip 过渡画面（即常见的"纹理先模糊后清晰"现象）。
- **保留（Retention）**：预算有余量时，系统会保留已加载的高清 Mip 以减少未来重新加载的开销，称为"Mip 缓存保留"。

---

## 实际应用

**开放世界游戏中的远近切换**：在《荒野大镖客：救赎 2》等开放世界游戏中，玩家骑马跨越地形时，地面纹理从 Mip 4（低清，约 64×64）实时升级到 Mip 0（高清，4096×4096），整个过程通过流式加载完成，而无需停顿加载画面。

**Unity 项目中的具体配置**：开启方法是在 Quality Settings 中勾选 "Texture Streaming"，然后对每张纹理资产在 Import Settings 中启用 "Stream ing Mipmaps" 选项。若某张 UI 纹理错误地启用了流式加载，可能导致 UI 元素在首帧出现模糊闪烁，正确做法是将其 `mipMapBias` 设置为负值或直接关闭该纹理的流式标志。

**内存超预算时的降级策略**：当场景纹理总需求超过预算，引擎会记录 `TextureStreaming.WantedMips` 与 `TextureStreaming.ResidentMips` 的差值作为"流失量"（Missing Mip Count）指标，开发者可通过分析该指标决定是增大预算还是减少场景中的纹理分辨率。

---

## 常见误区

**误区一：流式加载会消除所有内存峰值**

很多开发者认为开启 Mip Streaming 后显存占用会稳定在预算值以内。实际上，强制常驻纹理（Forced Resident）、RenderTexture、以及 Cubemap 等不参与流式调度的纹理资产会独立占用显存，不计入流式内存池。一个典型错误案例是将大量 512×512 的粒子纹理标记为强制常驻，导致额外占用数百 MB 显存，而开发者误以为流式系统会自动管理。

**误区二：Mip 数越少越省内存**

有人为"节省内存"在导入时关闭 Mipmap 生成，只保留 Mip 0。这实际上适得其反：没有 Mip 链则流式系统无法降级，纹理永远以最高分辨率驻留；而完整 Mipmap 链的总体积仅比 Mip 0 多 33%（等比数列求和：1 + 1/4 + 1/16 + … ≈ 4/3），却能让流式系统在必要时退回低清层级，节省大量显存。

**误区三：流式上传延迟可以忽略不计**

Mip 从磁盘到显存的异步上传在机械硬盘上可能耗时 200~500 ms，即使在 NVMe SSD 上也需要数毫秒的 DMA 传输时间。若游戏中存在摄像机瞬间切换到新场景区域的设计（如剧情过场衔接），必须提前触发流式预加载（Prefetch），而不能依赖系统的被动响应机制。

---

## 知识关联

**前置概念——Mipmap**：纹理流式加载的可行性完全依赖 Mipmap 结构。若纹理没有预生成多层 Mip，流式系统就没有可调度的"层级颗粒度"。Mipmap 的每一级分辨率减半的特性（Mip N 的尺寸为 Mip 0 的 `2^-N` 倍）直接决定了每次驱逐操作的内存释放量。

**横向关联——虚拟纹理（Virtual Texturing）**：Virtual Texturing（如 DirectX 12 的 Tiled Resources 和 UE5 的 Virtual Shadow Maps 原理）是比 Mip Streaming 更细粒度的调度技术——它以纹理的"Tile"（通常 128×128 texel）为单位管理驻留，而非以整 Mip 层为单位。Mip Streaming 是 Virtual Texturing 的概念前身，理解 Mip 优先级调度机制有助于理解 Virtual Texturing 的 Page Table 反馈机制。

**工程延伸——LOD 系统协同**：Mip Streaming 与模型 LOD 系统应协同工作：当物体切换到 LOD2（低多边形版本）时，其纹理的所需 Mip 也应相应降低，否则会出现"低精度模型使用高清纹理"的资源浪费，以及流式系统错误提升低价值纹理优先级的调度失误。