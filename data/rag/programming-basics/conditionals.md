---
id: "conditionals"
concept: "条件判断(if/else)"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 1
is_milestone: false
tags: ["控制流"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 条件判断（if/else）

## 概述

条件判断是程序根据某个布尔表达式的真假（`True` 或 `False`）来决定执行哪段代码的控制结构。在 Python 中，`if` 关键字后面跟随一个条件表达式，若该表达式求值为 `True`，则执行紧随其后的缩进代码块；若为 `False`，则跳过该块，转而执行 `else` 或 `elif` 分支。这种"分支执行"能力使程序不再只是顺序地从第一行运行到最后一行，而是能够对不同输入或状态做出不同响应。

条件判断结构最早可追溯到 1950 年代的 FORTRAN 语言中的 `IF` 语句，当时写作 `IF (expr) label1, label2, label3`，依据表达式的负、零、正三种结果跳转到不同行号。现代高级语言将其演化为更具可读性的 `if/else` 块结构，Python 进一步引入了 `elif`（即 else-if 的缩写）来支持多路分支，避免了大量嵌套。

在 AI 工程实践中，条件判断无处不在：模型推理完成后判断置信度是否超过阈值、数据预处理时过滤无效样本、API 调用时检查返回状态码是否为 200 等，都依赖条件判断来保证程序逻辑的正确性。

---

## 核心原理

### 布尔表达式与真值判断

`if` 语句的条件部分必须能求值为布尔类型。Python 中，以下值会被判断为 `False`：数字 `0`、空字符串 `""`、空列表 `[]`、空字典 `{}`、`None` 以及 `False` 本身；其余几乎所有值均为 `True`。这意味着 `if model_output:` 这样的写法，当 `model_output` 为空列表时会直接跳过执行块，而无需写 `if len(model_output) != 0:`。

条件表达式通常使用上一章学到的比较运算符（`==`、`!=`、`>`、`<`、`>=`、`<=`）和逻辑运算符（`and`、`or`、`not`）构成。例如：

```python
confidence = 0.87
threshold = 0.80

if confidence >= threshold:
    print("预测结果可信")
else:
    print("置信度不足，需要人工审核")
```

### if / elif / else 的完整结构

Python 条件判断的完整语法如下：

```python
if 条件A:
    # 条件A为True时执行
elif 条件B:
    # 条件A为False且条件B为True时执行
elif 条件C:
    # 以上均为False且条件C为True时执行
else:
    # 以上所有条件均为False时执行
```

关键规则：`elif` 和 `else` 分支都是可选的，但 `else` 最多只能出现一次且必须放在最后。Python 使用**缩进（通常为4个空格）**而非大括号来界定代码块，缩进不一致会直接引发 `IndentationError`。多个 `elif` 分支按顺序逐一判断，一旦某个条件满足，后续分支不再判断，这与连续写多个独立 `if` 语句的行为有本质区别。

### 嵌套条件判断

条件判断块内部可以再嵌套另一个条件判断，形成树状决策结构。例如，在处理模型 API 响应时：

```python
status_code = response.status_code
data = response.json()

if status_code == 200:
    if "predictions" in data:
        result = data["predictions"]
    else:
        result = []
else:
    print(f"请求失败，状态码：{status_code}")
    result = None
```

嵌套层级过深（超过3层）会显著降低代码可读性，实践中常通过提前返回（early return）或逻辑运算符合并条件来减少嵌套。

---

## 实际应用

**场景一：模型推理结果后处理**

在图像分类任务中，模型输出一个 0 到 1 之间的概率值，需要根据阈值转换为类别标签：

```python
def classify(probability, threshold=0.5):
    if probability >= threshold:
        return "猫"
    else:
        return "非猫"
```

调整 `threshold` 参数可以控制模型的精确率与召回率之间的权衡，而这个权衡本身就是通过条件判断来实现的。

**场景二：数据预处理中的异常值过滤**

```python
def clean_age(age):
    if age is None:
        return -1          # 用-1标记缺失值
    elif age < 0 or age > 150:
        return -1          # 超出合理范围视为异常
    else:
        return age
```

这段代码对同一字段的三种不同情况分别给出处理策略，是 `if/elif/else` 多路分支的典型用法。

**场景三：Python 三元表达式**

对于简单的二选一赋值，Python 支持单行条件表达式（ternary expression）：

```python
label = "正样本" if score > 0 else "负样本"
```

等价于三行的 `if/else` 写法，适合在列表推导式或函数参数中内联使用。

---

## 常见误区

**误区一：用 `==` 比较 `None`**

`if x == None:` 在技术上可以工作，但 Python 官方风格指南 PEP 8 明确要求应使用 `if x is None:`。原因在于 `==` 调用对象的 `__eq__` 方法，某些自定义类可能重写该方法导致意外结果，而 `is` 直接比较对象身份（内存地址），`None` 在 Python 中是单例对象，用 `is` 判断绝对可靠。

**误区二：将多个 `elif` 误写为多个独立 `if`**

```python
# 错误写法：三个条件都会被独立检查
if score >= 90:
    grade = "A"
if score >= 80:
    grade = "B"   # 当score=95时，这行仍会执行，grade被覆盖为"B"
if score >= 70:
    grade = "C"   # 最终grade="C"，结果错误！

# 正确写法：一旦匹配成功，后续elif不再判断
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
```

在 AI 工程的评分、分级、路由等场景中，这个错误会导致逻辑结果完全错误且难以调试。

**误区三：条件判断与赋值混淆（Python 中 `:=` 的边界）**

Python 3.8 引入了海象运算符 `:=`，允许在条件判断内部赋值：`if (n := len(data)) > 10:`。初学者常误以为普通 `if` 中可以直接写 `if x = 5:`（单等号），这在 Python 中会直接抛出 `SyntaxError`，因为单等号是赋值语句而非布尔表达式。这一点与 C/C++ 不同，C 语言允许 `if (x = 5)` 且不报错，容易跨语言混淆。

---

## 知识关联

**前置概念——运算符**：`if` 语句的条件表达式完全依赖比较运算符（`>`、`==`、`in`）和逻辑运算符（`and`、`or`、`not`）来构造。没有运算符知识，就无法写出有意义的判断条件。例如，`if 0.5 <= confidence < 0.9 and label != "unknown":` 这个条件同时用到了链式比较、逻辑与和不等于运算符。

**后续概念——循环（for/while）**：循环结构与条件判断结合使用是编程中最基础的模式。`while` 循环本质上是"当条件为 True 时反复执行"，其条件判断语法与 `if` 完全相同。`for` 循环内部常嵌套 `if` 来筛选元素，例如 `for sample in dataset: if sample["label"] != -1:` 用于跳过脏数据。掌握 `if/else` 之后，学习 `break`（满足条件时退出循环）和 `continue`（满足条件时跳过当次迭代）将会自然衔接。