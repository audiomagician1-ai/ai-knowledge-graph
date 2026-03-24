---
id: "service-discovery"
concept: "服务发现"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 7
is_milestone: false
tags: ["微服务"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 服务发现

## 概述

服务发现（Service Discovery）是分布式系统中动态定位服务实例网络地址的机制。在微服务架构中，每个服务实例的 IP 地址和端口号会随着容器调度、弹性伸缩、故障重启而频繁变化，服务发现系统负责维护一个实时更新的服务注册表，使得调用方无需硬编码目标地址，而是通过逻辑名称（如 `user-service`）查询并获得当前可用的实例列表。

这一机制起源于 2013 年前后微服务架构的规模化实践。Netflix 为解决其数百个微服务之间的地址管理问题，开发并开源了 Eureka（2012 年），成为服务发现领域的奠基性工具。此后 HashiCorp Consul（2014 年）、CoreOS etcd 以及 Kubernetes 内置的 kube-dns/CoreDNS 相继出现，形成了今天多样化的技术栈。

在 AI 工程系统中，服务发现尤为关键：模型推理服务（如多个 GPU 实例上运行的 TensorFlow Serving）需要根据负载动态扩缩容，若没有自动化的服务发现，API 网关每次实例变更都需要手动更新路由表，这在每日部署频率超过数十次的 CI/CD 流水线中是不可接受的。

---

## 核心原理

### 服务注册：主动注册与第三方注册

服务发现的前提是服务注册，有两种主流模式：

- **自注册模式（Self-Registration）**：服务实例启动时主动向注册中心发送 HTTP POST 请求，携带自身的 `host`、`port`、`serviceId` 和健康检查端点。Eureka Client 默认每 30 秒向 Eureka Server 续约一次心跳，若连续 3 次未续约则被标记为下线，实例会在 90 秒后从注册表删除。
- **第三方注册模式（Third-Party Registration）**：由外部 Registrar 进程（如 Kubernetes 控制器或 Registrator 工具）监听容器启动事件并代替服务写入注册中心，服务本身无需包含任何注册逻辑。Kubernetes 的 Endpoints 对象正是由 Endpoints Controller 自动维护的，反映所有 Ready 状态 Pod 的 IP 列表。

### 客户端发现与服务端发现

两种发现模式决定了负载均衡的位置：

**客户端发现（Client-Side Discovery）**：调用方直接查询注册中心，获取全量实例列表后在本地执行负载均衡算法（轮询、加权随机等），然后直接连接目标实例。Netflix Ribbon 是典型实现，它将 Eureka 的实例列表缓存在本地，每隔 30 秒刷新一次，减少对注册中心的压力。公式上，客户端选择实例的加权轮询可以表示为：

$$
\text{selected\_index} = \arg\max_{i} \left( w_i - \sum_{j<i} w_j \cdot \lfloor \text{count} / W \rfloor \right)
$$

其中 $w_i$ 为第 $i$ 个实例的权重，$W$ 为总权重。

**服务端发现（Server-Side Discovery）**：调用方将请求发送给负载均衡器（如 AWS ALB 或 Kubernetes Service），由负载均衡器查询注册中心并转发请求。客户端完全不感知后端实例数量，代价是多一次网络跳转（通常增加 1-5 ms 延迟）。

### 健康检查与一致性保障

服务注册中心必须持续验证实例健康状态，避免将流量路由到失效节点。健康检查有三种形式：

1. **TTL（Time-To-Live）心跳**：实例定期发送 keepalive 消息，Consul 默认 TTL 为 15 秒。
2. **HTTP 健康检查**：注册中心主动 GET 实例的 `/health` 端点，期望返回 200 状态码。
3. **TCP 检查**：仅验证端口可达性，适用于非 HTTP 服务（如 Redis、gRPC 服务）。

注册中心自身的高可用同样重要。Consul 使用 Raft 共识算法，在 3 节点集群下可容忍 1 节点故障，在 5 节点集群下可容忍 2 节点故障。Raft 要求写操作必须得到 `⌊N/2⌋ + 1` 个节点的确认，因此 3 节点 Consul 集群的写吞吐量约为单节点的 60-70%。

### DNS 与 API 两种查询接口

Consul 同时支持 DNS 接口（`user-service.service.consul`，默认端口 8600）和 HTTP API 接口（`GET /v1/health/service/user-service`）。DNS 方式兼容所有语言和框架，无需引入 SDK；HTTP API 方式可获取更丰富的元数据（版本标签、数据中心、健康状态细节），适合需要灰度发布或蓝绿部署的场景。

---

## 实际应用

**AI 推理集群的弹性扩缩容**：在 Kubernetes 上部署的 TensorFlow Serving 集群，通过 HPA（Horizontal Pod Autoscaler）在 GPU 利用率超过 70% 时自动扩容。新 Pod 就绪后，Kubernetes Endpoints Controller 在约 5 秒内将其 IP 写入 Endpoints 对象，kube-proxy 更新 iptables 规则后，API 网关即可将推理请求路由到新实例——整个过程无需任何人工干预。

**多版本模型的灰度发布**：使用 Consul 的服务标签（Tag）功能，将运行 BERT-v1 的实例标记为 `version:v1`，运行 BERT-v2 的实例标记为 `version:v2`。调用方通过查询 `GET /v1/health/service/bert-service?tag=v2` 仅获取 v2 实例列表，实现按标签过滤的精准路由，支持 A/B 测试。

**跨数据中心服务发现**：Consul 支持 WAN Federation，允许在北京和上海两个数据中心之间进行跨中心服务查询（`user-service.service.beijing.consul`），结合就近访问策略将跨区调用的平均延迟从 30 ms 降低到 5 ms 以内。

---

## 常见误区

**误区一：把服务发现等同于负载均衡**

服务发现解决的是"在哪里"的问题（定位可用实例地址），负载均衡解决的是"选哪个"的问题（流量分配策略）。二者经常协同工作，但概念独立。Nginx 可以做负载均衡但没有内置的动态服务发现；Eureka 提供服务发现但本身不做流量转发，需要 Ribbon 配合才能实现客户端负载均衡。

**误区二：认为注册表中的地址实时精确**

注册中心维护的实例列表存在一定的延迟窗口。以 Eureka 为例，由于有 30 秒的心跳间隔和最长 90 秒的剔除延迟，加上客户端本地缓存 30 秒刷新，一个实例从崩溃到被所有客户端感知最长可能需要 **2 分钟**。因此服务调用方必须实现重试（retry）和熔断（circuit breaker）逻辑，而不能假设服务发现返回的地址一定可达。

**误区三：Kubernetes 的 Service 已经足够，不需要独立的服务发现组件**

Kubernetes Service 通过虚拟 IP（ClusterIP）和 kube-proxy 提供了集群内的基础服务发现，但它有明显局限：不支持跨集群发现、不提供细粒度健康状态查询（仅能区分 Ready/NotReady）、无法按自定义标签过滤实例。在多集群 AI 平台、混合云部署或需要精细流量控制的场景中，仍需引入 Consul 或 Istio Service Registry 等专用组件。

---

## 知识关联

**与微服务入门的衔接**：微服务架构将单体应用拆分为多个独立部署的服务，正是这种拆分导致服务实例地址从"静态配置文件"变成了"动态变化的运行时信息"，服务发现是解决这一衍生问题的直接方案。理解微服务中的"服务边界"和"独立部署"概念，是正确设计服务注册粒度（以服务为单位还是以实例为单位）的前提。

**向后延伸的技术方向**：掌握服务发现后，可以进一步学习服务网格（Service Mesh）——Istio 的 Pilot 组件本质上是一个更高级的服务发现系统，它将发现的实例信息通过 xDS API 下发给 Envoy Sidecar，实现了服务发现、负载均衡、熔断、流量染色的统一控制面，是服务发现在大规模 AI 基础设施中的演进形态。API 网关的路由规则配置也高度依赖服务发现提供的实时实例信息。
