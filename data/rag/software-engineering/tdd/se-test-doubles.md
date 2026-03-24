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
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 测试替身

## 概述

测试替身（Test Double）是单元测试中用于替换真实依赖对象的仿制品，由Gerard Meszaros在2007年出版的《xUnit Test Patterns》一书中正式命名并分类。这个术语借鉴自电影行业的"替身演员"（stunt double）概念——当真实演员无法出场时，替身代为完成场景拍摄。在测试场景中，当真实依赖（数据库、外部API、文件系统等）难以控制或执行缓慢时，测试替身代替它们参与测试。

测试替身解决的核心问题是**测试隔离**：单元测试的目标是只验证被测单元（SUT，System Under Test）本身的逻辑，而不是验证其依赖项的行为。若一个发送邮件的函数测试真的发送了邮件，既浪费资源又难以断言结果，还会污染生产环境。通过引入测试替身，测试可以在完全受控的条件下运行，做到快速、可重复、互不干扰。

## 核心原理

### 五种测试替身的精确区分

Meszaros定义了五种测试替身，每种有不同的语义和用途：

**Dummy（哑对象）**：仅用于填充参数列表，不会被实际调用。例如一个方法签名要求传入Logger对象，但测试逻辑根本不触发日志路径时，传入`null`或空实现即为Dummy。它不包含任何行为逻辑。

**Stub（桩对象）**：提供预设的固定返回值，用于控制间接输入。例如`stubUserRepo.findById(1)`始终返回一个特定User对象。Stub只关注"给SUT提供数据"，不验证自身是否被调用。典型公式：`when(stub.method()).thenReturn(value)`。

**Fake（伪对象）**：拥有真实但简化的实现，例如用内存中的HashMap模拟数据库的完整CRUD操作。Fake与真实对象的区别在于它使用捷径实现，例如H2内存数据库就是对生产MySQL数据库的Fake替代。

**Spy（侦探对象）**：包装真实对象或手动记录调用信息，既执行部分真实逻辑，又记录被调用的次数和参数。测试结束后可断言"`sendEmail`方法被调用了恰好1次"。

**Mock（模拟对象）**：预先设定期望（expectation），测试结束时自动验证这些期望是否满足。Mock包含内置的断言机制，如果`mockEmailService.send()`从未被调用，测试会自动失败，无需手动断言。

### 状态验证 vs 行为验证

测试替身引入了两种不同的验证策略：

- **状态验证（State Verification）**：调用SUT之后，检查SUT或相关对象的状态。Stub和Fake通常配合状态验证使用。例如调用`cart.addItem(item)`后，断言`cart.getTotal() == 29.99`。

- **行为验证（Behavior Verification）**：验证SUT是否以正确的方式与依赖进行了交互。Mock和Spy配合行为验证使用。例如验证`paymentGateway.charge(userId, 29.99)`被调用了一次。

过度使用行为验证会导致测试与实现细节耦合，重构时频繁破坏测试，这是选择替身类型时必须权衡的关键点。

### 隔离框架的工作机制

现代测试框架如Mockito（Java）、unittest.mock（Python）、Sinon.js（JavaScript）通过运行时代理或字节码操作生成替身对象。以Mockito为例：

```java
UserRepository mockRepo = Mockito.mock(UserRepository.class);
when(mockRepo.findById(42)).thenReturn(new User("Alice"));
verify(mockRepo, times(1)).findById(42);
```

`mock()`创建了一个代理对象，`when...thenReturn`注册了Stub行为，`verify`执行了Mock期望验证。这三行代码同时体现了Stub（返回值控制）和Mock（调用验证）两种能力，这也是为什么日常开发中"mock"一词被混用来指代所有测试替身。

## 实际应用

**场景一：隔离第三方支付API**  
测试订单服务时，使用Stub替代支付网关，令`stub.charge()`返回`PaymentResult.SUCCESS`，使测试无需真实网络连接即可验证订单状态流转逻辑。失败路径测试只需让Stub返回`PaymentResult.INSUFFICIENT_FUNDS`，即可覆盖难以在真实环境中复现的异常分支。

**场景二：验证事件发布行为**  
用户注册完成后，系统应发布`UserRegisteredEvent`。使用Mock替代`EventBus`，测试结束后调用`verify(mockEventBus).publish(any(UserRegisteredEvent.class))`，精确验证事件类型和调用次数，而无需搭建完整的消息队列基础设施。

**场景三：用Fake简化集成测试**  
使用`FakeEmailSender`替代真实SMTP服务，Fake内部用`List<Email>`存储所有"已发送"邮件。测试不仅验证邮件是否发送，还可断言邮件内容：`assertThat(fakeEmailSender.getSent().get(0).getSubject()).isEqualTo("欢迎注册")`。

## 常见误区

**误区一：将Mock等同于所有测试替身**  
在Mockito等框架中，`mock()`方法返回的对象实际上既能充当Stub又能充当Mock，导致开发者将"mock"作为测试替身的通称。然而Meszaros的分类明确区分了五种替身，混淆概念会导致测试设计时目的不清晰——究竟是在控制输入（Stub的职责）还是验证交互（Mock的职责）。

**误区二：对所有依赖都使用Mock**  
对值对象、工具类（如`String.format`、`Math.abs`）和同一模块内的协作对象使用Mock，会导致测试代码量爆炸，且每次内部重构都要修改Mock期望。测试替身应只用于**跨越架构边界**的依赖：外部服务、I/O操作、时间/随机性来源。

**误区三：Stub与Fake可以互换**  
Stub返回硬编码值，无法正确响应不同的输入组合；Fake具有完整的简化逻辑，能对任意合法输入作出正确响应。当测试需要多次调用同一方法且每次输入不同时，Stub的局限性会暴露——例如`stubRepo.findById(1)`返回Alice、`findById(2)`返回Bob，需要为每种情况单独配置，而Fake的内存HashMap则自然支持任意键值查询。

## 知识关联

**依赖单元测试基础**：理解测试替身需要先掌握单元测试中的AAA结构（Arrange-Act-Assert），测试替身主要在Arrange阶段配置，在Assert阶段（Mock验证）完成其使命。没有明确的"被测单元"边界，就无法判断哪些对象需要被替换。

**引向测试模式**：掌握测试替身后，可以进一步学习更高层次的测试模式，例如"对象母亲模式"（Object Mother）用于构建复杂测试数据，"测试数据构建器模式"（Test Data Builder）用于流式创建Fake数据，以及"契约测试"（Contract Testing）——它在使用Stub的同时，通过Pact等工具验证Stub的行为是否与真实服务的契约一致，防止替身与现实脱节。
