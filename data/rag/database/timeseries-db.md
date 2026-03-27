---
id: "timeseries-db"
concept: "时序数据库"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 4
is_milestone: false
tags: ["timeseries", "influxdb", "iot"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 时序数据库

## 概述

时序数据库（Time Series Database，TSDB）是专门为存储和查询按时间戳索引的连续数据点而设计的数据库系统。与通用关系型数据库不同，时序数据库假设每条记录都附带一个时间戳，且数据写入模式几乎全为追加（append-only），极少发生更新或删除操作。这种设计使其在处理传感器读数、服务器指标、金融行情等场景时，写入吞吐量可比 PostgreSQL 高出 10-100 倍。

时序数据库的起源可追溯至 1999 年广泛部署的 RRDtool（Round Robin Database），它专为网络监控设计，使用固定大小的循环缓冲区存储历史数据。2013 年 InfluxDB 的发布标志着现代时序数据库时代的开始，随后 2017 年 TimescaleDB 以 PostgreSQL 扩展的形式出现，将 SQL 能力引入时序场景。如今时序数据已占全球生产数据总量约 30%，驱动了专用 TSDB 的快速普及。

在 AI 工程领域，时序数据库承担着模型训练数据采集、在线特征计算和模型性能监控三类核心任务。例如，实时推荐系统需要以毫秒级延迟读取用户近 1 小时内的行为序列，而通用数据库在此场景下的范围查询代价过高。时序数据库通过时间分区和压缩算法将这类查询的响应时间压缩至个位数毫秒级。

## 核心原理

### 时间分区与数据分片

时序数据库的物理存储以时间范围为单位划分为多个"分片"（Shard）或"块"（Chunk）。InfluxDB 默认按 7 天创建一个 Shard，TimescaleDB 默认将数据切割为 7 天一个 Chunk。当查询仅涉及最近 24 小时的数据时，数据库引擎可直接跳过所有历史分片，只扫描当前活跃分片，使 I/O 量从全表扫描的 O(N) 降低到 O(1)——与数据总量无关。过期数据的删除也变为直接丢弃整个分片目录，避免了逐行删除的开销。

### 列式压缩与专用编码

时序数据的相邻值往往高度相关，因此时序数据库采用专用压缩算法而非通用的 gzip。InfluxDB 对浮点数使用 Facebook Gorilla 算法（2015 年论文提出），利用相邻时间戳的 XOR 差值编码，可将 64 位双精度浮点序列压缩到平均 1.37 字节/点，压缩率超过 97%。对时间戳本身，则使用 Delta-of-Delta 编码：先记录相邻时间戳的差值 Δt，再记录 Δt 之间的差值 δ(Δt)，对于等间隔采样数据，δ(Δt) 全为 0，可压缩至接近 1 bit/点。TimescaleDB 在 PostgreSQL 层面叠加了 columnar compression，对数值列可达 20x 压缩比。

### 数据模型：Measurement、Tag 与 Field

InfluxDB 的数据模型由三层构成：**Measurement**（相当于表名，如 `cpu_usage`）、**Tag**（带索引的元数据键值对，如 `host=server01`）和 **Field**（实际数值，如 `value=72.5`）。Tag 值被存储在内存倒排索引中，支持 O(log N) 的过滤查询；Field 值仅按时间顺序存储，不建立索引。这一设计决定了一条写入语句的格式：

```
cpu_usage,host=server01,region=us-east value=72.5 1609459200000000000
```

其中末尾数字为 Unix 纳秒时间戳。Tag 数量过多（称为"高基数问题"，即 tag cardinality 超过 10^6）会导致内存索引膨胀，是 InfluxDB 生产环境最常见的性能陷阱。

### 连续查询与降采样

时序数据库内置数据生命周期管理功能。InfluxDB 的 **Retention Policy** 可自动删除超过指定时间（如 30 天）的原始数据，配合 **Continuous Query** 可在删除前将原始 10 秒采样自动聚合为 1 分钟均值并写入低精度表。TimescaleDB 对应功能为 **Continuous Aggregates**，用标准 SQL 语法定义：`CREATE MATERIALIZED VIEW … WITH (timescaledb.continuous)`。这一机制使存储成本随时间呈阶梯状下降，而非线性增长。

## 实际应用

**AI 模型监控**：MLflow 和 Prometheus 均使用时序数据库记录模型推理延迟、准确率漂移和 GPU 利用率。Prometheus 自带基于 LevelDB 的本地 TSDB，以 2 小时为单位将内存数据刷写到磁盘块，并通过 PromQL 查询语言支持如 `rate(http_requests_total[5m])` 这样的滑动窗口速率计算。

**金融高频数据存储**：TimescaleDB 被用于存储股票逐笔成交数据，利用其继承自 PostgreSQL 的 `time_bucket('1 minute', time)` 函数将 tick 数据实时聚合为 K 线，同时支持与账户表、标的信息表做 SQL JOIN，这是纯 NoSQL 时序数据库难以做到的。

**IoT 传感器管道**：工厂部署的温湿度传感器每秒产生数千个读数，通过 MQTT 协议推送至 InfluxDB，配合 Flux 查询语言的 `movingAverage()` 函数做异常检测，将滑动平均偏差超过 3σ 的数据点标记为异常并触发告警。

## 常见误区

**误区一：时序数据库可以替代关系型数据库做业务数据存储。** 时序数据库针对追加写入和时间范围查询优化，其数据模型不支持多表 JOIN（InfluxDB 原生不支持 JOIN，TimescaleDB 虽支持但性能不如 PostgreSQL 纯关系查询）。用 InfluxDB 存储用户订单、商品库存等频繁更新的业务数据会导致大量"墓碑标记"（tombstone）堆积，严重影响查询性能。

**误区二：Tag 和 Field 可以随意互换。** 很多初学者将需要过滤的字段（如设备 ID）存为 Field 而非 Tag，导致查询 `WHERE device_id = 'abc'` 变成全量扫描而非索引查找，性能下降数十倍。判断标准很简单：**需要在 WHERE 子句中作为过滤条件的维度必须存为 Tag**，仅用于数值计算的存为 Field。

**误区三：时序数据库可以高效处理任意粒度的历史回溯查询。** 未配置降采样策略时，查询跨度为 1 年的原始 1 秒采样数据（约 3100 万行）仍然很慢。时序数据库的查询效率优势仅在于"近期窗口的快速读取"，历史数据必须依靠降采样策略预先聚合，否则与全表扫描无异。

## 知识关联

从**数据库基本概念**过渡到时序数据库时，需要注意时序数据库放弃了传统 ACID 事务中的多行原子性保证——InfluxDB 的写入单位是单行，不支持跨行事务，这是其高写入吞吐量的代价。从**NoSQL 概述**的角度看，时序数据库属于 NoSQL 的一个垂直细分，类似文档数据库针对 JSON 优化、图数据库针对关系遍历优化，时序数据库的一切设计（分区策略、压缩算法、数据模型）都服务于"按时间顺序高速写入、按时间范围高速读取"这一单一目标。理解 LSM-Tree（Log-Structured Merge-Tree）存储引擎有助于进一步解释为何时序数据库能实现高写入吞吐：InfluxDB 的存储引擎 TSM（Time-Structured Merge Tree）正是从 LSM-Tree 演变而来，专门针对时间递增写入模式做了优化，消除了 LSM-Tree 在乱序写入时的写放大问题。