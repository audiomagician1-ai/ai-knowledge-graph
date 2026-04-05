---
id: "mcp-protocol"
concept: "MCP模型上下文协议"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 7
is_milestone: false
tags: ["Agent", "协议"]

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
updated_at: 2026-03-27
---


# MCP模型上下文协议

## 概述

MCP（Model Context Protocol）是由Anthropic于2024年11月正式发布的开放协议标准，专门用于规范AI模型与外部工具、数据源之间的通信方式。其核心目标是将"AI模型如何获取上下文信息"这一问题标准化，让任何符合MCP规范的客户端（如Claude Desktop、Cursor等IDE插件）都能与任何MCP服务器互操作，无需为每对组合单独编写适配层。

MCP诞生前，开发者为每个AI应用单独实现工具调用逻辑，导致大量重复的胶水代码。同一个"查询数据库"工具在不同AI产品中需要写四五套不同的集成代码。MCP通过定义统一的传输层（JSON-RPC 2.0 over stdio或HTTP+SSE）和语义层（Resources、Tools、Prompts三类原语），将这种M×N的集成复杂度降低为M+N。这种降维思想直接借鉴了LSP（Language Server Protocol）在代码编辑器生态中的成功经验。

MCP在Agent系统中的价值在于它解决了"工具发现"与"工具调用"的解耦问题：Agent运行时可以在不重新部署的情况下，通过MCP动态挂载新的数据源或能力，使系统具备真正意义上的可插拔工具扩展性。

## 核心原理

### 三类原语：Resources、Tools、Prompts

MCP协议将服务器能提供的一切抽象为三种原语。**Resources（资源）** 是只读的上下文数据，每个资源通过URI唯一标识，例如 `file:///project/src/main.py` 或 `postgres://db/table/users`，客户端调用 `resources/read` 方法获取其内容。**Tools（工具）** 是有副作用的可调用函数，服务器通过 `tools/list` 暴露工具列表，客户端通过 `tools/call` 触发执行，每个工具携带JSON Schema描述的输入参数规范。**Prompts（提示模板）** 允许服务器向客户端注入结构化的提示片段，支持参数化填充，适合将领域特定指令标准化分发。这三类原语的区分原则是：只读数据用Resources，写操作或副作用用Tools，复用性指令用Prompts。

### 传输层：JSON-RPC 2.0的两种模式

MCP底层通信格式严格遵循JSON-RPC 2.0规范，所有请求必须包含 `jsonrpc: "2.0"`、`id`、`method` 和 `params` 字段。传输层支持两种模式：**stdio模式**下，客户端以子进程方式启动服务器，通过标准输入输出流传递消息，延迟极低，适合本地工具服务器；**HTTP+SSE模式**下，客户端向服务器发送POST请求，服务器通过Server-Sent Events推送响应，支持跨网络部署和多客户端复用。协议还定义了 `notifications/message` 用于服务器向客户端单向推送日志或进度通知，无需客户端轮询。

### 能力协商：初始化握手机制

MCP连接建立时必须执行三步握手：客户端发送 `initialize` 请求，声明自身支持的 `protocolVersion`（当前主流为 `2024-11-05`）和 `capabilities`；服务器返回自己支持的能力集合，如 `{tools: {}, resources: {subscribe: true}}`；最后客户端发送 `initialized` 通知完成握手。`capabilities` 字段决定双方能使用哪些高级特性，例如只有服务器声明 `resources.subscribe: true` 时，客户端才能调用 `resources/subscribe` 监听资源变更，否则该方法调用将返回 `-32601 Method not found` 错误。

### 采样（Sampling）：反向调用模式

MCP有一个与传统工具调用完全相反的机制——**Sampling**。通常是客户端调用服务器的工具，但在Sampling场景下，MCP服务器可以通过 `sampling/createMessage` 方法请求客户端（即AI模型所在侧）执行一次推理。这允许服务器在处理复杂任务时将子任务的推理工作委托给AI模型，实现多步骤的人机协作流程，而整个过程仍在客户端的安全策略控制之下。

