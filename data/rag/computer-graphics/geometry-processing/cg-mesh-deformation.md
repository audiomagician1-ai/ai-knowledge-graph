---
id: "cg-mesh-deformation"
concept: "网格变形"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.4
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

# 网格变形

## 概述

网格变形（Mesh Deformation）是指对三维多边形网格的顶点坐标进行有规律的重新分配，从而改变物体形状的几何处理技术。区别于拓扑修改（增删顶点或边），网格变形严格保持原有网格的连接关系（即半边结构或邻接矩阵），仅操作顶点位置向量 $\mathbf{v}_i \in \mathbb{R}^3$。

这一技术在1986年由 Thomas Sederberg 和 Scott Parry 以"自由变形（Free-Form Deformation，FFD）"的形式正式提出，发表于 SIGGRAPH 1986 论文 *Free-Form Deformation of Solid Geometric Models*。自此，网格变形分化出两大主流分支：基于空间函数的 FFD 方法和基于骨骼驱动的蒙皮绑定（Skinning）方法。前者适合雕塑式的整体形变，后者则是游戏角色动画的工业标准。

理解网格变形的关键在于明确**谁在控制变形**：FFD 使用控制点格子驱动空间映射，骨骼蒙皮使用关节层级驱动权重混合。这两种驱动机制决定了各自适用的动画场景和计算开销。

---

## 核心原理

### 自由变形（FFD）

FFD 在网格外部构建一个规则的三线性参数体（通常为 $l \times m \times n$ 的控制点格子，例如 $4 \times 4 \times 4 = 64$ 个控制点）。对于网格中的每个顶点 $\mathbf{v}$，首先计算其在参数体内的局部坐标 $(s, t, u) \in [0,1]^3$，然后用三变量 Bernstein 多项式求和得到变形后的位置：

$$
\mathbf{v}' = \sum_{i=0}^{l} \sum_{j=0}^{m} \sum_{k=0}^{n} \binom{l}{i}\binom{m}{j}\binom{n}{k} s^i(1-s)^{l-i} t^j(1-t)^{m-j} u^k(1-u)^{n-k} \mathbf{P}_{ijk}$$

其中 $\mathbf{P}_{ijk}$ 是控制点坐标。当用户拖动某个控制点时，所有局部坐标受其影响的顶点都会平滑移动，产生连续光滑的形变效果。FFD 的优点是对底层网格格式无依赖，缺点是控制点与直觉解剖结构无对应。

### 骨骼蒙皮绑定（Linear Blend Skinning）

线性混合蒙皮（LBS，又称"骨骼蒙皮"）是游戏引擎（如 Unity、Unreal Engine）的主流实时变形方案。每块骨骼 $j$ 定义一个刚体变换矩阵 $\mathbf{T}_j$（由旋转 $\mathbf{R}_j$ 和平移 $\mathbf{t}_j$ 构成），每个顶点 $\mathbf{v}_i$ 携带对各骨骼的权重 $w_{ij}$，满足 $\sum_j w_{ij} = 1$。变形公式为：

$$
\mathbf{v}_i' = \sum_{j} w_{ij} \mathbf{T}_j \mathbf{v}_i^{\text{rest}}$$

其中 $\mathbf{v}_i^{\text{rest}}$ 是绑定姿势（Bind Pose）下的原始坐标，$\mathbf{T}_j = \mathbf{M}_j \mathbf{B}_j^{-1}$，$\mathbf{B}_j$ 是骨骼 $j$ 在绑定姿势下的全局变换，$\mathbf{M}_j$ 是当前姿势下的全局变换。权重 $w_{ij}$ 由美术人员手动绘制或自动热扩散算法（Heat Diffusion Skinning）计算得到。

### 蒙皮糖果问题（Candy-Wrapper Artifact）

LBS 存在著名的"糖果扭曲"伪影：当关节旋转角度超过约 90° 时，肘部或腕部网格会异常塌陷，原因是对旋转矩阵做线性插值时行列式趋近于零，导致体积坍缩。解决方案包括：

- **双四元数蒙皮（Dual Quaternion Skinning，DQS）**：2007年由 Ladislav Kavan 等人提出，用对偶四元数表示刚体变换再做线性混合，能保持体积不变形。  
- **球面线性插值（SLERP）**：对旋转分量单独插值后再重组变换矩阵。

---

## 实际应用

**角色动画**：在《堡垒之夜》等游戏中，每个角色网格绑定约 50–150 根骨骼，每个顶点最多受 4 根骨骼影响（GPU 寄存器限制），运行时用 GPU 的顶点着色器并行计算 LBS，单帧可在不足 0.1 毫秒内完成万级顶点变形。

**面部捕捉（Blendshape/Morph Target）**：这是另一种网格变形形式，为目标表情单独存储一套顶点偏移量 $\Delta \mathbf{v}_i^k$，最终位置为 $\mathbf{v}_i + \sum_k \alpha_k \Delta \mathbf{v}_i^k$，混合权重 $\alpha_k \in [0,1]$ 由面部追踪数据驱动。皮克斯在制作《寻梦环游记》时，每个主角面部使用了超过 300 个 Blendshape 目标。

**医学可视化**：FFD 用于交互式解剖模拟，医生可以通过调整控制点格子来预览软组织的手术效果，常见控制点分辨率为 $8\times8\times8$，以在交互流畅性与形变精度间取得平衡。

---

## 常见误区

**误区一：认为权重越均匀变形越好**  
均匀权重（每骨骼权重相等）会使关节区域网格完全不受任何单根骨骼主导，反而导致整个肢体像橡皮泥一样整体拖动，失去骨骼驱动的硬度感。正确做法是在骨干中段使用单骨骼接近1.0的权重，仅在关节过渡区设置渐变混合。

**误区二：FFD 和骨骼蒙皮是竞争关系，只能选其一**  
两者可以叠加使用。典型的 VFX 流程是先用骨骼蒙皮驱动大范围姿势，再对局部区域（如肌肉隆起）叠加一层 FFD 修正，这种组合在 Maya 中通过"Lattice Deformer 作为次级变形器"实现。

**误区三：Blendshape 是一种独立于网格变形的技术**  
Blendshape 本质上是顶点位移的线性叠加，是网格变形的一个特例，只是驱动信号来自动画师定义的目标形状而非骨骼旋转或控制点移动。其核心计算仍然是对顶点坐标向量的加权求和。

---

## 知识关联

网格变形以**网格表示**为直接前提：必须理解顶点列表、面索引和半边数据结构，才能明白"变形"究竟修改了哪些数据（仅顶点坐标缓冲区，不触及索引缓冲区）。FFD 所使用的三线性参数体是 B 样条体（B-spline Volume）的均匀特例，若要进一步研究非均匀控制，需掌握 NURBS 和 T-Spline 的参数化理论。骨骼蒙皮依赖正向运动学（FK）和逆向运动学（IK）提供关节变换矩阵，其中骨骼层级的矩阵链乘（Local→World 空间变换）是理解 $\mathbf{T}_j = \mathbf{M}_j \mathbf{B}_j^{-1}$ 中两个矩阵之差的必要背景。在几何处理的更高阶方向，网格变形延伸至微分坐标变形（Laplacian Deformation）和基于物理的弹性模拟（FEM 有限元法），这些方法将顶点位移与拉普拉斯算子或弹性势能挂钩，能处理体积保持和碰撞响应等更复杂的约束。