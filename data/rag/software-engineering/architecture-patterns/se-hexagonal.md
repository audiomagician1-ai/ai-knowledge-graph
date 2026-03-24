---
id: "se-hexagonal"
concept: "六边形架构"
domain: "software-engineering"
subdomain: "architecture-patterns"
subdomain_name: "架构模式"
difficulty: 3
is_milestone: false
tags: ["DDD"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 六边形架构

## 概述

六边形架构（Hexagonal Architecture）由 Alistair Cockburn 于 2005 年正式提出，也称为"端口与适配器模式"（Ports and Adapters Pattern）。其核心思想是将应用程序的业务逻辑与外部系统（数据库、UI、消息队列、第三方服务等）彻底隔离，业务逻辑居于六边形中心，所有外部通信均通过"端口"（抽象接口）和"适配器"（具体实现）进行。名称中的"六边形"并非指六条边有特殊意义，而是为了在架构图中直观地展示多个输入/输出方向的对称性。

与传统分层架构不同，六边形架构打破了"从上到下"的单向依赖链。分层架构中，业务层往往直接依赖数据访问层的具体实现，导致业务逻辑与持久化技术深度耦合。六边形架构通过 SOLID 中的依赖倒置原则（DIP）解决这一问题：业务层定义端口（接口），适配器层实现这些接口，依赖方向从"业务依赖基础设施"翻转为"基础设施依赖业务"。

六边形架构的重要意义在于**可测试性的本质提升**。因为业务逻辑只依赖抽象端口，测试时可以用内存伪实现（In-Memory Adapter）替换真实数据库，无需启动任何外部服务即可对完整业务逻辑进行单元测试。这正是现代微服务和 TDD 实践中广泛采纳该架构的直接原因。

---

## 核心原理

### 端口（Port）：业务定义的抽象边界

端口是由**应用程序内部**定义的接口，代表业务逻辑对外界的期望行为。端口分为两类：

- **驱动端口（Driving Port / Primary Port）**：外部调用业务逻辑的入口，例如 `OrderService` 接口，由 REST 控制器或 CLI 命令调用。
- **被驱动端口（Driven Port / Secondary Port）**：业务逻辑调用外部资源的出口，例如 `OrderRepository` 接口，由具体的 MySQL 适配器实现。

关键约束：端口的接口定义**必须用业务语言**描述，不得出现任何基础设施细节。例如，`OrderRepository.findById(OrderId id)` 是合法端口方法，而 `OrderRepository.executeSQL(String sql)` 则违反该原则。

### 适配器（Adapter）：连接外部世界的翻译层

适配器位于六边形外部，负责将外部技术协议转换为端口所定义的业务语言。同一个端口可对应多个适配器：

| 端口 | 适配器示例 |
|------|-----------|
| `UserRepository` | `JpaUserAdapter`（生产）、`InMemoryUserAdapter`（测试） |
| `NotificationPort` | `EmailAdapter`、`SmsAdapter`、`SlackAdapter` |
| `OrderInputPort` | `RestOrderController`、`GraphQLOrderResolver` |

适配器持有对端口接口的引用，**不允许**直接引用其他适配器，更不允许适配器之间形成调用链。

### 依赖方向规则

六边形架构的依赖规则可以用一个公式化表述来描述：

> **所有依赖箭头必须指向六边形内部（指向业务核心）。**

具体说，若适配器 A 实现了端口 P，则代码层面是 `class JpaUserAdapter implements UserRepository`，依赖方向是 `JpaUserAdapter → UserRepository（端口）→ 业务核心`。业务核心代码中绝对不出现 `import javax.persistence.*` 或 `import org.springframework.data.*` 这类基础设施包名。

Cockburn 原文中提到一条可操作验证标准：**如果你能在不修改任何业务逻辑代码的情况下，把 MySQL 换成 MongoDB，说明六边形架构实施正确。**

---

## 实际应用

### 电商订单系统示例

假设一个订单服务需要支持 REST API 和消息队列两种触发方式，并且存储层可能从 PostgreSQL 迁移到 DynamoDB。

```
【驱动侧适配器】
  RestOrderController   ──→  PlaceOrderUseCase（驱动端口）
  SqsOrderConsumer      ──→  PlaceOrderUseCase（驱动端口）

【业务核心】
  OrderApplicationService（实现 PlaceOrderUseCase）
  调用 →  OrderRepository（被驱动端口）
  调用 →  PaymentGateway（被驱动端口）

【被驱动侧适配器】
  PostgresOrderRepository  实现 OrderRepository
  StripePaymentAdapter     实现 PaymentGateway
```

当需要切换到 DynamoDB 时，只需新增 `DynamoOrderRepository implements OrderRepository`，业务核心代码零修改。

### 测试策略中的应用

六边形架构天然支持"测试金字塔"策略：使用 `InMemoryOrderRepository`（纯 Java HashMap 实现）可以将业务逻辑的单元测试执行时间从依赖真实数据库的 5-10 秒压缩到毫秒级。集成测试阶段再引入真实适配器进行验证。

---

## 常见误区

### 误区一：将适配器逻辑写入业务核心

常见错误是在 `OrderApplicationService` 中直接调用 Spring 的 `JpaRepository` 方法，或在业务类上加 `@Transactional`（属于 Spring 基础设施注解）。正确做法是事务管理由适配器层负责，业务核心只调用端口接口。一旦业务类中出现框架注解，六边形的隔离性即被破坏。

### 误区二：端口粒度过细等同于 CRUD 接口

有些开发者将端口设计成通用的 `save()`、`findAll()`、`delete()` 集合，本质上是把数据库表的 CRUD 操作暴露为端口，这与分层架构的 DAO 模式无本质区别。端口应以**业务用例为粒度**定义，例如 `findOverdueOrders(LocalDate cutoffDate)` 而非泛化的 `findAll(Specification spec)`。

### 误区三：六边形架构等于微服务架构

六边形架构是**应用内部的结构组织方式**，与服务部署粒度无关。一个单体应用完全可以采用六边形架构，一个微服务也可以内部实现为传统分层结构。两者解决的问题层面不同，不可混淆。

---

## 知识关联

**与分层架构的关系**：分层架构（表现层→业务层→数据层）是六边形架构的常见对比对象。分层架构中业务层对数据层存在直接依赖，六边形架构通过端口接口将这一依赖反转，是对分层架构在依赖方向上的根本性改进。

**与 SOLID 原则的关系**：六边形架构是依赖倒置原则（D原则）和接口隔离原则（I原则）在架构层面的集中体现。依赖倒置原则提供了理论依据，端口与适配器模式提供了落地的结构形式。

**通向领域驱动设计（DDD）**：DDD 中的"领域层"与"基础设施层"边界划分，与六边形架构的业务核心与适配器层高度对应。DDD 的聚合根、领域服务等概念自然地填充在六边形内部，而 DDD 的仓储模式（Repository Pattern）正是六边形被驱动端口的典型实现方式。学习 DDD 之前掌握六边形架构，能帮助理解为什么领域模型必须对持久化技术保持无感知。
