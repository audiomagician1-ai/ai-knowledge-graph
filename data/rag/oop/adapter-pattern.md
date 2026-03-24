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
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 适配器模式

## 概述

适配器模式（Adapter Pattern）是一种结构型设计模式，其核心机制是将一个类的接口转换成客户端所期望的另一种接口形式，使得原本因接口不匹配而无法协同工作的类能够正常合作。该模式的典型类比是现实中的电源适配器——一台美国设备使用110V插头，但中国插座提供220V/50Hz的三孔接口，适配器在两者之间完成电气转换，双方无需改变自身结构。

适配器模式最早由Gang of Four（GoF）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式提出，归类于结构型模式（Structural Patterns）。它解决的是已有代码的兼容性问题——当系统中存在无法修改的遗留代码（Legacy Code），或需要整合第三方库时，强行修改原有接口往往会破坏现有功能或违反开放封闭原则。适配器模式提供了一种"包装"机制，让新旧接口之间形成桥接层，而不必触动任何一方的内部实现。

在AI工程场景中，适配器模式极为常见：不同深度学习框架（如PyTorch与TensorFlow）之间的模型转换层、统一封装多个LLM供应商API（OpenAI、Anthropic、百度文心）的抽象接口，以及将旧版数据预处理管道对接新版训练框架，都是典型应用场景。

## 核心原理

### 组成角色与结构

适配器模式包含三个固定角色：

- **Target（目标接口）**：客户端所期望调用的接口，定义了客户端使用的方法签名
- **Adaptee（被适配者）**：已存在的类或接口，拥有客户端所需的功能，但接口形式不兼容
- **Adapter（适配器）**：核心类，持有或继承Adaptee的实例，同时实现Target接口，在内部完成接口转换逻辑

客户端仅依赖Target接口编写代码，完全感知不到Adaptee的存在。调用链为：`Client → Target接口 → Adapter → Adaptee`。

### 对象适配器与类适配器

适配器模式有两种实现方式，区别在于Adapter与Adaptee的关系类型：

**对象适配器（Object Adapter）** 使用组合（Composition）：Adapter内部持有一个Adaptee的实例，通过调用该实例的方法完成转换。这是更推荐的方式，因为它遵循"优先使用组合而非继承"原则，且可以适配Adaptee的子类。

```python
class OldDataLoader:
    def load_csv(self, path: str) -> list:
        return [...]  # 返回list格式

class NewTrainingInterface:
    def get_batch(self) -> dict:
        pass  # 期望返回dict格式，含'features'和'labels'键

class DataLoaderAdapter(NewTrainingInterface):
    def __init__(self, old_loader: OldDataLoader, path: str):
        self._loader = old_loader
        self._path = path
    
    def get_batch(self) -> dict:
        raw = self._loader.load_csv(self._path)
        return {'features': raw[:-1], 'labels': raw[-1]}
```

**类适配器（Class Adapter）** 使用多重继承：Adapter同时继承Target和Adaptee，通过继承关系直接获得Adaptee的方法。此方式在Python中可行，但在不支持多重继承的Java中无法直接实现，且与具体类紧密耦合，灵活性较低。

### 接口转换的三种典型操作

适配器内部的转换逻辑通常涉及以下三类操作：

1. **方法名映射**：将`get_batch()`调用转发给`load_csv()`，仅做名称层面的重命名
2. **数据格式转换**：如将NumPy数组转换为PyTorch Tensor：`torch.from_numpy(adaptee.get_array())`
3. **参数重组**：目标接口接收单个配置字典，而被适配者需要多个独立参数，适配器负责拆包重组

## 实际应用

### 统一多LLM供应商接口

在AI工程实践中，团队常需同时支持多个大语言模型供应商。OpenAI的调用格式为`client.chat.completions.create(model="gpt-4", messages=[...])`，而Anthropic Claude的格式为`client.messages.create(model="claude-3", max_tokens=1024, messages=[...])`，两者参数结构和返回值格式均不相同。

通过定义统一的`LLMInterface`目标接口，分别为OpenAI和Anthropic编写适配器类，业务代码只调用`llm.generate(prompt, max_tokens)`，切换模型供应商只需替换适配器实例，业务逻辑零改动。

### 旧版数据管道对接新框架

某AI团队有一套基于scikit-learn的数据预处理管道，其`transform(X)`方法返回NumPy数组。新引入的PyTorch训练框架要求DataLoader返回`(Tensor, Tensor)`格式的元组。编写`SklearnPipelineAdapter`，在其`__iter__`方法中调用原管道的`transform()`并执行`torch.FloatTensor()`转换，使两套系统无缝对接，同时完整保留了原管道中已调优的特征工程逻辑。

## 常见误区

### 误区一：将适配器模式与装饰器模式混淆

两者都对目标类进行"包装"，但目的截然不同。装饰器模式在**保持接口不变**的前提下为对象动态添加功能；适配器模式的目的是**转换接口**，使不兼容的接口变得兼容，被包装后接口形式本身发生了改变。判断依据：如果包装前后客户端调用的方法签名完全相同，是装饰器；如果方法名或参数格式发生了变化，是适配器。

### 误区二：将适配器用于"应该统一设计"的新系统

适配器模式是应对**已有不兼容代码**的解决方案，专门用于无法或不宜修改原有类的场景。如果是正在设计的全新系统，各模块接口不兼容是设计缺陷，应当在设计阶段统一接口规范，而不是堆砌适配器。过度使用适配器会在系统中引入额外的间接层，增加调试难度，掩盖真实的设计问题。

### 误区三：认为适配器必须一对一转换

一个适配器可以适配多个Adaptee，称为"双向适配器"或"多路适配器"。例如在LLM路由场景中，单个`UniversalLLMAdapter`可以根据`model_name`参数在内部选择调用OpenAI、Anthropic或本地Ollama实例，对外仍暴露统一的`generate()`接口。这种模式在AI网关产品（如LiteLLM）中被广泛采用。

## 知识关联

适配器模式建立在**接口（Interface）**概念之上——Target角色本质上是一个接口契约，Adapter通过实现该接口获得与客户端通信的资格。没有对接口与实现分离机制的理解，就无法解释为什么客户端可以"透明地"替换不同的Adapter实例。

在**设计模式概述**中学到的"针对接口编程，而非针对实现编程"原则，在适配器模式中得到了直接体现：客户端代码依赖抽象的Target接口，对Adapter的具体类型一无所知，因此可以在运行时注入不同的适配器实现（如切换LLM供应商），而不触发任何代码修改。这也是适配器模式能够支持依赖注入实践的结构原因。
