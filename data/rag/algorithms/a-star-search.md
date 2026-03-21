---
id: "a-star-search"
concept: "A*搜索算法"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 7
is_milestone: false
tags: ["图算法", "搜索"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 62.8
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# A*搜索算法

## 核心概念

A*（A-star）是一种启发式搜索算法，结合了Dijkstra算法的最优性保证和贪心搜索的效率。它通过估价函数 f(n) = g(n) + h(n) 来选择最有前途的节点进行探索。

## 关键公式

**f(n) = g(n) + h(n)**

- **g(n)**: 从起点到节点n的实际代价（已知）
- **h(n)**: 从节点n到目标的估计代价（启发函数）
- **f(n)**: 经过节点n的总估计代价

## 算法流程

```
1. 初始化：将起点加入openList，f(start)=h(start)
2. 循环：
   a. 从openList取出f值最小的节点current
   b. 如果current是目标 → 回溯路径，结束
   c. 将current移入closedList
   d. 遍历current的所有邻居neighbor：
      - 计算tentative_g = g(current) + cost(current, neighbor)
      - 如果neighbor在closedList且tentative_g ≥ g(neighbor) → 跳过
      - 如果tentative_g < g(neighbor) → 更新g、f，设parent
      - 将neighbor加入openList（如未在其中）
3. openList空了仍未到达目标 → 无解
```

## 启发函数h(n)的要求

### 可采纳性（Admissibility）
h(n)永远不高估实际代价：h(n) ≤ h*(n)
- 保证A*找到最优解
- 曼哈顿距离在网格中是可采纳的
- 欧氏距离在自由空间中是可采纳的

### 一致性（Consistency）
h(n) ≤ cost(n, n') + h(n')（三角不等式）
- 一致性蕴含可采纳性
- 保证每个节点只需扩展一次

## 常用启发函数

| 场景 | 启发函数 | 特点 |
|------|---------|------|
| 网格4方向 | 曼哈顿距离 | \|x1-x2\|+\|y1-y2\| |
| 网格8方向 | 切比雪夫距离 | max(\|Δx\|,\|Δy\|) |
| 自由空间 | 欧氏距离 | sqrt(Δx²+Δy²) |
| 无信息 | h=0 | 退化为Dijkstra |

## 复杂度

- **时间**: O(b^d)，b为分支因子，d为解的深度
- **空间**: O(b^d)，需存储所有已生成节点
- 好的启发函数可以大幅减少实际搜索节点数

## 与BFS和Dijkstra的关系

- **BFS**: 无权图最短路径，h=0且所有边权=1时A*退化为BFS
- **Dijkstra**: 带权图最短路径，h=0时A*退化为Dijkstra
- **A***: 用启发函数引导搜索方向，减少无效探索
