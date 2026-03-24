---
id: "polymorphism"
concept: "多态"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 4
is_milestone: false
tags: ["OOP"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 多态

## 概述

多态（Polymorphism）是面向对象编程的三大特征之一（另外两个是封装和继承），其名称来源于希腊语，意为"多种形态"。多态允许同一个方法调用在运行时根据对象的实际类型执行不同的行为，使得一个接口能够服务于多种数据类型。Python 在设计上天然支持多态，无需像 Java 那样强制声明 `interface` 或 `abstract` 关键字也能实现完整的多态行为。

多态的概念最早由 Christopher Strachey 在 1967 年的论文《Fundamental Concepts in Programming Languages》中系统提出，他将其分为"参数多态"和"特设多态"两类。在 AI 工程领域，多态的价值体现在构建可扩展的模型框架上——例如，同一个 `train()` 方法可以被不同的模型类（`LinearModel`、`NeuralNet`、`DecisionTree`）各自以不同方式实现，上层代码无需修改即可切换底层模型。

多态的本质是**运行时绑定**（Runtime Binding），即方法的具体实现在程序运行时才确定，而非编译时。这与静态语言的早期绑定（Early Binding）形成对比，是构建灵活 AI 管道（Pipeline）的基础机制。

---

## 核心原理

### 方法覆盖（Method Overriding）

方法覆盖是实现多态最直接的方式，依赖于继承关系。子类重新定义父类中同名、同参数列表的方法，当通过父类引用调用该方法时，实际执行的是子类的版本。以下是一个 AI 工程中的典型例子：

```python
class BaseModel:
    def predict(self, X):
        raise NotImplementedError("子类必须实现 predict 方法")

class LinearModel(BaseModel):
    def predict(self, X):
        return X @ self.weights + self.bias

class NeuralNet(BaseModel):
    def predict(self, X):
        return self.forward_pass(X)
```

当代码执行 `model.predict(X)` 时，Python 解释器通过 **MRO（Method Resolution Order，方法解析顺序）** 查找实际类型并调用对应实现。Python 的 MRO 使用 C3 线性化算法，确保多重继承场景下的方法查找顺序唯一且一致。

### 鸭子类型（Duck Typing）

Python 多态的独特之处在于"鸭子类型"——"如果它走路像鸭子，叫声像鸭子，那它就是鸭子"。Python 不要求对象必须继承自同一父类，只要对象拥有被调用的方法名，多态就能生效：

```python
class TorchDataLoader:
    def __iter__(self): ...

class CustomCSVLoader:
    def __iter__(self): ...

def train_epoch(dataloader):
    for batch in dataloader:  # 无论哪种 loader，都能工作
        ...
```

这种设计使得 AI 工程中的数据加载器、评估器等组件可以自由替换，而无需强制继承同一基类。

### 运算符重载（Operator Overloading）

Python 通过特殊方法（Dunder Methods）支持运算符多态。例如，`__add__` 方法使得 `+` 运算符对不同对象产生不同行为：PyTorch 中的 `Tensor.__add__` 执行 GPU 加速的张量加法，而普通 Python `int.__add__` 执行标量加法。这是特设多态（Ad-hoc Polymorphism）的典型实现，底层通过 `type(obj).__add__(obj, other)` 动态分派。

### 抽象基类（Abstract Base Class）

Python 的 `abc` 模块提供 `ABC` 和 `abstractmethod` 装饰器，用于强制子类实现特定方法，将多态的"约定"变为"契约"：

```python
from abc import ABC, abstractmethod

class Optimizer(ABC):
    @abstractmethod
    def step(self, params, grads):
        pass  # SGD、Adam 等子类必须各自实现
```

如果子类未实现抽象方法，在实例化时会抛出 `TypeError`，而非等到运行时调用时才报错，这提前捕获了实现缺失的问题。

---

## 实际应用

**场景一：统一模型评估接口**

在 AI 工程的模型选择阶段，通常需要对比多种模型的性能。利用多态，可以编写一个通用的评估函数：

```python
def evaluate_all(models: list[BaseModel], X_test, y_test):
    for model in models:
        preds = model.predict(X_test)  # 多态调用
        print(f"{type(model).__name__}: accuracy={accuracy(preds, y_test):.4f}")
```

传入 `[LinearModel(), NeuralNet(), DecisionTree()]`，每个对象调用自己的 `predict` 实现，上层代码零修改。

**场景二：Scikit-learn 的 Estimator 协议**

Scikit-learn 通过鸭子类型多态设计了通用 `Pipeline`。任何实现了 `fit(X, y)` 和 `transform(X)` 或 `predict(X)` 方法的对象，都能插入 Pipeline 中。这正是 Scikit-learn 能支持 100+ 算法无缝互换的根本原因，而非通过复杂的类型检查机制。

**场景三：损失函数的多态替换**

```python
class MSELoss:
    def __call__(self, pred, target):
        return ((pred - target) ** 2).mean()

class CrossEntropyLoss:
    def __call__(self, pred, target):
        return -torch.sum(target * torch.log(pred))

def train(model, loss_fn, data):
    for X, y in data:
        loss = loss_fn(model(X), y)  # 同一调用，不同行为
```

通过重写 `__call__`，损失函数对象表现为可调用对象，训练循环对具体损失类型完全透明。

---

## 常见误区

**误区一：重载（Overloading）等同于覆盖（Overriding）**

方法覆盖（Overriding）发生在继承体系中，子类重写父类的同名方法，这是多态的核心机制。而方法重载（Overloading）是同一类中定义多个同名但参数不同的方法，Java 支持此特性，但 **Python 不支持传统意义上的方法重载**——后定义的同名方法会直接覆盖前者。Python 通过默认参数和 `*args/**kwargs` 模拟重载效果，但这与多态是两个不同的概念。

**误区二：多态必须依赖继承**

受 Java 等静态语言影响，很多初学者认为多态必须通过继承实现。但在 Python 中，鸭子类型允许完全独立的两个类（无任何继承关系），只要它们各自实现了相同名称的方法，就能在同一多态调用中工作。AI 工程中许多框架（如 HuggingFace Transformers）正是利用这一特性，让自定义模型无需继承框架基类也能无缝集成。

**误区三：多态会显著降低运行性能**

多态的运行时分派确实比直接调用有额外开销，但在 Python 中这一开销通常可忽略不计（每次方法查找约 50-200 纳秒量级），AI 工程中的性能瓶颈几乎永远在矩阵运算、I/O 或内存传输上，而非多态分派本身。过早为了"避免多态开销"而写出重复的条件分支代码，反而会破坏系统的可维护性。

---

## 知识关联

**与继承的关系**：多态的方法覆盖机制以继承为前提——只有子类继承父类后，覆盖父类方法才有意义。继承定义了"是什么"（is-a 关系），多态决定了"做什么"（运行时行为）。没有继承，仍可通过鸭子类型实现多态，但抽象基类强制约束需要继承 `ABC`。

**与封装的协同**：多态通常与封装配合使用——父类将内部实现细节封装，对外暴露统一接口，子类在封装边界内自由替换实现。这是"对接口编程，而非对实现编程"设计原则的直接体现。

**在 AI 工程中的延伸**：掌握多态后，可以进一步学习设计模式中的**策略模式（Strategy Pattern）**和**工厂模式（Factory Pattern）**，这两种模式都是多态的高级应用形式，广泛用于 AI 框架中的算法选择和对象创建场景。
