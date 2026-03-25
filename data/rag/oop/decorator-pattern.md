---
id: "decorator-pattern"
concept: "装饰器模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 6
is_milestone: false
tags: ["设计模式"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 装饰器模式

## 概述

装饰器模式（Decorator Pattern）是一种结构型设计模式，其核心思想是在不修改原有类的前提下，通过将对象包裹在装饰器对象中，动态地为该对象添加新的职责或行为。与继承不同，装饰器模式在运行时组合功能，而非在编译期固定类层次结构。这一模式最早由"四人帮"（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式归类，书中将其定义为"动态地给一个对象增加一些额外的职责"。

装饰器模式解决的是"功能组合爆炸"问题。假设一个基础文本处理器需要支持加粗、斜体、加下划线三种格式，若使用继承，需要创建 2³=8 个子类（BoldText、ItalicText、UnderlineText、BoldItalicText……）来覆盖所有组合。而装饰器模式只需定义3个装饰类，在运行时按需叠加，类的数量从指数级降为线性级。

在AI工程领域，装饰器模式被广泛用于为模型推理管道动态附加日志记录、缓存、超时控制、输入验证等横切关注点（cross-cutting concerns），而不污染核心推理逻辑。Python语言的`@decorator`语法糖也源自这一设计模式的思想，使其在AI框架开发中极为常见。

## 核心原理

### 组件结构与UML关系

装饰器模式包含四个角色：
- **Component（抽象组件）**：定义对象的接口，例如抽象类`TextProcessor`，声明`process(text: str) -> str`方法。
- **ConcreteComponent（具体组件）**：实现基本功能的原始对象，例如`BasicTextProcessor`。
- **Decorator（抽象装饰器）**：持有一个Component类型的引用，并实现相同的Component接口。关键在于它与Component是"组合"关系而非"继承"关系——Decorator内部有一个`_wrapped: Component`成员变量。
- **ConcreteDecorator（具体装饰器）**：在调用被装饰对象的同名方法前后插入新逻辑，例如`LoggingDecorator`在调用`self._wrapped.process(text)`前后写入日志。

### 装饰链的调用机制

当多个装饰器叠加时，形成一条调用链。以`LoggingDecorator(CachingDecorator(BasicProcessor()))`为例：
1. 调用最外层`LoggingDecorator.process(text)`，记录入口日志
2. 内部调用`CachingDecorator.process(text)`，检查缓存
3. 缓存未命中时，调用`BasicProcessor.process(text)`执行实际逻辑
4. 结果沿链条反向返回，各层依次完成收尾操作

这一链式调用保证了"职责的透明性"：调用方持有的仍然是`Component`接口引用，完全不知道背后叠加了多少层装饰器。时间复杂度方面，每增加一层装饰器仅增加O(1)的方法调用开销。

### Python中的语法糖实现

Python的`@`语法本质上是`func = decorator(func)`的简写。以下是AI推理服务中典型的装饰器实现：

```python
def retry(max_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
        return wrapper
    return decorator

@retry(max_attempts=3)
def call_llm_api(prompt: str) -> str:
    # 实际调用大模型API
    ...
```

注意`functools.wraps`装饰器的使用——若省略它，`wrapper.__name__`会遮蔽原函数名，导致调试时堆栈信息失真。这是Python装饰器实现中最易忽略的细节。

## 实际应用

**AI推理管道的中间件叠加**：在LangChain等框架中，`Chain`对象支持通过装饰器模式叠加`CallbackHandler`。例如，`with_config(callbacks=[TokenCounterHandler(), LatencyTrackerHandler()])`实质上将原始Chain对象包裹在两层装饰器中，分别统计token消耗和推理延迟，而Chain的`invoke()`接口签名保持不变。

**模型服务的限流与缓存**：在FastAPI构建的模型服务中，常见的装饰器叠加方式为：
```python
@app.post("/predict")
@rate_limiter(max_rps=100)
@cache(ttl=300)
@validate_input(schema=PredictRequest)
async def predict(request: PredictRequest):
    ...
```
三个业务装饰器按从内到外的顺序依次生效：先验证输入，再查缓存，最后限流。执行时则以相反顺序（从外到内）逐层调用。

**PyTorch的`nn.Module`包装**：PyTorch中的`DataParallel`和`DistributedDataParallel`均是对`nn.Module`的装饰器式包装——`model = torch.nn.DataParallel(model)`在不改变`model.forward()`签名的前提下，附加了多GPU数据并行的能力，是装饰器模式在深度学习框架中的经典工业应用。

## 常见误区

**误区一：将装饰器模式与Python `@`语法等同**。Python的`@`语法是函数式装饰器，它操作的是函数对象；而GoF装饰器模式是面向对象设计，操作的是实现同一接口的类实例。前者无需共同接口，后者严格要求装饰器与被装饰对象实现相同的Component接口。两者目的相似，但Python的类装饰器（`class LoggingDecorator`包裹`instance`）才更接近GoF原意。

**误区二：认为装饰器模式可以完全替代继承**。装饰器模式仅适合在接口稳定的前提下叠加行为，若新行为需要改变对象的核心数据结构（例如为神经网络层添加新的可学习参数），仍需继承或组合到子类中实现。装饰器无法访问被装饰对象的私有成员，这是其根本限制。

**误区三：忽视装饰顺序的影响**。`GzipDecorator(EncryptDecorator(data))`与`EncryptDecorator(GzipDecorator(data))`产生完全不同的结果——正确顺序应先压缩再加密（因加密后数据熵极高，压缩效果接近零）。在AI服务中，`CacheDecorator(RateLimiterDecorator(...))`与`RateLimiterDecorator(CacheDecorator(...))`的限流粒度也截然不同：前者对缓存未命中请求限流，后者对所有请求限流。

## 知识关联

**前置知识——设计模式概述**：装饰器模式在GoF的23种模式中属于结构型模式，理解"组合优于继承"这一面向对象原则（Open/Closed Principle，即开闭原则）是掌握装饰器模式的前提——对扩展开放意味着可叠加装饰器，对修改封闭意味着不触碰原始ConcreteComponent代码。

**后续概念——代理模式**：代理模式（Proxy Pattern）与装饰器模式在代码结构上几乎相同，都持有对目标对象的引用并实现相同接口，但两者意图不同。装饰器模式的意图是**增强**对象功能（对象自身可在客户端直接使用，装饰是可选的增量），而代理模式的意图是**控制**对象访问（客户端通常不持有也不应直接持有被代理对象）。在AI工程中，模型服务的访问鉴权属于代理模式，而为模型调用附加性能追踪属于装饰器模式——这一区分是学习代理模式时最需厘清的边界。
