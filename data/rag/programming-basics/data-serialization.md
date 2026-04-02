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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 数据序列化

## 概述

数据序列化（Data Serialization）是将内存中的数据结构或对象转换为可存储或可传输的字节序列的过程，其逆过程称为反序列化（Deserialization）。例如，Python 中一个包含嵌套列表的字典对象存在于进程内存中时，无法直接写入磁盘或通过网络发送给另一台机器——序列化正是解决这一跨边界传递问题的技术手段。

序列化格式的演化与计算机网络发展紧密相连。XML 于1998年由 W3C 正式发布，成为早期 Web 服务（SOAP）的标准数据交换格式；JSON 在2001年由 Douglas Crockford 推广，因语法简洁迅速取代 XML 成为 REST API 的主流格式；YAML 在2001年同年出现，定位为人类可读的配置文件格式；Google 的 Protocol Buffers（Protobuf）则于2008年开源，专为高性能二进制序列化而设计。在 AI 工程领域，模型配置、训练数据集元数据、推理服务的请求/响应体，几乎无一例外地依赖某种序列化格式传递结构化信息。

## 核心原理

### JSON：轻量文本格式的工作机制

JSON（JavaScript Object Notation）使用六种基本数据类型：对象（`{}`）、数组（`[]`）、字符串（`""`）、数字、布尔值（`true`/`false`）和 `null`。其关键限制是**键必须是字符串**，且不支持注释。Python 的 `json` 模块通过 `json.dumps()` 将字典序列化为字符串，通过 `json.loads()` 反序列化。注意 Python 的 `tuple` 序列化后变为 JSON 数组，反序列化时恢复为 `list` 而非 `tuple`，这是一个典型的类型精度损失问题。JSON 文件本质上是 UTF-8 编码的文本，一个包含100万条记录的 JSON 文件通常比同等内容的 Protobuf 文件大3至10倍。

### YAML：配置文件的层级表达

YAML 使用**缩进**表示层级关系（不允许使用 Tab，必须用空格），用 `- ` 前缀表示列表项，用 `: ` 分隔键值对。YAML 是 JSON 的超集——所有合法的 JSON 都是合法的 YAML。YAML 最独特的特性是支持**锚点（Anchors）与别名（Aliases）**：使用 `&anchor_name` 定义锚点，使用 `*anchor_name` 引用，可避免配置重复。例如 AI 训练配置中，多个实验可共享同一基础超参数块。YAML 还支持多行字符串（`|` 保留换行，`>` 折叠换行），这在嵌入提示词模板时非常实用。Python 使用第三方库 `PyYAML`（`import yaml`），注意 YAML 1.1 规范中 `yes`/`no`/`on`/`off` 会被自动解析为布尔值，这是常见的隐式类型陷阱。

### Protobuf：二进制序列化的性能原理

Protobuf 要求预先用 `.proto` 文件定义数据结构（Schema），每个字段分配一个唯一的**字段编号**（Field Number），序列化后使用该编号而非字段名来标识数据，这是其体积小的核心原因：

```protobuf
message ModelConfig {
  int32 batch_size = 1;
  float learning_rate = 2;
  string model_name = 3;
}
```

Protobuf 使用 Varint 编码（变长整数），小数值占用字节少：值为1的 `int32` 仅占1字节，而 JSON 中同样的 `"batch_size": 1` 占14字节。Protobuf 序列化速度比 JSON 快约5至10倍，体积小约3至5倍（实测数据因内容而异）。其代价是二进制格式不可人眼读取，且依赖编译生成的代码（`protoc` 编译器将 `.proto` 文件转为各语言的类定义）。gRPC 框架默认使用 Protobuf 作为序列化格式。

### XML：结构严格的标签格式

