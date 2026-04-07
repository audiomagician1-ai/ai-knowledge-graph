# 并发数据结构

## 概述

并发数据结构（Concurrent Data Structures）是专为多线程环境设计的数据容器，其根本挑战在于：在多个线程同时读写的情况下，既保证数据的正确性（线程安全），又最大化并发吞吐量，避免因过度加锁导致的串行化瓶颈。Java 标准库 `java.util.concurrent`（JUC）包由 Doug Lea 主导设计，自 JDK 1.5（2004年，JSR-166）起正式引入，包含 `ConcurrentHashMap`、`ConcurrentLinkedQueue`、`ConcurrentSkipListMap` 等核心实现，是目前工业界使用最广泛的并发数据结构库。

并发数据结构的演化路径清晰可追溯：**第一代**依赖全局 `synchronized`（如 `Hashtable`、`Collections.synchronizedMap`），所有方法互斥，并发度为 1；**第二代**引入分段锁（Segment Lock），JDK 7 中 `ConcurrentHashMap` 默认 16 个 `Segment`，并发度提升至 16；**第三代**（JDK 8+）彻底转向 CAS 无锁操作与细粒度桶级锁，并发度上限等于数组桶数量（默认初始 16，最高可达 $2^{30}$）。这一演化背后是硬件的推动——现代多核 CPU 上，`synchronized` 的内核态切换开销在高竞争场景下比 CAS 自旋高出数十倍。

正确使用并发数据结构与手动 `HashMap + synchronized` 的性能差距十分显著：在 16 核机器、读多写少（读:写 = 9:1）场景下，`ConcurrentHashMap` 的吞吐量可达同步 `HashMap` 的 **8–12 倍**，因为 JDK 8 的读操作完全无锁（基于 `volatile` 读语义）（Lea, 2004）。

---

## 核心原理

### ConcurrentHashMap：桶级锁 + 无锁读 + 协同扩容

JDK 8 的 `ConcurrentHashMap` 底层使用 `Node<K,V>[]` 数组，每个数组槽（桶）独立加锁，锁粒度从 JDK 7 的 16 个 `Segment` 细化为 $n$ 个桶（$n$ 为数组长度）。核心设计要点如下：

**写操作**：通过 `synchronized(f)`（$f$ 为桶的头节点）对单个桶加锁，不同桶的写操作完全并行。首次插入空桶时，使用 CAS 直接写入，无需加锁，避免了不必要的锁竞争。

**读操作**：`Node.val` 与 `Node.next` 均用 `volatile` 修饰，读取时无需任何锁，直接利用 Java 内存模型的 `volatile` 可见性保证。这使读密集场景（如缓存查询）的吞吐量接近非线程安全的 `HashMap`。

**树化阈值**：当单个桶的链表长度超过 8 且数组总长度 $\geq 64$ 时，链表转为红黑树（`TreeBin`），最坏查找时间复杂度从 $O(n)$ 降至 $O(\log n)$。红黑树节点采用 `TreeBin` 而非直接 `TreeNode`，因为 `TreeBin` 内部维护了读写锁（通过状态位），允许多个并发读与单个写并存，进一步提升树节点上的读并发度。当链表长度缩减至 6 以下时，`TreeBin` 退化回链表，阈值差值（8 与 6 之差）是为了防止频繁树化/链表化的抖动。

**计数器设计**：`size()` 不使用全局锁，而是借鉴 `LongAdder`（Lea & 团队，JDK 8）的思想，将计数分散到 `CounterCell[]` 数组中。写入时，线程优先 CAS 更新 `baseCount`，失败则随机选一个 `CounterCell` 更新：

$$\text{size()} = \text{baseCount} + \sum_{i=0}^{m-1} \text{CounterCell}[i].\text{value}$$

其中 $m$ 为 `CounterCell` 数组的长度（2 的幂，最大为 CPU 核数）。这将多核 CAS 竞争从单点分散到多点，在 64 核机器上可将计数更新吞吐量提升约 40 倍（相比单个 `AtomicLong`）。

**协同扩容（Cooperative Transfer）**：触发扩容时，`transfer()` 方法将数组桶区间切分，每个参与线程认领一段（最小步长 `stride = Math.max((n >>> 3) / NCPU, 16)` 个桶），完成迁移的桶填入 `ForwardingNode`（hash 值为特殊标记 `MOVED = -1`）。其他线程在写入时检测到 `ForwardingNode`，自动调用 `helpTransfer()` 加入扩容协助，使扩容过程并行化，避免单线程扩容成为整体吞吐瓶颈。

### ConcurrentLinkedQueue：Michael-Scott 无锁队列

`ConcurrentLinkedQueue` 实现了 Michael & Scott 于 1996 年发表的无锁队列算法（MS Queue，发表于 *PODC 1996*，ACM）。其核心维护两个 `AtomicReference` 指针：`head`（指向哨兵节点）和 `tail`（指向或接近队尾节点）。

**入队（offer）**：

```
1. 读取当前 tail 节点 t
2. 读取 t.next（称为 q）
3. 若 q == null，CAS(t.next, null, newNode)：成功则再 CAS(tail, t, newNode)
4. 若 q != null，说明 tail 落后，先 CAS(tail, t, q) 再重试
```

这种"懒更新 tail"设计意味着 `tail` 可能落后真实队尾最多 1 个节点，减少了对 `tail` 本身的 CAS 竞争次数。整个入队操作是**无锁（lock-free）**而非**无等待（wait-free）**——某一线程的进展依赖于其他线程的 CAS 成功，但整体系统始终向前推进。

