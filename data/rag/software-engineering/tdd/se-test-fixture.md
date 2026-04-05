---
id: "se-test-fixture"
concept: "测试夹具"
domain: "software-engineering"
subdomain: "tdd"
subdomain_name: "测试驱动开发"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 测试夹具

## 概述

测试夹具（Test Fixture）是指在运行测试用例前后，负责建立和清理测试所需环境的一组代码结构。这些代码确保每个测试用例都能在已知、可预测的状态下开始执行，并在执行结束后将环境恢复原状。测试夹具最早由 Kent Beck 在 SUnit 框架（1994年为 Smalltalk 设计）中系统化引入，后被 JUnit 继承并推广到整个 xUnit 测试框架家族。

在测试驱动开发（TDD）中，测试夹具解决了"重复搭建测试环境"的问题。如果没有测试夹具，每个测试方法都必须自己创建数据库连接、初始化对象、填充测试数据，代码会大量重复且难以维护。测试夹具将这些准备工作统一抽取出来，让每个 `@Test` 方法只专注于验证一个具体行为。

## 核心原理

### SetUp：测试前的初始化

`SetUp` 方法（在 JUnit 5 中标注为 `@BeforeEach`，在 Python unittest 中命名为 `setUp`）在**每个**测试方法执行之前自动调用一次。其核心设计原则是：`SetUp` 运行后，系统应处于一个完全确定的初始状态，与之前任何测试的执行结果无关。

典型的 `SetUp` 操作包括：实例化被测对象、打开数据库事务、创建临时文件或目录、初始化内存中的测试数据集合。例如，测试一个购物车类时，`setUp` 通常会创建一个全新的 `ShoppingCart` 实例并向其中添加已知商品，使后续每个测试从完全相同的起点出发。

```java
@BeforeEach
void setUp() {
    cart = new ShoppingCart();
    cart.addItem(new Item("苹果", 3.50, 2));
}
```

### TearDown：测试后的清理

`TearDown` 方法（JUnit 5 中为 `@AfterEach`，unittest 中为 `tearDown`）在**每个**测试方法执行完毕后自动调用，无论测试是通过还是失败。其存在的关键原因是防止**测试污染**——一个测试遗留的状态影响后续测试的结果。

常见的 `TearDown` 操作包括：回滚数据库事务、关闭文件句柄、删除临时目录、清空单例对象的内部状态。值得注意的是，即使 `@Test` 方法中抛出了异常，xUnit 框架依然保证 `TearDown` 会被调用，这与 `try-finally` 语义一致。若测试框架不保证此行为，测试之间的隔离性就会被破坏。

### 数据工厂：结构化地生成测试数据

数据工厂（Data Factory / Object Mother）是测试夹具的一种高级模式，专门用于创建测试所需的复杂对象。当一个领域对象（如 `Order`）需要十几个字段才能构造，但测试只关心其中一个字段时，数据工厂提供带有合理默认值的构建方法，测试只需覆盖关心的字段。

Object Mother 模式由 ThoughtWorks 的 Nat Pryce 于 2003 年前后整理命名。在现代 Java 测试中，常见的实现是构建器（Builder）风格的工厂方法：

```java
public class OrderFactory {
    public static Order defaultOrder() {
        return new Order.Builder()
            .userId(999L)
            .status(OrderStatus.PENDING)
            .totalAmount(BigDecimal.valueOf(100.00))
            .build();
    }
}
```

### 共享状态：类级别夹具的使用与风险

除了每个测试方法独立执行的 `@BeforeEach/@AfterEach`，xUnit 还提供类级别夹具：JUnit 5 的 `@BeforeAll/@AfterAll`，NUnit 的 `[OneTimeSetUp]/[OneTimeTearDown]`。这类夹具在**整个测试类**中只执行一次，适合初始化成本极高的资源，例如启动嵌入式数据库（如 H2）或加载大型机器学习模型。

共享状态的最大风险是**测试顺序依赖**（Test Order Dependency）：若多个测试方法共享同一个对象实例，某个测试对该对象的修改会导致后续测试行为异常。规避方法是：被 `@BeforeAll` 初始化的对象必须是只读的（immutable）或在每个测试方法中以只读方式使用，所有写操作应在 `@BeforeEach` 中重置。

## 实际应用

**场景一：Web API 集成测试**  
使用 Spring Boot Test 测试 REST 接口时，`@BeforeEach` 会向测试数据库插入特定记录，`@AfterEach` 执行 `DELETE FROM orders WHERE test_batch_id = 'T001'` 清理这些记录，确保每次测试针对同一基线数据。

**场景二：文件处理模块测试**  
测试一个 CSV 解析器时，`setUp` 在系统临时目录（`System.getProperty("java.io.tmpdir")`）创建内容固定的 `.csv` 测试文件，`tearDown` 调用 `Files.deleteIfExists(testFilePath)` 删除该文件，避免磁盘残留。

**场景三：数据工厂减少测试重复**  
一套订单服务测试中，50 个测试方法需要各种 `Order` 对象。引入 `OrderFactory` 后，90% 的测试直接调用 `OrderFactory.defaultOrder()` 并只修改一个关心的字段，代码行数减少约 40%，且修改 `Order` 构造参数时只需更新工厂一处。

## 常见误区

**误区一：在 `@BeforeAll` 中修改共享对象**  
`@BeforeAll` 初始化的对象若在测试中被修改，测试将产生顺序依赖。常见错误是将 `List<Item>` 声明为 `static` 字段并在 `@BeforeAll` 中填充，然后在某个测试中调用 `list.clear()`，导致后续测试面对空列表。正确做法是将集合的填充移到 `@BeforeEach`，或确保所有测试只读访问该集合。

**误区二：`TearDown` 中包含断言**  
有开发者在 `tearDown` 中加入 `assert` 语句验证清理结果，例如 `assertNull(connection)`。这会导致当 `@Test` 本身失败时，`tearDown` 中的断言异常覆盖了原始失败信息，造成调试困难。清理代码应使用防御性写法（检查非空再关闭），不应通过断言验证清理状态。

**误区三：数据工厂返回可变共享实例**  
若 `OrderFactory.defaultOrder()` 每次返回同一个单例对象，而非新建实例，两个测试对该对象的修改会互相干扰。数据工厂的每次调用必须返回**全新独立的对象实例**，这是区别于单例模式的核心要求。

## 知识关联

测试夹具是理解 TDD 测试隔离性的基础——JUnit 5 的 `@ExtendWith` 扩展机制（如 `MockitoExtension`）本质上就是通过实现 `BeforeEachCallback` 和 `AfterEachCallback` 接口来插入自定义夹具逻辑。掌握测试夹具后，可进一步学习测试替身（Test Double）中的 Mock 对象：Mock 框架（如 Mockito）的 `@Mock` 注解依赖夹具机制在每个测试前自动重置 mock 状态，防止跨测试的交互记录污染。数据工厂模式直接引导向测试数据管理领域，如 Flyway/Liquibase 的数据库迁移脚本如何与集成测试夹具配合使用。