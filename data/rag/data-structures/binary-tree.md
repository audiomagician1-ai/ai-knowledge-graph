---
id: "binary-tree"
concept: "二叉树"
domain: "data-structures"
subdomain: "binary-tree"
subdomain_name: "二叉树"
difficulty: 2
is_milestone: false
tags: ["树", "数据结构", "递归"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Cormen et al., Introduction to Algorithms (CLRS), 4th ed."
  - type: "textbook"
    name: "Knuth, The Art of Computer Programming, Vol. 1"
scorer_version: "scorer-v2.0"
---
# 二叉树

## 定义与核心概念

二叉树（Binary Tree）是每个节点最多有**两个子节点**（左子、右子）的树形数据结构。形式化递归定义：二叉树要么是空树 ∅，要么是一个三元组 (L, root, R)，其中 L 和 R 是二叉树。

Knuth 在《The Art of Computer Programming》（Vol. 1, §2.3）中指出，二叉树与一般有序树存在本质区别：二叉树区分左右子树（即使只有一个子节点也有左右之分），而一般树不区分。

### 基本性质

```
设高度为 h 的二叉树：
  最少节点数：h + 1（退化链）
  最多节点数：2^(h+1) - 1（满二叉树）

设有 n 个节点的二叉树：
  最小高度：⌊log₂n⌋（完全二叉树）
  最大高度：n - 1（退化链）

关键计数：
  节点数 n、边数 e、叶节点数 n₀、度为2的节点数 n₂
  e = n - 1（树的基本性质）
  n₀ = n₂ + 1（二叉树特有性质）
```

## 二叉树的分类

| 类型 | 定义 | 节点数与高度关系 | 应用 |
|------|------|-----------------|------|
| **满二叉树** | 每层都满 | n = 2^(h+1)-1 | 理论分析 |
| **完全二叉树** | 除最后一层外全满，最后一层左对齐 | 2^h ≤ n ≤ 2^(h+1)-1 | 堆 |
| **平衡二叉树** | 左右子树高度差 ≤ 1 | h = O(log n) | AVL树 |
| **退化树** | 每个节点只有一个子节点 | h = n-1 | 链表的等价物 |
| **BST** | 左子树所有值 < 根 < 右子树所有值 | 平均 O(log n)，最坏 O(n) | 查找/排序 |

## 核心操作实现

### 节点定义与遍历

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# 三种DFS遍历
def preorder(root):    # 前序：根-左-右
    if not root: return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def inorder(root):     # 中序：左-根-右（BST → 有序序列）
    if not root: return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def postorder(root):   # 后序：左-右-根（适合删除/释放）
    if not root: return []
    return postorder(root.left) + postorder(root.right) + [root.val]

# BFS层序遍历
from collections import deque
def levelorder(root):
    if not root: return []
    result, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        result.append(node.val)
        if node.left: queue.append(node.left)
        if node.right: queue.append(node.right)
    return result
```

### 遍历的非递归实现

```python
# 中序遍历的迭代版本（Morris遍历为O(1)空间）
def inorder_iterative(root):
    result, stack = [], []
    current = root
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    return result
```

## 二叉搜索树（BST）

### 操作复杂度

| 操作 | 平均 | 最坏（退化） | 平衡BST |
|------|------|------------|---------|
| 查找 | O(log n) | O(n) | O(log n) |
| 插入 | O(log n) | O(n) | O(log n) |
| 删除 | O(log n) | O(n) | O(log n) |
| 最小/最大值 | O(log n) | O(n) | O(log n) |

### BST 删除的三种情况

```
1. 叶节点：直接删除
2. 一个子节点：用子节点替代
3. 两个子节点：
   找到中序后继（右子树的最小值）或中序前驱（左子树的最大值）
   用其值替换当前节点，然后删除该后继/前驱（转化为情况1/2）
```

## 平衡二叉树

### AVL 树（Adelson-Velsky & Landis, 1962）

最早的自平衡BST。平衡条件：每个节点的左右子树高度差（平衡因子）∈ {-1, 0, 1}。

**四种旋转**：

```
LL型（右旋）：左子树的左子树插入
    z               y
   / \            /     y   T4  →     x      z
 / \           / \    / x   T3       T1  T2  T3  T4
/ T1  T2

RR型（左旋）：右子树的右子树插入（镜像）
LR型（先左旋后右旋）：左子树的右子树插入
RL型（先右旋后左旋）：右子树的左子树插入
```

### 红黑树

CLRS（4th ed.）详述的平衡BST，通过颜色约束保证 h ≤ 2·log₂(n+1)：
1. 每个节点红色或黑色
2. 根节点黑色
3. 叶节点（NIL）黑色
4. 红色节点的子节点必须为黑色（无连续红色）
5. 从任一节点到其后代叶节点的路径上，黑色节点数相同

**实际应用**：Java TreeMap、C++ std::map、Linux CFS 调度器。

## Catalan 数与二叉树计数

n 个节点的不同二叉树结构数量 = 第 n 个 Catalan 数：

```
C_n = C(2n,n) / (n+1) = (2n)! / ((n+1)!·n!)

n=0: 1 (空树)
n=1: 1
n=2: 2
n=3: 5
n=4: 14
n=5: 42

渐近：C_n ~ 4^n / (n^(3/2)·√π)
```

## 参考文献

- Cormen, T.H. et al. (2022). *Introduction to Algorithms*, 4th ed. MIT Press. ISBN 978-0262046305
- Knuth, D.E. (1997). *The Art of Computer Programming, Vol. 1: Fundamental Algorithms*, 3rd ed. Addison-Wesley. ISBN 978-0201896831
- Adelson-Velsky, G.M. & Landis, E.M. (1962). "An algorithm for the organization of information," *Doklady Akademii Nauk SSSR*, 146(2), 263-266.

## 教学路径

**前置知识**：递归基础、基本数据结构（数组、链表）
**学习建议**：先用纸笔画出 7 节点的 BST 建树过程（按不同插入顺序），观察退化现象。再实现三种遍历（递归+迭代各一版）。最后手动执行 AVL 的四种旋转。LeetCode 推荐题：#94 中序遍历、#104 最大深度、#98 验证BST、#236 最近公共祖先。
**进阶方向**：B树/B+树（数据库索引）、Treap、跳表、线段树/树状数组。
