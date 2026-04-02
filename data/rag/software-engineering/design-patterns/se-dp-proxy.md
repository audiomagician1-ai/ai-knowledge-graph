---
id: "se-dp-proxy"
concept: "代理模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["结构型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 代理模式

## 概述

代理模式（Proxy Pattern）是一种结构型设计模式，通过引入一个代理对象来控制对另一个对象（真实主体）的访问。代理对象与真实主体实现相同的接口，使得客户端无需感知自己是在与代理还是真实对象交互。这种"中间层"机制允许在不修改原始类的前提下，附加访问控制、远程通信封装、延迟初始化等附加行为。

代理模式最早在1994年由GoF（Gang of Four）在《Design Patterns: Elements of Reusable Object-Oriented Software》中正式归类，书中列出了远程代理、虚拟代理、保护代理和智能引用四种子类型。该模式在早期分布式系统中随RPC（远程过程调用）技术的普及而广泛应用，Java的RMI（Remote Method Invocation）中的Stub对象即是远程代理的经典实现。

代理模式在现代软件工程中仍然高频出现：Spring AOP使用动态代理（JDK Proxy或CGLIB）实现事务管理和日志切面，Hibernate使用虚拟代理实现数据库查询的懒加载，Android的Binder机制是跨进程通信的保护代理实践。理解代理模式不仅是读懂主流框架源码的钥匙，也是手写中间件的基础技能。

---

## 核心原理

### 代理模式的基本结构

代理模式包含三个角色：**Subject（抽象主题）**定义真实主体和代理共同遵守的接口；**RealSubject（真实主体）**包含核心业务逻辑；**Proxy（代理）**持有一个指向 RealSubject 的引用，在转发请求前后可以插入任意附加逻辑。

```
Client ──→ Subject (interface)
              ↑           ↑
           Proxy ──持有── RealSubject
```

代理类的核心实现是：自身实现与 RealSubject 相同的接口，同时在方法内部通过 `realSubject.method()` 委托真实对象完成实际工作。与装饰器模式不同，代理通常**自行控制 RealSubject 的生命周期**（包括何时创建、是否允许访问），而装饰器的被装饰对象由外部传入。

### 三种典型子类型

**远程代理（Remote Proxy）**：本地代理对象封装了网络通信细节，客户端调用本地方法时，代理将请求序列化后通过网络发送到远端真实主体，再将响应结果反序列化返回。Java RMI 中，`rmiregistry` 注册的 Stub 对象就是典型的远程代理，调用 `stub.add(1, 2)` 时客户端代码无需感知任何 socket 操作。

**虚拟代理（Virtual Proxy）与懒加载**：真实主体的创建代价极高时（如加载一张 8MB 的高清图片），虚拟代理在对象真正被访问前推迟其初始化。代理内部维护一个 `private RealSubject instance = null;` 的字段，仅在首次调用 `request()` 时才执行 `instance = new RealSubject()`，这就是懒加载（Lazy Initialization）。Office 文档在打开时先用占位代理替换所有图片，滚动到可视区域才加载真实图像，正是此模式的直接体现。

**保护代理（Protection Proxy）**：代理在转发请求前检查调用方是否具备权限。例如：

```java
public void deleteRecord(User user, int recordId) {
    if (!user.hasRole("ADMIN")) {
        throw new AccessDeniedException("仅管理员可删除记录");
    }
    realSubject.deleteRecord(recordId);
}
```

Spring Security 的方法级注解 `@PreAuthorize("hasRole('ADMIN')")` 底层正是通过动态代理注入此类权限检查逻辑，而无需在业务类中编写任何安全代码。

### 静态代理与动态代理

**静态代理**在编译期生成代理类，需要为每个 RealSubject 手写一个对应的 Proxy 类，接口方法数量翻倍增加维护成本。**动态代理**在运行时通过反射生成代理类：Java `java.lang.reflect.Proxy` 要求 RealSubject 必须实现接口，代理逻辑写在 `InvocationHandler.invoke()` 中；CGLIB 则通过继承机制对无接口的类生成子类代理，`Enhancer.create()` 是其入口。动态代理使得一个 `InvocationHandler` 可以拦截任意接口的所有方法，这是 Spring AOP 能以极少代码实现横切关注点的技术基础。

---

## 实际应用

**MyBatis Mapper接口**：MyBatis 中的 Mapper 接口（如 `UserMapper`）没有实现类，框架在运行时通过 JDK 动态代理生成代理对象。调用 `userMapper.findById(1)` 时，`MapperProxy.invoke()` 方法解析方法名和注解，拼装 SQL 并执行，这使得开发者只需定义接口而无需写任何 JDBC 代码。

**图片懒加载组件**：Web 前端的 `IntersectionObserver` + 占位图的方案，本质是虚拟代理思想在 JavaScript 中的应用：DOM 中先插入低分辨率的占位元素（代理），当元素进入视口时才替换为真实的高清图片 URL 并触发网络请求。

**操作系统的写时复制（Copy-on-Write）**：Linux `fork()` 后父子进程共享同一内存页，操作系统通过一个内存页的代理机制将其标记为只读；只有当某个进程尝试写入时，才真正复制该内存页并更新映射。这是虚拟代理懒加载思想在操作系统层面的实现。

---

## 常见误区

**误区一：代理模式与装饰器模式可以互换使用**。二者结构极为相似，都持有与自身同接口的对象引用，但目的截然不同。装饰器用于**动态叠加功能**（如给 InputStream 加缓冲、加加密，可以多层嵌套），被装饰对象由调用方传入；代理用于**控制对象访问**（权限、远程、延迟），代理通常在内部决定是否以及何时创建真实主体，客户端不应持有也不必传入 RealSubject 实例。混淆两者会导致设计职责模糊，例如将业务权限检查逻辑错误地实现成装饰器链。

**误区二：虚拟代理的懒加载与缓存是同一回事**。懒加载关注的是**首次访问时才创建对象**，解决的是初始化时机问题，对象创建后代理每次仍可能重新访问真实主体。缓存关注的是**将已计算的结果存储以避免重复计算**，是性能优化策略。虚拟代理中通常结合这两者：首次访问创建并缓存 RealSubject（`if (instance == null) instance = new RealSubject()`），但这是两个独立概念，在多线程场景下懒加载还需要 `synchronized` 或 `double-checked locking` 保证线程安全，而单纯的缓存则不一定涉及对象创建同步。

**误区三：动态代理一定比静态代理性能差**。早期 JDK 反射较慢，动态代理确实有性能损耗。但 JDK 8+ 对反射做了大量优化，且 CGLIB 生成的字节码与静态代理性能几乎持平。实际上，对于方法调用频率极高（>10⁷次/秒）的热点路径才需要考虑此差异，绝大多数业务系统的代理开销完全可以忽略。

---

## 知识关联

**与装饰器模式的关系**：学习过装饰器模式后，可以将代理模式理解为"目的受限的装饰器"——装饰器对被装饰对象的内容一无所知且不加干涉，而代理主动管理真实主体的访问权和生命周期。两者代码结构高度相似，区分它们的关键在于：谁控制 RealSubject 的实例化，以及附加行为的目的是增强功能还是控制访问。

**通往外观模式的路径**：外观模式同样是在客户端与复杂子系统之间引入中间层，但外观封装的是**多个不同类**组成的子系统（对客户端隐藏复杂度），而代理封装的是**单一真实主体**（控制对这一个对象的访问）。理解代理模式中"单一对象的受控访问"之后，外观模式的"多对象的统一入口"便是自然的扩展方向。两者都体现了"封装变化点，降低客户端耦合"的结构型模式核心思路。