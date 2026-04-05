---
id: "blue-green-deployment"
concept: "蓝绿部署"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 4
is_milestone: false
tags: ["blue-green", "canary", "zero-downtime"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 蓝绿部署

## 概述

蓝绿部署（Blue-Green Deployment）是一种通过同时维护两套完全相同的生产环境来实现零停机发布的策略。其核心机制是：始终保持"蓝色"（Blue）和"绿色"（Green）两个版本的服务同时存在于基础设施中，流量路由器（通常是负载均衡器或反向代理）在任意时刻只将生产流量指向其中一个版本，另一个版本则处于空闲或预热状态。

这一概念由 Jez Humble 和 David Farley 在2010年出版的《Continuous Delivery》一书中正式系统化描述，成为持续交付实践的经典模式之一。在AI推理服务的部署场景中，蓝绿部署尤其关键——一个PyTorch模型从v1升级到v2时，若采用传统停机替换方式，即便仅有30秒中断，也会导致在线推理请求超时失败；蓝绿部署使得切换可以在DNS层面或Kubernetes Service层面完成，切换耗时可压缩至毫秒级。

与简单的滚动更新不同，蓝绿部署要求两套环境的资源投入几乎翻倍，但换来的是极为干净的回滚路径：发现新版本（绿色）存在问题时，仅需将路由切回蓝色环境，回滚时间通常不超过5秒，远快于重新部署的几分钟或十几分钟。

## 核心原理

### 双环境镜像与流量切换机制

蓝绿部署的技术实现依赖于一个关键不变量：**两套环境必须在任何时间点都具备接收全量生产流量的能力**。在Kubernetes中，这通常通过两个独立的Deployment（如 `model-service-blue` 和 `model-service-green`）加上一个共享的Service资源实现。Service的 `selector` 字段通过标签（Label）决定流量指向哪个Deployment：

```yaml
# 切换到绿色环境只需修改此 selector
selector:
  app: model-service
  slot: green   # 改为 blue 即可回滚
```

流量切换的完整过程：①在绿色环境部署新版模型镜像；②执行健康检查和冒烟测试（通常耗时2~10分钟）；③修改Service selector 完成秒级切换；④蓝色环境保留至少24小时以备回滚。

### 数据库与状态同步的挑战

蓝绿部署最棘手的问题不在计算层，而在数据库Schema兼容性。假设模型服务v2需要新增一张 `inference_cache` 表，若在切换前执行数据库迁移，蓝色（旧版）服务将遭遇不兼容的Schema；若切换后再迁移，则绿色服务在迁移期间功能受限。标准解法是**扩展-收缩（Expand-Contract）模式**：先以向后兼容方式扩展Schema（只加列不删列），完成蓝绿切换并稳定运行后，再执行第二次迁移收缩废弃字段。

对于AI系统中常见的特征存储（Feature Store）或模型元数据数据库，Expand-Contract模式同样适用，且必须严格遵守——跳过这一步骤是蓝绿部署失败的头号原因。

### 流量预热与连接池建立

新绿色环境在首次接收流量时存在"冷启动"风险：JVM类加载、Python模块导入、GPU显存分配、KV缓存填充等操作会导致首批请求延迟激增。解决方案是在切换前向绿色环境发送**镜像流量（Traffic Mirroring）**：Nginx的 `mirror` 指令或Istio的 `VirtualService` 的 `mirror` 字段可将生产请求同步复制一份发往绿色环境，绿色环境处理这些镜像请求但其响应不返回给用户。经过5~15分钟的镜像流量预热后，绿色环境的缓存命中率和平均延迟已接近稳定状态，此时再切换可将延迟抖动降低约70%。

## 实际应用

**大语言模型（LLM）服务版本升级**：某AI公司将其内部部署的LLM从LLaMA-2-7B升级至LLaMA-2-13B时，使用蓝绿部署策略。绿色集群预先分配了8张A100 GPU并完成模型权重加载（加载耗时约4分钟），随后通过Istio的 `VirtualService` 将100%流量瞬间切换至绿色集群，蓝色集群的8张GPU保留待机48小时后释放。整个过程用户端零感知中断。

**推荐系统模型迭代**：电商推荐模型每周更新一次，采用蓝绿部署配合A/B测试：切换前72小时，将10%的流量提前导入绿色环境（这实际上是蓝绿与金丝雀的混合策略），收集CTR等业务指标，确认指标不下降后执行100%切换。注意此时10%流量阶段属于**验证目的**而非逐步灰度，两者有本质区别（详见误区部分）。

**Kubernetes中的完整资源清单**：在生产实践中，每次蓝绿切换都应更新 `ConfigMap` 中记录当前活跃槽位（active slot）的值，便于自动化脚本判断下次部署应刷新哪个颜色的环境，避免覆盖当前活跃版本。

## 常见误区

**误区一：蓝绿部署等同于金丝雀发布**。蓝绿部署是**二元切换**——流量要么100%在蓝色，要么100%在绿色，不存在中间状态。金丝雀发布则是**渐进式灰度**，允许5% → 25% → 100%的流量逐步迁移，并在每个阶段设置自动回滚阈值。混淆二者会导致架构设计错误：如果你需要逐步验证新版本对不同用户群的影响，你需要的是金丝雀发布，蓝绿部署无法提供这种能力。

**误区二：蓝绿部署必然需要双倍成本**。这在物理服务器时代基本成立，但在云原生环境中可以通过**按需扩缩容**大幅降低成本。具体做法是：平时蓝色环境运行10个Pod，绿色环境缩减至0个Pod（仅保留Deployment资源定义）；部署时临时扩容绿色环境至10个Pod，完成切换并验证稳定后，将蓝色环境缩回0个Pod。峰值期间双倍资源占用通常不超过30分钟，额外成本可忽略不计。

**误区三：回滚蓝绿部署一定是安全的**。若新版本（绿色）在运行期间已向数据库写入了旧版本（蓝色）不兼容的数据格式，回滚到蓝色将导致数据读取报错。这是未遵循 Expand-Contract 数据库迁移模式的直接后果。正确做法是：在蓝绿切换的前48小时内，任何数据库变更必须保持双向兼容，确保蓝、绿两个版本都能正确处理期间产生的所有数据。

## 知识关联

蓝绿部署依赖 **CI/CD 流水线**提供自动化触发能力——典型实现是在 GitHub Actions 或 Jenkins 流水线中，将"修改 Kubernetes Service selector"作为流水线的最后一个 Stage，由流水线而非人工操作执行切换，避免人为失误。如果没有 CI/CD 流水线，蓝绿切换很容易因手动步骤遗漏（如忘记更新 ConfigMap 中的活跃槽位记录）而引发生产事故。

**Kubernetes** 是蓝绿部署最自然的执行平台：Deployment、Service、Label Selector 三个原语组合即可实现完整的蓝绿切换，无需额外工具。进阶场景中，Argo Rollouts 这一Kubernetes CRD扩展提供了声明式的蓝绿部署支持，可配置 `autoPromotionEnabled: false` 要求人工审批后再执行流量切换，适合对模型质量有严格把控需求的AI团队。掌握蓝绿部署后，实践者通常会进一步研究**渐进式交付（Progressive Delivery）**框架，将蓝绿部署与金丝雀发布、功能开关（Feature Flag）结合使用，构建更精细化的发布控制体系。