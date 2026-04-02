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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 工厂模式

## 概述

工厂模式（Factory Pattern）是一种创建型设计模式，其核心思想是**将对象的创建逻辑与使用逻辑分离**，通过专门的"工厂"类或方法来负责实例化具体对象，而调用者只需面向抽象接口编程，无需知道实际创建的是哪个具体类。

工厂模式最早由 Gang of Four（GoF）在1994年出版的《设计模式：可复用面向对象软件的基础》中系统化描述。GoF 将工厂模式细分为三种变体：简单工厂（Simple Factory，严格说不属于GoF23种模式）、工厂方法模式（Factory Method Pattern）以及抽象工厂模式（Abstract Factory Pattern）。这三种形态在 AI 工程中的模型加载、预处理器构建等场景中被广泛采用。

在 AI 工程场景中，工厂模式解决了一个实际痛点：不同任务需要实例化不同的模型（如 BERT 用于文本分类、ResNet 用于图像识别），若在业务代码中直接 `new BertModel()` 或 `new ResNetModel()`，会导致业务代码与具体模型类强耦合，每次新增模型都需修改业务逻辑，违反开闭原则（Open/Closed Principle）。

---

## 核心原理

### 简单工厂：静态创建方法

简单工厂通过一个静态方法根据传入参数决定创建哪个对象。其结构如下：

```python
class ModelFactory:
    @staticmethod
    def create(model_type: str):
        if model_type == "bert":
            return BertModel()
        elif model_type == "resnet":
            return ResNetModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
```

简单工厂的缺点在于，每增加一种新模型都必须修改 `ModelFactory` 内部的 `if-elif` 链，违反开闭原则。因此在需要频繁扩展模型类型的 AI 项目中，简单工厂只适合类型数量固定的场景。

### 工厂方法模式：委托子类决定实例化

工厂方法模式定义一个创建对象的接口（抽象方法），但将具体实例化推迟到子类实现。其关键结构遵循以下伪代码：

```python
from abc import ABC, abstractmethod

class BaseModelFactory(ABC):
    @abstractmethod
    def create_model(self):  # 工厂方法
        pass

class BertFactory(BaseModelFactory):
    def create_model(self):
        return BertModel(vocab_size=30522, hidden_size=768)

class ResNetFactory(BaseModelFactory):
    def create_model(self):
        return ResNetModel(layers=50)
```

新增模型类型时，只需新增一个工厂子类，不修改已有代码——这正是对"对扩展开放、对修改关闭"的精确体现。调用者持有 `BaseModelFactory` 类型引用，运行时多态决定实际创建哪个模型。

### 抽象工厂模式：创建产品族

抽象工厂在工厂方法基础上扩展，一个工厂负责创建**一组相互关联的对象**（称为"产品族"）。在 AI 工程中，典型例子是：NLP 流水线中的分词器（Tokenizer）与模型（Model）必须配套使用，BERT 分词器只能与 BERT 模型搭配，GPT 分词器只能与 GPT 模型搭配。

```python
class AbstractNLPFactory(ABC):
    @abstractmethod
    def create_tokenizer(self): pass
    
    @abstractmethod
    def create_model(self): pass

class BertNLPFactory(AbstractNLPFactory):
    def create_tokenizer(self): return BertTokenizer()
    def create_model(self): return BertModel()
```

抽象工厂保证了产品族内部的一致性约束：调用者只能获得同一工厂产出的配套对象，从根本上避免了"用 GPT 分词器处理 BERT 模型输入"这类错误搭配。

---

## 实际应用

**AI 框架中的模型注册机制**：PyTorch 和 Hugging Face Transformers 库大量使用了工厂模式变体。`AutoModel.from_pretrained("bert-base-uncased")` 本质上是一个工厂方法调用——`AutoModel` 根据模型名称字符串在内部注册表（`_model_type_to_module` 字典）中查找对应的具体模型类并实例化，调用者无需 `import BertModel`。

**数据预处理器工厂**：在机器学习流水线中，不同数据类型（文本、图像、表格）需要不同预处理器。可以构建 `PreprocessorFactory`，根据数据集配置文件中的 `data_type` 字段自动选择 `TextPreprocessor`、`ImagePreprocessor` 或 `TabularPreprocessor`，使同一套训练脚本支持多模态任务。

**强化学习环境工厂**：OpenAI Gym 的 `gym.make("CartPole-v1")` 正是简单工厂模式的经典实践——通过字符串 ID 屏蔽了 `CartPoleEnv` 等具体环境类的实例化细节，允许用户以统一接口切换不同仿真环境。

---

## 常见误区

**误区一：将简单工厂、工厂方法、抽象工厂混为一谈**。三者解决不同规模的问题：简单工厂只是封装 `if-else`；工厂方法解决单一产品的扩展问题（新增子类而非修改已有类）；抽象工厂解决多个相关产品必须配套创建的约束问题。在 AI 工程中选型时，若只有一类对象需要创建且类型较少，用简单工厂；若预计频繁新增类型，用工厂方法；若存在"分词器+模型"这样的配套约束，才考虑抽象工厂。

**误区二：认为工厂模式必须用类实现**。在 Python 中，工厂完全可以是一个函数或字典映射（注册表模式）。例如用 `MODEL_REGISTRY = {"bert": BertModel, "gpt2": GPT2Model}` 配合 `MODEL_REGISTRY[name](**kwargs)` 实现，代码量更少，且同样满足开闭原则——新增模型只需向字典注册，无需修改工厂函数本身。

**误区三：过度使用工厂模式导致类爆炸**。若系统中只有2-3种固定的模型类型，为每个模型创建独立工厂子类反而增加了无谓的类数量（工厂方法模式至少需要 N 个产品类 + N 个工厂类 + 1 个抽象工厂 = 2N+1 个类）。此时简单工厂或直接构造已足够，不必为了"使用设计模式"而引入不必要的复杂度。

---

## 知识关联

**前置基础——设计模式概述**：工厂模式属于 GoF 23 种设计模式中"创建型"分类下的具体模式，理解创建型模式统一关注"如何实例化对象"这一职责，有助于把握工厂模式与单例模式（Singleton）、原型模式（Prototype）的边界——工厂模式每次调用都创建新对象，而单例模式保证全局唯一实例。

**后续进阶——建造者模式（Builder Pattern）**：当工厂需要创建的对象本身构造过程极其复杂（如一个需要设置数十个超参数的深度学习模型配置对象），工厂模式只负责"选择创建哪个类"就会显得力不从心。建造者模式通过链式调用（`ModelBuilder().set_layers(50).set_dropout(0.1).build()`）解决复杂对象的**逐步构造**问题，是工厂模式在对象构造复杂度升高后的自然延伸。两者经常组合使用：工厂决定实例化哪个建造者，建造者负责具体构造过程。