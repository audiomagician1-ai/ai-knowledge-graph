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
quality_tier: "A"
quality_score: 79.6
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

# 工厂模式

## 概述

工厂模式是一类专门处理**对象创建**问题的设计模式，其核心思想是将"使用对象"与"创建对象"的代码分离，让调用方无需知道具体类名即可获得所需对象。与直接使用 `new ClassName()` 的方式相比，工厂模式将实例化逻辑集中管理，使系统在新增产品类型时只需修改工厂，而无需修改所有调用点。

工厂模式并非单一模式，而是一个由三个层次组成的模式家族：**简单工厂（Simple Factory）**、**工厂方法（Factory Method）**和**抽象工厂（Abstract Factory）**。GoF（四人帮）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式收录了工厂方法和抽象工厂，简单工厂虽未被收录其中，但因使用频率极高而被广泛讨论。

工厂模式在框架开发中极为重要。例如，Java 的 `Calendar.getInstance()` 就是简单工厂的典型应用，它根据系统语言环境返回不同的 `Calendar` 子类实例。理解三种工厂的差异，是选择合适创建策略的基础。

---

## 核心原理

### 简单工厂：集中判断，静态分发

简单工厂通常表现为**一个静态方法**，接收一个类型标识（字符串或枚举），内部用 `if-else` 或 `switch` 决定返回哪个具体类的实例。以下是一个日志器工厂示例：

```java
public class LoggerFactory {
    public static Logger createLogger(String type) {
        switch (type) {
            case "file":   return new FileLogger();
            case "db":     return new DatabaseLogger();
            default:       throw new IllegalArgumentException("Unknown type: " + type);
        }
    }
}
```

简单工厂的致命缺陷在于**违反开闭原则（OCP）**：每新增一种 Logger 类型，都必须修改 `createLogger` 方法本身。因此，当产品类型稳定（不超过3~5种）时使用简单工厂是合理的，但产品类型频繁扩展时应升级为工厂方法。

### 工厂方法：子类决定实例化

工厂方法模式定义一个**创建对象的接口（抽象方法）**，但由子类决定具体实例化哪个类。其结构包含四个角色：抽象产品（`Logger`）、具体产品（`FileLogger`）、抽象工厂（`LoggerCreator`，含抽象方法 `createLogger()`）、具体工厂（`FileLoggerCreator`）。

```java
public abstract class LoggerCreator {
    public abstract Logger createLogger();   // 工厂方法
    public void writeLog(String msg) {
        Logger logger = createLogger();      // 依赖抽象，而非具体类
        logger.log(msg);
    }
}
public class FileLoggerCreator extends LoggerCreator {
    @Override
    public Logger createLogger() { return new FileLogger(); }
}
```

工厂方法遵循**开闭原则**：新增 `DatabaseLogger` 只需新建 `DatabaseLoggerCreator`，不修改任何已有代码。代价是类的数量随产品种类线性增长——每增加1种产品，至少增加1个具体工厂类。

### 抽象工厂：产品族的整体切换

抽象工厂处理的是**多个相互关联产品的创建**，即"产品族"问题。例如 UI 框架中，Windows 风格的 `Button + Checkbox + TextInput` 是一族，macOS 风格又是另一族。抽象工厂接口同时声明多个工厂方法：

```java
public interface UIFactory {
    Button createButton();
    Checkbox createCheckbox();
    TextInput createTextInput();
}
public class WindowsUIFactory implements UIFactory {
    public Button createButton()     { return new WindowsButton(); }
    public Checkbox createCheckbox() { return new WindowsCheckbox(); }
    public TextInput createTextInput(){ return new WindowsTextInput(); }
}
```

抽象工厂的**关键约束**是：它擅长切换整个产品族（将 `UIFactory` 实现从 `WindowsUIFactory` 换为 `MacOSUIFactory`），但若要新增一种产品类型（如 `Dialog`），则必须修改抽象接口及**所有**具体工厂实现，代价很高。这是抽象工厂固有的扩展难点。

---

## 实际应用

**Spring 框架的 BeanFactory** 是工厂方法模式的经典工程实践。`BeanFactory` 接口定义了 `getBean(String name)` 抽象方法，`XmlBeanFactory`、`AnnotationConfigApplicationContext` 等具体类分别实现不同的 Bean 实例化策略。调用方只依赖 `BeanFactory` 接口，与具体创建逻辑完全解耦。

**JDBC 的 `DriverManager.getConnection()`** 是简单工厂的真实案例：传入不同的 URL 前缀（`jdbc:mysql://` 或 `jdbc:postgresql://`），返回对应数据库驱动的 `Connection` 对象，调用方无需感知 `MySQLConnection` 或 `PostgreSQLConnection` 的存在。

**跨平台 GUI 框架**（如早期的 Java Swing Look&Feel 或 Qt 的样式系统）则是抽象工厂的教科书案例：切换主题时，只需将抽象工厂实现替换为另一个平台的具体工厂，整套组件风格同步切换，不影响任何业务逻辑代码。

---

## 常见误区

**误区1：简单工厂等于工厂方法**  
两者最本质的区别在于**扩展方式**。简单工厂通过修改已有方法添加分支来扩展；工厂方法通过新增子类来扩展。GoF 未将简单工厂列为正式模式，原因正是它无法满足开闭原则，而工厂方法可以。判断依据：若创建逻辑写在一个静态方法的 switch/if 里，就是简单工厂。

**误区2：抽象工厂只是"更大的工厂方法"**  
工厂方法解决的是**单一产品的创建族谱**问题（不同子类决定创建哪种具体产品），抽象工厂解决的是**多产品的配套创建**问题（一次性确保一组产品属于同一风格/平台）。若一个工厂接口里只有一个 `create()` 方法，它退化为工厂方法；只有当接口同时定义多个相关产品的创建方法时，才是真正的抽象工厂。

**误区3：工厂模式会增加代码量，因此适合"大项目"才用**  
工厂模式适用的判断依据是**变化点是否在对象创建上**，而非项目规模。即便是小型项目，若创建逻辑散落在业务代码各处（每处都 `new ConcreteClass()`），一旦需要替换实现（例如单元测试时替换为 Mock 对象），修改成本极高。此时引入哪怕是最简单的简单工厂，也能显著降低测试与维护成本。

---

## 知识关联

**前置概念衔接**：学习单例模式时已接触"控制实例化过程"的思想——单例通过私有构造器限制创建，工厂模式则通过专属类承接创建职责。两者都是对 `new` 操作符的封装，但单例关注"只有一个"，工厂关注"由谁来创建"。

**后续概念过渡**：**建造者模式**处理的是单个复杂对象的分步构造（例如构建含有20个可选参数的 `HttpRequest` 对象），与工厂模式的区别在于：工厂关注创建"哪种类型"，建造者关注创建"怎样的配置"。**原型模式**则通过克隆已有对象来创建新对象，当对象创建成本极高（如需要大量数据库查询初始化）时，原型模式比工厂模式更高效。三种模式在实际系统中常组合使用：工厂方法决定原型对象的类型，原型负责具体复制。