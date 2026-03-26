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

Online Subsystem（简称 OSS）是 Unreal Engine 5 提供的一套标准化抽象接口层，专门用于屏蔽不同平台在线服务（如 Steam、Epic Online Services、PlayStation Network、Xbox Live 等）之间的底层差异。开发者通过统一的 `IOnlineSubsystem` 接口调用好友列表、成就、大厅、会话匹配等功能，无需直接接触各平台 SDK 的原生 API。这一机制由 Epic Games 在 UE4 时代引入，并在 UE5 中持续维护，其核心模块位于引擎源码 `Engine/Plugins/Online/OnlineSubsystem` 目录下。

OSS 的设计目标是"一次编写，多平台运行"。以 Steam 为例，当项目使用 `OnlineSubsystemSteam` 插件时，`IOnlineSession` 接口背后实际调用的是 Steamworks SDK 中的 `ISteamMatchmaking` 接口；切换到 EOS（Epic Online Services）时，同一段代码则驱动 `EOS_Sessions_*` 系列函数，开发者的业务代码无需修改。这种解耦在多平台发行项目中可节省大量适配工作量。

OSS 在插件开发场景中的地位尤为重要：任何需要接入联机功能的 UE5 插件，都必须通过 OSS 而非直接链接平台 SDK，才能保证插件在多平台项目中的可复用性。

---

## 核心原理

### 接口分层架构

OSS 将在线功能拆分为若干独立的子接口，每个子接口对应一类在线服务。常见子接口包括：

| 子接口 | 获取方法 | 负责功能 |
|---|---|---|
| `IOnlineSession` | `GetSessionInterface()` | 房间创建、加入、销毁、搜索 |
| `IOnlineFriends` | `GetFriendsInterface()` | 好友列表、邀请、在线状态 |
| `IOnlineAchievements` | `GetAchievementsInterface()` | 成就解锁与查询 |
| `IOnlineIdentity` | `GetIdentityInterface()` | 用户登录、身份令牌 |
| `IOnlineLeaderboards` | `GetLeaderboardsInterface()` | 排行榜读写 |

每个子接口的方法几乎全部是**异步回调**模式，基于 UE 的 `FDelegate` 系统完成通知。例如调用 `CreateSession()` 后，需要绑定 `OnCreateSessionCompleteDelegates` 委托才能获知创建结果，而不是通过返回值直接判断。

### 子系统的获取与生命周期

在 C++ 中获取当前平台对应的 OSS 实例，标准写法为：

```cpp
IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
if (OSS)
{
    IOnlineSessionPtr SessionInterface = OSS->GetSessionInterface();
}
```

`IOnlineSubsystem::Get()` 会根据 `DefaultEngine.ini` 中 `[OnlineSubsystem]` 段的 `DefaultPlatformService` 配置项返回对应实例，例如设置为 `Steam` 则返回 `FOnlineSubsystemSteam` 对象。若需要在同一进程中同时访问多个平台子系统（如同时使用 EOS 和本地空子系统），可调用 `IOnlineSubsystem::Get(FName("EOS"))` 传入具体名称。

OSS 实例由引擎在模块加载阶段统一创建，插件开发者**不应**手动 `new` 或 `delete` 这些对象，其生命周期由 `FOnlineSubsystemModule` 管理。

### 配置与插件激活方式

OSS 通过 `.ini` 配置与 `.uproject` 插件列表共同控制。以启用 Steam 子系统为例，需要在 `DefaultEngine.ini` 中添加：

```ini
[OnlineSubsystem]
DefaultPlatformService=Steam

[OnlineSubsystemSteam]
bEnabled=true
SteamDevAppId=480
```

同时在 `项目.uproject` 的 `Plugins` 数组中启用 `OnlineSubsystemSteam`。若两者不同步（配置了 Steam 但未启用插件），引擎会回退到 `NULL` 子系统，所有接口调用静默失败，这是初学者最常见的调试陷阱之一。

`NULL` 子系统（`OnlineSubsystemNull`）是 OSS 内置的本地模拟实现，支持局域网会话，不依赖任何第三方 SDK，专门用于开发期本地测试。

---

## 实际应用

### 在插件中封装会话创建逻辑

