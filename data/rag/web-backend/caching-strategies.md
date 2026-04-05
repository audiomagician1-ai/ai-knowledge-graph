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
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

TTL以秒为单位指定数据在缓存中的存活时长，是最基础的失效手段。Redis中通过`EXPIRE key seconds`命令设置，到期后键值通过**惰性删除**（访问时检测）与**定期删除**（每隔100ms随机扫描）两种机制清除。TTL设置本质上是业务一致性容忍度的量化：

- **短TTL（1–60秒）**：适用于实时排行榜、商品库存数量等高频变更数据。
- **中TTL（5分钟–1小时）**：适用于用户个人信息、订单状态等中等变更频率数据。
- **长TTL（1天–7天）**：适用于城市列表、商品分类树等极少变更的元数据。
- **永不过期（TTL = -1）**：仅用于系统级配置数据，须配合手动失效机制（如`DEL`命令）使用。

HTTP层的`Cache-Control: max-age=3600`与Redis TTL在语义上等价，但作用位置不同——前者在浏览器本地缓存和CDN节点生效，后者在服务端内存缓存层生效。

**例如**：一个用户头像URL几乎不会每天变更，可设置`Cache-Control: max-age=604800`（7天），同时在Redis中设置`EXPIRE user:avatar:12345 604800`，两层缓存共同减少图片服务器的请求压力。

### 2. 缓存淘汰算法（Eviction Policy）

当缓存占用内存达到`maxmemory`配置上限时，Redis必须按照指定算法淘汰旧数据以腾出空间：

| 算法 | 全称 | 核心逻辑 | 适用场景 |
|------|------|----------|----------|
| LRU | Least Recently Used | 淘汰最久未被访问的键 | 用户Session、页面缓存 |
| LFU | Least Frequently Used | 淘汰历史访问频率最低的键 | 热门商品、热搜词 |
| FIFO | First In First Out | 淘汰最早写入的键 | 日志缓冲等顺序场景 |
| Random | 随机淘汰 | 随机选取键淘汰 | 访问模式无规律时 |

Redis 8.x默认淘汰策略为`noeviction`（内存满时拒绝新写入），生产环境通常改为`allkeys-lru`或`allkeys-lfu`。值得注意的是，Redis的LRU实现**并非精确LRU**，而是每次随机采样`maxmemory-samples`（默认值为5）个键，淘汰其中最久未访问的那个，以O(1)时间复杂度换取少量精度损失。将`maxmemory-samples`调至10可接近精确LRU，但CPU开销增加约2倍（参考《Redis设计与实现》，黄健宏，机械工业出版社，2014年）。

LFU算法在Redis 4.0（2017年）中引入，通过一个8位的访问计数器（最大值255）和衰减因子`lfu-decay-time`（默认1分钟）来估算访问频率，解决了LRU无法识别"历史高频但近期未访问"的热点数据被误淘汰的问题。

### 3. 缓存更新模式

不同的更新模式决定了缓存与数据库之间的一致性保障等级：

**Cache-Aside（旁路缓存，最常用）**
读取时先查缓存，未命中则查数据库并回填缓存；写入时先更新数据库，再**删除**（而非更新）缓存。删除而非更新的原因：若并发写入场景下先更新缓存再更新数据库，可能导致旧值覆盖新值，造成永久性脏缓存。

**Write-Through（同步直写）**
每次写操作同时更新缓存和数据库，由缓存层保证两者同步。优点是缓存始终与数据库一致；缺点是写延迟增加，且对不会再被读取的数据造成无效缓存写入浪费。

**Write-Behind（异步回写）**
写操作只更新缓存，由后台异步任务批量刷新到数据库。写性能最高，但在缓存宕机时存在数据丢失风险，适用于日志统计、点赞计数等可容忍少量丢失的场景。

**Refresh-Ahead（预刷新）**
在缓存即将过期之前，由后台线程主动预取新数据并提前刷新缓存，避免TTL到期时的瞬间穿透。Netflix的EVCache系统大量采用此策略，将缓存命中率维持在99.9%以上（Netflix Tech Blog, 2013）。

---

## 关键公式与性能指标

缓存效益可用**命中率（Hit Rate）**和**期望访问时间**来量化：

$$
\text{Hit Rate} = \frac{N_{\text{hit}}}{N_{\text{hit}} + N_{\text{miss}}} \times 100\%
$$

$$
T_{\text{avg}} = h \cdot T_{\text{cache}} + (1 - h) \cdot T_{\text{db}}
$$

