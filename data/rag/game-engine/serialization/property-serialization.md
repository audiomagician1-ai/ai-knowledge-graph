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
content_version: 3
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
# 属性序列化

## 概述

属性序列化（Property Serialization）是游戏引擎中通过反射系统自动完成对象数据读写的机制。引擎在运行时扫描对象的元数据，找到所有标记为"可序列化"的属性字段，并将其值转换为持久化格式（如二进制流、JSON 或 XML），无需开发者手动编写每个字段的读写代码。

该机制最早在 Unreal Engine 3 的 UnrealScript 时代初具雏形，进入 UE4/UE5 后，`UPROPERTY()` 宏成为属性序列化的核心标注工具。Unity 则采用 `[SerializeField]` 特性（Attribute）配合 `SerializedObject` 系统实现类似功能。两套系统都依赖各自的反射层——UE5 的 `UProperty`/`FProperty` 体系，以及 Unity 的 `SerializedProperty` 树——来完成自动化读写。

属性序列化的意义在于将"哪些数据需要保存"与"数据如何保存"彻底解耦。关卡设计师在编辑器中调整的每一个 Actor 参数，之所以能在保存关卡后精确还原，正是因为这些参数字段在 C++ 或 C# 层被标注为可序列化属性，引擎序列化管线自动处理了剩余的一切。

---

## 核心原理

### 反射元数据驱动的字段发现

属性序列化的前提是反射系统已为目标类型生成了字段描述表。以 UE5 为例，编译时 Unreal Header Tool（UHT）解析所有带有 `UPROPERTY()` 宏的字段，并生成对应的 `FProperty` 描述对象，记录字段名称、类型、内存偏移量和序列化标志位。序列化时，引擎调用 `UObject::Serialize(FArchive& Ar)`，该函数遍历当前类的 `FProperty` 链表，对每个属性调用 `Property->SerializeItem(Ar, Data)`，完成值的实际读写。整个过程不依赖任何硬编码的字段名，新增属性只需加上宏即可自动纳入序列化。

### 序列化标志位与选择性序列化

并非所有 `UPROPERTY` 字段都参与全部序列化场景。UE5 提供多个控制标志：

- `SaveGame`：标注该属性参与存档系统（`UGameplayStatics::SaveGameToSlot`）
- `Transient`：标注该属性**不**写入磁盘，仅存在于运行时内存
- `EditDefaultsOnly` / `EditAnywhere`：控制编辑器可见性，不直接影响磁盘序列化但影响 CDO 差量写入

Unity 中等效的控制是 `[NonSerialized]`（阻止公有字段序列化）和 `[SerializeField]`（强制序列化私有字段）。标志位使引擎能针对不同目标（编辑器资产、网络复制、存档文件）选择不同的属性子集，避免冗余数据。

### 差量序列化（Delta Serialization）

UE5 的资产序列化不会将对象的全部属性值都写入 `.uasset`，而是只记录与类默认对象（Class Default Object，CDO）不同的属性，这一机制称为差量序列化。其核心公式为：

```
写入集合 = { p ∈ Properties | p.value(instance) ≠ p.value(CDO) }
```

这意味着一个 Blueprint Actor 的 `.uasset` 文件只存储被设计师实际修改过的属性值。当类结构更新、新增属性并赋予合理默认值时，旧资产文件不需要重写，加载时自动从 CDO 获取缺失值。这也是 UE5 热重载不会丢失场景中实例数据的底层原因之一。

### 版本兼容与属性重定向

属性名称改变会导致旧数据无法映射到新字段，造成数据丢失。UE5 通过 `FArchive` 内嵌的版本号（`UE_ASSET_MAGIC` 头部记录引擎版本）和 `FCoreRedirects` 系统解决此问题。在 `DefaultEngine.ini` 中添加：

```ini
[CoreRedirects]
+PropertyRedirects=(OldName="/Script/MyGame.MyActor.OldSpeed",NewName="/Script/MyGame.MyActor.NewSpeed")
```

