---
id: "serialization-intro"
concept: "序列化概述"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 1
is_milestone: false
tags: ["基础"]
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "industry"
    ref: "Gregory, Jason. Game Engine Architecture, 3rd Ed., Ch.6.4"
  - type: "industry"
    ref: "UE5 Documentation: Serialization Overview, Epic Games 2024"
  - type: "industry"
    ref: "Unity Manual: Script Serialization, Unity Technologies 2024"
  - type: "technical"
    ref: "Google Protocol Buffers Documentation, 2024"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 序列化概述

## 概述

序列化（Serialization）是将内存中的对象状态转换为可存储或可传输的数据格式的过程，而反序列化（Deserialization）则是将这些数据还原为内存对象的逆过程。在游戏引擎中，这一技术解决了一个根本性问题：RAM中的对象包含指针、虚函数表等平台相关结构，无法直接写入磁盘或通过网络传输，因此必须将对象的"有效数据"提取并以中立格式保存。

序列化概念最早在1980年代随面向对象语言普及而形成系统理论，Java在1997年（JDK 1.1）将其标准化为语言特性，引入`java.io.Serializable`接口。游戏引擎领域对序列化的需求远比通用软件复杂：一个典型的3D游戏场景文件需要同时序列化Transform（位置/旋转/缩放）、网格引用、材质属性、脚本组件状态等数十种异质数据类型。

序列化在游戏开发中是贯穿整个生命周期的基础能力。关卡存档、玩家进度保存、编辑器场景文件(.unity/.uasset)、网络同步数据包、热更新配置表、回放录制——这六类核心功能全部依赖序列化机制。缺少可靠的序列化方案，游戏引擎无法持久化任何运行时状态。

## 核心原理

### 序列化的数学模型

序列化可以形式化描述为一个映射函数：`S: Object → Bytes`，其反函数为 `D: Bytes → Object`，要求 `D(S(obj))` 语义等价于原始 `obj`（注意：内存地址可以不同，但逻辑状态必须一致）。这个"语义等价"要求是序列化设计的核心约束——指针不能直接序列化地址值，必须转换为对象ID或相对引用，这导致游戏引擎需要专门的**引用解析（Reference Patching）**阶段。

### 序列化格式的三种基本类型

游戏引擎序列化格式分为三大类：

**二进制格式**（如Unreal的`.uasset`、Unity的YAML转binary的`.prefab`）：数据紧凑，读写速度最快，但不可读、版本兼容性差。典型大小比文本格式小60%~80%。

**文本格式**（如JSON、YAML、XML）：人类可读，易于调试和版本控制diff，但解析速度慢。Unity早期使用YAML存储Scene文件，一个含500个GameObject的场景文件可达数MB。

**混合格式**：开发阶段用文本格式（方便编辑器调试），发布阶段自动转换为二进制（优化运行时性能）。Unreal Engine 4/5采用此策略，`.uasset`在Cooked版本与Editor版本之间存在格式差异。

### 序列化的关键技术挑战

**版本兼容性**是游戏序列化最棘手的问题。当游戏版本从1.0升级到1.1，如果删除了某个字段或更改了数据类型，旧存档文件将无法正确解析。解决方案是在每个序列化文件头部写入**版本号**（如Unreal使用`FPackageFileSummary`结构存储4字节版本号），并在反序列化时进行字段匹配而非位置匹配。

**循环引用**是另一个核心难题：对象A引用对象B，对象B反过来引用对象A，朴素的递归序列化会进入死循环。标准解法是维护一个"已访问对象集合"（通常是哈希表），遇到已序列化的对象只写入其ID而非再次展开。

**多态对象**序列化要求在数据中记录**类型标识符**（Type ID）。例如，一个`Component`数组中可能混存`RigidBodyComponent`和`AudioComponent`，反序列化时必须根据Type ID调用正确的构造函数，这通常需要引擎维护一张全局的类型注册表（Type Registry）。

## 实际应用

**Unity编辑器存档**：Unity的`.unity`场景文件本质上是YAML文本，每个GameObject对应一个YAML文档块，以`--- !u!1 &123456789`格式标记（`!u!1`表示GameObject类型，`&123456789`是File ID）。理解这一格式是解决Unity场景合并冲突的基础。

**游戏存档系统**：一个RPG游戏的存档需要序列化玩家等级、背包物品列表（含物品ID和数量）、任务状态标志位、地图探索记录等。实际开发中通常定义一个`SaveData`结构体，将其序列化为JSON或二进制写入`Application.persistentDataPath`目录，文件大小通常控制在数KB到数十KB之间。

**网络同步**：帧同步（Lockstep）架构要求每帧将所有玩家输入序列化为数十字节的数据包广播给所有客户端，要求序列化/反序列化延迟低于1ms。这迫使网络同步模块放弃通用序列化库，转而使用手写的位域（Bitfield）序列化。

**Unreal蓝图资产**：`.uasset`文件包含序列化后的蓝图图表，其中每个节点的位置、连接关系、变量类型都被完整保存，文件格式使用Unreal自研的二进制包格式，头部含`0x9E2A83C1`魔数（Package Magic Number）用于文件类型识别。

## 常见误区

**误区一：序列化只需要保存字段值**。许多初学者认为将对象所有public字段写入JSON就完成了序列化。但游戏对象通常含有**外部引用**（如Prefab对其他Asset的引用），这些引用不能序列化内容本身，而应序列化**引用路径或GUID**。Unity的`AssetDatabase`为每个Asset分配128位GUID，序列化时只存储GUID，加载时通过GUID查找实际资产。

**误区二：反序列化是序列化的简单逆操作**。实际上反序列化通常比序列化更复杂，因为它必须处理：文件版本与当前代码版本不匹配、字段缺失时的默认值填充、类型变更的数据迁移。Unreal Engine专门为此设计了`FArchive`类的版本迁移（Versioning）机制，通过`SerializePackageFileSummary`中的`FileVersionUE4`字段控制兼容性逻辑。

**误区三：序列化格式一旦确定无需更改**。游戏开发周期通常为2~5年，在此期间游戏逻辑类必然经历多次重构。如果序列化格式缺乏版本管理，每次重构都可能破坏历史存档，导致QA无法复现早期版本的bug。正确做法是从项目第一天起就在序列化头部加入版本字段，并编写数据迁移（Migration）函数。

## 知识关联

**前置知识**：需要理解游戏引擎的对象模型（GameObject/Component架构），因为序列化的对象粒度和引用关系取决于引擎的组件结构。了解内存布局（结构体对齐、指针大小）有助于理解为什么原始内存不能直接持久化。

**后续概念**：
- **二进制序列化**：深入学习如何用位操作和固定布局结构实现高性能序列化，适用于网络包和运行时存档
- **JSON序列化**：学习文本格式序列化在配置文件和编辑器工具中的具体实现
- **属性序列化**：了解如何通过反射系统（Reflection）自动化序列化流程，避免手动为每个类编写序列化代码
- **配置系统**：序列化在游戏参数配置中的应用，包括热更新和A/B测试方案
- **回放系统**：将游戏输入或状态增量序列化以实现战斗回放的特殊应用场景