---
id: "mn-na-rpc-framework"
concept: "RPC框架"
domain: "multiplayer-network"
subdomain: "network-architecture"
subdomain_name: "网络架构"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# RPC框架

## 概述

远程过程调用（Remote Procedure Call，RPC）是一种让程序像调用本地函数一样调用远程服务器上函数的通信机制。在多人游戏网络中，RPC框架将客户端与服务器之间复杂的消息序列化、传输、反序列化流程封装成对开发者透明的函数调用接口，使游戏逻辑开发者无需手动编写每一条网络消息的打包与解包代码。

RPC的概念最早由Nelson在1981年的论文《Implementing Remote Procedure Calls》中正式提出，此后逐渐演化出多种实现形式。游戏领域中最具代表性的是Unreal Engine从UE3时代沿用至今的Actor RPC系统，以及Unity的MLAPI（现为Netcode for GameObjects）中的`[ClientRpc]`和`[ServerRpc]`属性标记机制。2016年Google开源的gRPC基于HTTP/2和Protocol Buffers，虽然主要用于后端微服务，但也被部分游戏的大厅服务、匹配系统和游戏内服务器端逻辑所采用。

RPC框架在游戏网络中的意义在于：它将"谁在哪台机器上执行这段逻辑"的问题从业务代码中剥离出来。一个角色的`TakeDamage(int damage)`函数，无论最终在服务器还是客户端执行，开发者调用时的代码形式完全一致，框架负责完成路由决策与数据传输。

## 核心原理

### 调用语义与执行目标标注

游戏RPC框架必须解决的第一个问题是：这次调用应该在哪里执行？Unreal Engine的RPC系统定义了三种执行语义：`Server`（仅在服务器执行，客户端发起调用）、`Client`（仅在调用目标Actor的拥有客户端执行，服务器发起调用）、`NetMulticast`（在服务器和所有已连接客户端同时执行）。开发者在声明函数时通过`UFUNCTION(Server, Reliable)`这样的宏标注即可，编译器的代码生成步骤会自动生成对应的`_Implementation`函数体和网络分发存根。

### 可靠性与消息保证

游戏RPC不同于HTTP-RPC的关键差异是需要在UDP传输层之上手动管理可靠性。框架通常提供两种模式：**可靠RPC（Reliable）**通过序列号确认和重传保证消息必达，适用于伤害结算、物品拾取等不可丢失的游戏事件；**不可靠RPC（Unreliable）**则放弃重传，适用于每帧都在发送的动画播放通知或特效触发，丢失一帧不影响体验。Unreal Engine文档明确指出，`Reliable` RPC如果在单帧内堆积超过**256条**未确认调用，会导致连接被强制断开，这是新手开发者常遇到的崩溃原因。

### 序列化与IDL契约

gRPC使用Protocol Buffers（protobuf）作为接口定义语言（IDL），开发者在`.proto`文件中声明函数签名和参数类型，由`protoc`编译器自动生成C++/C#/Go等多语言的客户端存根（stub）和服务端骨架（skeleton）代码。一个典型的游戏匹配服务定义如下：

```protobuf
service MatchmakingService {
  rpc FindMatch(FindMatchRequest) returns (MatchResult);
  rpc StreamMatchEvents(MatchId) returns (stream GameEvent);
}
```

其中`stream`关键字代表服务端流式RPC，可以持续推送实时比赛事件而无需客户端反复轮询。自定义RPC框架（如Photon SDK或Mirror的RPC系统）则通常采用反射或代码生成的方式，将函数名哈希为2字节或4字节的方法ID，以减少每次调用的头部开销。

### 存根生成与透明性机制

RPC框架的核心技术实现依赖于**代理模式**：客户端调用的并非真实函数，而是一个本地存根，存根负责将参数按照约定格式序列化为字节流，附加方法ID和目标对象ID，通过底层传输层发送出去。服务器端的调度器读取方法ID，找到对应的真实函数并反序列化参数后执行。整个往返过程中，调用延迟等于网络RTT（Round-Trip Time）加上序列化/反序列化耗时，对于帧率敏感的游戏逻辑，这意味着不能在`Update`循环中对每个游戏对象无条件发起RPC调用。

## 实际应用

**角色技能触发**：在一款5v5 MOBA游戏中，客户端玩家按下技能键后，本地调用`[ServerRpc] CastSkill(int skillId, Vector3 targetPos)`，服务器验证冷却时间和资源消耗后，再调用`[ClientRpc] PlaySkillEffect(int skillId, Vector3 pos)`广播给房间内所有客户端播放技能特效。验证逻辑在服务器执行，表现逻辑在客户端执行，二者通过两次RPC调用分离。

**gRPC在游戏大厅的应用**：Steam平台风格的游戏大厅服务通常使用gRPC的双向流式调用，服务器通过`stream`持续推送房间人员变化事件，客户端通过同一连接发送准备状态更新，相比WebSocket长连接方案，gRPC内置了负载均衡和TLS支持，并且protobuf序列化体积比JSON减少约**60%-70%**。

**Minecraft的网络包系统**：Minecraft Java版实现了一套自定义RPC框架，将每种游戏操作映射为固定数字ID的数据包。例如`0x1C`包代表实体位置更新，服务器收到后广播给周围区块内的所有玩家。这种手写IDL的方案牺牲了自动代码生成的便利性，但对包大小和处理顺序有完全控制权。

## 常见误区

**误区一：Multicast RPC等同于广播，性能开销可以忽略**。`NetMulticast`调用实际上会将消息分别发送给每一个已连接的客户端，100人服务器上一次Multicast等于服务器发出100条独立消息。正确做法是对静态环境变化使用状态同步，仅对必须实时触发的瞬态事件使用Multicast RPC，并结合Unreal的relevancy系统过滤不在视野范围内的客户端。

**误区二：RPC适合同步所有游戏状态**。RPC是事件驱动的，它传递的是"动作"而非"状态"。若用RPC持续同步角色血量，一旦某条消息丢失或乱序，客户端状态便会永久偏离。血量、位置等持续变化的数值应使用属性复制（Property Replication）或状态同步机制，RPC只适合同步"玩家开枪"这类需要在特定时刻触发一次的事件。

**误区三：gRPC适合游戏实时战斗通信**。gRPC基于HTTP/2运行在TCP之上，其拥塞控制和队头阻塞特性对需要低延迟的实时战斗通信（目标RTT < 50ms）不利。gRPC适用于对延迟不敏感的服务层调用，例如匹配服务、排行榜查询、道具购买等，而实时战斗数据包应使用基于UDP的自定义RPC或ENet等专用库。

## 知识关联

**与网络协议设计的衔接**：RPC框架是构建在网络协议设计之上的应用层抽象。理解了TCP与UDP的可靠性差异、序列号机制和MTU限制后，才能正确判断为何游戏自定义RPC通常选择在UDP上实现可靠层，而非直接使用TCP，也才能理解为何protobuf的紧凑二进制编码对于控制RPC消息大小低于UDP推荐的**1400字节**阈值至关重要。

**为状态同步与帧同步提供基础**：游戏网络架构的进阶方向——帧同步（Lockstep）和状态同步（State Synchronization）——都依赖RPC作为底层消息传递原语。帧同步中每帧的"输入广播"本质上是一次Multicast RPC；状态同步中的脏属性通知也需要类似RPC的分发机制。掌握RPC框架的执行语义、可靠性配置和序列化开销，是进一步优化这两种同步架构的前提。