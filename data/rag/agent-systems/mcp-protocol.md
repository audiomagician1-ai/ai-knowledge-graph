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
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# MCP模型上下文协议

## 概述

MCP（Model Context Protocol，模型上下文协议）是由Anthropic于2024年11月正式发布的开放标准协议，专门用于规范AI模型与外部工具、数据源之间的双向通信方式。在MCP出现之前，每个AI应用都需要为每个工具单独编写集成代码，导致M×N的集成爆炸问题——M个模型与N个工具之间需要M×N套定制接口。MCP通过统一的协议层将这一复杂度降低为M+N，任何符合MCP规范的客户端都可以无缝连接任何MCP服务器。

MCP的设计哲学借鉴了语言服务器协议（LSP，Language Server Protocol）的成功经验。LSP统一了IDE与编程语言工具链之间的接口，MCP则将同样的思路应用于AI Agent与外部世界的交互。协议底层采用JSON-RPC 2.0作为消息格式，支持通过标准输入输出（stdio）和HTTP+SSE两种传输方式建立连接，这使得MCP服务器可以是本地进程，也可以是远程Web服务。

MCP的重要性在于它解决了Agent系统的工具碎片化难题。当一个Agent需要同时访问文件系统、数据库、GitHub仓库和Slack消息时，没有MCP则需要为每种资源编写不同的适配层；有了MCP，开发者只需实现一次MCP服务器接口，任何支持MCP的Agent框架（如Claude Desktop、Cursor、LangChain）均可直接调用。

## 核心原理

### 架构三角：Host、Client与Server

MCP定义了清晰的三层架构。**Host**是运行AI模型的宿主应用程序，例如Claude Desktop或一个自定义的Agent程序；**Client**是Host内嵌的协议客户端，负责与MCP服务器维持一对一的有状态连接；**Server**是暴露特定能力的独立进程，可以访问本地文件、数据库或调用远程API。一个Host可以同时持有多个Client，每个Client连接不同的Server，形成星型拓扑结构。

### 三类原语：Resources、Tools与Prompts

MCP协议将服务器能力抽象为三种原语：

**Resources（资源）** 是只读的数据单元，类似REST中的GET端点。每个Resource有唯一的URI标识（例如`file:///home/user/report.pdf`或`postgres://localhost/db/schema`），客户端通过`resources/read`请求获取内容。资源支持订阅机制，服务器可在资源变更时主动推送通知。

**Tools（工具）** 是可执行的操作，对应有副作用的函数调用。每个Tool必须提供JSON Schema格式的参数描述，模型在生成调用请求时依据该Schema填充参数。工具调用的完整流程是：模型输出`tools/call`请求 → Client转发至Server → Server执行并返回结果 → 模型基于结果继续推理。与Function Calling的关键区别在于，MCP的工具定义存储在Server侧而非每次注入到上下文中。

**Prompts（提示模板）** 是服务器预定义的可复用提示片段，客户端通过`prompts/get`动态获取，适合将领域特定的指令集中管理在服务器端。

### 连接生命周期与能力协商

MCP连接建立时必须经历三个阶段：**初始化（Initialize）**——客户端发送包含协议版本号（当前为`2024-11-05`）和自身支持能力列表的请求；**能力协商**——服务器返回其支持的原语类型和特性（如是否支持流式传输、是否支持资源订阅）；**运行阶段**——双方基于协商结果进行正式通信。协议要求客户端在收到`initialize`响应后必须发送`initialized`通知，这一握手机制确保双方状态同步。

安全模型方面，MCP规范要求Host负责用户授权决策，Server不得直接请求权限，所有敏感操作必须经过Host的显式批准流程，防止恶意服务器绕过用户控制执行危险操作。

## 实际应用

**本地开发场景**：开发者可以构建一个MCP文件系统服务器，暴露项目目录的读写工具。Claude Desktop连接该服务器后，可直接读取代码文件、写入修改结果，无需将文件内容手动粘贴到对话框。Anthropic官方提供了`@modelcontextprotocol/server-filesystem`的Node.js参考实现，配置仅需在`claude_desktop_config.json`中指定服务器启动命令即可。

**数据库查询自动化**：企业可将内部PostgreSQL数据库封装为MCP服务器，暴露`execute_query`和`list_tables`两个工具。业务人员用自然语言提问，Agent通过MCP工具生成并执行SQL，返回结构化数据。关键安全措施是在Server层强制只读权限，而非依赖模型的自我约束。

**多服务器编排**：一个复杂的研究Agent可同时连接Web搜索MCP服务器（工具：`search`、`fetch_page`）、文献数据库MCP服务器（工具：`search_papers`、`get_abstract`）和本地笔记MCP服务器（资源：`notes://`，工具：`create_note`）。Agent在单次任务中可跨越三个服务器调用，协议层自动处理连接管理，开发者无需编写跨服务协调代码。

## 常见误区

**误区一：MCP是Function Calling的替代品**。实际上两者层次不同。Function Calling是模型层面的能力，描述"模型如何表达调用意图"；MCP是传输层协议，描述"调用请求如何路由到执行环境"。在MCP架构中，模型仍然使用Function Calling机制生成工具调用请求，MCP负责将这个请求可靠地传递给正确的服务器并带回结果。两者是互补而非竞争关系。

**误区二：MCP服务器必须是远程HTTP服务**。MCP支持两种传输模式，其中stdio模式更适合本地工具——服务器作为子进程被启动，通过标准输入输出与客户端通信，完全不需要网络端口和身份验证配置。许多官方参考实现（如`server-sqlite`、`server-git`）均默认使用stdio模式，这使得本地MCP服务器的安全边界等同于本机进程权限，而非网络服务权限。

**误区三：实现一个MCP服务器需要从零处理JSON-RPC细节**。Anthropic和社区提供了Python SDK（`mcp`包）和TypeScript SDK（`@modelcontextprotocol/sdk`），开发者只需用装饰器标注函数即可将其注册为Tool或Resource，SDK自动处理序列化、连接管理和生命周期。一个最简MCP工具服务器的Python实现核心代码不超过15行。

## 知识关联

理解MCP需要以**工具调用（Function Calling）**为前提——MCP的Tools原语在语义上直接对应Function Calling中的函数定义，其JSON Schema参数描述格式与OpenAI Function Calling规范高度一致；熟悉Function Calling的开发者可以快速理解MCP工具的定义方式，差异主要在于定义的存储位置从客户端上下文迁移到了服务器端。

**RESTful API设计**经验有助于理解MCP Resources原语的设计逻辑——Resources的URI寻址机制和只读语义与REST的GET资源概念直接对应，而Tools的有副作用执行则类似于REST中的POST/PUT操作。具备REST设计经验的开发者在设计MCP服务器的接口边界时，可复用资源与操作分离的设计原则。

MCP目前正在向**多Agent协作**方向扩展：2024年发布的规范草案中加入了Agent-to-Agent通信的实验性支持，允许一个MCP服务器本身也是一个Agent，从而构建可动态组合的Agent网络拓扑。这代表了MCP从"模型访问工具"向"Agent访问Agent"的架构演进方向。
