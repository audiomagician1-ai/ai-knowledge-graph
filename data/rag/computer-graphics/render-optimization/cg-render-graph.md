---
id: "cg-render-graph"
concept: "渲染图"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 4
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 渲染图（Render Graph / Frame Graph）

## 概述

渲染图（Render Graph，有时也称 Frame Graph）是一种将单帧渲染流程抽象为有向无环图（DAG）的资源管理与调度框架，由 Yuriy O'Donnell 在 2017 年 GDC 演讲《FrameGraph: Extensible Rendering Architecture in Frostbite》中系统性地提出并推广。在此框架中，图的每个节点（Node）对应一个渲染阶段（Pass），每条有向边则对应 Pass 之间的资源依赖关系，例如一个 Pass 写入的颜色缓冲恰好是下一个 Pass 读取的输入纹理。

在 Frostbite 引擎引入渲染图之前，大型渲染管线的资源生命周期完全由程序员手工管理，当 Pass 数量超过数十个时，极易出现资源泄漏、无效同步屏障（Barrier）过多，以及无法在主机端并行提交命令包等问题。渲染图通过编译期（Compile Phase）的可达性分析，自动裁剪当前帧中不影响最终 Backbuffer 的"死亡 Pass"，并为剩余 Pass 自动推导所有 GPU 资源的最优生命周期与访问状态转换。

渲染图之所以重要，在于它将"**逻辑描述**"与"**物理执行**"彻底解耦：开发者在声明 Pass 时只需说明"我需要读取哪些资源、写入哪些资源"，而不必关心底层 API（Vulkan / D3D12 / Metal）所要求的具体 Image Layout、Resource State 或 Memory Barrier 时机。这使得渲染管线的新增、删除和重排变得如同编辑图结构一样直观。

---

## 核心原理

### 1. 三阶段执行模型：Setup → Compile → Execute

渲染图的每一帧处理分为三个严格顺序的阶段：

- **Setup（注册阶段）**：所有 Pass 向渲染图声明自身的输入资源（`read`）和输出资源（`write`），并创建对应的虚拟资源句柄（Virtual Resource Handle）。此阶段仅填充图结构，不分配任何 GPU 内存，也不记录任何 GPU 命令。
- **Compile（编译阶段）**：渲染图执行两项关键操作。第一，**剔除（Culling）**：从 Backbuffer 节点出发做逆向 DFS（深度优先搜索），将所有未被引用的 Pass 和资源标记为无效并丢弃，通常可裁剪 10%–30% 的无效工作。第二，**资源别名（Aliasing）**：对生命周期不重叠的虚拟资源分配同一块物理显存，Frostbite 内部数据显示此技术可节省约 **50% 的瞬态渲染目标（Transient Render Target）内存**。
- **Execute（执行阶段）**：按拓扑排序顺序依次执行各 Pass 的回调函数，渲染图在每次 Pass 切换前自动插入精确的 Pipeline Barrier / Resource State Transition，并负责按需分配与释放物理资源。

### 2. 虚拟资源与物理资源的映射

渲染图引入"虚拟资源"概念，是实现自动内存别名的关键。每个虚拟资源由一个描述符（ResourceDesc）唯一标识，包含格式（Format）、分辨率、MipLevel 数、用途标志（Usage Flags）等信息。编译阶段会构建一张**资源生命周期区间表**，区间定义为 `[first_write_pass_index, last_read_pass_index]`，生命周期区间不重叠的资源可以安全共用同一显存地址。公式化描述如下：

> 若资源 A 的区间为 [a₁, a₂]，资源 B 的区间为 [b₁, b₂]，且 a₂ < b₁ 或 b₂ < a₁，则 A 与 B 可别名同一物理内存块。

### 3. 自动 Barrier 推导与异步计算调度

