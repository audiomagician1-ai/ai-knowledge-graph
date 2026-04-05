---
id: "se-arch-refactor"
concept: "架构级重构"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 3
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 架构级重构

## 概述

架构级重构是指对软件系统的整体结构进行系统性调整，包括模块解耦、微服务拆分、代码分层重组等操作，其目标是改变系统的组织方式而非修改业务逻辑。与方法级或类级重构不同，架构级重构的影响范围横跨多个模块、服务甚至整个代码仓库，通常需要数周到数月才能完成。

架构级重构的实践可以追溯到2000年代中期大型单体应用（Monolithic Application）暴露出扩展性瓶颈的时期。Martin Fowler 在2004年出版的《Patterns of Enterprise Application Architecture》中系统描述了分层架构的调整模式；2014年前后，随着 Netflix、Amazon 等公司公开微服务迁移案例，微服务拆分成为架构级重构中最受关注的子类型。

架构级重构的价值在于它能解决因历史累积导致的结构性问题：当一个模块同时承担数据访问、业务逻辑和 UI 渲染三种职责时，任何一处修改都会引发连锁测试失败，这不是代码坏味道（Code Smell），而是架构腐化（Architecture Decay）。只有架构级重构才能从根本上分离这些关注点。

---

## 核心原理

### 模块解耦的依赖方向控制

模块解耦的核心度量指标是传入耦合（Afferent Coupling，Ca）与传出耦合（Efferent Coupling，Ce）之比，由此派生出不稳定性指标：

```
I = Ce / (Ca + Ce)
```

I 值越接近 1，模块越不稳定（依赖他人多，被依赖少）；越接近 0，模块越稳定但也越难修改。架构级重构的目标是让高层业务模块的 I 值趋向 1（允许频繁变化），让底层基础模块的 I 值趋向 0（保持稳定）。Robert C. Martin 将此命名为"稳定依赖原则（Stable Dependencies Principle）"。实际操作时，常用依赖倒置（Dependency Inversion）手段插入接口层，将双向依赖切断为单向依赖。

### 微服务拆分的边界识别

微服务拆分并不是按技术分层拆分，而是按**领域边界（Bounded Context）**拆分，这是 Eric Evans 在《Domain-Driven Design》（2003）中提出的概念。识别 Bounded Context 的实操方法是"事件风暴（Event Storming）"：将团队聚集，用橙色便利贴标记领域事件（如"订单已支付"），用蓝色标记命令（如"创建订单"），当两组便利贴之间出现明显的语义断层时，该断层处即为服务边界候选点。

微服务拆分遵循**绞杀者模式（Strangler Fig Pattern）**：新服务逐步接管单体的功能，通过流量路由层（如 API Gateway）控制新旧服务的请求比例，最终"绞杀"旧代码。Netflix 完成从单体到微服务的迁移历时约 7 年（2008—2015），这说明此类重构必须配合持续交付流水线才能保证过渡期的稳定性。

### 代码分层调整的层职责重划

分层调整最常见的场景是将"大泥球（Big Ball of Mud）"架构改造为严格分层架构（Presentation → Application → Domain → Infrastructure）。操作规则是：每一层只能调用其正下方一层的接口，Domain 层禁止直接引用任何 Infrastructure 层的具体类（如 `JpaRepository`），必须通过 Repository 接口进行隔离。

分层调整的执行顺序至关重要：应先建立 Domain 层的纯净领域模型（不含任何框架注解），再逐步将 Service 类中混杂的数据库调用抽取到 Infrastructure 层。若顺序颠倒——先动 Infrastructure 层——会导致大量 Service 代码同时失效，难以增量提交和回滚。

---

## 实际应用

**电商单体拆分案例**：某电商平台的 `OrderService` 类包含 4000+ 行代码，同时处理库存扣减、支付调用、物流通知三种业务。架构级重构的第一步是在同一单体内部用包（Package）级别的隔离模拟服务边界，禁止 `order` 包直接 `import inventory` 包的类，改为通过 `DomainEventPublisher` 发布事件；第二步才是将包提取为独立的微服务进程。这种"先逻辑拆分、后物理拆分"的策略可将风险分散在两个阶段。

**数据库共享问题**：微服务拆分中最棘手的场景是多个服务共享同一张数据库表。解决方案遵循数据库重构（Database Refactoring）中的"扩展-收缩模式（Expand-Contract Pattern）"：先扩展——在新服务中创建独立的数据副本并保持双写同步；待数据一致性验证通过后再收缩——停止旧服务对该表的写入，最终迁移完整所有权。

**分层违规的自动检测**：可使用 ArchUnit 这一 Java 测试库编写架构约束测试，例如：

```java
noClasses().that().resideInPackage("..domain..")
    .should().dependOnClassesThat()
    .resideInPackage("..infrastructure..");
```

此测试会在 CI 流水线中持续守护分层边界，防止重构成果被后续开发侵蚀。

---

## 常见误区

**误区一：把微服务拆分等同于性能优化**。微服务拆分的直接收益是团队自治和独立部署，而非性能提升。由于服务间调用从进程内函数调用（纳秒级）变为网络 HTTP/gRPC 调用（毫秒级），过度拆分反而会引入严重的延迟叠加。若拆分后出现"分布式单体（Distributed Monolith）"——服务间强耦合，必须同步部署——则说明 Bounded Context 划分失败，拆分工作净收益为负。

**误区二：架构级重构可以不修改测试**。单体内一个集成测试可以覆盖完整业务链路，但微服务拆分后同样的测试需要 Mock 外部服务或使用契约测试（Consumer-Driven Contract Testing，如 Pact 框架）替代。跳过测试策略调整的架构重构，会导致测试套件覆盖率虚高（数字不变，实际覆盖场景大幅萎缩）。

**误区三：分层重构可以一次性完成**。由于架构级重构涉及的文件数量可能达到数百个，试图在一个 Git 分支上完成全部修改会产生极难审查的巨型 Pull Request，且与主干的合并冲突会呈指数级增长。正确做法是使用"特性开关（Feature Toggle）"或"抽象分支（Branch by Abstraction）"技术，将大重构拆解为每次不超过 200 行变更的小步提交。

---

## 知识关联

**前置知识衔接**：架构级重构直接依赖**重构模式**中的提取接口（Extract Interface）、移动类（Move Class）等基础操作——微服务拆分的本质就是将这些小操作组合放大到跨服务边界的尺度。**数据库重构**中的 Expand-Contract 模式是处理服务间共享数据库的必备技术，在没有掌握数据库重构策略的情况下直接进行服务拆分，极易造成数据一致性事故。

**后续知识延伸**：**游戏代码重构**是架构级重构在特定领域的应用，游戏引擎中的 Entity-Component-System（ECS）架构替代传统面向对象继承树，与微服务拆分中 Bounded Context 的逻辑有对应之处——两者都是将"大而全的对象"分解为"职责单一的小单元"，但游戏场景下需要额外处理实时帧率约束和状态同步问题，这些约束会对重构策略的选择产生根本性影响。