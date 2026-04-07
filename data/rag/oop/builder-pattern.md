---
id: "builder-pattern"
concept: "建造者模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 3
is_milestone: false
tags: ["builder", "fluent-api", "design-pattern"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 建造者模式

## 概述

建造者模式（Builder Pattern）是一种创建型设计模式，专门用于分步骤构建复杂对象，其核心思想是将对象的**构建过程**与该对象的**最终表示**彻底分离。当一个对象需要多个可选参数、多个构建步骤或需要支持多种不同表示时，建造者模式可以避免"构造函数爆炸"——即因参数组合过多导致需要数十个重载构造函数的困境。

建造者模式由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式归类。GoF给出的经典意图是：将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。该书将其列为23种经典设计模式中的第3类创建型模式之一。

在AI工程实践中，建造者模式尤为重要。构建一个机器学习训练管道（Training Pipeline）往往涉及数据加载器、预处理步骤、模型结构、优化器、损失函数等十余个可选组件，每种组件都有多种候选实现。若使用普通构造函数，仅超参数组合就可能产生数百种函数签名；使用建造者模式则可以用流畅的链式调用逐步配置，最终调用 `build()` 生成一致的训练对象。

---

## 核心原理

### 四个角色及其职责

建造者模式标准结构由四个角色构成：

- **Product（产品）**：最终被构建的复杂对象，如 `NeuralNetworkConfig`。
- **Builder（抽象建造者）**：定义创建产品各部件的抽象接口，如 `abstract buildOptimizer()`、`abstract buildLoss()`。
- **ConcreteBuilder（具体建造者）**：实现Builder接口，负责具体部件的构造与组装，如 `AdamModelBuilder`。
- **Director（指挥者）**：按照固定顺序调用Builder中的方法，封装构建流程，但不关心具体实现，如 `TrainingDirector.construct(builder)`。

Director与ConcreteBuilder之间是**依赖注入**关系——Director只持有Builder的抽象接口引用，运行时注入不同的ConcreteBuilder即可产出不同产品，这正是"同样构建过程，不同表示"的实现机制。

### 流式建造者（Fluent Builder）变体

现代Python和Java代码中更常见的是省略Director的**流式建造者**，每个设置方法返回 `self`（Python）或 `this`（Java），支持方法链调用：

```python
config = (ModelConfigBuilder()
          .set_layers([256, 128, 64])
          .set_dropout(0.3)
          .set_optimizer("adam", lr=1e-3)
          .set_loss("cross_entropy")
          .build())
```

`build()` 方法在最后执行参数校验，例如检测 `dropout` 是否在 `[0, 1)` 区间、`layers` 列表是否非空，若校验失败则抛出 `ValueError`，而非等到训练开始时才出错。这种"构建时验证"是流式建造者相比直接赋值属性的关键优势。

### 与工厂模式的结构差异

工厂模式（Factory Pattern）一次性调用单个方法返回对象，适合构建步骤简单、产品类型依类型参数区分的场景；建造者模式则通过**多次方法调用逐步积累状态**，适合同一类型产品但内部配置高度可变的场景。用Python中的 `dataclass` 来比喻：工厂模式相当于调用 `__init__` 时一次性传入全部参数，建造者模式相当于逐字段赋值后调用 `frozen=True` 的 `replace()` 生成最终不可变对象。二者解决的问题规模不同，并非替代关系。

---

## 实际应用

### LLM推理客户端构建

在调用大型语言模型API时，请求对象包含 `model`、`temperature`、`max_tokens`、`system_prompt`、`tools`、`response_format` 等十余个可选字段。以下是使用建造者模式构建OpenAI请求对象的典型实现：

```python
request = (ChatRequestBuilder(model="gpt-4o")
           .with_system("你是一个代码审查助手")
           .with_temperature(0.2)
           .with_max_tokens(2048)
           .with_json_response()
           .build())
```

若某项目同时支持OpenAI和本地Ollama两套API，只需实现 `OpenAIRequestBuilder` 和 `OllamaRequestBuilder` 两个ConcreteBuilder，Director中的构建逻辑完全不变，切换后端只需替换注入的Builder实例。

### PyTorch数据管道构建

`torchvision.transforms.Compose` 本质上是一种简化的建造者模式——将多个变换步骤逐一添加后组合成最终的变换管道。更完整的建造者应用是构建 `DataLoader`：批大小、采样策略、`num_workers`、`pin_memory` 等参数适合通过建造者按需配置，并在 `build()` 时验证 `num_workers` 不超过系统CPU核心数（如 `os.cpu_count()`）。

---

## 常见误区

**误区一：认为建造者模式必须包含Director类。** 在实际AI工程代码（尤其是Python生态）中，Director往往被省略，直接由调用方通过方法链控制构建顺序。GoF定义的四角色结构适合Java等强类型语言中需要严格封装构建流程的场景；Python中的流式建造者变体同样合法，且更符合"Pythonic"风格。

**误区二：将建造者模式用于参数较少的简单对象。** 当一个对象只有2-3个必填参数时，引入Builder会增加不必要的类数量和代码量。建造者模式的收益随**可选参数数量**增加而显著提升，通常以超过4个可选参数作为引入该模式的经验阈值。对于简单对象，使用Python的关键字参数默认值（`def __init__(self, lr=1e-3, dropout=0.0)`）即可满足需求。

**误区三：`build()` 方法可有可无，随时都能获取半成品对象。** 建造者模式的一个重要契约是：只有调用 `build()` 之后，产品对象才处于完整、有效的状态。若允许外部直接访问中间状态的产品，校验逻辑就无法集中执行，导致运行时出现意外的 `None` 属性错误，彻底破坏了建造者模式的防御性构建优势。

---

## 知识关联

建造者模式直接依赖**设计模式概述**中介绍的创建型模式分类框架——理解"创建型模式负责对象实例化逻辑"是正确选择建造者模式使用场景的前提。与**工厂模式**的对比理解同样关键：工厂模式通过多态决定"创建哪种类型"，建造者模式通过分步配置决定"如何组装同一类型的内部结构"，两者在AI工程中经常组合使用——工厂方法负责选择并返回合适的Builder实例，Builder负责装配具体产品。

在Python AI工程栈中，`sklearn.pipeline.Pipeline`、Hugging Face的 `TrainingArguments`（通过`dataclasses`实现的建造者变体）以及LangChain的 `LLMChain` 构建流程，均体现了建造者模式的设计思想，是学习完本模式后可直接对照阅读的真实代码案例。