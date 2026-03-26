---
id: "qa-bl-lifecycle-states"
concept: "生命周期状态"
domain: "game-qa"
subdomain: "bug-lifecycle"
subdomain_name: "Bug生命周期"
difficulty: 1
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.8
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

# 生命周期状态

## 概述

Bug的生命周期状态（Lifecycle Status）是指一个Bug从被发现到最终关闭的过程中，所经历的一系列明确定义的阶段标记。每个状态代表Bug当前所处的处理阶段，并决定了下一步由哪个角色执行哪种操作。在游戏QA实践中，状态字段是缺陷追踪系统（如Jira、Bugzilla、Mantis）中最关键的单个字段，因为它直接控制Bug的流转走向。

这套状态体系的雏形最早在1970年代的软件工程文献中被提出，IBM内部使用的缺陷追踪流程是其重要来源之一。现代游戏开发团队普遍采用的标准流转路径为：**New → Open → Fixed → Verified → Closed**，同时存在一条回流路径 **Verified → Reopened → Open**，构成一个带有反馈环的有向图。

理解生命周期状态的重要性在于：状态管理直接影响游戏发布决策。当一款游戏进入金版（Gold Master）审核阶段时，项目经理会统计处于New、Open、Reopened状态的Bug数量，用于判断产品是否达到发布标准。若任何P0（崩溃级别）Bug不处于Closed状态，发布通常会被阻断。

---

## 核心原理

### 五大标准状态的定义与职责归属

**New（新建）**：测试人员发现并记录Bug后的初始状态。此时Bug信息已录入系统，但尚未被开发团队确认。处于New状态的Bug拥有者（Owner）默认为提交该Bug的测试员本人，或由缺陷追踪系统自动分配给QA Lead。New状态的核心任务是信息完整性——标题、重现步骤、预期行为、实际行为、截图/录像、优先级（Priority）和严重程度（Severity）必须填写完整。

**Open（已确认/处理中）**：开发人员或QA Lead审查Bug后，确认该问题确实存在且需要修复，将状态变更为Open，并将Bug分配给具体的责任开发人员。Bug所有权在此步骤发生第一次转移，从测试员转移至开发员。若开发认为该描述不构成Bug（如属于设计行为），可将其转为Invalid或Wontfix子状态，这两者通常被视为Closed的特殊变体。

**Fixed（已修复）**：开发人员完成代码修改并提交后，将状态改为Fixed，同时填写修复说明和相关的代码提交哈希（Commit Hash）或变更列表编号（Changelist Number）。此时Bug所有权再次转移，回到测试员一侧，等待验证。值得注意的是，Fixed状态本身不代表Bug消失，它仅意味着"开发认为已修复"。

**Verified（已验证）**：测试人员在固定版本（Build Number需与Fixed时记录的版本一致）中按照原始重现步骤执行验证，确认问题不再复现后，将状态改为Verified。版本号的一致性是验证有效性的前提——在错误的Build上验证是游戏QA中最常见的操作失误之一。

**Closed（已关闭）**：由QA Lead或项目经理确认Verified信息无误后，将Bug最终关闭。Closed是Bug生命周期的终点状态，在大多数缺陷追踪系统中，Closed状态下的Bug不可直接编辑，只能Reopen后再修改。

### 回流路径：Reopened状态的触发机制

当一个已处于Verified状态的Bug在后续测试版本中再次出现时，测试员将其状态改为**Reopened**。Reopened不是独立的并列状态，而是一个回流信号，表示"曾经修复的问题复发"。触发Reopened通常有三种原因：
1. 开发提交了新代码引入了回归（Regression），导致原有修复失效；
2. 测试员在Verified时使用了错误的Build，误判为已修复；
3. Bug的修复方案只覆盖了特定平台（如PC），而在另一平台（如PS5）上仍然存在。

Reopened状态的Bug优先级在项目管理上通常会自动提升，因为同一问题二次出现意味着修复质量或验证流程存在缺陷。

