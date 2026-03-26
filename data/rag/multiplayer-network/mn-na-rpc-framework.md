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

远程过程调用（Remote Procedure Call，RPC）是一种允许程序像调用本地函数一样调用运行在另一台机器上的函数的通信机制。在多人游戏中，客户端可以通过RPC通知服务器"玩家开枪了"，服务器也可以通过RPC广播"某玩家的血量变为75点"——这些调用在代码层面看起来与本地函数调用几乎相同，但底层实际上通过网络序列化参数、传输数据包并在远端执行对应函数。

RPC概念最早由Birrell和Nelson于1984年在论文《Implementing Remote Procedure Calls》中系统提出。游戏行业对RPC的使用可以追溯到早期MMO时代，Quake引擎在1996年就使用了类似RPC的消息分发机制来同步游戏状态。现代游戏引擎如Unreal Engine将RPC分为三类（Server、Client、NetMulticast），直接内建于引擎的网络复制系统中；Unity的Netcode for GameObjects同样提供了`[ServerRpc]`和`[ClientRpc]`属性标注方式。

RPC框架之所以在游戏网络编程中受到重视，是因为它将"通信"问题转化为"函数调用"问题，大幅降低了手动拼装字节流的开发负担。相比直接操作原始Socket，使用RPC框架可以将游戏逻辑代码中的网络通信样板代码减少60%-80%，同时框架本身可以统一处理序列化、连接管理和错误重试等横切关注点。

## 核心原理

### 调用流程与桩代码（Stub）

RPC的执行分为客户端桩（Client Stub）和服务端桩（Server Stub）两部分。客户端调用本地的Client Stub，该Stub将函数名称和参数序列化（Marshal）成字节流，通过网络发送给服务端；服务端的Server Stub接收字节流后反序列化（Unmarshal）参数，找到对应的真实函数并执行，最后将返回值以相同方式回传。在游戏场景中，参数序列化的效率至关重要：gRPC使用Protocol Buffers（protobuf）二进制格式，一个包含位置坐标`{x:1.5, y:2.3, z:0.0}`的消息编码后仅需约12字节，而等效JSON需要30+字节。

### 同步RPC与异步RPC的选择

游戏RPC几乎全部采用异步（Fire-and-Forget）模式，而非传统的同步阻塞调用。同步RPC会阻塞调用线程等待远端响应，在16.67ms（60fps帧预算）的游戏帧时间内，一次50ms的网络往返延迟会直接导致帧率崩溃。因此游戏中的RPC通常不返回值，而是通过回调函数或Promise/Future机制处理响应。Unreal Engine的NetMulticast RPC就是典型的单向广播调用，服务器调用后不等待任何客户端确认。

### 可靠性与顺序保证

游戏RPC框架必须允许开发者选择底层传输的可靠性级别。Unreal Engine的RPC支持`Reliable`和`Unreliable`两种标注：`Reliable`调用基于ACK确认机制保证送达但有延迟开销，适用于"玩家死亡"、"开门"等状态变更事件；`Unreliable`调用不保证送达，适用于每帧更新的位置信息（丢几包不影响体验）。自定义RPC框架通常使用消息序号（Sequence Number）字段来检测乱序和丢包，Valve的Source引擎网络层使用4字节序列号字段跟踪可靠消息。

### gRPC与自定义RPC的对比

gRPC是Google于2016年开源的通用RPC框架，使用HTTP/2作为传输层，支持双向流式传输（Bidirectional Streaming），适合游戏的大厅服务、匹配系统和聊天系统等延迟不敏感的服务端-服务端通信。然而gRPC在游戏实时战斗同步场景中存在明显劣势：HTTP/2的头部压缩和流量控制机制引入了约10-20ms的额外延迟，且无法直接使用UDP传输。主流的大型多人游戏（如《PUBG》、《Fortnite》）在实时同步部分均使用基于UDP的自定义RPC，只在后端微服务通信中使用gRPC。

## 实际应用

**Unreal Engine中的战斗系统RPC示例：**

```cpp
// 声明一个可靠的服务端RPC，客户端调用通知服务器发起攻击
UFUNCTION(Server, Reliable, WithValidation)
void ServerFireWeapon(FVector AimDirection);
```

服务端收到后验证合法性，再通过`NetMulticast_PlayFireEffect()`广播特效给所有客户端。这种"客户端请求→服务器验证→广播结果"的三段式RPC模式是权威服务器架构的标准实现方式，能有效防止客户端作弊。

**MMO中的技能释放流程：**在《World of Warcraft》式的MMO中，玩家释放技能时客户端立即发送一个`CastSpell(spellId, targetGuid)`的RPC到服务器，服务器进行冷却时间、魔法值、施法距离的合法性校验后，再通过RPC通知相关区域内的客户端播放特效和扣血数值。这里的RPC参数设计非常精炼：仅传递技能ID（2字节）和目标GUID（8字节），而不传递坐标等可以由服务器自行查询的冗余信息。

## 常见误区

**误区一：认为RPC调用是即时生效的。** 许多初学者编写`ClientRpc_UpdateHealth(50)`后，在同一帧内读取客户端血量时会发现值并未更新。RPC通过网络传输，存在至少一个网络往返时间（RTT，通常20-150ms）的延迟。客户端在收到并执行RPC之前，血量变量仍是旧值。正确做法是在UI更新逻辑中监听状态变化回调，而非RPC调用后立即读取。

**误区二：所有RPC都应该声明为Reliable。** 将位置同步、动画状态等高频RPC声明为`Reliable`会导致可靠消息队列（Reliable Channel）堆积。Unreal Engine的可靠通道有最大未确认包数量限制（默认256个），超出后连接会被强制断开。每帧调用的位置更新RPC必须设为`Unreliable`，并配合插值（Interpolation）算法平滑处理丢包。

**误区三：混淆RPC与属性复制（Property Replication）的使用场景。** RPC适合描述"事件"（开枪、跳跃、捡起道具），而属性复制适合描述"状态"（当前血量、位置、是否存活）。若用RPC同步血量（每次扣血都发一个RPC），当晚加入的客户端将错过所有历史RPC调用，无法得知当前血量；而属性复制在新客户端连接时会自动发送当前值。

## 知识关联

RPC框架建立在**网络协议设计**的基础之上：自定义RPC的消息格式设计直接应用了自定义协议中的消息头设计、操作码（Opcode）映射和字节对齐原则。例如，一个高效的游戏RPC消息头通常包含：2字节操作码（标识调用哪个函数）、2字节消息长度、4字节序列号，总共仅8字节开销。

在掌握RPC框架后，可以进一步学习**状态同步系统**（Delta Compression、快照插值）和**网络预测与回滚**（Rollback Netcode）——这些高级技术都以RPC作为基础通信原语，在RPC传递的事件和状态之上构建时间轴管理和客户端预测逻辑。