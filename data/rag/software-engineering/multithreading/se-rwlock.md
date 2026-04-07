# 读写锁

## 概述

读写锁（Read-Write Lock），又称共享-独占锁（Shared/Exclusive Lock），是一种专为**读多写少**工作负载设计的同步原语。其核心思想由 Courtois、Heymans 与 Parnas 三人于 1971 年在论文 *"Concurrent Control with 'Readers' and 'Writers'"*（Courtois et al., 1971, *Communications of the ACM*）中正式提出，该论文同时定义了"读者优先"和"写者优先"两种经典策略，奠定了此后五十年读写锁理论与实现的基础。

读写锁的三条核心并发规则精确且不可妥协：**第一，任意数量的读者线程可同时持有读锁（共享模式）；第二，写者线程持有写锁（独占模式）时，所有其他读者和写者必须阻塞；第三，写锁等待期间，是否允许新读者插队由具体的优先级策略决定。** 这三条规则共同构成了读写锁区别于互斥锁（Mutex）的全部语义差异——互斥锁无法区分读写意图，所有持有者均独占，而读写锁通过细粒度语义将读并发度从 1 提升至理论上的无限。

在工业实现层面，POSIX 标准于 POSIX.1-2001 中引入 `pthread_rwlock_t`，提供 `pthread_rwlock_rdlock`、`pthread_rwlock_wrlock`、`pthread_rwlock_unlock` 三个核心系统调用。Java 在 JDK 1.5（2004 年）通过 `java.util.concurrent.locks.ReentrantReadWriteLock` 将其纳入标准库，由 Doug Lea 设计实现。Linux 内核则提供了基于自旋的 `rwlock_t` 和基于信号量的 `rw_semaphore` 两种形态。

读写锁的性能收益并非无条件的。经验性的判断依据是：当读写操作比例（read-to-write ratio）超过约 **10:1**，且持有锁期间的临界区执行时间足够长（超过锁本身的元数据操作开销，通常在数十纳秒量级），才能观察到相对于互斥锁的显著吞吐量提升。若临界区极短（如仅更新一个整数），锁的开销本身可能反而使读写锁性能劣于简单的自旋互斥锁。

## 核心原理

### 读写状态兼容矩阵

读写锁的并发语义可以用一张二维兼容矩阵精确描述：

| 请求者 ↓ \ 持有者 → | 无持有者 | 读锁（N 个读者） | 写锁（1 个写者） |
|---|---|---|---|
| 读请求 | ✅ 立即授予 | ✅ 立即授予，计数 +1 | ❌ 阻塞直到写锁释放 |
| 写请求 | ✅ 立即授予 | ❌ 阻塞直到所有读锁释放 | ❌ 阻塞直到写锁释放 |

锁的内部状态可以用一个整数 $S$ 编码：$S = 0$ 表示无持有者；$S > 0$ 表示有 $S$ 个读者持有读锁；$S = -1$ 表示有一个写者持有写锁。读锁获取的原子操作语义为 $S \leftarrow S + 1$（仅当 $S \geq 0$ 时），写锁获取的原子操作语义为 $S \leftarrow -1$（仅当 $S = 0$ 时）。

在 `ReentrantReadWriteLock` 的具体实现中，Doug Lea 将 32 位 AQS（AbstractQueuedSynchronizer）状态字的**高 16 位**用于编码读者计数，**低 16 位**用于编码写者重入次数。因此单个 `ReentrantReadWriteLock` 的最大并发读者数为 $2^{16} - 1 = 65535$，写者最大重入深度同样为 65535。这一位域划分技巧使得读写状态的原子检测和更新可以用单次 CAS（Compare-And-Swap）操作完成。

### 写者饥饿问题与优先级策略

读写锁最核心的工程取舍是**写者饥饿（Writer Starvation）**问题。Courtois 等人（1971）在原始论文中已经指出，若采用读者优先（Readers-Preference）策略，持续不断的读者流会导致写者无限期等待；若采用写者优先（Writers-Preference）策略，持续不断的写者流则反过来让读者饥饿。

**读者优先策略**：当写者在等待时，新到的读者仍可立即获得读锁插入队列之前。Linux 内核 `rwlock_t`（`arch/x86/include/asm/spinlock.h`）采用此策略，其内部使用一个无符号整数，高位保留给写者请求，低 24 位为读者计数，读者获取锁仅需原子递增，写者则需等待低位清零。

**写者优先策略**：一旦有写者进入等待队列，所有后续读者也必须排队等待该写者之后。POSIX 标准允许实现选择任一策略（IEEE Std 1003.1，2017），glibc 的 `pthread_rwlock_t` 在 NPTL 实现中默认倾向于写者优先以避免写者饥饿。

**公平策略（FIFO）**：`ReentrantReadWriteLock` 在 `fair=true` 模式下基于 AQS 的 CLH 等待队列实现严格的 FIFO 顺序，读者和写者按到达顺序排队。公平模式下，若队列头部是一个写者，即使当前锁空闲也不允许新读者插队，写者等待时间上界由队列长度决定，但读吞吐量相应下降。

### 锁降级（Lock Downgrading）

读写锁支持一种称为**锁降级（Lock Downgrading）**的特殊操作：线程在持有写锁期间先获取读锁，然后释放写锁，最终以读锁持有者身份继续执行。锁降级保证了写者刚写入的数据在降级后仍然对自身可见，且不会被其他写者打断。`ReentrantReadWriteLock` 明确支持此操作，官方推荐的代码模式如下：

