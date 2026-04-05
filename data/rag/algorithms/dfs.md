---
id: "dfs"
concept: "深度优先搜索(DFS)"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 4
is_milestone: false
tags: ["图", "搜索"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 深度优先搜索（DFS）

## 概述

深度优先搜索（Depth-First Search，DFS）是一种图与树的遍历算法，其核心策略是：从起始节点出发，沿一条路径尽可能向深处探索，直到到达叶节点或无法继续前进，然后**回溯**（backtrack）到上一个有未访问邻居的节点，再继续向深处探索。这与广度优先搜索（BFS）逐层扩展的方式截然相反——DFS 优先"走完一条路"再考虑其他选择。

DFS 的思想可追溯至 19 世纪。法国数学家 Charles Pierre Trémaux 于 1882 年提出了一种用于解决迷宫问题的手工算法，该方法被认为是 DFS 的原型。现代计算机科学中，DFS 作为系统性算法由 Robert Tarjan 等人在 1970 年代形式化，并被用于设计著名的强连通分量算法（Tarjan's SCC，1972 年）。

DFS 的重要性在于其空间效率与递归天然的对应关系。在深度为 $d$ 的搜索树上，DFS 只需 $O(d)$ 的栈空间，而 BFS 在最坏情况下需要存储一整层节点，空间可达 $O(b^d)$（$b$ 为分支因子）。这使 DFS 特别适合深度大、分支多的搜索空间，例如棋盘游戏的博弈树或程序的调用图分析。

---

## 核心原理

### 递归实现与隐式调用栈

DFS 最自然的实现是递归。每次递归调用对应"沿一条边向下走一步"，函数返回对应"回溯"。以下是标准伪代码：

```
DFS(graph, node, visited):
    marked visited[node] = True
    process(node)
    for each neighbor v of node:
        if visited[v] == False:
            DFS(graph, v, visited)
```

递归版本借助**程序调用栈**隐式保存回溯路径。图中有 $V$ 个节点、$E$ 条边时，时间复杂度为 $O(V + E)$，这对邻接表表示的图是最优的。若使用邻接矩阵，则为 $O(V^2)$，因为查找邻居需遍历整行。

### 显式栈的迭代实现

递归在图深度极大时会导致栈溢出（Python 默认递归深度限制为 1000 层）。迭代版 DFS 用显式的数据结构——**栈（Stack）**——替代调用栈：

```
DFS_iterative(graph, start):
    stack = [start]
    visited = set()
    while stack is not empty:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            process(node)
            for each neighbor v of node (reversed order):
                if v not in visited:
                    stack.push(v)
```

注意：迭代版中邻居的入栈顺序与递归版的访问顺序**可能不同**，若需保持一致需将邻居逆序压栈。这一细节在面试和工程实践中是常见的陷阱点。

### DFS 时间戳与节点着色

DFS 可为每个节点记录两个时间戳：**发现时间** $d[v]$（节点第一次被访问时）和**完成时间** $f[v]$（节点所有邻居均处理完毕时）。这两个值满足括号定理（Parenthesis Theorem）：对于任意两节点 $u$ 和 $v$，区间 $[d[u], f[u]]$ 与 $[d[v], f[v]]$ 要么完全嵌套，要么完全不相交。

利用这一性质，DFS 可对图中的边进行分类：
- **树边（Tree Edge）**：构成 DFS 树的骨干边
- **后向边（Back Edge）**：指向祖先节点，存在后向边意味着图中有**环**
- **前向边（Forward Edge）**：指向后代节点（仅在有向图中出现）
- **横叉边（Cross Edge）**：连接两个无祖先-后代关系的节点

在无向图中，DFS 只会产生树边和后向边，**不会出现前向边和横叉边**，这是无向图 DFS 的重要特性。

---

## 实际应用

**拓扑排序（Topological Sort）**：对有向无环图（DAG）执行 DFS，将每个节点在完成时（$f[v]$ 记录时）压入一个结果栈，最终弹出顺序即为拓扑序。例如编译器分析模块依赖关系时，使用 DFS 完成拓扑排序的时间复杂度为 $O(V + E)$。

**检测图中的环**：在 DFS 遍历有向图时，维护一个"当前路径集合"（灰色节点集）。若某条边指向灰色节点，则发现了后向边，即图中存在环。Python 的 `import` 系统的循环依赖检测使用了类似机制。

**连通分量与强连通分量**：在无向图中，DFS 的一次完整遍历可识别所有连通分量。对于有向图，Tarjan 算法通过一次 DFS（$O(V + E)$）利用发现时间和 `low` 值找出所有强连通分量，比 Kosaraju 算法少一次图遍历。

**迷宫求解与游戏树搜索**：DFS 天然地模拟"走迷宫"行为。在国际象棋引擎的极小化极大（Minimax）搜索中，DFS 用于遍历博弈树；结合 Alpha-Beta 剪枝时，最优情况下可将需要评估的节点数从 $O(b^d)$ 降低至 $O(b^{d/2})$。

---

## 常见误区

**误区一：DFS 一定比 BFS 快**。DFS 与 BFS 的时间复杂度同为 $O(V + E)$，并无绝对快慢之分。DFS 的优势是空间开销小（$O(d)$ vs $O(b^d)$），但若目标节点离起点很近（浅层），BFS 会更快找到；DFS 可能沿错误路径走到很深处才回溯。

**误区二：迭代版 DFS 与递归版 DFS 完全等价**。如前所述，直接用栈模拟的迭代版 DFS 在节点访问顺序上与递归版存在差异。此外，迭代版在某些实现中对同一节点可能重复入栈（入栈时未标记 visited，仅出栈时标记），这会导致节点被处理多次，需谨慎设计 `visited` 的更新时机。

**误区三：DFS 找到的路径是最短路径**。DFS 找到的是"一条可行路径"，不保证最短。在无权图中，最短路径需要 BFS；在加权图中需要 Dijkstra 算法（时间复杂度 $O((V + E) \log V)$）。将 DFS 用于最短路径是一个典型的算法选择错误。

---

## 知识关联

**前置知识**：DFS 在**图（数据结构）**上运行，需理解邻接表与邻接矩阵的表示方式——邻接表使 DFS 时间复杂度为 $O(V+E)$，邻接矩阵则为 $O(V^2)$。**栈**是 DFS 的底层机制：递归调用栈与显式栈的等价性是实现迭代 DFS 的理论依据。与**BFS** 的对比揭示了 DFS 在空间复杂度上的优势以及在最短路径问题上的局限性。

**后续知识**：**拓扑排序**直接建立在 DFS 完成时间 $f[v]$ 的基础上，是 DFS 时间戳机制的直接应用，适用于任务调度、依赖解析等场景。**回溯法**是 DFS 框架的扩展——它在 DFS 的回溯节点处加入"撤销操作"，使算法能够在约束条件下枚举所有可行解，例如 N 皇后问题（8 皇后共有 92 个解）和数独求解器均依赖 DFS 的回溯结构。