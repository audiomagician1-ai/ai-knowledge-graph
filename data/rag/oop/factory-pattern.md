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
content_version: 3
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

工厂模式（Factory Pattern）是一种创建型设计模式，其核心目的是将对象的**创建逻辑**与**使用逻辑**解耦。调用方无需知道具体类的名称，只需向工厂请求所需类型的对象，工厂负责实例化并返回。这一模式最早由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式归类，在该书中被拆分为"简单工厂"、"工厂方法"和"抽象工厂"三个相关变体。

工厂模式在AI工程领域尤为重要，因为深度学习框架中存在大量需要根据配置动态创建的对象——例如根据字符串名称动态创建不同的优化器（Adam、SGD、RMSProp）、损失函数或数据增强策略。如果直接在业务代码中写 `if optimizer == "adam": return Adam(lr)` 这样的分支，当新增优化器类型时必须修改已有代码，违反了开放-封闭原则（OCP）。工厂模式通过将这些分支逻辑集中到工厂类中，使系统对扩展开放、对修改封闭。

## 核心原理

### 三种变体及其结构差异

**简单工厂（Simple Factory）**并非GoF正式模式，而是一个静态方法根据传入参数决定返回哪个子类实例。其结构仅有一个工厂类，包含一个静态方法 `create(type: str) -> Product`。优点是实现简单，缺点是每新增一种产品都必须修改工厂类本身。

**工厂方法（Factory Method）**是GoF正式收录的模式，其核心结构包含四个角色：
- `Creator`（抽象创建者）：声明抽象方法 `factory_method() -> Product`
- `ConcreteCreator`（具体创建者）：重写 `factory_method()` 返回特定子类
- `Product`（抽象产品）：定义产品接口
- `ConcreteProduct`（具体产品）：实现产品接口

工厂方法将"选择实例化哪个子类"的决策延迟到子类，调用方只依赖 `Creator` 抽象类，从而彻底隔离了对具体产品类的直接依赖。

**抽象工厂（Abstract Factory）**处理"产品族"问题。当系统需要同时创建多个相互关联的对象时使用——例如同时创建 `PyTorchOptimizer` + `PyTorchScheduler`，或 `TensorFlowOptimizer` + `TensorFlowScheduler`，保证同族产品之间的兼容性。抽象工厂接口声明多个 `create_X()` 方法，每个具体工厂实现整个产品族的创建。

### 注册表工厂（Registry Pattern）

在AI工程中，更常见的实现是"注册表工厂"，它结合了工厂模式与装饰器语法：

```python
_registry = {}

def register(name):
    def decorator(cls):
        _registry[name] = cls
        return cls
    return decorator

def create(name, **kwargs):
    return _registry[name](**kwargs)

@register("adam")
class AdamOptimizer:
    def __init__(self, lr=0.001): ...
```

使用 `@register("adam")` 装饰器时，新增优化器无需修改工厂函数，完全符合OCP。PyTorch的 `torch.optim` 模块以及Hugging Face的 `AutoModel.from_pretrained()` 背后均使用了类似的注册机制。

### 工厂模式与直接实例化的对比

直接调用 `Adam(lr=0.001)` 在调用方产生了对 `Adam` 类的硬依赖，单元测试时无法注入Mock对象。工厂模式使依赖方向反转：调用方依赖抽象工厂接口，具体产品类可随时替换。这在AI实验管理中极为关键——通过修改配置文件中的 `"optimizer": "sgd"` 即可切换训练策略，无需改动训练循环代码。

## 实际应用

**场景1：AI模型组件动态加载**

```python
# 基于配置文件创建不同的激活函数
class ActivationFactory:
    _map = {
        "relu": nn.ReLU,
        "gelu": nn.GELU,
        "silu": nn.SiLU,
    }
    @classmethod
    def create(cls, name: str) -> nn.Module:
        if name not in cls._map:
            raise ValueError(f"Unknown activation: {name}")
        return cls._map[name]()
```

这种写法让模型架构配置文件中的 `"activation": "gelu"` 可以直接驱动模型构建，LLM研究中切换激活函数（如从ReLU到SwiGLU）只需修改配置，不动模型代码。

**场景2：数据加载器工厂**

不同数据集（ImageNet、COCO、自定义CSV）的加载逻辑完全不同，但训练脚本只需调用 `DataLoaderFactory.create(config.dataset_type, **config.dataset_args)` 获得统一接口的 `DataLoader` 对象，训练主循环对数据集类型一无所知。

**场景3：Scikit-learn的`make_pipeline`与`clone`**

Scikit-learn的 `sklearn.base.clone(estimator)` 函数本质上是一个工厂方法，它通过读取 `estimator.get_params()` 重新构造相同类型和参数的新对象，避免了在交叉验证中复用同一实例导致的数据泄漏问题。

## 常见误区

**误区1：将简单工厂误认为等同于工厂方法**

简单工厂中的静态 `create()` 方法每次新增产品都必须修改工厂类，违反OCP；工厂方法通过新增 `ConcreteCreator` 子类扩展，不修改已有代码。两者的区别不是名称问题，而是扩展方式的根本不同。很多教程将简单工厂称为"工厂模式"，导致初学者误以为工厂模式必然存在大量 `if-elif` 分支。

**误区2：抽象工厂适用于所有多产品场景**

抽象工厂的价值在于保证**同族产品的约束关系**，而不是"只要有多种产品就用抽象工厂"。如果 `OptimizerFactory` 和 `SchedulerFactory` 之间没有必须配对的约束，独立的工厂方法更合适，强行引入抽象工厂只会增加4-6个额外类，造成过度设计。

**误区3：工厂模式会隐藏对象创建细节导致调试困难**

工厂模式确实将实例化集中到工厂类，但这反而使调试更方便——所有对象创建的日志、监控、参数校验逻辑都可以统一在工厂入口处添加，而不是散落在数十个调用点。在AI实验中，工厂可在 `create()` 时自动记录所有超参数，实现实验可复现性。

## 知识关联

工厂模式建立在**设计模式概述**中介绍的创建型模式分类和开放-封闭原则之上，掌握UML类图中的继承、聚合关系是读懂工厂方法四角色结构的前提。工厂模式处理的是**单步创建**问题——一次调用返回完整可用对象。

后续的**建造者模式（Builder Pattern）**解决的是**多步骤创建**问题：当对象的构造需要经历多个有序步骤、且中间状态有意义时（如逐层添加神经网络层构建模型），建造者模式通过 `Builder.add_layer().set_optimizer().build()` 的链式调用分离构造过程与表示。两者的关键区别在于：工厂模式的 `create()` 是原子操作，建造者模式的 `build()` 是多步骤过程的终点。在复杂AI系统中，常见的组合是**建造者模式内部调用工厂模式**——`ModelBuilder` 在每一步中使用 `LayerFactory.create(config)` 创建具体层对象。
