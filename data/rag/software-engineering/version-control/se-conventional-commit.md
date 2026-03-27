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

约定式提交（Conventional Commits）是一套针对 Git 提交消息的格式规范，由 Angular 团队于 2014 年首先在其开源框架的贡献指南中推广，后于 2019 年由社区整理为独立的 1.0.0 规范文档。该规范要求每条提交消息遵循固定的结构：`<类型>[可选作用域]: <描述>`，并可附带正文和脚注。这套规则让机器和人类都能以相同方式解读一条提交记录的语义含义。

约定式提交的价值在于将提交历史从自由文本变为**结构化数据**。当团队严格遵循该规范后，工具链可以自动推断版本号应如何升级（遵循语义化版本 SemVer 规则），自动生成 CHANGELOG.md 文件，并在 CI 流水线中对不合格的提交消息直接报错拦截，无需人工审查。

## 核心原理

### 提交消息的标准格式

完整的约定式提交消息由三部分组成：

```
<类型>[可选作用域]: <描述>

[可选正文]

[可选脚注]
```

其中"类型"字段是规范的核心，必须是预定义的关键词。规范官方明确要求必须支持的类型包括 `feat`（新功能）和 `fix`（缺陷修复），其余常用类型如 `docs`、`style`、`refactor`、`test`、`chore` 则由各团队自行约定。类型全部使用小写字母，冒号后紧跟一个空格，描述部分不以句号结尾。

### 与语义化版本的映射关系

约定式提交与 SemVer（语义化版本）存在精确的对应规则：

- 类型为 `fix` 的提交 → 触发 **PATCH** 版本号递增（如 1.2.3 → 1.2.4）
- 类型为 `feat` 的提交 → 触发 **MINOR** 版本号递增（如 1.2.3 → 1.3.0）
- 脚注中包含 `BREAKING CHANGE:` 或类型后附加 `!` 符号 → 触发 **MAJOR** 版本号递增（如 1.2.3 → 2.0.0）

例如，提交消息 `feat!: 移除对 Node 12 的支持` 中的感叹号明确标记了破坏性变更，会让自动化工具将主版本号从 1 升到 2，即使描述文字没有写"breaking change"，规范工具也能识别。

### BREAKING CHANGE 的两种声明方式

破坏性变更可通过两种等价方式声明。第一种是在类型或作用域后添加 `!`，例如 `refactor(auth)!: 重构登录接口参数`。第二种是在提交消息的**脚注区域**（正文之后，以空行隔开）写入 `BREAKING CHANGE: <详细说明>`，例如：

```
feat(api): 新增分页查询接口

BREAKING CHANGE: /users 接口不再支持 limit 参数，
请改用 pageSize 替代。
```

两种写法在工具解析时效果相同，但脚注写法可以提供更完整的迁移说明，适合面向外部用户的公共 API 变更。

## 实际应用

### 配合 commitlint 在 CI 中强制执行

团队通常使用 `commitlint` 工具配合 Git 的 `commit-msg` 钩子，在每次本地提交时自动校验格式。`@commitlint/config-conventional` 包内置了约定式提交的规则集。在 `.commitlintrc.json` 中写入 `{"extends": ["@commitlint/config-conventional"]}` 即可启用。若提交消息不符合规范，`git commit` 命令会直接返回非零退出码并阻止提交。

在 Pull Request 工作流中，还可以通过 GitHub Actions 的 `wagoid/commitlint-action` 检查 PR 中所有提交的格式，确保合并进主干的每一条记录都是合规的。这与 PR 审查流程直接衔接：审查者关注代码逻辑，而格式合规性完全由自动化工具负责。

### 使用 standard-version 自动生成变更日志

`standard-version` 是最常见的约定式提交配套工具。执行 `npx standard-version` 后，它会扫描自上次打标签（tag）以来的所有提交，按类型分组输出到 `CHANGELOG.md`，同时根据上述 SemVer 映射规则更新 `package.json` 中的版本号，最后自动创建一个新的 Git tag。整个发版流程从手动整理改动内容变为一条命令完成。

## 常见误区

### 误区一：`chore` 和 `refactor` 可以随意互用

`chore` 专指不影响生产代码的维护性工作，例如更新依赖版本、修改构建脚本、配置 CI 环境。`refactor` 则专指在不改变外部行为的前提下重构生产代码的内部结构。将代码逻辑重构错标为 `chore` 会导致自动生成的变更日志遗漏重要的代码变动，使其他开发者在阅读历史记录时产生误判。

### 误区二：破坏性变更只能在 `feat` 类型中出现

规范并未限制破坏性变更的类型。`fix!`、`refactor!`、`chore!` 均是合法写法。例如修复了一个 bug，但修复方式改变了原有 API 的返回值结构，此时应写 `fix!: 修正用户对象返回格式` 而不是强行改为 `feat`，否则提交历史的语义会产生混乱，误导后续维护者认为这是新增功能。

### 误区三：约定式提交是对每次提交都要写长篇说明的要求

规范对描述部分没有最低字数要求，正文和脚注均为可选项。对于简单改动，`fix(login): 修正密码框占位符文字` 这样一行完全符合规范。正文和脚注仅在需要解释**为何**做出改动或存在破坏性变更时才必须填写。团队的常见痛点不是消息太短，而是类型和作用域选择不一致，这才是需要通过 commitlint 统一规范的问题所在。

## 知识关联

约定式提交建立在 **Pull Request 工作流**的基础上：PR 工作流定义了代码合并进主干的路径，而约定式提交规范化了这条路径上每一个提交节点的语义标记。在 PR 合并时，通常需要选择将分支上的多个提交压缩（squash）为一个符合约定式提交规范的合并提交，还是保留每个独立的约定式提交记录，这一决策直接影响 CHANGELOG 的粒度。

掌握约定式提交后，团队可以进一步引入完全自动化的语义化发版流程。`semantic-release` 工具能在 CI 环境中读取约定式提交历史，自动计算版本号、发布 npm 包、创建 GitHub Release 并附上生成的变更日志，将整个发布流程从人工决策变为由提交历史驱动的自动化管线。