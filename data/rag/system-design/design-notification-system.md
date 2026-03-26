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
quality_tier: "B"
quality_score: 47.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.387
last_scored: "2026-03-22"
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

通知系统（Notification System）是指将特定事件触发的消息，通过一个或多个推送通道（Push Channel）可靠地投递给目标用户的分布式服务。与普通 API 调用不同，通知系统需要处理异步投递、多渠道适配、用户偏好路由以及大规模并发推送三类核心挑战，同时还必须保证"至少一次（At-Least-Once）"或"恰好一次（Exactly-Once）"的投递语义。

通知系统的设计范式在 2010 年代随着移动互联网爆发而成熟。Apple 于 2009 年推出 APNs（Apple Push Notification Service），Google 随后推出 GCM（现 Firebase Cloud Messaging，FCM），这两套协议确立了移动推送的行业标准：服务端不直接与设备建立长连接，而是通过第三方推送网关转发消息，从而将设备连接管理责任从业务服务器剥离。

在 AI 工程系统中，通知系统承担的角色更为关键：模型训练完成提醒、数据管道告警、A/B 实验结果播报等场景对通知的时效性和准确性有严格要求。设计不当会导致告警风暴（Alert Storm）——某次生产事故中，一个循环依赖导致 10 分钟内产生 200 万条重复告警，直接压垮下游通知服务。

---

## 核心原理

### 推送通道选择与分层路由

通知系统通常支持四类推送通道，各有不同的延迟与可靠性特征：

| 通道 | 典型延迟 | 打开率 | 适用场景 |
|------|----------|--------|----------|
| 短信（SMS） | 1–5 秒 | ~98% | 验证码、紧急告警 |
| 移动推送（APNs/FCM） | 1–10 秒 | 5–15% | 营销通知、事务提醒 |
| 邮件（SMTP/SES） | 1–60 秒 | 20–30% | 账单、详细报告 |
| 站内信（In-App） | <500 ms | 取决于用户在线 | 实时协作、交互提示 |

路由决策层需读取用户偏好表（User Preference Store），按优先级降级（Fallback）：若用户关闭移动推送，则自动降级到邮件。典型实现是一张 `channel_preference` 表，字段包括 `user_id`、`channel_type`、`enabled`、`quiet_hours_start/end`（勿扰时段），每次路由前查询该表并缓存到 Redis（TTL 建议 300 秒）以避免频繁数据库访问。

### 优先级队列与多级 QoS

单一 FIFO 队列无法满足通知系统的差异化时效要求。标准做法是将消息分为三个优先级桶：

- **Critical（P0）**：安全验证码、支付确认，目标投递延迟 < 3 秒，使用独立队列且不受流量限制
- **High（P1）**：订单状态变更、AI 模型告警，目标投递延迟 < 30 秒
- **Normal（P2）**：营销推送、每日摘要，可接受分钟级延迟

Kafka 实现时，P0/P1/P2 分别对应三个独立 Topic，消费者线程池按 `8:4:1` 比例分配（即 P0 有 8 个消费线程、P1 有 4 个、P2 有 1 个）。这样即使 P2 队列积压 100 万条，P0 消息仍能在毫秒级完成消费。RabbitMQ 的 `x-max-priority` 插件也支持单队列内 0–255 级优先级，但高并发场景下多 Topic 方案的吞吐性能更优。

### 延迟投递与批量投递

**延迟投递（Delayed Delivery）** 用于处理两类需求：（1）用户设置的勿扰时段，将通知推迟到 08:00 投递；（2）定时提醒，如"会议开始前 15 分钟通知"。实现方案有两种：
- **时间轮（Timing Wheel）**：Kafka 自带的延迟消息不原生支持任意时间，常见做法是在消息体中附带 `deliver_at` 时间戳，由一个 Scheduler 服务每秒扫描 Redis 的 Sorted Set（以 `deliver_at` 为 score），到期消息重新入队。这一方案支持任意延迟精度，典型误差 < 1 秒。
- **RocketMQ 延迟级别**：内置支持 18 个固定延迟级别（1s/5s/10s/.../2h），适合延迟精度要求不高的场景。

