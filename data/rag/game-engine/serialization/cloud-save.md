---
id: "cloud-save"
concept: "云存档"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 2
is_milestone: false
tags: ["云端"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 云存档

## 概述

云存档（Cloud Save）是将玩家游戏进度、设置及状态数据上传至远程服务器，并在多台设备之间自动同步的技术机制。与本地存档不同，云存档通过网络将序列化后的存档文件存储在云端（如 Steam Cloud、Apple Game Center、Google Play Games 等平台提供的存储服务），使玩家在手机、PC 或主机之间切换时无需手动转移存档。

云存档技术随着移动游戏的普及而快速成熟。Steam 于 2008 年推出 Steam Cloud 功能，为 PC 游戏提供了最早的主流云存档方案，每款游戏默认获得 1 GB 的云端存储配额。此后，Google Play Games（2012 年）和 Apple iCloud（iOS 5，2011 年）相继提供面向移动端的云存档 API。这些基础设施的出现使得跨设备游戏体验成为商业标准需求。

云存档的核心挑战不在于上传和下载本身，而在于**冲突解决**（Conflict Resolution）：当玩家在多台设备上离线游戏后重新联网，两份存档都有更新，系统必须决定保留哪一份或如何合并。处理不当会导致玩家丢失数小时的游戏进度，因此冲突解决策略是云存档实现中最需要精心设计的部分。

---

## 核心原理

### 存档数据的序列化与元数据标记

云存档的第一步是在本地存档系统的基础上，为每份存档附加**时间戳（Timestamp）**和**设备标识符（Device ID）**。时间戳通常使用 UTC Unix 时间（64 位整数，精确到毫秒），而非设备本地时间，以避免时区差异导致的比较错误。一条典型的存档元数据结构如下：

```
SaveMetadata {
    slot_id: int,
    timestamp_utc_ms: int64,
    device_id: string,
    checksum: string,       // SHA-256 of save content
    play_time_seconds: int  // 累计游戏时长
}
```

除时间戳外，累计游戏时长（`play_time_seconds`）是另一个重要的比较维度，因为玩家可能调整了系统时间，但累计游戏时长通常更难伪造，可作为辅助判断依据。

### 冲突检测与解决策略

冲突发生在"本地存档版本 ≠ 云端存档版本"且两者都比上次同步时间更新的情况下。常见的解决策略有三种：

**1. 最新时间戳优先（Last-Write-Wins, LWW）**
直接比较两份存档的 `timestamp_utc_ms`，保留较大值对应的存档。实现最简单，但在时钟不准确的设备上会出错，且无法处理"较旧时间戳但更多进度"的情况（例如玩家手机时钟慢了一天）。

**2. 玩家手动选择（User-Prompted Resolution）**
当检测到冲突时，向玩家展示两份存档的关键信息（时间、游戏时长、关卡进度），由玩家决定保留哪一份。这是《怪物猎人：世界》和多数 RPG 游戏采用的方案，因为对 RPG 玩家而言，一次错误覆盖的损失极大，应让玩家自主决策。

**3. 字段级合并（Field-Level Merge）**
对存档数据进行细粒度合并，例如成就解锁状态取两份存档的并集（`achievements = A.achievements ∪ B.achievements`），货币取较大值，主线进度取较新时间戳的值。这要求存档数据结构在设计时就标注每个字段的合并策略，实现成本最高但玩家体验最好，常见于《原神》等手游的跨平台设计中。

### 同步触发时机与带宽优化

云存档不应在每次游戏状态变化时都触发上传，而应在特定节点触发：**游戏正常退出时**、**进入主菜单时**、**每隔固定时间间隔（如 5 分钟）**。Steam Cloud 文档明确建议在 `OnApplicationQuit` 回调中触发最终同步，并在游戏启动时检查是否有更新的云端版本。

为减少带宽消耗，可只上传**差异数据（Delta）**而非完整存档文件。例如，若一个存档文件为 512 KB，而本次游戏只修改了任务状态（2 KB），则仅上传这 2 KB 的变更块，通过 JSON Patch（RFC 6902 标准）或自定义 diff 格式描述变更内容。

---

## 实际应用

**Unity 与 Google Play Games 插件集成**：在 Unity 中使用 Google Play Games Plugin for Unity（GPGS），调用 `PlayGamesPlatform.Instance.SavedGame.OpenWithManualConflictResolution()` 方法打开存档时，可传入冲突解决委托（delegate），在回调中访问 `ISavedGameMetadata` 的 `LastModifiedTimestamp` 属性比较两份存档。

**Steam Cloud 的自动同步配置**：开发者在 Steamworks 后台配置同步规则文件（`*.vdf`），指定需要同步的本地文件路径（如 `%USERPROFILE%/Saved Games/MyGame/*.sav`）和根路径。Steam 客户端在游戏启动前自动下拉云端最新版本，游戏退出后自动上传。开发者无需在游戏代码中编写任何上传逻辑，但也因此无法控制冲突解决行为——Steam 默认使用 LWW 策略。

**Epic Online Services（EOS）的 Player Data Storage**：EOS 提供 `EOS_PlayerDataStorage_WriteFile` 和 `EOS_PlayerDataStorage_ReadFile` API，支持最大 64 MB 的单文件存储，并通过 MD5 校验和检测文件完整性。EOS 不内置冲突解决逻辑，要求开发者自行实现，适合需要完全控制同步行为的自研引擎项目。

---

## 常见误区

**误区一：用本地时间戳作为冲突判断依据**
部分开发者直接使用 `DateTime.Now` 生成时间戳，但玩家设备的系统时钟可能不准确，或玩家为了"作弊"故意调整时间。正确做法是在服务器端记录接收时间戳，或使用 NTP 校准后的 UTC 时间，并将其与本地记录的累计游戏时长（服务端也应保存一份）交叉验证。

**误区二：云存档等同于实时同步**
云存档是**异步批量同步**，不是实时状态同步（那是网络多人游戏的职责）。试图用云存档实现"两台设备同时游玩同一存档"会导致频繁冲突且无法解决，因为存档文件的设计粒度是完整游戏状态快照，而非操作事件流。

**误区三：冲突解决只需保留最新版本即可**
LWW 策略在"玩家用老旧手机离线游玩了 20 小时后联网"的场景中，可能因为手机时钟落后导致 20 小时进度全部丢失。应结合 `play_time_seconds` 字段，当时间戳差异超过合理阈值（如 24 小时），优先以游戏时长较长的存档为准，或弹出提示让玩家选择。

---

## 知识关联

云存档直接依赖**存档系统**的序列化实现：存档系统负责将游戏对象状态序列化为字节流（JSON、二进制 Protobuf 等格式），云存档则在此基础上添加元数据标记、网络传输与冲突解决层。若存档系统设计时没有将存档数据与设备状态（如绝对路径、硬件 ID）耦合，则云存档的跨设备兼容性会好得多——这是反序列化时需要特别注意的兼容性问题，例如 `AssetReference` 路径在不同平台上可能不同。

在引擎架构层面，云存档的冲突解决逻辑通常在**存档管理器（Save Manager）**组件中独立封装，与游戏逻辑层解耦，使得更换底层云平台（如从 Steam Cloud 迁移到 EOS）时不影响游戏代码。开发者可以将冲突解决策略抽象为接口（`IConflictResolver`），针对不同游戏类型（休闲游戏用 LWW，RPG 用手动选择）注入不同实现。
