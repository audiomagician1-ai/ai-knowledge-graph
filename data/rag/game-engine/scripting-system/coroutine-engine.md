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
content_version: 4
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

协程系统是游戏引擎脚本层提供的一种**协作式多任务机制**，允许一段代码在特定挂起点暂停执行，将控制权归还给引擎主循环，并在未来某个时机自动恢复。与操作系统的抢占式线程不同，协程的切换完全由程序员和引擎逻辑主动控制，不涉及真正的并行执行，因此不需要互斥锁来保护共享状态。

协程（Coroutine）这一概念由 Melvin Conway 于 1958 年在汇编语言实现中首次提出，但在游戏引擎领域的广泛普及主要源于 Unity 引擎于 2009 年发布 Unity 2.x 时将其纳入 C# 脚本体系。Unity 的实现方式是基于 C# 迭代器（`IEnumerator`）的语法糖——开发者在函数中使用 `yield return` 语句声明挂起点，引擎每帧调用 `MoveNext()` 推进协程。这一设计极大地降低了异步逻辑的编写门槛，使"等待两秒后触发爆炸"这类时序逻辑无需状态机即可直接表达。

协程系统在游戏开发中的价值在于**将时间维度的逻辑压平为线性代码**。传统 Update 函数中处理跨帧等待需要手动维护计时器变量和状态标志，而协程可以用 `yield return new WaitForSeconds(2f)` 一行代替，大幅减少逻辑碎片化。

---

## 核心原理

### 挂起与恢复机制

协程的执行流依赖一个**延续（Continuation）对象**保存当前局部变量、执行位置（程序计数器偏移）。每次调用 `MoveNext()` 时，引擎恢复这份上下文并继续执行，直到遇到下一个 `yield` 语句或函数结束。以 Unity 为例，`StartCoroutine()` 返回一个 `Coroutine` 句柄，引擎内部维护一张协程列表，在每帧 `Update` 阶段结束后统一推进这些协程。

### 常见挂起类型及其触发时机

不同的 `yield` 指令对应引擎循环中不同的恢复位置：

| 挂起指令 | 恢复时机 |
|---|---|
| `yield return null` | 下一帧 Update 之后 |
| `yield return new WaitForSeconds(t)` | 至少经过 `t` 秒（受 `Time.timeScale` 影响）|
| `yield return new WaitForSecondsRealtime(t)` | 至少经过真实时间 `t` 秒（不受 timeScale 影响）|
| `yield return new WaitForFixedUpdate()` | 下一次 FixedUpdate 之后 |
| `yield return new WaitUntil(predicate)` | 谓词函数返回 `true` 的那一帧 |

`WaitForSeconds` 的计时公式为：  
**累计等待时间 = Σ (Time.deltaTime × Time.timeScale)**，当该值 ≥ 目标秒数时协程恢复。

### 协程的嵌套与链式执行

协程内部可以用 `yield return StartCoroutine(子协程)` 实现嵌套等待——父协程会阻塞直到子协程全部完成。这使得"加载资源 → 播放动画 → 开始战斗"的顺序流程可以用嵌套协程精确描述，而不必在每个步骤的回调里手动启动下一步。Lua 环境（如 cocos2dx 的 scheduler 或自定义 Lua 协程）则通过 `coroutine.resume()` / `coroutine.yield()` 这对原语实现等效语义。

### 定时器与异步任务的关系

协程系统也是引擎**定时器**功能的底层载体。`WaitForSeconds` 本质上是一个携带截止时间戳的对象，引擎在推进协程列表时比较当前时间与截止时间，决定是否恢复。相比手动 `Invoke("方法名", 延迟秒数)` 的字符串反射调用，协程定时方式具备编译期检查和上下文保留两项优势。Unreal Engine 的 Blueprint 中对应概念是 `Delay` 节点，其内部实现为引擎托管的延迟任务队列。

---

## 实际应用

**过场动画序列**：一个 Boss 入场演出需要依次播放飞入动画（1.5 秒）、震屏效果（0.3 秒）、对话框出现（等待玩家按键）。使用协程：
```csharp
IEnumerator BossEntrance() {
    PlayFlyInAnim();
    yield return new WaitForSeconds(1.5f);
    ShakeScreen(0.3f);
    yield return new WaitForSeconds(0.3f);
    ShowDialogue();
    yield return new WaitUntil(() => Input.GetKeyDown(KeyCode.Space));
    StartBattle();
}
```
全部时序逻辑在一个函数中一目了然，不需要任何外部状态变量。

**异步资源加载**：`yield return Resources.LoadAsync<Texture2D>("ui/portrait")` 将资源加载请求提交给引擎，协程在加载完成的帧自动恢复，紧接着即可安全使用加载结果。

**技能冷却 CD 倒计时**：技能触发后启动协程，在协程内将技能按钮设为不可用，`yield return new WaitForSeconds(cooldown)` 等待冷却时间结束，再将按钮恢复可用状态。这将冷却逻辑完整封装在技能对象内部，避免了在全局 Update 中遍历所有技能状态。

---

## 常见误区

**误区一：协程等同于多线程，可以执行耗时计算**  
协程在 Unity 中运行于主线程，`yield return` 只是让出本帧的剩余执行时间，下一帧仍在主线程恢复。若在协程内执行一次耗时 50ms 的循环，主线程依然会卡顿掉帧。真正的后台计算应使用 `System.Threading.Task` 或 Unity 的 `Job System`，不能用协程替代。

**误区二：协程在对象销毁后会自动停止**  
Unity 的协程绑定在 `MonoBehaviour` 实例上，当该 GameObject 被**禁用**（`SetActive(false)`）时协程暂停，被**销毁**（`Destroy`）时协程终止。但若通过另一个活跃的 MonoBehaviour 持有被销毁对象的协程句柄并继续操作，会引发空引用异常。需要在 `OnDestroy` 中主动调用 `StopAllCoroutines()` 清理。

**误区三：WaitForSeconds 的等待精度是精确的**  
`WaitForSeconds(2f)` 不保证恰好在 2 秒后恢复，而是在**累计时间首次超过 2 秒的那一帧**恢复。若游戏帧率为 10fps（deltaTime ≈ 0.1s），实际等待可能达到 2.1 秒。对精度要求极高的场景（如音频同步），应改用 `WaitForSecondsRealtime` 或基于 `AudioSettings.dspTime` 的精确调度。

---

## 知识关联

协程系统建立在**脚本系统概述**所介绍的引擎脚本生命周期之上——必须先理解 `Awake → OnEnable → Start → Update → LateUpdate` 的帧循环顺序，才能准确预判不同 `yield` 指令的恢复时机。`WaitForFixedUpdate` 的存在意义只有在知道物理步骤在 Update 之前执行的前提下才能理解。

在工程实践中，协程系统是通往更高级异步模式的桥梁：Unity 2020 引入的 `UniTask` 库基于 C# 5.0 的 `async/await` 语法，实现了零 GC 分配的协程等效功能，其底层仍依赖引擎的 PlayerLoop 注入机制，与协程共享同一套帧回调基础设施。掌握协程的挂起/恢复模型，是理解 `async/await` 状态机生成原理的直接前置知识。
