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

# 作用域

## 概述

作用域（Scope）是指程序中变量、函数或其他标识符可以被访问和引用的代码区域范围。每个变量在被声明时，就会关联到某个作用域，只有在该作用域内的代码才能合法读取或修改该变量的值。超出作用域范围访问变量，会导致"NameError"（Python）或"ReferenceError"（JavaScript）等错误。

作用域的概念随着结构化编程的普及而系统化。1960年代，ALGOL 60语言首次正式引入词法作用域（Lexical Scope）规则，确立了"变量的可见性由其在源代码中的位置决定"这一原则。此后C、Python、JavaScript等主流语言均继承了这一设计理念，尽管各语言在具体实现细节上存在差异。

在AI工程的数据处理和模型训练脚本中，作用域问题频繁出现。例如在循环内部定义的临时变量意外污染外部命名空间，或在函数中错误修改全局模型配置变量，都会导致训练结果不可复现。正确管理作用域是编写健壮、可调试代码的基础能力。

---

## 核心原理

### 局部作用域与全局作用域

在Python中，函数内部定义的变量属于**局部作用域**，函数外部定义的变量属于**全局作用域**。局部变量的生命周期仅限于函数调用期间，函数返回后即被销毁。

```python
learning_rate = 0.01  # 全局作用域

def train():
    batch_size = 32   # 局部作用域，函数外不可访问
    print(learning_rate)  # 可以读取全局变量
```

尝试在函数外访问 `batch_size` 会直接触发 `NameError: name 'batch_size' is not defined`。

### LEGB规则

Python使用**LEGB规则**来决定变量查找顺序，这4个字母分别代表：

- **L（Local）**：当前函数的局部作用域
- **E（Enclosing）**：外层嵌套函数的作用域
- **G（Global）**：模块级别的全局作用域
- **B（Built-in）**：Python内置名称（如`len`、`print`）

当Python解释器遇到一个变量名时，按L→E→G→B的顺序依次查找，找到第一个匹配即停止。若全部查找失败，则抛出`NameError`。

```python
x = "全局"

def outer():
    x = "外层"
    def inner():
        print(x)  # 按LEGB规则，找到E层的"外层"
    inner()
```

### global与nonlocal关键字

默认情况下，在函数内部对一个与全局变量同名的标识符赋值，Python会将其视为新的局部变量，**不会**修改全局变量。若确实需要在函数内修改全局变量，必须使用`global`关键字显式声明：

```python
total_epochs = 100

def update_epochs():
    global total_epochs
    total_epochs = 200  # 真正修改全局变量
```

而在嵌套函数中修改外层函数（非全局）的变量，则需使用`nonlocal`关键字。`nonlocal`是Python 3引入的特性，Python 2中不存在该关键字，这也是两个版本在作用域处理上的重要区别之一。

---

## 实际应用

### AI训练脚本中的作用域陷阱

在编写模型训练循环时，一个经典的作用域错误如下：

```python
results = []

for i in range(5):
    model_loss = i * 0.1
    results.append(model_loss)

print(model_loss)  # 此处可以访问，因为Python的for循环不创建新作用域
```

注意：Python的`for`循环**不创建独立作用域**，循环变量`i`和循环体内定义的`model_loss`在循环结束后仍然存在于当前作用域。这与C++或Java等语言行为不同，是Python初学者的常见混淆点。

### 使用函数封装隔离作用域

在数据预处理管道中，推荐将每个处理步骤封装进独立函数，利用局部作用域隔离中间变量，避免命名冲突：

```python
def normalize_data(data):
    mean = data.mean()      # mean仅在此函数内有效
    std = data.std()        # std仅在此函数内有效
    return (data - mean) / std
```

如果不封装进函数，`mean`和`std`会暴露在全局作用域，可能被后续代码意外覆盖。

---

## 常见误区

### 误区一：以为赋值等同于修改全局变量

很多初学者写出如下代码，期望修改全局的`learning_rate`：

```python
learning_rate = 0.01

def adjust():
    learning_rate = 0.001  # 实际上创建了一个同名局部变量！
```

函数执行后，全局`learning_rate`仍然是`0.01`。没有`global`声明时，函数内的赋值语句永远只作用于局部作用域，绝不影响同名的全局变量。

### 误区二：认为Python循环会创建新作用域

来自Java或C++背景的学习者常误以为Python的`for`/`while`循环块拥有独立作用域。实际上Python中只有**函数、类、模块**会创建新的作用域，循环和条件语句（`if`/`for`/`while`）均不创建独立作用域。这意味着在`if`块或`for`块中定义的变量，在块外同样可以访问。

### 误区三：混淆"变量遮蔽"与"变量修改"

当局部变量与全局变量同名时，发生的是**变量遮蔽（Shadowing）**，即局部变量在其作用域内"遮住"了全局变量，两者实际上是独立的两个对象，互不干扰。遮蔽不是修改，全局变量的值始终保持原样，直到使用`global`关键字后才能被函数内部真正修改。

---

## 知识关联

作用域与**函数**概念直接绑定——函数是Python中创建局部作用域的主要机制，每次函数调用都会生成一个新的局部命名空间（`locals()`字典），调用结束即释放。理解了函数的执行机制，才能准确预测LEGB规则的查找路径。

作用域也是理解**闭包（Closure）**的前提：闭包正是利用了LEGB中的E层（Enclosing作用域），让内层函数"记住"外层函数的局部变量，即使外层函数已经返回。在AI工程中，闭包常用于创建带有固定超参数的训练步骤函数。此外，模块级别的作用域管理与Python的**命名空间（Namespace）**机制深度关联，`import`语句的行为本质上也是在操作不同作用域之间的变量绑定关系。