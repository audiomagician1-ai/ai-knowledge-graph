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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 继承

## 概述

继承（Inheritance）是面向对象编程中的一种机制，允许一个类（子类/派生类）自动获取另一个类（父类/基类）的属性和方法，并在此基础上添加或覆盖特定行为。用Python语法表示最简单的继承结构为 `class Dog(Animal):` ——括号内的 `Animal` 就是父类，`Dog` 自动继承了 `Animal` 的所有非私有成员。

继承的思想最早在1967年的 Simula 语言中由 Ole-Johan Dahl 和 Kristen Nygaard 提出，随后被 Smalltalk（1972年）、C++（1983年）和 Java（1995年）进一步完善。继承的核心价值在于**代码复用**和**类型层次建模**：当多个类共享相同属性时，将公共逻辑上移到父类，可以消除重复代码，并且子类实例在类型检查中可以被视为父类类型（`isinstance(dog, Animal)` 返回 `True`）。

在AI工程实践中，继承广泛出现于框架设计中。例如，PyTorch 要求所有自定义神经网络模块都必须继承 `torch.nn.Module`，通过重写 `forward()` 方法来定义前向传播逻辑，这是一个强制使用继承的经典案例。

---

## 核心原理

### 属性与方法的继承规则

子类继承父类的所有**公有（public）和受保护（protected）**成员。以Python为例，单下划线前缀（`_method`）表示受保护，双下划线前缀（`__method`）触发名称改写（name mangling），变为 `_ClassName__method`，子类无法直接以原名访问。子类实例化时，Python的方法解析顺序（MRO，Method Resolution Order）按照 C3 线性化算法确定查找链，可通过 `ClassName.__mro__` 查看完整顺序。

### 方法重写（Override）与 super() 调用

子类可以定义与父类**同名的方法**，从而覆盖父类行为，这称为方法重写。若需在重写时保留父类逻辑，使用 `super()` 函数向上调用：

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)   # 调用 Animal.__init__
        self.breed = breed
```

不调用 `super().__init__()` 是新手最常见的错误，会导致父类初始化的属性（如 `self.name`）未被赋值。在多重继承场景下，`super()` 会严格按照 MRO 顺序向上传递调用，而非简单地调用"父类"。

### 单继承与多重继承

Python 支持多重继承，语法为 `class C(A, B):`，而 Java 只允许单继承（接口实现不计）。多重继承的最大风险是**菱形继承问题（Diamond Problem）**：若 `A` 和 `B` 都继承自 `Base`，且都重写了 `speak()` 方法，`C` 继承 `A, B` 时需要 MRO 来确定调用哪个版本。MRO的计算规则保证 `Base.speak()` 只被调用一次，避免重复初始化。

### 抽象类与强制接口

Python通过 `abc` 模块（Abstract Base Classes）实现抽象类。使用 `@abstractmethod` 装饰的方法必须在子类中被重写，否则子类实例化时会抛出 `TypeError`。例如：

```python
from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def predict(self, X):
        pass

class LinearRegression(Model):
    def predict(self, X):          # 必须实现，否则报错
        return X @ self.weights
```

抽象类本身无法被直接实例化（`Model()` 会报 `TypeError: Can't instantiate abstract class`），它只能作为继承的模板强制约束子类行为。

---

## 实际应用

**Scikit-learn 的估计器体系**：所有 Scikit-learn 模型都继承自 `BaseEstimator`，并根据功能混入 `ClassifierMixin`、`RegressorMixin` 等。通过继承 `BaseEstimator`，自定义模型自动获得 `get_params()` 和 `set_params()` 方法，使其兼容 `GridSearchCV` 等超参数搜索工具，无需重新实现这些方法。

**PyTorch 自定义层**：继承 `torch.nn.Module` 后，只需重写 `forward()`，就自动获得参数注册（`.parameters()` 返回所有可训练张量）、模型状态保存（`.state_dict()`）、GPU迁移（`.cuda()`）等功能。这些功能全部定义在父类 `nn.Module` 中，包含约1500行代码，子类通过继承零成本复用。

**数据加载器**：PyTorch 的 `Dataset` 是一个抽象基类，要求子类必须实现 `__len__()` 和 `__getitem__()` 两个方法。自定义图像数据集继承 `Dataset` 后，可直接传入 `DataLoader` 使用批量加载、shuffle、多进程等功能。

---

## 常见误区

**误区一：继承等同于代码复用，应尽量多用**
继承实际上建立了**强耦合**关系：父类的任何修改都会影响所有子类。当继承层级超过3层时，代码的可读性和可维护性急剧下降。"Is-A"关系（狗是动物）才适合继承；若是"Has-A"关系（汽车有发动机），应使用组合而非继承。

**误区二：方法重写会改变父类行为**
方法重写只影响子类实例的行为，父类及其他子类完全不受影响。`Animal` 实例调用 `speak()` 始终执行 `Animal.speak()`，`Dog` 实例才会执行重写后的版本。父类对象不知道也不关心子类的存在。

**误区三：`super()` 只调用直接父类**
在多重继承中，`super()` 调用的是 MRO 中的**下一个类**，而非固定的直接父类。在 `class C(A, B)` 中，`A.super()` 可能调用的是 `B` 而非 `object`，这与直觉不符。不理解 MRO 时盲目使用 `super()` 可能导致意料之外的方法调用顺序。

---

## 知识关联

**前置概念**：理解继承前需要掌握**类与对象**的基本结构——类定义属性和方法，对象是类的实例。继承在此基础上引入了类之间的层次关系，`__init__`、`self` 等概念在继承场景中有延伸用法（如 `super().__init__()` 的必要性）。

**后续概念**：继承是**多态**的实现基础之一——子类覆盖父类方法后，同一接口调用在运行时根据对象实际类型派发到不同实现，这就是多态的本质。然而，继承的强耦合缺陷直接催生了**组合优于继承**原则（出自《设计模式》GoF 1994年，原文："Favor object composition over class inheritance"），建议优先通过持有对象引用来复用行为。**模板方法模式**则是继承的典型设计模式应用：父类定义算法骨架（`final` 方法），将可变步骤声明为抽象方法由子类实现，这正是 PyTorch `nn.Module` + 自定义 `forward()` 的设计哲学。