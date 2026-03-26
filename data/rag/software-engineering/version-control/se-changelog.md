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

变更日志（Changelog）是一份按时间倒序记录软件版本变更历史的文档，通常以 `CHANGELOG.md` 文件存放于项目根目录。它的核心价值在于让用户和开发者快速了解每个版本新增了哪些功能、修复了哪些缺陷、以及是否存在破坏性变更（Breaking Changes），而无需逐条阅读 Git 提交记录。

变更日志的现代规范主要由 **Keep a Changelog**（keepachangelog.com）于2014年由 Olivier Lacan 提出，定义了一套标准化的分类体系，包括 `Added`、`Changed`、`Deprecated`、`Removed`、`Fixed`、`Security` 六个条目类别。与此同时，**语义化版本控制**（Semantic Versioning，简称 SemVer）的 `MAJOR.MINOR.PATCH` 格式为变更日志提供了版本号骨架，两者常配合使用。

在大型开源项目中，手动维护变更日志极易出现条目遗漏、格式不统一等问题。自动化工具通过解析 Git 提交信息生成 `CHANGELOG.md`，将发布流程从"开发者逐条回忆"变为"提交即记录"，显著降低发布前的整理成本。

---

## 核心原理

### 约定式提交（Conventional Commits）规范

自动化生成变更日志的基础是**约定式提交**（Conventional Commits）规范，版本 1.0.0 于2019年正式发布。该规范要求提交信息遵循以下格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

其中 `type` 字段决定了该提交会出现在变更日志的哪个分类下：
- `feat:` → 映射为 `Added` / 新功能，触发 MINOR 版本号递增
- `fix:` → 映射为 `Fixed` / 缺陷修复，触发 PATCH 版本号递增
- `feat!:` 或 footer 包含 `BREAKING CHANGE:` → 触发 MAJOR 版本号递增
- `chore:`、`docs:`、`test:` 等 → 默认不出现在用户可见的变更日志中

例如，一条提交 `feat(auth): add OAuth2 login support` 会自动归入下个版本的 `Added` 分类，描述文字为 "add OAuth2 login support"。

### 自动化工具链

目前主流的变更日志自动化工具有三类：

**1. standard-version / release-please**
`standard-version` 是 npm 生态中广泛使用的工具，运行 `npx standard-version` 后会自动：①根据提交历史计算新版本号；②更新 `package.json` 中的 version 字段；③生成或追加 `CHANGELOG.md` 条目；④创建 Git tag。`release-please` 是 Google 推出的替代品，通过 GitHub Actions 以 PR 形式管理发布流程。

**2. git-cliff**
用 Rust 编写的高性能工具，通过 `cliff.toml` 配置文件支持完全自定义的模板渲染（基于 Tera 模板引擎），适合需要非标准格式输出的项目。

**3. conventional-changelog-cli**
命令行工具，底层被 `standard-version` 所依赖，支持 angular、atom、codemeta 等多种预设风格。

### CHANGELOG.md 的文件结构

一份符合 Keep a Changelog 规范的 `CHANGELOG.md` 通常如下所示：

```markdown
# Changelog

## [1.2.0] - 2024-03-15
### Added
- 新增用户头像上传功能

### Fixed
- 修复在 Safari 16 下日期选择器崩溃的问题

## [1.1.0] - 2024-01-08
### Added
- 支持深色模式

[1.2.0]: https://github.com/org/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/org/repo/compare/v1.0.0...v1.1.0
```

文件末尾的链接区块将版本号与对应的 GitHub 比较视图关联，使读者可以点击直接查看两个版本之间的全部 diff。

---

## 实际应用

**GitHub Releases 自动发布**：在 GitHub Actions 流水线中，可将生成的 `CHANGELOG.md` 对应版本区块内容自动提取，作为 `gh release create` 命令的 release notes 正文，实现"提交代码→CI 触发→CHANGELOG 更新→GitHub Release 自动发布"的完整流程。

**monorepo 多包场景**：在使用 pnpm workspace 或 Lerna 管理的 monorepo 项目中，每个子包可维护独立的 `packages/my-pkg/CHANGELOG.md`。工具如 `changesets`（由 Atlassian 团队维护）专为此场景设计，开发者通过运行 `changeset add` 命令声明变更意图，在发布时统一合并为各包的变更日志。

**安全漏洞公告**：`Security` 分类条目在 `CHANGELOG.md` 中具有特殊意义。当某版本修复了 CVE 漏洞时，在该分类下注明 CVE 编号（如 `CVE-2023-45857`）可帮助使用者快速判断是否需要紧急升级，而不必另外查询安全公告页面。

---

## 常见误区

**误区1：把 CHANGELOG.md 当作 Git 提交历史的简单复制**
Git 提交历史面向开发者，记录的是实现细节（如 "refactor: extract auth middleware to separate file"）；而变更日志面向用户，应描述用户可感知的变化。一次用户可见的功能可能跨越十几条提交，变更日志只应呈现最终效果，而非每条中间提交。直接用 `git log --oneline` 的输出替代变更日志是最常见的错误。

**误区2：`[Unreleased]` 区块可以无限期留空**
Keep a Changelog 规范中的 `[Unreleased]` 区块用于实时记录尚未发布的变更，应在每次合并 PR 时即时更新。许多团队在发布前才集中填写，导致遗漏重要条目。正确做法是将 `CHANGELOG.md` 的更新纳入 PR 提交的 Definition of Done 检查清单，或完全依赖约定式提交实现自动化生成。

**误区3：破坏性变更（Breaking Change）不需要特别标注**
MAJOR 版本升级代表 API 不兼容，若变更日志中未明确标注 `BREAKING CHANGE` 及迁移指南，用户升级后遭遇崩溃将浪费大量排查时间。SemVer 规范明确要求破坏性变更必须体现在 MAJOR 版本号上，而变更日志是向用户传达这一信息的主要渠道。

---

## 知识关联

变更日志管理建立在 **Git 提交工作流**之上，理解 `git tag` 的创建机制有助于明白自动化工具如何确定"上一次发布以来的所有提交"——工具通过 `git log v1.1.0..HEAD` 这类命令获取区间内的提交记录。

向前延伸，变更日志管理直接支撑 **语义化版本控制（SemVer）** 的落地执行：约定式提交中的 `feat`/`fix`/`BREAKING CHANGE` 标记与 MINOR/PATCH/MAJOR 递增规则形成一一对应关系，使版本号的增减有据可查。对于持续交付（CD）流水线，`CHANGELOG.md` 的内容还常被直接消费为 **GitHub/GitLab Release** 的发布说明，连接版本管理与用户沟通两个环节。