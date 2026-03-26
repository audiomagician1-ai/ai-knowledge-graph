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
quality_tier: "B"
quality_score: 48.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
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

蓝绿部署（Blue-Green Deployment）是一种通过维护两套完全相同的生产环境来实现零停机发布的策略，由 Jez Humble 和 David Farley 在2010年出版的《持续交付》一书中系统阐述。其核心机制是：始终保持一个环境（蓝环境）运行当前生产版本，另一个环境（绿环境）部署并验证新版本，通过切换负载均衡器的路由目标完成版本升级。整个流量切换过程通常在数秒内完成，用户几乎感知不到服务中断。

蓝绿部署在 AI 工程的模型服务场景中尤为重要。当一个大语言模型从 v1 升级到 v2 时，新旧模型在推理结果上可能存在根本差异，不能像普通 Web 应用那样接受部分节点仍运行旧逻辑。蓝绿部署确保在任意时刻所有请求只命中同一个版本的模型服务，避免同一用户会话在不同请求中得到截然不同的响应结果。

## 核心原理

### 双环境对称架构

蓝绿部署要求两套环境在计算资源、网络配置、中间件版本上完全对称。以 Kubernetes 为例，通常用两个独立的 Deployment 资源分别命名为 `model-service-blue` 和 `model-service-green`，两者共享同一个 Service 对象，但 Service 的 `selector` 标签在某一时刻只指向其中一个 Deployment 的 Pod。流量切换等价于将 `kubectl patch service model-service -p '{"spec":{"selector":{"slot":"green"}}}'` 这一原子操作，整个切换延迟通常小于 1 秒。

### 路由切换与回滚机制

蓝绿部署的回滚代价极低，这是它区别于原地升级（In-place Upgrade）的关键优势。由于旧版本（蓝环境）在切换后仍然保持运行状态，一旦绿环境出现 P0 故障，只需将 Service selector 重新指向蓝环境，回滚时间等同于一次路由切换，通常在 30 秒以内，而原地升级的回滚需要重新拉取旧镜像并重启所有 Pod，往往需要数分钟。

### 健康检查与流量切换前验证

在将生产流量切换到绿环境之前，必须通过内部流量（如 `curl http://green-service:8080/health`）验证新版本的就绪状态。对于 AI 模型服务，验证不仅包括 HTTP 200 响应，还应包含冒烟推理测试——向绿环境发送标准测试输入并断言输出结果在预期误差范围（如分类置信度偏差不超过 0.05）以内。Kubernetes 的 `readinessProbe` 可自动阻止未通过健康检查的 Pod 接收流量，与蓝绿切换机制配合使用可构成双重保险。

### 数据库兼容性约束

蓝绿部署中最复杂的问题是数据库 Schema 兼容性。当蓝绿两套服务共享同一数据库时，切换期间数据库必须同时兼容新旧两个版本的写入格式。标准做法是采用"扩展-迁移-收缩"三阶段策略：先部署能同时读写新旧 Schema 的绿版本，确认蓝版本流量清零后，再执行删除旧字段的 Schema 清理操作。跳过兼容阶段直接修改 Schema 会导致蓝环境服务崩溃，这是蓝绿部署失败的最常见原因之一。

## 实际应用

**AI 模型版本升级场景**：以 PyTorch 模型服务为例，蓝环境运行 `resnet50-v1` 镜像提供图像分类服务，绿环境部署 `resnet50-v2` 镜像。在 Kubernetes 中创建绿环境的 Deployment 并等待所有副本 Ready 后，通过修改 Service selector 完成切换。切换后保留蓝环境至少 24 小时，以便在出现线上异常（如新模型对特定输入的推理延迟超过 SLA 阈值 200ms）时快速回滚。

**CI/CD 流水线集成**：在 GitHub Actions 或 Jenkins 流水线中，蓝绿部署通常实现为：构建新镜像 → 推送到镜像仓库 → 更新非活跃槽（inactive slot）的 Deployment → 执行集成测试 → 通过则切换路由 → 失败则删除非活跃槽的新镜像并报警。这一流程要求流水线能够查询当前活跃槽的标识，可通过读取 Kubernetes ConfigMap 中存储的 `active-slot: blue` 字段实现。

**金丝雀发布与蓝绿部署的配合使用**：对于高风险的 AI 模型升级，可先用金丝雀发布将 5% 流量引导至绿环境，观察关键指标（错误率、P99 延迟、模型预测分布偏移）稳定后，再执行完整的蓝绿切换。这种组合策略在 Netflix、Airbnb 等公司的 ML 平台中有广泛应用。

## 常见误区

**误区一：认为蓝绿部署必须使用两倍资源**。许多团队因资源成本而放弃蓝绿部署，实际上绿环境只需在发布窗口期间存在。对于 GPU 资源紧张的 AI 推理服务，可以在发布前临时扩容绿环境，流量切换完成并确认稳定（通常 1-2 小时）后即回收蓝环境资源，将额外资源消耗控制在整个发布生命周期的 10% 以内。

**误区二：混淆蓝绿部署与滚动更新（Rolling Update）**。Kubernetes 默认的 `RollingUpdate` 策略是逐步替换旧 Pod，在升级过程中新旧版本 Pod 同时提供服务。这对于 AI 模型服务是不可接受的——两个版本的模型可能对同一输入产生不同输出，导致同一用户会话内的响应前后不一致。蓝绿部署通过路由层的原子切换彻底避免了这种版本混用状态。

**误区三：忽略有状态服务的会话粘滞问题**。若 AI 服务维护了多轮对话上下文（存储在蓝环境本地内存中），切换到绿环境后这些状态将丢失。正确的做法是将会话状态外置到 Redis 等共享存储，在切换前确认所有活跃会话已超时或完成，或在切换时主动通知客户端重建会话。

## 知识关联

蓝绿部署建立在 **CI/CD 持续集成**的基础之上——只有流水线能够可靠地构建、测试、推送不可变镜像，蓝绿部署的自动化切换才有意义。没有 CI/CD 保障的蓝绿部署退化为手动操作，会引入人为错误风险。**Kubernetes 入门**知识是实施蓝绿部署的技术前提，理解 Deployment、Service、selector 机制才能正确实现路由切换逻辑；Kubernetes 的 `kubectl rollout` 命令虽提供了滚动更新，但实现真正的蓝绿部署需要在其之上手动管理双 Deployment 架构或使用 Argo Rollouts 等专用工具。掌握蓝绿部署后，可进一步学习金丝雀发布的流量权重控制（如按 5%/20%/100% 梯度放量）以及 A/B 测试框架，这些策略共同构成 MLOps 中模型上线的渐进式发布体系。