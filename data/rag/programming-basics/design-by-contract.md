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
quality_tier: "B"
quality_score: 48.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
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

契约式设计（Design by Contract，简称 DbC）是由 Bertrand Meyer 于 1986 年在设计 Eiffel 编程语言时提出的软件设计方法论。其核心思想来源于法律合同的隐喻：调用方（客户）和被调用方（供应商）之间存在明确的权利与义务关系，双方必须共同遵守约定，否则程序应当立即以可追踪的方式失败，而不是悄悄产生错误结果。

契约式设计通过三种断言来形式化描述函数或方法的行为约定：**前置条件（Precondition）**、**后置条件（Postcondition）**和**不变式（Invariant）**。在 AI 工程项目中，模型推理函数、数据预处理管道和特征工程模块往往包含隐含假设（例如"输入张量的值域必须在 [0,1] 之间"），这些假设一旦被违反，模型可能静默地输出错误预测而不抛出任何异常。契约式设计将这些隐含假设显式化，使问题在第一时间暴露。

该方法论已被 Python 的 `assert` 语句、Java 的 `@Requires`/`@Ensures` 注解库（如 Cofoja）以及 Python 第三方库 `icontract`、`deal` 等工具所支持，成为现代防御性编程实践中可落地的具体技术。

---

## 核心原理

### 前置条件（Precondition）

前置条件是**调用方在调用函数之前必须保证为真的条件**。如果前置条件被违反，责任在调用方，而非函数本身。例如，一个负责将图像归一化的函数：

```python
def normalize_image(img_array):
    assert img_array.ndim == 3, "前置条件违反：输入必须是3维数组 (H, W, C)"
    assert img_array.dtype == np.uint8, "前置条件违反：像素值类型必须为uint8"
    return img_array / 255.0
```

前置条件只检查**调用者的责任范围**，因此不应在函数内部修复违反前置条件的输入——修复行为是调用者的职责，函数只需快速失败并报告违反位置。

### 后置条件（Postcondition）

后置条件是**函数执行完毕后必须保证为真的条件**，代表函数对调用方的承诺。如果后置条件被违反，责任在函数实现本身。以下示例用 `icontract` 库的 `@icontract.ensure` 装饰器表达后置条件：

```python
import icontract

@icontract.ensure(lambda result: 0.0 <= result <= 1.0,
                  "后置条件违反：概率输出必须在[0,1]区间内")
def predict_probability(features):
    raw_score = model.forward(features)
    return sigmoid(raw_score)
```

后置条件在测试阶段能够捕获回归错误：若某次模型权重更新导致 sigmoid 分支溢出产生 `NaN`，后置条件断言会在预测函数返回处立即失败，而非在下游损失计算时产生难以追踪的错误。

### 不变式（Invariant）

不变式是**在对象生命周期的任意可观测时刻都必须保持为真的条件**，通常用于描述类的状态约束。不变式在每次公开方法调用前后都应成立（方法执行期间可以临时违反）。以一个维护滑动窗口特征缓存的类为例：

```python
class FeatureBuffer:
    def __init__(self, max_size: int):
        assert max_size > 0
        self._buffer = []
        self._max_size = max_size

    def _check_invariant(self):
        assert len(self._buffer) <= self._max_size, \
            f"不变式违反：缓冲区长度 {len(self._buffer)} 超过上限 {self._max_size}"

    def push(self, feature_vector):
        self._check_invariant()          # 入口检查
        self._buffer.append(feature_vector)
        if len(self._buffer) > self._max_size:
            self._buffer.pop(0)
        self._check_invariant()          # 出口检查
```

不变式将"缓冲区长度不得超过 `max_size`"这一业务规则从注释文字提升为可执行的运行时检查。

### 契约的互惠关系：里氏代入原则的精确表述

契约式设计提供了一种精确表述**里氏替换原则（Liskov Substitution Principle）**的方式：子类覆写方法时，前置条件只能**弱化或保持不变**（接受更多输入），后置条件只能**强化或保持不变**（提供更强承诺），不变式必须**维持或强化**。这被称为"前置条件逆变，后置条件协变"规则，违反此规则会导致多态调用时的运行时契约违反。

---

## 实际应用

**AI 数据预处理管道中的前置条件验证**：在特征工程函数入口添加前置条件，检查 DataFrame 的必要列是否存在、数值列是否含有 `NaN`、标签列的取值范围是否合法。这将数据质量问题的发现时刻从模型训练失败时（数小时后）提前至数据加载完成后（秒级）。

**模型推理服务的后置条件监控**：在在线推理服务中，对每次推理结果添加后置条件断言，例如分类模型的输出概率之和应在 `[0.99, 1.01]` 区间（考虑浮点误差）。在生产环境可将断言失败转换为告警日志而非抛出异常，实现非阻断式的合规性监控。

**配置对象的不变式保护**：超参数配置类（`HyperParams`）可通过不变式确保 `learning_rate > 0`、`batch_size` 为 2 的整数幂次、`dropout_rate ∈ [0, 1)` 等约束，防止配置错误在训练数千步后才以梯度爆炸的形式显现。

---

## 常见误区

**误区一：用契约替代单元测试**
契约式设计与测试是互补而非替代关系。断言在运行时检查**实际执行路径**上的单个调用，而单元测试通过**多组精心设计的输入**系统地验证函数行为。契约无法证明函数对所有合法输入都正确；测试无法覆盖生产环境的所有动态路径。两者结合使用才能最大化防御效果。

**误区二：在生产代码中全局禁用 assert**
Python 的 `python -O` 优化模式会剥除所有 `assert` 语句。如果将关键的安全约束（如权限验证）写入 `assert`，生产环境中这些检查将完全失效。应当区分**契约性断言**（可在经过充分验证后关闭的性能开销）和**防御性检查**（应始终执行的业务约束）：后者必须使用显式的 `if ... raise` 语句，而非 `assert`。

**误区三：前置条件越严格越好**
过于严格的前置条件会使函数难以被合法调用，产生"防御过度"的接口设计。例如，若归一化函数的前置条件要求输入"不含任何 NaN 且均值严格等于 0.5"，则调用方需要执行大量预处理，实际上将自身的实现责任转嫁给了调用者。前置条件应当只约束**函数正确运行所必需的最小条件集合**。

---

## 知识关联

契约式设计在机制上依赖**错误处理（try/catch）**：当断言失败抛出 `AssertionError` 或自定义异常时，调用栈的上层需要决定是传播失败还是记录日志后降级处理。已有 try/catch 基础的学习者能够立刻理解"前置条件失败应向上传播而非捕获"的原则，因为在调用方的 catch 块中静默忽略前置条件违反会掩盖真正的接口滥用。

契约式设计与**测试基础**的关联体现在：前置条件和后置条件的集合天然定义了函数的等价类划分，直接指导等价类测试用例的设计——每个违反前置条件的等价类对应一类"非法输入测试"，每个满足前置条件但期望特定后置条件成立的分支对应一类"合法输入测试"。换言之，写好契约文档的函数自带了系统性的测试规格说明书。