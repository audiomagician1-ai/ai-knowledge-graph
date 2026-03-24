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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 字典/映射

## 概述

字典（Dictionary）或映射（Map）是一种存储**键值对（key-value pair）**的数据结构，每个键（key）唯一对应一个值（value）。与数组通过整数索引访问元素不同，字典允许使用任意可哈希对象作为键，例如字符串、整数甚至元组。Python中称之为`dict`，JavaScript中称为`Object`或`Map`，Java中常用`HashMap`，Go中称为`map`。

字典的概念最早可追溯至1960年代的符号表（symbol table）设计，Lisp语言的关联列表（association list）是其原型之一。现代字典通常基于哈希表实现，Python的`dict`自3.7版本起正式保证**插入顺序**，这一改变直接影响了大量依赖字典遍历顺序的AI工程代码。

在AI工程中，字典几乎无处不在：模型的超参数配置、词汇表（vocabulary）的词到索引映射、API返回的JSON数据解析，都依赖字典结构。理解字典的行为是读懂`transformers`库配置文件、处理特征工程数据的基本前提。

---

## 核心原理

### 键值对结构与唯一键约束

字典的基本单元是键值对，写作`{key: value}`。**键必须唯一**：若对同一个键赋值两次，后者会覆盖前者。例如：

```python
config = {"lr": 0.001, "lr": 0.01}
print(config["lr"])  # 输出 0.01，前一个被覆盖
```

键还必须是**不可变（hashable）类型**：字符串、整数、浮点数、元组可以作为键，而列表和字典本身不能作为键，因为它们是可变对象，其哈希值会改变。值（value）则没有此限制，可以是任意类型，包括另一个字典（嵌套字典）。

### 核心操作及其时间复杂度

字典的查找、插入、删除操作的**平均时间复杂度均为O(1)**，这是它相比于遍历列表查找（O(n)）的核心优势。常用操作如下：

| 操作 | Python语法 | 说明 |
|------|-----------|------|
| 读取 | `d[key]` 或 `d.get(key, default)` | `get`在键不存在时返回默认值而非抛出`KeyError` |
| 写入 | `d[key] = value` | 键存在则更新，不存在则插入 |
| 删除 | `del d[key]` 或 `d.pop(key)` | `pop`可返回被删除的值 |
| 遍历 | `d.items()`, `d.keys()`, `d.values()` | 分别返回键值对、键、值的视图对象 |

在AI特征处理中，使用`d.get(token, 0)`比先检查`token in d`再访问快约15%，因为减少了一次哈希计算。

### 嵌套字典与字典推导式

AI工程中的配置文件常使用嵌套字典：

```python
model_config = {
    "encoder": {"hidden_size": 768, "num_layers": 12},
    "decoder": {"hidden_size": 512, "num_layers": 6}
}
# 访问嵌套值
print(model_config["encoder"]["hidden_size"])  # 768
```

**字典推导式（dict comprehension）**可以简洁地构建映射关系，例如构建词汇表：

```python
vocab = {word: idx for idx, word in enumerate(word_list)}
```

这一行代码将词列表转换为`词→索引`的字典，是NLP预处理中的标准写法。

---

## 实际应用

### 超参数管理

在训练神经网络时，超参数通常存储为字典，便于传递和记录：

```python
hparams = {
    "learning_rate": 3e-4,
    "batch_size": 32,
    "epochs": 100,
    "optimizer": "AdamW"
}
```

`transformers`库的`TrainingArguments`内部即将这些参数组织为字典，并通过`json.dumps(hparams)`序列化保存到实验日志中。

### 词汇表与词嵌入索引

BERT的词汇表文件`vocab.txt`加载后通常转换为两个互逆的字典：
- `token_to_id: {"[PAD]": 0, "[CLS]": 101, "hello": 7592, ...}`
- `id_to_token: {0: "[PAD]", 101: "[CLS]", 7592: "hello", ...}`

这两个字典的大小对于BERT-base均为**30,522个条目**，O(1)的查找性能使得分词和解码速度远超列表遍历方案。

### 缓存与记忆化

`functools.lru_cache`的底层实现依赖字典存储已计算结果。在推理时手动缓存重复调用：

```python
embedding_cache = {}
def get_embedding(text):
    if text not in embedding_cache:
        embedding_cache[text] = model.encode(text)
    return embedding_cache[text]
```

---

## 常见误区

**误区一：用列表代替字典做存在性判断**

新手常写`if item in my_list`来检查某元素是否存在。若`my_list`有10万个元素，每次检查耗时O(n)。将其转换为字典或集合后，同样操作仅需O(1)。在构建词汇过滤器时，这个差异可导致处理速度相差**数百倍**。

**误区二：直接访问不存在的键**

`d[key]`在键不存在时会抛出`KeyError`，而非返回`None`。AI工程中解析API响应或用户输入时，应习惯使用`d.get(key)`或`collections.defaultdict`，以避免因缺失字段导致程序崩溃。尤其是处理结构不统一的JSON数据时，此类错误极为常见。

**误区三：将字典键顺序视为不可靠**

部分开发者仍基于Python 3.6及更早版本的经验，认为字典遍历顺序不确定，为此引入额外的排序逻辑。Python 3.7+已将插入顺序作为**语言规范**保证，`collections.OrderedDict`在现代Python中仅用于需要显式重排顺序的特殊场景。

---

## 知识关联

**与数组/列表的关系**：列表使用从0开始的整数索引，字典使用任意可哈希键；列表擅长按位置顺序访问，字典擅长按语义名称快速查找。两者互补，AI工程中常将列表嵌套在字典值中，如`{"labels": [0, 1, 1, 0]}`。

**通往哈希表**：字典的O(1)性能来源于其底层的哈希表实现，理解哈希函数、哈希冲突（碰撞）及开放寻址法/链地址法，是理解字典在极端情况下性能退化至O(n)的原因，也是面试中的高频考点。

**通往集合（Set）**：Python的`set`本质上是只有键、没有值的字典，共享相同的哈希机制和O(1)查找特性，学会字典后理解集合的成本极低。

**通往数据序列化**：JSON格式与Python字典高度对应，`json.dumps()`将字典转为JSON字符串，`json.loads()`执行反向操作。掌握字典是理解AI工程中模型配置持久化、API通信数据格式的直接前置技能。
