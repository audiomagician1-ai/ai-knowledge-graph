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
quality_tier: "pending-rescore"
quality_score: 43.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 可观测性

## 概述

可观测性（Observability）这一术语源自控制论，由匈牙利裔美国工程师 Rudolf Kálmán 于1960年提出，用于描述"能否从系统外部输出推断内部状态"的能力。在分布式AI系统工程中，可观测性被重新定义为：通过收集日志（Logs）、指标（Metrics）、追踪（Traces）三类遥测数据，使工程师能够在不修改系统代码的前提下，回答任意关于系统内部状态的未知问题。这与传统监控（Monitoring）的本质区别在于：监控回答"是否出问题"，可观测性回答"为什么出问题"。

可观测性在AI推理服务和训练集群中尤为关键。一个典型的LLM推理集群可能同时运行数百个微服务，单次用户请求跨越10至20个服务节点，传统逐机器排查的方式已完全不可行。2021年AWS re:Invent大会披露，SRE团队将平均故障恢复时间（MTTR）从47分钟压缩至8分钟的核心手段，正是建立了完整的三支柱可观测性体系。

## 核心原理

### 第一支柱：结构化日志

原始文本日志（如`ERROR: connection failed`）在分布式环境中几乎无法聚合分析。结构化日志要求以固定Schema（通常为JSON）记录每一条日志，必须包含`timestamp`、`severity`、`service_name`、`trace_id`和`span_id`五个标准字段。`trace_id`是连接三大支柱的纽带——同一请求在所有服务产生的日志，必须携带相同的128位`trace_id`，才能在ELK（Elasticsearch + Logstash + Kibana）或Loki中实现跨服务日志关联查询。

AI系统特有的日志场景包括：模型推理延迟日志（记录每次forward pass耗时）、Token使用量日志（输入/输出Token数量）、以及特征工程失败日志（记录具体缺失特征名称和样本ID）。日志采样率（Sampling Rate）是关键决策：对于高流量AI服务，通常对正常请求按1%采样，对错误和慢请求保持100%全量记录。

### 第二支柱：时序指标

指标是对系统状态的数值型聚合，其数据模型由**名称、标签集（Label Set）和时间戳-数值对序列**构成。Prometheus的数据模型是业界标准，其PromQL查询语言支持如下典型表达式：

```
rate(llm_inference_requests_total{status="error"}[5m]) 
/ rate(llm_inference_requests_total[5m])
```

此式计算过去5分钟内推理请求的错误率。

AI系统需要监控四类核心指标，通称"四大黄金信号"（Google SRE手册提出）：**延迟**（P50/P95/P99分位数，而非平均值）、**流量**（每秒请求数QPS）、**错误率**（HTTP 5xx及模型级错误）、**饱和度**（GPU显存占用率、KV Cache命中率）。其中GPU显存饱和度是AI系统区别于普通Web服务的独特指标，当显存占用超过85%时，通常预示OOM（Out of Memory）错误即将发生。

### 第三支柱：分布式追踪

分布式追踪基于OpenTelemetry（OTel）标准，每次请求生成一个**Trace**，由多个**Span**构成有向无环图（DAG）。每个Span记录：操作名称、开始时间戳、持续时长、父Span ID，以及键值对形式的自定义属性（Attributes）。

在LLM应用中，一个典型Trace包含以下Span层级：
- `http.server`（接收用户请求，根Span）
  - `retrieval.vector_search`（RAG检索，含`embedding_model`属性）
  - `llm.completion`（模型推理，含`model_name`、`prompt_tokens`属性）
    - `tokenizer.encode`（分词）
    - `gpu.forward_pass`（GPU推理，最关键的耗时节点）
  - `http.response`（返回结果）

Jaeger和Zipkin是常用的Trace后端，它们通过`trace_id`将所有Span组装为火焰图（Flame Graph），直观呈现哪个服务是延迟瓶颈。

## 实际应用

**AI推理服务的可观测性落地**：部署一个基于vLLM的推理服务时，需在`/metrics`端点暴露Prometheus格式指标，包括`vllm:num_requests_running`（并发请求数）、`vllm:gpu_cache_usage_perc`（KV Cache使用率）。当KV Cache使用率持续超过90%时，应触发自动扩容或请求限流，这一阈值判断依赖Metrics支柱。

**慢查询根因分析**：当P99延迟突然从200ms升至2000ms时，标准排查流程为：① 查Metrics定位异常时间窗口（如14:23-14:35）；② 在该窗口内筛选`duration > 1s`的慢Trace；③ 展开慢Trace找到耗时最长的Span（如`retrieval.vector_search`占比87%）；④ 用该Span的`trace_id`在日志系统查询原始错误信息（如"向量索引未预热，进行全量扫描"）。此流程完整串联了三大支柱。

**模型性能退化检测**：记录每次推理的`model_accuracy_score`或`reward_score`作为业务指标（Business Metric），通过Grafana设置连续5分钟均值低于阈值即告警，可在用户投诉前发现模型退化问题。

## 常见误区

**误区一：将可观测性等同于日志收集**。许多团队在系统中仅部署ELK或EFK（Elasticsearch + Fluentd + Kibana）即认为已具备可观测性。实际上，缺少Traces意味着无法定位跨服务请求的延迟分布；缺少Metrics意味着无法设置有意义的SLO（服务等级目标）告警。只有三支柱全部覆盖，才能应对"服务整体正常但部分用户请求异常缓慢"此类复杂故障场景。

**误区二：越多数据越好**。全量收集所有日志和Trace会导致存储成本爆炸，以及查询时的信噪比下降。正确做法是实施**基于头部采样（Head-based Sampling）和尾部采样（Tail-based Sampling）的混合策略**：头部采样在请求入口按概率决定是否采集，尾部采样则在请求完成后，对耗时超过阈值或含错误的Trace进行补充全量保留。OpenTelemetry Collector原生支持Tail Sampling Processor配置。

**误区三：可观测性仅对生产环境有意义**。AI系统的模型训练过程同样需要可观测性：训练Loss曲线是指标、梯度异常是日志、DataLoader各阶段耗时是追踪。MLflow和Weights & Biases（W&B）正是将可观测性三支柱应用于训练循环的专用工具，其中W&B的`wandb.log()`每隔N个step记录一次指标，相当于训练过程的Metrics采集。

## 知识关联

**与熔断器模式的关联**：熔断器（Circuit Breaker）的状态转换（Closed → Open → Half-Open）依赖错误率指标的实时计算，而这正是可观测性第二支柱（Metrics）的输出。Hystrix和Resilience4j等熔断器库通常内置Metrics端点，可直接接入Prometheus采集，形成"可观测性数据驱动熔断决策"的闭环。熔断器打开时产生的大量降级日志，也需要通过日志聚合系统（第一支柱）进行告警，避免无声失败。

**与日志与监控的延伸**：传统监控关注预定义的已知故障模式（Known Unknowns），而可观测性通过追踪支柱引入的上下文关联能力，使工程师能够诊断从未预料到的故障（Unknown Unknowns）。从监控升级至完整可观测性体系，需要引入OpenTelemetry SDK完成代码插桩（Instrumentation），并部署Tempo（Traces）、Prometheus（Metrics）、Loki（Logs）构成Grafana推荐的PLT（Prometheus-Loki-Tempo）开源可观测性栈。
