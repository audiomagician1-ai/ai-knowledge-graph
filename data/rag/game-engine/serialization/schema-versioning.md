---
id: "schema-versioning"
concept: "Schema版本控制"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 2
is_milestone: false
tags: ["版本"]

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
# Schema版本控制

## 概述

Schema版本控制是指在游戏引擎序列化系统中，通过显式标记数据结构的版本号，使引擎能够正确读取不同版本序列化文件的机制。当玩家的存档文件由旧版本游戏创建，而当前运行的是新版本游戏时，Schema版本控制决定了这份存档能否被成功加载，以及哪些字段会被保留、丢弃或填充默认值。

该机制起源于数据库领域的"模式迁移"（Schema Migration）概念，在2000年代初随着网游兴起被引入游戏存档系统。Unity的序列化系统从版本4.0开始内置了`[FormerlySerializedAs]`属性，而虚幻引擎（Unreal Engine）则通过`FArchive::ArVer`字段（取值如`VER_UE4_ADDED_PACKAGE_SUMMARY_LOCALIZATION_ID = 516`）来区分不同版本的二进制格式。

对于拥有持久化存档的游戏（如RPG、策略游戏），Schema版本控制直接影响玩家是否会因为游戏更新而丢失数百小时的游戏进度。一个设计糟糕的版本控制方案可能导致存档静默损坏——数据看似加载成功，但关键字段使用了错误的默认值，这比加载失败更难调试。

## 核心原理

### 版本号的存储方式

最基础的实现是在每个序列化文件的头部（Header）写入一个整数版本号。例如：

```
[4字节魔数 0x47414D45] [4字节版本号 = 7] [后续数据...]
```

版本号通常采用单调递增的整数，而非语义化版本（SemVer），因为序列化系统只需要知道"哪个版本更新"，不需要区分主版本号和次版本号。部分系统（如Protocol Buffers）使用字段编号（Field Number）而非文件级版本号，每个字段的ID一旦分配就永久不变，这是另一种主流策略。

### 向后兼容（Backward Compatibility）

向后兼容指**新版本程序能读取旧版本数据**。实现策略包括：

- **添加可选字段**：新增字段时赋予默认值，读取旧存档时若字段缺失则使用默认值填充。例如游戏v2.0新增了`stamina`字段，读取v1.0存档时自动设为`100`。
- **字段重命名标记**：Unity的`[FormerlySerializedAs("oldFieldName")]`属性告知序列化器在读取旧数据时将`oldFieldName`映射到当前字段。
- **版本分支读取**：反序列化函数内部用`if (version < 5)` 执行旧读取路径，`else`执行新路径。

向后兼容是版本控制中**最优先保证**的方向，因为玩家升级游戏后必须能继续使用旧存档。

### 向前兼容（Forward Compatibility）

向前兼容指**旧版本程序能读取新版本数据**，这在游戏领域相对少见，主要出现在以下场景：多人游戏中客户端版本不一致，或主机游戏允许回退到旧版本存档。

实现向前兼容需要旧程序在遇到未知字段时能**跳过而非崩溃**。这要求数据格式中包含字段长度信息，以便旧程序计算出未知字段的字节范围并跳过。Protocol Buffers的TLV（Type-Length-Value）编码天然支持这一特性：每个字段包含类型和长度，未识别的字段可直接略过。

### 版本号的粒度选择

版本号可以施加在不同粒度上：
- **文件级**：整个存档文件一个版本号，简单但粗粒度
- **对象级**：每个可序列化类（如`PlayerData`、`InventoryData`）各自维护版本号，修改`InventoryData`不影响`PlayerData`的版本计数
- **字段级**：Protocol Buffers采用此策略，用字段编号替代版本号

对象级粒度是游戏引擎中最常见的折中方案，Unreal Engine的`UPROPERTY`系统和自定义`Serialize`函数均支持在类层级进行版本检查。

## 实际应用

**RPG存档升级场景**：假设游戏v1.0的`CharacterData`包含`hp`和`mp`两个字段，v2.0新增了`skillPoints`字段，v3.0将`mp`重命名为`mana`并删除了`hp`（改由装备计算）。Schema版本控制代码如下：

```csharp
void Deserialize(BinaryReader reader, int version) {
    if (version >= 1) hp = reader.ReadInt32();   // v1字段
    if (version >= 1) mp = reader.ReadInt32();
    if (version >= 2) skillPoints = reader.ReadInt32(); // v2新增
    if (version >= 3) mana = mp; // v3: mp改名为mana
    // hp在v3中被弃用，读取后丢弃
}
```

**多人游戏网络协议**：在帧同步游戏中，服务器发送的帧数据包含协议版本号。当某个客户端的版本落后时，服务器可以发送带有旧格式字段的兼容包，或拒绝该客户端连接并提示更新。

## 常见误区

**误区一：用字符串日期或哈希值作为版本号**。用`"2024-03-15"`或文件MD5作为版本号看似直观，但序列化系统需要**比较版本新旧**（`if version < X`），字符串无法进行有意义的大小比较，哈希值完全无序。版本号必须是单调递增的整数，才能支持"当版本低于N时执行迁移逻辑"这类判断。

**误区二：删除字段时立即移除读取代码**。开发者在v3.0删除了`legacyFlag`字段，便同时删除了对应的`reader.ReadByte()`调用。这会导致v1.0/v2.0存档中该字节的内容被后续字段读取，造成所有后续字段数据错位（off-by-one），表现为存档加载后数值全部异常。正确做法是保留读取代码但不使用返回值：`reader.ReadByte(); // deprecated in v3, skip`。

**误区三：认为向前兼容可以通过"不改变已有字段"来实现**。仅仅不修改旧字段是不够的——如果新版本在旧字段之间**插入**了新字段（而非追加到末尾），旧程序读取时字段偏移量已经错乱。向前兼容必须依赖带长度信息的格式（如TLV）或字段名/ID映射，单纯依赖字段顺序的格式无法实现向前兼容。

## 知识关联

Schema版本控制建立在**存档系统**的基础上：存档系统负责将游戏状态写入持久存储，而版本控制解决的是"不同时期写入的数据如何被正确读回"这一问题。没有存档系统提供的二进制读写接口，版本号字段就无处写入。

Schema版本控制直接引出**数据迁移**这一更复杂的话题。版本控制只是识别出"当前数据是旧版本"，而数据迁移负责将旧版本数据转换为新版本格式——例如将v1的`gold`（整数金币）拆分为v2的`gold`和`gems`（两种货币）。数据迁移通常通过"迁移链"实现：v1→v2→v3，每一步只负责相邻版本间的转换逻辑，使得版本跨度再大也能逐步升级。
