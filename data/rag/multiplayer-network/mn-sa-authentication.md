---
id: "mn-sa-authentication"
concept: "身份认证"
domain: "multiplayer-network"
subdomain: "server-architecture"
subdomain_name: "服务端架构"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 身份认证

## 概述

身份认证（Authentication）是多人游戏服务端架构中用于确认"这个玩家是谁"的技术流程，其结果决定了服务器是否允许某个客户端建立游戏会话。在网络游戏语境下，身份认证不仅要验证账号密码，还需要处理 Steam、PlayStation Network、Xbox Live 等平台 SDK 返回的第三方令牌，并将其转换为游戏服务内部统一的身份标识。

身份认证协议的工业化标准化发生在 2010 年代初期：OAuth 2.0 规范于 2012 年发布（RFC 6749），JWT（JSON Web Token）规范于 2015 年发布（RFC 7519）。现代游戏服务端普遍以这两项标准为基础，取代了早期游戏直接存储明文密码、服务器间通过 Session ID 传递状态的做法。

对于游戏服务端而言，身份认证是网关服务器接收客户端连接之后最先执行的检查步骤。未通过认证的连接在到达游戏逻辑服务（如房间服务器、匹配服务器）之前就会被拒绝，从而防止未授权客户端消耗业务层资源或伪造玩家身份发送操作指令。

---

## 核心原理

### JWT 令牌的结构与验证

JWT 由三段 Base64URL 编码的字符串拼接而成，格式为 `Header.Payload.Signature`。Header 声明签名算法（如 `HS256` 或 `RS256`），Payload 携带声明字段（Claims），例如 `sub`（玩家 UID）、`exp`（过期时间戳）、`iat`（签发时间）。Signature 由服务端密钥对前两段内容做 HMAC-SHA256 或 RSA 签名生成。

游戏网关服务器收到客户端附带的 JWT 后，不需要查询数据库，仅用本地存储的公钥（RS256 场景）或对称密钥（HS256 场景）重新计算 Signature 并比对，验证时间通常在 **1 毫秒以内**。同时检查 `exp` 字段，若当前时间超过该时间戳则视为令牌过期，强制客户端重新登录或刷新令牌。这种无状态验证方式使得游戏网关可以水平扩展，而无需共享 Session 存储。

### OAuth 2.0 授权码流程在游戏中的应用

当玩家通过 Steam 登录时，游戏客户端调用 Steam SDK 获取一个 **Steam Ticket**（一段加密字节串），随后将该 Ticket 发送给游戏自有的认证服务。认证服务调用 Steam Web API 的 `ISteamUserAuth/AuthenticateUserTicket` 接口，由 Steam 服务器验证 Ticket 真实性并返回 `steamid`。认证服务拿到 `steamid` 后，查找或创建对应的游戏账号，再签发一个游戏内部 JWT 返回给客户端。这一流程确保游戏服务器永远不会直接信任客户端声称的 Steam 身份，所有验证都经过 Steam 官方服务背书。

PlayStation 和 Xbox 平台采用类似流程，分别通过 PSN ID Token 和 Xbox XSTS Token 完成跨平台身份映射。

### 令牌刷新机制与双令牌设计

生产环境游戏服务通常发放两种令牌：**Access Token**（访问令牌，有效期短，通常 15 分钟至 1 小时）和 **Refresh Token**（刷新令牌，有效期长，通常 7 至 30 天）。Access Token 随每个 API 请求携带，Refresh Token 仅用于向认证服务申请新的 Access Token。

这种设计的安全价值在于：如果 Access Token 被截获，攻击者的可利用窗口仅限于其有效期（最多 1 小时），而不是整个账号会话时长。Refresh Token 通常与设备指纹或 IP 段绑定，异常换绑行为会触发强制重新验证，配合游戏反作弊系统检测账号共享行为。

---

## 实际应用

**多平台统一账号体系**：Fortnite（堡垒之夜）采用 Epic Games 账号体系，玩家在 PS5、Xbox、PC、Switch 上登录时，各平台 SDK 令牌均经过 Epic 认证服务映射为同一个 Epic Account ID，游戏服务端始终使用该内部 ID 索引玩家数据，从而实现跨平台进度共享。

**游戏内认证服务的部署位置**：认证服务通常部署为独立微服务，接口地址在网关层单独暴露（如 `/auth/login`、`/auth/refresh`），其余游戏业务接口（匹配、房间、商店）均在网关层配置 JWT 中间件，对请求头 `Authorization: Bearer <token>` 进行统一拦截验证，只有验证通过的请求才被路由至对应微服务。

**会话撤销场景**：当玩家被封禁时，游戏运营后台向 Redis 中写入该玩家 UID 的封禁记录。由于 JWT 本身无状态，网关中间件在验证签名和过期时间之后还需查询一次 Redis 黑名单，若命中则立即拒绝请求。这是 JWT 无状态特性与账号封禁业务需求之间的经典折衷方案。

---

## 常见误区

**误区一：混淆认证（Authentication）与授权（Authorization）**
身份认证只回答"你是谁"，例如验证某个 JWT 属于 UID 为 `100234` 的玩家；而授权回答"你能做什么"，例如判断该玩家是否有权进入某个付费游戏模式。游戏后端新手常将两者写在同一段逻辑中，导致封禁检查、权限检查、身份验证耦合在一起，难以独立更新。

**误区二：将平台 SDK 令牌直接作为游戏会话令牌使用**
Steam Ticket 和 PSN Token 是短期一次性凭证，不应被游戏服务器缓存后当作持久身份令牌使用。正确做法是完成平台验证后立即换发游戏自有 JWT，游戏后续所有服务只认游戏 JWT，避免因平台令牌过期导致游戏会话意外中断，也避免游戏服务对外部平台接口产生运行时强依赖。

**误区三：认为 HTTPS 使 JWT 签名验证变得多余**
HTTPS 保证的是传输层加密，防止中间人窃听；JWT 签名验证保证的是令牌内容未被篡改，且确实由本服务签发，而不是客户端伪造的。两者防御的攻击面不同，缺少 JWT 签名验证，即便使用 HTTPS，攻击者仍可伪造任意 Payload 声称自己是管理员账号。

---

## 知识关联

**前置概念——网关服务器**：网关服务器是身份认证逻辑的物理执行位置，JWT 中间件作为插件挂载在网关的请求处理管道上。网关负责提取令牌、调用验证逻辑，并将解析出的玩家 UID 以请求头形式（如 `X-Player-ID`）注入到转发给下游服务的请求中，使下游微服务无需重复验证。

**后续概念——速率限制**：速率限制策略通常以通过身份认证后的玩家 UID 为维度计数，而非以 IP 地址为维度，这样可以精确控制单个账号的请求频率，防止账号级别的刷接口行为，同时不误伤共享同一公网 IP 的合法玩家群体。

**后续概念——玩家数据模型**：认证服务在首次验证第三方平台令牌时，若数据库中不存在对应账号，会触发"注册流程"，创建一条新的玩家数据记录，并初始化玩家数据模型中的基础字段（如创建时间、平台绑定信息）。因此认证服务是玩家数据生命周期的起点。