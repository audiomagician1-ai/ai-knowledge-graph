---
id: "local-multiplayer-input"
concept: "本地多人输入"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["多人"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 本地多人输入

## 概述

本地多人输入（Local Multiplayer Input）是指在同一台设备上，由多个物理控制器（手柄、键盘区域、触摸区域等）分别控制不同的游戏角色或玩家实体的输入管理机制。与单人输入不同，本地多人输入需要解决"哪个控制器属于哪个玩家"的设备分配问题，以及如何将来自多个设备的输入流并行传递给对应的游戏逻辑。

本地多人输入的概念随着家用主机的普及而成熟。1990年代的 Super Nintendo 支持最多5个手柄（通过 Multitap 扩展器），这是最早要求引擎层面处理多设备分配的典型案例。进入 Xbox 360 时代后，XInput API 明确引入了"Player Index"（0到3）的概念，正式将控制器编号与玩家编号绑定，成为现代本地多人输入设计的基础范式。

本地多人输入的重要性在于它不仅是技术问题，更是用户体验问题。《超级马里奥�派对》《火箭联盟》《Towerfall》等本地多人游戏的成功，证明了正确实现设备分配和输入隔离对游戏体验的直接影响。如果系统错误地将玩家1的手柄输入路由给玩家2，或在一个玩家断开重连后丢失分配关系，将直接破坏游戏体验。

---

## 核心原理

### 设备分配（Device Assignment）

设备分配是本地多人输入的第一步，指将特定物理设备绑定到特定玩家槽位（Player Slot）的过程。常见的分配策略有两种：

- **预分配（Pre-assignment）**：游戏启动时按设备索引顺序自动分配，手柄0给玩家1，手柄1给玩家2，依此类推。简单但缺乏灵活性。
- **按需加入（Join-on-Press）**：未分配的玩家看到"按任意键加入"提示，第一个按下特定按键的设备被分配给该玩家槽位。《Towerfall Ascension》和大多数现代本地多人游戏采用此方式。

在 Unity 的 Input System 包中，`PlayerInputManager` 组件实现了 Join-on-Press 逻辑，通过 `JoinBehavior` 枚举控制加入方式，可设为 `JoinPlayersWhenButtonIsPressed` 或 `JoinPlayersManually`。

### 输入流隔离（Input Stream Isolation）

每个玩家必须拥有独立的输入状态上下文，互不干扰。实现方式是为每个玩家维护一个独立的输入映射实例（Input Action Map Instance），而非共享同一个全局映射。

在 Unity Input System 中，`PlayerInput` 组件为每个玩家创建独立的 `InputActionAsset` 实例，通过 `PlayerInput.actions` 访问该玩家专属的动作集合。Unreal Engine 的 `Enhanced Input` 系统则通过为每个 `PlayerController` 绑定独立的 `InputMappingContext` 来实现隔离。

如果错误地使用全局单例输入管理器，玩家1和玩家2的按键事件会混入同一事件队列，导致任意一个手柄的输入影响所有玩家，这是初学者最常犯的错误。

### 分屏视口管理（Split-Screen Viewport Management）

本地多人输入通常与分屏渲染配合使用。每个玩家的摄像机视口（Viewport）需要对应其控制的角色，并且输入坐标（尤其是鼠标/触摸的屏幕坐标）需要在各玩家视口内进行局部化换算。

常见分屏布局：
- 2人：上下或左右各50%
- 3人：一种常见布局为上方50%一个视口，下方50%分成两个25%视口（如《黄金眼007》的3人模式）
- 4人：四等分

当玩家在其分屏区域内使用鼠标瞄准时，必须将全局屏幕坐标转换为该玩家视口的局部坐标，否则瞄准计算会错位。Unity 中通过 `Camera.ViewportToScreenPoint` 和 `Camera.ScreenToViewportPoint` 完成此换算。

### 设备断开与重连处理（Device Disconnect/Reconnect）

无线手柄可能在游戏中途断开。健壮的本地多人系统需要：
1. 监听设备断开事件（Unity 中为 `InputSystem.onDeviceChange`，检查 `InputDeviceChange.Disconnected`）
2. 暂停该玩家的输入，而非销毁玩家对象
3. 设备重连后，将原设备重新绑定到原玩家槽位，而非创建新玩家

PlayStation 平台的规范要求（Technical Requirements Checklist, TRC）明确规定：手柄断开必须弹出系统级对话框暂停游戏，这也说明了断开处理在发行层面的强制性要求。

---

## 实际应用

**格斗游戏的双手柄分配**：在两人对战格斗游戏中，玩家选角界面通常用颜色区分玩家1（红框）和玩家2（蓝框），系统记录各自的设备索引。若玩家1使用键盘（WASD区域）、玩家2使用手柄，则需要同时管理两种不同类型的设备，要求输入抽象层将键盘特定区域映射与手柄映射统一到相同的虚拟动作（如"左移""攻击"）。

**派对游戏的动态加入**：《超级兔子人》（Ultimate Chicken Horse）支持最多4人本地游戏，并允许游戏进行中途加入。其实现依赖对每个新按下按键的设备进行检测，动态实例化新玩家角色，并将该设备锁定给新玩家。这要求输入系统在"监听模式"（任何设备的任何按键都触发加入）和"分配模式"（每个设备只向其绑定玩家发送输入）之间切换。

**单键盘双人游戏**：部分双人游戏（如《Fireboy and Watergirl》）在单键盘上划分两组按键，WASD给玩家1，方向键给玩家2。此时两个玩家共享同一物理设备，需要在软件层面将单一键盘的输入事件按键位分发给不同玩家的输入上下文，而非依赖设备级隔离。

---

## 常见误区

**误区1：用全局静态输入管理器处理多玩家输入**
许多初学者将 `Input.GetAxis("Horizontal")` 这类全局调用用于多人游戏，这在 Unity 旧版 Input Manager 中只能读取第一个手柄的输入。正确做法是为每个玩家指定设备索引，例如 `Gamepad.all[playerIndex]` 或使用 `PlayerInput` 组件的独立实例，确保每个玩家读取自己绑定设备的数据。

**误区2：设备索引等于玩家索引**
操作系统为手柄分配的设备索引（如 XInput 的 0~3）会因为手柄拔插而改变。若玩家2断开手柄再重新插入，操作系统可能将其识别为新设备并分配不同索引。游戏内部应维护独立的玩家-设备映射表（`Dictionary<int playerSlot, InputDevice device>`），而非假设索引固定不变。

**误区3：分屏游戏中不处理视口坐标转换**
在双人分屏游戏中，若玩家2的摄像机占据屏幕下半部分，UI点击检测或鼠标射线检测如果仍使用全屏幕坐标系计算，会导致玩家2在其视口内的交互位置偏移整整半个屏幕高度。必须为每个玩家的摄像机单独设置 `pixelRect` 并在射线检测时传入局部视口坐标。

---

## 知识关联

本地多人输入直接依赖**输入设备抽象**的概念：只有当系统将物理手柄抽象为统一的"虚拟输入设备"接口后，才能用一致的方式同时管理多个不同类型的设备（手柄、键盘分区、触摸区域）。具体来说，设备抽象提供了"按设备实例查询输入状态"的能力（区别于按名称查询全局状态），这是实现多玩家输入隔离的技术前提。

在引擎架构层面，本地多人输入与**玩家管理系统**（Player Management）紧密结合，后者负责玩家槽位的生命周期（创建、暂停、销毁），而本地多人输入负责为每个槽位维护正确的设备绑定关系。两者的分工边界在于：输入系统负责"谁的输入"，玩家管理负责"谁是玩家"。