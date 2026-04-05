---
id: "se-future-promise"
concept: "Future/Promise"
domain: "software-engineering"
subdomain: "multithreading"
subdomain_name: "多线程"
difficulty: 2
is_milestone: false
tags: ["异步"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Future/Promise：异步结果与链式操作

## 概述

Future/Promise 是一种用于表示**尚未完成的异步计算结果**的编程抽象。它将"发起计算"和"获取结果"两个动作在时间上解耦：调用方提交任务后立刻得到一个 Future 对象作为占位符，真正的计算结果会在未来某个时刻填入这个占位符，调用方无需阻塞等待。

Future 概念最早在 1977 年由 Henry Baker 和 Carl Hewitt 在论文 *The Incremental Garbage Collection of Processes* 中正式提出，并在 Lisp 的 Actor 模型中得到初步实现。Promise 这一术语则由 Daniel Friedman 和 David Wise 在同年独立提出。两者在语义上略有区别：Future 通常指**只读的结果容器**，而 Promise 是可由生产者主动写入结果的**可写端**——Java 的 `CompletableFuture`、JavaScript 的 `Promise`、C++ 的 `std::future/std::promise` 都体现了这种读写分离设计。

Future/Promise 的价值在于解决了传统回调地狱（Callback Hell）问题：在 Node.js 早期代码中，三层以上的嵌套回调极难维护，而 Promise 的链式 `.then()` 将异步流程展平为线性结构，显著提升了可读性与错误处理能力。

---

## 核心原理

### 状态机模型

每个 Promise/Future 对象内部维护一个**三态状态机**：

| 状态 | 含义 |
|------|------|
| `Pending`（待定） | 计算尚未完成，结果未知 |
| `Fulfilled`（已兑现） | 计算成功，结果已写入 |
| `Rejected`（已拒绝） | 计算失败，错误原因已写入 |

状态转换是**单向且不可逆**的：`Pending → Fulfilled` 或 `Pending → Rejected`，一旦进入终态便永久锁定。这一特性使 Future 天然具备**幂等性**——对同一个已完成的 Future 多次调用 `get()` 或 `.then()` 始终返回相同结果，不会重新执行计算。

### 链式操作（Chaining）

Promise 的 `.then(onFulfilled, onRejected)` 方法返回一个**新的 Promise**，从而形成链式调用。规范（Promises/A+ 规范，2012 年制定）明确规定：若 `onFulfilled` 返回一个 Promise，则下一个 `.then` 必须等待该 Promise 解析完成后才触发。这使得串行异步操作可以写成：

```javascript
fetch('/api/user')
  .then(res => res.json())          // 返回新 Promise
  .then(user => fetch(`/api/orders/${user.id}`))  // 链式等待
  .then(res => res.json())
  .catch(err => console.error(err)); // 统一捕获链中任意错误
```

`.catch()` 本质是 `.then(undefined, onRejected)` 的语法糖，错误会沿链**向下冒泡**直到遇到第一个 `onRejected` 处理器。

### Java 中的 CompletableFuture

Java 5 引入的 `Future<V>` 接口只支持阻塞式 `get()`，无法注册回调。Java 8 引入 `CompletableFuture<V>` 补足了这一缺陷，提供了 `thenApply`（同步变换）、`thenCompose`（异步扁平化，等价于 Promise 的 flatMap）、`thenCombine`（合并两个独立 Future 的结果）等操作。其中：

- `thenApply(f)` ≈ 对结果做 `f` 变换，返回 `CompletableFuture<U>`
- `thenCompose(f)` 中 `f` 本身返回 `CompletableFuture`，会自动解包，避免 `CompletableFuture<CompletableFuture<U>>` 嵌套

C++ 标准库（C++11）中，`std::promise<T>` 的 `set_value()` 写入结果，`std::future<T>` 的 `get()` 读取结果并阻塞至就绪，两者通过共享状态（Shared State）耦合，但 C++11 的 `std::future` 不支持链式操作，需要 C++20 的 `std::experimental::future` 才有 `.then()`。

### 并发组合操作

多个 Future 可以通过组合原语并发执行：

- **Promise.all()**（JavaScript）：接收 Promise 数组，**全部成功**才 Fulfilled，任意一个 Rejected 则整体 Rejected，适合并行独立请求。
- **Promise.race()**：第一个完成的 Promise（无论成功或失败）决定最终状态，常用于超时控制。
- **Promise.allSettled()**（ES2020 新增）：等待所有 Promise 进入终态，无论成功还是失败，结果数组完整保留每个状态，适合批量操作后汇总报告。

---

## 实际应用

**前端并行数据加载**：页面初始化时需要同时请求用户信息、权限列表、系统配置三个接口，使用 `Promise.all([fetchUser(), fetchRoles(), fetchConfig()])` 让三个请求并发执行，总耗时等于最慢那个请求的耗时，而非三者之和。

**Java 线程池异步任务**：`ExecutorService` 的 `submit(Callable<T>)` 方法返回 `Future<T>`，线程池中的工作线程执行实际计算，主线程继续处理其他逻辑，在需要结果时调用 `future.get(5, TimeUnit.SECONDS)` 并设置超时，防止无限阻塞。

**超时熔断**：利用 `Promise.race([dataFetch, timeout(3000)])` 实现请求超时：若 3000 毫秒内 `dataFetch` 未完成，`timeout` 的 Rejected 状态率先触发，整体 Promise 进入 Rejected，触发降级逻辑。

---

## 常见误区

**误区一：认为 Promise 本身创建了新线程**
Promise 构造函数中的执行器（executor）是**同步执行**的，并不会开辟新线程。JavaScript 是单线程环境，Promise 的异步性来自事件循环（Event Loop）将微任务队列中的回调推迟到当前调用栈清空后执行，而非并发执行。真正的多线程并发（如 Java `CompletableFuture.supplyAsync()`）则由底层线程池负责，Future 对象本身仅是结果占位符。

**误区二：链式 .then() 等于顺序同步执行**
`.then()` 注册的回调在当前 Promise Fulfilled 后**异步调度**，不会阻塞主线程。若在 `.then()` 中返回一个非 Promise 的普通值，该值会被自动包装为 `Promise.resolve(value)`，下一个 `.then` 仍在微任务队列中调度，而非立即同步执行。

**误区三：忽略 Promise 的错误吞噬问题**
未附加 `.catch()` 的 Promise 链中，Rejected 状态会被静默吞噬（在较旧的 Node.js 版本中不会抛出任何错误）。Node.js 15 起，未处理的 Promise Rejection 默认**终止进程**（exit code 1），因此所有 Promise 链末尾必须显式添加错误处理。

---

## 知识关联

**与线程基础的关系**：理解线程的阻塞与唤醒机制有助于理解 `Future.get()` 的底层实现——Java 的 `FutureTask` 使用 `LockSupport.park()` 阻塞调用线程，计算完成后调用 `LockSupport.unpark()` 唤醒，Future 是对这一底层机制的高层封装。

**通向协程**：Future/Promise 的链式操作虽然解决了回调地狱，但大量 `.then()` 嵌套仍有可读性负担，且错误栈追踪困难。协程（Coroutine）以及基于协程的 `async/await` 语法是 Promise 的进一步抽象：`await` 表达式本质上是在 Promise 的 `.then()` 回调处**挂起当前协程**，待 Promise Fulfilled 后恢复执行，使异步代码在写法上与同步代码完全一致，是 Future/Promise 模型的自然演进方向。