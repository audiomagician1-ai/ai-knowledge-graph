---
id: "sql-aggregation"
concept: "SQL聚合与分组"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 4
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
updated_at: 2026-03-27
---


# SQL聚合与分组

## 概述

SQL聚合与分组是将多行数据压缩为单个汇总值的操作机制，核心由聚合函数（Aggregate Functions）和 `GROUP BY` 子句协同完成。聚合函数对一组行执行计算并返回单个标量值，例如 `COUNT()` 统计行数、`SUM()` 求和、`AVG()` 求算术平均、`MAX()`/`MIN()` 求极值。这些函数在 SQL-92 标准中被正式规范化，至今仍是所有主流数据库（MySQL、PostgreSQL、SQLite、SQL Server）的基础特性。

`GROUP BY` 子句最早在 IBM System R（1974年）的关系代数实现中出现，其设计目的是把结果集按一个或多个列的唯一值划分成若干"分组"，再对每个分组独立运行聚合函数。这与逐行操作的 `WHERE` 筛选有本质区别：`WHERE` 在分组前过滤行，而 `HAVING` 子句专门在分组后对聚合结果进行条件筛选——这一顺序差异是初学者最常混淆的地方。

在 AI 工程的数据预处理和特征工程场景中，聚合与分组直接决定能否从原始日志、交易记录或用户行为表中高效提取统计特征（如每用户点击均值、每类别商品数量），避免将全量数据拉入 Python/Pandas 内存后再计算，降低数据管道的资源消耗。

---

## 核心原理

### 聚合函数的工作机制

五个标准聚合函数各有精确语义：
- `COUNT(*)` 统计包括 NULL 在内的所有行数；`COUNT(column)` 则忽略该列的 NULL 值，两者结果可能不同。
- `SUM(column)` 对列中所有非 NULL 值求和，若全为 NULL 则返回 NULL（而非 0）。
- `AVG(column)` 等价于 `SUM(column) / COUNT(column)`，分母只计非 NULL 行，因此均值不受 NULL 行影响。
- `MAX()` 和 `MIN()` 可作用于数值、字符串（按字典序）和日期类型，对 NULL 值同样忽略。

```sql
SELECT department,
       COUNT(*)        AS total_employees,
       AVG(salary)     AS avg_salary,
       MAX(salary)     AS top_salary
FROM employees
GROUP BY department;
```

### GROUP BY 的分组逻辑与 HAVING 过滤

`GROUP BY` 将 `FROM`/`WHERE` 处理后的结果集按指定列的唯一组合分桶。**SELECT 列表中出现的非聚合列，必须全部出现在 `GROUP BY` 中**，否则在严格模式（如 MySQL 的 `ONLY_FULL_GROUP_BY`，自 5.7.5 版本默认启用）下会报错。

`HAVING` 紧跟 `GROUP BY` 之后执行，专门筛选聚合结果：

```sql
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 8000;
```

SQL 的逻辑执行顺序为：`FROM → WHERE → GROUP BY → 聚合计算 → HAVING → SELECT → ORDER BY → LIMIT`，共 8 个阶段。理解这一顺序能解释为何 `HAVING` 中可以直接引用聚合函数，而 `WHERE` 中不能。

### 多列分组与 ROLLUP / CUBE 扩展

`GROUP BY` 支持多列组合分组，每个唯一的列值组合形成一个独立分组：

```sql
SELECT year, region, SUM(revenue) AS total_revenue
FROM sales
GROUP BY year, region;
```

SQL 标准还提供 `ROLLUP` 和 `CUBE` 修饰符（PostgreSQL、MySQL 8.0+、SQL Server 均支持）：
- `GROUP BY ROLLUP(year, region)` 除生成 `(year, region)` 级别的小计外，还额外生成 `(year)` 级别汇总行和全局总计行，共产生 N+2 层结果。
- `GROUP BY CUBE(year, region)` 生成所有可能维度组合的交叉汇总，对 2 列来说产生 2²=4 种分组层级。

### DISTINCT 与聚合的结合

