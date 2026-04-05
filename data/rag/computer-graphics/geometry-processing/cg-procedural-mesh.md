---
id: "cg-procedural-mesh"
concept: "程序化网格"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 99.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 程序化网格

## 概述

程序化网格（Procedural Mesh）是指在程序运行时通过算法动态生成或修改三角网格数据的技术体系。与预先由美术人员在 DCC 工具（如 Blender、Maya）中制作的静态网格不同，程序化网格的顶点位置、法线、UV 坐标和三角索引均由代码在 CPU 或 GPU 上实时计算产生。这使得同一套逻辑能够以极少的存储代价生成参数各异的无数种形体，而无需手工制作每一个变体。

程序化网格的思想可追溯至 1980 年代的分形地形生成算法。Ken Musgrave 在 1988 年的博士研究中系统化了基于分形布朗运动（fBm）噪声函数的地形网格生成方法，奠定了这一技术分支的理论基础（Musgrave et al., 1989，《Texturing and Modeling: A Procedural Approach》，Morgan Kaufmann）。进入游戏引擎时代后，《我的世界》（Minecraft，2011 年正式发布）将程序化体素网格的实时生成推向大众；虚幻引擎 5.2 的 PCG（Procedural Content Generation）框架（2023 年正式发布）则将其提升至可视化节点编程层面，支持亿级实例的散布与网格合并，标志着该技术进入工业化普及阶段。

程序化网格的核心价值在于**参数驱动的多样性**与**运行时适应性**。游戏中的无限地形、建筑物立面的窗户排列、道路沿曲线的自动放样，以及角色衣物随物理模拟而产生的实时形变，都依赖程序化网格技术。掌握这项技术意味着能以 $O(1)$ 存储复杂度的算法替代 $O(n)$ 规模的美术资产库。

---

## 核心原理

### 网格数据结构的运行时构造

程序化网格在内存中由两张并行数组构成：**顶点缓冲区**（Vertex Buffer）存储每个顶点的位置 `vec3`、法线 `vec3`、切线 `vec4` 和 UV 坐标 `vec2`；**索引缓冲区**（Index Buffer）存储以三角形为单位的无符号整数三元组，指明哪三个顶点构成一个面。

形式化表示：

$$
M = (V, \, I), \quad V = \{v_0, v_1, \ldots, v_n\}, \quad I = \{(i_0,i_1,i_2),\, (i_3,i_4,i_5),\, \ldots\}
$$

其中每个 $v_k = (\mathbf{p}_k,\, \mathbf{n}_k,\, \mathbf{uv}_k) \in \mathbb{R}^3 \times \mathbb{R}^3 \times \mathbb{R}^2$，每组索引三元组定义一个顺时针（或逆时针）朝向的三角面。

以 Unity 的 `Mesh` API 为例，生成一个正方形平面的最小实现如下：

```csharp
Mesh mesh = new Mesh();
// 4 个顶点，仅需 6 个索引复用（而非 6 个独立顶点）
mesh.vertices = new Vector3[] {
    new Vector3(0,0,0), new Vector3(1,0,0),
    new Vector3(0,0,1), new Vector3(1,0,1)
};
mesh.triangles = new int[] { 0,2,1, 2,3,1 };  // 两个三角形
mesh.uv = new Vector2[] {
    new Vector2(0,0), new Vector2(1,0),
    new Vector2(0,1), new Vector2(1,1)
};
mesh.RecalculateNormals();  // 自动计算顶点法线
```

索引复用（Indexed Drawing）是程序化网格节省显存的关键机制：一个顶点可被多个三角形共享，一个 4 顶点正方形只需 6 个索引，而非 6 个独立顶点，节省 33% 的顶点数据。

### 参数化形状生成算法

最基础的程序化网格是**参数化圆柱体**，其侧面顶点位置由以下公式确定：

$$
x = r \cdot \cos\!\left(\frac{2\pi \cdot i}{\text{segments}}\right), \quad
y = \frac{h \cdot j}{\text{stacks}}, \quad
z = r \cdot \sin\!\left(\frac{2\pi \cdot i}{\text{segments}}\right)
$$

其中 $r$ 为半径，$h$ 为高度，$i \in [0, \text{segments})$，$j \in [0, \text{stacks}]$。改变 `segments` 与 `stacks` 两个整数参数，即可在运行时生成从 4 棱柱到高精度圆管的任意细分级别。该方案的顶点数为 $(\text{segments}+1) \times (\text{stacks}+1)$，三角形数为 $2 \times \text{segments} \times \text{stacks}$，时间与空间复杂度完全可预测。

### 样条放样与截面扫掠

更高阶的程序化生成涉及**样条放样（Spline Extrusion）**：沿 Bezier 曲线或 Catmull-Rom 样条采样 $N$ 个截面位置，将二维轮廓多边形沿曲线法平面逐段放样并缝合，生成管道、道路或河床等连续体。

曲线上第 $t$ 个采样点处的局部坐标系由 Frenet-Serret 标架给出：

$$
\mathbf{T}(t) = \frac{\mathbf{C}'(t)}{|\mathbf{C}'(t)|}, \quad
\mathbf{N}(t) = \frac{\mathbf{T}'(t)}{|\mathbf{T}'(t)|}, \quad
\mathbf{B}(t) = \mathbf{T}(t) \times \mathbf{N}(t)
$$

其中 $\mathbf{T}$、$\mathbf{N}$、$\mathbf{B}$ 分别为切向量、主法向量和副法向量。截面多边形的每个顶点 $\mathbf{q}_k$ 经变换 $\mathbf{p}_k = \mathbf{C}(t) + q_x \mathbf{N}(t) + q_y \mathbf{B}(t)$ 映射到世界空间。相邻截面之间缝合四边形（拆分为 2 个三角形），总三角形数为 $2 \times (N-1) \times M$（$M$ 为截面顶点数）。