引擎加载资产时检测到属性名不匹配，便查询重定向表完成自动映射，而无需编写专用的版本迁移代码。

---

## 实际应用

**关卡编辑器中的 Actor 参数保存**：设计师在编辑器中修改 `AEnemy` 的 `PatrolRadius`（浮点型）和 `bIsAggressive`（布尔型），点击保存后，引擎将这两个标注了 `UPROPERTY(EditAnywhere, SaveGame)` 的字段的当前值通过差量序列化写入关卡包。下次打开关卡时，反射系统根据字段名自动还原数值，无需任何额外代码。

**存档系统中的玩家数据持久化**：在 UE5 中，创建继承自 `USaveGame` 的子类，将 `PlayerLevel`（整型）、`InventoryItems`（`TArray<FItemData>`）标注 `UPROPERTY(SaveGame)`，调用 `UGameplayStatics::SaveGameToSlot` 即可触发自动序列化，数据以二进制格式写入平台存储目录。读取时同样通过反射自动填充字段，整个流程无需手写 `fwrite`/`fread`。

**Unity Prefab 覆写（Override）系统**：Unity 的 Prefab 变体（Prefab Variant）本质上也是差量序列化——只有相对于基础 Prefab 发生改变的 `SerializedProperty` 值才会被记录在变体资产中。当美术修改角色的 `MeshRenderer.material`，Inspector 中该字段会显示粗体标记，表示该属性值已被序列化为覆写数据。

---

## 常见误区

**误区一：只要字段是 public 就会被序列化**
在 Unity 中，C# 的 `public` 字段默认参与序列化，但 `static`、`readonly`、实现了 `IEnumerable` 但不是 `List<T>` 的集合类型不会被序列化。更重要的是，属性（Property，即带 `get`/`set` 的成员）**默认不序列化**，必须显式添加 `[SerializeField]` 或使用 `[field: SerializeField]`。在 UE5 中，`UPROPERTY()` 括号内不写任何标志时该属性不会出现在编辑器中，但仍会参与对象序列化。混淆这两个维度（编辑器可见性 vs 磁盘序列化）是初学者的高频错误。

**误区二：属性序列化可以处理任意 C++ 类型**
UE5 的属性序列化只支持已在反射系统注册的类型。原生 `std::vector<int>`、`std::string` 不被 `FProperty` 系统识别，必须替换为 `TArray<int32>`、`FString`。自定义结构体若未添加 `USTRUCT()` 宏，同样无法自动序列化，运行时会静默跳过或触发断言。这也是为什么游戏项目要求将所有需要持久化的结构体都接入 UE5 反射系统。

**误区三：差量序列化保证向后兼容**
差量序列化只解决了"旧资产缺少新字段"的向前兼容问题（新字段从 CDO 取默认值）。若字段**类型**从 `float` 改为 `int32`，或结构体成员重新排列，旧二进制数据的字节布局与新类型不匹配，差量机制无法自动处理，必须结合版本号判断或自定义序列化函数（`Serialize` 虚函数重写）才能安全迁移。

---

## 知识关联

**依赖前置概念**：属性序列化建立在序列化概述所介绍的"数据→字节流→数据"基本转换流程之上，并进一步引入反射系统作为字段发现的自动化手段。理解 `FArchive` 的读写模式（`Ar.IsLoading()` / `Ar.IsSaving()`）和基本类型序列化操作符 `<<` 是理解属性序列化内部调用链的必要背景。

**指向后续概念**：当对象包含自定义结构体（`USTRUCT`）时，属性序列化的自动机制触及边界——结构体内部的复杂逻辑（如指针修复、条件序列化某成员）无法通过简单标注实现，这正是下一个主题"自定义结构体序列化"需要解决的问题。掌握属性序列化的标志位系统和差量机制，是理解为何某些结构体必须手动重写 `Serialize` 函数的直接动机。
