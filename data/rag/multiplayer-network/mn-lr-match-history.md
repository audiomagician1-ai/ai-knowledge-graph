---
id: "mn-lr-match-history"
concept: "战绩记录"
domain: "multiplayer-network"
subdomain: "leaderboard"
subdomain_name: "排行榜与统计"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 100.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 战绩记录

## 概述

战绩记录（Match History）是网络多人游戏中对每位玩家每一场对局结果的持久化存档系统，具体储存内容包括：胜负结果、击杀/死亡/助攻数据（KDA）、伤害输出、游戏时长、所使用的角色或装备配置，以及对局发生的精确UTC时间戳。与"玩家统计"中汇总的累计数值不同，战绩记录保留的是**每一场独立对局的原始快照**，允许玩家和系统回溯任意历史场次的完整数据，而不仅仅是均值或总量。

这一系统的雏形最早出现在1990年代的局域网对战游戏中，彼时仅以本地文本日志的形式存储在客户端，数据生命周期受限于玩家的本地磁盘。随着宽带互联网普及，《魔兽世界》（2004年）和《英雄联盟》（2009年）等标志性游戏将战绩记录全面迁移至云端服务器，实现跨设备、跨地区查询。如今，Riot Games曾公开披露其战绩数据库每日新增写入量超过**1亿条**记录，单条战绩记录的数据体积因游戏类型不同，通常在2 KB到200 KB之间（MOBA类游戏因角色技能数据复杂，单条记录约50–120 KB；射击类游戏因数据结构简单，通常仅需2–10 KB）。

战绩记录的核心价值在于为玩家提供可追溯的自我评估依据，同时为排行榜的分段计算、段位升降判定和匹配系统提供原始输入数据。一名玩家的最近20场胜率往往比其终身胜率更能反映当前实力，这种"近期表现窗口（Recency Window）"就依赖战绩记录的逐场存档才能实现。

---

## 核心原理

### 数据结构与存储方案

每一条战绩记录在数据库中对应一个"对局实体"（Match Entity），至少包含以下字段：

```sql
CREATE TABLE match_records (
    match_id       BIGINT PRIMARY KEY,          -- 全局唯一对局ID，64位整型
    player_id      BIGINT NOT NULL,             -- 玩家唯一标识
    champion_id    INT,                         -- 角色ID（MOBA类游戏）
    role           VARCHAR(20),                 -- 职位：TOP/JG/MID/BOT/SUP
    result         ENUM('WIN','LOSS','DRAW'),   -- 对局结果
    duration_sec   INT NOT NULL,                -- 对局时长（秒）
    stats_json     JSONB,                       -- KDA、伤害、视野等详细数值
    created_at     TIMESTAMPTZ NOT NULL,        -- UTC时间戳
    hmac_sig       CHAR(64)                     -- HMAC-SHA256防篡改签名
);

-- 核心查询索引：按玩家ID + 时间倒序
CREATE INDEX idx_player_time ON match_records (player_id, created_at DESC);
```

在存储架构上，热数据（近90天战绩）存储于关系型数据库（如PostgreSQL 14+）并建立玩家ID的B树索引，冷数据（超过1年的历史记录）则归档至对象存储（如Amazon S3），单条记录以Parquet格式压缩后存储成本可降低至原始JSON的**1/6至1/10**。冷热分层的判断阈值通常基于访问频率：90天以上的战绩查询量仅占全部请求的不足3%，因此将其归档能显著降低数据库I/O压力。

### 查询与游标分页机制

玩家查看战绩列表时，系统不会一次性返回数千场历史，而是使用**游标分页（Cursor-based Pagination）**。其原理如下：以上一次请求中最后一条记录的 `created_at` 时间戳（或 `match_id`）作为游标，下一页请求携带此游标，服务端执行以下查询：

```sql
SELECT * FROM match_records
WHERE player_id = :pid
  AND created_at < :cursor_timestamp   -- 游标条件替代 OFFSET
ORDER BY created_at DESC
LIMIT 20;
```

相比传统偏移分页（`OFFSET 1000 LIMIT 20`），游标分页在数据量达到10万条以上时查询耗时从约800ms降低至稳定的**5–20ms**，因为它完全避免了数据库扫描并跳过前N行的全表遍历。典型的单页返回数量为10至20条对局，《英雄联盟》的API默认每页返回20条，最大允许请求100条。

### 数据完整性与防篡改机制

战绩数据由权威服务器（Authoritative Server）在对局结束时直接写入数据库，客户端对战绩表没有任何写入权限。每条记录在写入时，服务端计算其HMAC-SHA256签名：

$$\text{sig} = \text{HMAC-SHA256}(K_{\text{server}},\ \text{match\_id} \| \text{player\_id} \| \text{result} \| \text{duration\_sec})$$

其中 $K_{\text{server}}$ 为仅服务端持有的256位密钥，$\|$ 表示字节串拼接。当客户端请求战绩时，服务端可重新计算签名并与存储值比对，若不一致则拒绝该记录并触发反作弊告警。这种方案被 Valve 的 Steam 平台和 Riot Games 的后端架构中广泛应用。

### 统计聚合：从单条记录到汇总指标

战绩记录存储原始数据，而"近30天KDA均值"、"某英雄胜率"等统计指标则通过**批量聚合任务（Batch Aggregation Job）**计算后写入专用的统计快照表（Stats Snapshot Table）。例如，计算玩家近N场某英雄的胜率公式为：

$$\text{WinRate}(p, c, N) = \frac{\sum_{i=1}^{N} \mathbf{1}[\text{result}_i = \text{WIN}]}{N} \times 100\%$$

