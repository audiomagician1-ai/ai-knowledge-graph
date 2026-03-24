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
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 单例模式

## 概述

单例模式（Singleton Pattern）是一种创建型设计模式，其核心约束是：一个类在整个程序运行期间只能存在唯一一个实例，并提供一个全局访问点来获取该实例。这个"唯一性"保证意味着，无论程序中多少处代码调用 `getInstance()` 方法，返回的都是同一个对象引用，内存地址完全相同。

单例模式由 GoF（Gang of Four）在 1994 年出版的《设计模式：可复用面向对象软件的基础》中正式定义。GoF 将其列为 23 种经典设计模式中的创建型模式，书中给出的原始结构包含一个私有静态成员变量保存实例、一个私有构造函数防止外部实例化，以及一个公有静态方法 `getInstance()` 提供访问入口。

单例模式在实践中常用于管理共享资源，例如数据库连接池、日志记录器、配置文件读取器等场景。这些组件若被反复创建，会带来内存浪费或状态不一致问题。以 Java 中的 `java.lang.Runtime` 类为例，JDK 将其设计为单例，保证每个 JVM 进程只有一个运行时环境对象可操作系统资源。

---

## 核心原理

### 基本结构与私有构造函数

单例模式的实现依赖三个关键要素。第一，将构造函数声明为 `private`，使外部代码无法通过 `new` 关键字创建实例。第二，在类内部声明一个 `private static` 类型的成员变量，用于持有唯一实例的引用。第三，提供 `public static getInstance()` 方法作为唯一入口。以下是最基础的"懒汉式"实现：

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

这段代码在单线程环境下正确，但在多线程环境下，两个线程同时通过 `if (instance == null)` 检查时，会各自创建一个实例，破坏唯一性。

### 线程安全的双重检查锁定（DCL）

解决多线程问题最常用的方案是**双重检查锁定（Double-Checked Locking，DCL）**。DCL 在第一次 `null` 检查后加入 `synchronized` 同步块，同步块内再做第二次检查，避免每次调用都争抢锁带来的性能损耗：

```java
public class Singleton {
    private volatile static Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

`volatile` 关键字在此处不可缺少。`instance = new Singleton()` 在 JVM 层面分为三步：①分配内存 ②初始化对象 ③将引用赋给 `instance`。JVM 可能将步骤②③重排序，导致另一个线程拿到一个尚未初始化完毕的对象。`volatile` 禁止了这种指令重排序，保证可见性与有序性。这个问题在 Java 1.5 之前的内存模型中实际存在，Java 5 修订 JSR-133 后 `volatile` + DCL 才真正安全。

### 饿汉式与静态内部类实现

**饿汉式**在类加载时立即创建实例，利用 JVM 的类加载机制保证线程安全：

```java
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();
    private Singleton() {}
    public static Singleton getInstance() { return INSTANCE; }
}
```

缺点是无论是否使用，实例在程序启动时就占用内存。

**静态内部类（Initialization-on-demand Holder）** 是兼顾懒加载与线程安全的最优雅方案：

```java
public class Singleton {
    private Singleton() {}
    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }
    public static Singleton getInstance() { return Holder.INSTANCE; }
}
```

`Holder` 类只有在第一次调用 `getInstance()` 时才被 JVM 加载，JVM 的类初始化过程由类加载锁保证线程安全，且无需手动同步。这是 Joshua Bloch 在《Effective Java》第三版 Item 83 中推荐的实现方式。

### 枚举单例

Java 中最简洁且抵御反序列化攻击的单例实现是枚举：

```java
public enum Singleton {
    INSTANCE;
    public void doSomething() { /* ... */ }
}
```

枚举由 JVM 保证每个枚举值只实例化一次，且天然防止通过反射或反序列化创建新实例——这两点是前几种实现方式难以同时满足的。《Effective Java》将此方法列为"实现单例的最佳方式"。

---

## 实际应用

**日志系统**：Log4j 的 `LogManager` 采用单例管理所有 Logger 的注册表，确保同一个 Logger 名称全局只对应一个实例，避免日志配置被覆盖。

**线程池**：Android 系统中 `Looper.getMainLooper()` 返回主线程的唯一 Looper 对象，通过静态成员变量 `sMainLooper` 持有引用，保证 UI 线程消息队列的唯一性。

**配置管理器**：Spring 框架中默认的 Bean 作用域（scope）就是 `singleton`，即每个 Spring 容器中一个 Bean 定义只对应一个实例。Spring 使用 `DefaultSingletonBeanRegistry` 中的 `ConcurrentHashMap<String, Object>` 作为单例注册表来缓存实例。

---

## 常见误区

**误区一：认为 synchronized 修饰 getInstance() 方法足够高效**。直接在方法签名上加 `synchronized` 确实线程安全，但每次调用都要竞争类锁，高并发场景下性能开销显著。DCL 或静态内部类方案只在首次初始化时有同步开销，后续调用无锁，性能差距可达数十倍。

**误区二：忽视反序列化破坏单例**。实现了 `Serializable` 接口的单例类，在反序列化时会调用 `ObjectInputStream.readObject()` 创建新实例，绕过私有构造函数。解决办法是在单例类中添加 `readResolve()` 方法并返回 `INSTANCE`，或直接使用枚举单例。

**误区三：在多 ClassLoader 环境中误以为唯一性仍然成立**。单例的"唯一"是相对于同一个 ClassLoader 而言的。在 Tomcat 等容器中，每个 Web 应用拥有独立的 ClassLoader，同一个单例类会被加载多次，产生多个互相独立的"单例"实例。这在分布式系统中尤为值得注意。

---

## 知识关联

学习单例模式需要具备**设计模式概述**的背景知识，理解创建型模式与结构型、行为型模式的分类依据，以及 GoF 模式描述语言中"意图、适用性、结构"等标准元素的含义。

单例模式是工厂模式、抽象工厂模式等创建型模式的对比参照：工厂方法每次调用可返回不同实例，而单例严格限定为一个。掌握单例后，可进一步学习**多例模式（Multiton Pattern）**——它将对象数量从严格的 1 扩展到由键值映射管理的有限集合，是单例的自然推广。同时，单例模式中的线程安全技巧（`volatile`、DCL、类加载锁）为学习 Java 并发编程中的**不可变对象**与**安全发布（Safe Publication）**概念奠定了实践基础。
