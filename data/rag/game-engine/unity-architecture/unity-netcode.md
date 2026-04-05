---
id: "unity-netcode"
concept: "Netcode for GameObjects"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 3
is_milestone: false
tags: ["网络"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Netcode for GameObjects

## 概述

Netcode for GameObjects（简称NGO）是Unity官方从2021年起推出的多人游戏网络框架，专为基于GameObject和MonoBehaviour架构的Unity项目设计。它取代了旧版UNET（Unity Networking）框架，后者已于2023年正式停止维护。NGO的核心设计哲学是"以游戏对象为中心"——网络状态直接绑定到场景中的GameObject，开发者通过添加组件而非编写底层Socket代码来实现联机功能。

NGO采用客户端-服务器（Client-Server）拓扑结构作为默认架构，其中一个实例承担Server角色，其余实例作为Client连接。它也支持Host模式，即同一进程同时担任Server和Client两种角色，这在小型局域网游戏或本地测试中极为常见。截至1.x版本，NGO不原生支持完全对等（P2P）网络拓扑。

NGO对Unity开发者的重要性在于它与Unity编辑器的深度集成：NetworkPrefabs列表、Scene Management、物理同步均在Unity Inspector中可视化配置，无需手动处理序列化或连接握手协议，大幅降低了多人游戏开发的入门门槛，适合难度3级左右的中低复杂度联机项目。

---

## 核心原理

### NetworkObject 与所有权模型

每个需要在网络中同步的GameObject都必须挂载`NetworkObject`组件，这是NGO网络身份的根本标识。每个NetworkObject拥有唯一的`NetworkObjectId`（64位整数），以及一个`OwnerClientId`属性标识当前"拥有者"客户端。

所有权（Ownership）决定了谁有权修改该对象的网络变量。默认情况下，Server拥有所有NetworkObject的权限（Server Authority）；通过调用`NetworkObject.ChangeOwnership(clientId)`可将控制权转移给特定客户端，适用于玩家角色控制等场景。

### NetworkVariable 与状态同步

`NetworkVariable<T>`是NGO实现自动状态同步的核心数据容器，支持基础值类型（int、float、bool、Vector3等）。声明示例：

```csharp
private NetworkVariable<int> m_Health = new NetworkVariable<int>(
    100,
    NetworkVariableReadPermission.Everyone,
    NetworkVariableWritePermission.Server
);
```

该变量在服务器修改后会自动广播给所有已连接客户端，开发者无需手动调用同步函数。读写权限由`NetworkVariableReadPermission`和`NetworkVariableWritePermission`两个枚举分别控制，默认写权限仅限Server。NGO内部使用**增量同步（delta compression）**机制，只传输变更值而非完整状态，降低带宽占用。

### ServerRpc 与 ClientRpc

远程过程调用（RPC）是NGO处理事件型通信的机制，分为两类：
- `[ServerRpc]`：由Client调用，在Server端执行。方法名必须以`ServerRpc`结尾。
- `[ClientRpc]`：由Server调用，在所有（或指定）Client端执行。方法名必须以`ClientRpc`结尾。

```csharp
[ServerRpc(RequireOwnership = true)]
private void FireWeaponServerRpc(Vector3 direction) { ... }
```

`RequireOwnership = true`（默认值）意味着只有该NetworkObject的Owner客户端才能发送此RPC，防止非法操控他人对象。

### 场景管理与生成流程

NGO通过`NetworkManager`单例组件统一管理整个网络会话，包括连接、断开、场景同步。启动时调用`NetworkManager.Singleton.StartServer()`、`StartClient()`或`StartHost()`。动态生成网络对象必须使用`NetworkObject.Spawn()`而非`Instantiate()`，且只能由Server端调用。所有需要网络生成的Prefab必须提前注册到`NetworkManager`的`NetworkPrefabs`列表，否则客户端无法正确实例化。

---

## 实际应用

**多人射击游戏中的玩家同步**：玩家角色Prefab挂载`NetworkObject`和`ClientNetworkTransform`组件，后者是NGO内置的Transform同步组件，将位置/旋转的控制权交给Owner客户端，避免服务器输入延迟导致的操控卡顿。血量使用`NetworkVariable<float>`存储，所有客户端实时读取并更新UI。

**实时策略游戏中的指令传递**：单位移动指令通过`[ServerRpc]`从客户端发送给服务器，服务器验证合法性后修改单位的目标位置NetworkVariable，所有客户端通过变量订阅事件`OnValueChanged`响应移动动画。

**房间大厅系统**：结合Unity的`Relay`服务（与NGO配套的中继服务），NGO可实现无需公网IP的跨网络联机。`NetworkManager`通过`UnityTransport`组件接入Relay分配的Join Code，最多支持100个并发连接（Relay服务免费层级限制）。

---

## 常见误区

**误区一：认为NetworkVariable可以存储引用类型（如List或自定义class）**
NGO的`NetworkVariable<T>`要求T实现`INetworkSerializable`接口或为基础值类型。直接传入`List<int>`等引用类型会导致编译错误或序列化失败。复杂数据应使用自定义结构体实现`INetworkSerializable`，或改用`NetworkList<T>`组件（NGO提供的专用集合类型）。

**误区二：在Client端调用`NetworkObject.Spawn()`**
`Spawn()`是服务器专属操作。在Client端调用不会抛出明显异常，但对象不会在网络中被其他玩家看到，仅在本地存在，造成游戏状态不一致。正确做法是通过`[ServerRpc]`请求服务器执行生成。

**误区三：混淆Host模式下的权限判断**
Host模式下`IsServer`和`IsClient`同时为`true`，而`IsHost`也为`true`。如果代码仅用`if (IsClient)`来过滤客户端逻辑，Host也会执行该分支，可能触发双重逻辑。需要"仅纯客户端执行"时应使用`if (IsClient && !IsServer)`。

---

## 知识关联

**与Unity引擎概述的关联**：NGO完全构建于Unity的MonoBehaviour生命周期之上，`NetworkBehaviour`类继承自MonoBehaviour，提供`OnNetworkSpawn()`和`OnNetworkDespawn()`等网络专属回调，替代部分`Start()`/`OnDestroy()`的职责。理解GameObject组件系统是使用NGO的前提，因为所有网络功能均以组件形式附加到GameObject上。

**与传输层的关系**：NGO本身不处理底层Socket，其传输层由可插拔的`INetworkTransport`接口实现，官方默认实现为`UnityTransport`（基于Unity Transport Package 1.0+，底层使用DTLS/UDP协议）。开发者也可替换为社区实现的Steam传输层（Facepunch.Transport）以接入Steam P2P网络。

**进阶方向**：掌握NGO后，可进一步学习面向ECS架构的`Netcode for Entities`（同为Unity官方框架，但针对DOTS技术栈），两者共享部分网络概念但API完全不同；或学习`Fish-Net`、`Mirror`等第三方Unity网络框架，对比不同权威模型和带宽优化策略的设计差异。