---
id: "db-migration"
concept: "数据库迁移"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 4
is_milestone: false
tags: ["运维"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 数据库迁移

## 概述

数据库迁移（Database Migration）是指对数据库模式（Schema）进行版本化管理的工程实践，通过编写可执行的迁移脚本来追踪、应用和回滚数据库结构的变更。与直接在数据库中手动执行DDL语句不同，迁移将每一次表结构变更——如新增列、删除索引、修改字段类型——封装为带有时间戳或序列号的版本文件，使数据库结构的演变过程可被代码仓库追踪。

数据库迁移工具的历史可以追溯到2005年前后。Ruby on Rails框架在1.0版本中引入了 `ActiveRecord::Migration`，首次将数据库迁移系统化并推广至工程界。此后，Flyway（2010年）、Liquibase（2006年）、Alembic（2012年，专为SQLAlchemy设计）等工具相继出现，成为各语言生态中的标准选择。在AI工程场景下，模型特征表、实验记录表、向量索引表随着业务迭代频繁变更，若无迁移管理则极易导致开发、测试、生产三套环境的数据库结构不一致，进而引发难以排查的线上故障。

迁移的核心价值在于将数据库结构变更纳入与应用代码同等级别的版本控制体系。一个团队如果有5名工程师同时开发不同功能，每人都可能需要修改数据库表结构，迁移机制确保这些变更能够被有序合并，并在CI/CD流水线中自动执行，无需手工同步SQL脚本。

---

## 核心原理

### 迁移文件的结构与命名

每个迁移文件包含两个方向的操作：`upgrade`（正向变更）和 `downgrade`（回滚变更）。以Alembic为例，一个典型迁移文件的核心结构如下：

```python
revision = '3a7f9c2e1b84'
down_revision = 'a1b2c3d4e5f6'

def upgrade():
    op.add_column('model_experiments',
        sa.Column('f1_score', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('model_experiments', 'f1_score')
```

其中 `revision` 是当前迁移的唯一哈希标识，`down_revision` 指向父迁移，这两个字段共同构成了迁移的有向无环图（DAG）结构。Flyway则采用文件名约定方式，如 `V20240315_001__add_feature_store_table.sql`，其中 `V` 前缀表示版本迁移，`20240315_001` 是版本号，双下划线后为描述性名称。

### 迁移状态追踪机制

迁移工具在目标数据库中维护一张专用的元数据表来追踪已执行的迁移。Flyway将此表命名为 `flyway_schema_history`，Alembic使用 `alembic_version`，Liquibase使用 `databasechangelog`。

以 `alembic_version` 为例，该表只有一列 `version_num`，存储当前数据库所处的迁移版本哈希值。每次执行 `alembic upgrade head` 时，Alembic会读取此值，沿DAG链路找到尚未执行的迁移，按顺序运行 `upgrade()` 函数，最后将 `version_num` 更新为最新版本。执行 `alembic downgrade -1` 则调用最近一次迁移的 `downgrade()` 函数，并将版本号回退一级。

### 破坏性迁移与零停机迁移

某些数据库变更操作被称为"破坏性迁移"（Destructive Migration），典型案例包括：直接删除列（`DROP COLUMN`）、修改列数据类型（如 `VARCHAR(100)` 改为 `VARCHAR(50)`）、添加 `NOT NULL` 约束而不指定默认值。这类操作在高并发的生产环境中可能导致表锁或应用报错。

工程界针对此类场景发展出"展开-收缩"模式（Expand-Contract Pattern），将一次破坏性变更拆分为至少3个独立的迁移步骤。以重命名列 `user_name` 为 `username` 为例：

1. **Expand**：新增 `username` 列，应用代码同时写入两列
2. **Migrate**：执行数据填充，将 `user_name` 数据复制至 `username`
3. **Contract**：旧代码下线后，删除 `user_name` 列

这种方式确保每一步迁移都可在不停机的状态下安全执行。

---

## 实际应用

**AI特征工程场景**：在构建机器学习特征存储时，初始表可能只有 `user_id`、`created_at` 等基础字段。随着特征迭代，需要陆续添加 `embedding_v1 VECTOR(768)`、`embedding_v2 VECTOR(1536)` 等向量列。通过迁移管理，每次特征版本升级都对应一条迁移记录，数据科学家可清楚知道某批训练数据对应的特征表处于哪个迁移版本，确保实验可复现。

**多环境一致性**：AI工程项目通常存在本地开发、staging、生产三套环境。将迁移脚本存入Git仓库，在GitHub Actions流水线中配置 `alembic upgrade head` 步骤，每次合并到main分支时自动对staging库执行迁移，生产部署前通过 `alembic current` 命令验证版本一致性，可将环境差异导致的Bug率降低60%以上（根据Flyway官方用户调研数据）。

**Liquibase的changeset去重机制**：Liquibase为每个changeset计算MD5哈希值存入 `databasechangelog` 表。如果已执行的changeset文件被篡改，下次运行时会检测到哈希不匹配并抛出 `ValidationFailedException`，这一机制有效防止了通过修改历史迁移文件来悄悄变更数据库的风险。

---

## 常见误区

**误区一：在迁移文件中混入DML操作**

迁移文件设计用于执行DDL（Data Definition Language，如 `CREATE TABLE`、`ALTER TABLE`），而非DML（Data Manipulation Language，如 `UPDATE`、`INSERT`）。若将大批量数据更新写入迁移脚本，会导致迁移执行时间过长、事务锁表，甚至在回滚时面临数据无法复原的问题。正确做法是将数据迁移逻辑写成独立的一次性脚本，与结构迁移分开执行。

**误区二：在团队环境中手动修改已发布的迁移文件**

已经提交并在任意环境中执行过的迁移文件必须视为不可变（Immutable）。修改历史迁移文件不会改变已执行数据库的实际状态，却会破坏版本追踪的一致性。当其他团队成员或其他环境拉取代码时，Alembic会因找不到匹配的 `down_revision` 链路而报错，或者Liquibase因MD5校验失败而拒绝执行。所有变更必须通过新增迁移文件来实现。

**误区三：认为 `downgrade` 总能安全回滚**

`downgrade` 操作可以回滚表结构变更，但无法自动恢复已被删除或覆盖的数据。例如迁移中执行了 `DROP COLUMN comments`，`downgrade` 可以重新添加该列，但列中原有的数据已永久丢失。因此，在生产环境执行包含删除操作的迁移前，必须先进行完整的数据库备份，而不能依赖 `downgrade` 作为安全保障。

---

## 知识关联

**与SQL基础（CRUD）的关系**：数据库迁移是SQL DDL语句（`CREATE TABLE`、`ALTER TABLE`、`DROP INDEX`等）的版本化封装。理解CRUD及基本表结构是读懂迁移脚本内容的前提，但迁移关注的是"变更过程"而非"数据操作"，是对SQL使用方式的工程化延伸。

**与ORM框架的关联**：Alembic通常与SQLAlchemy配合使用，支持通过 `alembic revision --autogenerate` 命令对比ORM模型定义与数据库现状，自动生成迁移文件草稿，极大减少手写迁移脚本的工作量，但自动生成的内容需人工审核，因为ORM无法检测所有隐含的破坏性变更。

**与CI/CD流水线的关联**：数据库迁移是持续部署体系中的关键环节，通常在应用服务启动之前执行，执行顺序为：运行迁移 → 启动API服务。若颠倒顺序，新代码访问旧结构会立即触发500错误。`alembic current` 和 `alembic history` 命令可集成到健康检查脚本中，用于验证部署后各环境的迁移版本是否符合预期。