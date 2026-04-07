---
id: "se-ddd"
concept: "领域驱动设计"
domain: "software-engineering"
subdomain: "architecture-patterns"
subdomain_name: "架构模式"
difficulty: 3
is_milestone: true
tags: ["DDD"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 领域驱动设计

## 概述

领域驱动设计（Domain-Driven Design，简称 DDD）是由 Eric Evans 在 2003 年出版的同名著作《Domain-Driven Design: Tackling Complexity in the Heart of Software》中系统阐述的软件建模方法论。其核心主张是：软件模型应该与业务领域的实际概念保持一致，而不是以数据库结构或 UI 层次驱动代码组织方式。

DDD 之所以区别于其他架构方法，在于它明确提出了"通用语言"（Ubiquitous Language）的概念——开发人员、产品经理和业务专家必须使用同一套术语描述同一件事。例如，在银行系统中，"账户冻结"不能在业务文档里叫 `freeze`、在数据库里叫 `status=2`、在代码里叫 `disabled`，三者必须统一为 `AccountFrozen`。这一要求直接影响类名、方法名乃至事件命名，消除了跨角色沟通中的语义漂移问题。

DDD 在 2010 年代随着微服务架构的普及再度受到广泛关注。限界上下文（Bounded Context）概念被直接映射为微服务的物理边界划分依据，使得 DDD 从单一大型系统的建模方法扩展为分布式系统的边界治理工具。

## 核心原理

### 限界上下文（Bounded Context）

限界上下文是 DDD 中最重要的边界概念，它定义了特定模型（包括通用语言）适用的范围。同一个词在不同限界上下文中可以有完全不同的含义：在电商系统里，"商品"在"库存上下文"中关注的是库存数量和 SKU，而在"营销上下文"中关注的是标签、活动资格。

两个限界上下文之间的集成关系通过**上下文映射（Context Map）**描述，Evans 定义了九种关系模式，常用的包括：
- **防腐层（Anti-Corruption Layer，ACL）**：下游上下文主动转换来自上游的模型，避免外部概念污染内部设计。
- **共享内核（Shared Kernel）**：两个上下文共用一部分模型，需要严格的协调机制。
- **开放主机服务（Open Host Service）**：上游提供标准化协议供多个下游接入。

### 聚合根（Aggregate Root）

聚合（Aggregate）是一组具有一致性边界的领域对象集合，聚合根是该集合唯一的外部访问入口。外部对象只能持有聚合根的引用，不能直接操作聚合内部的子实体。以订单系统为例，`Order` 是聚合根，`OrderItem` 是内部实体，外部代码不应直接修改 `OrderItem`，必须通过 `Order.addItem()` 或 `Order.removeItem()` 方法操作，由 `Order` 负责维护订单总金额与条目的一致性。

聚合根的设计直接决定事务边界：**一次事务只应修改一个聚合**。跨聚合的修改通过领域事件（Domain Event）实现最终一致性，而非使用分布式锁或数据库跨表事务。

### 实体、值对象与领域事件

**实体（Entity）**以身份标识符区分，`Order#10001` 和 `Order#10002` 是两个不同实体，即使所有属性相同。**值对象（Value Object）**则完全由属性值定义，没有独立标识，例如 `Money(100, "CNY")` 与另一个 `Money(100, "CNY")` 完全等价，且值对象应设计为不可变（immutable）。

**领域事件（Domain Event）**用于描述业务上已发生的事情，命名惯例为过去时，例如 `OrderPlaced`、`PaymentConfirmed`。它承载跨聚合、跨上下文的解耦协作，与六边形架构中的端口结合时，领域事件通过出站端口发布，由基础设施层的消息队列适配器实现。

## 实际应用

在电商平台重构场景中，一个典型的 DDD 落地过程如下：首先通过**事件风暴（Event Storming）**工作坊与业务方协作，识别出系统内所有领域事件（如 `OrderPaid`、`InventoryReserved`），再沿着事件的触发边界识别出"订单上下文""库存上下文""支付上下文"三个限界上下文。在代码结构上，每个限界上下文作为独立的 Maven 模块或微服务部署。

在与 Clean Architecture 结合时，聚合根和值对象位于最内层的 **Domain 层**，完全不依赖任何框架；应用服务（Application Service）位于 **Use Case 层**，负责编排聚合操作和发布领域事件；JPA Repository 的实现属于 **Infrastructure 层**，通过接口反向依赖注入。这种分层方式使聚合根的单元测试可以完全不启动 Spring 容器，测试速度从分钟级降至毫秒级。

## 常见误区

**误区一：将数据库表结构直接映射为领域模型。** 这是"贫血模型（Anemic Domain Model）"的典型成因——领域对象只有 getter/setter，业务逻辑全部散落在 Service 层。DDD 要求领域对象本身承载行为，例如 `Order.cancel()` 方法内部检查订单状态机规则，而不是在 `OrderService.cancelOrder()` 中写一堆 if-else 判断 `order.getStatus()`。

**误区二：把整个系统建模为一个聚合。** 有些团队将 `User` 聚合根下挂载几十个子实体，导致每次修改用户地址都要加载并锁定整个用户对象。聚合的设计原则是"尽量小"，Evans 在书中明确指出聚合应只包含维护一致性所必需的最小对象集。大型聚合直接导致数据库热点行锁和并发性能下降。

**误区三：为每个领域概念都创建限界上下文。** 限界上下文的划分粒度与团队规模相关——Conway 定律指出，系统架构趋向于模仿组织的沟通结构。一个 3 人团队维护 10 个限界上下文会产生大量跨上下文集成成本，得不偿失。

## 知识关联

DDD 与**六边形架构**的关系体现在端口与适配器层次的对应：领域模型放在六边形中心，Repository 接口是出站端口，消息发布接口是另一个出站端口，二者共同保证了领域层对技术细节的零依赖。**Clean Architecture** 提供了更具体的分层命名（Entities、Use Cases、Interface Adapters），DDD 的聚合根对应 Entities 层，应用服务对应 Use Cases 层，两套理论互为补充。

向后延伸至**Serverless 架构**时，DDD 的限界上下文为函数粒度的划分提供了业务语义依据——一个限界上下文内的领域事件处理器可以自然地映射为独立的 Lambda 函数，避免将不同上下文的业务逻辑混杂在同一个 FaaS 函数中，保持 Serverless 部署单元与业务边界的一致性。