`COUNT(DISTINCT column)` 对列去重后再计数，语义为"不同值的个数"，在统计 UV（独立用户数）时比 `COUNT(*)` 更精确：

```sql
SELECT COUNT(DISTINCT user_id) AS unique_users
FROM page_views
WHERE event_date = '2024-01-15';
```

---

## 实际应用

**用户行为特征提取（AI 特征工程）**：在推荐系统中，常需将用户-商品点击日志聚合为用户级特征向量。以下查询在数据库层面完成统计，避免全量数据传输：

```sql
SELECT user_id,
       COUNT(*)                          AS total_clicks,
       COUNT(DISTINCT item_category)     AS category_diversity,
       AVG(dwell_time_seconds)           AS avg_dwell,
       MAX(event_timestamp)              AS last_active
FROM click_log
WHERE event_date >= '2024-01-01'
GROUP BY user_id
HAVING COUNT(*) >= 5;   -- 过滤冷启动用户
```

**数据质量监控**：通过分组聚合快速发现各数据源的 NULL 比例和异常值分布：

```sql
SELECT data_source,
       COUNT(*)                                      AS total_rows,
       SUM(CASE WHEN feature_value IS NULL THEN 1 ELSE 0 END) AS null_count,
       ROUND(100.0 * SUM(CASE WHEN feature_value IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS null_pct
FROM feature_store
GROUP BY data_source;
```

**时序分桶统计**：结合日期函数对时间窗口聚合，生成每小时请求量用于模型监控：

```sql
SELECT DATE_FORMAT(request_time, '%Y-%m-%d %H:00:00') AS hour_bucket,
       COUNT(*) AS request_count,
       AVG(latency_ms) AS avg_latency
FROM api_logs
GROUP BY hour_bucket
ORDER BY hour_bucket;
```

---

## 常见误区

**误区1：在 WHERE 中使用聚合函数**

`WHERE AVG(salary) > 8000` 会直接报语法错误，因为 `WHERE` 在聚合计算发生前执行，此时不存在聚合结果可供引用。正确写法是将条件移到 `HAVING` 子句，或使用子查询。混淆 `WHERE` 与 `HAVING` 适用阶段，是 SQL 聚合查询中最高频的错误类型。

**误区2：COUNT(\*) 与 COUNT(column) 等价**

若列中存在 NULL 值，`COUNT(*)` 统计全部行，而 `COUNT(column)` 跳过 NULL 行，二者结果不同。例如一个 10 行的表中某列有 3 个 NULL，则 `COUNT(*) = 10`，`COUNT(column) = 7`。在统计有效填写率时，必须使用 `COUNT(column)` 而非 `COUNT(*)`。

**误区3：GROUP BY 中省略非聚合列**

部分旧版 MySQL（5.7 之前默认非严格模式）允许 SELECT 列表包含未出现在 `GROUP BY` 中的非聚合列，此时数据库会从该分组中随机取一行的值，结果不可预期。迁移到 MySQL 5.7+ 或 PostgreSQL 时，此类查询会直接报错，需补全 `GROUP BY` 列或将其包裹在 `ANY_VALUE()` 函数中（MySQL 特有）。

---

## 知识关联

**前置依赖（SQL基础/CRUD）**：聚合查询必须建立在 `SELECT`、`FROM`、`WHERE` 操作熟练的基础上，因为 `WHERE` 的行级过滤决定了进入 `GROUP BY` 的原始数据范围。多表的聚合通常还需要 `JOIN` 先将表合并再分组。

**后续延伸（窗口函数）**：窗口函数（`OVER` 子句）是聚合函数的重要升级——它能在保留原始行数的同时计算聚合值，而不像 `GROUP BY` 那样将多行压缩为一行。例如 `AVG(salary) OVER (PARTITION BY department)` 可以在每一行上同时显示员工工资和所在部门的平均工资，这是普通 `GROUP BY` 无法在单次查询中实现的。掌握 `GROUP BY` 的分组语义（特别是 `PARTITION BY` 与 `GROUP BY` 的对比）是理解窗口函数分区逻辑的直接跳板。