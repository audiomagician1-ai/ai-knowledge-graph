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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

协程（Coroutine）是一种可以在执行过程中主动挂起（suspend）并在稍后恢复（resume）执行的函数。与普通函数只有一个入口点不同，协程拥有多个挂起点，每次恢复时从上次挂起的位置继续执行，且局部变量和执行状态完全保留。这一特性使协程能够在单线程内实现并发风格的代码，而无需操作系统的线程调度介入。

协程的概念最早由 Melvin Conway 在 1963 年提出，用于编写 COBOL 编译器的汇编器。真正广泛应用是在 2012 年前后，Python 3.4 引入 `asyncio` 库，Python 3.5 加入 `async`/`await` 关键字，使协程进入主流开发视野。C++ 则在 C++20 标准中正式将协程纳入语言规范，通过 `co_await`、`co_yield`、`co_return` 三个关键字实现。Go 语言的 goroutine 可视为协程的变体，由运行时自动调度。

协程的重要性体现在：它解决了异步 I/O 编程中"回调地狱"（Callback Hell）的代码可读性问题。传统基于回调的异步代码需要将逻辑拆散到多个函数中，而使用 `async`/`await` 的协程可以将异步逻辑写成看起来与同步代码几乎相同的线性结构，显著降低了并发程序的开发难度。

## 核心原理

### 挂起与恢复机制

协程的核心是**协作式调度**：协程在特定的挂起点主动让出控制权，而非被操作系统强制抢占。当协程执行到 `await` 表达式（如等待网络响应）时，它将自己的状态打包成一个"协程帧"（Coroutine Frame）保存到堆内存上，然后把控制权返还给事件循环（Event Loop）。事件循环可以趁此机会运行其他就绪的协程，直到 I/O 完成后再唤醒原来的协程继续执行。

在 Python 中，一个协程对象在未被 `await` 或提交给事件循环之前不会执行任何代码——这是协程区别于普通函数调用的关键行为。以下是最小示例：

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)  # 挂起点：让出控制权 1 秒
    return "data"

