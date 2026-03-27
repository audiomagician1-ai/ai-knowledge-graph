---
id: "mn-ss-rpc-replication"
concept: "RPC与属性复制"
domain: "multiplayer-network"
subdomain: "state-synchronization"
subdomain_name: "状态同步"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# RPC与属性复制

## 概述

RPC（Remote Procedure Call，远程过程调用）与属性复制是网络多人游戏中实现状态同步的两种核心手段。RPC允许一台机器调用另一台机器上的函数并传递参数，属性复制则通过标记变量让引擎自动将其值从服务器推送到客户端。两者分工不同：RPC处理**事件驱动**的瞬时行为（如开枪、播放音效），属性复制处理**持续存在**的状态（如玩家生命值、位置、弹药数）。

属性复制的思想可以追溯到1996年前后早期多人联机游戏的"状态快照"机制，但现代属性复制在Unreal Engine 3（2006年）中得到了系统化的标记驱动实现，通过`UPROPERTY(Replicated)`宏让开发者显式声明哪些字段需要同步，而非全量广播所有数据。这一设计将带宽消耗降低了30%～60%，取决于Actor的属性数量。

理解两者的差异至关重要：如果用RPC来同步持续变化的血量，每次血量变化都需要显式调用，容易在丢包时造成永久性状态不一致；如果用属性复制来触发"爆炸"特效，引擎会在特定tick将属性值推送，但无法保证每个客户端都能精确收到触发时刻的值。选错工具会导致性能浪费或同步漏洞。

---

## 核心原理

### RPC的三种调用类型

在Unreal Engine的NetMulticast / Server / Client分类体系中，RPC分为三种：

- **Server RPC**：客户端调用，服务器执行。用于客户端向服务器报告意图（如按下跳跃键）。只有拥有该Actor所有权（Ownership）的客户端才能调用，否则调用被静默丢弃。
- **Multicast RPC**：服务器调用，所有已连接客户端及服务器自身执行。典型用途是播放全局音效或特效，例如角色死亡时的爆炸粒子。
- **Client RPC**：服务器调用，仅在该Actor的拥有客户端上执行。常用于给特定玩家发送UI提示，如"你已进入战区"。

RPC本质上是UDP报文上封装的函数调用，**不保证到达**（Unreliable修饰符）或**保证有序到达**（Reliable修饰符）。`Reliable` RPC通过重传机制确保执行，但每个连接同时最多只能有**256个未确认的Reliable RPC**，超出会断开连接，因此高频事件（如每帧发送的移动数据）绝对不应使用Reliable。

### 属性复制的标记与条件机制

属性复制需要两步：首先在声明处加`UPROPERTY(Replicated)`，然后在`GetLifetimeReplicatedProps`函数中用宏`DOREPLIFETIME`注册该属性。

```cpp
UPROPERTY(Replicated)
float Health;

void AMyCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyCharacter, Health);
}
```

引擎在每个**网络更新帧**（默认每秒约100次，由`NetUpdateFrequency`属性控制）比较属性的当前值与上次发送值，仅当发生变化时才生成差量包（Delta）并推送给相关客户端。

属性复制还支持**条件复制**（Conditional Replication），通过`DOREPLIFETIME_CONDITION`宏精细控制推送范围：
- `COND_OwnerOnly`：只复制给该Actor的拥有者，适合弹药数量等隐私数据。
- `COND_SkipOwner`：跳过拥有者，适合同步给旁观者。
- `COND_InitialOnly`：只在Actor首次Spawn时同步一次，适合不会改变的出生点坐标。

### RepNotify回调机制

属性加上`ReplicatedUsing`修饰符后，每当客户端收到该属性的更新，引擎会自动调用指定的回调函数（OnRep函数）：

```cpp
UPROPERTY(ReplicatedUsing = OnRep_Health)
float Health;

UFUNCTION()
void OnRep_Health();
```

OnRep函数是**纯客户端逻辑**，服务器不执行。它的典型用途是在血量变化时更新血条UI、播放受伤音效，或根据新旧值判断是否刚刚复活。需注意：OnRep函数不会在服务器本地赋值时触发，只在网络数据到达时触发，因此服务器端的UI更新必须单独处理。

---

## 实际应用

**案例一：角色受伤系统**

血量`Health`使用`ReplicatedUsing=OnRep_Health`标记，服务器在判定命中后直接修改`Health`值，属性复制自动将新值推送到所有相关客户端。客户端的`OnRep_Health`回调负责刷新血条UI和播放受伤动画。"造成伤害"这个动作本身不需要RPC，因为服务器是权威端，直接修改即可。

**案例二：技能特效触发**

玩家释放技能时，客户端先发送Server RPC `ServerCastSkill(SkillID)`，服务器验证合法性后，调用Multicast RPC `MulticastPlaySkillEffect(SkillID, Location)`在所有客户端播放特效。此场景不适合用属性复制，因为特效是一次性事件，若用布尔属性`bSkillActive`来触发，两次快速连续的技能释放可能导致属性值先变为true再变回false，客户端只收到最终false值，第二次特效被吞掉。

**案例三：门的开关状态**

门的`bIsOpen`布尔属性用`DOREPLIFETIME_CONDITION(ADoor, bIsOpen, COND_InitialOnly)`在新玩家加入时同步初始状态，之后通过服务器权威逻辑直接修改，结合RepNotify播放开门动画。晚加入的玩家会正确看到门的当前状态，而不是默认关闭状态。

---

## 常见误区

**误区一：对高频数据使用Reliable RPC**

移动同步、瞄准方向等每帧变化的数据若使用`Reliable`修饰符，在网络抖动时会堆积大量未确认的RPC，触发256条上限后服务器直接断开该客户端连接。正确做法是使用`Unreliable`并在应用层实现状态插值补偿（如Unreal内置的CharacterMovement组件）。

**误区二：在属性复制中依赖OnRep的执行顺序**

若两个属性A和B都有RepNotify，且B的OnRep逻辑依赖A的最新值，实际上引擎不保证OnRep_A一定在OnRep_B之前执行。正确做法是在OnRep_B内直接读取当前A的属性值（此时A的新值已由网络包写入，只是回调顺序不定），而非假设回调按声明顺序触发。

**误区三：RPC可以替代权威服务器逻辑**

部分开发者用Client RPC将"你的攻击命中了"的结论发给客户端，让客户端自行扣血。这实际上将权威判断移交给客户端，形成作弊漏洞。RPC传递的应是**服务器已验证的结果**或**客户端的意图请求**，伤害计算、碰撞判定等逻辑必须在服务器上执行。

---

## 知识关联

**前置概念——状态复制**：理解服务器-客户端的所有权模型（哪个客户端拥有哪个Actor）是正确使用Server RPC和Client RPC的前提，因为调用权限与所有权直接绑定。没有状态复制的基础概念，`COND_OwnerOnly`等条件复制宏的语义将难以理解。

**与移动预测的联系**：属性复制的`NetUpdateFrequency`默认值（角色通常设为100Hz，背景Actor可低至2Hz）直接影响玩家感知到的延迟。高移动速度的角色需要更高的更新频率，而OnRep回调配合插值算法是实现客户端平滑移动的标准路径。

**与网络优化的联系**：条件复制`COND_OwnerOnly`和低频`NetUpdateFrequency`是带宽优化的两大直接手段，理解属性复制的差量比较机制后，才能正确评估将哪些字段拆分为独立属性以最小化每帧的复制负载。