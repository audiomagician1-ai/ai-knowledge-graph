---
id: "ue5-gameframework"
concept: "UE5 GameFramework"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 2
is_milestone: false
tags: ["框架"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# UE5 GameFramework

## 概述

UE5 GameFramework 是 Unreal Engine 5 中定义游戏规则、管理玩家状态与控制逻辑的一套 C++ 类体系，其核心由 `AGameModeBase`、`AGameStateBase`、`APlayerController`、`APlayerState`、`APawn` 五个基础类构成。这套体系最初由 Epic Games 在 UE3 时代引入，至 UE4.14 版本正式将 `AGameMode` 拆分为 `AGameModeBase`（轻量版）与 `AGameMode`（含比赛流程状态机版），UE5 延续此设计并在底层进行了优化。

该体系解决的核心问题是：谁拥有游戏规则的权威性？答案是服务器端的 `AGameModeBase`——它仅存在于服务器，客户端无法直接访问，从而保证规则不被篡改。与之对应，`AGameStateBase` 负责将服务器的权威信息同步到所有客户端，形成服务器写、所有人读的信息广播通道。

理解 GameFramework 对 UE5 开发者的意义在于：几乎所有多人游戏的得分系统、回合管理、玩家生成（Spawn）逻辑都必须经过这套体系。错误地在 `PlayerController` 里写游戏规则，或在 `GameMode` 里存储需要客户端读取的数据，是初学者最常见的架构错误，会直接导致联机功能失效。

---

## 核心原理

### GameMode：规则的唯一权威

`AGameModeBase` 只在服务器（或单机模式的本地）实例化，客户端调用 `GetWorld()->GetAuthGameMode()` 在非服务器环境会返回 `nullptr`。它负责三件事：

1. **玩家登录**：`Login()` 函数在玩家连接时被调用，返回一个 `APlayerController` 实例。
2. **Pawn 生成**：`RestartPlayer(AController* NewPlayer)` 找到 PlayerStart 并调用 `SpawnDefaultPawnAtTransform()`，将 Pawn 与 Controller 绑定（`Possess`）。
3. **比赛流程**（仅 `AGameMode`）：内置状态机包含 `WaitingToStart → InProgress → WaitingPostMatch → LeavingMap` 四个阶段，通过 `SetMatchState(FName NewState)` 切换。

`AGameModeBase` 有一个重要属性 `DefaultPawnClass`，默认指向 `ADefaultPawn`，开发者通常在蓝图子类中将其修改为项目自定义的角色类。

### GameState：状态的广播频道

`AGameStateBase` 在服务器和所有客户端都存在，其属性通过 UE5 的属性复制（Replication）机制自动同步。存储在此处的数据应当是"所有玩家都需要知道的全局状态"，例如：当前比赛剩余时间 `float RemainingTime`、当前连接的 `PlayerArray`（`TArray<APlayerState*>` 类型，自动维护）。

访问 GameState 的正确方式是 `GetWorld()->GetGameState<AMyGameState>()`，这在客户端也可以正常返回有效指针，这正是它与 GameMode 的根本区别。

### PlayerController 与 PlayerState 的分工

`APlayerController` 代表"一个人类玩家的意志"——它处理输入（通过 `EnhancedInput` 系统绑定到 `UInputAction`）、控制摄像机、以及向服务器发送 RPC 调用。每个本地客户端只拥有自己的 `PlayerController`，其他玩家的 Controller 在本地不存在。

`APlayerState` 则存储需要跨 Pawn 生命周期持久化的玩家数据，例如玩家名称（`GetPlayerName()`）和得分（`SetScore(float S)`）。当玩家的 Pawn 死亡并重生时，PlayerController 和 PlayerState 不会销毁，而 Pawn 会被替换，这是两者的核心设计意图。`PlayerState` 同样在服务器和客户端都存在并自动复制。

### Pawn 与 Character 的继承关系

`APawn` 是可被 Controller "附身"（Possess）的基础可操控实体，`ACharacter` 是 `APawn` 的子类，额外包含 `UCharacterMovementComponent`，提供行走、跳跃、游泳等内置物理移动逻辑。UE5 的 `UCharacterMovementComponent` 支持网络预测（Network Prediction），在高延迟环境下仍能保持流畅的移动手感，这是直接使用 `APawn` 所不具备的能力。

---

## 实际应用

**单机 RPG 场景**：在 `AMyGameMode` 中重写 `HandleMatchHasStarted()`，在游戏开始时从存档读取数据并初始化世界。玩家角色继承 `ACharacter`，移动组件直接使用默认的 `UCharacterMovementComponent`，无需编写任何物理代码。

**多人射击游戏场景**：得分逻辑写在服务器端 `AMyGameMode::PlayerEliminated(AMyCharacter* Victim, AMyPlayerController* Killer)` 中，调用 `Killer->GetPlayerState()->SetScore()` 更新分数。`AMyGameState` 中存储 `TopScoringPlayers` 数组并标记为 `Replicated`，所有客户端的 HUD 通过读取 GameState 自动更新排行榜，而无需任何额外的网络调用。

**关卡切换**：服务器调用 `GetWorld()->ServerTravel(TEXT("/Game/Maps/Level2?listen"))` 触发关卡迁移，GameFramework 的生命周期管理确保 PlayerController 和 PlayerState 在迁移过程中被正确保留或重建，`AGameMode::GetSeamlessTravelActorList()` 可指定哪些 Actor 跨关卡持久存在。

---

## 常见误区

**误区一：在 PlayerController 里写游戏规则**
许多初学者将"玩家死亡后扣血"逻辑写在 `APlayerController` 中，并用 `ServerRPC` 调用。这虽然技术上可行，但违反了 GameFramework 的设计哲学：游戏规则的权威应集中在 `GameMode`，分散在 Controller 中的规则难以维护，且在 Controller 被销毁（如玩家断线重连）时逻辑会中断。

**误区二：混淆 GameMode 与 GameState 的用途**
将本应放在 `GameState` 的数据（如比赛剩余时间）直接存在 `GameMode` 中，然后试图在客户端 HUD 里读取，会发现永远拿不到数据。`GameMode` 客户端不可见是架构设计，不是 Bug。规则数据归 GameMode，展示数据归 GameState，这条边界必须清晰。

**误区三：混淆 AGameMode 与 AGameModeBase 的适用场景**
`AGameModeBase` 足够用于大多数单机游戏和自定义流程的多人游戏。`AGameMode` 额外提供的比赛状态机（MatchState）适合标准对战类游戏，但其内置的 `ReadyToStartMatch()` 等钩子函数如果不了解就贸然继承，会导致比赛永远无法开始（例如默认实现要求至少有一名玩家才进入 `InProgress`，单机测试时若忘记设置会卡在 `WaitingToStart`）。

---

## 知识关联

**前置概念**：了解游戏引擎中 Actor 的生命周期（`BeginPlay`、`Tick`、`EndPlay`）是使用 GameFramework 的基础，因为 GameMode、GameState 等类都继承自 `AActor`，其初始化顺序直接影响数据访问时序——`GameMode` 的 `InitGame()` 早于任何 Actor 的 `BeginPlay()`，这在多人游戏初始化中尤为关键。

**后续概念**：UE5 网络架构会在 GameFramework 的基础上深入讲解属性复制（`UPROPERTY(Replicated)`）、RPC 分类（`Server`/`Client`/`NetMulticast`）以及 `GameState` 中数据同步的底层机制——理解了 GameMode 只在服务器、GameState 在所有端这一设计后，网络复制的"为什么"就有了清晰的落脚点。UE5 引入的 `UReplicationGraph` 插件也是在 GameFramework 的 Actor 所有权模型之上构建的优化方案。