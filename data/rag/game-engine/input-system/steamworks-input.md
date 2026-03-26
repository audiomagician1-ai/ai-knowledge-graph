---
id: "steamworks-input"
concept: "Steam Input"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["平台"]

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


# Steam Input

## 概述

Steam Input 是 Valve 于 2016 年随 Steam Controller 一同正式推出的输入抽象层系统，最初称为 Steam Controller API，后更名为 Steam Input API。其核心职能是在游戏与物理输入设备之间插入一个统一的翻译层，使开发者无需为每种手柄单独编写适配代码——无论玩家使用 Xbox 手柄、PlayStation DualSense、任天堂 Pro Controller，还是 Steam Deck 的内置控制器，游戏只需调用同一套 API。

该系统的设计动机源于 Steam Controller 独特的双触控板硬件：传统手柄 API（如 XInput）无法表达触控板的连续坐标输入，Valve 因此设计了一套"动作集（Action Set）"抽象，将物理按键与游戏逻辑动作解耦。2018 年，Steam Input 扩展为支持所有主流手柄，并在 Steam 客户端中内置了通用配置界面，俗称"Big Picture 控制器配置"。

对游戏引擎开发者而言，Steam Input 的重要性在于：它允许玩家在 Steam 客户端层面重映射任意按键，甚至将陀螺仪、触控板映射为鼠标或摇杆输出，而无需游戏自身提供这些功能。这意味着如果游戏直接使用 XInput 或 SDL，玩家的 Steam Input 配置会在游戏看到输入之前完成转换，形成一条完整的虚拟化链路。

---

## 核心原理

### 动作集与动作层（Action Sets & Action Layers）

Steam Input 的基本单元不是"按键"，而是"动作（Action）"。开发者在游戏的 `game_actions_X.vdf` 配置文件中声明动作集，例如：

```
"ActionSet_InGame"
{
    "Button"   "Jump"
    "Button"   "Attack"
    "AnalogTrigger" "Accelerate"
    "StickPadGyro"  "Move"
}
```

每个动作集代表一种游戏状态下的完整输入语义。动作层（Action Layer）则是叠加在动作集之上的增量覆盖，例如"载具模式层"只覆盖移动相关动作，其余动作继承基础集，避免重复配置。游戏运行时调用 `ActivateActionSet(inputHandle, actionSetHandle)` 切换当前活跃集。

### 输入信号的虚拟化路径

Steam Input 有两种工作模式：**Native 模式**（游戏主动调用 Steam Input API）和 **Legacy 模式**（Steam 将手柄输出伪装成 XInput 或 DirectInput 设备）。在 Legacy 模式下，Steam 的 Virtual Controller 驱动在操作系统层面注册一个虚拟手柄，真实设备信号经 Steam 处理后由虚拟设备转发。这意味着游戏通过 XInput 轮询时，实际读取的是经过重映射的虚拟数据，而非原始硬件数据。这套机制解释了为何 PlayStation 手柄可以在只支持 XInput 的游戏中正常工作。

### Steam Deck 专项特性

Steam Deck 运行 SteamOS，其内置控制器通过 Steam Input 原生接入，提供以下 Deck 专属输入源：

- **左右触控板**：分辨率约为 1920×1080 的电容式触控板，可输出绝对坐标或模拟摇杆
- **陀螺仪（6轴 IMU）**：支持俯仰（Pitch）、偏航（Yaw）、滚转（Roll）三轴，常用于瞄准辅助
- **触控板触觉反馈（Haptics）**：通过 `TriggerRepeatedHapticPulse` API 控制脉冲频率（单位：微秒）

Steam Deck 默认以 Native Steam Input 模式运行，如游戏未集成 API，则自动降级为 XInput 仿真。开发者可在 Steamworks 后台的"Steam Input 默认配置"中上传官方推荐映射，玩家首次连接时自动应用。

### API 调用流程

集成 Steam Input API 的最小流程如下：

