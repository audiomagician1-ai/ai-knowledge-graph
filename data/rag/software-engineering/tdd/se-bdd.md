---
id: "se-bdd"
concept: "行为驱动开发"
domain: "software-engineering"
subdomain: "tdd"
subdomain_name: "测试驱动开发"
difficulty: 2
is_milestone: false
tags: ["BDD"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 行为驱动开发

## 概述

行为驱动开发（Behavior-Driven Development，BDD）是由 Dan North 于 2003 年在研究 TDD 实践时提出的方法论，最早发表于其 2006 年的文章《Introducing BDD》。BDD 的诞生源于 North 观察到开发团队在使用 TDD 时普遍困惑"测试应该从哪里开始写"以及"如何命名测试"，他将解决方案定向为：用描述系统**行为**的自然语言句子替代技术性的测试命名。

BDD 的核心思想是将软件需求转化为可执行的规范文档，让业务人员、测试人员和开发人员用同一种语言沟通。它引入了一套称为 **Gherkin** 的领域专用语言（DSL），Gherkin 文件以 `.feature` 为扩展名，使用英语（或其他自然语言）描述功能场景。Gherkin 语法由 Aslak Hellesøy 开发，作为 Cucumber 框架的一部分于 2008 年正式发布。

BDD 在现代软件开发中的价值在于消除"需求理解偏差"——据统计，软件项目中约 40–60% 的缺陷源于需求误解。通过把验收标准直接写成可运行的测试场景，团队在编写第一行实现代码之前就能确认所有人对功能的理解一致。

## 核心原理

### Given-When-Then 结构

BDD 规范的基本单位是**场景（Scenario）**，每个场景由三个固定关键词组织：

- **Given**（前置条件）：描述系统在动作执行之前所处的状态
- **When**（触发事件）：描述用户或系统执行的具体动作
- **Then**（预期结果）：描述动作发生后系统应呈现的可观测结果

一个典型的登录功能场景示例：

```gherkin
Feature: 用户登录
  Scenario: 使用正确凭据登录成功
    Given 用户已注册账号 "alice@example.com"，密码为 "Secret123"
    When 用户输入邮箱 "alice@example.com" 和密码 "Secret123" 并点击登录
    Then 页面跳转至用户主页
    And 页面顶部显示 "欢迎回来，alice"
```

`And` 和 `But` 是辅助关键词，用于在同一步骤类型下添加多个条件，避免重复书写 Given/When/Then。

### Gherkin 语言的关键组成

Gherkin 文件由以下层级构成：**Feature（功能）→ Scenario 或 Scenario Outline（场景/场景大纲）→ Steps（步骤）**。`Scenario Outline` 配合 `Examples` 表格可以用数据驱动方式运行同一场景的多组输入，例如：

```gherkin
Scenario Outline: 不同数量商品的总价计算
  Given 商品单价为 <price> 元
  When 用户购买 <quantity> 件
  Then 购物车总价显示为 <total> 元

  Examples:
    | price | quantity | total |
    | 10    | 3        | 30    |
    | 25    | 2        | 50    |
```

这种参数化写法避免了为每组测试数据单独编写重复场景的问题。

### Step Definitions 与框架绑定

Gherkin 本身只是规范文档，需要通过**步骤定义（Step Definitions）**将自然语言步骤绑定到实际的自动化代码。以 Cucumber for Java 为例：

```java
@Given("用户已注册账号 {string}，密码为 {string}")
public void userIsRegistered(String email, String password) {
    userRepository.create(email, password);
}
```

正则表达式或 Cucumber 表达式负责从步骤文本中提取参数，传入测试方法。主流 BDD 框架包括：Cucumber（Java/Ruby/JavaScript）、Behave（Python）、SpecFlow（.NET）和 JBehave（Java，由 Dan North 本人创建）。

## 实际应用

**电商购物车功能验收测试**：团队产品经理用 Gherkin 写出"用户将缺货商品加入购物车时系统应显示库存不足提示"的场景，开发人员根据该场景实现功能，QA 工程师验证场景通过，三方无需额外的口头沟通确认。

**持续集成流水线中的活文档**：Cucumber 生成的 HTML 报告可以直接作为业务验收文档存档，Gherkin feature 文件随代码一起提交到 Git 仓库，形成"始终与代码同步的需求文档"，解决了传统 Word 需求文档滞后于实现的问题。

**微服务契约测试**：在前后端分离项目中，BDD 场景可以描述 API 的输入输出行为（如"When 发送 POST /orders 请求，Then 返回 HTTP 201 状态码和订单 ID"），用作服务间接口契约的自动化验证。

## 常见误区

**误区一：认为 BDD 只是"用自然语言写测试"**。BDD 的目的是促进三方协作（业务、开发、测试）提前对齐需求，而不仅仅是改变测试代码的书写格式。如果 Gherkin 场景完全由开发人员独自编写，没有产品经理或业务人员参与评审，就失去了 BDD 最核心的价值，沦为仅有形式没有实质的"测试脚本"。

**误区二：对每个技术细节都编写 Gherkin 场景**。BDD 场景应描述**业务行为**，而非实现细节。错误示例："Given 数据库连接池大小为 10，When 执行 SQL SELECT…"——这类场景应当由单元测试或集成测试覆盖，而不是 Gherkin。过度使用 BDD 会导致场景维护成本极高，Dan North 本人也多次在演讲中警告"不要用 Cucumber 测试一切"。

**误区三：混淆 BDD 与 TDD 的适用层次**。TDD 在单元级别驱动类和方法的设计，循环周期以分钟计；BDD 在功能级别驱动业务场景的实现，循环周期以小时或天计。二者不是替代关系，而是作用于软件测试金字塔的不同层级——BDD 对应顶部的验收测试层，TDD 对应底部的单元测试层。

## 知识关联

BDD 直接继承自 TDD 的"先写测试，再写实现"思想：TDD 要求开发者在实现代码之前先写失败的单元测试，BDD 将这一原则扩展到功能层面，要求在实现之前先写失败的场景规范。理解 TDD 的红-绿-重构循环有助于理解 BDD 的外循环（Outer Loop）：先让 Gherkin 场景失败，再通过 TDD 内循环编写单元测试和实现代码，最终让场景通过。

BDD 也与**验收测试驱动开发（ATDD）**高度重叠——ATDD 强调在迭代开始前由客户、测试和开发三方共同编写验收标准，BDD 则提供了 Gherkin 这一具体的语言工具来落实 ATDD 的协作实践。学习 BDD 之后，可以进一步研究 Specification by Example（实例化需求）方法，该方法由 Gojko Adzic 在 2011 年系统化，是 BDD 思想在需求管理全流程中的延伸应用。