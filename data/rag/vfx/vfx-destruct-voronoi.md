---
id: "vfx-destruct-voronoi"
concept: "Voronoi碎裂"
domain: "vfx"
subdomain: "destruction"
subdomain_name: "破碎与销毁"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Voronoi碎裂

## 概述

Voronoi碎裂是一种基于Voronoi图数学结构的程序化碎裂算法，通过在三维空间中散布种子点（Site Points），将物体分割成若干多面体碎片，每个碎片对应Voronoi图中的一个胞元（Cell）。其数学基础来源于1908年乔治·沃罗诺伊（Georgy Voronoy）发表的空间划分理论：对于平面或空间中的任意点集 $S = \{p_1, p_2, \ldots, p_n\}$，每个胞元 $V(p_i)$ 定义为所有距 $p_i$ 比距其他任意种子点更近的空间点的集合，即 $V(p_i) = \{x \mid d(x, p_i) \leq d(x, p_j), \forall j \neq i\}$。这一划分产生的碎片自然呈现出凸多面体形态，非常符合硬质脆性材料（如混凝土、陶瓷、岩石）断裂后的真实碎片形状。

在特效行业中，Voronoi碎裂从2000年代中期开始在Houdini等DCC软件中获得广泛应用。Houdini的Voronoi Fracture SOP节点和RBD（Rigid Body Dynamics）系统紧密配合，使得程序化生成数百乃至数千块碎片并进行物理模拟成为标准流程。与手动切割或预制碎片库不同，Voronoi碎裂允许特效师通过控制种子点的分布、数量和权重，完全以参数化方式定义碎裂结果，可随时修改而无需重建几何体。

Voronoi碎裂在电影爆破、建筑倒塌、武器命中等场景中不可替代，因为它能在毫秒级时间内生成拓扑闭合（Watertight）的碎片几何体，每块碎片都有独立的外表面和内表面，内表面可单独指定材质（如混凝土断面纹理），使得碎裂效果既物理合理又视觉真实。

## 核心原理

### 种子点分布与碎片密度控制

种子点的空间分布直接决定最终碎片的大小和形态分布。均匀随机撒点（Uniform Random）会产生大小相近的碎片，适合均质材料；泊松盘采样（Poisson Disk Sampling）则保证任意两个种子点之间距离不小于设定阈值 $r$，生成的碎片更规整、避免出现极小碎片。在Houdini中，使用`scatter`节点以几何体表面积或体积密度作为权重，可以在曲率大的区域（如碰撞冲击点附近）集中更多种子点，从而模拟应力集中导致的局部细碎效果，而远离冲击点的区域碎片较大，符合裂缝传播的物理规律。

典型的电影级破碎场景（如建筑爆破）通常需要500至3000个Voronoi胞元，而近景道具破碎（如咖啡杯）只需20至80个胞元。种子点数量过少会导致碎片过大、缺乏细节；过多则会显著增加刚体模拟的计算成本，并可能产生几何退化（Degenerate Geometry）问题。

### 内表面生成与切割噪波

Voronoi碎裂的每次切割都生成两个匹配的多边形面——切割平面的两侧各一个，分属相邻碎片。这些新生成的面构成碎片的"内表面"（Interior Surface），在材质分配上与物体的原始外表面（Exterior Surface）独立处理。原始外表面保留原始UV和法线，内表面则需要额外展UV以贴合混凝土截面、木材纹理等断裂材质。

为了让切割平面不那么规则（真实断裂面绝非完美平面），Voronoi碎裂通常结合噪波位移（Noise Displacement）对切割边界施加扰动。Houdini的Voronoi Fracture节点提供`interior_noise`参数组，通过在切割点上叠加Perlin噪波或Voronoi噪波（后者产生更尖锐的断面形态），幅值通常设置在物体尺寸的1%至5%范围内，过大会导致相邻碎片几何体穿插（Interpenetration），破坏碎片的封闭性。

### 凸包约束与局限性

