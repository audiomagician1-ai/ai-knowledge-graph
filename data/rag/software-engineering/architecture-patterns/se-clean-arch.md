# Clean Architecture（整洁架构）

## 概述

Clean Architecture 是 Robert C. Martin（绰号 "Uncle Bob"）于 2012 年在其博客文章《The Clean Architecture》中首次系统阐述，并在 2017 年出版的同名书籍 *Clean Architecture: A Craftsman's Guide to Software Structure and Design*（ISBN 978-0134494166）中完整定义的软件架构模式。其核心视觉表现是一张由内到外分为四个同心圆层的"洋葱图"，从内到外依次为：实体层（Entities）、用例层（Use Cases）、接口适配器层（Interface Adapters）和框架与驱动层（Frameworks & Drivers）。

该模式在思想上综合吸收了 Alistair Cockburn 于 2005 年提出的六边形架构（Hexagonal Architecture，又称端口与适配器架构）以及 Jeffrey Palermo 于 2008 年提出的洋葱架构（Onion Architecture），并将其统一在一套精确的"依赖规则"之下。Martin 本人将这一类架构统称为"关注点分离"架构，其共同目标是将业务规则与技术细节彻底隔离，使系统在框架、数据库、UI 层面均保持独立可替换。

与传统的三层分层架构（表现层→业务层→数据层）不同，Clean Architecture 的层次不是线性堆叠的，而是围绕业务规则形成同心圆。这一区别在实践中意义重大：三层架构中数据库位于最底层，暗示业务逻辑依赖数据库；而 Clean Architecture 明确地把数据库推到最外层，视其为"可替换的细节"。

---

## 核心原理

### 依赖规则（The Dependency Rule）

Clean Architecture 的唯一强制性架构约束是：**源代码的依赖方向只能由外向内，绝不能反转。** 外层的框架可以依赖内层定义的接口，但内层的实体和用例绝不能 `import` 或引用外层的任何类、函数或数据结构。

这一规则通过 **依赖反转原则（Dependency Inversion Principle，DIP）** 在代码层面实现。当用例层需要持久化数据时，它不直接调用数据库驱动，而是调用一个在用例层内部定义的抽象接口（如 `UserRepository`）；接口适配器层中的具体类（如 `SqlUserRepository`）实现该接口，并通过依赖注入在运行时装配。用 Python 伪代码说明：

```python
# 合法：用例层引用实体层（内 → 更内）
from entities.user import User

# 合法：用例层定义抽象，接口适配器层实现它（外层依赖内层接口）
# use_cases/ports.py
from abc import ABC, abstractmethod
class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> User: ...

# 非法：实体层引用框架层（内层不能依赖外层）
# entities/user.py
from django.db import models  # ← 违反依赖规则，不允许出现
```

依赖规则用形式化语言可以表达为：若定义集合 $L_1 \subset L_2 \subset L_3 \subset L_4$ 分别代表四个层（从内到外），则对任意模块 $m_i \in L_i$ 和 $m_j \in L_j$，若 $i < j$，则 $m_i \not\rightarrow m_j$（$m_i$ 不依赖 $m_j$），而 $m_j \rightarrow m_i$ 是允许的。这个方向约束是 Clean Architecture 与简单分层架构在结构上最本质的区别。

### 四层结构的具体职责

**实体层（Entities）**：封装全企业范围的关键业务规则（Critical Business Rules）。这些规则即使不存在计算机系统、仅靠人工处理也同样成立。实体是纯 POJO/PORO（Plain Old Java/Ruby Object），不得含有任何框架注解或数据库映射元数据。例如，`Invoice` 实体中"含税金额 = 净额 × (1 + 税率)"的计算逻辑属于此层，与系统是否使用 Web 框架毫无关联。

**用例层（Use Cases）**：封装特定应用的业务规则（Application Business Rules），协调若干实体完成单一业务目标，如"创建订单"（`CreateOrderUseCase`）或"用户注册"（`RegisterUserUseCase`）。用例层只通过输入/输出数据结构（Input Port / Output Port）与外部交互。Martin 特别强调，用例类中不得出现 HTTP 状态码、SQL 语句、JSON 字段名等任何技术细节。每个用例对应一个独立的类，这使得用例的职责边界清晰，单元测试可以在无框架环境下直接实例化并运行。

**接口适配器层（Interface Adapters）**：负责数据格式转换，将来自外层的技术表示（如 HTTP 请求的 JSON 体、命令行参数）转换为用例可处理的输入数据结构，并将用例的输出结果转换为外层所需格式（如 HTTP Response、HTML 页面）。该层包含三类组件：Controller（接收外部输入并调用用例）、Presenter（格式化用例输出）和 Gateway（将用例的抽象仓库接口适配到具体数据库驱动）。

**框架与驱动层（Frameworks & Drivers）**：包含所有具体技术选型，如 Spring Boot、Django、React、MySQL、Redis 等。Martin 将其称为"细节"（Details），并指出"Web 是一个细节，数据库是一个细节"。该层的代码应尽量精简，主要作用是"胶水代码"——将框架的生命周期钩子与内层组件装配在一起。

### 跨层数据传输的约束

Clean Architecture 对跨层数据传输有明确规定：跨越边界传递的数据必须是简单的数据结构（如 DTO，Data Transfer Object），而**不能是实体对象本身**。这一约束防止外层通过引用实体对象间接获得对内层的控制权。Martin 在书中以"整洁"的定义做类比：数据越过边界时应被"剥皮"，只保留对目标层有意义的字段，避免不必要的耦合。

---

## 关键方法与公式

### 依赖注入的装配点（Composition Root）

