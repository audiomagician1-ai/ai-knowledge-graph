---
id: "monitoring-alerting"
concept: "监控与告警"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 5
is_milestone: false
tags: ["运维"]

# Quality Metadata (Schema v2)
content_version: 4
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
updated_at: 2026-03-30
---

# 监控与告警

## 概述

监控与告警（Monitoring & Alerting）是AI工程运维体系中针对模型服务、数据管道和基础设施进行持续状态采集、阈值判断与异常通知的完整闭环机制。与通用IT系统相比，AI系统的监控需要同时覆盖**基础设施层**（CPU/GPU利用率、内存）、**服务层**（QPS、延迟、错误率）和**模型层**（预测分布漂移、特征缺失率、输出置信度），三层指标缺一不可。

该领域的现代实践形成于2010年代中期。Google于2014年在SRE手册中系统化提出"四大黄金信号"（延迟、流量、错误率、饱和度），成为服务级监控的基准框架。Prometheus项目于2012年由SoundCloud发起，2016年成为CNCF第二个毕业项目，确立了**拉取式（Pull-based）指标采集**的行业标准，配合Grafana实现可视化，至今仍是AI工程监控栈的主流选型。

AI系统特有的模型性能退化（Model Degradation）问题使监控与告警的价值远超传统运维场景。一个上线的推荐模型在训练数据分布与生产数据分布发生偏移后，业务指标（如点击率）可能在数周内悄然下滑而不触发任何服务级告警，这种**静默失败（Silent Failure）**只能通过专门的模型监控指标体系加以发现。

---

## 核心原理

### 指标采集与存储模型

Prometheus使用**时间序列数据库（TSDB）**存储指标，每条数据由指标名称、标签集（Label Set）和时间戳-数值对组成。例如：

```
model_inference_latency_seconds{model="bert-v2", env="prod", quantile="0.99"} 0.312
```

上述标签设计允许按模型版本、环境切片查询，是AI多模型共存场景的关键能力。Prometheus默认采集间隔为15秒，数据保留周期默认15天，生产环境通常配置远程写入（Remote Write）到Thanos或Cortex以实现长期存储。

四类指标类型各有用途：
- **Counter**（只增计数器）：用于统计推理请求总数、错误总数
- **Gauge**（任意值）：用于记录当前GPU显存占用、批处理队列深度
- **Histogram**（直方图）：用于推理延迟的分位数（P50/P95/P99）统计
- **Summary**（摘要）：客户端计算分位数，适合不需要聚合的单实例场景

### 告警规则与PromQL

Prometheus AlertManager通过**PromQL（Prometheus Query Language）**定义告警规则。一条典型的AI服务告警规则如下：

```yaml
alert: HighInferenceLatency
expr: histogram_quantile(0.99, 
        rate(model_inference_latency_seconds_bucket[5m])) > 0.5
for: 2m
labels:
  severity: critical
annotations:
  summary: "模型P99延迟超过500ms持续2分钟"
```

`for: 2m` 字段定义了**告警持续时长（Pending Duration）**，避免瞬时毛刺触发误报。AlertManager负责对告警进行**去重（Deduplication）**、**分组（Grouping）**和**静默（Silencing）**，并通过Webhook、PagerDuty、Slack等渠道发送通知。

### 模型专项监控指标

AI系统需要在标准服务指标之外额外监控以下模型特有指标：

**数据漂移检测**：比较生产特征分布与训练基准分布之间的统计距离，常用KL散度（Kullback-Leibler Divergence）或PSI（Population Stability Index）。PSI计算公式为：

$$PSI = \sum_{i=1}^{n}(A_i - E_i) \times \ln\frac{A_i}{E_i}$$

其中 $A_i$ 为实际分布比例，$E_i$ 为期望分布比例。PSI < 0.1 表示分布稳定，0.1-0.25 为需关注区间，> 0.25 应触发模型重训告警。

**预测置信度分布**：监控模型输出softmax概率的均值和方差，当均值长期低于0.6（以分类任务为例）时，可能指示输入质量下降或模型老化。

