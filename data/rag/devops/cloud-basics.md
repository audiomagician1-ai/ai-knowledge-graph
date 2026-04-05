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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

AWS（Amazon Web Services）于2006年正式推出，是全球最早的商业化公有云平台，目前在全球云计算市场占据约32%的份额；GCP（Google Cloud Platform）于2011年发布，依托Google自身数据中心基础设施，在AI/ML工作负载和大数据处理上具有独特优势。两者均提供按需付费（Pay-as-you-go）的计费模式，以小时或秒为计费单位，用户无需预先购置物理服务器。

在AI工程领域，云服务的核心价值在于弹性伸缩（Elasticity）：训练一个大型语言模型时，可临时申请数百张GPU，训练完成后立即释放，仅需为实际使用的小时数付费。这与传统本地服务器（On-Premises）模式相比，可将基础设施成本降低40%–70%（根据工作负载类型而定）。AWS和GCP均提供全球分布的可用区（Availability Zone）机制，AWS目前拥有33个地理区域（Region）、105个可用区，GCP拥有40个以上的区域。

## 核心原理

### 计算服务：EC2 vs Compute Engine

AWS的弹性计算服务称为EC2（Elastic Compute Cloud），GCP对应产品为Compute Engine。两者均以**实例类型**（Instance Type）划分计算规格。以AI训练常用的GPU实例为例：AWS的`p4d.24xlarge`搭载8张NVIDIA A100 40GB，GCP的`a2-megagpu-16g`则搭载16张A100 40GB。

实例的选型直接影响成本。AWS EC2按需实例（On-Demand）价格固定但较贵；**Spot实例**（AWS）/ **Preemptible VM**（GCP）利用云服务商的闲置资源，价格可低至按需实例的10%–30%，但可能被随时中断（AWS Spot中断前会提供2分钟警告）。对于可以checkpoint的模型训练任务，使用Spot/Preemptible实例是降低成本的标准策略。

### 存储体系：S3 vs Cloud Storage

AWS S3（Simple Storage Service）是对象存储（Object Storage）的事实标准，GCP的对应产品为Cloud Storage。两者均采用**Bucket → Object**的两级层级结构，对象通过唯一的URI访问，例如`s3://my-bucket/data/train.csv`或`gs://my-bucket/data/train.csv`。

对象存储与传统文件系统的根本区别在于：S3/Cloud Storage中不存在真正的目录，`data/train.csv`中的`data/`只是键名（Key）的前缀，并非真实路径。这在AI工程中会影响数据集的批量读取效率——直接列举大量小文件时延迟较高，通常需将数据打包为TFRecord（TensorFlow）或Parquet格式后再上传。S3的标准存储层99.999999999%（11个9）耐久性保证来自跨可用区的多副本机制。

### IAM权限模型

AWS的IAM（Identity and Access Management）和GCP的Cloud IAM均采用**基于角色的访问控制（RBAC）**，但实现方式有所不同。AWS IAM通过**策略（Policy）**JSON文件精确控制权限，例如：

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-ml-bucket/*"
}
```

GCP则通过**服务账号（Service Account）**为计算资源分配身份，再将预定义角色（如`roles/storage.objectViewer`）绑定到该账号。AI工程中常见的安全问题是将密钥硬编码到训练脚本中——正确做法是为EC2实例附加IAM Role或为GCP VM绑定Service Account，令计算资源通过元数据服务自动获取临时凭证，无需明文密钥。

### 托管AI/ML服务

AWS提供SageMaker作为端到端ML平台，内置训练、调参（Hyperparameter Tuning Job）、部署（SageMaker Endpoint）等功能，最低部署延迟可达毫秒级。GCP提供Vertex AI，原生集成TensorFlow、PyTorch和JAX，其**Vertex AI Pipelines**基于Kubeflow Pipelines规范，适合构建可重复的MLOps流水线。相比自建Kubernetes集群，使用这些托管服务可减少约60%的运维配置工作。

## 实际应用

**场景一：模型训练数据管道**
将训练数据存储于S3或Cloud Storage，通过AWS DataSync或gsutil进行批量传输，再使用`torch.utils.data.DataLoader`配合`s3fs`或`gcsfs`库直接流式读取云端数据，避免将整个数据集下载到本地磁盘。

**场景二：推理服务部署**
在GCP上，可将训练好的模型导出为SavedModel格式，推送到Cloud Storage，再通过Vertex AI Endpoints一键部署，系统自动根据QPS（每秒查询数）进行自动扩缩容（Auto-scaling），并支持A/B测试流量分割（Traffic Split）。

**场景三：成本优化**
使用AWS的Cost Explorer分析GPU实例的利用率，若训练任务占空比低于40%，可将按需实例替换为Savings Plans（承诺使用1年或3年可节省约40%费用），或将批量推理任务迁移到Lambda无服务器架构（适合推理延迟要求≥100ms的场景）。

## 常见误区

**误区一：认为同一地区内数据传输是免费的**
AWS在同一区域（Region）内跨可用区的数据传输并非完全免费，EC2实例与S3之间的出站流量（Egress）在免费额度（每月100GB）用尽后按$0.09/GB计费。大规模模型训练中，数据加载产生的传输费用可能超过计算费用，因此应将训练实例与数据Bucket部署在同一Region。

**误区二：Spot/Preemptible实例不适合训练任务**
很多工程师因为担心中断而完全回避Spot实例。实际上，通过在训练代码中每隔N步保存Checkpoint到S3/Cloud Storage，即使实例被回收，重新申请后也能从断点续训，整体成本节省可高达70%。PyTorch Lightning内置了`on_save_checkpoint`回调，可自动完成此操作。

**误区三：GCP与AWS的"区域"概念等价**
GCP的Zone（区域）对应AWS的Availability Zone（可用区），GCP的Region与AWS的Region才是同一层级的概念。在GCP中，单个VM默认部署在单个Zone，跨Zone部署需要手动配置实例组（Managed Instance Group），而AWS的Auto Scaling Group默认支持跨多个AZ的高可用部署。

## 知识关联

掌握**服务器基础概念**（CPU/内存/磁盘/网络带宽的物理含义）是理解EC2实例类型（如`c5.4xlarge`代表计算优化型、16 vCPU、32GB内存）的前提，否则无法有效选型。虚拟化原理（Hypervisor）解释了为何云实例的vCPU性能与物理核心存在差异，以及为何网络I/O会有"Burst"限制。

在此基础上，云服务知识直接支撑**Docker与容器化**（AWS ECS/EKS、GCP Cloud Run/GKE均以容器为部署单元）、**CI/CD流水线**（GitHub Actions可直接调用AWS CLI或gcloud命令触发云端训练任务）以及**分布式训练**（多机多卡训练依赖VPC网络配置和IAM权限管理）等后续AI工程实践。