Clean Architecture 要求所有依赖注入的装配发生在系统的"组合根"（Composition Root）处——通常是应用程序的入口点（`main` 函数或启动类）。这是唯一允许外层实例化内层接口具体实现并注入的位置。这一模式由 Mark Seemann 在 *Dependency Injection in .NET*（Seemann, 2011）中明确命名。

用 Python 示例展示组合根的装配：

```python
# main.py（框架与驱动层，组合根）
from adapters.gateways.sql_user_repository import SqlUserRepository
from use_cases.register_user import RegisterUserUseCase
from adapters.controllers.user_controller import UserController

# 在此处装配依赖
repository = SqlUserRepository(db_connection)
use_case = RegisterUserUseCase(repository)   # 用例接收抽象接口
controller = UserController(use_case)
```

`RegisterUserUseCase` 的构造函数签名为 `__init__(self, user_repo: UserRepository)`，它只感知抽象接口，不知道 `SqlUserRepository` 的存在。

### 测试覆盖率与层次分布

Clean Architecture 的测试策略与测试金字塔高度吻合（Cohn, 2009）：
- 实体层和用例层应覆盖 **接近 100%** 的单元测试，因为它们无任何外部依赖，测试速度极快。
- 接口适配器层通常以集成测试为主，覆盖数据转换逻辑。
- 框架与驱动层的 E2E 测试数量最少，但覆盖关键业务路径。

这与传统架构形成对比：在传统三层架构中，业务逻辑与框架强耦合，单元测试需要 Mock 大量框架对象，测试编写成本高且执行慢。

---

## 实际应用

### 案例：将数据库从 MySQL 替换为 MongoDB

Clean Architecture 最具说服力的实证场景是数据库替换。假设系统使用 MySQL，`SqlUserRepository` 实现了 `UserRepository` 接口。若需迁移至 MongoDB，只需：

1. 在接口适配器层新增 `MongoUserRepository`，实现同一 `UserRepository` 接口。
2. 在组合根（`main.py`）中将注入的实现从 `SqlUserRepository` 切换为 `MongoUserRepository`。
3. 实体层和用例层的代码**零修改**。

此过程的变更范围被严格限制在接口适配器层和框架层，可通过 Git Diff 量化验证：核心业务代码的改动行数为 0。

### 案例：同一用例支持 REST API 与 gRPC

用例层的输入/输出端口（Input/Output Port）是纯数据结构，不绑定任何传输协议。一个 `PlaceOrderUseCase` 可以被两个独立的 Controller 调用：

- `RestOrderController`：解析 HTTP POST 请求体，构造 `PlaceOrderInput` DTO，调用用例，将 `PlaceOrderOutput` 序列化为 JSON 返回。
- `GrpcOrderController`：解析 Protobuf 消息，构造同样的 `PlaceOrderInput` DTO，调用同一用例，将输出序列化为 Protobuf 返回。

两个 Controller 共享同一个用例实例，业务逻辑无重复。

### 在 Java Spring Boot 项目中的目录结构

```
src/
├── domain/
│   ├── entities/          # 实体层：User, Order, Invoice
│   └── use_cases/         # 用例层：RegisterUserUseCase, PlaceOrderUseCase
│       └── ports/         # 用例定义的抽象接口：UserRepository
├── adapters/
│   ├── controllers/       # REST Controller
│   ├── presenters/        # 响应格式化
│   └── gateways/          # JPA Repository 实现
└── infrastructure/
    ├── config/            # Spring 配置与组合根
    └── persistence/       # JPA Entity 映射（不得出现在 domain/ 下）
```

这一目录结构使依赖方向在文件系统层面即可视化验证：`domain/` 目录下的任何文件不得 `import` `adapters/` 或 `infrastructure/` 下的类。

---

## 常见误区

### 误区一：将 JPA Entity 放入实体层

最高频的错误是将 Java 的 JPA/Hibernate 注解实体（带有 `@Entity`、`@Table` 等注解的类）直接用作 Clean Architecture 的实体层对象。这将数据库 ORM 框架的依赖引入了最内层，彻底违反依赖规则。正确做法是维护两套对象：领域实体（Domain Entity，无注解的纯 Java 类）和持久化实体（Persistence Entity，带 ORM 注解），并在 Gateway 层负责两者之间的映射转换。

### 误区二：用例层直接返回实体对象

若用例的 Output Port 返回 `User` 实体对象（而非 DTO），Controller 层就能通过该对象的方法间接调用业务逻辑，甚至可以修改实体状态，导致业务逻辑泄漏到外层。正确做法是用例层返回包含所需字段的不可变 DTO（如 `UserResponseModel`）。

### 误区三：每个用例都创建独立接口导致过度膨胀

Clean Architecture 要求每个用例对应独立的类，但并不要求每个用例都定义一个接口。当用例仅被单一 Controller 调用时，直接依赖具体用例类已足够；接口仅在需要多态或测试替换时才有价值。过度抽象会使项目文件数量激增，Martin 本人在书中警告"不要为了架构而架构"。

### 误区四：将 Clean Architecture 等同于 DDD

领域驱动设计（Domain-Driven Design，Evans, 2003）与 Clean Architecture 在部分概念上重叠（如实体、聚合根），但两者关注层面不同：DDD 解决的是如何对复杂业务领域建模，Clean Architecture 解决的是如何组织代码的依赖结构。两者可以结合使用：DDD 的聚合根可以成为 Clean Architecture 实体层的居民，DDD 的仓储接口（Repository）可以对应 Clean Architecture 用例层的输出端口。

---

## 知识关联

### 与 SOLID 原则的直接对应

Clean Architecture 可以被理解为 SOLID 原则在架构层面的集体应用：
- **S（单一职责）**：每个用例类只负责一个业务场景。
- **O（开闭原则）**：通过新增 Gateway 实现类来切换数据库，而不修改用例代码。