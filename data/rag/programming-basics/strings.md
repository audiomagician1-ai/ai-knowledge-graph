---
id: "strings"
concept: "字符串操作"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["数据类型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 字符串操作

## 概述

字符串（String）是由零个或多个字符组成的有序序列，在Python中以`str`类型表示，底层以Unicode码点存储。字符串是**不可变序列**（immutable sequence），这意味着对字符串的任何"修改"操作实际上都会创建一个新的字符串对象，原字符串在内存中保持不变。这一特性直接影响了字符串拼接在大规模循环中的性能表现。

字符串操作的系统化研究可追溯至1960年代SNOBOL语言——它是第一门将字符串处理作为核心功能的编程语言。现代AI工程中，文本预处理、分词、特征提取等环节均以字符串操作为基础。GPT类模型的tokenizer在运行前，首先需要对原始字符串执行normalization（Unicode标准化）、whitespace处理等操作，字符串操作的质量直接影响下游模型的输入质量。

Python的`str`类型提供了超过40个内置方法，掌握这些方法可以不借助正则表达式完成绝大多数文本清洗任务，在AI数据预处理管道中尤为重要。

---

## 核心原理

### 索引与切片

Python字符串支持正向索引（从`0`开始）和负向索引（从`-1`开始，`-1`表示最后一个字符）。切片语法为`s[start:stop:step]`，三个参数均可省略：

- `s[2:5]` 提取索引2、3、4的字符（不含5）
- `s[::-1]` 利用步长`-1`实现字符串原地翻转，时间复杂度O(n)
- `s[::2]` 提取所有偶数索引字符

切片操作返回新字符串，不修改原字符串。对长度为`n`的字符串，合法索引范围是`-n`到`n-1`，越界访问会触发`IndexError`，而切片越界则**不报错**（自动截断）。

### 常用变换方法

以下方法是AI文本预处理中出现频率最高的字符串操作：

| 方法 | 功能 | AI场景举例 |
|------|------|-----------|
| `s.lower()` / `s.upper()` | 大小写转换 | 统一英文文本大小写 |
| `s.strip(chars)` | 去除两端指定字符（默认空白符） | 清除爬取网页文本的首尾换行 |
| `s.split(sep, maxsplit)` | 按分隔符拆分为列表 | 将句子切分为词列表 |
| `sep.join(iterable)` | 将序列拼接为字符串 | 将token列表还原为句子 |
| `s.replace(old, new, count)` | 替换子串 | 批量替换脏数据标记符 |
| `s.find(sub)` | 返回首次出现的索引，未找到返回`-1` | 定位关键词位置 |

**字符串拼接的性能陷阱**：在循环中使用`+=`拼接字符串，每次都创建新对象，时间复杂度退化为O(n²)。正确做法是先将片段存入列表，最后调用`''.join(parts)`，时间复杂度为O(n)。

### 格式化与模板

Python提供三种字符串格式化方式，其中f-string（Python 3.6+引入）是AI工程中构建prompt的首选方式：

```python
name = "GPT-4"
tokens = 8192
# f-string：直接嵌入表达式，支持格式说明符
prompt = f"模型 {name} 的上下文窗口为 {tokens:,} tokens"
# 输出：模型 GPT-4 的上下文窗口为 8,192 tokens
```

`str.format()`方法支持通过位置`{0}`或关键字`{name}`引用参数，适合构建可复用的prompt模板。`%`格式化（如`"%s has %d items" % (s, n)`）是Python 2遗留语法，在新代码中应避免使用。

### 字符串与编码的关系

Python 3中`str`存储的是Unicode码点，而非字节。调用`s.encode('utf-8')`将`str`转换为`bytes`对象，调用`b.decode('utf-8')`执行逆操作。一个中文字符在UTF-8编码下占3个字节，但`len("汉")`返回`1`（字符数），`len("汉".encode('utf-8'))`返回`3`（字节数）——混淆这两个概念是处理多语言NLP任务时的常见错误根源。

---

## 实际应用

**场景1：构建LLM的few-shot prompt**

```python
examples = [
    ("今天天气真好", "正面"),
    ("服务态度很差", "负面"),
]
shots = "\n".join([f"文本：{t}\n情感：{l}" for t, l in examples])
query = "文本：这家餐厅还不错\n情感："
prompt = f"请判断以下文本的情感倾向。\n\n{shots}\n\n{query}"
```

这里`join`、f-string和列表推导式的组合展示了字符串操作在prompt工程中的典型用法。

**场景2：清洗爬取的训练语料**

```python
def clean_text(raw: str) -> str:
    text = raw.strip()                        # 去除首尾空白
    text = " ".join(text.split())             # 将连续空白压缩为单个空格
    text = text.replace("\u200b", "")         # 移除零宽空格（常见于网页文本）
    text = text.lower()                       # 统一小写
    return text
```

`"\u200b"`是零宽不换行空格的Unicode码点，它在视觉上不可见却会污染词表，`replace`精准清除该字符是语料清洗的标准步骤。

---

## 常见误区

**误区1：`len()`返回字节数**

初学者常误以为`len(s)`返回字节数。实际上`len()`对`str`对象返回**字符（码点）数**。`len("hello")` = 5，`len("你好")` = 2，但`len("你好".encode('utf-8'))` = 6。在计算BERT的max_length时，应使用tokenizer的token数，而非`len(s)`的字符数。

**误区2：用`+`在循环中拼接字符串**

由于字符串不可变，`result += piece`在每次迭代都分配新内存并复制已有内容。拼接10,000个长度为10的字符串时，`+`循环需要约5,000万次字节操作，而`join`只需约10万次。应始终使用`''.join(list)`代替循环`+=`。

**误区3：`replace`修改了原字符串**

初学者写出`s.replace('a', 'b')`后发现`s`没有变化，误以为`replace`方法失效。实际原因是字符串不可变，`replace`返回新字符串，必须赋值：`s = s.replace('a', 'b')`。这是不可变对象与可变对象在操作语义上的根本区别。

---

## 知识关联

**前置概念**：理解字符串操作需要具备**字符编码（ASCII/UTF-8）**知识。`encode`/`decode`方法的正确使用依赖于UTF-8多字节编码规则，而`ord('A')` = 65、`chr(65)` = `'A'`这类操作直接建立在ASCII码表之上。**变量与数据类型**知识则解释了为何`str`是不可变类型，以及`str`与`bytes`、`list`之间的类型转换逻辑。

**后续概念**：字符串操作是**KMP字符串匹配算法**的前置基础——KMP算法在字符串的索引层面操作，其`next`数组构建过程涉及子串比较，需要熟悉字符串索引和切片。**正则表达式**则是字符串操作能力的延伸：当`find`/`replace`/`split`无法表达复杂模式（如"匹配所有连续数字"）时，正则表达式提供了基于有限自动机的通用解决方案，但其底层仍调用字符串的字节/字符层表示。