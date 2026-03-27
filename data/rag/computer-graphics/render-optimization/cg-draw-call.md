---
id: "cg-draw-call"
concept: "Draw Call优化"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.424
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Draw Call优化

## 概述

Draw Call（绘制调用）是CPU向GPU发送"绘制这批几何体"的指令，每次调用都会触发一次完整的渲染状态校验与命令提交流程。在DirectX 11和OpenGL传统管线中，单次Draw Call的CPU端开销约为数十微秒，当场景中存在数千个独立物体时，单帧仅Draw Call的CPU消耗就可能超过16ms的帧预算，导致CPU成为渲染瓶颈。

Draw Call开销的历史可追溯到固定功能管线时代。DirectX 9时期，业界普遍将每帧2000次Draw Call视为移动平台的危险阈值，桌面平台约为5000次。随着DirectX 12和Vulkan的出现，多线程命令录制将单次Draw Call的CPU开销降低至约1微秒，但Draw Call数量仍然影响命令缓冲区大小和GPU提交频率，优化依然有价值。

减少Draw Call的核心意义在于降低CPU与GPU之间的同步等待和命令提交次数，让GPU能以更高的占用率持续工作，而不是频繁等待CPU准备下一条指令。

## 核心原理

### 静态批处理（Static Batching）

静态批处理在**构建时或加载时**将多个不移动的网格合并为单一顶点缓冲区（VBO），运行时以一次Draw Call提交整个合并后的网格。其前提是所有合并对象必须共享**同一材质实例**（相同Shader + 相同贴图 + 相同参数），这是因为一次Draw Call只能绑定一套渲染状态。

Unity引擎的静态批处理会为每个参与批次的对象在内存中保留原始顶点副本，因此会增加内存占用。合并100个各含500顶点的小物体，额外内存增量为 100 × 500 × (顶点stride字节数)，在顶点格式为32字节时约增加1.6MB。这是以空间换Draw Call数量的典型权衡。

### GPU Instancing（实例化渲染）

GPU Instancing允许单次Draw Call绘制同一网格的N个实例，每个实例通过**实例化缓冲区（Instance Buffer）**传递差异化数据，如变换矩阵、颜色或自定义属性。其核心API调用为 `DrawIndexedInstanced(indexCount, instanceCount, ...)` （DirectX）或 `glDrawElementsInstanced(mode, count, type, indices, instancecount)` （OpenGL）。

Instancing最适合绘制大量外观一致但位置/朝向不同的对象，例如草地、树木、粒子和人群。关键限制是所有实例**必须共享同一网格和材质**，但材质参数可以通过实例缓冲区逐实例变化（如颜色偏移）。当实例数量低于约20个时，Instancing的额外驱动开销可能使其性能劣于普通批处理，实际阈值因GPU架构而异。

### Indirect绘制（Indirect Draw）

Indirect Draw（如 `DrawIndexedInstancedIndirect` 或 `glMultiDrawElementsIndirect`）将绘制参数（顶点数量、实例数量、偏移量）存储在GPU显存缓冲区中，CPU只需提交"从缓冲区读取参数并绘制"的指令，**绘制参数本身由GPU上的Compute Shader动态填写**。

这一机制使GPU剔除（GPU Culling）成为可能：Compute Shader在GPU端完成视锥剔除和遮挡剔除后，将可见物体的绘制参数写入Indirect Buffer，CPU完全不介入可见性判断，彻底解耦CPU与场景规模的线性关系。《刺客信条：奥德赛》等现代3A游戏正是借助Indirect Draw将场景规模扩展至数十万个可绘制对象。

### 动态批处理（Dynamic Batching）

动态批处理在**每帧运行时**将小型动态网格合并，代价是CPU需要在每帧执行顶点变换和合并操作。Unity的动态批处理对单个网格的顶点数上限为300个顶点（未蒙皮），且受到15个以上UV通道等诸多限制。由于每帧合并成本较高，动态批处理对拥有复杂网格的对象实际上可能带来负收益，应优先考虑Instancing替代。

## 实际应用

**移动端游戏UI优化**：UI元素通常使用精灵图集（Sprite Atlas），同一图集内的所有UI元素共享一张贴图，渲染器可将相邻渲染层级的元素批入同一Draw Call。UGUI在Canvas下自动合批，但层级插入其他Shader类型的元素会打断批次（Batch Break），导致Draw Call数量翻倍。

**植被系统**：Unity HDRP和URP均内置了对草地和树木的GPU Instancing支持。渲染1000棵相同树木时，启用Instancing可从1000次Draw Call降至1次，实测在中端移动GPU上帧时间可从12ms降至3ms。

**场景物件批处理工作流**：美术资产管线中通过统一材质规范（如限制场景物件使用不超过5套材质），配合静态批处理，可使室外场景Draw Call从3000次降至400次以下。这要求美术与渲染工程师共同制定贴图打包（Texture Atlas）策略。

## 常见误区

**误区一：Draw Call数量越少越好，不惜一切代价合并**。过度合并会导致显存中存在巨大的合并网格，即使视口中只可见其中一小部分，GPU仍需处理完整几何体，实际可能增加顶点着色器工作量。正确做法是先做LOD和视锥剔除，再对通过剔除的可见对象执行批处理。

**误区二：Instancing总比静态批处理快**。静态批处理将数据预合并，运行时顶点访问是连续内存访问，缓存友好性更好；Instancing需要Shader内执行矩阵乘法等变换，在实例数量少时反而更慢。两者适用场景不同：静态不动的少量大型物件用静态批处理，大量重复小物件用Instancing。

**误区三：DirectX 12/Vulkan已经解决了Draw Call问题，无需优化**。虽然新API将单次Draw Call的CPU开销从~50μs降至~1μs，但在移动端（使用GLES 3.2或Vulkan移动版）驱动开销依然显著，且命令缓冲区大小仍受显存带宽限制，百万级Draw Call仍会造成帧率下降。

## 知识关联

理解Draw Call优化需要先掌握**渲染管线的CPU提交阶段**，明确哪些操作发生在CPU端、哪些在GPU端，才能判断瓶颈位置。

Draw Call优化的下一个关键话题是**状态排序（State Sorting）**：仅减少Draw Call数量不够，Draw Call的提交顺序影响状态切换次数（如Shader切换、渲染目标切换），无序提交会引入额外的GPU管线刷新开销，状态排序将相同渲染状态的Draw Call归组，与批处理形成互补。

另一个直接关联的技术是**图集批处理（Texture Atlas Batching）**：批处理的前提是共享材质，而共享材质的核心障碍往往是不同对象使用不同贴图。将多张小贴图打包进图集（Atlas），使原本无法合批的对象共享同一贴图，是将Draw Call优化落地的关键美术工作流。