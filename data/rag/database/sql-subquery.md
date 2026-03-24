---
id: "sql-subquery"
concept: "SQL子查询"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 5
is_milestone: false
tags: ["SQL"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# SQL子查询

## 概述

SQL子查询（Subquery）是嵌套在另一条SQL语句内部的完整SELECT语句，外层语句称为主查询（Outer Query），内层语句称为子查询（Inner Query）。子查询必须用圆括号`()`包裹，可以出现在`SELECT`、`FROM`、`WHERE`、`HAVING`等子句中，返回值可以是单个标量、单列多行、多行多列或一个完整的派生表。

子查询的概念最早随SQL标准的发展而正式化，在SQL-92标准中，`EXISTS`、`IN`以及相关子查询（Correlated Subquery）的语法被明确规范。与JOIN不同，子查询允许以更接近自然语言的方式表达嵌套逻辑，例如"找出工资高于部门平均工资的员工"——这类问题用子查询表达比用JOIN更为直觉。

在AI工程的数据预处理与特征提取场景中，子查询广泛用于从原始数据库中筛选训练样本、计算统计阈值和构建动态过滤条件。理解子查询的执行机制和性能特征，是写出高效数据管道SQL的必要前提。

---

## 核心原理

### 子查询的分类与位置

按**返回结果的类型**，子查询分为四种：
- **标量子查询**：返回1行1列，可用于`SELECT`列或`WHERE`中的比较运算。
- **行子查询**：返回1行多列，使用`(col1, col2) = (子查询)`语法比较。
- **列子查询**：返回多行1列，常配合`IN`、`ANY`、`ALL`使用。
- **表子查询**：返回多行多列，放在`FROM`子句中作为派生表，必须指定别名。

按**是否引用外层列**，子查询分为：
- **非相关子查询（Non-correlated）**：完全独立于外层查询，可单独执行，数据库引擎通常只执行一次。
- **相关子查询（Correlated Subquery）**：引用了外层查询的列，外层每扫描一行就需重新执行一次子查询，时间复杂度为O(N×M)，N为外层行数，M为子查询开销。

### 关键谓词的语义

**`IN` 与 `EXISTS` 的区别**是子查询中最常见的混淆点：

```sql
-- IN：先执行子查询，返回值列表后再过滤外层
SELECT name FROM employees
WHERE dept_id IN (SELECT id FROM departments WHERE location = 'Shanghai');

-- EXISTS：对外层每行检查子查询是否返回至少一行，找到即停止
SELECT name FROM employees e
WHERE EXISTS (SELECT 1 FROM departments d
              WHERE d.id = e.dept_id AND d.location = 'Shanghai');
```

`EXISTS`子查询中`SELECT`后写`1`、`*`或任意常量均等价，因为`EXISTS`只判断结果集是否非空，不关心具体列值。当子查询结果集较大时，`EXISTS`因短路机制通常更快；当外层表较大而子查询结果集较小时，`IN`可能更高效。

**`ANY` 与 `ALL`**：`> ANY (子查询)` 表示大于子查询返回值中的至少一个；`> ALL (子查询)` 表示大于子查询返回的所有值，等价于`> MAX(子查询)`。

### 相关子查询的执行机制

以"查找工资高于本部门平均工资的员工"为例：

```sql
SELECT name, salary, dept_id
FROM employees e1
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e2.dept_id = e1.dept_id  -- 引用外层e1
);
```

此子查询引用了外层的`e1.dept_id`，因此每处理外层一行，数据库都要重新计算对应部门的`AVG(salary)`。若`employees`表有10万行、100个部门，最坏情况下子查询执行10万次。优化方式是将此逻辑改写为JOIN派生表或窗口函数（见后续知识关联）。

---

## 实际应用

### AI特征工程中的样本过滤

在构建机器学习训练集时，常需要筛选满足多步条件的样本，子查询可以分层表达：

```sql
-- 筛选：过去30天内至少有3次购买行为的用户的所有交易记录
SELECT * FROM transactions
WHERE user_id IN (
    SELECT user_id FROM transactions
    WHERE created_at >= CURDATE() - INTERVAL 30 DAY
    GROUP BY user_id
    HAVING COUNT(*) >= 3
);
```

这里内层子查询计算活跃用户列表，外层再抽取这些用户的全量记录。将此逻辑改写成JOIN虽然可行，但子查询形式在语义表达上更清晰，且便于独立调试内层逻辑。

### FROM子句中的派生表

当需要对聚合结果再次聚合时，子查询作为派生表是直接解法：

```sql
-- 计算各部门平均工资的最大值（聚合的聚合）
SELECT MAX(avg_salary)
FROM (
    SELECT dept_id, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY dept_id
) AS dept_avg;  -- 派生表必须有别名
```

MySQL 8.0之前不支持CTE，派生表子查询是处理此类需求的标准方式。

---

## 常见误区

### 误区一：混淆NULL对IN结果的影响

当子查询返回的列表中包含`NULL`时，`col NOT IN (1, 2, NULL)` 会返回空结果集，而不是预期的"排除1和2之外的所有行"。原因是`col != NULL`的比较结果为UNKNOWN（SQL三值逻辑），导致整个`NOT IN`条件为UNKNOWN而非TRUE。解决方案是在子查询中加`WHERE col IS NOT NULL`，或改用`NOT EXISTS`替代`NOT IN`。

### 误区二：认为子查询总是慢于JOIN

现代数据库优化器（如MySQL 5.6+、PostgreSQL）会对特定模式的子查询自动执行"子查询去关联化"（Subquery Unnesting）优化，将某些相关子查询自动转换为等价的JOIN执行计划。盲目将所有子查询改写为JOIN并不总能提升性能，应以`EXPLAIN`实际执行计划为判断依据。

### 误区三：在UPDATE/DELETE中忘记MySQL的限制

MySQL不允许在`UPDATE`或`DELETE`语句中直接对被修改的表使用子查询引用，例如`DELETE FROM t WHERE id IN (SELECT id FROM t WHERE score < 60)`会报错`1093`。标准解法是将子查询再包一层派生表：`DELETE FROM t WHERE id IN (SELECT id FROM (SELECT id FROM t WHERE score < 60) AS tmp)`。

---

## 知识关联

**前置知识——SQL JOIN查询**：JOIN与子查询在许多场景下可以相互转换，但子查询能表达JOIN难以直接处理的"否定存在"语义（如`NOT EXISTS`），而JOIN在等值关联后需要对结果去重（`DISTINCT`）时往往代价更高。掌握JOIN原理是判断何时用子查询替代JOIN的基础。

**进阶方向——窗口函数**：前述"部门平均工资"相关子查询的典型性能问题，可以用窗口函数`AVG(salary) OVER (PARTITION BY dept_id)`一次扫描解决，彻底避免O(N×M)的相关子查询开销。窗口函数是替代相关子查询的最直接工具。

**进阶方向——CTE公共表表达式**：`WITH dept_avg AS (SELECT ...)` 语法将子查询命名为可复用的临时结果集，等价于FROM子句中的派生表子查询，但可读性更强，且同一CTE可在主查询中多次引用而不重复计算（部分数据库中被物化）。SQL子查询是理解CTE语法动机的直接前提。
