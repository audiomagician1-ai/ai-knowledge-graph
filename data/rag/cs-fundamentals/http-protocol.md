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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# HTTP协议

## 概述

HTTP（HyperText Transfer Protocol，超文本传输协议）是用于在客户端与服务器之间传输超文本数据的应用层协议，运行在TCP/IP协议栈之上，默认使用**80端口**。它是万维网数据通信的基础，由蒂姆·伯纳斯-李（Tim Berners-Lee）于1989年在欧洲核子研究组织（CERN）首次提出，1991年发布了最初的HTTP/0.9版本，该版本仅支持GET方法和HTML文档传输。

HTTP是一种**无状态（Stateless）**协议，即服务器不会在两次请求之间保留任何客户端的状态信息。每次请求都是独立的，服务器处理完一次请求后不会记住之前的交互。这一特性既带来了水平扩展的便利，也催生了Cookie、Session等状态管理机制的出现。

从AI工程视角来看，AI服务的绝大多数对外接口（API）都通过HTTP协议暴露。无论是调用OpenAI的`/v1/chat/completions`端点，还是部署自己的模型推理服务，理解HTTP协议的请求结构、响应码含义和头部字段，是正确调试和集成AI服务的前提。

## 核心原理

### 请求与响应结构

HTTP通信遵循严格的**请求-响应（Request-Response）**模型。一个完整的HTTP请求由三部分组成：

1. **请求行（Request Line）**：包含方法（Method）、请求目标URL和协议版本，例如 `GET /api/models HTTP/1.1`
2. **请求头（Headers）**：键值对形式的元数据，如 `Content-Type: application/json` 指定请求体的数据格式，`Authorization: Bearer sk-xxx` 携带认证令牌
3. **请求体（Body）**：可选部分，POST/PUT请求用来携带数据，GET请求通常没有请求体

HTTP响应同样包含三部分：**状态行**（如 `HTTP/1.1 200 OK`）、**响应头**和**响应体**。

### HTTP方法语义

HTTP/1.1定义了8种标准方法，AI工程中最常用的是：

| 方法 | 语义 | 典型场景 |
|------|------|----------|
| GET | 获取资源，幂等且无副作用 | 查询模型列表、获取任务状态 |
| POST | 提交数据，创建资源或触发操作 | 发送对话请求、上传文件 |
| PUT | 全量替换指定资源 | 更新整个配置对象 |
| DELETE | 删除指定资源 | 删除已上传的文件 |
| PATCH | 局部更新资源 | 修改模型参数的某个字段 |

**幂等性**是关键概念：GET、PUT、DELETE多次执行结果相同；POST不是幂等的，重复发送可能创建多条记录。

### HTTP状态码体系

HTTP状态码是三位数字，分为5类，每类有明确的语义范围：

- **1xx（信息）**：`100 Continue` 表示服务器已收到请求头，客户端可继续发送请求体
- **2xx（成功）**：`200 OK` 成功，`201 Created` 创建成功，`204 No Content` 成功但无响应体
- **3xx（重定向）**：`301 Moved Permanently` 永久重定向，`302 Found` 临时重定向
- **4xx（客户端错误）**：`400 Bad Request` 请求格式错误，`401 Unauthorized` 未认证，`403 Forbidden` 无权限，`404 Not Found` 资源不存在，`429 Too Many Requests` 触发限流
- **5xx（服务端错误）**：`500 Internal Server Error` 服务器内部错误，`503 Service Unavailable` 服务不可用

在AI API调用中，`429`状态码尤为重要——它表示超出了请求速率限制（Rate Limit），通常响应头中会包含 `Retry-After` 字段告知客户端需要等待的秒数。

### HTTP版本演进

- **HTTP/1.0**（1996年，RFC 1945）：每次请求需建立独立TCP连接，开销大
- **HTTP/1.1**（1997年，RFC 2068）：引入**持久连接（Keep-Alive）**，默认复用TCP连接；引入**分块传输编码（Chunked Transfer Encoding）**，支持流式响应——这正是AI大模型打字机效果的技术基础
- **HTTP/2**（2015年，RFC 7540）：引入**多路复用（Multiplexing）**，在同一TCP连接上并行传输多个请求，头部采用HPACK算法压缩，性能大幅提升
- **HTTP/3**（2022年，RFC 9114）：放弃TCP，改用基于UDP的**QUIC协议**，解决了TCP队头阻塞问题

## 实际应用

### 调用AI推理API

向OpenAI发送对话请求时，一个完整的HTTP请求如下：

```
POST /v1/chat/completions HTTP/1.1
Host: api.openai.com
Content-Type: application/json
Authorization: Bearer sk-xxxxxxxxxxxxxxxx

{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "你好"}],
  "stream": true
}
```

当 `stream: true` 时，服务器返回 `Transfer-Encoding: chunked` 头，通过HTTP/1.1的分块传输持续推送 `data: {...}` 格式的SSE（Server-Sent Events）数据，实现逐字输出效果。

### 理解限流与重试

AI平台API通常在响应头中返回限流信息：
```
x-ratelimit-limit-requests: 500
x-ratelimit-remaining-requests: 499
x-ratelimit-reset-requests: 2024-01-01T00:00:01Z
```

客户端程序需要检查这些头部字段，在收到 `429` 响应时实现指数退避重试策略。

## 常见误区

### 误区一：认为GET请求不能携带数据

GET请求虽然没有请求体（Body），但可以通过**查询字符串（Query String）**传递参数，例如 `GET /search?query=llm&limit=10`。GET不应有请求体是HTTP语义规范，而非技术限制——部分工具允许发送带Body的GET请求，但这违反RFC规范，行为不可预期。

### 误区二：混淆401与403状态码

`401 Unauthorized` 的实际含义是"**未认证**"（Unauthenticated），即服务器不知道你是谁，通常要求客户端提供 `Authorization` 头。`403 Forbidden` 是"**已认证但无权限**"，服务器知道你的身份，但你没有访问该资源的权限。在调试AI API时，API Key填写错误返回401，Key正确但无该模型访问权限则返回403。

### 误区三：认为HTTP/2完全替代了HTTP/1.1

HTTP/2的多路复用解决了并发性能问题，但HTTP/1.1的分块传输编码在流式AI响应场景中仍被广泛使用。许多AI推理框架（如vLLM、Ollama）的默认部署就使用HTTP/1.1的流式传输，而非HTTP/2。两个版本在实际生产中长期共存，选择哪个取决于具体的网络环境和延迟需求。

## 知识关联

**前置知识（TCP/IP协议）**：HTTP运行在TCP之上，TCP的三次握手为HTTP提供了可靠的连接。HTTP/1.1的Keep-Alive就是减少TCP握手次数的优化手段；HTTP/3改用QUIC（基于UDP）则彻底重构了这一关系。理解TCP的连接建立过程，有助于分析HTTP请求的首字节时间（TTFB）瓶颈。

**后续知识延伸**：
- **Fetch API**：是浏览器端发起HTTP请求的现代JavaScript接口，所有请求方法、头部设置都直接映射到HTTP协议概念
- **Session与Cookie**：是为了解决HTTP无状态特性而诞生的机制，通过 `Set-Cookie` 响应头和 `Cookie` 请求头在多次HTTP请求间传递状态
- **CORS跨域**：是浏览器对HTTP请求的安全限制，通过 `Access-Control-Allow-Origin` 等HTTP响应头来控制跨域访问权限
- **SSL/TLS与HTTPS**：是在HTTP下层加入TLS握手，使HTTP传输内容加密，端口从80变为443，但HTTP协议本身的报文结构不变