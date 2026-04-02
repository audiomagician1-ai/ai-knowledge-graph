---
id: "middleware"
concept: "中间件"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 4
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 中间件

## 概述

中间件（Middleware）是位于客户端请求到达最终路由处理函数之前、响应返回客户端之前，能够访问请求对象（`req`）、响应对象（`res`）以及下一个中间件函数（通常命名为 `next`）的函数。这种"夹层"式的设计使中间件能够在不修改核心业务逻辑的前提下，对请求和响应进行统一的预处理或后处理。

中间件模式最早在 20 世纪 80 年代的分布式系统领域出现，用于解决异构系统之间的通信问题。在 Web 后端领域，Node.js 框架 Express.js（2010年发布）将中间件模式标准化并普及，形成了至今被广泛使用的 `(req, res, next)` 三参数函数签名。Python 的 WSGI（Web Server Gateway Interface，PEP 3333）和 Django 的 Middleware 类同样采用了类似的链式调用思想。

中间件的意义在于实现**横切关注点（Cross-Cutting Concerns）的解耦**。身份认证、日志记录、请求限流、CORS 头注入等功能会横跨多个业务接口，如果将这些逻辑分散在每个路由中，不仅产生大量重复代码，也增加了维护成本。中间件将这些通用逻辑集中管理，使每个路由专注于自身的业务处理。

---

## 核心原理

### 中间件执行链与洋葱模型

多个中间件按注册顺序组成一条执行链。以 Express.js 为例，当 `next()` 被调用时，控制权交给链中的下一个中间件；若 `next()` 未被调用，请求将在当前中间件终止，不会继续向下传递。

Koa.js 将此升华为**洋葱模型（Onion Model）**，利用 `async/await` 使中间件在调用 `await next()` 前后均可执行代码：

```
请求 →  中间件A（前半段）
         → 中间件B（前半段）
              → 路由处理
         ← 中间件B（后半段）
←  中间件A（后半段）
```

这意味着中间件A的"后半段"在路由处理完成后才运行，非常适合实现响应耗时统计（记录 `Date.now()` 的差值）等需要包裹整个请求生命周期的功能。

### 中间件的四种类型

**应用级中间件**：通过 `app.use()` 注册，对所有请求生效。例如 `app.use(express.json())` 将请求体的 JSON 字符串自动解析为 JavaScript 对象，挂载到 `req.body`。

**路由级中间件**：绑定到特定路径，如 `app.use('/api/admin', authMiddleware)`，只拦截 `/api/admin` 前缀的请求进行权限校验。

**错误处理中间件**：Express.js 中以四个参数 `(err, req, res, next)` 标识，必须放在所有路由注册之后。当任意中间件调用 `next(err)` 或抛出错误时，框架跳过普通中间件，直接进入错误处理中间件。

**第三方中间件**：如 `helmet`（设置 14 个与安全相关的 HTTP 响应头）、`morgan`（HTTP 请求日志记录）、`cors`（跨域资源共享配置）。

### Django 中间件的 `__call__` 机制

在 Django 中，中间件被定义为一个实现了 `__init__(self, get_response)` 和 `__call__(self, request)` 方法的类。`get_response` 是由 Django 注入的、调用下一层的可调用对象。`MIDDLEWARE` 列表中靠前的中间件包裹靠后的中间件，形成嵌套调用结构。例如 `django.middleware.security.SecurityMiddleware` 排在列表第一位，会最先处理请求、最后处理响应，负责注入 `Strict-Transport-Security` 等安全响应头。

---

## 实际应用

**JWT 身份认证中间件**：在所有受保护路由之前注册一个中间件，从 `Authorization: Bearer <token>` 请求头中提取 JWT，使用密钥验证其签名（通常采用 HS256 或 RS256 算法）。验证通过后将解码后的用户信息挂载到 `req.user`，供后续路由直接使用；验证失败则立即返回 401 响应，不调用 `next()`。

**请求限流中间件**：`express-rate-limit` 库通过中间件实现滑动窗口或固定窗口限流。例如配置 `windowMs: 15 * 60 * 1000`（15分钟窗口）、`max: 100`（最多100次请求），超出限制时自动返回 429 Too Many Requests，有效防止暴力破解和 DDoS 攻击。

**AI 工程中的请求预处理中间件**：在调用大模型 API 的路由前，注册一个中间件对用户输入进行敏感词过滤或 prompt 注入检测，同时记录每次请求的 token 估算量，超过阈值时直接返回错误，避免不必要的 API 费用消耗。

**CORS 中间件**：`cors()` 中间件在响应头中注入 `Access-Control-Allow-Origin`、`Access-Control-Allow-Methods` 等字段。对于跨域预检请求（OPTIONS 方法），中间件直接返回 204，不进入业务路由，减少不必要的处理开销。

---

## 常见误区

**误区一：认为中间件只能在请求阶段运行**。实际上在洋葱模型（Koa）中，`await next()` 之后的代码在响应返回之前执行，属于响应处理阶段。即使在 Express 中，错误处理中间件也是在路由失败后才介入。混淆请求阶段与响应阶段会导致响应头已发送后仍尝试修改的错误（`Cannot set headers after they are sent`）。

**误区二：中间件注册顺序无关紧要**。中间件的顺序直接影响功能正确性。若将 `express.json()` 解析中间件注册在身份验证中间件之后，则验证中间件无法访问 `req.body` 中的用户凭据。日志中间件必须在所有路由之前注册，否则会遗漏部分请求的日志记录。正确顺序通常为：安全头 → 日志 → 请求体解析 → 认证 → 业务路由 → 错误处理。

**误区三：在异步中间件中遗漏错误传递**。在 Express 中，`async` 中间件内部抛出的 Promise rejection 不会自动触发错误处理中间件，必须用 `try/catch` 包裹并显式调用 `next(err)`。Express 5.x 已修复此问题，会自动捕获异步错误，但 Express 4.x（目前最主流版本）不具备此能力。

---

## 知识关联

**前置概念——服务器基础概念**：理解 HTTP 请求/响应的生命周期（请求头、请求体、状态码）是读懂中间件对 `req`/`res` 对象操作的前提。中间件对 `req` 对象的修改（如挂载 `req.user`）依赖对请求对象结构的熟悉程度。

**后续概念——任务队列**：当中间件检测到某操作（如发送邮件、生成报告）不需要阻塞当前 HTTP 响应时，会在中间件层将该任务推入消息队列（如 Bull、Celery），然后立即调用 `next()` 继续处理请求。中间件是触发异步任务的常见入口点，它决定了哪些操作进入任务队列、携带哪些上下文数据。