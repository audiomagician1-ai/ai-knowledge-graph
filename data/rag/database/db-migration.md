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
---
# 数据库迁移

## 概述

数据库迁移（Database Migration）是指对数据库结构（Schema）进行版本化管理的一套机制，通过有序执行的脚本文件来描述数据库从一个状态演进到另一个状态的全部变更。与直接修改数据库表结构不同，迁移将每一次 `ALTER TABLE`、`CREATE INDEX` 或 `DROP COLUMN` 操作封装为可追踪、可回滚的代码文件，使数据库结构变更像应用代码一样纳入版本控制。

数据库迁移工具的历史可以追溯到2005年前后，Ruby on Rails 框架将其作为内置功能推广，使"迁移文件"的概念被广泛接受。此后 Flyway（2010年首发）和 Liquibase 等独立工具相继出现，支持 Java、Python 等多语言生态。Python AI 工程领域常用的 Alembic 是 SQLAlchemy 的配套迁移工具，于2011年发布，目前是 FastAPI 和 LangChain 应用后端的主流数据库版本管理方案。

在 AI 工程中，数据库迁移尤其重要，因为模型迭代会频繁引发数据结构变更——例如为存储新的向量嵌入字段、修改标注表的枚举类型、或为特征工程新增宽表列。若无迁移机制，团队成员各自对数据库执行未记录的手动变更，极易导致开发、测试、生产三套环境的表结构不一致，造成难以复现的线上故障。

---

## 核心原理

### 迁移文件的版本号机制

每个迁移文件都携带一个唯一的版本标识符，用于确定执行顺序。Flyway 使用语义化文件名如 `V1__create_users_table.sql`、`V2__add_embedding_column.sql`，版本号严格递增。Alembic 则生成12位十六进制 revision ID，例如 `a3f8b2c1d4e5`，并在文件头部用 `revision` 和 `down_revision` 两个变量构成链表：

```python
revision = 'a3f8b2c1d4e5'
down_revision = '9e7c0b1a2f3d'
```

迁移工具维护一张名为 `alembic_version`（或 Flyway 的 `flyway_schema_history`）的系统表，记录当前数据库已应用到哪个版本。每次执行 `alembic upgrade head` 时，工具读取该表，计算出尚未执行的迁移文件集合，按版本链顺序逐一执行。

### upgrade 与 downgrade 的对称设计

每个迁移文件必须同时实现 `upgrade()` 和 `downgrade()` 两个函数，分别描述"正向变更"与"回滚操作"：

```python
def upgrade():
    op.add_column('predictions', sa.Column('confidence', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('predictions', 'confidence')
```

`downgrade` 函数确保可以通过 `alembic downgrade -1` 将数据库回退一个版本，或 `alembic downgrade base` 回退到初始状态。需要注意的是，并非所有变更都能完美回滚——删除带有非空约束的列后再 downgrade，若期间已写入数据，则可能因约束冲突而失败。

### 自动生成与手动编写

Alembic 提供 `alembic revision --autogenerate` 命令，通过比对 SQLAlchemy ORM Model 定义与数据库当前实际结构，自动生成迁移文件草稿。但自动生成有明确的局限性：它无法检测到列的重命名（只会生成 drop + add 两步）、无法处理自定义数据库函数，以及无法自动迁移已有行的数据（Data Migration）。因此，自动生成的文件必须经人工审查后才可提交。

数据迁移（Data Migration）与结构迁移（Schema Migration）是两类不同任务。前者在迁移文件的 `upgrade()` 中加入 `op.execute("UPDATE ...")` 语句来转换已有数据，例如将旧的 `label_string` 列的字符串值批量转换为新的整数 `label_id`。

---

## 实际应用

**场景一：为向量检索新增 pgvector 列**

在将 RAG 系统从关键词检索升级为向量检索时，需要向 `documents` 表新增一个 `embedding` 列，类型为 `vector(1536)`（对应 OpenAI text-embedding-ada-002 的输出维度）。迁移文件负责先启用 pgvector 扩展，再添加列，最后创建 HNSW 索引：

```python
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column('documents', sa.Column('embedding', Vector(1536)))
    op.execute("CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)")
```

**场景二：多环境部署的 CI/CD 集成**

在 GitHub Actions 流水线中，部署步骤在启动应用服务器前先执行 `alembic upgrade head`，确保生产数据库结构与代码版本严格对齐。若迁移脚本执行失败（例如因为某列已存在导致 `DuplicateColumn` 错误），流水线立即中断，防止不兼容的新代码访问旧结构数据库。

**场景三：团队协作中的迁移冲突解决**

当两位工程师同时基于 revision `abc123` 创建了各自的迁移文件时，会形成分叉。Alembic 在执行时会报 `Multiple head revisions` 错误。解决方式是执行 `alembic merge heads` 生成一个合并节点文件，其 `down_revision` 为一个包含两个父节点的元组 `('abc123_branch_a', 'abc123_branch_b')`。

---

## 常见误区

**误区一：直接在生产数据库手动执行 ALTER TABLE**

不经过迁移文件直接修改生产库，会导致 `alembic_version` 表中的版本号与实际结构脱节。后续执行 `alembic upgrade` 时，工具仍会尝试重新执行已被手动应用的变更，引发 `column already exists` 等错误。补救方式是使用 `alembic stamp <revision_id>` 强制将版本号标记到正确状态，但这需要精确知道当前数据库对应哪个 revision，操作风险较高。

**误区二：把迁移文件当作可修改的历史记录**

已提交并在任何环境中执行过的迁移文件不应再修改其内容。若需要撤销某次变更，正确做法是创建新的迁移文件执行反向操作，而不是修改原文件。修改已执行的迁移文件会导致工具无法验证文件内容哈希（Flyway 的 `checksum` 校验机制会直接报错），且无法反映数据库的真实演变历史。

**误区三：忽略迁移文件在测试环境的执行验证**

部分团队仅在本地和生产环境执行迁移，跳过测试环境。若迁移文件依赖生产库中已有的特定数据（如外键引用的枚举表记录），在空白测试数据库中执行时会因约束违反而失败，导致测试流水线无法检验迁移脚本的正确性。应当在 CI 中始终使用空数据库完整执行全部迁移，以验证从 `base` 到 `head` 的完整链路。

---

## 知识关联

数据库迁移建立在 SQL 基础（CRUD）的语法能力之上：`upgrade()` 函数中的 DDL 操作如 `CREATE TABLE`、`ALTER TABLE ADD COLUMN` 以及 `CREATE INDEX` 本质上是 SQL DDL 语句的程序化封装。熟悉 `SELECT`、`INSERT`、`UPDATE` 的学习者可以直接理解迁移文件中数据迁移部分的 `op.execute()` 内联 SQL 语句。

在 AI 工程的数据库体系中，数据库迁移是连接"数据库设计"与"持续交付"两个领域的实践工具。掌握迁移后，工程师能够在模型版本迭代周期中安全地演化存储特征向量、模型元数据和推理日志的表结构，而不必担心多环境不一致的问题。对于使用 FastAPI + SQLAlchemy + PostgreSQL 技术栈的 AI 应用，Alembic 迁移管理是生产化部署的必备技能。