其中 $p$ 为玩家，$c$ 为角色，$N$ 为统计窗口场次（通常取20、50或100）。聚合任务的典型刷新周期为每小时一次（面向排行榜）或每日一次（面向赛季统计报告）。分层存储设计确保高频查询的统计页面无需实时扫描全量战绩，读取延迟从秒级降至毫秒级。

---

## 关键公式与算法

### 近期表现权重衰减

在某些竞技游戏中，战绩系统不仅存储原始结果，还对近期场次施加**指数衰减权重**，使最新场次对当前表现评分的影响更大。加权胜率计算如下：

$$\text{WeightedWR}(p) = \frac{\sum_{i=1}^{N} w_i \cdot \mathbf{1}[\text{result}_i = \text{WIN}]}{\sum_{i=1}^{N} w_i}, \quad w_i = \lambda^{N-i}$$

其中 $\lambda \in (0, 1)$ 为衰减因子（典型值为 0.95），$i=N$ 为最新场次（权重最高），$i=1$ 为最早场次（权重最低）。例如当 $\lambda = 0.95$、$N = 20$ 时，最新场次权重为 $0.95^0 = 1.0$，第20场最旧记录权重仅为 $0.95^{19} \approx 0.377$，近期5场的权重占总权重的约**22%**。

### 对局ID生成：雪花算法（Snowflake）

为保证全局唯一且时序可排序，`match_id` 通常采用Twitter于2010年提出的**Snowflake算法**生成64位ID，结构如下：

```
| 1位符号位 | 41位毫秒时间戳 | 10位机器ID | 12位序列号 |
```

这使得 `match_id` 天然具有时间单调递增性，可作为排序键直接替代 `created_at` 进行游标分页，每台服务器每毫秒最多可生成 $2^{12} = 4096$ 个唯一ID，在 Riot Games 规模的并发写入场景下足以应对峰值流量。

---

## 实际应用案例

### 《英雄联盟》的战绩API（Riot Games）

Riot Games 通过 [Riot Developer Portal](https://developer.riotgames.com/) 开放了战绩查询 REST API。查询某玩家最近20场对局的典型调用流程为：

1. 通过 `/lol/summoner/v4/summoners/by-name/{summonerName}` 获取 `puuid`（玩家全局唯一ID）。
2. 通过 `/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20` 获取最近20个 `match_id` 列表。
3. 对每个 `match_id` 调用 `/lol/match/v5/matches/{matchId}` 获取完整对局详情。

单条完整对局JSON响应体约**80–150 KB**，包含10名玩家的全量数据。正因如此，第三方战绩查询网站（如 op.gg、u.gg）需要在自身服务器缓存战绩数据，而非每次直接调用 Riot API，以规避频率限制（开发者密钥限制为每秒20次请求）。

### 《王者荣耀》的战绩存储优化

腾讯《王者荣耀》日活跃用户峰值超过1亿，战绩写入峰值约为每秒**数十万条**。为应对如此规模，其后端采用写入队列（Kafka）缓冲后异步落库的方案：游戏服务器将战绩消息发送至 Kafka Topic，消费端批量写入分片MySQL（或 TiDB 分布式数据库），每个分片按 `player_id % 1024` 水平切分。这种架构将数据库瞬时写入压力削峰至均匀分布，避免对局结束潮（如整点前后）引发的写入尖峰导致数据库过载。

---

## 常见误区

**误区1：战绩记录与玩家统计是同一张表。**
实际上两者职责分离：战绩记录表（Match Records）存储每场对局的**原始明细**，玩家统计表（Player Stats Snapshot）存储**预计算的聚合结果**。若将两者合并，每次查询统计数据时都需全表扫描战绩明细，在百万场级别数据量下响应时间将劣化至秒级，无法支撑实时展示页面。

**误区2：游标分页的游标必须是自增整数ID。**
游标可以是任何具有严格全序关系的字段，包括 `TIMESTAMPTZ` 时间戳、Snowflake ID，甚至是 `(created_at, match_id)` 的复合游标。当同一毫秒内存在多条记录时，单纯以时间戳为游标会导致**游标碰撞（Cursor Collision）**，复合游标 `(created_at DESC, match_id DESC)` 可完全消除此问题。

**误区3：战绩数据一旦写入就不需要更新。**
实际上存在赛后数据订正场景：反作弊系统可能在对局结束数小时后判定某玩家使用了外挂，此时需要将该场战绩标记为无效（`is_void = TRUE`）并触发受影响玩家统计数据的重新计算。《英雄联盟》的"游戏重置"机制正是此类订正流程的具体实现。

**误区4：删除老战绩可以节省存储成本且无副作用。**
战绩记录是生成精彩回放（Highlight Replay）、反作弊追溯、赛季结算报告的基础数据源。贸然删除超过一定年限的记录将导致这些下游功能失效。正确做法是**冷归档**而非删除，将超龄数据迁移至低成本对象存储，在极少数被查询时按需恢复。

---

## 知识关联

### 与上游概念"玩家统计"的关系

玩家统计中的累计KDA、总胜场数、赛季积分等聚合指标，其数据来源正是战绩记录表的批量聚合运算结果。战绩记录是**原始数据层**，玩家统计是**聚合展示层**，两者构成典型的OLTP（在线事务处理）与OLAP（在线分析处理）分层架构——参见《数据密集型应用系统设计》[Kleppmann, 2017] 第3章对列存储与行存储分层设计的论述。

### 与下游概念"精彩回放"的关系

战绩记