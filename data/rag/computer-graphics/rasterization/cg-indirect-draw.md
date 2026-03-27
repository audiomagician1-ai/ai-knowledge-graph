---
id: "cg-indirect-draw"
concept: "间接绘制"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 间接绘制

## 概述

间接绘制（Indirect Draw）是一种让GPU直接从显存缓冲区读取绘制参数、无需CPU介入的渲染技术。与传统的直接绘制调用不同，间接绘制将绘制命令（如顶点数量、实例数量、起始偏移等）预先写入一块称为**间接缓冲区（Indirect Buffer）**的显存区域，GPU在执行时自行读取这些参数并驱动光栅化流程。这一机制从根本上打破了CPU必须逐帧向GPU"下命令"的瓶颈。

该技术在DirectX 11时代以`DrawInstancedIndirect`和`DrawIndexedInstancedIndirect`两个API函数正式进入主流图形管线，对应的OpenGL等价接口`glMultiDrawElementsIndirect`在GL 4.3（2012年）中引入。其真正的革命性意义在于：当间接缓冲区的内容由**前一帧的GPU计算着色器填写**时，整个场景裁剪、批次合并、LOD选择等逻辑可以完全在GPU侧完成，CPU仅需发出一次或极少次的间接绘制调用，这便是所谓的**GPU-Driven Rendering**架构的核心实现路径。

间接绘制在场景包含数万个独立网格的大型开放世界游戏中极为关键。以《刺客信条：奥德赛》（2018年）为例，其GPU剔除系统正是依赖间接绘制将CPU侧的Draw Call数量压缩至个位数量级，同时保持十万级别的场景物件渲染。

## 核心原理

### 间接缓冲区的数据结构

在DirectX 12中，`D3D12_DRAW_INDEXED_ARGUMENTS`结构体定义了一次间接绘制所需的全部参数：

```
IndexCountPerInstance  // 每个实例绘制的索引数量
InstanceCount          // 实例数量
StartIndexLocation     // 索引缓冲区的起始位置
BaseVertexLocation     // 顶点偏移量
StartInstanceLocation  // 实例数据的起始偏移
```

这5个32位整数（共20字节）构成一条完整的间接绘制命令。一个间接缓冲区可以连续存储成百上千条这样的结构，GPU逐条读取并执行，效果等同于CPU连续调用数百次`DrawIndexedInstanced`，但完全无需CPU参与。

### GPU-Driven流程中的两阶段渲染

完整的GPU-Driven间接绘制通常分为两个计算着色器阶段：

**第一阶段（剔除与参数生成）**：一个Compute Shader以场景中的每个物件为一个线程，读取该物件的包围盒数据和上一帧的深度缓冲（HZB，Hierarchical Z-Buffer），执行视锥体剔除和遮挡剔除。通过测试的物件，其绘制参数被写入间接缓冲区对应槽位，并通过`AppendStructuredBuffer`或原子计数器记录实际绘制数量。

**第二阶段（间接绘制执行）**：主渲染通道调用`ExecuteIndirect`（DX12）或`glMultiDrawElementsIndirect`（GL），GPU读取第一阶段生成的间接缓冲区，连续执行所有通过剔除的Draw Call。整个过程CPU只调用了**2次**GPU命令：一次Dispatch和一次间接绘制。

### 命令签名与参数验证

DX12引入了`CommandSignature`对象，它定义了间接缓冲区中每条命令的内存布局和步长（stride）。在Vulkan中对应的概念是`VkIndirectCommandsLayoutNV`（NV_device_generated_commands扩展）。这一设计允许每条间接命令携带额外的根常量或描述符绑定变更，从而实现每个物件使用不同材质贴图的**多材质间接绘制**，而不仅限于同质批次。

## 实际应用

**大规模植被与地形渲染**：一块包含50万棵树的森林场景，传统CPU批次可能产生数千次Draw Call。使用间接绘制时，Compute Shader在GPU侧完成实例裁剪和LOD分级（近距离使用高模，超过500米切换为低模），按LOD级别分别填入不同的间接缓冲区槽位，最终仅需3至4次`ExecuteIndirect`调用（对应3至4个LOD级别）完成全部渲染。

**粒子系统的动态批次**：物理模拟计算着色器在更新粒子位置后，同步将存活粒子数量写入间接缓冲区的`InstanceCount`字段。渲染通道直接调用间接绘制，无需CPU读回粒子数量——避免了GPU→CPU的回读同步等待（通常需要1至2帧的延迟代价）。

**遮挡剔除与HZB结合**：上一帧完成后，将深度缓冲降采样生成层次化深度图（HZB）。当前帧的剔除Compute Shader将每个物件的包围盒投影到HZB的适当Mip层级，若包围盒深度大于HZB采样值则判定为被遮挡，不写入间接缓冲区。这一技术使室内复杂建筑场景的Draw Call数量可减少60%至80%。

## 常见误区

**误区一：间接绘制总是比直接绘制更快**

间接绘制仅在场景足够复杂、Draw Call数量构成瓶颈时才能体现优势。对于场景简单（如Draw Call低于200次）的情况，引入Compute Shader剔除阶段和间接缓冲区管理的额外开销反而会使帧时间增加。另外，从显存读取间接参数本身存在约数十纳秒的延迟，当所有物件都不需要剔除时，这个开销是纯粹的浪费。

**误区二：间接绘制消除了所有CPU-GPU同步问题**

间接缓冲区作为GPU资源，在DX12和Vulkan中仍然需要正确的资源状态转换（Resource Barrier）。第一阶段Compute Shader写入间接缓冲区后，必须插入一道`UAV Barrier`，才能确保第二阶段的间接绘制读取到已完成写入的数据。遗漏这个屏障是间接绘制实现中最常见的Bug，表现为随机的渲染缺失或绘制参数错乱。

**误区三：间接绘制中每个物件必须使用相同的管线状态**

这是DX11时代间接绘制的局限性。在DX12的`ExecuteIndirect`配合可变步长`CommandSignature`机制，以及Vulkan的`NV_device_generated_commands`扩展下，每条间接命令可以携带不同的根描述符或推送常量（Push Constant），允许每个物件绑定不同的纹理索引，实现真正意义上的异质批次间接绘制。

## 知识关联

间接绘制依赖**深度缓冲**提供遮挡剔除所需的历史深度信息——HZB正是从上一帧的深度缓冲降采样而来，如果不理解深度缓冲的生成机制和精度特性（如反转深度Reversed-Z带来的精度分布差异），就难以正确配置HZB剔除的比较函数，导致遮挡剔除出现误判（错误剔除可见物件）。

向下一步，**Mesh Shader**（DX12 Agility SDK中引入，对应着色器模型6.5）与间接绘制在GPU-Driven架构中形成互补：Mesh Shader将网格的细分与剔除直接内化到可编程着色器阶段，而间接绘制则负责批次调度的GPU化。两者在现代GPU-Driven Rendering管线中通常协同使用——Mesh Shader处理网格簇（Meshlet）级别的精细剔除，间接绘制负责对象级别的粗粒度批次调度，共同构成高效的多层级剔除体系。