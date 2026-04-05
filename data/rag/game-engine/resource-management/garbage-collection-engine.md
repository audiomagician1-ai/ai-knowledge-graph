---
id: "garbage-collection-engine"
concept: "引擎垃圾回收"
domain: "game-engine"
subdomain: "resource-management"
subdomain_name: "资源管理"
difficulty: 3
is_milestone: false
tags: ["内存"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
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


# 引擎垃圾回收

## 概述

引擎垃圾回收（Garbage Collection，GC）是游戏引擎自动追踪并释放不再被任何对象引用的内存资源的机制。与操作系统级别的内存管理不同，引擎GC专门针对引擎管理对象（如UE5中的`UObject`体系或Unity中的托管堆对象）进行周期性扫描，找出"死亡"对象并回收其占用的内存。游戏引擎中的GC并不处理C++原生`malloc/free`分配的内存，它只管理引擎自己的对象系统。

Unity的GC机制基于Boehm-Demers-Weiser保守式垃圾回收器，从Unity 2021.2版本开始引入了增量式GC（Incremental GC）选项。UE5则采用完全不同的策略：Unreal引入了基于标记-清除（Mark-and-Sweep）算法的UObject GC系统，其GC间隔默认为60秒（可通过`gc.TimeBetweenPurgingPendingKillObjects`调整）。理解这两套系统的差异，对于避免游戏运行时的帧率尖刺（GC Spike）至关重要。

GC造成的帧率卡顿是移动端和主机游戏中最常见的性能问题之一。Unity老版本的Stop-the-World GC会暂停主线程数毫秒到数十毫秒，在60帧游戏中帧预算仅16.7ms的情况下，一次GC触发即可导致明显掉帧。

## 核心原理

### UE5的UObject GC机制

UE5的GC系统以`UObject`引用图为基础。引擎启动一个GC周期时，从一组"根对象"（Root Objects）出发，通过反射系统遍历所有标记了`UPROPERTY()`的指针字段，递归标记所有可达对象。未被标记的`UObject`实例进入`PendingKill`状态，随后在下一个GC周期被实际销毁并释放内存。

关键规则：普通C++指针指向的`UObject`**不会被GC追踪**，只有通过`UPROPERTY()`声明的指针或`TObjectPtr<T>`、`TWeakObjectPtr<T>`才在GC引用图中可见。因此，将`UObject`指针存入未标注`UPROPERTY`的`TArray`会导致该对象被意外回收，引发野指针崩溃。`AddToRoot()`方法可以将一个对象永久加入根集，防止其被GC回收。

UE5的GC默认运行在后台线程（Reachability Analysis阶段并行化），但最终的销毁阶段仍在游戏线程执行，通常耗时1–5ms，大型场景可能达到10ms以上。

### Unity的内存分区与GC触发条件

Unity的托管内存分为小对象堆（Small Object Heap）和大对象堆（Large Object Heap，LOH，阈值为85,000字节）。GC触发的主要条件有三：①托管堆某代（Generation 0/1/2）的分配超出阈值；②显式调用`System.GC.Collect()`；③内存压力达到系统警告级别。

Unity Boehm GC是非分代的（Non-generational），这意味着每次GC都扫描整个托管堆，而不像.NET CLR那样优先回收短寿命的Gen 0对象。这是Unity GC性能低于标准.NET的根本原因。启用增量式GC后，Unity将标记阶段拆分为多个时间片（每帧最多执行一定微秒数），通过`Scripting.GarbageCollector.incrementalTimeSliceNanoseconds`控制，默认值为3,000,000纳秒（3ms）。

### 引用类型与内存分配压力

在Unity中，每次在`Update()`中使用`new`创建引用类型（类实例、装箱值类型、`string`拼接、LINQ表达式等）都会向托管堆写入数据，逐渐触发GC。常见的隐性分配来源包括：`foreach`遍历某些集合（产生Enumerator对象）、格式化字符串、以及协程的`yield return`（每次执行都可能分配`IEnumerator`状态机对象）。使用Unity Profiler中的"Allocation"标记可以精确定位每帧的GC分配量（单位：Byte）。

## 实际应用

**对象池（Object Pooling）**是对抗GC压力最直接的手段。在Unity射击游戏中，子弹不应在发射时`Instantiate`、击中时`Destroy`，而应维护一个`Queue<GameObject>`池，通过`SetActive(false/true)`复用对象，从根本上消除频繁的托管内存分配。Unity 2021起内置了`UnityEngine.Pool.ObjectPool<T>`，提供线程安全的标准实现。

**UE5资产的异步加载与GC协调**是另一个典型场景。使用`FStreamableManager::RequestAsyncLoad()`加载资产后，必须持有返回的`TSharedPtr<FStreamableHandle>`，否则资产可能在下一个GC周期被回收。Epic官方推荐将长期使用的资产通过`UAssetManager`注册为强引用，避免软引用（`TSoftObjectPtr`）指向的资产被意外卸载。

在移动端Unity项目中，通常在关卡切换的Loading界面主动调用`System.GC.Collect()`并等待`Resources.UnloadUnusedAssets()`异步操作完成，将GC开销集中在非游戏时段，避免战斗流程中的卡顿。

## 常见误区

**误区一：在UE5中用裸指针存储UObject认为是安全的。** 很多开发者认为只要对象在逻辑上"还有用"就不会被GC。事实上，UE5 GC只认`UPROPERTY`标记的引用链，裸指针`AMyActor* Ptr`在GC眼中不存在。如果没有其他`UPROPERTY`引用链指向该对象，它会在下一个GC周期中被回收，导致`Ptr`成为悬空指针。正确做法是将其声明为`UPROPERTY() AMyActor* Ptr;`。

**误区二：Unity增量GC消除了所有GC停顿。** 增量GC将标记阶段分帧执行，但当堆中存在大量对象时，单帧仍可能超过时间片预算。更关键的是，增量GC在并发标记期间需要写屏障（Write Barrier），这给所有引用赋值引入了额外开销。对于LOH中的大对象，增量GC无法拆分其处理，Stop-the-World仍然会发生。

**误区三：`System.GC.Collect()`调用越多，内存越干净。** 频繁手动触发GC会强制将Gen 0/1对象提升至Gen 2（在标准.NET环境中），增加未来GC的扫描范围。在Unity的非分代GC中，频繁调用只会增加帧内停顿频率，正确的策略是集中在非敏感时机（如场景切换）调用一次。

## 知识关联

本概念直接建立在**资源管理概述**的基础之上——资源管理概述中讲述了引用计数（`TSharedPtr`/`TWeakPtr`）与手动管理的区别，GC正是这套体系在引擎托管对象层面的自动化延伸。`TWeakObjectPtr`在UE5中不阻止GC回收，而`TStrongObjectPtr`会阻止，这与资源管理概述中强/弱引用的定义完全对应。

在工程实践中，GC优化与**内存分析工具**密切相关：Unity的Memory Profiler（包）可以捕获托管堆快照，显示每个对象的引用链；UE5的`obj list`命令和Unreal Insights中的`GC`追踪通道可以列出当前存活的UObject数量及类型分布。掌握引擎GC原理后，开发者应进一步学习资产流送（Asset Streaming）策略，因为GC回收的是托管对象引用，而纹理/网格等非托管资产的实际卸载需要配合`ConditionalBeginDestroy()`（UE5）或`Resources.UnloadUnusedAssets()`（Unity）才能真正释放GPU内存。