## 实际应用

**本地文件系统工具服务器**是MCP最常见的部署场景。以Anthropic官方提供的 `@modelcontextprotocol/server-filesystem` 为例，服务器通过stdio模式启动，暴露 `read_file`、`write_file`、`list_directory` 等Tools，以及以 `file://` 为前缀的Resources。Claude Desktop在配置文件 `claude_desktop_config.json` 中注册该服务器后，用户对话时Claude可以直接读写指定目录下的文件，无需任何额外的Function Calling配置代码。

**数据库上下文注入**是Resources原语的典型用例。一个PostgreSQL MCP服务器可将数据库Schema以 `postgres://mydb/schema` 为URI暴露为Resource，Agent在规划SQL查询前先拉取该Resource作为上下文，再调用 `execute_query` Tool执行语句。相比将整个Schema塞入系统提示词，按需通过Resources动态加载可节省50%以上的上下文窗口占用。

**IDE集成Agent**场景中，Cursor和VS Code Copilot均已支持MCP，开发者可通过MCP服务器将代码审查规则、项目文档、测试覆盖率报告作为结构化Resources暴露给AI，避免重复粘贴上下文的手动操作。

## 常见误区

**误区一：MCP等同于升级版Function Calling。** Function Calling是AI模型推理层的能力，由模型决定何时调用哪个函数，调用格式与具体模型API绑定（如OpenAI的 `tools` 参数格式）。MCP是独立于模型的基础设施协议，定义的是工具服务器的部署、发现和通信规范。一个MCP服务器可以被支持MCP的任何客户端调用，不依赖特定模型的Function Calling实现。两者的关系是：客户端通常用Function Calling驱动AI决策调用哪个MCP工具，但MCP本身不关心AI层发生了什么。

**误区二：Resources是实时数据流。** 除非服务器明确声明支持 `resources.subscribe` 并且客户端订阅了特定资源，否则Resources仅代表一次性快照读取。客户端调用 `resources/read` 拿到的是请求时刻的内容，后续数据变更不会自动推送。将Resources当作WebSocket实时流使用会导致Agent使用过期数据做决策。

**误区三：MCP服务器必须是独立进程。** stdio模式下确实每个服务器是独立子进程，但HTTP+SSE模式允许多个MCP服务端共享同一HTTP服务进程。此外，MCP SDK（Python版为 `mcp` 库，TypeScript版为 `@modelcontextprotocol/sdk`）支持在同一个应用进程内以内存传输方式嵌入服务器逻辑，这在单元测试和轻量级部署中非常实用。

## 知识关联

理解MCP需要扎实的**Function Calling**基础，因为实践中Agent的决策层（用Function Calling让模型选工具）与执行层（用MCP调用工具实现）紧密配合。具体地，客户端将MCP服务器的 `tools/list` 返回结果转换为模型API所需的工具描述格式，模型选定工具后，客户端再将参数通过 `tools/call` 转发给MCP服务器——这一转换逻辑是MCP客户端的核心实现职责。

**RESTful API设计**知识在MCP服务器开发中体现为：Resources的URI设计遵循与REST资源路径相似的层次结构规范，而HTTP+SSE传输模式的端点设计（`POST /message` 发送请求，`GET /sse` 接收推送）也需要HTTP语义的理解。但需注意MCP不是REST API——它没有状态码语义，错误通过JSON-RPC的 `error` 字段返回，错误码 `-32700`（解析错误）、`-32600`（无效请求）、`-32601`（方法未找到）均来自JSON-RPC 2.0标准而非HTTP状态码体系。

随着MCP生态的扩展，下一步实践方向包括：构建支持多服务器并发连接的MCP客户端路由层、实现基于OAuth 2.0的MCP服务器身份验证（MCP 2025路线图中的重点），以及设计跨MCP服务器的工具编排流程以实现复杂的多步Agent任务。