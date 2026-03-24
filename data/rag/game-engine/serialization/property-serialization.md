---
id: "property-serialization"
concept: "属性序列化"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 3
is_milestone: false
tags: ["反射"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 属性序列化

## 概述

属性序列化（Property Serialization）是游戏引擎中利用反射系统自动读写对象数据的机制。与手写序列化代码不同，属性序列化通过在字段声明时附加元数据标记（如 Unreal Engine 的 `UPROPERTY()` 宏），让引擎的反射系统在运行时自动识别哪些字段需要被保存或加载，从而免去开发者手动编写每个字段的读写逻辑。

Unreal Engine 4 的属性序列化系统以 `FArchive` 类为核心，于 UE 早期版本即已存在，并在 UE4.0（2014年发布）后随蓝图系统的成熟而广泛用于关卡保存、网络同步和资产序列化三个主要场景。Unity 则采用 `[SerializeField]` 特性标注私有字段，由 `UnityEngine.SerializeReference` 处理多态引用，两套系统的设计思路虽有差异，但驱动原理相同——反射驱动。

属性序列化之所以重要，在于它把"哪些数据需要持久化"的决策权从运行时代码转移到了类型定义阶段。一旦字段被正确标注，引擎序列化器、编辑器面板、网络复制层可以共享同一份元数据，避免同一信息在多处重复声明而导致的不一致错误。

## 核心原理

### 反射元数据的生成与查询

以 Unreal Engine 为例，编译阶段的 Unreal Header Tool（UHT）扫描 `.h` 文件中的 `UPROPERTY()` 宏，为每个被标注的字段生成一个 `FProperty` 对象，存入该类对应的 `UClass` 元对象中。序列化时，代码调用 `UClass::SerializeTaggedProperties()`，该函数遍历 `UClass` 内所有 `FProperty`，对每个属性依次调用 `FProperty::SerializeItem()`，将字段值写入或读取自 `FArchive` 流。整个过程无需开发者编写任何字段级别的读写语句。

`FProperty` 携带字段名称、字节偏移量（Offset_Internal）、大小、属性标志（EPropertyFlags）等信息。序列化器通过 `Offset_Internal` 直接定位对象内存中的字段地址，因此性能开销主要在元数据遍历而非内存访问。

### 属性标志（Property Flags）的控制作用

`UPROPERTY()` 宏接受一系列说明符，这些说明符最终映射为 `EPropertyFlags` 枚举位掩码，精确控制序列化行为：

- `SaveGame`：字段被 `USaveGame` 子系统序列化，用于存档文件。  
- `Transient`：字段**不**写入磁盘，仅存在于运行时内存。  
- `Replicated`：字段参与网络复制，但不一定写入本地存档。  
- `SkipSerialization`：完全跳过属性序列化，常用于缓存字段。

例如，一个角色的当前 HP 应标注 `SaveGame`，而临时的 AI 感知结果应标注 `Transient`，两者共存于同一类中但序列化路径完全不同，这种细粒度控制是属性序列化的核心价值。

### 标签化序列化（Tagged Serialization）与版本兼容

Unreal 的属性序列化采用"名称-值"标签格式，每个字段在流中以字段名（FName）作为键写入，而非按固定字节偏移排列。这意味着当类新增或删除字段时，旧存档仍可加载：引擎按名称匹配字段，找不到对应标签则跳过，新增字段则使用默认值填充。这一机制依赖 `FArchive` 的 `ArVer`（Archive Version）字段配合 `CustomVersions` 表实现跨版本兼容，开发者可通过 `FCustomVersionRegistration` 注册自定义版本号（通常为 GUID + 整数版本），在序列化代码中做版本分支处理。

## 实际应用

**关卡编辑器属性面板**：编辑器的 Details 面板直接读取 `UClass` 的 `FProperty` 列表渲染输入控件，标注了 `EditAnywhere` 的属性自动出现在面板中，修改后通过同一属性序列化路径写入 `.uasset` 文件。开发者在 Actor 类中新增一行 `UPROPERTY(EditAnywhere, SaveGame) float MoveSpeed = 300.f;`，无需任何额外代码，编辑器立即可编辑，存档立即可保存。

**网络同步与存档的字段分离**：一个多人 RPG 的 `ACharacter` 子类可能同时拥有 `UPROPERTY(Replicated) float CurrentHP`（同步但不存档）和 `UPROPERTY(SaveGame) int32 Level`（存档但不实时同步），属性序列化允许同一字段声明驱动两套完全不同的数据管道，而无需分别维护同步列表和存档列表。

**热重载与实时编辑**：Unreal 的 Live Coding 和 Blueprint 重新编译流程依赖属性序列化把旧对象的字段值序列化到临时缓冲区，重建对象后再反序列化回来，从而保留编辑器中的运行时状态。

## 常见误区

**误区一：认为 `UPROPERTY()` 默认会被存入存档文件**  
仅添加 `UPROPERTY()` 而不加 `SaveGame` 说明符，字段**不会**被 `USaveGame` 的序列化路径处理。很多初学者在 `UGameInstance` 子类中标注了字段却发现存档后数据丢失，原因正是遗漏了 `SaveGame` 说明符。存档系统和编辑器序列化是两套独立的触发路径，标志位决定走哪条路。

**误区二：以为属性序列化会处理所有指针引用**  
`UPROPERTY()` 标注的 `UObject*` 指针在序列化时存储的是对象路径字符串（如 `/Game/Maps/Level1.Level1:BP_Enemy_0`），而非内存地址。若被引用对象不存在（资产被删除或路径变更），反序列化后指针为 `nullptr`。开发者常误以为对象引用会像普通值字段一样自动恢复，忽略了空指针检查，导致运行时崩溃。

**误区三：把 `Transient` 等同于"不占存档空间"的优化手段**  
`Transient` 的主要用途是语义标记——该字段是运行时派生数据，不应持久化。若开发者出于"节省存档大小"的目的滥用 `Transient`，会导致游戏重启后无法还原该字段，引发逻辑错误。正确做法是在加载回调（如 `PostLoad()` 或 `BeginPlay()`）中重新计算 Transient 字段的值。

## 知识关联

**前置概念——序列化概述**：理解属性序列化需要先掌握 `FArchive` 的流模型，即序列化和反序列化共用同一个 `<<` 运算符，方向由 `FArchive::IsLoading()` 标志决定。属性序列化的 `FProperty::SerializeItem()` 最终也调用这一机制，只是入口从手写代码变为反射遍历。

**后续概念——自定义结构体序列化**：当 `USTRUCT()` 内含 `TMap`、`TSet` 或非 UObject 的外部类型时，引擎的自动属性序列化可能无法正确处理，需要为结构体实现 `Serialize(FArchive& Ar)` 方法手动接管。掌握属性序列化的工作边界——即它能自动处理哪些类型、在哪些场景下失效——正是学习自定义结构体序列化的出发点。属性序列化覆盖了原生类型、`FString`、`UObject*` 引用和嵌套 `USTRUCT`，但对含有原始指针或第三方数据结构的类型则需要手动扩展。