其中：
- $h$ = 缓存命中率（0到1之间）
- $T_{\text{cache}}$ = 缓存访问时间（Redis典型值约0.1–1ms）
- $T_{\text{db}}$ = 数据库查询时间（MySQL典型值约5–50ms）

**例如**：若 $h = 0.95$，$T_{\text{cache}} = 0.5\text{ms}$，$T_{\text{db}} = 20\text{ms}$，则：

$$
T_{\text{avg}} = 0.95 \times 0.5 + 0.05 \times 20 = 0.475 + 1 = 1.475\text{ms}
$$

相比不使用缓存时的20ms，平均响应时间降低了**93%**。命中率从95%提升至99%时，$T_{\text{avg}}$ 进一步降至0.695ms，说明在高命中率区间，每提升1%命中率的边际收益依然显著。

---

## 实际应用

### 电商场景：多级缓存架构

典型电商系统采用三级缓存架构：

```python
import redis
import json
from functools import wraps

r = redis.Redis(host='localhost', port=6379, db=0)

def cache_aside(key_prefix, ttl=300):
    """Cache-Aside 装饰器：先查 Redis，未命中再查数据库"""
    def decorator(func):
        @wraps(func)
        def wrapper(product_id, *args, **kwargs):
            cache_key = f"{key_prefix}:{product_id}"
            # 1. 查询 Redis 缓存
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)  # 命中，直接返回
            # 2. 缓存未命中，查询数据库
            result = func(product_id, *args, **kwargs)
            if result:
                # 3. 回填缓存，设置 TTL（加随机抖动防止同时过期）
                import random
                actual_ttl = ttl + random.randint(0, 60)
                r.setex(cache_key, actual_ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_aside(key_prefix="product:detail", ttl=600)
def get_product_from_db(product_id):
    # 模拟数据库查询
    return {"id": product_id, "name": "示例商品", "price": 99.9}
```

上述代码中，TTL加入了`random.randint(0, 60)`的随机抖动，是防止**缓存雪崩**的关键手段——若数百个缓存键在同一秒集体过期，瞬间涌入数据库的请求将造成流量洪峰。

### AI推理场景：KV Cache管理

大语言模型推理中，Transformer的注意力计算会为每个token生成Key-Value矩阵，重复输入相同的Prompt前缀时可以复用这些KV缓存。以LLaMA-3-70B为例，单次推理的KV Cache占用约为：

$$
\text{KV Cache Size} = 2 \times n_{\text{layers}} \times n_{\text{heads}} \times d_{\text{head}} \times \text{seq\_len} \times \text{bytes\_per\_element}
$$

对于LLaMA-3-70B（80层，64头，128维，float16精度），处理1024个token的KV Cache约占用**20GB显存**。合理的KV Cache淘汰策略（如H2O算法中保留"重型"注意力头对应的token）可将显存占用压缩至原来的20%，同时将吞吐量提升3–5倍（Zhang et al., 2023, *H2O: Heavy-Hitter Oracle for Efficient Generative Inference*）。

---

## 常见误区

### 误区1：用更新代替删除（导致脏缓存）

在Cache-Aside模式下，写操作后应**删除**缓存键，而非直接写入新值。若采用"写数据库→写缓存"的顺序，在高并发场景下：
1. 线程A写数据库（新值）→ 尚未写缓存
2. 线程B写数据库（更新值）→ 写缓存（更新值）
3. 线程A写缓存（新值，覆盖了更新值）

此时缓存中存储的是**旧的"新值"**而非最终的"更新值"，且这一脏数据将持续到TTL过期，可能长达数小时。

### 误区2：TTL设为统一固定值（导致缓存雪崩）

若系统启动时批量将10万个键都设置为`TTL=3600`，则一小时后这10万个键将**同时失效**，导致数据库瞬间承受10万次并发查询。正确做法是在基础TTL上叠加随机抖动：`TTL = base_ttl + random(0, base_ttl * 0.1)`。

### 误区3：混淆缓存穿透、击穿、雪崩

| 问题 | 触发场景 | 解决方案 |
|------|----------|----------|
| 缓存穿透 | 查询数据库中不存在的key（如恶意请求ID=-1） | 布隆过滤器（Bloom Filter）拦截 |
| 缓存击穿 | 单个热点key恰好过期，瞬间大量并发穿透至数据库 | 互斥锁（Mutex）或永不过期+逻辑TTL |
| 缓存雪崩 | 大量key同时过期或Redis宕机 | TTL随机抖动 + Redis主从高可用 |

布隆过滤器的误判率公式为 $p \approx (1 - e^{-kn/m})^k$，其中 $k$ 为哈希函数个数，$n$ 为元素数量，$m$ 为bit数组大小。Redis 4.