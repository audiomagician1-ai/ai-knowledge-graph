---
id: "functions"
concept: "函数"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["模块化"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "textbook"
    title: "Structure and Interpretation of Computer Programs (2nd ed.)"
    author: "Harold Abelson, Gerald Jay Sussman"
    isbn: "978-0262510875"
  - type: "textbook"
    title: "Clean Code: A Handbook of Agile Software Craftsmanship"
    author: "Robert C. Martin"
    isbn: "978-0132350884"
  - type: "textbook"
    title: "Python Crash Course (3rd ed.)"
    author: "Eric Matthes"
    isbn: "978-1718502703"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 函数

## 概述

函数（Function）是编程中将一段具有特定功能的代码封装起来、赋予名称、可被反复调用的代码块。在Python中，函数用 `def` 关键字定义；在JavaScript中用 `function` 关键字或箭头语法 `=>` 定义。函数接收零个或多个输入（称为参数/Parameters），执行特定逻辑后可返回一个输出值（通过 `return` 语句）。

函数的概念最早可追溯到数学中的映射关系——给定输入，产生唯一确定的输出。1958年，Lisp语言将数学函数概念正式引入编程，使"函数是第一等公民"成为函数式编程的基础范式。现代AI工程中，从数据预处理管道到模型推理接口，几乎所有代码都以函数为基本组织单元。

在AI工程实践中，函数的价值体现在三个层面：第一，避免重复代码（DRY原则——Don't Repeat Yourself）；第二，使代码可测试，一个函数做一件事，可以单独验证其正确性；第三，为后续学习模块化开发、递归算法提供必要的结构基础。一个训练数据清洗脚本如果没有函数，往往超过200行无法维护；拆分成函数后，每个函数通常控制在10-30行以内。

---

## 核心原理

### 函数的定义与调用机制

函数定义时不执行任何代码，只有在被"调用"时才运行。以下是Python函数的完整结构：

```python
def calculate_accuracy(correct, total):  # 函数名 + 参数列表
    if total == 0:
        return 0.0                        # 提前返回
    accuracy = correct / total * 100
    return accuracy                       # 返回值

result = calculate_accuracy(85, 100)     # 调用：传入实参
print(result)                            # 输出：85.0
```

关键点：`def` 后的 `correct` 和 `total` 是**形参（Parameters）**，调用时传入的 `85` 和 `100` 是**实参（Arguments）**。这一区分在函数嵌套调用时尤为重要。

### 参数的四种传递方式

Python函数支持四种参数形式，这是Python有别于许多语言的独特之处：

| 参数类型 | 语法示例 | 说明 |
|---------|---------|------|
| 位置参数 | `def f(a, b)` | 按顺序传入，最基础 |
| 默认参数 | `def f(a, b=10)` | 未传时使用默认值 |
| 可变位置参数 | `def f(*args)` | 接收任意数量位置参数，存为元组 |
| 可变关键字参数 | `def f(**kwargs)` | 接收任意数量键值对，存为字典 |

在AI工程中，`**kwargs` 被大量用于模型配置传递。例如 `model.fit(X, y, **training_config)`，允许在不修改函数签名的情况下扩展配置项。

### 返回值与无返回值的区别

`return` 语句决定函数的输出。若函数没有 `return` 语句，Python默认返回 `None`。这一细节是初学者常见bug来源：

```python
def normalize_data(data):
    data = [x / max(data) for x in data]
    # 忘记写 return！

result = normalize_data([1, 2, 3, 4])
print(result)  # 输出 None，而不是归一化后的列表
```

函数也可以通过 `return a, b` 同时返回多个值——Python实际上将其打包为一个元组，调用方可用 `x, y = f()` 解包。

### 函数作为对象（高阶函数基础）

Python中函数本身是对象，可以赋值给变量、作为参数传递给其他函数。这一特性支撑了AI工程中大量的回调（callback）和管道（pipeline）设计：

```python
def preprocess(text):
    return text.strip().lower()

def apply_to_list(data, func):   # func 是一个函数参数
    return [func(item) for item in data]

clean_texts = apply_to_list(raw_texts, preprocess)
```

`apply_to_list` 接收另一个函数作为参数，这类函数称为**高阶函数（Higher-order Function）**。Python内置的 `map()`、`filter()`、`sorted(key=...)` 都是高阶函数。

---

## 实际应用

**AI数据预处理场景**：在处理机器学习数据集时，通常将每种清洗操作封装为独立函数：

```python
def remove_nulls(df):
    return df.dropna()

def encode_labels(df, column):
    df[column] = df[column].astype('category').cat.codes
    return df

def split_features_target(df, target_col):
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return X, y

# 串联调用，形成清晰的处理管道
df = remove_nulls(raw_df)
df = encode_labels(df, 'category')
X, y = split_features_target(df, 'label')
```

这种写法使每个步骤可以独立测试——可以单独对 `encode_labels` 输入一个测试DataFrame，验证其输出是否符合预期，而不需要运行整个数据流程。

**模型评估函数**：在比较多个模型时，将评估逻辑封装为函数可避免重复书写相同的计算代码：

```python
def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    accuracy = sum(p == t for p, t in zip(predictions, y_test)) / len(y_test)
    return round(accuracy, 4)
```

---

## 常见误区

**误区一：修改列表参数会影响原始数据**

Python中列表、字典等可变对象作为参数传入时，函数内对其的修改会直接影响函数外的原始变量（传递的是引用，而非副本）。字符串、整数、元组则不会被修改，因为它们是不可变类型。很多初学者误以为所有参数传入函数后都是独立副本。

```python
def bad_normalize(data):
    for i in range(len(data)):
        data[i] /= 100   # 直接修改了外部列表！

scores = [85, 90, 78]
bad_normalize(scores)
print(scores)  # [0.85, 0.9, 0.78]  原始数据被破坏！
```

解决方式：在函数内部用 `data = data.copy()` 或 `data[:]` 创建副本后再操作。

**误区二：`return` 之后的代码仍会执行**

函数一旦执行到 `return`，立即退出，其后的所有代码不再运行。初学者有时在 `return` 后写了额外的打印或赋值语句，误以为会被执行。

**误区三：默认参数使用可变对象**

`def f(data=[])` 这种写法会在所有调用之间共享同一个列表对象。这是Python函数定义的已知陷阱——默认参数只在函数定义时计算一次，而非每次调用时。正确做法是用 `def f(data=None)` 然后在函数内部写 `if data is None: data = []`。

---

## 知识关联

**与循环的关系**：在学习 `for`/`while` 循环之后，函数将循环体封装起来赋予其语义名称。例如，一段用 `for` 循环计算列表均值的代码，封装为 `calculate_mean(data)` 后，调用处的代码意图更加清晰。函数内部可以包含循环，循环内也可以调用函数。

**通向作用域**：函数是理解变量作用域（Scope）的前提。函数内部定义的变量是"局部变量"，函数外部的是"全局变量"，两者在内存中处于不同的命名空间。不理解函数边界，就无法理解为何函数内部修改一个变量不影响外部同名变量。

**通向递归**：递归（Recursion）是函数调用自身的特殊形式。学好普通函数的调用机制——尤其是每次调用都有独立的参数和局部变量——是理解递归调用栈的基础。

**通向错误处理**：`try/catch` 块经常需要包裹函数调用，捕获函数执行时可能抛出的异常。理解函数的返回值与异常的区别，是错误处理设计的关键问题。

**通向模块化**：当一个文件中的函数数量超过约10个时，需要将相关函数组织到独立的模块（`.py` 文件）中，通过 `import` 引用。模块本质上是函数和类的集合，是函数概念在文件级别的延伸。