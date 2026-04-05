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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

Mock与Stub是自动化测试中用于**隔离被测对象与外部依赖**的两种模拟技术。Stub（桩）提供预设的固定返回值，让被测代码在没有真实依赖的情况下正常执行；Mock（模仿对象）则更进一步，不仅能返回预设值，还会**记录交互行为**并允许测试结束后验证这些交互是否符合预期。两者的核心区别在于：Stub关注"状态验证"，Mock关注"行为验证"。

这两个概念由Gerard Meszaros在2007年出版的《xUnit Test Patterns》一书中正式定义并系统化区分。在此之前，业界常将所有模拟对象统称为"Mock"，导致概念混淆。Meszaros将测试替身（Test Double）划分为五类：Dummy、Fake、Stub、Spy、Mock，其中Stub和Mock是游戏测试中最常用的两类。

在游戏QA自动化中，网络服务器、数据库、物理引擎、随机数生成器等组件往往难以在单元测试中直接调用——服务器可能未启动，物理模拟耗时过长，随机数导致结果不可复现。Mock与Stub技术让测试代码能够**绕过这些依赖**，以毫秒级速度稳定运行，是构建可靠自动化测试套件的基础手段。

---

## 核心原理

### Stub：固定返回值的状态替代

Stub的工作原理是为被测代码提供一个"假的"依赖实现，该实现对所有调用返回预先硬编码的值。例如，游戏中的角色伤害计算模块依赖`IDiceRoller`接口（骰子投掷），正常运行时会生成1~20的随机整数。为了测试"暴击伤害应为普通伤害的2倍"这一逻辑，可以创建一个Stub，让`Roll()`方法始终返回`20`（最大值），从而**固定测试条件**，使断言结果完全可预测。

```python
class StubDiceRoller:
    def roll(self, sides: int) -> int:
        return 20  # 始终返回最大值，验证暴击逻辑

damage = calculate_damage(attacker, defender, StubDiceRoller())
assert damage == base_damage * 2  # 状态验证
```

### Mock：记录交互的行为验证

Mock对象在返回预设值的同时，会**记录自身被调用的次数、参数和顺序**。测试结束后，可以对这些交互记录进行断言。以游戏成就系统为例：当玩家击杀100名敌人时，应触发一次且仅一次`AchievementService.unlock("SLAYER")`调用。使用Stub无法验证这一点，但Mock可以精确断言：

```python
mock_achievement = Mock()
player.kill_enemy(enemy_count=100, achievement_service=mock_achievement)
mock_achievement.unlock.assert_called_once_with("SLAYER")  # 行为验证
```

Python的`unittest.mock`库中`Mock`类默认记录所有调用，`assert_called_once_with`会在调用次数不等于1或参数不匹配时抛出`AssertionError`。

### 测试替身的选择原则

**选Stub的场景**：只关心被测函数的输出结果，不关心它如何调用依赖。例如测试地图寻路算法返回的路径长度是否最短，网络延迟查询用Stub固定为`50ms`即可，无需验证查询被调用几次。

**选Mock的场景**：被测逻辑的正确性体现在对外部服务的调用方式上。例如游戏内购系统在支付失败时必须**精确调用一次**`LogService.record_failure()`而非零次或多次——过多调用会产生重复计费警告，过少则漏掉故障记录。

**Python中`MagicMock`与`Mock`的区别**：`MagicMock`额外支持魔术方法（如`__len__`、`__iter__`），适用于需要模拟列表或上下文管理器的游戏对象。

---

## 实际应用

### 模拟游戏服务器响应

多人游戏的匹配逻辑单元测试中，真实服务器不可用。使用`pytest-mock`库中的`mocker.patch`可将`MatchmakingServer.find_match()`替换为返回预设队伍数据的Stub，测试匹配算法逻辑而不依赖网络连接：

```python
def test_balanced_team_matching(mocker):
    mocker.patch(
        'matchmaking.MatchmakingServer.find_match',
        return_value=[{"id": 1, "rank": 1500}, {"id": 2, "rank": 1480}]
    )
    result = matchmaker.form_team(required_players=2)
    assert abs(result[0]["rank"] - result[1]["rank"]) <= 50  # 天梯分差≤50
```

### 验证存档系统的写入行为

RPG游戏的自动存档功能要求在角色死亡时调用`SaveManager.save(slot=0)`且不得调用`save(slot=1)`（槽位1为手动存档）。此场景必须用Mock而非Stub，因为需要验证具体的调用参数：

```python
mock_save = Mock()
character.die(save_manager=mock_save)
mock_save.save.assert_called_with(slot=0)
calls_to_slot1 = [c for c in mock_save.save.call_args_list if c[1].get("slot") == 1]
assert len(calls_to_slot1) == 0
```

---

## 常见误区

**误区一：将所有测试替身都叫做"Mock"**
这是最普遍的错误。当你只需要固定返回值（如让随机数生成器返回固定种子结果）时，使用的是Stub，而非Mock。错误地使用Mock会引入不必要的行为断言，导致测试在实现细节改变时频繁失败，即使功能本身依然正确。区分标准很简单：测试代码末尾有没有对模拟对象的`assert_called`类语句——有则为Mock验证，无则为Stub使用。

**误区二：Mock的验证越详细越好**
过度Mock（Over-mocking）是游戏测试自动化中常见的反模式。若某个测试断言`EventBus.publish`被调用了3次、每次参数完全匹配，则重构内部实现（如将3次独立发布合并为1次批量发布）会导致测试失败，即使游戏行为完全正确。Mock应只验证**对外部协作者有业务意义的关键交互**，而非内部实现的每一步。

**误区三：Stub和Mock可以替代集成测试**
Mock与Stub隔离了外部依赖，因此它们无法发现真实的服务器协议变更、数据库字段重命名等集成问题。游戏QA中若100%使用Mock替代真实后端，玩家排行榜接口的字段名从`score`改为`total_score`后，所有单元测试仍会通过，但线上功能已经崩溃。Mock与Stub负责单元层面的逻辑验证，与集成测试层互补，不可相互替代。

---

## 知识关联

**前置概念——测试报告**：测试报告中出现的`PASSED`/`FAILED`统计数据，其中相当一部分来自使用了Mock与Stub的单元测试。理解Mock验证失败（如`AssertionError: Expected call not found`）在报告中的含义，需要知道它反映的是**调用行为不符合预期**，而非功能输出错误，这与Stub相关测试的失败原因（断言返回值错误）性质不同。

**后续概念——TDD/BDD实践**：测试驱动开发（TDD）要求在编写实现代码前先写测试，此时被依赖的模块尚未实现，必须用Stub先行替代。BDD场景中描述"当服务返回错误时，游戏应显示重试提示"——"服务返回错误"这一前提条件正是通过配置Stub的返回值来构造的。掌握Mock与Stub是进行TDD/BDD的前提，因为没有测试替身技术，测试就无法在依赖缺失时独立运行。