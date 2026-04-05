---
id: "sql-basics"
concept: "SQL基础(CRUD)"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 3
is_milestone: false
tags: ["SQL"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# SQL基础（CRUD）

## 概述

SQL（Structured Query Language，结构化查询语言）的CRUD操作是对关系型数据库中数据进行操控的四类基本动作：Create（创建/插入）、Read（读取/查询）、Update（更新）、Delete（删除）。这四类操作分别对应SQL中的`INSERT`、`SELECT`、`UPDATE`、`DELETE`语句，几乎所有与数据库交互的应用程序——无论是简单的用户注册系统还是复杂的AI训练数据管道——都建立在这四条指令的组合之上。

SQL诞生于1974年，由IBM研究员Donald Chamberlin和Raymond Boyce基于Edgar Codd的关系模型理论设计，最初名为SEQUEL（Structured English Query Language）。1986年，SQL被ANSI标准化，之后形成了SQL-92、SQL:1999、SQL:2003等多个版本。现代主流数据库如PostgreSQL、MySQL、SQLite均遵循SQL标准的子集，但在细节语法上存在差异，例如MySQL使用`LIMIT`分页，而早期Oracle使用`ROWNUM`。

在AI工程场景中，CRUD操作是特征工程、数据标注管理、模型训练日志记录等工作的基础。例如，将标注完成的训练样本写入数据库用`INSERT`，从特征表中取出指定批次的样本用`SELECT`，修正错误标签用`UPDATE`，清理噪声数据用`DELETE`。掌握CRUD不仅是使用数据库的入门，更是后续理解事务、锁机制与查询优化的前提。

---

## 核心原理

### CREATE（插入数据）：INSERT语句

`INSERT INTO` 语句将新行写入指定表。基本语法有两种形式：

```sql
-- 指定列名的插入（推荐方式，更安全）
INSERT INTO users (username, email, created_at)
VALUES ('alice', 'alice@example.com', NOW());

-- 批量插入（一次写入多行，效率更高）
INSERT INTO training_samples (feature_vector, label)
VALUES ('[0.1, 0.5, 0.3]', 1),
       ('[0.9, 0.2, 0.7]', 0);
```

省略列名的插入方式`INSERT INTO table VALUES (...)`要求数值与表结构中列的顺序完全一致，表结构变更后极易出错，生产环境中应避免。批量`INSERT`相比循环执行单条`INSERT`，在MySQL 8.0环境下实测可将10,000行数据的写入耗时从约2秒降低至不足0.1秒。

### READ（读取数据）：SELECT语句

`SELECT` 语句的完整执行顺序为：`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`。理解这个顺序非常重要，因为`WHERE`子句中无法引用`SELECT`中定义的别名，正是由于`WHERE`在`SELECT`之前执行。

```sql
-- 基础查询：从模型日志表中取出精度高于0.9的最新10条记录
SELECT model_name, accuracy, trained_at
FROM model_logs
WHERE accuracy > 0.9
ORDER BY trained_at DESC
LIMIT 10;
```

`WHERE`子句中常用的条件运算符包括：比较运算符（`=`、`<>`、`>`、`<`）、范围查询（`BETWEEN 0.8 AND 1.0`）、集合匹配（`IN ('BERT', 'GPT', 'T5')`）、模式匹配（`LIKE 'gpt-%'`）、以及空值判断（`IS NULL` / `IS NOT NULL`）。注意判断NULL时必须使用`IS NULL`，不能用`= NULL`，因为`NULL = NULL`在SQL中返回的结果是`NULL`而非`TRUE`。

### UPDATE（更新数据）：UPDATE语句

`UPDATE` 语句修改表中已有行的列值，必须配合`WHERE`子句使用，否则将更新表中所有行——这是CRUD操作中最常见的灾难性错误之一。

```sql
-- 将指定ID的标注样本的标签从0修正为1
UPDATE training_samples
SET label = 1, updated_at = NOW()
WHERE sample_id = 4821;

-- 批量更新：将所有由annotator_id=3标注的样本标记为待复核
UPDATE training_samples
SET review_status = 'pending'
WHERE annotator_id = 3 AND review_status = 'approved';
```

在MySQL中，执行`UPDATE`前可以先用相同`WHERE`条件执行`SELECT COUNT(*)`确认影响行数。PostgreSQL则支持`UPDATE ... RETURNING`语法，可在更新后立即返回被修改的行，方便验证。

### DELETE（删除数据）：DELETE语句

`DELETE FROM` 语句逐行删除满足条件的记录，操作被记录在事务日志中，可以回滚。与之形成对比的是`TRUNCATE TABLE`，后者清空整张表且不记录逐行日志，速度极快但无法回滚（在大多数数据库中）。

```sql
-- 删除90天前的过期实验日志
DELETE FROM experiment_logs
WHERE created_at < NOW() - INTERVAL 90 DAY;
```

生产环境的安全删除实践：先用`BEGIN`开启事务，执行`DELETE`后查看影响行数，确认无误再`COMMIT`，否则`ROLLBACK`撤销操作。

---

## 实际应用

**AI训练数据管理场景**：假设一个图像分类项目将标注数据存储在`annotations`表中，典型的CRUD工作流如下：标注员完成标注后，系统调用`INSERT`将`(image_id, class_label, annotator_id, confidence)`写入表；质检员通过`SELECT ... WHERE confidence < 0.7`查出低置信度条目；对可修复的错误标注执行`UPDATE`修正`class_label`；对无法修复的噪声样本执行`DELETE`移除。整个流程形成闭环，数据质量持续迭代。

**数据版本与软删除**：直接`DELETE`会永久丢失数据，AI工程中常用"软删除"模式——给表增加`is_deleted TINYINT DEFAULT 0`列，删除时改为`UPDATE ... SET is_deleted = 1`，查询时加`WHERE is_deleted = 0`过滤。这样历史数据仍可追溯，满足机器学习实验的可复现性要求。

---

## 常见误区

**误区一：UPDATE/DELETE不写WHERE条件**。执行`UPDATE users SET password = 'reset'`会修改表中所有用户的密码；`DELETE FROM orders`会清空整张订单表。在MySQL中可通过设置`sql_safe_updates=1`来强制要求`UPDATE`和`DELETE`必须带`WHERE`条件，作为安全防护措施。

**误区二：用`= NULL`判断空值**。`SELECT * FROM logs WHERE error_message = NULL`永远返回0行，因为SQL中NULL与任何值（包括NULL自身）的`=`比较结果都是`UNKNOWN`，正确写法是`WHERE error_message IS NULL`。

**误区三：认为SELECT \* 是高效的默认选择**。`SELECT *`会读取表的所有列，当表有`TEXT`或`BLOB`类型的大字段（如存储原始文本的特征列）时，会传输大量不必要的数据。在AI工程中的特征表上，应始终明确列出所需字段，既减少网络传输，也让查询意图更清晰。

---

## 知识关联

CRUD操作建立在**数据库基本概念**之上，包括表（Table）、行（Row）、列（Column）、主键（Primary Key）、数据类型（如`VARCHAR`、`INT`、`FLOAT`、`DATETIME`）等结构定义。若不理解主键的唯一性约束，`INSERT`时的主键冲突错误将难以排查。

掌握CRUD之后，**SQL JOIN查询**会将`SELECT`能力大幅扩展，允许在单次查询中跨多张表合并数据，例如将`features`表和`labels`表按`sample_id`关联后一次性取出训练所需的完整数据行。**SQL聚合与分组**则在`SELECT`基础上引入`COUNT()`、`AVG()`、`GROUP BY`等统计能力，用于计算每个类别的样本数量或每个标注员的平均置信度。

在工程实践层面，**ORM基础**（如Python的SQLAlchemy）将CRUD操作封装为对象方法调用，例如`session.add(obj)`对应`INSERT`，`session.query(Model).filter(...)`对应`SELECT ... WHERE`；理解底层SQL才能在ORM生成低效查询时准确识别并优化。**数据库迁移**工具（如Alembic）则管理表结构的`CREATE TABLE`、`ALTER TABLE`操作，与数据层面的CRUD形成互补。