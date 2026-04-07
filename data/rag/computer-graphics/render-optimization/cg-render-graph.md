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
updated_at: 2026-03-30
---

# 渲染图（Render Graph / Frame Graph）

## 概述

渲染图（Render Graph，也称 Frame Graph）是一种将帧内所有渲染Pass及其资源依赖关系显式声明为有向无环图（DAG）的高层抽象系统。其核心思想由 Yuriy O'Donnell 在 2017 年 GDC 演讲《Frame Graph: Extensible Rendering Architecture in Frostbite》中系统提出，Frostbite 引擎随后将其工程化落地。与传统的"命令式"渲染流程不同，渲染图要求程序员在帧开始时**声明**所有Pass的输入输出资源，引擎再根据依赖关系自动完成资源生命周期管理、Pass排序和屏障插入。

渲染图解决了现代渲染管线中两个长期存在的工程痛点：其一，GPU资源（Texture、Buffer）的瞬态生命周期管理极为复杂，手动跟踪每张RT何时可以被Alias极易出错；其二，Vulkan / D12等低层API要求开发者手动插入精确的Pipeline Barrier和Image Layout转换，传统写法容易引入过度同步或遗漏同步。通过图结构，这两类问题都可以算法化处理，大幅减少渲染工程师的心智负担。

渲染图不仅是工程工具，它本质上也是一种**渲染优化框架**：通过自动裁剪（Culling）未被最终输出依赖的Pass、自动堆叠瞬态资源的显存别名（Memory Aliasing），可以将帧内GPU显存占用降低20%~40%（Frostbite的实测数据）。

---

## 核心原理

### 1. 图的构建阶段（Setup Phase）

在每帧开始时，渲染图进入Setup阶段。每个RenderPass通过调用 `builder.Read(resource)` 和 `builder.Write(resource)` 显式声明其资源依赖，并返回经过版本化的资源句柄（Versioned Handle）。每次 `Write` 操作会生成一个新版本号，例如资源 `GBuffer_Albedo` 在几何Pass中写入后变为版本1，SSAO Pass读取版本1后若再写入则升为版本2。这种版本化机制使得图中的每条有向边都精确对应"谁产生了哪个版本的数据"，从而构成真正的DAG而非带环图。

### 2. 编译阶段：Pass裁剪与资源生命周期计算

Setup完成后，渲染图执行一次**反向拓扑遍历**：从最终输出节点（如Swapchain Present节点）开始逆向标记所有被实际引用的Pass；未被标记的Pass（"无效Pass"）会被直接裁剪，其声明的资源也不会被分配显存。这一步的时间复杂度为 O(V + E)，其中 V 为Pass数量，E 为资源依赖边数量。

裁剪完成后，编译器遍历有效Pass的线性执行序列，计算每个资源的 **first_use** 和 **last_use** 时间戳，两个时间戳之间的帧段即为该资源的生命周期区间。不重叠的生命周期区间所对应的资源可进行**显存别名（Memory Aliasing）**——它们共享同一块物理显存，只是在不同时段激活。例如在典型的延迟渲染帧中，GBuffer中的 `Velocity` 纹理（生命周期：Pass 2–5）与 TAA 的 `MotionBlur_Temp`（生命周期：Pass 8–9）若大小格式一致，即可完全共用同一段显存。

### 3. 执行阶段：自动同步与Pass排序

渲染图在已计算好的线性拓扑序下执行，对每对相邻Pass之间的资源状态转换自动生成 Pipeline Barrier（Vulkan）或 Resource Transition（D3D12）。具体来说，对于资源 R，若 Pass A 将其作为 `RENDER_TARGET` 使用，Pass B 将其作为 `SHADER_READ` 使用，则图系统自动在 A、B 之间插入：

```
srcStageMask  = COLOR_ATTACHMENT_OUTPUT
dstStageMask  = FRAGMENT_SHADER
srcAccessMask = COLOR_ATTACHMENT_WRITE
dstAccessMask = SHADER_READ
oldLayout     = COLOR_ATTACHMENT_OPTIMAL
newLayout     = SHADER_READ_ONLY_OPTIMAL
```

