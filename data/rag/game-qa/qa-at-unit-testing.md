---
id: "qa-at-unit-testing"
concept: "单元测试"
domain: "game-qa"
subdomain: "automation-testing"
subdomain_name: "自动化测试"
difficulty: 2
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 单元测试

## 概述

单元测试（Unit Testing）是对程序中最小可测试单元——通常是单个函数、方法或类——进行独立验证的测试方式。在游戏开发中，"单元"可以是一个伤害计算函数、一条寻路算法逻辑、或一个角色属性的状态机转换。单元测试的核心特征是**隔离性**：每个测试用例只针对一段逻辑，不依赖数据库、网络连接、渲染管线或其他外部系统。

单元测试的概念由Kent Beck在1994年为Smalltalk语言开发SUnit框架时系统化，后来延伸为xUnit测试框架家族。在游戏领域，由于引擎的特殊性（如Unity的MonoBehaviour生命周期、Unreal的UObject系统），单元测试的落地比一般软件工程更有挑战性，但对于游戏逻辑层（战斗公式、经济系统、技能树计算）同样适用。

在测试金字塔模型中，单元测试位于底层，应当占总测试数量的约70%，执行时间通常要求在毫秒级别（单条测试 < 100ms）。单元测试能在代码提交阶段即时发现逻辑错误，大幅降低后期集成阶段的修复成本，这一成本比在系统测试阶段发现同样问题低10到100倍。

---

## 核心原理

### 1. AAA 模式：单元测试的标准结构

游戏单元测试应严格遵循 **Arrange-Act-Assert（准备-执行-断言）** 三段式结构：

- **Arrange（准备）**：创建测试所需的对象和输入数据，例如初始化一个角色的攻击力为100、防御穿透率为20%。
- **Act（执行）**：调用被测函数，例如执行 `CalculateDamage(attacker, defender)`。
- **Assert（断言）**：验证输出结果与预期是否一致，例如断言最终伤害值为80。

每个测试方法应只包含**一个Assert逻辑目标**（Single Assertion Principle），如果一个函数有多个分支逻辑，应拆分为多条独立测试用例。

### 2. 游戏常用测试框架选择

不同引擎生态对应不同的单元测试框架，选型直接影响编写效率：

| 引擎/语言 | 推荐框架 | 特点 |
|---|---|---|
| Unity (C#) | NUnit + Unity Test Runner | 内置于Package Manager，支持Play Mode与Edit Mode双模式 |
| Unreal (C++) | Automation Testing Framework | UE自带，通过`ADD_LATENT_AUTOMATION_COMMAND`支持异步 |
| 纯C++游戏逻辑 | Google Test (GTest) | 提供`EXPECT_EQ`、`ASSERT_NEAR`等丰富断言宏 |
| Python脚本逻辑 | pytest | 支持参数化测试，适合配置表数值验证 |

Unity中，Edit Mode测试不启动场景，执行速度快，适合测试纯逻辑函数；Play Mode测试会运行完整引擎，适合含协程的逻辑但速度较慢，**优先使用Edit Mode**覆盖纯逻辑层。

### 3. 依赖隔离：Mock 与 Stub 的使用

游戏逻辑中常有对外部系统的依赖，例如伤害计算函数可能调用`BuffManager.GetBuffMultiplier()`，而`BuffManager`依赖游戏运行时状态。单元测试要求将这些依赖替换为**测试替身（Test Double）**：

- **Stub**：返回预设固定值，例如令`MockBuffManager.GetBuffMultiplier()`始终返回`1.5f`，不执行真实逻辑。
- **Mock**：不仅返回预设值，还能验证某方法是否被调用了指定次数，例如验证伤害计算后`EventBus.OnDamageDealt`被调用恰好1次。

在C#中可使用**Moq**库或NSubstitute实现Mock对象；在GTest中使用**Google Mock（GMock）**并通过`EXPECT_CALL`宏定义调用预期。依赖注入（Dependency Injection）是实现可Mock代码的前提——将`BuffManager`通过构造函数传入，而非在函数内部`GetInstance()`获取单例。

### 4. 游戏数值测试的精度控制

游戏中大量使用浮点数，断言时不能使用精确等值比较（`==`），而应使用**容差断言**：

- GTest：`EXPECT_NEAR(actual, expected, 1e-5f)`
- NUnit：`Assert.AreEqual(expected, actual, delta: 0.001f)`
- pytest：`assert actual == pytest.approx(expected, rel=1e-4)`

对于概率性逻辑（如暴击率30%），不应在单元测试中直接测试随机结果，而是注入一个**可控的随机数生成器Mock**，强制输入边界值0.0和1.0来分别测试暴击与未暴击两条分支。

---

## 实际应用

**案例：测试RPG战斗伤害公式**

假设伤害公式为：`伤害 = 攻击力 × (100 / (100 + 防御力))`，攻击力100、防御力50时，期望伤害为66.67。

```csharp
[Test]
public void CalculateDamage_WithAtkAndDef_ReturnsCorrectValue()
{
    // Arrange
    var attacker = new CharacterStats { Attack = 100 };
    var defender = new CharacterStats { Defense = 50 };
    var calculator = new DamageCalculator();

    // Act
    float result = calculator.Calculate(attacker, defender);

    // Assert
    Assert.AreEqual(66.67f, result, delta: 0.01f);
}
```

**案例：使用参数化测试覆盖配置表边界值**

游戏中技能配置表有数百条记录，pytest的`@pytest.mark.parametrize`可读取CSV配置表，自动生成数百条测试用例，验证所有技能冷却时间不为0、伤害系数不为负数，无需手动编写每条用例。

---

## 常见误区

**误区一：测试MonoBehaviour内的逻辑而不拆分**

很多开发者把伤害计算直接写在`PlayerController : MonoBehaviour`的`Update`方法里，导致单元测试必须启动完整场景。正确做法是将纯逻辑抽离到无引擎依赖的普通C#类（Plain Old C# Object，POCO），MonoBehaviour只做调用转发，这样Edit Mode测试即可覆盖全部逻辑。

**误区二：一个测试方法验证多个行为**

例如一个测试方法同时验证伤害值计算正确、触发事件被调用、以及角色HP扣减正确——这违反单一职责原则。当测试失败时，无法直接定位是哪一个行为出问题，应拆分为三条独立测试方法，分别命名为 `CalculateDamage_Returns66_WhenAtk100Def50`、`CalculateDamage_FiresEvent_Once` 和 `TakeDamage_ReducesHP_Correctly`。

**误区三：测试私有方法**

有开发者为了提高覆盖率，使用反射强行测试私有方法。单元测试应通过**公共接口**来验证行为，若私有逻辑需要被直接测试，说明该逻辑应被重构为独立的可测试类，而非通过反射绕过访问控制。

---

## 知识关联

**前置知识**：测试金字塔定义了单元测试在整体测试体系中的位置和数量占比（约70%），理解金字塔有助于判断哪些逻辑值得写单元测试、哪些应留给上层测试。

**后续概念——集成测试**：单元测试只验证隔离逻辑，当多个通过单元测试的模块组合在一起时，它们的交互正确性需要集成测试来保证。例如`DamageCalculator`与`BuffManager`协同工作的正确性，不在单元测试覆盖范围内。

**后续概念——自动化回归**：稳定的单元测试集合是自动化回归流水线的执行主体。在CI/CD流程（如Jenkins、GitHub Actions）中，每次代码提交触发单元测试全量执行，执行时间应控制在3分钟以内以确保快速反馈，这一时间目标的达成依赖于单元测试的高速度和低耦合特性。