渲染图在 Execute 阶段利用编译期收集到的每个 Pass 对每个资源的最后访问类型（读/写/格式），为 Vulkan 生成精确的 `VkImageMemoryBarrier`，或为 D3D12 生成 `ResourceBarrierTransition`，避免了手工 Barrier 中普遍存在的"过度同步"问题（例如将所有资源统一转换为 `COMMON` 状态）。此外，渲染图可识别哪些 Pass 仅依赖 Compute Queue 资源，将其自动调度到独立的异步计算队列（Async Compute Queue）并行执行，GPU 并行度提升最高可达 **20%–40%**（依硬件而异）。

---

## 实际应用

**Unreal Engine 5 的 RDG（Rendering Dependency Graph）** 是目前应用最广泛的渲染图实现之一。UE5 中每个渲染 Pass 通过 `FRDGBuilder::AddPass()` 宏注册，资源通过 `FRDGTexture` / `FRDGBuffer` 等句柄引用，引擎在每帧 `FRDGBuilder::Execute()` 调用时完成编译与物理提交。Lumen 全局光照的多层 Pass（Screen Probe Gather → Radiance Cache Update → Denoiser）正是依赖 RDG 的拓扑排序确保正确执行顺序，同时将 Surface Cache 更新 Pass 自动卸载到 Async Compute。

**Frostbite 引擎的原始实现**中，Frame Graph 使得寒霜 AAA 游戏（如《战地 1》）将瞬态 RT 内存占用从约 **1.2 GB** 降低到约 **600 MB**，同时彻底消除了手工内存管理导致的渲染顺序错误类 Bug。

在 **Vulkan / D3D12 的移植场景**中，渲染图还被用于自动生成 Render Pass 的 `loadOp`/`storeOp` 配置：若某 RT 在当前帧的上一次写入在同一物理 Render Pass 内，则 `loadOp` 可设为 `DONT_CARE`，节省移动端 TBDR（Tile-Based Deferred Rendering）架构上的带宽开销。

---

## 常见误区

**误区一：渲染图等同于多线程渲染**  
渲染图的拓扑排序和资源别名机制本身是单线程完成的（Setup 和 Compile 阶段通常在主线程执行），它并不直接提供多线程命令录制能力。多线程提交需要在 Execute 阶段额外将 Pass 分组到不同 CommandList 并分配给工作线程，这是在渲染图之上叠加的并行策略，而非渲染图自身功能。

**误区二：渲染图的 Compile 阶段发生在 CPU 上，因此可以忽略其开销**  
编译阶段虽在 CPU 执行，但对于包含 200+ Pass 的复杂帧（例如带完整阴影级联、SSAO、TAA 的场景），DAG 遍历与生命周期计算可消耗 **0.3–1.0 ms** 的 CPU 时间。UE5 的 RDG 为此引入了 Pass 合并（Pass Merging）和渲染图缓存（Graph Caching）等优化以降低重复帧的编译成本。

**误区三：资源别名对所有 GPU 资源都安全适用**  
资源别名仅对生命周期严格不重叠的**瞬态资源**安全。跨帧持久化的资源（如 TAA 历史帧缓冲、Radiance Cache）绝对不能参与别名，否则会发生数据竞争。渲染图通常要求开发者在声明资源时显式标注 `Transient`（瞬态）或 `Imported`（外部导入/持久）标志，编译器据此决定是否允许该资源进入别名候选池。

---

## 知识关联

**前置概念**：渲染优化概述中介绍的 GPU 管线阶段划分（Vertex → Rasterization → Fragment）和渲染目标（Render Target）概念，是理解渲染图中 Pass 输入/输出语义的直接基础。了解 D3D12 Resource State 或 Vulkan Image Layout 的状态机模型，有助于直观理解渲染图自动 Barrier 推导的工作内容。

**横向关联**：渲染图与**多线程命令录制**（Command Buffer Threading）、**GPU Work Graph**（D3D12 Agility SDK 1.710 引入的新特性，允许在 GPU 端动态派发节点工作负载）在设计思路上有共同的"图节点调度"哲学，但渲染图的调度在 CPU 完成，GPU Work Graph 的调度在 GPU 完成，两者解决的问题层次不同。渲染图编译产出的精确 Barrier 序列也是**GPU 帧调试工具**（如 RenderDoc、PIX）中 Resource State Timeline 视图的直接数据来源。
