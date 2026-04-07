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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 协程系统

## 概述

协程（Coroutine）是一种能够在执行过程中主动暂停并在稍后恢复的函数。与普通函数必须从头运行到尾不同，协程拥有独立的执行状态（包括局部变量和程序计数器），可以在任意`yield`点挂起，将控制权交回给调度器，等待下一帧或特定条件满足后继续执行。游戏引擎中的协程并不是操作系统级别的线程，它们运行在同一个主线程上，通过引擎主循环的调度器轮流切换。

Unity 引擎在 2010 年左右将协程机制带入主流游戏开发视野，其底层基于 C# 的 `IEnumerator` 迭代器协议实现。Lua 语言从 5.0 版本（2003年）起内置了原生协程支持，成为许多游戏引擎（如使用 Lua 的 Cocos2d-x 和 LÖVE）实现协程系统的首选语言。

协程在游戏开发中解决了一个核心痛点：如何在不阻塞主线程的前提下，用线性代码描述跨越多帧的行为序列。例如让角色播放攻击动画、等待 0.5 秒、然后造成伤害，若用状态机或回调链实现会极为繁琐，而用协程可以写成三行顺序代码。

## 核心原理

### yield 挂起与恢复机制

协程的关键操作是 `yield`（让步）。当协程执行到 `yield` 语句时，它将当前的调用栈状态保存下来，把执行权交还给协程调度器，自身进入"挂起"状态。下一次被调度器唤醒时，从 `yield` 语句的下一行继续执行，所有局部变量的值保持不变。

在 Unity 中，`yield return new WaitForSeconds(1.5f)` 表示挂起当前协程 1.5 秒；`yield return null` 表示挂起一帧，下一帧继续。引擎每帧遍历所有挂起的协程，判断其恢复条件是否满足，满足则将其重新加入执行队列。

### 协程调度器的工作流程

游戏引擎主循环每帧按固定顺序处理协程：
1. **Update 前检查**：处理 `yield return null` 类型的协程（等待一帧）
2. **FixedUpdate 后检查**：处理 `WaitForFixedUpdate`
3. **帧末检查**：处理 `WaitForEndOfFrame`
4. **计时检查**：对 `WaitForSeconds` 类协程，比较当前时间与目标唤醒时间

Unity 协程调度器内部维护一个协程链表，每帧的时间复杂度为 O(n)，其中 n 是活跃协程数量。当活跃协程超过数百个时，调度开销开始显现，这是为什么游戏中不建议同时运行数千个 `WaitForSeconds` 协程的原因。

### 定时器的协程实现

传统定时器需要在每帧 Update 中手动递减计时变量，协程定时器则更简洁：

```lua
-- Lua 协程定时器示例
function Timer(seconds, callback)
    local elapsed = 0
    while elapsed < seconds do
        elapsed = elapsed + deltaTime
        coroutine.yield()
    end
    callback()
end
```

引擎层面，`WaitForSeconds` 使用的是游戏内时间（受 `Time.timeScale` 缩放影响），而 `WaitForSecondsRealtime` 使用系统真实时间，两者在暂停菜单、慢动作等场景下行为截然不同。暂停游戏时将 `timeScale` 设为 0，所有 `WaitForSeconds` 协程会冻结，但 `WaitForSecondsRealtime` 协程会继续计时。

### 协程与异步任务的关系

Unity 2017 引入了与 C# `async/await` 语法的融合路线，UniTask 库（基于 ValueTask）进一步将协程与异步任务统一，其分配内存从每次 `new WaitForSeconds()` 产生的约 40 字节 GC 压力降低到几乎零分配。Unreal Engine 5 的蓝图系统中的"延迟节点"（Delay Node）本质上也是协程，但通过可视化节点而非代码暴露给开发者。

## 实际应用

**过场动画序列**：协程可以精确控制多步骤过场，例如：淡入黑幕（等待 `FadeIn` 协程完成）→ 播放角色对话动画（等待动画长度 2.3 秒）→ 触发镜头切换 → 淡出黑幕。整个流程写成一个协程函数，代码可读性远高于嵌套回调。

**技能冷却系统**：技能释放后启动协程 `yield return new WaitForSeconds(cooldownTime)`，协程结束时将技能状态重置为可用，避免在每帧 Update 中维护浮点计时器变量。

**分帧加载**：加载大量资源时，可将加载逻辑放入协程，每帧只处理一批（如每帧实例化 10 个对象），在每批次之间 `yield return null`，避免单帧卡顿超过 16.6 毫秒（60fps 帧时间预算）。

**网络请求等待**：在不使用多线程的情况下，协程可配合 `WWW` 或 `UnityWebRequest` 等待网络响应，`yield return request.SendWebRequest()` 在请求完成前持续挂起，请求完成后自动恢复。

## 常见误区

**误区一：协程是多线程**。协程运行在主线程上，协程内部的代码与 Update、OnCollisionEnter 等回调不会并发执行，因此协程读写游戏对象数据无需加锁。而真正的 `System.Threading.Thread` 或 `Task.Run` 在 Unity 中访问 GameObject 会抛出异常，因为 Unity API 不是线程安全的。协程与线程是完全不同的并发模型。

**误区二：`yield return new WaitForSeconds(0)` 等同于 `yield return null`**。两者都等待一帧，但 `WaitForSeconds(0)` 会创建一个新的 `WaitForSeconds` 对象，产生 GC 分配，在频繁调用时会累积垃圾回收压力；`yield return null` 不分配任何堆内存。在性能敏感的循环协程中应始终使用 `yield return null`，或缓存 `WaitForSeconds` 实例。

**误区三：协程会在脚本禁用后自动停止**。Unity 中，禁用（Disable）MonoBehaviour 组件不会停止其上运行的协程，只有销毁（Destroy）GameObject 或调用 `StopCoroutine` / `StopAllCoroutines` 才会终止协程。这一行为导致的常见 Bug 是：组件被禁用后协程仍在修改场景状态，而开发者误以为协程已停止。

## 知识关联

协程系统建立在脚本系统概述所介绍的脚本生命周期（`Start`、`Update`、`OnDestroy`）之上：协程由脚本函数启动，其调度完全嵌入引擎主循环，协程的生命周期随宿主 GameObject 终止。理解 `Update` 每帧 16.6ms 的时间窗口，有助于判断何时应将逻辑拆分到协程以避免单帧超时。

协程系统与动画系统的交互体现在 `WaitForAnimationEnd` 等待动画片段播完；与物理系统的交互体现在 `WaitForFixedUpdate` 同步物理步进节奏（Unity 默认 FixedUpdate 间隔为 0.02 秒，即 50Hz）。掌握协程后，开发者会自然接触到 C# `async/await` 异步模型——两者都解决"等待后续续执行"的问题，但协程与引擎帧循环深度绑定，而 `async/await` 基于线程池，各有适用场景。