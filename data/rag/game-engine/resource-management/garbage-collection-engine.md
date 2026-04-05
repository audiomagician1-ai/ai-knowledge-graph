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
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 引擎垃圾回收

## 概述

引擎垃圾回收（Garbage Collection，GC）是游戏引擎自动追踪并释放不再被任何对象引用的内存资源的机制。与操作系统级别的内存管理不同，引擎GC专门针对引擎管理对象（如UE5中的`UObject`体系或Unity中的托管堆对象）进行周期性扫描，找出"死亡"对象并回收其占用的内存。UE5的GC**不处理**C++原生`malloc/free`分配的内存，它只管辖`UObject`继承体系下的对象图；Unity的GC则仅管理Mono/IL2CPP运行时中的托管堆（Managed Heap），C++层的`UnityEngine.Object`（纹理、网格等原生资源）须通过`Resources.UnloadUnusedAssets()`或`AssetBundle.Unload(true)`手动释放。

GC造成的帧率卡顿（GC Spike）是移动端和主机游戏中最高频的性能投诉来源之一。在60帧游戏中，每帧预算仅16.7ms；若一次Stop-the-World GC暂停主线程20ms，玩家将直观感受到画面冻结。Unity旧版Boehm GC在生产环境中可造成30ms甚至更长的单次暂停，而UE5默认配置下GC的游戏线程耗时通常在1–5ms，大型开放世界场景可超过10ms（参见《Unreal Engine 5 Performance Guide》，Epic Games, 2022）。

---

## 核心原理

### UE5的UObject GC机制：标记-清除与并行可达性分析

UE5的GC采用**标记-清除（Mark-and-Sweep）**算法，以`UObject`引用图为操作对象。每次GC周期分为三个阶段：

1. **可达性分析（Reachability Analysis）**：从"根集合"（Root Set）出发，通过引擎反射系统遍历所有被`UPROPERTY()`声明的指针字段，递归标记所有可达的`UObject`实例。该阶段自UE4.18起支持多线程并行化，可利用工作线程（Worker Threads）大幅缩短耗时。
2. **标记清理（Purge/Sweep）**：所有未被标记的`UObject`首先进入`PendingKill`状态（布尔标志位`EObjectFlags::RF_PendingKill`置位），随后在清理阶段调用`ConditionalBeginDestroy()`销毁对象并释放内存。该阶段**必须在游戏线程执行**，是GC暂停的主要来源。
3. **增量销毁**：对象的实际内存释放可在后续多帧分摊，由`GExitPurge`和`GIncrementalDestroyGarbage`控制。

GC的默认间隔通过控制台变量`gc.TimeBetweenPurgingPendingKillObjects`配置，默认值为**60秒**。在角色密集的关卡中，若每帧生成大量短生命周期的`UObject`（如每帧`NewObject<UParticleSystemComponent>()`），可将该值调小至30秒，但需权衡更频繁GC的开销。

**关键规则**：裸C++指针指向的`UObject`不在GC引用图中，只有以下三种方式声明的指针才被GC追踪：
- `UPROPERTY()` 修饰的成员指针
- `TObjectPtr<T>`（UE5新增，替代裸指针，兼具安全检查）
- `TArray<TObjectPtr<T>>` 或带 `UPROPERTY()` 的容器

将`UObject*`存入未加`UPROPERTY()`的`TArray<UObject*>`是最常见的野指针崩溃来源——GC会在下一个周期回收该对象，而数组中的指针变成悬空指针（Dangling Pointer）。

### Unity的内存分区与GC触发机制

Unity的托管内存由Boehm-Demers-Weiser保守式垃圾回收器（Boehm GC，Hans Boehm et al., 1988）管理。其核心特征是**非分代（Non-generational）**：每次GC都扫描整个托管堆，而非像.NET CLR那样优先回收短命的Generation 0对象。这是Unity托管GC性能低于标准.NET 6+运行时的根本原因。

托管堆分为两个区域：
- **小对象堆（SOH, Small Object Heap）**：分配大小 < 85,000字节的对象
- **大对象堆（LOH, Large Object Heap）**：分配大小 ≥ 85,000字节的对象，在Unity中**不参与压缩**，长期运行会产生内存碎片

GC触发的三类主要条件：
1. SOH分配超出当前代阈值（Unity Boehm默认约256KB起步，动态扩展）
2. 显式调用`System.GC.Collect()`（应避免在帧循环内调用）
3. 系统内存压力触发OS层警告（iOS/Android低内存通知）

从**Unity 2021.2**起，增量式GC（Incremental GC）作为正式功能发布（Project Settings → Player → Use Incremental GC）。增量GC将标记阶段拆分为多个时间片，每帧最多执行 `Scripting.GarbageCollector.incrementalTimeSliceNanoseconds` 纳秒的GC工作，默认值为**3,000,000 ns（3ms）**。启用后，单帧GC暂停从"一次性30ms"分散为"连续多帧各3ms"，显著降低尖刺幅度，但总GC时间略有增加。

### 引用类型分配压力与零分配编程模式

托管GC的根本驱动力是**堆分配速率（Allocation Rate）**。在Unity中，以下操作会在托管堆产生隐蔽分配：

| 操作 | 每次分配字节数（近似） |
|------|----------------------|
| `foreach` 遍历非泛型 `IEnumerable` | 24–40字节（枚举器装箱） |
| 字符串拼接 `"HP: " + hp` | 与字符串长度相关，通常50–200字节 |
| LINQ表达式（如`.Where().Select()`） | 每个委托约56字节 |
| `GetComponent<T>()` 在旧版Unity | 0字节（已优化，但需验证版本） |
| `new Vector3[]` 长度100 | 约824字节 |

