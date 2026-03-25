---
id: "pagination-cursor"
concept: "游标分页"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 3
is_milestone: false
tags: ["cursor", "pagination", "offset"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 游标分页

## 概述

游标分页（Cursor-based Pagination）是一种基于"书签"位置进行数据集分割的API分页技术。与传统的 `LIMIT offset, count` 不同，游标分页通过将某一行的唯一标识（通常是自增主键ID或时间戳）编码为不透明的游标字符串，每次请求时告诉数据库"从这条记录之后开始取N条"，从而避免数据库在深翻页时扫描大量无用行。

这一模式由Facebook Graph API在2010年前后推广，Twitter的Timeline API、GitHub的REST API（v3）和Stripe的API均采用此设计。其根本动机在于解决海量数据下分页性能崩溃的问题：当一个用户表已有1000万行时，`OFFSET 9999000 LIMIT 10` 会迫使数据库引擎跳过999.9万行数据，而游标分页通过索引范围扫描将这个操作降为 O(log n) 的索引查找。

游标分页对AI工程后端尤为重要，因为训练数据集导出、推理日志检索、向量数据库结果流式返回等场景都涉及对千万级数据的高效遍历，一旦使用Offset分页，接口响应时间会随翻页深度线性恶化，在深翻页时甚至达到秒级超时。

---

## 核心原理

### Offset分页的性能缺陷

传统Offset分页的SQL形式为：

```sql
SELECT * FROM logs ORDER BY id LIMIT 10 OFFSET 50000;
```

即使 `id` 列有B+树索引，MySQL/PostgreSQL仍需**读取并丢弃**前50000行，因为 `OFFSET` 是在索引定位后按顺序跳过的，无法直接跳转。实测在PostgreSQL 14中，对1000万行的表执行 `OFFSET 5000000` 耗时约2.3秒，而同等数据量的游标查询仅需约4毫秒——性能差距达500倍量级。此外，Offset分页存在**幻读问题**：若在第一页和第二页之间有新数据插入，第二页请求会漏掉或重复返回边界数据。

### 游标的构造与编码

游标本质是一个稳定的排序锚点。假设按 `created_at`（时间戳）升序分页，当前页最后一条记录的 `created_at = 2024-03-15T10:23:45Z`，`id = 8821`，则游标可以编码为：

```
cursor = Base64( "created_at:2024-03-15T10:23:45Z,id:8821" )
       = "Y3JlYXRlZF9hdDoyMDI0LTA..."
```

对客户端而言，游标是不透明的字符串，不暴露内部结构。服务端解码后，下一页查询变为：

```sql
SELECT * FROM events
WHERE (created_at, id) > ('2024-03-15T10:23:45Z', 8821)
ORDER BY created_at ASC, id ASC
LIMIT 10;
```

这个**行值比较**（Row Value Comparison）直接利用复合索引 `(created_at, id)` 做范围扫描，索引定位精确，无需跳过任何行。PostgreSQL自9.0版本起、MySQL自5.7.3起均原生支持行值比较语法。

### 双向游标与API设计规范

完整的游标分页响应体应同时返回 `next_cursor` 和 `prev_cursor`，以支持前向和后向翻页。GitHub API的实际响应头格式如下：

```
Link: <https://api.github.com/repos/owner/repo/issues?cursor=abc123&per_page=30>; rel="next",
      <https://api.github.com/repos/owner/repo/issues?cursor=xyz789&per_page=30>; rel="prev"
```

计算 `prev_cursor` 时，需将排序方向取反：若正向是 `(created_at, id) > (anchor_time, anchor_id)`，则反向是 `(created_at, id) < (first_record_time, first_record_id) ORDER BY created_at DESC`，取结果后再在应用层翻转顺序。

---

## 实际应用

**场景一：AI推理日志导出**
一个在线推理服务每天产生约800万条推理日志，运营人员需要将过去30天日志导出到数据湖。若用Offset分页，第2400万条之后的请求平均耗时超过8秒。改用游标分页后，每页10000条的导出脚本维持恒定的约120ms响应，整批导出总时长从3.5小时降至约11分钟。

**场景二：向量数据库结果分页**
Pinecone、Weaviate等向量数据库的官方SDK均使用游标分页返回相似度搜索结果。Weaviate的GraphQL接口中，`after` 参数就是游标ID，内部实现为对HNSW索引节点ID的范围迭代，不支持任意跳页正是其文档明确说明的设计取舍。

**场景三：Stripe账单系统**
Stripe API每个列表接口（如 `/v1/charges`）都使用 `starting_after={charge_id}` 作为游标，`charge_id` 本身即为自增有序ID（如 `ch_3Oab...`），无需额外编码，直接作为 `WHERE id > 'ch_3Oab...' LIMIT 10` 的条件。

---

## 常见误区

**误区一：游标分页可以实现任意跳页**
游标分页天然不支持"跳到第50页"这类随机访问。游标是线性书签，只能基于上一页的终点定位下一页起点。若业务确实需要"第N页"跳转功能（如搜索结果展示），必须保留Offset分页，或改用Elasticsearch的 `search_after` + `pit`（Point In Time）机制，两者在架构上是互斥取舍，而非游标分页的缺失功能。

**误区二：任何列都可以作为游标字段**
游标字段必须满足两个条件：**唯一性**（或与其他字段组合唯一）和**单调有序性**。使用 `status`（如 `pending/completed`）或 `score`（浮点数，可能重复）作为单一游标字段，会导致边界记录被跳过或重复返回。正确做法是将主键 `id` 作为后备排序键构成复合游标，即 `(sort_field, id)` 的组合，以保证全局唯一定位。

**误区三：游标字符串是安全的访问控制机制**
Base64编码的游标不是加密，仅是混淆。恶意用户可以解码游标、伪造任意位置的游标来探测数据。若需访问控制，必须在服务端验证游标指向的记录对该用户可见，游标本身不提供任何安全保障。

---

## 知识关联

游标分页建立在**索引原理**的基础上：复合索引 `(sort_key, id)` 是游标查询性能保障的直接依赖，若该索引缺失，游标查询会退化为全表扫描，性能反而可能不如小数据量下的Offset查询。在设计游标时需要确认查询的 `WHERE` 条件与 `ORDER BY` 字段完全匹配已有索引的前缀顺序。

从**RESTful API设计**角度，游标分页改变了分页参数的语义：`page=3` 这类绝对位置参数被 `cursor=<opaque_string>` 替代，API的幂等性增强（同一游标永远返回同一批数据），但可书签性（bookmarkability）依赖游标字符串的持久有效期，后端需要明确约定游标的过期策略（Stripe的游标不过期，而部分Elasticsearch PIT默认1分钟过期），这一策略应写入API文档作为合约。
