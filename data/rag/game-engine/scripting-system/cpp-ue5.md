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

# C++在UE5中的使用

## 概述

Unreal Engine 5 采用 C++ 作为底层脚本语言，并通过一套称为 **Unreal Header Tool（UHT）** 的代码生成系统扩展了标准 C++。开发者在普通 C++ 类上方添加特定宏（Macro），UHT 在编译前扫描这些宏并自动生成 `.generated.h` 文件，最终将 C++ 类型信息注册到 UE5 的反射系统（Reflection System）中。这套机制使引擎可以在运行时查询类的属性和方法，而不依赖标准 C++ 的 RTTI。

UE5 的宏体系起源于 UE3 时代（约2006年），随 UnrealScript 被逐步废弃而发展壮大，到 UE4（2014年）时全面取代脚本语言成为主要逻辑载体，并在 UE5 中进一步与 Blueprints 深度集成。当前版本（UE 5.3+）的 C++ 宏体系已能实现属性热重载（Hot Reload）和 Live Coding，允许在不重启编辑器的情况下重新编译部分 C++ 模块。

理解这套宏体系至关重要，原因在于 UE5 中几乎所有引擎功能——从 GC（垃圾回收）到 Editor 可视化再到网络同步——都依赖反射数据驱动。若不使用这些宏，C++ 对象将无法被垃圾回收器追踪，也无法在 Blueprint 中调用，更无法通过 `SaveGame` 序列化。

---

## 核心原理

### UCLASS 宏：将 C++ 类注册到引擎

`UCLASS()` 宏放置在类声明上方，紧接着必须在类体首行写 `GENERATED_BODY()`。这两者缺一不可——`UCLASS` 告诉 UHT 此类需要生成反射代码，而 `GENERATED_BODY()` 是 UHT 插入构造函数辅助代码的占位符。

```cpp
UCLASS(Blueprintable, BlueprintType)
class MYGAME_API AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();
};
```

`UCLASS` 的说明符（Specifier）控制类的行为：`Blueprintable` 允许在 Blueprint 编辑器中以该类为父类派生子类；`Abstract` 标记类为抽象类，禁止直接在关卡中放置实例；`NotBlueprintable` 则明确阻止 Blueprint 继承。`MYGAME_API` 是模块导出宏，确保该类在 DLL 边界可见，这是 UE5 模块化构建系统的要求。

### UPROPERTY 宏：属性反射与编辑器集成

`UPROPERTY()` 标记成员变量，使其进入反射系统，最直接的效果是该变量会被 UE5 的垃圾回收器追踪。对于指向 `UObject` 派生类的指针，若不加 `UPROPERTY()`，GC 可能在持有该指针时销毁对象，产生悬空指针（Dangling Pointer）崩溃。

```cpp
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
float MaxHealth = 100.0f;

UPROPERTY(VisibleInstanceOnly, Replicated)
int32 CurrentScore;
```

常用说明符含义如下：
- `EditAnywhere`：在编辑器的类默认值（CDO）和实例上均可编辑
- `EditDefaultsOnly`：仅在 CDO 中可编辑，实例只读
- `BlueprintReadWrite` / `BlueprintReadOnly`：控制 Blueprint 的读写权限
- `Replicated`：将属性标记为需要通过网络同步，需配合 `GetLifetimeReplicatedProps` 使用
- `SaveGame`：标记该属性参与 `USaveGame` 序列化

### UFUNCTION 宏：方法暴露与 RPC

`UFUNCTION()` 将 C++ 方法注册到反射系统，使其可从 Blueprint 调用、作为委托绑定目标，或作为网络远程过程调用（RPC）。

```cpp
UFUNCTION(BlueprintCallable, Category = "Combat")
void ApplyDamage(float DamageAmount, AActor* DamageCauser);

UFUNCTION(BlueprintNativeEvent, Category = "Events")
void OnDeath();
virtual void OnDeath_Implementation();

UFUNCTION(Server, Reliable, WithValidation)
void ServerFire(FVector Direction);
```

`BlueprintNativeEvent` 是一个重要模式：它在 Blueprint 中生成可覆盖的事件节点，同时 C++ 侧提供 `_Implementation` 后缀的默认实现。`Server`、`Client`、`NetMulticast` 说明符将函数变为 RPC，`Reliable` 保证数据包不丢失（基于 TCP 语义），`Unreliable` 则用于高频低优先级调用（如位置同步）。`WithValidation` 要求同时实现 `_Validate` 函数用于服务器端作弊检测。

---

## 实际应用

**角色属性系统**：在 `ACharacter` 派生类中，用 `UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Stats")` 声明基础属性（如移速、跳跃高度），美术和策划无需改动 C++ 即可在编辑器的 Blueprint 子类中调整数值。

**网络射击游戏的开火逻辑**：客户端调用 `ServerFire(Direction)`（标记为 `Server, Reliable`），服务器验证后广播 `NetMulticast_PlayFireEffect()`（标记为 `NetMulticast, Unreliable`），实现逻辑权威在服务器、表现效果全端播放的标准架构。

**编辑器工具扩展**：将函数标记 `UFUNCTION(CallInEditor, Category="Tools")` 后，该函数会在选中 Actor 时出现在 Details 面板的按钮中，策划可直接点击执行，例如批量刷新关卡中的寻路数据。

---

## 常见误区

**误区一：认为 `UPROPERTY` 只是用来在编辑器显示变量**
许多初学者以为去掉 `UPROPERTY` 只是让变量"在编辑器中不可见"，实际上对 `UObject*` 指针而言这会导致 GC 不追踪该引用。当引擎在下一次垃圾回收周期（默认每帧检查，阈值约60,000个追踪对象）运行时，该对象可能被销毁，裸指针变为野指针，在之后访问时触发访问违规崩溃（Access Violation）。

**误区二：`BlueprintNativeEvent` 与 `BlueprintImplementableEvent` 混淆**
`BlueprintImplementableEvent` 完全由 Blueprint 实现，C++ 侧**不能**提供默认实现（只有声明）；而 `BlueprintNativeEvent` 的 C++ 侧**必须**提供 `_Implementation` 函数作为默认逻辑，Blueprint 可以选择覆盖。若在 `BlueprintImplementableEvent` 函数上写 `_Implementation` 方法体，将导致链接错误（Linker Error LNK2005）。

**误区三：误以为 `UCLASS` 可以用于非 `UObject` 派生类**
`UCLASS` 只能标注继承自 `UObject`（或其子类如 `AActor`、`UActorComponent`）的类。对于纯数据结构应使用 `USTRUCT()`，对于枚举使用 `UENUM()`。强行在非 `UObject` 类上使用 `UCLASS` 会在 UHT 阶段报错，而不是在编译阶段，这让初学者容易困惑错误来源。

---

## 知识关联

**前置概念——脚本系统概述**：UE5 的脚本系统包含 C++ 和 Blueprint 两层，本文所描述的 `UCLASS/UPROPERTY/UFUNCTION` 宏体系正是两层之间的桥梁接口，理解脚本系统的双层结构有助于明白为何需要这套显式注解机制。

**后续概念——原生绑定（Native Binding）**：掌握本文的宏体系后，下一步是学习如何将 C++ 中注册的属性和函数与 Blueprint 图表中的节点、动画蓝图的通知（AnimNotify）以及 UMG 控件绑定。原生绑定依赖本文所讲的 `UPROPERTY` 和 `UFUNCTION` 反射数据，若没有正确的宏标记，绑定操作在运行时会静默失败或找不到对应字段。