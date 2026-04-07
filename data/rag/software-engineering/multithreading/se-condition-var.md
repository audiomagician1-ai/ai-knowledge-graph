---
id: "se-condition-var"
concept: "条件变量"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 2
is_milestone: false
tags: ["同步"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 条件变量

## 概述

条件变量（Condition Variable）是多线程编程中用于线程间同步的一种机制，它允许一个线程在某个条件不满足时**挂起等待**，并在另一个线程改变该条件后**通知**它继续执行。与互斥锁（Mutex）只能解决互斥访问问题不同，条件变量专门解决"等待某件事情发生"的协调问题。POSIX标准于1995年将条件变量正式纳入 `pthread` 库，C++11标准则将其封装为 `std::condition_variable`。

条件变量的设计来源于1974年C.A.R. Hoare提出的监视器（Monitor）理论模型。在Monitor模型中，条件变量就是线程在监视器内部等待特定条件成立的队列机制。Java中的 `Object.wait()` / `Object.notify()` 和C++中的 `std::condition_variable::wait()` / `notify_one()` 都是这一理论的具体实现。

条件变量之所以不可或缺，是因为仅靠互斥锁无法高效实现"等待某一状态"的语义。若线程持续轮询（busy-waiting）判断条件是否满足，会白白消耗CPU时间片；而条件变量允许线程将自己**原子性地释放锁并进入睡眠**，直到被唤醒后重新竞争锁，这是其根本价值。

---

## 核心原理

### Wait 操作的原子性

调用 `wait()` 时，条件变量执行的操作并非两步，而是**一个原子动作**：释放互斥锁 + 将当前线程加入等待队列。这种原子性至关重要。若"释放锁"和"进入等待"之间存在任何间隙，另一个线程可能在此间隙中改变条件并调用 `notify()`，导致通知丢失，当前线程永远沉睡。在C++中，其签名为：

```cpp
void wait(std::unique_lock<std::mutex>& lock,
          Predicate pred);  // pred 为条件谓词
```

`wait` 内部等价于：
```
while (!pred()) {
    unlock(mutex);
    block_this_thread();
    lock(mutex);
}
```

线程被唤醒后，`wait()` 会**重新获取互斥锁**，确保线程安全地检查条件并操作共享数据。

### Notify 的两种语义

条件变量提供两种通知方式，其行为差异直接影响性能与正确性：

- **`notify_one()`**：从等待队列中唤醒**恰好一个**等待线程。适用于多个等待线程可互换、条件满足时只需一个线程处理的场景，例如生产者每次放入一个任务时使用 `notify_one()`。
- **`notify_all()`**：唤醒**所有**等待线程，它们依次竞争互斥锁。适用于条件改变后多个线程都需要重新检查的场景，例如广播"配置已更新"。

滥用 `notify_all()` 会造成**惊群效应（Thundering Herd）**：100个线程同时被唤醒，但只有1个线程能成功获取锁并满足条件，其余99个线程再次回到等待状态，产生大量无效的上下文切换。

### 虚假唤醒（Spurious Wakeup）

虚假唤醒是指线程在**没有任何 `notify` 调用**的情况下从 `wait()` 返回。这并非Bug，而是条件变量在Linux内核（基于 `futex` 实现）和部分操作系统中的已知行为——内核在处理信号或优化调度时可能意外唤醒等待线程。

POSIX标准明确指出："使用条件变量时，应始终在循环中检查条件。"正因如此，永远不应这样写：

```cpp
// 错误写法：仅用 if 检查条件
mtx.lock();
if (queue.empty()) cv.wait(lk);  // 虚假唤醒后直接往下执行！
process(queue.front());
```

而应将条件检查置于 `while` 循环，或使用带谓词的 `wait` 重载，因为后者内部已封装了 `while` 循环。

---

## 实际应用

### 生产者-消费者模型

条件变量最经典的应用是有界缓冲区（Bounded Buffer）的生产者-消费者问题。该模型需要**两个条件变量**：

```cpp
std::mutex mtx;
std::condition_variable cv_not_full;   // 缓冲区不满：生产者等待此条件
std::condition_variable cv_not_empty;  // 缓冲区不空：消费者等待此条件
std::queue<int> buffer;
const int MAX_SIZE = 10;

// 生产者
void producer(int item) {
    std::unique_lock<std::mutex> lk(mtx);
    cv_not_full.wait(lk, []{ return buffer.size() < MAX_SIZE; });
    buffer.push(item);
    cv_not_empty.notify_one();  // 通知消费者缓冲区有数据
}

// 消费者
int consumer() {
    std::unique_lock<std::mutex> lk(mtx);
    cv_not_empty.wait(lk, []{ return !buffer.empty(); });
    int item = buffer.front(); buffer.pop();
    cv_not_full.notify_one();   // 通知生产者缓冲区有空位
    return item;
}
```

只用一个条件变量也能实现，但生产者和消费者都调用 `notify_all()` 时会互相唤醒对方，产生不必要的竞争，因此拆分为两个更高效。

### Java中的 await/signal

Java的 `ReentrantLock` 配合 `Condition` 接口实现相同语义：`condition.await()` 对应 `wait()`，`condition.signal()` 对应 `notify_one()`，`condition.signalAll()` 对应 `notify_all()`。`ArrayBlockingQueue` 内部正是通过两个 `Condition` 对象（`notEmpty` 和 `notFull`）实现有界阻塞队列的。

---

## 常见误区

### 误区一：不持有锁就调用 notify

有些初学者认为 `notify_one()` 不需要在持有互斥锁的情况下调用，因为它"只是发通知"。实际上，在锁外调用 `notify` 会引发竞态条件：等待线程可能在检查条件（锁内）和调用 `wait()`（原子释放锁）之间被通知，导致通知丢失。POSIX建议在持有锁时调用 `signal/broadcast`，虽然某些实现允许锁外调用，但为了可移植性和正确性，应始终在锁内 `notify`。

### 误区二：用条件变量替代信号量做计数

条件变量本身**不存储状态**——如果没有线程在等待时调用了 `notify_one()`，这次通知会**永久丢失**。因此不能用条件变量来计数"发生了多少次事件"。若需要记录事件次数，应使用信号量（`std::counting_semaphore`，C++20引入）而非条件变量。

### 误区三：认为虚假唤醒极少见可以忽略

在实际的多核Linux服务器上，高并发场景下虚假唤醒并非罕见。2013年Linux内核社区的邮件列表中有记录表明，在特定 `futex` 操作路径下虚假唤醒率可达数次/秒。忽略虚假唤醒的代码在压测时可能出现数据损坏或崩溃，而问题极难复现。

---

## 知识关联

学习条件变量需要先掌握**互斥锁（Mutex）**的基本用法，因为条件变量必须与互斥锁配合使用，`wait()` 操作依赖 `std::unique_lock` 的可解锁特性，而 `std::lock_guard` 因不支持中途解锁而无法与条件变量配合。

条件变量是实现**线程安全队列**、**线程池任务分发**、**读写锁**等高级并发结构的基础构件。理解生产者-消费者模型后，可进一步学习基于条件变量实现的 `std::future`/`std::promise` 机制——`promise::set_value()` 内部正是通过条件变量的 `notify_all()` 唤醒所有等待该 `future` 的线程。