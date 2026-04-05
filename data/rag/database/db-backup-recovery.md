---
id: "db-backup-recovery"
concept: "数据库备份恢复"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 3
is_milestone: false
tags: ["backup", "wal", "recovery", "disaster-recovery"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 数据库备份恢复

## 概述

数据库备份恢复是将数据库内容持久化到独立存储介质，并在数据丢失、损坏或误操作后将数据库还原到某个一致性状态的系统性技术。与复制（Replication）不同，备份针对的是"时间点恢复"场景——当主库和所有副本同时损坏或发生逻辑错误（如执行了`DROP TABLE`）时，只有备份能救场。

备份技术的演进与磁带存储密切相关。1970年代早期的数据库系统（如IBM IMS）依赖完整转储到磁带。1992年PostgreSQL前身Postgres引入了基于WAL的恢复机制。2000年代后，云对象存储（AWS S3、GCS）使备份存储成本降低约90%，同时催生了快照备份等新范式。

在AI工程场景中，备份恢复的重要性体现在：模型训练使用的特征工程数据库若因硬件故障损坏，重建标注数据可能花费数月人力；而一个设计良好的备份策略可以将**恢复时间目标（RTO）**控制在分钟级，**恢复点目标（RPO）**控制在秒级。

---

## 核心原理

### 全量备份（Full Backup）

全量备份将数据库在某一时刻的完整数据集复制到目标存储。PostgreSQL使用`pg_basebackup`工具执行全量备份，命令如下：

```bash
pg_basebackup -h localhost -U replicator -D /backup/base -Ft -z -P
```

`-Ft`表示以tar格式输出，`-z`启用gzip压缩。全量备份的大小等于数据库实际数据量，一个100GB的PostgreSQL库压缩后通常在30-60GB之间。全量备份是所有增量和差异备份的**基准点**，没有它，其他备份文件无法独立完成恢复。备份频率的典型设置是每7天执行一次全量备份。

### 增量备份与WAL归档

WAL（Write-Ahead Log，预写日志）是PostgreSQL和大多数关系型数据库实现增量备份的核心机制。数据库在修改任何数据页之前，必须先将变更写入WAL文件，WAL记录格式为`<LSN, 操作类型, 旧值, 新值>`，其中LSN（Log Sequence Number）是单调递增的64位整数，唯一标识每条日志记录的位置。

增量备份本质上是收集全量备份完成后产生的WAL段文件（每个段默认16MB，文件名如`000000010000000000000001`）。PostgreSQL通过`archive_command`参数将WAL自动归档：

```
archive_command = 'cp %p /archive/%f'
```

WAL归档使RPO理论上可降至最近一个WAL段写满的时间，通常不超过5分钟。`wal_level`参数必须设置为`replica`或`logical`，否则WAL中不包含足够的恢复信息。

### 时间点恢复（PITR）

PITR（Point-In-Time Recovery）基于全量备份+WAL归档，将数据库恢复到任意历史时间点。恢复过程分三步：

1. 将全量备份解压到新的数据目录
2. 在`recovery.conf`（PostgreSQL 12之前）或`postgresql.conf`（12及之后）中配置`restore_command`和`recovery_target_time`
3. 启动数据库，引擎自动重放WAL直到目标时间点

例如，若误操作在2024-03-15 14:32:07执行了`DELETE FROM features WHERE model_id=42`，可指定`recovery_target_time = '2024-03-15 14:32:00'`恢复到删除前一刻。重放期间数据库处于只读模式，重放完成后执行`SELECT pg_wal_replay_resume()`提升为可写状态。

### 物理备份 vs 逻辑备份

物理备份（如`pg_basebackup`）直接复制数据文件的二进制内容，恢复速度快，1TB数据库通常可在30分钟内完成恢复，但要求目标PostgreSQL版本与源版本的**主版本号完全相同**（如14.x只能恢复到14.x）。

逻辑备份（如`pg_dump`）导出的是SQL语句或自定义二进制格式，文件中包含`CREATE TABLE`、`COPY`等语句，支持跨版本迁移（如从PostgreSQL 13升级到15），但恢复100GB数据可能需要2-4小时，且无法实现PITR。

---

## 实际应用

**AI特征数据库的备份策略设计**：假设一个用于存储用户行为特征的PostgreSQL库，每天写入约5GB新数据。合理策略为：每7天执行一次全量`pg_basebackup`，启用WAL归档到S3（`archive_command = 'aws s3 cp %p s3://ml-backup/wal/%f'`），保留最近30天的WAL，WAL保留总量约为5GB×30天×增量比例≈150GB。

**快照备份**：AWS RDS、Google Cloud SQL等托管数据库服务提供存储层快照。RDS的自动备份会在每天的备份窗口内创建快照，并持续备份事务日志，支持将数据库恢复到最近5分钟内的任意时间点。快照的创建几乎不影响数据库性能，因为它操作的是底层EBS存储块的写时复制（Copy-on-Write）机制，而非数据库引擎层面。

**灾难恢复演练**：备份系统的价值必须通过定期恢复测试验证。推荐每季度执行一次完整的灾难恢复演练：从归档中拉取全量备份和WAL文件，在隔离环境中执行PITR恢复，用`pg_dump`对比源库和恢复库的关键表行数与校验和。未经测试的备份等同于没有备份。

---

## 常见误区

**误区一：复制可以替代备份**。数据库复制（Streaming Replication）实时同步主库变更到从库，但当主库执行了破坏性SQL（如`TRUNCATE TABLE training_data`），该操作会在数秒内同步到所有从库，导致主从库同时丢失数据。备份保存的是独立的历史快照，不会被主库的误操作污染。

**误区二：`pg_dump`文件是实时一致性备份**。`pg_dump`在导出期间对整个数据库使用`REPEATABLE READ`隔离级别，导出的数据对应dump开始时刻的一致性视图，这一点是正确的。但误区在于认为`pg_dump`可以替代WAL归档实现PITR——它不能。`pg_dump`只能恢复到dump执行完成时的状态，无法恢复到dump后到当前时间段内任意时间点的数据。

**误区三：备份存储在同一机房已足够**。如果备份文件与生产数据库在同一数据中心，发生机房级故障（火灾、洪水、断电）时，备份与数据会同时丢失。生产级别的备份策略要求遵循**3-2-1原则**：3份数据副本，保存在2种不同介质上，其中1份存放在异地（如跨Region的S3存储桶）。

---

## 知识关联

**与数据库复制的关系**：复制（Streaming Replication）和备份服务于不同的故障场景。复制处理硬件故障的高可用切换，将RTO压缩到秒级；备份处理逻辑错误和长期数据保留，提供跨时间的数据保护。两者应同时部署：复制保障可用性，备份保障数据安全性。WAL是两者共享的底层机制——Streaming Replication通过流式传输WAL实现同步，WAL归档则将WAL持久化到备份存储。

**与数据库基本概念的关联**：PITR的正确性依赖数据库的**ACID事务**保证，特别是持久性（Durability）——WAL的存在正是Durability的物理实现，确保已提交事务的WAL记录在磁盘上保留，使重放恢复成为可能。理解`checkpoint`机制（PostgreSQL默认每5分钟或每64个WAL段触发一次）有助于优化WAL归档量：checkpoint将脏数据页刷盘，此前的WAL段在恢复时不再需要从头重放。