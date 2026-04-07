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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

Cargo 是 Rust 官方内置的包管理器与构建系统，由 Mozilla Research 在 2014 年与 Rust 1.0 同期开发，并随 Rust 工具链一同分发。与 Python 的 pip 或 Node.js 的 npm 不同，Cargo 同时承担依赖管理、编译协调、测试运行和文档生成四项职责，开发者无需额外安装任何构建工具即可完成完整的项目生命周期管理。

Cargo 管理的最小单元称为 **crate**（板条箱），每个 crate 对应一个可发布的 Rust 库或可执行程序。crate 的元数据和依赖声明统一写在 `Cargo.toml` 文件中，采用 TOML 格式。截至 2024 年，Cargo 的配套公共仓库 [crates.io](https://crates.io) 已托管超过 14 万个 crate，累计下载量突破 400 亿次，是 Rust 生态系统的基础设施核心。

Cargo 的重要性在于它将"可重现构建"作为设计目标：通过 `Cargo.lock` 文件精确锁定每个依赖的版本哈希，确保不同机器上的编译结果二进制一致，这在安全敏感的系统级编程场景中尤为关键。

---

## 核心原理

### Cargo.toml 与依赖声明

每个 Cargo 项目的根目录下必须包含 `Cargo.toml`，其典型结构如下：

```toml
[package]
name = "my_app"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
criterion = "0.5"
```

`[package]` 段声明项目名称、语义化版本号和 Rust edition（目前有 2015、2018、2021 三个版本）。`[dependencies]` 下的版本字符串遵循 **SemVer（语义化版本规范）**，`"1.0"` 等价于 `">=1.0.0, <2.0.0"`，Cargo 会自动选择该范围内的最新兼容版本。`features` 字段允许按需启用 crate 的可选功能，避免引入不必要的编译依赖。

### Cargo.lock 与可重现构建

`Cargo.lock` 是 Cargo 在首次构建后自动生成的锁定文件，记录每个依赖（包括间接依赖）的确切版本号和内容哈希（SHA-256 格式）。对于可执行程序，应将 `Cargo.lock` 提交到版本控制；对于库 crate，则通常不提交，以允许下游项目灵活选择版本。运行 `cargo update` 会在 `Cargo.toml` 允许的版本范围内升级依赖并刷新 `Cargo.lock`，但不会跨越主版本号边界。

### 工作空间（Workspace）机制

当项目由多个相关 crate 组成时，Cargo 提供 **Workspace** 机制统一管理。在根目录的 `Cargo.toml` 中声明 `[workspace]` 段并列出成员路径，所有成员将共享同一个 `Cargo.lock` 和编译缓存目录（`target/`），避免重复编译公共依赖。大型 Rust 项目如编译器 `rustc` 本身就使用 Workspace 将数十个子 crate 组织在单一代码仓库中。

### 常用命令速查

| 命令 | 作用 |
|---|---|
| `cargo new my_proj` | 创建新项目，生成标准目录结构 |
| `cargo build --release` | 以优化模式编译，产物位于 `target/release/` |
| `cargo test` | 运行所有单元测试与集成测试 |
| `cargo doc --open` | 生成并打开 HTML 格式 API 文档 |
| `cargo publish` | 将当前 crate 发布到 crates.io |
| `cargo clippy` | 调用 Rust 官方 lint 工具检查代码质量 |

---

## 实际应用

**添加异步运行时依赖**：Rust 的异步编程需要手动选择运行时，最流行的选择是 `tokio`。只需在 `Cargo.toml` 写入 `tokio = { version = "1", features = ["full"] }`，执行 `cargo build` 后 Cargo 会自动从 crates.io 下载源码、编译并链接，全程无需手动配置 include 路径或链接器选项。

**条件编译与 features**：某个 HTTP 客户端 crate `reqwest` 同时支持同步和异步两种 API，两者通过 features 隔离。在 `Cargo.toml` 中声明 `reqwest = { version = "0.11", default-features = false, features = ["blocking"] }` 可仅编译同步版本，将编译时间从约 45 秒缩短至约 12 秒（在典型开发机上的实测参考数值）。

**跨平台编译**：通过 `cargo build --target aarch64-unknown-linux-gnu` 可以在 x86_64 主机上为 ARM64 Linux 生成二进制。配合 `.cargo/config.toml` 中配置的交叉编译链接器，Cargo 会自动将正确的 target triple 传递给 `rustc`，无需手写 Makefile。

---

## 常见误区

**误区一：混淆 `Cargo.toml` 中的版本范围语义**
许多初学者将 `"^1.2.3"` 和 `"1.2.3"` 认为是不同行为，但在 Cargo 中两者完全等价，`^` 前缀是默认规则可以省略。真正需要注意的是 `"=1.2.3"`（精确匹配）和 `"~1.2.3"`（只允许 patch 版本浮动，即 `>=1.2.3, <1.3.0`）这两种非默认语法。

**误区二：将 `Cargo.lock` 的提交策略一刀切**
一个常见错误是"所有项目都应提交 `Cargo.lock`"或"所有项目都不应提交"。正确做法是：若 `Cargo.toml` 的 `[package]` 中未声明 `publish = false` 且属于库，则通常不提交；若是最终可执行程序或需要 CI 可重现性，则必须提交。

**误区三：`cargo update` 会拉取最新大版本**
`cargo update` 只会在 `Cargo.toml` 中已声明的版本约束范围内更新，例如声明了 `serde = "1"` 时，即便 crates.io 上发布了 `serde 2.0`，`cargo update` 也不会将其纳入。必须手动修改 `Cargo.toml` 并指定新的主版本号，才能跨越主版本边界升级。

---

## 知识关联

学习 Cargo 不需要任何预备知识，是进入 Rust 生态的第一步。掌握 Cargo 后，自然会接触到以下更深层的主题：

- **`build.rs` 构建脚本**：Cargo 允许在项目根目录放置 `build.rs` 文件，该脚本在主代码编译前由 Cargo 调用，常用于生成 FFI 绑定（如通过 `bindgen` 为 C 库自动生成 Rust 接口）或在编译期探测系统库版本。
- **crates.io 发布流程**：发布 crate 需要通过 `cargo login` 绑定 API token，并确保 `Cargo.toml` 包含 `license`、`description` 和 `repository` 等必填字段，Cargo 会在 `cargo publish` 前自动校验这些元数据。
- **自定义 Cargo 子命令**：任何名为 `cargo-xxx` 的可执行文件放入 PATH 后，即可通过 `cargo xxx` 调用，这使得 `cargo-edit`（支持 `cargo add` 命令）、`cargo-watch`（文件变更时自动重编译）等社区工具得以无缝集成到标准工作流中。