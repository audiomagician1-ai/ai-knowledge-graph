---
id: "graph-ds"
concept: "图(数据结构)"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 5
is_milestone: false
tags: ["图"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 图（数据结构）

## 概述

图（Graph）是由顶点集合（Vertices）和边集合（Edges）组成的非线性数据结构，形式化定义为 $G = (V, E)$，其中 $V$ 是有限非空顶点集，$E \subseteq V \times V$ 是边的集合。与数组或链表这类线性结构不同，图中任意两个顶点之间都可以存在连接关系，因此图能够表达多对多的复杂关联，是计算机科学中表达力最强的基础数据结构之一。

图的理论基础可追溯至1736年，数学家莱昂哈德·欧拉（Leonhard Euler）为解决"柯尼斯堡七桥问题"而提出了图的雏形。他将城市的四块陆地区域抽象为4个顶点，将7座桥梁抽象为7条边，证明了"一笔画遍全部七座桥而不重复"的路径不存在——判断依据是：满足欧拉路径的充要条件为图中奇度顶点的个数为0（欧拉回路）或恰好为2（欧拉路径），而柯尼斯堡图有4个奇度顶点，故不满足。这是图论历史上第一个严格证明，发表于《圣彼得堡科学院评论》。

在AI工程领域，图结构直接支撑了知识图谱（Knowledge Graph）、神经网络计算图、社交网络分析和路径规划等核心应用。以Google的知识图谱为例，截至2023年其存储了超过5000亿个事实三元组，每个三元组 $(\text{实体}_A, \text{关系}, \text{实体}_B)$ 本质上就是图中的一条有向带标签边（labeled directed edge）。

参考经典教材：《算法导论》（Cormen et al., 2009，第三版，MIT Press）第22章对图的表示与遍历有完整的形式化处理。

---

## 核心原理

### 图的基本分类

图按边的方向性分为**有向图（Directed Graph）**和**无向图（Undirected Graph）**。无向图中边 $(u, v)$ 与 $(v, u)$ 等价，仅计为一条边；有向图中从 $u$ 指向 $v$ 的弧 $\langle u, v \rangle$ 与 $\langle v, u \rangle$ 是两条独立的有向边。若每条边附带数值权重 $w$，则称为**加权图（Weighted Graph）**，权重通常表示道路距离（单位：米）、通信延迟（单位：毫秒）或语义相似度（取值0~1）。

图还分为**稠密图（Dense Graph）**和**稀疏图（Sparse Graph）**。设 $|V| = n$，无向图的最大边数为 $\frac{n(n-1)}{2}$，有向图最大边数为 $n(n-1)$。当实际边数 $|E|$ 接近 $O(n^2)$ 时为稠密图；当 $|E| \approx O(n)$ 时为稀疏图。对于100个顶点的图，稠密图最多可有4950条无向边，而现实社交网络中平均每人约有150条好友关系（Dunbar's number），远小于理论上限，属于典型稀疏图。这一区分直接决定应选用邻接矩阵（适合稠密图，空间复杂度 $O(n^2)$）还是邻接表（适合稀疏图，空间复杂度 $O(n + |E|)$）来存储。

### 度（Degree）的概念与握手定理

顶点 $v$ 的**度（Degree）** $\deg(v)$ 是与该顶点关联的边的数量。**握手定理**指出：

$$\sum_{v \in V} \deg(v) = 2|E|$$

这意味着无向图中所有顶点度之和恒为偶数，且等于边数的两倍。在有向图中，顶点分为**入度（In-degree）** $\deg^-(v)$（指向 $v$ 的边数）和**出度（Out-degree）** $\deg^+(v)$（从 $v$ 出发的边数），满足：

$$\sum_{v \in V} \deg^-(v) = \sum_{v \in V} \deg^+(v) = |E|$$

PageRank算法（Page et al., 1999）的核心逻辑正是基于网页有向图中的入度结构，网页 $i$ 的排名分值由下式迭代计算：

$$PR(i) = \frac{1-d}{N} + d \sum_{j \in \text{in-neighbors}(i)} \frac{PR(j)}{\deg^+(j)}$$

其中阻尼系数 $d = 0.85$，$N$ 为网页总数。该公式本质上是一个在有向图上的随机游走稳态分布。

### 连通性与图的特殊形态

无向图中，若任意两个顶点之间都存在路径，则称为**连通图（Connected Graph）**；否则其中每个最大连通子图称为**连通分量（Connected Component）**。有向图则区分**强连通（Strongly Connected）**（任意两顶点互相可达）和**弱连通（Weakly Connected）**（忽略边方向后连通）。Kosaraju算法（1978年提出）可在 $O(|V| + |E|)$ 时间内找到有向图的所有强连通分量。

不含环的连通无向图称为**树（Tree）**，树满足 $|E| = |V| - 1$。若有向图中不含有向环，则称为**有向无环图（DAG，Directed Acyclic Graph）**。PyTorch和TensorFlow构建的神经网络计算图正是DAG：每个算子节点的输出连向下一个算子，反向传播时按拓扑逆序计算梯度，DAG结构保证了此拓扑排序的存在性与唯一性（在无分支情况下）。

---

## 关键公式与存储结构代码

### 邻接矩阵表示

对于 $n$ 个顶点的加权有向图，邻接矩阵 $A$ 的定义为：

$$A[i][j] = \begin{cases} w_{ij} & \text{若存在边} \langle i, j \rangle \text{，权重为} w_{ij} \\ 0 \text{ 或 } \infty & \text{若不存在边} \langle i, j \rangle \end{cases}$$

### Python实现：图的两种存储结构

```python
# === 邻接矩阵（适合稠密图） ===
# 5个顶点的无向加权图，INF表示无边
INF = float('inf')
n = 5
adj_matrix = [[INF] * n for _ in range(n)]
for i in range(n):
    adj_matrix[i][i] = 0  # 自身到自身距离为0

def add_edge_matrix(u, v, w):
    adj_matrix[u][v] = w
    adj_matrix[v][u] = w  # 无向图需双向赋值

# === 邻接表（适合稀疏图） ===
# 用字典实现，存储 {顶点: [(邻居, 权重), ...]}
from collections import defaultdict

class Graph:
    def __init__(self, directed=False):
        self.adj = defaultdict(list)
        self.directed = directed

    def add_edge(self, u, v, w=1):
        self.adj[u].append((v, w))
        if not self.directed:
            self.adj[v].append((u, w))  # 无向图双向添加

    def neighbors(self, u):
        return self.adj[u]  # O(deg(u)) 遍历邻居

# 示例：构建一个4顶点有向图
g = Graph(directed=True)
g.add_edge(0, 1, 5)   # 0→1, 权重5
g.add_edge(0, 2, 3)   # 0→2, 权重3
g.add_edge(1, 3, 2)   # 1→3, 权重2
g.add_edge(2, 3, 7)   # 2→3, 权重7
print(g.neighbors(0))  # 输出: [(1, 5), (2, 3)]
```

邻接表中，查询顶点 $u$ 的所有邻居时间复杂度为 $O(\deg(u))$；邻接矩阵查询两点间是否有边为 $O(1)$，但枚举所有邻居需 $O(n)$。当 $n = 10000$、$|E| = 50000$ 时，邻接表仅需约 $50000 \times 2 \times 8 = 800$ KB，而邻接矩阵需 $10000^2 \times 8 = 800$ MB，两者相差约1000倍。

---

## 实际应用

### 推荐系统中的二部图

用户和商品作为两类顶点，用户对商品的购买或评分行为作为边，构成**二部图（Bipartite Graph）**——二部图满足顶点集可分为两个互不相交的子集 $U$（用户）和 $I$（物品），所有边仅存在于 $U$ 和 $I$ 之间，$U$ 内部或 $I$ 内部无边。协同过滤算法通过分析此二部图中"用户-物品-用户"的长度为2的路径，计算用户间的共同评分物品数，进而推荐候选商品。Netflix于2009年举办的推荐系统竞赛（Netflix Prize）中，冠军队伍BellKor的算法核心即基于用户-电影二部图的矩阵分解。

### 地图导航中的加权有向图

高德地图、Google Maps等导航系统将城市路网建模为加权有向图：路口为顶点（北京城区约有12万个路口），道路为有向边（单行道为单向边），行驶时间为权重（随实时路况动态更新）。Dijkstra算法可在此图上计算单源最短路径，时间复杂度为 $O((|V| + |E|) \log |V|)$（使用优先队列）。对于10万顶点的稀疏路网，单次最短路径查询通常在50毫秒内完成。

### 深度学习中的计算图（DAG应用）

PyTorch中，每次执行 `y = x * w + b` 时会动态构建一个DAG：`x`、`w`、`b` 为叶节点，乘法算子和加法算子为中间节点，`y` 为根节点。调用 `y.backward()` 时，PyTorch按该DAG的拓扑逆序（从根到叶）逐节点应用链式法则，自动计算 $\frac{\partial y}{\partial w}$ 和 $\frac{\partial y}{\partial b}$。这一机制称为**自动微分（Automatic Differentiation）**，完全依赖图结构的拓扑排序保证正确的计算顺序。

### 知识图谱中的有向多关系图

知识图谱（如Wikidata）存储的是**异构有向图**：顶点类型包括实体（人、地点、概念）和属性值，边类型（关系）超过6000种（如"出生于"、"属于"、"开发者是"）。图神经网络（GNN）通过在此图上聚合邻居节点特征来学习实体嵌入向量，关系型GNN（如R-GCN，Schlichtkrull et al., 2018）专门处理多关系异构图，在知识图谱补全任务上的MRR（Mean Reciprocal Rank）指标比传统TransE模型提升约15%。

---

## 常见误区

**误区1：混淆树与图的关系。** 树是图的特例（无环连通无向图），满足 $|E| = |V| - 1$，但图不一定是树。常见错误是在处理一般图时套用树的遍历假设（如认为"访问过父节点就不会再回来"），导致BFS/DFS未正确标记已访问节点，产生无限循环。图的DFS必须维护 `visited` 集合，而树的DFS通常不需要。

**误区2：有向图与无向图的度计算混淆。** 在无向图中 $\deg(v)$ 唯一，但在有向图中必须区分 $\deg^+(v)$ 和 $\deg^-(v)$。例如，计算PageRank时使用的是出度 $\deg^+(j)$ 做归一化，若误用总度数 $\deg^+(j) + \deg^-(j)$，会导致概率分布不归一，排名计算错误。

**误区3：认为邻接矩阵一定比邻接表低效。** 对于Floyd-Warshall全源最短路径算法（时间复杂度 $O(n^3)$），其核心操作 `dist[i][k] + dist[k][j]` 是随机访问，邻接矩阵的 $O(1)$ 访问使缓存命中率极高；而邻接表在此场景下频繁跳转指针，实际运行时间反而