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
---
# 中间件

## 概述

中间件（Middleware）在Web后端架构中特指位于HTTP请求进入路由处理函数**之前**或响应返回客户端**之前**，对请求/响应对象进行拦截、处理或转发的函数或程序组件。以Express.js框架为例，中间件函数的签名固定为 `(req, res, next) => void`，其中 `next()` 调用决定是否将控制权移交给下一个中间件。

中间件概念最早在1990年代随着企业级Java应用（J2EE）的普及而被系统化。Java Servlet规范中定义的 `Filter` 接口是中间件思想的早期标准化形式，允许开发者在Servlet处理请求前后插入自定义逻辑。现代Web框架（如Django的MIDDLEWARE列表、FastAPI的依赖注入链、Koa.js的洋葱模型）均继承并演化了这一设计。

中间件的价值在于它将**横切关注点**（cross-cutting concerns）从业务逻辑中剥离。身份验证、日志记录、请求限流、CORS头注入等功能若散落在每个路由函数中，将导致大量重复代码。通过中间件，这些逻辑只需编写一次，可作用于全部路由或指定路由子集，使业务处理函数保持纯净。

---

## 核心原理

### 执行模型：责任链与洋葱模型

中间件的执行遵循**责任链模式**（Chain of Responsibility）。在Express.js中，中间件按照 `app.use()` 的注册顺序依次执行，每个中间件通过调用 `next()` 传递控制权，若某个中间件不调用 `next()`，则链条在此中断，后续中间件不会执行。

Koa.js引入了更精确的**洋葱模型**：中间件以 `await next()` 为分界点，请求阶段从外层向内层穿透，响应阶段从内层向外层回溯。伪代码如下：

```
中间件A（进入） → 中间件B（进入） → 路由处理 → 中间件B（退出） → 中间件A（退出）
```

这意味着中间件A可以在 `await next()` 之后访问并修改由内层中间件写入的响应数据，这是Express.js线性模型无法天然实现的能力。

### 作用域：全局、路由级与错误处理

中间件按作用范围分为三类：
- **全局中间件**：通过 `app.use(fn)` 注册，对所有路由生效，常见于日志记录（如Morgan）、JSON请求体解析（`express.json()`）。
- **路由级中间件**：挂载到特定路径或路由器实例，如 `router.use('/admin', authMiddleware)` 仅对 `/admin` 前缀的路由执行身份验证。
- **错误处理中间件**：Express.js中签名为四参数 `(err, req, res, next)`，必须注册在所有普通中间件之后，专门捕获由 `next(err)` 传递的错误对象并返回统一格式的错误响应。

### 中间件的状态与隔离性

HTTP是无状态协议，每个请求触发独立的中间件链调用，因此中间件函数本身不应持有请求级别的可变状态。正确做法是将请求相关数据挂载到 `req` 对象（如 `req.user = decodedToken`），而将数据库连接池、配置对象等**跨请求共享的资源**通过闭包注入中间件工厂函数。以限流中间件为例，内存存储的IP计数器必须在中间件函数外层初始化，否则每次请求都会重置计数。

---

## 实际应用

**JWT身份验证中间件**是AI工程后端最常见的中间件应用场景。实现逻辑为：从 `Authorization: Bearer <token>` 请求头中提取JWT字符串，使用 `jsonwebtoken.verify(token, SECRET_KEY)` 验证签名，将解码后的用户信息挂载到 `req.user`，随后调用 `next()` 放行。若验证失败，直接返回 `401 Unauthorized` 而不调用 `next()`，阻止请求进入业务路由。

**请求日志中间件**在记录请求方法、路径、耗时时，需在 `next()` 调用前记录开始时间戳（`Date.now()`），在响应完成事件（`res.on('finish')`）中计算耗时差值，这是因为 `next()` 之后的同步代码早于响应发送完成执行。

**AI推理请求限流中间件**在AI工程场景中尤为重要：大语言模型推理接口的调用成本高，常使用 `express-rate-limit` 库配置每IP每分钟最多20次调用，超出限制返回 `429 Too Many Requests`，避免单用户耗尽GPU资源。

**CORS中间件**通过注入 `Access-Control-Allow-Origin`、`Access-Control-Allow-Methods` 等响应头，解决前端跨域请求问题。Django中 `django-cors-headers` 库的 `CorsMiddleware` 必须放置在 `MIDDLEWARE` 列表的**最前面**，否则后续中间件抛出异常时响应将缺少CORS头，导致浏览器因跨域策略屏蔽错误信息。

---

## 常见误区

**误区一：认为调用 `next()` 后当前中间件立即停止执行**

在Express.js中，调用 `next()` 仅表示将控制权传递出去，但当前函数并未返回。若在 `next()` 之后仍有代码（例如再次调用 `res.json()`），将导致"Cannot set headers after they are sent"错误。正确写法是 `return next()` 或确保 `next()` 后无副作用代码。

**误区二：将中间件注册顺序视为无关紧要**

`express.json()` 必须在读取 `req.body` 的路由之前注册；身份验证中间件必须在受保护路由之前注册；错误处理中间件必须在所有路由之后注册。如果将 `app.use(errorHandler)` 放在路由定义之前，路由产生的错误将无法被它捕获，因为注册时路由尚未存在于链中。

**误区三：用中间件处理需要数据库查询的复杂权限逻辑**

全局身份验证中间件仅应做轻量的JWT签名验证（纯CPU计算，约0.5ms）。若将"查询数据库确认用户是否被封禁"的逻辑也放入全局中间件，则每个请求（包括健康检查、静态资源请求）都将产生数据库查询，造成不必要的数据库负载。此类逻辑应放入路由级中间件，仅作用于需要该权限检查的接口。

---

## 知识关联

**前置知识**：理解中间件需要掌握HTTP请求/响应生命周期（来自服务器基础概念），尤其是请求头结构（`Authorization`、`Content-Type`）和响应状态码语义（401/403/429）。中间件对 `req`、`res` 对象的操作本质上是对Node.js/WSGI HTTP对象的属性读写。

**后续概念**：中间件与**任务队列**（如Celery、Bull）的衔接点在于：AI推理等耗时操作不应在中间件或路由处理函数中同步执行（会阻塞事件循环超过30秒），正确做法是在路由层将任务序列化后推入消息队列（Redis/RabbitMQ），立即返回 `202 Accepted` 和任务ID，由独立Worker进程异步执行推理。中间件可在此流程中负责验证请求合法性、进行限流，再将通过验证的请求交由路由层入队。
