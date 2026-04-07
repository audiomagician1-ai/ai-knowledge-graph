---
id: "gp-as-definition-done"
concept: "Definition of Done"
domain: "game-production"
subdomain: "agile-scrum"
subdomain_name: "敏捷/Scrum"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 完成定义（Definition of Done）

## 概述

完成定义（Definition of Done，简称 DoD）是 Scrum 框架中一份明确的书面协议，列出了一个工作项、Sprint 或发布版本必须满足的所有标准，才能被团队正式宣告为"完成"。它不是主观判断，而是一份可逐条核查的清单。如果某个任务没有通过清单上的全部条目，它就不算完成，不能被纳入 Sprint Review 的演示范围，也不能计入速度（Velocity）。

DoD 的概念随着 Scrum 指南的迭代而逐步明晰。在 2017 年版 Scrum 指南中，DoD 被描述为对产品增量质量的"正式描述"；到 2020 年版，它被进一步强化为"组织标准"的一部分，要求组织层面存在统一的最低 DoD，各团队可以在此基础上叠加更严格的标准。这一演进说明 DoD 不是一次性文档，而是随项目成熟度动态调整的活文件。

在游戏开发中，DoD 解决了一个极其具体的痛点：美术资产"画完了但没有集成进引擎"、关卡"设计完成但未经帧率测试"、功能"代码合并但没有 QA 走查"——这些模糊的"完成"状态会在 Sprint 末期堆积成庞大的技术债。一份经过全团队签署的 DoD 将这种模糊消除于任务开始之前。

---

## 核心原理

### 三层 DoD 结构：任务、Sprint、发布

DoD 并非单一清单，而是按颗粒度分为至少三个层次，每层包含不同的验收标准。

**任务级 DoD（Task-level DoD）** 针对单个工作条目，例如一个角色动画任务的 DoD 可能包含：动画文件已导入引擎、已绑定到状态机、帧率在目标平台上不低于 30 FPS、命名遵循项目规范（如 `CH_PlayerRun_Loop`）。这一层强调的是可交付的最小单元是否自洽。

**Sprint 级 DoD（Sprint-level DoD）** 描述一个 Sprint 结束时整个增量必须达到的状态，通常包含：所有功能已通过回归测试、构建无编译错误、游戏在 PC/主机/移动端目标平台上均可运行至少 15 分钟不崩溃、Sprint Backlog 中所有故事点已关闭或已显式移回 Product Backlog。

**发布级 DoD（Release-level DoD）** 是最严格的层次，典型条目包括：本地化字符串覆盖率达到 100%、首日补丁包大小不超过平台要求（如 Nintendo Switch 要求补丁不超过 32 GB）、通过平台认证清单（Lotcheck / TCR / TRC）、用户数据隐私声明已更新。

### DoD 的书写原则：可验证性

每一条 DoD 条目必须能被第三方在 5 分钟内以客观标准验证，不能依赖作者的自我陈述。例如，"代码质量良好"是不合格的条目，因为无法客观核查；"代码已通过 SonarQube 静态分析且零 Critical 级别问题"则是合格条目。在游戏项目中，常见的可验证条目包括：构建在 CI/CD 系统中通过自动化测试（通过率须达到 100%）、内存占用在 PS5 上低于 1 GB 等具体数值。

### DoD 与验收标准（Acceptance Criteria）的分工

DoD 是适用于所有条目的通用门槛，而验收标准是针对单个 User Story 的特定要求。例如，"保存游戏功能"这个故事的验收标准是"玩家退出并重新进入后，进度从上次存档点恢复"，而 DoD 要求这个功能还必须通过 3 个以上测试案例的自动化回归测试——后者无论哪个故事都需满足。两者缺一不可，但不可互相替代。

---

## 实际应用

**案例一：独立游戏团队的渐进式 DoD**
一个 8 人独立游戏团队在项目初期将 Sprint 级 DoD 定为 4 条：构建可运行、新功能有对应测试场景、无 P1 级 Bug、设计文档已同步更新。第 6 个 Sprint 后，团队发现帧率问题频繁在发布前暴露，于是修订 DoD，新增第 5 条："所有新关卡在 GTX 1060 上以 1080p 分辨率测得帧率不低于 60 FPS"。这一修订直接使发布前的帧率修复工作量下降了约 40%。

**案例二：主机游戏的发布级 DoD 与平台认证对接**
某 AA 工作室在 PS5 版本开发中，将 Sony 的 TRC（Technical Requirements Checklist）直接映射为发布级 DoD 的子集，共 23 条强制项。每条 TRC 要求对应一个可自动检测的 CI 任务或一个 QA 手动测试用例编号。结果是在送审阶段首次通过率从上一款产品的 61% 提升至 89%，节省了约 3 周的返修周期。

---

## 常见误区

**误区一：DoD 由 Scrum Master 或 PO 单独制定**
DoD 必须由整个 Scrum 团队（开发者、PO、Scrum Master）共同制定，并经全员签署认可。如果开发者没有参与制定，他们在执行时会缺乏认同感，DoD 会沦为形式文件。Scrum 指南 2020 版明确指出"Developers are committed to the Definition of Done"，主体是开发者，而非管理层。

**误区二：DoD 设定后不应修改**
恰恰相反，DoD 是 Sprint Retrospective 的合法议题之一。当团队发现某类缺陷反复逃逸、或者技术栈更新带来新的质量标准时，应立即在 Retrospective 中提出修订。一份永远不变的 DoD 通常意味着团队的质量标准没有随项目成熟度提升，这在游戏开发的后期冲刺阶段会带来严重的技术债堆积。

**误区三：满足 DoD 等于达到发布质量**
任务级或 Sprint 级 DoD 的满足，并不代表该增量已可对外发布。Sprint 级 DoD 保证的是"潜在可交付"（potentially shippable），而发布级 DoD 还需满足平台认证、本地化、性能基准等额外条目。混淆两个层次会导致团队误以为"Sprint 通过了就可以上线"，从而跳过必要的发布前检验步骤。

---

## 知识关联

DoD 的有效运行依赖于**游戏敏捷适配**阶段建立的基础共识——团队需要在适配期已经明确了"Sprint"在游戏开发中的含义边界，例如一个 Sprint 是否包含 QA 环节，是否覆盖垂直切片（Vertical Slice）验证，这些决定直接影响 Sprint 级 DoD 的内容。没有这层适配，DoD 中的"完成"标准与实际开发节奏会产生错位。

向前延伸，DoD 是**规模化敏捷**（如 SAFe 或 LeSS）中"Program Increment（PI）Definition of Done"的前置基础。当多个 Scrum 团队协同开发同一款游戏时，各团队的 DoD 必须存在共同的最低集合，才能保证集成点（System Demo）的产出物能够无缝合并。如果两个团队对"代码审查完成"的定义不一致，集成阶段就会产生大量协调成本。规模化敏捷要求在团队级 DoD 之上额外定义 Program 级 DoD，而这一机制正是从单团队 DoD 的三层结构自然扩展而来的。