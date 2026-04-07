---
id: "red-black-tree"
concept: "红黑树"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 7
is_milestone: false
tags: ["树", "平衡"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 红黑树

## 概述

红黑树（Red-Black Tree）是一种自平衡二叉搜索树，由鲁道夫·拜尔（Rudolf Bayer）于1972年在论文 *Symmetric Binary B-Trees: Data Structure and Maintenance Algorithms*（Bayer, 1972）中首次提出，最初命名为"对称二叉B树"（Symmetric Binary B-Tree）。1978年，莱奥尼达斯·吉巴斯（Leonidas Guibas）与罗伯特·塞奇威克（Robert Sedgewick）在论文 *A Dichromatic Framework for Balanced Trees* 中正式引入红黑着色规则，将其重命名为红黑树，并建立了沿用至今的五条性质体系。

红黑树通过对每个节点附加一个颜色位（1 bit：红或黑），并强制维护五条颜色性质，确保树高严格满足 $h \leq 2 \cdot \log_2(n+1)$。在最坏情况下，查找、插入、删除的时间复杂度均为 $O(\log n)$。与 AVL 树相比，红黑树允许稍宽松的平衡条件——AVL 树要求任意节点左右子树高度差 $|h_L - h_R| \leq 1$，而红黑树仅保证最长路径不超过最短路径的两倍——换来的代价是插入最多2次旋转、删除最多3次旋转，远少于 AVL 树删除时可能发生的 $O(\log n)$ 次旋转。

红黑树在工业级系统中极为普遍：Linux 内核（自2.6版本起）用红黑树实现 CFS（完全公平调度器）中的进程调度队列和 `mm_struct` 虚拟内存区域管理；Java JDK 8 的 `HashMap` 在桶内链表长度超过8时转换为红黑树（`TreeMap`、`TreeSet` 同样如此）；C++ STL 的 `std::map` 和 `std::set` 底层实现也是红黑树。可参考《算法导论》第13章（Cormen et al., 2009, *Introduction to Algorithms*, 3rd ed., MIT Press）获得完整的形式化证明。

---

## 核心原理

### 五条红黑性质

红黑树必须严格满足以下五条性质，违反任何一条则该树不合法：

1. **节点着色**：每个节点是红色（RED）或黑色（BLACK）。
2. **根节点为黑**：根节点的颜色必须是黑色。
3. **叶子节点为黑**：所有 NIL 哨兵叶子节点（外部虚拟节点，不存储数据）为黑色。
4. **红色节点无相邻红子**：若节点为红色，则其两个子节点均为黑色（即树中不存在两个连续红节点）。
5. **黑高一致**：从任意节点出发，到达其所有后代 NIL 叶子节点的路径上，经过的黑色节点数量相同，该数量称为该节点的**黑高**（Black-Height，记作 $bh(x)$）。

由性质4和性质5可严格推导出：设整棵树的黑高为 $bh$，则树中内部节点数 $n$ 满足：

$$n \geq 2^{bh} - 1$$

因此树高 $h \leq 2 \cdot \log_2(n+1)$，保证了所有操作的 $O(\log n)$ 上界。

### 插入修复：旋转与重着色

新节点**默认涂为红色**，以避免破坏黑高（性质5）。插入后可能违反性质4（父节点也为红色），需根据叔父节点（Uncle，记作 $u$）的颜色分三种情况处理（以新节点 $z$、父节点 $p$、祖父节点 $g$、叔父节点 $u$ 命名）：

- **情况1：$u$ 为红色。** 将 $p$ 和 $u$ 改为黑色，$g$ 改为红色，然后将 $g$ 作为新的"问题节点"向上递归。此过程仅重着色，**不旋转**，但可能将问题传播至根（最坏 $O(\log n)$ 次重着色）。
- **情况2：$u$ 为黑色，$z$ 是"内侧"子节点（左右型 LR 或 右左型 RL）。** 对 $p$ 执行一次旋转（LR 情况左旋 $p$，RL 情况右旋 $p$），将其转化为情况3，此步执行**1次旋转**。
- **情况3：$u$ 为黑色，$z$ 是"外侧"子节点（左左型 LL 或 右右型 RR）。** 对 $g$ 执行一次旋转（LL 右旋 $g$，RR 左旋 $g$），并交换 $p$ 与 $g$ 的颜色。此步执行**1次旋转**，且操作完成后局部子树颜色合法，**不再向上传播**。

综合三种情况，插入操作**最多执行2次旋转**（情况2转情况3各一次），加上至多 $O(\log n)$ 次重着色。

### 删除修复：双黑节点处理

删除操作分两阶段：先按照二叉搜索树规则删除节点（用后继节点替换），再修复可能的颜色违规。若被删除节点为黑色，则其替代子节点会产生"**双黑**"（Double Black）问题，即该位置黑高缺少1。设双黑节点为 $x$，其兄弟节点为 $w$，修复分四种情况：

- **情况1：$w$ 为红色。** 对父节点旋转并交换 $w$ 与父节点颜色，将问题转化为情况2、3或4，执行**1次旋转**。
- **情况2：$w$ 为黑色，$w$ 的两个子节点均为黑色。** 将 $w$ 改为红色，将双黑上移至父节点，可能传播至根。**不旋转**。
- **情况3：$w$ 为黑色，$w$ 的"内侧"子节点为红色，"外侧"子节点为黑色。** 旋转 $w$ 并重着色，转化为情况4，执行**1次旋转**。
- **情况4：$w$ 为黑色，$w$ 的"外侧"子节点为红色。** 旋转父节点并重着色，双黑问题彻底消除，执行**1次旋转**。

删除操作最多执行**3次旋转**（情况1 + 情况3 + 情况4），重着色最多传播 $O(\log n)$ 次。这是红黑树相比 AVL 树在删除性能上的核心优势：AVL 树删除后需要沿路径逐级检查平衡因子，最坏旋转 $O(\log n)$ 次，而红黑树旋转次数有常数上界。

---

## 关键公式与算法

### 左旋操作（Left-Rotation）代码

左旋是红黑树调整的基本操作，时间复杂度 $O(1)$。以下为 Python 伪代码实现：

```python
class RBNode:
    def __init__(self, key):
        self.key = key
        self.color = 'RED'   # 新节点默认红色
        self.left = None
        self.right = None
        self.parent = None

def left_rotate(T, x):
    """
    对节点 x 执行左旋。
    前提：x.right 不为 NIL。
    效果：x 下沉为其右子 y 的左孩子，y 上升占据 x 原位置。
    """
    y = x.right           # y 是 x 的右子节点
    x.right = y.left      # y 的左子树变为 x 的右子树

    if y.left != T.NIL:
        y.left.parent = x

    y.parent = x.parent   # y 接管 x 的父节点位置
    if x.parent == T.NIL:
        T.root = y
    elif x == x.parent.left:
        x.parent.left = y
    else:
        x.parent.right = y

    y.left = x            # x 成为 y 的左子节点
    x.parent = y
```

右旋（`right_rotate`）与左旋完全对称，将上述代码中 `left/right` 互换即可。

### 黑高与树高关系

设红黑树的黑高（根节点的 $bh$）为 $k$，则：

- 树中内部节点数下界：$n \geq 2^k - 1$
- 树高上界：$h \leq 2k \leq 2\log_2(n+1)$

例如，当 $n = 10^6$（约100万节点）时，树高 $h \leq 2 \times \log_2(10^6 + 1) \approx 2 \times 19.93 \approx 39.86$，即查找操作**最多比较40次**即可定位任意节点。

---

## 实际应用

### Linux 内核 CFS 调度器

Linux 内核的完全公平调度器（CFS，Completely Fair Scheduler，自内核2.6.23版本引入）使用红黑树维护就绪队列，键值为每个进程的**虚拟运行时间**（`vruntime`，单位纳秒）。调度时选择 `vruntime` 最小的进程（即红黑树最左节点），时间复杂度 $O(\log n)$（$n$ 为就绪进程数）。内核源码位于 `kernel/sched/fair.c`，相关函数为 `__enqueue_entity()` 和 `__dequeue_entity()`。

### Java JDK 8 HashMap 的树化

Java 8 的 `HashMap` 在以下条件同时成立时，将桶内链表转换为红黑树（`TreeNode` 类，位于 `java.util.HashMap`）：
- 链表长度超过阈值 `TREEIFY_THRESHOLD = 8`；
- 哈希表总容量 `capacity >= MIN_TREEIFY_CAPACITY = 64`。

树化后单次 `get/put` 最坏时间复杂度从 $O(n)$（链表）降至 $O(\log n)$（红黑树），显著提升了哈希冲突严重时的性能。反向操作（树退化为链表）发生在节点数降至 `UNTREEIFY_THRESHOLD = 6` 时。

### C++ STL std::map 的底层实现

C++ 标准库中 `std::map<K,V>` 和 `std::set<K>` 均以红黑树为底层数据结构（GCC libstdc++ 实现于 `stl_tree.h`）。其 `insert()` 操作最坏 $O(\log n)$，而 `lower_bound()` 和 `upper_bound()` 等范围查询同样为 $O(\log n)$，这正是红黑树相比哈希表 `std::unordered_map` 的优势所在——哈希表不支持有序范围查询。

---

## 常见误区

### 误区1：红黑树比 AVL 树"更平衡"

恰恰相反。AVL 树的平衡条件更严格（高度差 $\leq 1$），树高上界约为 $1.44 \cdot \log_2(n)$，而红黑树树高上界为 $2 \cdot \log_2(n+1)$。红黑树的优势在于**写操作旋转次数少**（插入 $\leq 2$ 次，删除 $\leq 3$ 次），而 AVL 树的优势在于**读操作更快**（树更矮，平均查找路径更短）。在读多写少的场景下，AVL 树性能往往优于红黑树。

### 误区2：NIL 哨兵节点不重要，可以用 null 代替

NIL 哨兵节点是红黑树正确性的关键。性质3明确规定 NIL 节点为黑色，若直接用 `null` 且不统一处理，则在插入/删除修复代码中访问 `node.color` 时会出现空指针异常。标准实现（如《算法导论》伪代码）使用**单一共享 NIL 哨兵**（`T.nil`），所有叶子指针均指向该哨兵，节省空间的同时避免边界判断遗漏。

### 误区3：插入操作一定需要旋转

并不总是需要旋转。若插入路径上的叔父节点均为红色，则仅通过重着色（情况1）即可修复，整个插入过程**零旋转**。例如，向一棵只有根节点的红黑树插入一个新节点：新节点为红色，父节点（根）为黑色，不违反任何性质，无需任何修复操作。

### 误区4：红黑树与2-3-4树无关

红黑树本质上