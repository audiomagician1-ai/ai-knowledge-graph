---
id: "rate-limiting"
concept: "限流策略"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 5
is_milestone: false
tags: ["安全"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 限流策略

## 概述

限流策略（Rate Limiting Strategy）是指在Web后端服务中，通过算法控制客户端或用户在单位时间内能够发出的请求数量上限，防止服务因流量过载而崩溃。限流的本质是在系统的吞吐量与可用性之间建立一道可控的"水闸"，当请求速率超过预设阈值时，系统以HTTP 429（Too Many Requests）状态码拒绝多余请求，而非让所有请求竞争有限资源。

限流概念最早在电信网络的流量整形（Traffic Shaping）领域得到系统化研究，1990年代随互联网兴起后被引入HTTP服务。Twitter在2006年对外开放API时率先发布了业界广泛引用的限流规范——每小时150次免费请求，超额后返回403错误（后改为429），奠定了现代REST API限流的惯例。

在AI工程的Web后端场景中，限流策略尤为关键：大语言模型推理接口的单次调用成本远高于普通查询，OpenAI的GPT-4 API明确对RPM（每分钟请求数）和TPM（每分钟Token数）双维度限流。若不实施限流，一个被滥用或遭受DDoS攻击的AI服务在数分钟内就能耗尽GPU算力配额，造成不可逆的成本损失。

---

## 核心原理

### 令牌桶算法（Token Bucket）

令牌桶是目前最主流的限流算法之一，其模型如下：系统维护一个容量为 **B**（burst size）的桶，以固定速率 **r**（tokens/second）向桶中填充令牌；每次请求到来时消耗1个（或N个）令牌，桶空则拒绝请求。

核心公式：`available_tokens = min(B, last_tokens + r × (current_time - last_time))`

令牌桶允许短时间内的突发流量——只要桶中积累了足够令牌，客户端可以瞬间发出多达B个请求。AWS API Gateway的突发限制（Burst Limit）正是基于令牌桶，默认突发容量为5000个令牌，稳定速率为每秒10000个请求。

### 漏桶算法（Leaky Bucket）

漏桶与令牌桶方向相反：请求进入一个固定容量的队列（桶），系统以恒定速率 **r** 处理（漏出）队列中的请求。若队列满则新请求被丢弃。

漏桶的特性是**强制平滑输出**，无论入流量多么突发，出流量始终保持 r 请求/秒的恒定节奏。这适合需要保护下游脆弱服务的场景，例如调用第三方API时控制自身的请求节奏，防止触发对方的限流阈值。代价是对合法的突发请求增加了排队延迟。

### 固定窗口与滑动窗口计数器

**固定窗口**（Fixed Window）将时间轴切分为等长区间（如每分钟一个窗口），在窗口内用Redis的`INCR`+`EXPIRE`命令原子计数。最大缺陷是"临界问题"：若窗口边界恰在0:00:59~0:01:01之间，客户端可在2秒内发出2倍配额的请求。

**滑动窗口日志**（Sliding Window Log）用有序集合存储每次请求的时间戳，统计当前时刻往前T秒内的请求数，精度最高但内存占用正比于请求量。

**滑动窗口计数器**（Sliding Window Counter）是折中方案，公式为：
`estimated_count = prev_window_count × (1 - elapsed/window_size) + curr_window_count`

此公式利用上一窗口的计数按时间比例加权，在误差小于0.003%的情况下将内存复杂度从O(N)降至O(1)，被Cloudflare用于其全球限流系统。

### 分布式限流的一致性问题

单机限流使用本地内存计数即可，但分布式系统中多个节点各自计数会导致全局配额被超发。解决方案分为两类：

1. **中心化计数**：所有节点将请求计数写入Redis，使用`SETNX`或Lua脚本保证原子性，延迟约0.5~2ms，适合高精度场景。
2. **本地+同步**：每个节点分配子配额，周期性同步到中心存储，牺牲少量精度换取低延迟，适合超大规模场景（如字节跳动的分布式限流框架ByteGuard采用此思路）。

---

## 实际应用

**AI推理API网关**：在FastAPI或Nginx前端对`/v1/chat/completions`路由部署双维度限流——RPM用令牌桶控制突发，TPM用固定窗口每分钟统计消耗的token数。当TPM超限时返回429并在响应头写入`Retry-After: 60`，客户端根据此字段实现指数退避重试。

**用户分级配额**：结合JWT中的`plan`字段实现差异化限流。免费用户：20 RPM；Pro用户：500 RPM；企业用户：自定义。Redis Key格式设计为`rate_limit:{plan}:{user_id}:{window_timestamp}`，通过Lua脚本原子执行"检查+递增+设置过期"三步操作，避免竞态条件。

**IP维度的暴力破解防护**：对`/auth/login`接口设置独立的IP级限流：10分钟内最多尝试5次，失败超限后封禁IP 30分钟，并写入慢日志供安全审计。这与JWT认证形成联动——通过JWT已验证身份的正常请求走用户级配额，未携带有效JWT的请求走IP级配额。

---

## 常见误区

**误区1：限流阈值越严格越安全**
将阈值设得过低会误杀合法的高频用户，例如爬虫型合法客户或批量处理任务。正确做法是先通过P99延迟和错误率监控采集真实流量分布，再基于系统实测吞吐量上限（如压测确定的QPS峰值）设置阈值，通常留20%~30%余量而非直接卡死在峰值。

**误区2：限流完全等同于防DDoS**
限流控制的是请求速率，它无法阻挡分布式攻击中数千个低频IP的协同攻击（每个IP都在阈值内）。真正的DDoS防护需要结合流量清洗、IP信誉库、以及L3/L4层的网络过滤，限流只是应用层防护链的最后一环。

**误区3：用固定窗口计数实现毫秒级精度限流**
固定窗口在窗口边界处存在双倍突发漏洞，不适合对金融交易、AI算力计费等敏感场景进行精确控制。这些场景应使用滑动窗口日志或令牌桶，并通过Redis Lua脚本保证原子性，而非用Python层面的`if count > limit: reject`逻辑（存在TOCTOU竞态）。

---

## 知识关联

**与API认证（JWT/OAuth）的关联**：限流策略的执行通常依赖JWT中的`sub`（用户ID）或`plan`（订阅等级）字段来区分配额维度。在中间件管道中，认证中间件先验证JWT有效性，后续限流中间件再读取Payload中的用户标识进行配额匹配——两者是串行依赖关系，认证失败的请求甚至不应消耗限流计数。

**通向设计限流器**：掌握上述四种算法的原理后，"设计限流器"课题进一步要求将策略工程化：如何设计Redis数据结构支持水平扩展、如何在API响应头中标准化返回`X-RateLimit-Limit`、`X-RateLimit-Remaining`、`X-RateLimit-Reset`三个字段、以及如何通过配置中心动态调整阈值而无需重启服务。限流策略是这些设计决策的理论前提。