这种基于图结构生成的 Barrier 集合在正确性上有形式化保证：图中每条读写边恰好对应一条 Barrier，既不会遗漏同步，也不会插入冗余的全局屏障。

### 4. 瞬态资源池与帧间复用

渲染图将所有在图内创建并在帧末销毁的资源称为**瞬态资源（Transient Resources）**。这类资源通过带有哈希键（格式 + 大小 + Usage标志）的资源池管理，帧内创建时从池中匹配，帧末归还。持久资源（如历史帧的TAA缓冲区）则通过 `Import` 接口显式导入图中，其生命周期由外部代码控制。

---

## 实际应用

**Unreal Engine 5 的 RDG（Render Dependency Graph）**是目前工业界最广泛使用的渲染图实现。UE5 中的 RDG 使用 `FRDGBuilder` 类，每帧通过 `AddPass` 宏声明Pass及其 Lambda 回调，最终调用 `GraphBuilder.Execute()` 触发编译与执行。UE5 的 RDG 还实现了**Pass合并（Pass Merging）**优化：若相邻两个Pass均写入同一RenderTarget集合且无资源状态冲突，可被合并为同一个 Vulkan RenderPass，从而节省 Tile-Based GPU 上代价昂贵的 Framebuffer Flush 操作。

在移动端延迟渲染（如基于 Mali GPU 的设备）中，渲染图的Pass合并尤为重要。Mali 的 TBDR 架构要求将几何Pass（MRT写入）与光照Pass（读取GBuffer）合并为同一个 Subpass，否则会触发 Resolve 操作，产生约 4~8 倍的带宽开销。渲染图的编译器可以自动检测这种可合并模式并生成 Vulkan Subpass，避免手动维护 RenderPass 兼容性矩阵。

---

## 常见误区

**误区1：渲染图等同于多线程渲染**
渲染图的核心价值是资源生命周期管理与自动同步，与多线程录制命令并无直接关联。渲染图可以在单线程上串行执行所有Pass回调，并行化是可选的优化方向，但不是渲染图概念本身的内容。混淆两者会导致工程师期望引入渲染图后自动获得多核性能提升，实际上渲染图在单线程下已具有完整价值。

**误区2：所有Pass都应声明为瞬态资源**
对于需要跨帧持久化的资源（TAA历史帧缓冲、Shadow Map缓存、Irradiance Cache），若错误地声明为瞬态资源，渲染图会在帧末将其归还资源池，下一帧重新分配时数据已清零。正确做法是通过 `Import` 接口将这类资源以持久句柄引入图中，图只负责管理其帧内的读写顺序，不介入其分配与销毁。

**误区3：渲染图的编译开销可以忽略**
渲染图每帧需要执行拓扑排序、引用计数反向遍历和Barrier生成，对于包含200+个Pass的复杂帧，若未使用缓存机制，CPU侧的图编译时间可达0.5~1 ms。UE5 RDG 通过检测Pass集合是否变化来决定是否跳过重编译，称为"Pass Hash"机制。忽视这一开销并在每帧强制重编译，会在Pass数量增加时引入明显的CPU瓶颈。

---

## 知识关联

渲染图建立在**渲染优化概述**中介绍的GPU同步原语（Barrier、Semaphore）和显存分配策略之上——只有理解为何手动管理这些原语容易出错，才能体会渲染图自动化方案的必要性。

在图内部，渲染图与**Vulkan RenderPass/Subpass**机制深度耦合：渲染图的Pass合并优化本质上是将逻辑Pass映射到Vulkan Subpass，充分利用 TileMemory；若对 Subpass Dependency 语义不熟悉，调试渲染图生成的 Barrier 集合时将非常困难。

渲染图的资源版本化思想与**数据流分析（Data Flow Analysis）**中的SSA（Static Single Assignment）形式一脉相承——每次写入产生新版本，等价于 SSA 中对变量的重命名。对编译器原理有了解的工程师可以借助这一类比快速理解渲染图的版本化机制。掌握渲染图后，可进一步研究**可见性剔除**（将剔除结果作为渲染图的间接绘制参数）和**光线追踪管线集成**（光追Pass同样可作为渲染图节点，通过图机制与光栅化Pass共享加速结构资源）。