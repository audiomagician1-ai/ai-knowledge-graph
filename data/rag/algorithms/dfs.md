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
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.424
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 深度优先搜索（DFS）

## 概述

深度优先搜索（Depth-First Search，DFS）是一种图和树的遍历算法，其核心策略是：从起始节点出发，沿一条路径尽可能深入地访问节点，直到无法继续（遇到叶子节点或所有邻居已被访问），再回溯到上一个节点，继续探索其他未访问的分支。这种"一条路走到底、走不通再回头"的行为模式，与广度优先搜索（BFS）先展开当前层所有邻居的策略形成鲜明对比。

DFS 最早被系统化描述于19世纪法国数学家 Charles Pierre Trémaux 研究迷宫求解问题的论文中，现代计算机科学版本由 John Hopcroft 和 Robert Tarjan 在1970年代形式化，并因此共同获得1986年图灵奖。DFS 的时间复杂度为 **O(V + E)**，其中 V 是顶点数、E 是边数，空间复杂度在最坏情况（线性链状图）下为 **O(V)**，递归调用栈深度等于图的深度。

DFS 之所以在 AI 工程中举足轻重，是因为它是拓扑排序、强连通分量检测（Tarjan/Kosaraju 算法）、回溯搜索（如八皇后、数独求解）的直接基础。许多状态空间搜索问题，如博弈树搜索、依赖解析、编译器符号表分析，都依赖 DFS 的深度优先特性来高效地穷举路径。

---

## 核心原理

### 递归实现与显式栈实现

DFS 有两种等价的实现方式，其本质都依赖**后进先出（LIFO）**的栈结构。

**递归版本**（Python 伪代码）：
```python
visited = set()

def dfs(graph, node):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor)
```

**显式栈版本**（迭代）：
```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    stack.append(neighbor)
```

需要注意：两种写法在邻居访问顺序上可能产生差异——递归版本会按邻居列表顺序依次深入，而显式栈版本由于 `pop()` 取出最后压入的元素，实际访问顺序是邻居列表的**逆序**。在对遍历顺序有严格要求的场景（如拓扑排序）中，需要注意这一区别。

### DFS 时间戳与树/非树边分类

Tarjan 在1972年引入了 DFS **时间戳**（discovery time 和 finish time）机制，每个节点记录两个值：`d[v]`（首次被访问时的全局计数器值）和 `f[v]`（递归处理完该节点所有后代后的计数器值）。对于有向图，DFS 将边分为四类：

| 边类型 | 判断条件 | 意义 |
|--------|----------|------|
| 树边（Tree Edge） | `v` 通过 DFS 首次发现 `u` | 构成 DFS 生成树 |
| 后向边（Back Edge） | `u` 是 `v` 的祖先 | 有向图中存在环的证据 |
| 前向边（Forward Edge） | `u` 是 `v` 的后代但非树边 | 仅出现在有向图 |
| 横叉边（Cross Edge） | 其他情况 | 跨越不同 DFS 树的分支 |

**无向图的 DFS 只产生树边和后向边**，绝不产生前向边和横叉边，这一性质使得无向图的环检测只需判断是否存在后向边即可，时间复杂度严格为 O(V + E)。

### 连通性与强连通分量

在有向图中，DFS 的 finish time 排序是 Kosaraju 算法的关键：第一次 DFS 按 finish time 降序压栈，第二次在**转置图**（所有边反向）上按该顺序做 DFS，每次第二轮 DFS 访问到的节点集合恰好构成一个**强连通分量（SCC）**。两次 DFS 的总时间复杂度仍为 O(V + E)，比朴素的 O(V²) 方法快得多。Tarjan 的单次 DFS 算法利用 `low` 值（节点通过后向边能到达的最小 discovery time）同样在 O(V + E) 内完成 SCC 检测。

---

## 实际应用

**1. 依赖关系解析与拓扑排序**
在 Python 包管理器 pip 或 Node.js 的 npm 中，安装包前需要解析依赖顺序。将包依赖关系建模为有向无环图（DAG），对其执行 DFS，在节点的 `finish` 时刻将其压入结果栈，最终逆序输出即得到合法的安装顺序。若 DFS 过程中遇到后向边，则说明存在循环依赖，应立即报错。

**2. 迷宫与路径搜索**
在 AI 游戏开发中，DFS 可用于生成随机迷宫（Randomized DFS / Recursive Backtracker 算法）：从起点随机选择未访问邻居推进，无路可走时回溯，直到所有格子被访问，生成完美迷宫（无环且全连通）的时间复杂度为 O(V)。由于 DFS 不保证找到最短路径，路径搜索中通常与 A* 配合使用，DFS 负责快速探索可行性。

**3. 编译器与语法分析**
编译器在构建抽象语法树（AST）后，利用 DFS 的**后序遍历**（先处理子节点再处理父节点）生成代码。例如，表达式 `(a + b) * c` 的后序遍历产生逆波兰表达式 `a b + c *`，直接对应栈式虚拟机（如 JVM 字节码）的执行顺序。

---

## 常见误区

**误区一：DFS 一定比 BFS 占用更多内存**
这是错误的。BFS 需要同时存储当前层的所有节点，最坏情况下（宽树）队列大小为 O(V)；DFS 的递归栈深度等于路径长度，在**窄而深**的图（如链状图）中最坏为 O(V)，但在**宽而浅**的图（如完全二叉树，深度为 log₂V）中仅需 O(log V) 空间，远优于 BFS 的 O(V/2) 队列空间。

**误区二：迭代 DFS 与递归 DFS 完全等价**
前文已提到访问顺序的差异，更重要的是：迭代版本在某些实现中会将节点在入栈时标记为已访问，而递归版本在出栈（处理）时标记。这会导致在含重复边的图中，迭代版本可能遗漏部分节点的正确 finish time，从而在拓扑排序场景中产生错误结果。正确的迭代 DFS 需要在 `pop()` 后再检查是否已访问。

**误区三：DFS 无法检测无向图中的环**
有人认为因为无向图中每条边都是双向的，DFS 会把父节点的边误判为后向边。正确做法是在递归时传入 `parent` 参数，仅当邻居已被访问**且该邻居不是当前节点的直接父节点**时，才判定为后向边（即环存在）。若忽略 `parent` 判断，对任意含边的无向图都会误报环。

---

## 知识关联

**依赖前置知识：**
- **图（数据结构）**：DFS 的操作对象是图的邻接表或邻接矩阵表示；稀疏图使用邻接表使 DFS 达到 O(V + E)，而邻接矩阵会使复杂度退化为 O(V²)。
- **栈**：DFS 的显式实现直接使用栈的 push/pop 操作；理解递归调用栈等价于理解系统为 DFS 隐式维护了一个栈。
- **广度优先搜索（BFS）**：BFS 使用队列（FIFO），在无权图中保证最短路径；DFS 使用栈（LIFO），不保证最短路径但内存开销在深度受限时更低。两者在访问所有可达节点的功能上等价，选择依据是问题的拓扑结构。

**通向后续概念：**
- **拓扑排序**：完全建立在 DFS 的 finish time 机制之上，Kahn 算法（基于入度）和 DFS 算法（基于 finish time 逆序）是拓扑排序的两种标准实现，DFS 版本代码更简洁。
- **回溯法**：回溯法可视为带有**剪枝（pruning）**条件的 DFS——在搜索状态空间树时，若当前路径已无法产生有效解则提前回溯，而非遍历所有叶子节点。N 皇后问题使用回溯 DFS 的实际搜索次数远小于全枚举的 N! 次。
