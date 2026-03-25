---
id: "sql-cte"
concept: "CTE公共表表达式"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 4
is_milestone: false
tags: ["cte", "recursive", "sql"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# CTE 公共表表达式

## 概述

CTE（Common Table Expression，公共表表达式）是 SQL 标准中通过 `WITH` 关键字定义的具名临时结果集，其生命周期仅限于紧随其后的单条 `SELECT`、`INSERT`、`UPDATE` 或 `DELETE` 语句执行期间。与派生子查询不同，CTE 在语句开头集中声明，允许在同一查询中被多次引用，而底层数据库引擎（如 PostgreSQL、SQL Server）通常只物化一次。

CTE 语法最早在 SQL:1999 标准中被正式纳入，IBM DB2 是最早实现该特性的商业数据库之一。微软 SQL Server 在 2005 版本开始支持 CTE，MySQL 直到 8.0 版本（2018年发布）才加入完整支持，这也是很多开发者直到近年才广泛接触 CTE 的原因。SQLite 从 3.8.3 版本（2014年）起支持非递归 CTE，从 3.35.0 版本起支持递归 CTE。

CTE 的核心价值在于两点：第一，将复杂查询分解为多个具名逻辑块，消除了深层嵌套子查询带来的可读性问题；第二，它是 SQL 中实现递归查询（如遍历树形结构、图路径搜索）的唯一标准化机制。在 AI 工程的数据管道中，处理知识图谱的层级关系、组织架构树、用户行为路径等场景时，递归 CTE 几乎不可替代。

---

## 核心原理

### 基本语法结构

非递归 CTE 的完整语法如下：

```sql
WITH cte_name1 AS (
    SELECT ...
),
cte_name2 AS (
    SELECT ... FROM cte_name1 ...
)
SELECT * FROM cte_name2;
```

`WITH` 子句可以链式定义多个 CTE，后定义的 CTE 可以引用先定义的 CTE，形成流水线式的数据转换链。每个 CTE 通过 `AS (子查询)` 绑定一个名称，该名称在后续主查询及其他 CTE 中像普通表一样使用，支持 `JOIN`、`WHERE`、聚合等所有标准操作。

### 递归 CTE 的工作机制

递归 CTE 使用 `WITH RECURSIVE` 关键字（PostgreSQL、MySQL 8.0）或直接 `WITH`（SQL Server），其内部必须包含用 `UNION ALL` 连接的两个部分：

```sql
WITH RECURSIVE cte_name AS (
    -- 锚点成员（Anchor Member）：初始行集，不引用 cte_name
    SELECT id, name, parent_id, 1 AS depth
    FROM categories WHERE parent_id IS NULL

    UNION ALL

    -- 递归成员（Recursive Member）：引用 cte_name 自身
    SELECT c.id, c.name, c.parent_id, r.depth + 1
    FROM categories c
    INNER JOIN cte_name r ON c.parent_id = r.id
)
SELECT * FROM cte_name;
```

执行过程分为三步：① 执行锚点成员，将结果放入工作表；② 对工作表中的每一行执行递归成员，将新结果追加到工作表；③ 重复步骤②直至递归成员返回空集。SQL Server 默认最大递归层数为 100，可通过 `OPTION (MAXRECURSION 0)` 设置为无限制，PostgreSQL 无内置硬性限制但建议使用 `depth` 计数器防止死循环。

### CTE 与子查询的性能差异

CTE 并非总比子查询更快。在 PostgreSQL 中，CTE 默认作为"优化隔栏"（optimization fence）——查询优化器不会将外部 `WHERE` 条件下推到 CTE 内部，这在大表场景下可能导致全表扫描。PostgreSQL 12 起引入了 `WITH ... AS MATERIALIZED` 和 `WITH ... AS NOT MATERIALIZED` 关键字，允许开发者显式控制是否物化 CTE 结果。SQL Server 则总是尝试将 CTE 展开内联，不强制物化。因此在性能敏感场景中，必须通过 `EXPLAIN ANALYZE` 验证实际执行计划而非凭直觉判断。

---

## 实际应用

**场景一：AI 特征工程中的多步数据清洗**

在准备机器学习训练数据时，常需要对原始日志做多步骤转换：

```sql
WITH raw_events AS (
    SELECT user_id, event_type, event_time
    FROM user_logs
    WHERE event_time >= '2024-01-01'
),
session_windows AS (
    SELECT user_id, event_type,
           SUM(CASE WHEN event_type = 'session_start' THEN 1 ELSE 0 END)
               OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
    FROM raw_events
),
feature_agg AS (
    SELECT user_id, session_id,
           COUNT(*) AS events_per_session
    FROM session_windows
    GROUP BY user_id, session_id
)
SELECT user_id, AVG(events_per_session) AS avg_session_depth
FROM feature_agg
GROUP BY user_id;
```

这一模式将原本需要三层嵌套子查询的逻辑拆解为三个可独立阅读和调试的具名步骤。

**场景二：知识图谱的多跳路径查询**

在知识图谱中查找两个实体之间的所有关系路径（最大深度 5 跳）：

```sql
WITH RECURSIVE paths AS (
    SELECT entity_id, ARRAY[entity_id] AS path, 0 AS hops
    FROM entities WHERE entity_id = 'AI_MODEL'

    UNION ALL

    SELECT r.target_id, p.path || r.target_id, p.hops + 1
    FROM relationships r
    JOIN paths p ON r.source_id = p.entity_id
    WHERE r.target_id != ALL(p.path)  -- 防止环路
      AND p.hops < 5
)
SELECT * FROM paths WHERE entity_id = 'GPU_HARDWARE';
```

此查询使用 PostgreSQL 的数组类型 `ARRAY[]` 追踪访问路径并检测环路，是图数据库功能在关系型数据库中的标准实现方式。

---

## 常见误区

**误区一：认为 CTE 是持久的临时表**

CTE 的生命周期严格限定在单条 SQL 语句内，语句执行完毕后立即消失，不占用 `tempdb`（SQL Server）或 `temp` 表空间。很多初学者以为 `WITH` 定义的结果集可以在后续多条语句中复用，这是错误的——需要跨语句复用时应使用 `CREATE TEMPORARY TABLE` 或物化视图。

**误区二：递归 CTE 中混淆锚点成员与递归成员**

递归 CTE 的锚点成员绝对不能引用 CTE 自身的名称，而递归成员必须引用 CTE 自身。两者之间只能用 `UNION ALL` 连接，不能用 `UNION`（去重会导致性能急剧下降且语义错误）。此外，递归成员中不允许使用聚合函数（`GROUP BY`、`HAVING`）、`DISTINCT` 或窗口函数，这是 SQL 标准的硬性限制，违反会直接报语法错误。

**误区三：认为多次引用同一 CTE 等同于执行一次**

在 PostgreSQL 12 之前，CTE 强制物化，多次引用确实只计算一次。但在 SQL Server 和 PostgreSQL 12+ 的非物化模式下，每次引用 CTE 都可能触发独立的子查询执行，导致一个 CTE 被引用 3 次时实际执行 3 次底层扫描。如果 CTE 内包含开销大的聚合，应明确使用 `AS MATERIALIZED` 或将其结果存入临时表。

---

## 知识关联

CTE 建立在 **SQL 子查询**的基础上——非递归 CTE 本质上是具名的派生子查询，理解子查询的作用域和执行时机是读懂 CTE 执行计划的前提。同时，CTE 内部大量使用 **SQL JOIN 查询**，递归 CTE 的递归成员几乎总是通过 `INNER JOIN` 将递归结果集与原始表连接，两者的 JOIN 语义在 CTE 内部与普通查询完全一致。

在数据库进阶方向上，CTE 的物化行为与**物化视图**（Materialized View）的设计思想高度相关——当某个非递归 CTE 被全局大量引用时，将其升级为物化视图并建立索引是标准的性能优化路径。在 AI 工程的数据建模中，使用 CTE 构建的多步特征提取逻辑，通常是后续迁移到 **dbt**（data build tool）数据转换框架时每个 `model.sql` 文件的直接来源。