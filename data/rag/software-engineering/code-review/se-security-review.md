---
id: "se-security-review"
concept: "安全审查"
domain: "software-engineering"
subdomain: "code-review"
subdomain_name: "代码审查"
difficulty: 3
is_milestone: false
tags: ["安全"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 安全审查

## 概述

安全审查（Security Review）是代码审查流程中专门针对安全漏洞的结构化检查过程，目标是在代码合并或部署之前发现并修复注入攻击、跨站脚本（XSS）、跨站请求伪造（CSRF）等典型漏洞。与普通功能性代码审查不同，安全审查需要审查者具备攻击者视角（Attacker Mindset），主动寻找代码中可被恶意利用的输入路径、权限边界和数据流。

安全审查的系统化方法论主要来源于 OWASP（Open Web Application Security Project）组织。OWASP 自 2001 年成立以来，持续发布 OWASP Top 10 列表，将最常见的 Web 应用安全风险按严重程度排序，为安全审查提供了标准化的检查框架。最新版 OWASP Top 10（2021年版）将"注入"类漏洞归入 A03 类别，将"失效的访问控制"列为第一位风险，这一排序变化直接影响了安全审查中优先检查项目的顺序。

安全审查的重要性体现在漏洞修复成本的指数级增长规律：IBM 研究数据表明，在设计阶段发现的安全漏洞修复成本约为1倍基准，而在生产环境中修复同一漏洞的成本高达基准的30倍。因此，将安全审查嵌入代码审查环节，是降低整体安全风险最具性价比的工程实践。

## 核心原理

### 注入漏洞检查（Injection）

注入漏洞是指攻击者将恶意代码或命令嵌入应用程序的输入数据中，由后端解释器（SQL 引擎、OS Shell、LDAP 服务器等）直接执行。安全审查时，审查者需要识别所有"数据与命令未分离"的代码模式。

典型的 SQL 注入风险代码如下：

```python
query = "SELECT * FROM users WHERE name = '" + user_input + "'"
```

安全审查必须要求将其替换为参数化查询（Parameterized Query）：

```python
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```

审查清单中对注入的检查项应覆盖：SQL 注入、命令注入（`os.system(user_input)`）、LDAP 注入以及 XML/XPath 注入。判断标准统一为：**用户可控数据是否直接拼接进可执行字符串**。

### XSS 跨站脚本检查

XSS（Cross-Site Scripting）漏洞分为三类：反射型（Reflected）、存储型（Stored）和基于 DOM 的 DOM-Based XSS。安全审查针对三类 XSS 的检查方向不同：反射型需检查服务器端响应是否对 URL 参数进行 HTML 实体编码；存储型需追踪用户提交的内容从数据库读取到页面渲染的完整数据流；DOM-Based XSS 需检查前端 JavaScript 中 `innerHTML`、`document.write()`、`eval()` 等危险 API 是否使用了未经过滤的数据。

OWASP 推荐的 XSS 防御规则 #1 明确规定：将不可信数据插入 HTML 元素内容之前，必须对 `&`、`<`、`>`、`"`、`'`、`/` 这6个字符进行 HTML 实体转义。安全审查中若发现模板引擎的自动转义被手动关闭（如 Jinja2 的 `| safe` 过滤器、Django 的 `mark_safe()`），须视为高危项进行标记并要求明确书面说明必要性。

### CSRF 跨站请求伪造检查

CSRF（Cross-Site Request Forgery）攻击利用已登录用户的身份凭证，诱使其浏览器发送伪造请求。安全审查的检查重点是：所有改变服务器状态的 HTTP 请求（POST、PUT、DELETE、PATCH）是否携带并验证 CSRF Token。CSRF Token 必须满足三个条件：与用户 Session 绑定、每次请求随机生成、服务端进行双向校验。

审查时还需检查 `SameSite` Cookie 属性设置。`SameSite=Strict` 完全阻止跨站携带 Cookie；`SameSite=Lax` 允许顶级导航携带 Cookie。若代码中 Cookie 设置缺少 `SameSite` 属性或设置为 `SameSite=None` 却未配套 `Secure` 标志，需列为中危问题。

### 访问控制与敏感数据暴露检查

安全审查还需检查垂直越权（普通用户访问管理员功能）和水平越权（用户访问他人数据）问题。典型风险模式是直接对象引用（IDOR）：`/api/orders/1234` 接口仅通过 URL 中的数字 ID 访问资源，而未校验请求者是否拥有该订单的所有权。审查时需确认每个资源访问点均存在 `current_user.id == resource.owner_id` 类型的所有权校验逻辑。

## 实际应用

在 GitHub Pull Request 的安全审查实践中，审查者通常使用基于 OWASP Testing Guide 定制的安全审查清单，对每个 PR 中涉及用户输入处理、认证授权、文件上传、第三方依赖的变更代码逐项评分。例如，某金融系统在审查一个新增转账接口时，审查者发现该接口使用 GET 请求处理转账操作（违反状态变更应使用 POST 的原则），且未验证 CSRF Token，该问题被评为 P1（严重）并阻止合并，避免了攻击者通过构造恶意链接诱导用户点击即可转账的漏洞。

自动化安全扫描工具（如 Semgrep、Bandit、SonarQube）可以辅助安全审查，但覆盖率有限——Bandit 对 Python 代码的 SQL 注入检测依赖字符串拼接模式匹配，无法识别 ORM 框架层面的间接注入。因此，工具扫描结果应作为安全审查清单的补充输入，而非替代人工安全审查。

## 常见误区

**误区一：HTTPS 等同于安全，无需检查 XSS 和 CSRF**。HTTPS 只加密传输层数据，防止中间人窃听，但不能阻止 XSS 攻击——因为 XSS 脚本在用户浏览器内执行，属于客户端攻击，与传输加密无关。同理，HTTPS 也无法阻止 CSRF，因为 CSRF 利用的是浏览器自动携带合法 Cookie 的行为，而非截获传输数据。

**误区二：参数化查询解决了所有注入问题**。参数化查询有效防御 SQL 注入，但对命令注入（`subprocess.call(user_input, shell=True)`）、模板注入（Server-Side Template Injection，SSTI）、XML 外部实体注入（XXE）等其他注入类型无效。安全审查需针对每类注入的具体攻击向量分别检查，不能以"已使用参数化查询"代替完整的注入检查。

**误区三：前端做了输入验证就足够**。前端 JavaScript 验证可被攻击者使用 Burp Suite 等工具绕过，直接向后端接口发送恶意数据。安全审查必须确认服务端存在独立的输入验证和输出编码逻辑，前端验证仅作为用户体验优化措施，不计入安全控制层。

## 知识关联

安全审查在代码审查流程中依赖**审查清单**（Review Checklist）作为前置基础——通用审查清单提供了结构化的检查项管理机制，安全审查将其专门化为 OWASP Top 10 对齐的安全检查项清单，使每个注入、XSS、CSRF 的检查点都有对应的通过/失败判断标准，而非依赖审查者个人经验进行主观判断。

安全审查与威胁建模（Threat Modeling）形成互补关系：威胁建模在架构设计阶段识别系统级攻击面（如 STRIDE 模型中的仿冒、篡改、抵赖、信息泄露、拒绝服务、特权提升），而安全审查在代码实现阶段验证具体代码是否正确实现了威胁建模中确定的安全控制措施。两者协同覆盖了从设计到实现的完整安全验证链条。