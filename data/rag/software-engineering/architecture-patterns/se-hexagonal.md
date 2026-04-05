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

# 六边形架构

## 概述

六边形架构（Hexagonal Architecture）由 Alistair Cockburn 于 2005 年正式提出，其核心思想是将应用程序的业务逻辑与外部系统（数据库、UI、消息队列等）完全隔离。Cockburn 选择"六边形"这一形状并非因为边数有特殊含义，而是为了在图示中留出足够空间绘制多个端口与适配器，打破传统分层架构"上下关系"的思维定式。该架构也被称为"端口与适配器模式"（Ports and Adapters Pattern），这一别名更直接揭示了它的结构本质。

六边形架构解决了传统三层架构中业务逻辑被迫依赖基础设施的问题。在经典分层架构里，领域层往往需要直接引用数据库访问类，导致单元测试时必须启动数据库连接。六边形架构通过依赖反转原则（DIP，SOLID 中的 D），使业务核心只依赖抽象接口（端口），而数据库驱动、HTTP 客户端等具体实现（适配器）则依赖业务核心，彻底翻转了这一依赖方向。

## 核心原理

### 端口（Port）的定义与分类

端口是业务核心对外暴露或对外声明需求的抽象接口，分为两类：**驱动端口（Driving Port）**和**被驱动端口（Driven Port）**。驱动端口（也称主端口）是外部调用者进入应用的入口，例如 `OrderService` 接口中定义的 `placeOrder(command: PlaceOrderCommand): OrderId` 方法；被驱动端口（也称次端口）是业务核心声明自己所需的外部能力，例如 `OrderRepository` 接口中的 `save(order: Order): void`。端口始终以业务语言命名，不出现任何技术术语（如 `JdbcOrderRepository` 不是端口，而是适配器）。

### 适配器（Adapter）的职责

适配器实现端口接口，负责完成技术细节与业务模型之间的转换。以被驱动侧为例，`PostgresOrderRepository` 实现 `OrderRepository` 接口，内部将领域对象 `Order` 映射为 SQL 语句；`InMemoryOrderRepository` 同样实现该接口，仅用于测试环境。适配器的数量理论上不受限制，同一个端口可以有 MySQL 适配器、MongoDB 适配器和内存适配器三个并存实现，业务核心代码无需任何修改即可切换。驱动侧适配器的典型例子是 REST 控制器——它将 HTTP 请求反序列化后转换为命令对象，再调用驱动端口。

### 依赖方向规则

六边形架构严格规定：**所有依赖箭头必须指向六边形内部（业务核心）**。用代码表达即：业务核心包（`domain`、`application`）的 `import` 语句中，绝不允许出现基础设施包（`infrastructure`、`adapter`）的类名。这一规则可通过 ArchUnit（Java 生态）或 Dependency Cruiser（Node.js 生态）等工具在 CI 流水线中自动检测。违反此规则的典型症状是：领域实体中出现 `@Column`、`@Entity` 等 JPA 注解，这意味着领域层已被持久化框架污染。

### 应用层与领域层的内部结构

六边形内部通常进一步划分为应用层（Application Layer）和领域层（Domain Layer）。应用层包含用例类（Use Case），每个用例类实现一个驱动端口并调用若干被驱动端口，例如 `PlaceOrderUseCase` 类调用 `InventoryPort.reserve()` 和 `OrderRepository.save()`。领域层包含纯粹的业务规则，不依赖任何接口或外部声明。这种内部分层使六边形架构的可测试性达到最高——用例层的单元测试只需注入被驱动端口的 Mock 实现，完全无需 Spring 容器或数据库。

## 实际应用

**电商订单系统**是六边形架构的典型落地场景。驱动端口包括 `PlaceOrderUseCase`（供 REST 适配器调用）和 `ProcessPaymentCallbackUseCase`（供消息队列适配器调用）；被驱动端口包括 `OrderRepository`、`PaymentGateway`、`EmailNotificationPort`。当业务决定将支付网关从支付宝切换到微信支付时，只需新增一个 `WechatPayAdapter` 实现 `PaymentGateway` 接口，修改依赖注入配置，业务核心代码零改动。

**测试策略**上，六边形架构支持"测试金字塔"的完整实践：使用 `InMemoryOrderRepository` 进行用例层单元测试（执行速度在毫秒级），使用真实数据库连接进行适配器层集成测试（仅测试 SQL 映射逻辑），而无需为每个业务场景启动完整 Spring 上下文。实践数据显示，采用六边形架构的项目，其单元测试覆盖率通常可达 80% 以上且执行时间保持在 30 秒以内。

## 常见误区

**误区一：把六边形架构理解为"六层架构"**。六边形的边数与架构层数无关。"六边形"只是示意图的几何形状，实际项目中一个六边形可能拥有 3 个驱动适配器（REST、gRPC、CLI）和 5 个被驱动适配器（PostgreSQL、Redis、S3、Kafka、SMTP），总计 8 个适配器。将其误解为固定层数会导致开发者强行凑够六个模块。

**误区二：将数据库实体类（JPA Entity）直接当作领域对象使用**。这是六边形架构实施中最高频的错误。`@Entity` 注解的类与 ORM 框架耦合，将其暴露给领域层等同于让领域层隐式依赖 Hibernate。正确做法是在 `PostgresOrderRepository` 适配器内部维护一个独立的 `OrderJpaEntity` 数据类，并实现领域对象 `Order` 与 `OrderJpaEntity` 之间的双向映射方法。

**误区三：认为六边形架构必须配合微服务使用**。六边形架构是一种单体应用内部的代码组织方式，与部署架构无关。一个运行在单一 JVM 进程中的 Spring Boot 应用完全可以采用六边形架构，且能获得充分的好处：可测试性提升、依赖方向清晰、技术替换成本降低。

## 知识关联

六边形架构以**SOLID 原则**中的依赖倒置原则（DIP）为直接理论支撑——端口即高层抽象，适配器即低层实现，两者均依赖接口而非具体类。与**分层架构**相比，六边形架构的本质进化在于打破了"基础设施层必须位于底部"的单向约定，允许多个外部系统从任意方向连接到业务核心，而分层架构只能处理单一的调用方向（UI → 业务 → 数据）。

在后续概念中，**领域驱动设计（DDD）**与六边形架构高度契合：DDD 中的聚合根、值对象、领域事件自然居于六边形内部，限界上下文的边界与六边形边界吻合。**Clean Architecture**（Robert Martin，2017 年）是六边形架构的衍生与扩展，将六边形内部进一步细化为实体层、用例层、接口适配层三个同心圆，并为每一层定义了更严格的依赖规则，但其端口与适配器的核心思想直接继承自六边形架构。