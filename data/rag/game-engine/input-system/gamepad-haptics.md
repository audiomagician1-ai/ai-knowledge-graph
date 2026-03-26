---
id: "gamepad-haptics"
concept: "手柄震动反馈"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["反馈"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
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

# 手柄震动反馈

## 概述

手柄震动反馈（Rumble/Haptic Feedback）是游戏手柄通过内置马达产生机械振动，向玩家传递触觉信息的输入系统功能。现代手柄通常在握持部位内置两个偏心旋转质量（ERM）马达，分别负责低频重震和高频细震，两者独立控制、强度范围均为 0.0 到 1.0 的归一化浮点数。

震动反馈最早见于 1997 年任天堂 Nintendo 64 的 Rumble Pak 外接配件，随后索尼在 DualShock 1（1997年）将双马达直接集成到手柄内部，确立了沿用至今的双马达硬件架构。2020 年索尼 PS5 的 DualSense 引入自适应扳机（Adaptive Trigger），将震动的概念从整体握持扩展到左右扳机的可变阻力，标志着震动反馈进入第二阶段。

在游戏引擎的输入系统中，震动反馈属于**输出通道**而非输入通道——手柄将物理状态送往引擎的同时，引擎也向手柄发送驱动指令。正确管理震动生命周期对游戏体验至关重要：震动时序若与画面、音效失去同步，玩家的沉浸感会立刻崩溃。

---

## 核心原理

### 双马达架构与频率特性

标准双马达手柄（如 Xbox Controller、DualShock 4）包含：
- **低频马达（Low-frequency rumble）**：位于手柄左侧或下方，转速较低，产生 20–80 Hz 的沉重震感，常用于爆炸、碰撞、车辆引擎等低频事件。
- **高频马达（High-frequency rumble）**：位于右侧或上方，转速较高，产生 100–300 Hz 的细密震感，常用于枪声、电流、细碎颗粒等高频事件。

向手柄发送震动指令的典型 API 调用（以 Unity 的 `Gamepad.SetMotorSpeeds` 为例）：

```csharp
Gamepad.current.SetMotorSpeeds(lowFrequency: 0.8f, highFrequency: 0.3f);
```

两个参数各自独立，取值均为 [0.0, 1.0]，0.0 表示完全停止，1.0 表示最大转速。

### 震动包络与生命周期管理

震动效果通常需要定义一个**包络曲线（Envelope Curve）**，包括起始强度、峰值保持时长、衰减斜率和结束时间，否则马达会一直持续震动直到被显式停止。常见的错误是在游戏暂停、切换场景或玩家死亡时忘记调用停止指令，导致手柄在黑屏过渡期间仍在震动。

Unity Input System 和 Unreal Engine 均要求开发者在 `OnApplicationPause(true)` 回调中手动停止所有震动通道。Unreal 中对应函数为 `UGameplayStatics::SetPlayerControllerForceFeedback`，可传入 `FForceFeedbackEffect` 资产，在编辑器内直接绘制低频和高频的强度曲线。

### 自适应扳机（Adaptive Trigger）

DualSense 的自适应扳机内置电磁执行器，可在扳机行程的任意位置施加 0 到约 8 牛顿的阻力。PS5 SDK 定义了以下几种预设模式：

| 模式 | 说明 |
|------|------|
| `Off` | 无阻力，与普通手柄相同 |
| `Rigid` | 扳机在指定位置锁死 |
| `Pulse` | 在指定行程段内产生周期性脉冲阻力 |
| `Continuous` | 在指定范围内施加持续可变阻力 |

在《Returnal》中，拉动扳机至半程可进行普通射击，拉到底才激活瞄准辅助，阻力的段落感正是通过 `Pulse` 模式实现的。Unity 对 DualSense 的自适应扳机支持需要引入 Sony 官方的 `com.unity.inputsystem.enhance` 或第三方库（如 `UniSense`），Xbox 系手柄目前无对应硬件。

### 触觉反馈与线性马达（LRA）

任天堂 Switch 的 Joy-Con 和 Nintendo Switch Pro Controller 使用**线性谐振执行器（LRA，Linear Resonant Actuator）**而非 ERM 马达。LRA 通过电磁线圈驱动一个线性运动质量块，响应时间更短（< 5 ms），可以精确再现高保真触感波形，任天堂称其为 **HD Rumble**。

HD Rumble 的指令格式并非单一强度值，而是振幅和频率的组合，频率范围约为 41 Hz 到 1252 Hz，可以模拟液体在容器中流动的数量感，例如《1-2-Switch》中通过震动猜测球的数量。在游戏引擎中调用 HD Rumble 需要使用任天堂原生 SDK（NintendoSDK），在跨平台引擎中需通过抽象层分别处理 Switch 和其他平台。

---

## 实际应用

**射击类游戏的枪械反馈**：每次开枪时，高频马达以 0.6f 强度触发约 80 ms 的短脉冲，模拟枪械后坐力；使用全自动武器时，脉冲以武器射速（如 600 RPM = 每 100 ms 一次）重复叠加，营造扫射手感。

**赛车游戏的路面纹理**：低频马达以 0.2f–0.4f 持续运转模拟引擎震动，当车辆越过路肩沙石地面时，高频马达叠加 0.5f 的随机噪声，让玩家感受到路面粗糙度的变化。

**受伤/死亡反馈**：玩家受到重击时，双马达同时以 1.0f 发送约 200 ms 的全力震动，随后在 500 ms 内衰减至 0。这一包络通常在引擎的受伤事件委托中绑定，而非在每帧 Tick 中手动驱动。

---

## 常见误区

**误区一：震动越强越有反馈感**

持续将双马达保持在 1.0f 会使玩家在数分钟内产生感觉麻木，且手柄发热明显。正确做法是将震动强度与游戏事件的"冲击权重"精确匹配：走路时不应有任何震动，近距离爆炸才值得触发 0.8f 以上的强度。

**误区二：停止震动只需发送 0.0f**

部分引擎 API 要求显式调用停止方法（如 `StopMotor` 或传入全零 `ForceFeedbackValues`），而非覆写为零值。若仅将强度参数设为 0.0f，某些平台实现仍会保持马达的最后驱动状态。

**误区三：自适应扳机与普通震动可用同一套代码处理**

自适应扳机的驱动接口完全独立于双马达接口，它控制的是机械阻力而非振动，且仅 DualSense 支持此功能。在 PC/Xbox 平台编译时必须通过 `#if UNITY_PS5` 或 Unreal 的平台宏进行条件编译隔离，否则会在非 PS5 平台产生编译错误或运行时崩溃。

---

## 知识关联

本概念直接建立在**输入设备抽象**之上：输入设备抽象层将 Xbox 手柄、DualSense、Joy-Con 等不同硬件统一映射为逻辑设备，震动反馈的发送也需通过同一抽象层——开发者调用 `Gamepad.SetMotorSpeeds` 时，底层驱动自动路由到 XInput（Windows）、GNM（PS5）或 HID 协议，无需关心物理接口差异。同时，震动反馈的触发通常由**游戏事件系统**或**动画通知（Animation Notify）**驱动，例如在近战攻击动画的第 12 帧触发手柄震动，与打击音效保持同帧对齐，确保多感官反馈的时序一致。