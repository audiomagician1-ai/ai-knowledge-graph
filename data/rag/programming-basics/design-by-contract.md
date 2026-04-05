---
id: "design-by-contract"
concept: "契约式设计"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 3
is_milestone: false
tags: ["assertion", "precondition", "defensive"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 契约式设计

## 概述

契约式设计（Design by Contract，DbC）是由法国计算机科学家 Bertrand Meyer 于1986年提出的软件设计方法论，并在他发明的 Eiffel 编程语言中首次系统性实现。其核心思想是：软件模块之间的调用关系类似于法律合同——调用方必须满足前置条件（precondition），被调用方则保证完成后置条件（postcondition），而不变式（invariant）则是双方都必须维护的永久约束。这三类断言共同构成了函数或类的"契约文档"，使代码意图从注释中脱离出来成为可执行的规格说明。

该方法论在1990年代随着Eiffel语言商业化而逐渐传播，随后影响了Python的`assert`语句规范用法、Java的Contract库，以及C++的`GSL::Expects()`/`GSL::Ensures()`宏。在AI工程场景下，契约式设计特别重要：机器学习模型的输入往往有严格的数值范围约束（例如概率值必须在[0,1]区间），特征向量必须具有固定维度，缺失这些约束会导致模型静默输出错误结果而不抛出任何异常。

与防御性编程中"到处写if-else"的思路不同，契约式设计要求将职责明确归属——前置条件是调用方的义务，后置条件是被调用方的义务，这种分工使调试时能立即确定是哪一方违约，而不是在整条调用链上逐一排查。

## 核心原理

### 前置条件（Precondition）

前置条件描述调用某函数之前必须为真的条件，**违反时责任在调用方**。在Python中使用`assert`实现前置条件时，其形式为 `assert condition, "error message"`。例如一个计算 softmax 的函数，其前置条件包含：输入必须是一维 `numpy` 数组，且长度大于0，且不含 `NaN` 值。

```python
def softmax(x):
    assert x.ndim == 1, "输入必须是一维数组"
    assert len(x) > 0, "输入不能为空"
    assert not np.any(np.isnan(x)), "输入不能含NaN"
    # 计算逻辑...
```

前置条件应当仅检查调用方能够控制的输入，不应检查环境状态（如文件是否存在），后者属于异常处理的职责。

### 后置条件（Postcondition）

后置条件描述函数执行完毕后必须为真的条件，**违反时责任在被调用方（函数本身）**。继续softmax的例子，其后置条件为：输出数组所有元素之和等于1.0（允许浮点误差），且每个元素都在[0,1]之间。

```python
def softmax(x):
    # 前置条件...
    result = np.exp(x - np.max(x)) / np.sum(np.exp(x - np.max(x)))
    assert abs(np.sum(result) - 1.0) < 1e-6, "输出之和必须为1"
    assert np.all(result >= 0) and np.all(result <= 1), "输出必须在[0,1]"
    return result
```

后置条件的价值在于它将函数的数学规格说明编码进代码本身。当重构 softmax 的实现算法时，后置条件断言会立即验证新实现是否仍满足规格，相当于一个内嵌的单元测试。

### 不变式（Invariant）

不变式是对类的状态约束，要求在**所有公开方法执行前后**该条件都成立（方法执行中间可以暂时违反）。以一个维护滑动窗口特征的类为例：

```python
class SlidingWindowBuffer:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.buffer = []
        self._check_invariant()

    def _check_invariant(self):
        assert len(self.buffer) <= self.max_size, "缓冲区超出最大容量"
        assert self.max_size > 0, "最大容量必须为正整数"

    def push(self, value):
        self._check_invariant()  # 入口检查
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)
        self.buffer.append(value)
        self._check_invariant()  # 出口检查
```

不变式帮助在类的整个生命周期内防止状态腐化，对于持续接收流数据的AI推理服务尤为重要。

### 与`try/catch`的职责分工

契约式设计的断言（`assert`）与 `try/except` 错误处理服务于**不同目的**，不可互换：`assert`用于捕捉程序员错误（逻辑缺陷），在生产环境中可以用 `python -O` 标志完全禁用（优化模式下Python会跳过所有`assert`语句）；而`try/except`用于处理运行时的外部不确定性（网络超时、文件损坏）。若将前置条件写成`try/except`，则在性能敏感的推理循环中会带来不必要的开销，并掩盖了"这是编程错误而非运行时问题"的语义信息。

## 实际应用

**AI模型推理管道中的契约**：在一个图像分类推理函数中，前置条件可规定输入张量形状必须为`(batch_size, 3, 224, 224)`（ImageNet标准尺寸），像素值必须在[-2.12, 2.64]（ImageNet均值方差归一化后的合法范围）；后置条件规定输出 logits 张量形状为`(batch_size, 1000)`，且不含`NaN`或`Inf`。这类契约能在数据预处理管道失效时立即定位故障，而非让错误传播到损失计算步骤后才报错。

**数据转换函数的契约**：对于将原始用户行为日志转换为训练特征的函数，前置条件可以规定输入字典必须包含`timestamp`、`user_id`、`event_type`三个键，且`timestamp`的值必须是Unix时间戳（大于0的整数）；后置条件规定输出特征向量的维度恰好等于预定义的`FEATURE_DIM = 128`常量。

**Python的`hypothesis`库与契约结合**：`hypothesis`库可以自动生成大量随机输入来检验契约断言是否在边界条件下也能成立，相当于将契约转化为基于属性的测试（property-based testing），这是在AI项目中验证数据处理函数正确性的高效方法。

## 常见误区

**误区一：用`assert`校验外部输入（如用户请求或文件内容）**。`assert`在生产环境运行`python -O`时会被完全跳过，因此用`assert`保护来自API请求的数据会造成安全漏洞。外部输入必须用`raise ValueError`或专门的数据验证库（如`pydantic`）处理，只有对内部函数间调用的逻辑约束才应使用`assert`。

**误区二：前置条件过度严苛导致函数难以复用**。若一个函数的前置条件要求输入必须是经过特定归一化方法处理的数据，则该函数与特定预处理流程深度耦合。正确做法是让函数内部处理或转换合理范围内的输入，只有真正无法执行的状态（如None输入、维度完全错误）才应列入前置条件。

**误区三：把后置条件当作性能优化的障碍而全部删除**。正确做法是区分开发阶段和生产阶段的策略：在训练、测试和调试阶段保持所有断言启用；在对延迟极敏感的在线推理服务中，可以选择性地保留对模型输出健全性（sanity check）的断言，而禁用内部计算步骤的中间断言。

## 知识关联

**依赖前置知识**：`try/except` 错误处理提供了异常机制的基础词汇，契约式设计在此基础上明确了"谁的责任用什么机制表达"的语义分工——编程逻辑错误用`assert`，运行时外部异常用`try/except`。测试基础知识则与契约形成直接对应：前置条件对应测试用例的setup约束，后置条件对应`assert`验证语句，不变式对应类级别的fixture验证。

**向上支撑的能力**：掌握契约式设计后，可以自然地理解类型系统（如Python的`typing`模块和`mypy`静态检查器），它们本质上是在编译期强制执行一部分契约；也为理解形式化验证方法（如使用Z3 SMT求解器自动证明函数满足规格）打下概念基础。在AI工程的实践中，契约式设计的思维模式直接迁移到ML管道的数据验证框架（如`Great Expectations`库），该库的"期望"（Expectation）概念与后置条件在语义上完全同构。