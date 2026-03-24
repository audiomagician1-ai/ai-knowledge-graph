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
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 监控与告警

## 概述

监控与告警（Monitoring & Alerting）是AI工程运维体系中用于持续观测系统状态、检测异常并触发通知的完整闭环机制。具体而言，监控负责采集系统指标（Metrics）、追踪（Traces）和日志（Logs）三类信号，而告警则基于预设阈值或统计规则，在指标偏离正常范围时自动通知运维人员。在AI系统中，监控对象不仅包括CPU、内存等基础资源，还涵盖模型推理延迟、预测置信度分布、特征漂移（Feature Drift）等ML专属指标。

监控与告警体系的现代形态起源于2000年代的互联网基础设施运维需求。Nagios于2002年发布了首个广泛使用的开源监控系统，随后Prometheus在2012年由SoundCloud工程师开发，引入了时序数据库与拉取（Pull）模式的指标采集架构，成为当今AI工程领域最主流的监控方案之一。告警规则引擎Alertmanager则作为Prometheus的配套组件，提供了路由、分组、静默和抑制四种核心告警管理能力。

在AI系统中，监控与告警的重要性远超传统软件系统。因为AI模型存在数据漂移（Data Drift）和概念漂移（Concept Drift）问题——即便服务本身运行正常，模型预测质量也可能随时间悄然下降。如果没有针对模型输出分布的实时监控，这种"静默降级"现象可能持续数周才被发现，造成难以挽回的业务损失。

---

## 核心原理

### 指标采集与时序数据模型

Prometheus使用的数据模型将每个指标定义为：`metric_name{label_key="label_value", ...} value timestamp`。例如，AI推理服务的延迟指标可表示为 `inference_latency_seconds{model="resnet50", version="v2.1"} 0.032 1690000000`。Prometheus支持四种指标类型：Counter（单调递增计数器，如请求总数）、Gauge（可升降的瞬时值，如GPU显存占用）、Histogram（分布直方图，用于计算P99延迟）和Summary（客户端分位数统计）。AI系统通常使用Histogram类型记录推理延迟，因为它能在服务端计算任意分位数，公式为：`rate(inference_latency_seconds_bucket[5m])` 配合 `histogram_quantile(0.99, ...)` 可得到过去5分钟的P99延迟值。

### 告警规则与阈值设定

告警规则在Prometheus的YAML配置中以PromQL表达式形式定义，并设置 `for` 字段表示持续触发时长才真正发送告警，以避免毛刺（Spike）误报。例如，一条典型的AI推理服务告警规则如下：

```yaml
alert: HighInferenceLatency
expr: histogram_quantile(0.99, rate(inference_latency_seconds_bucket[5m])) > 0.5
for: 2m
labels:
  severity: critical
annotations:
  summary: "模型推理P99延迟超过500ms"
```

`for: 2m` 表示该条件需连续满足2分钟才会触发告警，这一参数的选择需权衡告警响应速度（越短越快）与误报率（越短越高）。AI场景中，模型首次加载（Cold Start）可能导致延迟短暂飙高，若 `for` 值设置过短，每次模型热重载都会触发虚假告警。

### 告警路由与分级管理

Alertmanager将告警按严重程度（Severity）分级为 `info`、`warning`、`critical` 三档，并通过路由树将不同级别的告警发送至不同接收渠道。`critical` 级别告警通常触发PagerDuty或电话呼叫，`warning` 级别发送至Slack，`info` 级别仅记录到告警历史。分组（Grouping）机制允许将同一时段内来自同一AI服务集群的多条相关告警合并为一条通知，避免告警风暴（Alert Storm）——当一个上游数据管道故障导致100个模型服务同时报错时，若无分组机制，运维人员将同时收到100条告警，严重影响故障定位效率。抑制（Inhibition）规则则允许在更高级别告警激活时自动压制低级别告警，例如当GPU集群宕机时，自动抑制所有依赖该集群的模型服务延迟告警。

### AI系统专属监控维度

