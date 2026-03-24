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
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# CORS跨域

## 概述

CORS（Cross-Origin Resource Sharing，跨源资源共享）是由W3C于2014年正式发布为标准（RFC 6454定义了"源"的概念，CORS规范本身在Fetch Living Standard中维护），用于控制浏览器是否允许一个网页向不同源的服务器发起HTTP请求的安全机制。所谓"不同源"，指的是协议（http/https）、域名（domain.com/other.com）、端口（80/8080）三者任意一个不同的情况。浏览器默认遵循**同源策略（Same-Origin Policy）**，会自动拦截跨源响应，CORS正是解决这一限制的官方机制。

CORS出现之前，开发者依赖JSONP（仅支持GET请求）或服务器代理等绕过方式，存在安全性差、局限性大等问题。CORS通过在HTTP响应头中加入`Access-Control-Allow-Origin`等字段，让服务器明确声明哪些外部源有权访问资源，将访问控制权交还给服务器端而非客户端，从根本上解决了跨域访问的标准化问题。

在AI工程的Web后端场景中，AI推理API通常部署在独立服务（如`api.model.com:8080`），而前端应用运行在`app.model.com`，源不同导致浏览器直接拦截响应。正确配置CORS是AI服务对外暴露REST API的必要步骤，错误配置会导致前端完全无法调用模型推理接口。

---

## 核心原理

### 简单请求与预检请求的区分

CORS将跨域请求分为两类，判断依据非常具体：

**简单请求（Simple Request）** 必须同时满足：
- HTTP方法为`GET`、`HEAD`或`POST`之一
- 请求头仅包含`Accept`、`Content-Type`（且值限于`text/plain`、`multipart/form-data`、`application/x-www-form-urlencoded`）等少数几个字段
- 不包含自定义请求头

满足条件的简单请求，浏览器直接发送，服务器在响应头中加入`Access-Control-Allow-Origin`即可放行。

**预检请求（Preflight Request）** 是对不满足简单请求条件的跨域请求的强制前置检查。例如，AI推理接口常用的`Content-Type: application/json` + `POST`组合，就会触发预检。浏览器会先自动发送一个`OPTIONS`方法的HTTP请求到目标URL，服务器必须正确响应这个OPTIONS请求，浏览器才会发送真正的业务请求。

### 关键响应头字段详解

服务器通过以下响应头字段与浏览器"协商"权限：

| 响应头 | 作用 | 示例值 |
|---|---|---|
| `Access-Control-Allow-Origin` | 声明允许的源 | `https://app.model.com` 或 `*` |
| `Access-Control-Allow-Methods` | 声明允许的HTTP方法 | `GET, POST, PUT, DELETE` |
| `Access-Control-Allow-Headers` | 声明允许的请求头 | `Content-Type, Authorization` |
| `Access-Control-Allow-Credentials` | 是否允许携带Cookie/认证信息 | `true` |
| `Access-Control-Max-Age` | 预检结果缓存秒数 | `86400`（即24小时） |

`Access-Control-Max-Age`的值直接影响性能：设置为`86400`意味着同一浏览器对同一接口的预检结果可缓存24小时，避免每次请求都发送OPTIONS预检，对高频调用的AI推理接口尤为重要。

### 携带凭证的跨域请求

当前端使用`fetch(url, { credentials: 'include' })`或`XMLHttpRequest`设置`withCredentials: true`时，浏览器会在跨域请求中携带Cookie。此时服务器端有两个**强制要求**：
1. `Access-Control-Allow-Origin`不能设为通配符`*`，必须指定具体源
2. 必须同时返回`Access-Control-Allow-Credentials: true`

违反任一条件，浏览器都会拦截响应并抛出CORS错误，即使HTTP状态码是200。

---

## 实际应用

### 在Python Flask/FastAPI中配置CORS

FastAPI是AI推理服务常用框架，使用`starlette`的`CORSMiddleware`配置如下：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.model.com"],  # 不要在生产环境用 *
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=86400,
)
```

注意`allow_origins=["*"]`与`allow_credentials=True`同时设置会导致运行时报错，FastAPI的`CORSMiddleware`会主动校验并抛出异常，这是一个常见的配置陷阱。

### Nginx反向代理层统一处理CORS

在生产环境中，AI服务往往通过Nginx代理，可在Nginx层统一添加CORS响应头，避免在每个微服务中重复配置：

```nginx
location /api/ {
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' 'https://app.model.com';
        add_header 'Access-Control-Allow-Methods' 'POST, GET, OPTIONS';
        add_header 'Access-Control-Max-Age' 1728000;
        return 204;
    }
    add_header 'Access-Control-Allow-Origin' 'https://app.model.com';
    proxy_pass http://inference_backend;
}
```

`return 204`（No Content）是预检响应的标准做法，告知浏览器OPTIONS请求成功且无响应体。

---

## 常见误区

**误区1：在服务端返回`Access-Control-Allow-Origin: *`就万能了**

通配符`*`看似最简单，但有两个实际限制：①无法与`Access-Control-Allow-Credentials: true`共存；②在某些企业安全扫描中会触发"CORS配置过于宽松"漏洞报警，导致上线审批被拒。生产环境应明确列出允许的源域名白名单。

**误区2：CORS是服务器安全机制，能阻止恶意调用**

CORS完全是**浏览器行为**，只有浏览器会自动发送预检并检查响应头。使用`curl`、Postman、Python的`requests`库直接发送HTTP请求，CORS头会被完全忽略，请求照常发出并收到响应。因此，CORS不能替代API鉴权（如JWT Token校验），它只保护普通用户的浏览器不被恶意网页劫持发起跨域请求。

**误区3：后端返回正确的CORS头，但前端仍然报错**

这通常发生在服务器返回HTTP 4xx/5xx错误时——浏览器在读取CORS头**之前**若发现HTTP错误，部分情况下仍会显示CORS错误而非真实的业务错误码，掩盖了真实原因。调试时应先用`curl -v`直接调用接口确认响应头内容，再排查业务逻辑错误。

---

## 知识关联

**依赖HTTP协议的前置知识**：理解CORS必须熟悉HTTP请求方法（特别是OPTIONS方法的语义）、HTTP响应状态码（204、200的区别）以及HTTP头部字段的格式规范。CORS的预检机制本质上是HTTP协议层面的一次额外握手，`Access-Control-*`系列响应头是HTTP协议在安全场景的扩展。

**与同源策略（Same-Origin Policy）的关系**：CORS是同源策略的"受控豁免"机制，二者相辅相成。同源策略限制了`document.cookie`读取、Canvas跨域图像操作、`localStorage`访问等多个维度，CORS专门处理其中的**跨源HTTP请求**这一类别，不覆盖同源策略的其他限制。

**向后端认证与授权机制延伸**：在配置了`credentials: include`的跨域场景中，Cookie携带的Session ID或JWT Token会随请求一并发送，这将CORS配置与后端的用户认证系统（如OAuth 2.0的Bearer Token机制）紧密耦合——CORS白名单的源必须是受信任的前端应用域名，否则任意网站都能以用户身份发起跨域请求，造成CSRF（跨站请求伪造）漏洞风险。
