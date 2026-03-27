---
id: "se-conventional-commit"
concept: "约定式提交"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 2
is_milestone: false
tags: ["规范"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 约定式提交

## 概述

约定式提交（Conventional Commits）是一套针对 Git 提交信息格式的书面规范，其完整规范版本于 2019 年首次发布为 1.0.0，目前广泛采用的是基于 Angular 团队内部代码提交规范演进而来的标准。该规范要求每条提交信息必须遵循 `<类型>[可选作用域]: <描述>` 的结构，例如 `feat(auth): add OAuth2 login support`，使每一次代码变更的意图在提交信息中一目了然。

约定式提交规范的直接价值在于使提交历史可以被机器解析。当工具扫描到 `feat:` 前缀时，它知道这是一个新功能；扫描到 `fix:` 时，它知道这是一个缺陷修复；扫描到 `BREAKING CHANGE:` 关键字时，它知道这涉及不兼容的变更。这种机器可读性是自动生成 CHANGELOG 和自动递增语义化版本号（SemVer）的基础——没有约定式提交，版本发布流程就无法完全自动化。

在实际团队协作中，约定式提交还解决了 Pull Request 审查时的沟通成本问题。审查者在看到 `refactor(database): extract query builder` 时，立即知道这次改动不引入新功能也不修复 Bug，不需要额外的回归测试，大幅提升了代码审查效率。

## 核心原理

### 提交信息的结构格式

约定式提交规范定义的完整提交信息结构如下：

```
<类型>[可选作用域]: <简短描述>

[可选正文]

[可选脚注]
```

**类型（type）** 是必填字段，规范强制要求的类型包括 `feat`（新功能）和 `fix`（缺陷修复），其他常用类型如 `docs`、`style`、`refactor`、`test`、`chore` 由社区约定俗成。类型后的冒号与空格不可省略，`feat:add login` 是不合规的，必须写成 `feat: add login`。

**作用域（scope）** 放在类型后的括号内，用于标识本次提交影响的代码模块，例如 `fix(parser): handle null pointer exception` 中的 `parser` 说明改动范围仅限于解析器模块。作用域是可选的，但团队一旦决定使用，就应在项目内保持一致。

**破坏性变更（BREAKING CHANGE）** 的标记有两种方式：在脚注区写 `BREAKING CHANGE: <描述>`，或在类型/作用域后添加感叹号，如 `feat!: remove deprecated API endpoint`。这两种方式都会触发语义化版本的主版本号（Major version）递增。

### 与语义化版本的对应关系

约定式提交与语义化版本 2.0.0 规范直接对应，映射规则如下：

- `fix:` 类型提交 → 触发 **补丁版本**（PATCH）递增，如 1.0.0 → 1.0.1
- `feat:` 类型提交 → 触发 **次版本**（MINOR）递增，如 1.0.0 → 1.1.0
- 包含 `BREAKING CHANGE` 的提交 → 触发 **主版本**（MAJOR）递增，如 1.0.0 → 2.0.0

工具链（如 `semantic-release`、`standard-version`）正是依据这套映射规则，扫描自上次发布以来的所有提交信息，自动计算出下一个合适的版本号，完全无需人工干预。

### 自动化 CHANGELOG 的生成原理

`CHANGELOG.md` 的自动生成依赖提交信息的结构化分类。工具按照提交类型将变更分组：所有 `feat:` 提交归入"新功能"章节，所有 `fix:` 提交归入"缺陷修复"章节，所有 `BREAKING CHANGE` 提交归入"破坏性变更"章节。`docs:`、`style:`、`chore:` 类型的提交通常不出现在面向用户的 CHANGELOG 中，因为它们不影响最终产物的行为。

以 `conventional-changelog-cli` 工具为例，执行 `npx conventional-changelog -p angular -i CHANGELOG.md -s` 命令，工具会读取 Git 日志，按上述规则提取并格式化内容，追加到 CHANGELOG 文件头部，整个过程耗时通常不超过 1 秒。

## 实际应用

### 配合 commitlint 强制执行规范

仅靠约定无法保证团队所有成员的提交格式合规。`commitlint` 配合 `husky` 的 Git Hooks 可以在本地提交时自动校验格式。在项目根目录创建 `commitlint.config.js` 并写入 `module.exports = { extends: ['@commitlint/config-conventional'] }`，再在 `package.json` 中配置 `commit-msg` hook，一旦有人提交 `fix bug in login` 这样不合规的信息，提交动作会被立即阻断并输出错误提示。

### 在 CI/CD 流水线中触发自动发布

在 GitHub Actions 中，可以配置一个 Release 工作流：当代码推送到 `main` 分支时，`semantic-release` 工具扫描自上次 Tag 以来的所有提交，若发现 `feat:` 类型的提交，则自动将 npm 包从 1.2.3 发布为 1.3.0，并同时创建对应的 GitHub Release 和更新 CHANGELOG，整个流程无需人工执行任何发布命令。

### Monorepo 中的作用域管理

在包含多个子包的 Monorepo 项目中，约定式提交的作用域字段用于区分变更所属的子包。例如 `feat(ui-button): add size variant` 和 `fix(ui-input): correct focus style`，`semantic-release` 的 Monorepo 插件可以识别作用域，仅对 `ui-button` 和 `ui-input` 两个子包分别发布新版本，而不触及其他未发生变更的子包。

## 常见误区

**误区一：认为所有提交都必须使用 feat 或 fix 类型。** 实际上日常开发中大量的提交属于 `refactor:`（重构，不改变外部行为）、`test:`（增加测试）或 `chore:`（构建脚本、依赖更新）。将一次依赖升级误写为 `feat: upgrade lodash` 会导致工具错误地递增次版本号，正确写法是 `chore: upgrade lodash to 4.17.21`。

**误区二：认为破坏性变更必须单独作为主版本提交。** 约定式提交规范允许 `fix!:` 和 `feat!:` 同时存在——即便是一个 Bug 修复，如果修改了公开 API 的签名，也应标记为 `fix!: change return type of parse() from string to object`。类型决定的是变更的意图，感叹号决定的是兼容性影响，二者相互独立。

**误区三：将约定式提交等同于代码注释或 PR 描述。** 约定式提交信息描述的是**一次原子提交做了什么**，而不是**为什么**要做或**如何**实现。"为什么"应写在提交信息的正文（body）区域，PR 描述中则可以包含更宏观的背景说明。三者各有其受众和使用场景，不可相互替代。

## 知识关联

学习约定式提交需要已掌握 Pull Request 工作流，因为约定式提交规范通常在 PR 合并节点发挥最大作用——许多团队使用 Squash Merge 策略，将整个 PR 的所有提交压缩为一条提交信息，此时这条合并提交的格式必须严格遵循约定式提交规范，才能被 CHANGELOG 工具正确解析。如果不理解 PR 的合并策略差异（Merge Commit vs. Squash Merge vs. Rebase Merge），就无法判断应该在每个小提交上执行规范还是仅在合并时执行规范。

约定式提交是语义化版本自动化发布流程的入口环节，掌握它之后可以进一步学习 `semantic-release` 的完整配置，以及如何在 GitHub Actions 或 GitLab CI 中搭建端到端的自动发布流水线。对于维护开源库的工程师而言，约定式提交还与 npm 发布流程、GitHub Releases API 深度集成，是现代软件发布工程不可或缺的基础规范。