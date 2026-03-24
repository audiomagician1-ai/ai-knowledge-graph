---
id: "disjoint-set"
concept: "并查集"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 6
is_milestone: false
tags: ["图", "集合"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 40.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 并查集

## 概述

并查集（Union-Find 或 Disjoint Set Union，简称 DSU）是一种专门用于处理**动态连通性问题**的树形数据结构。它维护一个元素的集合族，支持两种基本操作：将两个集合合并（Union），以及查询某个元素属于哪个集合（Find）。这两个操作赋予它独特的名称"并查集"。

并查集最早由 Bernard A. Galler 和 Michael J. Fischer 于 1964 年正式提出，用于解决等价类划分问题。1975 年，Robert Tarjan 证明了路径压缩与按秩合并结合后，单次操作的时间复杂度接近常数，精确地说是均摊 O(α(n))，其中 α 是 Ackermann 函数的反函数，实际使用中 α(n) ≤ 4，使得并查集在工程中几乎等同于 O(1) 操作。

并查集在 AI 工程中的重要性体现在图算法加速上：Kruskal 最小生成树算法依赖并查集判断是否形成环路，社交网络中的连通分量计算、图神经网络的子图划分以及聚类算法中的合并操作均需要用到并查集高效处理动态合并和查询的能力。

---

## 核心原理

### 数据表示：森林结构

并查集用一个数组 `parent[]` 表示一片森林，其中每棵树代表一个不相交集合。`parent[i]` 存储节点 i 的父节点编号。若 `parent[i] == i`，则节点 i 是其所在集合的**根节点**（代表元）。初始化时，每个元素自成一个集合：`parent[i] = i`，共 n 棵单节点树。

### Find 操作与路径压缩

`Find(x)` 沿着 parent 链向上寻找 x 所在树的根节点。朴素实现在最坏情况下退化为 O(n)（链状树）。**路径压缩**（Path Compression）优化：在 Find 的递归回溯时，将路径上所有节点的 parent 直接指向根节点，使得后续查询路径极短。

```python
def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])  # 递归时顺手压缩路径
    return parent[x]
```

路径压缩使树几乎扁平化，单次 Find 的均摊时间从 O(log n) 进一步降低。

### Union 操作与按秩合并

`Union(x, y)` 将 x 和 y 所在的两个集合合并。朴素实现直接让一棵树的根指向另一棵树的根，但可能导致树高持续增长。**按秩合并**（Union by Rank）维护一个 `rank[]` 数组记录树的高度上界，每次将秩较小的树挂到秩较大的树根节点下：

```python
def union(x, y):
    rx, ry = find(x), find(y)
    if rx == ry:
        return  # 已在同一集合
    if rank[rx] < rank[ry]:
        rx, ry = ry, rx  # 保证 rx 秩不小于 ry
    parent[ry] = rx
    if rank[rx] == rank[ry]:
        rank[rx] += 1
```

单独使用按秩合并可将 Find 的最坏时间复杂度降至 O(log n)；**同时使用路径压缩与按秩合并**，则达到 Tarjan 证明的 O(α(n)) 均摊复杂度。

### 连通性判断

判断 x 和 y 是否属于同一集合，只需检查 `find(x) == find(y)`。这是并查集解决动态连通性问题的核心语义：两个节点的根相同当且仅当它们在同一连通分量中。

---

## 实际应用

### Kruskal 最小生成树中的环检测

Kruskal 算法按边权从小到大排序后依次加边，每次加边前调用 `find()` 判断边的两端是否已连通——若 `find(u) == find(v)` 则跳过（加入会成环），否则调用 `union(u, v)` 合并。对 n 个节点 m 条边的图，整体复杂度为 O(m log m + m α(n))，瓶颈在排序而非并查集操作。

### 社交网络连通分量

在构建好友关系图时，每添加一条"A 与 B 是好友"的关系即调用 `union(A, B)`，随时可通过 `find(x) == find(y)` 判断两人是否属于同一社交圈（连通分量）。动态添加 10⁷ 条边后仍能在毫秒级完成查询，正是 α(n) 接近常数的体现。

### 图像分割与像素聚类

在基于图的图像分割算法（如 Felzenszwalb 算法，2004年）中，图像像素被初始化为独立集合，相邻像素按照颜色差异加权，逐步 Union 差异小的像素，最终不同根节点代表不同的分割区域。整个过程对百万像素图像可在 O(n α(n)) 时间内完成。

### 判断无向图是否有环

遍历图的所有边 (u, v)：若 `find(u) == find(v)` 则图中存在环，否则 `union(u, v)`。该方法比 DFS 更简洁，且无需维护访问状态数组。

---

## 常见误区

### 误区一：认为按秩合并中 rank 等于树的实际高度

引入路径压缩后，`rank[x]` 不再精确反映树的高度，而是一个**高度上界**。路径压缩会压平节点但不更新 rank 值，因此 rank 只在按秩合并决策时保证"不把高树挂到矮树下"的相对顺序，不能用 rank 做精确的层数计算。若需要精确高度，须使用不带路径压缩的纯按秩合并版本。

### 误区二：混淆集合大小与秩，用 size 替代 rank

**按大小合并**（Union by Size）同样有效：将节点数少的树挂到节点数多的树下，可用 `size[]` 数组实现，最坏情况 O(log n)。但 size 与 rank 不能混用——rank 记录高度上界，size 记录节点总数，两者衡量维度不同。许多教材将二者混淆，实际上结合路径压缩后两种策略均能达到 O(α(n)) 均摊复杂度，但代码实现逻辑不同。

### 误区三：忽视并查集只支持合并不支持分裂

标准并查集是**单向操作**：Union 合并两个集合后，无法撤销拆分回去。若业务场景需要"删除"某条边或"分离"两个节点，标准并查集无法处理。此时需要使用**可撤销并查集**（Rollback Union-Find），配合按秩合并（不使用路径压缩）和显式维护操作栈来实现回滚，时间复杂度退化为 O(log n)。

---

## 知识关联

**前置知识——图（数据结构）**：并查集处理的核心场景是图的连通性问题。理解图的节点、边、连通分量概念是使用并查集的前提；图的邻接表表示则直接配合 Kruskal 算法中的边列表遍历。

**后续应用——Kruskal 最小生成树**：Kruskal 算法的正确性依赖并查集的连通判断，掌握并查集后可将 Kruskal 的时间分析从 O(n²) 加速到 O(m log m)，这是学习最小生成树算法的直接动力。

**延伸方向——最小生成树（整体）**：Prim 算法不使用并查集而使用优先队列，与 Kruskal+并查集形成对比——稠密图用 Prim，稀疏图用 Kruskal，并查集是稀疏图场景下最小生成树求解效率的关键保证。此外，并查集思想还延伸至**离线最近公共祖先（LCA）算法**（Tarjan LCA）和**动态连通性**等进阶图算法中。