AI工程的监控体系需额外关注三类ML专属指标：  
1. **数据质量指标**：输入特征的缺失率、超出训练分布范围的样本比例（通常使用KS检验或PSI值量化，PSI > 0.2 通常视为严重漂移）；  
2. **模型输出指标**：预测标签分布、平均置信度、低置信预测（confidence < 0.5）的占比；  
3. **业务影响指标**：若存在真实标签反馈，可计算滚动窗口内的实时准确率，Evidently AI等工具专为此类指标的可视化监控而设计。

---

## 实际应用

**推荐系统的实时监控**：电商推荐模型需监控点击率（CTR）的每小时滚动均值，若CTR连续3小时低于历史同期均值的80%，触发 `warning` 告警，提示模型可能因用户行为分布变化而性能下降。同时监控推荐响应时间的P95值是否超过200ms，因为超过该阈值的延迟在电商场景中会显著影响转化率。

**NLP服务的异常检测**：大语言模型（LLM）推理服务需监控token生成速率（tokens/second），当使用vLLM等推理框架时，还需监控KV Cache命中率，该值低于60%通常意味着请求批处理策略需要调整。对于内容安全分类模型，需监控"违规"类别输出的日均占比，若24小时内该比例突增超过2倍标准差，触发安全团队告警。

**GPU集群资源监控**：通过NVIDIA DCGM Exporter将GPU指标暴露给Prometheus，监控GPU利用率（`DCGM_FI_DEV_GPU_UTIL`）、显存占用率（`DCGM_FI_DEV_MEM_COPY_UTIL`）和GPU温度（`DCGM_FI_DEV_GPU_TEMP`）。当温度持续超过85°C时立即告警，因为NVIDIA GPU的热保护机制会在90°C时自动降频，导致推理吞吐量骤降。

---

## 常见误区

**误区一：对所有指标设置固定阈值**  
许多工程师习惯将告警阈值设为固定数值（如"延迟 > 500ms 则告警"），但AI服务的负载通常具有强烈的周期性——日间请求量可能是夜间的10倍，固定阈值会导致白天大量误报或夜间漏报。正确做法是使用基于历史数据的动态基线，例如Prometheus的 `predict_linear()` 函数可预测指标趋势，或使用Grafana的异常检测插件建立时间感知的动态阈值。

**误区二：混淆监控与日志的职责边界**  
监控（Metrics）适合回答"当前系统状态是否正常"，时序数据以低成本保存数值型聚合信息；而日志适合回答"某次异常请求具体发生了什么"，保存高细节的原始事件。常见错误是试图用高频日志打点替代Prometheus指标，在每秒10万次推理的AI服务中，为每条请求写入完整日志会使存储成本膨胀20-50倍，且无法高效计算分位数。正确做法是指标采集覆盖所有请求，日志仅记录异常请求或按1%比例采样。

**误区三：忽视告警疲劳（Alert Fatigue）**  
一个配置不当的监控系统可能每天产生数百条告警，导致运维人员逐渐忽视所有告警通知，形成危险的"告警疲劳"。Google SRE实践建议：`critical` 级别告警每周不应超过5条，否则需要审查告警规则的合理性。解决方案包括提高 `for` 字段的持续时间门槛、合并相关告警、以及对低价值告警降级为 `info` 仅记录而不通知。

---

## 知识关联

**与日志与监控的关系**：日志与监控（Logging & Monitoring）覆盖了数据采集的基础层，重点在于如何生成和存储原始观测数据。监控与告警在此基础上增加了决策层——基于采集到的指标数据制定规则、触发响应动作，形成从"观测"到"行动"的完整闭环。Prometheus的 `scrape_interval`（默认15秒）决定了告警系统能够感知异常的最短响应时间，这一参数直接来源于日志与监控阶段的架构设计。

**与Service Mesh的关联**：学习Service Mesh（如Istio）后，AI服务的监控能力将从应用层指标扩展到网格层面的四黄金信号（延迟、流量、错误率、饱和度）。Istio通过Envoy Sidecar自动为每个AI微服务注入请求级别的遥测数据，无需修改模型服务代码即可获得服务间调用的完整追踪链路，与现有Prometheus告警规则无缝集成。

**与日志聚合的关联**：当告警触
