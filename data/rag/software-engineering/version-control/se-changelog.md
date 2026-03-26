---
id: "se-changelog"
concept: "变更日志管理"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 2
is_milestone: false
tags: ["文档"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.517
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 变更日志管理

## 概述

变更日志（Changelog）是软件项目中记录每个版本新增功能、问题修复和破坏性变更的结构化文档，通常以 `CHANGELOG.md` 文件的形式存储在项目根目录。它的直接受众是使用该软件的开发者和用户，帮助他们快速判断是否需要升级，以及升级后需要修改哪些代码。

变更日志的规范化写法有一个广泛采用的标准：**Keep a Changelog**（keepachangelog.com），由 Olivier Lacan 于 2014 年发起。该规范规定每个版本条目应包含 `Added`、`Changed`、`Deprecated`、`Removed`、`Fixed`、`Security` 六个分类，并要求按语义化版本号（SemVer）倒序排列，最新版本始终在文件顶部。

变更日志与 Git 提交历史的核心区别在于受众不同。`git log` 是写给开发者追踪内部变化的，而 `CHANGELOG.md` 是写给依赖该库的下游用户的。一份设计良好的变更日志可以将用户升级时的排查时间从数小时压缩到几分钟。

---

## 核心原理

### Keep a Changelog 文件结构

一个符合规范的 `CHANGELOG.md` 文件具有固定的 Markdown 结构。文件头部是项目名称和简短说明，随后每个版本占一个二级标题，格式为 `## [1.2.0] - 2024-03-15`，其中版本号用方括号括起，日期采用 ISO 8601 格式（`YYYY-MM-DD`）。版本号下方按六个分类用三级标题分组，未出现的分类可以省略。文件末尾通常附上版本号与 Git tag 对应的比较链接，例如：

```
[1.2.0]: https://github.com/owner/repo/compare/v1.1.0...v1.2.0
[Unreleased]: https://github.com/owner/repo/compare/v1.2.0...HEAD
```

`[Unreleased]` 条目是一个特殊占位符，开发过程中持续向其追加变更，正式发布时将其重命名为具体版本号。

### 语义化版本与分类的对应关系

变更日志的六个分类与语义化版本号的三段（MAJOR.MINOR.PATCH）直接对应：`Removed` 和 `Changed`（破坏性变更）触发 MAJOR 版本递增；`Added`（向后兼容的新功能）触发 MINOR 递增；`Fixed`（向后兼容的缺陷修复）和 `Security` 触发 PATCH 递增。正确地分类变更条目，意味着阅读 `CHANGELOG.md` 的用户可以直接从版本号推断升级风险等级。

### 自动化生成：Conventional Commits 与工具链

手动维护变更日志容易在发布压力下被遗漏，因此业界发展出基于 **Conventional Commits** 规范的自动化方案。该规范要求每条 Git 提交消息符合 `<type>(<scope>): <description>` 格式，其中 `type` 取值包括 `feat`（对应 Added）、`fix`（对应 Fixed）、`docs`、`chore` 等。含有 `BREAKING CHANGE:` 页脚的提交会被工具识别为破坏性变更。

主流工具 **standard-version**（已归档）和其继任者 **release-it** 或 **changesets** 会读取两个 Git tag 之间的所有符合规范的提交，按类型分组后自动追加到 `CHANGELOG.md`，同时自动递增 `package.json` 中的版本号并创建新 tag。例如，运行 `npx release-it` 后，工具会输出预览、确认后提交并推送，整个发布流程可在 2 分钟内完成。

---

## 实际应用

**npm 生态中的典型工作流**：在 `package.json` 的 `scripts` 中配置 `"release": "standard-version"`，每次需要发布时执行 `npm run release`。该命令会扫描上次 tag 以来的所有 `feat:` 和 `fix:` 类型提交，生成如下格式的 `CHANGELOG.md` 条目：

```markdown
## [2.1.0] - 2024-11-20

### Added
- 支持批量导出为 CSV 格式 ([#142](https://github.com/...))

### Fixed
- 修复在 Safari 16 下日期选择器无法弹出的问题 ([#138](https://github.com/...))
```

**monorepo 场景**：当一个仓库包含多个独立包时，工具 **changesets**（由 Atlassian 开源）采用"变更集文件"方式：每次 PR 合并时在 `.changeset/` 目录写入一个描述文件，记录受影响的包名和变更类型；发布时 `changeset publish` 汇总所有变更集，为每个包单独生成 `CHANGELOG.md` 并发布到 npm。

**GitHub Actions 集成**：在 CI 流水线中，可配置在推送 tag（如 `v*`）时自动运行 `gh release create`，并将 `CHANGELOG.md` 中当前版本的内容提取为 GitHub Release 的说明正文，实现一次推送、自动生成可视化的发布页面。

---

## 常见误区

**误区一：将提交日志直接粘贴为变更日志**。提交消息如 `fix typo`、`wip`、`merge branch 'feature/xxx'` 对终端用户毫无意义。变更日志条目应以用户视角描述影响，例如"修复了当输入包含特殊字符时搜索功能返回空结果的问题"，而不是"fix regex bug in search.js line 42"。自动化工具依赖 Conventional Commits 规范过滤掉 `chore`、`refactor` 等不面向用户的提交类型，正是为了解决这个问题。

**误区二：`CHANGELOG.md` 只需要在正式发布时更新**。Keep a Changelog 规范明确推荐维护一个持续更新的 `[Unreleased]` 区块。如果等到发布前才集中补写，极易遗漏两周前的某次关键 `Fixed` 条目，或者把对用户影响巨大的 `Removed` 变更写成无关紧要的措辞。

**误区三：破坏性变更可以放在 `Changed` 分类下不额外标注**。许多项目在做出破坏性变更时仅用 `Changed` 条目一笔带过，没有在条目前加 `**BREAKING CHANGE:**` 前缀或单独设立 `Removed` 分类。这会导致依赖自动化工具的用户升级后程序崩溃，而升级前扫描 `CHANGELOG.md` 时完全没有收到视觉警示。

---

## 知识关联

变更日志管理建立在**语义化版本控制（SemVer）**的三段式版本号规则之上：不理解 MAJOR/MINOR/PATCH 的含义，就无法正确地将变更条目与版本号升级幅度对应起来。理解 SemVer 规范（semver.org）是规范填写变更日志的前提。

在工具链层面，**Conventional Commits 提交规范**是实现自动化变更日志的直接依赖——只有当团队的 Git 提交历史符合该格式，`standard-version`、`release-it`、`changesets` 等工具才能从中提取有意义的条目。可以将 `commitlint` 配置到 Git `commit-msg` hook 中，在提交时自动验证消息格式，从源头保证自动化生成的变更日志质量。

对于发布了公共 npm 包或开源库的项目，`CHANGELOG.md` 的内容会直接同步到 npm 注册表的版本页面和 GitHub Releases，成为用户在 `npm info <package>` 或项目主页看到的第一手升级参考信息。