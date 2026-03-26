---
id: "se-coroutine"
concept: "协程"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 3
is_milestone: false
tags: ["异步"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 协程

## 概述

协程（Coroutine）是一种可以在执行过程中主动暂停（suspend）并在稍后恢复（resume）执行的函数。与普通函数"调用→执行→返回"的单次生命周期不同，协程可以多次挂起和恢复，且每次恢复时能从上次挂起的精确位置继续执行，本地变量状态完整保留。协程由 Melvin Conway 于 1963 年在其汇编语言编译器论文中首次提出并命名，距今已有超过六十年的历史。

协程的核心特征是**协作式调度**（Cooperative Scheduling）：协程主动放弃控制权，而非由操作系统强制抢占。这与线程的抢占式调度形成鲜明对比。一个线程可以承载成千上万个协程，而创建一百万个协程的内存开销通常只有几 GB（每个协程栈帧仅需几百字节），远低于线程（每个线程默认栈通常为 1～8 MB）。

协程之所以重要，是因为它解决了异步 I/O 编程中"回调地狱"（Callback Hell）的可读性问题。传统回调嵌套三到五层后代码几乎无法维护，而协程允许开发者用**顺序书写**的代码表达异步逻辑，编译器或运行时负责将其转换为状态机。Python 3.5 引入 `async/await` 语法、C++20 将协程纳入标准，都印证了协程已成为现代高并发编程的基础设施。

---

## 核心原理

### 暂停与恢复机制：挂起点与帧保存

当协程执行到挂起点（C++20 中为 `co_await`，Python 中为 `await`）时，运行时会将当前的**协程帧**（Coroutine Frame）保存到堆上——包括所有局部变量、当前执行位置（PC 指针）以及挂起前的中间计算结果。控制权随即返回给调用者或事件循环。当外部条件满足（例如 I/O 完成）后，事件循环重新调用协程的 `resume()` 方法，协程从保存的帧中恢复状态继续执行。

C++20 协程要求实现者提供 `promise_type`，其中 `initial_suspend()`、`final_suspend()` 和 `yield_value()` 三个方法控制协程的生命周期节点。一个最小可运行的 C++20 生成器协程大约需要 50 行样板代码，这也是 C++20 协程被认为"无栈协程、有架构负担"的原因。

### 有栈协程与无栈协程

协程分为两大类：**有栈协程**（Stackful Coroutine）和**无栈协程**（Stackless Coroutine）。

- **有栈协程**（也称 Fiber/绿色线程）为每个协程分配独立的调用栈，通常大小为 4 KB～1 MB 可动态增长。`ucontext_t`（POSIX）、Windows 的 `Fiber` API、Go 的 goroutine 均属此类。有栈协程可以在任意调用深度挂起，不要求语言层面的特殊标注。
- **无栈协程**（C++20、Python asyncio、Kotlin）不分配独立栈，挂起时只保存当前函数的局部变量帧，因此内存开销极小。代价是**只能在协程函数本身挂起**，不能在普通被调函数内部挂起，这就是为什么 Python 中调用 `async` 函数必须加 `await`，否则得到的是协程对象而非执行结果。

### async/await 的状态机变换

编译器处理 `async/await` 时，会将整个协程函数变换为一个**有限状态机**（FSM）。以下面的 Python 代码为例：

```python
async def fetch_data():
    data = await read_socket()   # 挂起点 0
    result = await process(data) # 挂起点 1
    return result
```

编译器将其转化为包含状态 `{0: 初始, 1: 等待read_socket, 2: 等待process, 3: 完成}` 的状态机对象，`__next__()` / `send()` 方法驱动状态迁移。每个挂起点之间的代码段成为一个状态的处理逻辑，`data` 和 `result` 被提升为状态机对象的成员变量以跨越挂起点存活。

### Future/Promise 与协程的协作

协程通常与 Future/Promise 配合工作：`await some_future` 的语义是"如果 future 尚未完成，挂起当前协程并将 resume 回调注册到 future 的完成回调链上；如果已完成，直接取出值继续执行"。C++20 中这一行为由 `awaitable` 对象的 `await_ready()`、`await_suspend()` 和 `await_resume()` 三个方法精确定义。`await_ready()` 返回 `true` 时协程不会真正挂起，零开销通过。

---

## 实际应用

**网络服务器高并发**：Python 的 `aiohttp` 框架基于 `asyncio` 事件循环，使用协程处理 HTTP 请求。单进程配合协程可轻松达到每秒数万请求（QPS），而传统的每连接一线程模型在 10,000 并发连接时会因线程切换开销崩溃。核心代码形如：

```python
async def handle(request):
    result = await db.query("SELECT ...")  # 不阻塞事件循环
    return web.Response(text=result)
```

**C++20 生成器（Generator）**：协程天然适合实现懒序列。用 `co_yield` 关键字每次产出一个值，调用方按需拉取，无需一次性将全部数据加载进内存。处理 TB 级日志文件时，协程生成器可将内存占用从 GB 级降至 KB 级。

**游戏引擎中的行为树**：Unity 的 `IEnumerator` / `yield return` 协程（有栈协程变体）被广泛用于描述 NPC 行为序列，如"移动到位置 A → 等待 2 秒 → 播放动画"，这种顺序逻辑比回调或状态机更直观，且不需要额外线程。

---

## 常见误区

**误区一：协程等于多线程，可以利用多核**。协程本身是单线程的协作调度，Python 的 `asyncio` 协程在同一个线程的事件循环中运行，无法绕过 GIL 利用多核 CPU 进行 CPU 密集型并行计算。协程擅长的是 **I/O 密集型**并发（等待网络、磁盘时释放 CPU），CPU 密集任务仍需多进程或多线程。

**误区二：`await` 一定会让协程挂起暂停**。如前所述，若 `await` 的 awaitable 对象的 `await_ready()` 返回 `true`（C++20）或 Future 已完成（Python），协程**不会挂起**，会直接取值继续执行。过度假设"每个 await 都是一次上下文切换"会导致错误的性能分析。

**误区三：有栈协程（Fiber）优于无栈协程**。有栈协程灵活但每个 Fiber 需要预分配栈空间（即使只是 4 KB 起步），百万级并发时内存压力仍然显著。无栈协程的帧大小由编译器静态分析确定，通常只有几十到几百字节，在超高并发场景下内存效率更优。两者各有适用场景，不存在绝对优劣。

---

## 知识关联

**前置概念——Future/Promise**：协程的 `await` 表达式直接操作 Future 对象。Future 代表"未来某时刻会有值"的占位符，协程将自身的恢复逻辑注册为 Future 的回调，实现非阻塞等待。没有 Future 的完成通知机制，协程无法知道何时该被唤醒。

**事件循环（Event Loop）**：协程本身不能自我驱动，必须有一个事件循环（如 Python 的 `asyncio.get_event_loop()` 或 C++ 的 `io_context`）负责监听 I/O 事件、管理就绪协程队列、依次调用 `resume()`。理解协程必须同时理解驱动它的事件循环架构。

**生成器（Generator）**：Python 的协程从生成器演化而来——Python 2.5 的 `yield` 表达式、Python 3.3 的 `yield from`、直到 Python 3.5 的 `async/await`。C++20 的 `co_yield` 生成器协程与 `co_await` 异步协程共享同一套底层机制，理解生成器是掌握协程完整图景的捷径。