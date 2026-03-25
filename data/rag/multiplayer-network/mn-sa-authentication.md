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
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 身份认证

## 概述

身份认证（Authentication）是网络多人游戏服务端架构中验证"玩家是谁"的过程，与授权（Authorization，验证"玩家能做什么"）是两个不同的概念。在游戏服务器收到客户端连接请求时，必须先确认请求方的真实身份，才能决定是否允许其加入游戏房间、访问角色数据或执行游戏内操作。

游戏身份认证机制经历了从简单用户名/密码到现代令牌体系的演变。2010年前，大多数端游直接在登录服务器上校验明文或MD5哈希密码；2012年前后，随着Steam、PlayStation Network等平台崛起，平台SDK认证逐渐成为主流。2018年后，JWT（JSON Web Token）在游戏后端中被广泛采用，成为跨微服务传递身份信息的标准方式。

对于多人游戏而言，身份认证直接影响反作弊、防小号、付费体系安全和玩家数据隔离。一旦认证被绕过，攻击者可以冒充其他玩家、刷取排名或非法访问他人账号资产，因此它是网关服务器之后第一道逻辑防线。

## 核心原理

### JWT令牌机制

JWT（JSON Web Token）由三段Base64Url编码组成，格式为 `Header.Payload.Signature`。

- **Header**：声明算法类型，游戏后端常用 `{"alg":"HS256","typ":"JWT"}` 或更安全的 `RS256`
- **Payload**：携带玩家身份声明（Claims），如 `player_id`、`platform`、`session_exp`（过期时间戳）
- **Signature**：对前两段用密钥签名，服务器验证签名即可确认令牌未被篡改，无需查询数据库

验证公式：`HMACSHA256(base64url(header) + "." + base64url(payload), secret)`

游戏服务器收到JWT后，只需本地验证签名和 `exp` 字段，延迟通常低于1毫秒，特别适合需要高并发的游戏场景。JWT的无状态特性使其可以被游戏的多个微服务（匹配服务、房间服务、道具服务）直接验证，而不需要集中式Session存储。

### OAuth 2.0在游戏平台中的应用

OAuth 2.0是游戏接入第三方平台账号（微信、Google Play、Apple Game Center）时的标准授权框架。游戏客户端不直接持有平台账号密码，而是通过以下流程获取访问令牌：

1. 客户端跳转到平台授权页，玩家同意授权
2. 平台返回授权码（Authorization Code），有效期通常仅600秒
3. 游戏服务端用授权码换取 `access_token` 和 `refresh_token`
4. 游戏服务端用 `access_token` 调用平台API获取玩家唯一标识（如Steam的 `steamid64`）
5. 服务端将平台标识与游戏内账号绑定，签发游戏自己的JWT

这种方式的关键优势是游戏服务器永远不接触玩家的平台账号密码。

### 平台SDK认证

Steam、Epic Games、Xbox Live等平台提供专用SDK，通过"会话票据"（Session Ticket）机制完成认证。以Steam为例，客户端调用 `ISteamUser::GetAuthTicketForWebApi()` 生成一段加密票据，发送给游戏服务器后，服务器调用Steam Web API的 `AuthenticateUserTicket` 接口验证其有效性和玩家SteamID。票据默认有效期为24小时，且一张票据只能验证一次（防重放攻击）。PlayStation Network的PSN Ticket机制与此类似，但使用NPTICKET格式，需要专用库解析。

### 令牌刷新与会话管理

游戏中玩家可能在线数小时，JWT的 `exp` 通常设置为15至60分钟，到期后客户端需使用 `refresh_token` 静默续期。游戏服务端需维护一张Refresh Token黑名单表（通常存于Redis），当玩家主动退出或被封号时，将其 `refresh_token` 的 `jti`（JWT ID）加入黑名单，实现强制下线。

## 实际应用

**多平台账号融合**：一款同时上线Steam和iOS的游戏，玩家在两个平台的账号需要绑定到同一游戏账号。服务端在首次OAuth验证后，将 `steam_id` 和 `apple_sub`（Apple的用户唯一标识）都写入玩家数据库的同一条记录，后续任意平台登录都能识别为同一玩家。

**游戏内服务间认证**：匹配服务创建房间后，需通知战斗服务器"此玩家已认证"。战斗服务器不直接联系认证服务，而是直接验证玩家客户端携带的JWT签名，只要签名私钥在内网安全分发，整个流程不增加网络往返。

**防小号场景**：大逃杀类游戏常见刷分小号问题。通过要求Steam账号必须拥有游戏且游戏时长超过2小时（Steam Web API可查询）才能进入排位模式，在认证层过滤大量临时账号，成本极低。

## 常见误区

**误区一：将认证（Authentication）和授权（Authorization）混为一谈**
认证只回答"你是谁"，确认玩家身份后签发JWT；授权回答"你能做什么"，例如是否拥有某个DLC或是否有GM权限。游戏服务端许多Bug来源于在认证通过后未做权限校验，导致普通玩家能调用管理员接口。JWT的Payload中可携带角色字段（如 `"role":"admin"`），但这属于授权范畴，需要单独校验。

**误区二：JWT Payload中的数据是加密的**
JWT默认只做签名（Sign），不做加密（Encrypt）。Base64Url是可逆编码，任何人都能解码Payload读取其中内容。因此不应在JWT Payload中存放敏感信息，如银行账号、明文密码、未公开的游戏内容。若需加密，应使用JWE（JSON Web Encryption）规范。

**误区三：平台SDK验证可以在客户端完成**
Steam Ticket的验证必须在服务端调用Steam Web API完成，客户端自行校验没有任何安全意义，因为客户端代码可以被逆向和篡改。任何仅在客户端执行的安全检查都应被视为无效的安全措施。

## 知识关联

**前置概念——网关服务器**：网关服务器负责TLS终结和基础流量过滤，身份认证逻辑运行在网关之后的认证服务中。网关可以做粗粒度过滤（如IP黑名单），但JWT签名验证和平台SDK调用由专门的认证服务处理。网关与认证服务之间通常通过gRPC或内网HTTP通信。

**后续概念——速率限制**：认证成功后，服务端知道了请求来自哪个具体玩家（携带 `player_id`），速率限制才能以玩家维度而非IP维度执行限流，避免NAT后多个玩家共享IP时误伤正常用户。

**后续概念——玩家数据模型**：认证服务验证身份后返回的 `player_id` 是玩家数据模型的主键，后续角色数据、背包数据、好友关系全部以此为根节点组织。多平台登录中的账号绑定逻辑，也要求玩家数据模型支持一个账号关联多个平台标识的结构。