**特征缺失率**：实时统计各特征字段的空值比例，单特征缺失率超过5%通常需要触发数据管道告警。

### 告警噪声治理

告警风暴（Alert Storm）是运维团队告警疲劳的主要来源。缓解策略包括：
1. **告警依赖抑制（Inhibition）**：若GPU节点宕机告警触发，则自动抑制该节点上所有模型服务的延迟告警，避免根因掩盖于大量衍生告警中
2. **告警聚合窗口**：AlertManager的`group_wait`（默认30秒）和`group_interval`（默认5分钟）参数控制同组告警的合并发送节奏
3. **SLO-based告警**：基于错误预算消耗速率（Burn Rate）而非固定阈值设定告警，Google SRE推荐使用1小时窗口的消耗速率超过14.4倍作为Page级别告警触发条件

---

## 实际应用

**LLM推理服务监控**：部署GPT类模型的推理服务时，需重点监控Token生成速率（tokens/s）、首Token延迟（Time-to-First-Token, TTFT）和KV Cache命中率。TTFT超过2秒通常是用户体验恶化的临界点，应设置P95 TTFT > 1.5s为Warning级告警。

**训练任务监控**：使用Prometheus结合Grafana的GPU监控面板（dashboard ID: 14574），实时跟踪NVIDIA GPU的SM利用率、显存带宽利用率，当GPU利用率持续低于30%超过10分钟时，告警提示可能存在数据加载瓶颈（DataLoader bottleneck）。

**在线特征服务告警**：在特征存储（Feature Store）与模型推理之间，对特征拉取延迟设置多级告警：P99 > 10ms为Info，P99 > 50ms为Warning，P99 > 100ms为Critical，并配置PagerDuty在Critical级别时触发On-Call轮值。

---

## 常见误区

**误区一：仅监控服务层指标而忽略模型层指标**
许多团队认为"服务响应正常 = 模型工作正常"。实际上，一个推理服务完全可以在P99延迟达标、错误率为零的情况下，因输入数据的用户行为变化导致模型预测质量持续下降。仅有服务层Prometheus指标而没有PSI检测或预测分布监控的AI系统，等同于在生产环境中盲目飞行。

**误区二：告警阈值一经设定永不调整**
固定阈值不适用于具有明显周期性的AI业务。电商推荐系统在双十一期间的QPS可能是平时的50倍，静态QPS告警阈值会在高峰期持续误报。正确做法是使用**动态基线告警**，基于过去4-8周同周期的滚动均值加3个标准差（3-sigma法则）动态设定阈值，或采用Prometheus的`predict_linear()`函数进行趋势预测。

**误区三：混淆告警（Alert）与通知（Notification）的职责边界**
AlertManager负责告警的路由和去重，而Slack/PagerDuty是通知渠道。将复杂的告警逻辑（如业务含义判断、上下文拼接）写入通知模板而非在AlertManager规则层处理，会导致告警规则难以测试和维护。告警规则应在Prometheus层完整定义条件，通知渠道只负责格式化输出。

---

## 知识关联

**前置知识衔接**：日志与监控课程建立了对可观测性（Observability）三支柱（Metrics/Logs/Traces）的基础认知，监控与告警在此基础上专注于**Metrics维度**的闭环自动化处理，将采集到的指标转化为可执行的运维动作（通知、自动扩缩容触发等）。

**通往Service Mesh**：掌握监控与告警后，Service Mesh（如Istio）将监控能力下沉至网络层，通过Envoy Sidecar自动采集服务间所有流量的延迟、错误率指标，无需业务代码侵入，是对本章手动埋点监控能力的架构级升级。Istio默认与Prometheus集成，告警规则的PromQL语法可直接复用。

**通往日志聚合**：当告警触发后，工程师需要快速关联日志进行根因分析。日志聚合（ELK/Loki栈）与监控告警通过**TraceID**相互打通，形成从Alert → Metric异常时间段 → 关联日志 → 具体错误堆栈的完整排查链路，是AI系统可观测性体系的最终形态。