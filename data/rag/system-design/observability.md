---
id: "observability"
concept: "可观测性"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 4
is_milestone: false
tags: ["logging", "metrics", "tracing", "opentelemetry"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 可观测性

## 概述

可观测性（Observability）源自控制论，由鲁道夫·卡尔曼（Rudolf Kálmán）于1960年在线性动态系统理论中正式提出，其核心定义是：**仅通过系统外部输出，能够推断系统内部状态的程度**。在AI工程的分布式系统语境下，可观测性被具体化为三大支柱：日志（Logs）、指标（Metrics）、追踪（Traces），通称"LMT三支柱"，由Charity Majors等工程师在2010年代后期将其系统化推广至云原生领域。

可观测性与传统监控（Monitoring）有本质区别。监控回答"预设的问题是否发生"，例如CPU是否超过80%；而可观测性回答"任何我事先未知的问题为何发生"。对于包含多个微服务、动态扩缩容的AI推理系统，一个模型预测延迟突发性升高可能来自特征工程、数据预处理、模型加载或下游数据库中的任何一个环节，此时没有可观测性基础设施，排查时间会从分钟级膨胀到数小时。

在AI工程中，可观测性还承担特有职责：追踪模型版本与预测结果的对应关系、检测数据漂移（Data Drift）触发的推理质量下降，以及在A/B测试框架中分别统计各模型版本的P99延迟。这使得AI系统的可观测性比普通Web服务更复杂，需要在标准LMT三支柱之上叠加**模型可观测性（Model Observability）**层。

---

## 核心原理

### 1. 日志（Logs）：事件的结构化记录

日志是系统在特定时刻发生的离散事件记录。现代AI工程强调**结构化日志**，即使用JSON格式而非纯文本，确保每条日志均可机器解析。例如，一条推理服务日志应包含字段：`model_version`、`request_id`、`input_token_count`、`latency_ms`、`status_code`。

日志级别通常分为TRACE、DEBUG、INFO、WARN、ERROR、FATAL六级，在生产环境的AI服务中，默认级别设置为INFO，WARN及以上级别触发告警。日志的最大挑战是**采样策略**：一个QPS为5000的推理服务若记录全量请求日志，每天将产生超过4亿条记录，存储成本不可接受。尾部采样（Tail-based Sampling）仅保留出现错误或延迟超过阈值的请求的完整日志，是常见解法。

### 2. 指标（Metrics）：时间序列的数值聚合

指标是将系统行为聚合为数值时间序列的机制，计算开销远低于日志。Prometheus是AI工程中最广泛使用的指标收集系统，其数据模型为：

```
metric_name{label_key="label_value", ...} value timestamp
```

指标类型分为四种：**Counter**（单调递增，如总请求数）、**Gauge**（可升降，如当前GPU内存占用MB）、**Histogram**（值分布，如延迟分桶统计，用于计算P50/P95/P99）、**Summary**（客户端计算的分位数）。AI推理服务的关键指标包括：模型加载时间、批处理队列长度、GPU利用率（`gpu_utilization_percent`）、每秒Token生成数（Token/s）。

Prometheus的采集周期（Scrape Interval）默认为15秒，这意味着指标的时间分辨率存在最小粒度限制，无法检测到15秒内发生并恢复的瞬时故障。

### 3. 追踪（Traces）：跨服务请求的因果链

分布式追踪基于**Dapper论文**（Google，2010年发表）提出的模型，将一次完整请求拆解为树状结构的Span集合。每个Span携带：`trace_id`（全局唯一）、`span_id`、`parent_span_id`、开始时间、结束时间、操作名称和标签。

OpenTelemetry（OTel）是当前行业标准，将日志、指标、追踪统一至同一SDK，避免厂商锁定。在AI推理系统中，一条追踪链通常跨越：API网关 → 特征服务 → 模型服务 → 后处理服务 → 结果缓存，每一跳都产生独立Span。通过Jaeger或Zipkin可视化这棵Span树，工程师能精确定位哪个服务贡献了多少毫秒的延迟。

追踪的**上下文传播（Context Propagation）**通过HTTP Header（如`traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`，遵循W3C Trace Context规范）在服务间传递，确保跨进程的Span能被正确关联至同一Trace。

### 4. 三支柱的关联与互补

单独任一支柱均有盲区：指标能告知P99延迟升高，但无法说明原因；日志能记录具体错误，但无法显示哪个下游服务是根因；追踪能显示调用链，但缺乏系统级聚合视图。三支柱通过共享`request_id`/`trace_id`字段实现关联：先用指标发现异常，再用追踪定位问题发生在哪条调用链，最后用日志查看该链路上的详细错误信息，形成"发现→定位→诊断"的完整工作流。

---

## 实际应用

**AI推理服务的SLO监控**：设定服务级别目标（SLO）如"P99延迟 < 200ms，成功率 > 99.9%"，通过Prometheus记录`histogram_quantile(0.99, rate(inference_latency_seconds_bucket[5m]))`，当该值持续超过0.2秒时触发PagerDuty告警，同时自动触发熔断器切换至轻量备用模型。

**大语言模型（LLM）服务的特殊指标**：对于GPT类服务，需额外监控Time-To-First-Token（TTFT）和每秒生成Token数（Throughput Token/s）。这两个指标与传统Web服务延迟指标不同，需要在Histogram桶边界设计上特别处理（如将桶边界设为50ms, 100ms, 200ms, 500ms, 1000ms, 2000ms而非默认值）。

**数据漂移检测**：将模型输入特征的统计分布（均值、标准差、分位数）作为Gauge指标定期上报，与训练集基准值对比，当Jensen-Shannon散度超过0.1时触发预警，此为模型可观测性层超出标准LMT三支柱的典型扩展场景。

---

## 常见误区

**误区一：可观测性等于大量打日志**。随意增加日志条数会引入三个问题：存储成本线性增长、日志I/O本身成为性能瓶颈（同步日志写入可使推理延迟增加10%-30%），以及噪声淹没真正有价值的信息。正确做法是明确每条日志的消费场景，区分应走日志还是走指标（高频重复的统计数据应走指标，非仅用Gauge记录而非写日志）。

**误区二：追踪对性能无影响**。分布式追踪的上下文注入和Span上报均有开销。Jaeger官方基准测试显示，全量采样（100%）可导致目标服务吞吐量下降约5%-15%。生产环境通常采用基于头部的概率采样（如1%固定采样率）结合尾部采样（100%保留错误和高延迟请求），而非全量追踪。

**误区三：三支柱各自独立部署即算完成可观测性建设**。如果Prometheus指标中的`request_id`标签与Elasticsearch中日志的`request_id`字段命名不一致，或追踪系统未注入`trace_id`到日志，三支柱将成为孤岛，无法联动排查。可观测性建设的关键交付物是**关联性**，而非三套系统的独立运行。

---

## 知识关联

**与熔断器模式的关系**：熔断器（Circuit Breaker）的状态转换（Closed→Open→Half-Open）直接依赖可观测性数据——错误率和响应延迟两个指标是熔断器判断是否触发的输入信号。若指标采集延迟超过熔断器的滑动窗口时间（如Resilience4j默认的60秒），熔断决策将基于过期数据，导致保护失效或错误触发。

**与日志与监控的关系**：传统日志与监控聚焦于预定义规则的告警，是可观测性的子集和前身。将既有监控系统升级为具备可观测性的系统，核心改造点在于：为日志添加结构化字段（尤其是`trace_id`）、将监控指标迁移至支持Histogram类型的系统、引入分布式追踪的上下文传播机制，三者缺一则无法实现完整的根因分析能力。