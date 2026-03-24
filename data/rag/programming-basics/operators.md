---
id: "operators"
concept: "运算符"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 运算符

## 概述

运算符（Operator）是编程语言中用于对一个或多个操作数执行特定计算或逻辑判断的符号。在Python等AI工程常用语言中，运算符直接作用于变量和数据类型所存储的值，产生新的计算结果或布尔判断值。例如，`+` 符号既可以对两个整数执行加法，也可以将两个字符串拼接，这种行为称为运算符重载（Operator Overloading）。

运算符的概念源于数学符号系统，但在1950年代FORTRAN语言设计时被正式纳入编程语言规范。Python在设计时引入了运算符优先级（Operator Precedence）体系，共定义了超过20种运算符，按照从低到高排列。理解运算符的优先级顺序对于编写正确的AI模型训练循环（如计算损失函数梯度）至关重要，错误的运算顺序会导致数值计算完全偏离预期。

在AI工程实践中，运算符频繁出现在数据预处理、特征工程和模型评估代码中。例如，计算均方误差（MSE）时需要组合使用算术运算符 `**`（幂运算）和 `/`（除法）；判断样本标签是否匹配时使用比较运算符 `==`；过滤满足多个条件的数据行时使用逻辑运算符 `and` 或 `&`。

## 核心原理

### 算术运算符

Python提供7种基础算术运算符：`+`（加）、`-`（减）、`*`（乘）、`/`（除，结果永远是浮点数）、`//`（整除，向下取整）、`%`（取模，返回余数）、`**`（幂运算）。其中 `//` 和 `%` 满足关系式：`a == (a // b) * b + (a % b)`，这在数据集分批处理（batch）时非常有用——当数据集有1000条样本、批大小为32时，`1000 % 32 = 8` 告诉你最后一批只有8条样本。整除运算 `7 / 2 = 3.5` 但 `7 // 2 = 3`，这是初学者最容易混淆的地方。

### 比较运算符

比较运算符共6种：`==`（等于）、`!=`（不等于）、`>`（大于）、`<`（小于）、`>=`（大于等于）、`<=`（小于等于）。所有比较运算符的返回值类型固定为布尔值 `True` 或 `False`，而非数字或字符串。需特别注意，`==` 比较的是**值是否相等**，而Python的 `is` 运算符比较的是**内存地址是否相同**，二者不可混用。例如 `[1, 2] == [1, 2]` 返回 `True`，但 `[1, 2] is [1, 2]` 返回 `False`，因为这是两个不同的列表对象。

### 逻辑运算符

Python的逻辑运算符包括 `and`、`or`、`not` 三个关键字（NumPy/Pandas环境中对应位运算符 `&`、`|`、`~`）。它们遵循**短路求值**（Short-circuit Evaluation）规则：`and` 表达式中若左侧为 `False`，右侧表达式不会执行；`or` 表达式中若左侧为 `True`，右侧同样跳过。优先级排序为：`not` > `and` > `or`。因此 `True or False and False` 的结果是 `True`，因为 `and` 先执行，`False and False = False`，再 `True or False = True`。

### 赋值运算符与增强赋值

赋值运算符 `=` 将右侧表达式的值绑定到左侧变量名。Python还提供增强赋值运算符，如 `+=`、`-=`、`*=`、`/=`、`//=`、`**=`，它们是"先运算后赋值"的简写形式。例如在训练循环中常见的 `loss += batch_loss`，等价于 `loss = loss + batch_loss`，用于累加每个批次的损失值。增强赋值对列表类型会触发原地修改，而普通赋值会创建新对象，这一差异影响内存使用效率。

### 运算符优先级

Python运算符优先级从高到低的关键层次为：`**` > 一元 `+/-` > `* / // %` > 二元 `+ -` > 比较运算符 > `not` > `and` > `or`。表达式 `2 + 3 * 4 ** 2` 的计算顺序是：先 `4**2=16`，再 `3*16=48`，最后 `2+48=50`。建议在复杂表达式中**主动添加括号**，如 `(2 + 3) * (4 ** 2)`，以消除优先级歧义。

## 实际应用

**数据标准化（Normalization）** 中，将特征值缩放到 [0, 1] 区间的公式为：`x_norm = (x - x_min) / (x_max - x_min)`，此处同时使用了减法 `-` 和除法 `/` 两种算术运算符，且除法在Python 3中自动返回浮点结果。

**过滤训练数据** 时，筛选年龄大于18且标签为正类的样本：`mask = (df['age'] > 18) & (df['label'] == 1)`，这里 `>` 和 `==` 是比较运算符，`&` 是Pandas中对应 `and` 的位运算符，因为Pandas的Series不支持Python原生 `and`。

**计算准确率** 时，`accuracy = correct_count / total_count * 100`，若 `total_count = 0` 会触发 `ZeroDivisionError`，因此实际代码中需使用比较运算符提前判断：`accuracy = correct_count / total_count * 100 if total_count > 0 else 0`。

## 常见误区

**误区一：混淆 `=` 与 `==`**。`=` 是赋值运算符，将值写入变量；`==` 是比较运算符，返回布尔值。在条件判断中写成 `if x = 5:` 会直接触发 `SyntaxError`，Python语法层面禁止在条件语句中使用赋值运算符（Python 3.8+的海象运算符 `:=` 是例外）。

**误区二：整数除法的类型预期错误**。Python 2中 `7 / 2 = 3`（整数除法），但Python 3中 `7 / 2 = 3.5`（浮点除法）。许多从Python 2迁移的代码在Python 3环境下因此产生数值错误。若需整除行为，应显式使用 `//` 运算符。

**误区三：在NumPy/Pandas中使用 `and` 替代 `&`**。对NumPy数组或Pandas Series使用 `and` 运算符会抛出 `ValueError: The truth value of an array is ambiguous`，因为 `and` 要求操作数是单一布尔值，而 `&` 才能对数组执行逐元素位运算。

## 知识关联

运算符直接依赖**变量与数据类型**的知识：整数类型支持 `//` 整除，浮点数类型支持 `/` 浮点除法，字符串类型支持 `+` 拼接和 `*` 重复，布尔类型是所有比较运算符和逻辑运算符的输出类型。不同数据类型对同一运算符的响应行为完全不同，这是理解运算符的前提。

比较运算符和逻辑运算符的输出结果（`True`/`False`）是**条件判断（if/else）** 的直接输入。`if score >= 60 and subject == 'math':` 这条语句中，`>=` 和 `==` 计算出两个布尔值，`and` 将它们合并为单一布尔值，再由 `if` 决定是否执行分支代码块。可以说，比较运算符和逻辑运算符是 `if/else` 结构得以运作的计算基础。
