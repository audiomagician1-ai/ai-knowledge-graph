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
quality_tier: "A"
quality_score: 79.6
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

# 装饰器模式

## 概述

装饰器模式（Decorator Pattern）是一种结构型设计模式，其核心思想是通过将对象放入包含特定行为的包装器对象中，来为原始对象动态添加新的功能，而不修改原始类的代码。GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式定义了这一模式，将其归类为结构型模式第4号。

装饰器模式的关键特性是它与继承的本质区别：继承在编译时静态扩展类功能，而装饰器在运行时动态叠加行为。假设有5种咖啡基础类型和10种配料选项，用继承实现需要 5×2^10 = 5120 个子类，而装饰器模式只需15个类（5个基础类 + 10个装饰器类）。这种组合爆炸问题是装饰器模式诞生的直接动因。

在AI工程领域，装饰器模式被广泛应用于模型推理管道的构建——例如为基础推理函数动态叠加日志记录、性能计时、输入校验、结果缓存等能力，无需修改核心推理逻辑。Python语言内置的 `@decorator` 语法糖正是对这一模式的语言级支持。

## 核心原理

### 结构组成与UML定义

装饰器模式由4个角色构成：
- **Component（抽象组件）**：定义基础接口，声明被装饰对象和装饰器的公共方法。
- **ConcreteComponent（具体组件）**：被装饰的原始对象，实现Component接口。
- **Decorator（抽象装饰器）**：持有一个Component类型的引用（组合关系），并实现相同的Component接口。
- **ConcreteDecorator（具体装饰器）**：在调用被包装对象方法的前后添加额外逻辑。

关键结构约束：Decorator类必须**既持有Component的引用，又实现Component接口**，这形成了递归嵌套的能力——装饰器可以嵌套装饰另一个装饰器。

### 行为叠加的递归调用链

当多个装饰器嵌套时，方法调用沿链传递。设基础组件为 `C`，两层装饰器分别为 `D1`、`D2`，调用 `D2.operation()` 的执行顺序为：

```
D2.pre_logic → D1.pre_logic → C.operation() → D1.post_logic → D2.post_logic
```

这种**洋葱模型**（Onion Model）是装饰器链执行的标准形式。在Python中，多个`@decorator`的叠加顺序遵循从下至上的包装规则：先声明的装饰器在外层，后声明的在内层。

### Python装饰器的函数式实现

Python中的装饰器本质是一个接收函数并返回新函数的高阶函数，与GoF经典面向对象实现等价但形式不同：

```python
def timing_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} 耗时: {elapsed:.4f}s")
        return result
    return wrapper

@timing_decorator
def run_inference(model, input_data):
    return model.predict(input_data)
```

`functools.wraps` 是使用Python装饰器时的关键补充——不加它会导致 `wrapper.__name__` 覆盖原函数名，破坏调试信息和文档字符串。正确写法是在 `wrapper` 上方加 `@functools.wraps(func)`。

## 实际应用

### AI推理管道的能力叠加

在构建LLM推理服务时，可以用装饰器模式将横切关注点（cross-cutting concerns）从核心推理逻辑中分离：

```python
@cache_decorator(ttl=300)        # 第3层：结果缓存300秒
@retry_decorator(max_retries=3)  # 第2层：失败自动重试3次
@log_decorator(level="INFO")     # 第1层：记录输入输出日志
def call_llm_api(prompt: str) -> str:
    return openai_client.chat(prompt)
```

三个装饰器各司其职，`call_llm_api` 函数本身只包含API调用逻辑，符合单一职责原则。任何一个装饰器可独立替换，例如将 `cache_decorator` 从本地内存缓存切换到Redis缓存，不影响其他层。

### 模型评估指标的动态注入

在模型训练框架中，可以用面向对象装饰器模式为不同数据集的评估器动态附加指标收集功能：基础 `Evaluator` 类只负责计算准确率，`MetricsDecorator` 在其外层追加F1-score计算，`TimingDecorator` 再外层追加推理延迟统计，整个评估管道在实验配置文件中通过组合构建，无需修改 `Evaluator` 源码。

## 常见误区

### 误区一：将Python的@语法糖等同于GoF装饰器模式

Python的`@decorator`语法本质是函数包装，而GoF装饰器模式要求装饰器与被装饰对象**共享同一接口**。纯函数式Python装饰器绕过了接口约束，导致类型检查失效。在严格的面向对象AI工程代码中，如果 `run_inference` 是某接口的实现，应使用继承自同一抽象基类的装饰器类，而非函数式装饰器，以确保 `isinstance` 检查和类型标注的正确性。

### 误区二：装饰器模式与继承可以随意互换

装饰器模式解决的是**运行时动态组合**问题，而非继承的简单替代。若AI系统在启动时就确定功能固定不变，继承更简洁直接。但若需要根据配置文件或运行时参数决定是否启用缓存、是否开启监控，装饰器模式是唯一能优雅处理这种动态性的选择。混淆两者会导致过度设计——对静态功能叠加使用装饰器链会增加不必要的类数量和调用开销。

### 误区三：装饰器链越长越灵活

每增加一层装饰器都引入一次额外的函数调用和闭包创建开销。在高频推理场景（如每秒数千次的向量检索调用）中，5层以上的装饰器链可能带来可量化的延迟累积。实际工程中应合并职责相近的装饰器，例如将日志和计时合并为 `ObservabilityDecorator`，保持装饰器链不超过3层。

## 知识关联

### 与设计模式概述的关联

在学习设计模式概述时已接触到"组合优于继承"（Composition over Inheritance）原则，装饰器模式是这一原则最直接的体现——Decorator类通过**组合**持有Component引用，而非继承ConcreteComponent。装饰器模式是将这一原则从理论落地为具体结构约束的标准范例。

### 向代理模式的延伸

代理模式（Proxy Pattern）与装饰器模式在结构上高度相似，两者都使用包装器持有原始对象的引用。核心区分点在于**意图**：装饰器模式的目的是**添加功能**，调用方知道自己在使用被增强的对象；代理模式的目的是**控制访问**（延迟加载、权限检查、远程代理），调用方通常不知道代理的存在。在AI服务网关中，限流和鉴权逻辑应使用代理模式实现，而非装饰器模式，尽管两者代码结构几乎相同。