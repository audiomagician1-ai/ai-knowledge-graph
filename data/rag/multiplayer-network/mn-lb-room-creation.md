---
id: "mn-lb-room-creation"
concept: "房间创建"
domain: "multiplayer-network"
subdomain: "lobby-system"
subdomain_name: "大厅系统"
difficulty: 2
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.364
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 房间创建

## 概述

房间创建（Room Creation）是大厅系统中玩家发起多人游戏会话的入口操作，指由一名玩家（通常成为该房间的Host/主机）向匹配服务器申请分配一个逻辑游戏空间，并设定该空间的初始参数与访问规则的完整流程。房间本质上是服务器端维护的一个状态对象，记录了参与者列表、房间元数据以及当前生命周期阶段。

房间创建机制在早期局域网游戏（如1998年的《星际争霸》Battle.net大厅）中以广播方式实现，Host客户端直接向局域网广播房间信息。随着互联网多人游戏普及，Valve的Steam Matchmaking API（2004年随Source引擎推出）将房间创建标准化为向专用服务器注册的异步请求模式，现代引擎如Unity Relay Service和Epic Online Services均沿用这一思路。

房间创建的质量直接影响游戏会话的稳定性：创建阶段设定的最大玩家数（MaxPlayers）、房间可见性（Public/Private）、自定义属性（Custom Properties）一旦写入服务器，在整个房间生命周期内将作为其他客户端匹配和加入决策的依据。配置错误在此阶段难以热修复，因此正确理解创建参数至关重要。

---

## 核心原理

### 房间创建请求与服务器响应流程

客户端调用创建接口后，请求报文包含三类核心字段：房间名称（RoomName，可选，用于私人邀请）、房间容量（Capacity，通常限制在2–64人之间）、以及初始元数据键值对（Properties Map）。服务器收到请求后执行以下操作：
1. 分配唯一房间ID（一般为UUID v4格式）；
2. 将创建者的Session Token绑定为Owner；
3. 将房间状态置为`OPEN`（等待玩家加入）；
4. 向创建者返回RoomID和加入Token。

整个创建往返时延（RTT）在主流云服务商中应控制在200ms以内，超时则需客户端重试。Photon PUN2框架的`PhotonNetwork.CreateRoom()`方法即遵循此异步回调模式，成功时触发`OnCreatedRoom()`，失败时触发`OnCreateRoomFailed(short returnCode, string message)`。

### 房间配置参数详解

房间创建时可设定的参数分为三个层级：

**基础参数**：`MaxPlayers`（最大玩家数，0表示无限制）、`IsVisible`（是否出现在公开房间列表）、`IsOpen`（是否允许新玩家加入，创建时通常为true）。

**自定义房间属性**（Custom Room Properties）：这是房间创建中最灵活的部分。开发者可将任意键值对附加在房间上，例如`{"map": "desert", "mode": "ranked", "skillLevel": 3}`。在Photon体系中，只有被列入`customRoomPropertiesForLobby`数组的属性键才会被同步到大厅，未列入的属性只有进入房间后才可读取，这一设计用于控制大厅服务器的带宽消耗。

**TTL参数**（Time-To-Live）：`PlayerTtl`指玩家断线后房间为其保留席位的毫秒数（默认0，即立即释放）；`EmptyRoomTtl`指房间在空置状态下被服务器自动销毁前的存活毫秒数，Photon默认值为10000ms（10秒）。合理设置这两个参数对断线重连体验至关重要。

### 房间生命周期状态机

房间从创建到销毁经历以下状态转换：

```
CREATING → OPEN → CLOSED → IN_GAME → ENDED → DESTROYED
```

- **CREATING**：服务器正在处理创建请求，尚未对外可见；
- **OPEN**：房间对外可见且接受加入请求；
- **CLOSED**：房主调用`SetOpen(false)`或人数达到`MaxPlayers`后自动关闭报名，但房间仍在大厅列表中显示（`IsVisible`仍为true）；
- **IN_GAME**：场景加载完毕，游戏逻辑开始运行；
- **ENDED**：游戏结束，房间回到等待状态或直接进入销毁流程；
- **DESTROYED**：`EmptyRoomTtl`超时或房主主动解散，服务器释放房间对象。

---

## 实际应用

**《Among Us》式快速房间创建**：玩家点击"创建游戏"后，客户端向Innersloth服务器提交一个6字符房间码（Room Code）申请，服务器从26^6 ≈ 3亿个可能组合中分配一个未占用的编码作为房间ID，创建时间通常在100ms内完成。这种短码设计使玩家可以通过语音轻松分享房间，无需复制粘贴UUID。

**MMO副本实例化**：在《魔兽世界》等游戏中，玩家组队进入地下城时触发的实例（Instance）创建本质上也是房间创建——服务器动态分配一个独立的地图副本，绑定到当前队伍的Group ID，并在所有成员离开后延迟300秒销毁（即EmptyRoomTtl = 300,000ms）。

**Unity + Mirror框架的本地实现**：在使用Mirror进行局域网开发时，调用`NetworkManager.singleton.StartHost()`会同时创建服务端与客户端，并通过uPnP或手动端口转发广播房间信息，省去中间服务器，适合小规模局域网派对游戏原型开发。

---

## 常见误区

**误区一：房间创建成功等于所有玩家可以立即加入**
实际上，`OnCreatedRoom()`回调触发时，房间仅在主机所在的服务器节点完成注册。对于跨区域的分布式大厅系统（如使用一致性哈希分片的Nakama服务器集群），房间数据同步到其他节点存在最终一致性延迟，通常为50–500ms。在此窗口内，其他区域的玩家搜索该房间可能得到"不存在"的结果，这是正常的CAP理论取舍，而非Bug。

**误区二：MaxPlayers设为0即可容纳无限玩家**
`MaxPlayers = 0`在Photon等框架中确实表示不限制人数，但这并不意味着服务器真的无限扩展。每个房间仍受服务器单一消息转发节点的带宽上限约束，Photon免费套餐房间消息速率上限为500条/秒，20人以上的房间若每帧同步位置（60Hz）将轻松超出此限制。

**误区三：创建房间后随时可以修改所有参数**
`MaxPlayers`和房间可见性（`IsVisible`）在大多数SDK中支持运行时修改，但部分平台（如Xbox Live的SmartMatch）对Session Template中定义的`peerToPeerRequirements`等安全相关参数设置了不可变约束，试图在游戏中途修改会返回`HTTP 403`错误。开发者必须在创建阶段就规划好这些参数，而不是依赖后期修改。

---

## 知识关联

房间创建依赖**会话管理**作为前置条件：玩家必须持有有效的Session Token（包含UserId和认证签名）才能向服务器提交创建请求，匿名Session通常被限制为只能加入公开房间，无法创建。

完成房间创建后，自然衍生出**房间列表浏览**需求——其他玩家需要查询并过滤可用房间；当多名玩家加入同一房间后，**队伍管理**负责将房间内玩家组织为具有角色分工的战队结构。

在网络拓扑层面，房间创建时确定的Host身份直接影响**主机迁移**（Host Migration）策略：若Host掉线，系统需要从已有玩家列表中选取新Owner，而新Owner的Session必须继承原房间的`RoomID`和`Properties`，这一继承机制在房间创建时写入的元数据设计中需预先考虑。最终，当房间从`CLOSED`过渡到`IN_GAME`状态时，**加载同步**接管流程，确保所有客户端在同一帧进入游戏逻辑。
