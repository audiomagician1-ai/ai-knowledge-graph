---
id: "caching-strategies"
concept: "缓存策略"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 6
is_milestone: false
tags: ["性能"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 99.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-06
---



# 缓存策略

## 概述

缓存策略（Cache Policy）是决定数据何时存入缓存、存储多长时间、何时失效以及何时更新的一套规则体系。在Web后端工程中，缓存策略直接影响系统响应延迟、数据库压力和数据一致性三者之间的权衡关系。一个设计错误的缓存策略，轻则造成用户读取脏数据，重则引发"缓存雪崩"导致数据库在数秒内被压垮。

缓存技术可追溯至1960年代IBM System/360的CPU多级缓存架构，而Web层面的缓存策略体系化始于HTTP/1.1规范（1997年，RFC 2068，由Roy Fielding等人起草）。该规范首次明确定义了`Cache-Control`、`Expires`、`ETag`、`Last-Modified`等响应头字段。2022年更新的RFC 9111进一步细化了`no-store`与`no-cache`的语义差异：`no-cache`并非禁止缓存，而是要求每次使用前必须向源站进行再验证（Revalidation）；`no-store`才是真正禁止将响应写入任何持久化存储。

缓存策略的核心价值在于打破"每次请求都重新计算或查询"的线性开销模式。以电商系统为例，商品详情页在双十一高峰期可能每秒被请求超过10万次（QPS=100,000），若每次都直接查询MySQL，数据库将在数秒内耗尽连接池（通常上限为1000–2000个连接）。通过合适的缓存策略，这10万次请求中99%以上可由Redis直接返回，数据库实际承受的QPS降至几百次。现代AI推理服务中，OpenAI于2024年10月推出的Prompt Caching功能同样遵循类似逻辑——对超过1024 tokens的Prompt前缀进行缓存，命中时每百万tokens节省约50%的处理成本（输入token价格减半）。

---

## 核心原理

### 1. TTL（Time-To-Live）过期机制

TTL以秒为单位指定数据在缓存中的存活时长，是最基础的失效手段。Redis中通过`EXPIRE key seconds`命令设置，到期后键值通过**惰性删除**（访问时检测）与**定期删除**（每隔100ms随机扫描约20个键）两种机制清除。TTL设置本质上是业务一致性容忍度的量化：

- **短TTL（1–60秒）**：适用于实时排行榜、商品库存数量等高频变更数据。
- **中TTL（5分钟–1小时）**：适用于用户个人信息、订单状态等中等变更频率数据。
- **长TTL（1天–7天）**：适用于城市列表、商品分类树等极少变更的元数据。
- **永不过期（TTL = -1）**：仅用于系统级配置数据，须配合手动失效机制（如`DEL`命令）使用。

HTTP层的`Cache-Control: max-age=3600`与Redis TTL在语义上等价，但作用位置不同——前者在浏览器本地缓存和CDN节点生效，后者在服务端内存缓存层生效。

**例如**：某电商平台的用户头像URL几乎不会每天变更，可在Nginx响应头中设置`Cache-Control: max-age=604800`（7天），同时在Redis中执行`EXPIRE user:avatar:12345 604800`，两层缓存共同减少图片服务器的请求压力，实测可将图片CDN回源率从100%降低至不足0.5%。

### 2. 缓存淘汰算法（Eviction Policy）

当缓存占用内存达到Redis `maxmemory`配置上限时，必须按照指定算法淘汰旧数据以腾出空间。Redis 7.x支持8种淘汰策略：

| 算法 | 全称 | 核心逻辑 | 适用场景 |
|------|------|----------|----------|
| `noeviction` | 无淘汰 | 写操作直接报错 | 不允许丢失任何数据的场景 |
| `allkeys-lru` | 全键LRU | 淘汰最久未被访问的键 | 通用热点数据缓存 |
| `volatile-lru` | 有TTL键LRU | 仅对设置了TTL的键执行LRU | 混合存储（缓存+持久数据）|
| `allkeys-lfu` | 全键LFU | 淘汰访问频率最低的键 | 长尾流量场景 |
| `volatile-ttl` | 最短TTL优先 | 优先淘汰即将过期的键 | TTL差异显著的场景 |
| `allkeys-random` | 全键随机 | 随机淘汰任意键 | 均匀访问分布场景 |

**LRU（Least Recently Used）** 的理论复杂度为 $O(1)$，通过双向链表+哈希表实现。Redis并非实现严格LRU，而是采用**近似LRU**：每次随机采样 `maxmemory-samples`（默认值=5）个键，从中淘汰最久未访问的那个，在内存占用和精度之间取得平衡。**LFU（Least Frequently Used）** 自Redis 4.0（2017年）引入，用一个24位计数器记录访问频率，其中高16位存储最后访问的分钟时间戳，低8位存储对数化的访问频次，能更准确地反映长期热度分布。

### 3. 缓存读写模式（Cache Patterns）

不同的读写时序决定了缓存与数据库之间的一致性保证级别，主要有以下四种模式：

**Cache-Aside（旁路缓存，最常用）**：读时先查缓存，缓存未命中才查DB并回填；写时直接更新DB，然后**删除**（而非更新）缓存键。删除而非更新的原因是：高并发下更新操作存在竞态条件，两个线程可能先后写入不同版本的旧数据，导致缓存长期持有脏值。

**Write-Through（同步写穿）**：每次写操作同时更新缓存和DB，保证强一致性，但写延迟加倍（需等待两次I/O），适用于写少读多的金融账户余额场景。

**Write-Behind（异步写回）**：写操作仅更新缓存，由后台线程批量异步刷新至DB，写吞吐量极高，但宕机时存在数据丢失风险，适用于游戏积分、点赞计数等可接受少量数据丢失的场景。

**Read-Through**：缓存层自动负责回填逻辑，应用代码只与缓存交互，DB查询由缓存中间件（如AWS ElastiCache的DAX）透明完成，减少应用层代码复杂度。

---

## 关键公式与性能指标

### 缓存命中率公式

$$\text{命中率（Hit Rate）} = \frac{\text{缓存命中次数}}{\text{总请求次数}} = \frac{H}{H + M}$$

其中 $H$ 为命中次数（Hit），$M$ 为未命中次数（Miss）。生产环境中Redis命中率应维持在 **95%以上**，低于90%则表明缓存键设计或TTL策略存在问题。

### 平均访问时间公式

$$T_{avg} = h \cdot T_{cache} + (1-h) \cdot (T_{cache} + T_{db})$$

其中 $h$ 为命中率，$T_{cache}$ 为缓存访问延迟（Redis单机约0.1–1ms），$T_{db}$ 为数据库查询延迟（MySQL复杂查询约10–100ms）。当 $h=0.99$，$T_{cache}=0.5\text{ms}$，$T_{db}=50\text{ms}$ 时：

$$T_{avg} = 0.99 \times 0.5 + 0.01 \times (0.5 + 50) \approx 0.495 + 0.505 = 1.0\text{ms}$$

对比无缓存时的50ms，响应时间缩短了**50倍**。

### 缓存空间估算

```python
# 估算Redis所需内存的简化模型
def estimate_redis_memory(
    total_keys: int,       # 总缓存键数量
    avg_key_size: int,     # 平均键名大小（字节）
    avg_value_size: int,   # 平均值大小（字节）
    redis_overhead: float = 1.5  # Redis内部结构开销系数（约50%）
) -> float:
    """
    返回预估内存占用（MB）
    Redis每个键的实际内存 ≈ (key_size + value_size) × overhead
    """
    raw_bytes = total_keys * (avg_key_size + avg_value_size)
    total_bytes = raw_bytes * redis_overhead
    return total_bytes / (1024 ** 2)

# 案例：100万商品缓存，键名平均30字节，值（JSON）平均500字节
memory_mb = estimate_redis_memory(1_000_000, 30, 500)
print(f"预估Redis内存：{memory_mb:.1f} MB")  # 输出：预估Redis内存：781.3 MB
```

---

## 实际应用场景

### 场景一：防止缓存穿透（Cache Penetration）

缓存穿透指查询一个**数据库中根本不存在**的键（如攻击者发送随机商品ID），导致每次请求都绕过缓存直达DB。解决方案有两种：

1. **缓存空值**：查询DB返回空结果时，向Redis写入`NULL`值并设置短TTL（如60秒），阻止重复穿透。代价是可能短暂缓存错误的"不存在"状态。
2. **布隆过滤器（Bloom Filter）**：在请求进入缓存层之前，用布隆过滤器预判键是否存在。布隆过滤器由Burton Howard Bloom于1970年提出，使用 $k$ 个哈希函数和 $m$ 位的位数组，可在 $O(k)$ 时间内完成判断，假阳性率（False Positive Rate）为：

$$\epsilon \approx \left(1 - e^{-kn/m}\right)^k$$

其中 $n$ 为已插入元素数量。当 $m/n = 10$、$k=7$ 时，假阳性率约为0.8%，即每1000次"不存在"的正确判断中约有8次误判，但**绝不会漏判真实存在的键**（零假阴性）。

### 场景二：防止缓存雪崩（Cache Avalanche）

缓存雪崩指大量缓存键在**同一时刻集中过期**，导致数据库瞬间承受全部流量。典型触发条件是系统初始化时批量设置了相同TTL（如统一设置3600秒）。

解决方案：在基础TTL上叠加随机抖动（Jitter）：

```python
import random

BASE_TTL = 3600  # 基础TTL：1小时

def get_ttl_with_jitter(base_ttl: int, jitter_ratio: float = 0.2) -> int:
    """
    在基础TTL上增加 ±20% 的随机抖动，避免集中过期
    例如：base_ttl=3600 → 实际TTL在 [2880, 4320] 秒之间均匀分布
    """
    jitter = int(base_ttl * jitter_ratio)
    return base_ttl + random.randint(-jitter, jitter)

# 批量设置10万个商品缓存，TTL均匀分散在2880–4320秒之间
for product_id in product_ids:
    ttl = get_ttl_with_jitter(BASE_TTL)
    redis_client.setex(f"product:{product_id}", ttl, product_data)
```

### 场景三：防止缓存击穿（Cache Breakdown）

缓存击穿特指**单个热点键**过期瞬间，数以千计的并发请求同时穿透到DB（与雪崩的区别在于：雪崩是大量键集中过期，击穿是单个热键瞬间失效）。解决方案是使用**互斥锁（Mutex）**：第一个未命中的请求获得Redis分布式锁（`SET lock:product:123 1 NX EX 5`），负责查询DB并回填缓存；其余请求自旋等待或返回降级数据，避免DB被几千个并发查询同时击中。

---

## 常见误区

**误区一：以为`Cache-Control: no-cache`等于禁止缓存。**
实际上`no-cache`的语义是"可以缓存，但每次使用前必须向源站验证"。若源站返回304 Not Modified，浏览器直接复用本地缓存，仅消耗一次网络往返而无需重新传输Body，比`no-store`（完全不缓存）更高效。真正禁止所有缓存存储