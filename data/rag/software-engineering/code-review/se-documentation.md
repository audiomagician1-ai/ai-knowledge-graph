---
id: "se-documentation"
concept: "文档实践"
domain: "software-engineering"
subdomain: "code-review"
subdomain_name: "代码审查"
difficulty: 2
is_milestone: false
tags: ["文档"]

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
updated_at: 2026-03-27
---


# 文档实践

## 概述

文档实践（Documentation Practice）是代码审查流程中对文档质量进行审核的专项活动，涵盖三类核心文档形式：API文档、README文件和架构决策记录（Architecture Decision Record，简称ADR）。代码审查不仅检查逻辑正确性，还必须确认代码改动是否同步更新了对应文档，因为代码与文档脱节是软件项目中最常见的技术债务来源之一。

文档实践的概念随着开源软件运动的兴起而系统化。1997年，Eric Raymond在《大教堂与市集》中强调文档对项目可维护性的决定性作用。2004年，Michael Nygard正式提出ADR概念，将架构决策的上下文、选项和结论以结构化文档固定下来，解决了"三个月后没人记得当初为什么这样设计"的典型困境。

在代码审查中强调文档实践，直接减少了新成员的上手时间（据统计，完善的文档可将入职时间缩短40%以上），并使API的错误使用率显著下降。审查者若发现一个新增的公开方法没有配套文档，应当将其视为与语法错误同等重要的问题而拒绝合并。

## 核心原理

### API文档的审查要点

API文档必须紧随代码变更同步更新，不能在合并后"补写"。审查时需检查以下具体内容：每个公开方法必须有功能描述、参数类型与含义、返回值说明以及可能抛出的异常类型。以Python的docstring规范为例，Google风格要求明确写出`Args:`、`Returns:`和`Raises:`三个标准段落。审查者应验证文档中的参数名称与实际代码参数名称完全一致——这是最常见的文档腐化形式，即代码重构后参数名改了但文档未更新。

对REST API而言，OpenAPI（Swagger）规范要求每个端点记录HTTP方法、路径参数、请求体schema、响应码（至少覆盖200、400、401、404、500）及示例。代码审查中应检查新端点是否已在`.yaml`或`.json`规范文件中注册，且示例请求/响应与实际实现的数据结构吻合。

### README文件的结构标准

README是项目的入口文档，代码审查中应按以下顺序检查其完整性：项目简介（一句话说明用途）、安装步骤（含具体命令，如`npm install`或`pip install -r requirements.txt`）、快速开始示例、配置说明、贡献指南链接。若某次PR新增了一个环境变量（如`DATABASE_URL`），审查者必须确认README中的配置表格或`.env.example`文件已同步添加该变量，否则新部署者将无法运行项目。

README的目标读者分层原则同样需要审查：面向使用者的README侧重安装和使用，面向贡献者的则需包含本地开发环境搭建步骤、测试运行命令（如`pytest tests/ -v`）和代码风格约定。两者混写是常见问题，审查时可建议拆分为`README.md`和`CONTRIBUTING.md`。

### 架构决策记录（ADR）

ADR的标准模板由Michael Nygard定义，包含五个固定字段：**标题**（编号+短标题，如"ADR-0012: 采用PostgreSQL替代MongoDB"）、**状态**（Proposed/Accepted/Deprecated/Superseded）、**背景**（驱动此决策的技术或业务约束）、**决策**（具体选择了什么）、**后果**（正面和负面影响）。

在代码审查中，当一个PR引入了重大架构变更——例如引入新的第三方库、变更数据库、修改服务间通信协议——审查者应要求提交者同时提交一份ADR文件，通常存放在项目的`docs/adr/`目录下。ADR的核心价值在于记录"为什么不选择其他方案"，因此**背景**字段必须列出被否决的备选方案及其否决理由，这是审查时最容易被忽略的检查点。

## 实际应用

**场景一：新增支付接口的PR审查**  
某PR新增了一个`POST /payments/charge`接口，代码审查中需同时检查：① OpenAPI规范文件中是否新增了该端点定义，包含`idempotency-key`请求头的说明；② 如果这是项目首次引入支付功能，是否提交了ADR说明选择Stripe而非Braintree的原因；③ README的"功能列表"章节是否更新。若三者缺一，PR不应通过。

**场景二：函数重命名的文档更新**  
将`calculate_fee(amount)`重命名为`compute_transaction_fee(amount, currency)`后，审查者需逐一确认：函数docstring中的`Args:`已描述新增的`currency`参数（类型为ISO 4217货币代码字符串）；README中引用该函数的示例代码已同步更新；若项目有Sphinx或JSDoc生成的API文档站点，`make docs`命令的输出无警告。

## 常见误区

**误区一：认为代码自解释，API文档可省略**  
部分工程师认为"代码写得足够清晰就不需要文档"。但文档描述的是"意图"，代码描述的是"实现"——一个函数命名为`retry_with_backoff(n)`，代码能告诉读者n是重试次数，但无法说明"n超过5时的降级策略是业务规定还是技术限制"。这类决策上下文只能通过文档传递。

**误区二：ADR只在架构会议上写，不属于代码审查范畴**  
实际上，ADR应与触发该决策的代码变更在同一个PR中提交。将ADR与代码分离会导致ADR仓库和代码仓库的状态不一致，六个月后无法追溯某个依赖是在哪个版本引入的。代码审查规范应明确规定：凡引入新依赖、变更数据库schema或修改API版本号的PR，必须包含ADR文件。

**误区三：README一次写好后不需要随PR更新**  
README是活文档，每次环境变量、依赖版本或启动命令发生变化，对应的README章节必须同步修改。审查者可通过在PR模板中添加checklist项"[ ] README是否需要更新"来强制提醒提交者检查，这是将文档审查嵌入流程的最低成本方式。

## 知识关联

文档实践与代码审查中的**接口设计审查**紧密相关：一个设计不良的API往往难以被文档清晰描述，因此若审查者发现某方法的docstring写得极其复杂，这本身可能是API需要重构的信号。文档难以书写意味着设计本身存在问题，这是代码审查的经验性判断原则之一。

在工具链层面，文档实践依赖具体工具支撑：Python项目使用Sphinx从docstring自动生成HTML文档，Java项目使用Javadoc，JavaScript/TypeScript使用JSDoc，REST API使用Swagger UI渲染OpenAPI规范。了解这些工具的输出格式，有助于审查者判断文档是否符合可自动化检验的规范要求，而不仅仅依赖人工阅读。

ADR的编号管理（从`ADR-0001`顺序递增）与**变更日志（CHANGELOG）**维护形成互补：CHANGELOG记录每个版本对外暴露的变化（遵循Keep a Changelog规范，使用`Added/Changed/Deprecated/Removed/Fixed/Security`分类），ADR记录内部技术决策的推理过程，两者共同构成项目历史的完整叙述。