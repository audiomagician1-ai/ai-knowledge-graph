---
id: "regex-basics"
concept: "正则表达式"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 3
is_milestone: false
tags: ["regex", "pattern-matching", "text-processing"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 正则表达式

## 概述

正则表达式（Regular Expression，简称 regex 或 regexp）是一种描述字符串模式的形式化语言，由数学家 Stephen Cole Kleene 于1956年首次提出，基于他在形式语言理论中定义的"正则集合"概念。最早的实用实现出现在 Unix 工具 `grep`（1973年由 Ken Thompson 编写）中，此后被纳入 Perl、Python、Java 等几乎所有主流编程语言。

正则表达式的核心价值在于：用一行模式字符串替代数十行手写循环逻辑，完成字符串的**匹配、搜索、提取和替换**。例如，验证一个电子邮件地址格式，如果用 `for` 循环逐字符检查需要约30行代码，而用正则表达式 `^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$` 一行即可完成。在 AI 工程中，正则表达式广泛用于训练数据清洗、日志解析、文本特征提取和模型输出后处理。

---

## 核心原理

### 元字符与字符类

正则表达式由**普通字符**和**元字符**构成。元字符是拥有特殊含义的符号，共有14个核心元字符：`. ^ $ * + ? { } [ ] \ | ( )`。

| 元字符 | 含义 | 示例 |
|--------|------|------|
| `.` | 匹配除换行符外任意一个字符 | `a.c` 匹配 `abc`、`a1c` |
| `\d` | 匹配数字，等价于 `[0-9]` | `\d{4}` 匹配 `2024` |
| `\w` | 匹配字母、数字或下划线，等价于 `[a-zA-Z0-9_]` | `\w+` 匹配 `hello_123` |
| `\s` | 匹配任意空白字符（空格、制表符、换行） | `\s+` 可分割词语 |
| `[aeiou]` | 字符类，匹配括号内任意一个字符 | `[aeiou]` 匹配元音字母 |
| `[^0-9]` | 否定字符类，匹配**不**在括号内的字符 | `[^0-9]` 匹配非数字 |

### 量词与贪婪/懒惰匹配

量词控制前一个元素重复的次数：

- `*`：0次或多次
- `+`：1次或多次  
- `?`：0次或1次
- `{n,m}`：最少 n 次，最多 m 次

**贪婪匹配**是量词的默认行为：引擎尽可能多地匹配字符。对字符串 `<b>bold</b>`，模式 `<.+>` 会匹配整个 `<b>bold</b>`（贪婪），而 `<.+?>` 加上 `?` 变为**懒惰匹配**，只匹配 `<b>`。这一区别在解析 HTML 标签或 JSON 片段时至关重要，错误使用贪婪模式会导致提取结果范围过大。

### 分组、捕获与断言

圆括号 `()` 创建**捕获组**，允许提取子字符串。例如，模式 `(\d{4})-(\d{2})-(\d{2})` 应用于 `2024-01-15`，第1组捕获 `2024`，第2组捕获 `01`，第3组捕获 `15`。在 Python 中通过 `match.group(1)` 访问各组。

使用 `(?:...)` 创建**非捕获组**，参与匹配但不分配组编号，可提升执行效率。

**零宽断言**（lookahead/lookbehind）是高级特性：
- `(?=pattern)`：正向先行断言，位置后紧跟 pattern，但不消耗字符
- `(?<=pattern)`：正向后行断言，位置前紧跟 pattern

例如，`\d+(?= dollars)` 从文本 `100 dollars` 中只提取 `100`，不包含 ` dollars`。

### Python 中的 re 模块

Python 的 `re` 模块是 AI 工程中最常用的正则表达式接口，提供5个核心函数：

```python
import re

# re.match() — 只从字符串开头匹配
# re.search() — 扫描整个字符串，返回第一个匹配
# re.findall() — 返回所有非重叠匹配的列表
# re.sub() — 替换匹配内容
# re.compile() — 预编译模式，提升循环中重复使用的性能

pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
ips = pattern.findall("Server 192.168.1.1 and backup 10.0.0.2 are online.")
# 结果：['192.168.1.1', '10.0.0.2']
```

注意字符串前的 `r` 前缀（原始字符串）：它使 `\d`、`\b` 等反斜杠序列不被 Python 字符串解析器提前处理，而是原样传递给正则引擎。**始终使用原始字符串编写正则模式**。

---

## 实际应用

### AI 训练数据清洗

爬取的网页文本常含有 HTML 标签、多余空白和特殊编码字符。使用 `re.sub(r'<[^>]+>', '', text)` 可删除所有 HTML 标签；`re.sub(r'\s{2,}', ' ', text)` 将连续多个空白合并为单个空格，这是 NLP 预处理管道中的标准步骤。

### 日志文件解析

AI 训练任务产生的日志格式固定，如：
```
[2024-03-15 14:23:01] Epoch 5/100, loss=0.3421, acc=0.8912
```
正则模式 `Epoch (\d+)/\d+, loss=([\d.]+), acc=([\d.]+)` 可批量提取所有轮次的损失值和准确率，用于绘制训练曲线，比手动字符串切割更健壮。

### 模型输出后处理

大语言模型生成的文本有时包含不需要的格式标记。例如从模型输出中提取 JSON 块：`re.search(r'\{.*?\}', output, re.DOTALL)` 使用 `re.DOTALL` 标志让 `.` 也能匹配换行符，从而提取跨多行的 JSON 对象。

---

## 常见误区

### 误区1：用正则表达式解析 HTML/XML

正则表达式只能处理**正则语言**（有限状态自动机可识别的语言），而 HTML 是**上下文无关语言**，理论上无法被正则表达式完整解析。嵌套标签 `<div><div></div></div>` 用正则无法可靠匹配。实践中应使用 `BeautifulSoup` 或 `lxml` 等专用解析器。

### 误区2：`re.match()` 与 `re.search()` 等价

`re.match()` **只从字符串位置0开始**尝试匹配，而 `re.search()` 扫描整个字符串。对字符串 `"hello world"`，`re.match(r'world', s)` 返回 `None`，而 `re.search(r'world', s)` 返回匹配对象。这是调试正则时最常见的错误来源。

### 误区3：忽略 `re.compile()` 的性能价值

在循环中对100万行日志重复调用 `re.findall(r'\d+', line)` 时，Python 每次都要重新编译模式。改用 `pattern = re.compile(r'\d+')` 后在循环外预编译，实测在大文本处理中可带来约20-40%的速度提升，这在处理 GB 级训练语料时差异显著。

---

## 知识关联

正则表达式建立在**字符串操作**基础之上：`str.find()`、`str.split()`、`str.replace()` 处理固定字符串，而正则表达式处理**模式**。理解字符串索引和切片是读懂 `match.start()`、`match.end()` 返回值的前提。

正则表达式与**循环**的关系是替代关系：`re.findall()` 内部等价于一个扫描字符串、逐位尝试匹配的 `while` 循环，但由 C 语言实现的引擎执行效率远高于纯 Python 循环。因此，当字符串处理逻辑可以用正则模式描述时，优先用正则替代手写循环。

在 AI 工程的更广泛工具链中，正则表达式是**数据预处理**阶段的基础工具，在 tokenization（分词）之前对原始文本进行规范化。掌握正则表达式后，学习 `pandas` 的 `str.extract()` 和 `str.replace()` 方法时会发现它们直接接受正则模式参数，可对整列数据批量执行正则操作。
