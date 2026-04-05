---
id: "fetch-api"
concept: "Fetch API与网络请求"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 4
is_milestone: false
tags: ["JS", "网络"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 81.7
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.971
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Fetch API 与网络请求

## 概述

Fetch API 是浏览器原生提供的基于 Promise 的网络请求接口，于 2015 年随 WHATWG Fetch 规范首次标准化，并在 Chrome 42、Firefox 39、Edge 14 等版本中陆续实装，取代了自 1999 年 IE5 引入的 `XMLHttpRequest`（XHR）成为现代前端发起 HTTP 请求的首选方案。与 XHR 的事件回调模型不同，Fetch 的每次请求返回一个 `Promise<Response>`，天然支持 async/await 语法链，使异步网络代码可以写成近乎同步的风格。

Fetch API 在 AI 工程前端场景中尤为重要。调用 OpenAI、Hugging Face 等大模型 REST 接口、上传图片到视觉识别服务、以 Streaming 模式逐 token 渲染模型输出，均依赖 Fetch 的流式读取能力（`ReadableStream`）。相比 axios 等第三方库，Fetch 无需额外安装，运行时体积为零，在 Edge Runtime 和 Service Worker 环境中也可直接使用，这对 Next.js API Routes 与 Cloudflare Workers 部署的 AI 应用至关重要。

---

## 核心原理

### 基本请求与 Response 对象

调用 `fetch(url, options)` 后，浏览器发出 HTTP 请求并返回 Promise。该 Promise 在**收到响应头**时即 resolve 为 `Response` 对象，而非等待响应体完全下载完毕。因此必须二次调用 `response.json()`、`response.text()` 或 `response.blob()` 等方法来消费响应体，这两步均为异步操作：

```javascript
const response = await fetch('https://api.example.com/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json',
              'Authorization': 'Bearer sk-...' },
  body: JSON.stringify({ prompt: 'hello' })
});
// 此时 response.ok 可读，但 body 尚未解析
const data = await response.json(); // 第二次 await
```

`Response` 对象包含 `status`（HTTP 状态码）、`ok`（200–299 范围为 true）、`headers`（`Headers` 对象）和 `body`（`ReadableStream`）四类属性。**关键点**：Fetch 对 4xx/5xx 状态码不会抛出异常，只有网络层错误（DNS 失败、CORS 拒绝、请求超时无内置支持）才会导致 Promise reject。

### CORS 与请求模式

Fetch 的 `mode` 选项控制跨域行为，共三个值：`cors`（默认，遵循 CORS 协议）、`same-origin`（跨域直接拒绝）、`no-cors`（允许跨域但响应体不可读，type 为 `"opaque"`）。调用第三方 AI API 时必须确认服务端返回正确的 `Access-Control-Allow-Origin` 响应头；若服务端不支持 CORS，前端须通过自建 proxy 转发请求，而非使用 `no-cors` 模式，后者无法读取响应数据。

预检请求（Preflight）由浏览器自动发送：当请求方法不是 GET/POST/HEAD，或 Content-Type 不属于 `application/x-www-form-urlencoded`、`multipart/form-data`、`text/plain` 三者之一时，浏览器会先发一次 `OPTIONS` 请求。向 AI 接口发送 `application/json` 格式的 POST 请求时，必然触发预检，服务端需返回 `Access-Control-Allow-Headers: Content-Type, Authorization`。

### Streaming 响应与 ReadableStream

大语言模型接口常以 Server-Sent Events（SSE）或 `Transfer-Encoding: chunked` 格式逐步返回 token，Fetch 的 `response.body` 是一个 `ReadableStream`，可通过 `getReader()` 逐块消费：

```javascript
const reader = response.body.getReader();
const decoder = new TextDecoder('utf-8');
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value, { stream: true });
  // 解析 "data: {...}\n\n" 格式，实时更新 UI
}
```

每次 `reader.read()` 返回的 `value` 是 `Uint8Array`，需用 `TextDecoder` 转码。`stream: true` 参数告知解码器当前块可能在多字节字符边界截断，避免乱码。

### 超时与取消请求

Fetch 本身不提供超时参数，必须结合 `AbortController` 实现。创建 `AbortController` 实例，将 `controller.signal` 传入 fetch options，调用 `controller.abort()` 后，对应请求的 Promise 会以 `AbortError` reject：

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 秒超时
try {
  const res = await fetch(url, { signal: controller.signal });
  clearTimeout(timeoutId);
} catch (e) {
  if (e.name === 'AbortError') console.log('请求已超时');
}
```

同一个 `AbortController` 的 signal 可同时传给多个 `fetch()` 调用，一次 `abort()` 可批量取消，适用于用户切换页面时中止多个并行 AI 推理请求的场景。

---

## 实际应用

**调用 OpenAI Chat Completions 接口**：将模型参数序列化为 JSON body，设置 `Authorization: Bearer <API_KEY>`，处理 `stream: true` 的 SSE 响应，解析每行 `data: {"choices":[{"delta":{"content":"..."}}]}` 并追加到 UI 文本框，最后一行为 `data: [DONE]` 表示流结束。

**上传图片到视觉模型**：使用 `FormData` 对象将 `File` 实例 append 进去，无需手动设置 `Content-Type`（浏览器会自动填写含 boundary 的 `multipart/form-data`），再通过 Fetch 以 POST 发送。错误地手动设置 `Content-Type: multipart/form-data` 会导致 boundary 缺失，服务端无法解析。

**批量并发请求**：结合 `Promise.all` 同时发起多个 Fetch，例如并行查询向量数据库的多个分片：`const results = await Promise.all(shardUrls.map(url => fetch(url).then(r => r.json())))`，总耗时取决于最慢的单个请求而非累加时间。

---

## 常见误区

**误区一：`fetch` 失败等同于 Promise reject**。实际上，只要服务器返回了任意 HTTP 响应（包括 404、500），`fetch` 的 Promise 就会 resolve。必须显式检查 `response.ok` 或 `response.status`，否则会把服务端错误误当成成功处理。正确做法：`if (!response.ok) throw new Error(\`HTTP ${response.status}\`)`。

**误区二：可以多次调用 `response.json()` 或 `response.text()`**。`Response` 的 body 是一次性流，第一次调用消费后，`response.bodyUsed` 变为 `true`，再次调用会抛出 `TypeError: body stream already read`。若需多次读取，应先调用 `response.clone()` 获取副本。

**误区三：Fetch 默认发送 Cookie**。默认情况下 Fetch 的 `credentials` 选项为 `"same-origin"`，跨域请求不携带 Cookie 或 Authorization 头中的凭据。调用需 Session 鉴权的跨域 AI 后端时，需显式设置 `credentials: "include"`，且服务端必须同时返回 `Access-Control-Allow-Credentials: true` 并明确指定 `Access-Control-Allow-Origin`（不能为 `*`）。

---

## 知识关联

Fetch API 以 **Promise** 为返回值基础，`async/await` 语法直接作用于每个 `fetch()` 和 `response.json()` 调用；若未掌握 Promise 的 resolve/reject 机制，会难以理解"网络成功但业务失败"的双层错误处理模式。**HTTP 协议**知识决定了如何正确构造请求头（`Content-Type`、`Authorization`）、理解预检请求的触发条件、以及 chunked 传输与 SSE 的区别，这些均直接影响 Fetch 的配置方式。在 AI 工程实践中，Fetch 与 **Web Workers** 配合可将网络请求移出主线程，与 **Service Worker** 结合可实现模型推理结果的离线缓存，与 **WebSocket** 相比，Fetch+SSE 模式更适合单向流式输出（如 LLM 生成），而 WebSocket 更适合双向实时交互场景。