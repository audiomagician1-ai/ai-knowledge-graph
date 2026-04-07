# Future/Promise：异步结果与链式操作

## 概述

Future/Promise 是一种将**异步计算结果**封装为第一类对象（First-Class Object）的编程抽象，其根本设计目标是把"发起计算"与"消费结果"两个操作在时间轴上彻底解耦。调用方提交异步任务后，立即获得一个代表"未来某时刻结果"的占位符对象（Future），真正的值由生产者线程或事件循环在计算完成后写入；消费者线程可在任意时刻通过轮询、阻塞等待或注册回调三种方式获取结果，而无需关心计算何时发生。

Future 概念最早可追溯至 1977 年：Henry Baker 与 Carl Hewitt 在论文 *The Incremental Garbage Collection of Processes*（Baker & Hewitt, 1977）中，将 Future 作为 Actor 模型传递延迟消息的机制正式引入计算机科学文献。同年，Daniel Friedman 与 David Wise 在 *CONS Should Not Evaluate Its Arguments*（Friedman & Wise, 1976）中独立提出了惰性求值意义下的 Promise 概念。Promise/A+ 规范（Domenic Denicola et al., 2012）则是 JavaScript 生态中将链式 `.then()` 语义标准化的关键文献，直接影响了 ECMAScript 2015（ES6）中 `Promise` 的语言级内建支持，以及 ES2017 引入的 `async/await` 语法糖。

两端语义在现代语言中的分工极为清晰：**Promise 是可写端**（生产者持有，负责填入成功值或错误原因），**Future 是只读端**（消费者持有，负责查询或等待结果）。C++ 标准库 `<future>` 头文件中 `std::promise<T>` 与 `std::future<T>` 是这一生产者/消费者分离设计最直接的体现，二者通过共享状态（Shared State）对象相连。

---

## 核心原理

### 三态状态机与不可逆转换

每个 Promise/Future 实例内部维护一个**严格三态有限状态机**：

| 状态 | 语义 | 可转换目标 |
|------|------|-----------|
| `Pending`（待定） | 计算尚未完成，结果未知 | `Fulfilled` 或 `Rejected` |
| `Fulfilled`（已兑现） | 携带成功结果值 $v$ | 终态，不可再变 |
| `Rejected`（已拒绝） | 携带失败原因 $e$ | 终态，不可再变 |

状态机的**单向性与不可逆性**是 Future 幂等行为的理论基础。形式化地，设 $S(t)$ 为 Future 在时刻 $t$ 的状态，则：

$$S(t_1) \in \{\text{Fulfilled}, \text{Rejected}\} \Rightarrow S(t_2) = S(t_1), \quad \forall t_2 > t_1$$

这意味着对同一个已兑现的 Future 多次调用 `get()` 或注册多个 `.then()` 回调，均返回相同的值 $v$，不会重新触发计算。这与 Java 中的 `volatile` 变量或 Haskell 中的 `MVar` 有本质区别——后两者允许重复写入，而 Future 的写入是**一次性的 CAS（Compare-And-Swap）操作**。

在 Java `CompletableFuture` 的 OpenJDK 实现（JDK 8+）中，内部结果字段 `Object result` 初始为 `null`（对应 Pending），通过 `Unsafe.compareAndSwapObject(this, RESULT, null, r)` 原子地将其从 `null` 修改为实际值或封装异常的 `AltResult` 对象。并发场景下，只有第一次 CAS 成功的线程完成写入，后续尝试均被静默丢弃，从而在无锁（Lock-Free）前提下保证写入唯一性。

### 链式操作的传播语义

Promises/A+ 规范定义了 `.then(onFulfilled, onRejected)` 的精确语义，其核心规则如下：

1. `.then()` 必须返回一个**新的 Promise**，记为 $p_2$；
2. 若 `onFulfilled` 正常返回值 $x$，则执行"Promise Resolution Procedure" $\text{Resolve}(p_2, x)$：
   - 若 $x$ 是普通值，则以 $x$ 兑现 $p_2$；
   - 若 $x$ 本身是 thenable（具有 `.then` 方法的对象），则 $p_2$ 的状态**跟随** $x$ 的最终状态（adopt semantics）；
3. 若 `onFulfilled` 或 `onRejected` 抛出异常 $e$，则以 $e$ 拒绝 $p_2$，错误沿链向下游自动传播，直至遇到 `.catch()` 处理器；
4. **回调必须异步执行**（在当前执行上下文的 Microtask 队列中调度），即使 Promise 已处于已兑现状态，也不得在 `.then()` 调用栈内同步触发回调，以保证行为的一致性。

规则 4 是 JavaScript Promise 与 Java `CompletableFuture` 的重要差异之一：后者的回调默认在完成 Future 的线程中同步执行，需要显式指定 `Executor` 才能切换执行上下文。

### 并发组合子（Combinator）

单个 Promise 的价值有限，真正的威力来自多 Promise 的并发组合：

- **`Promise.all(iterable)`**：当且仅当所有输入 Promise 均兑现时，以结果数组兑现；若任意一个被拒绝，立即以该错误拒绝，其余 Promise 的结果被丢弃（Fail-Fast 语义）。时间复杂度为 $O(\max(t_i))$，其中 $t_i$ 为第 $i$ 个 Promise 的完成时间，相比串行 $O(\sum t_i)$ 在 I/O 密集场景下收益显著。
- **`Promise.allSettled(iterable)`**（ES2020 引入）：等待所有 Promise 落定（无论成功或失败），以包含 `{status, value/reason}` 对象的数组兑现，适合需要知晓所有子任务状态的批量操作。
- **`Promise.race(iterable)`**：以**最先落定**（无论成功或失败）的 Promise 的结果落定，常用于实现请求超时：将目标请求与一个在 $n$ 毫秒后 `reject` 的 Promise 竞速。
- **`Promise.any(iterable)`**（ES2021 引入）：以第一个**成功兑现**的 Promise 的值兑现；若全部被拒绝，则以 `AggregateError` 拒绝，包含所有错误原因。

