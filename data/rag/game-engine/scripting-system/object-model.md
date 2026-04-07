---
id: "object-model"
concept: "引擎对象模型"
domain: "game-engine"
subdomain: "scripting-system"
subdomain_name: "脚本系统"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 引擎对象模型

## 概述

引擎对象模型（Engine Object Model）是游戏引擎脚本系统中用于描述、组织和操作游戏实体的统一抽象层，它定义了引擎内部所有可操作对象的类型结构、属性访问规则和生命周期语义。不同于普通的面向对象类层次结构，引擎对象模型必须同时满足三个约束：在运行时支持类型查询（反射），在磁盘与内存之间支持往返序列化，以及向脚本语言暴露统一的属性访问接口。

历史上，虚幻引擎1（1998年）率先将 `UObject` 作为所有游戏对象的公共基类，并围绕它建立了完整的垃圾回收、属性系统和包序列化机制，这一设计奠定了现代引擎对象模型的基本形态。Unity 则以 `UnityEngine.Object` 为根，采用 C# 托管对象与原生 C++ 对象双栈的方式实现类似功能，托管侧的 `instanceID`（一个32位整数）充当连接两端的唯一句柄。Godot 4 的 `Object` 类通过 `ClassDB` 在运行时注册所有类的元数据，脚本绑定直接查询 `ClassDB` 而无需额外代码生成步骤。

引擎对象模型的重要性在于：它是类型系统、反射和序列化这三个子系统的共同基础——去掉它，编辑器无法显示属性面板，存档系统无法持久化状态，脚本语言也无法调用引擎功能。

## 核心原理

### 运行时类型信息（RTTI）与元类

引擎对象模型通常用一个"元类"或"类描述符"结构来存储每个类型的运行时信息，而不依赖 C++ 原生的 `typeid`（因为其结果在不同编译器间不可移植，且不携带属性元数据）。以虚幻引擎为例，每个 `UObject` 子类持有一个指向 `UClass` 的静态指针；`UClass` 本身也是 `UObject` 的子类，这形成了自描述的元对象循环（metaclass loop）。调用 `MyActor->IsA<APawn>()` 时，引擎沿 `UClass::SuperStruct` 链向上遍历，直到找到匹配或到达根节点，时间复杂度为 O(继承深度)。

Godot 的 `ClassDB` 采用哈希表存储类名到 `ClassInfo` 的映射，`ClassInfo` 内含方法列表、属性列表和父类名字符串。这种设计允许 GDScript 在运行时动态查询任意类是否存在某个方法，无需编译期代码生成。

### 属性描述符与字段偏移量

对象模型中的"属性"不是简单的 C++ 成员变量，而是一个携带名称、类型标签、字节偏移、访问标志和可选元数据的描述符结构。虚幻引擎的 `FProperty` 存储了 `Offset_Internal`（字段在对象内存布局中的字节偏移），读取属性值时的公式为：

```
void* value_ptr = (uint8*)object_ptr + property->Offset_Internal;
```

通过这一公式，脚本虚拟机和编辑器可以在不知道具体 C++ 类型的情况下，用统一接口读写任意属性。属性描述符还携带 `PropertyFlags`，例如 `CPF_SaveGame` 标志决定该属性是否参与存档序列化，`CPF_BlueprintVisible` 决定它是否在蓝图编辑器中可见——这两个功能都直接依赖于属性描述符的存在。

### 对象身份、所有权与生命周期

引擎对象模型必须解决普通 C++ 对象不需要解决的问题：多个脚本和系统可能同时持有同一对象的引用，对象的销毁必须安全地通知所有持有者。虚幻引擎通过"对象名路径"（如 `/Game/Maps/TestLevel.TestLevel:PersistentLevel.BP_Enemy_0`）为每个 `UObject` 分配全局唯一标识，并用一个全局对象数组 `GUObjectArray` 跟踪所有存活对象。当对象被 `MarkPendingKill()` 标记后，所有指向它的 `TWeakObjectPtr` 会在下次访问时自动返回 `nullptr`，而不会产生悬空指针。

Unity 的实现则将 C# 托管引用和原生对象分离：托管端的 `UnityEngine.Object` 变量在原生对象销毁后仍然存活，但重写过的 `==` 运算符会让它与 `null` 的比较返回 `true`，这正是 Unity 中著名的"假 null"现象（fake null）的来源。

## 实际应用

**编辑器属性面板的自动生成**：编辑器遍历选中对象的属性描述符列表，根据每个 `FProperty` 的类型标签（`FIntProperty`、`FFloatProperty`、`FObjectProperty` 等）选择对应的控件绘制逻辑，无需为每个类手写编辑器代码。Unreal Editor 中的 Details 面板完全由这套机制驱动，支持数千种不同组件类型的属性展示。

**存档与关卡序列化**：虚幻引擎的 `UPackage` 序列化流程遍历所有标记了 `CPF_SaveGame` 的属性，将其值写入二进制流。反序列化时，系统根据属性名字符串在元类中查找对应描述符，再用偏移量写回内存，从而实现版本容错（新增的属性在旧存档中找不到记录时直接使用默认值）。

**脚本热重载**：Godot 4 在 GDScript 热重载时，通过 `ClassDB` 保存旧实例的属性值字典，销毁旧实例，创建新类的实例，再将字典中的值逐一恢复——整个过程依赖属性描述符的名称作为稳定键。

## 常见误区

**误区一：认为引擎对象模型等同于 C++ 继承层次**。实际上，引擎对象模型是叠加在 C++ 类型系统之上的第二套类型系统。一个 C++ 类可以不继承 `UObject` 而只用 `USTRUCT` 标记，此时它获得属性反射和序列化支持，但没有垃圾回收和对象身份管理——这说明对象模型的各个功能是可以部分订阅的，而非全有或全无。

**误区二：认为序列化只需要把成员变量写入文件**。标准 `memcpy` 式序列化无法处理指针（内存地址在下次运行时会变化）、对其他对象的引用（需要替换为路径或 ID）、版本迁移（字段重命名或删除）以及平台字节序差异。引擎对象模型通过属性描述符的类型标签区分值类型字段和引用类型字段，对后者执行"对象路径替换"而非直接存储指针值。

**误区三：认为 `GetClass()` 与 `typeid()` 等价**。`UObject::GetClass()` 返回的 `UClass` 携带蓝图扩展的属性和函数，即使同一个 C++ 类被不同蓝图子类化，每个蓝图实例的 `GetClass()` 返回不同的 `UClass`，而 `typeid()` 对所有这些实例返回相同结果。这一差异在判断"对象是否属于某个具体蓝图类型"时至关重要。

## 知识关联

**前置：原生绑定**。原生绑定解决了"如何让脚本调用一个具体的 C++ 函数"，而引擎对象模型在此之上建立了通用的属性访问协议——脚本不再需要知道调用的是哪个具体函数，只需通过属性名字符串查询描述符再读写偏移量即可。原生绑定中手写的 `lua_register` 或 `pybind11::class_` 绑定代码，在引入对象模型后可以由代码生成工具（如虚幻的 UHT——Unreal Header Tool）根据属性描述符自动产生，消除了手动维护绑定代码与 C++ 定义同步的负担。

引擎对象模型还是蓝图可视化脚本、动画状态机序列化、网络属性同步（`Replicated` 标志也存储在 `FProperty` 的 `PropertyFlags` 中）等高级功能的共同基础设施，理解它的内部结构可以帮助开发者在遇到"属性在编辑器中不显示"或"存档丢失某个字段"等问题时，直接定位到描述符配置而非盲目排查业务逻辑。