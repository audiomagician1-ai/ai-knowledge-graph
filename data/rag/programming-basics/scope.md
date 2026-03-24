---
id: "scope"
concept: "作用域"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["基础"]

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
# 作用域

## 概述

作用域（Scope）是指程序中变量、函数或其他标识符的**可见范围和有效生命周期**。一个变量在某段代码中"可见"，意味着该代码可以读取或修改这个变量；一旦超出作用域，该变量就无法被访问。作用域的本质是一套命名空间规则，决定了解释器或编译器在遇到某个名字时，应该去哪里寻找它对应的值。

作用域的概念可以追溯到1960年代的ALGOL 60语言，那是第一个正式引入"词法作用域"（Lexical Scope）规则的主流编程语言。在此之前，早期LISP使用动态作用域，导致函数行为难以预测。词法作用域的发明让程序员只需阅读代码文本本身，就能准确判断变量的归属，极大地提升了程序的可读性和可维护性。现代主流语言——Python、JavaScript、Java、C++——全部默认使用词法作用域。

在AI工程实践中，作用域决定了模型训练脚本、数据预处理管道以及推理服务的变量隔离方式。一个训练循环里错误地引用了外层作用域的学习率变量，可能导致整个实验结果无法复现，排查成本极高。正确理解作用域是写出无副作用、可测试、可复用代码的前提。

---

## 核心原理

### 1. 词法作用域与作用域链

词法作用域（Lexical Scope，又称静态作用域）规定：**变量的作用域在代码书写时就已确定，与函数的调用位置无关**。每当创建一个新的函数，就产生一个新的作用域。内层作用域可以访问外层作用域的变量，外层则无法访问内层。

这种嵌套关系形成**作用域链**（Scope Chain）。当代码引用变量 `x` 时，解释器首先在当前作用域查找；找不到则向上一级作用域查找；依此类推，直到全局作用域；若仍找不到，则抛出 `NameError`（Python）或 `ReferenceError`（JavaScript）。

```python
x = 10  # 全局作用域

def outer():
    x = 20  # outer 的局部作用域

    def inner():
        print(x)  # 输出 20，沿作用域链找到 outer 的 x

    inner()

outer()
```

### 2. Python 的 LEGB 规则

Python 将作用域精确地划分为四个层级，按照 **L → E → G → B** 的顺序查找变量：

| 字母 | 层级 | 说明 |
|------|------|------|
| L | Local（局部） | 当前函数内部 |
| E | Enclosing（闭包外层） | 嵌套函数的外层函数 |
| G | Global（全局） | 模块顶层 |
| B | Built-in（内建） | Python内置命名空间，如`len`、`range` |

这四个层级是Python独有的命名，其他语言有类似概念但叫法不同。值得注意的是，在Python中，**在局部作用域内对全局变量赋值，必须使用`global`关键字声明**；否则Python会将其视为新的局部变量，可能引发`UnboundLocalError`。

```python
learning_rate = 0.001  # 全局变量

def update_lr():
    global learning_rate   # 声明修改全局变量
    learning_rate = 0.0005
```

### 3. 变量遮蔽（Variable Shadowing）

当内层作用域定义了与外层同名的变量时，内层变量会**遮蔽**（Shadow）外层变量。在遮蔽期间，外层变量对内层代码完全不可见，但外层变量本身的值不受影响。

```python
batch_size = 32  # 全局

def train():
    batch_size = 64  # 遮蔽全局 batch_size，仅在 train() 内有效
    print(batch_size)  # 64

train()
print(batch_size)  # 仍为 32，全局未被修改
```

遮蔽在AI工程中是一类高频隐患：若在训练函数内部无意中使用了与全局超参数相同的变量名，实际运行的值可能与预期完全不同。

### 4. 闭包与作用域的持久化

**闭包**（Closure）是函数与其所在词法作用域的组合。当内层函数被返回后，它仍然持有对外层作用域变量的引用，这些变量不会随外层函数执行结束而消失。

```python
def make_scheduler(initial_lr):
    lr = initial_lr

    def step():
        nonlocal lr
        lr *= 0.9  # nonlocal 关键字允许修改闭包变量
        return lr

    return step

scheduler = make_scheduler(0.1)
print(scheduler())  # 0.09
print(scheduler())  # 0.081
```

`nonlocal` 关键字（Python 3引入）专门用于在闭包中修改外层（非全局）的变量，是处理闭包作用域的标准工具。

---

## 实际应用

**AI训练脚本中的超参数隔离**：将学习率、批次大小等超参数定义在全局作用域或配置对象中，训练函数通过参数传入而非直接引用全局变量。这样每次调用函数时，作用域内的值来源明确，便于超参数搜索框架（如Optuna）替换不同值进行实验。

**数据预处理管道**：使用闭包为不同数据集生成各自独立的归一化函数，每个闭包持有该数据集专属的`mean`和`std`值，互不干扰：

```python
def make_normalizer(mean, std):
    def normalize(x):
        return (x - mean) / std
    return normalize

train_norm = make_normalizer(0.485, 0.229)
val_norm   = make_normalizer(0.456, 0.224)
```

**避免循环变量捕获陷阱**：在Python的`for`循环中，循环变量属于函数作用域（而非块作用域），若在循环中创建闭包，所有闭包捕获的是同一个变量的最终值。这是机器学习代码中批量生成回调函数时的经典错误来源。

---

## 常见误区

**误区一：认为Python的`if/for/with`块会创建新作用域**。Python中只有函数、类、模块和推导式（如列表推导）会创建新的作用域。`for`循环内部定义的变量在循环结束后仍然存在于函数作用域中，这与C++、Java的块作用域行为截然不同。

**误区二：认为`global`关键字是声明变量**。`global x`不会创建新变量，它只是告诉Python"此函数内对`x`的赋值应作用于全局作用域"。如果全局作用域本就没有`x`，执行赋值后才会在全局创建它；在赋值之前读取`x`仍会报错。

**误区三：混淆`nonlocal`与`global`的适用范围**。`nonlocal`只能引用**最近的封闭函数作用域**中的变量，不能跳过中间层直达全局。若需修改全局变量，只能使用`global`，`nonlocal`无法替代。在三层嵌套函数中，最内层用`nonlocal`修改的是中间层的变量，而非最外层。

---

## 知识关联

**与函数的关系**：函数是作用域的直接创造者——每次调用函数都会生成一个全新的局部作用域，该作用域在函数返回后通常立即销毁（闭包是例外）。函数的参数默认存在于函数的局部作用域中，这也是参数名不会污染外部命名空间的原因。

**向后延伸至类与模块**：类定义体构成独立作用域，但它不参与函数的LEGB查找链——类内部的方法无法直接访问类体中定义的变量，必须通过`self.变量名`显式访问。模块则对应全局作用域，`import`语句将模块名引入当前全局作用域。理解这一层级，有助于在大型AI工程项目中合理组织配置、日志、模型定义等模块的变量归属。
