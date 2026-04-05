---
id: "b-tree"
concept: "B树与B+树"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 7
is_milestone: false
tags: ["树", "数据库"]

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


# B树与B+树

## 概述

B树（B-Tree）由Rudolf Bayer和Edward McCreight于1972年在波音研究实验室（Boeing Scientific Research Laboratories）联合提出，论文题为《Organization and Maintenance of Large Ordered Indexes》，发表于*Acta Informatica*期刊。"B"的含义至今众说纷纭，Bayer本人从未明确解释，但学界普遍接受"Balanced"或"Boeing"两种说法。B树是一种自平衡的多路搜索树，每个节点可存储多个键值并拥有多个子节点，这与AVL树每个节点最多两个子节点的二叉限制截然不同。

B+树（B+ Tree）是对B树的工程性改进，由Douglas Comer于1979年在论文《The Ubiquitous B-Tree》（*ACM Computing Surveys*, 11(2):121-137）中系统整理和命名。其核心结构差异在于：所有实际数据记录只存储在叶节点，内部节点仅存储键值用于路由导航，且所有叶节点通过双向链表顺序相连。这一设计使B+树天然支持高效的范围查询，而纯B树完成同样操作必须执行代价较高的中序遍历。

B树族之所以统治数据库和文件系统索引领域长达半个世纪，根本原因在于磁盘I/O特性：磁盘读写以页（Page）为单位，一次读取通常为4KB或16KB，随机访问延迟约为10毫秒，而内存访问仅需100纳秒，差距约为10万倍。MySQL InnoDB引擎默认页大小为16KB，一个B+树节点恰好对应一个磁盘页，内部节点可存储约1170个键指针对，这意味着存储1亿条记录的B+树高度仅约3～4层，查找只需3～4次磁盘I/O，整个索引结构在工程上几乎达到最优。

---

## 核心原理

### B树的精确结构定义与节点约束

一棵**m阶B树**满足以下精确条件（以Knuth定义为准，见《The Art of Computer Programming》Vol.3, 1998）：

- 根节点至少有2个子节点（除非整棵树只有根节点，此时根即叶）
- 每个非根内部节点拥有 $\lceil m/2 \rceil$ 到 $m$ 个子节点
- 每个节点最多存储 $m-1$ 个键，最少存储 $\lceil m/2 \rceil - 1$ 个键
- 所有叶节点位于同一层（绝对平衡，高度一致）
- 每个含 $k$ 个键的内部节点恰好有 $k+1$ 个子节点

以**5阶B树**为例，每个非根节点最少存2个键，最多存4个键，拥有3至5个子节点。以**3阶B树**（又称2-3树）为例，每个节点存1或2个键，拥有2或3个子节点，是B树中阶数最低、结构最简洁的实例。

B树的高度上界可由以下公式确定：若树中共有 $N$ 个键，则树高 $h$ 满足：

$$h \leq \log_{\lceil m/2 \rceil} \frac{N+1}{2}$$

对于m=1001（千路B树），存储10亿条记录时，高度上界约为 $\log_{500}(5 \times 10^8) \approx 3.17$，即至多4层，验证了B树在超大数据集上的高效性。

### B树的插入与分裂机制

B树的插入操作始终在叶节点执行。若目标叶节点尚未满（键数 < m-1），直接插入并保持有序。若叶节点已满（含m-1个键），触发**分裂（Split）**：

1. 将节点中第 $\lceil m/2 \rceil$ 个键（中位键）**上推**至父节点
2. 原节点左半部分（前 $\lceil m/2 \rceil - 1$ 个键）保留为左子节点
3. 原节点右半部分（后 $m - \lceil m/2 \rceil$ 个键）形成新的右子节点
4. 若父节点因接收上推键而满溢，则继续向上递归分裂

**根节点分裂**是B树唯一的增高方式：当分裂传播至根节点时，创建一个新根节点，原根的中位键成为新根的唯一键，原根分裂的两半成为新根的左右子节点，树高加1。这一机制保证了所有叶节点始终处于相同深度。

以5阶B树插入序列 [10, 20, 5, 6, 12, 30, 7, 17] 为例：当第一个节点被插满4个键后，下一次插入将触发分裂，中位键上推至新创建的根节点，整个过程演示了B树"从叶向根生长"的独特特性。

### B+树与B树的结构差异对比

B+树在B树基础上引入两项关键工程改进：

**改进一：内部节点不存数据，仅存键（Key）和子节点指针**。这意味着相同的16KB页面，B树内部节点若每条记录占100字节，只能存约160条键值；而B+树内部节点仅存8字节整型键+6字节指针=14字节，同样页面可存约1170个指针，扇出（Fan-out）提升约7倍，树高相应降低。

**改进二：叶节点通过双向链表顺序链接**。所有叶节点按键值从小到大用双向链表串联，使得范围查询 `WHERE age BETWEEN 20 AND 30` 只需找到第一个满足条件的叶节点，然后沿链表顺序扫描，无需回溯父节点，时间复杂度为 $O(\log N + k)$，其中 $k$ 为范围内记录数。

