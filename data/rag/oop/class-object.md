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
---
# 类与对象

## 概述

类（Class）是面向对象编程中定义数据结构和行为的蓝图模板，对象（Object）则是依据这份蓝图在内存中创建的具体实例。类本身不占用运行时的实例数据内存，只有通过实例化（instantiation）操作才会在堆内存中分配对象的存储空间。Python中使用`class`关键字定义类，Java则在类定义中强制声明所有成员变量的类型，两者都体现了"先定义模板，再创建实例"的设计哲学。

面向对象编程（OOP）由艾伦·凯（Alan Kay）在1967年设计Simula语言时奠定基础，他明确提出"对象是拥有状态和行为的自治单元"这一核心思想。Python中一切皆对象——整数`42`是`int`类的实例，函数也是`function`类的实例，这与C语言中函数和基本类型不具备对象语义形成鲜明对比。

在AI工程实践中，将神经网络层、数据集、训练器抽象为类，能让代码在规模扩大时保持可维护性。PyTorch的`nn.Module`就是一个典型的类，用户通过继承它并重写`forward()`方法来定义自定义网络层，每次创建`model = MyNet()`都产生一个独立的对象实例，持有自己的权重张量。

## 核心原理

### 类的结构：属性与方法

类由两类成员构成：**属性（attribute）** 存储对象的状态数据，**方法（method）** 定义对象的行为。Python中类的最简定义如下：

```python
class NeuralLayer:
    def __init__(self, input_dim, output_dim):
        self.input_dim = input_dim    # 实例属性
        self.output_dim = output_dim
        self.weights = None           # 实例属性，初始为None
    
    def initialize(self):             # 实例方法
        import random
        self.weights = [[random.gauss(0, 0.01) 
                         for _ in range(self.output_dim)]
                        for _ in range(self.input_dim)]
```

`__init__`是Python中的**构造方法**（constructor），在执行`layer = NeuralLayer(128, 64)`时自动调用，负责初始化对象的实例属性。Java中对应的是与类同名的构造函数。属性分为实例属性（每个对象独立拥有）和类属性（所有实例共享），例如`NeuralLayer.layer_count = 0`就是类属性，可统计已创建的层数量。

### 实例化：从类到对象的内存过程

执行`obj = ClassName(args)`时，Python解释器依次完成三步：①调用`ClassName.__new__()`在堆内存中分配对象空间并返回引用；②调用`__init__()`用传入参数初始化该对象；③将对象引用绑定到变量名`obj`。变量`obj`本质上是存储在栈上的指针，指向堆中的对象实体。因此`a = NeuralLayer(128, 64)`和`b = NeuralLayer(128, 64)`产生两个不同对象，`a is b`返回`False`，但`a.input_dim == b.input_dim`返回`True`。

对象的身份（identity）、类型（type）和值（value）是三个独立概念：`id(a)`返回对象的内存地址（CPython中为整数），`type(a)`返回`<class 'NeuralLayer'>`，而`a.input_dim`才是具体的值。

### `self` 参数的本质

Python实例方法的第一个参数`self`是对当前对象自身的显式引用，这与Java中隐式的`this`关键字功能相同但写法不同。当调用`layer.initialize()`时，Python在底层实际执行的是`NeuralLayer.initialize(layer)`——即把对象作为第一个参数传入。理解这一点能解释为何在类定义外部直接调用未绑定方法会报错：`NeuralLayer.initialize()`缺少必要的`self`参数。

### 类属性 vs 实例属性的覆盖机制

当实例属性与类属性同名时，实例属性优先级更高，会**遮蔽（shadow）**类属性，而非修改它。例如：

```python
class Model:
    dropout_rate = 0.5   # 类属性，所有实例默认共享

m1 = Model()
m1.dropout_rate = 0.3   # 为m1创建了独立的实例属性
m2 = Model()
print(m2.dropout_rate)  # 输出0.5，m2仍使用类属性
```

这一机制在AI框架配置管理中极为常见，允许为特定模型实例覆盖全局默认超参数。

## 实际应用

**AI数据集封装**：将数据加载逻辑封装为类，是PyTorch `Dataset`的标准用法。自定义`class ImageDataset`持有`self.file_paths`（属性）并实现`__len__`和`__getitem__`方法，每次`DataLoader`迭代时调用这些方法取批次数据。不同数据集（训练集、验证集）作为同一个类的不同实例，各自管理自己的文件路径列表，互不干扰。

**实验追踪器**：在机器学习实验中，定义`class ExperimentTracker`，其属性包括`self.metrics_history = []`、`self.start_time`，方法包括`log_epoch(loss, accuracy)`和`save_checkpoint()`。每次实验创建一个新实例，避免多次实验的数据相互污染——这是直接使用全局变量记录指标时难以避免的问题。

**强化学习环境**：OpenAI Gym的每个环境都是一个类的实例。`env = gym.make('CartPole-v1')`创建了一个持有自身状态（杆的角度、小车位置）的对象，`env.reset()`和`env.step(action)`是操作该状态的方法。多个`env`实例可并行运行，各自维护独立的物理状态，这正是对象实例隔离性的直接价值体现。

## 常见误区

**误区一：混淆类和对象**。初学者常说"创建了一个类"时实际描述的是创建了对象。类是静态的代码定义，在程序启动时加载一次；对象是运行时动态生成的内存实体，可以创建成千上万个。`type(NeuralLayer)`返回`<class 'type'>`（类本身是`type`的实例），而`type(layer)`返回`<class 'NeuralLayer'>`，两者层级不同。

**误区二：认为类属性修改是安全的全局配置**。对可变类属性（如列表）执行原地修改（`append`）而非重新赋值时，所有实例都会受到影响。例如`Model.layer_names.append('conv3')`会修改所有`Model`实例共享的列表，而`m1.layer_names = ['conv3']`只影响`m1`。在AI工程中，误用可变类属性存储训练状态是难以追踪的bug来源。

**误区三：认为`__init__`是唯一的对象创建入口**。Python还支持`__new__`方法在`__init__`之前控制对象分配，单例模式（Singleton）正是通过重写`__new__`实现的——让类始终返回同一个实例。此外，`@classmethod`修饰的工厂方法（如`Model.from_config(config_dict)`）也是创建对象的常见替代方式，在加载预训练模型时非常实用。

## 知识关联

类与对象建立在**函数**和**变量与数据类型**的基础上：方法本质上是定义在类命名空间内的函数，属性类型依赖于Python的基本数据类型系统（`int`、`list`、`dict`等）。掌握类与对象后，直接进入**封装**概念——封装讨论如何通过访问控制（`_`和`__`前缀命名约定）保护对象内部状态，是类设计的质量保障机制。**继承**则在类的基础上引入`class SubClass(ParentClass)`语法，建立类之间的层级关系，PyTorch中`nn.Linear`继承自`nn.Module`就是典型案例。**抽象**进一步规定哪些方法必须由子类实现（Python通过`abc.ABC`和`@abstractmethod`装饰器实现）。最终，**设计模式**将类与对象的组织方式上升为可复用的架构方案，如工厂模式、观察者模式等，均以类与对象为基本构件。
