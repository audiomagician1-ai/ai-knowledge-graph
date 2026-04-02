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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 属性序列化

## 概述

属性序列化是游戏引擎中利用反射系统自动读写对象属性的机制，无需开发者手动编写每个字段的存取代码。在 Unreal Engine 中，凡是用 `UPROPERTY()` 宏标记的成员变量，引擎的 `FArchive` 序列化系统便可在存档、网络同步或编辑器持久化时自动处理这些变量的读写流程。这与传统手动序列化的区别在于：开发者声明字段的"意图"，而非描述"过程"。

该机制起源于 90 年代末商业引擎对大规模关卡数据管理的迫切需求。Unreal Engine 1（1998 年发布）已初步引入基于宏标记的属性系统，到 Unreal Engine 4 时形成了以 UObject 反射系统为核心的完整属性序列化框架。Unity 则在 2012 年前后通过 `[SerializeField]` 特性将 C# 反射与 YAML 格式的场景文件结合，形成了另一条技术路线。这两种方案都表明，反射驱动的自动序列化已成为现代引擎的标准配置。

属性序列化的重要性在于它直接决定了哪些数据能够跨越运行时边界——即从内存中的活跃对象转换为可存储或可传输的字节流。一个角色的生命值、背包内容或关卡触发器状态，都依赖属性序列化在存档与加载之间保持一致性。错误地配置属性标记会导致数据静默丢失，且往往在运行时才能发现。

---

## 核心原理

### 反射元数据的生成

属性序列化的基础是编译期生成的反射元数据。在 Unreal Engine 中，Unreal Header Tool（UHT）在编译前扫描所有 `.h` 文件，为每个 `UPROPERTY()` 标记的字段生成对应的 `FProperty` 对象，记录字段名称、数据类型、内存偏移量（offset）及序列化标志位。序列化时，`FArchive` 遍历类的 `FProperty` 链表，通过偏移量直接读写内存地址，不依赖开发者编写任何 `if/else` 分支。

在 Unity 中，C# 反射在运行时通过 `System.Reflection.FieldInfo` 获取字段信息，`SerializedObject` 和 `SerializedProperty` API 将这些信息桥接到编辑器的 Inspector 面板和 YAML 场景文件写入流程。与 UHT 不同，Unity 的反射元数据在运行时动态获取，有轻微性能开销。

### 属性标记与过滤规则

并非所有属性都会被序列化，引擎通过标记（specifier）精确控制序列化范围。Unreal Engine 的 `UPROPERTY()` 支持以下关键标记：

- `SaveGame`：仅在调用 `USaveGame` 存档时序列化该字段；
- `Transient`：明确排除序列化，字段值在加载后始终为默认值；
- `Replicated`：将字段纳入网络复制系统，但不影响磁盘序列化；
- `EditAnywhere` / `VisibleAnywhere`：控制编辑器可见性，间接影响序列化优先级。

缺少 `UPROPERTY()` 宏的 C++ 成员变量对引擎完全透明，序列化系统无法感知其存在，即使它在内存中有值，保存存档后重新加载也会得到零值或垃圾数据。

Unity 的规则与此相反：默认情况下，`public` 字段自动参与序列化，`private` 字段则需要显式添加 `[SerializeField]` 特性。`[NonSerialized]`（C# 标准特性）或 Unity 专属的 `[HideInInspector]` 可将字段排除在外。两种引擎的默认策略相反，是跨引擎开发者的常见混淆来源。

### FArchive 的双向读写模型

Unreal Engine 的 `FArchive` 采用"单一操作符双向语义"设计：重载 `<<` 操作符同时承担读（加载）和写（保存）两种方向。序列化函数只需写一次：

```cpp
Archive << Health;
Archive << Inventory;
```

`FArchive::IsLoading()` 在内部决定数据流方向。这消除了读写代码不一致导致的版本错位问题。每个支持序列化的类型需实现 `Serialize(FArchive& Ar)` 虚函数，基础类型（`int32`、`float`、`FString`）已由引擎内置实现，`TArray`、`TMap` 等容器模板也内置了元素递归序列化逻辑。

---

## 实际应用

**RPG 游戏存档**：角色类 `APlayerCharacter` 中，`Health`（`float`）、`Level`（`int32`）和 `InventoryItems`（`TArray<FItemData>`）均标记为 `UPROPERTY(SaveGame)`。调用 `UGameplayStatics::SaveGameToSlot()` 时，引擎自动遍历所有 `SaveGame` 属性并写入存档文件，读档时反向填充内存，无需开发者编写任何循环或文件操作代码。

**编辑器关卡配置**：关卡触发器 `ATriggerVolume` 中的 `TriggerRadius`（`float`）标记 `EditAnywhere`，设计师在编辑器中拖拽调整后，该值通过属性序列化写入 `.umap` 文件。即使游戏发布后，关卡包内的触发器尺寸依然与设计师设定的值完全一致。

**Unity 预制体（Prefab）持久化**：Unity 中 `MonoBehaviour` 子类的 `[SerializeField] private float MoveSpeed` 字段，在保存预制体时被序列化为 YAML 格式：`m_MoveSpeed: 5.5`。这意味着修改脚本中的字段默认值不会自动覆盖已保存预制体中的值——引擎优先读取 YAML 文件中的序列化数据。

---

## 常见误区

**误区一：认为添加 `UPROPERTY()` 就等于一定会被存档**。`UPROPERTY()` 只让引擎能"看见"该属性，具体是否存入存档取决于是否携带 `SaveGame` 标记，以及序列化的调用路径是否经过 `USaveGame` 子系统。仅标记 `EditAnywhere` 的属性只会序列化到关卡或蓝图资产文件，运行时调用存档接口时并不处理它。

**误区二：认为 `Transient` 属性在任何情况下都不会被序列化**。`Transient` 的确排除了磁盘序列化和默认网络复制，但 `FArchive` 在做内存复制（如蓝图构造脚本中的对象克隆）时可能仍会读取该字段，因为克隆操作使用独立的序列化标志位。依赖 `Transient` 阻止数据扩散时需检查具体序列化路径。

**误区三：修改字段类型不会影响已有存档的读取**。属性序列化通过字段名称匹配存档数据，若将 `Health` 从 `int32` 改为 `float`，旧存档中对应条目的字节布局不变，加载时类型不匹配会导致数据静默截断或读取失败。这要求引擎项目在修改已序列化属性类型时必须同步编写版本迁移逻辑（Unreal 通过 `CustomVersions` 机制处理）。

---

## 知识关联

**前置概念——序列化概述**：属性序列化建立在序列化的基础概念之上，即对象状态与字节流之间转换的通用框架。理解 `FArchive` 的流模型和 Unity Asset 文件的结构，是正确配置属性标记的前提。

**后续概念——自定义结构体序列化**：当需要序列化的字段类型是自定义的 `USTRUCT`（Unreal）或普通 C# 结构体（Unity）时，引擎的自动机制需要开发者为结构体额外声明每个子字段的标记，或手动实现 `Serialize` 函数。自定义结构体序列化正是在属性序列化能力无法完全覆盖时的下一步精细控制手段，处理嵌套数据、条件序列化及二进制版本兼容问题。