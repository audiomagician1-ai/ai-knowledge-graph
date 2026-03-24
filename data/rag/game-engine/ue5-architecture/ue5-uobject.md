---
id: "ue5-uobject"
concept: "UObject系统"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.394
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# UObject系统

## 概述

UObject是虚幻引擎（Unreal Engine）所有游戏对象的基类，定义在`Runtime/CoreUObject/Public/UObject/Object.h`文件中。自UE1时代起，Epic便将对象系统设计为引擎功能的基础层，到UE5中，UObject系统已演进为支持蓝图反射、垃圾回收、序列化、网络复制等功能的统一框架。所有继承自UObject的类都必须使用`UCLASS()`宏标记，这是引擎识别、追踪和管理这些对象的前提条件。

UObject系统的核心价值在于它将C++运行时与引擎的托管生命周期连接起来。一个原生C++ `new`出来的对象，引擎无从感知其存在；而通过`NewObject<T>()`创建的UObject实例，会被注册到全局对象数组`GUObjectArray`中，从创建到销毁全程由引擎掌控。这意味着开发者不需要手动`delete`UObject，但代价是必须遵守引擎规定的创建和引用规则，否则会导致悬空指针或内存泄漏。

## 核心原理

### 反射系统（Reflection）

UE5的反射系统通过Unreal Header Tool（UHT）在编译预处理阶段自动生成`.generated.h`和`.gen.cpp`文件来实现。当开发者在类中声明`UPROPERTY()`或`UFUNCTION()`宏时，UHT会将这些字段的类型信息、名称、元数据写入一个`UClass`对象。每个UObject类在运行时都对应一个唯一的`UClass`实例，通过`GetClass()`方法可获取它。

`UClass`继承自`UStruct`，内部维护一张`TArray<FProperty*>`属性列表和`TArray<UFunction*>`函数列表。通过这张表，可以在运行时用字符串找到任意属性或调用任意函数，蓝图节点"Set Variable by Name"等功能正是依赖这一机制。反射还支持`CDO`（Class Default Object），每个`UClass`在引擎启动时自动创建一个默认对象，用于存储属性默认值，`GetArchetype()`本质上就是访问CDO链。

### 垃圾回收（Garbage Collection）

UE5的垃圾回收采用**标记-清除（Mark-and-Sweep）**算法，默认每隔`GEngine->TimeBetweenPurgingPendingKillObjects`秒（默认约60秒）执行一次完整GC，也可通过`ForceGarbageCollection(true)`触发。GC的根集（Root Set）由`GUObjectArray`中所有标记了`RF_RootSet`标志的对象构成，典型的根集成员包括`GEngine`、各`UPackage`等。

引用图遍历时，引擎只追踪被`UPROPERTY()`标记的UObject指针。如果你在C++中用裸指针`UMyObject* Ptr`（没有`UPROPERTY()`）持有一个UObject，GC遍历时不会发现这条引用，被引用的对象可能在下一次GC中被销毁，留下野指针——这是UE开发中最常见的崩溃原因之一。`AddToRoot()`可强制将某对象加入根集防止回收，对应的`RemoveFromRoot()`则需要在适当时机手动调用。

### 对象创建与标志位（Object Flags）

创建UObject必须使用`NewObject<T>(Outer, Class, Name, Flags)`，其中`Outer`指定了该对象在对象层级中的"所有者"。当Outer被GC回收时，所有以其为Outer的子对象也会随之失效。常用的对象标志（`EObjectFlags`）包括：
- `RF_Transient`：标记后该对象不会被序列化到磁盘，适合运行时临时对象；
- `RF_Public`：允许其他包引用此对象；
- `RF_NeedPostLoad`：序列化加载完成后需调用`PostLoad()`。

`FObjectInitializer`是构造函数参数中的特殊对象，在`UMyClass::UMyClass(const FObjectInitializer& ObjectInitializer)`中可用它覆盖子组件的默认类，这是修改蓝图可扩展默认组件类型的标准方式。

### 序列化与CDO

UObject通过重写`Serialize(FArchive& Ar)`参与序列化，但通常不需要手动重写——引擎的`UObject::Serialize`会自动遍历所有`UPROPERTY`字段并读写二进制数据。`.uasset`文件本质上是一个`FPackageFileSummary`头部加上若干序列化的UObject数据块。CDO的属性值作为差量基准，实例只存储与CDO不同的字段，这大幅压缩了存档体积。

## 实际应用

**数据资产（Data Asset）**：继承`UDataAsset`（其本身继承UObject）后，通过`UPROPERTY(EditAnywhere)`暴露属性，在编辑器中填写数值，运行时用`TSoftObjectPtr`或直接引用加载——整个流程依赖UObject的序列化与反射支持。

**蓝图可调用函数**：在C++类中声明`UFUNCTION(BlueprintCallable, Category="MyGame")`，蓝图编辑器通过查询`UClass`的函数表自动生成对应节点，无需任何额外绑定代码。

**运行时类型检查**：`Cast<ACharacter>(SomeActor)`比`dynamic_cast`更快，因为它使用引擎内部的`UClass`继承链（`IsChildOf()`），不依赖RTTI，且在非Editor构建中RTTI默认是关闭的（`/GR-`编译选项）。

**编辑器细节面板**：任何`UPROPERTY(EditAnywhere, BlueprintReadWrite)`字段会自动出现在编辑器的Details面板中，支持撤销/重做（通过`UObject::Modify()`事务系统）。

## 常见误区

**误区一：用`new`代替`NewObject`创建UObject**
用`new UMyObject()`创建的对象不会被注册到`GUObjectArray`，GC不知道它的存在，也无法进行序列化、蓝图访问等操作。正确做法始终是`NewObject<UMyObject>(this)`，让引擎完整接管对象生命周期。

**误区二：在非UPROPERTY的裸指针中存储UObject引用**
如`UMyObject* CachedRef;`（没有`UPROPERTY()`宏），下一次GC可能销毁`CachedRef`指向的对象，但指针本身的值不会被清空，读取时会访问已释放内存。正确做法是加上`UPROPERTY()`，或使用`TWeakObjectPtr<UMyObject>`——后者在对象被GC后会自动置为`nullptr`。

**误区三：混淆UObject的销毁时机**
调用`ConditionalBeginDestroy()`或`MarkAsGarbage()`（UE5中替代了旧版的`MarkPendingKill()`）只是将对象标记为待回收，对象在下一次GC运行前仍然存在。试图在此之后访问该对象是未定义行为。如果需要立即清理逻辑状态，应在`BeginDestroy()`中执行，而非依赖析构函数（GC不保证析构函数调用时机）。

## 知识关联

UObject系统建立在**UE5模块系统**之上——`CoreUObject`模块是最先被加载的引擎模块之一，在`FEngineLoop::Init()`的早期阶段完成`GUObjectArray`初始化。没有模块系统提供的动态链接与加载机制，UObject的跨模块反射无法工作。

掌握UObject后，**Actor-Component模型**是直接延伸：`AActor`继承自`UObject`（经由`AActor : public UObject`），`UActorComponent`同样继承自`UObject`，两者的Tick、网络复制、序列化都依赖UObject层的基础设施。**委托与事件系统**中的`DECLARE_DYNAMIC_MULTICAST_DELEGATE`宏生成的类也是UObject的属性类型，需要`UPROPERTY()`才能被蓝图绑定。**UE5智能指针**（如`TSharedPtr`）则与UObject体系完全独立，用于非UObject的原生C++对象，理解两套系统的边界是避免内存问题的关键。**Data Asset与DataTable**则是UObject序列化和反射在数据驱动设计中的直接应用。
