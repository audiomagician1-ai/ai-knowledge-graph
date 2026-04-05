---
id: "kruskal-mst"
concept: "Kruskal最小生成树"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 6
is_milestone: false
tags: ["图"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Kruskal最小生成树

## 概述

Kruskal算法是一种贪心算法，用于在加权无向连通图中寻找最小生成树（Minimum Spanning Tree，MST）。其核心思路是：将所有边按权重从小到大排序，依次选取权重最小的边，若该边不构成环，则将其加入生成树，直到生成树包含 $V-1$ 条边（$V$ 为顶点数）。最终结果是一棵连接所有顶点、总权重最小的无环树。

该算法由约瑟夫·克鲁斯卡尔（Joseph Kruskal）于1956年在论文《On the shortest spanning subtree of a graph and the traveling salesman problem》中正式提出，比Prim算法晚发表约两年。Kruskal算法的独特之处在于它以"边"为主体进行构建，而非以"顶点"为主体扩展，这使得它在稀疏图（边数远少于 $V^2$）上尤为高效。

Kruskal算法的时间复杂度为 $O(E \log E)$，其中 $E$ 为边数。排序操作主导了这个复杂度，并查集的查找与合并操作接近 $O(\alpha(V))$（近似常数）。在AI工程中，Kruskal算法常用于聚类分析、神经网络剪枝和图神经网络的图结构预处理等场景。

---

## 核心原理

### 贪心选边策略

Kruskal算法基于贪心性质：每次选取当前未加入生成树中权重最小的合法边。所谓"合法"是指加入该边后不形成环。这一贪心策略的正确性由**割性质（Cut Property）**保证：对于图中任意一个割（将顶点集分为两个非空子集），跨越该割的权重最小边一定属于某棵最小生成树。Kruskal算法本质上是对割性质的反复应用。

### 环检测与并查集

判断加入一条边 $(u, v)$ 是否形成环，等价于判断 $u$ 和 $v$ 是否已在同一连通分量中。Kruskal算法依赖**并查集**（Union-Find）数据结构高效完成这一判断：

- `Find(x)`：返回 $x$ 所属连通分量的根节点，配合路径压缩（Path Compression）优化后近似 $O(1)$。
- `Union(u, v)`：将 $u$ 和 $v$ 所在的两个连通分量合并，配合按秩合并（Union by Rank）可保持树高 $O(\log V)$。

若 `Find(u) == Find(v)`，则边 $(u, v)$ 会形成环，跳过；否则调用 `Union(u, v)` 合并两个分量并将该边加入MST。

### 算法完整流程

以一个5顶点图为例，边集为：`{(A,B,1), (B,C,4), (A,C,3), (C,D,2), (D,E,5), (B,E,6)}`。

1. **排序**：按权重升序排列所有边：`(A,B,1), (C,D,2), (A,C,3), (B,C,4), (D,E,5), (B,E,6)`
2. **选边**：
   - 选 `(A,B,1)`：A、B不同分量，合并，MST边数=1
   - 选 `(C,D,2)`：C、D不同分量，合并，MST边数=2
   - 选 `(A,C,3)`：A（与B同）、C（与D同）不同分量，合并，MST边数=3
   - 选 `(B,C,4)`：B、C已在同一分量，**跳过**
   - 选 `(D,E,5)`：D所在分量与E不同，合并，MST边数=4
3. **结束**：MST包含 $V-1=4$ 条边，总权重为 $1+2+3+5=11$。

---

## 实际应用

**聚类分析（单链接聚类）**：Kruskal构建MST后，删除最长的 $k-1$ 条边即可得到 $k$ 个簇，这等价于单链接（Single-Linkage）层次聚类。例如在图像分割任务中，将像素作为节点，颜色差异作为边权，用Kruskal构建MST再裁剪，能高效分割视觉相似区域。

**神经网络结构剪枝**：将神经网络权重矩阵构建为完全图，以参数绝对值为负权重（即越小的权重对应越大的图边权），使用Kruskal算法选取重要连接边，可在保持网络连通性的前提下最大化裁剪冗余连接，这在模型压缩研究中有实际应用记录。

**电力网格与通信网络规划**：Kruskal算法是最早被工程界采纳的MST算法之一，用于最小化电缆铺设总长度。在 $V=1000$、$E=5000$ 的稀疏城市通信图上，Kruskal由于只需对5000条边排序，远比对1000个顶点逐一扩展的Prim算法高效。

---

## 常见误区

**误区一：认为Kruskal算法能处理有向图**。Kruskal算法仅适用于**无向图**。有向图的最小生成树（称为最小树形图）需要使用朱刘算法（Edmonds算法）求解，其时间复杂度为 $O(VE)$，思路完全不同。将Kruskal直接套用在有向图上会得到错误结果。

**误区二：忘记处理非连通图**。若输入图本身不连通，Kruskal算法无法生成一棵覆盖所有顶点的树，而是生成**最小生成森林**（每个连通分量一棵树）。算法结束时若MST中边数少于 $V-1$，应返回"图不连通"或森林结果，而非报错。很多实现忽略了这个边界条件。

**误区三：认为Kruskal必定比Prim慢**。在稠密图（$E \approx V^2$）中，排序 $O(E \log E) = O(V^2 \log V)$ 确实比Prim使用Fibonacci堆的 $O(E + V \log V)$ 慢。但在稀疏图（$E \approx V$）中，Kruskal的 $O(E \log E) \approx O(V \log V)$ 反而更具优势，两者各有适用场景。

---

## 知识关联

**前置依赖——并查集**：Kruskal算法的环检测完全依赖并查集的`Find`和`Union`操作。若不理解路径压缩和按秩合并，就无法分析Kruskal的真实时间复杂度（不加优化的并查集会使整体退化到 $O(E \log E \cdot V)$）。并查集的正确实现是Kruskal达到理论复杂度的必要条件。

**后续概念——最小生成树的应用与变体**：掌握Kruskal后，可进一步学习次小生成树（Second MST）的求法（在MST中替换一条边）、度约束最小生成树（限制某顶点最大度数）以及动态最小生成树（支持边的插入删除）。这些变体问题都以理解Kruskal的贪心选边逻辑为基础，在竞争性编程和AI图算法研究中频繁出现。与Prim算法的对比分析也是最小生成树专题中不可回避的核心内容。