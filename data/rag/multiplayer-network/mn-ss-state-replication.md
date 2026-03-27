---
id: "mn-ss-state-replication"
concept: "状态复制"
domain: "multiplayer-network"
subdomain: "state-synchronization"
subdomain_name: "状态同步"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.536
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 状态复制

## 概述

状态复制（State Replication）是多人游戏网络架构中的一种机制，指将游戏世界中某个对象的当前状态数据从一台机器（通常是服务器）自动同步到另一台或多台机器（客户端），使所有玩家看到的游戏世界保持一致。与RPC（远程过程调用）的"调用一次性动作"不同，状态复制关注的是持久性数据的持续一致性——例如角色的生命值、位置坐标、是否着火等属性，这些值在任意时刻都需要在多个机器上保持相同的副本。

UE5（Unreal Engine 5）的Replication系统是当前最具代表性的引擎级状态复制框架，由Epic Games在UE3时期奠定基础，经UE4逐步完善，并在UE5中引入了Enhanced Replication Flow和Push Model等重要优化。该系统以Actor为复制单元，通过`UPROPERTY(Replicated)`宏标记需要同步的变量，再由引擎在每个网络帧（默认约66ms，即NetUpdateFrequency=15Hz）自动检测变量变化并打包发送差量数据。

理解状态复制对网络多人游戏开发的重要性体现在：状态复制处理的是"世界是什么样子"这一问题，而非"发生了什么事件"。一个未经正确复制的属性（如弹药数量）在客户端断线重连后会显示错误初始值，而复制属性则会在客户端加入时通过Initial Replication发送完整快照，保证状态正确性。

---

## 核心原理

### Actor的复制资格与所有权

在UE5中，只有`bReplicates = true`的Actor才会参与状态复制。每个可复制Actor都有一个`NetOwner`（网络所有者），通常是控制该Actor的`PlayerController`。引擎通过`UNetDriver`管理所有客户端连接，每个连接对应一个`UNetConnection`，其内部维护了一个"相关Actor列表"（Relevant Actor List）。只有距离玩家视角在`NetCullDistanceSquared`阈值内（默认225,000,000平方厘米，即150米）的Actor才被判定为"相关"并参与同步，超出范围的Actor会被从复制队列中剔除，从而节省带宽。

### 属性标记与脏标记机制

UE5传统的Pull Model复制中，引擎在每个复制帧遍历所有可复制Actor，对比每个`Replicated`属性的当前值与上次发送值，若发生变化则标记为"脏"（Dirty）并加入本帧发送队列。这种轮询方式在Actor数量超过数千时会产生显著的CPU开销。为此，UE5引入了**Push Model**（在`NetCore`模块中启用，需定义`WITH_PUSH_MODEL=1`），改为由开发者在修改属性后主动调用`MARK_PROPERTY_DIRTY_FROM_NAME(ClassName, PropertyName, this)`通知引擎，将复制检测从O(N×P)降低到仅对实际变化的属性进行处理。

### 序列化与差量压缩

当属性被确认为脏时，UE5使用`FNetBitWriter`将其序列化为二进制数据。对于数值类型，引擎支持量化压缩，例如`FVector_NetQuantize`将浮点向量压缩为整数分量（精度0.1厘米），`FVector_NetQuantize10`精度为0.1，`FVector_NetQuantize100`精度为0.01，可将一个三分量向量从12字节压缩到约4-6字节。对于结构体（`USTRUCT`），可实现`NetSerialize`函数自定义序列化逻辑，实现位级压缩。数据包通过UDP发送，UE5的可靠UDP层（基于DTLS加密可选）负责丢包重传和乱序处理。

### RepNotify回调机制