标准Voronoi碎裂生成的每个胞元都是**凸多面体（Convex Polyhedron）**，这是由Voronoi图的数学性质决定的——胞元是有限个半空间（Half-Space）的交集，交集必然为凸集。这一特性对刚体模拟极为有利，因为凸体碰撞检测算法（如GJK算法）的时间复杂度远低于凹体，使得数千块碎片的实时模拟成为可能。

然而，凸包约束也带来明显局限：复杂形状物体（如L形构件、中空管道）内部会出现**Ghost Surface**——切割平面延伸到物体外部区域，生成不应存在的内表面片段。解决方案是先将源几何体分解为多个凸壳（Convex Hull Decomposition），对每个子凸体独立应用Voronoi碎裂，再合并结果。Houdini 19.0之后的版本在Voronoi Fracture SOP中集成了自动凸分解预处理步骤，有效减少了Ghost Surface的出现概率。

## 实际应用

**混凝土墙体爆破**：在《速度与激情》系列的建筑破坏特效中，Voronoi碎裂被用于生成建筑立面的程序化碎片。特效师将冲击点处的种子点密度设置为背景区域的8至12倍，配合粒子系统驱动碎片飞溅方向，配合Houdini的Constraint Network限制碎片初始粘连，仅在模拟冲击力超过设定阈值时断开约束，实现分阶段碎裂效果。

**地面裂缝生成**：Voronoi图不仅用于三维体碎裂，也广泛用于地面龟裂纹路的程序化生成。通过在二维平面上生成Voronoi图，其胞元边界即为裂缝走向，配合法线贴图烘焙，可快速生成干旱土地或古老陶瓷釉面的龟裂图案，种子点数量在200至600之间时视觉效果最自然。

**武器命中玻璃**：玻璃碎裂需要呈现以冲击点为中心的放射状裂纹。技术实现上，以命中点为中心用径向权重分布种子点——靠近命中点的种子点间距约为0.5厘米，边缘区域扩展至5厘米，Voronoi胞元自然形成由密到疏的梯度分布，与真实玻璃同心裂纹（Hertzian Cone）模式高度吻合。

## 常见误区

**误区一：碎片数量越多效果越好**。实际上，Voronoi碎裂的视觉质量并不与胞元数量线性正相关。当碎片数超过场景摄影机视野中可分辨的极限（通常在镜头距离5米处约为300块），增加碎片数只会提升模拟计算量，而不产生视觉差异。经验法则是：近景特写使用50至150块，中景使用300至800块，远景超过1000块时应考虑使用LOD（Level of Detail）替换方案。

**误区二：Voronoi碎裂可以直接模拟所有材质**。Voronoi碎裂产生凸多面体碎片，适合硬质脆性材料；木材沿木纹方向的各向异性断裂、金属的韧性撕裂变形均无法由标准Voronoi碎裂直接再现。模拟木材断裂时，应将种子点分布限制在垂直于木纹方向上形成薄片状胞元，并结合形变模拟（Deformation Simulation）才能近似木材劈裂效果。

**误区三：Voronoi碎裂会自动产生正确的裂缝传播顺序**。Voronoi图是静态空间划分，算法本身不包含时序信息。碎片"从冲击点向外依次破碎"的动态效果完全来自Houdini RBD中的Constraint Network设置——只有当冲击波传播模型（通常用SOP Solver逐帧扩展激活半径）与碎片约束断开逻辑配合，才能实现真实的渐进式碎裂动画。

## 知识关联

Voronoi碎裂建立在**破碎系统概述**所介绍的程序化碎裂基本概念之上，了解刚体碎裂的几何要求（封闭网格、独立碎片索引）是正确使用Voronoi Fracture SOP的前提。Voronoi图的凸胞元特性与RBD求解器的碰撞代理（Collision Proxy）机制直接对接，每个Voronoi碎片可直接用其凸包作为物理代理而无需简化，节省了手动设置碰撞体的工作量。

掌握Voronoi碎裂后，下一步是学习**预碎裂工作流**——即在模拟前将Voronoi碎片烘焙为静态几何体并与约束网络预设配合的制作流程。预碎裂工作流的核心问题是如何将程序化的Voronoi