asyncio.run(fetch_data())
```

### C++20 协程的三个关键字

C++20 的协程规范定义了三个专属关键字，各有精确用途：

- **`co_await expr`**：挂起当前协程，等待 `expr` 所代表的 awaitable 对象完成。awaitable 对象必须实现 `await_ready()`、`await_suspend()` 和 `await_resume()` 三个方法。
- **`co_yield value`**：挂起协程并向调用者产出一个值，用于实现惰性生成器（Generator）。等价于 `co_await promise.yield_value(value)`。
- **`co_return value`**：终止协程并设置最终返回值，与普通 `return` 不同，它会触发 Promise 对象的 `return_value()` 方法。

一个函数只要包含上述任一关键字，编译器就会将其转化为协程。编译器会自动生成协程状态机，将局部变量提升到堆分配的协程帧中。

### 有栈协程与无栈协程

协程分为两大类型，差异显著：

**有栈协程（Stackful Coroutine）**，也称 Fiber，拥有独立的调用栈（通常为 8KB~1MB）。切换时需保存并恢复完整的寄存器上下文（x86-64 上约需保存 6 个寄存器）。Boost.Fiber 和操作系统级的 Windows Fiber 属于此类。有栈协程可以在任意调用深度挂起，更灵活但开销更大。

**无栈协程（Stackless Coroutine）**，Python 的 `async def` 和 C++20 协程均属此类。每个协程对象只占用一个堆上的状态结构，切换开销极低，但挂起点只能位于协程函数自身体内，不能在被调用的普通函数内部挂起。Python 中每个协程帧大小通常在数百字节量级，因此单进程可以轻松维持数万个并发协程。

### 与 Future/Promise 的协作

协程依赖 Future/Promise 机制来驱动挂起与唤醒。当协程 `await` 一个 Future 对象时，若 Future 尚未完成（`await_ready()` 返回 `false`），协程将自身的 continuation（恢复句柄 `coroutine_handle`）注册到 Future 的回调列表中，然后挂起。当 Promise 端调用 `set_value()` 解决该 Future 时，事件循环或线程池会执行保存的 continuation，从而恢复协程。这一机制使协程本质上是 Future/Promise 的语法糖，将链式 `.then()` 回调转化为线性的 `await` 语句。

## 实际应用

**高并发 Web 服务器**：Python 的 FastAPI 框架基于 `asyncio` 协程构建，单进程可处理数千个并发 HTTP 请求。每个请求处理函数定义为 `async def`，在等待数据库查询或外部 API 调用时自动挂起，让出 CPU 给其他请求，吞吐量远超同等线程数的同步 Flask 应用。

**游戏逻辑脚本**：Lua 和 Unity C# 中的协程（`IEnumerator` + `yield return`）用于编写游戏行为序列。例如，"怪物移动到位置A，等待2秒，播放攻击动画"可写成一个线性协程，而无需用状态机或计时器回调拆散逻辑。Unity 的 `StartCoroutine` 每帧推进协程执行，是游戏开发中协程最直观的应用场景之一。

**生成器与惰性流**：Python 的 `yield` 和 C++20 的 `co_yield` 实现惰性数据生成器。处理无限序列（如实时传感器数据流）时，生成器每次只计算当前值，不预先分配完整序列的内存，内存占用为 O(1) 而非 O(n)。

## 常见误区

**误区一：协程实现了真正的并行**。协程在单线程内以协作式调度运行，同一时刻只有一个协程在 CPU 上执行。Python 的 `asyncio.gather()` 可以"并发"运行多个协程，但并非并行——它们在同一线程内交替执行，遇到 I/O 等待时切换。若要利用多核，需要结合 `multiprocessing` 或将协程运行在多个线程的线程池上。CPU 密集型任务使用协程不仅无益，还会因为阻塞事件循环而拖慢整个程序。

**误区二：`async def` 函数可以像普通函数一样直接调用获得结果**。调用 `async def` 函数返回的是一个协程对象，而非函数的计算结果。必须通过 `await`（在异步上下文中）或 `asyncio.run()`（在同步入口）来驱动协程执行。直接调用 `fetch_data()` 而不 `await` 是一个常见的 Python 新手错误，程序不会报错但也不会执行任何实际逻辑，Python 3.7+ 会为此发出 `RuntimeWarning: coroutine 'fetch_data' was never awaited`。

**误区三：有栈协程（Fiber）比无栈协程更先进**。两者各有适用场景。Fiber 的优势是可以在任意调用深度透明挂起，适合改造遗留的同步代码库。但 Fiber 每个实例需要预分配独立调用栈（通常 64KB 起），维持 10 万个并发 Fiber 需要约 6.4GB 内存，而同等数量的无栈协程可能只需数百 MB。选择哪种协程类型取决于具体场景，而非存在绝对优劣。

## 知识关联

**前置概念**：协程的挂起-唤醒机制直接建立在 **Future/Promise** 之上。`co_await` 本质上是在等待一个 Promise 被解决，事件循环负责在 Promise 完成时调用协程的恢复句柄。没有 Future/Promise 提供的异步结果容器，协程就缺乏与外部 I/O 系统（如套接字、文件系统）交互的桥梁。理解 `std::promise<T>::set_value()` 如何触发 `std::future<T>` 的就绪状态，有助于理解 C++20 中 awaitable 对象的底层工作方式。

**拓展方向**：掌握协程后，可以进一步研究结构化并发（Structured Concurrency）的设计理念，例如 Python 3.11 引入的 `asyncio.TaskGroup` 和 C++ 提案中的 `std::execution`（P2300）。此外，协程是实现反应式编程（Reactive Programming）的基础技术之一，RxPY 和 C++ Ranges 的惰性求值管道均与协程的 `co_yield` 生成器模型高度相关。