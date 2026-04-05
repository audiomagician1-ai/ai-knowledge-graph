---
id: "dependency-injection"
concept: "依赖注入"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 6
is_milestone: false
tags: ["设计"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 81.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.974
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 依赖注入

## 概述

依赖注入（Dependency Injection，简称DI）是一种设计模式，其核心思想是：对象不应自行创建它所依赖的对象，而应由外部"注入者"将依赖对象传递给它。这直接实现了SOLID原则中的"依赖倒置原则"（DIP）——高层模块不依赖低层模块，二者都依赖抽象接口。

依赖注入的概念由Martin Fowler在2004年的文章《Inversion of Control Containers and the Dependency Injection Pattern》中正式命名和系统阐述，将其从"控制反转"（IoC）这一更宽泛的概念中分离出来，明确了"注入"的机制。在此之前，Spring框架（2002年发布）已经将这一模式广泛应用于Java生态。

在AI工程的面向对象设计中，依赖注入尤为关键：一个模型推理类（`ModelInferencer`）不应硬编码使用某个特定的模型加载器，而应接受任意满足`ModelLoader`接口的对象。这样，在训练环境中注入`LocalModelLoader`，在生产环境注入`RemoteModelLoader`，测试时注入`MockModelLoader`，无需修改`ModelInferencer`本身的代码。

---

## 核心原理

### 三种注入方式

依赖注入有三种具体实现方式，各有其适用场景：

**构造器注入（Constructor Injection）**：依赖通过构造函数参数传入，注入后不可更改，适合必需依赖。

```python
class ModelInferencer:
    def __init__(self, model_loader: ModelLoader, logger: Logger):
        self._loader = model_loader
        self._logger = logger
```

**属性注入（Setter/Property Injection）**：依赖通过公开属性或setter方法设置，适合可选依赖或需要在运行时更换的依赖。

**接口注入（Interface Injection）**：对象实现一个"接收注入"的接口，由容器调用该接口传入依赖。此方式在Python中较少见，常见于Java的早期IoC框架。

三种方式中，**构造器注入**是最推荐的，因为它强制要求依赖在对象构建时完备，避免"对象构建成功但无法正常工作"的半初始化状态。

### 依赖倒置的数学含义

若未使用依赖注入，依赖关系为：`A → B`（A直接依赖B的具体实现）。引入接口`IB`后，关系变为：`A → IB ← B`。高层模块`A`和低层模块`B`都依赖抽象`IB`，依赖方向被"倒置"。这种结构使得替换`B`为`B'`时，`A`的代码无需改动，满足开闭原则。

### IoC容器的角色

在大型AI系统中，手动管理依赖注入会随着组件数量增加变得繁琐。IoC容器（如Python的`dependency-injector`库、Java的Spring）负责：
1. **注册**：将接口与具体实现类绑定（例如将`ModelLoader`绑定至`OnnxModelLoader`）
2. **解析**：在需要时自动实例化并注入依赖，支持递归解析（被注入的对象本身也有自己的依赖）
3. **生命周期管理**：控制依赖对象是单例（Singleton）、每次请求新建（Transient），还是按请求作用域（Scoped）

---

## 实际应用

### AI推理服务的可测试设计

假设构建一个文本分类服务：

```python
from abc import ABC, abstractmethod

class TextPreprocessor(ABC):
    @abstractmethod
    def preprocess(self, text: str) -> list: ...

class ClassificationModel(ABC):
    @abstractmethod
    def predict(self, features: list) -> str: ...

class TextClassificationService:
    def __init__(self, preprocessor: TextPreprocessor, model: ClassificationModel):
        self._preprocessor = preprocessor
        self._model = model

    def classify(self, text: str) -> str:
        features = self._preprocessor.preprocess(text)
        return self._model.predict(features)
```

测试时只需注入`MockTextPreprocessor`和`MockClassificationModel`，整个测试无需加载真实模型，运行速度从分钟级降至毫秒级。生产环境则注入`BertPreprocessor`和`TorchClassificationModel`，无需修改`TextClassificationService`的任何代码。

### 多环境配置切换

在AI工程中，同一套代码需要在本地开发（使用CPU小模型）、云端生产（使用GPU大模型）、CI测试（使用存根Mock）三种环境下运行。通过依赖注入，只需在启动入口（Composition Root）按环境变量决定注入哪个具体实现，业务逻辑代码完全不感知环境差异。

---

## 常见误区

### 误区一：把依赖注入等同于使用IoC容器框架

依赖注入是一种**设计模式**，不需要任何框架即可实现——手动在`main()`函数或工厂方法中传入依赖对象，就已经是依赖注入。IoC容器只是自动化管理注入过程的工具，适用于依赖关系复杂的大型项目。在小型AI脚本中，手动注入往往更清晰。

### 误区二：构造函数参数越多，说明依赖注入做得越好

一个类的构造函数接受7个以上依赖参数，通常意味着该类承担了过多职责，违反了单一职责原则（SRP），而非依赖注入本身的问题。依赖注入揭露了这种"过度耦合"，但不应被用来掩盖它——正确做法是重新划分类的职责。

### 误区三：依赖注入会导致性能开销

构造器注入的本质只是将对象引用作为参数传递，Python中一次参数赋值的开销约为纳秒级。IoC容器的反射解析在首次构建时有开销，但通常在初始化阶段发生，不影响推理路径上的热代码性能。将"使用了DI容器"与"运行时性能差"混为一谈，是对依赖注入的误解。

---

## 知识关联

**与SOLID原则的关系**：依赖注入是实现SOLID中"D"（依赖倒置原则）的最直接机制，同时支撑"O"（开闭原则，通过注入不同实现而非修改代码来扩展行为）和"L"（里氏替换原则，注入的子类实现必须能替换基类接口）。没有对SOLID原则的理解，依赖注入只是一种"把参数传进去"的表面操作，无法理解其架构价值。

**与工厂模式的区别**：工厂模式在内部创建对象（`A`调用`Factory.create()`获得`B`），创建控制权仍在`A`内部；依赖注入则是将创建权完全移至外部，`A`不知道也不关心`B`是如何被创建的。两者都解决"谁来创建依赖"的问题，但控制权的归属相反。

**在AI工程系统设计中的延伸**：掌握依赖注入后，可进一步理解面向接口编程在模型版本管理（热替换模型实现）、A/B测试框架（注入不同策略对象）和分布式推理系统（注入本地或远程推理客户端）中的具体应用，这些场景都以依赖注入为基础设计技术。