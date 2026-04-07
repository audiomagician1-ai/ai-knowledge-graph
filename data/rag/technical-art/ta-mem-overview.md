---
id: "ta-mem-overview"
concept: "内存管理概述"
domain: "technical-art"
subdomain: "memory-budget"
subdomain_name: "内存与预算"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 内存管理概述

## 概述

游戏运行时需要同时管理三种物理上彼此独立的内存区域：系统RAM（主内存）、VRAM（显卡专用显存）以及共享内存（在集成显卡架构中由CPU与GPU共用的统一内存池）。这三类内存的读写速度、容量上限和访问延迟各不相同，技术美术必须清楚地知道每一类资产最终驻留在哪块内存中，才能精准地诊断和解决内存超限问题。

这一分类体系随着GPU从外置扩展卡演变为现代游戏机SoC而变得更加复杂。PlayStation 4于2013年发布时，采用了统一的GDDR5内存池，总容量8 GB由CPU和GPU共同瓜分，彻底打破了PC端RAM与VRAM泾渭分明的传统模型。理解这段历史对于判断主机平台与PC平台的内存策略差异至关重要。

对技术美术而言，忽视内存类型区分最直接的代价是：一张超出VRAM容量的4K纹理会被驱动程序静默地迁移到系统RAM，导致GPU在每次采样时产生PCIe总线延迟，帧时间可能上升数毫秒，而性能监视器上显示的VRAM占用却看起来"正常"。

---

## 核心原理

### 系统RAM的角色与典型容量

系统RAM（如DDR4/DDR5）是CPU直接寻址的主内存，带宽通常在50–80 GB/s量级。在游戏中，系统RAM主要存放：CPU端的游戏逻辑数据、音频PCM流、已解压但尚未提交给GPU的网格顶点缓冲暂存区，以及用于流式加载的资产队列。当前主流PC游戏的推荐最低系统RAM为16 GB，高端建议为32 GB。游戏进程并非独占全部RAM，操作系统和后台进程一般会占用2–4 GB，因此实际可用预算低于物理总量。

### VRAM的独占性与带宽优势

VRAM（如GDDR6/GDDR6X）焊接在显卡PCB上，专供GPU使用，带宽远高于系统RAM，RTX 4090的GDDR6X带宽高达1008 GB/s。纹理、渲染目标（Render Target）、深度缓冲、Shader常量缓冲区（Constant Buffer）以及顶点/索引缓冲的最终版本都必须存放在VRAM中才能获得最优渲染性能。VRAM容量相对系统RAM更为紧张：中端显卡如RTX 4060仅配备8 GB VRAM，而一套4K PBR材质集合在未压缩情况下轻易超过2 GB。这正是BC7、ASTC等GPU纹理压缩格式在内存管理中不可或缺的原因。

### 共享内存与统一内存架构（UMA）

在集成显卡（如Intel Iris Xe、AMD Radeon集成核显）和现代游戏主机（PS5、Xbox Series X、Nintendo Switch）上，CPU与GPU访问同一块物理内存池，称为统一内存架构（Unified Memory Architecture，UMA）。PS5的UMA池为16 GB GDDR6，带宽448 GB/s，操作系统保留约1.5 GB，游戏可用约14.5 GB。在UMA中不存在VRAM溢出到RAM的概念，但同样存在CPU与GPU争抢带宽的问题。苹果M系列芯片同样采用UMA，M2 Pro最高提供32 GB统一内存，GPU和CPU共享该池，Unity和Unreal在Apple Silicon上的内存预算规划需要以此为准。

### PCIe传输的代价