`UPROPERTY(ReplicatedUsing = OnRep_FunctionName)`允许在属性值被客户端接收并应用后自动触发指定函数。例如，当服务器将角色的`bIsOnFire`从`false`改为`true`时，客户端收到更新后会调用`OnRep_IsOnFire()`，在此函数中播放火焰粒子特效和音效，而无需通过额外的RPC通知。RepNotify函数的签名可以带一个旧值参数：`void OnRep_Health(float OldHealth)`，通过比较新旧值实现受伤闪烁、治疗特效等差异化表现。

---

## 实际应用

**角色生命值同步**：在`ACharacter`子类中声明`UPROPERTY(Replicated) float Health`，在`GetLifetimeReplicatedProps`函数中调用`DOREPLIFETIME(AMyCharacter, Health)`注册该属性。服务器端对生命值的任何修改（无论来自伤害计算还是回血Buff）都会在下一个复制帧自动推送到所有客户端，无需手动调用任何发送函数。

**条件复制（Conditional Replication）**：使用`DOREPLIFETIME_CONDITION`可以精细控制复制目标。例如`COND_OwnerOnly`使某个属性只同步给控制该Actor的客户端（如弹药数量不需要广播给所有人），`COND_SkipOwner`则跳过所有者只同步给旁观者（如动画混合权重）。这种机制使带宽利用率大幅提升，一个典型的32人射击游戏服务器通过合理使用条件复制可将每秒总带宽从约800Kbps降低到约350Kbps。

**Subobject复制**：UE5允许复制`UObject`子对象（如武器组件），需在`ReplicateSubobjects`函数中手动调用`Channel->ReplicateSubobject(WeaponComponent, ...)`或使用UE5.1引入的`Registered Subobject List`（调用`AddReplicatedSubObject(WeaponComponent)`）自动管理，后者避免了手动重写`ReplicateSubobjects`的常见遗漏错误。

---

## 常见误区

**误区一：认为复制是实时的**
状态复制受`NetUpdateFrequency`控制，默认值为1~100Hz不等（`APawn`默认100Hz，`AActor`默认1Hz）。这意味着一个低频Actor的属性变化最多需要1秒才能到达客户端。开发者有时直接在客户端读取复制属性来做碰撞判定，却忘记该值已落后最多一个复制周期，导致本地预测与服务器状态不一致。对于高频需求（如精确位置），应使用角色移动组件（`UCharacterMovementComponent`）内置的预测-校正机制，而非依赖普通属性复制。

**误区二：在客户端修改Replicated属性会同步到服务器**
UE5的状态复制是严格单向的：**服务器 → 客户端**。在客户端代码中修改一个`Replicated`属性，该修改只存在于本地，下一次服务器复制帧到来时会被服务器值直接覆盖。若需要客户端向服务器传递状态变更请求，必须通过`Server RPC`（服务端RPC）实现，这是RPC与属性复制两套机制各司其职的分工所在。

**误区三：所有属性都应该复制**
每个被标记为`Replicated`的属性都会在每次发生变化时占用带宽，并在初始复制时发送全量数据。将UI显示用的派生数据（如由生命值计算得来的血条颜色）也标记为复制属性是常见的过度复制错误。正确做法是只复制"原始状态数据"（生命值），在客户端通过RepNotify本地计算派生表现。

---

## 知识关联

状态复制是学习网络多人游戏开发的切入点，掌握它要求了解UE5项目的基本Actor继承结构（`AActor` → `APawn` → `ACharacter`）以及C++宏系统的基本用法，无需额外网络编程前置知识。

在此基础上，下一个核心概念是**RPC与属性复制**的协同使用：状态复制解决"持久状态同步"，而RPC解决"一次性事件触发"，两者分别对应UDP可靠/不可靠通道的不同使用场景。理解状态复制后，学习者会自然遇到"客户端何时能相信自己的本地值"这一问题，这将引向**客户端预测**（Client-Side Prediction）与**服务器权威**（Server Authority）的深层架构设计——例如UE5的`UCharacterMovementComponent`本质上是在状态复制基础上构建的预测-校正状态机，其`SavedMoves`队列保存了最近256帧的移动快照用于服务器校正回滚。