---
id: "cloud-basics"
concept: "云服务基础(AWS/GCP)"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 4
is_milestone: false
tags: ["云"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 云服务基础（AWS/GCP）

## 概述

Amazon Web Services（AWS）于2006年正式推出S3存储服务和EC2计算服务，被公认为现代云计算的起点。Google Cloud Platform（GCP）于2008年推出App Engine，随后在2012年全面扩展为完整的云平台。两者均采用"按使用量付费"（Pay-as-you-go）模型，彻底改变了AI工程师获取计算资源的方式——从需要数周采购物理服务器，变为数分钟内启动数百台虚拟机进行模型训练。

对AI工程领域而言，云服务的核心价值在于提供弹性GPU/TPU算力。AWS的`p4d.24xlarge`实例搭载8块NVIDIA A100 GPU，单实例算力峰值达400 TFLOPS；GCP的TPU v4 Pod则包含4096个TPU核心，专为TensorFlow和JAX框架优化。这意味着AI工程师无需自建昂贵的GPU集群，即可按需访问训练大型语言模型所需的算力。

云服务在AI工程中的重要性还体现在生态系统完整性上。AWS提供SageMaker作为端到端ML平台，GCP提供Vertex AI，两者均集成了数据存储、模型训练、超参数调优、模型部署和监控的完整流水线，显著降低了MLOps的工程复杂度。

---

## 核心原理

### 计算资源抽象：虚拟机与容器实例

AWS通过EC2（Elastic Compute Cloud）提供虚拟机实例，实例类型命名遵循`[系列][代际].[规格]`格式，例如`g5.4xlarge`表示第5代GPU优化实例的4xlarge规格。GCP的等价产品是Compute Engine，实例类型采用`[前缀]-[CPU数量]`格式，如`n2-standard-32`表示32核通用计算实例。

对于AI推理场景，AWS的`inf2`实例搭载Inferentia2芯片，每美元推理成本比通用GPU实例低约40%。GCP的`a2-ultragpu`实例则搭载A100 80GB显存版本，适合需要大显存的LLM推理。选择实例类型时，AI工程师必须权衡内存带宽（Memory Bandwidth）、显存容量和每小时价格三个维度。

### 对象存储：S3与GCS的工作机制

AWS S3（Simple Storage Service）使用扁平命名空间，对象通过`s3://bucket-name/prefix/object-key`格式寻址。S3的PUT操作具有强一致性（Strong Consistency），自2020年12月起所有区域生效，意味着写入后立即可读，消除了AI训练数据管道中的数据竞争问题。

GCP的Cloud Storage（GCS）与S3功能对等，使用`gs://bucket-name/object-path`格式。两者均支持多存储类别：标准存储（热数据，训练集）、近线存储（30天未访问降级，适合检查点文件）和冷线存储（90天未访问，适合归档模型版本）。在AI工程实践中，训练数据通常存放在与计算实例同区域的S3/GCS桶中，以避免跨区域传输费用（AWS跨区域出口费约$0.02/GB）。

### IAM权限模型：身份与访问管理

AWS IAM（Identity and Access Management）基于JSON格式的Policy文档控制权限，核心结构为：

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-training-bucket/*"
}
```

GCP使用基于角色的访问控制（RBAC），通过`roles/storage.objectViewer`等预定义角色或自定义角色绑定到服务账号（Service Account）。在AI工程中，SageMaker训练任务通过IAM角色获取S3数据读取权限；Vertex AI训练任务通过服务账号获取GCS访问权限。权限配置错误是AI训练任务启动失败最常见的原因之一，必须确保执行角色同时拥有计算资源权限和存储资源权限。

### 托管ML服务：SageMaker与Vertex AI

AWS SageMaker的训练任务通过`CreateTrainingJob` API提交，需指定`AlgorithmSpecification`（包含训练容器镜像URI）、`ResourceConfig`（实例类型和数量）和`InputDataConfig`（S3数据路径）。SageMaker会自动将数据从S3拉取到实例的`/opt/ml/input/data/`目录，训练完成后将模型产物上传至`/opt/ml/model/`对应的S3路径。

GCP Vertex AI的等价操作是`CustomJob`，使用`worker_pool_specs`定义多机多卡训练配置，支持通过`CLUSTER_SPEC`环境变量自动注入分布式训练所需的节点信息，与TensorFlow的`tf.distribute.MultiWorkerMirroredStrategy`原生集成。

---

## 实际应用

**大模型微调场景**：在AWS上微调一个7B参数的LLaMA模型，通常选择`ml.p3.16xlarge`实例（8块V100 16GB）或`ml.g5.12xlarge`实例（4块A10G 24GB）。数据集存放在S3，通过SageMaker Experiments追踪实验，最终模型推送至SageMaker Model Registry。完整流程通过SageMaker Pipelines编排，确保可复现性。

**批量推理场景**：使用AWS Batch或GCP Batch提交数千个推理任务，每个任务处理一个数据分片。结合Spot实例（AWS）或Spot VM（GCP），可将推理成本降低60-90%。需设置检查点机制应对Spot实例被回收（AWS提供2分钟回收警告，GCP提供30秒回收警告）。

**实时推理部署**：SageMaker Endpoints支持多模型端点（Multi-Model Endpoint），单个端点可托管数千个模型，适合多租户AI服务场景。GCP的Vertex AI Endpoints支持流量分割（Traffic Splitting），可将5%流量路由至新模型版本进行A/B测试。

---

## 常见误区

**误区一：认为相同规格实例在AWS和GCP上性能完全等同**。实际上，GCP的TPU v4使用BF16（bfloat16）格式存储激活值，在训练Transformer模型时相比NVIDIA GPU的FP16有独特的数值稳定性优势，但部分使用FP16优化的PyTorch模型需要修改才能在TPU上高效运行。不能简单地将PyTorch训练代码迁移到TPU而不做任何适配。

**误区二：将S3/GCS视为本地文件系统使用**。S3和GCS是对象存储，不支持原地修改（In-place Modification），每次"修改"实际上是覆盖写入整个对象。在AI训练中，频繁将小批量梯度检查点（如每100步保存一次）直接写入S3会产生大量API请求费用（S3 PUT请求$0.005/1000次）并引入I/O延迟，正确做法是先写入本地EBS/本地SSD，定期批量同步至S3。

**误区三：忽视数据传输费用导致账单超支**。AWS的出口流量（Egress）从EC2传输到互联网的费用为$0.09/GB（前10TB/月），但同区域内EC2到S3的传输免费。若训练集群在`us-east-1`而数据桶在`us-west-2`，每次训练Epoch都会产生跨区域传输费用。GCP同样对跨区域流量收费，同大洲跨区域约$0.01/GB，跨大洲约$0.08/GB。

---

## 知识关联

学习本概念需要具备服务器基础概念（CPU/GPU架构、网络协议、Linux文件系统），因为理解EC2实例类型选择需要知道vCPU与物理核心的关系，理解S3性能调优需要知道TCP连接数与吞吐量的关系。

在AI工程的开发运维实践中，云服务基础是容器化部署（Docker/Kubernetes on EKS/GKE）、CI/CD流水线（AWS CodePipeline/GCP Cloud Build）和分布式训练编排的前提条件。掌握AWS IAM和GCP IAM的权限模型后，才能安全地构建跨服务的ML工作流，避免将凭证（Credentials）硬编码在训练脚本中——这是AI工程安全实践的基本要求。熟悉S3/GCS的数据管理后，可进一步学习数据版本控制工具DVC（Data Version Control）与云存储的集成方案。