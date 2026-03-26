---
id: "minimum-spanning-tree"
concept: "最小生成树"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 6
is_milestone: false
tags: ["图算法"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.406
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 最小生成树

## 概述

最小生成树（Minimum Spanning Tree，MST）是在一个带权无向连通图中，选取恰好 **n-1** 条边将所有 n 个顶点连通，且所选边的权重之和最小的树形结构。注意"生成"二字意味着必须包含原图的全部顶点，而"树"意味着无环且连通。对于同一张图，最小生成树可能不唯一（当存在权重相同的边时），但最小总权重是唯一的。

这一问题由 Otakar Borůvka 在 1926 年首次研究，当时的工程背景是为摩拉维亚地区规划最低成本的电网。随后，Joseph Kruskal 在 1956 年提出了以贪心边排序为核心的算法，Robert Prim 在 1957 年独立提出了基于顶点扩展的算法。两者解决的是同一个问题，但策略完全不同，适用场景也有所差异。

在 AI 工程中，最小生成树被用于聚类分析（单链接聚类的层次树等价于 MST）、特征图构建、神经网络中的稀疏连接设计以及知识图谱的骨干提取。理解两种算法的时间复杂度与数据结构依赖，有助于在边数稀疏或稠密的图上选择更高效的实现。

---

## 核心原理

### 切割性质（Cut Property）与贪心正确性

MST 算法的正确性依赖一个数学定理：对图的任意"切割"（将顶点集分为两部分 S 和 V\S），**跨越该切割的权重最小边必定属于某棵 MST**。Kruskal 和 Prim 都是这一性质的具体实例化。只要每步选择"当前合法的最小权重边"，就能保证最终结果最优，这是贪心策略在此处成立的严格依据，而非直觉。

### Kruskal 算法：按边排序 + 并查集

Kruskal 的思路是"全局视角"：将所有边按权重从小到大排序，逐条检查每条边是否连接了两个尚未连通的分量，若是则加入 MST，否则跳过。判断两顶点是否已连通依赖**并查集（Union-Find）**数据结构，使用路径压缩和按秩合并后，每次 Find/Union 操作的均摊时间复杂度为 **O(α(n))**（α 为反阿克曼函数，实际可视为常数）。

总时间复杂度为 **O(E log E)**，排序步骤占主导。对于稀疏图（E ≈ O(V)），此复杂度约为 O(V log V)，非常高效。Kruskal 的缺点是需要一次性获取全部边并排序，对流式或动态图场景不友好。

```
Kruskal(G):
  将所有边按权重升序排列
  初始化并查集，每个顶点为独立分量
  MST_edges = []
  for each edge (u, v, w) in sorted order:
      if Find(u) ≠ Find(v):
          MST_edges.append((u, v, w))
          Union(u, v)
      if len(MST_edges) == n-1: break
  return MST_edges
```

### Prim 算法：从顶点扩展 + 优先队列

Prim 的思路是"局部视角"：维护一个已加入 MST 的顶点集合 S，初始时 S 仅含任意起点。每轮从所有"一端在 S 内、一端在 S 外"的边中选权重最小的边，将对应新顶点加入 S，重复 n-1 次。

使用**二叉堆（最小优先队列）**时，总时间复杂度为 **O((V + E) log V)**；若使用**斐波那契堆**，可将复杂度优化到 **O(E + V log V)**，在稠密图（E ≈ O(V²)）上明显优于 Kruskal。Prim 每次只需访问当前顶点的邻接边，天然适合邻接表存储和稠密图场景。

```
Prim(G, start):
  dist[v] = ∞ for all v; dist[start] = 0
  优先队列 PQ = {(0, start)}
  inMST = set()
  while PQ not empty:
      (w, u) = PQ.pop_min()
      if u in inMST: continue
      inMST.add(u)
      for each neighbor v of u with edge weight c:
          if v not in inMST and c < dist[v]:
              dist[v] = c
              PQ.push((c, v))
```

---

## 实际应用

**网络基础设施规划**：在构建光纤骨干网时，城市节点为顶点，铺设成本为边权，MST 直接给出最低总成本连通方案。Borůvka 的原始电网问题正是此类场景。

**聚类分析中的单链接方法**：对数据点构建完全图（边权为欧氏距离），其 MST 的最长边对应两个最远的簇间连接。删除 MST 中权重最大的 k-1 条边，即可将数据分成 k 个簇，这等价于单链接层次聚类的最终切割结果。

**图像分割**：在基于图的图像分割算法（如 Felzenszwalb-Huttenlocher 2004 年算法）中，像素作为顶点，相邻像素的颜色差异作为边权，MST 用于判断区域内部差异与区域间差异的比较阈值。

**稀疏化大规模知识图谱**：在知识图谱推理任务中，对关系权重图求 MST 可提取最关键的 n-1 条语义骨干边，大幅降低图神经网络的计算量，同时保留全局连通性。

---

## 常见误区

**误区1：认为 MST 中两点间路径是图中的最短路径**
MST 保证的是"总边权最小的生成树"，而非任意两点间的最短路径。例如，图中顶点 A 到顶点 C 的直接边权重为 3，但 MST 可能选择了 A→B→C（权重 1+1=2），此时 MST 路径恰好也是最短路径；但若 MST 为了保证全局最小总权而绕行，A→C 在 MST 上的路径可能比图中直接边更长。最短路径问题需要 Dijkstra 或 Bellman-Ford，与 MST 是不同的问题。

**误区2：Prim 和 Kruskal 任意场景下效率相同**
两者的时间复杂度随图的稀疏程度而有本质差异。稀疏图（E ≈ V）时 Kruskal 的 O(E log E) 约为 O(V log V)，优于 Prim 的 O((V+E) log V)；稠密图（E ≈ V²）时，Prim 配合斐波那契堆的 O(E + V log V) = O(V²) 优于 Kruskal 的 O(V² log V²) = O(V² log V)。在工程实践中，对稠密图（如全连接神经层的权重图）盲目使用 Kruskal 会造成不必要的性能损耗。

**误区3：带负权边的图不能求 MST**
MST 算法并不要求边权为正。Kruskal 和 Prim 都对负权边成立，因为它们的正确性依赖切割性质，而该性质对任意实数权重均有效。与最短路径问题不同，MST 算法不存在"负权环导致无限循环"的问题——生成树本身无环，负权边只会优先被选入 MST。

---

## 知识关联

**前置概念的具体依赖**：Kruskal 算法直接调用**并查集**的 Find 和 Union 操作，若不使用路径压缩和按秩合并，时间复杂度会退化为 O(E·V)，算法在大图上将不可用。理解并查集的均摊分析是理解 Kruskal 复杂度的必要条件。**图（数据结构）**的邻接表 vs. 邻接矩阵存储选择直接影响 Prim 的实现效率：邻接矩阵下遍历邻居需 O(V)，邻接表下仅需 O(degree(v))。

**Kruskal MST 的单独学习路径**：本文档与"Kruskal最小生成树"作为独立前置概念的关系在于：单独学习 Kruskal 侧重其并查集实现细节，而本文档在此基础上补充了与 Prim 的对比分析，以及切割性质这一统一理论框架，使学生能在给定图的特征（稀疏/稠密、动态/静态）下做出算法选择。

**延伸方向**：在 AI 工程中，MST 的变体包括**最大生成树**（将边权取反后求 MST，用于最大瓶颈路径）、**度约束最小生成树**（限制某顶点的度数，NP-hard问题）以及**Steiner树**（允许只连接顶点子集，常见于芯片布线优化）。