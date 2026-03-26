---
id: "cg-parametric-surface"
concept: "参数曲面"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 3
is_milestone: false
tags: ["数学"]

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


# 参数曲面

## 概述

参数曲面是三维空间中通过两个独立参数 $(u, v)$ 定义的曲面，其数学表达式为向量值函数 $\mathbf{S}(u, v): \mathbb{R}^2 \rightarrow \mathbb{R}^3$，将参数域（通常是 $[0,1] \times [0,1]$ 的矩形区域）映射到三维空间中的曲面点。与隐式曲面（用 $F(x,y,z)=0$ 定义）不同，参数曲面可以直接生成曲面上的点坐标，这使得它在图形学中的渲染和采样极为便捷。

参数曲面理论的发展与汽车工业密切相关。1962年，雷诺公司工程师皮埃尔·贝塞尔（Pierre Bézier）开发了以他命名的贝塞尔曲面，用于设计汽车车身曲面；几乎同时，保罗·德卡斯特利奥（Paul de Casteljau）在雪铁龙公司独立推导了同一算法。此后，B样条曲面和NURBS（非均匀有理B样条）曲面相继成为CAD/CAM领域和电影特效行业的核心建模工具，至今NURBS仍是Maya、Rhino等工业软件的标准曲面表示格式。

参数曲面在几何处理中的重要性体现在其精确描述自由曲面的能力上。一个NURBS曲面可以精确表达球面、圆柱面等二次曲面，而Bézier曲面只能近似表达，这一区别直接影响了工业设计中的公差计算。此外，参数曲面天然提供了曲面的微分几何量（法向量、主曲率），这是网格曲面难以高精度计算的。

---

## 核心原理

### Bézier曲面：张量积构造

Bézier曲面由 $(m+1) \times (n+1)$ 个控制点 $\mathbf{P}_{ij}$ 通过张量积方式构造：

$$\mathbf{S}(u,v) = \sum_{i=0}^{m} \sum_{j=0}^{n} B_i^m(u) \cdot B_j^n(v) \cdot \mathbf{P}_{ij}$$

其中 $B_i^m(u) = \binom{m}{i} u^i (1-u)^{m-i}$ 是 $m$ 次伯恩斯坦基函数。最常用的是**双三次Bézier曲面**（$m=n=3$），需要 $4 \times 4 = 16$ 个控制点，能描述绝大多数工业外形。Bézier曲面具有**凸包性**（曲面完全在控制点的凸包内）和**端点插值性**（角点 $\mathbf{S}(0,0)=\mathbf{P}_{00}$），但**不具备局部修改性**，改动一个控制点会影响整张曲面。

### B样条曲面与节点向量

为克服Bézier曲面缺乏局部控制的缺陷，B样条曲面引入了**节点向量**（Knot Vector）：

$$\mathbf{S}(u,v) = \sum_{i=0}^{m} \sum_{j=0}^{n} N_{i,p}(u) \cdot N_{j,q}(v) \cdot \mathbf{P}_{ij}$$

其中 $N_{i,p}(u)$ 是由节点向量 $U = \{u_0, u_1, \ldots, u_{m+p+1}\}$ 通过Cox-de Boor递推公式定义的 $p$ 次B样条基函数。**局部支撑性**是其关键性质：每个 $N_{i,p}(u)$ 仅在 $[u_i, u_{i+p+1})$ 区间非零，因此修改控制点 $\mathbf{P}_{ij}$ 只影响其邻域内的曲面形状，这对交互式建模至关重要。$p=3$（三次）的B样条曲面在工业中最为常见，在 $C^2$ 连续性与计算效率间取得最佳平衡。

### NURBS曲面：有理扩展与精确二次曲面

NURBS（Non-Uniform Rational B-Spline）在B样条基础上为每个控制点引入**权重** $w_{ij} > 0$：

$$\mathbf{S}(u,v) = \frac{\sum_{i=0}^{m} \sum_{j=0}^{n} N_{i,p}(u) N_{j,q}(v) w_{ij} \mathbf{P}_{ij}}{\sum_{i=0}^{m} \sum_{j=0}^{n} N_{i,p}(u) N_{j,q}(v) w_{ij}}$$

