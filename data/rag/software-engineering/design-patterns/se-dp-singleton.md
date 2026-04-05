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
content_version: 4
quality_tier: "S"
quality_score: 82.9
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

# 单例模式

## 概述

单例模式（Singleton Pattern）是一种创建型设计模式，其核心约束是：**一个类在整个程序生命周期内只能存在唯一一个实例**，并且提供一个全局访问点来获取该实例。这一约束通过将构造函数声明为私有（`private`）来强制实现——外部代码无法直接调用 `new` 关键字创建对象，只能通过类自身提供的静态方法（通常命名为 `getInstance()`）获取实例。

单例模式最早在1994年由 Gang of Four（GoF）在《Design Patterns: Elements of Reusable Object-Oriented Software》一书中正式收录，被归类为创建型模式。它解决的问题是：某些资源（如配置管理器、数据库连接池、日志记录器）若允许多个实例并存，会导致状态不一致或资源浪费。例如，若应用中存在两个数据库连接池实例，线程可能从不同池获取连接，造成事务管理混乱。

单例模式的重要性在于它是线程安全与延迟初始化两个目标之间的经典博弈场景。正确实现单例需要处理多线程竞态条件，这使它成为考察开发者对 Java 内存模型（JMM）或 C++ 对象模型理解深度的常见面试题目。

---

## 核心原理

### 基础结构：私有构造 + 静态实例

单例模式的最简实现（饿汉式）如下：

```java
public class Singleton {
    private static final Singleton INSTANCE = new Singleton(); // 类加载时即创建
    private Singleton() {}  // 禁止外部 new
    public static Singleton getInstance() { return INSTANCE; }
}
```

饿汉式在类加载阶段由 JVM 的类加载器保证线程安全，无需额外同步，但无论是否用到该实例，都会在程序启动时占用内存。若实例化开销较大（如加载 100MB 配置文件），这会显著拖慢启动速度。

### 懒汉式与双重检查锁定（DCL）

延迟初始化（懒汉式）将实例创建推迟到第一次调用时，但在多线程环境下必须使用**双重检查锁定（Double-Checked Locking, DCL）**：

```java
public class Singleton {
    private static volatile Singleton instance; // volatile 是关键
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {              // 第一次检查（无锁）
            synchronized (Singleton.class) {
                if (instance == null) {      // 第二次检查（有锁）
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

`volatile` 关键字此处缺一不可。`new Singleton()` 在字节码层面分为三步：①分配内存、②调用构造函数初始化、③将引用赋给 `instance`。JVM 可能对步骤②③重排序，导致另一个线程看到一个非 null 但未完成初始化的实例。`volatile` 通过禁止指令重排序（happens-before 语义）消除这一风险。若省略 `volatile`，DCL 在 Java 1.5 之前的 JVM 上是有已知 bug 的。

### 静态内部类：兼顾延迟加载与线程安全的优雅方案

```java
public class Singleton {
    private Singleton() {}
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    public static Singleton getInstance() { return Holder.INSTANCE; }
}
```

`Holder` 类只在 `getInstance()` 首次被调用时才会被 JVM 加载，此时类初始化由 JVM 的类加载锁（Class Loading Lock）保证原子性，无需 `synchronized` 或 `volatile`。这是 Java 中单例实现的**推荐方案**，代码量最少，性能最佳。

### 枚举单例：防止反射与反序列化破坏

```java
public enum Singleton {
    INSTANCE;
    public void doSomething() { ... }
}
```

Joshua Bloch 在《Effective Java》第3版第3条中明确推荐枚举单例。它天然防止两种单例"破坏"：①通过 `Constructor.setAccessible(true)` 反射调用私有构造函数（枚举的构造函数在 JVM 层面被禁止反射调用）；②对象反序列化时 `readObject()` 会创建新实例（枚举的反序列化由 JVM 保证返回同一常量）。

---

## 实际应用

**配置中心**：Spring 框架中 `ApplicationContext` 默认以单例作用域（`@Scope("singleton")`）管理 Bean，整个容器中同一 Bean 定义只有一个实例，这正是单例模式的框架级应用。

**日志记录器**：`java.util.logging.Logger` 的 `getLogger(name)` 方法维护一个以 logger 名称为键的内部 Map，确保同名 logger 返回同一实例，避免日志输出重复或丢失。

**线程池管理**：Android 开发中，`Glide.with(context)` 内部通过单例维护全局 `RequestManagerRetriever`，确保图片缓存状态全局一致，防止因多实例导致缓存命中率下降。

**数据库连接池**：HikariCP 连接池在应用中通常以单例形式持有，一个 `HikariDataSource` 实例管理固定数量（如默认最大10个）的数据库连接，若允许多实例，连接总数将超出数据库服务器的承受上限。

---

## 常见误区

**误区一：懒汉式只加一个 `synchronized` 就够了**
很多初学者写出 `public static synchronized Singleton getInstance()`，这确实线程安全，但每次调用 `getInstance()` 都需要获取锁，在高并发场景下（如每秒数万次调用日志单例）性能急剧下降。DCL 方案将同步块缩小到"仅首次创建时"，99.9% 的调用走无锁路径，性能差异可达数十倍。

**误区二：单例模式等于全局变量，应当尽量避免**
单例确实共享了全局状态，但它与全局变量的区别在于：单例封装了实例化逻辑、可以延迟初始化、支持继承和多态（可通过子类替换实现）。正确的认识是：**无状态或只读状态的单例**（如工具类、配置读取器）风险极低；**持有可变状态的单例**（如全局计数器）在多线程下需额外同步，应谨慎使用。

**误区三：单元测试中单例天然可用**
由于单例在 JVM 中持续存在，一个测试用例修改了单例状态后，可能污染后续测试。解决方案是：①为单例提供 `resetForTesting()` 方法（仅测试代码调用）；②通过依赖注入（DI）将单例作为接口注入，测试时注入 Mock 对象，这也是 Spring 推荐的做法。

---

## 知识关联

**前置概念**：学习单例模式前需理解设计模式中"创建型模式"的分类意图——创建型模式关注对象实例化过程的控制，单例是其中约束最强的一种（限定为1个实例）。

**与工厂模式的关系**：工厂模式（Factory Pattern）通常自身以单例实现。例如，`ConnectionFactory` 作为单例存在，同时负责创建多个 `Connection` 对象。单例控制"工厂自身只有一个"，工厂模式控制"如何创建产品对象"，两者职责互补，常在同一代码库中协作出现。

**与依赖注入的关系**：现代框架（Spring、Guice）用依赖注入容器替代手写单例，容器默认以单例作用域管理对象，但通过配置可改为原型（每次新建）。手写单例因难以替换实现而不利于测试，DI 容器解决了这一问题，是单例思想的工程化演进。