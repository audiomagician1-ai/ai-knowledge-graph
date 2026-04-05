---
id: "se-clean-arch"
concept: "Clean Architecture"
domain: "software-engineering"
subdomain: "architecture-patterns"
subdomain_name: "架构模式"
difficulty: 3
is_milestone: false
tags: ["原则"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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


# Clean Architecture（整洁架构）

## 概述

Clean Architecture 是 Robert C. Martin（绰号 "Uncle Bob"）于 2012 年在其博客文章中首次系统阐述、并在 2017 年出版的同名书籍中完整定义的架构模式。它的核心视觉表现是一张由内到外分为四个同心圆层的"洋葱图"，从内到外依次为：实体层（Entities）、用例层（Use Cases）、接口适配器层（Interface Adapters）和框架与驱动层（Frameworks & Drivers）。

该模式综合吸收了 Alistair Cockburn 的六边形架构（2005）和 Jeffrey Palermo 的洋葱架构（2008）的思想，并将其统一在一套明确的"依赖规则"之下。与单纯的分层架构不同，Clean Architecture 的层次不是线性堆叠的，而是围绕业务规则形成同心圆，任何外层的代码都不能在内层留下任何名称、引用或痕迹。

Clean Architecture 最重要的意义在于使业务逻辑对框架、数据库和 UI 保持独立——例如，可以在不修改任何用例代码的前提下，将数据库从 MySQL 替换为 MongoDB，或将 REST API 替换为 gRPC 接口。这种特性让核心业务逻辑可以在没有框架的情况下被单元测试，极大降低了长期维护成本。

---

## 核心原理

### 依赖规则（The Dependency Rule）

Clean Architecture 的唯一强制性规则是：**源代码的依赖方向只能由外向内**，绝不能反转。外层的框架可以依赖内层的接口，但内层的实体绝不能 `import` 外层的任何类或函数。用 Python 伪代码来说明：

```
# 合法：用例层引用实体层
from entities.user import User

# 非法：实体层引用框架层（如 Django ORM）
from django.db import models  # ← 这在 entities/ 目录下不允许出现
```

这一规则通过**依赖反转原则（DIP）**实现：内层定义接口（如 `UserRepository` 的抽象类），外层提供具体实现（如 `SqlUserRepository`），通过依赖注入在运行时装配。

### 四层结构的具体职责

**实体层（Entities）**：封装全企业范围的业务规则，包含最核心的数据结构和纯业务逻辑函数，与任何应用场景无关。例如，`Invoice` 实体中计算税额的方法属于这里，无论是 Web 应用还是命令行工具都复用同一份代码。

**用例层（Use Cases）**：封装特定应用的业务规则，协调实体完成特定操作，如"创建订单"或"用户注册"。用例层只能通过接口与外部交互，不得出现 HTTP 状态码、SQL 语句等技术细节。

**接口适配器层（Interface Adapters）**：负责数据格式转换，将来自外层（如 HTTP 请求的 JSON）转换为用例可处理的数据结构，或将用例的输出结果转换为框架所需格式。Controller、Presenter 和 Gateway 都属于本层。

**框架与驱动层（Frameworks & Drivers）**：包含所有具体技术选型，如 Spring Boot、Django、MySQL 驱动、React 等，是"插件"性质的存在，更换时理论上不影响内层任何代码。

### 跨边界的数据传输对象（DTO）

当数据跨越同心圆边界时，必须使用简单的数据结构（如 DTO 或 Plain Old Objects），而不能传递实体对象本身进入外层，也不能将框架的数据模型（如 ORM 的 `Model` 对象）传入内层。这一要求防止了外层对实体层的隐式耦合——例如，禁止将 Django ORM 的 `User` 模型对象直接传入用例层，而应将其映射为一个仅含必要字段的 `UserDTO`。

---

## 实际应用

**电商系统中的订单服务**：实体层定义 `Order` 和 `OrderItem`，包含验证逻辑；用例层有 `PlaceOrderUseCase`，依赖抽象的 `OrderRepository` 接口；接口适配器层有 `OrderController` 处理 HTTP 请求，以及 `SqlOrderRepository` 实现数据库存储；框架层引入 Spring Boot 和 Hibernate。当业务要求从关系型数据库迁移到 DynamoDB 时，只需编写一个新的 `DynamoOrderRepository` 实现并注入，`PlaceOrderUseCase` 代码无需任何改动。

**测试策略上的优势**：由于实体层和用例层不依赖任何框架，测试用例无需启动 Spring 容器或连接数据库。以一个包含 50 个用例的系统为例，所有用例的单元测试可以在 2 秒内完成，而传统分层架构中依赖 Spring Context 的集成测试可能需要 30 秒以上。

---

## 常见误区

**误区一：认为必须严格实现四层，不能增减**。Martin 本人明确表示四层仅是示意，实际项目可能有五层或六层。关键不是层数，而是"依赖方向只能向内"这一条规则。强行把所有概念塞入四层反而会造成过度设计。

**误区二：将 Clean Architecture 等同于文件目录结构**。一些项目仅是按照 `entities/`、`usecases/`、`adapters/` 创建文件夹，但代码中仍有大量跨层的直接 `import`，实质上并未遵守依赖规则。Clean Architecture 是代码依赖关系的约束，而非文件组织惯例，缺乏依赖注入机制的"Clean Architecture"项目是名不副实的。

**误区三：认为所有项目都适合使用 Clean Architecture**。对于简单的 CRUD 服务或生命周期短的原型项目，引入实体层、用例层、DTO 转换等机制会导致代码量和复杂度成倍增加，而收益极低。Martin 自己也指出，该架构最适合业务规则复杂、需要长期演进的系统。

---

## 知识关联

**与分层架构的关系**：传统三层架构（表现层→业务层→数据层）的依赖方向是线性向下的，数据层处于最低层，框架细节（如 ORM）渗透至业务层。Clean Architecture 通过依赖反转原则将数据库推到了最外层，解决了传统分层架构中业务代码对数据库强耦合的痼疾。

**与 SOLID 原则的关系**：Clean Architecture 的可行性依赖于 SOLID 中的 D（依赖反转原则）和 I（接口隔离原则）。用例层定义窄小的 Repository 接口体现了 ISP，而外层实现这些接口体现了 DIP。若没有扎实的 SOLID 实践，层间边界无法真正维持。

**通向领域驱动设计**：Clean Architecture 的实体层与 DDD 中的领域层高度重叠，用例层对应 DDD 的应用服务层。掌握 Clean Architecture 后，学习 DDD 时可以直接将其实体、聚合根、领域服务映射到 Clean Architecture 的内层同心圆，两套体系在边界保护和业务中心化的理念上完全一致。