```java
ReentrantReadWriteLock rwl = new ReentrantReadWriteLock();
Lock readLock  = rwl.readLock();
Lock writeLock = rwl.writeLock();

writeLock.lock();
try {
    // 修改共享数据结构
    sharedData = computeNewValue();
    readLock.lock();   // 降级第一步：持有写锁期间获取读锁
} finally {
    writeLock.unlock(); // 降级第二步：释放写锁（此时仅持有读锁）
}
try {
    // 以读锁身份安全读取刚写入的数据
    use(sharedData);
} finally {
    readLock.unlock();
}
```

与锁降级对称的**锁升级（Lock Upgrading）**——即持有读锁时尝试获取写锁——在 `ReentrantReadWriteLock` 中**不被支持**，尝试升级将导致死锁：线程 A 持有读锁并等待写锁，而写锁必须等待所有读锁（包括 A 自己的读锁）释放，形成自我死锁。PostgreSQL 的 `LWLock`（轻量级锁，`src/backend/storage/lmgr/lwlock.c`）通过专门的 `LWLockUpdateMode` 接口支持读锁到写锁的升级，但要求升级操作失败时能够回退，实现代价较高。

## 关键方法与性能公式

### 吞吐量增益模型

设系统中读操作平均持续时间为 $T_r$，写操作平均持续时间为 $T_w$，单位时间内读操作到达率为 $\lambda_r$，写操作到达率为 $\lambda_w$，读写比 $\rho = \lambda_r / \lambda_w$。

在互斥锁模型下，有效并发度（Effective Concurrency）恒为 1。在读写锁（读者优先）模型下，若无写操作争用，读操作的有效并发度为正在运行的读者数量。根据 Little's Law，当 $\lambda_r T_r < 1$（系统稳定）时，平均同时运行的读者数量为：

$$\bar{N}_r = \lambda_r \cdot T_r$$

读写锁相对于互斥锁的吞吐量提升倍数（忽略锁元数据开销）近似为：

$$\text{Speedup} \approx \frac{\rho \cdot T_r + T_w}{\rho \cdot T_r / \bar{N}_r + T_w}$$

当 $\rho \gg 1$ 且 $\bar{N}_r \gg 1$ 时，此式趋近于 $\bar{N}_r$，即并发读者数即为加速比上限。这也解释了为何读写比低时读写锁的性能增益有限。

### StampedLock 的乐观读

Java 8 引入的 `StampedLock`（同样由 Doug Lea 设计）通过**乐观读（Optimistic Read）**进一步优化读写锁模型。乐观读不加锁，仅读取一个时间戳（stamp），操作完成后通过 `validate(stamp)` 验证期间是否有写者介入：

```java
StampedLock sl = new StampedLock();

long stamp = sl.tryOptimisticRead();  // 不加锁，获取 stamp
int x = point.x;                      // 读取数据（可能被并发写入）
int y = point.y;
if (!sl.validate(stamp)) {            // 验证 stamp 是否仍有效
    stamp = sl.readLock();            // 回退为悲观读锁
    try { x = point.x; y = point.y; }
    finally { sl.unlockRead(stamp); }
}
```

乐观读的性能优势在于完全避免了 CAS 操作（仅一次 volatile 读），在 CPU 缓存命中的场景下，乐观读的吞吐量可达悲观读锁的 **2～7 倍**（JEP 155 性能测试数据）。`StampedLock` 不支持重入，且其 stamp 机制要求读操作必须幂等（可以安全重试）。

## 实际应用

### 案例：Java 并发缓存实现

最典型的读写锁应用场景是缓存（Cache）——读操作（缓存查询）远多于写操作（缓存失效与更新）。以下是一个使用 `ReentrantReadWriteLock` 实现的线程安全缓存：

```java
public class ReadWriteCache<K, V> {
    private final Map<K, V> cache = new HashMap<>();
    private final ReentrantReadWriteLock rwl = new ReentrantReadWriteLock();

    public V get(K key) {
        rwl.readLock().lock();
        try {
            return cache.get(key);    // 多线程可并发执行
        } finally {
            rwl.readLock().unlock();
        }
    }

    public void put(K key, V value) {
        rwl.writeLock().lock();
        try {
            cache.put(key, value);    // 独占执行，阻塞所有读者
        } finally {
            rwl.writeLock().unlock();
        }
    }
}
```

例如，一个 HTTP 路由表（routing table）在服务启动后几乎只有读操作（每次请求分发），仅在热更新路由规则时才有写操作（每数分钟一次），读写比轻松超过 10000:1，此场景下读写锁能将路由查询的并发吞吐量从互斥锁的单线程等效提升至接近 CPU 核数倍。

### 案例：Linux 内核 `rw_semaphore`

Linux 内核的 `rw_semaphore`（读写信号量，定义于 `include/linux/rwsem.h`）用于保护内存映射（`mmap_lock`，即原 `mmap_sem`）等核心数据结构。内核的虚拟内存区域（VMA，`vm_area_struct`）链表在每次 `mmap`、`munmap`、`mprotect` 调用时需要写锁，而在缺页中断（page fault）处理中仅需读锁。由于缺页中断频率远高于内存映射修改频率，`rw_semaphore` 在此场景中显著降低了缺页处理的串行化开销（Torvalds, Linux Kernel Documentation, 2021）。

### 案例：数据库系统中的多粒度锁

关系数据库（如 PostgreSQL、MySQL InnoDB）使用分层读写锁实现多粒度锁（Multiple Granularity Locking, MGL）。表级别使用意向锁（Intention Lock），行级别使用读写锁（S 锁/共享锁