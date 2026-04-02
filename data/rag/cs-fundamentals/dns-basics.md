---
id: "dns-basics"
concept: "DNS原理"
domain: "ai-engineering"
subdomain: "cs-fundamentals"
subdomain_name: "计算机基础"
difficulty: 3
is_milestone: false
tags: ["dns", "domain", "resolution"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# DNS原理

## 概述

DNS（Domain Name System，域名系统）是将人类可读的域名（如 `www.example.com`）转换为机器可路由的IP地址（如 `93.184.216.34`）的分布式数据库系统。该系统由Paul Mockapetris于1983年设计，并发布于RFC 882和RFC 883文档中，1987年的RFC 1034和RFC 1035成为至今仍在使用的标准规范。在DNS出现之前，互联网依赖单一的HOSTS.TXT文件维护主机名到IP的映射，由斯坦福研究院手工维护，这在网络规模扩大后完全无法扩展。

DNS的重要性远超简单的"地址簿"比喻。在AI工程实践中，模型训练集群、微服务架构、API网关的相互发现都依赖DNS解析；当训练任务跨多节点通信时，节点间的主机名解析延迟直接影响分布式训练的同步效率。DNS默认使用UDP协议的**53端口**进行查询（响应超过512字节时切换为TCP），查询延迟通常在几毫秒到几十毫秒之间，缓存命中时可降至亚毫秒级。

## 核心原理

### 域名的层级结构

DNS采用树形层级命名空间。以 `api.openai.com.` 为例（注意末尾的点代表根域），从右到左依次是：
- **根域（Root）**：用 `.` 表示，由IANA管理13组根服务器（逻辑上）
- **顶级域（TLD）**：`com`、`org`、`cn` 等，由ICANN授权各注册机构管理
- **二级域**：`openai`，由域名持有者在注册商处注册
- **子域**：`api`，由域名持有者自行配置

每个层级由独立的权威DNS服务器负责，这种分布式设计使得全球DNS系统能扩展到支持超过3.5亿个注册域名。

### 递归查询与迭代查询

这是DNS原理中最容易混淆的核心机制，两者在**谁负责追踪答案**上有本质区别。

**递归查询（Recursive Query）**：客户端向本地递归解析器（Recursive Resolver，通常是ISP或公司内网提供的服务器，如 `8.8.8.8` 或 `114.114.114.114`）发出一次查询，解析器承诺返回最终结果或错误。所有中间查询工作由解析器代劳，客户端只等待最终答案。

**迭代查询（Iterative Query）**：递归解析器向根服务器、TLD服务器、权威服务器逐级查询时采用的方式。每个被询问的服务器只返回"下一步该问谁"的引荐（Referral），而不是最终答案。解析器收到引荐后自行发起下一次查询。

完整的解析流程如下：
1. 浏览器查询本地DNS缓存 → 未命中
2. 查询操作系统 `/etc/hosts` 或系统缓存 → 未命中
3. 向递归解析器（如 `8.8.8.8`）发起**递归查询**
4. 解析器向根服务器发起**迭代查询**，根服务器返回 `.com` TLD服务器地址
5. 解析器向 `.com` TLD服务器迭代查询，获得 `openai.com` 的权威服务器地址
6. 解析器向权威服务器查询，获得最终A记录（IPv4地址）或AAAA记录（IPv6地址）
7. 解析器将结果缓存并返回给客户端

### DNS记录类型与TTL机制

DNS存储的不仅是IP地址，而是多种类型的资源记录（Resource Record）：

| 记录类型 | 用途 | 示例 |
|---------|------|------|
| **A** | 域名→IPv4地址 | `api.example.com. 300 IN A 1.2.3.4` |
| **AAAA** | 域名→IPv6地址 | `api.example.com. 300 IN AAAA ::1` |
| **CNAME** | 域名→另一域名的别名 | `www → example.com.` |
| **MX** | 邮件服务器指向 | 优先级数字越小越优先 |
| **TXT** | 文本信息，常用于SPF/DKIM验证 | — |
| **NS** | 指定区域的权威名称服务器 | — |

**TTL（Time To Live）** 是记录中的整数秒字段，定义了缓存的有效时长。例如 `300` 表示缓存5分钟后必须重新查询。低TTL（如60秒）适合频繁变更IP的服务，但会增加解析器负载；高TTL（如86400秒=1天）减少查询次数，但上线变更后旧地址的传播失效需要等待整个TTL周期。

## 实际应用

**AI推理服务的负载均衡**：大型模型推理集群通常使用DNS轮询（Round-Robin DNS）将同一域名映射到多个后端IP，每次查询返回不同排序的IP列表。例如某推理API域名可能同时指向 `10.0.0.1`、`10.0.0.2`、`10.0.0.3` 三台GPU服务器，客户端依据返回顺序选择第一个地址，从而分散请求压力。

**Kubernetes中的服务发现**：K8s内置CoreDNS（从1.13版本成为默认DNS插件），为集群内每个Service自动注册形如 `my-service.my-namespace.svc.cluster.local` 的DNS记录。AI训练任务中，参数服务器（Parameter Server）和工作节点通过这个内部DNS互相发现，无需硬编码IP，支持Pod的动态扩缩容。

**CDN加速原理**：CDN服务商（如Cloudflare、Akamai）通过**CNAME链**将用户域名指向CDN的调度域名，后者的权威服务器根据查询来源的IP地理位置返回距离最近的边缘节点IP，实现就近访问。这是DNS被用于流量调度而非纯粹地址解析的典型场景。

## 常见误区

**误区一：修改DNS记录后立即全球生效**。实际上，由于TTL缓存机制，变更传播时间取决于旧记录的TTL值。若原记录TTL为86400秒（1天），则全球各地缓存最长需要24小时才会过期刷新。正确做法是在计划变更前提前将TTL调低到300秒，等待旧缓存过期后再执行切换，切换稳定后再恢复高TTL。

**误区二：CNAME和A记录可以互换使用**。CNAME是别名指向另一个域名，解析时需要额外一次查询；更关键的是，**根域名（Zone Apex，如 `example.com`）不能设置CNAME记录**，因为RFC规定根域必须有SOA和NS记录，而CNAME记录不能与其他记录共存。这就是为什么许多服务商提供"ALIAS"或"ANAME"记录作为根域的CNAME替代方案。

**误区三：DNS查询内容是加密的**。传统DNS查询使用明文UDP/TCP传输，中间网络设备可以看到并篡改查询内容，存在DNS劫持风险（如ISP强制跳转广告页）。DNS over HTTPS（DoH，RFC 8484，2018年发布）和DNS over TLS（DoT，RFC 7858）通过加密信道传输DNS查询，是解决该问题的现代方案，但截至目前并非所有环境默认启用。

## 知识关联

**依赖HTTP协议知识**：当浏览器发起HTTP请求时，DNS解析是建立TCP连接之前的**必要前置步骤**。HTTP的 `Host` 头字段携带域名，但底层TCP连接建立需要IP地址，两者之间正是由DNS桥接。理解HTTP请求的完整生命周期必须包含DNS解析阶段的延迟计算。

**依赖网络基础知识**：DNS的UDP传输特性（53端口，无连接、低开销）、递归解析器IP的配置（操作系统网络配置的 `nameserver` 字段）、以及DNS缓存中毒攻击（利用UDP无连接特性伪造响应）都建立在对IP/UDP协议栈的理解之上。在网络抓包分析（如Wireshark）中，DNS报文具有独特的二进制格式：前12字节为固定头部，包含事务ID（2字节）、标志位（2字节）以及各节计数字段。