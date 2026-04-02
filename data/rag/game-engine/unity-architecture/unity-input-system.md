---
id: "unity-input-system"
concept: "Unity Input System"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 2
is_milestone: false
tags: ["输入"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 54.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.5
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Unity 新输入系统

## 概述

Unity 新输入系统（Input System Package）是 Unity 于 2019 年作为独立 Package 发布、并在 Unity 2020.1 起成为官方推荐替代方案的输入处理架构。它的包名为 `com.unity.inputsystem`，通过 Package Manager 安装，与旧版 `UnityEngine.Input` 类并行存在但互不兼容。旧系统基于帧轮询（每帧调用 `Input.GetAxis()`），而新系统采用事件驱动模型，大幅降低了不必要的 CPU 开销。

新系统的设计目标是解决旧 `Input` 类的三个痛点：硬编码设备绑定、缺乏运行时重绑定支持、以及多人本地输入混用困难。新系统将"按什么键"与"触发什么行为"彻底解耦，开发者通过配置 `InputActionAsset` 资产文件管理所有绑定，无需修改代码即可支持键盘、手柄、触摸屏和 XR 控制器。

## 核心原理

### Action、Binding 与 Processor 三层模型

**Action（输入动作）** 是新系统的最小逻辑单元，代表一个游戏行为（如"跳跃""移动"）。每个 Action 有三种类型：`Value`（持续返回数值，适合摇杆）、`Button`（只关心按下/释放，适合按键）、`PassThrough`（不进行状态合并，适合鼠标移动）。选错类型会导致事件丢失或重复触发。

**Binding** 将具体的物理输入路径绑定到 Action 上。路径格式为 `<Device>/control`，例如键盘空格键写作 `<Keyboard>/space`，PS4 手柄叉键写作 `<DualShockGamepad>/buttonSouth`。一个 Action 可以拥有多个 Binding，系统会自动合并它们的值。Binding 还支持 **Composite**，例如 `1D Axis` 组合将 `<Keyboard>/a` 设为负方向、`<Keyboard>/d` 设为正方向，返回范围 `[-1, 1]` 的浮点值。

**Processor（处理器）** 是挂载在 Binding 或 Action 上的值变换管线。内置处理器包括 `Normalize`（将值规范到指定范围）、`Invert`（反转方向）、`DeadZone`（死区裁切，默认下限 0.125、上限 0.925）和 `ScaleVector2`（缩放二维输入）。多个处理器按配置顺序依次执行，形成处理链。

### InputActionAsset 与控制方案

所有 Action 组织在 **InputActionAsset**（`.inputactions` 文件）内。资产内部分为若干 **Action Map**，每个 Map 代表一种输入上下文（如 `Gameplay`、`UI`、`Vehicle`）。同一时刻可以启用多个 Map，但同名 Action 优先级以最后启用的 Map 为准。

**Control Scheme（控制方案）** 定义了"使用哪些设备"的规则。例如 `Keyboard&Mouse` 方案要求同时具备 `Keyboard` 和 `Mouse` 设备才能激活；`Gamepad` 方案只需一个 `Gamepad`。系统会根据当前连接的设备自动切换控制方案，也可通过 `PlayerInput.SwitchCurrentControlScheme()` 手动切换。

### 事件回调与 PlayerInput 组件

代码中订阅 Action 有两种主流方式。第一种是直接订阅委托：

```csharp
inputActions.Gameplay.Jump.performed += ctx => Jump();
inputActions.Gameplay.Move.performed += ctx => move = ctx.ReadValue<Vector2>();
```

第二种是使用 **PlayerInput** 组件，在 Inspector 中选择通知方式：`Send Messages`（调用 `GameObject` 上的 `OnJump()`）、`Broadcast Messages`（向子物体广播）或 `Invoke Unity Events`（直接连接 UnityEvent）。`PlayerInput` 还内置了多人输入管理，通过 `PlayerInputManager` 最多支持 `8` 个本地玩家独立绑定设备。

## 实际应用

**多平台角色移动** 是最典型用例。创建 `Move` Action，类型设为 `Value`，Control Type 选 `Vector2`；添加 `WASD Composite Binding` 供键盘使用，同时添加 `<Gamepad>/leftStick` 供手柄使用。在 `Update` 中通过 `moveAction.ReadValue<Vector2>()` 读取，两种设备无需额外判断，自动合并。

**运行时重绑定** 可通过 `InputActionRebindingExtensions.PerformInteractiveRebinding()` 实现。调用后系统进入监听状态，玩家按下任意键后自动写入新 Binding 路径，整个流程无需手写解析代码，绑定结果可序列化为 JSON 字符串存储到 `PlayerPrefs`。

**XR 手柄震动** 通过 `InputSystem.QueueEvent()` 搭配 `DualMotorRumbleCommand` 结构体发送，左右电机强度各为 `0f~1f` 浮点值，此功能在旧 `Input` 系统中完全不可用。

## 常见误区

**误区一：混用新旧输入系统**。在 Project Settings → Player → Active Input Handling 中选择 `Both` 可同时启用，但 `Input.GetKey()` 与新系统的事件回调会产生重复处理逻辑，且旧系统不支持新系统的 Action Map 切换。正式项目应选 `Input System Package (New)`，彻底关闭旧系统。

**误区二：忘记在 OnDisable 中取消订阅**。直接订阅 `performed` 委托时，若不在 `OnDisable()` 中调用 `inputActions.Disable()` 或手动 `-=` 取消注册，场景卸载后委托引用仍然存活，导致 `MissingReferenceException` 或内存泄漏。使用 `PlayerInput` 组件的 `Invoke Unity Events` 模式可规避此问题，因为组件生命周期由 Unity 管理。

**误区三：误解 Action 的 started / performed / canceled 三个阶段**。对于 `Button` 类型，`started` 在按下瞬间触发，`performed` 也在按下瞬间触发（两者几乎同时），`canceled` 在松开时触发。对于持有 `Hold` Interaction 的 Button，`performed` 会延迟到默认 `0.4` 秒长按后才触发，`started` 仍在按下瞬间触发，若只订阅 `performed` 则会误以为"单击没有反应"。

## 知识关联

学习新输入系统的前提是理解 Unity 的 **MonoBehaviour 生命周期**（`Awake`、`OnEnable`、`Update`、`OnDisable`），因为 Action 的 Enable/Disable 必须与组件生命周期同步。同时需要熟悉 **ScriptableObject** 概念，因为 `InputActionAsset` 本质上是一个 ScriptableObject 资产。

掌握新输入系统后，可进一步学习 **输入系统架构设计**，例如基于新系统封装输入抽象层（Input Facade），将 `InputActionReference` 暴露为可配置字段，实现输入逻辑与游戏逻辑的完全解耦。也可结合 **Unity Multiplayer（Netcode for GameObjects）** 学习网络环境下的本地输入预测与服务端校验，此时新系统的事件驱动模型能精确记录每帧输入时间戳，优于旧系统的轮询方式。