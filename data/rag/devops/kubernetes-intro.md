---
id: "kubernetes-intro"
concept: "Kubernetes入门"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 7
is_milestone: false
tags: ["编排"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.424
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Kubernetes入门

## 概述

Kubernetes（简称K8s）是由Google于2014年开源的容器编排系统，其前身是Google内部运行超过十年的Borg系统。K8s这一缩写来自"K"与"s"之间恰好有8个字母的命名规律。它解决了在生产环境中手动管理数百乃至数千个容器时面临的部署、扩缩容、故障恢复与服务发现等核心难题。

相比Docker Compose仅适用于单机多容器编排的局限，Kubernetes天然支持多节点集群，能够跨物理机或云主机调度容器工作负载。在AI工程场景中，GPU训练任务、模型推理服务、特征计算Pipeline往往需要弹性扩缩容与资源隔离，这正是Kubernetes的核心能力所在。

Kubernetes于2016年成为Cloud Native Computing Foundation（CNCF）的首个项目，目前最新稳定版本已进入v1.3x系列，每年发布三到四个次要版本。掌握Kubernetes不仅是部署模型服务的必要技能，也是后续学习Helm Charts、Service Mesh等高级主题的前提。

---

## 核心原理

### 控制平面与工作节点的架构分层

Kubernetes集群由**控制平面（Control Plane）**和**工作节点（Worker Node）**两类角色构成。控制平面包含四个关键组件：
- **kube-apiserver**：集群的唯一入口，所有kubectl命令和内部组件通信均通过REST API访问它；
- **etcd**：分布式键值存储，保存整个集群的状态数据，生产环境通常部署为3或5节点的etcd集群以保证高可用；
- **kube-scheduler**：基于资源请求（requests）、节点亲和性（affinity）等策略将Pod分配到合适节点；
- **kube-controller-manager**：运行Deployment、ReplicaSet等控制器的循环逻辑，持续将**实际状态**驱动至**期望状态**。

工作节点上运行**kubelet**（与控制平面通信并管理容器生命周期）、**kube-proxy**（维护iptables或IPVS规则实现Service负载均衡）以及容器运行时（如containerd）。

### Pod、Deployment与ReplicaSet的层次关系

**Pod**是Kubernetes的最小调度单位，封装一个或多个共享网络命名空间和存储卷的容器。Pod本身是不稳定的——节点宕机后Pod不会自动重建，因此实际工作中几乎不直接创建裸Pod。

**ReplicaSet**通过`replicas`字段维持指定数量的Pod副本，当某个Pod异常终止时，控制器会立即创建替代Pod。**Deployment**在ReplicaSet之上增加了滚动更新（Rolling Update）能力：默认策略下，`maxSurge=25%`（可多创建的Pod比例）与`maxUnavailable=25%`（可同时不可用的Pod比例）共同控制更新节奏，确保服务零中断升级。

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### Service与Ingress的网络访问机制

Pod的IP地址在重建后会改变，因此Kubernetes引入**Service**作为稳定的访问入口。Service通过**Label Selector**匹配目标Pod，类型包括：
- `ClusterIP`（仅集群内访问，默认类型）；
- `NodePort`（在每个节点的30000-32767端口暴露服务）；
- `LoadBalancer`（由云厂商创建外部负载均衡器）。

**Ingress**资源配合Ingress Controller（如Nginx Ingress或Traefik）实现基于HTTP路径或域名的七层路由，例如将`/api/predict`转发至推理服务，将`/metrics`转发至监控服务。这是将AI推理API暴露给外部调用方的标准做法。

### 资源配额：requests与limits

Kubernetes用两个字段控制容器资源使用：`requests`是调度器分配节点时参考的保证量，`limits`是容器运行时的上限。典型的GPU推理Pod配置：

```yaml
resources:
  requests:
    memory: "4Gi"
    nvidia.com/gpu: "1"
  limits:
    memory: "8Gi"
    nvidia.com/gpu: "1"
```

若容器内存使用超过`limits`，内核会触发OOMKill；若CPU超过`limits`，则被限速（throttle）而非终止。未设置`requests`时，Pod默认被标记为`BestEffort` QoS类，资源紧张时最先被驱逐。

---

## 实际应用

**AI模型推理服务的水平扩缩容**：将TensorFlow Serving或Triton Inference Server打包为容器镜像，通过Deployment部署3个副本，配合Horizontal Pod Autoscaler（HPA）设定当CPU利用率超过60%时自动扩容，最大副本数设为10。HPA每隔15秒（默认）查询Metrics Server获取指标并作出决策。

**ConfigMap与Secret管理模型配置**：模型服务的参数（如批量大小、超时阈值）存放在ConfigMap中，API密钥或数据库凭证存放在Secret（Base64编码存储，建议配合外部Secret管理工具如Vault）。两者均可以环境变量或文件挂载形式注入容器，修改ConfigMap后可通过滚动重启使配置生效：`kubectl rollout restart deployment/inference-server`。

**命名空间隔离多团队环境**：在同一集群中，用`namespace: team-nlp`和`namespace: team-cv`分别隔离NLP团队和CV团队的工作负载，配合ResourceQuota限制每个命名空间可申请的CPU总量（如`limits.cpu: "40"`），防止某团队的训练任务耗尽集群资源。

---

## 常见误区

**误区一：将Deployment的`replicas`设为1等同于高可用**
单副本Deployment在节点发生故障时，控制器需要感知节点不可达（默认需等待约5分钟的`node.kubernetes.io/not-ready`容忍时间）才会重新调度Pod，期间服务完全中断。生产环境的推理服务至少应设置2-3个副本，并配合`podAntiAffinity`规则确保副本分散在不同节点上。

**误区二：混淆容器的`command`覆盖与Dockerfile的`ENTRYPOINT`关系**
Kubernetes YAML中的`command`字段对应Dockerfile的`ENTRYPOINT`（完全覆盖），`args`字段对应`CMD`。许多初学者认为`command`是在镜像原有入口点之后追加命令，导致容器启动行为与预期不符，尤其在调试模型服务启动脚本时频繁出现此类问题。

**误区三：直接kubectl apply修改生产集群而不经过版本控制**
Kubernetes提供了声明式API，所有YAML清单文件应纳入Git管理，通过CI/CD流水线应用变更。直接`kubectl edit`或`kubectl set image`修改生产资源会导致配置漂移（Configuration Drift），集群实际状态与代码仓库描述不一致，给后续Helm Charts和GitOps工作流的引入造成阻碍。

---

## 知识关联

**与Docker Compose的关键差异**：Docker Compose的`docker-compose.yml`与Kubernetes YAML在概念上有对应关系——`services`对应Deployment+Service，`volumes`对应PersistentVolume，`networks`对应Namespace+NetworkPolicy——但Kubernetes增加了跨节点调度、自愈能力和RBAC权限控制，这些是Compose完全不具备的特性。

**通向Helm Charts**：随着微服务数量增加，手动维护几十个YAML文件的重复配置（如每个服务都需要相似的Deployment+Service+HPA模板）变得难以维护。Helm将这些文件参数化为Chart模板，用`values.yaml`统一管理变量，是Kubernetes之上的包管理器，与apt/pip的定位类似。

**健康检查与就绪探针的前置依赖**：Kubernetes的`livenessProbe`和`readinessProbe`机制建立在Pod生命周期管理之上——只有理解Deployment滚动更新如何判断新Pod是否就绪（Ready状态），才能正确配置HTTP探针的`initialDelaySeconds`和`failureThreshold`参数，避免推理服务在模型权重加载完成前就被纳入Service负载均衡而返回503错误。