> **例如**：Unity Asset Store 上广泛使用的 Curvy Splines 插件（2013 年首发）正是基于此原理，在运行时以 60fps 实时更新道路网格，支持截面顶点数 $M$ 从 4 到 64 的动态调整。

---

## 关键公式与算法

### Marching Cubes 等值面提取

当程序化网格需要表达隐式体（如 SDF 符号距离场或体素密度场）时，最经典的算法是 **Marching Cubes**（Lorensen & Cline, 1987，*SIGGRAPH '87 Proceedings*）。算法将三维标量场划分为边长为 $d$ 的立方体网格，对每个立方体的 8 个角点采样密度值 $f(x,y,z)$，依据 8 位二进制编码（$2^8 = 256$ 种拓扑情形，化简后为 15 种基本构型）从预置查找表中取出三角形模板，再通过线性插值确定三角形顶点在棱边上的精确位置：

$$
\mathbf{p} = \mathbf{v}_A + \frac{(iso - f_A)}{(f_B - f_A)}(\mathbf{v}_B - \mathbf{v}_A)
$$

其中 $iso$ 为等值面阈值，$f_A$、$f_B$ 分别为棱边两端的标量值，$\mathbf{v}_A$、$\mathbf{v}_B$ 为端点位置。《我的世界》的地形系统并未使用 Marching Cubes（其体素采用 Greedy Meshing 合并同色方块面），但 No Man's Sky（2016）的星球地形则大量依赖变体版 Marching Cubes 实现平滑洞穴与山脉。

### Geometry Shader 与 GPU 端生成

当顶点数超过百万量级时，CPU 端逐顶点计算成为瓶颈。GPU 端的解决方案有两类：
1. **Geometry Shader**（DirectX 10，2006 年引入）：可在 GPU 上将一个输入图元扩展为最多 1024 个输出顶点，适合草地、毛发等高密度重复几何体的就地生成。
2. **Compute Shader + DrawIndirect**（DirectX 11，2009 年引入）：在 Compute Shader 中填充顶点缓冲区，再通过 `DrawIndirectArgs` 将绘制参数完全保留在 GPU 侧，避免 CPU–GPU 数据回读，适合实时地形曲面细分（Tessellation）场景。

---

## 实际应用

### 无限地形生成

开放世界游戏（如《荒野大镖客：救赎 2》）将地图划分为若干 **Chunk**（通常 16×16 米或 32×32 米），以玩家位置为中心按视距动态加载或卸载 Chunk 网格。每个 Chunk 的高度图由多层 Perlin 噪声叠加生成：

$$
h(x,z) = \sum_{k=0}^{K-1} A_k \cdot \text{noise}(2^k \cdot x / \lambda,\; 2^k \cdot z / \lambda)
$$

其中 $A_k = A_0 \cdot g^k$（$g \approx 0.5$ 为增益系数），$\lambda$ 为基础频率波长，$K$ 通常取 6~8 层。最终网格的顶点 $y$ 分量即为 $h(x,z)$，UV 坐标按 $\lambda$ 归一化后用于纹理贴图。

### 建筑立面程序化

建筑可视化领域使用**形状文法（Shape Grammar）**（Müller et al., 2006，*ACM SIGGRAPH 2006*）驱动程序化网格：先将建筑体量拆分为楼层高度切片（Split Y），再将每个楼层按窗户模数切分为若干单元（Split X），最后对每个单元插入预置的窗框、阳台或墙面子网格并合并为最终 Mesh。CityEngine 软件（Esri）正是基于此方法，能够从一条规则脚本自动生成整个街区的建筑网格。

### 角色服装物理形变

角色布料模拟的每帧输出是一组经物理求解器（如 NVIDIA PhysX 的 PBD 解算器，Position Based Dynamics）更新后的新顶点位置。这些顶点直接写回 `Mesh.vertices`（Unity）或通过 Skinned Mesh 的 Delta Morph 目标叠加，实现每帧最高 30,000 个顶点的实时重新提交，而无需重建索引缓冲区。

---

## 常见误区

### 误区一：忘记在顶点共享边界处焊接法线

程序化生成网格时，初学者常对每个三角形独立分配顶点（即"爆炸网格"），导致每条棱边拥有两组位置相同但法线不同的顶点。渲染结果是所有面片之间出现硬边（Hard Edge），圆柱体看起来像多面棱柱。正确做法是对共享棱上的顶点使用相同索引，并在全部三角形提交后调用 `RecalculateNormals()` 或手动按面积加权平均各相邻面法线：

$$
\mathbf{n}_v = \text{normalize}\!\left(\sum_{f \ni v} \text{Area}(f) \cdot \mathbf{n}_f\right)
$$

### 误区二：每帧重新创建 Mesh 对象

在 Unity 中，若每帧执行 `new Mesh()` 然后赋值，会触发 GC 分配并导致显存反复申请释放。正确的做法是在 `Start()` 中创建一次 `Mesh` 对象，随后每帧仅更新 `mesh.vertices`（或使用 `mesh.SetVertices(List<Vector3>)` 避免数组装箱）并调用 `mesh.MarkDynamic()` 通知驱动该缓冲区会频繁修改，底层会将其分配至 `DYNAMIC_DRAW` 显存区域，减少 PCIe 带宽占用约 20%~40%（依硬件而异）。

### 误区三：混淆世界空间法线与切线空间法线

程序化网格提交的