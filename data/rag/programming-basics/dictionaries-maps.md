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
quality_tier: "S"
quality_score: 82.9
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

# 字典/映射

## 概述

字典（Dictionary）或映射（Map）是一种以**键值对（Key-Value Pair）**为基本存储单位的数据结构，通过唯一的键（Key）来快速定位对应的值（Value）。与数组通过整数下标访问元素不同，字典允许使用字符串、整数、元组等可哈希对象作为键，这使得数据的语义表达更加直观。例如，存储一名学生的信息时，字典可以用 `{"name": "张三", "age": 20, "score": 95.5}` 来组织，而非依赖下标 `[0]`、`[1]`、`[2]` 猜测含义。

字典的概念最早可追溯到1950年代的关联数组（Associative Array）研究，Lisp语言在1958年引入了类似的属性列表结构。Python 在3.7版本（2018年）正式将字典的**插入顺序保持**纳入语言规范，这一改变使字典在数据处理流水线中更加可预测。现代主流语言均内置了字典类型：Python 的 `dict`、JavaScript 的 `Object/Map`、Java 的 `HashMap`、C++ 的 `std::unordered_map`。

在 AI 工程中，字典几乎无处不在：模型的超参数配置、特征工程中的类别编码映射、推理结果的标签-置信度对应，都依赖字典结构来组织数据。掌握字典的操作方式是读写 JSON 配置文件、调用 REST API、处理 NLP 词汇表的前提技能。

---

## 核心原理

### 键值对的唯一性约束

字典中每个键必须唯一。若向同一键写入两次值，后者会覆盖前者，而不会报错或追加。例如在 Python 中：

```python
config = {"lr": 0.01, "lr": 0.001}
print(config["lr"])  # 输出 0.001，第一个值被静默覆盖
```

这一特性决定了字典天然适合作为"去重后的映射表"。键的可哈希性（Hashability）是字典的底层要求：列表不能作为键（因为列表可变，哈希值不稳定），但元组可以。尝试 `{[1,2]: "value"}` 会抛出 `TypeError: unhashable type: 'list'`。

### 查找复杂度：O(1) 的平均性能

字典的核心优势在于平均 **O(1)** 的键查找时间复杂度，这与底层哈希表实现直接相关。当字典调用 `d[key]` 时，系统计算 `hash(key)` 得到桶索引，直接定位存储位置，而无需像列表那样逐元素遍历（O(n)）。Python 字典在负载因子超过 **2/3** 时会触发扩容，将容量扩展为原来的约2倍，以维持查找性能。

这意味着：统计一段文本中每个词出现的频率，用字典实现比用两个列表分别存词和计数快得多——100万词的文本，字典方案的查找阶段是 O(1)，而列表方案是 O(n)，差距可达数百倍。

### 字典的基本操作与方法

以 Python 为例，字典的关键操作如下：

| 操作 | 语法 | 说明 |
|---|---|---|
| 安全读取 | `d.get("key", default)` | 键不存在时返回默认值而非报错 |
| 遍历键值 | `d.items()` | 返回 (key, value) 元组的视图对象 |
| 合并字典 | `d1 \| d2`（Python 3.9+）| 右侧键值优先覆盖左侧 |
| 条件插入 | `d.setdefault("key", [])` | 键不存在才插入，已存在则保持原值 |

`d.get(key, default)` 在 AI 工程中极为常用，例如解析模型返回的 JSON 时，若某字段可能缺失，使用 `result.get("confidence", 0.0)` 比直接 `result["confidence"]` 安全得多。

### 嵌套字典与深层访问

字典的值可以是另一个字典，形成嵌套结构（Nested Dictionary）。深度学习框架的配置文件通常采用此结构：

```python
model_config = {
    "encoder": {"layers": 12, "hidden_size": 768, "dropout": 0.1},
    "decoder": {"layers": 6, "hidden_size": 512}
}
# 访问嵌套值
hidden = model_config["encoder"]["hidden_size"]  # 768
```

访问深层键时，若中间层键缺失会直接抛出 `KeyError`，这是嵌套字典操作中最常见的错误来源。`collections.defaultdict` 或递归 `get` 链是处理此问题的标准方案。

---

## 实际应用

**词汇表构建（NLP 必备操作）**：将文本语料转化为模型可处理的整数索引时，词汇表本质上就是一个字典 `{"the": 0, "apple": 1, "model": 2, ...}`，反向映射（id→词）则是另一个字典。BERT 模型的 `vocab.txt` 文件加载后即存储为这种结构，词汇量通常在 30,000 到 50,000 个键之间。

**超参数管理**：训练脚本中将所有超参数集中到一个字典，可以整体传入函数、打印记录、序列化为 JSON 存档：

```python
hparams = {"batch_size": 32, "epochs": 100, "optimizer": "adam", "lr": 3e-4}
```

**API 响应解析**：调用 OpenAI 等模型 API 返回的 JSON 对象，在 Python 中直接解析为字典，通过 `response["choices"][0]["message"]["content"]` 这样的链式键访问提取生成文本。

**特征编码映射**：将类别型特征（如城市名）映射为整数或 embedding 索引时，字典是维护"类别→编号"对应关系的标准工具，确保训练和推理阶段使用一致的编码方案。

---

## 常见误区

**误区一：直接用 `d[key]` 读取不确定是否存在的键**
许多初学者习惯用 `d[key]` 读取值，当键不存在时会抛出 `KeyError` 导致程序崩溃。正确做法是用 `d.get(key, 默认值)` 或提前用 `if key in d` 判断。在 AI 推理服务中，若请求字段偶发缺失，这个错误会直接导致接口 500。

**误区二：认为字典遍历顺序不可预测**
Python 3.7 之前的字典确实无序，因此许多教材和代码注释仍写着"字典无序"。但在 Python 3.7+ 中，字典**严格保持插入顺序**。若代码运行在 Python 3.6 及以下环境，才需要使用 `collections.OrderedDict` 来保证顺序。混淆版本导致的排查成本极高。

**误区三：用字典存储大量数字索引数据**
当键是连续整数（0, 1, 2, ...）时，有些初学者仍使用字典 `{0: v0, 1: v1, ...}` 而非列表。字典每个键值对在 CPython 中占用约 200-300 字节，而列表每个元素只占约 8 字节（指针大小）。存储 100 万个连续整数索引数据，字典的内存开销是列表的约 30 倍，同时失去了切片等列表操作。

---

## 知识关联

**前置概念——数组/列表**：列表通过整数索引访问元素，字典将这一机制泛化为任意可哈希键的访问。理解列表的索引操作是理解"为何字典可以用字符串当'下标'"的基础对比。

**后续概念——哈希表**：字典的 O(1) 查找性能直接来源于哈希表的实现机制。学习哈希表将揭示字典如何计算桶索引、如何处理哈希碰撞（链地址法 vs 开放寻址法），以及为何哈希函数质量影响字典的最坏情况性能（O(n)）。

**后续概念——集合（Set）**：Python 的 `set` 可以理解为只有键没有值的特殊字典，底层同样使用哈希表，支持 O(1) 的成员检测。字典的 `.keys()` 视图对象本身就支持集合运算（交集、并集）。

**后续概念——数据序列化**：字典是 JSON 格式的直接对应结构（JSON object ↔ Python dict），掌握字典的嵌套结构和数据类型约束，是正确使用 `json.dumps()` / `json.loads()` 以及 YAML、TOML 等配置格式的前提。