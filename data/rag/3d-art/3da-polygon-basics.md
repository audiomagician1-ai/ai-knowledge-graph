---
id: "3da-polygon-basics"
concept: "多边形基础"
domain: "3d-art"
subdomain: "modeling-fundamentals"
subdomain_name: "建模基础"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 85.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "reference"
    citation: "Murdock, K. L. (2021). 3ds Max 2022 Bible. Wiley."
  - type: "reference"
    citation: "Blain, J. M. (2019). The Complete Guide to Blender Graphics: Computer Modeling & Animation (5th ed.). CRC Press."
  - type: "reference"
    citation: "Shirley, P., & Marschner, S. (2009). Fundamentals of Computer Graphics (3rd ed.). A K Peters/CRC Press."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 多边形基础

## 概述

多边形基础（Polygon Fundamentals）是三维建模中描述几何形体的最基本单元体系，由顶点（Vertex）、边（Edge）、面（Face/Polygon）三类元素共同构成一张可渲染的网格（Mesh）。这三类元素之间存在严格的拓扑依存关系：没有独立存在的边，每条边必须连接两个顶点；没有独立存在的面，每个面必须由至少三条边围合而成。

多边形网格建模的历史可追溯至1960年代波音公司的计算机辅助设计实验，Ivan Sutherland于1963年在其博士论文《Sketchpad: A Man-Machine Graphical Communication System》中首次系统性地描述了交互式计算机图形的几何表示方法，奠定了多边形建模的理论基础。真正的工业级普及是在1980年代随着Silicon Graphics Inc.（SGI）工作站的推广而实现的。早期3D游戏引擎（如John Carmack于1996年开发的Quake引擎）严格限制每个模型只能使用三角面（Triangle），因为三角形是唯一能保证所有顶点共面的最简多边形，GPU硬件光栅化管线至今仍以三角形为最小渲染单位。现代GPU每秒可处理数十亿个三角形，例如NVIDIA GeForce RTX 4090的理论三角形吞吐量约为每秒1820亿个。

理解多边形基础对于3D美术从业者至关重要，因为几乎所有主流软件（Maya、Blender、3ds Max、ZBrush）的建模操作本质上都是对顶点、边、面的增删与移动。一个包含错误拓扑的网格会直接导致动画蒙皮变形失败、烘焙法线贴图出现撕裂、以及游戏引擎中的渲染穿帮。（Blain, 2019）

---

## 核心原理

### 三元素的精确定义

**顶点（Vertex）** 是三维空间中的一个坐标点，至少包含三个分量：X、Y、Z位置坐标。在实际的网格数据结构中，顶点还可以附带法线方向、UV贴图坐标、顶点色（RGBA）等属性数据。在Blender的内部数据格式（BMesh结构）中，每个顶点仅存储位置信息，而法线等属性存储在面的"角（Loop）"层级上，这一设计使得同一顶点在不同相邻面上可以携带不同的法线值，从而支持硬边（Hard Edge）效果。

**边（Edge）** 是连接两个顶点的线段，是网格拓扑的骨架。边在拓扑学上有三种状态：
- **边界边（Boundary Edge）**：仅被一个面使用，存在于网格的开口处，例如角色模型颈部截面的一圈边。
- **流形边（Manifold Edge）**：被恰好两个面共享，是合法封闭网格的标准状态，是布尔运算和UV展开的前提条件。
- **非流形边（Non-Manifold Edge）**：被三个或以上的面共享，会导致布尔运算、展UV等操作出错，在Blender中可通过 `Mesh → Clean Up → Select Non-Manifold` 快速定位。

**面（Face/Polygon）** 是由三条或以上边围合形成的封闭平面区域，根据顶点数量分为：三角面（Tri，3个顶点）、四边面（Quad，4个顶点）、N-Gon（5个及以上顶点）。三者在细分行为、动画形变以及渲染管线中的处理方式各有本质区别。

### 欧拉公式与网格有效性

判断一个封闭多面体网格是否合法，依赖欧拉-庞加莱公式（Euler-Poincaré Formula），由莱昂哈德·欧拉于1758年首先对凸多面体给出证明，亨利·庞加莱于19世纪末将其推广至任意亏格曲面：

$$V - E + F = 2(1 - G)$$

其中：
- $V$ = 顶点数（Vertices）
- $E$ = 边数（Edges）
- $F$ = 面数（Faces）
- $G$ = 网格的亏格（Genus），即拓扑学意义上的"把手"数量：球体 $G=0$，圆环（甜甜圈形）$G=1$，双孔曲面 $G=2$

**例如**，验证一个标准立方体：$V=8$，$E=12$，$F=6$，代入公式：

$$8 - 12 + 6 = 2 \quad (G=0)$$

结果为2，符合无孔封闭曲面的标准。再验证一个圆环体（Torus）：若细分为4×4的格子，则 $V=16$，$E=32$，$F=16$，代入公式：$16 - 32 + 16 = 0 = 2(1-1)$，符合 $G=1$ 的单孔曲面。当计算结果不满足该公式时，通常意味着网格存在非流形几何或孤立顶点（Shirley & Marschner, 2009）。

### 面法线的数学定义

