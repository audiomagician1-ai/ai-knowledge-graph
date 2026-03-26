---
id: "online-subsystem"
concept: "Online Subsystem"
domain: "game-engine"
subdomain: "plugin-development"
subdomain_name: "插件开发"
difficulty: 3
is_milestone: false
tags: ["网络"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.8
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

# Online Subsystem（在线子系统）

## 概述

Online Subsystem（OSS）是 Unreal Engine 5 提供的一套多平台在线服务抽象层，其核心职责是将 Steam、Epic Online Services（EOS）、PlayStation Network、Xbox Live 等各家平台的 SDK 差异屏蔽在统一接口之后。开发者只需调用 `IOnlineSubsystem::Get()` 获取接口指针，无需关心底层是调用 Steam API 的 `SteamMatchmaking()` 还是 EOS 的 `EOS_Lobby_CreateLobby()`，便可实现跨平台的大厅、好友、成就、存档等功能。

OSS 在 UE4.0 时代（约 2014 年）随引擎正式公开发布，最初仅支持 Steam 和主机平台。UE5 时期，Epic 将自家的 EOS 深度集成为默认推荐后端，并通过 `OnlineSubsystemEOS` 插件将其包装成标准 OSS 接口，使得单一代码库可同时服务于 PC、主机和移动端。

OSS 的重要性在于它直接影响多人游戏的可移植性：若不使用它而直接调用 Steam SDK，移植到 PlayStation 时需重写所有网络相关逻辑。采用 OSS 后，更换平台通常只需在 `DefaultEngine.ini` 中切换 `DefaultPlatformService` 一行配置，大幅降低多平台维护成本。

---

## 核心原理

### 接口分层架构

OSS 将在线功能拆分为若干独立接口（Interface），每个接口对应一类服务：

- `IOnlineIdentity`：账号登录与身份验证
- `IOnlineSessionInterface`：会话（Session）的创建、搜索、加入
- `IOnlineFriends`：好友列表与在线状态
- `IOnlineAchievements`：成就解锁与查询
- `IOnlineLeaderboards`：排行榜读写

通过 `IOnlineSubsystem::GetSessionInterface()` 等方法获取各接口的 `TSharedPtr`，若当前平台不支持某接口则返回 `nullptr`，开发者需自行做空指针检查。

### 委托（Delegate）驱动的异步模型

OSS 的所有网络操作均为异步，通过 UE 的委托系统返回结果。例如创建会话时，需先绑定 `OnCreateSessionCompleteDelegate`，调用 `CreateSession()` 后等待委托触发：

```cpp
SessionInterface->OnCreateSessionCompleteDelegates.AddUObject(
    this, &UMyGameInstance::OnCreateSessionComplete);
SessionInterface->CreateSession(0, SessionName, SessionSettings);
```

委托回调中会携带 `bool bWasSuccessful` 参数，以及具体的错误码（`EOnJoinSessionCompleteResult::Type`）。这种模式意味着不能在同一帧内连续依赖多个 OSS 操作的结果，必须以委托链的形式串联调用。

### 插件模块注册机制

每个 OSS 实现（如 Steam、EOS）都是一个独立的 UE 插件，其模块需继承 `IOnlineSubsystemModule` 并向 `FOnlineSubsystemModule` 工厂注册自己的名称。`DefaultEngine.ini` 中的以下配置决定运行时加载哪个实现：

```ini
[OnlineSubsystem]
DefaultPlatformService=EOS

[OnlineSubsystemEOS]
bEnabled=true
```

引擎启动时，`FOnlineSubsystemModule::LoadDefaultSubsystem()` 根据该配置通过模块名动态加载对应插件 DLL，完成实例化。多个 OSS 可同时共存，通过 `IOnlineSubsystem::Get(FName("Steam"))` 指定名称访问非默认实现。

### Session 与 Lobby 的区别

在 OSS 语义中，`Session` 是一个抽象的"可加入游戏实例"，其底层在 Steam 上映射为 Steam Lobby，在 EOS 上映射为 EOS Session 或 EOS Lobby（需通过 `bUsesPresence` 等 `FOnlineSessionSettings` 字段区分）。`FOnlineSessionSettings` 中 `NumPublicConnections`（公开槽位数）、`bShouldAdvertise`（是否广播到大厅列表）等字段直接控制平台 SDK 的对应参数。

---

## 实际应用

**多人房间系统**：在一款 4 人合作游戏中，房主调用 `CreateSession` 创建一个 `NumPublicConnections=4` 的会话，其他玩家通过 `FindSessions` 搜索并调用 `JoinSession` 加入。加入成功后，OSS 返回平台相关的连接地址字符串（通过 `GetResolvedConnectString`），游戏实例再调用 `ClientTravel` 进行实际的 UE 网络连接。全程代码无需区分是 Steam 还是 EOS 后端。

**跨平台成就解锁**：调用 `IOnlineAchievements::WriteAchievements()`，传入 `FOnlineAchievementsWrite` 对象并设置成就 ID 和进度值（0.0f 至 100.0f），OSS 负责将其转化为 Steam 的 `SetAchievement()` 或 PlayStation 的 Trophy 解锁调用。成就 ID 字符串需在各平台开发者后台与代码中保持一致。

**开发阶段使用 NULL 后端**：将 `DefaultPlatformService=NULL` 配置为内置的 `OnlineSubsystemNull`，它在本机通过局域网广播模拟会话搜索，无需任何第三方账号即可测试多人逻辑，是插件开发期间最常用的调试手段。

---

## 常见误区

**误区一：认为 OSS 负责底层网络传输**
OSS 只处理"玩家如何找到彼此并建立连接信息"，即**服务发现层**，而 UE 的 `NetDriver`（基于 UDP 的 `UIpNetDriver` 或 EOS P2P 的 `UEOSNetDriver`）才负责实际的数据包收发。调用 `JoinSession` 只是获得了对方的地址，真正的网络连接由随后的 `ClientTravel` 触发。混淆两者会导致调试时在错误层面寻找延迟或丢包问题。

**误区二：把 OSS 接口当作同步 API 使用**
部分开发者在调用 `FindSessions()` 后立刻读取结果，得到空列表便认为搜索无结果。实际上 `FindSessions` 是异步的，必须等待 `OnFindSessionsCompleteDelegates` 触发，回调中的 `SessionSearch->SearchResults` 数组才包含有效数据。在非委托路径中读取结果是 OSS 开发中最高频的 Bug 来源。

**误区三：同一 OSS 名称在不同平台行为完全一致**
`FOnlineSessionSettings` 的某些字段在不同 OSS 实现中会被忽略。例如 `bUsesStats=true` 在 Steam OSS 中触发统计数据上报，但在 `OnlineSubsystemNull` 中完全无效。开发者需查阅各平台 OSS 插件的源码（位于 `Engine/Plugins/Online/` 目录下）确认哪些字段被真正消费，不能假定所有后端行为对齐。

---

## 知识关联

学习 OSS 需要先理解 **UE5 插件结构**，因为每个 OSS 实现本身就是一个遵循 `IModuleInterface` 生命周期的插件模块，`StartupModule()` 中完成 SDK 初始化，`ShutdownModule()` 中释放 SDK 资源。不熟悉插件模块加载顺序会导致在其他插件的 `StartupModule` 中过早调用 `IOnlineSubsystem::Get()` 而返回空指针。

OSS 与 **UE GameInstance** 紧密配合：`UGameInstance` 是持有 OSS 委托绑定的推荐生命周期载体，因为它跨 Level 存在，不会因场景切换导致委托绑定丢失。与此相关的 **Session 生命周期管理**（`DestroySession` 与 `OnDestroySessionComplete`）也需在 `GameInstance::Shutdown()` 中妥善清理，否则在 Steam 等平台会出现游戏退出后大厅仍残留的问题。