---

## 关键方法与公式

### async/await 的脱糖（Desugaring）变换

ES2017 的 `async/await` 是 Promise 链的语法糖，编译器（如 Babel、TypeScript）将其变换为状态机。以下面的函数为例：

```javascript
async function fetchUser(id) {
  const res = await fetch(`/api/user/${id}`);
  const data = await res.json();
  return data.name;
}
```

其语义等价于：

```javascript
function fetchUser(id) {
  return fetch(`/api/user/${id}`)
    .then(res => res.json())
    .then(data => data.name);
}
```

更深层地，TypeScript 编译器将 `async` 函数展开为基于 `__generator` 的协程状态机，每个 `await` 对应状态机中的一个暂停点（Suspension Point）。C# 5.0（Anders Hejlsberg et al., 2012）是将 `async/await` 引入主流语言的先驱，其 `Task<T>` 类型对应 JavaScript 的 `Promise<T>`，且 C# 编译器生成的状态机代码早于 JavaScript 规范，是后者设计的重要参考。

### 错误传播的短路模型

在 Promise 链 $p_1 \to p_2 \to \cdots \to p_n$ 中，设第 $k$ 个环节抛出异常 $e$，则 $p_{k}, p_{k+1}, \ldots$ 均以 $e$ 被拒绝，直到某个环节的 `onRejected` 处理器返回正常值 $r$，此后链从 $r$ 重新进入 Fulfilled 路径。这与同步代码中 `try/catch` 的控制流在语义上完全对应，差别仅在于沿 Promise 链传播而非沿调用栈展开。

$$\text{若 } f_k \text{ 抛出异常 } e, \quad p_{k} = \text{Rejected}(e), \quad p_{k+1} = \text{Rejected}(e), \quad \ldots$$

直到遇到第一个定义了 `onRejected` 的 `.then()` 或 `.catch()` 节点。

### Java CompletableFuture 的函数式 API

Java 8 引入的 `CompletableFuture<T>`（Doug Lea 主导设计，JSR-166）提供了完整的函数式组合 API：

- `thenApply(Function<T,U>)`：对结果进行同步映射，返回 `CompletableFuture<U>`；
- `thenCompose(Function<T, CompletableFuture<U>>)`：对结果执行返回 Future 的函数，并展平（flatMap 语义），避免产生 `CompletableFuture<CompletableFuture<U>>` 的嵌套；
- `thenCombine(CompletableFuture<U>, BiFunction<T,U,V>)`：并发等待两个 Future 完成后合并结果；
- `exceptionally(Function<Throwable,T>)`：对异常进行恢复，对应 `.catch()` 的错误恢复语义。

`thenCompose` 与 `thenApply` 的区分是 Java 异步编程的常见难点：前者是 Monad 的 `bind`（`>>=`）操作，后者是 Functor 的 `fmap` 操作，二者的选择直接决定链式调用是否会产生不必要的嵌套层。

---

## 实际应用

### 案例一：并发 API 聚合

假设前端页面需要同时请求用户信息、权限列表和消息数量三个独立接口，串行请求需要 $t_1 + t_2 + t_3$ 时间，而使用 `Promise.all` 并发请求仅需 $\max(t_1, t_2, t_3)$：

```javascript
const [user, permissions, messageCount] = await Promise.all([
  fetchUser(userId),          // ~120ms
  fetchPermissions(userId),   // ~80ms
  fetchMessageCount(userId),  // ~50ms
]);
// 总耗时约 120ms，而非 250ms
```

若三个接口均返回 P95 延迟约 100ms，串行模式的 P95 总延迟为 300ms，并发模式下降至 100ms，在高频页面中对用户感知延迟有决定性影响。

### 案例二：带超时的请求竞速

```javascript
function fetchWithTimeout(url, ms) {
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
  );
  return Promise.race([fetch(url), timeout]);
}
```

此模式利用 `Promise.race` 的 Fail-Fast 特性实现超时控制，无需修改 `fetch` 本身，是 Promise 组合子"正交组合"特性的典型体现。需要注意的是，超时后被丢弃的 `fetch` 请求在浏览器底层仍会继续执行并占用连接资源，必要时需通过 `AbortController` 配合取消。

### 案例三：Scala Future 与 ExecutionContext

Scala 标准库中的 `Future[T]`（引入自 Scala 2.10，2012 年）要求所有 Future 操作显式传入 `ExecutionContext`，决定计算在哪个线程池上调度：

```scala
import scala.concurrent.{Future, ExecutionContext}
import ExecutionContext.Implicits.global

val result: Future[Int] = Future(heavyComputation()).map(_ * 2)
```

这与 JavaScript Promise 的单线程事件循环模型截然不同：Scala Future 的回调真实地在 `ExecutionContext` 管理的线程池上并行执行，因此共享可变状态需要额外的同步保护。

---

## 常见误区

### 误区一：混淆 Promise 链与嵌套 Promise

在 JavaScript 中，`.then()` 内部**返回**一个 Promise 与**嵌套调用** `.then()` 有本质区别。错误写法：

```javascript
fetchUser(id).then(user => {
  fetchOrders(user.id).then(orders => {  // 嵌套，回调地狱重现
    console.log(orders);
  });
});
```

正确写法是从 `onFulfilled` 中**返回**内