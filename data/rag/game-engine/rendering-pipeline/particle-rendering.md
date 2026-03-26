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

粒子渲染是游戏引擎渲染管线中专门处理大量微小视觉元素的技术体系，用于模拟火焰、烟雾、爆炸、魔法特效、雨雪等自然现象。与静态网格体渲染不同，粒子渲染需要同时管理成千上万个生命周期短暂、属性持续变化的独立图元，每个粒子拥有自己的位置、速度、颜色、透明度和缩放等属性。

粒子系统的概念由William Reeves于1983年在皮克斯（Pixar前身Lucasfilm）开发《星际迷航II：可汗之怒》的"创世纪效果"时首次系统性提出，论文《Particle Systems—A Technique for Modeling a Class of Fuzzy Objects》奠定了该技术的理论基础。早期粒子完全依赖CPU计算每帧的粒子状态，在粒子数量超过数千个时就会造成明显的性能瓶颈。现代游戏引擎（如Unreal Engine的Niagara和Unity的VFX Graph）已将粒子模拟计算迁移到GPU上，单帧可处理数百万个粒子。

粒子渲染在游戏视觉质量中占据重要位置，因为自然界中许多现象本质上就是离散微粒的集合行为。一个高品质的爆炸特效往往同时运行火核、碎片、烟雾、火花四个独立的粒子发射器，每个发射器使用不同的渲染类型和混合模式。

## 核心原理

### Billboard粒子

Billboard（广告牌）粒子是最常见、性能开销最低的粒子渲染类型。其核心原理是：每个粒子在三维空间中实际上只是一个由两个三角形构成的四边形面片（Quad），但该面片始终朝向摄像机，从而让二维纹理看起来具有立体感。这种"始终面向摄像机"的行为通过在顶点着色器中用摄像机的Right向量和Up向量替换面片的本地坐标轴来实现。

Billboard存在三种对齐模式：**Camera-Facing**（面片完全朝向摄像机位置）、**Velocity-Aligned**（面片沿粒子运动方向拉伸，常用于子弹轨迹）、**Fixed-Axis**（仅绕某一固定轴旋转，常用于草地和烟柱）。烟雾和火花特效几乎都使用Camera-Facing模式，而雨滴下落时则使用Velocity-Aligned以产生拉伸的线条感。

### Ribbon粒子（缎带粒子）

Ribbon粒子将同一发射器按时间顺序生成的粒子串联成一条连续的带状网格，用于渲染闪电、刀光、魔法拖尾等需要连续轨迹的特效。相邻两个粒子节点之间生成一个矩形面片，面片的UV坐标沿轨迹方向均匀展开，使纹理在整条缎带上连续流动。Ribbon的宽度由每个节点的"Width"属性控制，可以实现从粗到细的自然衰减效果。

Ribbon渲染的技术难点在于节点数量与精度的权衡：节点过少会导致转弯处出现明显折角，节点过多则增加顶点数量和GPU带宽。Unreal Engine的Niagara系统中，Ribbon渲染器专门提供了"Curve Tension"参数（默认值0.0到1.0之间）来控制节点间的贝塞尔插值平滑度。

### Mesh粒子

Mesh粒子不使用平面面片，而是以一个完整的三维网格体作为单个粒子的形状进行实例化渲染。一颗爆炸产生的碎石、散落的树叶、飞溅的水珠都适合使用Mesh粒子。其底层实现依赖**GPU Instancing**技术：同一个网格体的顶点数据只上传一次，通过实例化绘制调用（DrawInstanced）将几何体数据在不同位置、旋转、缩放下重复渲染，大幅减少Draw Call数量。

Mesh粒子可以接受光照计算，使碎片在不同光照环境下产生真实的明暗变化，这是Billboard粒子通常无法做到的。但代价是顶点数量远多于四边形面片，因此单帧支持的Mesh粒子数量通常比Billboard少一个数量级。

### GPU粒子模拟

GPU粒子将粒子的物理状态更新（位置积分、碰撞检测、速度衰减）从CPU转移到GPU的Compute Shader中执行。粒子状态（位置、速度、生命值等）存储在GPU端的**结构化缓冲区（StructuredBuffer）**中，每帧由Compute Shader并行更新所有粒子，完全绕过CPU-GPU数据传输瓶颈。

典型的GPU粒子更新公式为：
$$\vec{p}_{t+1} = \vec{p}_t + \vec{v}_t \cdot \Delta t + \frac{1}{2}\vec{a} \cdot \Delta t^2$$

其中 $\vec{p}$ 为粒子位置，$\vec{v}$ 为速度，$\vec{a}$ 为加速度（含重力），$\Delta t$ 为帧间隔时间。Unity VFX Graph中，每个Compute Shader线程组（Thread Group）默认处理64个粒子，对100万粒子发起约15625次线程组调度。

## 实际应用

**火焰特效**通常叠加三层Billboard粒子：最内层使用Additive加法混合的橙黄色纹理模拟火核，中间层使用半透明烟灰色粒子模拟烟雾，外层使用稀疏的Velocity-Aligned粒子模拟上升火星。三层混合后产生层次丰富的视觉效果。

**激光剑拖尾**是Ribbon粒子的经典应用场景：武器挥舞时在世界空间中每隔2-3毫秒记录一个节点，Ribbon渲染器将这些节点串联成发光带状轨迹，节点的Alpha值随粒子生命周期从1衰减到0，使轨迹末端自然消隐。

**粒子与深度缓冲的软粒子技术**解决了粒子面片与不透明几何体相交时产生的硬切边问题。通过采样场景深度纹理，计算粒子面片到最近不透明表面的距离，当距离小于某阈值（通常0.5到2.0个世界单位）时线性降低粒子透明度，使粒子自然融入场景边缘。

## 常见误区

**误区一：Billboard粒子一定不能有光照效果。** 实际上通过"法线贴图Billboard"技术，可以为面片存储一张法线纹理，使粒子在光照计算中产生立体感。Unreal Engine的Niagara支持在Billboard粒子上启用光照响应，常用于需要接受场景光照的雪花和魔法粒子特效。

**误区二：粒子数量越多特效越好。** 粒子渲染的性能瓶颈通常不在于粒子计算本身，而在于**过度绘制（Overdraw）**——半透明粒子叠加绘制时每个像素被片元着色器执行多次。屏幕中心一个1920×1080分辨率区域内叠加20层半透明粒子，意味着该区域超过2000万个像素操作，远比单纯增加粒子数量更消耗GPU带宽。

**误区三：Ribbon粒子和Trail（拖尾）是完全不同的系统。** 两者视觉效果相似，但Ribbon是粒子系统内的一种渲染模式，多条Ribbon可以从同一发射器并行生成；而传统的Trail组件通常附加在单个GameObject上，只能产生一条轨迹，且状态管理逻辑不同。

## 知识关联

粒子渲染建立在**渲染管线概述**的基础知识之上：Billboard粒子的摄像机朝向变换发生在顶点着色器阶段，半透明粒子的混合操作（Additive、Alpha Blend）发生在输出合并阶段，软粒子技术需要访问深度缓冲，这些都是渲染管线各阶段的直接应用。理解透明渲染排序问题（Painter's Algorithm与深度排序的局限性）有助于解释为何粒子特效在某些角度会出现错误的穿透表现。GPU粒子的Compute Shader机制与后续的GPU驱动渲染（GPU-Driven Rendering）架构思想一脉相承，是理解现代引擎高性能渲染策略的重要起点。