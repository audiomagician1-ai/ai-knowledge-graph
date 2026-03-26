---
id: "se-database-refactor"
concept: "数据库重构"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 3
is_milestone: false
tags: ["数据库"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.536
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 数据库重构

## 概述

数据库重构（Database Refactoring）是指在不改变数据库语义行为的前提下，对数据库的Schema（结构模式）进行小步骤的改进性修改。与代码重构类似，数据库重构的核心约束是"外部可观察行为不变"——查询结果、存储的业务数据含义、以及与数据库交互的应用程序逻辑均不应因此而发生语义变化。2006年，Scott Ambler 和 Pramod Sadalage 在其著作《Refactoring Databases: Evolutionary Database Design》中首次系统性地定义了数据库重构的概念，并整理出超过60种具体的重构模式。

数据库重构诞生于"演化式数据库设计"（Evolutionary Database Design）的实践背景下。传统数据库设计倡导"先设计后实现"的大爆炸式建模，而演化式设计则认为数据库Schema应当随业务需求持续、安全地演进，每次变更以尽可能小的步骤推进。这种理念在敏捷开发和持续交付流水线中尤为关键，因为数据库Schema变更历来是生产部署中风险最高的环节之一。

数据库重构之所以独立于代码重构成为一个专门领域，根本原因在于数据库的双重约束：**结构变更（DDL）会影响存量数据的物理存储**，同时**多个应用甚至多个团队可能同时依赖同一张表**。删除一列或重命名一张表，在代码世界中只需全局搜索替换，但在数据库世界中可能立刻导致生产故障，且历史数据可能永久丢失。

---

## 核心原理

### 1. 展开-收缩模式（Expand-Contract Pattern）

展开-收缩（又称 Parallel Change）是数据库重构中实现零停机变更的核心技术模式，分为三个阶段：

- **展开阶段（Expand）**：在现有Schema基础上新增结构，例如新增一列 `email_address` 同时保留旧列 `email`，应用程序同时写入两列，读取时优先读新列。
- **迁移阶段（Migrate）**：将旧列的存量数据通过后台脚本批量迁移到新列，迁移期间两列并存，应用程序双写。
- **收缩阶段（Contract）**：确认所有消费方均已切换到新列后，删除旧列。

这一模式将一次危险的原子变更拆解为可回滚的三个小步骤，每个步骤都可独立部署。整个周期通常横跨多个迭代，数据库和代码的版本不一定同步发布。

### 2. 迁移脚本版本化（Versioned Migration Scripts）

Flyway、Liquibase 等工具将每一次数据库变更封装为带版本号的迁移脚本，并将执行历史存储在数据库内的专用元数据表（Flyway 使用 `flyway_schema_history`）中。脚本命名规范如 `V1__create_user_table.sql`、`V2__add_email_column.sql`，版本号严格递增，保证幂等性——同一脚本在同一数据库实例上只执行一次。

这种机制使 Schema 变更历史可追溯、可审计，并能随代码一同纳入 Git 版本控制，从而实现"基础设施即代码"的数据库层实践。

### 3. 常见重构类型

Scott Ambler 将60余种重构模式分为以下几类：

| 类别 | 示例 | 说明 |
|------|------|------|
| **结构重构** | 拆分列（Split Column）| 将 `full_name` 拆为 `first_name` + `last_name` |
| **数据质量重构** | 引入列约束（Introduce Column Constraint）| 为已有列增加 `NOT NULL` 或 `CHECK` 约束 |
| **引用完整性重构** | 添加外键（Add Foreign Key）| 为已有关联列补充外键约束 |
| **架构重构** | 移动表（Move Table）| 将表从一个 Schema 移动到另一个 Schema |
| **方法重构** | 重命名存储过程（Rename Stored Procedure）| 保持向后兼容的同名包装函数过渡 |

### 4. 向后兼容性与过渡期管理

数据库重构必须解决"新旧消费方共存"问题。常用技术包括：

- **视图（View）作为适配层**：重命名表 `users` 为 `accounts` 后，创建同名视图 `CREATE VIEW users AS SELECT * FROM accounts`，旧消费方无感知过渡。
- **触发器同步双写**：在展开阶段通过触发器（Trigger）确保旧列数据自动同步到新列，避免依赖应用层实现双写逻辑。
- **过渡期时间窗口**：Ambler 建议过渡期长度应不短于所有消费应用的一个完整发布周期，企业级项目通常为1到3个月。

---

## 实际应用

**电商系统订单表拆分**：某平台 `orders` 表包含 `shipping_address` 单列（格式为"省市区街道"拼接字符串），需重构为独立的四列以支持地址搜索功能。执行路径为：①新增 `province`、`city`、`district`、`street` 四列（展开）；②通过 Flyway 脚本解析存量 `shipping_address` 数据并回填新列（迁移）；③更新应用程序读写逻辑至新列，并在下一个迭代删除 `shipping_address` 旧列（收缩）。整个过程线上服务零中断。

**PostgreSQL 大表加列的零停机实践**：PostgreSQL 10 之前，对千万行级别的大表执行 `ALTER TABLE ADD COLUMN DEFAULT 'xxx'` 会锁全表数分钟。重构做法是：先 `ADD COLUMN NOT NULL DEFAULT NULL`（瞬间完成），再通过分批 `UPDATE` 回填默认值（每批1000行，`pg_sleep(10ms)` 间隔），最后 `ALTER COLUMN SET DEFAULT` 并添加约束，全程无表级锁。

**Liquibase 实现跨数据库兼容迁移**：使用 Liquibase XML 描述变更集（Changeset），同一脚本可在 MySQL、PostgreSQL 和 Oracle 三种数据库上执行，由 Liquibase 负责翻译为各数据库的方言 DDL，避免了针对不同环境维护多套 SQL 脚本的人工成本。

---

## 常见误区

**误区一：重构等同于 Schema 升级迁移脚本**

许多团队将数据库重构简单理解为"写一个 ALTER TABLE 脚本"。实际上，数据库重构强调的是**可逆性**和**小步骤**——每一步骤在执行后系统仍处于一致可运行状态。一个包含20条 DDL 语句的单一大迁移脚本不是重构，而是大爆炸式变更，一旦中途失败往往难以回滚。Ambler 的定义明确要求每次重构应足够小，能在单次数据库事务或极短时间窗口内完成。

**误区二：展开阶段完成后可立即执行收缩**

开发团队常误以为新旧列双写稳定一两天后就可以删除旧列。但如果系统存在定期批处理作业（如每月月结报表）或尚未部署的旧版本应用实例（蓝绿部署残留），过早执行收缩会立即引发生产故障。正确做法是通过监控日志确认旧列的读写引用量降为零，且等待时间需覆盖所有消费方的最长发布周期。

**误区三：视图过渡层可以长期保留**

为兼容旧消费方创建的过渡视图或同义词，常因"暂时还没时间清理"而成为永久性技术债务。这些适配层会模糊真实 Schema 结构，导致后续查询优化器无法利用底层表的索引统计信息（尤其在涉及视图嵌套时），引发性能退化。过渡视图应在收缩阶段与旧列一同删除，需写入团队的"技术债务看板"追踪。

---

## 知识关联

数据库重构依赖**SQL DDL 基础知识**（ALTER TABLE、CREATE VIEW、触发器语法）以及对**事务隔离级别**的理解——展开阶段的双写一致性直接依赖于数据库的 READ COMMITTED 或 SERIALIZABLE 隔离级别选择。

在工具层面，Flyway（基于约定的版本化 SQL 迁移，适合简单项目）与 Liquibase（基于 XML/YAML 变更集，支持回滚和多数据库方言）是两个最主流的数据库重构工具，两者的选择标准在于团队是否需要跨数据库兼容性和声明式回滚能力。

数据库重构是实施**持续集成/持续交付（CI/CD）**的必要条件之一：若 Schema 变更无法自动化、版本化执行，数据库将成为流水线中唯一需要人工干预的环节，阻断整个自动化部署链条。掌握数据库重构后，可进一步学习**事件溯源（Event Sourcing）**和 **CQRS 模式**——这两者将数据库层的演进推向更极端的形式，彻底分离读写模型的 Schema 演化路径。