XML 使用开闭标签（`<tag></tag>`）和属性（`<tag attr="val">`）表达数据，支持 DTD 和 XML Schema 进行严格的结构验证。XML 的命名空间（Namespace）机制通过 URI 区分来自不同来源的同名标签，这是 JSON 所不具备的特性。在 AI 工程中，XML 现多见于遗留系统接口和 Office 文档格式（如 `.docx` 本质上是 ZIP 包含的 XML 文件）。Python 处理 XML 使用标准库 `xml.etree.ElementTree`，解析大文件推荐使用 `iterparse` 进行流式处理以节省内存。

## 实际应用

**Hugging Face 模型配置**：`config.json` 是 Transformers 模型仓库的核心文件，使用 JSON 存储架构参数（如 `"hidden_size": 768`、`"num_attention_heads": 12`），在 `from_pretrained()` 加载时自动反序列化为配置对象。

**训练实验管理**：MLflow 和 Weights & Biases 均接受 YAML 格式的实验配置文件。使用 YAML 的锚点特性，可以定义基础配置后让多个实验继承并覆盖特定字段，避免复制粘贴错误。

**大规模推理服务**：当 AI 推理 API 的 QPS（每秒查询数）超过数万时，将请求/响应格式从 JSON 切换到 Protobuf 可显著降低序列化的 CPU 占用和网络带宽消耗，这是 Google、字节跳动等公司内部 AI 服务的常见优化手段。

**数据集元数据**：Hugging Face Datasets 库使用 `dataset_info.json` 存储数据集的特征描述（features schema），用 JSON 精确描述每列的类型，确保跨机器加载时数据类型一致。

## 常见误区

**误区一：认为 JSON 可以无损序列化所有 Python 对象**。Python 的 `datetime`、`numpy.ndarray`、`set`、自定义类实例默认均无法被 `json.dumps()` 处理，会抛出 `TypeError`。解决方案是实现自定义 `JSONEncoder` 子类或使用 `default` 参数传入转换函数。另外，JSON 数字精度有限：JavaScript 的 `Number` 类型是64位浮点，超过 `2^53 - 1`（约9千万亿）的整数在通过 JSON 传递给 JavaScript 客户端时会丢失精度，AI 中常用的模型参数量（如 GPT-4 估计约1.8万亿）若作为整数通过 JSON 传递需特别注意。

**误区二：认为 YAML 比 JSON 更安全因为"只是配置文件"**。`PyYAML` 的 `yaml.load()` 默认使用全功能加载器，可执行任意 Python 代码（通过 `!!python/object` 标签），加载不受信任的 YAML 文件会导致远程代码执行漏洞。正确做法是始终使用 `yaml.safe_load()`，它只支持基本数据类型，不执行任意对象构造。

**误区三：认为 Protobuf 的字段编号可以随意更改**。一旦 `.proto` 定义的字段编号在生产环境使用，就**不能修改**，因为序列化数据中存储的是编号而非字段名。修改编号会导致旧数据反序列化时字段错位。正确的演化方式是只添加新编号字段，废弃旧字段时用 `reserved` 关键字保留其编号以防复用。

## 知识关联

数据序列化直接依赖**字典/映射**数据结构——JSON 对象本质上是字典的文本表示，理解键值对的概念是正确使用 `json.loads()` 返回结果的前提。**变量与数据类型**的知识决定了序列化时的类型映射规则，例如 Python 的 `float` 到 JSON 数字再到 Protobuf `float32` 的精度变化链条。**文件 I/O** 技能是序列化的实际出口：`json.dump(obj, f)` 与 `json.dumps(obj)` 的区别正在于前者直接写入文件对象，后者返回字符串——这两条路径对应"持久化存储"与"网络传输"两种序列化使用场景。掌握这三个基础概念后，可进一步学习 Apache Avro（带内嵌 Schema 的二进制格式，Kafka 生态常用）和 MessagePack（二进制 JSON 替代品）等进阶格式，以及在 AI 特定场景下的 `safetensors` 格式——后者专为安全存储模型权重张量而设计，已成为 Hugging Face 的推荐格式。