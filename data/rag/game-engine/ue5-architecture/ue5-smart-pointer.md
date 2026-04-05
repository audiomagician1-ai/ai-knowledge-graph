---
id: "ue5-smart-pointer"
concept: "UE5智能指针"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 2
is_milestone: false
tags: ["内存"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# UE5智能指针

## 概述

UE5智能指针是虚幻引擎为非UObject类提供的一套内存管理模板类，包含`TSharedPtr<T>`、`TWeakPtr<T>`和`TUniquePtr<T>`三种类型。这套系统模仿C++11标准库的`std::shared_ptr`等语义，但针对UE5的多线程环境和内存追踪需求进行了重新实现，位于`Runtime/Core/Public/Templates/`目录下。

智能指针系统专门服务于**不继承UObject的C++类**。UObject体系已有自己的垃圾回收机制（GC）和`UPROPERTY`追踪，因此`TSharedPtr`等类型不应用于UObject子类——混用会导致引用计数与GC同时管理同一对象，引发双重释放崩溃。理解这条边界是正确使用UE5智能指针的前提。

虚幻引擎在UE4时代引入这套系统，目的是替代裸指针手动管理的`FRenderResource`、`FShader`等渲染子系统内部数据结构，以减少内存泄漏和野指针问题。UE5继续沿用并将其扩展到Nanite、Lumen等新渲染模块中。

---

## 核心原理

### TSharedPtr：共享所有权与引用计数

`TSharedPtr<T>`通过一个独立的**引用计数控制块（Reference Controller）**记录强引用数（Strong Reference Count）和弱引用数（Weak Reference Count）。当强引用计数降至0时，被管理对象立即析构；当弱引用计数也降至0时，控制块本身才被释放。

创建`TSharedPtr`的推荐方式是`MakeShared<T>(Args...)`，该函数将控制块和对象数据分配在同一块内存中，避免两次堆分配，性能优于`TSharedPtr<T>(new T(Args...))`形式。线程安全方面，UE5提供两种模式：`ESPMode::ThreadSafe`（使用原子操作，默认模式）和`ESPMode::NotThreadSafe`（使用普通整数，性能更高，仅限单线程场景）。

```cpp
// 推荐写法：一次内存分配
TSharedPtr<FMyData> Data = MakeShared<FMyData>(42);

// 访问原始指针
FMyData* RawPtr = Data.Get();
```

### TWeakPtr：观察而不持有

`TWeakPtr<T>`持有对控制块的弱引用，不增加强引用计数，因此不阻止对象被析构。在使用`TWeakPtr`所指向的对象前，必须调用`Pin()`方法将其提升为`TSharedPtr`，该操作会检查强引用计数是否仍大于0：

```cpp
TWeakPtr<FMyData> WeakData = Data; // 不增加强引用计数
if (TSharedPtr<FMyData> Pinned = WeakData.Pin())
{
    // 安全访问，Pinned保证对象在此作用域内存活
    Pinned->DoSomething();
}
```

`TWeakPtr`的典型用途是打破循环引用：若A持有B的`TSharedPtr`，B也持有A的`TSharedPtr`，则两者的强引用计数永远不会归零，造成内存泄漏。将其中一方改为`TWeakPtr`即可打破循环。

### TUniquePtr：独占所有权

`TUniquePtr<T>`语义等同于C++11的`std::unique_ptr`，保证同一时刻只有一个指针持有对象所有权。它**不可复制，只可移动**，转移所有权使用`MoveTemp()`（UE5的`std::move`等价宏）：

```cpp
TUniquePtr<FMyData> Owner = MakeUnique<FMyData>(100);
TUniquePtr<FMyData> NewOwner = MoveTemp(Owner); // Owner变为nullptr
```

`TUniquePtr`没有引用计数开销，当需要明确单一所有权时（如工厂模式返回对象、类成员独占资源）应优先选择它而不是`TSharedPtr`，后者的控制块内存开销和原子操作代价在高频分配场景中不可忽视。

---

## 实际应用

**渲染资源管理**：UE5的`FSceneRenderer`使用`TUniquePtr<FSceneRenderer>`在`FRendererModule::BeginRenderingViewFamily()`中创建渲染器实例，并通过`MoveTemp`传递给渲染线程，明确表达所有权转移语义。

**插件与子系统数据**：编写不继承`UObject`的插件内部服务类时，常用`TSharedPtr`搭配`TSharedFromThis<T>`基类（类似`std::enable_shared_from_this`），允许对象内部安全地获取指向自身的`TSharedPtr`：

```cpp
class FMyService : public TSharedFromThis<FMyService>
{
public:
    TSharedPtr<FMyService> GetSelf() { return AsShared(); }
};
```

**委托与回调防止悬空**：将`TWeakPtr`与`TDelegate`结合，注册回调时传入`TWeakPtr`，回调触发时通过`Pin()`检查对象是否仍然存活，避免回调执行时访问已析构的对象。

---

## 常见误区

**误区一：将TSharedPtr用于UObject子类**
将`TSharedPtr<AActor>`这类写法引入代码会导致Actor同时受引用计数和UE5 GC双重管理。GC在标记-清除阶段可能销毁Actor，而`TSharedPtr`的引用计数仍为1，随后引用计数归零时再次调用析构函数，产生崩溃。UObject子类应使用`TObjectPtr<T>`或裸指针搭配`UPROPERTY`。

**误区二：误以为TSharedPtr是线程安全的数据访问**
`ESPMode::ThreadSafe`仅保证**引用计数增减操作**本身的原子性，不保证所指向对象的数据成员在多线程访问时的安全。并发读写`TSharedPtr`所指向对象的字段仍需额外的互斥锁或原子变量保护。

**误区三：不必要地使用TSharedPtr代替TUniquePtr**
许多开发者习惯性地使用`TSharedPtr`管理所有堆对象，但若对象所有权确实是单一的，控制块的额外内存分配（通常16字节）和原子操作会累积成可观的开销。在每帧大量创建销毁临时数据结构的场景中，`TUniquePtr`或栈分配是更正确的选择。

---

## 知识关联

理解UE5智能指针需要先掌握**UObject系统**：正因为UObject已有完整的GC和反射机制，智能指针才被设计成专门服务于UObject体系之外的纯C++类。两套系统的边界划分是UE5内存管理架构的核心分水岭——`UPROPERTY`宏追踪的是UObject引用图，`TSharedPtr`控制块追踪的是非UObject对象的引用计数，二者互不干涉。

在渲染、音频、网络等子系统的源码阅读中，遇到`TSharedRef<T>`时需注意它是`TSharedPtr`的不可为空变体：构造时必须提供有效对象，且调用`.Get()`时无需空检查，适合表达"永远有效的共享引用"语义，常见于`IRenderer`等接口的传递中。