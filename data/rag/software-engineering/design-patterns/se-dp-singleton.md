---
id: "se-dp-singleton"
concept: "单例模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["创建型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 单例模式

## 概述

单例模式（Singleton Pattern）是一种创建型设计模式，其核心约束是：**一个类在整个程序运行期间只能存在一个实例**，并提供一个全局访问点来获取该实例。它由 GoF（Gang of Four）在 1994 年出版的《Design Patterns: Elements of Reusable Object-Oriented Software》中正式归纳，是书中 23 种设计模式里最简单也最容易被误用的一种。

单例模式的诞生源于对"共享资源管理"问题的抽象。典型场景包括：操作系统的打印队列管理器、数据库连接池、应用程序日志记录器。这些对象如果存在多份实例，要么造成资源浪费，要么引发数据不一致。单例模式通过将构造函数设为私有（`private`），强制外部代码只能通过统一的静态方法获取实例，从语言层面封堵了意外创建多个实例的可能。

---

## 核心原理

### 基础结构：三个必要条件

实现单例模式必须满足三点：
1. **私有构造函数**：防止外部通过 `new` 创建实例
2. **静态私有实例变量**：存储唯一实例
3. **静态公有访问方法**（通常命名为 `getInstance()`）：返回该唯一实例

以 Java 为例，最朴素的实现（懒汉式）如下：
```java
public class Singleton {
    private static Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```
然而这段代码**在多线程环境下是不安全的**——两个线程可能同时通过 `instance == null` 检查，各自创建一个实例。

---

### 线程安全实现：双重检查锁定（DCL）

双重检查锁定（Double-Checked Locking，DCL）是解决单例多线程安全问题的经典方案：

```java
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {                    // 第一次检查
            synchronized (Singleton.class) {
                if (instance == null) {            // 第二次检查
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

此处 `volatile` 关键字**不可省略**。原因在于 `instance = new Singleton()` 在字节码层面分为三步：①分配内存 ②初始化对象 ③将引用赋给 `instance`。JVM 指令重排可能使步骤③先于步骤②执行，导致另一个线程拿到一个**未完成初始化的实例**。`volatile` 通过禁止指令重排序解决了这一问题。DCL 方案在 Java 5 之后才完全可靠，因为 Java 5 才对 `volatile` 的内存语义做出了规范增强。

---

### 最优实现：静态内部类与枚举

**静态内部类方式**利用 JVM 类加载机制天然保证线程安全：
```java
public class Singleton {
    private Singleton() {}
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```
`Holder` 类只在第一次调用 `getInstance()` 时才被加载，JVM 的类加载过程本身是线程安全的，因此无需任何同步代码。

**枚举方式**由 Joshua Bloch 在《Effective Java》第二版（2008年）中推荐，是 Java 平台上**最简洁且防反射攻击**的单例实现：
```java
public enum Singleton {
    INSTANCE;
    public void doSomething() { ... }
}
```
枚举类型的反序列化不会创建新实例，且枚举构造函数天然对反射调用抛出 `IllegalArgumentException`，而普通单例如果不额外处理，可通过 `Constructor.setAccessible(true)` 被反射破坏。

---

## 实际应用

**Spring 框架的 Bean 默认作用域**就是单例。Spring 容器通过 `DefaultSingletonBeanRegistry` 内部维护一个 `Map<String, Object>` 存储所有单例 Bean，当你声明 `@Service` 或 `@Component` 时，默认即为单例作用域（`scope="singleton"`），整个 `ApplicationContext` 生命周期内只有一个实例。

**日志框架 Log4j/SLF4J** 中的 `LogManager` 使用单例模式管理全局日志配置。应用程序任意位置通过 `LogManager.getLogger(ClassName.class)` 获取的 `Logger` 工厂，均来自同一个管理器实例，确保日志配置的统一性。

**Android 开发**中，`Application` 类本身由系统保证全局唯一，但开发者通常额外为数据库访问对象（如 Room 的 `RoomDatabase`）实现单例，防止多个数据库连接对象同时存在引发 `SQLiteDatabaseLockedException`。

---

## 常见误区

**误区一：认为单例模式"天生"线程安全**。懒汉式（延迟初始化）的单例在没有同步措施时完全不是线程安全的。饿汉式（类加载时直接初始化静态变量）是线程安全的，但如果初始化代价很高且未必用到，会造成资源浪费。不同实现方式的线程安全保证机制不同，不可混淆。

**误区二：单例模式是全局变量的"高级替代品"**。单例模式强调"唯一实例"语义，同时封装了实例的创建逻辑；全局变量只是全局可访问，没有任何创建控制。然而单例模式确实带来了全局状态，这使得依赖单例的类难以进行单元测试（无法轻易替换实例），这也是业界建议在可以使用依赖注入的场合**优先用 DI 容器管理单例**，而非手写单例类的原因。

**误区三：序列化与反射不会破坏单例**。对于普通 Java 类实现的单例，执行反序列化会调用 `readResolve` 机制，若未重写 `readResolve()` 方法，将创建一个全新实例，破坏唯一性。使用枚举实现或在类中显式声明 `protected Object readResolve() { return INSTANCE; }` 才能防止此问题。

---

## 知识关联

单例模式建立在**设计模式概述**所介绍的"创建型模式"分类之上，是理解其他创建型模式（如工厂方法、抽象工厂）的对照基准——工厂模式解决"如何创建对象"，单例模式解决"限制创建对象的数量为一"。

在并发编程中，DCL 实现直接关联 Java 内存模型（JMM）中的 `happens-before` 规则和 `volatile` 语义，理解单例的线程安全实现有助于深入掌握 JMM 中可见性与有序性的保证机制。

单例模式的滥用会导致代码紧耦合和测试困难，这推动了**依赖注入（Dependency Injection）**模式的广泛使用。Spring、Guice 等 DI 框架本质上将单例的生命周期管理从业务代码中剥离出来，由容器统一控制，既保留了"唯一实例"的语义，又保持了类的可测试性。
