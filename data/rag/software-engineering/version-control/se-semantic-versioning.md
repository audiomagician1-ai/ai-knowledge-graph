---
id: "se-semantic-versioning"
concept: "语义化版本"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 2
is_milestone: false
tags: ["规范"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 52.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.5
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 语义化版本

## 概述

语义化版本（Semantic Versioning，简称 SemVer）是由 Tom Preston-Werner（GitHub 联合创始人）于 2011 年提出并发布的版本号规范，核心格式为 `MAJOR.MINOR.PATCH`，即三段由点号分隔的非负整数，例如 `2.7.1`。每一段数字都承载着明确的 API 兼容性语义，使得依赖方仅凭版本号就能判断升级是否安全。

SemVer 规范诞生于依赖地狱（dependency hell）问题愈发严重的背景下。当 npm、RubyGems、Composer 等包管理器开始流行，数以千计的库相互依赖，若没有统一的版本语义，升级任何一个依赖包都可能引发连锁失败。SemVer 1.0.0 规范于 2013 年正式定稿，目前广泛应用于 npm、Cargo、Composer、Maven 等生态系统。

与随意递增的构建号或基于日期的版本（如 `20231104`）不同，SemVer 将版本号变化与 API 合约直接绑定。当你看到 `axios` 从 `0.27.2` 升级到 `1.0.0`，就知道存在破坏性变更；从 `1.3.0` 升级到 `1.4.0`，则意味着有新功能但向后兼容。这种约定大幅降低了维护多项目依赖树的认知成本。

---

## 核心原理

### MAJOR.MINOR.PATCH 三段语义

三个版本号段的递增规则在 SemVer 规范中有严格定义：

- **PATCH**（修订号）：仅修复 Bug，且修复后的行为与公开 API 文档一致，向后兼容。例如修正 `parseDate()` 在闰年边界的计算错误。
- **MINOR**（次版本号）：新增公开 API 或功能，同时保持向后兼容。例如新增 `parseDate(locale)` 可选参数。MINOR 递增时，PATCH 必须归零。
- **MAJOR**（主版本号）：做出不兼容的 API 变更。例如移除 `parseDate()` 函数或修改其返回值结构。MAJOR 递增时，MINOR 和 PATCH 均归零。

这意味着从 `3.4.2` 升级到 `3.4.3` 可以放心做，从 `3.4.2` 到 `3.5.0` 需要验证新功能是否冲突，而从 `3.x.x` 到 `4.0.0` 则必须查阅迁移指南。

### 0.x.y 初始开发阶段的特殊规则

SemVer 明确规定：**主版本号为 0 时（即 `0.y.z`），任何次版本号的变更都可能包含破坏性更改**。这是专门为尚未稳定的初始开发阶段设计的豁免条款。许多开源项目在发布 `1.0.0` 之前会经历漫长的 `0.x` 阶段，例如 Vue.js 从 `0.11` 演进到 `1.0.0` 经历了约两年时间。开发者不应对 `0.x.y` 范围内的依赖使用宽松的版本范围符号（如 `^`），因为自动升级可能引入破坏性变更。

### 预发布版本与构建元数据

SemVer 支持在基础版本号后附加预发布标识和构建元数据：

```
1.0.0-alpha.1
1.0.0-beta.3
1.0.0-rc.2
1.0.0+20231104.git.abc1234
```

预发布版本（连字符后跟标识符）的优先级**低于**正式版本：`1.0.0-alpha < 1.0.0-beta < 1.0.0-rc.1 < 1.0.0`。构建元数据（加号后的部分）不影响版本优先级比较，仅作为附加信息。npm 的 `dist-tag` 机制正是基于此，`alpha`、`beta`、`next` 标签对应不同稳定级别。

### 版本范围与兼容性符号

包管理器基于 SemVer 语义实现了版本范围选择器。以 npm 为例：

| 符号 | 含义 | 示例 |
|------|------|------|
| `^` | 兼容版本，允许 MINOR 和 PATCH 升级 | `^1.2.3` 匹配 `>=1.2.3 <2.0.0` |
| `~` | 近似版本，仅允许 PATCH 升级 | `~1.2.3` 匹配 `>=1.2.3 <1.3.0` |
| `>=` / `<` | 精确范围 | `>=1.2.0 <2.0.0` |

注意：当主版本为 0 时，`^0.2.3` 等价于 `~0.2.3`，即 npm 对 0.x 版本的 `^` 符号会自动收紧范围，这是专门针对初始开发阶段不稳定性的保护机制。

---

## 实际应用

**React 的版本策略**：React 在 `0.14` 阶段将核心拆分为 `react` 和 `react-dom` 两个包，到 `15.0.0` 正式遵循 SemVer。React `16.0.0`（2017年）引入了 Fiber 架构，尽管大多数 API 保持兼容，仍以 MAJOR 发布，因为部分内部生命周期行为有不兼容变更。React `17.0.0` 到 `18.0.0` 的升级引入了并发特性，属于典型的 MAJOR 跳跃。

**Node.js 的长期支持版本与 SemVer**：Node.js 结合 SemVer 和 LTS（Long-Term Support）策略，偶数 MAJOR 版本（如 18、20）进入 LTS 状态，获得 30 个月维护期。SemVer 在此承诺同一 MAJOR 版本内的 C++ 原生插件 API（N-API）向后兼容，开发者无需为每个次版本重新编译原生模块。

**Cargo（Rust）的自动版本解析**：Rust 的包管理器 Cargo 完全基于 SemVer，在 `Cargo.toml` 中写 `serde = "1.0"` 等价于 `^1.0.0`，Cargo 会自动选取 `1.x.x` 范围内的最新版本。Cargo 还内置了 `cargo semver-checks` 工具，可静态检测代码变更是否违反了 SemVer 承诺，例如将 `pub fn` 改为 `pub(crate) fn` 会被识别为破坏性变更。

---

## 常见误区

**误区一：内部实现变化也必须递增 MAJOR**

SemVer 的承诺范围仅限于**公开 API（Public API）**，私有实现细节的重构不触发 MAJOR 递增。如果你将一个内部排序算法从快排改为归并排序，只要公开函数签名和返回值不变，这属于 PATCH 级别变更。许多开发者误以为任何重大重构都要升 MAJOR，导致版本号膨胀，反而失去了版本语义的可信度。

**误区二：遵循 SemVer 意味着绝不引入 Bug**

SemVer 中的 PATCH 递增承诺向后兼容，但这并不意味着新版本不会引入新 Bug。SemVer 描述的是**意图层面的兼容性承诺**，而非运行时的完全等价性。`1.2.4` 可能在修复某个 Bug 的同时引入另一个 Bug，但只要没有主动修改公开 API 的契约，仍符合 SemVer 规范。依赖方仍然需要在 CI 中运行完整测试套件来验证升级后的实际行为。

**误区三：从 `1.9.0` 不能直接跳到 `2.0.0`**

SemVer 不强制版本号连续递增，也不禁止跳跃式发布。从 `1.9.0` 直接发布 `2.0.0` 是完全合规的，只要确实存在破坏性 API 变更。同样，`2.0.0` 之后可以直接发布 `3.0.0` 而跳过所有 `2.x` 版本，这在需要快速迭代公开 API 的早期项目中很常见。

---

## 知识关联

语义化版本建立在二进制版本控制的基础上——Git 等版本控制系统通过 `tag` 命令将某个提交标记为特定版本号（如 `git tag v2.1.0`），这是 SemVer 版本与代码快照关联的技术基础。没有版本控制系统的标签机制，SemVer 版本号就是无根之木。

掌握 SemVer 之后，自然引出**变更日志管理（Changelog）**的需求：仅凭版本号变化无法得知具体改动了什么，因此规范化的 `CHANGELOG.md` 与 SemVer 配套使用，记录每个版本的新增（对应 MINOR）、修复（对应 PATCH）和破坏性变更（对应 MAJOR）。[Conventional Commits](https://www.conventionalcommits.org/) 规范将提交信息格式化（如 `feat:`、`fix:`、`BREAKING CHANGE:`），进一步实现从 Git 提交历史自动生成 Changelog 并推算下一个 SemVer 版本号，形成完整的版本发布自动化流水线。