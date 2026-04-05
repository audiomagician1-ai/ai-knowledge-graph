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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# SQL子查询

## 概述

SQL子查询（Subquery）是嵌套在另一个SQL语句内部的完整SELECT查询，外层语句称为主查询，内层语句称为子查询。子查询的结果作为临时数据集，供主查询的WHERE、FROM、SELECT或HAVING子句使用。与JOIN不同，子查询在语法上表现为一对括号内的独立SELECT语句，例如 `SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees)`。

子查询概念随SQL标准的演进而发展。ANSI SQL-86标准首次正式规定了子查询语法，SQL-92标准进一步引入了相关子查询（Correlated Subquery）和EXISTS谓词的完整语义。在AI工程的数据处理流水线中，子查询常用于从原始数据表中筛选训练样本、计算特征统计基准值，以及过滤异常标注数据。

子查询之所以重要，在于它能够将复杂的多步骤数据逻辑压缩为单条SQL语句，使数据分析师可以用声明式方式表达"先计算均值，再筛选超过均值的记录"这类嵌套逻辑，而无需借助临时表或多次查询。

## 核心原理

### 子查询的四种位置

子查询可以出现在四个不同位置，每个位置有不同的行为规则。

**WHERE子句中的子查询**最为常见，用于过滤行，要求子查询返回单列数据。配合比较运算符（`=`、`>`、`<`）时，子查询必须返回**恰好一个值**；配合`IN`、`ANY`、`ALL`时，可返回多行单列结果。例如，`WHERE model_id IN (SELECT id FROM models WHERE accuracy > 0.95)` 会从模型日志表中提取所有准确率超过95%的模型记录。

**FROM子句中的子查询**（又称派生表，Derived Table）必须赋予别名，其结果被视为虚拟表参与后续查询。语法为 `FROM (SELECT ... ) AS alias_name`。这种形式允许对聚合结果再次聚合，例如先计算每类样本的平均标注时间，再求各类平均时间的最大值。

**SELECT子句中的子查询**（标量子查询）必须只返回1行1列，常用于在每行结果中附加一个汇总值，例如 `SELECT name, salary, (SELECT AVG(salary) FROM employees) AS avg_salary`，在每一行都显示全局平均薪资以便比较。

**HAVING子句中的子查询**与WHERE位置类似，但作用于分组聚合后的结果集，例如 `HAVING COUNT(*) > (SELECT AVG(cnt) FROM (SELECT COUNT(*) AS cnt FROM orders GROUP BY user_id) t)`。

### 非相关子查询与相关子查询

**非相关子查询（Non-correlated Subquery）**仅执行一次，其结果与外层查询无关。数据库引擎先执行内层查询，将结果缓存，再执行外层查询。时间复杂度为 O(N + M)，其中N是主查询扫描行数，M是子查询扫描行数。

**相关子查询（Correlated Subquery）**的内层查询引用了外层查询的列，因此对外层每一行都要重新执行一次内层查询。典型形式为：

```sql
SELECT e.name
FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e.department_id
);
```

此处内层查询通过 `e.department_id` 引用外层别名 `e`，对每位员工都需要重新计算其所在部门的平均薪资。若员工表有10000行，内层查询就会执行10000次，时间复杂度退化为 O(N × M)，在大数据集上性能极差，是使用相关子查询的最大风险点。

### EXISTS 与 IN 的语义差异

`EXISTS` 谓词配合相关子查询使用，只要子查询返回至少一行，结果即为TRUE，不关心具体返回值，通常写作 `SELECT * FROM ... WHERE EXISTS (SELECT 1 FROM ...)`。`IN` 则将外层列与子查询返回的整个列表逐一比较。

当子查询结果集包含NULL值时，`IN` 会因三值逻辑导致意外的行被过滤掉，而 `EXISTS` 不受此影响。因此在子查询可能返回NULL的场景下，`EXISTS` 比 `IN` 更安全可靠。

## 实际应用

**AI训练数据清洗**：假设有 `annotations` 表记录标注员对每条样本的标注结果，需要找出被至少2名标注员标记为"低质量"的样本ID：

```sql
SELECT sample_id
FROM annotations
WHERE quality_label = 'low'
GROUP BY sample_id
HAVING COUNT(DISTINCT annotator_id) >= 2;
```

若要进一步结合子查询，从 `samples` 表中取出这些低质量样本的完整元数据，可将上述查询作为IN子查询嵌入：

```sql
SELECT * FROM samples
WHERE id IN (
    SELECT sample_id FROM annotations
    WHERE quality_label = 'low'
    GROUP BY sample_id
    HAVING COUNT(DISTINCT annotator_id) >= 2
);
```

**模型性能基准比较**：在模型评估表中找出精度高于同类别模型平均精度的所有模型，使用相关子查询：

```sql
SELECT model_name, accuracy, model_type
FROM model_results r1
WHERE accuracy > (
    SELECT AVG(accuracy)
    FROM model_results r2
    WHERE r2.model_type = r1.model_type
);
```

**派生表计算分位数**：先用子查询计算每个特征的P95值，再用外层查询过滤超出范围的异常值，是特征工程中清洗离群点的标准SQL模式。

## 常见误区

**误区一：认为子查询总是比JOIN慢。** 非相关子查询经现代查询优化器处理后，往往会被自动改写为等价的JOIN执行计划，性能相当甚至更优。真正性能差的是**相关子查询**，因为它会对外层每行执行一次内层扫描。判断是否为相关子查询的关键标志是：内层SELECT语句中是否引用了外层查询的表别名或列名。

**误区二：混淆标量子查询与多行子查询的使用场景。** 将返回多行的子查询放在 `=` 右侧会引发运行时错误（如PostgreSQL报错 `ERROR: more than one row returned by a subquery used as an expression`）。若子查询可能返回多行，必须改用 `IN`、`ANY`、`ALL` 或 `EXISTS`，或者在子查询内添加 `LIMIT 1` 明确约束。

**误区三：过度嵌套子查询导致可读性崩溃。** SQL标准理论上允许无限层嵌套，但实践中超过3层的子查询维护成本极高。当嵌套层数超过2层时，应考虑改用CTE（公共表表达式，即WITH子句）重构，将每层子查询命名为可复用的逻辑单元，这也是子查询进阶到CTE的自然动机。

## 知识关联

学习SQL子查询需要以**SQL JOIN查询**为基础。许多子查询场景（尤其是WHERE IN子查询）在语义上与INNER JOIN等价，理解JOIN的连接逻辑有助于判断何时用JOIN替代子查询以获得更好性能。同时，相关子查询中的外层-内层引用关系，与LEFT JOIN处理"查找不存在关联记录"的逻辑是直接互补的。

子查询是学习**CTE公共表表达式**的直接前驱。CTE本质上是有命名的子查询，语法为 `WITH cte_name AS (SELECT ...)` 放在主查询前，解决了深度嵌套子查询的可读性问题，还支持递归查询（`WITH RECURSIVE`），可处理树形或图结构数据。

**窗口函数**（如 `ROW_NUMBER()`、`RANK()`、`LAG()`）与FROM子句子查询关系密切：窗口函数通常写在子查询的SELECT列表中，外层查询再对窗口函数的计算结果进行过滤（因为窗口函数不能直接出现在WHERE子句中）。这种"窗口函数 + 外层过滤子查询"的二层结构是SQL高级数据分析的标准范式。