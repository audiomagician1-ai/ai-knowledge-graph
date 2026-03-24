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
content_version: 3
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

监控与告警（Monitoring & Alerting）是AI工程运维体系中的主动防御机制，通过持续采集系统指标、设定阈值规则并在异常发生时触发通知，将被动故障响应转变为主动风险管控。与单纯的日志记录不同，监控侧重于**时序数据的实时采集与可视化**，而告警则是在指标越界时通过PagerDuty、Slack、邮件等渠道将异常推送给运维人员。

该领域的现代体系建立在2012年SoundCloud开源的Prometheus项目之上。Prometheus采用**拉取（pull）模型**主动抓取各服务暴露的`/metrics`端点，与传统推送模型相比大幅降低了服务间耦合度，成为云原生监控事实标准。Grafana于2014年发布，作为Prometheus的可视化配套工具，目前二者的组合在AI推理服务、模型训练集群监控中占主导地位。

对于AI工程而言，监控与告警的重要性远超传统Web服务：模型推理延迟（P99 latency）、GPU利用率、特征分布偏移（data drift）等指标若不能被及时捕捉，将直接导致线上模型静默失效——即模型仍在运行但预测质量已大幅下降，而无人察觉。

---

## 核心原理

### 四大黄金指标（Four Golden Signals）

Google SRE团队在《Site Reliability Engineering》（2016）中总结了服务监控的四大黄金指标：

| 指标 | 含义 | AI场景示例 |
|------|------|------------|
| **延迟（Latency）** | 请求处理时间 | 模型推理P99延迟 > 200ms触发告警 |
| **流量（Traffic）** | 系统吞吐量 | 每秒推理请求数（RPS） |
| **错误率（Errors）** | 失败请求比例 | 模型返回空结果率 > 0.1% |
| **饱和度（Saturation）** | 资源使用上限接近程度 | GPU显存使用率 > 90% |

这四项指标构成告警规则设计的基础框架，任何AI推理服务应至少覆盖这四个维度。

### Prometheus告警规则语法与PromQL

Prometheus使用**PromQL（Prometheus Query Language）**定义告警条件。一条典型的告警规则如下：

```yaml
- alert: HighInferenceLatency
  expr: histogram_quantile(0.99, rate(inference_duration_seconds_bucket[5m])) > 0.2
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "模型推理P99延迟超过200ms"
```

其中`for: 2m`表示条件需持续满足2分钟才触发，避免因短暂抖动产生**告警风暴（alert storm）**。`histogram_quantile(0.99, ...)`计算第99百分位延迟，比平均值更能反映用户真实体验。

### 告警分级与抑制机制

生产环境中告警必须分级管理，常见的三级体系为：

- **P0（Critical）**：立即唤醒值班人员，如模型服务完全不可用，响应SLA通常为5分钟内
- **P1（Warning）**：工作时间内处理，如特征缺失率连续1小时超过5%
- **P2（Info）**：记录备查，不主动通知

Alertmanager（Prometheus配套组件）提供**路由（routing）、分组（grouping）和静默（silencing）**三种告警管理手段。分组机制可将同一时间段内同一服务的50条告警合并为1条通知，避免运维人员被淹没在告警噪音中。

### AI特有的模型监控指标

传统基础设施指标无法捕获AI系统的质量退化，需额外监控：

- **数据漂移（Data Drift）**：输入特征分布与训练集分布的KL散度 `D_KL(P||Q) = Σ P(x) log(P(x)/Q(x))`，当KL散度超过设定阈值（如0.1）时触发模型重训练告警
- **预测置信度分布**：若模型输出的平均置信度从0.85下滑至0.65，通常预示模型已遇到训练分布外数据
- **业务指标关联**：点击率、转化率等业务KPI与模型预测分数的相关性异常下降

---

## 实际应用

### 案例一：GPU训练集群监控

在大规模模型训练场景中，使用**DCGM Exporter**将NVIDIA GPU的利用率、显存占用、温度、NVLink带宽等指标暴露为Prometheus格式。告警规则示例：当任一GPU温度超过85°C且持续3分钟时触发P1告警，自动通知调度系统降低该节点的任务优先级。若显存OOM（Out of Memory）错误率在5分钟内超过3次，则升级为P0并停止该节点上的所有训练任务。

### 案例二：推理服务SLO告警

基于**服务等级目标（SLO）**设计告警规则比固定阈值更具业务意义。假设SLO要求99.9%的推理请求在100ms内完成，可用"错误预算"消耗速率触发告警：

```
错误预算消耗率 = 实际错误率 / (1 - SLO目标)
当消耗率 > 1（即预算耗尽速度快于补充速度）时告警
```

Netflix、Uber等公司均采用此方式替代简单阈值告警，显著减少了误报率。

### 案例三：多模型A/B测试监控

当同时运行模型A和模型B进行流量切分时，需监控两者预测分布的**统计显著性差异**。通过Grafana面板实时展示两个模型的PSI（Population Stability Index）指标，PSI > 0.25时触发告警，提示模型行为差异超出可接受范围。

---

## 常见误区

### 误区一：告警阈值越低越安全

很多团队初期将告警阈值设置得极为敏感，如CPU使用率超过60%即告警，导致每天产生数百条告警，运维人员因"告警疲劳（alert fatigue）"开始忽略通知，真正的P0故障反而被淹没。正确做法是：每条告警必须对应一个**明确的人工响应动作**，无需人工干预的情况不应触发告警，应由自动化系统处理。

### 误区二：仅监控基础设施指标忽略模型质量指标

GPU利用率正常、推理延迟达标，并不意味着AI系统运行良好。2021年多家推荐系统公司的案例表明，特征管道中某个字段静默置零导致模型输入分布剧变，但所有基础设施指标均显示绿灯，直至业务指标下滑15%才被发现。根因追溯耗时4小时，若事先配置了特征均值异常告警，可在30分钟内定位。

### 误区三：混淆监控与日志的职责边界

监控系统（Prometheus+Grafana）处理的是**聚合时序数值**（如每分钟请求总数），不适合存储原始请求内容；日志系统（ELK/Loki）处理的是**结构化事件记录**，不适合做实时指标计算。将大量原始日志写入Prometheus会导致基数爆炸（cardinality explosion）——当标签组合超过百万级时，Prometheus内存消耗会呈指数级增长，这是新手最常见的性能陷阱。

---

## 知识关联

**前置基础**：学习本概念需要掌握**日志与监控**的基础知识，特别是理解指标（Metrics）、日志（Logs）、追踪（Traces）三者在可观测性体系中的不同数据形态与存储方式，以及Prometheus的数据模型（counter、gauge、histogram、summary四种指标类型的适用场景）。

**延伸方向**：掌握监控与告警后，**Service Mesh**（如Istio）可将告警能力扩展至服务间通信层，自动采集mTLS流量的延迟与错误率，无需修改应用代码即可获得全链路监控覆盖。**日志聚合**（如Loki、ELK Stack）则与监控形成互补——当Prometheus告警触发后，运维人员需要通过日志聚合系统钻取该时段的原始事件，完成从"发现问题"到"定位根因"的完整闭环。三者共同构成AI系统可观测性（Observability）的完整技术栈。
