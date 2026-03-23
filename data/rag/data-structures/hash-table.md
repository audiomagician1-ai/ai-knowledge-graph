---
id: "hash-table"
concept: "哈希表"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 4
is_milestone: false
tags: ["映射"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 哈希表

## 概述

哈希表（Hash Table）是一种通过哈希函数将键（Key）映射到数组索引，从而实现平均 $O(1)$ 查找、插入和删除操作的数据结构。其核心思想最早可追溯至1953年 IBM 工程师 Hans Peter Luhn 的内部备忘录，他提出用"散列"方法加速信息检索。Donald Knuth 在《计算机程序设计艺术》第3卷（Sorting and Searching）中对哈希表进行了系统性的理论分析[Knuth, 1998]，将其奠定为计算机科学的基础数据结构之一。

哈希表之所以在 AI 工程中具有不可替代的地位，在于它直接支撑了词嵌入查找表、特征存储、去重集合等高频操作。Python 的 `dict` 和 `set`、Java 的 `HashMap`、C++ 的 `unordered_map` 均以哈希表为底层实现。在自然语言处理中，词汇表（vocabulary）通常存储为哈希表，GPT 系列模型的 tokenizer 在编解码时依赖哈希表将 token 字符串映射到整数 ID，单次查找耗时与词汇表大小无关。

## 核心原理

### 哈希函数与槽位映射

哈希函数 $h: U \rightarrow \{0, 1, \ldots, m-1\}$ 将全域键集 $U$ 压缩到大小为 $m$ 的数组（桶数组）中。一个理想的哈希函数应满足**均匀散列假设**：任意键等概率地映射到 $m$ 个槽位中的任意一个。实践中常用的除留余数法定义为：

$$h(k) = k \bmod m$$

为减少聚集现象，$m$ 通常取不接近2的幂次的质数，例如选 $m = 97$ 而非 $m = 128$。对于字符串键，MurmurHash3 和 xxHash 是现代工程中最常用的非加密哈希算法，xxHash 在单线程下吞吐量可超过 30 GB/s，远优于 MD5 的约 400 MB/s。

### 冲突解决：链地址法与开放寻址法

当两个不同的键 $k_1 \neq k_2$ 满足 $h(k_1) = h(k_2)$ 时，即发生**哈希冲突**。主流解决策略有两类：

**链地址法（Chaining）**：每个槽位存储一个链表，冲突元素追加到链表尾部。设哈希表中存储了 $n$ 个元素，$m$ 个槽位，**负载因子**定义为 $\alpha = n/m$。链地址法下，成功查找的平均探测次数为 $1 + \alpha/2$；当 $\alpha \leq 0.75$ 时性能维持在常数级别。Java 的 `HashMap` 采用此策略，并在链表长度超过8时自动将链表转换为红黑树，将最坏情况从 $O(n)$ 降为 $O(\log n)$（JDK 8 引入）。

**开放寻址法（Open Addressing）**：所有元素存储在数组本身，冲突时按探测序列寻找下一个空槽。线性探测的序列为 $h(k, i) = (h(k) + i) \bmod m$，但会引发**主聚集（Primary Clustering）**问题。双重哈希使用两个独立哈希函数：

$$h(k, i) = (h_1(k) + i \cdot h_2(k)) \bmod m$$

其中 $h_2(k)$ 必须与 $m$ 互质，可取 $h_2(k) = 1 + (k \bmod (m-1))$。Python 3.6+ 的 `dict` 采用紧凑型开放寻址实现，负载因子上限为 $2/3$，超出后触发扩容（resize）至原容量的约2倍。

### 动态扩容与摊还分析

当负载因子超过阈值时，哈希表必须执行**重新哈希（Rehashing）**：分配新的更大数组，将所有元素逐一重新插入。单次 rehash 的时间复杂度为 $O(n)$，但通过**摊还分析（Amortized Analysis）**可证明，若每次扩容将容量翻倍，则 $n$ 次插入操作的总代价为 $O(n)$，单次插入的摊还代价仍为 $O(1)$[Cormen et al., 2022]（即《算法导论》第4版第11章的结论）。这与动态数组（如 `std::vector`）的扩容策略完全一致，均采用几何级数增长以保证摊还效率。

## 实际应用

**AI 特征存储与 Embedding 查找**：在推荐系统中，用户ID和商品ID通常以哈希表存储对应的 Embedding 向量。Meta 的 DLRM（Deep Learning Recommendation Model）中，稀疏特征的 Embedding 表本质上是一个巨型哈希表，键为特征ID，值为低维稠密向量。TensorFlow 的 `tf.lookup.StaticHashTable` 和 PyTorch 的 `nn.EmbeddingBag` 均在底层依赖哈希映射处理稀疏 ID。

**NLP 词汇表与 Tokenizer**：Hugging Face Tokenizers 库中，`vocab` 字段是一个 Python `dict`（即哈希表），将 BPE 子词映射到整数 token ID。GPT-2 的词汇表大小为50,257，`tiktoken`（OpenAI 的 tokenizer 库）使用哈希表实现从字节序列到 token ID 的 $O(1)$ 查找，编码速度可达约 1 GB/s。

**去重与数据清洗**：在训练数据预处理中，使用哈希集合（Hash Set）对数十亿条文本进行精确去重。Common Crawl 数据清洗管道使用 MD5 或 SHA-1 哈希值作为文档指纹存入哈希集合，可在线性时间内完成 TB 级数据集的去重，内存占用远低于排序去重。

## 常见误区

**误区1：哈希表查找总是 $O(1)$**
哈希表的 $O(1)$ 是**平均情况**下的期望复杂度，而非最坏情况保证。当所有键均映射到同一槽位时（极端冲突），链地址法退化为链表，查找时间为 $O(n)$。在安全敏感场景中，攻击者可构造**哈希碰撞攻击**（Hash DoS），刻意提交大量冲突键导致服务器性能崩溃。Python 从 3.3 版本起引入哈希随机化（`PYTHONHASHSEED`），通过在进程启动时随机化字符串哈希种子来缓解此问题。

**误区2：哈希表与字典完全等价**
字典（Dictionary/Map）是一种抽象数据类型（ADT），只规定了键值对的插入、删除、查找接口，并不规定实现方式。哈希表是字典的一种具体实现，另一种常见实现是平衡二叉搜索树（如红黑树）。C++ 的 `std::map` 使用红黑树实现，保证 $O(\log n)$ 操作并维护键的有序性；而 `std::unordered_map` 使用哈希表实现，提供平均 $O(1)$ 操作但不保证顺序。混淆两者会导致在需要有序遍历时错误地使用哈希表。

**误区3：负载因子越低越好**
降低负载因子确实减少冲突，但代价是更高的内存浪费。若 $\alpha = 0.1$，则约90%的槽位为空，对缓存局部性（cache locality）也无益——开放寻址法在 $\alpha$ 适中（如0.5~0.7）时，由于数据在连续内存中分布，反而具有良好的 CPU 缓存命中率。Robin Hood Hashing 等变体在 $\alpha$ 接近0.9时仍可维持约2.5次平均探测，是高内存效率场景下的工程选择。

## 代码示例

以下是 Python 中用链地址法手动实现的最小化哈希表：

```python
class HashTable:
    def __init__(self, m=97):
        self.m = m  # 槽位数，选质数
        self.buckets = [[] for _ in range(m)]
    
    def _hash(self, key):
        return hash(key) % self.m  # Python内置hash已随机化
    
    def put(self, key, value):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[idx]):
            if k == key:
                self.buckets[idx][i] = (key, value)  # 更新已有键
                return
        self.buckets[idx].append((key, value))  # 新键追加到链表
    
    def get(self, key):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        raise KeyError(key)

ht = HashTable()
ht.put("transformer", 512)
print(ht.get("transformer"))  # 输出: 512
```

## 思考题

1. Python 的 `dict` 要求键必须是**可哈希的（hashable）**，即实现了 `__hash__` 和 `__eq__` 方法，而列表 `list` 不可哈希。请解释：为什么允许可变对象作为哈希表的键会破坏哈希表的正确性？如果一个对象在插入后其哈希值发生改变，会发生什么？

2. 在开放寻址法中，删除一个元素不能简单地将槽位置为空（None），而必须放置一个特殊的**墓碑标记（Tombstone）**。请分析：如果直接置空会导致哪种具体的查找错误？墓碑标记的积累又会带来什么新问题？

3. 布隆过滤器（Bloom Filter）可以看作哈希表的一种概率性变体，它牺牲了精确性换取极低的内存占用。请思考：布隆过滤器使用多个哈希函数的原因是什么？与标准哈希表相比，它在哪类 AI 工程场景（如大规模爬虫去重、近似最近邻检索）中更适用？
