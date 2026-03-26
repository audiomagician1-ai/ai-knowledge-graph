---
id: "se-vendoring"
concept: "Vendoring"
domain: "software-engineering"
subdomain: "package-management"
subdomain_name: "包管理"
difficulty: 2
is_milestone: false
tags: ["策略"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.481
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Vendoring（依赖内嵌）

## 概述

Vendoring 是一种包管理策略，指将项目所依赖的第三方库或模块的源代码直接复制到项目自身的代码仓库中，通常存放在名为 `vendor/` 的子目录下。与动态从外部注册表（如 npm、PyPI、crates.io）拉取依赖不同，vendoring 使得依赖代码成为项目代码库的组成部分，构建时无需访问任何外部网络。

这一实践最早在 Go 语言社区中得到广泛规范化。2015 年，Go 1.5 引入了实验性的 vendor 目录支持，2016 年 Go 1.6 将其正式确立为标准行为——当项目根目录存在 `vendor/` 文件夹时，编译器优先从该目录解析依赖，而非 `$GOPATH`。这一设计直接推动了 vendoring 在整个行业的讨论与普及。

Vendoring 解决了"依赖消失"问题的现实威胁。2016 年著名的 left-pad 事件中，npm 上一个仅 11 行代码的包被作者删除，导致数千个依赖其的项目构建失败，包括 React 和 Babel。如果这些项目使用了 vendoring，该事件对其构建流程毫无影响。

## 核心原理

### vendor 目录的结构与解析逻辑

在典型的 Go 项目中，`vendor/` 目录镜像了完整的模块路径。例如，`github.com/gin-gonic/gin` 包的代码会存放于 `<项目根>/vendor/github.com/gin-gonic/gin/`。编译器在查找导入路径时，按照"本地 vendor 优先"的原则进行解析，只有在 vendor 目录中找不到对应包时，才会尝试其他路径。

在 JavaScript 生态中，npm 的 `node_modules/` 从设计上已是一种半 vendor 机制，但严格意义上的 vendoring 要求将 `node_modules/` 提交到版本控制系统（如 Git），而非仅保留 `package-lock.json`。两者的关键区别在于：lock 文件记录版本号，vendoring 记录实际代码。

### 锁定依赖与可重复构建

Vendoring 提供了比版本锁定文件更强的构建确定性。版本锁定文件（如 `Cargo.lock`、`yarn.lock`）依赖于注册表在未来仍提供该精确版本，而 vendoring 完全消除了这一外部依赖。即使 PyPI 下线、某个 npm 包被撤回（unpublish），或某个 GitHub 仓库被删除，vendor 目录中的代码依然完整可用。这一特性对 CI/CD 流水线尤为关键，因为离线或网络受限的构建环境极为常见。

### 代码审计与供应链安全

Vendoring 使第三方依赖代码可以像项目自身代码一样接受代码审查（code review）。当团队执行 `go mod vendor` 或 `cargo vendor` 后，依赖的变更会以 diff 的形式出现在 pull request 中，审查人员可以直接看到哪些第三方代码发生了改动。这是防范"供应链投毒"攻击（如在依赖更新中植入恶意代码）的有效手段。2021 年，SolarWinds 供应链攻击事件之后，这一优势受到了安全社区的更多重视。

## 实际应用

**Go 项目的标准工作流**：运行 `go mod vendor` 命令，Go 工具链会自动读取 `go.mod` 和 `go.sum` 文件，将所有依赖下载并写入 `vendor/` 目录，同时生成 `vendor/modules.txt` 清单文件。此后使用 `go build -mod=vendor` 即可完全脱离网络进行构建。

**Rust 与 Cargo**：`cargo vendor` 命令将所有 crate 的源码写入 `vendor/` 目录，并输出需要添加到 `.cargo/config.toml` 的配置片段，告知 Cargo 从本地路径而非 crates.io 解析依赖。这在嵌入式系统或航空航天软件开发中尤为常用，因为此类环境通常要求严格的离线构建与代码溯源。

**企业级内网构建场景**：许多金融机构和政府项目的构建服务器无法访问公共互联网。这些环境强制要求 vendoring，开发者在本地网络完成依赖内嵌后，将整个含 vendor 目录的代码库推送到内网 GitLab，CI 服务器直接在隔离网络中完成编译，全程零外部请求。

## 常见误区

**误区一：Vendoring 与 lock 文件是等价的**。锁定文件（`package-lock.json`、`go.sum`）只记录依赖的版本号和哈希校验值，不包含实际源代码。若注册表删除了该版本，lock 文件无法恢复构建。Vendoring 存储的是真实的源代码文件，两者在构建隔离性上存在本质差异。

**误区二：Vendoring 会导致仓库过大而不可实践**。对于大多数应用层项目，vendor 目录增加的体积在 Git 的增量存储下是可接受的。Go 官方标准库本身的许多工具就推荐在生产项目中使用 vendoring。真正需要权衡的是依赖更新频率较高时的 diff 噪音问题，而非纯粹的存储体积。

**误区三：Vendor 目录中的代码可以随意修改**。虽然技术上可以直接编辑 `vendor/` 中的文件，但这是危险做法。当运行 `go mod vendor` 进行依赖更新时，所有手动修改都会被覆盖。正确的做法是通过 `replace` 指令（Go modules）或 patch 机制（如 `patch-package` for npm）维护对上游代码的修改。

## 知识关联

Vendoring 建立在版本控制系统（Git）的基础上，理解 Git 的 commit 粒度有助于判断是否应将 vendor 目录纳入追踪。掌握 vendoring 后，自然会延伸到"私有依赖代理"（如 Athens for Go、Verdaccio for npm）的话题——代理服务器可视为团队共享的"云端 vendor 目录"，在不将代码提交到每个项目仓库的前提下实现类似的离线保障。此外，vendoring 与容器化构建（Docker multi-stage build）结合使用时，可实现完全确定性的镜像构建，这是现代 DevOps 流水线中的重要实践方向。