### 状态转换的合法路径矩阵

并非所有状态之间都可以互相跳转。合法的转换路径如下：

| 当前状态 | 可转换到 | 执行角色 |
|----------|----------|----------|
| New | Open / Invalid / Duplicate | 开发或QA Lead |
| Open | Fixed / Wontfix | 开发人员 |
| Fixed | Verified / Reopened | 测试人员 |
| Verified | Closed / Reopened | QA Lead |
| Reopened | Open | 开发人员 |
| Closed | （终止，不可直接跳转） | — |

从New直接跳转到Closed（绕过Fixed和Verified）是被明确禁止的操作，这样做会导致Bug在统计报告中被算作"已处理"，但实际上从未被修复和验证，是数据污染的重要来源。

---

## 实际应用

在一款RPG游戏的主线任务测试中，测试员发现"接取任务NPC对话触发后游戏崩溃"。具体的状态流转过程如下：

- 测试员记录Bug，状态设为**New**，附上崩溃日志和重现步骤（必须在第3章地图、玩家等级10以上触发）；
- QA Lead审核后确认可复现，将其设为**Open**，优先级定为P0，分配给引擎程序员A；
- 程序员A发现是对话脚本空指针问题，修复后提交Changelist #48291，状态改为**Fixed**；
- 测试员在Build 0.9.12（即包含#48291的版本）上重新执行相同步骤，崩溃不再出现，状态改为**Verified**；
- QA Lead核对Build号无误后，将其**Closed**；
- 两天后，新的Build 0.9.15中程序员B的对话系统重构意外覆盖了修复，测试员再次复现崩溃，将状态改为**Reopened**，并在备注中标明"回归于Build 0.9.15"。

---

## 常见误区

**误区一：Fixed即等于已解决，可以直接关闭**

许多初入游戏QA的测试员误认为，当开发将状态改为Fixed后，QA可以直接将其Close，跳过Verified步骤。这是错误的——Fixed仅代表开发主观认为问题已解决，验证工作必须由测试员在正确版本上独立完成。跳过Verified步骤相当于放弃了QA对修复质量的把关职能，在游戏测试规范（如ISTQB游戏测试扩展指南）中被列为流程违规。

**误区二：Reopened与New是等价的**

部分测试员在遇到回归Bug时，倾向于重新提交一个New状态的Bug，而不是将原Bug改为Reopened。这样做会导致同一问题在系统中存在两条记录，破坏历史追踪链。正确做法是在原Bug记录上执行Reopen操作，并在评论中注明首次出现版本和再次出现版本，保持修复历史的完整性。

**误区三：Invalid和Duplicate等同于Closed**

将Bug标记为Invalid（非Bug，属于设计行为）或Duplicate（与已存在Bug重复）时，这类状态在统计上属于关闭类别，但其含义与真正意义上的Closed完全不同。Closed意味着"已修复并验证"，而Invalid意味着"不需要修复"。混淆这两类状态会导致月度缺陷修复率（Fix Rate）数据失真，影响对团队开发质量的评估。

---

## 知识关联

生命周期状态建立在**Bug分类体系**的基础上：Bug的Priority和Severity分类决定了状态流转的紧急程度——P0 Bug在Open状态下通常需要在24小时内转入Fixed状态，而P3 Bug可以在当前迭代结束时统一处理。理解分类体系是正确执行状态流转的前提，因为不同优先级的Bug对应不同的状态变更SLA（服务级别协议）。

掌握生命周期状态后，下一个关键概念是**复现方法**。有效的复现步骤是驱动Bug从New顺利进入Open状态的核心条件——开发人员能否快速确认Bug存在，很大程度上取决于测试员提供的复现信息是否清晰、完整且在指定环境下可重复执行。无法复现的Bug往往会在New状态中长期停滞，甚至被直接标记为Invalid，导致真实问题被忽视。