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
quality_tier: "S"
quality_score: 82.9
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

# 正则表达式

## 概述

正则表达式（Regular Expression，缩写为 regex 或 regexp）是一种用特定符号描述字符串模式的形式语言，由数学家 Stephen Kleene 于 1956 年在其正则集合理论中首次形式化定义。最早的实用实现出现在 Unix 工具 grep（1973 年由 Ken Thompson 开发）中，此后逐步成为几乎所有编程语言的内置特性。正则表达式的理论基础是有限自动机（Finite Automaton）：每条正则表达式都可以被编译为一个确定性有限自动机（DFA）来执行匹配。

在 AI 工程的日常编程中，正则表达式用于清洗训练数据、提取非结构化文本中的实体（如 URL、邮箱、日期）、以及对模型输出进行后处理验证。与简单的字符串 `find()` 或 `split()` 相比，正则表达式能用一行代码表达"以字母开头、后跟 3-5 位数字、结尾为 `.csv`"这类复杂条件，大幅减少循环逻辑的冗余。

Python 标准库中的 `re` 模块是 AI 工程师最常用的正则接口，而更高性能的场景可使用第三方库 `regex`（支持可变长度反向查找等高级特性）。

---

## 核心原理

### 基本语法元素

正则表达式由**字面字符**和**元字符**两类符号构成。常用元字符及含义如下：

| 元字符 | 含义 | 示例 |
|--------|------|------|
| `.` | 匹配除换行符外任意单个字符 | `a.c` 匹配 `abc`、`a1c` |
| `^` / `$` | 匹配字符串开头 / 结尾 | `^Hello` |
| `*` / `+` / `?` | 前项重复 0+次 / 1+次 / 0或1次 | `\d+` |
| `{m,n}` | 前项重复最少 m 次、最多 n 次 | `\w{3,5}` |
| `[]` | 字符集合，匹配其中任意一个 | `[aeiou]` |
| `\|` | 或运算 | `cat\|dog` |
| `()` | 分组捕获 | `(\d{4})-(\d{2})` |

预定义字符类进一步简化书写：`\d` 等价于 `[0-9]`，`\w` 等价于 `[a-zA-Z0-9_]`，`\s` 匹配空白字符（空格、制表符、换行符）。

### 贪婪匹配与非贪婪匹配

量词默认为**贪婪模式**，即尽可能多地匹配字符。对字符串 `<tag>content</tag>`，模式 `<.*>` 会匹配整个字符串而非单个标签。在量词后添加 `?` 切换为**非贪婪模式**：`<.*?>` 只匹配 `<tag>`。

在处理 HTML 片段或 JSON 输出时，误用贪婪模式是导致提取错误的首要原因，因此必须明确区分两种模式的行为差异。

### 捕获组与反向引用

`()` 创建捕获组，匹配结果可通过 `group(n)` 按序号取出。例如，解析日期字符串：

```python
import re
m = re.search(r'(\d{4})-(\d{2})-(\d{2})', '发布于 2024-03-15')
year, month, day = m.group(1), m.group(2), m.group(3)
# year='2024', month='03', day='15'
```

`(?P<name>...)` 语法创建**命名捕获组**，用 `m.group('year')` 按名称取值，可读性更高且不受组顺序变动的影响。反向引用 `\1`（或 `(?P=name)`）则允许在同一模式内引用已捕获内容，例如检测重复单词：`\b(\w+)\s+\1\b`。

### 零宽断言

零宽断言匹配的是**位置**而非字符，不消耗字符串内容：

- `(?=...)` **正向先行断言**：当前位置后面紧跟指定模式。`\d+(?= USD)` 匹配后面跟着" USD"的数字，但结果不含" USD"。
- `(?<=...)` **正向后行断言**：当前位置前面是指定模式。`(?<=¥)\d+` 提取人民币金额数字。
- `(?!...)` 和 `(?<!...)` 是对应的否定版本。

零宽断言在提取特定格式的模型输出（如"仅提取冒号后的数值"）时极为实用。

---

## 实际应用

### 数据清洗：去除噪声字符

爬取的语料往往含有 HTML 实体、多余空白和控制字符。以下代码用三条正则一次性完成三类清洗：

```python
import re

def clean_text(text):
    text = re.sub(r'&[a-z]+;', ' ', text)        # 替换 HTML 实体
    text = re.sub(r'[\x00-\x1f\x7f]', '', text)  # 删除控制字符
    text = re.sub(r' {2,}', ' ', text)            # 合并多余空格
    return text.strip()
```

### 提取结构化信息

从非结构化文本中抽取邮箱地址，常用模式为：

```python
EMAIL_PATTERN = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
emails = re.findall(EMAIL_PATTERN, document)
```

此模式覆盖了 `user.name+tag@sub.domain.co.uk` 这类复杂地址，但有意排除了以数字开头的顶级域（如 `.123`），以降低误报率。

### 验证模型输出格式

当要求大语言模型输出固定格式（如"分数: 整数/10"）时，正则可快速验证并提取值：

```python
pattern = r'分数[：:]\s*([0-9]|10)/10'
match = re.search(pattern, llm_output)
score = int(match.group(1)) if match else None
```

---

## 常见误区

### 误区一：用正则解析 HTML 或 JSON

正则表达式只能处理**正则文法**，而 HTML 和 JSON 是**上下文无关文法**，存在任意深度嵌套。用 `<div>.*?</div>` 解析多层嵌套 `<div>` 会产生错误结果。正确做法是使用 `BeautifulSoup`（HTML）或 `json.loads()`（JSON），仅在提取已知固定格式的叶节点内容时才考虑辅以正则。

### 误区二：忽视 re.compile() 的性能差异

在循环中直接调用 `re.search(pattern, text)` 时，Python 每次都会重新编译模式字符串。当需要对数百万条文本重复应用同一模式时，应预先调用 `compiled = re.compile(pattern)` 再用 `compiled.search(text)`，实测可节省 20%–40% 的运行时间。

### 误区三：混淆原始字符串与普通字符串

`\n` 在 Python 普通字符串中是换行符，但在正则中 `\n` 代表匹配换行符的模式。若写 `re.search('\d+', text)`，Python 先将 `\d` 解释为字符 `d`（反斜杠被吃掉），导致匹配失败。正则模式应始终使用原始字符串字面量 `r'\d+'`，避免双重转义问题。

---

## 知识关联

**前置知识**：正则表达式的操作对象是字符串，`re.sub()` 的替换逻辑本质上是字符串拼接，需要熟悉 Python 字符串的切片与编码（尤其是 Unicode 下 `\w` 默认匹配中文字符）。`re.findall()` 返回列表，遍历结果需要 `for` 循环配合条件判断，循环控制流是后处理逻辑的基础。

**横向扩展**：掌握正则后，可进一步学习解析器组合子（Parser Combinator）和上下文无关文法，以处理正则无法应对的嵌套结构。在 AI 工程流水线中，正则表达式常与 `pandas` 的 `str.extract()` 方法结合使用，对 DataFrame 列批量提取特征；也可嵌入 LangChain 的 `OutputParser` 中，作为结构化输出验证的第一道防线。