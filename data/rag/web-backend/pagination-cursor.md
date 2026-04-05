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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 游标分页

## 概述

游标分页（Cursor-based Pagination）是一种基于"位置标记"而非"行偏移量"来分割数据集的分页技术。不同于传统的 `LIMIT offset, count` SQL 语法，游标分页使用某个字段的具体值（通常是自增主键 ID 或时间戳）作为查询的起点，通过 `WHERE id > cursor_value LIMIT n` 的方式获取下一页数据，从根本上规避了偏移量扫描的性能问题。

该技术在 2010 年代随着社交媒体无限滚动（Infinite Scroll）场景的爆发而得到广泛应用。Twitter、Facebook 的公开 API 均采用此方案，Twitter API v2 使用 `next_token` 字段作为游标返回值。游标分页的核心优势在于：当数据集达到百万行规模时，Offset 分页的 `LIMIT 1000000, 20` 会触发全表扫描并丢弃前 100 万行，而游标分页只需从索引直接定位到游标位置，时间复杂度从 O(offset) 降至 O(log n)（B+树索引下）。

游标分页特别适用于实时数据流场景。当用户翻页期间有新数据插入时，Offset 分页会导致同一条记录在第 N 页和第 N+1 页均出现（幽灵记录问题），而游标分页以具体值为锚点，彻底免疫插入和删除导致的数据偏移。

## 核心原理

### 游标的数学本质

游标本质上是一个**稳定的排序锚点**。设数据按字段 `id` 升序排列，第一页查询为：

```sql
SELECT * FROM posts ORDER BY id ASC LIMIT 20;
```

返回结果中最后一行的 `id` 值（设为 `last_id = 842`）即为游标。第二页查询变为：

```sql
SELECT * FROM posts WHERE id > 842 ORDER BY id ASC LIMIT 20;
```

这个不等式过滤配合 `id` 字段上的 B+树索引，数据库引擎可以通过索引范围扫描（Index Range Scan）直接跳转到 id=842 之后的叶节点，完全跳过前 842 行的读取。MySQL InnoDB 中主键索引即为聚簇索引，此查询的 IO 开销固定为常量级。

### 游标编码与传输格式

游标值通常不直接暴露原始字段值，而是通过 Base64 编码进行不透明封装（Opaque Cursor），原因有二：① 防止客户端对游标值进行算术操作（如手动构造 `cursor - 1` 来回翻页）；② 便于在不修改 API 接口的情况下更换内部游标字段。

例如，游标值 `{"id": 842, "created_at": "2024-01-15T10:30:00Z"}` 编码后返回为：
```
eyJpZCI6IDg0MiwgImNyZWF0ZWRfYXQiOiAiMjAyNC0wMS0xNVQxMDozMDowMFoifQ==
```

GraphQL 规范中的 Relay Cursor Connection 规范（2015 年发布）将此格式标准化，定义了 `edges`、`node`、`cursor`、`pageInfo` 四个字段的固定结构，`pageInfo` 中包含 `hasNextPage`、`hasPreviousPage`、`startCursor`、`endCursor` 四个元数据字段。

### 复合游标处理非唯一排序字段

当排序字段为非唯一值（如 `likes_count`）时，单字段游标会产生歧义——多行具有相同 `likes_count=100` 时无法确定断点位置。解决方案是构造**复合游标**，以辅助唯一字段（通常是 `id`）消除歧义：

```sql
SELECT * FROM posts
WHERE (likes_count < 100) 
   OR (likes_count = 100 AND id < 8421)
ORDER BY likes_count DESC, id DESC
LIMIT 20;
```

此 SQL 中的 `(likes_count, id)` 联合索引需要预先创建，且字段顺序必须与 `ORDER BY` 一致，否则查询优化器无法使用索引。这是使用复合排序时游标分页实现中最容易出错的环节。

## 实际应用

**场景一：AI 模型训练日志 API**
AI 训练平台通常需要实时展示亿级训练日志。使用游标分页，以 `log_id`（自增 BIGINT）为游标，每页返回 100 条，服务端响应时间稳定在 5-10ms。相比之下，若使用 Offset 分页查询第 10 万页（`LIMIT 10000000, 100`），MySQL 在无缓存情况下响应时间可超过 30 秒。

**场景二：用户动态时间线**
Twitter-like 应用中，首次加载调用 `GET /timeline?limit=20`，响应体包含 `next_cursor: "eyJpZCI6IDM4OTJ9"`。用户下滑触发 `GET /timeline?after=eyJpZCI6IDM4OTJ9&limit=20`。因为锚点是具体 ID 值，在用户查看期间新发布的帖子不会导致已看内容重复出现。

**场景三：向量数据库检索结果分页**
Pinecone、Weaviate 等向量数据库的 REST API 均采用游标分页，以保证大规模语义搜索结果在多次请求间的一致性。Weaviate 的 `after` 参数即为游标分页实现，要求配合 `sort` 字段使用。

## 常见误区

**误区一：认为游标分页支持随机跳页**
游标分页天然不支持"跳转到第 50 页"这类操作，因为获取第 50 页的游标必须先获取前 49 页的最后一条记录。若业务需求包含页码跳转（如搜索引擎结果页），应混合使用 Offset 分页（限制最多跳转到第 100 页）或预计算页码表。盲目将所有分页场景替换为游标分页是错误的架构决策。

**误区二：游标值可以用时间戳代替 ID**
使用 `created_at` 时间戳作为游标字段在高并发写入场景下存在精度问题：同一毫秒内插入的多条记录具有相同时间戳，导致游标定位歧义，可能丢失最多 `qps × 1ms` 条记录。正确做法是以数据库自增 ID 为主游标，时间戳仅作为复合游标的辅助字段。

**误区三：游标在所有数据库中性能表现一致**
游标分页的性能优势依赖于游标字段上存在索引。若开发者在 `created_at` 字段上建游标但忘记创建索引，查询将退化为全表扫描，性能甚至差于 Offset 分页（因为多了一个 `WHERE` 过滤运算）。在 PostgreSQL 中可通过 `EXPLAIN ANALYZE` 确认查询使用了 `Index Scan` 而非 `Seq Scan`。

## 知识关联

游标分页的性能优势完全依赖**索引原理与优化**中 B+树索引的范围扫描特性：游标的 `WHERE id > value` 正是利用 B+树叶节点的有序链表结构做 O(log n) 定位，若索引概念不清晰，无法理解为何游标分页在第 100 万页仍保持稳定的响应时间。

在 **RESTful API 设计**层面，游标分页改变了分页参数的语义：传统 `?page=3&size=20` 参数体系需替换为 `?after=<cursor>&limit=20`，响应体中的 `Link` Header（RFC 5988 定义）也需要携带 `next` 和 `prev` 关系链接。游标应通过 Base64 编码封装为不透明字符串，以符合 RESTful API 中"接口稳定性"的设计原则，避免客户端对游标内部结构产生依赖。