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

状态复制（State Replication）是多人游戏中服务器将游戏对象的权威状态自动同步到所有客户端的机制。其核心思想是：服务器持有唯一的"真相"，客户端的本地状态是服务器状态的镜像副本。当服务器上某个Actor的血量从100变为75时，状态复制系统负责将这一变化推送至每一个已连接的客户端，无需游戏逻辑手动发送网络消息。

状态复制概念的工程化实现可追溯至1990年代的DOOM（1993）网络代码，但现代框架级状态复制的标志性产物是Unreal Engine在虚幻竞技场（Unreal Tournament，1999）开发期间建立的Replication系统。该系统将复制逻辑从游戏代码中抽象出来，由引擎统一管理对象生命周期、属性变更检测和数据序列化，开发者只需声明"哪些属性需要复制"，引擎负责其余全部工作。

状态复制的重要性体现在它解决了网络游戏最根本的一致性问题：所有玩家需要在同一个虚拟世界中交互，而物理上每人的数据副本存在毫秒级乃至秒级延迟差异。没有状态复制，开发者每次修改一个游戏变量都必须手动编写序列化、发送和反序列化代码，这在拥有数百个可变属性的现代游戏中完全不可行。

---

## 核心原理

### Actor网络角色（NetRole）与复制方向

UE5中每个Actor实例都持有两个枚举值：`Role`（本机角色）和 `RemoteRole`（远端角色），取值来自`ENetRole`枚举，包含`ROLE_Authority`（权威端，即服务器）、`ROLE_SimulatedProxy`（模拟代理，其他玩家的客户端视图）和`ROLE_AutonomousProxy`（自主代理，拥有控制权的本地客户端）。

复制方向**只能从Authority流向Proxy**，这是状态复制与RPC的根本区别。服务器上`Role == ROLE_Authority`的Actor修改了标记为`Replicated`的属性，引擎在下一次网络更新tick时将差异值序列化后广播给所有拥有该Actor相关代理的客户端。客户端不能通过属性复制机制向服务器写入状态。

### 属性标记与脏标记机制

要使某个C++成员变量参与状态复制，必须在`GetLifetimeReplicatedProps`函数中用宏`DOREPLIFETIME(ClassName, PropertyName)`注册，并在变量声明处附加`UPROPERTY(Replicated)`说明符。引擎内部为每个已注册属性维护一个**脏标记（dirty bit）**：当Authority端属性值发生变更时，脏标记被置位；在网络更新周期（默认与游戏tick频率解耦，服务器NetUpdateFrequency通常为100Hz，客户端Actor默认值为`NetUpdateFrequency = 100.0f`）中，引擎扫描所有脏标记并仅序列化发生变化的属性，这种**增量复制**策略大幅降低了带宽消耗。

条件复制宏`DOREPLIFETIME_CONDITION`进一步精细化控制，例如`COND_OwnerOnly`使属性只复制给Actor的拥有者，`COND_SkipOwner`跳过拥有者只同步其他人，`COND_InitialOnly`仅在Actor首次在客户端生成时复制一次初始值，此后不再同步变更。

### RepNotify回调机制

当客户端属性被远端值覆写时，开发者可以声明`OnRep_PropertyName()`函数并在`UPROPERTY`中写`ReplicatedUsing=OnRep_PropertyName`，引擎在成功写入新值**之后**立即调用该函数。此回调是客户端响应状态变化（如播放受击动画、更新UI血条）的标准入口点。需要注意回调参数可以接受旧值：`OnRep_Health(float OldHealth)`，这样可以根据血量差值决定播放轻伤还是重伤特效，而无需客户端自己维护历史状态。

---

## 实际应用

**多人射击游戏中的血量同步**：玩家A被击中后，服务器上Authority Actor的`Health`属性从100.0降至65.0。由于`Health`注册了`DOREPLIFETIME`，引擎在下一个网络帧将差值序列化为4字节浮点数，推送至所有相关客户端。玩家A的客户端收到更新后触发`OnRep_Health`，HUD血条立刻从满格缩短；其他旁观玩家的客户端同步收到更新，他们看到的玩家A头顶血量条也相应减少。整个过程游戏逻辑层完全不涉及Socket操作。

**门的开关状态同步**：关卡中一扇门使用`bool bDoorOpen`存储开关状态，配合`OnRep_DoorOpen`回调驱动蓝图时间轴播放开门动画。当服务器设置`bDoorOpen = true`后，晚加入的客户端也能通过`COND_InitialOnly`以外的默认条件收到当前状态，保证新玩家进入服务器时看到的是已经打开的门，而不是初始关闭状态。

**网络优先级与相关性（Relevancy）**：状态复制并非对所有客户端无差别发送。UE5通过`NetCullDistanceSquared`（默认225,000,000 平方厘米，即约150米）控制复制相关性：超出该距离的Actor不会向对应客户端复制任何属性，节省带宽的同时防止信息泄露。

---

## 常见误区

**误区一：认为状态复制是实时的**。状态复制受`NetUpdateFrequency`控制，存在固有的帧间延迟。一个Actor若将`NetUpdateFrequency`设为10（即每秒最多10次更新），则两次复制之间最多有100ms的状态滞后。将其误设为1Hz后抱怨"属性同步太慢"是典型的配置错误，而不是引擎缺陷。

**误区二：在客户端直接修改Replicated属性会同步回服务器**。客户端对`Replicated`属性的本地修改既不会上传服务器，也会在下一次服务器推送到来时被覆盖还原。许多初学者在客户端写`Health -= 10`后发现值"弹回"，根本原因正在于此。需要修改权威状态必须通过Server RPC（`UFUNCTION(Server, Reliable)`）请求服务器操作。

**误区三：RepNotify在服务器端也会触发**。默认情况下`OnRep_`函数**只在客户端执行**，服务器直接修改属性本身不经过该回调。若需要服务器在属性变更时也执行某些逻辑，应在赋值语句之后显式调用，或使用`UFUNCTION(Server)` + 单独的逻辑函数，而不是依赖RepNotify的自动触发。

---

## 知识关联

状态复制是理解UE5多人网络的入门基础。学习本概念之前无需掌握特定网络理论，但需要具备UE5 Actor生命周期和UPROPERTY宏的基本认知。

掌握状态复制后，下一步自然进入**RPC与属性复制**的对比学习：状态复制解决"What（当前值是什么）"的问题，而RPC解决"When（某个瞬时事件何时发生）"的问题。例如，子弹击中的瞬间爆炸特效不应该用属性复制（因为它是一次性事件而非持久状态），而应使用`NetMulticast RPC`广播给所有客户端。两者的选择标准——**持久状态用复制属性，瞬时事件用RPC**——是多人游戏网络架构设计的核心判断依据。