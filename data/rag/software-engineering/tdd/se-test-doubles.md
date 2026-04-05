---
id: "se-test-doubles"
concept: "测试替身"
domain: "software-engineering"
subdomain: "tdd"
subdomain_name: "测试驱动开发"
difficulty: 2
is_milestone: true
tags: ["技巧"]

# Quality Metadata (Schema v2)
content_version: 4
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

# 测试替身

## 概述

测试替身（Test Double）是在单元测试中用来替代真实依赖对象的模拟对象总称。这一术语由Gerard Meszaros在其2007年出版的《xUnit Test Patterns》一书中正式提出，借用了电影行业中"替身演员"（stunt double）的概念——当真实演员无法出场时，替身代为完成拍摄任务。在软件测试中，测试替身扮演着相同角色：当数据库连接、外部API、邮件服务等真实依赖难以在测试环境中使用时，测试替身代为接管交互。

测试替身的核心价值在于实现**测试隔离**。如果一个单元测试依赖真实的数据库，那么测试速度慢、结果不稳定、测试失败原因也难以定位。通过引入测试替身，开发者可以精确控制依赖的行为，确保每次测试运行的输入输出完全可预测，测试执行速度也可从数秒降至毫秒级别。Meszaros将测试替身细分为五种类型：Dummy、Stub、Fake、Spy和Mock，每种类型服务于不同的测试意图。

---

## 核心原理

### Stub：控制间接输入

Stub（桩对象）用于向被测代码提供预设的返回值，从而控制测试的间接输入。例如，当被测代码调用 `UserRepository.findById(1)` 时，Stub直接返回一个预先构造的 `User` 对象，而不触及任何数据库。Stub只关注"给出什么答案"，不验证自己被调用了多少次。在Python的`unittest.mock`库中，`MagicMock` 配合 `return_value` 属性即可创建Stub。Stub适合用于测试**当依赖返回特定值时，被测逻辑是否正确分支**。

### Mock：验证间接输出

Mock（模拟对象）不仅能返回预设值，更重要的是它记录所有调用，并在测试结束时**验证交互行为是否符合预期**。例如，验证 `EmailService.send()` 在用户注册后被调用恰好一次，且参数为正确的邮件地址。Mock的核心公式可以表达为：`verify(mock.method()).times(N)`。如果 `EmailService.send()` 被调用了零次或两次，Mock会让测试失败。Java的Mockito框架使用 `verify(emailService, times(1)).send(anyString())` 实现这一验证。Mock用于测试**被测代码是否对依赖发出了正确的调用指令**。

### Fake：可运行的简化实现

Fake（伪对象）是依赖的一个功能简化但可真正运行的实现。最典型的例子是用内存中的`HashMap`代替真实的数据库存储层：`InMemoryUserRepository`实现了与真实`UserRepository`相同的接口，所有`save`和`find`操作都在内存中完成，无需网络连接或SQL引擎。Fake与Stub的关键区别在于：Fake有真实的业务逻辑，数据在同一次测试会话中是持久化的；而Stub只是硬编码返回值，没有状态。SQLite的内存模式（`:memory:`）在集成测试中扮演的就是Fake的角色。

### Spy：观察真实对象的行为

Spy（间谍对象）包装了真实对象，在调用真实方法的同时记录调用信息。与Mock的不同之处在于，Spy默认执行真实逻辑，而非完全替换它。例如，用Spy包装真实的`Logger`对象，测试代码正常运行，同时额外记录`Logger.warn()`被调用了几次。Mockito中通过 `@Spy` 注解或 `spy(new RealObject())` 创建Spy。Spy适合在**无法或不需要完全替换依赖，但又需要观测某些交互**的场景中使用。

### Dummy：填充参数占位

Dummy（哑对象）是最简单的测试替身，仅用于填充方法签名所需的参数，在测试执行过程中永远不会被实际使用到。例如，测试 `OrderService.cancel(order, user, reason)` 时，如果测试只关心 `reason` 参数对取消逻辑的影响，`user` 参数可以传入一个空的 `new User()` 对象——这就是Dummy。Dummy的存在纯粹是为了让代码能够编译和运行。

---

## 实际应用

**场景一：支付网关测试**  
电商系统中，`PaymentService` 依赖第三方支付API。真实API在测试中会产生实际扣款，且网络延迟不稳定。解决方案是创建 `StubPaymentGateway`，让其在接收到特定卡号（如`4111111111111111`）时始终返回成功，接收到`4000000000000002`时返回余额不足错误。通过切换Stub的返回值，可以覆盖支付成功、失败、超时等所有分支逻辑，整套测试无需任何网络请求。

**场景二：验证通知发送逻辑**  
订单完成后系统需发送短信通知。测试中用Mock替代 `SmsService`，在调用 `orderService.complete(order)` 后，执行 `verify(smsMock).send(order.getCustomerPhone(), contains("订单已完成"))`，同时验证短信内容和接收号码均正确，且仅发送一次，避免重复通知。

**场景三：Fake替代Redis缓存**  
在本地开发和CI环境中，用 `InMemoryCache` Fake替代Redis客户端，使得缓存相关测试无需启动Redis进程，CI流水线中节省约30秒的容器启动时间，且不依赖环境配置。

---

## 常见误区

**误区一：Mock和Stub可以混用，没有区别**  
很多开发者将Mock和Stub当作同义词互换使用，但它们的测试意图截然不同。Stub只设置返回值，不做事后验证；Mock强制验证交互发生。如果测试既设置了返回值又验证了调用次数，这个对象是Mock，不是Stub。混淆概念会导致测试职责模糊，难以判断测试失败的根因。

**误区二：替身越多，测试越好**  
过度使用Mock（尤其是对每个依赖都Mock）会导致测试与实现细节耦合过紧。一旦重构内部调用顺序，即使业务逻辑正确，大量Mock验证也会失败。Martin Fowler将这种测试称为"脆性测试"（Fragile Test）。测试替身应只覆盖**跨越系统边界**的依赖（如数据库、网络、时间），而非所有对象间的协作。

**误区三：Fake与真实实现保持同步是自动的**  
使用Fake时，开发者常忽视Fake本身需要维护。当真实`UserRepository`新增了 `findByEmail()` 方法，`InMemoryUserRepository` Fake若未同步更新，基于Fake的测试将无法覆盖新方法，产生测试盲区。良好实践是让Fake实现与真实实现相同的接口，利用接口约束强制同步。

---

## 知识关联

**前置基础：单元测试与集成测试**  
理解测试替身需要先掌握单元测试的**隔离原则**——单元测试只测试一个代码单元，而非整个调用链。测试替身正是实现这一隔离的工具。集成测试场景中，Fake（如内存数据库）同样扮演重要角色，但此时不隔离组件间的真实交互，而是隔离外部基础设施。

**后续进阶：测试模式与测试覆盖率**  
掌握五种测试替身类型后，可以进一步学习**测试模式**中的"四阶段测试模式"（Arrange-Act-Assert-Annihilate）和"对象母亲模式"（Object Mother），这些模式规范了测试替身的创建和组织方式。在分析**测试覆盖率**时，合理使用Stub控制条件分支输入，是提升分支覆盖率（Branch Coverage）的关键手段——通过切换Stub返回值，同一段被测代码的`if-else`两个分支都可以被覆盖到。