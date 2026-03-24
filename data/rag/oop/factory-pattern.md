---
id: "factory-pattern"
concept: "工厂模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 5
is_milestone: false
tags: ["设计模式"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 工厂模式

## 概述

工厂模式（Factory Pattern）是一种创建型设计模式，其核心思想是将对象的**创建逻辑**与**使用逻辑**分离，由一个专门的"工厂"负责实例化具体类。调用者只需指定所需对象的类型，无需了解该类型对象的具体构造方式。工厂模式在《设计模式：可复用面向对象软件的基础》（GoF，1994年）中被正式收录，并细分为简单工厂、工厂方法（Factory Method）和抽象工厂（Abstract Factory）三种变体。

工厂模式解决的根本问题是**依赖倒置**：当代码直接使用 `new ClassName()` 创建对象时，调用方与具体类之间产生强耦合，一旦需要替换实现类，所有调用点均需修改。工厂模式通过引入创建接口，使调用方只依赖抽象类型而非具体类型，从而使系统更易于扩展和测试。

在AI工程场景下，工厂模式尤其常见于**模型加载器**和**预处理管道**的构建——不同任务（文本分类、目标检测、语音识别）需要实例化不同的模型对象，通过工厂模式可以根据配置文件动态决定实例化哪种模型，而无需在业务代码中写满 `if/elif` 分支。

---

## 核心原理

### 简单工厂（Simple Factory）

简单工厂不属于GoF的23种正式模式，但最直观。其结构由一个静态方法 `create(type)` 构成，内部使用条件分支返回不同子类的实例：

```python
class ModelFactory:
    @staticmethod
    def create(model_type: str):
        if model_type == "bert":
            return BertModel()
        elif model_type == "gpt":
            return GPTModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
```

**缺点明确**：每新增一种模型类型，就必须修改 `ModelFactory` 的源码，违反了**开闭原则**（对扩展开放，对修改关闭）。

### 工厂方法（Factory Method）

工厂方法模式将创建逻辑推迟到子类实现，定义抽象工厂接口 `create_model()`，每种具体工厂子类覆写该方法：

```python
from abc import ABC, abstractmethod

class BaseModelFactory(ABC):
    @abstractmethod
    def create_model(self):
        pass

class BertFactory(BaseModelFactory):
    def create_model(self):
        return BertModel(vocab_size=30522, hidden_size=768)

class GPTFactory(BaseModelFactory):
    def create_model(self):
        return GPTModel(vocab_size=50257, n_layers=12)
```

此结构满足开闭原则：新增模型类型只需新增一对 `(ProductClass, FactoryClass)`，无需改动已有代码。其UML结构包含四个角色：**抽象产品**、**具体产品**、**抽象工厂**、**具体工厂**。

### 抽象工厂（Abstract Factory）

当系统需要创建**一族相关对象**时使用抽象工厂。例如，AI推理系统同时需要匹配的模型（Model）和对应的分词器（Tokenizer），两者必须来自同一"产品族"才能正常协作：

```python
class AbstractAIFactory(ABC):
    @abstractmethod
    def create_model(self): pass

    @abstractmethod
    def create_tokenizer(self): pass

class BertSuite(AbstractAIFactory):
    def create_model(self):
        return BertModel()
    def create_tokenizer(self):
        return BertTokenizer(vocab_file="bert-base-uncased-vocab.txt")
```

抽象工厂保证了同族对象之间的**兼容性约束**，避免出现GPT模型配BertTokenizer的混用错误。代价是：新增一种产品类型（如新增 `create_embedder()`）需要修改所有具体工厂类。

---

## 实际应用

**场景1：多后端推理引擎切换**

PyTorch、ONNX Runtime、TensorRT是AI推理的三种常见后端，各自的初始化参数差异极大（TensorRT需指定 `max_workspace_size`，ONNX Runtime需指定 `execution_provider`）。用工厂方法模式，业务层只调用 `engine_factory.create_engine(config)`，底层自动根据 `config.backend` 字段实例化对应引擎，实现零代码侵入的后端切换。

**场景2：数据预处理管道**

NLP任务中，中文文本需要 `JiebaTokenizer`，英文文本需要 `WhitespaceTokenizer`，代码扫描语言标签后交由 `TokenizerFactory.create(lang)` 返回对应实例。该模式在 Hugging Face `transformers` 库的 `AutoModel.from_pretrained()` 方法中有明确体现——`AutoModel` 本身就是一个工厂，通过读取 `config.json` 中的 `model_type` 字段决定实例化哪个具体模型类。

**场景3：单元测试中替换真实模型**

测试阶段不希望加载真实的大模型（耗时数分钟），可以创建 `MockModelFactory` 替换生产环境的 `RealModelFactory`，注入轻量级的 stub 对象，整个测试用例运行时间从分钟级压缩到毫秒级。

---

## 常见误区

**误区1：将简单工厂等同于工厂方法模式**

两者结构不同：简单工厂的"工厂"是一个静态方法，无需继承；工厂方法的"工厂"是一个抽象类，依赖多态。当需要通过依赖注入替换工厂实现时，简单工厂无法做到（静态方法不可被覆写），工厂方法可以。把简单工厂用于需要开闭原则的场景，是最典型的滥用。

**误区2：认为抽象工厂适用于所有多类型创建场景**

抽象工厂的适用条件非常具体：必须存在**多个产品维度**且产品之间有**族约束**。如果只有一个产品维度（只需创建模型，不涉及配套的tokenizer、optimizer等），强行使用抽象工厂反而引入不必要的类爆炸——每增加一种模型，就需要新增至少1个工厂类+1个产品类，而工厂方法只需新增1个工厂类。

**误区3：工厂模式解决了所有对象创建问题**

工厂模式适合创建**同一类型体系**下的对象。若对象的构建步骤复杂且有顺序依赖（如先设置层数、再设置激活函数、最后编译），仅靠工厂无法优雅表达——此时需要转向**建造者模式**，通过链式调用 `builder.set_layers(12).set_activation("gelu").build()` 来分步构造。

---

## 知识关联

工厂模式建立在**设计模式概述**中介绍的"面向接口编程"和"开闭原则"之上——不理解为什么要避免 `new ConcreteClass()`，就无法体会工厂方法的价值。工厂方法的多态机制直接依赖抽象类与继承体系，因此对Python `ABC`（Abstract Base Class）或Java `interface` 的掌握是前提。

工厂模式完成了"创建单一对象"的职责分离，但面对构建步骤复杂的对象时能力有限，这正是**建造者模式**的切入点：建造者模式将复杂对象的构建过程拆解为多个独立步骤，可以看作工厂模式在"构建复杂度"维度上的延伸。两者的边界在于：工厂关注**创建哪种类型**，建造者关注**如何一步步构建同一类型**。
