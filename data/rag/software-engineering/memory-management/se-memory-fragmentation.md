---
id: "se-memory-fragmentation"
concept: "内存碎片化"
domain: "software-engineering"
subdomain: "memory-management"
subdomain_name: "内存管理"
difficulty: 3
is_milestone: false
tags: ["问题"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 内存碎片化

## 概述

内存碎片化（Memory Fragmentation）是指内存空间在经历反复分配与释放操作后，产生大量无法被有效利用的离散空闲块的现象。具体表现为：即使系统中空闲内存的总量足以满足某次分配请求，但由于这些空闲空间被已占用的内存块分隔成互不相邻的小片段，导致分配器无法找到一块足够大的连续区域来完成分配，最终引发分配失败或性能下降。

这一问题在20世纪60年代早期随着分时操作系统的兴起而被系统性研究。1969年，Donald Knuth 在其著作《计算机程序设计艺术》（TAOCP）第一卷中首次对内存碎片化问题进行了定量分析，提出了著名的**"50%规则"**：在使用首次适配（First Fit）策略的堆分配器中，约有50%的空闲块会因碎片化而无法被利用。

碎片化在长期运行的服务端程序（如数据库、Web服务器）中尤为致命。Redis 在实际部署中因碎片化导致的内存占用可比实际数据量高出30%至50%，而 Firefox 早期版本曾因严重的堆碎片化问题导致长时间运行后内存占用翻倍，这直接推动了 jemalloc 分配器的开发与集成。

---

## 核心原理

### 外部碎片与内部碎片的区别

**外部碎片（External Fragmentation）** 是指空闲内存存在于已分配块之间的间隙中，虽然总量充足却无法被整合利用。例如，堆上有三个大小分别为16B、8B、16B的空闲块交替分布，若请求分配32B，即使总空闲量为40B，三个块均无法单独满足该请求。

**内部碎片（Internal Fragmentation）** 则发生在已分配块内部。当分配器为了对齐（Alignment）或分箱（Binning）策略而将8字节请求向上取整为16字节时，多出的8字节虽已被"分配"给请求方，却不被实际使用。内部碎片的量化公式为：

$$F_{internal} = \sum_{i=1}^{n}(allocated_i - requested_i)$$

其中 $allocated_i$ 为第 $i$ 次分配实际占用的字节数，$requested_i$ 为用户请求的字节数。

### 碎片化的量化指标

衡量碎片化程度通常使用**碎片率（Fragmentation Ratio）**：

$$F = \frac{V_{total} - V_{used}}{V_{total}} \times 100\%$$

其中 $V_{total}$ 为分配器从操作系统申请的总内存，$V_{used}$ 为用户程序实际有效使用的内存。若某进程向OS申请了100MB但只有60MB存放有效数据，碎片率即为40%。Linux 内核通过 `/proc/[pid]/smaps` 提供的 `Rss`（实际驻留集大小）与应用层数据大小之差，可近似反映这一比率。

### 碎片化的成因机制

碎片化的根本诱因是**分配寿命的差异性**。若所有对象生命周期相同，则它们会同时释放，不会产生间隙。但现实程序中，短寿命的小对象（如临时字符串，通常16～64字节）与长寿命的大对象（如缓存条目，可达数MB）混合分配时，短寿命对象的释放会在大对象周围留下"空洞"，这些空洞往往太小以至于无法容纳下一个大对象请求。

---

## 实际应用

### 紧凑化（Compaction）

紧凑化是消除外部碎片最直接的手段：将所有已分配的内存块移动到地址空间的一端，从而在另一端合并出一大块连续空闲区。Java 的 G1 GC（Garbage-First Garbage Collector）在执行 Full GC 时会对堆进行紧凑化，但代价是需要暂停所有应用线程（Stop-The-World）并更新所有指向被移动对象的引用指针。C/C++ 中因存在原始指针，移动对象后指针会失效，因此传统 malloc 实现（如 glibc 的 ptmalloc2）**不进行紧凑化**，这是 C/C++ 程序碎片问题更难处理的根本原因。

### 分级分配策略（Size-Class Allocation）

jemalloc 和 tcmalloc 通过将请求大小映射到预定义的尺寸类（Size Classes）来同时控制内外部碎片。jemalloc 4.x 定义了约232个尺寸类，覆盖从8字节到4MB的请求，同一尺寸类的对象集中在固定大小的 slab（内存页集合）中分配，使得释放后的空位可以立即被同尺寸的下一次请求复用，将外部碎片几乎降为零。Redis 6.0 起默认使用 jemalloc，正是基于这一原因。

### 内存池（Memory Pool）

对于生命周期均一的对象集合（如 HTTP 请求处理期间创建的所有对象），使用内存池可以完全消除碎片：所有对象从同一连续块中顺序分配（Bump Pointer Allocation），请求处理结束后整块释放，无需逐一 `free`。Nginx 的 `ngx_pool_t` 正是此设计，每个请求拥有独立内存池，避免了反复 malloc/free 带来的碎片积累。

---

## 常见误区

**误区一：碎片率高意味着必须立即紧凑化**
碎片率高并不总是需要紧凑化的信号。若程序后续的分配请求尺寸较小，现有的碎片空洞完全能够满足需求，执行紧凑化反而浪费CPU时间。Redis 的 `activedefrag`（主动碎片整理）功能有两个触发阈值：`active-defrag-ignore-bytes 100mb`（碎片浪费超过100MB）**且** `active-defrag-enabled` 碎片率超过10%，两个条件必须同时满足才启动，避免无谓的整理操作。

**误区二：内部碎片可以通过频繁释放来消除**
内部碎片是分配粒度与请求大小不匹配造成的，与释放频率无关。一个请求了17字节但被分配了32字节的块，在整个生命周期内内部碎片始终是15字节，释放操作只是归还整个32字节，并不能"回收"那15字节的内部碎片——该浪费在分配时就已经发生，只有通过更精细的尺寸类划分（减小相邻尺寸类的间距）才能从根本上降低内部碎片。

**误区三：垃圾回收语言不存在碎片问题**
具有移动式GC（Moving GC）的语言（如Java、Go）理论上可以通过紧凑化消除外部碎片，但并非所有GC都执行紧凑化。Go 的 GC 使用非移动式标记清除算法，其运行时内存分配器同样采用尺寸类（67个大小类，最大32KB）来管理碎片，Go 程序在长期运行后同样会出现显著的碎片化问题。

---

## 知识关联

学习内存碎片化需要以**内存分配器**的工作机制为前提，具体包括：首次适配（First Fit）、最佳适配（Best Fit）、下次适配（Next Fit）三类基本分配算法如何生成不同程度的碎片——Best Fit 倾向于产生大量微小残余空洞，加剧外部碎片；Next Fit 则使碎片更均匀分布。边界标签技术（Boundary Tags）和空闲链表（Free List）的具体实现方式，直接决定了合并（Coalescing）操作能否及时将相邻空闲块合并为更大的可用块，从而对抗外部碎片的积累。理解这些底层机制是选择与调优生产环境内存分配器的关键基础。
