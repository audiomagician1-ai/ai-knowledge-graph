# CTE 公共表表达式

## 概述

CTE（Common Table Expression，公共表表达式）是 SQL 标准中通过 `WITH` 关键字定义的具名临时结果集，其生命周期仅限于紧随其后的单条 `SELECT`、`INSERT`、`UPDATE` 或 `DELETE` 语句执行期间。与派生子查询不同，CTE 在语句开头集中声明，允许在同一查询中被多次引用，而底层数据库引擎（如 PostgreSQL、SQL Server）通常只物化一次。

CTE 语法最早在 SQL:1999 标准中被正式纳入，IBM DB2 是最早实现该特性的商业数据库之一。微软 SQL Server 在 2005 版本开始支持 CTE，MySQL 直到 8.0 版本（2018年4月发布）才加入完整支持，这也是很多开发者直到近年才广泛接触 CTE 的原因。SQLite 从 3.8.3 版本（2014年2月）起支持非递归 CTE，从 3.35.0 版本（2021年3月）起支持递归 CTE。Oracle Database 从 9i Release 2（2002年）起即通过 `WITH` 子句支持非递归 CTE，从 11g Release 2（2009年）起完整支持递归变体。

CTE 的核心价值在于两点：第一，将复杂查询分解为多个具名逻辑块，消除了深层嵌套子查询带来的可读性问题；第二，它是 SQL 中实现递归查询（如遍历树形结构、图路径搜索）的唯一标准化机制。在 AI 工程的数据管道中，处理知识图谱的层级关系、组织架构树、用户行为路径等场景时，递归 CTE 几乎不可替代。根据 Stack Overflow 2023 年开发者调查，PostgreSQL 以 45.55% 的使用率成为最受欢迎的数据库，其对 CTE 的完整支持是吸引开发者的重要因素之一。

> **参考文献**
> - Eisenberg, A., & Melton, J. (1999). *SQL:1999, formerly known as SQL3*. ACM SIGMOD Record, 28(1), 131–138.
> - Itzik Ben-Gan. (2016). *T-SQL Fundamentals* (3rd ed.). Microsoft Press. Chapter 5: Table Expressions, pp. 157–203.
> - Date, C. J. (2011). *SQL and Relational Theory: How to Write Accurate SQL Code* (2nd ed.). O'Reilly Media. pp. 213–241.
> - Celko, J. (2010). *Joe Celko's Trees and Hierarchies in SQL for Smarties* (2nd ed.). Morgan Kaufmann. Chapter 3: Recursive Queries, pp. 47–89.
> - Chandra, A. K., & Harel, D. (1982). Horn clause queries and generalizations. *Journal of Logic Programming*, 1(1), 1–15.

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

若需为 CTE 的输出列显式命名，可在 CTE 名称后紧跟括号列出列名：

```sql
WITH monthly_sales(month, region, total) AS (
    SELECT DATE_TRUNC('month', order_date), region, SUM(amount)
    FROM orders
    GROUP BY 1, 2
)
SELECT * FROM monthly_sales WHERE total > 100000;
```

这种写法在列名来自聚合表达式或计算列时尤其有助于提升可读性。值得注意的是，CTE 内部可以嵌套使用窗口函数、子查询甚至 `CASE WHEN` 等复杂表达式，但 CTE 本身不支持在定义内部直接使用 `ORDER BY`（除非配合 `FETCH FIRST` 子句），这一点与物化视图有本质区别。

### 递归 CTE 的工作机制

递归 CTE 使用 `WITH RECURSIVE` 关键字（PostgreSQL、MySQL 8.0）或直接 `WITH`（SQL Server、Oracle），其内部必须包含用 `UNION ALL` 连接的两个部分：

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

执行过程分为三步：① 执行锚点成员，将结果放入工作表；② 对工作表中的每一行执行递归成员，将新结果追加到工作表；③ 重复步骤②直至递归成员返回空集。SQL Server 默认最大递归层数为 100，可通过 `OPTION (MAXRECURSION 0)` 设置为无限制；PostgreSQL 无内置硬性限制，但建议使用 `depth` 计数器防止死循环；MySQL 8.0 通过系统变量 `cte_max_recursion_depth`（默认值 1000）控制最大递归深度。

### 递归 CTE 的复杂度分析

递归 CTE 的时间复杂度可以用以下公式近似描述：若树的平均分支因子为 $b$，最大深度为 $d$，则递归成员最多执行 $d$ 轮，总处理行数上界为：

$$T(b, d) = \sum_{k=0}^{d} b^k = \frac{b^{d+1} - 1}{b - 1}$$

其中 $b$ 为每个节点的平均子节点数（分支因子），$d$ 为树的最大深度，$T(b, d)$ 为递归 CTE 在整个执行过程中累计处理的行数上界。

例如，一棵分支因子为 $b=10$、深度为 $d=5$ 的组织架构树，递归 CTE 最多处理 $T(10,5) = \frac{10^6 - 1}{9} \approx 111{,}111$ 行。这说明即使是中等规模的树形结构，若分支因子或深度过大，递归 CTE 的开销也会以指数级增长，必须谨慎评估。对于分支因子 $b=2$（典型二叉树）、深度 $d=20$ 的场景，总行数约为 $2^{21} - 1 \approx 200$ 万行，已超出很多在线查询的合理阈值，此时应考虑将层级关系预先展平存储（Closure Table 模式）。

