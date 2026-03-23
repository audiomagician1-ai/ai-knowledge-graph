---
id: "inheritance"
concept: "继承"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 4
is_milestone: false
tags: ["OOP"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.9
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 继承

## 概述

继承（Inheritance）是面向对象编程中子类自动获得父类属性和方法的机制，通过 `class Child(Parent)` 这样的语法建立"是一种"（is-a）关系。继承创建的是类层次结构：子类不仅拥有父类的全部非私有成员，还可以新增自己独特的属性和方法，或者覆盖父类已有的方法。

继承概念由 Ole-Johan Dahl 和 Kristen Nygaard 在1967年设计 Simula 67 语言时首次正式引入，这也是世界上第一个面向对象语言。Python 3 中所有类默认隐式继承自 `object` 基类，这意味着即使你写 `class Dog:` 也等价于 `class Dog(object):`，所有类天然拥有 `__str__`、`__repr__`、`__eq__` 等魔术方法。

继承在AI工程中具有直接的实用价值：PyTorch 所有神经网络模块都必须继承 `nn.Module`，TensorFlow 的自定义层必须继承 `tf.keras.Layer`。这种强制继承保证子类能被框架的训练循环、参数管理、序列化等基础设施自动识别和处理，而不是依赖鸭子类型的约定。

---

## 核心原理

### 方法解析顺序（MRO）

Python 使用 **C3线性化算法**决定多继承时的方法查找顺序。给定 `class D(B, C):`，Python 调用 `D.__mro__` 可以查看完整的解析链。C3算法保证两个规则：子类永远在父类之前，同级父类按声明顺序排列。

例如：
```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
# D.__mro__ = (D, B, C, A, object)
```

在PyTorch自定义层中，如果同时继承 `nn.Module` 和一个自定义 `Mixin` 类，MRO顺序直接决定 `__init__` 和 `forward` 哪个版本被调用，错误的顺序会导致模型参数无法注册。

### `super()` 与协作式多继承

`super()` 不是"调用父类方法"，而是"按MRO顺序调用下一个类的方法"。这一区别在多继承时至关重要。

```python
class ModelBase(nn.Module):
    def __init__(self, device):
        super().__init__()   # 沿MRO传递调用，最终到达 nn.Module.__init__
        self.device = device
```

如果子类 `__init__` 忘记调用 `super().__init__()`，PyTorch的 `nn.Module` 内部的 `_parameters`、`_modules` 字典将不会被创建，后续调用 `.parameters()` 或 `.to(device)` 时会抛出 `AttributeError`。

### 方法覆盖（Override）与 `super()` 扩展

子类可以完全覆盖父类方法，也可以先调用 `super()` 再扩展。两种策略有本质区别：

| 策略 | 适用场景 | 代码模式 |
|------|---------|---------|
| 完全覆盖 | 父类逻辑完全不适用 | 直接定义同名方法 |
| 扩展覆盖 | 在父类基础上增加行为 | `super().method()` + 新逻辑 |

在AI工程中，自定义 `Dataset` 类必须覆盖 `__len__` 和 `__getitem__` 两个抽象方法，PyTorch 的 `DataLoader` 内部依赖这两个方法来分批和打乱数据。如果只覆盖其中一个，运行时会抛出 `TypeError: Can't instantiate abstract class`。

### 访问控制：名称修饰（Name Mangling）

Python 没有真正的 `private` 关键字，但双下划线前缀（`__attr`）会触发名称修饰机制，将属性重命名为 `_ClassName__attr`。这实际上阻止了子类直接访问该属性。

```python
class Trainer:
    def __init__(self):
        self.__learning_rate = 0.001   # 存储为 _Trainer__learning_rate

class CustomTrainer(Trainer):
    def show_lr(self):
        print(self.__learning_rate)    # AttributeError！
        print(self._Trainer__learning_rate)  # 可以访问
```

单下划线 `_attr` 只是约定（"请勿外部访问"），并不触发名称修饰，子类可以直接访问。

---

## 实际应用

**构建神经网络层的标准模式**是继承在AI工程中最典型的用法。自定义注意力层必须：

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()                    # 必须调用，注册参数字典
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)

    def forward(self, query, key, value):
        # 具体实现
        pass
```

`nn.Module` 父类的 `__setattr__` 被重写，能自动检测到 `self.W_q = nn.Linear(...)` 这样的赋值，将其注册进 `_modules` 字典——这是继承父类行为后获得的"隐式能力"。

**scikit-learn 自定义变换器**也依赖继承 `BaseEstimator` 和 `TransformerMixin`：继承 `TransformerMixin` 后只需实现 `fit` 和 `transform`，就自动获得 `fit_transform` 方法（父类用这两个方法组合实现的），可直接插入 `Pipeline`。

---

## 常见误区

**误区1：继承等于代码复用，复用就该用继承**

继承建立的是强耦合的"是一种"关系，修改父类可能意外破坏所有子类。如果目的只是复用某几个方法，而子类和父类之间没有真正的分类关系，应使用组合（将对象作为属性持有）而非继承。例如，`DataLoader` 不继承 `Dataset`，因为加载器不"是一种"数据集，而是"持有"数据集。

**误区2：`super()` 只调用直接父类**

很多人认为 `super().__init__()` 只调用直接父类的 `__init__`，但实际上在菱形继承结构中，`super()` 按MRO顺序传递调用，每个中间类也会被执行一次。如果某个中间类没有调用 `super().__init__()`，就会打断这条调用链，导致某些祖先类的初始化被跳过——这是多继承中最难调试的bug之一。

**误区3：子类会继承私有方法（双下划线）**

双下划线方法（如 `__compute`）因名称修饰机制，在子类中以 `_ParentClass__compute` 的形式存在，无法通过 `self.__compute()` 直接调用。这不同于Java的 `private`：Python的双下划线不阻止子类覆盖，只阻止子类用原名访问。

---

## 知识关联

**前置概念**：理解继承需要先掌握类与对象——特别是 `__init__` 方法和实例属性的初始化机制，因为继承中最容易出错的正是子类 `__init__` 与父类 `__init__` 的协调调用。

**后续概念**：继承自然引出**多态**——子类覆盖父类方法后，父类引用调用同名方法时执行子类版本，这正是PyTorch `forward` 分发机制的工作方式。**模板方法模式**将继承的方法覆盖系统化：父类定义算法骨架（如 `fit` 的步骤顺序），子类覆盖具体步骤，整体流程由父类控制。**组合优于继承**原则则是对继承滥用的矫正——当你能明确说出两个类之间"是一种"关系时才使用继承，否则用对象组合来获得更松散的耦合。
