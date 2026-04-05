---
id: "render-graph"
concept: "渲染图(RDG)"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 渲染图（RDG）

## 概述

渲染图（Render Dependency Graph，RDG）是一种将一帧内所有渲染操作组织为有向无环图（DAG）的调度系统，图中每个节点代表一个渲染Pass，每条有向边代表Pass之间的资源依赖关系。RDG的核心职责是：在帧开始时声明全部Pass及其输入输出资源，在帧结束前由系统自动推断资源生命周期、插入必要的屏障（Barrier）并剔除无效Pass，最终以最优顺序提交GPU命令。

RDG概念的工程化落地以2017年育碧在GDC上发表的《Framegraph: Extensible Rendering Architecture in Frostbite》为标志性里程碑，寒霜引擎（Frostbite）率先将帧图思想应用于生产项目。此后，虚幻引擎4.22版本（2019年）引入了自己的RDG实现，并在UE5中将其作为所有渲染代码的强制路径。RDG的出现解决了手动管理Vulkan/DX12显式API中资源状态的复杂性——在这些API下，程序员必须精确控制每个纹理从`D3D12_RESOURCE_STATE_RENDER_TARGET`切换到`D3D12_RESOURCE_STATE_SHADER_RESOURCE`的时机，而RDG将这一繁琐工作完全自动化。

RDG之所以重要，在于它将"描述帧"与"执行帧"彻底分离。开发者只需声明Pass的读写关系，系统即可在编译阶段完成Pass裁剪（Culling）和资源别名（Aliasing），将瞬态资源的GPU显存占用降低30%~50%（寒霜引擎实测数据），同时避免了手动排布屏障时极易产生的竞态条件（Race Condition）。

---

## 核心原理

### 1. 帧图的构建阶段（Setup Phase）

在Setup阶段，CPU端按逻辑顺序调用`AddPass()`注册每个Pass，每个Pass通过`FRDGBuilder`声明它所读取（`Read`）和写入（`Write`）的`FRDGTexture`或`FRDGBuffer`对象。这些资源在此阶段仅是虚拟句柄，尚未分配实际GPU内存。以UE5的代码模式为例：

```cpp
FRDGTextureRef SceneColor = GraphBuilder.CreateTexture(Desc, TEXT("SceneColor"));
GraphBuilder.AddPass(
    RDG_EVENT_NAME("BasePass"),
    PassParameters,
    ERDGPassFlags::Raster,
    [](FRHICommandList& RHICmdList) { /* 执行体 */ }
);
```

系统将所有Pass及资源引用存入内部DAG，此时不发出任何GPU命令。整个Setup阶段完全在CPU上完成，通常耗时低于0.5ms。

### 2. 图编译阶段（Compile Phase）

编译阶段执行三项关键操作：

- **Pass裁剪**：从最终输出资源（如交换链后缓冲区）出发，反向遍历DAG，凡是其输出不被任何后续Pass或最终输出引用的Pass将被标记为Culled并跳过执行。这使得调试用的截图Pass或未开启的特效Pass无需手动开关即可自动剔除。
- **资源生命周期推断**：系统记录每个资源的"首次写入Pass"与"最后一次读取Pass"，据此确定资源的`FirstAccess`和`LastAccess`，将生命周期不重叠的资源映射到同一块GPU内存（资源别名/Aliasing），这是瞬态资源（Transient Resources）的核心节省机制。
- **屏障插入**：根据相邻Pass对同一资源的访问类型差异（如从`UAV_WRITE`变为`SRV_READ`），系统在两Pass之间自动插入`ResourceBarrier`，保证读写一致性，同时将屏障批量合并以减少API调用次数。

### 3. 执行阶段（Execute Phase）

执行阶段按编译后的拓扑顺序依次调用各Pass的Lambda函数体。在调用前，RDG将虚拟资源句柄解析为真实的`FRHITexture`或`FRHIBuffer`指针，并提交该Pass所需的屏障。支持异步计算（Async Compute）的引擎（如UE5）会在此阶段将`ERDGPassFlags::AsyncCompute`标记的Pass调度到Async Compute队列，与图形队列并行执行，典型情景是将SSAO计算与GBuffer渲染重叠执行，节省约0.8~1.2ms帧时间（视GPU型号而定）。

---

## 实际应用

**延迟渲染管线中的GBuffer管理**：在延迟渲染中，GBuffer由4~5张纹理组成（Albedo、Normal、Roughness/Metallic、Depth）。使用RDG时，BasePass声明对所有GBuffer纹理的Write权限，LightingPass声明对全部GBuffer的Read权限，系统自动在两Pass之间插入从`RENDER_TARGET`到`SHADER_RESOURCE`的状态转换屏障，开发者无需关心DX12的`D3D12_RESOURCE_STATE`枚举值。

**瞬态资源的显存复用**：后处理链中，SSAO纹理在LightingPass读取后即失效，而后续的Bloom降采样纹理在BloomSetup之后也不再需要。RDG的Aliasing机制可以让这两张分辨率和格式相同的纹理共享同一段64MB的瞬态堆（Transient Heap）内存，物理显存只分配一次。

**条件性Pass的零开销裁剪**：当玩家关闭动态阴影设置时，ShadowDepthPass的输出纹理不会被后续任何Pass引用，RDG在编译阶段将其Cull，CPU端的`AddPass()`调用的开销仅为记录一个节点入图，Lambda函数体永远不会执行，不产生任何GPU命令，也不分配Shadow Map显存。

---

## 常见误区

**误区一：认为RDG是运行时调度，Setup阶段会阻塞GPU**
RDG的Setup阶段完全是CPU端的图构建操作，不发出任何GPU命令。GPU命令仅在Execute阶段提交。因此频繁调用`AddPass()`本身不会造成GPU等待，但若在Setup阶段进行大量CPU计算，则会延迟整帧的命令提交时机，间接影响GPU利用率。

**误区二：认为被Cull的Pass的Lambda函数体不会被编译器优化**
Pass被Culled仅意味着Execute阶段不调用Lambda，但Lambda本身仍被编译进二进制。更重要的是，传入`AddPass`的`PassParameters`结构体中的资源引用会被RDG用于建立依赖关系，即使Pass被Cull，这些资源的引用仍会影响生命周期分析，因此不能通过传入空Parameters来"欺骗"系统跳过依赖检测。

**误区三：以为RDG可以自动处理跨帧资源**
RDG仅管理单帧内的瞬态资源生命周期。跨帧持久资源（如TAA历史帧缓冲区、阴影缓存）必须使用`RegisterExternalTexture()`以外部资源形式注入RDG，由开发者负责其状态管理，RDG只负责记录该资源在本帧内的访问状态并在帧末将其状态正确归还给外部所有者。

---

## 知识关联

RDG建立在**GPU驱动渲染**（GPU-Driven Rendering）的显式API基础之上：Vulkan和DX12要求程序员手动声明资源状态转换，RDG正是对这一显式管理需求的高层封装，将图形程序员从逐资源的屏障管理中解放出来，专注于渲染算法本身。

掌握RDG之后，下一个学习目标是**GPU性能分析**（GPU Profiling）。RDG为性能分析提供了天然的结构化数据：每个`RDG_EVENT_NAME`标记的Pass都会在RenderDoc、Nsight等工具中形成独立的性能区间，Pass的Cull率、瞬态内存的Aliasing命中率等指标直接反映帧图设计的优劣。理解RDG的编译与执行分离机制，是正确解读GPU Capture中时间线和内存占用图的前提。