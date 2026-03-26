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

Kubernetes（常缩写为K8s，其中"8"代表"ubernete"中的8个字母）是Google于2014年基于内部系统Borg的设计经验开源的容器编排平台，2016年正式捐赠给CNCF（云原生计算基金会）管理。与Docker Compose只能在单台主机上编排容器不同，Kubernetes专为跨多台物理或虚拟机的大规模容器集群设计，能够自动处理容器的调度、扩缩容、故障恢复和滚动更新。

K8s解决的核心问题是：当AI推理服务或训练任务需要在数十乃至数百台机器上稳定运行时，手动管理容器部署已经完全不现实。例如，一个GPU推理集群需要在某节点宕机后30秒内自动将Pod迁移到其他节点，这正是Kubernetes的自愈能力所针对的场景。在AI工程领域，K8s已成为部署模型服务、特征工程流水线和离线批处理任务的标准基础设施。

---

## 核心原理

### 控制平面与工作节点的二层架构

Kubernetes集群由**控制平面（Control Plane）**和**工作节点（Worker Node）**两类角色构成。控制平面包含四个关键组件：`kube-apiserver`负责接收所有REST请求并作为集群的唯一入口；`etcd`是一个分布式键值存储，保存整个集群的状态数据；`kube-scheduler`根据CPU、内存、GPU资源及亲和性规则决定Pod被调度到哪个节点；`kube-controller-manager`运行多个控制器循环，持续将实际状态驱动向期望状态。每个工作节点上运行`kubelet`（负责与控制平面通信并管理本节点Pod的生命周期）和`kube-proxy`（维护节点上的iptables/IPVS规则实现服务路由）。

### Pod——Kubernetes最小调度单元

K8s不直接调度单个容器，而是调度**Pod**。一个Pod是一组共享网络命名空间和存储卷的容器集合，Pod内的容器通过`localhost`直接通信。每个Pod在集群内拥有唯一IP地址，但该IP随Pod重建而改变，因此不应直接用于服务发现。典型的AI服务Pod通常包含一个主推理容器和一个sidecar容器（如日志收集器），两者共享同一网络和`/var/log`挂载点。Pod的资源需求通过`requests`（调度保障）和`limits`（硬上限）两个字段声明：

```yaml
resources:
  requests:
    memory: "2Gi"
    nvidia.com/gpu: "1"
  limits:
    memory: "4Gi"
    nvidia.com/gpu: "1"
```

其中`requests`决定调度器选择节点的依据，`limits`触发OOMKill或CPU throttle。

### Deployment、Service与Namespace的协作

**Deployment**是管理无状态Pod副本的控制器，通过`replicas`字段声明期望副本数，并内置滚动更新策略（`maxSurge`和`maxUnavailable`参数控制更新节奏）。当`replicas: 3`的Deployment中某个Pod崩溃，ReplicaSet控制器会在几秒内创建新Pod补足至3个。

**Service**为一组具有相同标签的Pod提供稳定的虚拟IP（ClusterIP）和DNS名称，解决Pod IP漂移问题。Service类型分为ClusterIP（集群内访问）、NodePort（暴露节点端口，范围30000–32767）、LoadBalancer（云厂商负载均衡器）三种。AI推理服务通常通过`ClusterIP` Service在集群内部被其他微服务调用。

**Namespace**提供资源隔离边界，常见做法是为`dev`、`staging`、`prod`三个环境创建独立Namespace，配合ResourceQuota限制每个环境可使用的CPU和GPU总量，防止开发环境的测试任务抢占生产推理资源。

### 声明式配置与kubectl的工作方式

K8s采用**声明式（Declarative）**而非命令式配置模型：用户在YAML文件中描述期望状态，提交后由控制器持续协调。`kubectl apply -f deployment.yaml`命令将配置提交给apiserver，与etcd中存储的当前状态对比后触发必要变更。常用调试命令包括：`kubectl logs <pod> -c <container>`查看指定容器日志、`kubectl exec -it <pod> -- /bin/bash`进入容器、`kubectl describe pod <pod>`查看事件和资源绑定详情。

---

## 实际应用

**AI模型推理服务部署**：将PyTorch Serving镜像打包后，创建Deployment指定`replicas: 4`和GPU资源需求，配合HorizontalPodAutoscaler（HPA）在GPU利用率超过70%时自动扩容至最多16个副本。通过`ClusterIP` Service暴露8501端口，供前端API网关调用。

**离线批处理任务**：使用Kubernetes的`Job`资源类型（而非Deployment）提交数据预处理或模型批量评估任务，设置`completions: 100`和`parallelism: 10`实现100个任务分批10并行执行，任务完成后Pod自动清理。

**多租户GPU资源管理**：在AI平台中为不同团队创建独立Namespace，用ResourceQuota限制每个团队最多申请8块GPU，避免某个团队的大规模训练任务耗尽集群GPU资源，影响在线推理服务。

---

## 常见误区

**误区一：把Pod当作长期运行的服务单元直接使用**。初学者常直接创建Pod而不使用Deployment，导致Pod故障后无人重建。应当始终通过Deployment、StatefulSet或Job等控制器管理Pod，让控制平面负责维护副本数量和健康状态。

**误区二：混淆`requests`和`limits`的调度含义**。设置`limits`但不设置`requests`时，K8s默认将`requests`等于`limits`，可能导致调度器找不到"资源充足"的节点（即便实际节点使用率很低）而造成Pod挂起（Pending状态）。在GPU场景下这个误区尤为常见。

**误区三：认为Service的ClusterIP等同于容器IP**。ClusterIP是虚拟IP，由kube-proxy通过iptables规则实现负载均衡，不对应任何实际网卡。尝试在节点上`ping`某个ClusterIP地址通常不会得到响应，这并不代表Service配置错误。

---

## 知识关联

学习K8s入门前需要掌握Docker Compose，因为K8s的YAML配置与Compose的`services`定义在结构上有相似性（都描述镜像、端口、环境变量、卷挂载），但K8s引入了控制器、调度器等Compose完全没有的抽象层，两者的资源模型本质不同。

掌握K8s基础后，下一步学习**Helm Charts**——它是K8s的包管理工具，将复杂的多资源YAML模板化，一条命令即可部署含Deployment、Service、ConfigMap的完整AI服务栈。**健康检查与就绪探针**（livenessProbe和readinessProbe）建立在对Pod生命周期的理解之上，是K8s自愈能力的核心实现机制，直接影响滚动更新的零停机效果。**蓝绿部署**则是在K8s中通过操作Service的标签选择器在两组Deployment之间切换流量，实现无损发布的高级运维策略。**Service Mesh**（如Istio）在K8s Service的基础上增加了mTLS、流量镜像和熔断能力，适用于大规模AI微服务集群的可观测性需求。