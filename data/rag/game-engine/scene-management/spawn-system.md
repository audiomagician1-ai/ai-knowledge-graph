---
id: "spawn-system"
concept: "生成系统"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 2
is_milestone: false
tags: ["生成"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 生成系统

## 概述

生成系统（Spawning System）是游戏引擎场景管理模块中负责在运行时动态创建和销毁游戏对象的机制。具体而言，它管理 Actor 或 Prefab 从模板定义到具体实例的转化过程，以及实例完成使命后的内存回收流程。在 Unreal Engine 中，这一操作通过 `SpawnActor<T>()` 函数实现；在 Unity 中，对应的接口是 `Object.Instantiate()` 与 `Object.Destroy()`。

生成系统的概念随着面向对象游戏引擎的发展而成熟，早期游戏（如1990年代的DOS游戏）通常使用静态数组预分配固定数量的敌人或子弹对象。到2000年代，引擎开始支持真正的动态实例化，但频繁调用 `new` 与 `delete`（或其脚本语言等价物）带来了垃圾回收的性能峰值问题。现代生成系统因此几乎必然与**对象池（Object Pool）**技术耦合，以摊平内存分配的开销。

理解生成系统直接影响游戏的运行时帧率稳定性。一个射击游戏每秒可能生成数十枚子弹，若每次均分配新内存并在击中后立即释放，GC（垃圾回收器）压力会导致帧时间出现明显的毛刺（Spike）。正确配置生成系统与对象池可将此类毛刺压缩到 0.1ms 以下的可接受范围。

---

## 核心原理

### 实例化：从模板到对象

实例化是将 Prefab（Unity 术语）或 Actor 蓝图/C++ 类（Unreal 术语）复制为独立运行时对象的过程。在内存层面，这包含以下步骤：

1. **分配内存**：在堆上为新对象申请与模板大小匹配的内存块。
2. **复制组件树**：将模板的组件层级（Transform、Mesh、Collider 等）深拷贝到新实例。
3. **初始化生命周期**：调用对象的初始化回调，例如 Unity 的 `Awake()` → `OnEnable()` → `Start()` 调用链，或 Unreal 的 `PostInitializeComponents()`。
4. **注册到场景**：将对象注册进引擎的场景图（Scene Graph），使其参与渲染、物理和逻辑更新循环。

实例化时必须提供的最小参数集通常包括：**位置（Position）**、**旋转（Rotation）**，以及可选的**父节点（Parent Transform）**。在 Unity 中，签名为：

```csharp
GameObject.Instantiate(prefab, position, rotation, parent);
```

### 销毁与回收

销毁是实例化的逆过程，但其顺序与实例化相反：

1. 调用销毁回调（Unity 的 `OnDisable()` → `OnDestroy()`）。
2. 从场景图中注销，停止参与更新循环。
3. 解除对其他对象的引用，触发引用计数归零。
4. 释放内存（或归还对象池）。

`Object.Destroy(obj)` 在 Unity 中并非立即执行，而是标记对象为"待销毁"，在当前帧末尾的清理阶段统一处理。这意味着同一帧内对已调用 `Destroy()` 的对象调用方法不会立即报错，但访问其字段可能返回意外值。

### 对象池模式与生成系统的结合

对象池的核心数学逻辑是：维护一个大小为 `N` 的空闲队列（Free Queue），生成时从队列头部取出并激活，回收时禁用并压回队列尾部，避免真实的内存分配与释放。

- 队列为空时的策略有两种：**扩容**（动态增大池子上限，适合爆发性场景）和**拒绝生成**（适合有明确上限的子弹或粒子系统）。
- 预热（Warm-up）是指在游戏加载阶段预先实例化 `N` 个对象并立即禁用，避免首次触发时的延迟。Unity 的 `ObjectPool<T>` 类（Unity 2021 起内置于 `UnityEngine.Pool` 命名空间）提供了 `prewarm` 参数直接支持此功能。

### 生成点（Spawn Point）管理

生成系统通常与场景中的生成点对象配合使用。生成点存储一组候选位置与旋转，生成系统通过策略选择具体位置（轮询、随机、最近玩家等）。生成点本身是轻量的空 Actor/GameObject，不携带 Mesh 组件，其 Transform 仅作为坐标载体。

---

## 实际应用

**射击游戏子弹系统**：以一款枪战游戏为例，玩家每分钟可能射出 600 发子弹（10发/秒）。若不使用对象池，每秒 10 次 `Instantiate` + 10 次 `Destroy` 调用会在 Unity 的 Mono 堆上累积约 80–200 字节/次的碎片。配置一个容量为 30 的子弹对象池，并在子弹飞出屏幕或碰撞后调用 `pool.Release(bullet)` 而非 `Destroy(bullet)`，可将 GC Alloc 降至 0 bytes/frame。

**波次敌人生成**：塔防游戏中，敌人按波次批量生成。生成系统读取一张 ScriptableObject 配置表（如 `WaveData`），按时间间隔（如每 0.5 秒一个）从对应敌人类型的对象池取出实例，并将其注册到 AI 管理器。波次结束后，所有存活的敌人被强制回收回池，而非销毁，以备下一关复用。

**程序化地图生成**：地牢类游戏在运行时动态生成房间 Prefab。由于房间 Prefab 体积较大（含 Tilemap、Light、Trigger），通常不适合对象池，此类场景仍使用直接 `Instantiate`，但会将生成操作分散到多帧（通过协程或 `IEnumerator`）以避免单帧卡顿，这是另一种控制生成开销的策略。

---

## 常见误区

**误区一：认为 `Destroy()` 立即释放内存**
许多初学者在调用 `Destroy(enemy)` 后的同一帧继续引用 `enemy` 的属性，导致 `NullReferenceException`。正确理解是：`Destroy()` 仅在当前帧末统一执行，且销毁后该变量仍持有一个 Unity 的"假空"引用（`== null` 返回 true，但 C# 层面的 object 不为 null），因此必须手动将引用置为 `null` 或使用 null 合并运算符做安全判断。

**误区二：对所有对象类型都套用对象池**
对象池适用于生命周期短、创建频繁、结构一致的对象（子弹、粒子、UI 提示）。对于生命周期长（如场景中的 Boss）、结构复杂（含大量子组件的角色）或数量极少（全程不超过 5 个）的对象，对象池的维护开销（激活/禁用回调、重置状态逻辑）反而高于直接 `Instantiate`/`Destroy` 的成本。

**误区三：混淆 Prefab 实例化与场景加载**
`Instantiate(prefab)` 是在已加载场景内动态添加对象，而 `SceneManager.LoadScene()` 是整场景替换。两者均会触发对象的 `Awake` 和 `Start`，但 `Instantiate` 出来的对象不会在场景切换时自动持久化，除非调用 `DontDestroyOnLoad()`——这是独立于生成系统之外的跨场景生命周期管理功能。

---

## 知识关联

生成系统直接依赖**场景管理概述**中建立的场景图（Scene Graph）概念：`Instantiate` 的本质是向场景图插入新节点，`Destroy` 是移除节点。理解场景图的层级结构（父子关系、Transform 继承）是正确设置 `parent` 参数、避免对象生成后坐标错乱的前提。

生成系统的性能优化实践（对象池）会延伸到**内存管理**与**性能分析（Profiling）**主题，Unity Profiler 的 Memory 视图中可以直接观察 `GC.Alloc` 是否因未正确使用对象池而产生，这是验证生成系统配置是否正确的标准方法。此外，生成系统与**物理系统**紧密协作——生成带 Collider 的对象时，物理引擎必须在同帧将其纳入碰撞宽相（Broad Phase），这也是为什么大量同帧生成会造成物理线程的额外开销。