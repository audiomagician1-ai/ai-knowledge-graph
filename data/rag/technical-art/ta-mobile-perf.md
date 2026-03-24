---
id: "ta-mobile-perf"
concept: "移动端性能"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 移动端性能

## 概述

移动端性能优化是技术美术领域中一个与桌面端截然不同的专项课题，其核心差异来源于移动端GPU采用的**基于瓦片的渲染架构（Tile-Based Rendering，TBR）**，而非桌面端的立即模式渲染（Immediate Mode Rendering，IMR）。这一架构差异从根本上改变了Draw Call、带宽消耗和Overdraw的代价计算方式，使得许多在PC端无害的操作在移动端会造成严重性能瓶颈。

移动端GPU的代表性厂商包括ARM（Mali系列）、Qualcomm（Adreno系列）和苹果（Apple GPU），它们虽然实现细节各异，但都以TBR或其进化形式TBDR（Tile-Based Deferred Rendering，典型代表为Apple GPU和PowerVR）为基础。移动端GPU通常集成在SoC（片上系统）芯片中，与CPU共享同一块LPDDR内存，没有独立的显存。这意味着GPU访问主内存的带宽极其珍贵，带宽消耗直接关联功耗，而功耗又直接触发热降频机制。

对于技术美术而言，理解移动端性能的意义在于：一款在PC端运行流畅的视觉效果，移植到移动端后可能因为一个Alpha混合半透明物体的滥用或一次无意义的RT读写操作，就将帧率从60fps打入30fps甚至更低，且这种下降往往伴随设备发热，最终导致持续性能衰减而非稳定低帧。

---

## 核心原理

### TBR架构与On-Chip Memory

TBR架构将屏幕划分为若干个小瓦片（Tile），典型尺寸为**16×16像素或32×32像素**。GPU每次仅处理一个Tile的几何体和像素，所有光栅化和像素着色计算都在GPU内部高速的**片上内存（On-Chip Memory / GMEM）**中进行，Tile计算完毕后才将结果写回主内存（System RAM）。这与IMR架构中每个Draw Call立即将结果写回显存的方式形成鲜明对比。

TBR的关键优势在于：只要渲染过程不主动"打断"这一流程，深度测试（Depth Test）、模板测试（Stencil Test）和Alpha混合等操作全部在片上内存内完成，**完全不消耗主内存带宽**。然而，一旦发生以下操作，TBR就会被迫将片上内存的内容"Flush"回主内存，再重新加载：
- 切换Render Target（RT）
- 在着色器中采样当前正在写入的Render Target（称为"Framebuffer Fetch"滥用）
- 使用需要读取前帧数据的效果（如屏幕空间折射）

每一次Flush和Reload都会产生大量带宽消耗，这是移动端后处理链条代价远高于PC端的直接原因。

### 带宽优化：移动端第一性能杀手

由于GPU与主内存共享带宽，移动端的带宽通常仅有**30–60 GB/s**（如Snapdragon 8 Gen 2约51 GB/s），远低于桌面端独立GPU的400–1000 GB/s。带宽消耗不仅影响渲染速度，更直接转化为热量。降低带宽消耗的主要手段包括：

- **使用ASTC压缩格式**：ASTC（Adaptive Scalable Texture Compression）是移动端标准纹理压缩格式，ASTC 6×6可将原始RGBA8纹理压缩至约2.37 bpp（原始为32 bpp），压缩比约13:1，且支持HDR和透明通道。
- **减少Render Target数量和尺寸**：每一张全屏RT（如1080p RGBA16F）占用约8 MB，频繁读写数张全屏RT的后处理流水线在移动端是最典型的带宽超标场景。
- **正确设置LoadAction和StoreAction**：在Unity中对应`RenderBufferLoadAction.DontCare`和`RenderBufferStoreAction.DontCare`，告知GPU无需加载或保存某张RT的内容，避免无意义的Flush。不正确设置这两个参数是移动端开发中最常见的隐式带宽浪费来源。

### 热降频（Thermal Throttling）

移动端设备依赖被动散热（无风扇），当SoC温度超过阈值（通常为**85°C至95°C**，因厂商不同而异），系统会强制降低CPU和GPU的工作频率以控制功耗，这一机制称为热降频（Thermal Throttling）。

