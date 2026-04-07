---
id: "mn-na-nat-traversal"
concept: "NAT穿透"
domain: "multiplayer-network"
subdomain: "network-architecture"
subdomain_name: "网络架构"
difficulty: 4
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# NAT穿透

## 概述

NAT穿透（NAT Traversal）是指让位于不同NAT（网络地址转换）设备后方的两台主机，在无需修改路由器配置的情况下建立直接通信连接的技术集合。家用路由器普遍采用NAT将一个公网IP地址映射给局域网内多台设备，这使得外部主机无法直接"拨入"某台内网设备，从而阻断了P2P游戏连接的建立。NAT穿透的目标，就是绕过这道屏障，让两个玩家的客户端直接交换游戏数据包，而非依赖中间服务器转发每一帧状态。

NAT穿透技术的系统化始于2003年前后的VoIP领域。IETF于2008年正式发布RFC 5389（STUN协议规范），随后RFC 5766（TURN）和RFC 8445（ICE框架）相继标准化，形成了今天游戏行业广泛采用的穿透技术栈。这套标准最初为实时音视频通话设计，但因游戏同样需要低延迟的P2P连接，PlayStation Network、Xbox Live、Steam等平台均将ICE框架移植进了各自的对战匹配系统。

在多人游戏中，NAT穿透成功与否直接决定玩家能否以最低延迟对战。两台中国玩家的机器若能直接P2P连通，往返延迟（RTT）可低至10-30ms；若穿透失败而必须经由远端中继服务器，延迟可能翻倍甚至更高，且中继服务器的带宽成本由开发商承担。因此NAT穿透成功率是衡量多人游戏网络层质量的关键指标之一。

---

## 核心原理

### NAT类型与穿透难度分级

NAT设备的行为模式直接决定穿透策略的选择。RFC 3489将NAT分为四种类型，难度从低到高依次为：

- **完全圆锥型（Full Cone）**：内网IP:Port映射到固定公网IP:Port后，任何外部主机均可向该公网端口发包，穿透最容易。
- **受限圆锥型（Restricted Cone）**：只有内网主机曾主动发包的目标IP才能回包，但目标端口不受限。
- **端口受限圆锥型（Port Restricted Cone）**：目标IP和端口均须匹配才能回包。
- **对称型（Symmetric NAT）**：每次新建连接都分配不同的公网端口，两台对称型NAT之间的直连穿透成功率接近0%，几乎必须回落到中继服务器。

家用宽带路由器约60%属于端口受限圆锥型，约15%属于对称型。游戏引擎在设计NAT检测逻辑时，会在握手阶段先探测对方NAT类型，再决定采用打洞还是中继。

### STUN：公网地址发现

STUN（Session Traversal Utilities for NAT）协议解决的问题是：内网主机不知道自己的公网IP和端口，无法告诉对方"来哪里找我"。客户端向公网STUN服务器（默认UDP端口3478）发送绑定请求，服务器将观察到的源IP和源端口原封不动地写回响应体中，客户端由此得知自己的**映射地址**（Mapped Address）。整个过程仅需一次UDP往返，延迟极低。STUN本身不转发游戏数据，只做地址发现，因此其服务器带宽开销几乎可以忽略。

### UDP打洞（UDP Hole Punching）

获得双方公网地址后，UDP打洞是实现直连的核心手段。假设玩家A的公网地址为`203.0.113.10:54321`，玩家B为`198.51.100.20:60000`，双方通过信令服务器交换各自地址后，**同时**向对方的公网地址发送UDP探测包。A向B发包的同时，A的NAT会在自己的映射表中为该连接打开一个"孔"，允许B的回包通过；B端同理。关键在于"同时"——两端必须几乎同步发出探测包，否则先到的包会被另一端NAT丢弃，这就是需要信令服务器协调时序的原因。对于端口受限圆锥型NAT，此方法成功率可达85%以上。

### TURN：受控中继回落

