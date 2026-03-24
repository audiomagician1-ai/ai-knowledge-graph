---
id: "task-queue"
concept: "任务队列"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 4
is_milestone: false
tags: ["celery", "async", "background-jobs"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 任务队列

## 概述

任务队列（Task Queue）是一种将耗时操作从HTTP请求-响应周期中剥离出来，交由后台工作进程异步执行的架构模式。当用户触发一个需要30秒才能完成的图像处理请求时，若在Web进程中同步执行，用户将被迫等待并占用宝贵的线程资源；任务队列则允许Web进程立即返回"任务已提交"的响应，将实际处理工作推入队列，由独立的Worker进程消费执行。

任务队列的概念在2009年前后随着Ruby的Delayed::Job和Resque库开始流行，Python生态中的Celery于2009年首次发布，此后成为最主流的任务队列框架之一。Node.js生态中的BullMQ（Bull的继任者）则依托Redis的List和Sorted Set数据结构实现了相似功能。这两套工具代表了任务队列在不同语言生态中的主流实践路径。

任务队列在AI工程的Web后端中尤为关键：模型推理、批量嵌入生成、向量数据库索引构建等操作通常耗时数秒至数分钟，完全不适合在同步请求中执行。通过任务队列，可以实现推理请求的削峰填谷、GPU资源的串行化利用以及失败任务的自动重试。

## 核心原理

### 生产者-消费者模型与Broker

任务队列依赖三个角色：**Producer**（生产者，即Web应用）、**Broker**（消息代理，存储任务）、**Worker**（消费者，执行任务）。Producer调用 `task.delay(args)` 或 `task.apply_async(args)` 将序列化后的任务消息写入Broker；Worker进程持续轮询或监听Broker，取出任务并执行。Celery支持Redis、RabbitMQ、Amazon SQS等多种Broker；BullMQ则强制使用Redis，并利用Redis的原子操作保证同一任务不被两个Worker重复领取。

任务消息本身是一个包含任务名称、参数、任务ID（UUID）和元数据的序列化对象，Celery默认使用JSON序列化，也支持pickle（存在安全风险，生产环境应避免）。BullMQ将任务存储在Redis的Hash中，任务ID格式为 `bull:{queue_name}:{jobId}`。

### 任务状态机与Result Backend

一个Celery任务在其生命周期中经历以下状态：`PENDING → STARTED → SUCCESS / FAILURE / RETRY`。若配置了Result Backend（如Redis或数据库），任务执行结果和异常信息会被持久化，供生产者通过 `AsyncResult(task_id).get()` 查询。BullMQ中对应的状态为 `waiting → active → completed / failed`，可通过 `job.getState()` 获取。

Celery的Result Backend配置示例：`app.conf.result_backend = 'redis://localhost:6379/1'`，其中数据库编号1与Broker（通常用编号0）隔离，避免键名冲突。未配置Result Backend时，任务结果将永久丢失，适用于"fire-and-forget"场景（如发送通知邮件）。

### 定时任务与Beat调度器

除即时异步任务外，任务队列框架还支持定时任务（Cron-style Scheduling）。Celery通过独立进程`celery beat`实现调度，配置示例：

```python
app.conf.beat_schedule = {
    'rebuild-index-every-hour': {
        'task': 'tasks.rebuild_vector_index',
        'schedule': crontab(minute=0),  # 每小时整点执行
    },
}
```

BullMQ使用 `repeat: { pattern: '0 * * * *' }` 参数实现相同功能，底层通过Redis的Sorted Set按执行时间戳排序待执行的重复任务。需要注意：Celery Beat是单点进程，生产环境中必须保证其高可用，否则定时任务将全面停止。

### 并发模型与Worker配置

Celery Worker支持三种并发模型：`prefork`（多进程，默认，适合CPU密集型）、`gevent`/`eventlet`（协程，适合IO密集型）、`solo`（单线程，适合调试）。启动命令 `celery -A myapp worker --concurrency=4 --pool=prefork` 会创建4个子进程并行处理任务。BullMQ的Worker通过 `concurrency` 参数控制同时处理的任务数，底层基于Node.js的事件循环，天然适合IO密集型任务（如调用外部AI API）。

## 实际应用

**场景一：AI模型推理队列**
用户上传文档后，Web接口立即返回 `task_id`，后台Celery Worker调用本地部署的Ollama或OpenAI API进行文本分析，完成后将结果写入数据库，前端通过轮询 `/tasks/{task_id}/status` 接口获取进度。这一模式避免了LLM推理延迟（通常5~30秒）阻塞Web服务器线程。

**场景二：批量向量嵌入**
知识库更新时，将数千条文档的嵌入生成任务拆分为每批100条，通过 `group()` 原语并行分发给多个Worker，最终用 `chord()` 汇总结果并触发向量数据库的索引刷新。Celery的 `chord` 原语要求配置Result Backend，因为需要等待所有子任务完成后才能触发回调。

**场景三：定时数据同步**
每天凌晨2点通过Celery Beat触发任务，从第三方数据源拉取最新数据并增量更新向量索引，这类任务的执行耗时不影响任何用户请求，同时通过 `max_retries=3, countdown=60` 配置实现网络异常时的自动重试。

## 常见误区

**误区一：任务函数内直接共享Django ORM对象**
Celery Worker运行在独立进程中，不能将Django QuerySet或SQLAlchemy Session对象作为任务参数传递，因为这些对象无法跨进程序列化。正确做法是只传递对象的主键（整数ID），在Worker内部重新查询数据库：`obj = MyModel.objects.get(id=obj_id)`。

**误区二：误以为任务天然幂等**
Worker崩溃后Broker会将任务重新分配，若任务不具备幂等性（如重复扣款、重复发送邮件），将导致严重业务错误。应在任务逻辑中通过数据库唯一约束或Redis SETNX实现去重，Celery的 `acks_late=True` 配置会在任务执行完成后才确认消息，减少丢失但增加重复执行概率，需结合幂等设计使用。

**误区三：用任务队列替代流式响应**
对于需要实时流式输出的LLM推理（如ChatGPT流式回复），任务队列并不合适，因为它本质上是"执行完成后获取结果"的模型。流式场景应使用WebSocket或Server-Sent Events直接推送，任务队列适合的是"提交→等待→查询结果"的异步模式。

## 知识关联

**与消息队列的关系**：任务队列构建在消息队列之上——Redis的List/Sorted Set或RabbitMQ的AMQP协议提供了底层消息存储和传输能力，而Celery/BullMQ在其上封装了任务序列化、Worker管理、重试策略、优先级队列等专为任务执行场景设计的高级特性。消息队列关注"消息的可靠传递"，任务队列关注"函数的可靠异步执行"。

**与中间件的关系**：任务队列框架本身充当Web框架与后台处理逻辑之间的中间件层。在Django中，Celery通过 `django-celery-results` 与ORM集成；在Express.js中，BullMQ的Queue实例通常在应用初始化时作为中间件注入，供路由处理器调用 `queue.add()`。理解中间件的请求拦截与依赖注入机制，有助于在Web后端中正确初始化和复用Queue连接实例，避免每次请求重复创建Redis连接的性能损耗。
