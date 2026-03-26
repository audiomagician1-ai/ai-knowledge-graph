---
id: "se-cargo"
concept: "Cargo"
domain: "software-engineering"
subdomain: "package-management"
subdomain_name: "包管理"
difficulty: 2
is_milestone: false
tags: ["Rust"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.1
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

# Cargo：Rust 的包管理器与构建系统

## 概述

Cargo 是 Rust 编程语言的官方包管理器和构建系统，由 Rust 核心团队开发，随 Rust 1.0 在 2015 年 5 月正式发布。它将依赖管理、编译、测试、文档生成等功能整合到一个统一的工具中，开发者通过一个 `Cargo.toml` 文件即可描述项目的全部元数据和依赖关系。

与其他语言的包管理器不同，Cargo 与 Rust 编译器 `rustc` 深度集成，它不仅下载依赖，还负责确定正确的编译顺序、传递编译标志以及管理条件编译特性（features）。Rust 官方注册表 crates.io 是 Cargo 的默认包源，截至 2024 年已托管超过 15 万个公开 crate（Rust 中对包的称呼）。

Cargo 的重要性在于，它解决了 Rust 生态中跨平台构建脚本不一致的问题。由于 Rust 频繁用于系统编程和嵌入式场景，Cargo 的 `build.rs` 构建脚本机制允许在编译前动态生成代码或链接本地 C 库，这是 npm 或 pip 等工具所不具备的设计。

## 核心原理

### Cargo.toml 与 Cargo.lock 的分工

Cargo 使用两个文件管理依赖状态。`Cargo.toml` 是开发者手动维护的配置文件，使用 TOML 格式，包含 `[package]`、`[dependencies]`、`[dev-dependencies]` 等段落。例如，在 `[dependencies]` 中写 `serde = "1.0"` 表示接受语义化版本 `>=1.0.0, <2.0.0` 的任意版本。

`Cargo.lock` 则由 Cargo 自动生成，记录了每个依赖被实际解析到的精确版本（如 `serde 1.0.193`）和其内容哈希值。官方建议：应用程序（binary crate）应将 `Cargo.lock` 提交到版本控制，以保证团队成员和 CI 使用完全相同的依赖版本；而库（library crate）不应提交 `Cargo.lock`，因为库的使用者会用自己的锁文件。

### 语义化版本与依赖解析

Cargo 的版本解析器遵循语义化版本规范（SemVer 2.0.0），但有一条 Rust 特有规则：版本号 `0.x.y` 中，只有 `y` 可以兼容更新，即 `0.8.0` 与 `0.9.0` 被视为**不兼容**。这与大多数 SemVer 实现不同，影响依赖图中版本去重的行为。

当多个依赖同时引用同一个 crate 的不同版本时，Cargo 允许在同一个二进制中同时链接两个不兼容版本（如 `tokio 0.2` 和 `tokio 1.0`），这称为"版本并存"（duplicate versions）。这在迁移期间非常有用，但会增加二进制体积。

### Features 条件编译机制

Cargo 的 features 系统允许 crate 将可选功能暴露给下游用户。在 `Cargo.toml` 中通过 `[features]` 段落定义，如：

```toml
[features]
default = ["std"]
std = []
async = ["tokio"]
```

下游依赖可以通过 `serde = { version = "1.0", features = ["derive"] }` 启用特定功能。Features 只能被启用，不能被关闭——如果依赖树中任何一个 crate 开启了某个 feature，则整个编译过程中该 feature 都会生效（称为 feature 联合，feature unification）。

### 常用命令体系

Cargo 的核心命令与其功能一一对应：

- `cargo new my_project`：创建新项目，`--lib` 标志创建库项目
- `cargo build --release`：以优化模式编译，产物位于 `target/release/`
- `cargo test`：运行 `#[test]` 标注的单元测试和 `tests/` 目录下的集成测试
- `cargo doc --open`：基于源码注释生成 HTML 文档并在浏览器打开
- `cargo publish`：将 crate 发布到 crates.io（需要 API token 认证）
- `cargo update`：在 `Cargo.toml` 指定的版本范围内将依赖升级到最新版，并更新 `Cargo.lock`

## 实际应用

**Workspace 管理单仓库多项目**：大型 Rust 项目（如 Rust 编译器本身）使用 Cargo Workspace，在根目录的 `Cargo.toml` 中声明 `[workspace]`，将多个 crate 组织在同一仓库中。所有成员 crate 共享同一个 `Cargo.lock` 和 `target/` 编译目录，避免重复编译相同依赖，节省磁盘和时间。

**链接 C 库的构建脚本**：开发 Rust 与 C 互操作的项目时，可在项目根目录放置 `build.rs` 文件。Cargo 在编译主代码前先编译并运行这个脚本，脚本通过向 stdout 输出 `cargo:rustc-link-lib=ssl` 等指令通知 Cargo 链接系统库。`openssl` crate 就是通过这一机制在编译时自动检测系统 OpenSSL 版本的。

**私有注册表与镜像**：企业环境中可在 `.cargo/config.toml` 中将 crates.io 替换为国内镜像（如字节跳动的 `rsproxy.cn`）或公司内部私有注册表，无需修改任何项目代码。

## 常见误区

**误区一：`cargo update` 会跨越大版本升级依赖**。实际上 `cargo update` 只在 `Cargo.toml` 中声明的版本约束范围内更新。若声明 `tokio = "1.0"`，则 `cargo update` 永远不会升级到 `tokio 2.x`，必须手动修改 `Cargo.toml`。

**误区二：`dev-dependencies` 中的 crate 会影响发布产物**。`[dev-dependencies]` 仅在运行 `cargo test` 或 `cargo bench` 时参与编译，执行 `cargo build --release` 或 `cargo publish` 时完全不包含，因此可以放心在其中添加体积较大的测试辅助库如 `proptest` 或 `criterion`。

**误区三：在库的 `[features]` 中随意设置 `default`**。由于 feature 联合的特性，如果某个库将某个重量级功能放入 `default`，所有间接依赖该库的项目都会默认编译这个功能。`serde` 团队为此将 `derive` 宏功能设计为非默认 feature，正是为了让不需要派生宏的用户避免编译 `syn` 等过程宏依赖。

## 知识关联

学习 Cargo 之前，了解语义化版本（SemVer）规范有助于理解依赖声明中版本号的含义，但 Cargo 本身在 `cargo new` 即可上手使用，无硬性前置要求。

掌握 Cargo 之后，可以进一步探索以下方向：crates.io 生态中的热门 crate（如 `serde`、`tokio`、`clap`）的使用、使用 `cargo-audit` 工具检查依赖中的安全漏洞（其数据库来自 RustSec Advisory Database）、以及通过 `cargo-flamegraph` 进行性能剖析。Cargo 也是理解 Rust 模块系统（`mod`、`use`、`pub`）的实践载体，因为 crate 是 Rust 编译和命名空间的基本单元。