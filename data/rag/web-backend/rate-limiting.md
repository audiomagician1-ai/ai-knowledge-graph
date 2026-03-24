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
---
# 限流策略

## 概述

限流策略（Rate Limiting Strategy）是Web后端系统中用于控制客户端在单位时间内发送请求数量的机制，目的是防止服务因流量过载而崩溃，保障后端资源的公平分配。当某个AI推理服务或普通API接口面临高并发请求时，限流策略决定哪些请求被正常处理、哪些被延迟、哪些被直接拒绝（通常返回HTTP 429 Too Many Requests状态码）。

限流策略的雏形出现在1990年代的网络路由领域，最初用于控制TCP/IP数据包的传输速率。2000年代随着RESTful API的普及，Twitter、GitHub等平台将其引入HTTP服务层。Twitter在2013年将其API限额明确设定为每15分钟窗口15次请求（v1.1接口），这一公开披露使限流策略作为API设计规范被广泛讨论和采用。

在AI工程场景中，限流策略尤为关键：大型语言模型的单次推理可能消耗数秒GPU计算时间，若不加限制，单一用户的批量请求可直接耗尽服务器资源，导致其他用户完全无法访问。OpenAI的GPT-4 API使用TPM（Tokens Per Minute）和RPM（Requests Per Minute）双维度限流，正是基于这一现实需求。

---

## 核心原理

### 令牌桶算法（Token Bucket）

令牌桶算法是目前最广泛使用的限流实现之一。系统维护一个容量为 `B` 的令牌桶，以固定速率 `r`（单位：令牌/秒）向桶中添加令牌，每次请求消耗1个令牌，若桶中令牌不足则拒绝或排队。

**关键公式：**
```
可用令牌数 = min(B, 上次令牌数 + r × Δt)
```
其中 `Δt` 为距上次请求的时间间隔（秒）。令牌桶允许突发流量：若用户长时间未发送请求，桶内令牌积累至上限 `B`，可在短时间内连续发出 `B` 次请求，适合对突发合理请求友好的AI API场景。

### 漏桶算法（Leaky Bucket）

漏桶算法以恒定速率处理请求，无论输入流量多高，输出速率固定为 `r` 请求/秒。请求到达时先进入容量为 `B` 的队列，溢出则丢弃。与令牌桶不同，漏桶**不允许突发**：即使桶未满，输出速率依然受限。这适合对下游服务保护更严格的场景，例如AI模型推理队列需要平滑流量以避免GPU内存溢出。

### 固定窗口计数器（Fixed Window Counter）

将时间切分为固定长度的窗口（如每60秒一个窗口），在窗口内维护请求计数器，超过阈值则拒绝。实现最简单，但存在**窗口边界突刺问题**：假设限额为每分钟100次，攻击者可在第59秒发送100次、第61秒再发送100次，在2秒内实际处理了200次请求。

### 滑动窗口日志（Sliding Window Log）

为每个客户端维护带时间戳的请求日志，每次请求时清除窗口之前的旧记录，再统计当前窗口内的请求数。若计数超过阈值则拒绝。精度最高，彻底消除固定窗口的边界突刺，但存储成本随请求量线性增长——每个请求需要存储一条时间戳记录，高并发场景下Redis内存消耗显著，通常用 `ZADD` + `ZREMRANGEBYSCORE` 命令组合实现。

### 滑动窗口计数器（Sliding Window Counter）

结合固定窗口的低内存消耗与滑动日志的高精度，通过对相邻两个固定窗口的计数进行加权插值估算当前滑动窗口内的请求数：

```
当前估算请求数 = 当前窗口计数 + 上一窗口计数 × (1 - 当前窗口已过时间比例)
```

Cloudflare在其限流产品中采用此算法，在误差约0.003%的前提下，将存储成本从滑动日志的O(N)降低至O(1)。

---

## 实际应用

**OpenAI API的多维度限流：** OpenAI对GPT-4 API同时施加RPM（如tier 1用户500 RPM）和TPM（如tier 1用户30,000 TPM）两种限制。AI工程师需要在客户端实现指数退避重试（Exponential Backoff）：首次重试等待1秒，第二次2秒，第三次4秒，并在请求头中读取 `x-ratelimit-remaining-requests` 和 `x-ratelimit-reset-requests` 字段来精确控制请求节奏，而非盲目重试。

**Redis实现分布式限流：** 在多实例部署的AI服务中，单机内存限流会导致各节点独立计数，实际通过流量是限额的N倍。使用Redis的原子操作可实现跨实例共享计数：
```lua
-- Lua脚本保证原子性
local count = redis.call('INCR', key)
if count == 1 then redis.call('EXPIRE', key, window) end
if count > limit then return 0 end
return 1
```
此Lua脚本在Redis中原子执行，避免INCR和EXPIRE之间的竞态条件。

**按用户等级差异化限流：** 企业级AI平台通常将限流与JWT中的用户等级字段绑定。解析JWT的 `tier` 字段后，免费用户限额设为10 RPM，专业用户100 RPM，企业用户1000 RPM，在API网关层（如Kong、Nginx）完成鉴别，无需请求穿透至业务服务。

---

## 常见误区

**误区一：限流只在服务端实现即可，客户端无需感知。** 实际上，优秀的限流设计要求服务端返回标准的 `Retry-After` 响应头（RFC 6585定义），告知客户端需等待多少秒后重试。若客户端收到429后立即重试，会造成"重试风暴"（Retry Storm），在限流解除瞬间大量请求同时涌入，反而使服务再次过载。AI SDK应内置退避策略而非忽略429响应。

**误区二：令牌桶和漏桶算法效果等价，选哪个都一样。** 两者在突发流量处理上有本质差异。令牌桶允许以桶容量 `B` 为上限的突发请求，适合用户体验优先的AI对话API；漏桶强制输出平滑，适合保护下游GPU推理服务不受瞬时冲击。错误地为AI推理队列选用令牌桶，可能导致突发的 `B` 个请求同时占用显存，触发OOM（Out of Memory）错误。

**误区三：限流阈值设置一次后无需调整。** 限流阈值应当依据实测的P99延迟和系统容量动态调整，而非凭经验固定。Netflix曾记录到其API网关在静态限流阈值下，在流量正常的假日期间因阈值设置过低而误伤大量合法用户请求，最终引入基于实时延迟的自适应限流（Adaptive Rate Limiting）。

---

## 知识关联

**与API认证（JWT/OAuth）的联系：** 限流策略在JWT认证之后生效——需要先从JWT的 `sub`（用户ID）或 `tier`（用户等级）字段提取限流键，再执行计数器逻辑。没有可信的身份标识，限流只能基于IP地址，容易被NAT后的合法用户误伤，也容易被代理IP规避。因此JWT认证是实现精细化限流的前提。

**通向限流器设计的路径：** 掌握上述四种算法后，下一阶段的"设计限流器"课题将聚焦于在分布式系统中选型、实现和权衡这些算法——包括如何处理Redis单点故障时的降级策略、如何设计支持动态配置热更新的限流规则引擎，以及如何对限流行为进行可观测性监控（如记录被限流的请求来源分布和触发频率）。
