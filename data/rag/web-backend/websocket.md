---
id: "websocket"
concept: "WebSocket实时通信"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 5
is_milestone: false
tags: ["网络"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# WebSocket实时通信

## 概述

WebSocket是一种在单个TCP连接上提供全双工（full-duplex）通信的网络协议，由IETF于2011年通过RFC 6455标准化，W3C同步发布了浏览器端JavaScript API规范。与传统HTTP协议的"请求-响应"模式不同，WebSocket建立连接后，服务器可以在没有客户端请求的情况下主动向客户端推送数据，客户端也可以随时向服务器发送消息，双方通信完全对等。

WebSocket协议的诞生是为了解决HTTP轮询（polling）和长轮询（long-polling）的根本缺陷。HTTP轮询需要客户端每隔几秒发起一次请求来"假装"实时，每次请求携带数百字节的HTTP头部开销，而WebSocket握手完成后每帧数据只有2到10字节的头部开销。在AI应用场景中，大语言模型流式输出（streaming）的token逐字传输正是依赖WebSocket或SSE（Server-Sent Events）实现的，WebSocket因其双向特性成为聊天机器人、协作编辑等AI产品的首选通信层。

## 核心原理

### 握手升级过程（HTTP Upgrade）

WebSocket连接始于一次特殊的HTTP请求，称为"协议升级"。客户端发送包含以下关键头部的HTTP GET请求：

```
GET /chat HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

服务器验证后返回HTTP 101状态码（Switching Protocols），并在响应中包含`Sec-WebSocket-Accept`头，其值是将客户端发来的`Sec-WebSocket-Key`与固定GUID字符串`258EAFA5-E914-47DA-95CA-C5AB0DC85B11`拼接后做SHA-1哈希再Base64编码的结果。这一握手机制防止了非WebSocket客户端误触发协议升级。握手完成后，底层TCP连接从HTTP协议切换为WebSocket帧协议，连接长期保持打开状态。

### 帧结构与数据传输

WebSocket数据以"帧"（Frame）为单位传输，每个帧包含：1位FIN标志（标记消息是否结束）、3位RSV保留位、4位操作码（Opcode）、1位MASK标志、7位基础Payload长度字段。操作码定义了帧类型：`0x1`表示文本帧（UTF-8），`0x2`表示二进制帧，`0x8`为关闭帧，`0x9`和`0xA`分别是Ping和Pong心跳帧。

客户端发往服务器的帧**必须**用4字节掩码（Masking Key）对Payload做XOR混淆，这是RFC 6455的强制要求，目的是防止代理服务器缓存污染攻击。服务器发往客户端的帧则**不需要**掩码。这个非对称设计导致浏览器端发送数据时有微小的额外计算开销。

### 连接生命周期管理

WebSocket连接需要主动管理心跳以检测"僵尸连接"（zombie connections）。标准做法是服务器每隔30秒发送Ping帧，客户端必须在协议层面自动回复Pong帧；若超时未收到Pong，服务器关闭该连接。Node.js的`ws`库中可通过`pingInterval`和`pingTimeout`参数配置这一行为。

正常关闭流程遵循"四次挥手"逻辑：发起方发送关闭帧（包含2字节关闭码，如`1000`表示正常关闭，`1008`表示策略违规），对方回送关闭帧确认，随后底层TCP连接终止。异常断开（网络中断）则需依靠心跳机制检测。

## 实际应用

**Node.js服务端实现（ws库）**：

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    // 广播给所有已连接客户端
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data.toString());
      }
    });
  });
  
  // 心跳检测
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });
});

setInterval(() => {
  wss.clients.forEach(ws => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);
```

**浏览器客户端**使用原生`WebSocket`构造函数，URL方案为`ws://`（明文）或`wss://`（TLS加密，生产环境必须使用）。`readyState`属性有4个值：`0`（CONNECTING）、`1`（OPEN）、`2`（CLOSING）、`3`（CLOSED），在发送消息前必须检查状态为`1`。

**AI流式输出场景**：OpenAI API的流式响应通过SSE实现，但自建推理服务或需要双向交互（如用户中途打断生成）的场景更适合WebSocket。服务端接收用户输入后，将LLM逐步生成的token通过`ws.send(JSON.stringify({type:'token', content:'...'}))` 实时推送，前端累积渲染。

## 常见误区

**误区一：WebSocket可以完全替代HTTP REST API**。WebSocket擅长持续性低延迟双向通信，但不适合做资源查询、文件上传等一次性请求场景。WebSocket连接没有内建的请求-响应匹配机制，若需要在WebSocket上实现RPC语义，必须手动在消息中加入`requestId`字段来匹配响应，这增加了额外复杂度。HTTP REST对于CRUD操作仍是更合适的选择。

**误区二：WebSocket连接是"免费"的，可以无限制建立**。每个WebSocket连接在服务器端占用一个文件描述符（file descriptor），Linux系统默认的`ulimit -n`限制通常为1024或65536。单台Node.js服务器实际能维持的并发WebSocket连接数受内存（每连接约几十KB）和文件描述符双重限制。生产环境需要配置`ulimit`、使用Redis Pub/Sub在多实例间转发消息（如Socket.IO的`socket.io-redis`适配器），才能支撑水平扩展。

**误区三：`ws://`和`wss://`在功能上等同只是加密与否的区别**。实际上许多企业代理服务器和防火墙会拦截未加密的WebSocket连接，因为`ws://`的握手在代理看来像是异常的HTTP请求。生产环境中几乎必须使用`wss://`，且Nginx反向代理需要明确配置`proxy_http_version 1.1`和`proxy_set_header Upgrade $http_upgrade`才能正确转发WebSocket连接。

## 知识关联

**前置知识衔接**：WebSocket的客户端API天然是事件驱动的异步模式，`ws.onmessage`、`ws.onopen`等事件处理器需要用async/await或Promise封装才能与应用业务逻辑优雅集成。例如，等待连接建立可以封装为`new Promise((resolve) => { ws.onopen = resolve; })`，充分利用已掌握的Promise模式。

**后续知识铺垫**：设计聊天系统时，WebSocket是传输层的具体实现，但完整系统还需要解决消息持久化（用户离线消息存储）、房间/频道路由、消息去重（幂等性）和已读状态同步等问题。Socket.IO库在WebSocket之上增加了房间（room）、命名空间（namespace）和自动重连机制，是从原生WebSocket进阶到聊天系统设计的重要过渡技术。理解WebSocket帧协议的双向特性，是后续实现"用户正在输入"状态广播、消息撤回推送等聊天系统高级功能的技术基础。