一个典型的多人游戏插件会将 OSS 的会话操作封装为组件或子系统。以 `UGameInstanceSubsystem` 为载体：

```cpp
void UMySessionSubsystem::CreateGameSession(int32 MaxPlayers)
{
    IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
    IOnlineSessionPtr Sessions = OSS->GetSessionInterface();

    FOnlineSessionSettings Settings;
    Settings.NumPublicConnections = MaxPlayers;
    Settings.bUsesPresence = true;
    Settings.bAllowJoinInProgress = false;

    // 绑定回调
    CreateSessionCompleteDelegateHandle = Sessions->AddOnCreateSessionCompleteDelegate_Handle(
        FOnCreateSessionCompleteDelegate::CreateUObject(this, &ThisClass::OnCreateSessionComplete)
    );

    Sessions->CreateSession(0, NAME_GameSession, Settings);
}
```

`NAME_GameSession` 是引擎预定义的 `FName` 常量，值为 `"GameSession"`，用于标识主游戏会话，区别于用于大厅的 `NAME_PartySession`。

### EOS 插件中的 OSS 应用

Epic Online Services 提供了 `OnlineSubsystemEOS` 插件，它同样实现了全套 `IOnlineSubsystem` 接口。在该插件的 `OnlineSubsystemEOS.uplugin` 中，其 `Type` 字段为 `"Runtime"`，`WhitelistPlatforms` 可指定仅在特定平台加载，这正是 UE5 插件结构中条件加载机制在 OSS 场景下的具体体现。

---

## 常见误区

### 误区一：以为 OSS 接口调用是同步的

OSS 的所有核心操作（创建会话、搜索会话、登录、读取好友列表）均为**异步**执行。直接在调用 `FindSessions()` 后立即读取结果容器，会得到空数据。正确做法是在 `OnFindSessionsComplete` 委托触发后再访问 `FOnlineSessionSearch::SearchResults` 数组。忽略委托绑定是导致联机功能"调了没反应"的首要原因。

### 误区二：直接链接平台 SDK 而绕过 OSS

部分开发者因 OSS 文档不完善而直接在插件中 `#include` Steamworks 头文件并调用 `SteamAPI_*` 函数。这会导致插件在非 Steam 平台（如主机版或 Epic Games Store 版）上编译失败或运行崩溃。OSS 的存在正是为了避免这种硬编码依赖，插件应始终通过 `IOnlineSubsystem` 接口层访问平台功能。

### 误区三：混淆 NULL 子系统与"无网络"状态

`OnlineSubsystemNull` 并非表示"没有在线功能"，而是一个**完整的功能实现**，支持基于 LAN 广播的会话创建与搜索（使用 UDP 广播，默认端口 14001）。在打包测试时若忘记切换配置，项目可能意外使用 NULL 子系统而非目标平台子系统，造成线上功能测试结果与实际平台不符。

---

## 知识关联

### 前置知识衔接

理解 OSS 需要熟悉 **UE5 插件结构**中的模块依赖声明方式。OSS 的各平台实现（如 `OnlineSubsystemSteam`）在其 `.Build.cs` 中通过 `AddEngineThirdPartyPrivateStaticDependencies(Target, "Steamworks")` 引入第三方库，而插件的 `PublicDependencyModuleNames` 中需要包含 `"OnlineSubsystem"` 和 `"OnlineSubsystemUtils"` 模块，后者提供了 `UOnlineEngineInterface` 等 Blueprint 可用的辅助类。不了解 `.Build.cs` 的模块依赖体系，将无法正确配置 OSS 的编译依赖链。

### 横向关联概念

OSS 与 UE5 的 **GameInstance** 生命周期深度绑定：`IOnlineSubsystem::Get()` 在 `GameInstance` 初始化之后才可靠可用，在 `UGameInstance::Init()` 中注册 OSS 委托是业界通行实践。此外，UE5.1 起引入的 **Online Services**（`OnlineServicesInterface`，位于 `Engine/Plugins/Online/OnlineServices`）是 OSS 的下一代替代方案，采用更现代的异步 `TOnlineResult<T>` 模式取代委托回调，两套系统目前并行存在于引擎中，插件开发者需根据目标引擎版本选择使用哪套 API。