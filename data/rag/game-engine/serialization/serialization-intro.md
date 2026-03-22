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
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
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
---
# 序列化概述

## 概述

序列化（Serialization）是将**内存中的对象状态转换为可存储或可传输的字节流**的过程；反序列化（Deserialization）是其逆过程。在游戏引擎中，序列化无处不在——存档保存、网络同步、资产加载、编辑器撤销系统、热重载都依赖它。

Gregory（2021）指出，序列化是游戏引擎最"隐形"但最关键的基础设施之一。一个设计良好的序列化系统使内容创作者能够自由修改数据格式而无需程序员介入；一个设计糟糕的序列化系统则是引擎中最大的技术债务来源。

**核心问题**：内存中的对象包含指针、虚函数表、平台相关布局——这些都不能直接写入文件或发送到网络。序列化的本质是**将机器相关的运行时表示转换为机器无关的持久化表示**。

## 核心知识点

### 1. 序列化格式分类

| 格式类型 | 代表 | 可读性 | 大小 | 速度 | 适用场景 |
|---------|------|--------|------|------|---------|
| **文本格式** | JSON, XML, YAML | 高 | 大（3-10x） | 慢 | 配置文件、调试、编辑器 |
| **二进制格式** | FlatBuffers, Protobuf | 低 | 小（基准） | 快 | 运行时资产、网络传输 |
| **混合格式** | MessagePack, CBOR | 中 | 中（1.2-2x） | 中 | API 通信、跨语言交换 |

**游戏引擎的典型策略**：
- **开发期**用文本格式（JSON/YAML），便于版本控制和手动编辑
- **打包发布**时转换为二进制格式（"Cooking"过程），优化加载速度
- UE5 使用自定义二进制格式（`.uasset`），加载速度比 JSON 快 **50-100 倍**

### 2. 核心技术挑战

**版本兼容性**（Version Tolerance）：
游戏更新后数据结构变化（新增字段、删除字段、类型更改），旧版本存档必须能被新版本正确加载。

解决方案：
- **字段标签系统**（Protocol Buffers 方式）：每个字段有唯一数字 ID，按 ID 匹配而非位置
- **Schema 版本号**：文件头记录版本，加载时执行迁移（Migration）
- **UE5 方式**：FProperty 系统 + 基于 FName 的字段匹配 + CustomVersions 迁移链

**指针与引用**：
内存地址在每次运行时不同，不能直接序列化。解决方案：
- 将指针转换为**唯一标识符**（GUID、路径、索引）
- 反序列化时通过标识符重建引用关系
- UE5 使用 FSoftObjectPath（字符串路径）和 FObjectPtr（延迟加载引用）

**多态对象**：
基类指针指向派生类时，需要序列化实际类型信息。
- **类型标签**：写入类名/类型 ID，反序列化时通过工厂模式创建正确类型
- UE5 使用 UClass 反射系统自动处理

### 3. 主要引擎的序列化架构

**UE5 序列化**：
- 核心类：`FArchive`（抽象 IO 流，统一读/写接口）
- `operator<<` 重载实现双向序列化（同一代码同时处理读和写）
- `UObject` 通过 `Serialize()` 虚函数自动序列化所有 UPROPERTY 标记的字段
- 蓝图类完全通过反射序列化，无需手写代码

**Unity 序列化**：
- `[Serializable]` 属性标记可序列化类
- `JsonUtility` 处理 JSON；`BinaryFormatter` 处理二进制（已不推荐）
- ScriptableObject 和 MonoBehaviour 的 `[SerializeField]` 字段由引擎自动持久化
- 限制：不支持多态、不支持字典（需要自定义 Wrapper）

### 4. 性能优化策略

| 策略 | 原理 | 效果 |
|------|------|------|
| **内存映射文件**（mmap） | 将文件直接映射到虚拟地址空间，按需加载 | 启动时间降低 60-80% |
| **零拷贝反序列化** | FlatBuffers：直接读取缓冲区，不创建中间对象 | 反序列化时间趋近于零 |
| **增量序列化** | 只序列化变化的字段（Delta Serialization） | 网络带宽降低 70-90% |
| **异步加载** | 在后台线程执行 IO 和反序列化 | 不阻塞主线程 |
| **预计算布局** | 编译期确定内存布局，运行时直接 memcpy | 反序列化速度接近内存带宽极限 |

## 关键原理分析

### 序列化与反射的关系

完善的反射系统（运行时获取类型信息——字段名、类型、偏移量）使序列化可以完全自动化。UE5 的 `UPROPERTY` 宏 + Unreal Header Tool (UHT) 生成反射数据，使得新增一个可序列化字段只需一行宏声明。没有反射的引擎（如纯 C++ 项目）则需要手动编写每个类的序列化代码——维护成本极高。

### 序列化即接口契约

序列化格式一旦发布就成为**接口契约**（API Contract）。修改格式等同于修改公共 API——必须维护向后兼容。这就是为什么 Protocol Buffers 强制要求"永不复用字段号"。

## 实践练习

**练习 1**：用 JSON 和 Protocol Buffers 分别序列化一个游戏角色对象（名称、等级、装备列表），比较文件大小和加载时间。

**练习 2**：在现有序列化中新增一个字段"技能点数"，测试旧版本存档是否能正确加载（不含新字段时应有合理默认值）。

## 常见误区

1. **"JSON 足够快"**：对于编辑器数据可以，但运行时加载数千个资产时 JSON 解析是严重瓶颈
2. **忽略版本兼容**：开发早期不考虑版本控制，后期每次改结构都要手动迁移存档
3. **序列化一切**：运行时计算的缓存数据（如导航网格）不应序列化——它们应该按需重建