---
id: "idempotency"
concept: "幂等性设计"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 4
is_milestone: false
tags: ["idempotent", "retry", "api-design"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 幂等性设计

## 概述

幂等性（Idempotency）源自数学概念：若操作 f 满足 f(f(x)) = f(x)，则称 f 具有幂等性。在系统设计中，幂等性指一个操作无论执行一次还是多次，产生的副作用（side effect）完全相同。注意这里强调的是"副作用"而非"返回值"——第二次调用 `DELETE /orders/123` 可能返回 404，但系统状态（订单已删除）与第一次成功后完全一致，因此该操作依然幂等。

幂等性设计的需求源于分布式系统中的"网络不可靠"现实。在 HTTP/1.1 规范（RFC 7231，2014年发布）中明确规定 GET、PUT、DELETE、HEAD 方法必须是幂等的，而 POST 和 PATCH 默认不幂等。然而规范只定义了语义要求，实际工程中 POST 用于创建资源、触发支付等场景时，必须通过额外机制强制保证幂等性。

幂等性设计在 AI 工程中尤为关键。AI 推理服务的单次调用成本高（调用 GPT-4 API 每千 token 约 $0.03），网络超时后客户端重试若缺乏幂等保护，会导致重复计费、重复写入训练日志、重复触发下游 webhook，在高并发场景下这些问题会被放大数十倍。

## 核心原理

### 幂等键（Idempotency Key）机制

幂等键是客户端生成的全局唯一标识符，随请求一同发送，服务端用它来识别重复请求。Stripe 支付 API 是该模式的经典实现：客户端在 HTTP Header 中携带 `Idempotency-Key: <UUID>`，服务端以该键为索引，在数据库中存储请求的处理结果，TTL 通常设为 24 小时。若在 TTL 内收到相同幂等键的请求，直接返回缓存结果，不重新执行业务逻辑。

幂等键的生成规则至关重要：必须由**客户端**生成（不能由服务端分配），推荐使用 UUID v4（128位随机数，碰撞概率约为 1/2^122），或对"业务语义 + 时间窗口"做哈希，如 `SHA256(user_id + order_items + date)`。将幂等键与请求体绑定校验也是最佳实践——若相同幂等键携带不同请求体，应返回 422 Unprocessable Entity 而非静默复用旧结果。

### 数据库层面的幂等保障

数据库唯一约束是实现幂等性的最可靠手段之一。在订单创建场景中，对 `(user_id, idempotency_key)` 建立唯一索引，当并发两个相同幂等键的请求同时到达时（网络重试常见场景），数据库唯一约束会让其中一个事务抛出 `Duplicate Key Error`，应用层捕获该错误后查询已有记录并返回，整个过程无需分布式锁。

"先查后写"（Check-then-Act）模式在并发下是**非幂等**的典型陷阱：`SELECT COUNT(*) ... WHERE key=?` 后再 `INSERT` 存在 TOCTOU（Time-of-Check-Time-of-Use）竞态条件。正确做法是使用 `INSERT ... ON DUPLICATE KEY UPDATE`（MySQL）或 `INSERT ... ON CONFLICT DO NOTHING`（PostgreSQL）这类原子操作，将"查重+写入"合并为单条 SQL 语句。

### 状态机与幂等操作设计

将资源状态设计为有限状态机（FSM），可以从架构层面保证操作幂等。以 AI 任务调度服务为例，任务状态定义为：`PENDING → RUNNING → COMPLETED / FAILED`。"启动任务"操作的幂等实现是：仅在状态为 PENDING 时执行转换，若状态已为 RUNNING 或 COMPLETED，直接返回当前状态而不报错。这要求数据库更新语句携带状态前置条件：`UPDATE tasks SET status='RUNNING' WHERE id=? AND status='PENDING'`，通过检查受影响行数（affected rows）判断是否为重复操作。

HTTP 方法的幂等语义需要在 PUT 与 PATCH 中特别区分：PUT 要求客户端发送完整资源表示（全量更新），天然幂等；PATCH 若使用相对操作（如 `{"op": "increment", "path": "/count", "value": 1}`）则**不幂等**，若使用绝对赋值（如 `{"count": 5}`）则幂等。AI 工程中配置更新 API 应优先使用绝对赋值的 PATCH 或 PUT，避免重试导致数值类字段被多次累加。

## 实际应用

**AI 推理服务的去重防护**：调用大模型 API 时，客户端应为每个用户请求生成幂等键（如 `SHA256(session_id + user_message + model_version)`），存入 Redis 并设置过期时间 30 秒。若同一用户在 30 秒内因网络问题重复提交，直接从 Redis 返回第一次的推理结果，避免对 OpenAI/Anthropic API 的重复计费，同时确保用户看到的回复一致。

**数据流水线的幂等写入**：在 ETL 或特征工程管道中，使用"upsert"模式替代"insert"：以特征向量的内容哈希作为主键，`INSERT INTO feature_store ... ON CONFLICT (content_hash) DO UPDATE SET updated_at = NOW()`。即使管道因故障重跑，特征数据不会重复写入，但 `updated_at` 时间戳会更新，方便监控。

**支付与积分发放**：电商 AI 推荐系统完成下单后触发积分发放 API，需携带 `order_id` 作为幂等键。积分服务维护 `awarded_orders` 表，`INSERT INTO awarded_orders (order_id, points) VALUES (?, ?) ON CONFLICT (order_id) DO NOTHING`，确保同一订单无论因网络重试触发多少次，积分只发放一次。

## 常见误区

**误区一：认为 GET 请求天然幂等就无需关注**。GET 请求的幂等性指不产生副作用，但实际工程中有些 `GET /generate-report` 接口实际上触发了异步任务创建——这类接口的 HTTP 语义与行为不符。正确做法是将其改为 POST，并显式通过幂等键保护，而非依赖 GET 的"假幂等"。

**误区二：将幂等性与无状态混淆**。幂等性关注"多次操作结果一致"，而无状态（Stateless）关注"服务器不保存客户端会话状态"。实现幂等键机制**必须**在服务端存储已处理请求的记录（有状态），这与 RESTful 的无状态约束存在张力，需要将幂等键存储视为"基础设施状态"而非"会话状态"来理解和解释。

**误区三：认为幂等键 TTL 越长越好**。24 小时是 Stripe 的工程权衡结果：既覆盖绝大多数网络重试窗口（99.9% 的重试在 1 小时内完成），又控制了存储成本。TTL 设为永久会导致幂等键表无限增长；TTL 设为 1 分钟则无法覆盖跨越维护窗口的重试场景。AI 工程中应根据具体任务的 SLA 和重试策略（如指数退避最大等待时间）来设定 TTL。

## 知识关联

本概念建立在 **RESTful API 设计**基础上：RFC 7231 对 HTTP 方法幂等语义的定义是幂等性设计的规范依据，理解 PUT 与 POST 的语义差异是选择幂等实现策略的前提。幂等键的服务端存储结构（如 Redis Hash 或数据库唯一索引）直接关联到**分布式事务**中的"防重表"模式——分布式事务的最终一致性方案（如 TCC、Saga）在补偿操作中同样依赖幂等保证来防止重复补偿。具体地说，Saga 模式中每个参与者的正向操作和补偿操作都必须是幂等的，否则协调器在故障重启后重放事件日志时会导致状态不一致。掌握幂等性设计后，可以直接应用于构建可靠的 AI 服务网关、任务调度器和数据管道等生产级组件。