1. 调用 `SteamInput()->Init(false)` 初始化（参数 `false` 表示不显示手柄图标覆盖层）
2. 每帧调用 `SteamInput()->RunFrame()` 驱动数据更新
3. 调用 `GetConnectedControllers(handles)` 枚举当前连接设备
4. 用 `GetAnalogActionData` / `GetDigitalActionData` 读取动作状态

数字动作返回 `InputDigitalActionData_t`，其中 `bState`（bool）表示当前是否按下；模拟动作返回 `InputAnalogActionData_t`，`x`/`y` 为 -1.0 到 1.0 的浮点值。

---

## 实际应用

**Unity 集成示例**：Unity 项目若通过 Steamworks.NET 插件使用 Steam Input，需在 `Assets/StreamingAssets` 目录放置 `controller_config` 文件夹并包含 `.vdf` 动作配置文件。Unity 的 Input System 包本身不直接集成 Steam Input，开发者通常编写适配器将 `GetDigitalActionData` 的结果转发至自定义 `InputAction`。

**Godot 4 与 Steam Deck**：Godot 4 通过 GodotSteam 插件暴露 Steam Input API。由于 Godot 的 Input Map 系统与 Steam Input 动作集是平行独立的结构，推荐做法是在 Steam Input 层定义高层语义动作（如 `ui_confirm`），游戏内 Godot 的 InputMap 只处理非 Steam 平台的回退逻辑。

**在线游戏的手柄图标提示**：Steam Input API 提供 `GetGlyphSVGForActionOrigin` 函数，根据当前控制器类型返回对应按键图标的 SVG 数据，分辨率无关。这使得 UI 可以自动在 Xbox A 键图标与 PlayStation ✕ 键图标之间切换，无需硬编码图片资源。

---

## 常见误区

**误区一：Steam Input 与 XInput 可以同时读取同一设备**

许多开发者在集成 Steam Input API 后，同时保留了 XInput 轮询代码，以为二者互补。实际上，当 Steam Input 以 Native 模式运行时，Valve 建议将 XInput 手柄加入屏蔽名单（通过 `EnableDeviceCallbacks` 监听）。若不加区分地同时读取，Xbox 手柄的输入会被 Steam Input 拦截导致 XInput 端读取到空数据，而开发者误以为是设备兼容性问题。

**误区二：所有 Steam Deck 游戏必须集成 Steam Input API**

Steam Deck 的验证标准（Deck Verified）并不强制要求 Native Steam Input 集成。Legacy 模式下 Steam 的 XInput 仿真可让绝大多数游戏正常运行。强制集成的场景只有当游戏需要读取触控板原始坐标或陀螺仪数据时，因为这两类输入无法通过 XInput 仿真传递。

**误区三：Steam Input 配置保存在游戏本地**

Steam Input 的控制器配置存储在 Steam 云端，路径格式为 `userdata/<steamid>/241100/remote/controller_config/`，其中 `241100` 是 Steam Input 配置应用的 AppID。这意味着玩家换机后配置自动同步，但也意味着游戏无法在自身存档目录中找到或修改这份配置，必须通过 Steamworks API 或 Steam 客户端界面操作。

---

## 知识关联

Steam Input 以**输入映射（Input Mapping）**为基础：理解抽象动作与物理按键的绑定关系是使用 Steam Input 动作集的前提，Steam Input 的 Action Set 机制本质上是将状态机式的上下文切换引入输入映射系统。与传统引擎内置的输入映射不同，Steam Input 的映射发生在引擎之外的 Steam 层，两套系统共存时需要明确各自的职责边界。

在 Steam Deck 开发实践中，Steam Input 与 **Steamworks SDK** 深度绑定——所有 API 调用均通过 `ISteamInput` 接口完成，该接口在 Steamworks SDK 1.50 版本后才稳定支持完整的 Deck 输入特性（包括触觉反馈 API `TriggerSimpleHapticEvent`）。若项目面向 PC 多平台发布，还需考虑与 SDL3 的 `SDL_GameController` API 的兼容策略，两者在抽象层次上相似但互不依赖。