---
id: "adapter-pattern"
concept: "适配器模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 3
is_milestone: false
tags: ["adapter", "wrapper", "design-pattern"]

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

# 适配器模式

## 概述

适配器模式（Adapter Pattern）是一种结构型设计模式，其核心目标是将一个类的接口转换成客户端所期望的另一种接口形式，使原本因接口不兼容而无法协作的类能够共同工作。就像现实中的电源适配器将220V交流电转换为笔记本需要的19V直流电一样，适配器模式在软件层面充当了"翻译器"的角色。

该模式由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中首次系统化描述，被归类为结构型模式。其诞生背景是大量遗留系统（Legacy System）集成问题——开发者经常需要将不受自己控制的第三方库或旧代码与新系统对接，而无法修改原始接口定义。

在AI工程领域，适配器模式尤为常见。当需要将不同深度学习框架（如PyTorch模型接口与TensorFlow Serving接口）对接时，或将不同数据源的格式统一为模型训练管道期望的标准格式时，适配器模式提供了一种无需修改原有代码即可实现接口兼容的系统化方法。

## 核心原理

### 两种实现形式：类适配器与对象适配器

适配器模式有两种经典实现形式，它们的结构差异直接影响使用场景的选择。

**类适配器**通过多重继承实现：适配器类同时继承目标接口（Target）和被适配者（Adaptee），直接重写目标接口方法并在内部调用被适配者的方法。在Python中，由于支持多重继承，类适配器写法如下：

```python
class ClassAdapter(Target, Adaptee):
    def request(self):           # Target接口期望的方法
        return self.specific_request()  # 调用Adaptee的方法
```

**对象适配器**通过组合（Composition）实现：适配器类实现目标接口，并在内部持有一个被适配者的实例引用。GoF更推荐对象适配器，因为它遵循"优先使用组合而非继承"原则，耦合度更低，且允许适配同一个被适配者类的不同子类。

### 四个参与角色及其职责

适配器模式由以下四个角色构成，缺一不可：

1. **Target（目标接口）**：客户端代码直接依赖的接口，定义了客户端期望调用的方法，例如 `predict(input_tensor)` 。
2. **Client（客户端）**：只知道Target接口的存在，完全不了解Adaptee的代码。
3. **Adaptee（被适配者）**：已有的类，拥有实际功能但接口与Target不兼容，例如某旧版模型库的 `run_inference(numpy_array)` 方法。
4. **Adapter（适配器）**：核心角色，实现Target接口，内部将对Target方法的调用委托给Adaptee的对应方法，并负责必要的数据格式转换。

### 数据转换逻辑的封装

适配器不仅是方法名的映射，往往还承担数据格式转换职责。以AI推理服务为例，一个典型的适配器需要完成：将客户端传入的JSON字符串反序列化 → 转换为Numpy数组 → 调用旧版推理引擎 → 将返回的原始概率数组重新封装为标准ResponseObject。这些转换逻辑全部封装在Adapter内部，Client和Adaptee双方均无感知。

## 实际应用

### AI框架接口统一

在MLOps流水线中，团队常需同时支持多个模型框架。可定义统一的 `ModelInferenceInterface`（Target），要求实现 `infer(self, input: dict) -> dict` 方法。针对PyTorch模型创建 `PyTorchModelAdapter`，内部将输入dict转换为 `torch.Tensor`，调用 `model.forward()`，再将结果转回dict。针对sklearn模型创建 `SklearnModelAdapter`，内部调用 `model.predict_proba()`。业务代码统一调用 `ModelInferenceInterface`，无需关心底层框架差异。

### 数据集格式适配

HuggingFace的 `datasets` 库返回 `Dataset` 对象，而某自定义训练循环期望接收标准Python迭代器。通过编写 `HuggingFaceDatasetAdapter` 实现 `__iter__` 和 `__len__` 方法，内部调用Dataset的批量获取逻辑，即可无缝接入原有训练代码，无需修改训练循环的任何一行。

### 第三方API接入

当从OpenAI API切换至Azure OpenAI或本地部署的Ollama时，两者的请求参数结构存在差异。通过为每个服务实现统一的 `LLMClient` 适配器接口（定义 `chat_complete(messages: list, model: str) -> str`），可以在不修改调用方代码的前提下自由切换底层LLM服务提供商。

## 常见误区

### 误区一：将适配器模式与装饰器模式混淆

两者都对已有类进行包装，但目的截然不同。**适配器模式的目的是转换接口**——Adapter实现的是与Adaptee完全不同的Target接口；而**装饰器模式的目的是增强功能**——Decorator实现的是与被装饰对象完全相同的接口，只是在调用前后附加额外行为。判断标准很简单：如果包装后对外暴露的方法签名与原始类不同，那是适配器；如果方法签名相同只是行为增强，那是装饰器。

### 误区二：适配器应承担业务逻辑

适配器的职责仅限于**接口转换和数据格式转换**，不应包含任何业务逻辑判断。如果在适配器中加入"当输入长度超过512时截断"这样的业务规则，会导致该规则被隐藏在适配层，难以测试和维护。业务逻辑应放在Client或Adaptee自身中，适配器只做纯粹的"翻译"工作。

### 误区三：过度使用适配器导致"适配器地狱"

当系统中有大量相互不兼容的接口时，开发者容易为每一对接口都创建适配器，最终形成复杂的适配器链（A适配B，B适配C，C适配D）。正确的做法是：如果接口不兼容是系统性问题，应优先通过定义统一的**门面（Facade）接口**来从根本上解决，而不是无限叠加适配器层。

## 知识关联

适配器模式依赖对**接口（Interface）**概念的理解——必须能够区分Target接口与Adaptee实现，才能判断何处需要适配以及适配的边界在哪里。同时需要理解**设计模式概述**中结构型模式与行为型模式的分类逻辑，明确适配器解决的是"结构兼容性"问题而非"行为协调"问题。

在AI工程的实践脉络中，适配器模式与**策略模式**形成互补关系：策略模式用于在运行时切换算法实现，而适配器模式使得那些原本接口不兼容的算法实现能够被纳入策略模式的统一框架中。两者结合使用，是构建可扩展AI推理服务的常见架构手法。理解适配器模式还为后续学习**门面模式（Facade）**奠定基础——当需要适配的接口从"一对一"扩展到"多个子系统统一入口"时，门面模式接替了适配器模式的工作。