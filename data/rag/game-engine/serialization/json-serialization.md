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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# JSON序列化

## 概述

JSON序列化是将游戏引擎中的对象、组件数据转换为JSON（JavaScript Object Notation）文本格式，并在需要时从该文本还原为内存对象的过程。JSON格式由Douglas Crockford于2001年正式规范化，并于2013年以ECMA-404标准发布，其核心语法仅使用花括号`{}`、方括号`[]`、冒号`:`和逗号`,`六种标点符号，人类无需任何专用工具即可直接阅读和编辑。

在游戏引擎开发中，JSON序列化主要服务于两类场景：一是设计师和程序员需要手工编辑的配置数据（例如角色属性表、关卡参数），二是调试阶段需要快速检查游戏状态的场合。与二进制序列化格式相比，JSON文本文件可以被版本控制系统（Git、SVN）进行逐行diff比较，这使得游戏资产的改动历史清晰可追溯。

JSON序列化的代价是性能：解析一个100KB的JSON文件通常比解析等效的MessagePack二进制格式慢3到5倍，文件体积也通常大30%到50%。因此，在游戏引擎中采用JSON序列化时，工程师必须明确区分"编辑时格式"与"运行时格式"——JSON适合前者，不适合后者。

## 核心原理

### JSON数据模型与游戏对象的映射

JSON支持六种基本类型：字符串、数字、布尔值、null、对象（键值对集合）和数组。一个典型的游戏角色组件在JSON中的表示如下：

```json
{
  "componentType": "RigidBody",
  "mass": 75.5,
  "useGravity": true,
  "velocity": [0.0, 0.0, 0.0],
  "constraints": {
    "freezeRotation": ["X", "Z"]
  }
}
```

游戏引擎在实现JSON序列化时，需要建立从C++/C#类型到JSON类型的映射规则：`float`和`double`映射到JSON数字，`Vector3`通常映射为包含三个元素的数组或带有`x/y/z`键的对象，`Quaternion`映射为包含四个元素的数组。选择哪种映射方式会影响文件可读性，例如`[1.0, 0.0, 0.0, 0.0]`比`{"x":1.0,"y":0.0,"z":0.0,"w":0.0}`更紧凑，但后者在调试时语义更清晰。

### 序列化与反序列化流程

JSON序列化的标准流程分为三步：①通过反射（Reflection）或手动注册的方式扫描对象的字段；②将每个字段值按类型规则转为JSON节点；③将节点树写入字符串或文件流。

反序列化流程则相反，但多出一个**类型校验**步骤：解析器读取JSON文本生成语法树后，需逐字段检查类型是否与目标类定义匹配。例如，若JSON中`mass`字段的值为`"75.5"`（字符串），而目标类期望`float`，引擎应决定是报错还是进行隐式转换。Unity的`JsonUtility`选择宽松策略（忽略未知字段），而Unreal Engine的JSON模块默认采用严格策略。

### 浮点数精度问题

JSON规范本身不限制数字精度，但JSON库的实现会引入精度问题。IEEE 754双精度浮点数最多有效数字约为15至17位，而许多JSON序列化库默认只输出6位有效数字。这对游戏数据危害显著：世界坐标若使用6位精度，在10万单位范围内误差可达0.01单位。引擎中正确的做法是将`double`使用`%.17g`格式输出，或对`float`使用`%.9g`格式，确保数值往返序列化（round-trip）后与原始值完全相同。

## 实际应用

**场景配置文件**：虚幻引擎4的`.uproject`文件和Unity的部分`ProjectSettings`文件均采用JSON格式存储引擎版本、插件启用状态等配置，原因正是需要让开发者在文本编辑器中直接修改并通过Git追踪变更。

**调试快照**：在游戏逻辑调试中，可以将当前帧的关键游戏状态序列化为JSON文件保存到磁盘，下一次运行时从该JSON文件恢复状态，复现特定的Bug场景。这种"状态快照"工作流依赖JSON的人类可读性，因为开发者需要手动修改快照中的某个数值来缩小问题范围。

**热更新配置**：移动游戏中常见的做法是从服务器下载JSON格式的数值配置（如角色等级经验表、活动奖励规则），由于JSON解析库在所有平台都有成熟实现（Android和iOS均内置JSON解析能力），无需额外部署反序列化工具链，维护成本低。

## 常见误区

**误区一：认为JSON适合存储所有游戏资产**。JSON本质是文本格式，存储纹理、音频、网格等二进制大数据时，通常需要将字节数组转为Base64编码，这会使数据体积增加约33%，且编解码本身额外消耗CPU时间。游戏引擎中正确的做法是仅用JSON描述资产的元数据（路径、参数），而非资产本体。

**误区二：认为JSON反序列化速度足够用于运行时**。以解析一个包含1000个NPC属性的JSON文件为例，在低端移动设备上使用RapidJSON（C++最快的JSON库之一）可能仍需15至30毫秒，足以造成明显卡顿。游戏引擎的正确实践是在打包阶段（Build Pipeline）将JSON转换为二进制格式（如FlatBuffers或自定义格式），运行时只加载二进制版本，JSON文件仅保留在开发目录中。

**误区三：忽视JSON不支持注释的限制**。标准JSON（ECMA-404）不允许`//`或`/* */`注释，这对需要在配置文件中大量注释的游戏策划人员造成不便。常见的解法是使用JSON5或JSONC（JSON with Comments）变体，但需注意引入非标准解析库，可能带来跨平台兼容风险。

## 知识关联

学习JSON序列化之前，需要掌握**序列化概述**中的核心概念：对象图（Object Graph）遍历、序列化标记（Serialization Marker）以及序列化版本控制的必要性。JSON序列化是序列化概述中讨论的"文本类序列化格式"的典型代表，而MessagePack、Protobuf是同一框架下的"二进制类格式"代表，三者形成直接对比。

JSON序列化是学习**数据表系统**的前置技术。游戏中的数据表（DataTable）——如武器伤害表、技能参数表——在编辑和版本管理阶段通常以JSON或CSV存储，引擎的数据表系统需要实现从JSON行数组到结构化数据表对象的批量反序列化，并进一步建立索引加速运行时查找。理解JSON序列化的字段映射规则和类型校验逻辑，是实现数据表系统导入管线的直接前提。