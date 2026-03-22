---
id: "cg-mesh-representation"
concept: "网格表示"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 2
is_milestone: false
tags: ["核心", "网格", "数据结构"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Botsch et al., Polygon Mesh Processing, AK Peters 2010"
  - type: "documentation"
    name: "OpenMesh / CGAL / libigl documentation"
scorer_version: "scorer-v2.0"
---
# 网格表示

## 定义与核心概念

网格表示（Mesh Representation）是用离散的多边形面片逼近连续曲面的数据结构，是计算机图形学、CAD/CAM 和物理仿真的基础数据格式。Botsch 等人在《Polygon Mesh Processing》中将其形式化为一个元组 **M = (V, E, F)**：
- **V** = {v₁, v₂, ..., vₙ}：顶点集合（3D坐标）
- **E** = {e₁, e₂, ..., eₘ}：边集合（顶点对）
- **F** = {f₁, f₂, ..., fₖ}：面集合（有序顶点环）

一个典型游戏角色模型约 **10K-100K** 个三角面片；电影级模型可达 **10M+**（如皮克斯角色平均 4M quad面）。

## 基础表示方法

### 1. 面片表列（Face-Vertex List / Indexed Face Set）

最简单最通用的格式：

```
Vertices:  V = [(x₀,y₀,z₀), (x₁,y₁,z₁), ...]
Faces:     F = [(0,1,2), (1,3,2), ...]   // 顶点索引

OBJ文件示例（一个四面体）：
v  0.0  0.0  0.0
v  1.0  0.0  0.0
v  0.5  1.0  0.0
v  0.5  0.5  1.0
f  1 2 3
f  1 2 4
f  2 3 4
f  1 3 4
```

| 属性 | 值 |
|------|---|
| 内存 | O(V + F)，每顶点 12B + 每面 12B（三角） |
| 邻接查询 | O(F) 遍历 —— **无拓扑信息** |
| 适用 | 渲染、传输（GPU直接消费） |
| 缺陷 | 无法高效回答"顶点v的相邻面是什么？" |

### 2. 半边数据结构（Half-Edge / DCEL）

学术界和高级几何处理的标准数据结构（OpenMesh 的核心）：

```
struct HalfEdge {
    Vertex*   target;        // 指向终点
    HalfEdge* opposite;      // 对边（反向半边）
    HalfEdge* next;          // 同一面上的下一条半边
    Face*     face;          // 所属面
};

struct Vertex {
    Point3D   position;
    HalfEdge* outgoing;      // 任一条出发半边
};

struct Face {
    HalfEdge* halfedge;      // 面上任一条半边
};
```

**邻接查询的时间复杂度**：

| 查询 | 半边结构 | 面片表列 |
|------|---------|---------|
| 顶点的所有相邻面 | O(度数) | O(F) |
| 面的三个邻接面 | O(1) | O(F) |
| 边的两个邻接面 | O(1) | O(F) |
| 顶点的1-ring邻域 | O(度数) | O(F) |
| 是否为流形 | 构建时检查 | 额外遍历 |

**代价**：每条边需 2 个半边，内存约为面片表列的 **3-4 倍**。

### 3. 角表（Corner Table）

Rossignac 提出的紧凑拓扑结构，特别适合三角网格：

```
对于三角网格：每面3个角（corner），角c属于面c/3
Corner Table:  O[c] = 对角的corner索引
               V[c] = 顶点索引

邻接操作（常数时间）：
next(c) = 3(c/3) + (c+1)%3    // 同面下一角
prev(c) = 3(c/3) + (c+2)%3    // 同面上一角
opposite(c) = O[c]             // 对面对角
```

内存：每个三角仅需 **1 个整数（opposite index）** 额外存储，极其紧凑。

### 4. 对比总结

| 数据结构 | 内存/三角 | 邻接查询 | 非流形支持 | 典型用途 |
|---------|----------|---------|-----------|---------|
| Face-Vertex | ~24 B | O(F) | 是 | GPU渲染、OBJ/STL文件 |
| Half-Edge | ~96 B | O(1)-O(度) | 否（仅流形） | 几何处理（细分、简化） |
| Corner Table | ~28 B | O(1) | 否 | 紧凑三角网格处理 |
| Winged-Edge | ~120 B | O(1) | 否 | 历史（1974年Baumgart） |

## Euler-Poincaré 公式与流形验证

对于闭合2-流形（genus g）：

```
V - E + F = 2(1 - g)

球面（g=0）：V - E + F = 2
环面（g=1）：V - E + F = 0
双环面（g=2）：V - E + F = -2

三角网格的推论：E = 3F/2, V ≈ F/2
→ 每个顶点平均度数 ≈ 6
```

验证网格是否为有效2-流形的检查清单：
1. 每条边恰好被 2 个面共享（非流形边 → 边被 >2 面共享）
2. 每个顶点的 1-ring 形成单一扇形（非流形顶点 → 多扇形）
3. 面法线方向一致（可定向性）

## 网格文件格式

| 格式 | 拓扑 | 属性 | 大小（1M三角） | 主要用途 |
|------|------|------|--------------|---------|
| OBJ | Face-vertex | UV、法线、材质 | ~70 MB（文本） | 交换格式 |
| STL | 独立三角 | 无（冗余顶点） | ~80 MB | 3D打印 |
| PLY | Face-vertex | 任意属性 | ~30 MB（二进制） | 点云/扫描 |
| glTF/GLB | Face-vertex | PBR材质、动画 | ~15 MB（压缩） | Web/实时 |
| FBX | 半边等效 | 骨骼、变形 | ~40 MB | 游戏/DCC |
| USD | 分层 | 场景图 | 可变 | 电影/Omniverse |

## LOD 与网格简化

实时渲染中，根据摄像机距离切换不同精度的网格（Level of Detail）：

| LOD级别 | 三角数比例 | 距离阈值（典型） | 算法 |
|---------|----------|----------------|------|
| LOD0 | 100% | < 10m | 原始 |
| LOD1 | 50% | 10-30m | QEM（Garland & Heckbert, 1997） |
| LOD2 | 25% | 30-80m | QEM + 法线保护 |
| LOD3 | 10% | > 80m | Aggressive decimation |

**QEM（Quadric Error Metrics）**：
```
每个顶点维护一个 4×4 误差矩阵 Q
边折叠代价 = v̄ᵀ(Q₁+Q₂)v̄
其中 v̄ 是最优收缩点位置
贪心选择代价最小的边进行折叠
```

UE5 的 Nanite 系统使用基于 DAG 的动态 LOD，实现了**无需手动 LOD 设置**的百亿三角场景渲染。

## 参考文献

- Botsch, M. et al. (2010). *Polygon Mesh Processing*. AK Peters/CRC Press. ISBN 978-1568814261
- Garland, M. & Heckbert, P. (1997). "Surface Simplification Using Quadric Error Metrics," *ACM SIGGRAPH* Proceedings, 209-216.
- Rossignac, J. (2001). "3D Compression Made Simple: Edgebreaker with Zip and Wrap on a Corner-Table," *IEEE Trans. Visualization and Computer Graphics*.

## 教学路径

**前置知识**：线性代数基础（向量、矩阵）、基本数据结构（数组、链表）
**学习建议**：先用 OBJ 格式手写一个简单的立方体并用 MeshLab 可视化，再实现 Face-Vertex 的邻接查询（体会其低效），然后实现半边数据结构。推荐使用 libigl（C++）或 Open3D（Python）进行实践。
**进阶方向**：细分曲面（Catmull-Clark / Loop）、参数化（UV展开）、网格修复（自相交/非流形检测）。
