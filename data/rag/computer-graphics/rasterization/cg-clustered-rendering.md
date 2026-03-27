---
id: "cg-clustered-rendering"
concept: "簇式渲染"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 簇式渲染

## 概述

簇式渲染（Clustered Rendering）是一种将视锥体（Frustum）三维切分为数百至数千个子空间单元（称为"簇"，Cluster），并将光源预分配到每个簇中，从而在着色时仅对当前片元所在簇内的光源进行计算的技术。与Forward+将屏幕划分为二维Tile不同，簇式渲染在Z轴方向上也进行了细分，使得每个子单元在世界空间中呈现为一个轴对齐截锥体（Axis-Aligned Frustum Slice），这一特性使其能更精确地处理深度分布不均匀的场景。

该技术由Ola Olsson、Markus Billeter和Ulf Assarsson于2012年在论文《Clustered Deferred and Forward Shading》中正式提出，随后迅速被工业界采纳。其提出的直接动机是：Forward+在Z轴上不加区分，一个Tile内深度跨度极大时会引入大量错误的光源分配，而三维分簇可将每簇的光源数量从数十个压缩至个位数，显著降低着色开销。

簇式渲染因其支持透明物体、粒子、体积雾等无法在延迟渲染中高效处理的效果而备受青睐。《毁灭战士（DOOM 2016）》的id Software团队在GDC 2016上公开分享了其基于簇式渲染的Mega Texture与光照系统，证明该技术在主机平台每帧处理超过500个动态光源时仍可维持60fps性能目标。

## 核心原理

### 视锥体三维分簇策略

簇的划分方式直接影响光源分配质量。最常用的方案是在X、Y方向按屏幕像素均匀分块（如16×8个块），在Z方向按指数分布划分切片，切片的深度边界公式为：

$$z_k = z_{near} \cdot \left(\frac{z_{far}}{z_{near}}\right)^{k/K}$$

其中 $k$ 为切片索引，$K$ 为Z方向总切片数（典型值为24或32），$z_{near}$ 和 $z_{far}$ 为近远裁剪面距离。指数分布的原因在于透视投影中近处物体深度变化密集，线性分布会造成近处切片过厚而远处切片过薄，指数方案使每个切片在视角空间中占据大致相同的感知比例。

一个典型的簇配置为16×8×24，共3072个簇；高端实现可达32×16×32，即16384个簇，GPU内存占用约为 $3072 \times 4 \times 2 = 24\text{KB}$（每簇存储光源偏移量和计数各一个uint32）。

### 光源分配阶段

在CPU或GPU的Compute Shader中，对场景中每个光源（点光源、聚光灯）计算其包围体（球体或圆锥体）与簇截锥体的相交测试。点光源与簇的相交可简化为球体与轴对齐截锥体的相交判断：将球心变换到视角空间后，分别对近平面、远平面及四侧面执行有向距离测试，六个判断全部通过则标记该簇受此光源影响。

实现中通常维护两个全局Buffer：`LightIndexList`（存储所有簇引用的光源索引的扁平化列表）和`LightGrid`（每个簇对应一个起始偏移`offset`和光源数量`count`）。GPU上的Assign Lights Pass使用原子操作（`atomicAdd`）动态填充这两个Buffer，整个过程在约0.2ms内完成（1080p，512光源，GTX 1080 Ti参考数据）。

### 着色阶段查询

在Fragment Shader中，片元根据其屏幕坐标（x, y）和线性深度值 $z_{view}$ 计算所属簇的三维索引：

$$k = \left\lfloor \frac{\log(z_{view}/z_{near})}{\log(z_{far}/z_{near})} \cdot K \right\rfloor$$

通过该索引查询`LightGrid`，获取该簇的`offset`和`count`，仅循环遍历`count`个光源执行BRDF计算，无需遍历场景中全部光源。此查询全为整数运算，GPU执行开销约为2-3个ALU指令。

## 实际应用

**游戏引擎集成：** Unity的HDRP（High Definition Render Pipeline）从2018版本起以Clustered Forward为默认光照路径，默认配置为64×64像素Tile、32个Z切片，支持最多512个实时点光源和聚光灯同时渲染而不触发性能降级。

**体积效果渲染：** 由于簇本身是三维子空间，体积雾（Volumetric Fog）可直接在每个簇上积分散射方程，无需额外的三维Texture采样。Frostbite引擎（EA）在《战地1》中正是利用簇的三维结构将体积光照计算从O(n·像素数)降低为O(n·簇数)，性能提升约4倍。

**透明物体多pass处理：** 簇式渲染支持在Forward Pass中对透明几何体使用与不透明物体相同的LightGrid，避免了延迟渲染中透明物体需要单独Forward Pass且无法共享光源信息的问题，这在粒子系统数量庞大（如烟雾模拟中10万个粒子）的场景中尤为重要。

## 常见误区

**误区一：簇越多着色越快。** 增加簇数会提升光源分配精度，但`LightGrid`的显存占用与读取延迟也线性增长。当Z切片从24增加到64时，每个线程束（Warp）的LightGrid加载量增加2.7倍，可能导致L1 Cache命中率下降，实际渲染时间反而上升。最优簇粒度需根据场景光源密度和目标硬件的Cache大小经过Profile确定。

**误区二：簇式渲染完全替代了延迟渲染。** 两者适用场景不同：在超高面数（>1000万三角形）、大量Overdraw的场景中，延迟渲染的GBuffer机制仍可有效减少冗余着色，此时Clustered Deferred（先写GBuffer再用簇查询）比Clustered Forward更优。仅在MSAA需求强烈或透明物体占比超过30%的场景下，Clustered Forward才能体现出明显优势。

**误区三：光源分配只需在CPU执行。** CPU串行执行光源-簇相交测试时，512光源×3072簇的测试量约为157万次，耗时约3-5ms，占用宝贵的主线程时间。GPU Compute Shader实现可将同等工作量压缩至0.1-0.3ms，因此现代实现几乎均将Assign Lights Pass迁移至GPU执行。

## 知识关联

簇式渲染在Forward+的基础上引入了Z轴分层，解决了Forward+的Tile在深度方向上光源分配不精确的核心缺陷——这两个技术形成了直接的演进关系，簇式渲染的LightGrid结构可视为Forward+的TileBuffer在三维空间中的自然推广。理解Forward+中Tile的Cull与Assign机制（特别是Min-Max Depth压缩和AABB测试）是掌握簇式渲染相交判断逻辑的前提。

在延迟渲染体系中，簇式渲染既可作为独立的Forward路径（Clustered Forward），也可嵌入GBuffer之后的光照Pass（Clustered Deferred），两种组合方式的选择取决于MSAA需求和透明物体比例。掌握簇式渲染后，可进一步研究虚拟阴影贴图（Virtual Shadow Maps）在簇结构上的索引优化，以及光线追踪与簇式光源剔除的混合方案——这些都是当前实时渲染的前沿课题。