在传统分离式架构（独立显卡+系统RAM）中，当VRAM不足时，驱动程序会将部分资源"降级"到系统RAM，GPU通过PCIe总线访问这些资源。PCIe 4.0 x16的理论带宽约为32 GB/s，仅为GDDR6X的3%左右。一次纹理溢出后，每帧的纹理读取延迟从纳秒级上升到微秒级，这在复杂场景中会累积为可观的帧时间开销。NVIDIA的Resizable BAR（AMD称Smart Access Memory）技术可将CPU对VRAM的访问带宽提升至约12 GB/s，一定程度上缓解反向传输瓶颈，但无法解决GPU读取系统RAM时的根本延迟问题。

---

## 实际应用

**Unreal Engine 5中的内存类型分配实例：** 一个中等规模的开放世界关卡，其Nanite几何体数据存放于系统RAM的流送缓存（约1–2 GB），当前可见的Nanite页面（Page）会被上传至VRAM（约200–400 MB动态占用），Lumen的辐射缓存（Radiance Cache）和屏幕空间GI数据作为Render Target始终驻留VRAM。技术美术在排查内存问题时，需要分别用`Stat Memory`命令查看CPU端分配，以及GPU厂商工具（如NSight、RenderDoc）查看VRAM占用，两者数字加起来才是真实的总内存代价。

**移动端案例：** 高通骁龙8 Gen 2采用UMA设计，GPU与CPU共享LPDDR5X内存，总带宽约76.8 GB/s。一款移动游戏若将所有纹理以RGBA8888格式保存而不使用ASTC压缩，一套角色贴图集（Albedo + Normal + PBR）在1024×1024下未压缩需要12 MB，而ASTC 6×6压缩后仅需约2.2 MB，在共享内存池极其有限的移动端，这种差距直接决定游戏是否会触发iOS/Android的内存警告并被系统杀死。

---

## 常见误区

**误区一：VRAM占用显示正常就代表没有内存问题。**  
GPU驱动程序会在VRAM满载时静默地将资源迁移至系统RAM（称为内存溢出或"fall back to system memory"），此时NVIDIA控制面板或任务管理器显示的VRAM占用可能不超过总容量，但渲染性能已经因PCIe带宽瓶颈而严重下降。正确的诊断方法是同时监控"专用显存"与"共享显存"两项数值，后者非零即表明已发生溢出。

**误区二：主机平台的内存总量等于游戏可用内存。**  
以Xbox Series X为例，其16 GB GDDR6内存中，约2.5 GB由操作系统、社交层（Party、截图功能）和快速切换缓冲区预留，游戏实际可用约13.5 GB，且其中10 GB带宽为560 GB/s（高速池），其余3.5 GB带宽为336 GB/s（标准池）。将所有预算都按16 GB来规划，会在认证阶段因超出系统保留边界而直接被拒。

**误区三：集成显卡"没有显存"所以性能一定差。**  
集成显卡确实没有独立VRAM，但这不等于没有GPU可用内存。现代UMA架构中，GPU动态从共享内存池分配所需空间，上限通常是系统内存的50%（可在BIOS调整）。真正导致集成显卡性能差的是内存带宽不足（如76 GB/s vs 1008 GB/s），而非"没有显存"这一错误表述。在针对集成显卡优化时，减少内存带宽消耗（降低纹理分辨率、使用压缩格式）比减少内存总用量更为关键。

---

## 知识关联

本文所述的RAM/VRAM/共享内存三分法是后续所有内存预算规划的基础坐标系。**纹理内存预算**将在VRAM预算框架下，具体讨论mipmap、压缩比和流式策略如何在8 GB典型VRAM限制内容纳数百张材质。**网格内存预算**将区分顶点缓冲在VRAM中的驻留策略与LOD系统在RAM中的预加载队列。**内存池管理**将利用本文的分类直接说明如何为不同内存类型分别建立分配器。**主机内存限制**则会将PS5/Xbox Series X的具体数字细化为开发规范。**音频内存预算**涉及PCM流在系统RAM中的管理，与VRAM预算相互独立但共同消耗整机内存总量。前置知识**性能优化概述**中关于CPU/GPU时间线的理解，是本文PCIe传输延迟对帧时间影响分析的铺垫。