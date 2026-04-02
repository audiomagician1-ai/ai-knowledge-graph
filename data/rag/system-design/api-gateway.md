---
id: "api-gateway"
concept: "API网关"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 6
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# API网关

## 概述

API网关（API Gateway）是部署在客户端与后端服务之间的反向代理服务器，充当系统的统一入口点，负责接收所有外部请求并将其路由到对应的后端微服务。与简单的负载均衡器不同，API网关还承担认证鉴权、限流熔断、协议转换、请求聚合等横切关注点的处理，使各微服务专注于业务逻辑本身。

API网关的概念在2010年代随着微服务架构的普及而成熟。Netflix在2012年开源的Zuul是业界最早被广泛采用的API网关之一，此后AWS于2015年推出托管服务Amazon API Gateway，Kong（基于OpenResty/Nginx）等开源方案也相继出现。在AI工程场景中，API网关尤为关键——大模型推理服务的调用通常涉及高并发、高延迟、token计量计费等特殊需求，这些都需要网关层进行专项处理。

在AI系统设计中，API网关解决了一个具体痛点：当系统同时提供GPT-4、Claude、本地部署的LLaMA等多个模型接口时，调用方不需要知道每个模型的实际地址、认证方式和请求格式，由网关统一适配。这不仅降低了客户端复杂度，也让后端模型的替换或扩容对外部完全透明。

## 核心原理

### 请求路由与服务发现

API网关的路由规则通常基于请求路径、HTTP方法、请求头或查询参数进行匹配。例如，`POST /v1/chat/completions` 路由到OpenAI兼容接口，`POST /v1/embeddings` 路由到向量化服务，`GET /v1/models` 返回网关聚合后的模型列表。路由表可以是静态配置文件（如Kong的声明式YAML），也可以结合服务注册中心（如Consul、Etcd）实现动态更新，后者称为服务发现集成。

网关执行路由时的匹配优先级通常遵循"最长前缀匹配"原则：`/v1/chat/completions/stream` 会优先匹配比 `/v1/chat` 更具体的规则。Kong网关的路由优先级还会将正则表达式规则排在精确路径之后，避免过度匹配。

### 认证鉴权与限流

API网关集中处理认证，避免每个微服务重复实现。常见方案包括：JWT验证（网关验证签名后，将解码后的用户ID通过请求头 `X-User-Id` 传递给下游）、API Key校验（将Key映射到租户身份）、OAuth 2.0的Token Introspection。对于AI推理服务，网关还需实现**基于Token用量的限流**，这与普通的RPS（每秒请求数）限流不同——一次请求可能消耗4000个token，另一次只消耗50个，简单计数限流无法准确控制成本。

限流算法中，令牌桶（Token Bucket）适合允许突发流量的场景，漏桶（Leaky Bucket）适合平滑输出，固定窗口计数器实现简单但存在边界突刺问题。Redis + Lua脚本是分布式环境下实现滑动窗口限流的主流方案，通过 `ZADD` 和 `ZRANGEBYSCORE` 操作维护时间窗口内的请求记录，单次原子操作的时间复杂度为O(log N)。

### 协议转换与请求聚合

协议转换是API网关的重要能力之一。例如，外部客户端通过HTTPS/REST调用，而内部某服务使用gRPC通信，网关负责在两种协议间做转换，客户端无需安装protobuf工具。在AI工程中，一个典型场景是：网关将OpenAI格式的请求（`{"model": "gpt-4", "messages": [...]}`）转换为私有化部署的vLLM服务所接受的格式，实现"OpenAI兼容层"。

请求聚合（Request Aggregation）允许网关将一个客户端请求拆分为对多个下游服务的调用并合并结果。例如，AI助手的"用户个人主页"接口需要同时获取用户基本信息、历史对话摘要和使用量统计，网关可并行调用三个微服务后聚合响应，将客户端的3次网络往返压缩为1次，显著降低端到端延迟。

### 可观测性与熔断

网关是采集全局可观测性数据的理想位置，因为所有流量都经过此节点。标准实践是在网关层统一注入请求追踪ID（Trace ID），并记录每次请求的延迟、状态码、上游服务名称、token消耗量等指标，上报至Prometheus或Datadog。

熔断器（Circuit Breaker）模式在网关层实现后，当某个下游AI服务的错误率在60秒内超过50%时，熔断器切换到"打开"状态，后续请求直接返回预设的降级响应而不再访问该服务，待30秒冷却期后进入"半开"状态进行探测。这防止了因单个服务故障导致的级联崩溃。

## 实际应用

**AI模型代理网关**：LiteLLM是专为AI工程设计的开源API网关，通过统一的OpenAI格式接口，将请求路由到OpenAI、Anthropic、Azure OpenAI、本地Ollama等100+个模型提供商。它在网关层实现了按模型的成本追踪（每次请求记录input tokens × 单价 + output tokens × 单价），并提供基于预算的自动限流——当某个API Key的月度花费超过设定上限时，自动拒绝新请求并返回429状态码。

**生产环境的蓝绿部署**：当GPT-4升级到新版本时，网关可配置流量权重：90%请求路由到稳定版本，10%路由到新版本，通过对比两组的错误率和延迟决定是否全量切换，这被称为金丝雀发布（Canary Release）。Kong Gateway通过插件 `request-termination` 和加权负载均衡原生支持此模式。

**多租户AI平台**：SaaS型AI平台中，网关通过API Key识别租户，为每个租户单独配置：允许调用的模型列表、RPM（每分钟请求数）上限、月度Token配额、以及数据隔离策略（确保租户A的对话历史不会出现在租户B的上下文中）。

## 常见误区

**误区一：将网关等同于负载均衡器**。Nginx在L4/L7做流量分发，但不内置JWT验证、限流策略管理或服务发现集成，每次规则变更需要重启或reload。API网关在此基础上提供了动态配置的Admin API（如Kong的`/routes`和`/plugins`端点），无需重启即可添加新路由或修改限流规则，这在需要频繁上线新AI模型的场景中至关重要。

**误区二：网关越多功能越好**。将大量业务逻辑（如用户积分扣减、对话内容过滤）放入网关插件，会使网关成为难以维护的"上帝组件"。网关应只处理与流量管理直接相关的横切关注点，业务逻辑应保留在各自的微服务中。以内容安全审核为例，正确做法是网关将请求转发到专门的内容审核微服务，而非在网关插件中嵌入审核模型。

**误区三：网关是单点故障风险可以忽略的**。由于所有流量都经过网关，其可用性直接决定整个系统的可用性。生产环境必须以集群模式部署（至少3节点），使用共享数据存储（如Kong集群模式依赖PostgreSQL或Cassandra同步配置）。AWS API Gateway的SLA为99.95%，对应每月约22分钟不可用时间，自建网关需要通过多可用区部署达到同等标准。

## 知识关联

API网关直接建立在**微服务架构**的基础上：微服务将单体拆分为独立服务后，必然需要一个统一的对外入口来管理服务间通信的复杂性，这正是网关出现的原因。理解微服务的服务注册与发现机制（Consul、Kubernetes Service）是配置动态路由的前提。

在向更高级系统设计演进时，API网关与**服务网格**（Service Mesh，如Istio）形成互补：网关处理南北向流量（外部到内部），服务网格处理东西向流量（微服务间通信）。在AI工程的MLOps流水线中，网关还与**模型注册表**（Model Registry）结合使用——当新模型版本通过评估后，自动更新网关路由规则，实现模型的持续交付。