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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 房间创建

## 概述

房间创建（Room Creation）是大厅系统中玩家发起多人游戏会话的入口操作，指由某一客户端向服务器申请分配一个独立的游戏房间实体，并附带初始化参数，使其他玩家随后可以加入这个逻辑空间共同游戏。房间在服务器端通常表示为一个包含元数据（房间名称、最大人数、地图、模式等）和成员列表的数据结构，而房间创建就是向这个结构写入初始值、分配唯一 Room ID 的过程。

从历史沿革来看，早期局域网游戏（如1999年发布的《星际争霸》Battle.net大厅）采用广播发现机制，房间创建仅相当于客户端开始监听某个端口并广播自身存在。随着互联网多人游戏的普及，专用大厅服务器模式逐渐成为主流：房间创建请求由客户端发往中心服务器，服务器统一分配资源，避免了NAT穿越失败导致房间无法被发现的问题。现代云游戏中间件（如Photon、Mirror、Nakama）将房间创建封装为一次 RPC 或 REST 调用，底层自动处理房间的状态持久化与路由。

房间创建在大厅系统中的重要性体现在：它是整个多人游戏会话生命周期的起点，房间的初始参数（特别是最大人数上限 `MaxPlayers` 和可见性标志 `IsVisible`）直接决定后续的匹配效率和玩家体验。配置错误（如最大人数设为0或房间未设为公开）会导致房间永远无法填满或出现在列表中，这些问题往往在创建阶段就已埋下。

---

## 核心原理

### 创建请求的参数结构

一次标准的房间创建请求通常包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `RoomName` | string | 房间显示名称，可选（留空时服务器自动生成 GUID） |
| `MaxPlayers` | uint8 | 最大玩家数，典型值为 2~64 |
| `IsVisible` | bool | 是否出现在房间列表中 |
| `IsOpen` | bool | 是否允许新玩家加入 |
| `CustomProperties` | map | 业务自定义属性，如地图名、游戏模式、密码哈希 |

以 Photon PUN2 为例，创建房间的核心调用为：
```csharp
RoomOptions options = new RoomOptions {
    MaxPlayers = 8,
    IsVisible = true,
    IsOpen = true,
    CustomRoomProperties = new Hashtable { {"map", "desert"} }
};
PhotonNetwork.CreateRoom("MyRoom", options, TypedLobby.Default);
```
服务器收到请求后返回一个 `RoomID`（在 Photon 中即房间名，在 Nakama 中为 UUID 字符串），此后所有加入操作都引用这个 ID。

### 房间生命周期状态机

房间从创建到销毁经历明确的状态转换：

```
[Created] → [WaitingForPlayers] → [InProgress] → [Finished] → [Destroyed]
```

- **Created**：服务器完成分配，创建者（即"房主"，Host）自动加入，人数为1。
- **WaitingForPlayers**：房间处于 `IsOpen=true` 状态，接受其他玩家加入。
- **InProgress**：房主调用开始游戏逻辑，通常将 `IsOpen` 设为 `false` 阻止新成员加入。
- **Finished/Destroyed**：所有玩家离开后，服务器销毁房间，释放 RoomID。

值得注意的是，若创建者在 `WaitingForPlayers` 阶段断线，需要主机迁移机制接管，否则房间直接进入 `Destroyed` 状态，这是房间创建阶段就应设置"是否允许主机迁移"标志的原因。

### 服务器端的房间分配策略

服务器在处理创建请求时，存在两种主要分配模式：

1. **名称冲突处理**：若客户端指定的 `RoomName` 已存在，服务器应返回错误码（Photon 返回 `ErrorCode.GameAlreadyExists = 32758`），而非静默覆盖。客户端需捕获此错误并提示玩家重命名。

2. **自动命名模式**：`RoomName` 传入空字符串时，服务器生成唯一标识（通常为 UUID v4），适合快速匹配场景。此时玩家通过邀请码或深层链接分享房间，而非手动输入名称。

房间元数据的存储位置也影响性能：轻量大厅（如 Photon 的 Lobby）只索引被标记为 `CustomRoomPropertiesForLobby` 的字段，未标记的自定义属性不参与列表过滤，从而减少大厅广播流量。

---

## 实际应用

**多人射击游戏的标准创建流程**：玩家在主菜单点击"创建房间"，客户端弹出配置界面，填写房间名（最多16个字符）、选择地图和模式、设置最大人数（4/8/16）及是否需要密码。确认后调用创建 API，等待服务器返回成功回调（`OnCreatedRoom`），随后 UI 切换至房间等待界面，显示当前玩家列表和开始按钮。

**快速联机（Quickmatch）场景**：系统尝试加入已有房间失败（无可用房间）时，自动降级为创建房间——即"加入或创建"（Join or Create）模式。Photon 提供 `PhotonNetwork.JoinRandomOrCreateRoom()` 接口直接封装这一逻辑，避免开发者手动处理"加入失败→创建"的状态跳转。

**房间密码的正确处理**：密码不应以明文存储于 `CustomProperties`，而应在客户端本地计算哈希（如 SHA-256 截取前8字节）后传入，服务器仅存储哈希值。加入时对比哈希而非原始密码，防止服务器日志泄露明文密码。

---

## 常见误区

**误区一：认为房间创建成功等同于游戏服务器就绪**
房间创建成功仅代表大厅服务器上的元数据记录已建立，游戏逻辑服务器（Game Server）的实例化是另一个异步过程，在使用专用服务器架构（Dedicated Server）时尤为明显。若开发者在 `OnCreatedRoom` 回调中立即发送游戏内 RPC，可能因游戏服务器尚未就绪而丢包。正确做法是等待 `OnJoinedRoom` 且服务器确认 `PlayerCount >= 1` 后，再初始化游戏逻辑。

**误区二：将 `MaxPlayers` 设为大值以"灵活使用"**
部分开发者将 `MaxPlayers` 设为 255 以避免人数限制，但服务器的位置同步、状态广播的带宽消耗与玩家数量正相关（P2P 模型下为 O(n²) 的连接数）。20人的房间其全连接状态数据量约为4人房间的25倍。`MaxPlayers` 应根据游戏类型精确设置，而非作为保险值随意填写。

**误区三：房间名唯一性依赖客户端检查**
先检查再创建（Check-Then-Act）是典型的竞态条件：客户端查询"MyRoom是否存在"返回否，但在创建请求到达服务器前，另一个客户端已用相同名称创建了房间。正确做法是完全依赖服务器的原子性冲突检测，客户端只处理服务器返回的 `GameAlreadyExists` 错误码，而非在本地预判。

---

## 知识关联

**前置概念——会话管理**：房间创建必须在客户端持有有效会话（Session Token）的前提下进行，服务器通过会话验证创建者身份，防止匿名客户端无限创建房间耗尽服务器资源。会话中的 `UserID` 将被写入房间元数据作为 OwnerID。

**后续概念——房间列表浏览**：房间创建时设置的 `IsVisible` 标志和 `CustomRoomPropertiesForLobby` 字段，直接决定该房间如何出现在其他玩家的浏览列表中，两者通过大厅服务器的索引机制关联。

**后续概念——队伍管理**：房间创建后，可在房间内进一步划分队伍，队伍数据作为 `CustomProperties` 的子结构挂载在房间上，队伍管理的上限（如最多几支队伍）受制于创建时 `MaxPlayers` 的值。

**后续概念——主机迁移**：是否在创建时启用主机迁移标志（Photon 中为 `PlayerTtl` 和 `EmptyRoomTtl` 参数），决定了房主断线时房间是立即销毁还是等待新主机接管，这是房间创建阶段最关键的容错配置之一。