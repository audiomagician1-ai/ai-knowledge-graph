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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 代理模式

## 概述

代理模式（Proxy Pattern）是一种结构型设计模式，通过引入一个代理对象（Proxy Object）作为真实对象（Real Subject）的替代或占位符，由代理对象控制外部对客户端对真实对象的访问。代理对象与真实对象实现相同的接口（Subject Interface），使客户端无需感知自己是在与代理还是真实对象交互。

代理模式最早在1994年由GoF（Gang of Four）在《设计模式：可复用面向对象软件的基础》一书中正式归纳，原始定义为"Provide a surrogate or placeholder for another object to control access to it"。该书将代理模式列为23种经典设计模式之一，属于结构型分类。代理的思想更早可追溯至操作系统中的虚拟内存页表机制——用地址映射表作为物理内存的"代理"，按需加载页面。

在AI工程场景中，代理模式尤其重要：调用大语言模型（LLM）接口时，代理对象可以在不修改业务逻辑的前提下透明地完成缓存重复请求、限流保护、日志记录和权限校验。这使得AI服务调用层与业务层解耦，降低了对昂贵API调用的依赖，也为单元测试提供了Mock替代真实模型的途径。

---

## 核心原理

### 三角色结构与接口统一

代理模式由三个角色构成：**Subject（抽象主题接口）**、**RealSubject（真实主题）**和**Proxy（代理类）**。其中Subject定义了RealSubject和Proxy共同实现的接口，这是代理能够透明替换真实对象的关键。UML类图中，Proxy持有一个指向RealSubject的引用（组合关系），并在自己的方法实现中调用RealSubject的对应方法，前后可插入附加逻辑。

```python
from abc import ABC, abstractmethod

class LLMService(ABC):  # Subject
    @abstractmethod
    def complete(self, prompt: str) -> str:
        pass

class OpenAIService(LLMService):  # RealSubject
    def complete(self, prompt: str) -> str:
        # 实际调用 OpenAI API，费用约 $0.002/1K tokens
        return call_openai_api(prompt)

class CachingLLMProxy(LLMService):  # Proxy
    def __init__(self, real_service: LLMService):
        self._real = real_service
        self._cache = {}

    def complete(self, prompt: str) -> str:
        if prompt not in self._cache:
            self._cache[prompt] = self._real.complete(prompt)
        return self._cache[prompt]
```

### 四种主要代理类型及其差异

代理模式按用途细分为四种经典变体，它们的核心区别在于**在何时创建真实对象、附加何种控制逻辑**：

- **虚拟代理（Virtual Proxy）**：延迟创建开销大的真实对象，直到真正需要时才实例化。例如，图像编辑器中用代理占位符表示高分辨率图片，只有用户滚动到该图片时才加载真实数据。
- **保护代理（Protection Proxy）**：在调用真实对象方法前校验权限，不同角色获得不同访问级别。AI平台中，免费用户代理拦截GPT-4调用并降级至GPT-3.5。
- **远程代理（Remote Proxy）**：将本地方法调用转换为网络请求，隐藏网络通信细节。Java RMI（Remote Method Invocation）的Stub本质上就是远程代理。
- **智能代理（Smart Proxy）**：在访问真实对象时附加引用计数、日志或缓存等额外功能，本节示例中的`CachingLLMProxy`属于此类。

### 与装饰器模式的结构差异

代理模式与装饰器模式（Decorator Pattern）在UML结构上极为相似，但意图截然不同，这一差异直接影响使用决策：

| 维度 | 代理模式 | 装饰器模式 |
|------|----------|------------|
| 意图 | 控制对真实对象的访问 | 动态扩展对象的功能 |
| 真实对象的创建 | 通常由代理内部创建或持有固定引用 | 由外部传入，支持链式叠加 |
| 接口变化 | 接口保持不变 | 接口可被扩展 |
| 典型场景 | 权限、缓存、懒加载 | 日志、压缩、加密叠加 |

代理的关键特征是：**客户端通常不知道也不需要知道代理的存在**；而装饰器通常由客户端主动构建装饰链。

---

## 实际应用

**AI推理服务限流代理**：在生产环境中，每秒调用LLM次数受API速率限制（如OpenAI Tier-1限额为60 RPM）。保护代理可在`complete()`方法入口处维护令牌桶算法，超限时抛出`RateLimitException`而不真正发起HTTP请求，避免触发API提供商的429错误。

**向量数据库懒加载代理**：Pinecone、Weaviate等向量数据库的连接初始化耗时约200-500ms。使用虚拟代理，可以在应用启动时立刻返回代理对象，将真正的连接延迟至首次调用`query()`或`upsert()`时，显著改善服务冷启动时间。

**单元测试Mock代理**：在AI工程的测试流程中，将`OpenAIService`替换为返回固定字符串的`MockLLMProxy`，既绕过网络依赖，又将测试成本从约$0.01/次降低至零，同时保证测试的确定性（Determinism）。

**Python的`__getattr__`动态代理**：Python可通过覆写`__getattr__`实现透明动态代理，无需预先知道真实对象的所有方法名称，适合为第三方SDK动态注入日志逻辑。

---

## 常见误区

**误区一：代理必须完全透明**。部分开发者认为代理对象永远不应改变真实对象的返回值。然而智能代理（Smart Proxy）完全可以修改结果，例如缓存代理返回的是缓存副本而非新鲜调用结果；保护代理在权限不足时可以返回降级响应（Fallback Response）。透明性指的是**接口层面一致**，而非行为层面完全等同。

**误区二：代理模式与装饰器模式可以互换**。两者UML图形态相近，但代理通常**自己控制真实对象的生命周期**（在内部`new`真实对象），装饰器则接收外部注入的被装饰对象。若将LLM缓存层错误地实现为装饰器，在链式叠加多个装饰器时，相同的缓存键可能在不同层次被重复命中或失效，造成缓存语义混乱。

**误区三：虚拟代理等同于工厂方法的懒加载**。工厂方法的懒加载直接返回真实对象本身，调用方持有真实对象引用；虚拟代理返回的始终是代理对象，调用方永远通过代理访问，真实对象的创建细节对调用方完全隐藏。这在需要持续拦截每次访问（如统计调用次数）时具有工厂懒加载无法替代的优势。

---

## 知识关联

理解代理模式需要先掌握**设计模式概述**中的结构型模式分类逻辑——GoF将结构型模式定义为"处理类或对象的组合"，代理模式通过组合关系（而非继承）持有真实对象，是组合优于继承原则的典型体现。此外，需要熟悉**装饰器模式**的接口包装机制，才能准确辨别两种模式在意图和真实对象生命周期管理上的根本差异，避免在AI服务治理层（缓存、限流、权限）中错误选型。

在Python标准库中，`unittest.mock.MagicMock`、`weakref.proxy()`以及`functools.cached_property`的内部实现均体现了代理模式的思想；在AI框架层面，LangChain的`CacheBackedEmbeddings`和Hugging Face推理端点的重试包装器也是代理模式在工程落地中的直接应用。掌握代理模式后，学习者可以进一步探索**服务网格（Service Mesh）**中的Sidecar代理机制——Envoy代理本质上是分布式系统中代理模式的网络级延伸。