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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 服务发现

## 概述

服务发现（Service Discovery）是分布式系统中服务实例动态定位的机制，解决了"客户端如何找到服务端IP和端口"这一根本问题。在单体架构时代，服务地址是静态配置的，而在微服务架构中，服务实例数量动态变化、IP地址由容器编排系统（如Kubernetes）随机分配，静态配置文件完全无法应对这种动态性。服务发现机制通过维护一个实时更新的服务注册表来解决这一问题。

服务发现的概念随微服务架构的普及而成熟，Netflix在2012年开源的Eureka是最早被广泛使用的服务发现组件之一。2014年前后，随着Docker容器技术爆发，Consul（HashiCorp，2014年发布）和etcd（CoreOS，2013年发布）相继成为主流。在AI工程领域，当模型推理服务、特征工程服务、向量数据库服务等多个组件协同工作时，服务发现是实现动态扩缩容的必要前提。

服务发现的重要性在于：推理服务的实例数量会随请求负载动态伸缩，一个GPU推理节点宕机后新实例在几秒内启动并注册，调用方无需人工干预即可感知变化。没有服务发现，AI推理集群的弹性扩缩容只能停留在理论层面。

## 核心原理

### 服务注册与注册表

服务发现的基础是**服务注册表（Service Registry）**，本质是一个键值数据库，存储格式通常为：

```
服务名 → [(IP1:Port1, 元数据1, TTL1), (IP2:Port2, 元数据2, TTL2), ...]
```

服务实例启动时向注册表写入自身信息，这一过程称为**服务注册**。注册方式分两种：
- **自注册模式（Self-Registration）**：服务进程自己调用注册中心API完成注册，如Spring Boot应用启动时自动调用Eureka注册接口。
- **第三方注册模式（Third-Party Registration）**：由部署平台（如Kubernetes的Endpoint Controller）代劳，服务代码本身对注册中心无感知。

每条注册记录通常携带**TTL（Time-To-Live）**，Consul的默认TTL为15秒，服务实例必须每隔一定时间发送心跳续约，否则注册表将自动删除该条目，防止"僵尸服务"积压。

### 客户端发现 vs 服务端发现

这是服务发现架构中最重要的设计分叉点：

**客户端发现（Client-Side Discovery）**：客户端直接查询注册中心获取实例列表，自行执行负载均衡算法（轮询、最少连接等）选定目标实例后直连。Netflix Ribbon采用此模式，优点是客户端掌控路由逻辑，延迟低；缺点是每种语言的客户端都要实现相同的发现逻辑，维护成本高。

**服务端发现（Server-Side Discovery）**：客户端请求统一打向负载均衡器（如AWS ALB或Nginx），由负载均衡器查询注册中心并转发请求。Kubernetes的Service资源配合kube-proxy实现的就是此模式，客户端只需知道一个稳定的虚拟IP（ClusterIP），与服务发现的复杂性完全解耦。

### 健康检查机制

注册表的价值取决于数据的准确性，因此健康检查是服务发现不可分割的组成部分。Consul提供三种健康检查方式：
1. **HTTP Check**：定期GET一个健康检查端点（如`/health`），期望返回200状态码。
2. **TCP Check**：仅验证端口是否可建立TCP连接。
3. **TTL Check**：服务主动上报自身健康状态，超时未上报则判定不健康。

Kubernetes则使用**Liveness Probe**和**Readiness Probe**双探针机制：Liveness决定是否重启容器，Readiness决定是否将Pod加入Service的Endpoints列表，后者直接影响服务发现结果。一个推理服务Pod可能存活但模型尚未加载完成，此时Readiness Probe失败可确保流量不被路由到未就绪实例。

### DNS-based服务发现

Kubernetes的Service DNS是DNS-based服务发现的典型实现。集群内CoreDNS为每个Service自动创建DNS记录，格式为：

```
<service-name>.<namespace>.svc.cluster.local
```

查询该域名返回的是Service的ClusterIP，而非具体Pod IP。这种方式将服务发现的复杂性完全隐藏在DNS协议后面，任何能发起DNS查询的程序都可以实现服务发现，与编程语言无关。

## 实际应用

**AI推理集群的动态扩缩容**：在一个典型的LLM推理服务中，模型推理Pod由HPA（Horizontal Pod Autoscaler）根据GPU利用率自动扩缩。新推理Pod启动并通过Readiness Probe后，Kubernetes自动将其IP加入Service的Endpoints，请求立即被路由到新实例。整个过程从Pod就绪到接收流量通常在5秒以内，无需修改任何配置文件。

**多模型服务路由**：在构建多模型推理平台时，不同版本的模型（如`model-v1`、`model-v2`）注册为不同的服务名称，通过服务发现实现金丝雀发布——先将5%流量路由到`model-v2`服务，观察错误率和延迟后逐步扩大比例。Istio的VirtualService结合服务注册表可以精确实现这种流量分配。

**特征服务的故障隔离**：在在线推理管道中，特征工程服务通常部署多个实例。若其中一个实例的健康检查连续失败3次，Consul会将其标记为unhealthy并从服务发现结果中排除，调用方自动感知并绕开故障实例，实现对上游服务透明的故障转移。

## 常见误区

**误区一：服务发现只是负载均衡的另一种说法**

服务发现和负载均衡是两个不同层次的概念。服务发现解决"知道去哪里"的问题——获取可用实例列表；负载均衡解决"具体选哪个"的问题——从列表中按算法选一个。客户端发现模式下两者由客户端合并实现，但在服务端发现模式下，服务发现由注册中心负责，负载均衡由独立的负载均衡器负责，它们的职责是分离的。

**误区二：Kubernetes环境下不需要独立的服务发现组件**

Kubernetes内置的Service DNS适用于集群内服务调用，但在以下场景下仍需独立服务发现方案：跨集群服务调用、集群外的传统应用需要调用集群内服务、需要携带自定义元数据（如GPU型号、模型版本）进行服务筛选。此时Consul或自研注册中心仍有必要。

**误区三：注册中心可用性要求和普通业务服务相同**

注册中心是整个微服务集群的基础设施，其不可用将导致所有新启动的服务无法注册、所有服务发现查询失败。因此注册中心必须以高可用模式部署——Consul推荐至少3个Server节点以满足Raft共识算法的容错要求（可容忍1个节点故障），而不能单点部署。

## 知识关联

**前置知识衔接**：微服务入门中学习到的服务拆分原则直接产生了服务发现的需求。单体应用内部方法调用不存在网络寻址问题，正是拆分为独立进程部署后，服务间调用才需要动态地址解析机制。CAP理论是理解注册中心数据一致性取舍的基础——Consul默认强一致（CP），Eureka选择可用性（AP），在网络分区时Eureka继续提供可能过时的注册信息而Consul拒绝读写。

**横向关联概念**：服务发现与API网关紧密配合——API网关通常是服务端发现模式的流量入口，它从注册中心获取后端服务列表后执行路由。服务发现与配置中心（如Apollo、Consul KV）经常共用同一基础设施，Consul本身同时提供服务注册和KV存储两种能力。在服务网格（Service Mesh）中，Istio的控制平面xDS协议将服务发现结果推送给每个Pod旁的Envoy sidecar代理，是服务发现机制的进一步演进形式。