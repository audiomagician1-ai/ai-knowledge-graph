---
id: "http-protocol"
concept: "HTTP协议"
domain: "ai-engineering"
subdomain: "cs-fundamentals"
subdomain_name: "计算机基础"
difficulty: 3
is_milestone: false
tags: ["网络", "Web"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# HTTP协议

## 概述

HTTP（HyperText Transfer Protocol，超文本传输协议）是一种用于在客户端与服务器之间传输超文本数据的应用层协议，运行在TCP/IP协议栈之上，默认使用**端口80**。它由蒂姆·伯纳斯-李（Tim Berners-Lee）于1989年在欧洲核子研究组织（CERN）提出，最初版本HTTP/0.9仅支持GET方法和HTML文档传输。1996年发布的HTTP/1.0（RFC 1945）引入了请求头、响应码和多媒体内容支持；1997年的HTTP/1.1（RFC 2068）增加了持久连接和分块传输；2015年的HTTP/2引入了二进制分帧和多路复用；2022年正式标准化的HTTP/3则基于QUIC协议（运行在UDP上）彻底替代了TCP底层传输。

HTTP是一种**无状态协议**，这意味着服务器在处理完一次请求后不会保留任何关于该客户端的信息，每次请求都是完全独立的。这一设计使得服务器扩展变得简单，但也带来了用户身份识别的挑战，因此后续衍生出了Cookie、Session等机制来弥补无状态带来的不足。在AI工程中，HTTP是调用远程模型推理接口（如OpenAI API、HuggingFace Inference API）的基础传输协议，几乎所有的RESTful API通信都依赖HTTP实现。

---

## 核心原理

### 请求-响应模型

HTTP采用严格的**请求-响应（Request-Response）**模式：客户端发起请求，服务器返回响应，一次交互完成后（HTTP/1.0中）连接即关闭。一个完整的HTTP请求由三部分组成：**请求行**（包含方法、URL、协议版本）、**请求头（Headers）**和可选的**请求体（Body）**。

典型的HTTP/1.1请求结构如下：
```
GET /api/v1/models HTTP/1.1
Host: api.example.com
Authorization: Bearer sk-abc123
Accept: application/json
```

服务器响应同样由三部分组成：**状态行**（协议版本 + 状态码 + 状态文本）、**响应头**和**响应体**。例如，`HTTP/1.1 200 OK` 表示请求成功，`404 Not Found` 表示资源不存在，`429 Too Many Requests` 是AI API限流时最常见的错误码。

### HTTP方法语义

HTTP定义了多种请求方法，每种方法有明确的语义约定：

| 方法 | 语义 | 是否有Body | 幂等性 |
|------|------|-----------|--------|
| GET | 获取资源 | 否 | 是 |
| POST | 创建资源/提交数据 | 是 | 否 |
| PUT | 完整替换资源 | 是 | 是 |
| PATCH | 部分更新资源 | 是 | 否 |
| DELETE | 删除资源 | 可选 | 是 |

在AI工程实践中，向大语言模型发送推理请求（如`POST /v1/chat/completions`）使用POST方法，因为每次请求创建一次新的推理计算，且请求体包含输入文本；而查询可用模型列表（如`GET /v1/models`）则使用GET方法。**幂等性**意味着多次执行同一请求结果相同，这对于客户端重试逻辑设计至关重要。

### HTTP状态码分类

HTTP状态码是三位数字，按首位数字分为五类：
- **1xx（信息性）**：如`100 Continue`，服务器告知客户端继续发送请求体
- **2xx（成功）**：`200 OK`（成功）、`201 Created`（资源已创建）、`204 No Content`（无响应体）
- **3xx（重定向）**：`301 Moved Permanently`（永久重定向）、`302 Found`（临时重定向）
- **4xx（客户端错误）**：`400 Bad Request`（请求格式错误）、`401 Unauthorized`（未认证）、`403 Forbidden`（无权限）、`404 Not Found`
- **5xx（服务端错误）**：`500 Internal Server Error`、`503 Service Unavailable`

在调用AI推理API时，`422 Unprocessable Entity` 通常表示请求参数格式正确但语义错误（如`temperature`值超出0-2范围），这与`400 Bad Request`（JSON格式本身错误）需要区别处理。

### HTTP/1.1的持久连接与HTTP/2的多路复用

HTTP/1.1通过`Connection: keep-alive`头实现**持久连接**，避免每次请求都重新建立TCP三次握手，但每条TCP连接在同一时刻只能处理一个请求（队头阻塞问题）。HTTP/2引入**二进制分帧层**，将数据切割为帧（Frame），同一TCP连接上的多个请求可以交错传输，真正实现多路复用，延迟显著降低。HTTP/3将底层协议换为QUIC（基于UDP），在弱网环境下（如移动端AI应用）丢包恢复速度比TCP快3-5倍。

---

## 实际应用

**调用OpenAI Chat Completions API**是HTTP协议在AI工程中的典型场景。完整请求如下：

```http
POST https://api.openai.com/v1/chat/completions
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "你好"}],
  "temperature": 0.7
}
```

服务器返回`200 OK`及JSON格式的响应体，其中`choices[0].message.content`字段包含模型回复。若API密钥无效，返回`401 Unauthorized`；若每分钟请求数超过限额，返回`429 Too Many Requests`，客户端应读取`Retry-After`响应头中的等待秒数后重试。

**流式响应（Streaming）**是另一个重要应用：通过设置`"stream": true`并配合`Transfer-Encoding: chunked`响应头，服务器以Server-Sent Events（SSE）格式逐块推送生成的token，客户端可实时渲染文字输出，而非等待全部生成完毕。这正是ChatGPT打字机效果的底层HTTP机制。

---

## 常见误区

**误区一：认为HTTP和HTTPS是两种完全不同的协议。** HTTP本身不加密，明文传输所有内容（包括Authorization头中的API密钥）。HTTPS并非独立协议，而是HTTP运行在TLS（Transport Layer Security）加密层之上，默认端口从80变为443，数据格式与HTTP完全相同，仅在传输层增加了加密和证书验证。因此HTTPS的请求方法、状态码、头部格式与HTTP一致。

**误区二：GET请求不能携带Body。** HTTP规范（RFC 7231）技术上并未禁止GET请求包含Body，但强烈不建议——大多数服务器、代理、CDN会忽略GET请求的Body，且语义上GET表示"获取"而非"提交"。在ElasticSearch中`GET /index/_search`携带JSON Body是一个著名的反常规用法，造成许多工程师困惑。

**误区三：HTTP/2一定比HTTP/1.1快。** HTTP/2的多路复用优势在高延迟、多资源的场景下才明显。若服务器在单一TCP连接上发生严重丢包（如移动网络），HTTP/2的所有请求会因TCP层队头阻塞而全部停滞，反而不如HTTP/1.1的多连接策略，这正是HTTP/3改用UDP+QUIC的直接原因。

---

## 知识关联

**前置知识**：理解HTTP需要掌握TCP/IP协议——HTTP依赖TCP提供的可靠字节流传输，HTTP的连接建立本质上是TCP三次握手。HTTP的端口号（80/443）属于TCP端口空间，DNS解析域名为IP后，HTTP才能确定目标服务器地址。

**后续概念**：
- **Fetch API与网络请求**：浏览器端发起HTTP请求的现代JavaScript接口，直接对应HTTP的方法、头部和状态码操作
- **Session与Cookie**：HTTP无状态特性的补充机制，Cookie通过`Set-Cookie`响应头和`Cookie`请求头在HTTP报文中传递
- **CORS跨域**：浏览器安全策略，通过HTTP的`Origin`请求头和`Access-Control-Allow-Origin`响应头控制跨域HTTP请求权限
- **SSL/TLS与HTTPS**：在HTTP传输层添加加密，将HTTP的明文通信升级为密文，使用443端口代替80端口