当双方NAT均为对称型，或打洞多次失败时，TURN（Traversal Using Relays around NAT，RFC 5766）提供中继回落。客户端向TURN服务器申请一个**分配地址**（Relayed Address），对方将数据发往该地址，TURN服务器再转发给真实客户端。TURN服务器需要承载完整的双向游戏流量，带宽成本显著高于STUN。正因如此，多数游戏平台将TURN用量纳入成本监控，并尝试通过优化ICE候选优先级顺序来降低TURN回落率。

### ICE：统一协商框架

ICE（Interactive Connectivity Establishment，RFC 8445）是将STUN和TURN整合到一套候选地址协商流程中的框架。ICE定义了三类候选地址：
1. **Host候选**：本机局域网IP:Port（同一局域网内直连使用）
2. **Server Reflexive候选**：由STUN发现的公网映射地址
3. **Relayed候选**：TURN分配的中继地址

两端通过信令通道交换候选列表后，ICE按照优先级顺序（Host > Server Reflexive > Relayed）对所有候选对进行连通性检查（Connectivity Check），选出延迟最低且能通信的候选对作为最终连接路径。ICE的优先级公式为：`priority = (2^24) * type_pref + (2^8) * local_pref + (256 - component_id)`，其中`type_pref`对Host、Server Reflexive、Relayed分别取126、100、0。

---

## 实际应用

**PlayStation Network的NAT类型提示**：PS4/PS5在网络设置界面会显示NAT类型1/2/3，其中类型3对应对称型NAT，用户会看到"无法与部分玩家进行语音聊天或多人游戏"的警告。索尼的系统实际上是在运行ICE检测后将结果翻译为简化的用户可读等级。

**Unity Relay与Netcode for GameObjects**：Unity 2021.2起官方提供Unity Relay服务，底层即为TURN中继，与Unity Transport配合使用。当ICE打洞失败时，SDK自动将流量路由至就近的Relay节点，开发者无需自行实现回落逻辑。

**《英雄联盟》的连接流程**：Riot Games的Peer-to-Play特性在观战模式中使用ICE框架，让观战客户端直接从游戏客户端拉取数据流，减少官方服务器的带宽压力，同时降低观战延迟约200ms。

---

## 常见误区

**误区一：TCP同样可以高效打洞**
TCP打洞理论上可行，但由于TCP的SYN包需要精确的时序同步，且许多NAT设备会提前重置不完整的TCP握手，实际成功率远低于UDP打洞。游戏中99%的NAT穿透实现使用UDP，即便底层游戏协议是可靠传输，也会在UDP上自行实现可靠层（如RUDP），而非依赖TCP打洞。

**误区二：STUN服务器全程参与游戏数据传输**
STUN服务器仅在连接建立阶段被调用一次，用于地址发现，之后游戏数据完全不经过STUN服务器。混淆STUN与TURN是新手最常见的错误——TURN才是转发数据的服务器。一旦ICE协商完成，STUN服务器对该连接的作用已结束。

**误区三：开放DMZ或UPnP等同于NAT穿透**
DMZ和UPnP是从路由器配置层面绕过NAT限制的方法，要求用户手动操作或设备支持UPnP协议，属于"预防"手段而非"穿透"手段。NAT穿透技术（STUN/TURN/ICE）不修改路由器配置，适用于绝大多数无法操控路由器的玩家场景，两者解决问题的层次完全不同。

---

## 知识关联

**前置概念——P2P架构**：NAT穿透是P2P架构能在真实网络环境中落地的必要条件。P2P架构描述了"两台客户端直接通信"的拓扑模型，而NAT穿透回答了"如何在普遍存在NAT的互联网上实际建立这条连接"的工程问题。没有NAT穿透，P2P游戏架构在家用宽带环境下几乎无法工作。

**后续概念——中继服务器**：当NAT穿透彻底失败（尤其是双方均为对称型NAT时），流量必须经由中继服务器（对应ICE中的TURN回落路径）转发。中继服务器的选址、带宽规划、以及如何在保证连通性的同时控制中继使用率，是理解游戏后端基础设施成本结构的下一步核心议题。NAT穿透成功率越高，中继服务器的压力就越小，这两个概念形成直接的成本权衡关系。