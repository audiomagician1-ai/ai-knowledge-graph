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

RPC（Remote Procedure Call，远程过程调用）与属性复制是网络多人游戏中实现状态同步的两种互补机制。RPC允许一个网络节点（服务器或客户端）在远端节点上触发函数执行，而属性复制则通过将对象的成员变量标记为"可复制"，让引擎自动检测并广播变更。这两种机制共同构成了现代网络游戏引擎（如Unreal Engine的NetDriver系统）中同步逻辑的基础手段。

属性复制的概念可追溯至1990年代的CORBA分布式对象系统，但将其深度整合进游戏引擎是Quake和Unreal系列引擎在1996至1998年间的创新。Unreal Engine 4/5中，属性复制通过`UPROPERTY(Replicated)`宏标记，服务器每隔固定网络帧（默认66ms，对应约15Hz网络更新频率）检查一次"脏标记"并向相关客户端推送差量。理解这两种机制的不同触发方式和传输特性，能帮助开发者在正确场合选用正确工具，避免带宽浪费或同步漏洞。

## 核心原理

### 属性复制的工作流程

属性复制依赖服务器的权威地位（Authority）。当一个Actor在服务器上修改了被标记为`Replicated`的属性，引擎在下一个网络更新帧会将该属性的新值序列化后通过UDP数据包推送给所有拥有该Actor副本的客户端。客户端收到数据后会直接覆盖本地属性值，并可选地调用`OnRep_属性名()`回调函数执行副作用逻辑（例如播放特效、更新UI）。

属性复制只保证**最终状态一致性**，不保证每次中间变化都被传递。若服务器在同一帧内将血量从100改为50再改为80，客户端最终只会收到80这一个值。因此属性复制适合同步持续状态（位置、血量、弹药数），而不适合同步离散事件（开枪、跳跃）。

### RPC的三种类型

Unreal Engine定义了三种RPC调用方向，理解其方向性是正确使用的关键：

| RPC类型 | 调用方 | 执行方 | 典型用途 |
|---|---|---|---|
| `Server` | 客户端 | 服务器 | 客户端请求服务器执行某动作（如开枪验证） |
| `Client` | 服务器 | 特定客户端 | 服务器向单个客户端推送私有信息（如得分结算） |
| `NetMulticast` | 服务器 | 所有客户端+服务器 | 广播瞬间事件（如爆炸特效触发） |

`Server` RPC默认需标记`Reliable`或`Unreliable`：`Reliable`保证送达但增加延迟开销；`Unreliable`允许丢包，适合高频率低重要性数据（如角色的语音振幅）。Unreal Engine内部以队列方式处理Reliable RPC，连续丢失100个确认包后会强制断开连接。

### 带宽消耗对比与选择依据

属性复制与RPC在带宽开销上差异显著。属性复制采用差量压缩（Delta Compression），仅传输变化的字段；而每次RPC调用都会产生独立的数据报文头（Header开销约为20-40字节）。对于每秒触发超过20次的高频事件，优先考虑将数据存入可复制属性而非连续发送RPC。

条件复制（Conditional Replication）通过`DOREPLIFETIME_CONDITION`宏进一步精细化属性复制目标，例如`COND_OwnerOnly`只向拥有者客户端复制（用于弹药数量），`COND_SkipOwner`则跳过拥有者（用于他人可见的装备状态），有效减少不必要的带宽占用。

## 实际应用

**射击游戏中的开枪逻辑**：玩家按下扳机时，客户端调用`Server_Fire()`（Server RPC）向服务器报告射击意图。服务器执行碰撞检测后，若命中则修改目标Actor的`Health`属性（属性复制自动同步到所有客户端），同时调用`NetMulticast_PlayFireEffect()`播放枪口火焰特效（Multicast RPC，因为特效无需持久存储）。这一组合确保了：判定由服务器权威执行，视觉反馈及时广播，持久数据通过属性自动同步。

**MMO中的背包物品同步**：玩家背包内容属于私有状态，应使用`COND_OwnerOnly`条件复制的`TArray<FItemData> InventoryItems`属性，只同步给拥有者客户端。若服务器发放奖励物品，修改该数组后引擎自动向目标客户端推送，并触发`OnRep_InventoryItems()`更新背包UI，无需手动编写任何Client RPC。

**实时位置同步**：角色的`ReplicatedMovement`结构体（Unreal Engine内置）每帧在服务器更新后以`Unreliable`方式广播给客户端，配合客户端本地的运动预测（Client-Side Prediction），在100ms延迟下仍能保持流畅的视觉表现。

## 常见误区

**误区一：认为客户端可以直接修改复制属性**。属性复制是单向的（服务器→客户端），客户端修改本地的`Replicated`属性值不会传播到其他机器，且下次服务器推送时会被覆盖还原。若需要客户端驱动状态变更，必须先通过`Server` RPC向服务器请求，由服务器执行后通过属性复制同步结果。

**误区二：Multicast RPC等同于属性复制**。`NetMulticast` RPC在调用时刻才向所有当前在线客户端发送，此后新加入的客户端永远不会收到这条RPC。而属性复制会在新客户端请求Actor信息时（Initial Replication阶段）传递属性的当前值。因此用Multicast RPC同步"当前是否着火"状态会导致中途加入的玩家看不到已燃烧的物体——正确做法是用`bool bOnFire`属性复制表示持续状态，Multicast RPC仅触发点火瞬间的粒子特效。

**误区三：Reliable RPC可以无限量使用**。Reliable RPC通过维护确认队列保证送达，但队列长度有上限（Unreal Engine默认256条），超出后会自动降级为Unreliable处理。在高频逻辑（如每帧调用）中滥用Reliable RPC会迅速填满队列，引发不可预期的同步故障。

## 知识关联

本概念直接建立在**状态复制**的基础上：状态复制定义了服务器权威模型和Actor的`bReplicates = true`初始化，RPC与属性复制是状态复制在代码层面的两种具体实现手段。掌握属性复制需要熟悉`GetLifetimeReplicatedProps()`函数——该函数是Unreal Engine中声明所有参与复制的属性清单的强制入口点，遗漏任何属性都会导致该属性静默失效而不报错。RPC机制与网络所有权（Network Ownership）紧密相连，`Server` RPC只能由拥有该Actor的客户端调用，理解这一限制能避免"RPC调用无反应"类问题的调试困境。这两种机制的综合运用，是构建角色移动同步、伤害系统和游戏状态机等更复杂网络功能的直接前置能力。