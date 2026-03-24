---
id: "abstraction"
concept: "抽象"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 4
is_milestone: false
tags: ["OOP"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 抽象

## 概述

抽象（Abstraction）是面向对象编程中的一种设计原则，指通过隐藏实现细节、只暴露对象的本质特征和行为接口，使程序员能以简化的视角操作复杂系统。在Python中，抽象通常通过抽象基类（Abstract Base Class，简称ABC）实现，借助`abc`模块的`ABCMeta`元类和`@abstractmethod`装饰器来定义不可直接实例化的抽象类。

抽象的思想在计算机科学中由Edsger Dijkstra等人在1968年结构化编程运动期间系统提出。在面向对象编程语言兴起后，抽象被正式纳入Booch、Rumbaugh等人提出的OOP四大基本特性之一（另外三个是封装、继承、多态）。Python在2.6版本引入了`abc`模块，提供了语言级别的抽象支持。

抽象在AI工程中尤为重要。构建一个机器学习流水线时，数据加载器、模型训练器、评估器等组件可以通过抽象类定义统一接口，使得切换不同的具体实现（例如从PyTorch换成TensorFlow的模型训练器）无需修改调用方代码。这一特性直接降低了复杂AI系统的维护成本与耦合度。

---

## 核心原理

### 抽象类与抽象方法

抽象类是不能被直接实例化的类，其存在目的是作为一组相关子类的"合同模板"。在Python中，定义抽象类需要继承`ABC`（或显式指定`metaclass=ABCMeta`），并用`@abstractmethod`标记必须由子类实现的方法：

```python
from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def train(self, data):
        pass

    @abstractmethod
    def predict(self, x):
        pass
```

若子类未实现所有`@abstractmethod`方法，尝试实例化该子类时Python将抛出`TypeError`，而非等到运行时才报错。这一机制将接口违约从运行时错误提前至定义阶段。

### 数据抽象与过程抽象的区别

**数据抽象**关注"是什么"——将数据及其操作捆绑为一个抽象类型，隐藏内部存储结构。例如，`Stack`抽象类只暴露`push`、`pop`、`is_empty`接口，不论底层用列表还是链表实现，调用者无需知晓。

**过程抽象**关注"怎么做"——将一段操作的细节封装为一个命名单元（函数或方法），调用方只需知道输入输出契约。例如，`normalize(data)`方法将归一化的具体计算步骤（减均值除标准差，公式为 $\hat{x} = (x - \mu) / \sigma$）对调用者不可见。

两者结合时，抽象类同时提供数据结构的隐藏与行为接口的规范，是OOP中最完整的抽象形式。

### 抽象层次（Levels of Abstraction）

良好的系统设计遵循"每个模块只与相邻抽象层次交互"的原则。在AI工程中，常见抽象层次从低到高依次为：

1. **硬件层**：GPU张量计算
2. **框架层**：PyTorch/TensorFlow算子
3. **模型层**：`nn.Module`子类
4. **任务层**：`Trainer`、`Evaluator`抽象类
5. **应用层**：实验管理脚本

若`Trainer`抽象类直接依赖GPU的底层CUDA调用（跨越多层），则违反了抽象层次原则，导致代码在CPU环境下无法运行且难以测试。

---

## 实际应用

**统一AI模型接口：** 在构建多模型对比实验框架时，可定义如下抽象类：

```python
class AIModel(ABC):
    @abstractmethod
    def fit(self, X_train, y_train): pass

    @abstractmethod
    def score(self, X_test, y_test) -> float: pass
```

`RandomForestModel`、`SVMModel`、`NeuralNetModel`分别继承`AIModel`并实现`fit`和`score`。实验主循环只需遍历`List[AIModel]`，不关心各模型内部训练逻辑，新增模型时不修改主循环代码。

**数据预处理管道抽象：** scikit-learn中的`BaseEstimator`和`TransformerMixin`是抽象化的典型案例，规定所有变换器必须实现`fit()`和`transform()`方法。用户自定义的标准化器、特征选择器只需继承这两个混入类，即可无缝接入`Pipeline`对象。

---

## 常见误区

**误区一：抽象类等于接口。** 抽象类可以包含有具体实现的方法和实例属性，而纯接口（如Java的`interface`）只允许方法签名。Python的ABC可以同时提供默认行为（具体方法）和强制实现的契约（抽象方法），两者职责不同。混淆二者会导致设计者要么在抽象类中放入过多具体逻辑，要么将本应共享的默认实现重复写在每个子类中。

**误区二：抽象越多越好。** 过度抽象会产生"抽象税"——为了实例化一个功能，需要追踪5层继承链才能找到实际代码。著名的"FizzBuzz企业版"反例展示了将一个3行问题过度抽象为15个类的荒谬。合理的标准是：当一个行为确实有2个以上不同的具体实现，且调用方需要统一对待时，才引入抽象类。

**误区三：`@abstractmethod`方法体必须为空。** Python允许抽象方法拥有方法体，子类可通过`super().method()`调用它。这一特性常用于提供默认逻辑的同时强制子类显式覆盖——例如抽象`validate()`方法提供通用字段检查，子类必须调用并追加领域特定验证规则。

---

## 知识关联

**前置概念——类与对象：** 抽象类本质上仍是类，继承了类的所有语法规则。理解`__init__`、方法解析顺序（MRO）和继承语法是使用`ABC`的前提。抽象类通过`ABCMeta`修改了类的实例化行为，若不熟悉Python元类机制，`TypeError: Can't instantiate abstract class`报错会令人困惑。

**后续概念——接口：** Python中没有`interface`关键字，通常用"只含抽象方法、无具体实现"的抽象类来模拟接口。学习接口设计（如`Iterable`、`Comparable`等协议接口）是抽象思想的自然延伸，也是理解Python鸭子类型与静态类型检查工具（如`mypy`）如何协同工作的关键步骤。抽象类定义了"必须实现什么"，而接口协议进一步规范了"类型系统如何验证实现"。
