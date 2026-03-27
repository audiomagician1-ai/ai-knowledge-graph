---
id: "vfx-vfxgraph-overview"
concept: "VFX Graph概述"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.517
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# VFX Graph概述

## 概述

Unity VFX Graph 是Unity引擎中基于节点式可视化编程的粒子特效编辑系统，于2018年随Unity 2018.3版本以预览版形式首次发布，并在Unity 2019.3版本中正式进入稳定版（Production Ready）。与Unity传统的粒子系统（Particle System / Shuriken）不同，VFX Graph将全部粒子计算任务卸载至GPU，利用Compute Shader在GPU上并行执行粒子逻辑，使单个特效中的粒子数量可突破百万级别。

VFX Graph仅支持具有Compute Shader能力的现代图形API，包括DirectX 11/12、Vulkan、Metal和PlayStation 5等平台。这一硬件限制意味着VFX Graph目前无法在移动端老旧设备或WebGL环境中运行，这是选用该系统时必须优先考量的因素。VFX Graph的数据文件格式为`.vfx`，本质上是一个包含有向图结构的JSON-like资产，存储于Unity工程的Assets目录中。

VFX Graph的核心价值在于两点：一是通过GPU粒子模拟极大提升特效规模与视觉复杂度；二是通过可视化节点图替代脚本编写，让美术人员能够在不编写C#代码的前提下独立制作复杂粒子行为。这两点共同构成了VFX Graph区别于Shuriken的根本性差异。

## 核心原理

### GPU驱动的粒子模拟

VFX Graph将每个粒子的属性（位置、速度、颜色、生命周期等）储存在GPU显存中的粒子缓冲区（Particle Buffer）里，每一帧通过Compute Shader并行计算所有存活粒子的状态更新。相比之下，Shuriken在CPU上执行粒子逻辑，每帧需要通过DrawCall将粒子数据从CPU内存传输至GPU，形成带宽瓶颈。VFX Graph消除了这一CPU-GPU数据传输开销，从而支撑百万数量级的粒子实时运算。

一个典型的VFX Graph特效在运行时，粒子数据全程驻留在GPU显存中，CPU端只负责提交少量参数（如播放速度、发射速率）给GPU，这种架构被称为"GPU-Resident"模式。

### 节点图结构与执行顺序

VFX Graph使用有向无环图（DAG，Directed Acyclic Graph）来描述粒子行为逻辑。图中的节点分为两类：**Operator（运算节点）**负责数值计算（如加法、噪声、随机数），**Block（行为块）**负责定义粒子在特定阶段的行为（如Set Velocity、Gravity）。这些Block被组织进**Context（上下文）**容器中，构成粒子生命周期的各个阶段。

整张图的执行顺序严格遵循：`System Initialize → Update → Output`的生命周期管线，这与GPU Compute Shader的Dispatch调用顺序直接对应。

### 与渲染管线的绑定关系

VFX Graph要求项目使用**高清渲染管线（HDRP）**或**通用渲染管线（URP）**，无法在内置渲染管线（Built-in Render Pipeline）中工作。在Unity 2021.2之后，URP对VFX Graph的支持已较为完整，但HDRP仍提供更多高级光照选项，例如受HDRP光照影响的粒子Lit Output。VFX Graph的Output Context最终会调用SRP（Scriptable Render Pipeline）的Batch Renderer来执行GPU Instancing渲染，进一步减少DrawCall开销。

## 实际应用

**大规模环境特效**：在游戏场景中模拟暴风雪、火山爆发或沙尘暴时，VFX Graph能以超过50万粒子的规模在现代PC（如RTX 3070）上维持60fps稳定运行，而Shuriken在超过10万粒子时通常已出现明显性能下降。

**实时事件响应特效**：通过VFX Graph提供的`Event`接口，可以在C#中调用`visualEffect.SendEvent("OnHit")`，精确触发某个特效图内部定义的事件，驱动特定的Spawn Context执行。这使得"命中特效""技能释放特效"等需要与游戏逻辑精确同步的特效制作变得简洁直观。

**程序化特效生成**：VFX Graph支持通过`Exposed Property`向图中暴露可在Inspector或C#中动态修改的参数，如粒子颜色、发射半径等。美术可以将同一张VFX图复用于多个场景，仅通过修改Exposed属性来产生差异化视觉效果，而无需复制多份资产。

## 常见误区

**误区一：VFX Graph是Shuriken的升级版，可以完全替代**
这是常见的错误认知。VFX Graph不支持Built-in渲染管线，也不支持不具备Compute Shader能力的平台（如大多数旧款Android设备），而Shuriken在这些平台上仍可正常运行。对于移动端项目或需要广泛平台兼容性的游戏，Shuriken依然是更合适的选择。两者在当前阶段是并列存在、各有适用场景的系统。

**误区二：节点越多，特效性能越差**
VFX Graph中的Operator节点（数学运算）会被Unity编译进Compute Shader的HLSL代码中，在GPU上执行时其性能代价远低于粒子数量本身。增加10个Vector3加法Operator对帧率的影响，远不如将粒子数量从10万增加到20万显著。真正决定VFX Graph性能的核心指标是**活跃粒子数量**和**Output Context使用的渲染通道复杂度**，而非图中节点的数量。

**误区三：VFX Graph只能制作粒子特效**
VFX Graph的Output Context不仅支持Billboard Quad（公告板面片，即传统粒子），还支持输出Mesh粒子（每个粒子渲染一个指定网格）、Line Strip（线段），以及在HDRP中输出受全局光照影响的Lit粒子。这意味着VFX Graph可用于制作程序化植被摆动、大规模群体动画等超出传统"粒子特效"范畴的应用。

## 知识关联

学习VFX Graph概述是进入该系统所有后续概念的起点。下一个直接衔接的概念是**Context系统**，它定义了VFX Graph图内粒子生命周期的四种核心阶段（Spawn、Initialize、Update、Output），是整张VFX图的骨架结构。理解GPU-Resident粒子模拟的架构原理，有助于后续理解为何Initialize Context只执行一次而Update Context每帧执行，以及为何在VFX Graph中访问碰撞数据的方式与Shuriken完全不同。

此外，VFX Graph与Unity **Shader Graph**共享相似的节点编辑器UI框架（均基于Unity的GraphView API构建），但两者解决的问题域完全不同——Shader Graph处理材质着色逻辑，VFX Graph处理粒子行为逻辑。了解这一关系有助于避免在学习阶段混淆两个系统的使用场景。