NURBS的核心优势在于**精确表达二次曲面**：一个标准球面可用3×9个NURBS控制点精确表示（不是近似），而任何多项式参数曲面（包括Bézier和B样条）都无法做到这一点。当所有权重相等时，NURBS退化为普通B样条曲面。权重值增大会将曲面"拉向"对应控制点，权重趋向无穷时曲面将通过该控制点。

### 曲面微分几何量的计算

给定参数曲面 $\mathbf{S}(u,v)$，其**单位法向量**为：
$$\hat{\mathbf{n}} = \frac{\mathbf{S}_u \times \mathbf{S}_v}{|\mathbf{S}_u \times \mathbf{S}_v|}$$
其中 $\mathbf{S}_u = \partial\mathbf{S}/\partial u$，$\mathbf{S}_v = \partial\mathbf{S}/\partial v$ 是两个切向量。第一基本形式 $I = E\,du^2 + 2F\,du\,dv + G\,dv^2$（$E=\mathbf{S}_u\cdot\mathbf{S}_u$，$F=\mathbf{S}_u\cdot\mathbf{S}_v$，$G=\mathbf{S}_v\cdot\mathbf{S}_v$）用于计算曲面上的弧长和面积，是曲面细分和纹理映射等操作的数学基础。

---

## 实际应用

**汽车车身建模**：主流汽车厂商使用CATIA软件中的NURBS曲面设计车身。A级曲面（Class-A Surface）要求曲面之间保持 $G^2$（曲率）连续，而不仅是 $C^1$（切线）连续，这通过调整相邻NURBS片之间的控制点行方向和间距来实现。

**游戏引擎中的Bézier曲面**：早期PlayStation 2游戏引擎支持硬件级别的**细分曲面**（Subdivision Surfaces），而DirectX 11引入了Tessellation阶段，允许GPU将双三次Bézier曲面片实时细分为三角网格。调用时通过设置Tessellation Factor（1到64之间的整数）控制细分密度，距摄像机近的区域使用更高因子，实现**LOD（细节层次）**效果。

**电影特效中的NURBS动画**：Pixar早期电影（如1986年的《棋逢对手》）使用B样条曲面建模，通过动画化控制点的位置实现角色形变。现代特效流程中，布料仿真结果（三角网格）有时需要反向拟合为NURBS曲面，以满足后期工序的精度要求，这一过程称为**曲面重建**（Surface Reconstruction）。

---

## 常见误区

**误区一：认为NURBS曲面"更精确"是因为控制点更多**。实际上NURBS的精确性来源于**有理函数**（分子分母均为多项式之比），而不是控制点数量。用 $p=2$ 次、9个控制点的NURBS圆弧精确表达半圆，与控制点数量无关，关键是每个控制点的权重值（半圆的中间控制点权重为 $w = \cos(45°) = \frac{\sqrt{2}}{2} \approx 0.707$）。

**误区二：以为 $u$ 和 $v$ 方向可以任意互换**。Bézier/B样条曲面的参数化是**有方向性**的：$u$ 方向用 $p$ 次基函数，$v$ 方向用 $q$ 次基函数，两者可以不同。此外，节点向量的非均匀性会导致曲面在 $u$ 和 $v$ 方向的参数速度不均匀，在计算等参线（Isoparametric Curves，即固定 $u$ 或 $v$ 为常数所得曲线）时必须考虑弧长重参数化。

**误区三：将Bézier曲面片的 $G^1$ 拼接条件简化为"相邻法向量相同"**。准确条件是：在公共边界处，两侧曲面的偏导数 $\mathbf{S}_u^{(1)}$ 和 $\mathbf{S}_u^{(2)}$ 以及公共切向量 $\mathbf{S}_v$ 满足 $\mathbf{S}_u^{(1)} = \alpha \mathbf{S}_u^{(2)} + \beta \mathbf{S}_v$（$\alpha > 0$）。仅对齐控制点使法向量一致是 $C^1$ 连续的充分条件，而 $G^1$ 允许参数速度不同，条件更宽松。

---

## 知识关联

从**几何处理概述**的基础出发，参数曲面引入了从离散（点云、网格）