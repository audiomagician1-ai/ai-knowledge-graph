---
id: "testing-basics"
concept: "测试基础"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 3
is_milestone: false
tags: ["unittest", "tdd", "assertion"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "S"
quality_score: 83.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 测试基础

## 概述

软件测试是通过执行程序来发现代码缺陷的系统性过程。在AI工程的编程实践中，测试分为多个层级：**单元测试（Unit Test）**针对最小可测试单元（通常是单个函数或类方法），**集成测试（Integration Test）**验证多个模块协同工作的正确性，**端到端测试（E2E Test）**则模拟真实用户的完整操作流程。理解这三个层级的边界，是写出有效测试代码的前提。

测试驱动开发（Test-Driven Development，TDD）由Kent Beck在2003年出版的《Test-Driven Development: By Example》中系统化阐述，其核心循环被称为"红-绿-重构（Red-Green-Refactor）"：先写一个必然失败的测试（红），再写最少量的代码使测试通过（绿），最后在不改变行为的前提下改善代码结构（重构）。这个循环通常每次持续不超过10分钟。

在AI工程项目中，测试尤为关键，因为数据预处理函数、特征工程管道和模型推理接口的错误往往难以通过肉眼排查。一个未经测试的数据清洗函数可能静默地将`NaN`替换为0，导致模型训练结果偏差，而这类缺陷在没有自动化测试的情况下可能在生产环境中潜伏数周。

---

## 核心原理

### 单元测试的结构：AAA模式

单元测试通常遵循**Arrange-Act-Assert（准备-执行-断言）**三段式结构。以Python的`unittest`框架为例：

```python
import unittest

def add(a, b):
    return a + b

class TestAddFunction(unittest.TestCase):
    def test_positive_numbers(self):
        # Arrange
        x, y = 3, 5
        # Act
        result = add(x, y)
        # Assert
        self.assertEqual(result, 8)
```

`assertEqual`、`assertTrue`、`assertRaises`是最常用的三类断言方法。其中`assertRaises`专门用于验证函数在异常输入下是否正确抛出错误，这与错误处理（try/except）的使用场景直接相关——测试代码验证的正是生产代码的异常分支是否被正确触发。

### 测试覆盖率与其局限

**代码覆盖率（Code Coverage）**用公式表示为：

$$\text{覆盖率} = \frac{\text{被测试执行的代码行数}}{\text{总代码行数}} \times 100\%$$

Python的`coverage.py`工具可以生成详细的覆盖率报告。行业普遍将80%视为可接受的最低覆盖率门槛，但覆盖率100%并不等于代码无缺陷——测试可以执行到某一行代码，但如果断言写错，依然无法发现逻辑错误。例如，`assert result >= 0`会让一个返回`-1`的加法函数"通过"测试。

### 集成测试与模块边界

集成测试验证的是**模块接口的契约**，而非模块内部实现。当你的AI推理模块依赖一个数据库读取模块时，集成测试需要将两者连接起来，验证数据从数据库到推理结果的完整路径是否正确。

在集成测试中，**Mock（模拟对象）**是隔离外部依赖的关键工具。Python的`unittest.mock.patch`可以将真实的数据库连接替换为返回固定数据的假对象，使测试在没有真实数据库的环境中稳定运行。这种隔离保证了集成测试失败时，问题一定出在被测模块的集成逻辑上，而非外部服务的可用性上。

### TDD的红-绿-重构实践

TDD要求测试代码**先于**生产代码存在。以实现一个文本截断函数为例：

1. **红**：写`test_truncate_at_10_chars`，此时`truncate()`函数不存在，测试必然报错（`NameError`）
2. **绿**：实现`truncate(text, limit): return text[:limit]`，测试通过
3. **重构**：添加边界检查（`limit`为负数时的处理），同时保持测试继续通过

每次重构后重新运行所有测试，是保证重构安全性的唯一机制。

---

## 实际应用

**AI数据预处理管道的单元测试**：假设有一个函数`normalize_scores(scores)`将分数列表归一化到`[0, 1]`区间。单元测试应覆盖四种情况：正常输入、全相同值（分母为零的边界情况）、空列表、含`None`的列表。其中分母为零的情况直接对应生产代码中必须存在的`try/except ZeroDivisionError`分支。

**pytest框架的参数化测试**：使用`@pytest.mark.parametrize`装饰器，可以用一个测试函数覆盖多组输入输出对，避免重复编写结构相同的测试方法。例如验证`tokenize()`函数对中文、英文、混合文本三种输入分别返回正确的token列表，只需一个测试函数配合三组参数即可完成。

**集成测试的真实场景**：在AI推理服务中，集成测试通常覆盖"接收HTTP请求 → 调用预处理模块 → 加载模型 → 返回预测结果"这条完整链路。使用`requests-mock`库可以在不启动真实HTTP服务器的情况下，验证各模块之间的数据格式协议是否匹配。

---

## 常见误区

**误区1：测试代码不需要维护**
许多开发者将测试代码视为一次性脚本，不按函数命名规范命名，不处理测试数据的清理（teardown）。实际上，一个测试数据库连接未在`tearDown()`中关闭，会导致后续测试因端口占用而随机失败，这类"脆弱测试（Flaky Test）"比没有测试更有害，因为它们会让团队逐渐停止信任测试结果。

**误区2：集成测试可以完全替代单元测试**
集成测试的执行成本（启动时间、依赖服务数量）远高于单元测试。一个包含200个单元测试的项目可以在3秒内完成全部测试；同等数量的集成测试可能需要5分钟。如果开发者每次提交代码都需要等待5分钟，他们会减少测试频率，测试保护网就会失效。**测试金字塔**原则建议：单元测试数量最多，集成测试次之，E2E测试最少。

**误区3：TDD会降低开发速度**
短期来看，TDD确实会让单个功能的首次开发时间增加约15-35%。但研究（Microsoft Research 2008年的"Realizing quality improvement through test driven development"）表明，采用TDD的团队在交付后的缺陷密度降低了40-90%，因此总体调试和修复时间显著减少。

---

## 知识关联

**与前置概念的连接**：单元测试的测试对象就是**函数**——每个测试用例针对一个函数的特定行为。**模块与导入**决定了测试文件如何引用被测代码，Python中`from mymodule import my_function`是测试文件的标准起点。**错误处理（try/except）**与`assertRaises`形成直接对应关系：生产代码用try/except处理异常，测试代码用`assertRaises`验证异常处理逻辑是否被正确触发。

**通向后续概念**：掌握单元测试和集成测试的基本框架后，**前端测试**引入了DOM操作验证、组件渲染测试等浏览器环境特有的挑战，需要Jest、Testing Library等专门工具。**契约式设计（Design by Contract）**则将测试中的"前置条件-后置条件"思想内化为代码本身的一部分，用`assert`语句直接在函数内声明输入输出的约束，是测试思维从测试文件向生产代码的延伸。