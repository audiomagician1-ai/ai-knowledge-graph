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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 抽象

## 概述

抽象（Abstraction）是面向对象编程中将复杂系统的本质特征提取出来，隐藏不必要的实现细节，只暴露对外必要接口的设计方法。它的核心操作是"去掉什么"——识别哪些细节对调用者无关紧要，然后将其封装隐藏。在Python中，抽象通过`abc`模块（Abstract Base Class）实现；在Java中，`abstract`关键字直接支持抽象类的定义。

抽象的概念在编程领域由Edsger Dijkstra于1968年在结构化编程论文中正式提出，他指出程序员的主要任务是通过逐层抽象来管理复杂度。在AI工程领域，抽象尤为关键——一个神经网络训练框架可以把`Optimizer`抽象为只含`step()`和`zero_grad()`方法的基类，无论底层是SGD、Adam还是自定义优化器，上层训练循环代码完全不需要改变。

抽象与封装的区别常被混淆，但两者目标不同：封装是隐藏"如何实现"，抽象是定义"能做什么"。正是这种区别使得抽象成为多态性和接口设计的前提——没有对行为的抽象定义，就无法实现可替换的组件化系统。

## 核心原理

### 抽象类与抽象方法

抽象类（Abstract Class）本身不能被实例化，它存在的唯一目的是被继承。一个类只要包含至少一个抽象方法，就必须声明为抽象类。抽象方法只有方法签名，没有方法体（或只有空实现）。

以Python为例：

```python
from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def forward(self, x):
        pass  # 没有具体实现
    
    @abstractmethod
    def loss(self, y_pred, y_true):
        pass
```

任何继承`Model`的子类，若未实现`forward`和`loss`，在实例化时会直接抛出`TypeError`，而不是等到调用时才报错——这是抽象类的静态保护机制，将错误发现时机从运行时提前到实例化时。

### 抽象层级（Levels of Abstraction）

抽象不是一次性的，而是分层的。以PyTorch为例，其抽象层级从下到上至少有四层：

1. **硬件层**：CUDA核函数，直接操作显存
2. **张量层**：`torch.Tensor`，屏蔽了内存管理和设备差异
3. **模块层**：`nn.Module`，屏蔽了参数管理和梯度追踪
4. **应用层**：`nn.Linear`、`nn.Conv2d`等，屏蔽了具体运算实现

每一层只依赖下一层的接口，而不关心下层的具体实现。当NVIDIA发布新架构时，只需修改第1层，第2至第4层的代码完全不受影响。这正是抽象的价值：变化被隔离在最小范围内。

### 数据抽象与过程抽象

**过程抽象**将一系列操作封装为带名称的函数或方法，调用者只需知道"调用`train_one_epoch()`能完成一轮训练"，无需了解内部的批次迭代、梯度清零、反向传播顺序。

**数据抽象**将数据结构与其操作捆绑为一个抽象数据类型（ADT）。例如`Dataset`抽象类要求子类实现`__len__()`和`__getitem__()`，使用者面对的是统一的"可索引、有长度的数据集"概念，而不论底层数据是CSV文件、数据库还是内存数组。

两种抽象在AI工程中通常同时出现：`nn.Module`既抽象了数据（参数`state_dict`），也抽象了过程（`forward`调用）。

## 实际应用

**场景一：统一模型接口**

在AI工程的模型服务化场景中，定义抽象基类`BasePredictor`，强制所有模型实现`preprocess()`、`predict()`、`postprocess()`三个方法。无论部署的是图像分类模型、NLP模型还是推荐系统模型，推理服务框架只调用这三个抽象方法。新增一种模型类型时，只需实现这三个方法，不修改任何框架代码——满足开闭原则（对扩展开放，对修改关闭）。

**场景二：损失函数抽象**

PyTorch的`nn.Module`本身就是一个抽象机制。所有损失函数（`CrossEntropyLoss`、`MSELoss`等）都继承自它，训练循环只写`criterion(output, target)`，具体损失计算完全透明。这使得切换损失函数只需改动一行实例化代码。

**场景三：数据加载抽象**

HuggingFace的`datasets`库将各种数据集（MNIST、COCO、自定义CSV）统一抽象为具有`map()`、`filter()`、`select()`方法的`Dataset`对象。用户用同一套代码处理不同来源的数据，抽象屏蔽了数据格式差异。

## 常见误区

**误区一：认为抽象类越多越好**

抽象是有成本的——它增加了类层次深度，使代码跳转更复杂。如果一个系统中只有一种实现，强行引入抽象类只会增加不必要的间接层。正确做法是：当第二种实现出现时再提取抽象（"Rule of Three"原则），而不是预先设计过度抽象的架构。

**误区二：把抽象类和接口等同**

抽象类可以包含有具体实现的方法（非抽象方法），也可以有成员变量；而接口（在Java中）原则上只定义方法签名，不含状态。Python的`ABC`允许混合使用，但在语义上，抽象类表达"是一种"（is-a）的继承关系，接口表达"能做"（can-do）的能力契约。两者的适用场景不同。

**误区三：以为隐藏了细节就完成了抽象**

封装可以隐藏细节，但真正的抽象要求设计出稳定、正确的接口语义。如果`forward()`方法的调用约定（输入张量的形状要求、返回值含义）没有明确规定，即使实现被隐藏，调用者仍然需要阅读源码——这说明抽象设计失败，只做到了封装而没有做到有效抽象。

## 知识关联

学习抽象之前需要掌握**类与对象**的基本概念——抽象类本质上是一种特殊的类，若不理解类的继承机制，就无法理解抽象方法被子类覆写的过程。抽象类中的`super().__init__()`调用涉及继承链的初始化顺序，这也是前置知识的直接延伸。

抽象学习完毕后，自然引出**接口**（Interface）的概念。接口是"纯抽象"的极端形式——所有方法都是抽象的，不含任何实现状态。Python通过只含`@abstractmethod`的ABC模拟接口；Java和C#则将接口作为独立语言构造提供。理解了抽象类的局限（单继承约束、状态耦合），就能理解为何需要接口作为更轻量的行为约定机制。在AI工程实践中，抽象类适合描述"同类模型的公共骨架"，接口适合描述"跨类型的能力契约"，两者配合构成完整的面向对象设计工具集。