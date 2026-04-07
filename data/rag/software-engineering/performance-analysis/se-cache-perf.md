# 缓存性能

## 概述

缓存性能（Cache Performance）描述程序运行时CPU多级缓存系统的命中效率、缺失代价与带宽利用率特征。现代x86-64处理器的缓存层级结构呈现出极为陡峭的延迟梯度：以Intel Core i9-12900K为例，L1数据缓存容量48KB、访问延迟约4个时钟周期；L2缓存1.25MB、延迟约12个周期；L3共享缓存30MB、延迟约40周期；主内存DRAM访问延迟则高达200~300个时钟周期（Drepper, 2007）。这意味着一次L1缓存命中与一次主内存访问的代价相差约60倍，而程序的实际吞吐量在很大程度上取决于访问落在哪一层。

缓存层级结构的理论基础可追溯至Maurice Wilkes在1965年发表的论文《Slave Memories and Dynamic Storage Allocation》，他首次系统描述了"存储层次"（Memory Hierarchy）的必要性，以解决处理器速度与存储器速度之间持续扩大的"存储墙"（Memory Wall）问题。Wulf和McKee（1995）正式提出"Memory Wall"术语，指出自1980年至1995年，CPU性能年增长率约55%，而DRAM访问速度年增长仅7%，预测两者差距将在2010年前扩大至1000倍量级。

在工业界实践中，Google对其数据中心服务的分析表明，L3缓存缺失（LLC Miss）是CPU利用率高而有效工作吞吐量低的首要原因之一（Kanev et al., 2015，ISCA 2015论文《Profiling a Warehouse-Scale Computer》）。使用`perf stat -e cache-misses,cache-references ./program`可直接量化程序的LLC命中率，当LLC缺失率超过5%时，通常表明内存访问模式存在系统性优化空间。

## 核心原理

### 缓存行与伪共享

CPU缓存的最小操作单位是**缓存行**（Cache Line）。在x86-64架构上，缓存行固定为**64字节**（ARM Cortex-A系列亦为64字节，部分POWER架构为128字节）。当程序读取内存地址`0x1000`处的1个字节时，CPU实际将`0x1000`到`0x103F`的连续64字节整块加载到L1缓存。这一机制带来两个重要推论：首先，紧邻的数据能够"搭便车"共享同一次内存访问；其次，若程序跨越缓存行边界访问两个独立字段，则每个字段都需触发独立的缓存行加载。

**伪共享**（False Sharing）是多核场景下最隐蔽的缓存性能杀手。设有两个计数器变量`counter_a`和`counter_b`，它们在内存中相邻存放，恰好落在同一条64字节缓存行内。当CPU核心0频繁写入`counter_a`、核心1频繁写入`counter_b`时，MESI缓存一致性协议（Modified-Exclusive-Shared-Invalid）会使该缓存行在两个核心之间反复经历"失效→重新加载→修改"的循环，即使两个变量在逻辑上完全独立。实测数据表明，伪共享可使多线程程序的可伸缩性从线性退化至接近串行（Drepper, 2007）。

解决方案是强制对齐至缓存行边界。C++17引入了`std::hardware_destructive_interference_size`常量（通常等于64），可用于填充结构体：

```cpp
struct alignas(std::hardware_destructive_interference_size) PaddedCounter {
    std::atomic<int64_t> value;
    // 填充至64字节，阻止与其他变量共享缓存行
};
```

### 数据局部性的两个维度

**时间局部性**（Temporal Locality）：近期访问过的内存位置在短时间内极可能再次被访问。循环内部的累加变量`sum`在整个循环执行期间会数百万次被读写，CPU将其长期保留在寄存器或L1缓存中，延迟接近零。编译器的循环不变量外提（Loop-Invariant Code Motion）优化本质上也是对时间局部性的利用。

**空间局部性**（Spatial Locality）：程序倾向于访问当前地址附近的内存。这一原理对数据结构选择有深刻影响。考虑按行优先（Row-Major）vs 列优先访问C语言中的`double a[1024][1024]`矩阵：

- **行优先遍历**（`a[i][j]`，`j`内层循环）：相邻访问地址间距为8字节，每加载一条64字节缓存行可服务8次访问，空间局部性充分。
- **列优先遍历**（`a[i][j]`，`i`内层循环）：相邻访问地址间距为`1024 × 8 = 8192`字节，每条缓存行仅被利用1次即被替换，产生大量**容量缺失**（Capacity Miss）。

以GCC 12在Intel i7-11700K上的实测数据为例，对同一1024×1024 double矩阵求行列累加，行优先版本耗时约3.2ms，列优先版本耗时约18.7ms，差距达5.8倍，仅因访问顺序不同。

### 三C缺失模型

Patterson和Hennessy在《Computer Organization and Design》（2017, 第5版）中将缓存缺失归纳为三类（"3C模型"）：

**强制缺失（Compulsory Miss / Cold Miss）**：数据首次被访问，缓存中必然不存在。无论缓存多大、替换策略如何，首次访问均产生此类缺失。预取（Prefetching）是唯一有效的缓解手段：`__builtin_prefetch(&array[i+16], 0, 3)` 告知CPU提前将未来访问的地址载入缓存，通常提前8~16个迭代发出预取指令以覆盖约200个周期的内存延迟。

