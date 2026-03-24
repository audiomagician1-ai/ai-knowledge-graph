---
id: "proxy-pattern"
concept: "代理模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 4
is_milestone: false
tags: ["proxy", "lazy-loading", "design-pattern"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 代理模式

## 概述

代理模式（Proxy Pattern）是一种结构型设计模式，其核心机制是创建一个与原始对象实现相同接口的代理类，客户端通过调用代理对象来间接访问真实对象（Real Subject），从而在不修改真实对象代码的前提下，在访问路径上插入额外的控制逻辑。代理对象持有对真实对象的引用，并决定是否、何时以及如何将请求转发给真实对象。

代理模式最早由 Gang of Four（GoF）在1994年的著作《Design Patterns: Elements of Reusable Object-Oriented Software》中正式收录，书中将其归类为结构型模式（Structural Pattern）。历史上，代理模式的雏形出现在分布式计算领域：CORBA（Common Object Request Broker Architecture）中的 Stub/Skeleton 机制就是一种远程代理的早期实现，客户端持有的 Stub 对象透明地代理了跨网络的方法调用。

在 AI 工程领域中，代理模式具有特殊价值。大型语言模型（LLM）的推理调用成本高昂，使用缓存代理可以拦截重复的 Prompt 请求，避免每次都触发实际的模型推理；同时，在多智能体系统（Multi-Agent System）中，"Agent"本身的命名就部分借鉴了代理模式的思想——一个 Agent 代理人类用户对工具和环境进行受控访问。

---

## 核心原理

### UML 结构与角色分工

代理模式的标准 UML 结构包含三个角色：

- **Subject（抽象主题）**：定义真实对象和代理对象共同实现的接口，使代理可以无缝替换真实对象。
- **RealSubject（真实主题）**：实现 Subject 接口，包含实际的业务逻辑。
- **Proxy（代理）**：同样实现 Subject 接口，内部持有 `RealSubject` 的引用，在调用 `RealSubject` 的方法前后可以执行附加操作。

Python 示例结构如下：

```python
class Subject:
    def request(self): pass

class RealSubject(Subject):
    def request(self):
        return "真实对象处理请求"

class Proxy(Subject):
    def __init__(self):
        self._real_subject = None  # 延迟初始化

    def request(self):
        if self._real_subject is None:
            self._real_subject = RealSubject()
        # 访问控制或日志等附加逻辑
        return self._real_subject.request()
```

### 四种经典代理类型

**虚拟代理（Virtual Proxy）**：延迟创建开销巨大的对象，直到真正需要时才实例化。在 AI 工程中，加载一个 7B 参数量的本地语言模型需要数秒和数 GB 内存，虚拟代理可以推迟 `model.load()` 的调用时机，仅在首次真正推理时才触发加载。

**保护代理（Protection Proxy）**：在转发请求前检查调用方的权限。例如，对同一个 LLM 接口，VIP 用户代理允许访问 GPT-4，而普通用户代理自动将请求路由到 GPT-3.5，访问控制逻辑封装在代理内部，真实模型对象无需感知权限差异。

**远程代理（Remote Proxy）**：为位于不同地址空间的对象提供本地代表。Python 的 `xmlrpc.client` 模块自动生成的客户端对象即是远程代理，调用其方法时自动序列化参数、发起 HTTP 请求并反序列化结果。

**缓存代理（Caching Proxy）**：存储昂贵操作的结果并在重复请求时返回缓存值。对 LLM API 的调用中，相同 Prompt 的缓存代理可将 Token 消耗降至零，OpenAI 官方的 Prompt Caching 功能本质上就是在服务端实现了这一代理语义。

### 代理的转发决策逻辑

代理的核心控制点是 `request()` 方法中的转发条件，其通用形式为：

```
代理行为 = 前置处理(pre-processing) → [条件判断] → 转发/拦截 → 后置处理(post-processing)
```

代理可以选择：①完全透明转发；②修改参数后转发；③拦截请求并返回缓存/默认值；④抛出异常拒绝访问。这四种选择共同构成了代理在访问控制上的完整语义空间。

---

## 实际应用

### AI 工程中的模型访问代理

在构建 AI 应用时，直接在业务代码中调用 `openai.ChatCompletion.create()` 会导致重试逻辑、限流处理、成本记录等横切关注点散落各处。使用代理模式，可以创建一个 `LLMProxy` 类实现与真实客户端相同的 `chat()` 接口，在内部集中实现：指数退避重试（如最多重试3次，间隔 2^n 秒）、每次调用的 Token 用量记录、以及基于 MD5 哈希 Prompt 的本地缓存查询。业务层只持有 `LLMProxy` 对象，无需感知这些基础设施细节。

### 延迟加载嵌入模型

Sentence Transformers 等嵌入模型在 `import` 后仍需数秒进行模型权重加载。在 RAG 系统中，使用虚拟代理包装 `SentenceTransformer("all-MiniLM-L6-v2")`，可以在服务启动时仅创建代理对象而不加载384维权重，首次调用 `encode()` 时才触发实际加载，使服务启动时间从约8秒降低到不足1秒。

### Django REST Framework 中的权限代理

`django-guardian` 库通过对象级权限代理，在每个对象的访问请求到达 View 之前，由代理层查询 `UserObjectPermission` 表并决定是否放行，实现了比 Model 级权限粒度更细的保护代理机制。

---

## 常见误区

**误区一：将代理模式等同于装饰器模式**

两者都使用组合并实现相同接口，但意图根本不同：装饰器模式的目的是**增强**被包装对象的功能，通常可以叠加多个装饰器，且被装饰对象由客户端显式传入；而代理模式的目的是**控制访问**，代理通常自行管理真实对象的生命周期（如虚拟代理的延迟初始化），客户端无需知道真实对象的存在。Python 的 `functools.lru_cache` 在接口上像装饰器，但其缓存访问拦截语义使其本质上属于缓存代理。

**误区二：认为代理必须完全透明**

实际上，保护代理可以合法地拒绝请求或返回不同结果，缓存代理返回的是历史结果而非实时计算值。"透明"仅指接口层面（实现相同接口），并不意味着行为必须与真实对象完全一致。混淆这一点会导致开发者在保护代理中为了"保持透明"而放弃必要的访问拒绝逻辑。

**误区三：将代理模式与 Python `__getattr__` 魔法方法等同**

使用 `__getattr__` 动态拦截属性访问可以实现类似效果，但这是语言特性而非设计模式。真正的代理模式要求显式声明与 Subject 相同的接口，这使得类型检查器（如 mypy）能够静态验证代理的合规性；而 `__getattr__` 方式是动态的，会绕过静态类型检查，在大型 AI 工程项目中增加维护风险。

---

## 知识关联

**与设计模式概述的关联**：设计模式概述中介绍的"面向接口编程而非实现"原则是代理模式得以工作的基础——只有当客户端依赖抽象 `Subject` 接口而非具体 `RealSubject` 类时，Proxy 的无缝替换才成为可能。GoF 的23种模式分类体系将代理归入结构型模式，与适配器、门面、装饰器同属一类，理解该分类有助于快速定位代理的应用场景。

**与装饰器模式的关联**：从代码结构看，装饰器模式和代理模式的类图几乎相同，均为"包装器持有被包装对象引用"。关键区别在于：装饰器的被包装对象由外部注入（构造函数参数），代理的真实对象通常由代理自身创建或从固定来源获取。在 AI 工程中，常见的组合方式是：用装饰器为 LLM 客户端添加日志功能，再将装饰后的对象包裹在缓存代理中，两层结构各司其职。掌握代理模式后，可以进一步学习面向方面编程（AOP）——Spring AOP 的动态代理机制是代理模式在框架层面的系统化应用，其 `@Transactional` 注解本质上通过 CGLIB 生成的子类代理在方法前后注入事务控制逻辑。
