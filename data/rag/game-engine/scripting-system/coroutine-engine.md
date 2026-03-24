---
id: "coroutine-engine"
concept: "协程系统"
domain: "game-engine"
subdomain: "scripting-system"
subdomain_name: "脚本系统"
difficulty: 2
is_milestone: false
tags: ["异步"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 协程系统

## 概述

协程系统（Coroutine System）是游戏引擎脚本层提供的一种**协作式多任务机制**，允许函数在执行过程中主动暂停（yield）并在稍后恢复，而不阻塞主线程的帧循环。与操作系统线程的抢占式调度不同，协程的切换时机完全由程序员通过 `yield` 指令控制，因此不存在数据竞争的风险，非常适合游戏逻辑中常见的"等待某个条件成立后继续执行"的场景。

协程的概念最早由 Melvin Conway 于 1963 年提出，用于描述可以互相调用、彼此协作的子程序。游戏引擎领域对协程的大规模普及主要归功于 Unity，其在 Unity 3.x 版本中将 C# 迭代器（`IEnumerator`）作为协程的底层实现机制对外暴露，使得游戏开发者无需编写复杂的状态机，便能以线性风格描述跨越多帧的行为逻辑。

协程系统在游戏开发中解决的核心痛点是：过场动画序列、UI 渐变效果、AI 行为等逻辑往往需要跨越数十乃至数百帧才能完成。如果用普通函数实现，开发者必须手动将逻辑拆分成"本帧执行什么、下帧执行什么"的状态机，代码量倍增且难以维护。协程系统让这类时序逻辑的表达回归自然的顺序书写方式。

---

## 核心原理

### yield 指令与帧循环的集成

协程的暂停点由 `yield` 语句标记。在 Unity 的实现中，引擎在每帧 `Update` 结束后统一检查所有已注册协程的恢复条件，满足条件的协程在当帧（或指定时机）被唤醒继续执行。常见的 yield 类型包括：

- **`yield return null`**：暂停当前帧，在**下一帧 Update 之后**恢复。
- **`yield return new WaitForSeconds(t)`**：等待 `t` 秒（受 `Time.timeScale` 影响）后恢复，适合淡入淡出等时间相关效果。
- **`yield return new WaitForFixedUpdate()`**：在下一次 **FixedUpdate**（默认 0.02 秒/次）之后恢复，用于物理相关的延迟操作。
- **`yield return new WaitUntil(predicate)`**：每帧轮询 `predicate` 委托，条件为 `true` 时恢复，适合等待异步加载或玩家输入。

### C# 迭代器状态机的底层实现

Unity 的协程本质上是编译器将含有 `yield return` 的方法自动转换为实现 `IEnumerator` 接口的**有限状态机类**。每次调用 `MoveNext()` 时，状态机从上次暂停的位置继续执行，直到遇到下一个 `yield return` 或方法结束。引擎持有一个协程列表，每帧对列表内所有协程调用 `MoveNext()` 并检查返回的 `YieldInstruction` 对象是否满足恢复条件。这意味着协程的调度开销主要来自**每帧遍历列表**和**虚函数调用**，当同时运行数千个协程时，这一开销不可忽视（Unity 官方建议对高频协程改用 ECS Job System 或手写状态机）。

### 定时器与时间缩放

`WaitForSeconds` 内部使用 `Time.time`（受 `timeScale` 影响），而 `WaitForSecondsRealtime` 则使用 `Time.realtimeSinceStartup`（不受暂停影响）。在实现"游戏暂停但 UI 动画继续播放"的需求时，必须选择正确的 yield 类型。例如，暂停菜单的弹出动画需使用 `WaitForSecondsRealtime`，否则当 `timeScale = 0` 时动画将永远无法完成。

### 协程的生命周期管理

协程与启动它的 MonoBehaviour 实例绑定：当该对象被禁用（`SetActive(false)`）或销毁时，其上的所有协程自动停止。通过 `StartCoroutine()` 返回的 `Coroutine` 句柄可传入 `StopCoroutine()` 手动停止。若需要协程脱离对象生命周期独立运行，需将其挂载在一个常驻场景的单例对象上（常见的 `CoroutineRunner` 模式）。

---

## 实际应用

**过场对话序列**：角色对话系统中，每句台词需要等待玩家点击或等待 2 秒自动推进。用协程表达如下：

```csharp
IEnumerator PlayDialogue(string[] lines) {
    foreach (var line in lines) {
        dialogueBox.text = line;
        yield return new WaitUntil(() => Input.GetMouseButtonDown(0));
        yield return null; // 跳过同帧的重复点击
    }
}
```

这段逻辑用状态机实现需要额外维护 `currentLine` 索引、`waitingForClick` 布尔值等多个字段，而协程版本完整逻辑仅需 6 行。

**渐变效果**：UI 透明度从 1 渐变到 0 需要持续约 0.5 秒，协程可用 `while (alpha > 0)` 配合 `yield return null` 逐帧递减，精确控制效果时长而不占用额外线程资源。

**异步资源加载等待**：`yield return SceneManager.LoadSceneAsync("Level2")` 可等待场景加载完毕后再执行后续逻辑，是 Unity 异步 API 与协程结合的典型模式。

---

## 常见误区

**误区一：协程等同于多线程**
协程始终运行在**主线程**上，任意时刻只有一个协程的代码在执行，不存在并行计算。`WaitForSeconds(1)` 并不会让 CPU 在后台睡眠 1 秒，而是每帧都被检查是否已过去 1 秒。因此协程无法加速 CPU 密集型计算，试图用协程并行化大量数学运算会导致帧率下降而不是提升。

**误区二：yield return new WaitForSeconds() 的 new 开销可忽略不计**
在每帧反复执行的循环中写 `yield return new WaitForSeconds(0.1f)` 会在托管堆上**每次分配一个新对象**，产生 GC 压力。正确做法是将 `WaitForSeconds` 实例缓存为成员变量，或使用 `WaitForSecondsRealtime` 的缓存版本，从而避免高频 GC Alloc。

**误区三：协程在对象禁用后仍会自动恢复**
许多初学者认为 `yield return new WaitForSeconds(5)` 会像定时器一样在 5 秒后必然触发。实际上，若挂载协程的 GameObject 在等待期间被 `SetActive(false)`，协程将被**立即终止**而不是暂停，恢复后也不会继续运行，需手动重新启动。

---

## 知识关联

协程系统建立在**脚本系统概述**所描述的 MonoBehaviour 生命周期（Awake → Start → Update → LateUpdate）之上，其调度时机嵌入在这一帧循环的特定插槽中——理解 Update 与 FixedUpdate 的调用顺序，才能正确选择 `WaitForFixedUpdate` 还是 `yield return null`。

对于更复杂的异步需求，协程系统是理解 Unity **Async/Await（UniTask）** 和 **Job System** 的前置基础：UniTask 将 C# 原生 `async/await` 语法适配到 Unity 的帧循环调度中，本质上是对协程调度模型的扩展与性能优化；而 Job System 则走向了另一个方向——真正利用多核并行，弥补协程无法并行计算的短板。理解协程的单线程本质和 yield 驱动模型，有助于清晰判断何时应选用协程，何时必须升级到 Job System。
