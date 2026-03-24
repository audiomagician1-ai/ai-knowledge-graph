---
id: "vfx-niagara-gpu"
concept: "GPU模拟"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# GPU模拟

## 概述

GPU模拟（GPU Compute Sim）是Niagara系统中的一种粒子执行模式，它将粒子的生成、更新、碰撞等所有计算任务从CPU迁移到GPU的计算着色器（Compute Shader）上执行。与CPU模拟每帧仅能在单线程或有限线程中处理数千粒子不同，GPU模拟利用GPU的大规模并行架构，理论上可在单帧内同步处理**数十万乃至数百万个粒子**，同时保持60fps的实时渲染性能。

该功能的基础是DirectX 11引入的Compute Shader技术（2009年），Unreal Engine 4.20版本将其整合进Niagara系统的早期Preview版本，至UE5正式成为生产级特性。GPU模拟的核心意义在于打破了CPU粒子数量的上限瓶颈——大型烟雾、沙尘暴、成千上万枚子弹的弹道轨迹，这些效果在CPU模拟下会导致明显的帧率下降，而GPU模拟将计算负载转移到本就负责图形渲染的硬件上，实现了计算资源的充分利用。

## 核心原理

### 执行模型：并行线程组

GPU模拟的调度单位是**线程组（Thread Group）**。Niagara GPU模拟默认将粒子分配到大小为64的线程组中，每个线程对应一个粒子的计算任务。当场景中有512,000个活跃粒子时，系统会自动分配8,000个线程组并行执行。这与CPU模拟的串行逐粒子迭代有本质区别：CPU每帧遍历所有粒子的时间复杂度为O(n)，而GPU模拟在线程数充足时接近O(1)的墙钟时间（wall-clock time）。

### 粒子数据存储：GPU缓冲区结构

CPU模拟的粒子属性存储在系统主内存（RAM）中，而GPU模拟的所有粒子属性——位置（float3）、速度（float3）、生命周期（float）、颜色（float4）等——均以**StructuredBuffer**或**RWBuffer**的形式常驻于显存（VRAM）中。这意味着每帧CPU端**无需回读粒子数据**，避免了PCIe总线传输的延迟（典型延迟约0.3ms~1ms，对于百万级粒子可能高达数毫秒）。启用GPU模拟后，在Niagara发射器属性面板中将"Sim Target"设置为`GPUCompute Sim`，同时需关闭`Fixed Bounds`外的动态边界估算。

### 粒子上限与Fixed Bounds

GPU模拟要求在编辑阶段手动指定**最大粒子数（Max GPU Particle Count）**，默认上限为**1,048,576（即2²⁰ = 1M）**粒子，这是因为GPU显存缓冲区必须在初始化时静态分配。超出此数量的粒子发射请求会被系统静默丢弃，不会触发运行时报错，因此性能调试时需特别注意实际粒子数与上限的关系。与此同时，GPU模拟必须配置**Fixed Bounds**（固定包围盒），因为GPU端的粒子位置数据无法在每帧廉价地同步回CPU用于Visibility Culling的AABB计算，固定包围盒告知渲染器该发射器始终占据的空间范围。

### 碰撞与深度缓冲采样

GPU模拟支持基于**场景深度缓冲（Scene Depth Buffer）**的碰撞检测，对应Niagara模块`Collision (GPU)`。该模块在每个粒子的移动步骤中对当前帧的深度贴图进行采样，将粒子的屏幕空间投影位置与深度值比较，检测穿透后执行反弹或销毁。这种方法计算代价极低（每粒子约1次纹理采样），但存在固有局限：**相机背面或屏幕外的几何体无法参与碰撞**，且碰撞精度受深度缓冲分辨率影响。

## 实际应用

**大规模弹道与战场粒子效果**：在射击类游戏中，同屏爆炸产生的碎石、弹壳、火星可能需要50,000~200,000粒子同时运动。使用GPU模拟后，单个爆炸效果的粒子数可从CPU模式下的500个提升至50,000个，视觉密度提升100倍，而GPU耗时仅增加约0.8ms（在RTX 3080级别GPU上测试数据）。

**流体状烟雾与大气散射**：体积烟雾效果通常需要在3D空间中密集分布数十万个代表烟雾微粒的点粒子或Sprite粒子。结合`Curl Noise Force`模块，GPU模拟可以在每帧内为每个粒子独立计算三维旋度噪声偏移，产生自然流动的烟雾形态，这在CPU模式下因计算量过大几乎无法实时运行。

**GPU模拟与Mesh粒子的结合**：在CPU模式下，每个Mesh粒子需要独立的Draw Call，10,000个Mesh粒子意味着10,000次Draw Call，这对渲染线程是灾难性的。切换到GPU模拟后，Niagara通过**GPU Instancing**将所有同类Mesh粒子合并为1次Instanced Draw Call，Draw Call数量降低至1，同时GPU端计算每个实例的变换矩阵，这是Mesh粒子大规模使用的前提条件。

## 常见误区

**误区一：GPU模拟总是比CPU模拟快。** 对于粒子数量少于约5,000个的简单效果，GPU模拟反而可能因为Compute Shader的调度开销、显存分配和同步机制，导致比CPU模拟多出约0.1~0.3ms的固定成本。GPU模拟的优势需要粒子数量足够大才能显现，通常建议以**10,000粒子**作为考虑切换的参考阈值。

**误区二：GPU模拟支持所有Niagara模块。** 许多依赖CPU端逻辑的模块——例如`Spawn Per Unit`的精确距离计算、读取场景Actor位置的`Get Actor Position`、以及大部分事件（Event）系统——在GPU模拟模式下不可用或功能受限。Niagara编辑器会用橙色警告标注不兼容模块，开发者切换Sim Target前必须审查模块兼容性列表。

**误区三：Fixed Bounds设大一些没有副作用。** 过大的Fixed Bounds会导致渲染器的遮挡剔除（Occlusion Culling）失效——即使粒子系统实际上完全在相机视锥之外，引擎仍会因为包围盒与视锥相交而执行GPU模拟计算，造成不必要的GPU开销。应将Fixed Bounds设置为粒子实际运动范围的1.1~1.5倍，而非无脑扩大。

## 知识关联

学习GPU模拟需要先掌握**Mesh粒子**的基本配置，原因是GPU模拟与Mesh粒子结合时涉及Instanced Rendering的概念，理解Mesh粒子的Draw Call问题能让开发者清晰认识到GPU模拟在渲染批处理上的具体收益。

GPU模拟是**Simulation Stage**（模拟阶段）的必要前提：Simulation Stage允许在单帧内对GPU粒子执行多次迭代计算（例如流体模拟的多步积分），而这种多Pass计算机制只有在粒子数据完全驻留于显存时才能高效实现，CPU模拟无法支持Simulation Stage。

在性能分析方向，GPU模拟的开销需要通过**GPU Profile**（Unreal Insights中的GPU Track或`stat gpu`命令）来定量评估，CPU端的`stat Niagara`仅能反映CPU调度时间而非实际GPU计算耗时，两种工具的分工直接由GPU模拟的执行架构决定。