**批量投递（Batch Delivery）** 将同一用户在时间窗口内（如 5 分钟）产生的多条同类通知合并为一条摘要推送，公式为：

```
合并阈值 = max(batch_size, time_window)
```

即满足 `batch_size`（如 10 条）或超过 `time_window`（如 300 秒）时触发投递，两个条件满足其一即可。批量投递可将移动推送量降低 60–80%，显著减少用户打扰并节省 APNs/FCM API 调用费用。

### 幂等性与投递保证

通知系统必须为每条通知分配全局唯一 `notification_id`（建议使用 Snowflake 算法生成 64 位 ID）。投递服务在调用 APNs/FCM 前，先向 Redis 写入 `SET notification:{id}:status "processing" NX EX 300`，若写入失败说明已有消费者在处理，直接跳过，防止同一消息被重复推送给用户。投递结果（成功/失败/设备 Token 失效）异步回写到 `notification_log` 表，供后续重试和报表统计使用。

---

## 实际应用

**AI 训练平台通知**：用户提交的 GPU 训练任务完成后，系统需将训练结果（精度、损失曲线链接）通过邮件发送给用户。由于训练任务可能在深夜完成，通知服务读取用户时区信息，将邮件延迟到用户当地 08:00–22:00 时间段内投递，避免夜间打扰。若用户同时开启移动推送，则移动端走 P1 队列立即推送，邮件走 P2 队列等待合适时机。

**电商大促告警**：双 11 期间，库存预警通知量可达平时 50 倍。通知服务通过水平扩展消费者实例（Kubernetes HPA，目标 CPU 利用率 70%）应对峰值，同时对 P2 营销通知启用批量合并，将"商品降价提醒"汇总为每小时一封摘要邮件，将 SMTP 发送量从 800 万次/小时压缩至 30 万次/小时。

**实时协作工具**：Slack 类系统中，当用户被 @mention 时走 P0 通道（站内信 + 移动推送并行），普通频道消息走 P2 批量站内信。FCM 的 `collapse_key` 特性可将同一会话的多条未读通知合并为一条，避免用户手机锁屏通知栏被刷满。

---

## 常见误区

**误区一：所有通知走同一个消息队列**
很多初级设计将所有通知类型混入同一 Kafka Topic，导致营销邮件积压时，支付验证码也被延迟投递。正确做法是按优先级隔离 Topic，P0 消息的消费者线程池必须与 P1/P2 完全隔离，共享线程池会引入排队等待时间，打破 3 秒内投递的 SLA。

**误区二：直接在业务服务中调用 APNs/FCM API**
在 HTTP 请求处理链路内同步调用第三方推送 API，会导致 APNs 超时（通常 10–30 秒）直接影响用户请求响应时间。正确做法是业务服务只负责将通知事件写入消息队列（写入延迟 < 5 ms），由独立的 Notification Worker 异步消费并调用推送网关。

**误区三：忽略 Token 失效导致的静默失败**
APNs 对失效 Device Token 返回 `410 Gone` 状态码，FCM 返回 `registration_not_registered`。若不处理这两个错误码，系统会持续向无效 Token 发送请求，浪费配额并掩盖真实投递成功率。必须在收到这些错误后立即将对应 Token 标记为失效并停止推送。

---

## 知识关联

通知系统依赖**消息队列**作为异步解耦的基础设施——Kafka 的分区机制为优先级队列的隔离提供了物理保障，RabbitMQ 的 Dead Letter Queue（DLQ）为失败重试提供了标准模式。没有消息队列，通知服务与业务服务之间的强依赖会使系统在推送峰值时整体崩溃。

**可扩展性**原则直接体现在通知系统的水平扩展策略中：Notification Worker 是无状态服务，可通过增加实例数线性提升吞吐量；但 Scheduler 服务（扫描延迟队列）是有状态的，需要通过分布式锁（Redlock 算法）保证同一时刻只有一个实例执行扫描，防止重复触发延迟消息，这是通知系统中可扩展性与一致性之间最典