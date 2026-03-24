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
---
# 代理模式

## 概述

代理模式（Proxy Pattern）是一种结构型设计模式，通过引入一个代理对象来控制对真实对象（RealSubject）的访问。代理对象与真实对象实现相同的接口，客户端无需知道它交互的究竟是代理还是真实对象。代理在转发请求前后可以执行额外操作，例如延迟初始化、权限验证或远程通信。

该模式最早由四人组（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式定义。代理模式与装饰器模式在结构上高度相似——两者都持有被包装对象的引用——但目的截然不同：装饰器用于动态添加职责，代理用于控制访问。代理模式关注的是"是否访问"和"如何访问"，而不是"访问时额外做什么"。

代理模式在现代软件开发中解决的核心痛点是：真实对象可能创建代价高昂、位于远程服务器、或需要受到访问限制，直接暴露真实对象会带来性能、安全或架构问题。

## 核心原理

### 角色结构与类图

代理模式包含三个固定角色：

- **Subject（抽象主题）**：定义代理与真实对象共同遵循的接口，通常是一个接口或抽象类，包含 `request()` 方法。
- **RealSubject（真实主题）**：实现真正业务逻辑的对象，是代理最终要访问的目标。
- **Proxy（代理）**：持有一个 `RealSubject` 类型的引用，实现 `Subject` 接口，在调用 `realSubject.request()` 前后添加控制逻辑。

```
Subject (interface)
    ↑               ↑
RealSubject       Proxy ──持有──→ RealSubject
```

代理的核心结构可以用以下伪代码表示：

```java
class Proxy implements Subject {
    private RealSubject realSubject; // 延迟初始化

    public void request() {
        if (realSubject == null) {
            realSubject = new RealSubject(); // 懒加载
        }
        // 前置控制逻辑
        realSubject.request();
        // 后置控制逻辑
    }
}
```

### 三种主要代理类型

**虚拟代理（Virtual Proxy）**：用于延迟创建开销极大的对象，即"懒加载"。典型场景是图像查看器：用户打开包含100张高清图片的文档时，虚拟代理先显示占位符，只有当用户滚动到某张图片时才真正加载该图片对象。`ImageProxy` 在 `display()` 被首次调用时才执行 `new HighResolutionImage(filename)` 构造真实对象。

**远程代理（Remote Proxy）**：为位于不同地址空间（通常是另一台服务器）的对象提供本地代表。Java RMI（远程方法调用）和 gRPC 的客户端存根（Stub）就是远程代理的典型实现——本地调用 `stub.getPrice()` 实际上通过网络序列化参数、发送请求、反序列化响应，但调用方无需关心这一切细节。

**保护代理（Protection Proxy）**：在转发请求之前检查调用者是否有权限。例如，文件系统代理会在 `read()`、`write()`、`delete()` 调用前验证当前用户的访问级别（如只读 vs 管理员），而不修改 `RealFile` 类本身的任何代码。

### 懒加载机制

懒加载（Lazy Initialization）是虚拟代理最重要的特性，遵循"按需创建"原则。其成本收益关系可以用以下方式衡量：

> 若真实对象创建时间为 T，使用概率为 P（0 < P < 1），则期望创建成本从 T 降低到 P×T。

当 P 远小于1时（例如用户通常只查看文档中前几张图片），懒加载带来显著性能提升。Java 的 `Hibernate` ORM 框架大量使用虚拟代理实现懒加载关联对象——查询 `Order` 实体时，其关联的 `OrderItems` 集合默认不立即从数据库加载，直到代码真正访问该集合属性。

## 实际应用

**Spring AOP 的动态代理**：Spring 框架的面向切面编程在运行时动态生成代理类。当 `@Transactional` 注解标注的方法被调用时，Spring 生成的代理对象在方法执行前开启事务、执行后提交或回滚，真实的业务 Bean 完全感知不到事务逻辑。Spring 优先使用 JDK 动态代理（要求目标类实现接口），否则使用 CGLib 字节码代理。

**浏览器中的图片懒加载**：HTML 的 `loading="lazy"` 属性背后体现了虚拟代理思想——浏览器用轻量占位符替代真实图片，仅在元素进入视口时才发起网络请求加载真实图片资源。

**API 网关作为远程代理**：微服务架构中的 API 网关充当所有下游服务的远程代理，客户端只与网关交互，网关负责路由、负载均衡、SSL 终止和认证，对外暴露统一接口，对内转发至真实微服务实例。

**Windows COM 中的代理/存根**：Windows COM 组件对象模型在跨进程调用时自动生成代理（Proxy）和存根（Stub），调用方进程持有的 COM 接口指针实际上指向一个进程外代理对象，完全实现了透明的跨进程通信。

## 常见误区

**误区一：将代理模式与装饰器模式混淆**。两者结构相同，区别在于意图：代理模式中代理类通常自行管理 RealSubject 的生命周期（例如负责创建它），客户端不直接持有 RealSubject；装饰器模式中被装饰对象由客户端创建后传入装饰器，客户端可以选择使用原对象或装饰后的对象。代理隐藏真实对象，装饰器增强真实对象。

**误区二：认为代理一定会降低性能**。保护代理和虚拟代理的引入确实增加了一层函数调用，但虚拟代理通过延迟创建昂贵对象通常能大幅提升整体性能。远程代理的性能瓶颈来自网络 I/O，而非代理模式本身。关键在于：代理引入的固定开销是纳秒级方法调用，而其节省的成本可能是数百毫秒的对象初始化或网络往返时间。

**误区三：认为代理必须在编译时静态生成**。Java 的 `java.lang.reflect.Proxy` 类支持在运行时通过 `Proxy.newProxyInstance()` 动态创建代理对象，只需提供 `InvocationHandler` 实现。这意味着同一个 `InvocationHandler` 可以代理实现了不同接口的多种对象，是 AOP、RPC 框架的核心实现机制，而非设计模式本身的限制。

## 知识关联

**与装饰器模式的关系**：学习代理模式需要先理解装饰器模式，因为两者使用完全相同的类结构（包装对象 + 相同接口）。区分两者的关键在于：装饰器在运行时为对象新增行为，代理在运行时控制对对象的访问。同一个"持有引用 + 转发调用"的结构，赋予不同意图，就分别成为了装饰器和代理。

**对后续概念的支撑**：代理模式是理解 AOP（面向切面编程）的直接前提——AOP 的拦截器本质上就是系统级的动态代理，将横切关注点（日志、事务、安全）从业务代码中分离。此外，理解远程代理有助于深入掌握 RPC 框架（如 Dubbo、gRPC）的客户端存根设计，以及服务网格（Service Mesh）中 Sidecar 代理模式的架构意图。
