---
id: "cors"
concept: "CORS跨域"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 4
is_milestone: false
tags: ["安全"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# CORS跨域

## 概述

CORS（Cross-Origin Resource Sharing，跨源资源共享）是W3C于2014年正式发布的RFC 6454标准，用于解决浏览器的同源策略限制。同源策略规定：只有当协议（http/https）、域名（host）、端口（port）三者完全相同，两个URL才属于同源。CORS通过在HTTP请求和响应中添加特定的头部字段，告知浏览器是否允许来自不同源的请求访问服务端资源，从而在安全可控的前提下突破同源限制。

CORS出现之前，开发者常用JSONP（JSON with Padding）绕过同源策略，但JSONP只支持GET请求且存在XSS安全风险。CORS作为官方标准方案，支持所有HTTP方法（GET、POST、PUT、DELETE等），并将跨域控制权交给服务端，由服务端通过响应头明确声明哪些来源、哪些方法被允许，安全性大幅提升。

在AI工程的Web后端场景中，前端调用模型推理API、向量检索接口或数据可视化服务时，前后端几乎必然部署在不同端口甚至不同域名下（如前端在 `app.example.com`，推理服务在 `api.example.com:8080`），CORS配置是这类场景能否正常工作的先决条件。

## 核心原理

### 简单请求与预检请求的区分

CORS将请求分为两类，判断条件严格。**简单请求**须同时满足：
- HTTP方法为 `GET`、`POST` 或 `HEAD` 之一；
- Content-Type 仅限 `text/plain`、`multipart/form-data`、`application/x-www-form-urlencoded`；
- 不含自定义请求头（如 `Authorization`、`X-Custom-Header`）。

满足以上条件时，浏览器直接发送请求，并自动在请求头中附加 `Origin` 字段（如 `Origin: https://app.example.com`）。服务端响应后，浏览器检查响应中的 `Access-Control-Allow-Origin` 字段，决定是否将响应暴露给JS代码。

如果请求不符合简单请求条件（例如使用 `application/json` 作为Content-Type，或者携带 `Authorization` Bearer Token），浏览器会先自动发送一次 **OPTIONS 预检请求（Preflight Request）**，询问服务端是否允许该跨域请求。只有服务端正确响应预检请求之后，浏览器才会发送实际请求。

### 关键HTTP头部字段详解

CORS协议通过以下头部字段完成协商：

**请求端（浏览器自动添加）：**
- `Origin`：标识请求来源，格式为 `协议://域名:端口`
- `Access-Control-Request-Method`：预检请求中声明实际请求的HTTP方法
- `Access-Control-Request-Headers`：预检请求中声明实际请求携带的自定义头

**响应端（服务端必须配置）：**
- `Access-Control-Allow-Origin`：允许的来源，可设为具体域名或通配符 `*`（注意：携带Cookie时不能使用 `*`，必须指定具体域名）
- `Access-Control-Allow-Methods`：允许的HTTP方法列表，如 `GET, POST, PUT, DELETE`
- `Access-Control-Allow-Headers`：允许的请求头列表，如 `Content-Type, Authorization`
- `Access-Control-Max-Age`：预检结果的缓存时间（单位秒），设置后在此时间内浏览器不再重复发送预检请求，推荐值为 `86400`（1天）
- `Access-Control-Allow-Credentials`：是否允许携带Cookie，值为 `true` 时必须配合具体 `Allow-Origin`

### Cookie与凭证的特殊处理

当前端请求需要携带Cookie（如Session认证）时，必须同时满足两个条件才能生效：
1. 前端请求需设置 `credentials: 'include'`（fetch API）或 `withCredentials: true`（XMLHttpRequest）；
2. 服务端响应必须同时包含 `Access-Control-Allow-Credentials: true` 且 `Access-Control-Allow-Origin` 为具体域名而非 `*`。

任意一侧缺失，浏览器都会阻止JS读取响应内容，且控制台会抛出明确的CORS错误（而非网络错误）。

## 实际应用

**FastAPI中的CORS配置示例：**

在AI后端常用的FastAPI框架中，通过中间件一行代码开启CORS：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # 生产环境指定具体域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=86400,
)
```

**Nginx层统一处理CORS：**

当模型推理服务（如Triton Inference Server）不便修改代码时，可在Nginx反向代理层统一添加CORS响应头，通过 `add_header` 指令为所有后端服务统一配置，避免各服务重复处理。

**本地开发调试场景：**

前端运行在 `localhost:3000`，后端API在 `localhost:8000`，即使是同一台机器，端口不同也属于跨域。此场景下临时将 `allow_origins` 设为 `["*"]` 是常见做法，但**必须**在部署到生产环境前改回具体域名白名单。

## 常见误区

**误区一：服务端配置了CORS，但请求仍然失败**

许多开发者以为CORS是服务端的问题，认为只要服务端加了 `Access-Control-Allow-Origin` 就万事大吉。实际上，携带自定义头（如 `Authorization`）的请求会触发预检，如果服务端没有正确响应 OPTIONS 预检请求（返回200/204且包含正确的 `Access-Control-Allow-Headers`），实际请求根本不会被发出。排查时应先在浏览器开发者工具的Network标签中查找OPTIONS请求，检查其响应状态码和头部。

**误区二：`Access-Control-Allow-Origin: *` 是最安全通用的设置**

通配符 `*` 实际上是最宽松的设置，意味着任何来源都可以访问该接口。对于公开只读的静态资源或完全公开的API（如公共数据集接口）可以使用，但对于涉及用户数据或AI模型内部逻辑的接口，必须指定具体的允许来源白名单，否则恶意网站可以诱导用户浏览器向你的服务发起跨域请求并读取响应。

**误区三：CORS是服务端的安全防护机制**

CORS的执行主体是**浏览器**，不是服务端。服务端返回的 `Access-Control-Allow-Origin` 头部只是"告知浏览器"是否允许，服务端本身已经处理了请求并返回了响应——只是浏览器会根据响应头决定是否将结果暴露给JavaScript代码。这意味着非浏览器客户端（如curl、Postman、Python requests）完全不受CORS限制，CORS无法替代服务端的身份认证和权限校验。

## 知识关联

**前置知识（HTTP协议）：** CORS的所有机制均建立在HTTP头部扩展上，预检请求是标准的OPTIONS方法，理解HTTP请求/响应头的格式和传输方式是读懂CORS错误信息的前提。同源策略本身也是基于HTTP URL结构（协议+主机+端口）定义的。

**关联技术（身份认证）：** CORS配置与JWT Bearer Token认证紧密耦合。JWT通过 `Authorization` 头传递，这会触发预检请求，因此服务端的 `Access-Control-Allow-Headers` 必须包含 `Authorization`。同样，基于Session-Cookie的认证需要同时配置 `Allow-Credentials: true` 和具体的 `Allow-Origin`，两套认证方案的CORS配置要求完全不同。

**工程实践（API网关）：** 在微服务架构中，多个AI推理服务统一通过API网关（如Kong、AWS API Gateway）对外暴露时，CORS策略通常统一在网关层配置，各下游服务无需单独处理，这是消除CORS重复配置、保证策略一致性的标准做法。