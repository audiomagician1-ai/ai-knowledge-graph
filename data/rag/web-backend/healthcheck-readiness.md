---
id: "healthcheck-readiness"
concept: "健康检查与就绪探针"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 3
is_milestone: false
tags: ["healthcheck", "kubernetes", "probe"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 健康检查与就绪探针

## 概述

健康检查（Health Check）与就绪探针（Readiness Probe）是Web后端服务向运行时平台暴露自身运行状态的标准机制。具体做法是在HTTP服务中实现 `/health`（存活检查）和 `/ready`（就绪检查）两个端点，供Kubernetes等编排平台周期性调用，以决定是否重启容器或将流量路由到该实例。

这一模式起源于Google内部的Borg调度系统，Kubernetes在2014年开源时将其形式化为`livenessProbe`和`readinessProbe`两种探针类型。2018年Kubernetes 1.11版本进一步引入了`startupProbe`（启动探针），专门处理启动耗时较长的应用程序，避免存活探针在应用初始化期间误判导致无限重启。

对AI推理服务而言，这两个端点尤为关键：模型文件可能需要数十秒才能加载至GPU显存，若不区分"进程存活"与"服务就绪"这两种状态，Kubernetes会在模型尚未加载完毕时便向该Pod转发推理请求，导致请求失败或超时。

## 核心原理

### `/health` 端点与存活探针（Liveness Probe）

`/health` 端点回答的问题是：**"这个进程还活着吗？"** 它只检查服务进程本身是否处于正常运行状态，而不检查依赖项。典型实现仅返回HTTP 200和固定JSON体 `{"status": "ok"}`，响应时间应控制在5毫秒以内。

Kubernetes `livenessProbe` 配置示例如下：

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 15
  failureThreshold: 3
```

`failureThreshold: 3` 意味着连续3次探测失败后，Kubernetes才会重启该容器。`initialDelaySeconds` 给应用留出启动缓冲时间。存活探针失败的后果是**容器重启**，因此绝不应将数据库连通性等外部依赖纳入 `/health` 检查——否则数据库短暂抖动会触发服务雪崩式重启。

### `/ready` 端点与就绪探针（Readiness Probe）

`/ready` 端点回答的问题是：**"这个实例能接收流量吗？"** 它需要检查所有服务依赖项是否就绪，包括数据库连接池是否建立、缓存是否预热、AI模型是否加载完成、配置是否已从远端拉取等。任一依赖不满足，应返回HTTP 503。

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 1
  successThreshold: 1
```

就绪探针失败的后果是将该Pod从Service的Endpoints列表中**摘除**，而非重启容器。这是与存活探针最本质的区别：Pod继续运行，只是暂时不接收流量。当 `/ready` 重新返回200时，Kubernetes自动将该Pod重新加入负载均衡池。

### 响应体设计规范

生产级实现通常在 `/ready` 端点返回结构化响应，便于运维排查：

```json
{
  "status": "degraded",
  "checks": {
    "database": {"status": "ok", "latency_ms": 3},
    "model_loaded": {"status": "fail", "detail": "weights not in GPU memory"},
    "redis": {"status": "ok", "latency_ms": 1}
  }
}
```

HTTP状态码必须准确反映整体状态：全部通过返回200，任一失败返回503。不能仅依赖响应体中的字段，因为Kubernetes只判断HTTP状态码，不解析响应体内容。

### 启动探针的补充角色

对于加载大型语言模型（如7B参数规模，加载时间可能超过60秒）的服务，应同时配置 `startupProbe`：

```yaml
startupProbe:
  httpGet:
    path: /health
    port: 8080
  failureThreshold: 30
  periodSeconds: 5
```

`failureThreshold × periodSeconds = 30 × 5 = 150秒`，在这150秒内启动探针接管存活检查的职责，防止模型加载期间被误杀。

## 实际应用

**FastAPI实现示例**：在Python AI服务中，通常用一个全局布尔变量 `model_ready` 追踪模型加载状态：

```python
model_ready = False

@app.on_event("startup")
async def load_model():
    global model_ready
    model.load_weights("model.pt")  # 耗时操作
    model_ready = True

@app.get("/health", status_code=200)
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    if not model_ready:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ok"}
```

**滚动更新场景**：执行 `kubectl rollout` 时，新Pod必须通过就绪探针后，旧Pod才会被终止。若新版本模型加载失败导致 `/ready` 持续返回503，Kubernetes会暂停滚动更新并保留旧版本Pod，实现零停机部署的安全保障。

## 常见误区

**误区一：`/health` 和 `/ready` 检查相同内容**。许多初学者在两个端点中实现完全相同的逻辑，失去了两者分离设计的意义。正确做法是 `/health` 只验证进程自身，`/ready` 验证所有外部依赖。若将数据库检查放入 `/health`，数据库重启维护时会触发所有服务Pod级联重启。

**误区二：就绪探针检查超时导致流量丢失**。`/ready` 中对数据库执行 `SELECT 1` 等检查若设置超时不当（如默认30秒查询超时），会导致探针响应时间超过Kubernetes的 `timeoutSeconds`（默认1秒），Pod被反复摘除和加入负载均衡池，造成流量抖动。应为探针中的每个依赖检查设置独立的短超时（100-300毫秒）。

**误区三：成功部署后忽视就绪探针的持续监控价值**。就绪探针不仅在启动时有效，运行期间若Redis连接池耗尽，`/ready` 返回503可自动触发流量切换，为自愈提供基础能力，而非一次性检查。

## 知识关联

学习本概念需要理解Kubernetes中Pod、Service、Endpoints三者的关系——就绪探针失败时操作的正是Endpoints对象，从中移除对应的Pod IP。同时需要了解HTTP状态码语义，特别是200与503的含义，因为Kubernetes探针判断完全依赖状态码而非响应体。

在此基础上，可以进一步探索服务网格（如Istio）的流量管理策略，其熔断器（Circuit Breaker）机制可以看作是就绪探针在应用层的延伸——两者都在解决"何时将流量路由到某个实例"这一本质问题，区别在于就绪探针由编排平台感知，熔断器由调用方感知。此外，Prometheus的 `up` 指标与BlackBox Exporter也常与这两个端点配合使用，实现可观测性体系的完整闭环。