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

时序数据库（Time Series Database，TSDB）是专门针对时间序列数据设计的数据库系统，其核心存储单元是带有时间戳的观测值序列，例如传感器每秒上报的温度读数、服务器每5秒采集的CPU利用率、或股票市场每毫秒更新的报价。与关系型数据库的行列模型不同，时序数据库将时间轴视为第一公民（first-class citizen），数据按时间顺序连续写入，查询模式也以时间范围切片为主。

时序数据库的专项发展始于2011年前后。OpenTSDB（2011年发布，基于HBase）是最早广泛使用的开源时序数据库之一，随后InfluxDB于2013年由InfluxData公司推出，采用纯Go语言编写，无外部依赖。2017年，TimescaleDB以PostgreSQL扩展的形式出现，将时序能力嫁接到成熟的关系型引擎之上。这一演进路线反映了时序数据在物联网、DevOps监控、金融量化三大场景的爆炸式增长需求。

时序数据库的必要性体现在性能数字上：针对高基数（high cardinality）时序数据，InfluxDB的写入吞吐量可达每秒数百万数据点，而将同样的时间戳数据写入MySQL后执行范围聚合查询，性能差距可达10至100倍。这种差距源于时序数据库针对追加写入、列式压缩和时间窗口聚合所做的专项优化。

---

## 核心原理

### 数据模型：度量、标签与字段

InfluxDB的数据模型由四个层级构成：**measurement**（相当于表名，例如 `cpu_usage`）、**tag set**（索引化的元数据键值对，例如 `host=web01,region=us-east`）、**field set**（实际观测值，例如 `value=72.3`）、**timestamp**（纳秒精度的Unix时间戳）。一条完整的Line Protocol写入语句格式为：

```
cpu_usage,host=web01,region=us-east value=72.3 1609459200000000000
```

标签（tag）与字段（field）的区分至关重要：标签自动建立倒排索引，支持高效过滤，但其唯一组合数量（即基数）过大会导致内存占用急剧上升——这被称为"高基数问题"（high cardinality problem）。将用户ID或会话ID直接作为标签是常见的设计失误，因为百万级用户ID会创建百万条索引条目。

TimescaleDB采用不同路径：数据存储为标准PostgreSQL表，时间列加上普通列，但通过`create_hypertable()`函数将物理表自动分割为**chunk**（时间分片）。默认chunk间隔为7天，每个chunk是一个独立的PostgreSQL子表，可分别压缩、独立失效（expire）。

### 压缩与存储引擎

InfluxDB 1.x使用自研的**TSM（Time-Structured Merge Tree）**存储引擎，其设计借鉴了LSM Tree但针对时序场景做了改造。TSM引擎的压缩算法对不同数据类型分别处理：时间戳列使用Delta编码后再进行Simple8b压缩，浮点数列使用XOR差分编码（Gorilla算法，来自Facebook 2015年的论文），布尔值列使用位打包（bit-packing）。实际压缩率通常在10:1至20:1之间，即1GB原始数据压缩后占用50~100MB磁盘空间。

TimescaleDB的压缩（需PostgreSQL 12+）通过`compress_chunk()`或自动压缩策略实现，将列数据转为`ARRAY`类型存储，同一列的连续值存在一起，与行式存储相比可获得约20倍的压缩比提升。

### 数据保留策略与降采样

时序数据库原生支持**Retention Policy（保留策略）**。InfluxDB中可对同一measurement设置多个保留策略，例如：原始1秒精度数据保留30天，1分钟聚合数据保留1年，1小时聚合数据永久保留。配合**Continuous Query（连续查询）**，系统自动将细粒度数据降采样（downsampling）写入粗粒度保留策略，SQL等效写法为：

```sql
-- TimescaleDB中的连续聚合
CREATE MATERIALIZED VIEW cpu_1min
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 minute', time) AS bucket,
       host, AVG(value) AS avg_value
FROM cpu_usage GROUP BY bucket, host;
```

InfluxDB 2.x则将Continuous Query替换为**Task**（基于Flux脚本语言）执行周期性降采样。

---

## 实际应用

**AI模型监控**：在MLOps流水线中，模型推理延迟、请求吞吐量、特征漂移指标（如PSI值）每分钟上报至InfluxDB。Grafana通过InfluxQL或Flux语言查询90分位延迟：`SELECT percentile("latency_ms", 90) FROM "inference" WHERE time > now() - 24h GROUP BY time(5m), "model_version"`。

**IoT传感器数据处理**：工厂部署的振动传感器以1000Hz采样率持续写入，TimescaleDB利用`time_bucket_gapfill()`函数填充因网络抖动造成的数据空洞，避免在异常检测模型的输入特征中出现NaN值。

**金融高频数据存储**：加密货币交易所使用InfluxDB存储每笔tick数据（bid/ask/volume），利用TSM引擎的列压缩将数十亿条记录的存储成本控制在TB级别以内，查询特定交易对过去30分钟的VWAP（成交量加权平均价格）响应时间在毫秒级。

---

## 常见误区

**误区一：把时序数据库当作通用数据库使用**。时序数据库对UPDATE和DELETE操作支持极差——InfluxDB的数据模型中，同一时间戳+tag组合的重复写入会覆盖旧值，但随机更新历史数据在性能上不可接受（TSM引擎需要重写整个chunk）。若业务需要频繁修改历史记录（如订单状态更新），应使用关系型数据库而非时序数据库。

**误区二：以为标签越多越好，滥用高基数标签**。InfluxDB官方文档明确警告：当tag的唯一值组合（series cardinality）超过1000万时，内存索引可能消耗数GB RAM并导致查询变慢。正确做法是将高基数属性（如UUID）放入field而非tag，仅将低基数的分类属性（如地域、设备类型）作为tag。

**误区三：混淆InfluxDB 1.x与2.x的查询语言**。InfluxDB 1.x使用**InfluxQL**（类SQL语法），而2.x引入了全新的**Flux**函数式语言，两者不兼容。Flux支持join、map/reduce等复杂操作，但学习曲线陡峭；InfluxDB 3.x（2023年推出）又转向支持标准SQL和Apache Arrow Flight协议，迁移路径需谨慎规划。

---

## 知识关联

**前置概念衔接**：理解时序数据库需要已掌握关系型数据库中的索引原理——时序数据库的标签索引本质上是倒排索引（类似全文检索），而TimescaleDB的hypertable分区逻辑是关系型数据库分区表概念的直接延伸。NoSQL中的LSM Tree写入模型（如Cassandra所用）与InfluxDB的TSM引擎共享相同的追加优先写入哲学，理解LSM Tree的Level Compaction有助于理解TSM的文件合并机制。

**横向对比**：Prometheus是另一个重要的时序系统，采用拉取（pull）模型收集指标，本地存储使用自研的TSDB格式（chunk大小固定为两小时）；它与InfluxDB的推送（push）模型形成对比，在Kubernetes监控生态中占据主导地位。ClickHouse虽非专用时序数据库，但其列式存储和向量化执行在时序分析查询上也有极强竞争力，常被用于替代方案评估。