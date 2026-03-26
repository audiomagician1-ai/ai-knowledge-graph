---
id: "se-test-patterns"
concept: "测试模式"
domain: "software-engineering"
subdomain: "tdd"
subdomain_name: "测试驱动开发"
difficulty: 2
is_milestone: false
tags: ["模式"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
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

# 测试模式

## 概述

测试模式（Testing Patterns）是测试驱动开发中经过实践验证的结构化代码组织方法，专门用于解决测试代码的可读性、可维护性和数据构造问题。三种最核心的测试模式分别是：AAA模式（Arrange-Act-Assert）、Builder Pattern（建造者模式）和Object Mother（对象母亲模式）。这三种模式各自解决测试代码中的不同痛点，组合使用时可以将测试套件的维护成本降低60%以上。

AAA模式由Bill Wake于2001年在极限编程社区中系统化提出，随后被《xUnit Test Patterns》（Gerard Meszaros，2007年）进一步标准化。Object Mother模式则由ThoughtWorks公司的工程师在2000年代初率先应用于大型企业项目。这些模式之所以重要，是因为测试代码同样是需要维护的生产资产——一个混乱的测试文件与一个混乱的业务代码文件同样会拖累项目进度。

## 核心原理

### AAA模式：三段式结构

AAA模式将每个测试用例强制划分为三个明确分离的阶段：**Arrange（准备）**、**Act（执行）**、**Assert（断言）**。

- **Arrange** 阶段：初始化所有测试所需的对象、配置测试替身（Mock/Stub）、设定输入数据。
- **Act** 阶段：调用且**仅调用一次**被测对象的目标方法。
- **Assert** 阶段：验证执行结果，通常对应一个逻辑断言点（允许多行断言验证同一个概念）。

```python
def test_order_total_includes_tax():
    # Arrange
    cart = ShoppingCart()
    cart.add_item(Product(price=100.0), quantity=2)
    tax_service = StubTaxService(rate=0.08)

    # Act
    total = cart.calculate_total(tax_service)

    # Assert
    assert total == 216.0  # 200 * 1.08
```

AAA模式的关键约束是Act阶段只有**一行代码**。如果Act阶段需要多行，说明被测方法的职责过于分散，暗示了生产代码的设计问题。

### Builder Pattern：链式数据构造

Builder Pattern在测试中的用法与生产代码中的GoF建造者模式结构相似，但目的不同——它专门用于构造复杂的测试数据对象，同时保持测试本身的声明式可读性。

核心做法是为每个复杂领域对象创建一个对应的TestBuilder类，提供链式调用接口，并设置合理的**默认值**：

```java
public class OrderBuilder {
    private String customerId = "default-customer";
    private List<OrderItem> items = List.of(defaultItem());
    private OrderStatus status = OrderStatus.PENDING;

    public OrderBuilder withCustomer(String customerId) {
        this.customerId = customerId;
        return this;
    }

    public Order build() {
        return new Order(customerId, items, status);
    }
}

// 测试中只声明与当前测试相关的字段
Order order = new OrderBuilder()
    .withCustomer("vip-123")
    .build();
```

Builder Pattern的核心价值在于**默认值策略**：每个字段都有业务有效的默认值，测试代码只需指定与当前测试场景相关的那一两个字段，其余字段保持默认。这使得一个20字段的领域对象在测试中依然可以被一行代码创建出来。

### Object Mother：共享工厂方法集合

Object Mother模式将测试中反复用到的**预定义对象实例**集中管理在一个工厂类中。它与Builder Pattern的区别在于：Builder Pattern适合需要细粒度定制的场景，而Object Mother适合存储业务意义明确、反复复用的"典型对象"。

```csharp
public static class CustomerMother {
    public static Customer VipCustomer() =>
        new Customer(id: "VIP-001", tier: Tier.Gold, creditLimit: 50000);

    public static Customer NewCustomer() =>
        new Customer(id: "NEW-001", tier: Tier.Bronze, creditLimit: 1000);

    public static Customer BlacklistedCustomer() =>
        new Customer(id: "BLK-001", tier: Tier.None, isBlacklisted: true);
}
```

Object Mother中的每个工厂方法命名应直接反映业务场景（`VipCustomer()`、`BlacklistedCustomer()`），而不是技术描述（`CustomerWithGoldTierAndHighCredit()`）。这样测试代码读起来接近业务需求文档，便于非技术成员理解测试意图。

## 实际应用

**电商订单系统中三种模式的协同使用：**

假设要测试"黑名单用户不能下单"的业务规则：

```python
def test_blacklisted_customer_cannot_place_order():
    # Arrange（使用Object Mother创建典型对象，使用Builder定制订单）
    customer = CustomerMother.blacklisted_customer()
    order = OrderBuilder().with_customer(customer).build()
    order_service = OrderService(fraud_checker=StubFraudChecker())

    # Act
    result = order_service.place_order(order)

    # Assert
    assert result.is_failure()
    assert result.error_code == "CUSTOMER_BLACKLISTED"
```

这个例子展示了三种模式的分工：AAA结构化测试布局，Object Mother提供预定义的黑名单用户对象，Builder Pattern构造只指定了相关字段的订单对象。

在前端测试中，Object Mother常用于存储API响应的JSON fixture对象；在微服务集成测试中，Builder Pattern用于构造不同配置的HTTP请求对象。

## 常见误区

**误区一：在Assert阶段进行额外的Act操作。**
常见错误写法是在断言时调用又一个方法来获取状态：`assert order_service.get_order(order.id).status == "PLACED"`。这在Act阶段之外引入了第二个动作，违反AAA的单一执行原则，同时将`get_order`方法的正确性引入了当前测试，造成测试职责不清晰。正确做法是在Act阶段直接捕获`place_order`的返回值并断言。

**误区二：Object Mother演变成"上帝工厂"。**
随着项目增长，一些团队将所有可能的对象变体都塞入同一个Object Mother类，最终该类超过1000行。正确的做法是按照领域边界拆分多个Mother类（`OrderMother`、`CustomerMother`、`PaymentMother`），每个类只包含5-10个有明确业务语义的工厂方法，超过这个数量时应考虑是否引入Builder Pattern来替代部分变体。

**误区三：Builder的默认值设置为null或零值。**
如果`OrderBuilder`的默认`customerId`是`null`，那么每个使用Builder的测试都必须显式设置客户ID，Builder的便利性荡然无存。默认值必须是业务上**有效的**值，能让对象在不做任何定制的情况下通过所有业务验证。

## 知识关联

测试模式在技术上依赖**测试替身**（Mock、Stub、Fake）作为前置知识——AAA模式的Arrange阶段几乎总是需要配置某种形式的测试替身来隔离外部依赖。没有测试替身的基础知识，就无法正确理解Arrange阶段为何会包含`StubTaxService`或`MockPaymentGateway`这样的对象构造。

三种测试模式之间也存在递进关系：初学者先掌握AAA获得测试结构化的基本能力；当测试数据构造开始出现大量重复时引入Object Mother；当Object Mother中出现过多相似变体时将其中部分替换为Builder Pattern。理解这个演化路径有助于避免过度设计——对简单项目盲目引入Builder Pattern反而增加了无谓的代码量。