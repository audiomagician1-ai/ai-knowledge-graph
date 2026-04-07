# 属性序列化

## 概述

属性序列化（Property Serialization）是游戏引擎利用反射系统元数据，自动将对象成员变量转换为持久化字节流、并在反序列化时从字节流重建对象状态的机制。其核心价值在于将"字段声明"与"读写逻辑"解耦：开发者只需通过宏或特性标注哪些字段需要持久化，序列化框架便根据编译期或运行期生成的元数据自动完成后续的二进制布局映射、版本兼容处理和跨平台字节序转换。

该机制的工业级实现最早可追溯至 Unreal Engine 1（Epic Games，1998 年发布），其属性系统已通过 `UPROPERTY` 宏将字段元数据嵌入类描述符。到 Unreal Engine 4（2015 年开源代码库）时，以 `FProperty`、`FArchive` 与 `UObject` 三者为核心的完整反射序列化框架趋于成熟（Zherdin & Löffler，*Unreal Engine 4 Game Development Essentials*，2016）。Unity 则在 2012 年随 Unity 4.0 引入 `[SerializeField]` 特性与 YAML 格式场景文件，将 C# 运行时反射与编辑器 Inspector 管线打通（Unity Technologies，官方文档 *Script Serialization*，2023）。两条技术路线的共同本质是：**序列化的信息源不是手写的读写函数，而是描述字段布局的反射元数据**。

属性序列化直接决定哪些数据能跨越运行时边界。一个 RPG 角色的当前生命值、背包物品列表、已触发的剧情标记，若序列化配置错误，在存档保存后重新加载时会静默回落为默认值，而非抛出异常，使问题难以定位。

---

## 核心原理

### 反射元数据的编译期生成（Unreal Engine 路线）

Unreal Engine 的属性序列化依赖编译前由 **Unreal Header Tool（UHT）** 执行的代码生成步骤。UHT 扫描所有标注 `UCLASS()`、`USTRUCT()` 的头文件，为每个 `UPROPERTY()` 字段生成对应的 `FProperty` 子类实例（如 `FIntProperty`、`FObjectProperty`、`FArrayProperty`），每个实例存储以下关键信息：

- **字段名称**（`FName`）：用于序列化时的键值匹配和版本兼容查找；
- **内存偏移量**（`Offset_Internal`）：从对象基地址到该字段的字节偏移，序列化时通过指针算术 `(uint8*)Object + Offset` 直接定位内存；
- **类型描述符**：决定序列化时调用的具体 `Serialize()` 重载，例如 `FArrayProperty` 会先写入元素数量（`int32`），再逐元素递归序列化；
- **属性标志位**（`EPropertyFlags`）：控制该字段是否参与存档、网络复制或编辑器显示。

序列化执行时，`FArchive` 遍历目标类的 `FProperty` 链表，对每个未标记 `CPF_Transient` 的字段调用其 `SerializeItem()` 方法，整个过程无需开发者编写任何 `if/else` 分支。这一设计使得新增字段只需声明一次宏标记，序列化、编辑器显示、蓝图绑定三条管线同时更新。

### 运行时反射路线（Unity / C# 路线）

Unity 的序列化依赖 C# 运行时的 `System.Reflection` API，在编辑器进程中通过 `FieldInfo.GetValue()` / `FieldInfo.SetValue()` 读写字段。`SerializedObject` 和 `SerializedProperty` 将反射信息桥接到 YAML 格式的 `.unity` 场景文件写入流程。与 UHT 的编译期生成不同，Unity 的元数据在运行时动态获取，引入轻微性能开销，因此 Unity 官方推荐在热路径中避免频繁调用反射 API，改用预缓存的 `SerializedProperty` 引用。

Unity 序列化系统的默认规则如下（Unity Technologies，2023）：

| 字段访问修饰符 | 默认序列化行为 | 覆盖方式 |
|---|---|---|
| `public` | 自动序列化 | `[NonSerialized]` 排除 |
| `private` / `protected` | 不序列化 | `[SerializeField]` 加入 |
| `static` | 永远不序列化 | 无法覆盖 |
| `readonly` | 不序列化 | 无法覆盖 |

### 属性标记与过滤语义

Unreal Engine 的 `UPROPERTY()` 宏支持多组正交的 specifier，每组控制不同管线的行为，互不干扰：

- **`SaveGame`**：仅当调用 `UGameplayStatics::SaveGameToSlot()` 触发的 `SaveGame` 过滤路径时序列化；常规关卡流送序列化不包含此字段；
- **`Transient`**：对所有序列化路径不可见，字段在对象加载后总是获得类型默认值，适用于缓存计算结果或帧级临时状态；
- **`Replicated`**：将字段注册进网络复制系统（`GetLifetimeReplicatedProps()`），但与磁盘序列化正交，可同时标记 `SaveGame` 和 `Replicated`；
- **`SkipSerialization`**：字段元数据保留（编辑器可见），但序列化调用时跳过，适用于需要在编辑器中展示但由代码重建的衍生数据。

---

## 关键公式与数据结构

### 序列化偏移量寻址

属性序列化的内存寻址依赖以下计算：

$$
\text{FieldPtr} = \text{ObjectBasePtr} + \Delta_{\text{offset}}
$$

其中 $\text{ObjectBasePtr}$ 是对象实例的起始地址，$\Delta_{\text{offset}}$ 是 UHT 在代码生成阶段写入 `FProperty::Offset_Internal` 的编译期常量。对于继承体系，子类字段的偏移量紧接父类布局末尾排列，`FProperty` 链表按继承层级链式存储，确保父类字段在子类对象上的偏移计算仍然正确。

### 二进制存档的字段块结构

Unreal Engine 的 `.uasset` 和存档文件中，每个属性字段的序列化块遵循以下格式：

