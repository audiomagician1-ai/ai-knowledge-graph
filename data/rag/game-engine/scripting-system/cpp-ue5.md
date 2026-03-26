---
id: "cpp-ue5"
concept: "C++在UE5中的使用"
domain: "game-engine"
subdomain: "scripting-system"
subdomain_name: "脚本系统"
difficulty: 2
is_milestone: false
tags: ["UE5"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# C++在UE5中的使用：UCLASS/UPROPERTY/UFUNCTION宏体系

## 概述

虚幻引擎5（UE5）通过一套被称为"虚幻头文件工具（UHT，Unreal Header Tool）"的代码生成机制，将标准C++扩展为一套具备运行时反射能力的语言系统。开发者在普通C++类上标注特定宏，UHT在编译前扫描这些宏并自动生成`.generated.h`文件，最终将类型信息注册进UE5的反射系统（UObject系统）。这一机制使C++代码能够与蓝图编辑器、序列化、网络复制和垃圾回收等引擎子系统无缝协作。

宏体系的核心由三个主宏构成：`UCLASS`用于声明类，`UPROPERTY`用于声明属性，`UFUNCTION`用于声明函数。这套体系自UE3时代（约2006年）便已存在雏形，到UE4/UE5中逐步规范化。每个使用了`UCLASS`宏的类都必须继承自`UObject`或其子类，并且头文件末尾必须包含`#include "ClassName.generated.h"`，否则编译会报错。

理解这套宏体系至关重要，因为UE5中几乎所有引擎功能——包括蓝图暴露、属性面板显示、`SaveGame`序列化、RPC网络调用——都依赖反射元数据的存在。没有正确标注宏的C++类，无法被蓝图继承，也无法通过`Cast<T>()`进行安全类型转换。

---

## 核心原理

### UCLASS宏与类声明

`UCLASS`宏放置在C++类定义的正上方，其括号内可以填写说明符（Specifier）来控制类的行为。常用说明符包括：

- `Blueprintable`：允许该类在编辑器中被蓝图继承
- `BlueprintType`：允许该类作为蓝图变量类型使用
- `Abstract`：标记为抽象类，不可在编辑器中直接实例化
- `NotBlueprintable`：显式禁止蓝图继承

类体内部必须紧跟`GENERATED_BODY()`宏（UE4之前为`GENERATED_UCLASS_BODY()`），该宏由UHT展开为构造函数声明、反射注册代码等自动生成内容。例如：

```cpp
UCLASS(Blueprintable, BlueprintType)
class MYGAME_API AMyActor : public AActor
{
    GENERATED_BODY()
    // ...
};
```

注意`MYGAME_API`是DLL导出宏，与项目名称绑定，在模块构建时自动生成。

### UPROPERTY宏与属性反射

`UPROPERTY`宏标注成员变量，使其进入UE5反射系统，从而支持蓝图读写、编辑器面板显示、垃圾回收追踪和网络复制。常用说明符：

- `EditAnywhere`：在编辑器中（实例和默认值）均可修改
- `EditDefaultsOnly`：仅在类默认值面板修改，不允许对单个实例修改
- `BlueprintReadWrite`：蓝图可读可写
- `BlueprintReadOnly`：蓝图只读
- `Replicated`：该属性参与网络复制（需配合`GetLifetimeReplicatedProps`使用）
- `Category = "分类名"`：控制属性在编辑器Details面板中的分组显示

对于指向`UObject`的指针，**必须**标注`UPROPERTY`，否则垃圾回收器（GC）不会追踪该引用，可能导致指针悬挂（Dangling Pointer）。这是UE5内存安全的关键规则：

```cpp
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
float Health = 100.0f;

UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
TObjectPtr<UStaticMeshComponent> MeshComponent;
```

UE5.0起推荐使用`TObjectPtr<T>`替代裸指针`T*`，前者在编辑器构建中提供额外的空指针访问检测。

### UFUNCTION宏与函数暴露

`UFUNCTION`宏标注成员函数，将函数元数据注册进反射系统。常用说明符：

- `BlueprintCallable`：函数可在蓝图中作为节点调用
- `BlueprintPure`：函数无副作用，在蓝图中显示为无执行引脚的纯函数节点
- `BlueprintNativeEvent`：C++提供默认实现，蓝图可覆写；C++实现函数名需加`_Implementation`后缀
- `BlueprintImplementableEvent`：C++只声明，实现完全由蓝图提供
- `Server`/`Client`/`NetMulticast`：RPC网络函数标识符，需配合`Reliable`或`Unreliable`使用

```cpp
UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "Combat")
void OnDamaged(float DamageAmount);
// C++中实现时函数名为：
void AMyActor::OnDamaged_Implementation(float DamageAmount) { ... }
```

`BlueprintNativeEvent`的`_Implementation`命名约定是UHT强制要求的，命名错误会导致链接错误而非编译错误，初学者需特别注意。

---

## 实际应用

在制作一个具有血量系统的`ACharacter`子类时，典型的宏标注流程如下：将`MaxHealth`和`CurrentHealth`用`UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Replicated)`标注，使策划可在蓝图默认值面板调整数值，同时在多人游戏中自动同步给客户端。受伤函数`TakeDamage`用`UFUNCTION(BlueprintNativeEvent)`标注，允许蓝图子类在C++基础逻辑之上添加粒子效果或UI更新，而无需修改C++源文件。

UE5的`GameplayAbilitySystem`（GAS）插件本身就大量依赖`UPROPERTY`标注的`FGameplayAttributeSet`来追踪角色数值，所有`Attribute`（如`Health.Value`）都必须通过`UPROPERTY`注册才能被GAS的`Modifier`系统识别和修改。

---

## 常见误区

**误区一：忘记包含`.generated.h`或包含位置错误。**  
`#include "ClassName.generated.h"`必须是该头文件中**最后一个**`#include`语句，否则UHT生成代码中的前置声明会引用到未定义的类型，产生难以追踪的编译错误。

**误区二：认为`UPROPERTY`对基础类型（如`float`、`int32`）可以省略。**  
对于非指针的基础类型，省略`UPROPERTY`不会导致崩溃，但会使该属性无法在编辑器中显示、无法被蓝图访问、无法被`SaveGame`序列化，功能静默缺失。只有`UObject`指针省略`UPROPERTY`才会立即造成GC崩溃。

**误区三：混淆`BlueprintPure`与`BlueprintCallable`的适用场景。**  
`BlueprintPure`函数在蓝图中没有执行流引脚（白色箭头），每次被引用时都会被重新求值，在同一帧内多次引用`BlueprintPure`函数可能导致重复计算开销。有副作用的函数（如修改状态、播放音效）若误标为`BlueprintPure`，会产生难以调试的逻辑问题。

---

## 知识关联

本文所述宏体系建立在**脚本系统概述**中介绍的"反射与元数据"概念之上——UHT正是UE5脚本系统中将静态C++类型转换为运行时可查询元数据的具体实现机制。

掌握`UCLASS/UPROPERTY/UFUNCTION`宏标注规则后，下一步是学习**原生绑定（Native Binding）**：即如何在C++中通过`BindUFunction`、委托（`DECLARE_DYNAMIC_MULTICAST_DELEGATE`）和`FTimerHandle`等机制，让反射系统中已注册的函数响应引擎事件，从而实现C++逻辑与蓝图事件系统的双向通信。