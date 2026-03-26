---
id: "service-mesh"
concept: "Service Mesh"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 5
is_milestone: false
tags: ["istio", "envoy", "sidecar"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Service Mesh（服务网格）

## 概述

Service Mesh 是一种专门处理微服务间通信的基础设施层，通过在每个服务实例旁边部署一个轻量级代理（称为 Sidecar）来拦截和管理所有网络流量，而无需修改应用程序代码。与传统的在应用层实现服务发现、负载均衡的方式不同，Service Mesh 将这些网络关注点下移到独立的基础设施层，使业务代码保持纯粹。

Service Mesh 的概念由 Buoyant 公司的 William Morgan 在 2017 年正式提出并命名，随后 Google、IBM 和 Lyft 联合发布了 Istio 0.1 版本（2017 年 5 月），将 Service Mesh 推向主流工程实践。其底层数据平面代理通常基于 Envoy（由 Lyft 开发），每个 Sidecar 代理处理服务的入站和出站流量，形成一张覆盖整个微服务架构的"网格"。

在 AI 工程的 MLOps 场景中，Service Mesh 解决了 AI 系统特有的痛点：模型推理服务需要金丝雀发布来安全上线新模型版本，特征存储与训练服务之间需要 mTLS 加密，以及跨数十个微服务的分布式追踪对调试数据管道至关重要。

## 核心原理

### 数据平面与控制平面的分离架构

Service Mesh 采用两层架构。**数据平面**由所有 Sidecar 代理实例构成，以 Istio 为例，每个 Pod 中注入一个 Envoy 代理容器，该代理通过 iptables 规则（REDIRECT 模式，端口 15001 拦截出站，15006 拦截入站）劫持所有进出 Pod 的 TCP 流量。**控制平面**在 Istio 1.5 版本后合并为单一的 `istiod` 进程，包含 Pilot（服务发现与路由规则下发）、Citadel（证书管理）和 Galley（配置验证）三个子组件，通过 xDS API（包括 CDS、EDS、LDS、RDS）将配置推送到各 Envoy 代理。

### 流量管理的细粒度控制

Istio 通过 `VirtualService` 和 `DestinationRule` 两种 CRD 实现声明式流量管理。`VirtualService` 定义路由规则，例如将 90% 流量导向模型 v1、10% 流量导向模型 v2，实现金丝雀发布；`DestinationRule` 定义目标服务的负载均衡策略（如 ROUND_ROBIN、LEAST_CONN）、连接池大小和熔断阈值。熔断配置示例：`consecutiveGatewayErrors: 5` 表示连续 5 次网关错误后触发熔断，`baseEjectionTime: 30s` 表示驱逐时间为 30 秒。此外，`ServiceEntry` 允许将外部服务（如第三方 AI API）注册到网格中统一管理。

### 可观测性：指标、追踪与日志的三位一体

每个 Envoy Sidecar 自动采集四类黄金指标：请求量（`istio_requests_total`）、延迟（`istio_request_duration_milliseconds`）、错误率和流量字节数，无需业务代码埋点。分布式追踪方面，Istio 与 Jaeger 或 Zipkin 集成，通过在 HTTP Header 中传播 `x-b3-traceid`、`x-b3-spanid` 等 B3 追踪头实现跨服务链路追踪——应用程序唯一需要做的就是转发这几个 Header。Kiali 是 Istio 专属的拓扑可视化工具，能实时渲染服务间调用图并标注健康状态，对于理解 AI 推理链路中的瓶颈服务尤为有效。

### 安全：mTLS 与 RBAC 授权

Istio 的 `PeerAuthentication` CRD 可以在整个命名空间或单个服务级别强制启用 mTLS（STRICT 模式），此时服务间通信的 TLS 握手和证书轮换完全由 istiod 的 Citadel 组件自动管理，证书有效期默认为 24 小时并自动续签。`AuthorizationPolicy` CRD 实现服务级 RBAC，例如可以精确配置"只允许特征服务访问模型仓库服务的 GET /model 接口"，防止内部服务越权访问。

## 实际应用

**AI 模型的渐进式发布**：在 KServe 部署的推理服务上，通过 `VirtualService` 将新模型版本的流量从 5% 逐步提升到 100%，同时监控 `istio_request_duration_milliseconds_bucket` 中 P99 延迟是否超过 SLA（如 200ms），若超出则自动回滚——整个过程无需重新部署服务。

**多租户 AI 平台的安全隔离**：在共享 GPU 集群上，不同租户的推理服务部署在不同命名空间，通过 `AuthorizationPolicy` 配合 `PeerAuthentication` STRICT 模式，确保租户 A 的特征数据服务不可能被租户 B 的服务访问，满足数据合规要求。

**数据管道的故障注入测试**：使用 Istio 的 `VirtualService` 故障注入能力（`fault.delay` 注入 5 秒延迟，`fault.abort` 注入 HTTP 503 错误），在不停机的情况下测试数据预处理服务的超时重试逻辑是否健壮。

## 常见误区

**误区一：Service Mesh 等同于 API Gateway**。API Gateway 处理南北向流量（外部客户端到服务），通常部署在集群边缘；Service Mesh 处理东西向流量（服务间通信），部署在集群内部每个 Pod 旁边。两者职责不同，Istio 的 `Ingress Gateway` 可以承担部分 API Gateway 职能，但内部 Sidecar 代理不处理集群外部的原始请求。

**误区二：Sidecar 注入对性能的影响可忽略不计**。实际测量显示，Envoy Sidecar 在每次请求中增加约 0.2~0.5ms 的额外延迟，CPU 开销约为每 1000 RPS 消耗 0.5 个 vCPU。对于高频推理服务（如每秒数万次请求），这一开销不可忽视，需要权衡可观测性收益与性能代价，部分场景可选用更轻量的 Ambient Mesh（Istio 1.22 GA）模式替代传统 Sidecar 模式。

**误区三：启用 Service Mesh 后应用自动获得全部可观测性**。Istio 的分布式追踪依赖应用程序手动转发 B3 追踪 Header（`x-b3-traceid` 等），若应用不转发这些 Header，追踪链路会在该服务处断开，无法形成完整的跨服务调用链。很多团队部署 Istio 后发现 Jaeger 中的追踪只有单跳，正是因为遗漏了这个关键步骤。

## 知识关联

Service Mesh 以 **Kubernetes** 为运行基础，istiod 通过 Kubernetes Admission Webhook 自动向打了 `istio-injection: enabled` 标签的命名空间中的 Pod 注入 Sidecar 容器，并利用 Kubernetes Service 和 Endpoint 对象作为服务发现的数据来源。若对 Pod 生命周期和命名空间隔离机制不熟悉，理解 Sidecar 注入的工作方式会有困难。

在可观测性维度，Service Mesh 与**监控与告警**体系深度集成：Envoy 暴露的 Prometheus 格式指标（路径 `/stats/prometheus`，端口 15090）直接被 Prometheus 抓取，再通过预置的 Grafana Dashboard（如 Istio Service Dashboard）展示服务健康状况。Service Mesh 提供的黄金指标是在 Prometheus + Alertmanager 告警规则中配置 SLO 告警的数据来源，两个知识模块在 AI 系统的生产运维中形成完整的可观测性闭环。