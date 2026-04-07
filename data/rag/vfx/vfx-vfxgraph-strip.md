---
id: "vfx-vfxgraph-strip"
concept: "Strip粒子"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Strip粒子

## 概述

Strip粒子（条带粒子）是VFX Graph中一种特殊的粒子输出类型，其核心机制是将同一粒子系统中按时间顺序发射的粒子连接成连续的多边形条带网格，而不是渲染独立的四边形面片。每个Strip由一系列顶点按发射顺序串联而成，Unity在GPU端实时计算相邻粒子之间的连接关系，生成拉伸的四边形带状几何体。

Strip粒子的概念源自游戏引擎对"轨迹渲染"的长期需求。早期引擎依赖Trail Renderer组件在CPU端逐帧记录对象位置来模拟拖尾，而VFX Graph从Unity 2018.3版本引入Strip输出后，将这一计算完全迁移至GPU，支持同时运行数万条独立Strip而不造成显著的CPU开销。

Strip粒子的核心价值在于它能够精确表达"具有历史路径的运动体"，包括闪电、刀光、飞弹轨迹、烟雾卷须等效果。与普通粒子系统在粒子死亡后立即消失不同，Strip保留了粒子从诞生到消亡的整段空间路径，使视觉效果具有时间连续性。

## 核心原理

### Strip的数据结构与容量

VFX Graph中每条Strip在内存中以一段连续的粒子数组形式存储，数组索引顺序即为Strip的顶点顺序。在VFX Asset属性中需要设置`Strip Capacity`（条带容量）和`Max Strip Count`（最大条带数量）两个关键参数。Strip Capacity决定单条Strip最多能包含多少个粒子节点，超过容量后新粒子会复用最旧的位置。举例来说，若将Strip Capacity设为32，则每条Strip最多由32个四边形片段首尾相接构成，形成31段连续的几何体。

### 顶点展开与UV计算

在输出阶段，Strip中每个粒子节点会展开为两个顶点（左右各一），两顶点沿粒子的`tangent`（切线方向）向两侧偏移，偏移距离由粒子的`size`属性决定。沿Strip长度方向的UV坐标默认通过`Strip Progress`属性计算，取值范围为0到1，代表该节点在Strip中的相对位置（0为Strip头部，1为尾部）。开发者可利用此属性配合渐变纹理实现头部透明、尾部显现的经典刀光效果，公式为：`Alpha = Gradient.Sample(stripProgress)`。

### 粒子属性在Strip中的特殊行为

在Strip模式下，`Particle Attribute`（粒子属性）分为两类：**逐粒子属性**（Per-Particle）和**逐Strip属性**（Per-Strip）。颜色、大小、旋转等属性属于逐粒子属性，每个节点独立存储，可随时间插值变化。而初始发射位置、Strip ID等属于逐Strip属性，由该条Strip的第一个粒子决定，后续粒子共享。在`Initialize Strip`上下文中设置的属性会作用于整条Strip的初始状态，而`Update Particle`上下文中对每帧每个节点的修改则产生逐节点的形状变化。

### 与噪声函数的结合

Strip粒子的形态控制高度依赖噪声函数。在`Update Particle`上下文中，对每个节点的位置叠加Curl Noise或Perlin Noise位移，会使整条Strip呈现有机弯曲的形态，而非僵硬直线。关键参数是噪声的`Field Transform`中的`Frequency`（频率），较低频率（如0.1~0.3）产生平滑弯曲的卷须状，较高频率（如2.0以上）则产生破碎闪烁的电弧感。由于噪声计算在GPU端进行，即使同时运行10,000条Strip，帧率损耗也远低于CPU端等效计算。

## 实际应用

**刀光与武器轨迹**：在角色攻击动画中，可将Strip Capacity设为16，将Strip的生命周期（`lifetime`）设置为约0.15秒，每帧在武器骨骼位置发射新粒子节点，配合`Strip Progress`驱动不透明度渐变纹理，使轨迹头部清晰、尾部快速消散。

**闪电效果**：单条Strip从起点到终点发射约20~30个粒子，在`Update Particle`中对每个节点施加高频Curl Noise（Frequency ≈ 3.0，Intensity ≈ 0.5米），使条带在空间中剧烈扭曲。在`Output Strip Quad`中使用发光（Emissive）材质，并在每帧随机重置节点噪声偏移的seed值，即可模拟闪电颤抖的视觉效果。

**烟雾飘带**：将单条Strip的粒子数量设为64，生命周期设为3~5秒，在Update阶段叠加低频噪声（Frequency ≈ 0.05）以及向上的Drag力，配合按`Age over Lifetime`渐变的透明度，可生成随风飘动的香烟烟雾拖尾。

## 常见误区

**误区一：将Strip Capacity设得过大导致内存浪费**。许多开发者在不了解Strip内存机制的情况下，将Strip Capacity设为128甚至256。实际上，VFX Graph会按照`Max Strip Count × Strip Capacity`预分配GPU显存，若有1000条Strip且容量为256，则预分配256,000个粒子的存储空间。大多数轨迹效果使用16~32的容量已足够，过大的容量会造成数倍的显存开销。

**误区二：在Initialize Particle而非Initialize Strip中设置Strip级属性**。Strip的起始位置、颜色等若在`Initialize Particle`中设置，则仅对第一个粒子节点生效，后续节点会使用默认值导致条带出现错误的跳变。需明确区分：控制整条Strip特征的属性必须放在`Initialize Strip`上下文中，控制单个节点随时间变化的属性才放在`Initialize Particle`和`Update Particle`中。

**误区三：混淆Strip Progress与粒子Age**。`Strip Progress`描述的是粒子在整条Strip中的空间位置（0到1），与时间无关；而`Age over Lifetime`描述的是单个粒子节点自身的生命进度。用`Age over Lifetime`来控制Strip尾部渐隐会导致整条Strip同步淡出，而非从尾到头的渐进消失效果，正确做法是用`Strip Progress`驱动不透明度曲线。

## 知识关联

Strip粒子的形态控制直接依赖**噪声函数**：Curl Noise的散度特性使Strip节点位移在空间上保持连续性而不产生断裂，这是普通Perlin Noise难以替代的。理解噪声的Frequency、Octave参数含义，是调出自然感Strip轨迹的必要前提。

Strip粒子的静态烘焙版本可通过**Point Cache**系统实现。当需要在场景中放置预先录制好的Strip轨迹路径（如固定的魔法阵纹路），可将Strip的粒子位置序列烘焙为Point Cache资产，供其他VFX Graph系统读取重放，从而将动态Strip转化为可复用的静态数据资源。