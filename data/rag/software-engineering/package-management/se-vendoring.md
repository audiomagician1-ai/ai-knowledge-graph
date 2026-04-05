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
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

Vendoring 是一种将项目所有外部依赖的源代码或二进制文件直接复制到项目自身代码仓库中的包管理策略。采用这种做法后，项目构建时不再需要访问外部包注册表（如 npm、PyPI、crates.io），所有依赖以"快照"形式永久保存在项目的 `vendor/` 目录（或等价目录）下。

这一做法最早在 Go 语言社区得到系统性推广。2015 年，Go 1.5 引入了对 `vendor` 目录的官方支持，允许开发者将依赖包放入 `./vendor/` 后由编译器优先从该目录加载，而非从 `$GOPATH` 全局缓存中查找。这直接催生了 `go mod vendor` 命令（Go 1.11 模块系统引入），成为 Vendoring 在主流语言中最具代表性的官方实现。

Vendoring 的核心价值在于构建的可重复性与离线可用性。当某个 npm 包的维护者删除了已发布版本（如 2016 年著名的 `left-pad` 事件，该包的删除导致数千个依赖项目构建失败），使用 Vendoring 的项目完全不受影响，因为该依赖的代码早已存储在自己的仓库中。

## 核心原理

### 目录结构与文件布局

执行 Vendoring 后，项目根目录下会出现 `vendor/` 子目录，其内部按依赖包的命名空间或模块路径组织。以 Go 项目为例，`vendor/github.com/gin-gonic/gin/` 下存放的是 gin 框架的完整源文件；同时根目录会生成一个 `vendor/modules.txt` 文件，记录每个依赖的版本号、模块路径和所包含的包列表，用于验证 vendor 目录内容与 `go.sum` 锁文件的一致性。

在 PHP 的 Composer 工具中，`composer install --no-dev` 会将依赖安装到 `vendor/` 目录，并生成 `vendor/autoload.php`，项目只需 `require 'vendor/autoload.php'` 即可自动加载所有依赖类，整个 `vendor/` 目录通常随代码一起提交到版本控制系统。

### 锁文件与 Vendoring 的协作关系

Vendoring 与锁文件（lock file）是两种相互补充的依赖固化机制，但作用层次不同。锁文件（如 `package-lock.json`、`go.sum`、`Cargo.lock`）记录的是依赖的精确版本号和内容哈希值，安装时仍需从网络下载；而 Vendoring 更进一步，将实际代码内容存入仓库，完全消除了对网络的依赖。两者可以同时使用：`go mod vendor` 命令会在生成 `vendor/` 目录的同时保留 `go.sum` 文件，构建时通过 `-mod=vendor` 标志指定优先使用 vendor 目录。

### 内容校验机制

为防止 vendor 目录中的文件被意外篡改，Go 工具链在执行 `go build` 时会自动校验 `vendor/modules.txt` 中记录的模块元数据与实际文件内容是否匹配，发现差异时会报错并拒绝构建。这一机制确保了 vendor 快照的完整性，避免了"依赖投毒"（dependency poisoning）攻击——即攻击者修改 vendor 目录中的第三方代码来注入恶意逻辑。

## 实际应用

**CI/CD 离线构建**：在隔离的持续集成环境中（如企业内网的 Jenkins 或 GitLab Runner），构建节点可能无法访问公共包注册表。使用 Vendoring 后，`go build -mod=vendor ./...` 或 `npm install --offline` 可以完全离线完成构建，构建时间也因省去网络请求而缩短，大型 Go 项目可节省 30 秒以上的依赖下载时间。

**Kubernetes 项目**：Kubernetes 源码是 Vendoring 最广为人知的实例之一。其 `vendor/` 目录包含超过 200 个第三方依赖，目录大小超过 100 MB，直接提交在 `kubernetes/kubernetes` 主仓库中。这使得任何人克隆该仓库后无需额外步骤即可编译出完整的 `kubectl` 或 `kube-apiserver` 二进制文件。

**Ruby on Rails 部署**：使用 Bundler 的 `bundle install --deployment` 命令会将 gem 安装到项目本地的 `vendor/bundle/` 目录，Heroku 等 PaaS 平台在检测到该目录存在时会优先使用其中的 gem，从而避免 Gemfile.lock 中指定的版本在 rubygems.org 上被撤回时导致的部署失败。

## 常见误区

**误区一：Vendoring 会导致仓库体积失控**
部分开发者认为将依赖代码提交到 Git 仓库会使仓库变得无法管理。实际上，依赖的源代码是纯文本文件，Git 的 delta 压缩对其效果良好。更重要的是，vendor 目录的内容在依赖不更新时不会变化，不会像二进制文件那样每次提交都产生全量存储。对于需要严格审计供应链安全的企业项目，这一"代价"是合理的。Rust 的 Cargo 工具提供 `cargo vendor` 命令，其文档明确指出 vendor 目录适合需要离线构建或供应链审查的场景。

**误区二：Vendoring 等同于依赖版本管理**
Vendoring 解决的是依赖的"可用性"问题（代码在哪里），而不是"版本选择"问题（用哪个版本）。版本选择和升级仍然依赖 `go.mod`、`package.json` 或 `Cargo.toml` 等清单文件。执行 `go get golang.org/x/text@v0.14.0` 更新版本后，必须重新运行 `go mod vendor` 才能同步更新 vendor 目录中的实际代码，否则两者会出现不一致，导致 Go 工具链报错。

**误区三：使用 Vendoring 后不需要维护锁文件**
即使使用了 Vendoring，仍然需要保留锁文件。原因是锁文件提供的哈希校验是独立的安全层，而 `modules.txt` 等 vendor 元数据文件是专门为构建工具服务的，两者记录的信息维度不同。丢弃锁文件会导致其他开发者在重新生成 vendor 目录时可能拉取到不同的间接依赖版本。

## 知识关联

理解 Vendoring 需要先了解包管理的基本概念——即项目如何声明和获取外部依赖。掌握 Vendoring 之后，可以进一步学习**依赖安全扫描**（Software Composition Analysis，SCA），因为 vendor 目录提供了一个稳定的代码快照，工具如 `govulncheck` 或 `npm audit` 可以对其进行静态分析，识别已知 CVE 漏洞。此外，Vendoring 也与**构建系统隔离**（如 Bazel 的 `WORKSPACE` 文件和 `rules_go` 的 `gazelle`）密切相关：Bazel 要求所有外部依赖以确定性方式提供，Vendoring 正是满足这一要求的常见实现路径之一。对于需要发布可重复构建（Reproducible Builds）软件的项目，Vendoring 配合 `SOURCE_DATE_EPOCH` 环境变量和固定工具链版本，可以实现字节级别相同的构建产物。