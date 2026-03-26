---
id: "serverless"
concept: "Serverless架构"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 6
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Serverless架构

## 概述

Serverless架构（无服务器架构）是一种云计算执行模型，开发者只需编写和部署代码逻辑，底层服务器的配置、扩缩容、运维工作完全由云平台自动管理。"Serverless"并非真的没有服务器，而是指开发者无需感知服务器的存在。计费模式是其最显著的特征：按函数实际执行的次数和消耗的CPU/内存资源计费，而非按服务器运行时长计费，空闲时费用为零。

Serverless的概念随2014年AWS Lambda的发布正式进入主流。Lambda允许开发者上传一段代码，指定触发条件（如HTTP请求、文件上传事件），平台在毫秒级内启动容器执行代码，执行完毕后立即回收资源。此后Google Cloud Functions（2016年）、Azure Functions（2016年）相继推出，Serverless生态迅速成熟。

在AI工程领域，Serverless架构尤其适合部署推理接口：AI模型的请求往往呈现峰谷波动明显的特点，使用传统服务器需要按峰值配置资源，大量时间资源闲置浪费。Serverless的按需执行特性可将这类场景的基础设施成本降低60%-80%。

## 核心原理

### 函数即服务（FaaS）

FaaS（Function as a Service）是Serverless最核心的执行单元。每个函数是一个独立的、无状态的代码片段，有明确的输入参数和返回值。以AWS Lambda为例，一个函数的最大执行时长为15分钟，内存配置范围为128MB至10,240MB，超出限制则被强制终止。函数的代码包（含依赖）在AWS Lambda上不得超过250MB（解压后），这直接影响AI模型部署时的打包策略。

函数的触发方式多样：API Gateway触发（HTTP/HTTPS请求）、S3事件触发（文件上传/删除）、消息队列触发（SQS/SNS）、定时触发（类似Cron Job）。AI推理场景通常使用API Gateway + Lambda的组合，前端发送POST请求携带输入数据，Lambda加载模型执行推理并返回结果。

### 冷启动问题

冷启动（Cold Start）是Serverless最重要的性能瓶颈。当函数长时间未被调用或首次部署后，云平台需要从零初始化容器环境、加载运行时、执行初始化代码，这个过程通常耗时100ms至数秒不等。对于Python运行时的AWS Lambda，加载PyTorch或TensorFlow等大型深度学习框架时，冷启动时间可达5-10秒，对实时推理服务而言不可接受。

缓解冷启动的方案包括：①预置并发（Provisioned Concurrency），AWS Lambda允许预先初始化指定数量的实例保持热状态，但此时将按时长计费，失去了Serverless的成本优势；②精简依赖，通过ONNX Runtime替代完整深度学习框架，将包体积从数百MB压缩至20MB以内，显著缩短冷启动时间；③定时Ping，每5分钟用定时任务触发一次函数，强制保持实例活跃。

### 无状态执行与持久化

Serverless函数的执行环境是无状态的，每次调用都可能运行在不同的容器实例中，/tmp目录（Lambda上最大512MB，可配置至10GB）仅在同一实例的多次调用间短暂共享，实例回收后数据消失。这意味着AI模型权重文件不能缓存在函数实例内存中跨调用复用（除非命中同一个热实例）。

解决方案是将模型权重存储在Amazon S3，函数冷启动时将模型文件下载到/tmp目录并加载到内存，后续同一实例的调用可以命中内存缓存，避免重复下载。持久化业务数据必须写入外部存储：关系型数据库（RDS）、键值存储（DynamoDB/Redis）或对象存储（S3）。

### BaaS（后端即服务）

Serverless架构通常与BaaS（Backend as a Service）配合使用。BaaS将数据库、身份认证、文件存储等后端能力封装为托管服务，开发者直接调用API而不管理底层。例如Firebase（Google）提供实时数据库+身份认证，Supabase提供PostgreSQL+Row Level Security，使得一个AI应用的后端可以完全由FaaS函数+BaaS服务构成，零服务器运维。

## 实际应用

**AI图像处理管道**：用户上传图片到S3，S3事件触发Lambda函数，函数调用预加载在/tmp的YOLO模型进行目标检测，将检测结果写入DynamoDB，整个链路无需维护任何服务器，按实际处理图片数量计费。

**定时批量推理**：使用EventBridge（CloudWatch Events）每小时触发一次Lambda，从RDS拉取待处理数据，批量调用外部LLM API（如OpenAI）完成文本分类，结果写回数据库。这是Serverless最适合的场景之一：低频、批量、执行时间可预期。

**轻量级AI API**：使用AWS Lambda + API Gateway构建一个文本嵌入接口，后端加载sentence-transformers的轻量模型（all-MiniLM-L6-v2，约22MB），冷启动约800ms，正常请求响应时间50-200ms，月调用量100万次以内时成本约$0.20，远低于常驻EC2实例的费用。

## 常见误区

**误区一：Serverless适合所有AI推理场景**。Serverless函数有执行时长上限（Lambda最长15分钟），且不支持GPU实例（Lambda仅提供CPU执行环境，截至2024年不支持原生GPU）。大型语言模型的在线推理、需要GPU加速的实时视频处理无法在标准Serverless函数上运行，应选择Kubernetes + GPU节点或专用推理服务（如SageMaker Endpoints）。

**误区二：Serverless一定比传统服务器便宜**。当请求量持续高并发时（如每秒数千次调用），Serverless的按调用计费模式反而比常驻服务器更贵。Lambda的定价为每100万次请求$0.20加上按GB-秒计算的计算费用，高并发场景下成本会超过同等规格的EC2实例，需要根据实际流量模式进行成本建模再做决策。

**误区三：函数内的全局变量在调用间共享**。函数中在handler外部定义的变量（如模型对象）在同一个热实例的多次调用间确实会被复用，但这不等同于"全局状态可靠"——一旦实例被回收重建，全局变量会重新初始化。在并发扩容时，多个实例各自维护独立的全局变量，写操作不会在实例间同步，用全局变量做计数器或缓存共享数据是错误的设计。

## 知识关联

学习Serverless架构需要具备服务器基础概念的扎实理解，特别是HTTP请求生命周期、进程与内存管理、容器技术基础——因为Serverless的冷启动问题本质上是容器初始化时间问题，不理解容器就无法解释为何Python运行时冷启动慢于Node.js。

Serverless与容器化部署（Docker/Kubernetes）形成互补关系：Serverless适合事件驱动、低频、短时的任务；Kubernetes适合长时运行、需要GPU、需要精细调度的服务。在AI工程项目中，两者通常共存于同一系统：用Serverless处理数据预处理和轻量API，用Kubernetes集群托管大模型推理服务。此外，理解API Gateway的限流配置（如AWS API Gateway默认10,000 RPS的区域限制）和Lambda的并发配额（默认区域并发上限1,000，可申请提高）对于设计生产级Serverless系统至关重要。