面法线（Face Normal）由面上两条非共线边向量的叉积计算得出。对于一个三角面，三个顶点按逆时针顺序排列为 $V_1$、$V_2$、$V_3$，其法线 $\mathbf{N}$ 的计算公式为：

$$\mathbf{N} = (V_2 - V_1) \times (V_3 - V_1)$$

顶点顺序（Winding Order）决定叉积方向，进而决定面的"正面"朝向。OpenGL默认以逆时针顺序为正面，DirectX默认以顺时针顺序为正面，这一差异是跨引擎移植时产生背面剔除错误的常见根源。

### 四边面与三角面的本质差异

四边面（Quad）在建模中被广泛偏爱，原因在于它的边排列方式天然形成可预测的**边循环（Edge Loop）**和**边环（Edge Ring）**结构。边循环是一组首尾相连、穿越四边面中心的边序列；边环则是一组共享同一组平行边的四边面序列。这两种结构在角色关节处（如嘴角、眼眶、手腕）能够在骨骼驱动时产生自然的拉伸形变，因为蒙皮权重（Skinning Weight）沿边循环方向平滑过渡。

而三角面会在关节区域产生不可预测的折痕，因此行业规范要求：角色模型的骨骼影响区域必须使用全四边面网格，三角面仅允许出现在不参与形变的静态区域（如头盔后脑、鞋底）。

N-Gon（五边形及以上）在使用细分曲面（Subdivision Surface）算法——如Pixar于1978年提出、Edwin Catmull与Jim Clark共同发明的Catmull-Clark算法——时会产生额外的拓扑奇点（Extraordinary Point），导致细分后的曲面出现不均匀的凸起或压痕，因此高模制作规范通常要求在细分前将所有N-Gon转换为四边面或三角面。

---

## 关键公式与数据模型

### 面数与细分的关系

在Catmull-Clark细分算法中，每执行一次细分操作，面数增长规律为：

$$F_n = F_0 \times 4^n$$

其中 $F_0$ 为初始面数，$n$ 为细分级别。

**例如**，一个初始面数为 $F_0 = 6$（标准立方体六个面）的模型：
- 1级细分：$6 \times 4^1 = 24$ 面
- 2级细分：$6 \times 4^2 = 96$ 面
- 3级细分：$6 \times 4^3 = 384$ 面
- 6级细分：$6 \times 4^6 = 24{,}576$ 面

ZBrush雕刻的高精度模型在6级细分时可轻松达到数百万面，这正是ZBrush为何需要专用的DynaMesh和ZRemesher算法来管理超高密度网格的原因。

### 渲染顶点数的计算

GPU渲染管线实际处理的"渲染顶点（Render Vertex）"数量不等于几何顶点数，其估算公式为：

$$V_{render} \approx V_{geo} + \sum_{seam} UV_{breaks} + \sum_{edge} Normal_{breaks}$$

即几何顶点数加上所有UV缝合点数量、再加上所有法线硬边导致的顶点拆分数。一个立方体在几何层面有 $V_{geo} = 8$ 个顶点，但由于每个面的法线方向不同，在渲染层面会被展开为 $V_{render} = 24$ 个渲染顶点（每个顶点在6个面上各自存储一份法线数据）。因此，几何顶点数只是建模阶段的参考，实际性能评估需要看引擎导入后的三角面数与渲染顶点数（Murdock, 2021）。

---

## 实际应用

### 低多边形游戏模型制作

次时代游戏中一个标准的人形角色模型面数通常在5,000至15,000个三角面之间（手游端可能低至1,500三角面，主机端AAA游戏角色可达60,000三角面以上）。**例如**，《原神》PC端主角模型约8,000三角面，而《赛博朋克2077》主角V的面数接近80,000三角面。在有限的面数预算下，建模师需要精确分配多边形密度：面部表情区域（眼睛周围、嘴唇）分配约20%的面数，而平坦的躯干背部可能仅用4个四边面（即8个三角面）表示。

### Blender中的基础操作验证

在Blender 3.x及4.x版本中，选中一个默认立方体后按 `Tab` 进入编辑模式，状态栏会显示 "Verts: 8 | Edges: 12 | Faces: 6"，与欧拉公式完全对应。使用 `Alt + 左键` 点击任意边可以选中整条边循环，直观验证四边面拓扑的规律性。按 `Ctrl + R` 执行循环切割（Loop Cut）时，只有四边面网格才能产生连续的切割线，三角面和N-Gon会打断循环，这直观说明了为何业界坚持使用四边面布线。

### ZBrush高模与低模的Retopology工作流

ZBrush雕刻的高精度模型包含数百万个多边形，这些高模最终需要通过Retopology（重拓扑）工序，重新用手动布线的低面数四边面网格替代，以适应动画和实时渲染需求。**案例**：在角色面部重拓扑时，建模师需要在眼眶周围规划同心圆形边循环（通常5至7条），在嘴角规划放射状边循环，这两组边循环在面部动画中分别控制眼睛眨合与嘴唇张合的形变质量。Maya的Quad Draw工具和Blender的RetopoFlow插件是完成这一工序的主流工具。

### 硬表面建模中的倒角控制

硬表面建模（Hard Surface Modeling）中，倒角（Bevel）操作将单条锐利边替换为由2至5条边组成