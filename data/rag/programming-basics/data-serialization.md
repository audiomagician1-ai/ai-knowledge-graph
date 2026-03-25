---
id: "data-serialization"
concept: "数据序列化"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 3
is_milestone: false
tags: ["json", "xml", "yaml", "serialization"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 数据序列化

## 概述

数据序列化（Data Serialization）是将内存中的数据结构或对象转换为可存储或可传输的字节序列的过程，其逆过程称为反序列化（Deserialization）。具体地说，当Python程序中有一个包含嵌套列表和字典的复杂对象时，这个对象只存在于运行时内存中，一旦进程结束便消失；序列化使其变成一段JSON字符串或二进制字节流，可以写入磁盘、通过HTTP发送或存入数据库。

数据序列化的标准化进程始于20世纪80年代的ASN.1（Abstract Syntax Notation One，1984年由ITU-T发布），用于电信协议中的结构化数据编码。JSON诞生于2001年，由Douglas Crockford从JavaScript对象字面量语法中提炼而来，于2013年成为ECMA-404标准。Protocol Buffers（Protobuf）则是Google内部系统于2001年开始使用、2008年开源的二进制序列化方案，目前驱动着Google每秒处理的数十亿次RPC调用。

在AI工程中，数据序列化贯穿模型训练的全生命周期：训练数据集以JSONL格式存储用于流式读取，模型超参数以YAML写入配置文件，推理服务的API请求和响应以JSON封装，而高性能特征存储则依赖Protobuf或Apache Arrow的二进制格式以减少I/O瓶颈。理解不同格式的编码开销，直接影响数据管道的吞吐量。

---

## 核心原理

### JSON：基于文本的键值编码

JSON（JavaScript Object Notation）使用六种数据类型：字符串、数字、布尔值、null、数组和对象（键值映射）。其编码规则规定，**所有键必须是双引号括起来的字符串**，这与Python字典允许整数键不同。JSON不支持注释，不支持日期类型（日期需编码为ISO 8601字符串如 `"2024-01-15T08:30:00Z"`），也不支持二进制数据（需先Base64编码，体积膨胀约33%）。

Python操作JSON的核心函数有四个：`json.dumps(obj)` 将对象序列化为字符串，`json.dump(obj, fp)` 写入文件流，`json.loads(s)` 从字符串反序列化，`json.load(fp)` 从文件流读取。参数 `indent=2` 启用美化输出，`ensure_ascii=False` 保留UTF-8中文字符（否则中文会被转义为 `\uXXXX` 形式）。

### YAML：人类可读的层次化配置格式

YAML（YAML Ain't Markup Language）通过**缩进**（默认2个空格）表示层次结构，不使用花括号或方括号。其独特之处在于**隐式类型推断**：字符串 `true` 会被自动解析为布尔值，`1e3` 被解析为浮点数1000.0，`2024-01-15` 被解析为日期对象——这在编写AI训练配置时可能引发难以追踪的类型错误。YAML支持多行字符串（`|` 保留换行，`>` 折叠换行），以及锚点（`&anchor`）和引用（`*anchor`）机制避免重复配置。

```yaml
# PyTorch训练配置示例（YAML特有的注释语法）
model:
  hidden_size: 768
  dropout: 0.1
training:
  lr: 1.0e-4    # 科学计数法被解析为float
  epochs: 100
  seed: &seed 42
eval:
  seed: *seed   # 引用锚点，值同为42
```

### Protobuf：二进制紧凑编码

Protobuf使用 `.proto` 文件定义消息结构，字段通过**字段编号**（Field Number）而非字段名称进行编码，这使得反序列化时无需字符串匹配，也允许在不破坏向后兼容性的前提下重命名字段。每个字段在二进制流中编码为 `Tag-Length-Value (TLV)` 三元组，其中Tag = `(field_number << 3) | wire_type`。

以下是一个对比数字：同一份包含100个浮点数的数组，JSON编码约需1.2KB，YAML约需900B，而Protobuf仅需约412B（`float` 类型每个4字节）。在AI推理服务处理每秒10万次请求的场景中，这种差距直接转化为带宽成本和延迟。

### XML与现代替代品的对比

XML（可扩展标记语言，1998年由W3C发布）使用开闭标签 `<tag>value</tag>` 编码，支持属性（`<model version="2">`）和命名空间，但这种冗余使得同等数据的XML文件体积通常是JSON的2-3倍。当前AI工程中XML主要出现在ONNX（Open Neural Network Exchange）模型格式相关工具链和某些企业数据集成场景中，新项目通常不再优先选择XML。

---

## 实际应用

**场景一：JSONL格式存储训练数据**  
大语言模型的微调数据集通常使用JSONL（JSON Lines）格式存储，即每行一个独立的JSON对象，而不是将所有数据包裹在一个JSON数组中。这样做的好处是支持流式读取（`for line in file`），无需将整个数据集加载到内存，对于百GB级数据集尤为关键。HuggingFace的 `datasets` 库默认支持直接加载JSONL文件。

**场景二：模型服务API的请求/响应**  
OpenAI API的Chat Completion请求体是标准JSON，其中 `messages` 字段是一个对象数组，每个对象包含 `role` 和 `content` 两个字符串键。当 `stream=true` 时，响应变为Server-Sent Events流，每个事件体仍是JSON，这要求客户端对每个到来的数据块分别调用 `json.loads()`。

**场景三：Protobuf在特征存储中的应用**  
在实时推荐系统中，用户特征（如历史点击序列、实时行为向量）以Protobuf序列化后存储于Redis，一次特征查询从Redis读取后直接调用 `feature_proto.ParseFromString(raw_bytes)` 完成反序列化，延迟通常在1ms以内。若改用JSON，仅字符串解析的CPU开销便增加3-5倍。

---

## 常见误区

**误区一：JSON的数字类型与Python一致**  
JSON规范本身不区分整数和浮点数，统一称为"number"。Python的 `json.loads('{"x": 1}')` 返回整数，但 `json.loads('{"x": 1.0}')` 返回浮点数。更危险的是，JSON没有规定数字精度上限，而JavaScript（JSON最初的宿主语言）使用64位双精度浮点数，超过 `2^53 - 1`（即9007199254740991）的整数在JavaScript端会丢失精度——这在处理雪花算法生成的64位ID时是实际的工程陷阱，解决方案是将大整数序列化为字符串。

**误区二：YAML完全兼容JSON**  
YAML 1.2规范声称JSON是YAML的子集，但YAML 1.1（仍被Python的PyYAML库默认使用的版本）存在差异：YAML 1.1中 `yes`/`no`/`on`/`off` 会被解析为布尔值，而JSON和YAML 1.2不会。在编写包含这些词语的字符串配置时（如某些AWS配置键），必须用引号明确标注：`value: "yes"`。

**误区三：Protobuf的向后兼容性是自动的**  
Protobuf的字段编号一旦在生产环境使用就**不能修改或重用**。若将字段2从 `string name` 改为 `int32 count`，旧版客户端发来的序列化数据中字段2仍是字符串编码，新版服务器会因Wire Type不匹配而抛出解析错误。正确做法是弃用（`reserved 2; reserved "name";`）旧字段并使用新编号添加新字段，这是Protobuf版本管理的核心约束。

---

## 知识关联

本概念直接依赖**字典/映射**的理解：JSON对象和Python `dict` 之间的类型映射（`dict↔object`、`list↔array`、`str↔string`、`int/float↔number`、`None↔null`）是序列化操作的基础。**变量与数据类型**决定了哪些Python类型可以直接序列化（`datetime` 对象无法直接 `json.dumps()`，需自定义 `default` 函数处理）。**文件I/O** 是序列化结果的主要落地方式，`json.dump()` 与 `open()` 的配合使用要求理解文件句柄的写入模式（`'w'` vs `'wb'` 用于文本vs二进制格式）。

在AI工程的后续实践中，数据序列化是构建数据管道（Data Pipeline）、部署模型API服务、实现分布式训练节点间通信的前置技能。掌握不同格式的性能特征和适用场景，能够直接指导TFRecord（TensorFlow专用二进制格式）、Apache Parquet（列式存储）等更专业的AI数据格式的学习。
