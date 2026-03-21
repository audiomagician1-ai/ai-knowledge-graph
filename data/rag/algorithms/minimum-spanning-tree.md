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
content_version: 1
quality_tier: "A"
quality_score: 69.8
generation_method: "ai-batch-v1"
unique_content_ratio: 0.973
last_scored: "2026-03-21"
sources: []
---
# 最小生成树

## 核心概念

最小生成树（MST, Minimum Spanning Tree）是一个连通加权无向图的子图，它包含所有顶点，使用最少的边（n-1条）使图连通，且总边权最小。

## 两种经典算法

### Kruskal算法（边导向）

思想：贪心地选择权重最小的边，只要不形成环就加入MST。

```python
# Python: Kruskal算法
def kruskal(n, edges):
    """n: 顶点数, edges: [(weight, u, v), ...]"""
    edges.sort()  # 按权重排序
    parent = list(range(n))
    
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # 路径压缩
            x = parent[x]
        return x
    
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False  # 已连通，加入会形成环
        parent[ra] = rb
        return True
    
    mst_weight = 0
    mst_edges = []
    for w, u, v in edges:
        if union(u, v):
            mst_weight += w
            mst_edges.append((u, v, w))
            if len(mst_edges) == n - 1:
                break
    return mst_weight, mst_edges
```

时间复杂度: O(E log E)，瓶颈在边排序。

### Prim算法（点导向）

思想：从任意起点出发，每次贪心地选择连接已访问集和未访问集的最小权边。

```python
# Python: Prim算法（使用优先队列）
import heapq

def prim(n, adj):
    """adj: 邻接表 adj[u] = [(weight, v), ...]"""
    visited = [False] * n
    heap = [(0, 0)]  # (weight, vertex)
    mst_weight = 0
    
    while heap:
        w, u = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        mst_weight += w
        for weight, v in adj[u]:
            if not visited[v]:
                heapq.heappush(heap, (weight, v))
    
    return mst_weight
```

时间复杂度: O(E log V)，使用二叉堆。

⚠️ 注意：以上为Python实现。在C++中通常使用`priority_queue`，Java中使用`PriorityQueue`，API不同但逻辑一致。

## 两种算法对比

| 特征 | Kruskal | Prim |
|------|---------|------|
| 思想 | 边排序+并查集 | 点扩展+优先队列 |
| 时间 | O(E log E) | O(E log V) |
| 适合 | 稀疏图 | 稠密图 |
| 数据结构 | 并查集 | 优先队列 |

## 性质

- MST不一定唯一（相同权重的边可能有不同选择）
- 切割性质（Cut Property）: 跨越任何切割的最小权边一定在某个MST中
- 环性质（Cycle Property）: 任何环中的最大权边一定不在某个MST中

## 典型应用

- **网络设计**: 最小成本连通城市/建设网络
- **聚类**: Kruskal停止条件改为k个连通分量
- **近似算法**: 旅行商问题(TSP)的2-近似解

## 与图数据结构的关系

MST算法建立在图的基础之上。理解图的表示（邻接表/邻接矩阵）和基本遍历是学习MST的前提。
