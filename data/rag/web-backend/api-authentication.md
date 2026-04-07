---
id: "api-authentication"
concept: "API认证(JWT/OAuth)"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 5
is_milestone: false
tags: ["安全"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# API认证（JWT/OAuth）

## 概述

API认证是Web后端保护资源访问的机制，JWT（JSON Web Token）和OAuth 2.0是当前最主流的两种方案。JWT是一种紧凑的、URL安全的令牌格式，由RFC 7519标准于2015年正式定义；OAuth 2.0则是一套授权框架，由RFC 6749于2012年发布，专门解决第三方应用在不暴露用户密码的前提下访问受保护资源的问题。

这两者解决的问题层次不同：JWT是**令牌格式**，描述如何编码和验证身份信息；OAuth 2.0是**授权流程**，描述各角色如何交互以颁发令牌。在AI工程的API服务中，模型推理接口、数据上传端点等都需要认证保护，因为未授权的调用不仅会导致资源滥用，还可能泄露训练数据或模型权重。

## 核心原理

### JWT的三段式结构

JWT由三个Base64URL编码的部分通过`.`连接组成：**Header.Payload.Signature**。

- **Header**：声明令牌类型和签名算法，例如 `{"alg": "HS256", "typ": "JWT"}`
- **Payload**：包含Claims（声明），分为注册声明（如`iss`发行者、`exp`过期时间、`sub`主题）、公共声明和私有声明
- **Signature**：使用Header指定的算法对前两部分计算签名

以HS256为例，签名公式为：

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

服务端收到JWT后，无需查询数据库，只需用相同密钥重新计算签名并比对，即可验证令牌合法性。这是JWT与Session Token的根本区别——JWT是**无状态**的，服务端不存储会话。

### OAuth 2.0的四种授权流程

OAuth 2.0定义了四种授权类型（Grant Types），针对不同场景：

1. **Authorization Code Flow（授权码流程）**：适用于有服务器端的Web应用，用户通过浏览器重定向获取授权码，再由后端用授权码换取Access Token。这是最安全的流程，授权码只能使用一次且有效期极短（通常10分钟）。

2. **Client Credentials Flow**：用于机器到机器（M2M）通信，例如AI调度服务调用推理API，直接用`client_id`和`client_secret`换取Token，不涉及用户。

3. **Implicit Flow**：已被OAuth 2.1草案废弃，因为Token直接暴露在URL Fragment中存在泄露风险。

4. **Device Authorization Flow**：适用于无浏览器设备（如GPU服务器），设备轮询授权服务器直到用户在其他设备完成授权。

OAuth 2.0框架中定义了四个核心角色：资源拥有者（用户）、客户端（第三方应用）、授权服务器（颁发Token）、资源服务器（保护API）。

### Access Token与Refresh Token的生命周期

Access Token有效期应设计得较短，推荐**15分钟至1小时**，以减少令牌泄露后的风险窗口。Refresh Token有效期较长（如30天），仅用于向授权服务器换取新的Access Token，且每次刷新后旧的Refresh Token应立即失效（Refresh Token Rotation机制）。

JWT作为Access Token时存在一个重要问题：由于其无状态特性，**无法主动撤销**已颁发的JWT。解决方案包括：维护一个令牌黑名单（引入Redis存储已撤销的`jti`声明值）、或将Access Token有效期缩短到5分钟以内。

## 实际应用

**AI推理API的认证设计**：假设部署了一个图像识别模型API，使用Client Credentials Flow为企业客户颁发Token。客户端携带`client_id`和`client_secret`向`/oauth/token`端点POST请求，授权服务器返回JWT格式的Access Token。客户端在后续请求中将Token放入HTTP请求头：`Authorization: Bearer eyJhbGci...`。推理服务通过验证JWT签名（使用授权服务器的公钥，RS256算法）来确认请求合法，无需每次请求都查询数据库。

**微服务内部认证**：在AI平台的多服务架构中，数据预处理服务、训练调度服务、模型服务三者之间的内部调用同样需要认证。常见做法是每个服务持有自己的`client_id`/`client_secret`，通过Client Credentials Flow获取短期Token（有效期通常设为5分钟），服务间调用时附带Token，网关或中间件统一验证。

**PKCE扩展**：若前端单页应用（SPA）直接调用AI API，由于无法安全存储`client_secret`，需在Authorization Code Flow中添加PKCE（Proof Key for Code Exchange，RFC 7636）。客户端生成随机字符串`code_verifier`，计算其SHA-256哈希作为`code_challenge`，防止授权码劫持攻击。

## 常见误区

**误区一：JWT越大越好，存放大量信息**
JWT的Payload是Base64URL编码而非加密，任何持有Token的人都可以解码读取其中内容（只是无法伪造签名）。因此，不应将用户密码、完整权限列表或敏感个人信息放入JWT Payload。标准做法是只存放用户ID（`sub`）和角色等最小必要信息，详细权限在服务端按需查询。

**误区二：OAuth 2.0负责认证（Authentication）**
OAuth 2.0本质上是**授权（Authorization）框架**，它回答"该应用能访问哪些资源"，而不是"这个用户是谁"。要在OAuth基础上实现认证，需要OpenID Connect（OIDC）协议——OIDC在OAuth 2.0之上增加了`id_token`（也是JWT格式）和`/userinfo`端点，才真正解决"用户身份"问题。将纯OAuth Token用于身份认证会导致安全漏洞。

**误区三：只要HTTPS就不需要关注Token存储位置**
在浏览器中，JWT存储位置决定了不同的攻击面：存入`localStorage`易受XSS攻击（JavaScript可直接读取）；存入`httpOnly` Cookie可防止XSS但引入CSRF风险（需配合`SameSite=Strict`或CSRF Token缓解）。HTTPS只保护传输层，无法防护已注入恶意脚本对本地存储的读取。

## 知识关联

学习JWT/OAuth之前需要掌握RESTful API设计，因为Bearer Token通过HTTP `Authorization`请求头传递，而API的资源路径设计直接影响OAuth中资源服务器的权限粒度划分（Scope设计）。

掌握JWT/OAuth后，自然延伸到**限流策略**：通常基于JWT中的`sub`（用户ID）或`client_id`进行per-client限流，令牌的身份信息是限流逻辑的输入依据。**Web安全基础**与本主题紧密相连，JWT签名算法的选择（对称HS256 vs 非对称RS256/ES256）、算法混淆攻击（将`alg`改为`none`的历史漏洞）都属于Web安全范畴。**OAuth与OIDC**是本概念的直接进阶——OIDC在OAuth 2.0框架上定义了标准化的用户认证协议，是构建统一登录（SSO）系统和AI平台多租户认证体系的基础。