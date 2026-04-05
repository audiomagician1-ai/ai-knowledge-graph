---
id: "cross-play"
concept: "跨平台联机"
domain: "game-engine"
subdomain: "platform-abstraction"
subdomain_name: "平台抽象"
difficulty: 3
is_milestone: false
tags: ["网络"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 跨平台联机

## 概述

跨平台联机（Cross-Platform Play，简称Cross-Play）是指运行于不同硬件平台或操作系统上的玩家能够共享同一个多人游戏会话的技术能力。例如，PlayStation 5玩家与PC玩家、Xbox Series X玩家同时进入同一场《火箭联盟》比赛。这一能力需要游戏引擎在网络层面抽象掉底层平台差异，统一处理来自不同SDK的账户标识、会话管理和数据包传输。

跨平台联机的商业推动始于2017年前后。彼时Epic Games旗下《堡垒之夜》率先实现了PC、主机与移动端的跨平台对战，打破了索尼长期以来对PlayStation封闭生态的坚守。2019年，索尼正式开放跨平台联机政策，此后几乎所有主流多人游戏引擎（Unreal Engine、Unity、Godot）均开始内置或以插件形式支持跨平台网络后端。

从技术视角看，跨平台联机要解决三个独立但相互关联的问题：**平台账户互通**（不同平台的身份认证如何统一）、**跨平台匹配**（如何在异构玩家池中公平分组）以及**输入公平性**（键鼠与手柄玩家同场竞技时如何平衡体验）。游戏引擎的平台抽象层正是承载这三项职责的基础设施。

---

## 核心原理

### 平台账户互通

每个主机平台都有独立的账户系统：索尼的PSN ID、微软的Xbox Live GamerTag、任天堂的Nintendo Account，以及PC端的Steam ID或Epic账户。要让这些账户在同一游戏会话中共存，引擎必须引入**统一用户标识符（Unified Player ID）**机制。

Unreal Engine通过**Online Subsystem**（简称OSS）抽象层实现这一点。OSS将平台特定的账户接口封装为 `IOnlineIdentity` 接口，开发者调用 `GetUniquePlayerId(LocalUserNum)` 即可获得一个平台无关的 `FUniqueNetId` 对象，而不必直接操作PSN或Xbox的原生API。在实际运行时，该对象内部存储的字符串格式因平台不同而不同（如Steam格式为`STEAM_0:1:XXXXXXXX`），但上层逻辑代码无需感知这一差异。

Epic Online Services（EOS）进一步提供了**EOS Connect**机制，支持将PSN、Xbox Live、Steam等外部账户映射到同一个Product User ID（PUID），从而实现真正的跨平台好友关系和成就同步。每个PUID是一个128位UUID，在EOS后端唯一标识一名玩家，无论其从哪个平台登录。

### 跨平台匹配

匹配系统在跨平台联机中面临额外的复杂性，因为不同平台的在线玩家数量不对等——PC端玩家通常远多于某一款游戏在特定主机上的玩家数。单纯将所有平台玩家合入同一匹配池可以缩短等待时间，但会引发体验失衡。

现代跨平台匹配的核心公式是在传统Elo/TrueSkill评分基础上附加**平台权重系数**（Platform Weight Factor, PWF）。以《使命召唤：现代战争》的SBMM（技能匹配）为例，其匹配算法会在±50 Elo范围内优先匹配同平台玩家，超时后（默认30秒）扩展至跨平台池，同时标记玩家的输入类型以备分组参考。

Unreal Engine的`FindSessions`调用支持通过`FOnlineSearchSettings`附加自定义键值对，开发者可以插入`SEARCH_PLATFORM_TYPE`等自定义字段，让专用服务器在会话列表过滤时优先返回输入类型匹配的房间，实现软性同平台优先。

### 输入公平性

跨平台联机最受玩家关注的争议点是**输入设备不对等**问题。键鼠玩家在第一人称射击游戏中具有更高的精确度和转向速度，而手柄玩家依赖瞄准辅助（Aim Assist）弥补设备劣势。当二者混合匹配时，如果瞄准辅助强度不当，会导致手柄玩家对键鼠玩家拥有"粘滞瞄准"优势，反而破坏公平性——这一现象在《Apex英雄》的职业赛事中引发了持续争议。

引擎层面的应对策略是**输入类型检测与动态参数调整**。Unity的Input System（2019年引入，包名`com.unity.inputsystem`，版本1.0起稳定）可通过`InputDevice`的`description.deviceClass`字段区分Gamepad和Mouse，游戏逻辑据此在运行时切换不同的`InputActionAsset`配置，从而为手柄玩家启用较高的瞄准辅助强度（典型值0.6~0.8），为键鼠玩家禁用（值为0）。

在专用服务器架构中，服务器端会记录每名玩家的`InputScheme`枚举值，匹配系统可选择强制同输入类型匹配（Console Pool / PC Pool隔离），或允许跨输入类型混合但在大厅界面以图标形式公示，由玩家自主决策是否进入。《火箭联盟》在2020年引入跨平台功能时即采用后者策略，并允许玩家在设置中关闭跨平台，从而将选择权还给玩家。

---

## 实际应用

**《我的世界》基岩版（Bedrock Edition）** 是目前跨平台联机覆盖平台最广的案例，支持iOS、Android、Windows、Xbox、PlayStation、Switch共六大平台互通。微软在基岩版中使用Xbox Live作为统一账户后端，非Xbox平台玩家必须绑定免费的微软账户才能进入跨平台服务器，这是"统一账户层"策略的典型实现。

**Unreal Engine的Lyra示例项目**（随UE5发布）内置了完整的EOS跨平台联机实现，包括`CommonUser`插件处理多平台登录、`LyraFrontendStateComponent`管理跨平台大厅UI，以及`UCommonSessionSubsystem`封装跨平台会话的创建与加入。开发者可直接参考Lyra的`B_LyraFrontEnd` Blueprint学习EOS Connect的完整账户绑定流程。

---

## 常见误区

**误区一：跨平台联机等同于跨存档（Cross-Save/Cross-Progression）。** 跨平台联机只解决不同平台玩家能否进入同一场对局，不包含角色数据、成就或购买记录的同步。《命运2》支持跨平台联机，但其跨存档功能（Cross Save）是独立系统，需要额外绑定Bungie账户才能激活，二者的实现层完全分离。

**误区二：开启跨平台只需服务器端修改，客户端无需改动。** 实际上，跨平台联机要求客户端SDK的版本严格对齐，且各平台的平台认证审核（如索尼的"跨平台Play"认证、微软的XR-015要求）均需单独申请并调整客户端代码，任何一端的SDK版本不兼容都会导致握手失败。

**误区三：输入公平性只影响射击游戏。** 格斗游戏中，手柄玩家与键盘玩家的帧精度存在差异——键盘可实现每帧独立按键，而手柄摇杆存在死区（Dead Zone）和响应曲线偏差，这在《街霸6》的线上天梯中同样引发了平衡性讨论。引擎层的输入公平性处理必须根据游戏类型定制。

---

## 知识关联

跨平台联机建立在**平台抽象概述**所描述的硬件差异隔离机制之上：没有统一的渲染后端抽象（如Vulkan/Metal/DirectX的统一图形API层）和统一的文件IO抽象，客户端代码无法以相同的构建流程部署到六个不同平台，跨平台联机也就无从谈起。平台抽象层所提供的编译条件隔离（`#if PLATFORM_PS5 ... #endif`）和运行时能力查询接口，是Online Subsystem能够在同一套代码中支持多个平台SDK的前提条件。

在引擎架构演进方向上，随着GDC 2023上多家发行商公布的跨平台成就系统标准化提案，未来的游戏引擎平台抽象层预计会将成就、排行榜和好友关系统一归入跨平台身份层，而不是像现在这样由各平台OSS各自实现。届时，跨平台联机的账户互通部分将进一步简化，但输入公平性与动态匹配权重问题仍将是需要游戏设计师而非引擎开发者持续调校的工程课题。