**容量缺失（Capacity Miss）**：程序的工作集（Working Set）超过缓存容量，导致先前加载的数据在被再次访问前已被替换。对于L1数据缓存（通常32~64KB），工作集超过此阈值后性能急剧下降。分块（Cache Blocking / Tiling）技术通过将大型数据集分割为适合L1/L2缓存大小的子块来消除此类缺失。

**冲突缺失（Conflict Miss）**：组相联缓存（Set-Associative Cache）中，多个内存地址映射到同一个缓存组（Cache Set），超出组的路数（Associativity）后产生缺失，即使缓存整体并未占满。典型场景：步长为2的幂次（如4096字节）的数组访问，大量地址映射至同一组，导致频繁替换。调整数组行维度为非2的幂次（如在末尾添加填充列）可消除冲突缺失。

## 关键方法与公式

### 缓存命中率与平均内存访问时间

程序的**平均内存访问时间**（AMAT, Average Memory Access Time）由以下递归公式定义：

$$\text{AMAT} = t_{L1} + m_{L1} \cdot (t_{L2} + m_{L2} \cdot (t_{L3} + m_{L3} \cdot t_{MEM}))$$

其中 $t_{L1}$、$t_{L2}$、$t_{L3}$、$t_{MEM}$ 分别为各层命中时的访问延迟（单位：时钟周期），$m_{L1}$、$m_{L2}$、$m_{L3}$ 分别为各层的缺失率（Miss Rate，0到1之间）。

以具体数值代入：若 $t_{L1}=4$，$m_{L1}=0.05$，$t_{L2}=12$，$m_{L2}=0.3$，$t_{L3}=40$，$m_{L3}=0.5$，$t_{MEM}=250$，则：

$$\text{AMAT} = 4 + 0.05 \times (12 + 0.3 \times (40 + 0.5 \times 250))$$
$$= 4 + 0.05 \times (12 + 0.3 \times 165) = 4 + 0.05 \times 61.5 = 4 + 3.075 \approx 7.08 \text{ 周期}$$

若通过优化将 $m_{L1}$ 从0.05降至0.01，AMAT降为约4.6周期，吞吐量提升约35%。这一公式清晰表明：**L1缺失率的优化效益远大于L3缺失率的同等比例优化**，因为L1缺失会引发后续所有层级的访问代价累加。

### 分块矩阵乘法（Cache Blocking）

朴素的 $N \times N$ 矩阵乘法 $C = A \times B$，内层循环访问矩阵 $B$ 的一列时步长为 $N$，当 $N$ 较大（如 $N=1024$，矩阵大小8MB）时工作集远超L2缓存，产生大量容量缺失。**分块矩阵乘法**将计算分解为 $B_s \times B_s$ 的子块（$B_s$ 称为块大小，Block Size），选取 $B_s$ 使三个子块恰好适合L2缓存：

$$3 \times B_s^2 \times \text{sizeof(double)} \leq L2\text{容量}$$

若L2容量为256KB，则 $B_s \leq \sqrt{256 \times 1024 / (3 \times 8)} \approx 104$，实践中取 $B_s = 64$ 或 $B_s = 32$。实测对比（GCC -O3，Intel i7）：朴素1024×1024矩阵乘法耗时约5.2秒，分块版本（$B_s=64$）耗时约1.1秒，加速比约4.7倍。

## 实际应用

### 面向缓存的数据结构设计：AoS vs SoA

**数组结构体**（Array of Structs, AoS）与**结构体数组**（Struct of Arrays, SoA）是影响缓存性能的核心数据布局决策。

例如，游戏引擎中存储10000个粒子的位置和生命值：

```cpp
// AoS 布局：每个粒子的全部字段连续存放
struct Particle { float x, y, z; float health; };
Particle particles[10000];  // 粒子[0]的x,y,z,health连续，粒子[1]紧随其后

// SoA 布局：同类字段连续存放
struct ParticleSystem {
    float x[10000], y[10000], z[10000];
    float health[10000];
};
```

若物理更新循环**仅**更新位置`(x, y, z)`而不访问`health`，AoS布局中每条64字节缓存行包含4个粒子的`(x,y,z,health)`，但`health`字段占用的16字节是无效加载；SoA布局中`x`、`y`、`z`数组各自连续，缓存利用率达100%。SIMD指令（AVX2可同时处理8个float）在SoA布局下可直接向量化，AoS布局则需要昂贵的gather操作。

### 链表 vs 数组的缓存性能差异

标准`std::list`（双向链表）的每个节点通过`new`独立分配，节点在堆内存中分散分布，相邻节点地址差可能超过数千字节，空间局部性极差。对100万个整数进行顺序遍历：`std::vector`（连续内存）约耗时1.2ms，`std::list`约耗时15~20ms，差距源于后者每次节点跳转几乎必然触发缓存缺失。对缓存性能敏感的场景应优先使用`std::vector`、`std::deque`或基于内存池的链表（Pool-Allocated List），使节点在物理上连续存放。

### 硬件预取与软件预取

现代CPU内置了流式预取器（Stream Prefetcher），能自动检测步长规律并提前加载数据。步长为1个缓存行（64字节对齐的连续访问）的循环，硬件预取器可完全覆盖内存延迟，使性能接近L1缓存速度。然而，不规则访问模式（如哈希表查找、图的BFS遍历）无法被硬件预取器识别，需要手动插入软件预取指令：

```cpp
for (int i = 0; i < N; i++) {
    __builtin_prefetch(&data[next[i + 16]], 0, 1);  // 提前16步预取
    process(data[next[i]]);
}
```

提前步数的选择取决于内存延迟与循环体执行时间的比值