热降频的危险在于它是**累积性的**：一款游戏可能在冷机状态下稳定60fps，但经过10-15分钟持续高负载后，GPU频率从最高的710 MHz（以Adreno 740为例）降至400 MHz左右，导致帧率持续下滑至40fps以下，而开发者在短时测试中从未发现此问题。对此，技术美术需要主动使用**长时压力测试（Sustained Performance Test）**而非短时截帧分析来评估移动端性能，Unity的Android Player Profiler连续录制至少15分钟才能暴露热降频导致的性能曲线下滑。

---

## 实际应用

**案例1：移动端Bloom效果的TBR适配**  
PC端Bloom通常包含多次全屏Blit（亮度提取→多级降采样→上采样→合并），每一次Blit在移动端都意味着一次RT切换，触发TBR Flush。优化方案是将降采样和上采样的Pass数量压缩至最少，或使用Dual Kawase Blur替代标准高斯模糊，将采样次数从标准5×5卷积的25次减少至每Pass仅4次采样，同时将全部Pass的RT分辨率限制在屏幕1/4（540p→270p→135p），大幅降低每次Flush的数据量。

**案例2：TBDR的HSR（Hidden Surface Removal）与不透明物体渲染顺序**  
Apple GPU和PowerVR的TBDR架构在像素着色之前执行完整的可见性判断（HSR），彻底消除Overdraw，前提是不透明物体的材质Shader**不包含`discard`指令（即clip()）**和Alpha Test。一旦Shader中有clip()，GPU无法在着色前确认像素是否可见，HSR失效，退化为与Mali相似的逐像素深度测试，Overdraw代价恢复正常。因此在移动端，应将Alpha Test效果替换为Alpha-to-Coverage（在MSAA环境下）或使用Distance Field代替纹理透明，以保留TBDR的HSR优势。

---

## 常见误区

**误区1：移动端Draw Call数量是首要瓶颈**  
受早期移动端（2010-2015年）性能限制观念影响，许多开发者认为控制Draw Call数量是移动端优化的头等大事。然而现代移动端GPU（Mali-G710、Adreno 730+、Apple A15+）对CPU侧Draw Call提交的处理能力已大幅提升，真正的首要瓶颈几乎总是**带宽和片上内存压力**，而非Draw Call数量本身。盲目合并Mesh（静态合批）反而可能增加顶点数量和带宽消耗。

**误区2：Alpha混合在移动端仅影响Overdraw**  
在桌面IMR架构中，Alpha混合的主要代价是Overdraw（像素着色重复计算）。但在TBR架构中，半透明物体必须在不透明物体完全渲染完成后才能正确混合，这意味着渲染半透明物体时GPU必须先加载（Load）当前Tile的颜色缓冲，完成混合后再存储（Store），**每个半透明Draw Call都强制触发一次片上内存的Load操作**，带宽代价远超桌面端。粒子系统滥用半透明是移动端帧率崩溃的最常见原因之一。

**误区3：只需在目标机型上测试不发热就算通过**  
不同移动设备的散热能力差异极大：同一款SoC在厚机身旗舰手机中可能持续性能运行30分钟，在轻薄机型中5分钟内即触发热降频。正确的测试策略是使用**性能最差的目标机型**（而非旗舰设备），在室温25°C环境下连续运行30分钟，使用Snapdragon Profiler或Mali Graphics Debugger监控GPU频率曲线，确保频率无持续下降。

---

## 知识关联

本概念直接依赖**GPU性能分析**的基础知识，特别是对GPU渲染流水线（顶点处理→光栅化→像素着色→ROP输出）的理解，以及使用GPU专项分析工具（如RenderDoc、Xcode GPU Frame Debugger、Snapdragon Profiler）抓帧和解读Overdraw、带宽、像素填充率等指标的能力。没有这些工具使用经验，无法定量判断移动端某次优化是否有效——例如，优化ASTC压缩设置后，需要通过Snapdragon Profiler的"Memory Traffic"数据确认带宽确实下降，而非主观判断帧率变化。

移动端性能优化还与**Shader复杂度控制**高度关联：移动端GPU的ALU算力（浮点计算单元数量）普遍低于桌面端，复杂的PBR光照计算（如多次IBL卷积采样）在移动端需要替换为预计算或简化版本。此外，**LOD系统**和**遮挡剔除**虽然