**ABA 问题**：`ConcurrentLinkedQueue` 通过 GC 回收机制天然规避了 ABA 问题（节点被 GC 前不会被复用），无需 `AtomicStampedReference`。但在非 GC 语言（如 C++）中，MS Queue 实现必须引入危险指针（Hazard Pointer）或版本计数来解决 ABA。

**性能特征**：在低竞争场景下，`ConcurrentLinkedQueue` 的吞吐量优于基于锁的 `LinkedBlockingQueue`；但在极高竞争下（数百线程同时入队），CAS 重试导致的 CPU 自旋可能使吞吐量低于带有背压机制的阻塞队列。

### ConcurrentSkipListMap：跳表的无锁实现

跳表（Skip List）由 William Pugh 于 1990 年在论文 *"Skip Lists: A Probabilistic Alternative to Balanced Trees"*（*Communications of the ACM*, 33(6)）中提出。跳表通过多层链表索引实现 $O(\log n)$ 的查找，期望层数为 $\log_{1/p} n$，其中概率参数 $p$ 通常取 $\frac{1}{4}$ 或 $\frac{1}{2}$。

`ConcurrentSkipListMap` 是 JDK 中唯一的排序并发 Map，适合需要有序遍历的场景（如范围查询）。其无锁实现的核心挑战是：如何在多线程下安全地插入和删除层级节点？

**逻辑删除（Logical Deletion）**：删除一个节点时，不直接修改链表，而是先将该节点的 `value` 字段 CAS 置为 `null`（标记为逻辑删除），再在后续操作中物理移除。这避免了并发删除与插入之间的竞争条件。

**节点层级概率**：每个新节点的层级由随机数决定，JDK 实现中：

$$P(\text{level} \geq k) = p^{k-1}, \quad p = 0.5$$

即第 $k$ 层的概率为 $2^{-(k-1)}$，最大层数硬编码为 62（对应最大容量约 $2^{62}$ 个元素）。

**范围查询优势**：`ConcurrentSkipListMap` 实现了 `NavigableMap` 接口，支持 `subMap()`、`headMap()`、`tailMap()` 等范围操作，其并发度在范围扫描场景下远优于 `ConcurrentHashMap`（后者不保证有序性）。

---

## 关键方法与公式

### CAS 原语与线性化

并发数据结构的正确性依赖**线性化（Linearizability）**：每个操作在其调用与返回之间的某个时间点表现得像原子操作（Herlihy & Wing, 1990，*Journal of the ACM*, 37(3)）。CAS 是实现线性化的基础原语：

$$\text{CAS}(\&\text{addr}, \text{expected}, \text{new}) = \begin{cases} \text{true, addr} \leftarrow \text{new} & \text{if addr} = \text{expected} \\ \text{false} & \text{otherwise} \end{cases}$$

CAS 的硬件实现（x86 的 `LOCK CMPXCHG` 指令）在缓存行层面保证原子性，开销约为 10–20 个 CPU 周期（无竞争情况下）。

### 负载因子与扩容触发

`ConcurrentHashMap` 在 `putVal` 中检查是否需要扩容：

$$\text{当 size} \geq \text{sizeCtl 时触发扩容}, \quad \text{sizeCtl} = \lfloor \text{capacity} \times 0.75 \rfloor$$

负载因子 0.75 是空间与时间的经典权衡——若改为 0.5 则内存浪费加倍，若改为 1.0 则哈希碰撞率大幅上升（在随机哈希下，负载因子为 1 时期望碰撞链长约为 $e^{-1} \cdot n \approx 0.37n$）。

### 阻塞队列的公平性与吞吐量权衡

`LinkedBlockingQueue` 使用两把锁（`putLock` 和 `takeLock`）分别控制入队与出队，允许生产者与消费者真正并行。其容量限制（默认 `Integer.MAX_VALUE`）通过 `AtomicInteger count` 追踪，入队后若 count 之前为 0 则唤醒消费者，出队后若 count 之前等于 capacity 则唤醒生产者。

---

## 实际应用

### 案例一：高并发缓存系统中的 ConcurrentHashMap

例如，在一个 QPS 达到 50 万的电商商品详情缓存服务中，使用 `ConcurrentHashMap` 作为本地一级缓存，初始容量设置为 `expectedSize / loadFactor + 1`（避免早期扩容），并发度无需手动设置（JDK 8 自动管理）。写入时使用 `putIfAbsent` 或 `computeIfAbsent`（后者对 key 的计算过程持有桶锁，避免重复计算），读取时的 `get()` 完全无锁，适合读写比 100:1 的缓存场景。

需要注意：`ConcurrentHashMap` 不允许 null 键或 null 值（`Hashtable` 同样禁止），这与 `HashMap` 不同。其原因在于：在并发环境下，`get(key) == null` 无法区分"键不存在"与"键对应值为 null"这两种语义，而 `HashMap` 可以通过 `containsKey` 二次检查（但 ConcurrentHashMap 做不到原子性的二次检查）。

### 案例二：生产者-消费者任务调度中的阻塞队列选型

在 Java 线程池（`ThreadPoolExecutor`）中，工作队列的选择直接影响任务调度行为：

- **`LinkedBlockingQueue`（无界）**：`newFixedThreadPool` 默认使用，任务无限堆积可能导致 OOM；
- **`ArrayBlockingQueue`（有界）**：使用单把锁保护读写，公平模式下按 FIFO 唤醒等待线程，但吞吐量低于双锁的 `LinkedBlockingQueue`；
- **`SynchronousQueue`**：`newCachedThreadPool` 使用，不存储任务，生产者与消费者必须同步握手，内部通过 `Transferer`（公平模式用队列，非公平模式用栈）实现；
- **`LinkedTransferQueue`（JDK 7）**：