$$
[\underbrace{\text{FName(FieldName)}}_{变长}]\ [\underbrace{\text{FName(TypeName)}}_{变长}]\ [\underbrace{\text{int32(Size)}}_{4\text{字节}}]\ [\underbrace{\text{int32(ArrayIndex)}}_{4\text{字节}}]\ [\underbrace{\text{Value...}}_{Size\text{字节}}]
$$

这一布局使版本兼容成为可能：加载时若遇到当前类中不存在的 `FieldName`，序列化器可通过 `Size` 字段直接跳过该块，而不会破坏后续字段的解析，从而实现字段的向前兼容删除（Unreal Engine 源码 `UnrealEngine/Engine/Source/Runtime/CoreUObject/Private/Serialization/`）。

### 版本号与兼容性管理

Unreal Engine 提供两层版本控制：

1. **引擎版本号**（`EUnrealEngineObjectUE5Version`）：硬编码于引擎源码，随引擎版本递增，控制引擎内置类型的序列化格式；
2. **自定义版本号**（`FCustomVersionRegistration`）：项目级版本号，开发者在升级序列化格式时递增，通过 `FArchive::CustomVer()` 查询当前文件版本，在字段的 `Serialize()` 重载中编写版本分支：

```cpp
void UMyComponent::Serialize(FArchive& Ar)
{
    Super::Serialize(Ar);
    if (Ar.CustomVer(FMyGameVersion::GUID) >= FMyGameVersion::AddedHealthRegen)
    {
        Ar << HealthRegenRate; // 仅在新版本存档中读写
    }
}
```

---

## 实际应用

### 案例：SaveGame 系统的属性过滤

在一个开放世界 RPG 中，`APlayerCharacter` 持有以下几类字段：

```cpp
UPROPERTY(SaveGame)
int32 CurrentHealth;          // 需要存档

UPROPERTY(Transient)
UParticleSystemComponent* DustEffect; // 运行时生成，不存档

UPROPERTY(Replicated, SaveGame)
TArray<FItemData> Inventory;  // 既需要网络同步，也需要存档

UPROPERTY()
FVector LastKnownPosition;    // 没有 SaveGame 标记：存档时跳过
```

调用 `UGameplayStatics::SaveGameToSlot()` 时，引擎内部实例化一个带 `PPF_SaveGame` 过滤标志的 `FObjectAndNameAsStringProxyArchive`，遍历 `FProperty` 链表时仅处理 `CPF_SaveGame` 标志位为真的字段。`LastKnownPosition` 虽有 `UPROPERTY()` 宏，但因缺少 `SaveGame` specifier 而被跳过，重新加载后其值为 `FVector::ZeroVector`。

### 案例：Unity 中嵌套自定义类型的序列化陷阱

Unity 序列化系统要求自定义值类型（`struct`）必须标注 `[System.Serializable]` 才能被 `SerializedObject` 递归处理。例如：

```csharp
[System.Serializable]
public struct InventorySlot
{
    public string ItemId;
    public int    Quantity;
}

public class PlayerInventory : MonoBehaviour
{
    [SerializeField]
    private List<InventorySlot> slots; // 正确序列化
}
```

若省略 `[System.Serializable]`，`slots` 列表在 Inspector 中显示为空，YAML 场景文件中也不会写入任何内容，但运行时 `slots.Count` 会返回 0 而非抛出异常，导致难以察觉的数据丢失。

Unity 序列化系统对自引用类型（如链表节点）存在已知限制：递归序列化深度硬上限为 **7 层**，超出后字段被截断为 null（Unity Technologies，*Script Serialization*，2023）。

---

## 常见误区

### 误区一：`UPROPERTY()` 等同于"总是序列化"

仅标记 `UPROPERTY()` 不附加任何 specifier 的字段，在 **关卡流送和蓝图默认值序列化** 路径下会被处理，但在 **SaveGame 路径** 下会被跳过。开发者常因此以为存档功能已覆盖所有 `UPROPERTY()` 字段，导致角色属性在存档读取后被重置。正确做法是为需要存档的字段显式添加 `SaveGame` specifier，并在代码审查清单中将此项列为必检项。

### 误区二：Transient 字段不占用内存

`Transient` 仅影响序列化管线的处理逻辑，字段在运行时内存中正常存在、正常读写，`CPF_Transient` 标志只通知序列化遍历器跳过该字段。将 `UTexture2D*` 缓存标记为 `Transient` 并不减少其运行时内存占用，需要配合 `UPROPERTY(Transient)` 确保 GC 仍能追踪该指针以防止悬空引用。

### 误区三：Unity `public` 字段的序列化优先于逻辑封装

部分开发者为了让字段在 Inspector 中可见，将其设为 `public`，但这同时将字段暴露给所有外部代码，破坏封装性。正确做法是保持 `private` 访问修饰符，配合 `[SerializeField]` 特性实现"仅 Inspector 可见、不对外暴露"的效果。Unity 编辑器序列化系统完全支持对 `private [SerializeField]` 字段的读写，与 `public` 字段行为一致。

### 误区四：字段重命名不需要迁移处理

序列化字段的名称是持久化文件中的键（Unreal 使用 `FName`，Unity 使用 YAML 键名）。将 `CurrentHealth` 重命名为 `Health` 后，旧存档文件中的 `CurrentHealth` 块在加载时找不到对应字段而被跳过，新字段 `Health` 以默认值初始化——旧数据静默丢失。Unreal Engine 提供 `UPROPERTY(meta=(DeprecatedProperty, DeprecationMessage="Use Health instead"))` 与 `CoreRedirects` 机制处理字段重命名迁移；Unity 则需要通过 `ISerializationCallbackReceiver` 接口在 `OnAf