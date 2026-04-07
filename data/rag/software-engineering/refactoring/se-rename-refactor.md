---
id: "se-rename-refactor"
concept: "重命名重构"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 1
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

# 重命名重构

## 概述

重命名重构（Rename Refactoring）是指在不改变代码行为的前提下，将变量、方法、类或参数的名称替换为能够准确表达其语义的标识符。这是所有重构手法中操作频率最高、入门门槛最低的一种，Martin Fowler 在 1999 年出版的《重构：改善既有代码的设计》中将其列为首要推荐手法，并明确指出"修改函数名称"（Rename Function）是消除命名异味的直接工具。

重命名重构的必要性源于代码命名的衰退过程。随着需求变更，原本准确的名称 `getTempData()` 可能已经演变为一个返回用户账户余额的方法，此时名称与功能之间产生了语义鸿沟。Philip Karlton 曾说"计算机科学中最难的两件事之一就是命名"，而重命名重构正是修复这一问题的系统化手段。

重命名重构之所以重要，是因为代码被阅读的次数远多于被编写的次数。研究表明，开发者平均花费 58% 的时间阅读代码，而非编写代码。一个名为 `d` 的变量比一个名为 `elapsedDays` 的变量需要额外的认知成本来解读，这种成本在大型代码库中会成倍累积。

---

## 核心原理

### 语义化命名的三个维度

重命名重构要求新名称在三个维度上同时达标：**意图（Intent）**、**作用域（Scope）**和**类型暗示（Type Hint）**。

- **意图**：方法名应表达"做什么"而非"怎么做"。将 `calcXYZ()` 重命名为 `calculateMonthlyInterestRate()` 揭示了方法的业务意图。
- **作用域**：局部变量可以使用较短名称（如循环变量 `i`），而类级成员变量应使用完整描述性名称（如 `customerOrderCount`）。
- **类型暗示**：布尔变量应以 `is`、`has`、`can` 开头，如 `isPaymentConfirmed`；返回集合的方法应使用复数形式，如 `getActiveOrders()`。

### 安全重命名的操作步骤

重命名重构的核心要求是**全范围替换**，而非手动查找替换。手动修改极易遗漏，因此现代 IDE 提供了专用的重命名操作：

1. 在 IntelliJ IDEA 或 VS Code 中，选中目标标识符，按 `Shift+F6`（IntelliJ）或 `F2`（VS Code）触发重命名。
2. IDE 会通过静态分析找到该标识符的所有引用点，包括跨文件引用、接口实现、子类覆盖等。
3. 预览所有将被修改的位置，确认后一次性应用。
4. 如果项目包含反射调用（如 `Class.forName("OldClassName")`），IDE 可能无法自动检测，需手动排查字符串中的硬编码名称。

如果不使用 IDE 辅助，安全的手动流程是：先添加新名称的别名，让新旧名称共存一段时间，通过编译和测试后再删除旧名称。

### 命名模式与反模式

**正确命名模式**：

| 类型 | 反模式 | 正确模式 |
|------|--------|---------|
| 方法 | `process()` | `validateAndSaveUserProfile()` |
| 布尔变量 | `flag` | `isEmailVerified` |
| 类 | `Manager2` | `CustomerOrderService` |
| 常量 | `N` | `MAX_RETRY_ATTEMPTS` |

**命名长度的平衡**：重命名不意味着名称越长越好。`getTheListOfActiveCustomerAccountsFromDatabase()` 这样的名称过度冗余，应精简为 `findActiveCustomerAccounts()`，去掉实现细节（"FromDatabase"是实现，非语义）。

---

## 实际应用

### 示例一：变量重命名

重构前：
```python
def calc(x, y, n):
    r = x * (1 + y) ** n
    return r
```

重构后：
```python
def calculateCompoundInterest(principal, annualRate, years):
    finalAmount = principal * (1 + annualRate) ** years
    return finalAmount
```

参数 `x`、`y`、`n` 和局部变量 `r` 经过重命名后，无需注释即可理解这是复利计算公式 `A = P(1+r)^n`。

### 示例二：类名重命名

一个最初处理数据导入的类 `DataHandler`，随着业务演进变成了专门解析 CSV 格式发票文件的类。重命名为 `InvoiceCsvParser` 后，新接手的开发者无需阅读类内部代码即可理解其职责边界。

### 示例三：消除误导性命名

方法 `getUserData()` 实际执行了数据库写操作（记录用户访问日志）。这是典型的误导性命名，应重命名为 `logUserAccessAndReturnProfile()`，或更好的做法是将方法拆分，让每个方法只做一件事并准确命名。

---

## 常见误区

### 误区一：重命名等于搜索替换文本

很多初学者使用编辑器的"全局搜索替换"功能来执行重命名重构，这会导致严重问题。例如将变量 `count` 替换为 `itemCount`，可能同时修改了注释、字符串字面量，甚至其他模块中含有 `count` 的不相关变量名（如 `discountRate` 中的 `count` 子串）。正确做法是使用 IDE 的语义感知重命名功能，它基于抽象语法树（AST）定位引用，而非字符串匹配。

### 误区二：缩写命名是为了"简洁"

`usrMgr`、`acctSvc`、`invProc` 这类缩写命名在短期内看起来简洁，但当团队新成员或半年后的自己接手代码时，缩写的含义需要重新猜测。Google 的 Java 编码规范明确要求避免非通用缩写（"通用"指如 `URL`、`ID` 这类行业标准缩写）。重命名重构的目标是用完整的词汇传达语义，而不是追求键盘输入的省力。

### 误区三：认为重命名会引入风险而不愿操作

有开发者担心"修改名称可能破坏系统"。实际上，在使用 IDE 辅助重命名的条件下，只要代码没有依赖字符串形式的反射调用，重命名是零行为变更的操作——因为重命名本身不改变任何逻辑，只改变标识符。真正的风险来自于不重命名，让命名腐化积累成理解障碍。

---

## 知识关联

重命名重构的前置概念是**代码异味**中的"神秘命名（Mysterious Name）"异味，这是 Fowler 在《重构》第二版中列出的第一种代码异味，重命名重构是消除该异味的直接手段。另一个前置概念是**重构概述**中关于"不改变可观测行为"的核心约束——理解这个约束后才能区分重命名（安全）和修改方法签名语义（可能破坏调用方）的本质差别。

在学习重命名重构之后，下一步是**微重构**，它将单次小改动组合成系统化的改进序列。例如先对一个方法内所有变量执行重命名重构，再决定是否需要进一步提取方法（Extract Method）。掌握重命名重构为微重构提供了最基础的操作单元——每次微重构序列几乎都以重命名作为起点或结束动作，用以确保最终代码的可读性。