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

Steam Input 是 Valve 公司于 2016 年随 Steam Controller 发布时推出的输入抽象层系统，后续版本扩展为通用控制器配置框架，支持 Xbox 手柄、PlayStation DualShock/DualSense、Nintendo Switch Pro Controller 以及 Steam Deck 内置手柄等数十种设备。它的核心功能是在操作系统原生驱动层与游戏应用层之间插入一个中间层，让玩家可以在 Steam 客户端界面中为任意游戏重新映射按键、摇杆和触摸板，而游戏本身只需接收经过翻译后的统一输入信号。

Steam Input API（SIAPI）与传统的 XInput/DirectInput 路径截然不同。传统路径下，游戏直接向操作系统查询设备原始状态；而 SIAPI 路径下，Steam 进程拦截设备信号，应用开发者在游戏代码中调用 `SteamInput()->GetAnalogActionData()` 或 `SteamInput()->GetDigitalActionData()` 这类接口，获取的是已经过配置层处理的"动作"数据，而非原始按钮编号。这种设计使得 Steam Deck 上的触摸板、陀螺仪等非标准输入源可以无缝模拟传统手柄输入。

对游戏开发者而言，集成 Steam Input 的实际意义在于：Steamworks SDK 中的 Steam Input API 允许游戏注册具名动作集（Action Set），例如将"游泳"状态和"战斗"状态分别定义为两个不同的动作集，并在运行时切换，从而让同一个物理按键在不同游戏情境下触发不同行为，而无需在游戏代码层面硬编码这种切换逻辑。

---

## 核心原理

### 动作与动作集（Actions & Action Sets）

Steam Input 的映射单元不是"按下A键"这样的物理描述，而是开发者自定义的语义化动作名称，例如 `"jump"`、`"fire"`、`"move"`。开发者在 VDF（Valve Data Format）格式的动作配置文件 `game_actions_APPID.vdf` 中声明所有动作及其所属动作集，然后在代码中通过 `SteamInput()->GetActionSetHandle("InGameControls")` 获取句柄，再用 `SteamInput()->ActivateActionSet(inputHandle, setHandle)` 在运行时激活指定集合。数字动作（Digital Action）代表布尔值输入，模拟动作（Analog Action）代表二维向量输入，二者完全独立于底层设备类型。

### 输入信号转换流水线

物理设备的原始信号经过以下流水线处理：
1. **设备驱动采集**：Steam 客户端通过 HID 协议以约 1000Hz 轮询设备（Steam Controller 和 Steam Deck 内置手柄）或使用系统 API 采集其他手柄数据。
2. **配置层变换**：应用玩家自定义配置，包括死区形状（圆形/十字/自定义）、灵敏度曲线、陀螺仪到摇杆的映射参数等。
3. **模式映射**：触摸板可配置为"摇杆模式"、"鼠标模式"或"按钮板模式"，同一硬件在不同模式下产生完全不同的语义输出。
4. **动作分发**：最终结果通过共享内存或命名管道传递给游戏进程，游戏调用 SIAPI 接口读取。

### 陀螺仪输入与运动控制

Steam Input 对陀螺仪的处理尤为精细，这是其区别于纯 XInput 的重要特性。陀螺仪原始数据单位为弧度/秒（rad/s），Steam 配置界面允许设置"陀螺仪灵敏度"（实质上是 rad/s 到像素/帧的比例系数）、"稳定"功能（低速运动时应用额外死区）以及"陀螺仪激活条件"（例如右摇杆推入触发陀螺仪辅助瞄准）。DualSense 和 Switch Pro Controller 的陀螺仪数据通过 Steam Input 统一封装后，游戏代码只需调用 `SteamInput()->GetMotionData()` 即可获取，无需针对不同厂商的陀螺仪协议分别适配。

### Steam Deck 专项适配

Steam Deck 的物理布局包含两个触摸板、两个摇杆、四个背键（L4/L5/R4/R5）和陀螺仪，这些在 XInput 标准中均无对应定义。Steam Input 为 Deck 提供了专属的"Steam Deck"控制器配置模板，开发者可以在 VDF 文件中针对 `controller_steamdeck` 设备类型单独定义配置，而不影响其他手柄设备的配置。Deck 的触摸板默认在游戏运行时作为鼠标操控，但 SIAPI 集成的游戏可将其配置为径向菜单或自定义虚拟摇杆。

