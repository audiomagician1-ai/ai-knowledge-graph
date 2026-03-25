---
id: "mn-na-relay-server"
concept: "中继服务器"
domain: "multiplayer-network"
subdomain: "network-architecture"
subdomain_name: "网络架构"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 中继服务器

## 概述

中继服务器（Relay Server）是网络多人游戏架构中的一种数据转发节点，专门用于在两个无法直接建立P2P连接的客户端之间代为传递游戏数据包。当NAT穿透技术（如STUN协议的打洞机制）尝试失败后，客户端会退回到通过中继服务器传输的方案，以保证游戏会话不中断。

中继服务器的标准化实现来自IETF于2010年发布的RFC 5766，即TURN协议（Traversal Using Relays around NAT）。TURN协议在STUN的基础上定义了服务器如何为客户端分配传输地址（Relayed Transport Address），并负责将收到的数据包转发给目标端点。在游戏行业中，Unity的Relay服务、Valve的Steam Datagram Relay（SDR）以及Epic的EOS P2P模块都在底层使用了基于TURN思想的中继方案。

中继服务器对于游戏可达性（Reachability）至关重要。统计数据显示，在真实互联网环境中，约8%至15%的玩家对局会因对称NAT（Symmetric NAT）或严格防火墙策略导致打洞失败，此时若无中继服务器兜底，这部分玩家将完全无法进行联机游戏。

---

## 核心原理

### TURN协议的分配与转发流程

TURN中继服务器的工作分为三个阶段。第一阶段，客户端向TURN服务器发送`Allocate Request`，服务器为该客户端在自身的公网IP上分配一个临时的"中继地址"（Relayed Address），有效期通常为600秒。第二阶段，客户端将这个中继地址告知对方（通过信令服务器），对方向该地址发送数据包。第三阶段，TURN服务器收到数据包后，查找地址映射表，将数据包封装后转发给真实的目标客户端。整个过程中，双方客户端的真实IP对彼此完全不可见。

### 带宽成本与服务器负载

中继服务器与P2P直连最本质的区别在于：所有游戏流量都必须经过服务器，带宽消耗是直连的两倍。以一个60Hz更新率的射击游戏为例，若每个数据包为100字节，一对一的连接每秒产生约12KB的上行流量，若通过中继则服务器需同时承担12KB下行（接收）和12KB上行（转发），即每个活跃连接占用约24KB/s的服务器带宽。对于拥有100个并发房间的中型游戏服务，仅中继流量就可能达到4.8MB/s以上，这是中继服务器运营成本高于普通信令服务器的直接原因。

### ICE候选优先级与中继选择时机

在WebRTC和现代游戏网络库中，中继服务器并非第一选择，而是通过ICE（Interactive Connectivity Establishment）框架按优先级排列的最后备选方案。ICE框架为候选地址定义了优先级公式：

```
优先级 = (2^24) × 类型偏好 + (2^8) × 本地偏好 + (256 - 组件ID)
```

其中类型偏好（Type Preference）规定：本地候选（Host）为126，服务器反射候选（Srflx，即STUN结果）为100，而中继候选（Relay）仅为0。这意味着只有在所有更高优先级的连接尝试均超时（通常等待约5秒）后，ICE才会选择中继路径建立连接。

---

## 实际应用

### Unity Relay 服务的使用场景

Unity的Relay服务（属于Unity Gaming Services）允许开发者无需自建TURN服务器即可为玩家提供中继兜底。开发者通过`RelayServiceSDK`申请一个`Allocation`，获得`JoinCode`后，房主和加入者分别持`JoinCode`连接到Relay服务器，服务器在内部维护两端的映射关系。对于手机游戏或家用宽带环境下的休闲联机游戏，这种方案可以将连接成功率从直连的约85%提升至接近100%。

### Steam Datagram Relay 的地域路由优化

Valve的SDR不仅仅是失败时的备选方案，它还作为主动的路由优化工具使用。SDR在全球部署了数十个接入点（Point of Presence, PoP），客户端连接到最近的PoP后，数据在Valve私有骨干网络内传输，绕过公网路由的拥塞。这使得SDR在某些地区的延迟甚至低于公网直连，例如从东南亚到欧洲的连接，经由SDR中继平均可减少20-40ms的抖动。

### 对称NAT场景下的必要性

企业网络、4G/5G移动网络通常部署对称NAT，其特点是为每个不同的目标IP都分配不同的外部端口，导致STUN打洞完全无效。在这类网络中，中继服务器是唯一可行的连通方案，游戏客户端在检测到对称NAT类型后（通过向STUN服务器发送测试请求并比对外部端口是否一致来判断），应当跳过打洞阶段，直接请求TURN分配以缩短连接建立时间。

---

## 常见误区

### 误区一：中继服务器与游戏服务器（Dedicated Server）是同一回事

中继服务器仅负责透明地转发原始UDP/TCP数据包，它不解析游戏逻辑，不处理位置同步或伤害计算，对数据内容完全无感知。专用游戏服务器则运行完整的游戏模拟，是游戏权威（Authority）所在地。一个游戏可以同时使用专用服务器处理游戏逻辑，并在玩家与专用服务器之间插入中继服务器来解决网络可达性问题，两者并不冲突。

### 误区二：使用中继服务器后延迟必然高得不可接受

延迟增加的实际幅度取决于中继服务器的地理位置和网络质量。在地理分布合理的中继节点部署下，额外增加的延迟通常仅为10-30ms，对大多数非格斗类游戏的体验影响有限。真正导致高延迟的情况是使用了地理位置远离双方玩家的单一中继节点，而非中继机制本身。优化方案是在多个地区部署中继节点，并在ICE协商阶段选择离双方最近的节点。

### 误区三：中继服务器会暴露玩家IP

这是一个与直连P2P相反的特性。使用中继服务器后，数据包的收发双方只能看到中继服务器的IP地址，双方的真实公网IP对彼此完全不可见，这反而增强了隐私保护并防止了DDoS攻击。相比之下，纯P2P直连会将双方IP互相暴露，是游戏中玩家遭受DDoS攻击的主要原因之一。

---

## 知识关联

**与NAT穿透的关系**：中继服务器是NAT穿透失败后的兜底机制，两者在ICE框架中形成有序的降级路径（打洞优先，中继备选）。理解NAT的四种类型（Full Cone、Restricted Cone、Port Restricted Cone、Symmetric）能帮助开发者预测何时会触发中继，从而在带宽预算中为中继流量留出余量。TURN协议本身也依赖STUN协议的消息格式（Magic Cookie字段`0x2112A442`）来编码请求和响应，两者在协议层面紧密耦合。

**向高级架构的延伸**：掌握中继服务器的工作原理后，开发者可进一步研究多路径传输（Multipath）和基于中继的匹配系统优化，例如在匹配时优先将能够直连的玩家配对，仅将确认需要中继的玩家分配到配备了高带宽中继节点的房间，以此控制整体中继成本。