---
id: "se-cr-tooling"
concept: "审查工具"
domain: "software-engineering"
subdomain: "code-review"
subdomain_name: "代码审查"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 审查工具

## 概述

代码审查工具是专门用于辅助开发团队进行代码审阅、批注和合并决策的软件平台。与早期通过邮件互传 diff 文件的方式相比，现代审查工具提供了内联评论（inline comment）、自动化检查触发、审批状态跟踪等功能，使审查过程可追溯、可量化。根据 SmartBear 于 2022 年发布的《State of Code Review》报告，在受访的 1000 余名开发者中，62% 的团队将 GitHub PR Review 作为主要审查工具，17% 使用 Gerrit，而 Crucible 的使用率已下降至 3% 以下（SmartBear, 2022）。

当前主流的三类工具分别是：集成在 Git 托管平台上的 **GitHub Pull Request Review**、谷歌开源的 **Gerrit**，以及 Atlassian 旗下已停止更新的 **Crucible**。这三种工具的诞生背景各不相同：GitHub PR Review 随 GitHub 平台于 2008 年上线，以社交化协作为设计理念；Gerrit 由谷歌内部工具 Mondrian 演化而来，2008 年由 Shawn Pearce 开源，专为 Android 开源项目的大规模多团队协作设计；Crucible 则是 Atlassian 在 2007 年推出的商业产品，与 Jira 和 Confluence 深度整合，但自 2020 年起 Atlassian 已宣布该产品进入维护模式，不再新增功能。工具选型直接影响团队的分支策略、CI/CD 集成方式和权限管控粒度。

---

## 核心原理

### GitHub Pull Request Review 的工作机制

GitHub PR Review 基于**分支合并请求**模型。开发者从主干创建特性分支，完成开发后发起 Pull Request，整个 diff 在浏览器中可视化呈现为 `Files Changed` 视图（支持 `Unified` 和 `Split` 两种 diff 模式）。审查者可在具体代码行添加 `line comment`，也可发起正式 `Review` 并选择以下三种状态之一：

- **Comment**：仅留下评论，不影响合并状态；
- **Approve**：批准该 PR，贡献一票有效赞成；
- **Request changes**：要求修改，该 PR 被标记为阻塞状态，在提交者回应并重新请求 Review 之前无法合并。

GitHub 的 **Branch Protection Rules** 可配置"至少需要 N 名审查者批准"（N 可在仓库设置中设为 1 至 6），以及"代码所有者（CODEOWNERS 文件中指定的人员）必须审查"等强制策略。`CODEOWNERS` 文件的语法类似 `.gitignore`，例如：

```
# 所有 Python 文件必须由 @backend-team 审查
*.py @backend-team

# docs 目录必须由 @tech-writer 审查
/docs/ @tech-writer
```

整个审查历史以 conversation thread 形式保留在 PR 页面，每个 thread 可被单独标记为 `Resolved`，方便追踪修改落实情况。GitHub 还在 2023 年引入了 **PR Summary（由 Copilot 生成的 AI 摘要）**功能，可自动归纳变更意图，减少审查者阅读上下文的时间成本。

### Gerrit 的变更集审查模型

Gerrit 采用完全不同的**变更集（Change）**模型，而非分支模型。开发者通过特殊命令将提交推送到 Gerrit 服务器：

```bash
# 推送到 main 分支的审查队列
git push origin HEAD:refs/for/main

# 推送时附加审查者和话题标签
git push origin HEAD:refs/for/main%r=alice@example.com,topic=feature-login
```

每个提交形成一个独立的 Change，拥有唯一的 Change-Id（写入 commit message 的形如 `I3b3a5e6d...` 的 41 位十六进制哈希串）。若需修改已提交的 Change，开发者必须保留原 Change-Id 并执行 `git commit --amend`，再次推送后 Gerrit 会自动将其归入同一 Change 的新 Patchset（如 Patchset 2、Patchset 3），历史 Patchset 完整保留可供对比。

Gerrit 的评分系统是其最显著特征：每个 Change 需要在两个维度上同时满足阈值才能合并：

$$\text{可合并条件} = \left( \max(\text{Code-Review}_i) \geq +2 \right) \land \left( \min(\text{Code-Review}_i) > -2 \right) \land \left( \max(\text{Verified}_i) \geq +1 \right)$$

其中 `Code-Review` 维度评分范围为 **−2 到 +2**，`Verified` 维度评分范围为 **−1 到 +1**。任何单个 **−2** 评分均构成一票否决（veto），即使其余所有审查者均打出 +2 也无法合并——此设计来源于谷歌的工程文化，强调资深工程师（通常具备 `Owner` 权限）可独立阻止不符合架构规范的代码合入主干。`Verified` 维度通常由 Jenkins 或 Zuul 等 CI 系统自动写入，代表构建和测试通过。

Gerrit 还原生支持**主题（Topic）**功能，允许将跨仓库的多个相关 Change 分组联动，在合并时要求所有关联 Change 同时处于可合并状态，这对于需要同步修改多个微服务仓库的场景（例如同时变更 API 接口定义仓库和客户端仓库）非常实用。

### Crucible 的审查会话模型

Crucible 将代码审查组织为**审查会话（Review Session）**，其核心区别在于：它不仅支持 Git，还能直接对接 SVN、Mercurial 和 Perforce 等多种版本控制系统，甚至支持对任意文件片段（无需关联某次提交）发起审查。每个 Review Session 有明确的生命周期状态机：`Draft → Review → Summarize → Closed`，审查负责人（Moderator）可在任意阶段手动推进或回退状态。