零分配目标的实践手段：使用`StringBuilder`替代字符串拼接；用`List<T>.Clear()`复用列表而非重新`new`；以`Span<T>`或`NativeArray<T>`（Unity Collections包）在非托管内存操作批量数据；对象池（`UnityEngine.Pool.ObjectPool<T>`，Unity 2021+）复用频繁创建销毁的组件实例。

---

## 关键公式与性能指标

GC开销的核心度量是**单次GC耗时**与**GC触发频率**的乘积，可用下式估算每秒GC占用的帧时间比例：

$$
R_{GC} = \frac{T_{gc} \times F_{gc}}{1000} \times 100\%
$$

其中 $T_{gc}$ 为单次GC平均耗时（ms），$F_{gc}$ 为每秒GC触发次数，$R_{GC}$ 为GC占用帧时间的百分比。例如，$T_{gc} = 5\text{ms}$，$F_{gc} = 2\text{次/秒}$，则 $R_{GC} = 1\%$，在60帧预算中消耗约0.6帧，属于可接受范围；若 $T_{gc} = 20\text{ms}$，$F_{gc} = 3$，则 $R_{GC} = 6\%$，每秒损失约3.6帧，必须优化。

在UE5中，可通过以下控制台命令实时监控GC耗时：

```
stat gc
gc.DumpReachabilityAnalysisStats 1
```

在Unity中，使用 **Memory Profiler 1.1.0+**（Package Manager安装）或内置Profiler的"GC Alloc"列精确定位每帧分配热点。

---

## 实际应用与优化策略

### UE5 GC调优实践

**案例**：某开放世界项目在角色密集区域出现每分钟一次、持续8ms的GC卡顿。排查步骤如下：

1. 运行 `stat gc`，确认 `GC.PurgeGarbage` 耗时峰值为8ms，触发间隔恰好60秒——符合默认GC周期。
2. 在 `DefaultEngine.ini` 中将间隔调整为30秒，将单次GC对象数量减半，耗时降至4ms。
3. 使用 `gc.VerifyNotReachableObjects 1` 检查是否存在意外根引用导致大量对象无法回收。
4. 对高频创建的子弹`UObject`改用对象池，通过`UGameplayStatics::SpawnEmitterAtLocation`替代每次`NewObject`，使每GC周期待回收对象数从约2000个降至150个，耗时进一步降至0.8ms。

**`AddToRoot()` 的正确使用**：该方法将对象永久加入根集，GC永不回收。适用场景：单例管理器（在游戏生命周期内始终存活的`UGameInstance`子系统）。滥用此接口会造成内存泄漏，必须配套调用`RemoveFromRoot()`。

```cpp
// 正确：游戏启动时注册全局数据表，退出时手动清理
UDataTable* GlobalTable = NewObject<UDataTable>();
GlobalTable->AddToRoot();

// 退出或关卡卸载时
GlobalTable->RemoveFromRoot();
GlobalTable = nullptr;
```

### Unity GC优化：对象池与增量GC配合使用

**案例**：某手游射击场景每秒生成60颗子弹，每颗子弹挂载`BulletController`（包含3个`string`类型日志字段），导致每帧托管分配约14KB，每3秒触发一次Full GC（约18ms暂停）。

优化方案：
1. 启用增量GC，将18ms单次暂停分散为6帧×3ms。
2. 用`UnityEngine.Pool.ObjectPool<BulletController>`实现子弹复用，将每帧分配降至 < 1KB。
3. 将`string`日志字段改为`int`枚举标志位，彻底消除该字段的堆分配。

优化后GC触发频率从0.33次/秒降至约0.02次/秒（每50秒一次），玩家可感知的卡顿完全消失。

```csharp
// Unity对象池使用示例（Unity 2021+）
private ObjectPool<BulletController> _bulletPool = new ObjectPool<BulletController>(
    createFunc: () => Instantiate(bulletPrefab).GetComponent<BulletController>(),
    actionOnGet: (b) => b.gameObject.SetActive(true),
    actionOnRelease: (b) => b.gameObject.SetActive(false),
    actionOnDestroy: (b) => Destroy(b.gameObject),
    collectionCheck: false,
    defaultCapacity: 64,
    maxSize: 256
);

// 获取子弹
BulletController bullet = _bulletPool.Get();
// 归还子弹（替代Destroy）
_bulletPool.Release(bullet);
```

---

## 常见误区

**误区1：UE5中用裸指针持有UObject就足够安全**
错误原因：未加`UPROPERTY()`的`UObject*`成员指针对GC不可见，GC会在60秒后回收该对象，导致下次访问触发访问违例（Access Violation）。正确做法是始终用`UPROPERTY()`或`TObjectPtr<T>`声明UObject成员指针，或对栈上临时引用使用`TStrongObjectPtr<T>`（UE5.1+）。

**误区2：Unity中调用`System.GC.Collect(0)`只回收Gen 0开销很小**
错误原因：Unity Boehm GC是**非分代**的，调用`GC.Collect(0)`实际上仍会触发**全堆扫描**，与`GC.Collect(2)`耗时几乎相同。应避免在任何帧循环路径中手动触发GC，必要时放在加载过渡黑屏阶段执行。

**误区3：增量GC能解决所有Unity GC问题**
增量GC仅分散了**标记阶段**的耗时，清理（Sweep）和内存碎片整理仍可能产生集中暂停。对于LOH（≥85,000字节）上的大型数组，增量GC无法分散其回收开销，必须从源头减少大型托管分配。

**误区4：`Resources.UnloadUnusedAssets()`等同于GC**
该函数释放的是Unity**原生层**（C++）的资源（纹理、音频剪辑等），与托管堆GC是两套独立机制。调用它不会触发托管GC，反之亦然。两者需分别管理。