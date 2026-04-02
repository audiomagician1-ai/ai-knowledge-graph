---
id: "save-game-system"
concept: "存档系统"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 2
is_milestone: false
tags: ["存档"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 38.0
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.355
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 存档系统

## 概述

存档系统（Save System）是游戏引擎中负责将游戏运行时状态序列化到持久存储介质、并在需要时反序列化恢复游戏状态的完整机制。与普通的数据序列化不同，存档系统必须同时处理三个层面的问题：**哪些数据需要被保存**（存档范围）、**以何种格式保存**（存档结构）、以及**版本不匹配时如何迁移**（版本兼容性）。游戏存档本质上是游戏世界某一时间截面的快照（Snapshot），包括玩家属性、关卡进度、物品栏状态、NPC 状态乃至随机数生成器的当前种子值。

存档系统的设计可以追溯到 1980 年代早期的文字冒险游戏。1980 年发布的 *Zork* 系列首次引入了"SAVE/RESTORE"命令，将游戏对象树序列化为纯文本格式存入磁盘。随着游戏规模扩大，现代游戏引擎（如 Unity 的 PlayerPrefs 和自定义 SaveManager、Unreal Engine 的 USaveGame 类体系）都提供了专用的存档框架，以应对 GB 级开放世界存档数据的复杂需求。

存档系统在实际开发中之所以常常成为技术债的来源，是因为游戏内容在开发周期中持续变化：新增道具、删除关卡、修改角色属性结构，都可能导致旧存档在新版本中无法正确加载，产生数据损坏或游戏崩溃。因此存档系统不仅是序列化技术的应用，更是一个需要前瞻性设计的版本管理问题。

---

## 核心原理

### 存档数据的选取与标记

游戏运行时对象中，并非所有字段都需要被存档。存档系统通常使用**标记机制**区分持久数据与瞬态数据。在 Unity 中，开发者通过 `[System.Serializable]` 特性标记可序列化类，并配合自定义的 `[SaveField]` 特性（或排除 `[NonSerialized]`）精确控制存档范围。例如，角色的 `currentHP`（当前血量）需要存档，但 `cachedRenderer`（渲染组件引用）属于运行时引用，无需也无法跨场景持久化。

一个常见的存档数据结构采用**键值字典**加**类型化数据块**的混合形式：

```
SaveFile {
    version: uint32          // 存档格式版本号
    timestamp: int64         // 存档时间（Unix时间戳）
    chunks: Map<string, byte[]>  // 模块化数据块
}
```

将存档拆分为独立 chunk（如 `"player"`、`"world"`、`"quests"`）的好处在于：加载时可以只反序列化所需模块，同时当某个模块的 Schema 发生变化时，其他模块不受影响。

### 序列化格式选择

存档系统常用的序列化格式有三种，各有权衡：

- **JSON/XML**：人类可读，便于调试，但体积大且解析慢。适合独立游戏或开发阶段使用。一个包含 500 个物品的背包 JSON 存档可能达到 80KB，而等效二进制只需 8KB。
- **二进制序列化**（如自定义格式或 MessagePack）：体积小、读写快，但不具备自描述性，版本迁移必须手动处理字段偏移变化。
- **Protocol Buffers（protobuf）**：Google 于 2008 年开源，使用字段编号（field number）而非字段名称标识数据，天然支持字段增删的向前/向后兼容，是大型商业游戏存档的常见选择。protobuf 的核心规则是：**已分配的字段编号永远不能复用**，删除字段时必须将其标记为 `reserved`。

### 版本迁移机制

版本迁移（Migration）是存档系统最容易被忽视却最关键的功能。标准做法是在存档文件头部存储一个 `schema_version` 整数，加载时通过**迁移链（Migration Chain）**逐步升级：

```
migrate_v1_to_v2(data): 将旧的 "stamina" 字段重命名为 "endurance"
migrate_v2_to_v3(data): 新增 "crafting_unlocks" 字段，默认值为空列表
migrate_v3_to_v4(data): 将 "gold" 从 int32 扩展为 int64
```

加载器读取版本号后，依次调用从当前版本到目标版本之间所有的迁移函数。例如一个 v1 存档加载到 v4 版本游戏时，依次执行 `v1→v2 → v2→v3 → v3→v4` 三次迁移。每个迁移函数应保持**幂等性**：对同一数据执行两次结果应与执行一次相同，以防止迁移过程中断后重试导致数据错误。

---

## 实际应用

**《塞尔达传说：荒野之息》**的存档系统将世界状态分为全局状态（GameData）和场景状态（SceneData）两个独立文件。GameData 记录林克的属性与任务标志，SceneData 按场景分块存储宝箱开闭、敌人死亡等信息，总存档大小约为 3MB。这种分块存储使得加载特定区域时无需反序列化整个世界。

在 Unity 项目中，一个实用的存档系统实现步骤为：① 定义 `ISaveable` 接口，要求每个需要存档的 MonoBehaviour 实现 `CaptureState()` 和 `RestoreState(object)` 方法；② 由全局 `SaveManager` 在存档时遍历所有 `ISaveable` 对象，以对象的 GUID 为键收集状态字典；③ 使用 `BinaryFormatter` 或 `JsonUtility` 将字典序列化后写入 `Application.persistentDataPath` 下的 `.sav` 文件。游戏版本号应同时写入 `Application.version` 字段，供后续迁移判断使用。

移动游戏通常将存档写入平台专属路径：iOS 写入 `NSDocumentDirectory`（会被 iCloud 备份），Android 写入 `/data/data/<package>/files/`（内部存储）。开发者需要特别注意 **Android 外部存储的权限变更**——Android 10（API 29）起强制启用分区存储，直接路径写入外部存储的旧代码将失效。

---

## 常见误区

**误区一：使用 Unity `BinaryFormatter` 作为长期存档格式**
`BinaryFormatter` 将 C# 类的完整类型信息（含程序集名称）序列化到文件中。一旦重命名命名空间、迁移代码到新程序集或升级 Unity 版本，旧存档立即无法反序列化，抛出 `SerializationException`。正确做法是使用与代码结构解耦的中间数据对象（DTO，Data Transfer Object）专门承载存档数据，并控制其命名稳定性。

**误区二：存档时机只考虑主动存档，忽略自动存档频率**
许多开发者在设计存档系统时只实现了玩家手动触发的存档，而在存档失败（磁盘满、IO 错误）时没有设置备份机制。专业做法是维护**双缓冲存档**（Dual-Buffer Save）：每次写入新存档前，将上一次的存档重命名为 `.bak` 文件，确保即使新存档写入中途断电，也可以回退到上一个完整存档。

**误区三：认为版本号相同就代表存档兼容**
同一个 `schema_version` 内的热更新（hotfix）如果修改了序列化字段，同样会破坏已有存档。应将**游戏内容版本**（控制关卡、数值平衡）与**存档格式版本**（控制序列化结构）分开管理。存档格式版本只在序列化结构发生变化时递增，而非跟随游戏版本号。

---

## 知识关联

存档系统建立在**二进制序列化**技术之上——理解字节对齐、字段编码和端序（Endianness）问题是实现高效存档格式的前提，尤其在设计跨平台存档（PC 与主机互通）时，需要统一规定使用小端序（Little-Endian）存储多字节整数。

掌握存档系统的基本结构后，可以进一步学习 **Schema 版本控制**，系统化地管理存档格式的演进历史，以及如何在团队协作中避免多人同时修改存档结构产生的冲突。**检查点存档**（Checkpoint Save）在此基础上引入了时间维度，解决"在哪里保存"的问题。**云存档**将存储介质从本地文件系统扩展到远程服务器，引入同步冲突解决等额外挑战。**存档加密**则解决存档数据被玩家篡改（作弊）的安全问题，通常采用 HMAC-SHA256 对存档内容签名而非加密，以平衡性能开销。**场景持久状态**专注于大型开放世界中如何高效存储和流式加载分散在数百个场景中的状态数据，是存档系统在具体场景类型上的深度应用。