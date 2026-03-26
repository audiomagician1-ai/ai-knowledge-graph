---
id: "qa-at-mocking-stubbing"
concept: "Mock与Stub"
domain: "game-qa"
subdomain: "automation-testing"
subdomain_name: "自动化测试"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Mock与Stub

## 概述

Mock与Stub是自动化测试中用于替代真实外部依赖的两类模拟技术。在游戏测试场景下，"外部依赖"包括网络服务器、数据库、支付接口、第三方SDK（如广告SDK、语音SDK）等在单元测试中难以直接调用的组件。Stub提供预设的固定返回值，用于隔离被测代码的输入条件；Mock则在此基础上进一步验证被测代码是否以正确的方式调用了依赖项（例如调用次数、参数是否匹配）。

这两个概念最早在2000年由Tim Mackinnon、Steve Freeman和Philip Craig在论文《Endo-Testing: Unit Testing with Mock Objects》中系统化提出。进入游戏开发领域后，随着Unity Test Framework、Unreal的FAutomationTestBase等框架的普及，Mock与Stub成为游戏逻辑层单元测试的标配工具。

在游戏QA中使用这两项技术的核心价值在于：使测试可以脱离真实服务器环境独立运行，将网络延迟、服务器状态等不确定因素从测试结果中排除，从而让每次CI流水线上的自动化测试都能在毫秒级完成，且结果完全可重复。

## 核心原理

### Stub的工作方式

Stub本质上是一个"哑替身"：它实现了与真实依赖相同的接口，但对所有方法调用只返回预先写死的数据，不执行任何真实逻辑。以游戏中的登录系统为例，真实的`IAuthService.Login(username, password)`会发起HTTP请求到认证服务器。使用Stub时，可以创建一个`StubAuthService`，让它的`Login()`方法直接返回`AuthResult.Success("mock_token_123")`，无论传入什么参数。Stub的核心特征是：**它不关心自己被如何调用，只负责提供测试所需的输入数据**。

### Mock的工作方式与验证机制

Mock在Stub的基础上增加了"行为验证"能力。Mock对象会记录自己被调用的方式，测试结束后通过`Verify()`断言来确认预期的交互是否发生。以Moq（C#主流Mock库，版本4.x起广泛用于Unity项目）为例，典型代码结构如下：

```csharp
var mockLogger = new Mock<IGameLogger>();
// 执行被测逻辑
gameSystem.ProcessLevelUp(player);
// 验证：IGameLogger.Log()必须被调用恰好1次，且参数包含"LevelUp"
mockLogger.Verify(l => l.Log(It.Is<string>(s => s.Contains("LevelUp"))), Times.Once());
```

这里`Times.Once()`是Moq框架的调用次数约束，`It.Is<T>()`是参数匹配器。如果`ProcessLevelUp`内部没有调用日志记录，测试会立即失败，从而暴露缺失的日志埋点。

### Stub与Mock的本质区别

马丁·福勒（Martin Fowler）在其博客《Mocks Aren't Stubs》（2004年）中明确定义了两者区别：Stub用于**状态验证**（验证被测对象在操作后的状态是否正确），Mock用于**行为验证**（验证被测对象与依赖项之间的交互是否符合预期）。在游戏测试中，测试"玩家击败Boss后金币数量增加500"属于状态验证，使用Stub足够；而测试"玩家购买道具后系统必须调用支付日志记录接口"则属于行为验证，必须使用Mock。

## 实际应用

**场景一：隔离服务器匹配逻辑**
游戏大厅的匹配系统依赖`IMatchmakingServer`接口。在测试"匹配超时后客户端自动重试3次"这一规则时，使用Stub让`IMatchmakingServer.FindMatch()`始终返回`MatchResult.Timeout`，就可以在不启动任何服务器进程的情况下，快速验证重试计数器逻辑是否正确。整个测试执行时间可以从原本需要等待真实超时（通常30秒）缩短到不足10毫秒。

**场景二：验证成就系统的事件上报**
成就解锁后必须向数据分析平台上报事件。使用Mock替代`IAnalyticsService`，在玩家触发"首次击杀"成就后，验证`IAnalyticsService.TrackEvent("achievement_unlock", "first_kill")`被调用了恰好1次，确保上报代码不遗漏也不重复。

**场景三：模拟支付SDK的各类返回状态**
真实支付SDK（如Apple IAP、Google Play Billing）无法在自动化测试中触发真实交易。通过Stub预设`PaymentResult.Success`、`PaymentResult.UserCancelled`、`PaymentResult.NetworkError`三种返回值，可以完整覆盖支付流程的所有分支逻辑，而这些场景在手动测试中极难复现（如模拟网络断开时的支付中断）。

## 常见误区

**误区一：Mock与Stub可以随意互换使用**
许多初学者将所有模拟对象统称为"Mock"，但在游戏测试中混用会导致测试意图不清晰。如果只需要控制`IRandomService.NextInt()`的返回值来测试掉落率计算，使用Stub即可；若你同时用Mock对它进行调用次数验证，则测试会因为随机数被调用的次数与内部实现绑定而变得脆弱——一旦算法重构改变了调用次数，测试就会误报失败，这是过度Mock的典型问题。

**误区二：Stub的返回值越接近真实数据越好**
在游戏道具系统的单元测试中，有人会为Stub构建包含数百个字段的完整道具JSON，认为这样"更真实"。实际上Stub只需要返回当前被测逻辑所需的最少字段。返回冗余数据不仅增加维护成本，还会在数据结构变更时导致大量不相关的Stub需要同步更新。

**误区三：使用Mock后就不需要集成测试**
Mock与Stub只能验证代码在假设依赖行为正确的前提下是否正常工作，无法发现真实服务器接口协议变更导致的问题。例如，服务器将登录接口的返回字段从`token`改为`access_token`，所有使用Stub的单元测试仍会通过，问题只会在集成测试中暴露。单元测试层的Mock覆盖不能替代针对真实环境的集成测试。

## 知识关联

**与测试报告的关系**：测试报告中记录的每一条单元测试用例，如果其中涉及外部服务调用，几乎都依赖Mock或Stub来保证测试的独立性。阅读测试报告时看到某个用例名称包含"WithMockedServer"或"StubPayment"等字样，说明该用例已通过模拟技术与真实环境解耦，其失败原因应从被测逻辑本身而非外部服务中排查。

**通向TDD/BDD实践**：测试驱动开发（TDD）的红-绿-重构循环在游戏开发中几乎必须配合Mock使用——当被测模块的依赖尚未实现时，用Mock临时占位可以让开发者先写测试再写实现。BDD框架（如SpecFlow）中的场景步骤（Given/When/Then）同样依赖Stub来构造Given阶段的初始状态，例如`Given the server returns a full lobby`可以直接对应一个返回预设数据的Stub配置。