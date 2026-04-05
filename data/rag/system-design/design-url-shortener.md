---
id: "design-url-shortener"
concept: "设计短链接系统"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 7
is_milestone: false
tags: ["实战"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 设计短链接系统

## 概述

短链接系统（URL Shortening System）将长达数百字符的原始URL压缩为6-8位的短标识符，使得 `https://www.example.com/very/long/path?param=value` 变为 `https://bit.ly/3xK9mP`。这类系统的核心挑战并非算法本身，而在于：如何在每秒数万次重定向请求下保证毫秒级响应，同时维护短码的全局唯一性。

短链接服务的商业实践最早可追溯至2002年TinyURL的上线，2009年Twitter因140字符限制推动了bit.ly的爆发式增长。现代短链接系统每日处理数十亿次302重定向请求，Pinterest、Slack等产品内嵌了私有短链服务。设计此类系统要求工程师同时解决**写入时的唯一ID生成**与**读取时的高并发缓存**两个截然不同的性能瓶颈。

从规模估算角度，一个中等规模的短链接服务每天新增1亿条短链，意味着系统需要在10年内支持约3650亿条记录。6位字母数字组合（62^6 ≈ 568亿）不够，因此工业实践中通常采用7位（62^7 ≈ 3.5万亿）作为最小安全位数。这一数学约束直接决定了ID生成策略的选型。

---

## 核心原理

### 短码生成策略

**方案一：哈希截断法**
对原始URL计算MD5或SHA-256哈希值，取前7位Base62编码字符作为短码。公式如下：

```
short_code = Base62_encode(MD5(original_url))[0:7]
```

碰撞概率约为 `1 - e^(-n²/2m)`（生日悖论公式），当已存储n=10亿条记录、码空间m=62^7时，碰撞概率约0.014%，因此必须加入碰撞检测逻辑（数据库唯一键冲突后对URL拼接随机盐重新哈希）。

**方案二：全局自增ID + Base62转换**
数据库自增ID（如MySQL AUTO_INCREMENT）经Base62编码后直接作为短码，ID=1转为"1"，ID=3500000000转为"3d2lg"。此方案消除碰撞，但存在短码可被预测枚举的安全风险，需额外引入**ID混淆**（如与固定盐异或后再编码）。

**方案三：分布式唯一ID（Snowflake变体）**
Twitter Snowflake算法生成64位整数，取低42位数值做Base62编码，可生成约7位短码，且天然有序、分布式无锁生成，适合日均亿级写入场景。

### 重定向机制与HTTP状态码选择

短链服务必须在301与302重定向之间做出明确选择：
- **301 Permanent Redirect**：浏览器缓存后不再请求短链服务器，节省带宽，但**丧失点击统计能力**。
- **302 Found（临时重定向）**：每次点击都经过短链服务器，支持访问统计、A/B测试和链接失效控制，是绝大多数商业系统的选择，代价是每次额外一跳网络延迟（通常15-50ms）。

系统响应头示例：
```
HTTP/1.1 302 Found
Location: https://original-long-url.com/...
Cache-Control: no-cache
```

### 读写分离与缓存架构

短链系统读写比极度不均衡，通常为**100:1**甚至更高（创建1次，被访问数百次）。标准三层缓存架构如下：

1. **CDN层**：对热门短链在边缘节点缓存302响应，适合全球化部署，可将核心服务器请求量降低70%以上。
2. **Redis缓存层**：`short_code → original_url` 的KV映射，TTL设为24-48小时，命中率可达95%以上。单个Redis实例可支撑10万QPS查询。
3. **MySQL/PostgreSQL持久层**：仅处理缓存未命中的1-5%请求，以及写入操作。主表结构：`(id BIGINT PK, short_code VARCHAR(8) UNIQUE, original_url TEXT, created_at DATETIME, expire_at DATETIME, user_id BIGINT)`。

---

## 实际应用

**场景一：营销活动短链（含点击分析）**
电商大促期间，运营人员为每个商品页生成短链并追踪转化率。系统需要将每次302重定向事件异步写入Kafka消息队列，消费端聚合统计IP、User-Agent、时间戳，入库ClickHouse进行分析。**关键设计**：重定向本身（同步，低延迟）与统计记录（异步，允许短暂延迟）严格解耦，避免统计写入阻塞主链路。

**场景二：短链过期与自定义别名**
企业客户要求 `company.com/sale2024` 这样的可读短码，同时设置72小时后自动失效。数据库`expire_at`字段配合Redis TTL双重过期控制，定时任务（如每小时一次的MySQL DELETE WHERE expire_at < NOW()）清理过期记录，Redis设置相同TTL确保缓存与DB一致。

**场景三：防滥用限速**
公开短链API每IP每分钟最多允许创建10条短链，使用Redis `INCR` + `EXPIRE` 实现滑动窗口限速：
```
key = "rate:create:{ip}:{minute_bucket}"
count = INCR(key)
if count == 1: EXPIRE(key, 60)
if count > 10: return 429 Too Many Requests
```

---

## 常见误区

**误区一：用MD5哈希就不需要考虑碰撞**
许多初学者认为MD5输出空间（128位）足够大，7位截断不会碰撞。但实际上截断后的有效空间仅有62^7 ≈ 3.5万亿，当系统存储超过数亿条记录时碰撞概率已不可忽略，必须在数据库设置`UNIQUE INDEX`并在应用层处理`Duplicate Key`异常，重试生成。

**误区二：数据库自增ID直接暴露等于短码**
若短码直接是`1, 2, 3...`的十进制序列，攻击者可枚举所有短链并爬取目标URL。Base62编码不等于加密，需叠加ID混淆（位操作置换或XOR随机盐），或采用专用的**ID混淆库**（如Hashids）将整数映射为不可逆的短字符串，防止业务信息泄露。

**误区三：选择301重定向"优化性能"**
301重定向确实减少了服务器负载，但代价是**永久失去对该链接的控制权**——链接一旦被浏览器缓存，即使后台修改目标URL或标记链接为失效，用户仍会被直接跳转到旧地址。商业产品中301仅用于不需要统计且永不变更的静态场景，绝大多数业务场景应使用302。

---

## 知识关联

**前置知识衔接**：系统设计入门中的CAP定理在短链系统中有具体体现——短链系统选择**AP**（可用性+分区容忍性），允许缓存与数据库短暂不一致（刚刚删除的失效链接在Redis TTL过期前仍可访问），换取高可用与低延迟。

**数据库索引设计**：`short_code`列的`UNIQUE INDEX`是本系统最关键的索引，其B+树结构保证O(log n)查找。URL列不适合建索引（TEXT类型超过767字节的前缀限制），若需"已存在的URL返回原短码"功能，需对URL做SHA-256哈希后单独存储哈希值并建索引。

**水平扩展路径**：当单MySQL实例写入成为瓶颈（通常在1万 QPS写入时），可引入**数据库分片**——按`short_code`首字符或ID范围水平切分至多个分片，每个分片维护独立的自增ID区间（如分片1使用奇数ID，分片2使用偶数ID，类似flickr的Ticket Server方案），保证全局唯一性同时线性扩展写入吞吐量。