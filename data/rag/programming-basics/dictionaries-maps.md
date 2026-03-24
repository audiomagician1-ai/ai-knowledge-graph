---
id: "dictionaries-maps"
concept: "字典/映射"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["数据类型"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 字典/映射

## 概述

字典（Dictionary）或映射（Map）是一种以**键值对（key-value pair）**为基本单位的数据结构，其中每个唯一的键（key）精确对应一个值（value）。与数组通过整数索引访问元素不同，字典允许使用任意不可变对象（如字符串、整数、元组）作为键，这使得"通过名称查找数据"成为 O(1) 平均时间复杂度的操作。

字典的概念源自数学中的**函数映射** f: X → Y，即定义域中每个元素映射到值域中唯一的元素。在编程实现上，Python 3.7+ 正式将字典规范为**有序**数据结构，按插入顺序保留键的排列，而早期版本（Python 3.6 及以前）中字典是无序的。Java 中的 `HashMap`、JavaScript 中的对象字面量（`{}`）、Go 中的 `map[string]int` 都是映射概念的具体实现。

在 AI 工程的日常开发中，字典无处不在：模型的超参数配置、词汇表（词 → 整数 ID）、批量数据的特征存储、API 返回的 JSON 数据解析，全部依赖字典结构。掌握字典的工作原理是读懂和编写任何 AI 训练脚本的前提。

---

## 核心原理

### 键值对的存储与查找

字典的每条记录形如 `"learning_rate": 0.001`，其中 `"learning_rate"` 是键，`0.001` 是值。Python 中使用花括号创建字典：

```python
config = {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100
}
```

访问某个值时写 `config["learning_rate"]`，返回 `0.001`。字典内部通过**哈希表**实现，对键调用 `hash()` 函数得到整数哈希值，再映射到内存槽位，因此查找时间与字典大小无关，平均为 O(1)。这与数组的线性搜索（O(n)）形成鲜明对比。

### 键的唯一性与不可变性约束

字典中**同一个键只能出现一次**。若重复赋值，后者会覆盖前者：

```python
d = {"a": 1, "a": 2}
print(d)  # {'a': 2}
```

键必须是**可哈希（hashable）**的不可变类型。Python 中字符串、整数、浮点数、元组均可作键；列表和字典本身不可作键，因为它们可变，哈希值无法固定。例如 `{[1,2]: "bad"}` 会抛出 `TypeError: unhashable type: 'list'`。值（value）则无此限制，可以是任意对象，包括另一个字典（嵌套字典）。

### 常用操作与方法

Python 字典提供了一套专用方法，行为不同于列表操作：

| 操作 | 写法 | 说明 |
|------|------|------|
| 获取值（带默认） | `d.get("key", 0)` | 键不存在时返回 0，而非抛异常 |
| 遍历键值对 | `for k, v in d.items()` | 同时拿到键和值 |
| 仅遍历键 | `for k in d.keys()` | 返回视图对象，非列表副本 |
| 合并字典 | `d1 \| d2`（Python 3.9+） | 右侧键优先覆盖 |
| 删除并返回 | `d.pop("key")` | 安全删除 |

`dict.get()` 方法在 AI 工程中尤为重要——解析不确定字段的 JSON 响应时，用 `response.get("error", None)` 比直接 `response["error"]` 安全得多。

### 字典推导式

类似列表推导式，字典支持一行内构建映射关系：

```python
# 构建词汇表：词 -> 索引
vocab = {word: idx for idx, word in enumerate(["cat", "dog", "bird"])}
# {'cat': 0, 'dog': 1, 'bird': 2}
```

这在构建 NLP 词汇表或将类别标签转换为整数编码时极为常用，代替手写 for 循环可减少约 60% 的代码行数。

---

## 实际应用

**超参数管理**：AI 实验中通常用字典统一管理超参数，再传入训练函数：

```python
hparams = {"lr": 3e-4, "dropout": 0.1, "hidden_dim": 256}
model = build_model(**hparams)
```

`**hparams` 语法将字典解包为关键字参数，是 Python 字典的独特特性。

**词汇表与词嵌入索引**：在 Transformer 模型中，分词器（Tokenizer）内部维护一个字符串到整数的字典，例如 BERT 的词汇表大小为 30,522，格式为 `{"[PAD]": 0, "[UNK]": 100, "hello": 7592, ...}`。模型根据整数索引查找对应的嵌入向量行。

**JSON 数据解析**：调用 OpenAI API 返回的响应是嵌套字典，通过 `response["choices"][0]["message"]["content"]` 逐层访问，每一层 `["key"]` 都是字典查找操作。

**计数与频率统计**：用 `collections.Counter`（本质是字典子类）统计词频：`Counter(tokens)` 返回 `{"the": 1523, "model": 312, ...}`，是文本预处理的标准工具。

---

## 常见误区

**误区一：用 `d["key"]` 访问不存在的键**  
直接使用方括号访问不存在的键会抛出 `KeyError`，而非返回 `None`。AI 工程中解析外部 API 或配置文件时，字段可能缺失，应统一使用 `d.get("key", default_value)` 或先用 `if "key" in d` 判断。许多初学者因此让程序在运行时意外崩溃。

**误区二：认为字典遍历顺序不确定**  
这在 Python 3.6 之前是正确的，但从 **Python 3.7 起字典按插入顺序迭代**已成语言规范（不只是 CPython 实现细节）。依赖字典顺序的代码在 Python 3.7+ 中是安全的，但若代码需要兼容旧版环境，仍应使用 `collections.OrderedDict` 并注明原因。

**误区三：将字典键与列表索引混淆**  
字典不支持切片操作（`d[0:2]` 会报 `TypeError`），也无法通过位置整数访问第 n 个元素，除非键本身就是整数。若需要"按位置第三个键值对"，应先调用 `list(d.keys())[2]` 转换，这也暗示此时可能更适合用列表或 `OrderedDict` 配合额外索引。

---

## 知识关联

**前置概念——数组/列表**：列表用连续整数索引（0, 1, 2...）定位元素，字典则将这一机制推广到任意不可变键。理解列表的"位置即地址"模型，有助于理解为什么字典需要哈希函数将键转化为内存位置——这是字典相对于列表的核心扩展。

**后续概念——哈希表**：字典是哈希表最直接的高层封装。学习哈希表将揭示字典内部的碰撞处理（开放寻址 vs. 链地址法）、装载因子（Python 字典在装载因子超过 2/3 时触发扩容）等实现细节，解释为何字典偶尔会有 O(n) 的最坏情况查找。

**后续概念——集合（Set）**：Python 的集合可理解为"只有键、没有值"的字典，底层同样使用哈希表，因此 `in` 运算符在集合中也是 O(1)。字典的 `.keys()` 视图对象本身就支持集合运算（交集 `&`、并集 `|`）。

**后续概念——数据序列化**：字典是 JSON 格式的直接对应物（JSON 对象 ↔ Python 字典）。`json.dumps(d)` 将字典序列化为 JSON 字符串，`json.loads(s)` 执行反向操作。掌握字典结构后，理解 JSON、YAML、MessagePack 等序列化格式的嵌套规则将变得直观，因为它们的核心数据模型均为键值映射。
