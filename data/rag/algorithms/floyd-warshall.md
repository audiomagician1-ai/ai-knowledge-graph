---
id: "floyd-warshall"
concept: "Floyd-Warshall算法"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 4
is_milestone: false
tags: ["shortest-path", "graph", "dp"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.1
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

# Floyd-Warshall算法

## 概述

Floyd-Warshall算法是一种用于求解**加权图中所有顶点对之间最短路径**的动态规划算法，能够同时处理有向图与无向图，并支持负权边（但不允许存在负权环）。与Dijkstra算法每次只能计算单一源点到其他顶点的最短路径不同，Floyd-Warshall一次运行即可得到图中所有 V² 对顶点之间的最短距离，时间复杂度为 **O(V³)**，空间复杂度为 **O(V²)**。

该算法由Robert Floyd于1962年发表在《Communications of the ACM》期刊上，但其核心思想与Stephen Warshall在同年提出的传递闭包算法高度相关，因此以两人共同命名。值得注意的是，这一动态规划思路最早可追溯到Bernard Roy在1959年的独立发现，因此在法国文献中有时也称作"Roy-Floyd算法"。

Floyd-Warshall在AI工程中的重要性体现在路径规划、知识图谱中的实体关系推断、以及强化学习中的状态距离估计等场景。当图规模较小（V ≤ 500）但需要频繁查询任意两点间最短距离时，Floyd-Warshall预计算一张距离矩阵的策略往往优于多次调用Dijkstra。

---

## 核心原理

### 动态规划状态定义

Floyd-Warshall的关键在于定义三维DP状态：

> **dp[k][i][j]** = 只允许使用编号为 1 到 k 的顶点作为中间节点时，从顶点 i 到顶点 j 的最短路径长度。

状态转移方程为：

$$dp[k][i][j] = \min\bigl(dp[k-1][i][j],\; dp[k-1][i][k] + dp[k-1][k][j]\bigr)$$

其中 dp[k-1][i][j] 表示"不经过顶点 k"的最短路径，dp[k-1][i][k] + dp[k-1][k][j] 表示"经过顶点 k 中转"的路径长度。由于对任意固定的 k，dp[k][i][k] = dp[k-1][i][k] 且 dp[k][k][j] = dp[k-1][k][j]（第 k 行和第 k 列不受第 k 次迭代影响），可以将三维数组压缩为二维矩阵原地更新，使空间降至 O(V²)。

### 初始化与边界条件

初始矩阵 dist[i][j] 按如下规则填充：
- dist[i][i] = 0（自身到自身距离为零）
- 若存在边 (i, j)，则 dist[i][j] = 边权 w(i, j)
- 若不存在边 (i, j)，则 dist[i][j] = +∞

三重循环的**外层循环必须是中间节点 k**，内层才是起点 i 和终点 j。如果将循环顺序写成 i-j-k，则算法将给出错误结果，这是初学者最常犯的实现错误。

### 负权环检测

算法结束后，若存在某个顶点 v 使得 dist[v][v] < 0，则说明图中存在**负权环**。负权环会导致最短路径无穷递减，因此Floyd-Warshall在这种情况下无法给出有意义的结果。检测代码只需在三重循环结束后遍历对角线元素即可，时间代价仅为额外 O(V)。

### 路径重建

仅靠 dist 矩阵只能知道最短距离，无法还原路径。需要维护一个**前驱矩阵 next[i][j]**，初始时若存在边 (i,j) 则 next[i][j] = j，否则为 null。每当执行松弛操作 dist[i][j] = dist[i][k] + dist[k][j] 时，同步更新 next[i][j] = next[i][k]。重建路径时，从起点 i 出发不断查询 next 直到抵达终点 j，时间为 O(V)。

---

## 实际应用

**网络路由协议**：互联网中的RIP（Routing Information Protocol）早期变体使用类似Floyd-Warshall的逻辑维护路由表，计算网络中所有路由器对之间的最短跳数路径。

**知识图谱实体距离**：在AI知识图谱中，可将实体视为顶点、关系视为有向边，用Floyd-Warshall预计算实体间的最小关系跳数，从而支持"两个实体最短关联路径"的实时查询，避免每次查询都启动BFS/Dijkstra。

**城市交通规划**：一个包含 300 个交叉口的城市路网，使用Floyd-Warshall只需 300³ = 2.7×10⁷ 次操作即可预计算全部 90,000 对节点间最短行驶时间，适合离线批量预处理后存入缓存。

**差分约束系统**：若存在约束 xⱼ - xᵢ ≤ wᵢⱼ，可将其建模为有向边，然后用Floyd-Warshall判断系统是否有解（存在负权环则无解），并求各变量的可行范围。

---

## 常见误区

**误区一：认为Floyd-Warshall能处理负权环**
部分学习者混淆"支持负权边"与"支持负权环"。Floyd-Warshall在有负权边时仍然正确，但若图中存在负权环，算法会得到错误的负无穷距离，且对角线 dist[v][v] < 0 是唯一可靠的检测手段，必须显式加以检查。

**误区二：循环顺序可以任意调换**
Floyd-Warshall的正确性严格依赖**k 在最外层**这一顺序。若写成 for i... for j... for k...，则在处理 dist[i][j] 时，所需的 dist[i][k] 或 dist[k][j] 尚未被完整更新，导致结果错误。Dijkstra没有类似的循环顺序约束，因此从Dijkstra迁移过来的开发者容易在此出错。

**误区三：对稀疏大图优先选择Floyd-Warshall**
当顶点数 V = 1000 时，Floyd-Warshall需要执行 10⁹ 次操作，在大多数硬件上需要数秒甚至更长。对于稀疏图（边数 E << V²），对每个顶点运行一次Dijkstra（使用优先队列）的总复杂度为 O(V·(E + V)logV)，通常远快于 O(V³)。选择Floyd-Warshall应限制在 V ≤ 400~500 的稠密图场景。

---

## 知识关联

**与Dijkstra最短路径的关系**：Dijkstra解决的是单源最短路径问题，贪心地从已确定顶点向外扩展，时间复杂度为 O((V+E)logV)。Floyd-Warshall可以视为对所有顶点同时执行"松弛"的全局DP方案。两者的本质区别在于：Dijkstra不支持负权边，而Floyd-Warshall支持负权边但不支持负权环；Dijkstra适用于稀疏图单次查询，Floyd-Warshall适用于小型稠密图的全源预计算。

**与动态规划的关系**：Floyd-Warshall是图论算法中DP思想最直接的体现之一——状态 dp[k][i][j] 以"可使用的中间节点集合"作为阶段划分，子问题之间的重叠性使得三维DP的总计算量从朴素的指数级降到 O(V³)。理解这一状态定义方式，有助于举一反三地处理其他"允许集合递增"类型的图DP问题，例如传递闭包（Warshall算法将加法换成逻辑OR即可）。