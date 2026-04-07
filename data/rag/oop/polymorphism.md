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
quality_tier: "A"
quality_score: 79.6
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

# 多态

## 概述

多态（Polymorphism）是面向对象编程中允许同一个接口或方法名，根据调用对象的实际类型表现出不同行为的机制。词源来自希腊语 "poly"（多）+ "morphe"（形态），字面意思就是"多种形态"。在Python中，多态通过鸭子类型（Duck Typing）和方法重写（Method Overriding）共同实现，而在Java、C++等静态类型语言中则依赖虚函数表（vtable）机制。

多态的理论基础由Alan Kay在设计Smalltalk语言（1972年）时系统化，他将其确立为面向对象编程的三大支柱之一（另外两个是封装和继承）。在AI工程场景中，多态使得不同的模型类（如`LinearRegressor`、`RandomForest`、`NeuralNetwork`）可以共享统一的`fit(X, y)`和`predict(X)`接口，调用方代码无需关心底层实现细节。

多态之所以在AI工程中极为重要，是因为它支撑了sklearn的`Pipeline`和`Estimator`架构——sklearn中所有估计器都实现了相同的接口规范，这使得用`SVC`替换`LogisticRegression`时调用代码无需修改一行，仅靠多态即可完成模型切换。

---

## 核心原理

### 方法重写（Method Overriding）

子类重新定义父类中已有方法，是实现运行时多态的基本手段。当父类引用指向子类对象并调用该方法时，执行的是子类版本，而非父类版本。这种"晚绑定"（Late Binding）发生在运行时，而非编译时。

```python
class BaseModel:
    def predict(self, X):
        raise NotImplementedError("子类必须实现predict方法")

class LinearModel(BaseModel):
    def predict(self, X):
        return X @ self.weights  # 矩阵乘法

class TreeModel(BaseModel):
    def predict(self, X):
        return self._traverse_tree(X)  # 树遍历
```

调用 `model.predict(X)` 时，Python解释器在运行时查找 `model` 的真实类型，动态决定调用哪个 `predict`，这正是多态的核心行为。

### 鸭子类型（Duck Typing）与结构多态

Python不要求显式的继承关系来实现多态——"如果它走路像鸭子，叫声像鸭子，那它就是鸭子"。只要对象拥有被调用的方法，Python就接受它，这称为结构多态（Structural Polymorphism）或隐式接口。

```python
def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)   # 不检查model的类型
    return accuracy_score(y_test, predictions)

# 以下三种对象都能传入，无需继承同一父类
evaluate_model(sklearn_svm, X, y)
evaluate_model(pytorch_wrapper, X, y)
evaluate_model(custom_rule_engine, X, y)
```

这与Java的接口多态不同：Java需要显式声明 `implements Predictor`，Python只需对象存在 `predict` 方法即可。

### 参数多态与函数重载

Python原生不支持基于参数类型的函数重载（同名函数不同签名），但可以通过 `functools.singledispatch`（Python 3.4引入）模拟：

```python
from functools import singledispatch

@singledispatch
def process_input(data):
    raise TypeError(f"不支持类型: {type(data)}")

@process_input.register(np.ndarray)
def _(data):
    return data.astype(float)   # 处理numpy数组

@process_input.register(list)
def _(data):
    return np.array(data, dtype=float)  # 处理Python列表
```

`singledispatch` 根据第一个参数的运行时类型选择对应实现，这是Python中实现参数多态的标准方式。

---

## 实际应用

**sklearn中的Estimator多态**：sklearn要求所有模型类实现 `fit(X, y)` 和 `predict(X)` 方法。`GridSearchCV` 接受任意满足此接口的估计器对象，内部调用 `estimator.fit()` 而不关心它是SVM还是决策树。这种设计让同一套超参数搜索代码能服务于上百种不同算法，是工业级AI系统可扩展性的直接来源。

**深度学习框架中的Layer多态**：PyTorch的`nn.Module`要求子类实现`forward(x)`方法。`nn.Sequential`在前向传播时依次调用每个层的`forward`，但它只持有`nn.Module`类型的引用，实际执行的是`Conv2d`、`BatchNorm2d`、`ReLU`各自的`forward`实现。这使得构建任意复杂的网络结构时，`Sequential`本身的代码无需改动。

**回调与钩子的多态扩展**：在Keras/PyTorch Lightning中，`Callback`基类定义了`on_epoch_end`、`on_train_begin`等方法，用户通过重写这些方法注入自定义逻辑（如早停、学习率调度、日志记录），训练循环代码调用`callback.on_epoch_end()`时自动分发到对应子类实现，完全解耦了训练框架与用户定制逻辑。

---

## 常见误区

**误区一：多态等同于方法重写**。方法重写是实现多态的手段之一，但多态本身是指"通过统一接口操作不同类型对象"的能力。如果重写后的子类方法不通过父类引用调用，多态效果就没有发挥。在Python中，即使没有继承关系，通过鸭子类型同样能实现多态，说明多态的本质在于接口的一致性，而非类的层级结构。

**误区二：Python中覆盖父类方法时不需要调用`super()`**。这一误区在AI工程中尤其危险。`__init__`方法中如果忘记调用`super().__init__()`，父类的初始化逻辑会被完全跳过。例如继承`nn.Module`时必须调用`super().__init__()`，否则PyTorch的参数注册机制无法正常工作，导致`model.parameters()`返回空迭代器，训练时梯度无法传播。

**误区三：多态会带来显著的性能开销**。在Python中，方法查找通过MRO（方法解析顺序，Method Resolution Order）进行，每次调用都需要在`__dict__`链中查找方法。但在实际AI工程中，模型推断的性能瓶颈几乎永远在矩阵运算（由C/CUDA实现）而非Python层的方法分发，多态引入的调用开销通常可以忽略不计。

---

## 知识关联

多态依赖继承提供的父子类关系作为基础——没有继承建立的类型层次结构，就无法通过父类引用实现运行时多态。Python的MRO算法（C3线性化，由Samuele Pedroni于2002年在Python 2.3中引入）决定了多层继承时方法的查找顺序，直接影响多态的行为结果。

在AI工程的进阶实践中，多态是设计模式的基础语言：策略模式（Strategy Pattern）用多态替换条件分支，让不同的优化算法（SGD、Adam、RMSProp）通过统一的`step()`接口可互换；工厂模式（Factory Pattern）利用多态在运行时根据配置创建不同的模型对象，是ML系统配置化的核心手段。理解多态的行为边界，是从"能写代码"到"能设计可扩展AI系统架构"的关键跨越。