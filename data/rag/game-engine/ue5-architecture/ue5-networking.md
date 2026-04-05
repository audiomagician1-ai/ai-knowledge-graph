---
id: "ue5-networking"
concept: "UE5网络架构"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 3
is_milestone: false
tags: ["网络"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# UE5网络架构

## 概述

UE5的网络架构建立在虚幻引擎长达二十余年迭代的客户端-服务器（Client-Server）模型之上，其设计目标是让游戏逻辑开发者在多数情况下无需手动处理底层套接字通信。该架构的三大支柱是：属性复制（Replication）、远程过程调用（RPC）以及网络驱动（NetDriver）。UE5的网络代码入口位于`Engine/Source/Runtime/Engine/Classes/Engine/NetDriver.h`，整个系统在游戏运行时由`UNetDriver`实例统一调度。

该架构采用**权威服务器**（Authoritative Server）模式，即Server拥有游戏状态的最终决定权，Client只能通过RPC向Server发送请求，再由Server将最新状态复制回各Client。这与点对点（P2P）架构本质不同：在UE5默认模型下，没有任何Client可以直接修改另一个Client所看到的Actor状态。这一设计使作弊防御更容易实现，但也意味着所有需要同步的逻辑必须标记正确的网络角色（NetRole）。

UE5在UE4基础上引入了**Iris Replication System**（虚幻引擎5.1起作为实验功能，5.3起可生产使用），以替换沿用多年的传统复制管道，重点解决大规模场景下的CPU瓶颈问题。传统系统使用逐Actor轮询方式检查脏标志（dirty flag），而Iris改用基于筛选器（Filter）和数据包组（ReplicationGroup）的批量处理管道，在千人同屏场景下可将复制CPU开销降低约40%。

## 核心原理

### 属性复制（Property Replication）

属性复制的触发前提是：Actor的`bReplicates`设置为`true`，且该属性在`GetLifetimeReplicatedProps`函数中通过`DOREPLIFETIME`宏进行注册。服务器在每个网络帧（默认频率由`NetUpdateFrequency`控制，默认值为100Hz）检查已标记为复制的属性是否与上次发送给该Client的快照（Shadow State）存在差异；若存在差异则将变更打包进UDP数据包发往对应Client。

```cpp
// 典型注册示例
void AMyActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyActor, Health);
    DOREPLIFETIME_CONDITION(AMyActor, AmmoCount, COND_OwnerOnly);
}
```

`COND_OwnerOnly`是15种内置条件之一，表示该属性仅同步给拥有该Actor的Client，可显著减少不必要的带宽消耗。当属性到达Client后，引擎自动调用标记了`ReplicatedUsing`的回调函数（`OnRep_`函数），开发者在此处更新视觉效果或触发本地逻辑。

### 远程过程调用（RPC）

RPC分为三种类型，其方向和执行位置完全不同：
- **Server RPC**：由Client调用，在Server上执行；必须标记`WithValidation`以防止恶意Client滥用。
- **Client RPC**：由Server调用，在拥有该Actor的Client上执行；常用于播放UI反馈或音效。
- **NetMulticast RPC**：由Server调用，同时在Server本机及所有已连接Client上执行。

RPC在UFUNCTION宏中通过`Server`、`Client`、`NetMulticast`关键字声明。需要特别注意：**RPC不保证送达**——底层使用UDP传输，仅当RPC被声明为`Reliable`时引擎才会增加确认重传机制，因此高频调用（如每帧触发的移动更新）应使用`Unreliable`以避免队列堆积导致延迟激增。

### 网络驱动（NetDriver）与连接管理

`UNetDriver`是整个网络栈的调度核心，负责管理`UNetConnection`列表和`UChannel`体系。每个已连接的Client对应一个`UNetConnection`，其内部包含若干`UActorChannel`，每个`UActorChannel`负责一个已复制Actor的状态同步。

`UNetDriver`的默认实现是基于UDP的`UIpNetDriver`，底层通过`FSocket`与平台无关的套接字抽象层通信。在Steam或Epic Online Services环境下，可替换为`UOnlineSubsystemSteamNetDriver`等自定义实现，而上层的Replication逻辑完全不变。NetDriver还集成了**包预算（Packet Budget）**机制：每个Client每帧可发送的字节数由`MaxClientRate`（默认15000 bytes/s）和`MaxInternetClientRate`控制，超出预算的数据包将被延后到下一帧发送。

### 网络角色（NetRole）与相关性（Relevancy）

每个Actor在每个机器上拥有`ENetRole`枚举值：`ROLE_Authority`（服务器本机）、`ROLE_AutonomousProxy`（拥有该Actor的Client）、`ROLE_SimulatedProxy`（其他Client）。大量UE5系统（如`CharacterMovementComponent`的本地预测逻辑）通过判断`GetLocalRole()`来决定是否执行物理模拟还是仅插值显示。

Actor**相关性**（IsNetRelevantFor）决定服务器是否为某Client复制该Actor。默认规则基于距离阈值`NetCullDistanceSquared`（默认225,000,000平方厘米，即1500米），超出距离的Actor不会被复制给该Client。开发者可重写`IsNetRelevantFor`实现视锥体裁剪、队友可见性等自定义逻辑。

## 实际应用

**多人射击游戏的生命值同步**：`Health`属性在Server上扣减后通过`DOREPLIFETIME`自动同步到所有Client；同时Server向受击Client发送`Client RPC`播放受击音效（仅该玩家听到），向全体Client发送`NetMulticast RPC`触发血液粒子效果（所有人可见）。两种机制分工明确，避免用一个NetMulticast RPC做所有事情。

**大型开放世界的兴趣管理**：《堡垒之夜》等基于UE的大型多人游戏通过自定义`NetDriver`的Prioritization函数，对重要Actor（如持枪敌人）提高`NetPriority`值（默认1.0，关键Actor可设为3.0），确保在带宽受限时优先更新高威胁目标，低优先级的背景NPC则降频更新。

**Iris系统的实际迁移**：在`DefaultEngine.ini`中添加`[/Script/Iris.IrisSettings] bEnableIris=true`即可在UE5.3+项目中启用Iris管线。启用后原有的`DOREPLIFETIME`宏和`OnRep_`函数无需修改，Iris通过`UObjectReplicationBridge`自动适配现有代码。

## 常见误区

**误区一：认为NetMulticast RPC与属性复制可以互相完全替代。** 实际上两者的语义根本不同：属性复制保证新加入的Client能收到当前最新值（状态同步），而Multicast RPC是瞬时事件，中途加入的Client永远不会收到已经广播过的RPC调用。因此"爆炸发生"这类一次性事件适合用RPC，而"当前HP为80"这类持久状态必须用属性复制。

**误区二：认为`Reliable` RPC不会有任何问题，所有RPC都应设为Reliable。** UE5的Reliable RPC使用序号确认机制，底层维护一个发送窗口；当某条Reliable RPC因网络丢包迟迟未收到ACK时，后续所有Reliable消息都会被阻塞（队头阻塞问题）。官方文档明确指出每帧调用Reliable RPC超过一定次数（通常认为超过约10次/秒）会导致连接不稳定乃至断线。

**误区三：误以为在Client端直接修改Actor属性会同步到Server。** Client端对`ROLE_SimulatedProxy` Actor的属性修改只影响本地表现，下一次Server复制数据到来时会直接覆盖Client的本地修改。若Client需要影响服务器状态，必须通过`Server` RPC主动请求，服务器验证后再通过属性复制更新所有端。

## 知识关联

UE5网络架构以**GameFramework**（`AGameMode`、`APlayerController`、`APawn`等类）为运行基础：`AGameMode`仅存在于Server，负责权威逻辑；`APlayerController`在Server和对应Client各有一份，是Server RPC的典型载体；`APawn`在所有Client上有复制实例。理解`NetRole`枚举与这些类在不同机器上的存在性，是正确使用Replication和RPC的前提条件。

在UE5的高级网络开发中，网络架构与**在线子系统（Online Subsystem）**紧密协作：会话创建、匹配和NAT穿透由Online Subsystem处理，连接建立后的数据同步才移交给NetDriver。此外，**CharacterMovementComponent**内置的客户端预测（Client Prediction）和服务端校正（Server Reconciliation）逻辑是对本架构最复杂的实际应用，其源码`CharacterMovementComponent.cpp`超过14000行，完整展示了如何在该网络架构约束内实现流畅的本地手感。