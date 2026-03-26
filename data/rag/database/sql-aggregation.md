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
quality_tier: "B"
quality_score: 49.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
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

SQL聚合（Aggregation）是将多行数据压缩为单一结果值的操作，通过COUNT、SUM、AVG、MAX、MIN等聚合函数实现。当你需要知道"用户表里有多少条记录"或"过去30天订单的平均金额是多少"时，聚合函数是唯一能直接回答这类问题的工具。聚合操作改变了结果集的基数（cardinality）——原本100万行的表，经过COUNT聚合后只返回1行。

GROUP BY子句是聚合的搭档，它将数据按照指定列的值划分为若干分组，聚合函数随后在每个分组内独立计算。GROUP BY语法最早随SQL标准在1986年由ANSI正式规范化，此后成为所有主流关系型数据库（MySQL、PostgreSQL、Oracle、SQL Server）的核心查询能力。没有GROUP BY时，聚合函数作用于整张表；有了GROUP BY后，同一个COUNT或SUM可以同时返回每个分组的独立统计结果。

在AI工程的数据处理链路中，SQL聚合与分组承担着特征工程的关键前处理职责。训练机器学习模型之前，往往需要从原始事件日志表中聚合出"用户过去7天购买次数""商品月均销量"等统计特征，这类操作几乎全部依赖GROUP BY + 聚合函数完成，其执行效率直接决定了特征生成流水线的吞吐量。

## 核心原理

### GROUP BY的执行顺序与逻辑分组

SQL查询的逻辑执行顺序为：FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT。GROUP BY在WHERE之后执行，意味着WHERE先过滤原始行，再对过滤后的数据分组。这一顺序有实际约束：SELECT子句中出现的非聚合列，必须全部列在GROUP BY子句中，否则查询会报错（MySQL在严格模式`ONLY_FULL_GROUP_BY`下同样报错）。

举例说明：若按`department_id`和`job_title`两列分组，则SELECT中除聚合函数外，只能出现这两列；若尝试同时SELECT `employee_name`，则违反GROUP BY规则，因为同一个分组内可能存在多个不同的员工姓名，数据库无法决定返回哪一个。

### 五大聚合函数的精确语义

- **COUNT(\*)** 统计分组内的总行数，包含NULL值所在的行；**COUNT(column)** 则只统计该列非NULL的行数，两者结果可能不同。
- **SUM(column)** 对分组内指定列的所有非NULL值求和；若分组内该列全为NULL，SUM返回NULL而非0。
- **AVG(column)** 等价于 `SUM(column) / COUNT(column)`，分母是非NULL行数，而非总行数，这导致含NULL的列均值计算结果可能与预期不符。
- **MAX/MIN** 返回分组内指定列的极值，支持数值、字符串、日期类型的比较。

公式示例：统计各部门平均薪资时，
```sql
SELECT department_id, AVG(salary) AS avg_sal
FROM employees
GROUP BY department_id;
```
若某部门有员工salary为NULL，该行不计入AVG的分子与分母，平均值仅反映有薪资记录员工的均值。

### HAVING子句：对分组结果的过滤

HAVING在GROUP BY之后执行，专门用于过滤聚合结果，这是它与WHERE的本质区别。WHERE无法引用聚合函数（因为WHERE执行时分组尚未完成），但HAVING可以。典型用法：

```sql
SELECT customer_id, COUNT(order_id) AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(order_id) >= 5;
```

此查询筛选出累计下单5次及以上的客户。若将`HAVING COUNT(...) >= 5`误写为WHERE子句，数据库会直接报语法错误，因为WHERE中不允许出现聚合函数。

### DISTINCT与聚合的组合

`COUNT(DISTINCT column)` 统计分组内指定列的不重复值数量，这是一个高成本操作，数据量大时需要去重排序，执行计划中通常会出现HashAggregate或Sort节点。在PostgreSQL中，对1000万行数据执行`COUNT(DISTINCT user_id)`的耗时可比`COUNT(*)`高出3至5倍，在设计大数据量查询时需特别注意。

## 实际应用

**AI特征工程中的用户行为聚合**：在推荐系统训练数据准备阶段，常见操作是从用户点击日志表按user_id分组，计算`COUNT(*)`（总点击次数）、`COUNT(DISTINCT item_id)`（点击商品种类数）、`MAX(click_time)`（最近点击时间）等多维特征，一条GROUP BY语句可同时生成十几个统计特征列，替代反复扫描全表的低效方案。

**数据质量监控**：用GROUP BY + COUNT检测重复数据是标准做法：
```sql
SELECT user_id, COUNT(*) AS cnt
FROM user_profiles
GROUP BY user_id
HAVING COUNT(*) > 1;
```
返回结果若非空，说明user_id存在重复记录，需要进一步清洗。

**时间维度聚合**：结合日期函数，按月或按周汇总指标。例如MySQL中`DATE_FORMAT(created_at, '%Y-%m')`配合GROUP BY，可生成月度销售额趋势表，为时序预测模型提供训练数据。

**多列分组的笛卡尔展开**：对`GROUP BY city, product_category`分组时，结果行数等于两列的有效组合数，而非两列基数之积。若数据中city有20个取值、product_category有50个取值，但实际组合只出现600种，则结果为600行，而非1000行。

## 常见误区

**误区一：SELECT中的非聚合列不在GROUP BY中**
MySQL在非严格模式下允许SELECT列出未出现在GROUP BY的列，此时MySQL会从分组的任意一行取值，结果具有不确定性。这是一个隐蔽的数据错误来源：查询不报错，但返回的非聚合列值是随机的某行数据。建议始终开启`sql_mode=ONLY_FULL_GROUP_BY`以强制报错提示。

**误区二：用WHERE过滤聚合结果**
初学者常写`WHERE COUNT(*) > 10`，会收到"Invalid use of group function"错误。正确做法是将聚合过滤条件放在HAVING中。但需注意：能用WHERE提前过滤原始行的条件，不应挪到HAVING——`WHERE status = 'active'`先减少参与分组的数据量，效率远高于在HAVING中过滤。

**误区三：NULL值对聚合结果的影响被忽视**
SUM、AVG、MAX、MIN均自动忽略NULL，只有COUNT(*)不忽略NULL（因为它统计行数而非列值）。若一列存在大量NULL且业务上NULL应视为0，必须用`COALESCE(column, 0)`显式转换后再聚合，否则SUM结果会偏小，AVG结果会偏高（分母变小导致均值虚高）。

## 知识关联

**前置概念衔接**：掌握SQL基础CRUD之后，GROUP BY是第一个改变结果集结构的操作。WHERE过滤行、SELECT投影列，这两者不改变数据的"行列粒度"；而GROUP BY将多行折叠为一行，是理解数据粒度变换的关键跨越。JOIN操作产生的宽表常作为GROUP BY的数据源，先JOIN后GROUP是特征工程的标准模式。

**衔接窗口函数**：窗口函数（Window Function）是聚合与分组的自然延伸。普通GROUP BY会将分组内的多行压缩为一行，导致原始明细数据丢失；而窗口函数使用`OVER(PARTITION BY ... ORDER BY ...)`语法，在保留每一行原始数据的同时，附加上分组内的聚合计算结果。例如`SUM(salary) OVER(PARTITION BY department_id)`在每行返回该员工所在部门的薪资总和，而不是将部门压缩为一行。理解GROUP BY中"分组折叠"与窗口函数中"分组不折叠"的差异，是掌握窗口函数的核心前提。