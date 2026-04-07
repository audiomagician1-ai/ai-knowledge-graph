# SQL JOIN查询

## 概述

SQL JOIN查询是关系型数据库中将两张或多张表按照指定的列关系横向合并为一个结果集的操作。与UNION纵向拼接行不同，JOIN通过匹配两表中的关联列（通常是外键与主键的对应关系）来横向扩展列数，使原本分散在不同表中的数据可以在单次查询中协同使用。

JOIN操作的理论基础来自1970年Edgar F. Codd在论文《A Relational Model of Data for Large Shared Data Banks》（发表于《Communications of the ACM》第13卷第6期，第377–387页）中提出的关系代数，其中"自然连接"（Natural Join）是JOIN的数学原型。Codd于1981年因此项工作荣获图灵奖。现代SQL标准（SQL-92，由ISO/IEC 9075:1992正式发布）规范了INNER JOIN、LEFT OUTER JOIN、RIGHT OUTER JOIN、FULL OUTER JOIN和CROSS JOIN五种语法形式，所有主流数据库（MySQL 8.0、PostgreSQL 15、SQL Server 2022）均遵循此标准。

Ramakrishnan & Gehrke（2003）在《Database Management Systems》第三版中对上述五种JOIN的执行语义与代数等价性有系统性论述，是理解JOIN底层原理的权威参考。Date（2003）在《An Introduction to Database Systems》第八版中进一步阐述了关系代数与SQL语法之间的对应关系，特别指出NATURAL JOIN因隐式匹配同名列而存在语义歧义，生产环境应优先使用显式ON条件的JOIN语法。Garcia-Molina、Ullman与Widom（2008）在《Database Systems: The Complete Book》第二版中系统梳理了JOIN优化器的代价模型，为理解查询计划选择提供了数学框架。

在AI工程的数据预处理阶段，训练数据通常存放在经过范式化的多张表中，JOIN是将用户行为表、商品属性表、标签表等合并为可供模型消费的宽表的必要手段。一次错误的JOIN类型选择会导致训练样本数量或标签值出现系统性偏差，直接影响模型质量。例如，在某大型电商推荐系统实践中，误将LEFT JOIN替换为INNER JOIN后，冷启动用户（约占全量用户的18%）被完全过滤，导致新用户推荐召回率下降约23个百分点。

**核心问题**：在构建机器学习训练集时，应如何选择JOIN类型才能同时保留冷启动样本、避免行数膨胀，并维持正负样本的原始比例？若正样本本身仅占全量用户的3%，错误的JOIN类型会如何系统性地扭曲这一比例，进而导致线上与线下评估指标的严重背离？这种偏差能否通过事后样本权重调整完全修复，还是存在不可弥补的信息损失？

## 关系代数基础与行数计算公式

理解JOIN的本质需要从关系代数的角度建立数学直觉。设表 $A$ 有 $|A|$ 行，表 $B$ 有 $|B|$ 行，连接键在 $A$ 中唯一、在 $B$ 中可重复（即一对多关系），则：

$$|\text{INNER JOIN}| = \sum_{k \in A \cap B} \text{count}_B(k)$$

其中 $\text{count}_B(k)$ 表示键值 $k$ 在表 $B$ 中出现的次数，$A \cap B$ 表示两表中键值的交集，$k$ 为连接列的具体取值（如 `user_id` 的某个整数值）。特别地：

- **一对一关系**：$|\text{INNER JOIN}| \leq \min(|A|, |B|)$，每个键最多出现一次
- **一对多关系**：$|\text{INNER JOIN}| = |B_{\text{matched}}|$，即 $B$ 中能匹配上的行数
- **多对多关系**：$|\text{INNER JOIN}|$ 可达 $|A| \times |B|$（退化为笛卡尔积）
- **CROSS JOIN**：$|\text{CROSS JOIN}| = |A| \times |B|$，无条件笛卡尔积

对于LEFT JOIN，结果行数满足：

