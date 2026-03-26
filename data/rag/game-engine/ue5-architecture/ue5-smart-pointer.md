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
quality_tier: "B"
quality_score: 45.8
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

# UE5智能指针

## 概述

UE5智能指针是Unreal Engine提供的一套用于管理**非UObject**堆内存的模板类工具，包含`TSharedPtr`、`TWeakPtr`、`TUniquePtr`和`TSharedRef`四种类型。由于UObject体系已有垃圾回收（GC）负责内存管理，智能指针专门服务于那些继承自`FBase`或普通C++类的对象，填补了GC无法覆盖的内存安全空白。

这套智能指针系统由Epic Games随UE4引入，并沿用至UE5。其设计参考了C++11标准库的`std::shared_ptr`，但刻意不与标准库互通，原因是Epic需要在引擎内部提供线程安全模式的可选控制、更细粒度的调试追踪，以及避免不同平台STL实现不一致带来的问题。

在实际开发中，当你的数据结构（如自定义的渲染数据、音频缓冲、Slate UI控件）不适合继承`UObject`时，智能指针是防止内存泄漏和悬垂指针的首选方案。Slate控件体系大量使用`TSharedPtr<SWidget>`作为控件树的节点持有方式，是引擎源码中智能指针最集中的应用场景。

---

## 核心原理

### TSharedPtr：共享所有权与引用计数

`TSharedPtr<T>`通过**引用计数**（Reference Count）实现共享所有权。其内部维护两个计数器：**强引用计数**（Strong Reference Count）和**弱引用计数**（Weak Reference Count）。当强引用计数归零时，所指对象被销毁；当弱引用计数也归零时，存储计数器本身的控制块（ReferenceController）才被释放。

创建`TSharedPtr`的推荐方式是`MakeShared<T>()`，而非`TSharedPtr<T>(new T())`。`MakeShared`将对象本体与引用计数控制块分配在**同一块连续内存**中，减少一次堆分配，提升缓存局部性。

`TSharedPtr`提供两种线程安全模式，通过第二个模板参数`ESPMode`指定：
- `ESPMode::ThreadSafe`：使用原子操作更新引用计数，多线程安全但有性能开销。
- `ESPMode::NotThreadSafe`（默认）：使用普通整数，适合单线程场景，性能更高。

```cpp
TSharedPtr<FMyData, ESPMode::ThreadSafe> ThreadSafePtr = MakeShared<FMyData, ESPMode::ThreadSafe>();
```

### TWeakPtr：观察而不占有

`TWeakPtr<T>`持有弱引用，不增加强引用计数，因此不阻止对象销毁。使用前必须调用`Pin()`将其提升为`TSharedPtr`，若对象已被销毁则返回空指针。这一机制消除了悬垂指针问题——你永远无法通过`TWeakPtr`直接访问一个已销毁的对象。

```cpp
TWeakPtr<FMyData> WeakRef = SharedRef;
if (TSharedPtr<FMyData> Pinned = WeakRef.Pin())
{
    // 安全访问
}
```

`TWeakPtr`的典型用途是**打破循环引用**：若对象A持有B的`TSharedPtr`，B也持有A的`TSharedPtr`，两者引用计数永不归零，产生内存泄漏。解决方法是让其中一方改为`TWeakPtr`。

### TUniquePtr：独占所有权

`TUniquePtr<T>`代表对对象的**唯一所有权**，不可复制，只能通过`MoveTemp()`（即C++的`std::move`在UE中的等价宏）转移所有权。当`TUniquePtr`离开作用域，所指对象自动析构，没有引用计数开销，运行时成本等同于原始指针。

```cpp
TUniquePtr<FMyData> Owner = MakeUnique<FMyData>(42);
TUniquePtr<FMyData> NewOwner = MoveTemp(Owner); // Owner变为空
```

对于明确只需单一所有者的资源（如RAII文件句柄、临时计算缓冲），`TUniquePtr`是三者中性能最优的选择。

### TSharedRef：非空的共享引用

`TSharedRef<T>`与`TSharedPtr`行为相同，但**保证永不为空**，不提供`IsValid()`检查，访问时无需空指针判断。Slate的`SNew()`宏返回的即是`TSharedRef<SWidget>`，在控件树构建中强制保证每个节点有效。

---

## 实际应用

**Slate UI控件管理**是最典型的应用场景。所有继承自`SWidget`的控件（`SButton`、`STextBlock`等）均通过`TSharedRef`持有，父控件通过`TSharedPtr<SWidget>`存储子控件列表。`SNew(SButton)`宏在内部调用`MakeShared`，返回`TSharedRef<SButton>`。

**插件与模块中的子系统**若不适合用`UObject`管理生命周期，常以`TUniquePtr`存储在模块类中。例如自定义渲染器可写为：

```cpp
class FMyRenderModule : public IModuleInterface
{
    TUniquePtr<FMyRenderer> Renderer;
public:
    virtual void StartupModule() override
    {
        Renderer = MakeUnique<FMyRenderer>();
    }
};
```

**跨线程数据传递**中，将`TSharedPtr<T, ESPMode::ThreadSafe>`从游戏线程传递给渲染线程是常见模式，引用计数的原子性保证两端都能安全持有或释放数据。

---

## 常见误区

**误区一：对UObject使用智能指针**

`TSharedPtr<AActor>`是错误用法。UObject的生命周期由GC管理，GC不感知智能指针的引用计数。当GC决定回收该UObject时，引用计数仍不为零，导致双重释放或访问已回收内存。对UObject应使用`TWeakObjectPtr<AActor>`或让其被`UPROPERTY()`修饰的裸指针持有。

**误区二：混用线程安全模式**

将`ESPMode::NotThreadSafe`的`TSharedPtr`传递给工作线程操作，会导致引用计数的数据竞争，出现计数错误进而引发崩溃或内存泄漏。两种模式的指针类型**不能互相赋值**，编译器会报错提醒。

**误区三：忽略循环引用**

两个`TSharedPtr`互相持有对方时，析构永远不会触发。在设计双向关联的数据结构（如双向链表节点、父子控件回调）时，必须明确哪一方持有弱引用。可借助内存分析工具或`TSharedPtr::GetSharedReferenceCount()`在调试阶段检查计数异常。

---

## 知识关联

**与UObject系统的边界**：UObject使用GC（基于标记-清除算法），智能指针使用引用计数，两套机制相互独立。选择哪种取决于对象是否需要`UCLASS`反射、蓝图支持、网络复制等UObject特性——需要这些特性则用UObject，否则可用智能指针获得更轻量的内存管理。

**与原始指针的取舍**：引擎性能敏感路径（如每帧高频调用的渲染循环）有时仍使用原始指针配合手动生命周期管理，以避免引用计数的原子操作开销。`TUniquePtr`在此场景中是从裸指针向安全代码迁移的最小代价选项，因为它运行时零开销。

**Slate框架的深度依赖**：学习Slate开发时，`TSharedPtr`/`TSharedRef`/`TWeakPtr`的熟练运用是前提条件，因为整个Slate控件树的构建、持有与事件回调绑定均建立在这套智能指针体系之上，而非UObject/GC体系。