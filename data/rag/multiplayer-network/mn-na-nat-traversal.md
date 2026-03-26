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
quality_tier: "B"
quality_score: 45.2
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

# NAT穿透

## 概述

NAT穿透（NAT Traversal）是指在网络地址转换（Network Address Translation）设备后方的两台主机，通过特定协议和技术手段绕过NAT限制，建立直接点对点连接的技术集合。NAT设备通常由家用路由器或运营商设备扮演，它将私有IP地址（如192.168.x.x）映射到公网IP，导致外部主机无法主动连接到NAT后方的设备——这正是多人游戏中玩家直连失败的最根本原因。

NAT穿透技术在2003年前后随着VoIP通信需求而快速发展，IETF于2008年发布RFC 5389正式标准化STUN协议，2010年发布RFC 5766标准化TURN协议，2010年发布RFC 5245正式定义ICE框架。游戏行业大规模采用这些技术始于2010年代，Steam、PlayStation Network和Xbox Live的P2P对战功能均依赖ICE/STUN机制实现玩家主机之间的直连，以降低延迟并减少中继服务器带宽成本。

在网络多人游戏架构中，NAT穿透直接决定玩家能否以低延迟直连对战。若穿透失败，游戏必须回退到中继服务器（TURN服务器）转发所有数据包，带宽成本急剧上升，延迟也会增加30-100ms以上。成功的NAT穿透可使延迟接近玩家之间的物理网络延迟，对于FPS、格斗游戏等对延迟极敏感的类型尤为关键。

## 核心原理

### NAT类型与穿透难度分级

NAT行为按照RFC 4787分类，不同类型的穿透成功率差异巨大。**完全锥形NAT（Full Cone NAT）**最宽松，一旦内部主机向外发送数据包，任何外部主机都可通过该映射端口回传数据，穿透成功率接近100%。**受限锥形NAT（Restricted Cone NAT）**要求内部主机曾向目标IP发过包才允许该IP回传。**端口受限锥形NAT（Port Restricted Cone NAT）**进一步要求IP和端口都匹配。**对称NAT（Symmetric NAT）**最严格，对每个不同的目标IP:Port组合都分配不同的外部端口，两个对称NAT设备之间的直连穿透成功率接近0%，此时必须使用TURN中继。

### STUN协议：发现公网地址

STUN（Session Traversal Utilities for NAT）的工作原理是：客户端向公网上的STUN服务器（默认端口3478/UDP）发送绑定请求，服务器将观察到的客户端公网IP和端口原样返回给客户端。客户端由此得知自己的"外部地址映射"（Mapped Address）。例如，一台内网地址为192.168.1.5:50000的主机，STUN服务器可能返回其公网映射为203.0.113.10:34521。这个公网地址随后通过信令服务器（如游戏大厅服务器）交换给对方，使对方知道应该连接哪个地址。STUN本身不转发任何游戏数据，仅用于地址发现，服务器压力极小。

### ICE框架：候选地址收集与连通性检测

ICE（Interactive Connectivity Establishment，RFC 5245/8445）是将STUN和TURN整合为统一工作流程的框架。ICE将所有可能的连接路径称为"候选（Candidate）"，分为三类：**Host候选**（本机局域网IP:端口）、**Server Reflexive候选**（通过STUN获取的公网映射地址）、**Relay候选**（通过TURN服务器分配的中继地址）。

两端各自收集候选后，通过信令通道互相交换候选列表，然后按照优先级公式 `priority = (2^24 × type_preference) + (2^8 × local_preference) + component_id` 对候选对进行排序，依次使用STUN绑定请求进行连通性检测（Connectivity Check）。第一个双向均能通过的候选对即被选中作为实际数据传输路径。Host候选优先级最高（type_preference=126），Relay候选最低（type_preference=0），保证只要直连可行就优先直连。

### TURN协议：穿透失败时的兜底机制

TURN（Traversal Using Relays around NAT，RFC 5766）在两个对称NAT之间无法直连时提供数据中继。客户端向TURN服务器发送Allocate请求，服务器分配一个中继传输地址（Relayed Transport Address）。之后所有游戏数据包先发往TURN服务器，再由服务器转发给对端。TURN使用HMAC-SHA1进行长期凭证认证，防止服务器被滥用。一个TURN服务器在100Mbps带宽下通常只能支持约500个并发游戏会话（按每会话200kbps估算），因此运营成本远高于STUN服务器。

## 实际应用

**主机游戏平台**：PlayStation Network的NAT类型显示功能正是基于STUN检测的结果——NAT类型1对应直接连接，NAT类型2对应受限锥形或端口受限锥形，NAT类型3对应对称NAT。许多玩家因NAT类型3无法与他人直连，只能依赖PSN的TURN中继，导致延迟飙升。

**WebRTC游戏**：基于浏览器的多人游戏（如Agar.io、部分HTML5游戏）大量使用WebRTC，其底层即完整实现了ICE/STUN/TURN框架。开发者只需配置`RTCPeerConnection`的`iceServers`参数，填入STUN服务器地址（Google免费提供`stun.l.google.com:19302`）和TURN服务器凭证即可。

**Unity/Unreal的P2P方案**：Unity的Relay服务（原Unity Transport）和Unreal的EOS P2P均内置ICE穿透流程。开发者调用`StartSession`类接口时，底层自动完成STUN发现、ICE候选收集和连通性检测，穿透失败时自动切换至平台提供的TURN中继，整个过程对游戏逻辑层透明。

## 常见误区

**误区一：STUN服务器会转发游戏数据**。许多开发者混淆STUN与TURN的职责。STUN服务器仅在ICE握手阶段参与，只处理极小的绑定请求/响应报文（通常小于100字节），一旦直连建立即完全退出通信链路。实际的游戏UDP数据包直接在两个玩家主机间传输，不经过STUN服务器。

**误区二：端口转发（UPnP）等同于NAT穿透**。UPnP让路由器自动为本机开放特定端口，效果类似手动端口映射，本质是修改NAT表项，属于主动配置。ICE/STUN是在不修改NAT设备的前提下，利用NAT状态机的"空洞打孔（Hole Punching）"特性实现穿透，二者原理完全不同，且UPnP需要路由器支持并开启该功能，而NAT穿透在任何标准NAT下均可尝试（对称NAT除外）。

**误区三：两端同时发包就能穿透对称NAT**。UDP打洞（UDP Hole Punching）在锥形NAT下有效——两端同时向对方的STUN候选地址发包，各自在本端NAT上打开通道。但对称NAT每次向不同目标发包时都会分配新端口，无法预测对方实际连接时使用的外部端口，因此纯打洞技术对两端均为对称NAT的情况几乎无效，必须引入TURN中继。

## 知识关联

NAT穿透建立在P2P架构的基础连接需求之上：P2P架构要求玩家主机之间直接通信，而NAT穿透正是实现这一要求的技术保障。没有NAT穿透，P2P架构在现实家用网络环境（几乎所有家庭路由器都开启NAT）中几乎寸步难行。

当NAT穿透失败时，系统必然回退到**中继服务器**方案。中继服务器（即TURN的游戏层实现）承接了穿透失败的流量，是NAT穿透失败路径的直接后续环节。理解NAT穿透的成功率和失败场景，有助于在架构设计时合理估算中继服务器的容量需求——通常10%-30%的P2P连接会因对称NAT而需要中继，这一比例在移动网络（运营商大量使用CGNAT）中可高达50%以上。