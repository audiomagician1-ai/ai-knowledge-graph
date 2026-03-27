---
id: "cg-subdivision"
concept: "细分曲面"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 3
is_milestone: false
tags: ["算法"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 细分曲面

## 概述

细分曲面（Subdivision Surface）是一种通过反复对多边形网格执行局部细化规则，从而在极限情况下逼近光滑曲面的几何表示方法。与NURBS曲面不同，细分曲面可以处理任意拓扑结构的网格，包括带有亏格（genus）的封闭曲面和具有奇异顶点（valence ≠ 4的顶点）的网格，这使其成为三维建模与动画中处理复杂有机形状的首选工具。

细分曲面的理论基础由Edwin Catmull与Jim Clark于1978年共同提出，当年发表于SIGGRAPH会议论文《Recursively generated B-spline surfaces on arbitrary topological meshes》。与此同时，Charles Loop在1987年的硕士论文中提出了专门针对三角网格的Loop细分方案。这两种方案至今仍是工业界和学术界使用最广泛的细分算法。

细分曲面在实际生产中意义重大：皮克斯动画公司自1997年《精灵鼠小弟》起全面采用Catmull-Clark细分曲面替代NURBS建模角色皮肤，大幅简化了复杂有机体的建模流程。OpenSubdiv（由皮克斯开源）和Blender的Subdivision Surface修改器均实现了GPU加速的实时细分，支持现代影视级渲染管线。

---

## 核心原理

### Catmull-Clark细分规则

Catmull-Clark细分作用于四边形为主的多边形网格，每次细分将每个多边形面分裂，使面数变为原来的4倍。具体分三步计算新顶点坐标：

**面点（Face Point）**：每个面的面点 $F$ 为该面所有顶点坐标的算术平均值：
$$F = \frac{1}{n}\sum_{i=1}^{n} v_i$$
其中 $n$ 为该面的顶点数。

**边点（Edge Point）**：每条内部边的边点 $E$ 由边的两个端点与相邻两个面的面点共同决定：
$$E = \frac{v_1 + v_2 + F_1 + F_2}{4}$$
边界边的边点直接取两端点的中点。

**顶点点（Vertex Point）**：原网格中度为 $n$ 的普通顶点（valence = $n$）更新为：
$$V' = \frac{Q}{n} + \frac{2R}{n} + \frac{(n-3)V}{n}$$
其中 $Q$ 是相邻面的面点均值，$R$ 是相邻边中点的均值，$V$ 是原顶点坐标。当顶点度 $n=4$ 时，该规则退化为均匀双三次B样条曲面的细分规则，极限面即双三次B样条曲面。

### Loop细分规则

Loop细分专门作用于三角网格，每次细分将每个三角形分裂为4个小三角形。

**偶数顶点（新插入的边点）**：对内部边上新插入的顶点，其坐标由四个邻近顶点加权决定：
$$E_{new} = \frac{3}{8}(v_1 + v_2) + \frac{1}{8}(v_3 + v_4)$$
其中 $v_1, v_2$ 是该边的两端点，$v_3, v_4$ 是两侧三角形的对顶点。权重 $3/8$ 和 $1/8$ 源自Loop对四次箱样条（quartic box spline）的推导。

**奇数顶点（原始顶点的更新）**：度为 $n$ 的内部顶点更新权重为：
$$\beta = \frac{1}{n}\left(\frac{5}{8} - \left(\frac{3}{8} + \frac{1}{4}\cos\frac{2\pi}{n}\right)^2\right)$$
更新后顶点坐标为 $(1-n\beta)V + \beta\sum_i v_i$，其中求和遍历所有直接邻接顶点。Loop细分的极限面在普通点处是 $C^2$ 连续的，但在奇异顶点（$n \ne 6$）处仅保证 $C^1$ 连续。

### 奇异顶点与极限面的连续性

两种细分方案都存在**奇异顶点**（extraordinary vertex）问题：对于Catmull-Clark，度不等于4的顶点是奇异顶点；对于Loop，度不等于6的顶点是奇异顶点。在奇异顶点处，细分方案仅能保证 $C^1$（切平面连续），无法达到普通点处的 $C^2$ 连续。极限曲面的位置可通过细分矩阵的主特征向量计算，而切平面方向则由次特征向量的线性组合给出——这一结论由Halstead等人在1993年通过特征分析严格证明。

---

## 实际应用

**影视角色建模**：在DCC软件（如Autodesk Maya、Blender、ZBrush）中，艺术家用少量面的"控制网格"定义角色的粗略形状，渲染时由细分曲面自动生成高分辨率平滑几何体。皮克斯《寻梦环游记》中人物皮肤使用Catmull-Clark细分，控制网格面数约5000面，最终渲染时细分至约30万面。

**游戏引擎的自适应细分**：DirectX 11和Vulkan的Tessellation着色器阶段可实现屏幕空间自适应细分：距摄像机近的区域细分级别高，远处级别低，通过连续LOD避免了传统离散LOD的突变问题。Hardware Tessellation通常以Phong Tessellation或PN三角形近似Catmull-Clark结果。

**CAD/CAM与T样条的竞争**：航空航天和汽车设计中，细分曲面与T样条（T-Spline）竞争，前者拓扑灵活，后者可精确满足G2连续要求。Autodesk Fusion 360采用T样条，而许多影视管线坚持使用Catmull-Clark因其工具链更成熟。

---

## 常见误区

**误区1：细分层数越多越好**
细分层数增加使面数以4的幂次增长（Catmull-Clark每次细分后面数 × 4），第5级细分即可从1000面控制网格生成超过100万面的几何体。实际应用中，3级细分通常已足够满足特写镜头需求，盲目增加层数会导致内存和渲染时间急剧上升而可见改善极小——这是边际收益递减的直接体现。

**误区2：细分曲面就是对顶点坐标插值**
Catmull-Clark和Loop细分都是**近似**细分而非插值细分——极限曲面不一定过原始控制网格的顶点。如需曲面精确通过给定顶点（如角色面部关键点），需使用插值细分方案（如Butterfly细分）或对控制顶点施加"逆细分"预处理（即求解线性方程 $MV' = V_{target}$）。

**误区3：边界处理方式唯一**
实际实现中，Catmull-Clark对边界顶点的处理方式有多种约定（"Sharp"、"Crease"权重、折痕规则等），OpenSubdiv明确区分了`boundaryInterpolation`的三种模式：`none`、`edgeOnly`和`edgeAndCorner`，不同模式会产生明显不同的边界形状，建模时若不加以区分会导致模型在不同软件间出现不一致的渲染结果。

---

## 知识关联

学习细分曲面需要扎实掌握**网格表示**（Mesh Representation）基础：半边数据结构（Half-Edge Structure）是实现细分规则的标准数据结构，因为细分规则需要高效查询"顶点的邻接面与邻接边"，半边结构的这些操作均为 $O(1)$ 时间复杂度；而简单的顶点-面表（Vertex-Face List）则需要 $O(n)$ 遍历。

细分曲面与**样条曲线/曲面**（B-Spline、NURBS）有深刻的理论联系：在规则四边形网格（所有顶点度=4）上，Catmull-Clark的极限面精确等价于双三次均匀B样条曲面；在规则三角网格（所有顶点度=6）上，Loop细分的极限面等价于四次箱样条曲面。这一对应关系使得细分曲面可视为"可以处理任意拓扑的广义样条曲面"。

在更高级的几何处理方向，细分曲面连接到**多分辨率分析**（Multiresolution Analysis）：将细分矩阵进行小波分解，可得到几何信号的多尺度表示，支持压缩、去噪和细节叠加（Displacement Mapping）等操作，这是计算机动画中"形变传递"和"皮肤权重编辑"技术的几何学基础。