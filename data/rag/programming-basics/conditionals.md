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
quality_tier: "B"
quality_score: 47.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
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

条件判断是编程中根据布尔表达式的真假（`True` 或 `False`）来决定执行哪段代码块的控制流机制。当 `if` 后的表达式求值为 `True` 时，执行紧随其后的代码块；当求值为 `False` 时，程序跳转到 `else` 分支（如果存在）或直接跳过整个结构继续向下执行。

条件判断结构最早可追溯到1950年代的FORTRAN语言，彼时以 `IF (expr) label1, label2, label3` 的三路跳转形式出现。现代的 `if/else` 语法由ALGOL 60（1960年）正式确立，此后被C、Python、Java等几乎所有主流语言沿用。Python使用缩进（标准为4个空格）而非花括号来界定代码块，这是与C系语言最显著的语法差异。

在AI工程中，条件判断贯穿数据预处理、模型推理、结果后处理的每个阶段。例如，当模型置信度低于0.6时触发人工审核，当输入文本长度超过512个token时进行截断处理——这类逻辑都依赖条件判断来实现。

---

## 核心原理

### if / elif / else 的语法结构

Python中条件判断的完整语法如下：

```python
if 条件A:
    # 条件A为True时执行
elif 条件B:
    # 条件A为False且条件B为True时执行
else:
    # 以上条件均为False时执行
```

`elif` 是 "else if" 的缩写，可以连续写多个，但 `else` 只能出现一次且必须放在最后。Python逐行从上到下检查条件，一旦某个分支匹配成功，**其余分支全部跳过**，不再继续判断。这与连续写多个独立 `if` 语句的行为截然不同。

### 条件表达式的真值判断

`if` 后的条件不限于比较运算符，Python中许多对象本身即有布尔值：

- **为 `False` 的值**：`0`、`0.0`、`""`（空字符串）、`[]`（空列表）、`{}`（空字典）、`None`
- **为 `True` 的值**：非零数字、非空字符串、非空容器

因此 `if model_outputs:` 等价于 `if len(model_outputs) > 0:`，两者检查列表是否非空。条件可通过 `and`、`or`、`not` 进行组合，其中 `not` 优先级最高，`and` 次之，`or` 最低。

### 嵌套条件与短路求值

条件判断可以嵌套，即在一个 `if` 块内部再写另一个 `if/else`。嵌套深度过大（通常超过3层）会严重降低代码可读性，在AI工程实践中建议通过**提前返回**（early return）或将子逻辑封装为函数来减少嵌套层数。

Python的 `and` 和 `or` 运算符具有**短路求值**特性：
- `A and B`：若A为 `False`，B不被执行
- `A or B`：若A为 `True`，B不被执行

这一特性可用于防止空指针错误，例如：`if result is not None and result.score > 0.8:` 能保证只有 `result` 非空时才访问其 `.score` 属性。

### 三元表达式（条件表达式）

Python提供单行条件赋值语法：

```python
label = "正类" if probability >= 0.5 else "负类"
```

等价于完整的 `if/else` 块，适合简单的值选择场景，在AI推理结果的标签映射中十分常见。

---

## 实际应用

**场景1：AI模型置信度阈值过滤**

```python
confidence = model.predict_proba(sample)[0][1]  # 取正类概率

if confidence >= 0.9:
    decision = "自动通过"
elif confidence >= 0.6:
    decision = "人工复核"
else:
    decision = "自动拒绝"
```

这种三档阈值结构在信贷审批、内容审核等AI系统中是标准模式，三个阈值将整个概率空间 [0, 1] 切分为三个互不重叠的区间。

**场景2：数据预处理中的缺失值处理**

```python
if age is None or age < 0 or age > 150:
    age = median_age  # 用训练集中位数填充异常值
```

这里 `or` 连接的三个条件共同定义了"无效年龄"的范围，任意一个为 `True` 即触发填充逻辑。

**场景3：根据运行环境切换模型设备**

```python
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
```

这是PyTorch项目中出现频率极高的一行代码，用三元表达式在GPU可用时自动切换至GPU推理。

---

## 常见误区

**误区1：用多个独立 `if` 替代 `elif`，导致逻辑错误**

```python
# 错误写法：即使第一个if已匹配，后续if仍会被检查
if score >= 60:
    grade = "及格"
if score >= 80:   # 当score=85时，grade会被覆盖两次
    grade = "良好"
```

改用 `elif` 后，一旦 `score >= 60` 匹配，`elif score >= 80` 就不会再执行，逻辑才是正确的互斥分支。在AI系统中，这类错误可能导致标签被静默覆盖而难以调试。

**误区2：混淆赋值运算符 `=` 与相等比较运算符 `==`**

`if x = 5:` 在Python中会直接抛出 `SyntaxError`（而在C语言中则是合法但危险的写法）。条件判断中必须使用 `==` 进行相等性比较，使用 `is` 进行对象身份比较（尤其是与 `None` 比较时应写 `if x is None:` 而非 `if x == None:`）。

**误区3：将浮点数用 `==` 做精确比较**

模型输出的概率值是浮点数，`if prob == 0.1:` 几乎永远不会成立，因为浮点数在IEEE 754标准下存在精度误差（如 `0.1 + 0.2` 的结果是 `0.30000000000000004`）。正确做法是使用区间判断：`if abs(prob - 0.1) < 1e-6:`。

---

## 知识关联

**与运算符的关系**：条件判断的 `if` 后必须跟一个能求值为布尔类型的表达式，这正是比较运算符（`>`、`<`、`==`、`!=`、`>=`、`<=`）和逻辑运算符（`and`、`or`、`not`）的用武之地。没有运算符知识，就无法构造有意义的条件表达式。

**通往循环（for/while）的桥梁**：`for` 和 `while` 循环内部几乎总是包含条件判断——`break` 语句（跳出循环）和 `continue` 语句（跳过本次迭代）都依附于 `if` 结构使用，例如 `if loss < 1e-4: break` 用于在损失收敛时提前终止训练循环。掌握条件判断是理解循环中流程控制的前提。