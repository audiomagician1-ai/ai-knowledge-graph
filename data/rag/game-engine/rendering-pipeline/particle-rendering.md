---
id: "particle-rendering"
concept: "粒子渲染"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 2
is_milestone: false
tags: ["特效"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 粒子渲染

## 概述

粒子渲染是游戏引擎渲染管线中专门处理大量细小、短暂视觉元素的技术体系，用于模拟火焰、烟雾、爆炸、魔法特效、雨雪等自然现象。与静态网格体不同，粒子系统需要在单帧内同时渲染数百到数十万个独立的视觉单元，每个单元拥有独立的位置、旋转、缩放、颜色和生命周期属性。

粒子渲染的发展可追溯到1982年William Reeves在Lucasfilm制作电影《星际迷航II》时提出的粒子系统概念，随后被游戏业界采用。早期粒子系统完全依赖CPU逐帧更新每个粒子的属性，在粒子数量超过数千个时性能开销迅速成为瓶颈。DirectX 11于2009年引入计算着色器（Compute Shader），使GPU粒子成为主流方案，允许百万级别粒子在GPU上并行模拟。

粒子渲染之所以需要专门的管线处理，是因为粒子数量庞大、生命周期极短（通常为0.1秒到10秒）、几何形状极简（多为平面四边形），且渲染顺序直接影响半透明混合的正确性。这些特征与常规不透明几何体的渲染策略截然不同，需要单独设计排序、剔除和批处理策略。

## 核心原理

### Billboard 粒子

Billboard是最基础也最常见的粒子渲染形式，其本质是一个始终朝向摄像机的四边形（Quad），由两个三角形组成，共4个顶点。Billboard的朝向分为三种模式：**屏幕对齐（Screen-Aligned）**让四边形完全平行于屏幕平面；**摄像机朝向（Camera-Facing）**让四边形法线指向摄像机位置；**轴对齐（Axis-Aligned）**将四边形约束在某一固定轴方向旋转，常用于模拟树木或竖直烟柱。

Billboard的朝向矩阵计算使用摄像机的View矩阵的上向量和右向量：粒子的局部坐标轴直接取自View矩阵的第一列（Right）和第二列（Up），从而保证四边形永远正对摄像机。实现时通常将Billboard的顶点展开写入顶点缓冲，或在几何着色器（Geometry Shader）中将单个点扩展为四个顶点的四边形，后者节省了带宽但几何着色器本身存在一定性能开销。

### GPU 粒子

GPU粒子将粒子的物理模拟——位置更新、速度积分、碰撞检测、生命周期递减——全部搬到GPU的计算着色器中执行。粒子数据存储在两个乒乓（Ping-Pong）结构的结构化缓冲区（StructuredBuffer）中：一帧读取缓冲A并将结果写入缓冲B，下一帧反向操作。位置更新公式采用欧拉积分：`P(t+Δt) = P(t) + V(t)·Δt`，速度受重力、风力等外力影响：`V(t+Δt) = V(t) + A·Δt`，其中A为合加速度向量（单位：m/s²）。

GPU粒子的发射与死亡管理通过一个原子计数器（Atomic Counter）配合"自由列表（Free List）"缓冲实现。当粒子生命周期归零时，GPU将其索引推回自由列表；新粒子发射时从自由列表弹出可用索引。这套机制允许GPU粒子在不回读数据到CPU的情况下，完全在GPU端自主管理粒子池，避免了每帧CPU-GPU之间的数据传输开销，Unreal Engine的Niagara系统和Unity的VFX Graph均采用此架构。

### Ribbon 粒子

Ribbon（条带）粒子将同一粒子发射器连续发射的粒子点串联成一条光滑曲线形状，常用于模拟闪电、刀光、飞行轨迹等拖尾效果。Ribbon的几何体由相邻粒子点之间的"样条挤出"构成：对于每相邻两个粒子点P₀和P₁，沿其连线的垂直方向（在屏幕空间或世界空间中）拉伸出宽度W，形成一个矩形段。

Ribbon的UV坐标有两种常用分配方式：**拉伸模式**将整条Ribbon的纹理从头到尾拉伸为0到1；**平铺模式**按每段的世界空间长度重复纹理，保证纹理像素密度均匀。当Ribbon节点数量超过设定上限（Unreal中默认为30个节点）时，最旧的节点会被移除，形成动态滚动的轨迹效果。

### Mesh 粒子

Mesh粒子将普通的三维网格体作为粒子的视觉表示，而不是平面四边形。这允许渲染碎石、硬币、落叶等具有真实三维形态的粒子效果。由于每个Mesh粒子共享同一份顶点缓冲数据，渲染时使用GPU实例化（GPU Instancing）技术：单次DrawCall通过`DrawIndexedInstanced`接口提交，每个实例读取各自的变换矩阵、颜色偏移等逐实例数据。

Mesh粒子的性能瓶颈与Billboard粒子截然不同：Billboard的顶点数固定为4，而Mesh粒子的顶点数取决于网格体复杂度，一个200面的碎石粒子在1万个实例时需要处理200万个顶点。因此Mesh粒子通常配合LOD（细节层级）技术，在粒子远离摄像机时自动切换到面数更少的网格版本。

## 实际应用

**爆炸特效**通常组合使用多种粒子类型：初始冲击波使用Mesh粒子（扭曲的球形网格）、火焰核心使用Billboard粒子配合加法混合（Additive Blending）、烟雾使用Billboard粒子配合透明混合（Alpha Blend）、飞溅碎片使用Mesh粒子的GPU实例化渲染。

**半透明排序**是粒子渲染在实际项目中最常见的视觉问题。粒子使用Alpha Blend时必须从后向前排序（Painter's Algorithm），否则远处粒子会遮挡近处粒子。GPU粒子排序通常使用GPU上的并行基数排序（Radix Sort）算法，对粒子按摄像机深度值（View-space Z值）排序，每帧排序的时间复杂度为O(n)。

**Unreal Engine的Niagara**将粒子渲染分为模拟阶段（Simulate Stage）和渲染阶段（Render Stage），允许同一套粒子数据同时驱动Billboard渲染器、Ribbon渲染器和Mesh渲染器，三种渲染器并行工作，极大提升了特效的视觉复杂度。

## 常见误区

**误区一：Billboard粒子始终比Mesh粒子性能好。** 这一判断忽略了DrawCall数量的影响。如果Mesh粒子能通过GPU Instancing合并为单次DrawCall，而Billboard粒子由于使用了不同贴图导致批次被打断，Mesh粒子的实际渲染开销反而可能更低。真正影响粒子渲染性能的是Overdraw（同一像素被多个半透明粒子重复绘制）而非粒子类型本身。

**误区二：GPU粒子完全不需要CPU参与。** GPU粒子的模拟确实在GPU执行，但发射参数（发射位置、发射速率、初速度范围）通常仍由CPU上的游戏逻辑每帧写入一个小型常量缓冲区（Constant Buffer）。只有粒子的逐粒子物理积分才是纯GPU计算，粒子系统的行为控制逻辑依然依赖CPU。

**误区三：Ribbon粒子只需存储粒子位置。** Ribbon渲染正确显示还需要存储每个节点的切线方向和宽度，若仅存储位置，当相邻两点的连线方向突变时，Ribbon的垂直展开方向会发生翻转，产生"蝴蝶结"形状的几何错误。

## 知识关联

粒子渲染建立在渲染管线概述的基础上——理解顶点缓冲、DrawCall提交流程和混合状态（Blend State）是读懂粒子渲染实现细节的前提。粒子的Billboard矩阵构建直接使用了View矩阵的列向量，与相机系统的坐标变换知识紧密相连。GPU粒子的计算着色器调度涉及线程组（Thread Group）和共享内存（Shared Memory）的使用，与GPU计算管线的知识体系相互补充。半透明粒子的排序与深度缓冲的关系，则将粒子渲染与深度测试、帧缓冲管理等渲染管线后处理阶段紧密联系在一起。