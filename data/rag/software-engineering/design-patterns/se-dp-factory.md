---
id: "se-dp-factory"
concept: "工厂模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: true
tags: ["创建型"]

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
# 工厂模式

## 概述

工厂模式是一组专门用于**对象创建**的设计模式，其核心思想是将"如何创建对象"的逻辑从"使用对象"的代码中分离出来，通过一个专门的"工厂"角色来负责实例化。客户端代码只需声明需要什么类型的产品，而不关心产品是如何被 `new` 出来的。这种分离使得新增产品类型时，调用方代码无需修改。

工厂模式家族源于1994年GoF（Gang of Four）出版的《Design Patterns: Elements of Reusable Object-Oriented Software》，书中正式定义了**工厂方法模式（Factory Method）**和**抽象工厂模式（Abstract Factory）**两种形态。简单工厂（Simple Factory）虽未被GoF收录为正式模式，但因其使用广泛，常被作为入门形态一并讲解。三者的复杂度和适用场景依次递增，构成一条清晰的学习路径。

工厂模式在实际开发中极为常见，Java标准库中的 `Calendar.getInstance()`、`NumberFormat.getInstance()` 均是工厂方法的典型应用；Spring框架的 `BeanFactory` 则是抽象工厂思想的工业级实践。理解三种工厂的区别，能帮助开发者在面对不同规模的对象创建需求时，选用复杂度最适配的方案。

---

## 核心原理

### 简单工厂（Simple Factory）

简单工厂并非GoF正式模式，但结构最直观。它由**一个工厂类**承担所有产品的创建，内部通常使用 `if-else` 或 `switch` 根据传入的类型参数决定实例化哪个具体类。

```java
class ShapeFactory {
    public static Shape create(String type) {
        if ("circle".equals(type)) return new Circle();
        if ("square".equals(type)) return new Square();
        throw new IllegalArgumentException("Unknown type");
    }
}
```

问题在于：每次新增产品（如 `Triangle`），都必须修改 `ShapeFactory` 的源代码，违反了**开闭原则（OCP）**。因此简单工厂适用于产品种类固定、数量少（通常不超过5种）的场景。

### 工厂方法模式（Factory Method）

工厂方法通过**将创建逻辑下放到子类**解决了简单工厂的扩展问题。其结构包含4个角色：
- **Product（抽象产品）**：定义产品接口
- **ConcreteProduct（具体产品）**：实现产品接口
- **Creator（抽象工厂）**：声明工厂方法 `factoryMethod()`，返回 `Product`
- **ConcreteCreator（具体工厂）**：重写 `factoryMethod()` 返回具体产品

新增一种产品只需新增一对 `ConcreteProduct + ConcreteCreator`，**无需修改已有代码**，完全遵守开闭原则。代价是类的数量随产品种类线性增长：产品种类为 *n* 时，需要 *n* 个具体工厂类 + *n* 个具体产品类，共 **2n** 个额外类。

### 抽象工厂模式（Abstract Factory）

抽象工厂处理的是**产品族**问题——多个相关产品需要协同使用，且存在多套风格（称为"产品族"）时使用。例如，UI组件库存在 `Windows风格` 和 `macOS风格` 两族，每族都包含 `Button`、`Checkbox`、`Dialog` 三种产品。

抽象工厂接口定义**一组**创建方法：

```java
interface GUIFactory {
    Button createButton();
    Checkbox createCheckbox();
    Dialog createDialog();
}
class WindowsFactory implements GUIFactory { ... }
class MacOSFactory implements GUIFactory { ... }
```

抽象工厂的关键限制：**新增产品族容易，新增产品种类困难**。若要在所有风格中追加 `TextField`，必须修改 `GUIFactory` 接口及所有具体工厂类，这与工厂方法的扩展方向恰好相反。

### 三种工厂对比总结

| 维度 | 简单工厂 | 工厂方法 | 抽象工厂 |
|------|----------|----------|----------|
| GoF收录 | 否 | 是 | 是 |
| 扩展产品种类 | 需改工厂类 | 新增子类 | 需改接口 |
| 扩展产品族 | 需改工厂类 | 不涉及 | 新增实现类 |
| 产品维度 | 单一 | 单一 | 多维 |
| 适用规模 | 小型 | 中型 | 大型 |

---

## 实际应用

**日志框架 SLF4J** 使用工厂方法模式：`LoggerFactory.getLogger(Class)` 是工厂方法，调用方只依赖 `Logger` 接口，底层可无缝切换 Logback、Log4j2 等具体实现，编译期无需任何改动。

**数据库访问层**是抽象工厂的经典场景：定义 `DbFactory` 接口包含 `createConnection()`、`createCommand()`、`createTransaction()` 三个方法，分别实现 `MySQLFactory` 和 `PostgreSQLFactory`。切换数据库时，只需替换工厂实例，业务代码中所有 `Connection`、`Command` 的创建代码均无需修改。

**游戏开发中的地图生成**：不同关卡风格（雪地、沙漠、丛林）各自是一个产品族，每族需要创建 `地形`、`敌人`、`道具` 等多种配套对象。用抽象工厂可保证同一关卡内所有元素风格统一，避免出现"雪地关卡却刷新出沙漠敌人"的逻辑错误。

---

## 常见误区

**误区一：认为工厂方法等价于"静态工厂方法"**
工厂方法模式中的 `factoryMethod()` 必须是**可被子类重写的实例方法**（通常是 `protected`），依靠多态实现扩展。而 `static` 静态方法无法被重写，本质上属于简单工厂的变体，将两者混淆会导致误以为自己在使用工厂方法模式，实际上扩展时仍需修改工厂类。

**误区二：产品维度少时强行使用抽象工厂**
如果系统只有一类产品（如只有 `Button`），即便存在多种风格，抽象工厂也退化成了工厂方法，此时引入抽象工厂接口反而增加了不必要的间接层。抽象工厂的价值在于**强制保证同族产品的一致性**，单维产品无此需求。

**误区三：认为简单工厂"不够好"应被淘汰**
产品种类固定（如支付方式仅有微信、支付宝、银行卡三种，几乎不会扩展）时，简单工厂的代码量最少、最易读。过度设计引入工厂方法会产生6个额外类却毫无收益。选择模式的依据是**变化点**，而非追求"高级"。

---

## 知识关联

学习工厂模式需要熟悉**面向接口编程**和**多态**，这是工厂方法依靠子类重写实现扩展的语言基础；同时需了解设计模式概述中的**开闭原则**，才能理解三种工厂在扩展性上的取舍逻辑。

工厂模式专注于**单步创建**一个产品对象，后续的**建造者模式（Builder）**则专注于分步骤构建一个内部结构复杂的对象——例如拥有十余个可选参数的 `HttpRequest`，用工厂方法无法优雅处理参数组合爆炸问题，这正是建造者模式登场的场景。**原型模式（Prototype）**则通过克隆已有实例来创建对象，是工厂模式之外另一条解决对象创建问题的路径，两者在创建成本高昂的对象（如深度拷贝配置对象）时可以互补使用。
