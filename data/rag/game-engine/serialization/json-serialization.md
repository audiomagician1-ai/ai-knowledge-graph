---
id: "json-serialization"
concept: "JSON序列化"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 2
is_milestone: false
tags: ["格式"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# JSON序列化

## 概述

JSON（JavaScript Object Notation）序列化是将游戏引擎中的对象数据转换为符合JSON规范的文本字符串，或将该字符串还原为内存对象的过程。JSON格式由Douglas Crockford在2001年正式规范化，并于2013年以ECMA-404标准发布，其语法仅包含六种数据类型：字符串、数字、布尔值、null、数组和对象。

在游戏引擎领域，JSON序列化因其可读性被广泛用于关卡配置、角色属性表、UI布局描述等需要设计师直接编辑的场合。例如Unity引擎早期的.meta文件和场景资产描述文件曾大量使用YAML（与JSON同属文本类序列化），而Unreal Engine则在蓝图资产以外的配置文件（如DefaultEngine.ini之外的JSON配置）中采用JSON存储项目元数据。JSON文件可以直接用记事本打开、人工修改和版本控制系统（如Git）进行差异比对，这是二进制格式无法直接提供的调试便利。

JSON序列化在游戏引擎中的地位来自于它在"开发效率"与"运行性能"之间的明确取舍：与MessagePack、FlatBuffers等二进制格式相比，JSON的解析速度慢3到10倍，文件体积通常大30%至50%，但它在迭代开发阶段几乎不需要额外工具即可检查和修改数据。

## 核心原理

### JSON数据结构与游戏对象映射

JSON的核心结构是键值对对象（`{}`）和有序数组（`[]`）。一个典型的游戏角色配置用JSON表达如下：

```json
{
  "characterId": 1042,
  "name": "骑士",
  "stats": { "hp": 500, "atk": 85, "def": 60 },
  "skills": ["冲锋", "格挡", "战吼"]
}
```

游戏引擎的JSON序列化库（如C#中的`Newtonsoft.Json`或`System.Text.Json`，C++中的`nlohmann/json`）通过反射机制或手动映射将内存中的类字段与JSON键名对应。`System.Text.Json`在.NET 5引入后，对UTF-8字节流的直接处理速度比早期`Newtonsoft.Json`快约2倍，但对复杂多态类型的支持需要额外配置`JsonDerivedType`特性。

### 序列化与反序列化的具体过程

**序列化**（对象→字符串）：引擎遍历对象的字段，将`int`、`float`、`string`等基础类型转为JSON字面量，将嵌套对象递归转为JSON对象，将`List<T>`或数组转为JSON数组。`float`类型在JSON中存储时需注意精度：JSON规范本身不限制数字精度，但JavaScript的IEEE 754双精度浮点数只能精确表示53位整数，在跨语言传输超过2^53的整数时会出现精度丢失。

**反序列化**（字符串→对象）：解析器逐字符扫描JSON文本，构建抽象语法树或直接流式绑定到目标类型。流式解析（Streaming Parse）相比DOM解析内存占用更低，适合大型关卡文件；`System.Text.Json`的`Utf8JsonReader`即采用此模式，无需将整个文件加载为字符串。

### 性能取舍的量化认知

在游戏引擎实践中，JSON序列化的性能瓶颈主要体现在三处：①字符串编码/解码（UTF-8转换）；②内存分配（大量字符串对象产生GC压力）；③数字解析（文本数字转二进制浮点的CPU开销）。以加载一个包含10,000个游戏对象的关卡文件为例，JSON解析通常需要30至80毫秒，而等效的二进制格式（如MessagePack）可压缩至8至15毫秒。因此，JSON序列化在游戏引擎中通常仅用于**编辑器阶段**和**启动时一次性加载**，不用于每帧更新的运行时数据同步。

## 实际应用

**关卡与场景配置**：Godot引擎在其`.tscn`（场景文件）之外，允许开发者将关卡数据单独以JSON导出供外部工具（如Tiled地图编辑器）读写，再在引擎启动时一次性反序列化为`TileMap`节点。

**本地化文本表**：游戏常将多语言字符串存储为JSON文件，键为字符串ID，值为翻译文本。此场景下JSON格式允许翻译人员无需专业工具直接编辑文件，体积问题可通过按语言分包缓解。

**存档系统的调试模式**：许多引擎在Debug构建中将存档格式切换为JSON（而Release构建使用二进制），使QA工程师能够直接读取存档内容定位数值异常，而无需编写专门的存档查看工具。

**网络协议原型阶段**：在游戏后端接口尚未稳定时，客户端与服务器间的数据交换常先以JSON实现，待协议固定后再迁移至Protocol Buffers以降低带宽消耗（通常可减少40%至70%的传输量）。

## 常见误区

**误区一：JSON可以直接存储所有游戏数据类型**
JSON原生只支持数字、字符串、布尔、null、对象、数组六种类型，不支持`Vector3`、`Color`、`DateTime`、二进制Blob等游戏引擎常见类型。`Vector3(1.0, 2.0, 3.0)`必须手动序列化为`{"x":1.0,"y":2.0,"z":3.0}`或`[1.0,2.0,3.0]`，这需要为每种自定义类型编写转换器（Converter）。纹理、音频等二进制资产绝不应嵌入JSON（即使Base64编码会使体积增大约33%），而应存储为文件路径引用。

**误区二：JSON序列化天然支持对象引用和循环引用**
标准JSON格式没有引用（Reference）的概念，若游戏对象图中存在循环引用（如父节点持有子节点，子节点又持有父节点），直接序列化会导致无限递归和栈溢出。`Newtonsoft.Json`通过`ReferenceLoopHandling.Serialize`和`$id`/`$ref`扩展字段解决此问题，但这是对标准JSON的私有扩展，不同库之间不兼容。

**误区三：JSON文件越小越好，应该去除所有空白**
在开发阶段，压缩（Minified）JSON会使人工调试变得困难。正确的做法是在版本库中保存格式化（Pretty-Printed）JSON，在打包发布时使用构建脚本自动压缩，两者分阶段处理，而非在开发期间为节省几KB而牺牲可读性。

## 知识关联

学习JSON序列化需要先理解序列化概述中确立的**数据持久化**基本目标：将运行时内存状态映射为可存储或传输的格式。JSON是最直观的文本类序列化方案，掌握其六种数据类型和键值对结构是理解所有文本序列化格式（包括YAML、TOML、XML）的参照基准。

掌握JSON序列化后，学习**数据表系统**时会遇到JSON的直接延伸：游戏中的怪物属性表、道具配置表本质上是JSON对象数组，数据表系统在JSON基础上增加了索引（按ID快速查找）、热重载（文件变更时自动反序列化）和类型验证（JSON Schema校验字段合法性）等工程化能力。JSON Schema标准（draft-07及以上版本）可定义字段类型约束和必填项，是大型项目中验证数据表正确性的标准手段。
