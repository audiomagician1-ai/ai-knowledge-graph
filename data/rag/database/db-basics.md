---
id: "db-basics"
concept: "数据库基本概念"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 3
is_milestone: false
tags: ["数据库"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 数据库基本概念

## 概述

数据库（Database）是按照特定数据模型组织、存储并可被多用户共享访问的持久化数据集合。与普通文件存储不同，数据库通过**数据库管理系统（DBMS, Database Management System）**提供数据的增删改查、并发控制和持久化保证，从根本上解决了20世纪60年代程序与数据高度耦合（即"数据依赖"问题）所带来的维护噩梦。1970年，IBM研究员Edgar F. Codd在论文《A Relational Model of Data for Large Shared Data Banks》中提出关系模型，奠定了现代关系型数据库的理论基础。

数据库区别于简单CSV文件或内存字典的关键在于：它提供**持久化**（程序崩溃后数据不丢失）、**并发访问**（多个客户端同时读写不互相干扰）以及**结构化查询能力**（通过声明式语言而非遍历全文件来检索数据）。在AI工程场景中，数据库承担着训练数据集的元数据管理、特征存储（Feature Store）、模型版本记录以及在线推理时的用户画像查询等职责，直接影响模型训练和推理的吞吐效率。

---

## 核心原理

### 数据模型：关系模型的表结构

关系型数据库用**二维表（Table）**表示实体及其关系。每张表由若干**列（Column/Attribute）**和**行（Row/Tuple/Record）**构成。列定义了字段名和数据类型（如 `INT`、`VARCHAR(255)`、`FLOAT`），行代表一条具体记录。表与表之间通过**外键（Foreign Key）**建立引用关系：子表中的外键列值必须在父表的主键列中存在，否则违反**参照完整性约束**，DBMS会拒绝该操作。

关系模型中最核心的标识符是**主键（Primary Key）**——在一张表中唯一标识每一行的列或列组合。例如，用户表中的 `user_id INT NOT NULL` 被设为主键后，数据库会自动为其建立唯一索引，保证不存在两条记录拥有相同的 `user_id`。

### 数据库 vs. DBMS vs. 数据库实例

三个概念常被混淆：
- **数据库**：磁盘上实际存储的数据文件集合（如 `.ibd` 文件）
- **DBMS**：管理数据库的软件系统，如 MySQL 8.0、PostgreSQL 15、SQLite 3.x
- **数据库实例（Instance）**：DBMS 进程加载到内存中的运行态，包含缓冲池（Buffer Pool）、日志缓冲等内存结构

同一台机器上可以运行一个 DBMS 实例，同时管理多个数据库（如 `db_train`、`db_inference`、`db_user`），每个数据库内再包含若干张表。

### 数据完整性的三类约束

数据库通过约束（Constraint）在写入阶段拦截"脏数据"，而非依赖应用层校验：

1. **实体完整性**：主键列不允许 NULL，且值唯一
2. **参照完整性**：外键值必须在被引用表中存在（或为 NULL，如允许的话）
3. **域完整性**：列级约束，例如 `CHECK (age >= 0 AND age <= 150)` 或 `NOT NULL`

这三类约束由 DBMS 在执行 `INSERT`/`UPDATE` 时自动校验，失败时返回错误码（如 MySQL 的错误 1452 表示外键约束违反）。

### 存储层：页与块的概念

关系型数据库并非逐行读写磁盘，而是以**页（Page）**为最小 I/O 单位。MySQL InnoDB 的默认页大小为 **16 KB**；PostgreSQL 为 **8 KB**。一次磁盘读取会将整页加载进内存缓冲池。这意味着即使你只查询一行数据，数据库也会读取该行所在的整页（可能包含数十至数百行）——这正是理解索引优化必须掌握的物理基础。

---

## 实际应用

**AI 特征存储场景**：在推荐系统中，用户的历史行为特征通常存储在关系型数据库（如 PostgreSQL）的 `user_features` 表中，字段包括 `user_id BIGINT`、`feature_vector JSONB`、`updated_at TIMESTAMP`。在线推理时，系统根据请求携带的 `user_id` 查询对应特征行，延迟要求通常在 **10 ms** 以内。如果直接扫描全表（表扫描），百万级数据会导致查询超时；为此需要在 `user_id` 上建立索引——这是后续学习索引原理的直接动机。

**MLflow 实验记录**：MLflow 默认使用 SQLite 数据库文件（`mlflow.db`）记录每次训练的超参数、评估指标和模型工件路径。每次 `mlflow.log_param("lr", 0.001)` 调用都会向 `params` 表插入一行，`run_id` 作为外键关联到 `runs` 表。这是关系模型外键约束在实际 AI 工具链中的典型体现。

**多表联查示例**：查询所有准确率超过 0.9 的实验名称及其学习率：
```sql
SELECT e.name, p.value AS learning_rate
FROM experiments e
JOIN runs r ON r.experiment_id = e.experiment_id
JOIN params p ON p.run_id = r.run_id
JOIN metrics m ON m.run_id = r.run_id
WHERE p.key = 'lr' AND m.key = 'accuracy' AND m.value > 0.9;
```
此查询涉及 4 张表的连接，展示了关系模型通过外键将分散数据重新聚合的能力。

---

## 常见误区

**误区一：数据库等同于 Excel 表格**
Excel 没有并发控制——两人同时修改同一单元格会产生"最后写入者获胜"的数据丢失；Excel 没有事务——写到一半断电导致文件损坏。数据库的 WAL（Write-Ahead Log，预写日志）机制保证了即使进程崩溃，磁盘上的数据也处于一致状态。Excel 更无法在百万行数据上执行毫秒级的条件查询。

**误区二：主键必须是自增整数**
主键的唯一要求是"在表内唯一且非空"。UUID（如 `550e8400-e29b-41d4-a716-446655440000`，128位）常用于分布式场景的主键，避免多节点写入时的 ID 冲突。但 UUID 作为主键会导致 InnoDB 的 B+ 树索引出现页分裂（因为 UUID 无序），相比自增 INT 插入性能会下降 20%–50%，因此选择主键类型需权衡分布式需求与写入性能。

**误区三：数据库只有关系型一种**
关系型数据库（MySQL、PostgreSQL）以外，还有文档型（MongoDB，存储 JSON 文档）、键值型（Redis，纯内存存储）、列族型（HBase，适合稀疏宽表）和向量数据库（Milvus、Pinecone，专门存储高维浮点向量并支持近似最近邻搜索）。在 AI 工程中，向量数据库被用于存储文本嵌入（Embedding），是 RAG 系统的基础组件，而这些场景用 MySQL 建模会极为低效。

---

## 知识关联

**前置知识——变量与数据类型**：数据库列类型（`INT`、`VARCHAR`、`FLOAT`、`BOOLEAN`）直接对应编程语言的基本数据类型。理解 `INT` 占 4 字节、`BIGINT` 占 8 字节有助于估算表的存储空间：一张含 100 万行、每行平均 200 字节的表约占 **200 MB** 磁盘空间。

**后续概念衔接**：
- **SQL基础（CRUD）**：掌握表结构后，`SELECT`/`INSERT`/`UPDATE`/`DELETE` 语句是操作行数据的具体语法
- **数据库范式**：基于"消除数据冗余"目标，规定如何将宽表拆分为多张窄表（第一范式要求列原子性，第三范式消除传递依赖）
- **索引原理**：基于"页为单位的 I/O"这一物理现实，B+ 树索引通过减少页加载次数将查询从 O(n) 降至 O(log n)
- **事务（ACID）**：建立在数据完整性约束之上，进一步保证多条 SQL 语句的原子性执行
- **NoSQL概述**：在关系模型无法满足水平扩展或灵活 Schema 需求时，各类 NoSQL 数据库提供了不同的权衡策略