### CTE 与子查询的性能差异

CTE 并非总比子查询更快。在 PostgreSQL 12 之前，CTE 默认作为"优化隔栏"（optimization fence）——查询优化器不会将外部 `WHERE` 条件下推到 CTE 内部，这在大表场景下可能导致全表扫描。PostgreSQL 12（2019年10月发布）引入了 `WITH ... AS MATERIALIZED` 和 `WITH ... AS NOT MATERIALIZED` 关键字，允许开发者显式控制是否物化 CTE 结果。SQL Server 则总是尝试将 CTE 展开内联，不强制物化。因此在性能敏感场景中，必须通过 `EXPLAIN ANALYZE`（PostgreSQL）或 `SET STATISTICS IO ON`（SQL Server）验证实际执行计划而非凭直觉判断。

以下对比总结了四大主流数据库对 CTE 物化行为的默认策略差异：

| 数据库 | 默认行为 | 显式控制语法 | 版本要求 |
|--------|----------|--------------|----------|
| PostgreSQL ≤ 11 | 强制物化 | 不支持 | — |
| PostgreSQL ≥ 12 | 自动判断 | `AS [NOT] MATERIALIZED` | 12+ |
| SQL Server | 内联展开 | 无直接控制 | 全版本 |
| MySQL 8.0 | 内联展开 | 无直接控制 | 8.0+ |
| Oracle 12c+ | 自动判断 | `WITH ... AS INLINE` | 12c+ |

---

## 关键公式与执行模型

递归 CTE 的执行模型本质上是一个**不动点迭代**（Fixed-Point Iteration）过程。设第 $k$ 轮递归产生的行集为 $R_k$，则：

$$R_0 = \text{Anchor}$$
$$R_{k+1} = \text{RecursiveMember}(R_k)$$
$$\text{Result} = \bigcup_{k=0}^{\infty} R_k$$

当 $R_{k+1} = \emptyset$ 时迭代终止。这一语义等价于 Datalog 语言中的最小不动点语义（Least Fixed Point Semantics），由 Chandra 和 Harel 于 1982 年在关系数据库查询完备性研究中形式化描述。该语义保证了只要递归成员每轮产生的行集严格缩小（或最终为空），算法必然终止——这正是 SQL 标准要求递归成员不得使用聚合、`DISTINCT`、`GROUP BY` 等可能导致结果集不单调递增的操作符的根本原因。

对于非递归 CTE，其执行成本可近似为：

$$C_{\text{CTE}} = C_{\text{scan}} + n_{\text{ref}} \times C_{\text{lookup}}$$

其中 $C_{\text{scan}}$ 为 CTE 内部子查询的一次执行成本，$n_{\text{ref}}$ 为 CTE 被引用的次数，$C_{\text{lookup}}$ 为从物化结果集中检索数据的成本（在物化模式下接近顺序扫描）。在内联模式下，公式退化为：

$$C_{\text{inline}} \approx n_{\text{ref}} \times C_{\text{scan}}$$

这一对比公式解释了为何当 $n_{\text{ref}} \geq 2$ 且 $C_{\text{scan}}$ 较大时，强制物化反而能降低总成本；而当 $n_{\text{ref}} = 1$ 且优化器可以下推过滤条件时，内联模式通常更优。实践中，当 CTE 对应的子查询涉及多表 `JOIN` 且结果集行数超过 10 万行，但被引用次数仅为 1 时，在 PostgreSQL 12+ 中显式使用 `AS NOT MATERIALIZED` 可以让优化器做更充分的谓词下推。

---

## 实际应用示例

### 场景一：AI 特征工程中的多步数据清洗

在准备机器学习训练数据时，常需要对原始日志做多步骤转换。例如，针对某电商平台 2024 年第一季度的用户行为日志（日均记录量约 5000 万条），可用如下 CTE 链提取"用户平均会话深度"特征：

```sql
WITH raw_events AS (
    SELECT user_id, event_type, event_time
    FROM user_logs
    WHERE event_time >= '2024-01-01'
      AND event_time <  '2024-04-01'
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

这一模式将原本需要三层嵌套子查询的逻辑拆解为三个可独立阅读和调试的具名步骤。在实际工程中，若 `raw_events` 的过滤结果仍超过 1 亿行，应考虑将其物化为临时表并建立 `(user_id, event_time)` 复合索引以加速后续窗口函数计算。

### 场景二：知识图谱的多跳路径查询

例如，在某 AI 技术知识图谱中查找"大语言模型（LLM）"与"GPU 硬件"之间的所有关系路径（最大深度 5 跳）：

```sql
WITH RECURSIVE paths AS (
    SELECT entity_id, ARRAY[entity_id] AS path, 0 AS hops
    FROM entities WHERE entity_id = 'LLM'

    UNION ALL

    SELECT r.target_id, p