$$|\text{LEFT JOIN}| = |A| + \sum_{k \in A \setminus B} 0 + \sum_{k \in A \cap B} (\text{count}_B(k) - 1)$$

化简后等价于：

$$|\text{LEFT JOIN}| = \max\left(|A|,\ \sum_{k \in A \cap B} \text{count}_B(k)\right)$$

即结果行数不少于左表行数，且当存在一对多匹配时会超过左表行数。这一公式是判断JOIN后是否需要去重的决策依据。

例如，若 $|A|=1000$，$|B|=5000$，其中800个键在两表均存在，每个匹配键在 $B$ 中平均出现6.25次，则INNER JOIN结果约为5000行，而非1000行——这是初学者最常忽视的行数膨胀陷阱。LEFT JOIN的结果行数同样为5000行（因一对多匹配超过左表行数1000），而并非初学者直觉上认为的"至少保留1000行且恰好等于1000行"。

对于FULL OUTER JOIN，结果行数上界为：

$$|\text{FULL OUTER JOIN}| = |A| + |B| - |\text{INNER JOIN}|$$

在 $A$、$B$ 完全不相交时，FULL OUTER JOIN结果等于 $|A| + |B|$，每行对侧均为NULL。

**JOIN选型决策树**：在动手写SQL之前，应先回答三个问题：①是否需要保留无匹配行？（是则用LEFT/FULL JOIN，否则用INNER JOIN）②哪一侧是主表，不能丢失记录？（以主表为LEFT JOIN的左侧）③连接键在两表中是否唯一？（若非唯一需提前评估行数膨胀风险）。

## 核心原理

### INNER JOIN：交集匹配

INNER JOIN返回两张表中满足ON条件的行的交集，不满足条件的行在两侧均被丢弃。其逻辑等价于关系代数中的θ连接（θ-join）。标准语法为：

```sql
SELECT a.user_id, b.order_amount
FROM users a
INNER JOIN orders b ON a.user_id = b.user_id;
```

若`users`表有1000行，`orders`表有5000行，但只有800位用户曾下单，INNER JOIN结果最多5000行（一个用户可对应多笔订单），但所有无订单用户记录会被排除在外。在构建机器学习训练集时，若用INNER JOIN连接用户特征表和标签表，会自动过滤掉无标签样本，这一行为在正负样本不均衡场景下需要特别注意。

**案例**：某广告点击率预测任务中，全量用户100万，正样本（点击）3万（占3%）。开发者使用INNER JOIN仅连接有点击记录的用户，结果集中正样本率人为升至100%，完全丢失了97%的负样本信息。模型AUC虚高约0.15（从真实0.72飙升至0.87），在线效果与离线评估出现严重偏差，A/B实验期间CTR不升反降2.1个百分点。正确做法是以全量用户为左表执行LEFT JOIN，再用`COALESCE(label, 0)`将NULL标签填充为0，保留完整的正负样本分布。

### LEFT JOIN：保留左表全部记录

LEFT OUTER JOIN（通常简写为LEFT JOIN）以左表为基准，保留左表的全部行。若右表中无匹配行，右表对应列填充NULL。标准语法示例：

```sql
SELECT a.user_id, b.order_amount
FROM users a
LEFT JOIN orders b ON a.user_id = b.user_id;
```

此查询返回全部1000位用户，其中200位未下单用户的`order_amount`为NULL。利用`WHERE b.user_id IS NULL`可以精准筛选出"从未下单的用户"，这是一种比NOT IN更高效的反连接（Anti-Join）写法。在PostgreSQL 15中可利用Hash Anti-Join执行计划加速，实测在千万行表上比NOT IN子查询快约4倍；在MySQL 8.0中同样可触发anti-join优化，需确保连接列有索引。

值得重点关注的是**ON条件与WHERE条件的语义差异**。例如：

