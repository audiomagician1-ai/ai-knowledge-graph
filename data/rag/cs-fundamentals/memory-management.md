---
id: "memory-management"
concept: "内存管理"
domain: "ai-engineering"
subdomain: "cs-fundamentals"
subdomain_name: "计算机基础"
difficulty: 4
is_milestone: false
tags: ["paging", "segmentation", "virtual-memory"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "A"
quality_score: 82.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "academic"
    author: "Arpaci-Dusseau, R. H. & Arpaci-Dusseau, A. C."
    year: 2018
    title: "Operating Systems: Three Easy Pieces (v1.01)"
    url: "https://pages.cs.wisc.edu/~remzi/OSTEP/"
  - type: "academic"
    author: "Kwon, W., Li, Z., Zhuang, S., Sheng, Y., Zheng, L., Yu, C. H., Gonzalez, J., Zhang, H. & Stoica, I."
    year: 2023
    title: "Efficient Memory Management for Large Language Model Serving with PagedAttention"
    venue: "ACM SOSP 2023"
    url: "https://arxiv.org/abs/2309.06180"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---

# 内存管理

## 概述

内存管理是操作系统负责协调计算机内存资源分配、使用和回收的核心机制，具体包括：将物理内存划分为可寻址单元、在多个进程之间隔离地址空间、以及在物理内存不足时借助磁盘扩展可用容量。现代64位操作系统为每个进程提供高达128TB的虚拟地址空间（Linux x86-64默认配置），而实际物理内存通常只有几GB到几百GB，这一巨大差距正是内存管理技术存在的根本原因。

内存管理的概念最早在1960年代随分时系统的出现而成形。1961年，英国曼彻斯特大学的Atlas计算机首次实现了分页虚拟内存系统，奠定了此后60年内存管理技术的基础架构。1970年代Unix的普及使得分段+分页的混合模式成为主流，而1985年Intel 80386处理器引入的硬件保护模式则将内存隔离机制固化到CPU层面。2007年，Linux内核2.6.23版本引入了Completely Fair Scheduler（CFS）并同步优化了内存压缩策略；2023年，vLLM项目在ACM SOSP会议上发表PagedAttention论文（Kwon et al., 2023），将操作系统分页思想直接移植到大语言模型推理框架，标志着内存管理理论在AI工程领域迎来新的里程碑。

在AI工程领域，内存管理直接决定了大模型能否在有限硬件上运行。一个70亿参数的语言模型（如LLaMA-7B）以FP16精度加载需要约14GB内存；若采用量化（INT8约7GB，INT4约3.5GB）或分页注意力机制（PagedAttention），可在同等显存下将吞吐量提升2-4倍。理解内存管理原理是优化推理框架、避免OOM崩溃的必要前提。

> **参考文献**：Arpaci-Dusseau & Arpaci-Dusseau（2018）的《Operating Systems: Three Easy Pieces》对分页、分段及虚拟内存置换算法有系统性的教学描述，是本节理论部分的重要参考来源。

---

## 核心原理：分页（Paging）

分页将物理内存和虚拟内存均切割为固定大小的块，虚拟块称为**页**（Page），物理块称为**页框**（Frame）。Linux默认页大小为4KB，大页（HugePage）为2MB或1GB。CPU中的内存管理单元（MMU）通过**页表**完成虚拟地址到物理地址的转换。

地址转换的核心公式为：

$$\text{物理地址} = \text{页表}[\text{虚拟页号}] \times \text{页大小} + \text{页内偏移}$$

其中虚拟页号（VPN）由虚拟地址的高位比特决定，页内偏移由低位比特决定。例如，在4KB页大小下，一个48位虚拟地址的低12位为页内偏移，高36位用于索引多级页表。

多级页表（Linux使用4级：PGD→PUD→PMD→PTE）将单进程页表的内存开销从数GB压缩到实际使用量级别。TLB（Translation Lookaside Buffer）是页表的硬件缓存，命中时地址转换仅需1个时钟周期，未命中则需要数十至数百个周期遍历多级页表。

**例如**，在Intel Skylake架构上，L1 TLB有64个条目（4KB页）和32个条目（2MB大页），L2 TLB有1536个条目；一次TLB命中约1个时钟周期，TLB缺失后的页表遍历（Page Table Walk）需要约40-100个时钟周期，若涉及缺页中断并触发磁盘I/O则延迟可高达数百万个时钟周期。AI推理时频繁访问大张量会导致TLB抖动（Thrashing），因此vLLM等框架切换到2MB大页以降低TLB缺失率。

**思考问题**：如果一个AI推理服务同时处理128个并发请求，每个请求的KV Cache占用约256MB，那么所需的页表条目数量是多少？使用2MB大页相比4KB小页能节省多少页表内存开销？

---

## 核心原理：分段（Segmentation）

分段将程序的逻辑结构（代码段、数据段、堆、栈）映射为大小可变的内存区域，每个段由**段基址**（Base）和**段界限**（Limit）描述。x86架构下，段寄存器（CS、DS、SS、ES）存储段选择子，通过GDT（Global Descriptor Table）或LDT（Local Descriptor Table）查找段描述符后加上偏移得到线性地址，该线性地址再经分页转换为物理地址——这就是x86保护模式下"分段+分页"两级转换的完整流程。

线性地址的计算公式为：

$$\text{线性地址} = \text{段基址}(\text{段选择子}) + \text{段内偏移}$$

纯分段的缺点是产生**外碎片**（External Fragmentation）：假设内存中有三块空闲区域分别为100KB、200KB、150KB，总计450KB，但一个需要300KB连续空间的程序仍无法分配。这一问题在现代系统中通过分段+分页结合或直接使用纯分页来解决。

**例如**，Linux在x86-64模式下实际上已"弱化"了分段的作用：内核将所有段的基址设置为0，段界限设置为最大值，使得线性地址等同于虚拟地址，分段实质上退化为不做地址转换，全部隔离保护工作交由分页机制承担。这一设计简化了内核代码并提高了可移植性。

---

## 核心原理：虚拟内存与页面置换

虚拟内存允许进程使用超过物理内存总量的地址空间，操作系统通过**缺页中断**（Page Fault）按需将页面从磁盘（Swap区）加载到物理内存。页面置换算法决定当物理页框耗尽时换出哪一页：

- **LRU（最近最少使用，Least Recently Used）**：换出最长时间未访问的页，实际通过近似算法（如Clock算法）实现，因精确LRU需要维护时间戳链表开销过大。理论上LRU的缺页率接近OPT算法的1.2-1.5倍（在典型工作负载下）。
- **OPT（最优算法，Bélády's Algorithm）**：换出未来最长时间不会被访问的页，理论最优但无法预测未来，仅用于评估基准。1966年由László Bélády在IBM系统期刊上提出。
- **CLOCK算法**：每个页框维护1个访问位，指针扫描时若访问位为1则清零并跳过，为0则换出；近似LRU且开销为$O(1)$。
- **工作集模型（Working Set Model）**：由Denning于1968年提出，定义进程在时间窗口$\Delta$内访问的页面集合为工作集$W(t, \Delta)$，当物理内存无法容纳所有进程的工作集时，系统发生抖动（Thrashing）。

**缺页中断的处理开销**公式可近似为：

$$\text{有效内存访问时间} = (1 - p) \times t_{\text{mem}} + p \times t_{\text{fault}}$$

其中 $p$ 为缺页率，$t_{\text{mem}}$ 为正常内存访问时间（约100ns），$t_{\text{fault}}$ 为缺页处理时间（约10ms，含磁盘I/O）。若 $p = 0.001$（千次访问一次缺页），有效访问时间约为 $0.999 \times 100\text{ns} + 0.001 \times 10\text{ms} \approx 10.1\mu\text{s}$，是正常访问时间的100倍。

Linux内核使用基于CLOCK的二次机会（Second-Chance）LRU，并通过`/proc/sys/vm/swappiness`参数（默认值60，范围0-200）控制换出积极程度：值越大越倾向于使用Swap，值设为0时内核尽量避免换出匿名页（Anonymous Pages）。

---

## 核心原理：内存分配策略

**动态内存分配**在堆上进行，C语言`malloc`底层通常使用dlmalloc（Doug Lea于1987年设计）或jemalloc（Jason Evans于2006年为FreeBSD设计，后被Facebook广泛采用）。其核心数据结构是**空闲链表**，分配算法包括：

| 算法 | 描述 | 碎片特征 | 时间复杂度 |
|------|------|----------|------------|
| 首次适配（First Fit） | 找到第一个足够大的块 | 头部碎片积累 | $O(n)$ |
| 最佳适配（Best Fit） | 找最小满足的块 | 大量细小内碎片 | $O(n)$ |
| 伙伴系统（Buddy System） | 按2的幂次分配，合并相邻伙伴 | 最大内碎片50% | $O(\log n)$ |
| Slab分配器 | 为固定大小对象预分配缓存池 | 适合频繁申请释放的内核对象 | $O(1)$ |

伙伴系统的内存利用率可用公式估算：若请求大小为 $s$，实际分配为 $2^{\lceil \log_2 s \rceil}$，则内部碎片率最大为 $\frac{2^{\lceil \log_2 s \rceil} - s}{2^{\lceil \log_2 s \rceil}} < 50\%$。Linux内核的伙伴系统（`mm/page_alloc.c`）管理11个阶（Order 0至Order 10），最大连续分配为 $2^{10} \times 4\text{KB} = 4\text{MB}$。

Python的内存分配由CPython的`pymalloc`管理（自Python 2.3引入，Python 3.x持续优化）：小于512字节的对象使用预分配的内存池（256KB的Arena→4KB的Pool→固定大小的Block），大对象直接调用系统`malloc`。AI框架（PyTorch 2.x、TensorFlow 2.x）则在此之上实现了显存分配器，PyTorch的`caching_allocator`（位于`c10/cuda/CUDACachingAllocator.cpp`）会缓存已释放的显存块避免重复的`cudaMalloc`调用，因后者延迟高达数毫秒；PyTorch 2.0引入的`torch.cuda.memory.CUDAPluggableAllocator`接口允许用户自定义分配策略。

**思考问题**：为什么AI训练框架通常在进程启动时一次性申请大块显存（预分配池化策略），而不是按需调用`cudaMalloc`？这与操作系统Slab分配器的设计思想有何相似之处？

---

## 实际应用

### 大模型推理中的KV Cache内存管理

Transformer在推理时需为每个token存储Key-Value向量，序列长度增加时KV Cache线性增长。对于GPT-3（175B参数，96层，d_model=12288），在FP16精