| 特性 | B树 | B+树 |
|------|-----|------|
| 数据存储位置 | 所有节点均可存数据 | 仅叶节点存完整数据 |
| 内部节点容量 | 受数据大小限制，扇出低 | 仅存键+指针，扇出极大 |
| 叶节点连接方式 | 无链表结构 | 双向链表顺序连接 |
| 范围查询效率 | 需中序遍历，$O(N)$ | 链表顺序扫描，$O(\log N + k)$ |
| 单点查询 | 可能在内部节点命中，最优 $O(1)$ | 必须到达叶节点，固定 $O(\log N)$ |
| 全表扫描 | 需遍历所有节点 | 仅遍历叶节点链表即可 |

### 删除操作与借键/合并机制

B+树删除叶节点中的键时，若删除后该节点键数低于 $\lceil m/2 \rceil - 1$（即下溢），触发**再平衡（Rebalance）**：

- **借键（Borrow/Rotation）**：优先检查左兄弟或右兄弟节点。若左兄弟键数 > $\lceil m/2 \rceil - 1$，则将左兄弟最大键经父节点"旋转"至当前节点（父节点的分隔键降至当前节点，左兄弟最大键升至父节点），这与AVL树的单旋/双旋在思路上有相似之处，但操作对象是键值而非节点拓扑。

- **合并（Merge）**：若左右兄弟均只有最少键数，则将当前节点与一个兄弟节点合并，同时将父节点中对应的分隔键删除并下沉至合并节点（B+树中因叶节点存完整数据，分隔键直接删除即可）。合并使父节点键数减少1，可能引发向上级联的合并，最终若根节点键数降为0，则删除根节点，树高减少1。

---

## 关键公式与性能分析

### 树高与I/O次数计算

设B+树阶数为 $m$，叶节点每页可存 $l$ 条完整记录，总记录数为 $N$，则：

$$h = \lceil \log_m \lceil N / l \rceil \rceil + 1$$

以MySQL InnoDB实际参数代入：内部节点页16KB，每条索引项14字节（8字节BigInt主键 + 6字节页指针），$m \approx 16384 / 14 \approx 1170$；叶节点存完整行，假设每行1KB，$l = 16$；总记录数 $N = 10^8$：

$$h = \lceil \log_{1170} \lceil 10^8 / 16 \rceil \rceil + 1 = \lceil \log_{1170}(6.25 \times 10^6) \rceil + 1 = \lceil 2.08 \rceil + 1 = 3$$

即高度为3，查找任意记录只需3次磁盘I/O，其中根节点页通常常驻内存，实际只需2次物理I/O。

### Python代码示意：B树节点结构

```python
class BTreeNode:
    def __init__(self, leaf=False):
        self.keys = []          # 存储键值列表，最多 m-1 个
        self.children = []      # 存储子节点指针，最多 m 个
        self.leaf = leaf        # 是否为叶节点

class BTree:
    def __init__(self, t):
        """
        t: 最小度数（minimum degree），节点键数范围 [t-1, 2t-1]
        对应 m 阶 B树中 m = 2t，即 Knuth 定义的阶数
        """
        self.root = BTreeNode(leaf=True)
        self.t = t  # t=2 对应3阶B树（2-3树），t=500 对应千路B树

    def search(self, node, key):
        """在以node为根的子树中搜索key，返回(节点, 索引)或None"""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)  # 在内部节点命中（B树特有）
        if node.leaf:
            return None       # 未找到
        return self.search(node.children[i], key)  # 递归进入子树
```

上述 `search` 方法体现了B树与B+树的本质差异：B树在内部节点即可命中返回（第8行），而B+树的 `search` 必须始终递归至叶节点层，内部节点只做路由。

---

## 实际应用

### MySQL InnoDB中的B+树索引实现

MySQL InnoDB存储引擎使用B+树实现所有索引，包括聚簇索引（Clustered Index）和二级索引（Secondary Index）。

**聚簇索引**：以主键为键，叶节点直接存储完整行数据（即数据与索引合一）。InnoDB规定每张表必须有主键，若未显式定义，引擎自动创建隐藏的6字节ROWID作为主键。因此，InnoDB表的物理存储顺序与主键B+树的叶节点顺序完全一致，主键范围查询可触发顺序磁盘读取，性能极佳。

**二级索引**：以非主键列为键，叶节点存储的不是完整行，而是该行的主键值。查询时先通过二级索引B+树找到主键，再通过聚簇索引B+树找到完整行，这一过程称为**回表（Index Lookup Back to Clustered Index）**。若查询列均在二级索引中，则无需回表，即**覆盖索引（Covering Index）**优化，例如 `SELECT name FROM users WHERE age = 25` 若建有 `(age, name)` 联合索引，则无需回表。

### PostgreSQL与MongoDB的B树差异

PostgreSQL同样使用B树索引（其实现更接近于纯B+树变体），但支持对几乎所有数据类型建立B树索引，包括文本的前缀匹配。PostgreSQL的B树实现（见源码 `src/backend/access/nbtree/`）在并发控制上采用**链接技术（Lehman-Yao B-link Tree, 1981）**，每个节点增加一个"右链接指针"指向右兄弟，使得并发读取无需加锁，显著提升高并发场景性能。

MongoDB 3.2之前使用自研的B树变体，3.2版本起将默认存储引擎切换为WiredTiger，其索引结构同样基于B+树，并在磁盘上以Snappy压缩存储，实测压缩率约为2:1至5:1。

### 文件系统中的应用：HFS+与NTFS

Apple HFS+文件系统（1998年随Mac OS 8.1引入）使用B树存储目录结构，每个目录