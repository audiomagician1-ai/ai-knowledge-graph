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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

Voronoi碎裂是一种基于Voronoi图（泰森多边形）数学结构驱动的程序化物体破碎算法，通过在三维空间中散布种子点（Site Points），将物体体积划分为若干个凸多面体碎块，每个碎块由距离该种子点最近的所有空间点构成。这种方法由乔治·沃罗诺伊（Georgy Voronoy）于1908年提出的二维平面分割概念延伸至三维实体破碎领域，现已成为Houdini、Cinema 4D、Blender等主流特效软件内置的标准破碎方案。

与传统的手动拆分模型相比，Voronoi碎裂最大的价值在于**程序化可控性**：通过调整种子点的数量、分布密度和随机种子（Random Seed）值，美工人员可以在不手动建模的情况下生成数十乃至数千块碎片，并能在不同镜头需求之间快速迭代。

## 核心原理

### Voronoi图的几何构造

算法的数学基础是欧几里得距离（Euclidean Distance）度量下的空间分割。给定 $n$ 个种子点 $P = \{p_1, p_2, \ldots, p_n\}$，每个Voronoi单元格 $V(p_i)$ 定义为：

$$V(p_i) = \{ x \in \mathbb{R}^3 \mid d(x, p_i) \leq d(x, p_j), \forall j \neq i \}$$

两相邻单元格之间的交界面称为**Voronoi平面（Voronoi Plane）**，其几何形状始终是平面而非曲面，这就是为什么Voronoi碎裂产生的断面都是平整多边形而非有机曲面——这一特性与玻璃、混凝土等脆性材料的实际断裂形态高度吻合。

### 种子点分布策略

种子点的分布方式直接决定碎片的视觉风格：

- **均匀随机分布（Uniform Random）**：碎片大小相近，适合模拟质地均匀的陶瓷或冰块
- **泊松圆盘采样（Poisson Disk Sampling）**：保证相邻种子点之间的最小间距，避免出现过小的碎片，在Houdini中通过`scatter` SOP配合最小点距参数实现
- **密度纹理驱动（Density Map）**：将贴图的灰度值映射为种子点密度，在高灰度区域生成更多密集碎片，用于模拟局部撞击点附向外扩散的碎片密度梯度，比如子弹穿孔处碎片细密、边缘碎片粗大的效果

### 内部结构与碎片属性

每个Voronoi碎块在生成后都是一个独立的封闭凸多面体网格。破碎算法需要对原始几何体执行**体积布尔运算**，将每个Voronoi单元格与输入网格取交集，因此输入网格必须为封闭实体（Solid Mesh），否则会出现内部面缺失的穿帮问题。

碎块数量 $n$ 与种子点数量之间呈1:1关系，但在实际制作中，种子点数量超过约500个时，Houdini的`Voronoi Fracture` SOP的计算时间会从秒级跳升至分钟级，通常需要结合细节层次（LOD）策略分区处理。

## 实际应用

**爆炸与冲击波碎裂**：在建筑物爆破镜头中，常将建筑按楼层分区，每区独立运行Voronoi碎裂，底部楼层使用密集种子点（每区约200-400个）模拟爆炸中心的粉碎效果，顶部楼层使用稀疏种子点（每区约20-50个）模拟大块崩落，两者合并后驱动刚体动力学模拟。

**玻璃破碎**：Voronoi碎裂特别适合平面玻璃，结合"内部材质"（Interior Detail）贴图工作流，可以为每块碎片的断面赋予独立的玻璃截面着色器，呈现折射和磨砂边缘。Houdini的`Voronoi Fracture`节点提供了`Inside Group`和`Outside Group`输出，分别对应断面多边形和原始表面多边形，精确区分两类材质区域。

**地形地面开裂**：将种子点限制在一个薄层切片内，可以生成类似干旱土地龟裂纹路的二维碎裂图案，用于地面沉降或魔法阵开裂等特效。

## 常见误区

**误区一：种子点越多，碎片越真实**

增加种子点数量会使碎片趋于均匀的多面体形状，反而显得人工痕迹明显。真实的脆性材料碎裂遵循材料内部缺陷分布，碎片大小差异悬殊。正确做法是使用非均匀密度贴图控制种子点分布，或叠加两层不同密度的Voronoi碎裂（粗碎+细碎）来模拟多级破碎。

**误区二：Voronoi碎裂可以直接用于所有材质**

Voronoi碎块的断面全部是平面多边形，这对混凝土和玻璃是优点，但对木材、橡胶等纤维性或韧性材料则完全失真——木材破裂会产生沿纤维方向延伸的锯齿状断面，此时需要结合噪波置换（Noise Displacement）对Voronoi断面进行二次变形，或改用专门的各向异性碎裂算法。

**误区三：碎裂节点输出即可直接模拟**

Voronoi碎裂输出的几何体通常存在共享顶点（Shared Vertices）问题，相邻碎片在断面处顶点坐标完全重合。若不进行**分离（Separate Pieces）**处理，刚体模拟引擎会将所有碎片识别为同一连接体而无法分离。在Houdini中必须执行`Assemble` SOP并启用`Pack Geometry`选项，确保每个碎片获得独立的`name`属性后再送入Bullet或RBD求解器。

## 知识关联

**前置概念——破碎系统概述**：理解破碎系统概述中的刚体约束（Constraints）机制是使用Voronoi碎裂的必要基础，因为碎裂只生成几何体，真正控制"何时断开"的是约束网络中每条约束边的强度阈值参数（`Strength`）。

**后续概念——预碎裂工作流（Pre-Fracture Workflow）**：Voronoi碎裂是预碎裂工作流的核心几何生成步骤。预碎裂工作流进一步解决了Voronoi碎裂在动态模拟中的性能问题——通过离线烘焙碎片缓存（Alembic/USD），避免在每帧实时执行体积布尔运算，使百万面数碎片场景进入可实时预览的制作管线。