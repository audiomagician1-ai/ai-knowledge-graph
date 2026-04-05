---
id: "session-cookie"
concept: "Session与Cookie"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 4
is_milestone: false
tags: ["状态"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Session与Cookie

## 概述

Cookie是HTTP协议在无状态基础上实现状态保持的机制，由Netscape公司工程师Lou Montulli于1994年发明，最初用于解决购物车数据的跨请求持久化问题。Cookie本质上是服务器通过`Set-Cookie`响应头写入客户端浏览器的键值对数据，浏览器在后续请求中自动通过`Cookie`请求头将其回传给服务器，整个过程无需应用代码干预。

Session（会话）是服务器端的状态存储机制，通过在服务器内存或数据库中保存用户会话数据，并仅向客户端下发一个不含敏感信息的会话标识符（Session ID）来实现状态管理。典型的Session ID形如`JSESSIONID=ABC123DEF456`，其本身不包含任何用户数据，只是一把访问服务器端数据的"钥匙"。

两者的核心区别在于数据存储位置：Cookie将数据存储在客户端（浏览器），Session将数据存储在服务器端。这一差异直接决定了两者在容量、安全性和扩展性上的不同取舍，是Web后端身份认证架构选型的基础。

## 核心原理

### Cookie的属性与生命周期

一个完整的`Set-Cookie`头包含多个属性，控制Cookie的行为：

```
Set-Cookie: sessionid=xyz123; Max-Age=3600; Path=/; Domain=example.com; Secure; HttpOnly; SameSite=Lax
```

- **Max-Age / Expires**：`Max-Age=3600`表示Cookie在3600秒（1小时）后过期。省略该属性则为会话Cookie（Session Cookie），浏览器关闭即删除。
- **HttpOnly**：设置此标志后，JavaScript无法通过`document.cookie`读取该Cookie，是防御XSS攻击窃取Cookie的关键措施。
- **Secure**：仅在HTTPS连接下传输Cookie，防止明文传输时被中间人截获。
- **SameSite**：取值`Strict`、`Lax`或`None`，控制跨站请求是否携带Cookie，是防御CSRF攻击的主要手段。Chrome 80版本（2020年2月）起将`SameSite`默认值从`None`改为`Lax`，这一变更影响了大量依赖跨站Cookie的应用。

单个Cookie的大小限制约为4KB，每个域名下浏览器通常允许存储20\~50个Cookie。

### Session的工作流程

Session的完整工作流程分为四步：

1. 用户首次请求时，服务器创建Session对象并生成唯一的Session ID（通常是128位随机字符串）。
2. 服务器通过`Set-Cookie: SESSIONID=<随机值>; HttpOnly`将Session ID写入客户端Cookie。
3. 客户端后续请求自动携带该Cookie，服务器从Cookie中提取Session ID。
4. 服务器用Session ID查找存储在内存、Redis或数据库中的Session数据，恢复用户状态。

Session数据存储在服务器端带来**水平扩展问题**：若Session存于单台服务器内存，用户请求被负载均衡器转发到另一台服务器时将找不到Session，导致认证失效。解决方案包括：粘性会话（Sticky Session，同一用户始终路由到同一服务器）、集中式Session存储（如Redis集群）或改用无状态的JWT令牌。

### Cookie与Session的对比关系

| 维度 | Cookie | Session |
|------|--------|---------|
| 存储位置 | 客户端浏览器 | 服务器端 |
| 存储容量 | ≤4KB | 理论无限（受服务器资源限制） |
| 安全性 | 数据可被客户端读取/篡改 | 数据不暴露给客户端 |
| 服务器负担 | 无状态，轻量 | 需维护Session存储 |
| 典型有效期 | 可持久化（设置Expires） | 通常30分钟（服务器设定） |

## 实际应用

**用户登录认证**：用户提交用户名和密码后，服务器验证成功则创建Session，存储`user_id`、`role`等信息，并将Session ID通过Cookie下发。后续请求中服务器通过Session ID反查用户身份，无需每次重新验证密码。Django框架默认使用数据库表`django_session`存储Session数据，Express.js搭配`express-session`中间件实现相同功能，默认将Session存储在内存中。

**购物车持久化**：电商网站常将未登录用户的购物车数据直接存储在Cookie中（数据较少时），登录后合并到服务端Session或数据库。这也是Cookie的原始发明场景。

**"记住我"功能**：勾选"记住我"时，服务器生成一个长效Token（有效期通常为30天）写入持久化Cookie（设置`Max-Age`或`Expires`），并在数据库记录Token与用户的映射。这与普通Session Cookie（浏览器关闭即失效）是两套不同的机制。

**A/B测试分组**：通过Cookie存储用户的实验分组标识（如`ab_group=variant_b`），保证同一用户在多次访问中始终看到相同的实验版本，无需服务器查询。

## 常见误区

**误区一：Session就是存储在Cookie里的数据**。Session是服务器端的数据结构，Cookie只是传输Session ID的载体之一。Session ID也可以通过URL参数（如`?JSESSIONID=xxx`）或请求头传递，但URL方式会将Session ID暴露在浏览器历史记录和服务器日志中，安全性更差，现代应用已基本弃用。

**误区二：设置了HttpOnly的Cookie就绝对安全**。HttpOnly阻止JavaScript读取Cookie，但无法防止CSRF攻击——攻击者诱导用户浏览器自动携带Cookie发送跨站请求，无需读取Cookie值本身。防御CSRF需要结合`SameSite`属性或CSRF Token机制，而非仅依赖HttpOnly。

**误区三：Cookie删除等于Session销毁**。清除浏览器中的Session ID Cookie只会让客户端"遗忘"会话凭证，但服务器端的Session数据依然存在，直至超时被垃圾回收。正确的退出登录实现必须同时调用服务器端的Session销毁接口（如`request.session.invalidate()`），否则旧Session ID若被他人获取仍可复用，构成安全漏洞。

## 知识关联

**前置知识**：HTTP协议的无状态特性（每个请求相互独立）是Cookie和Session存在的根本原因。理解HTTP请求/响应头的结构，特别是`Set-Cookie`和`Cookie`头的格式，是掌握Cookie机制的前提。

**浏览器存储机制**：Cookie是浏览器存储的最早形式，其4KB容量限制催生了`localStorage`（5\~10MB，持久化）和`sessionStorage`（5\~10MB，标签页级别生命周期）的出现。三者在容量、生命周期、自动随请求发送等维度各有权衡。

**Web安全基础**：Cookie的`HttpOnly`、`Secure`、`SameSite`属性直接对应XSS、中间人攻击、CSRF三类攻击的防御策略，Session固定攻击（Session Fixation）要求服务器在认证成功后必须重新生成Session ID。

**OAuth与OIDC**：传统Session-Cookie方案在微服务和跨域场景下扩展性差，JWT（JSON Web Token）作为无状态的替代方案将用户状态编码在令牌本身中，OAuth 2.0和OIDC协议在此基础上构建了标准化的第三方授权和身份联合体系。