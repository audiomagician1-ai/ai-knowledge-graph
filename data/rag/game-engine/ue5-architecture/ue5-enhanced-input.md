---
id: "ue5-enhanced-input"
concept: "Enhanced Input System"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 2
is_milestone: false
tags: ["输入"]

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
updated_at: 2026-04-01
---


# Enhanced Input System（增强输入系统）

## 概述

Enhanced Input System（EIS）是Unreal Engine 5中取代旧版 `UPlayerInput` 与 `UInputComponent` 绑定方式的新一代输入框架，于UE 5.0正式作为插件内置，并在5.1版本后成为新项目的默认输入方案。与旧版"轴映射 + 动作映射"的静态配置不同，EIS将输入的**采集、修饰、上下文切换**三个阶段显式分离，让开发者可以在运行时动态添加或移除输入映射集合（Input Mapping Context，IMC）。

EIS的核心价值在于其**数据驱动**设计：所有输入规则存储在 `UInputAction` 和 `UInputMappingContext` 两类资产中，不需要修改C++代码即可完成大部分输入行为的调整。这对于需要频繁迭代按键方案的游戏（例如支持多控制器、多角色切换的RPG或格斗游戏）大幅降低了维护成本。

## 核心原理

### 三大核心资产

EIS围绕三类对象构建：

- **UInputAction（IA）**：描述一个"逻辑动作"，例如"跳跃"或"移动"，其值类型（`EInputActionValueType`）可以是 `bool`、`float`、`FVector2D` 或 `FVector`，对应不同维度的输入信号。
- **UInputMappingContext（IMC）**：将物理按键（如键盘 `Space`、手柄 `FaceButton_Bottom`）与 `UInputAction` 绑定，并指定附加的 Trigger 和 Modifier 列表。
- **UEnhancedInputComponent**：替代旧版 `UInputComponent`，提供 `BindAction<FInputActionValue>` 模板函数，将 IA 的触发事件绑定到C++或蓝图回调。

### Input Trigger（输入触发器）

Trigger 决定了一个物理输入何时真正激活 `UInputAction`。内置 Trigger 类型包括：

| Trigger类型 | 行为描述 |
|---|---|
| `Pressed` | 按键从未按下变为按下的瞬间触发一次 |
| `Released` | 松开时触发 |
| `Hold` | 持续按住超过 `HoldTimeThreshold`（默认0.2秒）后触发 |
| `Tap` | 按下并在 `TapReleaseTimeThreshold`（默认0.2秒）内松开 |
| `ChordAction` | 依赖另一个 IA 同时处于激活状态（组合键实现） |

Trigger 可以叠加：同一按键绑定可以同时挂载 `Hold` 和 `Released`，实现"长按执行A、短按执行B"的逻辑，而无需额外代码判断。

### Input Modifier（输入修饰器）

Modifier 在 Trigger 评估前对原始输入值做数学变换。常用内置 Modifier：

- **DeadZone**：将 `[-LowerThreshold, LowerThreshold]`（默认0.2）范围内的摇杆值映射为0，消除手柄漂移。
- **Swizzle Input Axis Values**：重排 `FVector` 各分量，例如将摇杆 Y 轴映射到世界坐标 Z 轴。
- **Negate**：对值取反，常用于让同一 IA 的两个按键分别控制正负方向。
- **Scalar**：乘以固定系数，可用于灵敏度缩放。

Modifier 按列表顺序依次执行，形成管线（Pipeline），最终输出值传递给 `FInputActionValue`。

### 上下文优先级与动态切换

`UEnhancedInputLocalPlayerSubsystem` 提供 `AddMappingContext(IMC, Priority)` 和 `RemoveMappingContext(IMC)` 接口。Priority 为整数，数值越大优先级越高。当两个 IMC 绑定同一物理键到不同 IA 时，高优先级的 IMC 会**阻断（Consume）**低优先级的处理，除非低优先级的绑定设置了 `bBlockInput = false`。例如：载具模式 IMC（Priority=1）覆盖步行模式 IMC（Priority=0），进入载具时 `AddMappingContext` 即可完成切换，离开时 `RemoveMappingContext` 还原，全程无需修改 Character 蓝图逻辑。

## 实际应用

**角色移动输入**：创建 `IA_Move`，类型设为 `FVector2D`。在 IMC 中，将键盘 `W` 绑定到 IA_Move 并添加 Modifier：`Swizzle(YXZ)`，使 Y 分量对应前后；将 `S` 绑定同一 IA 并额外添加 `Negate`，实现向后移动。这样四个方向键共用一个 IA，`AddMovementInput` 只需响应单个回调。

**载具与步行的输入切换**：步行 IMC Priority=0 包含跳跃、交互等动作；驾驶 IMC Priority=1 包含油门、转向。当玩家进入载具时，仅调用 `AddMappingContext(VehicleIMC, 1)`，驾驶输入立即生效，且自动屏蔽步行的跳跃输入，不需要任何 `if` 分支判断。

**蓄力攻击**：使用 `Hold` Trigger（`HoldTimeThreshold = 0.5f`）和 `Pressed` Trigger 绑定到同一物理键但不同 `UInputAction`：`IA_AttackLight`（Pressed）与 `IA_AttackCharge`（Hold），分别触发轻攻击与蓄力攻击，逻辑完全在数据资产中配置。

## 常见误区

**误区一：认为旧版 AxisMapping 与 EIS 可以混用而不产生冲突**
若项目启用了 Enhanced Input 插件但未将 `DefaultPlayerInputClass` 改为 `UEnhancedPlayerInput`（在 `DefaultInput.ini` 中设置），旧版轴映射仍然生效，会导致某些输入被处理两次或互相干扰。迁移到 EIS 必须同步修改项目设置中的 `Input > Default Player Input Class` 和 `Default Input Component Class`。

**误区二：误以为 Modifier 在 Trigger 之后执行**
实际上管线顺序是：**Raw Input → Modifier Pipeline → Trigger Evaluation → Action Value Output**。Modifier 先对原始值做变换，Trigger 再判断变换后的值是否满足激活条件。因此 DeadZone Modifier 必须排在 Trigger 之前，若顺序配置错误，`Hold` Trigger 可能因为接收到漂移的原始值而提前激活。

**误区三：为每个按键方向创建独立的 UInputAction**
旧版设计习惯会为"向前""向后"分别创建两个动作。在 EIS 中，正确做法是创建单个 `FVector2D` 类型的 `IA_Move`，利用 `Negate` 和 `Swizzle` Modifier 处理方向差异，多个按键绑定到同一 IA。这样回调函数只有一个，`FInputActionValue::Get<FVector2D>()` 已包含完整的二维向量信息。

## 知识关联

**前置概念——Actor-Component模型**：EIS 的绑定发生在 `AActor` 初始化阶段的 `SetupPlayerInputComponent(UInputComponent*)` 回调中，需要将参数强制转型为 `UEnhancedInputComponent*` 才能调用 `BindAction`。理解 Component 的生命周期（`BeginPlay` 前完成绑定）是正确配置 EIS 的前提；`UEnhancedInputLocalPlayerSubsystem` 本身也是 `ULocalPlayer` 的 Subsystem，依赖 Subsystem 机制的 Actor-Component 管理体系运作。

**后续概念——输入系统概述**：掌握 EIS 的具体实现后，可以横向对比UE整体输入处理流水线：从操作系统原始事件 → `FSlateApplication` → `APlayerController::InputKey` → EIS处理层的完整路径，以及 EIS 与 UI 输入（`UWidget` 的 `OnKeyDown`）之间的优先级关系，形成对UE5输入架构的全局视图。