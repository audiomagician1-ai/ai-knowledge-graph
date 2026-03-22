---
id: "graph-theory-basics"
concept: "图论基础"
domain: "mathematics"
subdomain: "discrete-math"
subdomain_name: "离散数学"
difficulty: 2
is_milestone: false
tags: ["图论", "基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Diestel, Graph Theory, 5th ed., Springer GTM 173"
  - type: "textbook"
    name: "Cormen et al., Introduction to Algorithms (CLRS), 4th ed."
scorer_version: "scorer-v2.0"
---
# 图论基础

## 定义与历史

图论（Graph Theory）研究由**顶点**（Vertices）和**边**（Edges）组成的关系结构。形式化定义：图 G = (V, E)，其中 V 是顶点集，E ⊆ V×V 是边集。

图论诞生于 Euler（1736）对柯尼斯堡七桥问题的证明：不可能恰好经过每座桥一次遍历所有四块陆地。Euler 的关键洞察——将陆地抽象为顶点、桥抽象为边——开创了拓扑学和组合数学的先河。

Diestel（2017）在《Graph Theory》中指出："如果组合数学有一个统一主题，那就是图。"（5th ed., GTM 173, Preface）

## 基本概念

### 图的分类

| 类型 | 定义 | 例 |
|------|------|---|
| 无向图 | 边无方向：(u,v) = (v,u) | 社交网络 |
| 有向图（Digraph） | 边有方向：(u,v) ≠ (v,u) | 网页链接 |
| 加权图 | 边附带权重 w(e) | 地图导航 |
| 简单图 | 无自环、无重边 | 大多数理论研究 |
| 多重图 | 允许重边 | 交通网络 |
| 完全图 K_n | 每对顶点间都有边 | |E| = n(n-1)/2 |
| 二部图 | V可分为两组，边只在组间 | 匹配问题 |

### 度与握手定理

顶点 v 的度 deg(v) = 与 v 相连的边数。

**握手定理**（Euler, 1736）：
```
Σ deg(v) = 2|E|   [对所有 v ∈ V]

推论1：奇数度顶点的个数必为偶数
推论2：平均度 = 2|E|/|V|
```

有向图中区分入度 deg⁻(v) 和出度 deg⁺(v)：
```
Σ deg⁺(v) = Σ deg⁻(v) = |E|
```

## 图的表示

### 邻接矩阵

```
n×n 矩阵 A，A[i][j] = 1 当 (i,j) ∈ E
         
空间：O(n²)
边查询：O(1)
遍历邻居：O(n)
适用：稠密图（|E| ≈ n²）
```

### 邻接表

```
每个顶点维护一个邻居列表

空间：O(n + m)，m = |E|
边查询：O(deg(v))
遍历邻居：O(deg(v))
适用：稀疏图（|E| << n²）
```

CLRS（4th ed.）建议：当 |E| < |V|²/64 时优选邻接表，否则优选邻接矩阵。

## 核心问题与算法

### 1. 图遍历

| 算法 | 数据结构 | 时间复杂度 | 应用 |
|------|---------|-----------|------|
| BFS（广度优先） | 队列 | O(V+E) | 最短路径（无权）、层序遍历 |
| DFS（深度优先） | 栈/递归 | O(V+E) | 连通分量、拓扑排序、环检测 |

```python
# BFS 模板
from collections import deque
def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for neighbor in graph[v]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

### 2. 最短路径

| 算法 | 约束 | 复杂度 | 思想 |
|------|------|--------|------|
| Dijkstra | 非负权 | O((V+E)log V) | 贪心 + 优先队列 |
| Bellman-Ford | 允许负权 | O(VE) | 动态规划（松弛V-1轮） |
| Floyd-Warshall | 全源最短路 | O(V³) | DP: d[i][j] = min(d[i][j], d[i][k]+d[k][j]) |

### 3. 连通性

- **无向图连通分量**：一次 DFS/BFS → O(V+E)
- **有向图强连通分量**：Tarjan 算法或 Kosaraju 算法 → O(V+E)

### 4. 最小生成树

| 算法 | 策略 | 复杂度 |
|------|------|--------|
| Kruskal | 按权排序 + Union-Find | O(E log E) |
| Prim | 类 Dijkstra 贪心扩展 | O((V+E)log V) |

**Cut property**（最小生成树的理论基础）：对图的任意割，穿越割的最小权边必属于某棵 MST。

## 特殊图与经典定理

### Euler 路径与回路

- **Euler 回路**存在 ⟺ 图连通且所有顶点度数为偶数
- **Euler 路径**存在 ⟺ 图连通且恰好 0 或 2 个奇度顶点

### Hamilton 回路

经过每个**顶点**恰好一次的回路。判定是 **NP-完全问题**（Karp, 1972）。
- Dirac 定理（1952）：若 n ≥ 3 且每个顶点 deg(v) ≥ n/2，则存在 Hamilton 回路

### 图着色

**四色定理**（Appel & Haken, 1976）：任何平面图可用 4 种颜色着色使相邻顶点不同色。这是首个借助计算机辅助完成的重大数学证明。

色数 χ(G) 的基本界：
```
ω(G) ≤ χ(G) ≤ Δ(G) + 1

ω(G) = 最大团大小
Δ(G) = 最大度数
Brooks定理：当G不是完全图或奇圈时，χ(G) ≤ Δ(G)
```

## 参考文献

- Diestel, R. (2017). *Graph Theory*, 5th ed. Springer GTM 173. ISBN 978-3662536216
- Cormen, T.H. et al. (2022). *Introduction to Algorithms*, 4th ed. MIT Press. ISBN 978-0262046305
- Euler, L. (1736). "Solutio problematis ad geometriam situs pertinentis," *Commentarii academiae scientiarum Petropolitanae*, 8, 128-140.

## 教学路径

**前置知识**：集合论基础、基本算法概念
**学习建议**：先手绘小图理解度、路径、连通的直觉，再实现 BFS 和 DFS。学习最短路径时，在 5-6 个节点的图上手动执行 Dijkstra 算法。图论的核心在于**将实际问题建模为图**的能力。
**进阶方向**：网络流（Ford-Fulkerson）、匹配理论（Hungarian算法）、谱图论、随机图模型。
