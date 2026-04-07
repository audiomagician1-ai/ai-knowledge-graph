---
id: "design-notification-system"
concept: "设计通知系统"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 5
is_milestone: false
tags: ["notification", "push", "priority-queue"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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


# 设计通知系统

## 概述

通知系统（Notification System）是一种将事件触发的消息按需投递给目标用户的基础设施，核心职责是在正确的时间、通过正确的渠道，将正确的消息送达正确的接收方。区别于普通消息队列，通知系统需要额外处理用户偏好路由、多渠道降级、限频（Rate Limiting）等业务语义，其复杂性来自于"送达保证"与"用户体验不打扰"之间的持续张力。

通知系统的大规模工程化实践成型于2010年代智能手机普及时期。Apple于2009年推出APNs（Apple Push Notification service），Google随后在2010年推出C2DM（后演化为FCM/Firebase Cloud Messaging），这两项基础设施确立了移动推送的行业架构范式：设备注册Token → 服务端持有Token → 通过第三方网关投递。时至今日，一个成熟的通知系统需要同时对接APNs、FCM、短信SMS网关、电子邮件SMTP/API服务（如SendGrid、SES）以及站内信（In-App）渠道。

通知系统设计的难度主要体现在三个维度：第一，Pinterest级别的系统需要每天处理超过100亿条通知；第二，不同渠道的延迟SLA差异极大（推送通常要求P99在3秒内，而批量营销邮件可以接受分钟级延迟）；第三，系统需要在消息丢失（漏送）与重复投递之间做精细的一致性权衡。

---

## 核心原理

### 1. 推送通道选择与多路由架构

通知系统的第一层决策是**渠道路由（Channel Routing）**。系统在接收到通知请求时，必须查询用户设备信息表和偏好配置，决定通过哪个（或哪几个）渠道发送。标准路由优先级通常为：App推送（APNs/FCM）→ SMS → Email → In-App消息。

多渠道降级（Fallback）是实现高送达率的关键机制。例如，当APNs返回`BadDeviceToken`错误（Token失效）时，系统应自动标记该Token为无效并尝试SMS渠道。Uber的通知系统文档显示，其降级机制可将整体送达率从单渠道的82%提升至96%以上。每条通知的渠道路由结果需要记录，用于后续的送达率分析和用户触达行为建模。

渠道选择还需考虑**成本差异**：SMS单条成本约为推送通知的50-100倍，因此系统必须设置明确的降级触发条件，而非无差别地向所有渠道广播。

### 2. 优先级队列设计

通知系统必须区分至少三个优先级层次，并为每个优先级维护独立的消息队列（通常基于Kafka或RabbitMQ实现）：

- **P0（Critical）**：账户安全告警、交易验证码，要求秒级送达，队列单独部署，消费者独占资源，不与其他流量共享线程池。
- **P1（Transactional）**：订单确认、行程开始通知，允许10秒级延迟。
- **P2（Marketing/Batch）**：促销活动推送、周报摘要，允许分钟级至小时级延迟。

优先级队列的反饥饿（Anti-Starvation）机制同样重要：当P2队列积压超过阈值（如100万条）时，系统需触发限流而非无限堆积，否则会导致营销通知在活动结束后才送达，造成负面用户体验。Kafka的`max.poll.interval.ms`和`fetch.max.bytes`参数在此处需要针对P0和P2分别调优——P0消费者应设置极小的batch size以降低端到端延迟。

### 3. 延迟投递与批量投递

**延迟投递（Delayed Delivery）** 通常通过两种方案实现：
1. **定时任务扫描**：将定时通知存储在DB中，用Cron Job或调度框架（如Quartz、Celery Beat）定期扫描待发队列。适合精度要求≥1分钟的场景。
2. **延迟消息队列**：RabbitMQ的`x-message-ttl`配置或RocketMQ原生支持的18个固定延迟级别（1s/5s/10s/.../2h），可实现秒级精度的延迟投递。

**批量投递（Batch Delivery）** 的核心是将短时间内触发的同类通知合并为单条推送，以减少对用户的打扰并节省渠道成本。典型实现是使用时间窗口聚合：在5分钟内累积同一用户的多条"点赞"通知，合并为"张三等5人赞了你的帖子"后一次性投递。聚合逻辑需要维护一个以`(user_id, notification_type)`为键的临时缓冲区（通常存在Redis中，设置TTL为窗口时长）。

### 4. 限频与用户安静时段

通知系统必须实现**限频器（Rate Limiter）**，防止同一用户在短时间内收到大量通知。常见策略是滑动窗口计数：单个用户在任意1小时内收到的推送不超过5条，在任意24小时内不超过10条。超出限额的通知应入站内信队列而非直接丢弃。

安静时段（Quiet Hours）需要按用户时区处理：系统存储用户的`timezone`字段，在本地时间22:00至8:00期间，将P2级通知暂存并在第二天8:00批量投递。这要求调度模块在投递前实时计算目标用户的本地时间，而非依赖服务器时区。

---

## 实际应用

**Facebook通知系统**采用三层架构：前端事件收集层 → 通知聚合服务（处理合并逻辑）→ 渠道投递层。其"通知摘要"（Notification Digest）功能每天将数十亿条原始事件压缩为数亿条聚合通知，聚合率约达90%，显著降低了用户通知疲劳（Notification Fatigue）。

**电商大促场景**（如双11）面临通知洪峰问题：系统在活动开始前需提前将营销通知入队，通过令牌桶（Token Bucket）算法控制出队速率，避免APNs/FCM网关因瞬时请求量过大返回`TooManyRequests`错误（FCM的默认QPS上限为每个项目250万/分钟，超出后返回HTTP 429）。

**AI推荐型通知系统**在决策层引入ML模型：根据用户历史打开率、当前时段、设备活跃状态预测最佳发送时机（Send Time Optimization，STO），Netflix和LinkedIn均有此类系统的公开论文。预测结果会将通知的计划发送时间延迟0-24小时，与延迟投递模块直接集成。

---

## 常见误区

**误区一：将通知系统设计为同步调用链**。初学者常设计成"业务逻辑 → 同步调用APNs → 返回结果"的架构。此方案的致命缺陷是：当APNs出现网络抖动（平均每月发生数次）时，会直接阻塞业务主流程，导致P99延迟从毫秒级跳升至秒级。正确做法是业务层只负责将通知请求写入消息队列（写操作<10ms），由异步Worker池负责调用外部渠道网关。

**误区二：所有通知使用同一队列**。将P0安全验证码与P2营销邮件放入同一队列，会导致在营销大促期间P0通知因队列积压而延迟送达，直接影响用户账户安全体验。优先级隔离（队列物理分离 + 消费者资源隔离）是不可省略的设计要求，而非优化项。

**误区三：忽视幂等性设计**。消息队列的at-least-once投递语义会导致Worker重复消费同一条通知消息。若未在渠道调用前检查幂等键（通常是`notification_id`存入Redis，TTL设为24小时），用户将收到重复推送。APNs的`apns-collapse-id`头字段和FCM的`collapse_key`参数可在网关层实现消息折叠，但服务端的幂等控制仍是必需的第一道防线。

---

## 知识关联

通知系统的设计建立在**可扩展性**原则的直接应用之上：渠道投递层必须支持水平扩展，APNs连接池（每条TCP长连接可复用，但单连接并发请求数上限为1500）的管理是扩展时的关键瓶颈点，Worker节点数量扩容时需同步增加连接池容量。

**消息队列**是通知系统的核心基础设施：Kafka适合高吞吐的批量营销通知（可达百万级TPS），RabbitMQ的`x-delayed-message`插件更适合需要精确延迟的事务性通知。两者在通知系统中常共存，分别服务不同优先级的通知流。理解Kafka的`Consumer Group`与`Partition`分配机制，直接决定通知消费者集群能否均匀分摊负载，是通知系统调优的必备前置知识。