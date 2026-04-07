---
id: "sql-window-functions"
concept: "窗口函数"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 4
is_milestone: false
tags: ["window-function", "analytics", "sql"]

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
updated_at: 2026-03-26
---



# 窗口函数

## 概述

窗口函数（Window Function）是SQL标准中一类特殊的函数，它对查询结果集中的"窗口"（一组相关行）进行计算，并为每一行返回一个值，**而不会像GROUP BY那样将多行折叠成一行**。这是窗口函数与聚合函数最本质的区别：执行`SUM(salary) OVER (PARTITION BY dept)`时，每个员工行都保留在结果中，同时获得其部门的薪资总和。

窗口函数在SQL:2003标准中被正式纳入规范，PostgreSQL 8.4（2009年）是最早完整实现该标准的主流数据库之一。MySQL直到8.0版本（2018年）才完整支持窗口函数，这导致此前大量MySQL项目需要用自关联或用户变量模拟实现，代码极为繁琐且性能低下。

在AI工程的数据处理阶段，窗口函数对时序特征构造至关重要。计算用户过去N天的行为累计、为训练数据打上排名标签、提取前后时间步的特征值——这些操作在特征工程中极为常见，而窗口函数是唯一能在单次SQL扫描中优雅完成这些任务的工具。

## 核心原理

### OVER子句与窗口定义

所有窗口函数的核心是`OVER()`子句，它定义了每行计算时所参照的"窗口范围"。完整语法如下：

```sql
函数名() OVER (
    PARTITION BY 分组列
    ORDER BY 排序列
    ROWS/RANGE BETWEEN 起始边界 AND 终止边界
)
```

`PARTITION BY`将结果集切分为独立的子窗口，类似GROUP BY但不合并行；`ORDER BY`决定窗口内的行序，对排名函数和偏移函数至关重要；`ROWS/RANGE`子句定义滑动窗口的物理或逻辑边界，例如`ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`表示当前行及前两行共3行的范围。

### 排名函数：ROW_NUMBER / RANK / DENSE_RANK

三个排名函数在处理**并列值**时行为不同，必须精确区分：

- `ROW_NUMBER()`：无论值是否相同，始终给出唯一连续整数（1,2,3,4）
- `RANK()`：并列时给相同排名，**并跳过后续编号**（1,1,3,4）
- `DENSE_RANK()`：并列时给相同排名，**不跳过后续编号**（1,1,2,3）

```sql
SELECT name, score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS rn,
    RANK()       OVER (ORDER BY score DESC) AS rnk,
    DENSE_RANK() OVER (ORDER BY score DESC) AS drk
FROM exam_results;
```

在AI工程中，当需要为每个用户取其最近一条记录时，用`ROW_NUMBER()`配合`PARTITION BY user_id ORDER BY created_at DESC`后过滤`rn=1`，是业界标准做法，避免了低效的相关子查询。

### 偏移函数：LAG / LEAD

`LAG(col, n, default)`返回当前行**向前**偏移n行的值；`LEAD(col, n, default)`返回**向后**偏移n行的值。第三个参数`default`定义边界处无法偏移时的默认返回值（若省略则返回NULL）。

```sql
-- 计算每日销售额与前一天的差值（用于时序特征）
SELECT date, revenue,
    LAG(revenue, 1, 0) OVER (ORDER BY date) AS prev_revenue,
    revenue - LAG(revenue, 1, 0) OVER (ORDER BY date) AS delta
FROM daily_sales;
```

在构造机器学习时序特征时，`LAG(value, 1)`到`LAG(value, 7)`可以一次性生成7个滞后特征，替代需要7次自关联的传统写法，查询计划中只需一次表扫描。

### 聚合窗口函数：滑动统计

普通聚合函数加上`OVER`子句即变为聚合窗口函数。计算7日移动平均：

```sql
SELECT date, revenue,
    AVG(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ma7
FROM daily_sales;
```

`ROWS`基于物理行数，`RANGE`基于逻辑值范围（如`RANGE BETWEEN INTERVAL '6 DAY' PRECEDING AND CURRENT ROW`）。当日期存在缺失时，两者结果不同：`ROWS`始终取固定行数，`RANGE`基于时间距离取行，处理不规则时序数据时需要明确选择。

## 实际应用

**场景1：特征工程中的用户行为序列**

为推荐系统构造用户行为特征时，需要每个用户最近3次点击的商品ID。使用`ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY click_time DESC)`标注序号后，用`CASE WHEN rn=1 THEN item_id END`提取，或直接用`LAG`/`LEAD`在同一行展开序列特征。

**场景2：去重保留最新记录**

数据清洗时常需要在重复数据中保留最新一条：
```sql
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY user_id ORDER BY updated_at DESC
    ) AS rn
    FROM user_profile
)
SELECT * FROM ranked WHERE rn = 1;
```
这比`GROUP BY + MAX + 子查询关联`的写法性能通常高出30%-50%（在有索引的情况下）。

**场景3：计算百分位排名**

`PERCENT_RANK()`返回`(rank-1)/(total_rows-1)`，`NTILE(n)`将窗口内行均匀分为n个桶，常用于将连续特征分箱或识别异常值（顶部1% NTILE=100的记录）。

## 常见误区

**误区1：认为窗口函数可以在WHERE子句中直接过滤**

窗口函数在SQL执行顺序上位于`SELECT`阶段，晚于`WHERE`和`GROUP BY`。因此`WHERE ROW_NUMBER() OVER(...) = 1`会报错，必须将窗口函数封装在CTE或子查询中再过滤。执行顺序：FROM → WHERE → GROUP BY → HAVING → **SELECT（含窗口函数）** → ORDER BY。

**误区2：混淆ROWS与RANGE的语义**

`ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING`精确表示3行（物理）；而`RANGE BETWEEN 1 PRECEDING AND 1 FOLLOWING`在`ORDER BY score`的情况下，会把score值在`[当前值-1, 当前值+1]`范围内的**所有行**都纳入窗口。当存在大量相同分数时，RANGE窗口会意外扩大，导致计算结果与预期不符。

**误区3：在GROUP BY之后误用PARTITION BY**

当查询同时含有`GROUP BY`和窗口函数时，`PARTITION BY`操作的是`GROUP BY`聚合**之后**的结果集，而非原始明细行。若需要对明细行使用窗口函数，不能先GROUP BY，或者需要将GROUP BY的结果作为子查询，再在外层应用窗口函数。

## 知识关联

窗口函数以**SQL聚合与分组**为基础：`PARTITION BY`是`GROUP BY`逻辑的泛化，`SUM() OVER()`是`SUM() GROUP BY`的不折叠版本，理解GROUP BY的执行语义是正确使用窗口函数的前提。

与**SQL子查询**的关系体现在替代关系上：大多数需要相关子查询计算行间关系的场景（如"取每组最大值对应的行"、"计算累计百分比"），都可以用窗口函数以更低的时间复杂度实现——相关子查询对每行执行一次子查询，复杂度为O(n²)，而窗口函数借助排序和滑动计算，通常为O(n log n)。窗口函数是SQL技能树中连通聚合、子查询与复杂特征工程的关键节点。