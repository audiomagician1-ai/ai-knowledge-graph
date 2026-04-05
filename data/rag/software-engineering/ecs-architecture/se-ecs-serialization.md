---
id: "se-ecs-serialization"
concept: "ECS序列化"
domain: "software-engineering"
subdomain: "ecs-architecture"
subdomain_name: "ECS架构"
difficulty: 3
is_milestone: false
tags: ["持久化"]

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


# ECS序列化

## 概述

ECS序列化是指将Entity-Component-System架构中的世界状态（World）转换为可存储或传输的数据格式，以及从该格式还原世界状态的完整过程。与面向对象系统的序列化不同，ECS序列化的对象不是带有方法的对象实例，而是纯数据的Archetype块（Chunk）和Entity-Component的稀疏映射关系。

该技术最早随Unity DOTS（Data-Oriented Technology Stack）的发展在2018年前后被广泛讨论，Unity的`com.unity.entities`包专门提供了`SerializeUtility`类来处理ECS世界的序列化。其根本挑战在于：ECS中的Entity ID本质上是一个整数句柄（Handle），序列化时必须解决跨存档的ID重映射问题，否则组件中存储的EntityReference在反序列化后将指向错误的目标。

ECS序列化的主要应用场景包括三类：游戏存档（Save/Load）、场景导入导出（SubScene）以及网络同步的World快照（Snapshot）。每类场景对序列化的完整性、速度和大小有不同的取舍要求，例如网络快照要求增量序列化以减少带宽，而存档则要求完整性优先。

## 核心原理

### Entity ID 重映射机制

ECS世界中每个Entity由一个`(Index, Version)`二元组唯一标识，Index是数组下标，Version防止"僵尸引用"。序列化时，原始Index不能直接写入存档，因为反序列化到新World时，相同Index的槽位可能已被占用。

标准做法是构建一个**重映射表（Remapping Table）**：序列化时为每个Entity分配一个连续的序列化ID（从0开始的稳定整数），反序列化时再将序列化ID映射回新World分配的真实Entity。Unity的`EntityRemapUtility.CalculateEntityRemapArray`函数专门完成这一工作，其输出是一个`NativeArray<EntityRemapUtility.EntityRemapInfo>`结构数组。

### Archetype与Chunk的二进制布局

ECS数据在内存中以Archetype为单位组织：相同组件组合的Entity共享一个Archetype，并被密集存储在固定大小（Unity中为16KB）的Chunk中。序列化时，逐Chunk读取数据效率最高，因为同一Chunk内的Component数据是连续内存布局（SoA，Structure of Arrays）。

序列化输出通常包含以下段：
1. **Archetype定义段**：记录每个Archetype包含的Component类型列表（以StableTypeHash标识，而非运行时TypeIndex）
2. **Chunk数据段**：按Archetype分组存储的原始Component二进制数据
3. **Entity映射段**：Entity到Archetype槽位的索引信息

使用StableTypeHash（基于组件类型的完整限定名计算的64位哈希）而非运行时TypeIndex，是保证存档在代码版本迭代后仍可读取的关键设计。

### SharedComponent与ManagedComponent的特殊处理

普通的`IComponentData`（值类型）可以直接二进制拷贝，但`ISharedComponentData`和`IManagedComponent`需要特殊处理。SharedComponent在Chunk中只存储一个索引，真实数据存放在World级别的SharedComponentStore中；ManagedComponent（如含有string或数组的组件）存储在GC堆上，无法直接memcpy。

对这两类组件，序列化框架通常采用反射或手动实现`IComponentData`的`BlobAsset`替代方案。Unity官方推荐对需要序列化的可变长数据使用`BlobAssetReference<T>`，因为BlobAsset本身是不可变的连续内存块，序列化为字节数组后可以通过`BlobAssetStore`统一管理，避免重复存储相同内容的BlobAsset。

### 增量快照与完整快照

完整快照（Full Snapshot）序列化当前World的所有Entity和Component，适合存档系统；增量快照（Delta Snapshot）只记录自上一帧/上一快照以来发生变化的Component，依赖`ChangeVersion`机制——ECS框架在每次System写入某个ComponentType时递增该Chunk的`ChangeVersion`值，序列化器通过比较`ChangeVersion`与上次快照时的版本号来判断是否需要重新序列化该Chunk。

## 实际应用

**SubScene导入导出（Unity DOTS）**：Unity编辑器将一个Scene中的GameObject转换为ECS Entity时，会调用`GameObjectConversionSystem`并最终通过`SerializeUtility.SerializeWorld`将结果写入`.entities`二进制文件。运行时通过`SceneSystem.LoadSceneAsync`异步加载，反序列化后直接Instantiate到主World，这使得场景加载速度比传统GameObject加载快3-10倍（取决于Entity数量）。

**游戏存档**：一个典型的存档系统需要两步：先用`EntityQuery`筛选出带有`Saveable`标记组件的Entity子集，再对该子集序列化。这避免了将临时性Entity（如子弹、特效）写入存档。反序列化时需要先销毁旧的Saveable Entity，再加载存档数据，Entity重映射在此步骤中自动处理。

**网络状态同步**：在帧同步或状态同步架构中，服务器每帧将World序列化为快照发送给客户端。每个快照大小通常压缩到几十KB以内，可使用LZ4算法对Chunk数据段进行压缩，因为同类型Component的连续二进制数据具有高度重复性，压缩比通常达到3:1以上。

## 常见误区

**误区一：认为Entity ID在存档中是稳定的**。很多初学者直接将`Entity.Index`存入存档中作为引用，重新加载后用该Index查找Entity，导致引用到错误Entity或崩溃。正确做法是在存档数据中用序列化ID（或业务层的GUID组件）标识Entity，反序列化完成后通过重映射表建立ID到Entity的索引。

**误区二：将所有Component都标记为可序列化**。System运行时会创建大量临时性Component（如`LocalToWorld`矩阵、`PhysicsVelocity`），这些数据在下一帧System执行后会被完全重新计算。把它们也序列化会使存档体积膨胀，且反序列化后System会立即覆盖这些值，没有意义。应区分"源数据组件"和"派生数据组件"，只序列化前者。

**误区三：认为ECS序列化天然支持版本兼容**。当添加或删除某个Component类型时，旧存档中包含该类型的Archetype定义在反序列化时会因StableTypeHash找不到对应类型而失败。需要显式实现迁移逻辑（Migration），在反序列化管线中检测缺失类型并补填默认值，这与传统JSON存档的字段缺失处理不同，需要在Archetype粒度而非字段粒度进行处理。

## 知识关联

ECS序列化建立在对ECS基本数据结构的理解之上——Archetype、Chunk和ComponentType是序列化数据的基本单位，理解Chunk的16KB内存布局才能理解为何按Chunk序列化效率最高。Entity的`(Index, Version)`生命周期机制直接决定了重映射表存在的必要性。

在具体实现中，ECS序列化与`IJobChunk`/`IJobEntityBatch`紧密相关：高性能序列化往往在Job中并行处理多个Chunk，利用Burst Compiler将序列化逻辑编译为SIMD指令。BlobAsset系统是处理不可变引用数据序列化的标准配套工具，SubScene系统则是ECS序列化在场景管理层面的完整应用案例。