```sql
-- 写法A：过滤条件写在ON中（保留所有用户）
SELECT a.user_id, b.order_amount
FROM users a
LEFT JOIN orders b ON a.user_id = b.user_id AND b.status = 'paid';

-- 写法B：过滤条件写在WHERE中（退化为INNER JOIN语义）
SELECT a.user_id, b.order_amount
FROM users a
LEFT JOIN orders b ON a.user_id = b.user_id
WHERE b.status = 'paid';
```

写法A保留全部用户，未付款订单用户的`order_amount`为NULL；写法B则过滤掉无付款订单的用户，语义退化为INNER JOIN。这是生产环境中频繁出现的逻辑错误，在代码评审时需重点检查。

### RIGHT JOIN与FULL OUTER JOIN

RIGHT JOIN是LEFT JOIN的镜像，以右表为基准保留右表全部行。实践中几乎所有RIGHT JOIN都可以通过交换表顺序改写为LEFT JOIN，可读性更高，建议团队统一使用LEFT JOIN风格。

FULL OUTER JOIN返回两表的并集，两侧均不匹配的行都保留（对侧填NULL）。MySQL 8.0不原生支持FULL OUTER JOIN，可通过`LEFT JOIN UNION ALL RIGHT JOIN WHERE左表键 IS NULL`模拟：

```sql
SELECT a.user_id, b.order_amount
FROM users a
LEFT JOIN orders b ON a.user_id = b.user_id
UNION ALL
SELECT a.user_id, b.order_amount
FROM users a
RIGHT JOIN orders b ON a.user_id = b.user_id
WHERE a.user_id IS NULL;
```

FULL OUTER JOIN在数据质量核查场景中尤为有用。例如，对比线上服务日志表与线下计算结果表时，使用FULL OUTER JOIN可同时找出"线上有但线下无"（右表NULL）和"线下有但线上无"（左表NULL）的异常记录，一次查询完成双向数据核对，避免两次LEFT JOIN再手工合并结果的繁琐操作。

### CROSS JOIN与笛卡尔积的危险与正当用途

CROSS JOIN返回两表行数之积的笛卡尔积，没有ON条件。若表A有1000行、表B有2000行，结果为200万行，占用存储空间可能超过原表数百倍。在没有WHERE条件保护的情况下，误将INNER JOIN写成CROSS JOIN（或忘写ON条件）会产生灾难性的全笛卡尔积，耗尽数据库内存甚至导致服务宕机。

CROSS JOIN的正当用途包括：生成日期序列与产品列表的全组合，用于填充稀疏矩阵。

**案例**：某零售企业需要构建LSTM时序预测模型，要求输入为每个产品每天的销售量。原始销售表高度稀疏，某产品某天无销售则无记录。处理方案是先用`generate_series('2024-01-01'::date, '2024-12-31'::date, '1 day'::interval)`在PostgreSQL中生成365天日期序列，再与100种产品执行CROSS JOIN生成36500行基础框架表，最后LEFT JOIN实际销售记录，将NULL填充为0，从而得到完整密集的时间序列，训练集行数从原来的约12000行（稀疏）扩充为标准36500行（密集），LSTM模型的验证集MAE降低了约18%。

### SELF JOIN：同表内的关联

SELF JOIN是将一张表与其自身进行JOIN，需要为两个副本分别指定别名，避免列名歧义。典型用途是查询层级结构，例如员工表中查询每位员工及其直属上级的姓名：

```sql
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;
```

使用LEFT JOIN（而非INNER JOIN）的原因在于：最高层级的CEO没有上级（`manager_id`为NULL），若使用INNER JOIN则CEO记录会被过滤掉，导致组织层级数据不完整。

在推荐系统中，SELF JOIN可用于计算用户对之间的共同点击商品数，进而构建用户相似度矩阵：

```sql
SELECT a.user_id AS user_a, b.user_id AS user_b,
       COUNT(*) AS common_items
FROM click_log a
INNER JOIN click_log b ON a.item_id = b.item_id
WHERE a.user_id < b.user_id  -- 避免重复对称计算
GROUP BY a.user_id, b.user_id;
```

此查询是基于物品的协同过滤（Item-based CF）的基础数据准备操作。注意`a.