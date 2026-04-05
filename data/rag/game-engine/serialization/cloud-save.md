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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 云存档

## 概述

云存档（Cloud Save）是指将游戏进度数据序列化后上传至远程服务器，使玩家能够在不同设备之间无缝继续游戏的技术体系。与本地存档不同，云存档需要解决网络传输、版本一致性和多设备写入冲突三个独立问题。Steam、PlayStation Network、Xbox Live、Apple Game Center等平台均提供专有的云存档服务，但底层面临的工程挑战高度相似。

云存档技术在2000年代中期随着宽带普及而快速发展。Valve在2008年随Steam更新引入Steam Cloud功能，允许开发者在游戏目录中指定需要同步的文件路径。这一设计确立了"文件级别同步"作为早期云存档的主流模式，后续逐渐演进为基于键值对（Key-Value）或结构化JSON的数据级同步，以减少无谓的全量上传带宽消耗。

云存档的重要性在于它打破了"存档绑定设备"的传统限制。《原神》玩家可以在PC端和移动端之间切换，《Minecraft》基岩版通过Xbox Live同步进度，《动物森友会》通过Nintendo Switch Online实现云备份。对游戏引擎开发者来说，实现云存档意味着序列化层必须输出确定性（deterministic）的字节流，以便服务器能够对两个版本进行比较和合并。

## 核心原理

### 序列化数据的上传时机

云存档系统通常在以下三个触发点执行上传：游戏退出时（exit hook）、达到里程碑事件时（如通关某章节）以及定时轮询（通常间隔300秒）。选择不当的上传频率会产生两类问题：频率过高导致服务器压力过大，频率过低导致意外断电后进度丢失。Unity的游戏服务SDK（Unity Gaming Services - Cloud Save）采用"脏标记"（dirty flag）机制，只有当本地数据发生变化后，下一次轮询才真正触发网络请求，否则跳过本次上传。

### 冲突检测与解决策略

当同一账号从两台设备分别写入数据后，服务器收到两份时间戳不同、内容不同的存档，此时需要冲突解决（conflict resolution）。常见策略有三种：

**最后写入胜出（Last Write Wins，LWW）**：以服务器收到请求的时间戳为准，丢弃较早的版本。实现简单但风险高——玩家在飞机上用离线模式游玩5小时后联网，这5小时进度可能被一台只同步了1小时前数据的旧设备覆盖。

**语义合并（Semantic Merge）**：针对游戏数据的业务逻辑进行字段级合并。例如货币字段取两者最大值，已解锁成就取两个集合的并集，游戏时长取两者之和。《炉石传说》的客户端与Battle.net服务器之间使用的就是类似的字段级合并策略，确保卡牌收藏不会因为多设备登录而丢失。

**用户手动选择**：当自动策略无法安全合并时，弹出UI让玩家选择保留哪个存档版本。多数单机RPG游戏倾向于此策略，因为剧情进度通常无法无损合并。

### 数据版本号与迁移

每份云存档应附带schema版本号（例如 `save_version: 3`）。当游戏更新后，旧版存档结构可能缺少新字段或字段含义发生变化，序列化层需要在反序列化时执行迁移（migration）。典型做法是维护一个迁移函数链：`MigrateV1ToV2()` → `MigrateV2ToV3()`，每次反序列化时从当前版本号开始依次执行到最新版本。若服务器存储的是 `save_version: 1` 而客户端已是版本3，则需要连续执行两次迁移，迁移完成后立即重新上传，将服务器端更新为版本3。

## 实际应用

**Unity Gaming Services Cloud Save** 提供的API以键值对为单位操作，单个key的value上限为5 KB，单个玩家的总存储上限为10 MB。开发者调用 `CloudSaveService.Instance.Data.Player.SaveAsync(dict)` 上传数据，调用 `LoadAsync(keys)` 拉取指定键的数据，网络延迟较低时完整读写往返通常在200毫秒以内。

**Epic Online Services（EOS）Player Data Storage** 则以文件为单位，支持最大400 KB的单文件，总容量限制为256 MB。EOS的冲突检测依赖MD5校验和，若本地文件的MD5与服务器记录的MD5不同，SDK会触发回调函数，由开发者自定义合并逻辑。

对于使用Godot引擎的开发者，云存档通常需要手动集成Firebase Firestore或自建REST接口，因为Godot原生不提供云存档模块。一种常见方案是将 `FileAccess` 输出的JSON字符串直接通过 `HTTPRequest` 节点POST到后端，以玩家的JWT token作为身份标识。

## 常见误区

**误区一：本地存档完全一致则无需上传**
部分开发者认为只要本地文件的哈希未变化就跳过同步，但忽略了一种情形：服务器端由于另一台设备的上传已更新，而本地尚未拉取最新版本。此时"本地未变化"并不代表两端一致，正确做法是在上传前先执行拉取（pull-before-push），或使用乐观锁（optimistic lock）——上传请求中携带本地最后一次成功拉取的版本号，服务器拒绝版本号不匹配的写入请求。

**误区二：时间戳可以可靠地区分新旧存档**
设备系统时间可能被玩家手动修改，或在不同时区导致显示混乱。云存档应使用服务器端时间戳（server-side timestamp）作为权威时间源，绝对不能信任客户端上报的本地时间作为冲突仲裁依据。Steam Cloud文档明确指出，文件同步以Steam服务器记录的上传时间为准，而非文件的本地修改时间（mtime）。

**误区三：加密存档就能防止玩家篡改云存档**
AES加密可以防止存档内容被读取，但并不能阻止玩家将一份旧的已加密存档文件重新上传以"回滚"进度（如刷取成就奖励后回滚）。真正的防篡改需要在服务器端验证业务逻辑的合法性，例如检查货币增量是否超过该会话的理论最大收益，而不仅仅依赖客户端序列化数据的加密。

## 知识关联

云存档建立在本地**存档系统**的序列化基础之上。本地存档系统负责将游戏状态转化为可持久化的字节表示；云存档则在此之上增加网络传输层和冲突解决层。如果本地存档的序列化格式不稳定（例如使用了不确定性的哈希表遍历顺序），云存档的差量比较就会失效，每次都退化为全量上传。

从数据结构角度，理解云存档的冲突解决模型有助于进一步学习**分布式系统中的CRDT（无冲突复制数据类型）**概念——云存档的语义合并策略（成就取并集、货币取最大值）本质上是特定业务场景下的手工CRDT实现。同时，云存档的schema版本迁移模式与数据库迁移（database migration）工程实践高度相通，掌握云存档迁移机制有助于理解后续更复杂的后端数据演进策略。