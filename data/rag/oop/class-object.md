---
id: "class-object"
concept: "类与对象"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 3
is_milestone: false
tags: ["OOP"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 37.5
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.344
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 类与对象

## 概述

类（Class）是面向对象编程中用于定义数据结构和行为的蓝图模板，而对象（Object）是依据该蓝图在内存中创建的具体实例。在Python中，使用`class`关键字定义类，每次调用类名加括号（如`Dog()`）便会在堆内存中分配一块新的空间，创建出一个独立的对象实例。类与对象的关系，类似于建筑图纸与实际建筑的关系——同一张图纸可以建造无数栋外形相同但彼此独立的建筑。

面向对象编程（OOP）的思想最早由Ole Johan Dahl和Kristen Nygaard在1967年设计的Simula语言中正式提出，随后Smalltalk-80（1980年）将其发扬光大。Python从1.0版本（1994年）起便原生支持类与对象机制，且Python中一切皆为对象——整数`42`、字符串`"hello"`、甚至函数本身都是某个类的实例。这与C++等语言中基本类型不是对象的设计截然不同。

在AI工程场景中，类与对象是组织复杂系统的基础工具。神经网络框架PyTorch的核心类`nn.Module`就是通过类与对象机制实现的：每个自定义模型都继承自`nn.Module`，并在`__init__`方法中定义层结构，在`forward`方法中定义前向计算逻辑。理解类与对象是读懂PyTorch、scikit-learn等AI框架源码的必要前提。

---

## 核心原理

### 类的结构：属性与方法

一个类由两类成员构成：**属性（Attribute）**存储数据状态，**方法（Method）**定义操作行为。属性本质上是绑定到对象上的变量，方法本质上是第一个参数为`self`的函数。`self`参数指向调用该方法的具体对象实例，是Python中访问实例属性的唯一途径。

```python
class NeuralLayer:
    def __init__(self, input_size, output_size):
        self.weights = [[0.0] * output_size for _ in range(input_size)]
        self.bias = [0.0] * output_size

    def get_param_count(self):
        return len(self.weights) * len(self.weights[0]) + len(self.bias)
```

在上例中，`weights`和`bias`是**实例属性**，每个`NeuralLayer`对象都拥有自己独立的副本。若将属性定义在方法外部（类体直接缩进层），则成为**类属性**，被所有实例共享——修改类属性会影响所有实例，这是初学者最容易踩的陷阱之一。

### `__init__`构造方法与对象实例化

`__init__`是Python类的构造方法，在执行`obj = MyClass()`时由Python解释器自动调用。其完整调用链为：首先由`__new__`方法在内存中分配对象空间并返回实例，随后`__init__`接收该实例（即`self`）并进行属性初始化。对于AI工程，每次实例化模型类时，`__init__`负责初始化所有权重张量和超参数，确保不同模型实例之间参数相互隔离。

```python
layer1 = NeuralLayer(784, 128)  # 输入784维，输出128维
layer2 = NeuralLayer(128, 10)   # 输入128维，输出10维
# layer1和layer2各自拥有独立的weights和bias
```

### 实例标识与内存模型

Python中每个对象都有三个基本属性：**id**（内存地址，由`id()`获取）、**类型**（由`type()`获取）、**值**。两个变量可以指向同一个对象（`a is b`为`True`），也可以是值相等但地址不同的独立对象（`a == b`为`True`但`a is b`为`False`）。

对象在内存中占用的空间大小可用`sys.getsizeof()`查询——一个空的自定义类实例在CPython中通常占用56字节基础空间，每增加一个实例属性，`__dict__`字典的内存开销随之增加。在大批量创建对象时（如处理百万级样本的数据集类），可使用`__slots__`声明固定属性名来替代`__dict__`，内存占用可降低约40%-50%。

---

## 实际应用

**场景一：封装数据集加载逻辑**

PyTorch中的`Dataset`基类要求子类实现`__len__`和`__getitem__`两个方法。通过类与对象机制，可以将CSV文件读取、数据预处理、标签编码等逻辑封装在一个类中：

```python
class ImageDataset:
    def __init__(self, file_path, transform=None):
        self.data = pd.read_csv(file_path)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image = self.data.iloc[idx, 1:].values.reshape(28, 28)
        label = self.data.iloc[idx, 0]
        return image, label
```

实例化`dataset = ImageDataset("train.csv")`后，通过`dataset[0]`即可获取第一条样本，接口简洁且行为可复用。

**场景二：超参数配置对象**

在AI实验管理中，常用一个类统一存储超参数，避免参数散落在全局变量中：

```python
class TrainingConfig:
    learning_rate = 0.001
    batch_size = 32
    epochs = 100
    dropout_rate = 0.5
```

通过`config = TrainingConfig()`创建配置实例后传递给训练函数，不同实验可修改实例属性而不影响类定义本身。

---

## 常见误区

**误区一：混淆类属性与实例属性的修改行为**

```python
class Model:
    version = "v1.0"  # 类属性

m1 = Model()
m1.version = "v2.0"  # 这里实际是给m1创建了一个新的实例属性
print(Model.version)  # 仍然输出 "v1.0"
```

对实例执行赋值操作并不会修改类属性，而是在该实例的`__dict__`中创建一个同名的实例属性遮蔽了类属性。若要修改类属性必须通过类名直接赋值：`Model.version = "v2.0"`。

**误区二：认为`self`是关键字**

`self`在Python中只是约定俗成的参数名，并非保留关键字。将其命名为`this`或`s`在语法上完全合法。真正的语义在于：实例方法的第一个参数始终接收调用该方法的实例对象，名字叫什么都能正常运行，但违反`self`命名约定会严重降低代码可读性。

**误区三：将类等同于字典**

类与字典都能存储键值对形式的数据，但类提供了方法绑定、继承、访问控制、魔术方法重载等字典无法实现的能力。对于简单数据聚合，Python 3.7+推荐使用`dataclass`装饰器，它自动生成`__init__`、`__repr__`、`__eq__`方法，兼顾了类的能力与字典的简洁性。

---

## 知识关联

**前置概念衔接**：类中的方法本质是函数（定义方式相同，只是多了`self`参数），类的属性本质是变量（但作用域绑定在实例上）。若对函数参数传递机制或变量作用域不熟悉，会直接导致对`self`和实例属性的困惑。

**后续概念延伸**：掌握类与对象后，**封装**进一步讨论如何用访问控制（Python中以单下划线`_`和双下划线`__`为约定）保护属性；**继承**讨论如何用`class SubClass(ParentClass)`语法复用父类代码；**抽象**通过`abc.ABC`和`@abstractmethod`定义不可直接实例化的抽象类（PyTorch的`nn.Module`即依赖此机制）。**枚举类型**（`enum.Enum`）是类机制的特殊应用，用于定义有限状态的常量集合，在AI工程中常用于表示模型运行阶段（训练/验证/测试）。**设计模式**（如单例模式、工厂模式）则是在类与对象基础上总结的高级代码组织方案。