---

## 实际应用

**《赛博朋克 2077》的 Steam Deck 优化**：CD Projekt Red 在 1.6 补丁中为 Steam Deck 单独提供了 Steam Input 配置，将左触摸板配置为快速物品轮盘（径向菜单模式），右触摸板配置为鼠标模式用于精准瞄准，同时启用右摇杆按压触发的陀螺仪辅助。这套配置通过 Steam Workshop 共享，玩家无需修改任何游戏内设置即可体验。

**独立游戏集成示例**：在 Unity 项目中集成 Steamworks.NET 后，只需在 `Awake()` 中调用 `SteamInput.Init(false)`（参数表示不明确显示 Steam Input 覆盖提示），然后在 `Update()` 中每帧调用 `SteamInput.RunFrame()` 刷新状态，再通过动作句柄读取输入。整套集成代码量不超过 50 行，相比为每种手柄设备单独处理输入事件要精简得多。

**手柄图标自动适配**：SIAPI 提供 `SteamInput()->GetGlyphForActionOrigin()` 接口，可根据当前连接的实际手柄类型返回对应按键图标（例如 Xbox 的ABXY或 PlayStation 的△○×□），游戏 UI 无需硬编码图标判断逻辑，Valve 的图标资源库已包含主流手柄的完整图标集。

---

## 常见误区

**误区一：Steam Input 会覆盖游戏内的键位设置**

许多开发者误以为启用 Steam Input 后玩家的游戏内键位设置会失效。实际上，Steam Input 默认只在游戏未调用 SIAPI 初始化时以"兼容模式"运行，此时 Steam 将手柄信号模拟为 XInput 或键鼠输出，游戏内设置仍然有效。只有游戏主动调用 `SteamInput()->Init()` 声明使用 SIAPI 后，Steam Input 层才会完全接管并通过动作系统工作，两种模式不会同时激活。

**误区二：所有 Steam 游戏都自动获得 Steam Input 支持**

Steam 客户端确实会对所有游戏默认启用手柄兼容层（将手柄模拟为 XInput），但"兼容模式"与"原生 SIAPI 集成"是本质不同的两件事。兼容模式下，陀螺仪无法传递给游戏，触摸板只能模拟摇杆，动作集切换功能完全不可用。要获得完整 Steam Input 功能，开发者必须显式集成 Steamworks SDK 并提交 VDF 动作配置文件。

**误区三：Steam Input 仅适用于 Steam Deck**

虽然 Steam Deck 是 Steam Input 功能最受益的平台，但 Steam Input API 同样在 Windows/Linux/macOS 桌面端有效，且对 PlayStation DualSense 的触摸板和自适应扳机的支持（通过 Steam Input 抽象后）甚至早于许多游戏引擎的原生 DualSense 支持。2020 年 Steam 客户端更新后，DualSense 的触觉反馈参数也可通过 `SteamInput()->TriggerHapticPulse()` 在非 Deck 设备上调用。

---

## 知识关联

**前置概念——输入映射**：理解输入映射中"物理键→逻辑动作"的转换思路是学习 Steam Input 动作集设计的直接基础。Steam Input 的 VDF 配置文件本质上是一个更加复杂的输入映射表，只是映射规则由运行时的 Steam 客户端解析而非游戏引擎内部系统处理。掌握了"动作名"与"绑定"分离的基本思想后，Steam Input 的 Action Set 分层设计会更易理解。

**延伸方向——Steamworks SDK 其他模块**：Steam Input API 是 Steamworks SDK 的子集，深入使用时会涉及到 Steam 的云存储（用于同步玩家自定义配置）、Steam Workshop（用于共享社区手柄配置）以及 Steam Remote Play（Steam Input 是 Remote Play Together 多人共享控制的底层基础）。理解这些模块的协作方式有助于构建完整的 Steam 平台游戏发行方案。