Crucible 的**度量统计模块**内置了审查效率指标，例如：审查缺陷密度（每千行代码发现的缺陷数）、平均审查时长、各成员的评论数分布等，这些数据直接输出到与之配套的 Bamboo CI 面板中。然而由于 Atlassian 在 2020 年停止新功能开发，Crucible 已不支持 GitHub Actions 等现代 CI 框架的集成，这是其市场份额持续萎缩的直接原因。

---

## 关键对比维度与选型公式

在实际选型时，可以从五个维度量化评估三种工具的适用性：

| 维度 | GitHub PR Review | Gerrit | Crucible |
|---|---|---|---|
| 分支模型 | 特性分支 + PR | 单提交 Change | 会话绑定任意文件 |
| 否决机制 | 无一票否决 | −2 即否决 | Moderator 手动关闭 |
| 跨仓库联动 | 无原生支持 | Topic 分组 | 无 |
| CI 集成 | GitHub Actions 原生 | Zuul/Jenkins 脚本 | Bamboo（已停更） |
| 权限粒度 | 仓库级 + CODEOWNERS | 项目/分支/标签三级 | 会话级 |
| 适用团队规模 | 2～500 人 | 50～数千人 | 遗留项目维护 |

对于需要在 GitHub PR Review 和 Gerrit 之间做选择的团队，可以用以下经验判断式辅助决策：

$$\text{选择 Gerrit} \iff \left( |\text{贡献者数量}| > 50 \right) \lor \left( \text{存在跨仓库原子提交需求} = \text{true} \right) \lor \left( \text{需要一票否决机制} = \text{true} \right)$$

---

## 实际应用案例

**案例一：Android 开源项目（AOSP）使用 Gerrit**

AOSP 拥有超过 900 个 Git 仓库，每日处理来自全球数百家 OEM 厂商和谷歌内部工程师提交的变更。Gerrit 的 Topic 功能使得一次跨 `frameworks/base`、`hardware/interfaces` 和 `vendor/google` 三个仓库的 API 变更可以绑定为同一个 Topic，合并时由 `submit whole topic` 操作原子性地一次性合并，避免三个仓库分别合并时产生的短暂不一致状态。AOSP 的 Gerrit 实例地址为 `android-review.googlesource.com`，任何人均可访问，直观了解其评分流程。

**案例二：中小型 SaaS 团队使用 GitHub PR Review**

某 20 人规模的 SaaS 团队，后端采用 Python + FastAPI，将 CODEOWNERS 配置为：核心认证模块 `auth/` 必须由安全负责人 `@security-lead` 审查，数据库迁移脚本 `migrations/` 必须由 DBA `@dba-team` 审查。结合 Branch Protection Rules 要求至少 2 名 Approve，该团队在 6 个月内将线上事故率降低了 34%（内部数据，2023年）。

**案例三：Crucible 的遗留系统维护场景**

某金融机构的核心交易系统仍运行在 SVN 上，无法迁移至 Git。由于 Crucible 支持直接对 SVN revision 发起 Review Session，该团队保留 Crucible 用于合规审查留档，将每次 Review Session 的 `Closed` 状态截图作为监管要求的"四眼原则"（Four-Eyes Principle）证明材料归档至 Confluence。

---

## 常见误区

**误区 1：Gerrit 的 +2 可以由多个 +1 累加替代。**
错误。Gerrit 的 `Code-Review` 评分不做算术求和，+1 与 +1 之和并不等于 +2。+2 是一个独立的离散评分等级，必须由具有 +2 权限的账号（通常是项目 Owner 或 Maintainer）单独打出。这是 Gerrit 权限系统中最常见的理解偏差，曾导致多个开源项目的新贡献者等待合并却不知缺少何种审批。

**误区 2：GitHub PR 的 Request Changes 等同于一票否决。**
不准确。Branch Protection Rules 仅要求"满足最低 Approve 数量"，管理员账号默认具有 bypass 权限，可在 `Request Changes` 状态下强制合并（Force Merge）。真正实现强制阻止合并的方式是同时开启 `Require review from Code Owners` 且确保 CODEOWNERS 文件正确配置对应路径。

**误区 3：Crucible 停止更新意味着立即不可用。**
不准确。Atlassian 区分了"维护模式（Maintenance Mode）"与"停止支持（End of Support）"。Crucible 的官方支持终止日期为 2024 年 4 月 2 日，在此之前安全补丁仍会发布。但考虑到其不支持现代 CI 工具链集成，新项目不应再选用 Crucible；存量用户应制定向 GitHub 或 Gerrit 的迁移计划。

**误区 4：三种工具都只能审查新增代码。**
错误。GitHub PR Review 支持对 PR 内任意文件的任意行发表 `line comment`，包括未被本次提交修改的上下文代码行（需切换至 `Viewed` 模式）。Crucible 更支持对历史版本的任意快照发起审查。Gerrit 则允许对 Patchset 之间的 diff 进行逐行评论。

---

## 知识关联

本节所介绍的三种工具，与以下概念存在直接的上下游关系：

- **审查清单（Review Checklist）**：工具决定了清单条目能否被自动化验证。GitHub Actions 可在 PR 创建时自动运行 `flake8`、`eslint` 等静态分析工具，将结果以 Check 状态写回 PR，从而将清单中的格式类条目从人工审查中解放出来；Gerrit 则通过 `Verified` 维度的 CI 自动打分实现类似效果。

- **建设性反馈（Constructive Feedback）**：三种工具均提供 comment thread 功能，但 GitHub PR Review 在 2022 年新增了**建议变更（Suggested Changes）**功能：审查者可以在评论中直接嵌入修改后的代码片段，提交者一键即可将建议 commit 到 PR，极大降低