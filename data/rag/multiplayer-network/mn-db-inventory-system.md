---
id: "mn-db-inventory-system"
concept: "背包/库存系统"
domain: "multiplayer-network"
subdomain: "database-design"
subdomain_name: "数据库设计"
difficulty: 3
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.379
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 背包/库存系统

## 概述

背包/库存系统（Inventory System）是网络多人游戏中用于持久化存储玩家虚拟物品的数据库模型。它不只是一个"物品列表"，而是需要处理物品堆叠（Stacking）、唯一属性（如耐久度、附魔）、格子限制、跨角色交易等复杂业务逻辑的完整数据层设计。

该概念随着 1997 年《网络创世纪》（Ultima Online）的商业化普及而成为 MMO 标配设计。早期实现往往将整个背包序列化为一个 BLOB 字段存储在玩家表中，但随着交易所、拍卖行、仓库等系统的出现，这种做法暴露了无法支持跨玩家查询、无法防止重复物品（Item Duplication）等严重缺陷。

背包系统设计质量直接影响三件事：数据库写入热点（高频玩家每秒可能产生 5-20 次物品变动）、物品复制漏洞的防御能力，以及拍卖行等经济系统的查询性能。错误的表结构设计会导致这三个问题同时恶化。

## 核心原理

### 物品定义与实例的分离（Template-Instance Pattern）

背包系统最基本的架构决策是将**物品模板（Item Template）**与**物品实例（Item Instance）**分开存储。物品模板表（`item_templates`）存储所有"铁剑"共享的属性：基础攻击力、重量、图标 ID 等，由游戏策划维护，行数通常在数千到数万级别。物品实例表（`item_instances`）则存储某个玩家手中那把铁剑的当前耐久度（`durability`）、强化等级（`enhance_level`）、绑定状态（`bind_status`）等运行时属性。

```sql
CREATE TABLE item_instances (
    instance_id  BIGINT PRIMARY KEY AUTO_INCREMENT,
    template_id  INT NOT NULL REFERENCES item_templates(id),
    owner_id     BIGINT NOT NULL REFERENCES players(player_id),
    slot_index   SMALLINT,          -- NULL 表示在仓库或交易中
    quantity     INT NOT NULL DEFAULT 1,
    durability   SMALLINT,
    extra_attrs  JSON,              -- 随机词缀、附魔等扩展字段
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

`extra_attrs` 使用 JSON 列而非额外的 EAV（Entity-Attribute-Value）表，可以避免多表 JOIN 的开销，适合读多写少的词缀场景。

### 堆叠机制与原子性保证

可堆叠物品（如药水、箭矢）不应为每一个药水创建一行记录，而是用 `quantity` 字段表示数量。但堆叠操作涉及**原子性**问题：两个客户端同时消耗同一堆药水时，若不加锁，可能出现 `quantity` 扣减竞争。正确做法是使用带条件的 UPDATE：

```sql
UPDATE item_instances
SET quantity = quantity - :consume_amount
WHERE instance_id = :id
  AND owner_id = :player_id
  AND quantity >= :consume_amount;
```

通过检查 `affected_rows == 1` 来判断操作是否成功，这是一种无锁的乐观扣减策略。对于不可堆叠的唯一物品（如装备），`quantity` 恒为 1，`instance_id` 本身即唯一标识。

### 格子索引与背包布局模型

格子式背包（如《暗黑破坏神》风格的 2D 格子）需要 `slot_x` + `slot_y` 两列，而线性列表式背包（如《魔兽世界》）只需 `slot_index` 一列。`slot_index` 的取值范围取决于背包格子数上限，通常 0–127 表示主背包，128–255 表示扩展背包页，256+ 表示仓库。

`(owner_id, slot_index)` 需要设置唯一约束，以防止服务器 Bug 导致两件物品占据同一格子（此类 Bug 曾在 2004 年《传奇》服务端中引发大规模物品复制事件）。

### 交易与物品转移的事务设计

玩家间交易必须在单个数据库事务中完成 `owner_id` 的双向变更，否则任何中途失败都会造成物品凭空消失或复制：

```sql
BEGIN;
  UPDATE item_instances SET owner_id = :buyer_id,  slot_index = :buyer_slot
    WHERE instance_id = :item_id AND owner_id = :seller_id;
  UPDATE players SET gold = gold - :price WHERE player_id = :buyer_id AND gold >= :price;
  UPDATE players SET gold = gold + :price WHERE player_id = :seller_id;
COMMIT;
```

拍卖行系统通常引入 `item_escrow` 暂存表，将物品从卖家背包转移至托管状态，成交后再转移给买家，避免在线玩家背包的直接锁定。

## 实际应用

**《魔兽世界》的实现参考**：WoW 使用每个角色独立的物品表，`bag_slot` 和 `slot` 双列定位，其中 `bag_slot = 255` 表示装备栏，这种设计被大量后续 MMO 模仿。

**手游背包设计差异**：手机 MMO（如《原神》）通常不设格子限制，改用分类上限（武器最多 2000 件），数据库层面移除 `slot_index`，增加 `category_type` 列，并对 `(owner_id, category_type)` 建立复合索引以支持分类筛选查询。

**物品回收与软删除**：物品丢弃不应直接 DELETE，而应设置 `deleted_at` 时间戳实现软删除。这为 GM 工具提供了物品找回能力，同时也是审计物品流通（用于反外挂分析）的数据基础。

## 常见误区

**误区一：将背包数据存为 JSON BLOB 在玩家表中**。这在玩家数达到数百万时会导致背包字段成为热点大字段，每次物品变动都需要读取、修改、写回整个 JSON，无法对单件物品加行锁，也无法支持"查询所有持有某物品的玩家"这类运营需求。

**误区二：可堆叠物品也使用 instance_id 唯一区分每一个**。为1000支箭矢创建1000行记录不仅浪费存储，还会让背包查询的结果集膨胀，更重要的是它让"消耗10支箭"从一次 UPDATE 变成需要选择并删除10行记录，产生不必要的锁竞争。

**误区三：忽略 `(owner_id, slot_index)` 唯一约束**。仅在应用层检查格子是否为空，在高并发下（如网络重传导致同一请求被处理两次）仍会出现格子冲突，正确做法是依赖数据库唯一约束作为最后一道防线，通过捕获 Duplicate Key 异常来处理冲突。

## 知识关联

本系统建立在**玩家数据模型**的基础上：`item_instances.owner_id` 直接外键关联玩家表的 `player_id`，背包的读写权限验证（防止玩家操作他人物品）也依赖玩家表中的会话认证字段。理解玩家数据模型中的 `player_id` 生成策略（自增 vs UUID）对背包表的分库分表方案有直接影响——若按 `player_id` 分片，则同一玩家的所有物品实例天然落在同一分片，避免跨分片事务。

背包系统向上支撑了**拍卖行/交易所**、**邮件附件**、**公会仓库**等更复杂的物品流转系统，这些系统本质上都是对 `owner_id` 的转移逻辑加上各自的业务约束，其事务设计模式与本文的交易模型保持一致。