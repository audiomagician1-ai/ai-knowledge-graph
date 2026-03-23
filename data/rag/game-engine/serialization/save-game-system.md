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
---
# 存档系统

## 概述

存档系统（Save System）是游戏引擎中负责将游戏运行时状态序列化到持久存储介质、并在需要时反序列化还原的子系统。其核心任务是捕获玩家进度的"快照"——包括角色属性、地图状态、物品栏内容、任务标志位等——并以结构化格式写入磁盘、闪存或云端。区别于普通的二进制序列化，存档系统还必须处理游戏版本升级后数据结构变化带来的**向前兼容**和**向后兼容**问题。

存档系统在家用游戏机普及的1980年代末随之出现。早期FC（红白机）卡带使用SRAM和纽扣电池保存几百字节的数据；PlayStation时代引入了内存卡（Memory Card），容量仅128KB，迫使开发者极度压缩存档结构。现代游戏存档动辄数MB，且需在PC、主机、移动端之间同步，对系统设计的要求发生了根本性变化。

存档系统的设计质量直接影响玩家体验：存档损坏、版本不兼容导致进度丢失，是玩家差评的主要来源之一。同时，存档文件也是作弊和修改的目标，因此系统设计必须兼顾可读性、鲁棒性和安全性三者的平衡。

---

## 核心原理

### 存档数据的结构设计

存档文件通常由**文件头（Header）**和**数据体（Body）**两部分组成。文件头至少包含以下字段：

- **魔数（Magic Number）**：固定字节串，用于识别文件格式，例如 `0x53415645`（ASCII "SAVE"）
- **版本号（Version）**：无符号整数，标识存档格式版本，升级游戏时用于触发迁移逻辑
- **时间戳（Timestamp）**：Unix时间，用于多存档槽的排序显示
- **校验和（Checksum）**：CRC32或MD5哈希，检测文件损坏或篡改

数据体部分按游戏系统划分为若干**存档块（Save Block）**，每个块对应一个游戏子系统（如PlayerBlock、InventoryBlock、QuestBlock），块之间相互独立，便于局部更新和局部迁移。

### 序列化格式的选择

游戏存档常用三种格式：

1. **自定义二进制格式**：体积最小，读写速度最快，适合主机游戏。缺点是可读性为零，调试困难。一个典型的主角属性块只需 `struct PlayerData { int32_t hp; int32_t maxHp; float posX; float posY; }` 共16字节。
2. **JSON/XML文本格式**：可读性强，易于调试，但体积是二进制格式的3～10倍。适合PC独立游戏或需要MOD支持的场景。
3. **Protocol Buffers / FlatBuffers**：Google推出的跨语言二进制序列化方案，FlatBuffers可零拷贝读取，适合大型跨平台项目。FlatBuffers的模式文件（.fbs）本身就记录了字段定义，天然支持版本追踪。

### 版本迁移机制

版本迁移（Migration）是存档系统区别于普通序列化的核心能力。当游戏从版本2更新至版本3，若新增了一个`staminaMax`字段，旧存档中没有该字段，加载时必须填入默认值100；若删除了`legacyFlag`字段，旧存档中多余的字节必须被跳过。

通用的版本迁移模式如下：

```
LoadSave(file):
    header = ReadHeader(file)
    if header.version == CURRENT_VERSION:
        return Deserialize(file)
    else:
        data = Deserialize(file, header.version)
        for v in range(header.version, CURRENT_VERSION):
            data = MigrationTable[v → v+1](data)
        return data
```

`MigrationTable`是一个以版本号为键的函数映射，每个迁移函数只负责相邻两个版本之间的转换。这种**链式迁移**设计确保即使玩家跳过多个版本更新，存档依然可以逐步迁移至最新格式，无需为每对版本组合单独编写迁移逻辑。

### 原子写入与存档安全

游戏突然崩溃或掉电时，若存档文件写到一半，会产生损坏的存档。正确做法是**原子写入**：先将新存档写到临时文件`save.tmp`，写入完成后再通过文件系统的`rename()`操作替换旧文件`save.dat`。在大多数操作系统（Windows NTFS、Linux ext4）中，`rename()`是原子操作，不会出现中间状态。

---

## 实际应用

**《塞尔达传说：旷野之息》**采用了分块存档设计，将神庙完成状态、科洛克种子、武器耐久等分存于不同的数据块，使得自动存档（Auto Save）只需刷新部分块，而非重写整个存档文件，显著降低了IO开销。

**《暗黑破坏神 II》**的.d2s存档文件中包含一个16字节的MD5校验头，官方服务器通过校验该值来检测离线存档修改，这是存档校验与反作弊结合的经典案例。

独立游戏常用Unity的`PlayerPrefs`作为轻量存档方案，但`PlayerPrefs`在Windows上将数据写入注册表，在macOS写入plist文件，每次写入最大限制约1MB，不适合存储复杂游戏状态。正式项目应改用自定义序列化写入`Application.persistentDataPath`目录下的文件。

---

## 常见误区

**误区一：版本号只需在破坏性变更时才递增**
实际上，任何对存档结构的修改——包括新增可选字段——都应递增版本号并编写对应迁移函数。若新增字段时不递增版本，加载旧存档时将无法区分"该字段是0还是根本不存在"，导致默认值逻辑失效。

**误区二：JSON存档不需要版本字段，字段名就是文档**
JSON字段名确实有自描述性，但字段语义会随版本变化。例如`"damage": 50`在v1中表示固定伤害，在v2中可能改为基础伤害（需乘以倍率），这种语义变化单靠字段名无法区分，必须依赖版本号加迁移逻辑。

**误区三：存档直接存在`StreamingAssets`目录**
`StreamingAssets`是只读目录（在Android打包后尤其如此），向其写入存档在部分平台上会静默失败。存档文件必须写入`Application.persistentDataPath`（Unity）或对应平台的用户数据目录。

---

## 知识关联

存档系统建立在**二进制序列化**的基础上：理解字节序（大端/小端）、结构体内存布局和基本类型的二进制表示，是手写自定义存档格式的前提。

掌握存档系统后，可以进一步学习**Schema版本控制**，用Protocol Buffers或Avro等带有内置版本管理的Schema语言替代手写迁移表，将版本兼容性从代码逻辑提升为工具链保障。**检查点存档（Checkpoint Save）**在此基础上引入了时间维度，解决"如何在游戏流程中选择最优快照时机"的问题。**存档加密**则在存档结构成熟后，通过AES-128等算法对数据体加密，结合文件头中的HMAC签名抵御外部篡改，是商业游戏防作弊的必要手段。
