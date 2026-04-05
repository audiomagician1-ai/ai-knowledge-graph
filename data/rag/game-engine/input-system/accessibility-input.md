---
id: "accessibility-input"
concept: "无障碍输入"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["可达性"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 无障碍输入

## 概述

无障碍输入（Accessible Input）是游戏引擎输入系统中专门为行动障碍、感知障碍或认知障碍玩家设计的一套输入适配机制。其核心功能包括三个方向：按键重映射（Key Remapping）、自动辅助（Auto-Assist）和开关控制（Switch Control）。这三类机制使得标准手柄、键鼠方案无法使用的玩家，能够通过改装外设或替代控制器参与游戏。

无障碍输入的系统性关注始于2000年代末。微软在2018年发布了 Xbox 自适应手柄（Xbox Adaptive Controller），这是第一款由主流游戏平台商专门为障碍玩家设计的硬件，其3.5mm插孔阵列允许接入脚踏板、吹吸管等外部开关设备。这一硬件的出现倒逼引擎层的输入系统必须以更灵活的方式支持任意设备-动作映射，而不是假设玩家使用标准输入设备。

游戏引擎的无障碍输入功能直接影响游戏能否通过微软的 Xbox 无障碍认证（Xbox Accessibility Guidelines, XAG）或 PlayStation 的无障碍自评报告（Accessibility Feature Summary）。XAG 1.3版本中明确要求，游戏必须支持全按键重映射，且所有游戏功能不得强制要求同时按下三个或以上按键。

---

## 核心原理

### 按键重映射（Key Remapping）

按键重映射的实现依赖于将物理输入（Physical Input）与游戏动作（Game Action）之间的映射表抽象为可运行时修改的数据结构。在 Unreal Engine 中，这套结构由 `UInputMappingContext` 和 `UInputAction` 承载；在 Unity 的 Input System 包中，对应的是 `InputActionAsset` 与 `InputBinding`。

重映射的关键技术点在于**冲突检测**：当玩家将"攻击"重映射到某个按键时，系统必须检查该按键是否已被"移动"或"系统菜单"占用，并给出提示或允许交换。XAG 要求重映射配置必须能够**持久化存储**——Unity Input System 提供 `SaveBindingOverridesAsJson()` 方法将覆写绑定序列化为 JSON 字符串，开发者应将此字符串写入 `PlayerPrefs` 或平台存档系统。

对于同时按键（Chord，如 `LT + A`）障碍，重映射系统还应支持将组合键拆分为顺序按键（Sequential Input），即玩家先按 A 再按 B 等同于同时按下 A+B，容许时间窗口通常设置为 500ms 到 1000ms。

### 自动辅助（Auto-Assist）

自动辅助指引擎或游戏逻辑对玩家的输入进行补偿，以降低对精准操作的要求。最常见的实现有三类：

1. **瞄准辅助（Aim Assist）**：通过在目标周围设置"吸附区域"（Magnetism Zone），当玩家的瞄准方向与目标的夹角小于某个阈值（通常为5°到15°）时，摄像机旋转速度会被乘以一个减速系数（0.0到0.7之间），使准星自动靠近目标。
2. **按键保持辅助（Hold Assist / Toggle Assist）**：将需要长按的动作（如奔跑、瞄镜）转换为点击切换（Toggle），彻底消除对持续按压能力的要求。《最后生还者 第二部》将此功能单独列为"按钮辅助"，允许把全部长按操作一键转为切换模式。
3. **连击辅助（Button Mashing Assist）**：将需要快速重复按键的 QTE 场景，改为单次长按或持续按住即可完成，典型实现是将"在2秒内按下X键15次"等效为"按住X键2秒"。

### 开关控制（Switch Control）

开关控制是最底层的无障碍输入模式，专为只能触发一个或两个物理开关的玩家（如仅能用面部肌肉控制的玩家）设计。其工作原理是**扫描（Scanning）**：系统在屏幕上的可交互元素或动作列表之间自动循环高亮，玩家在期望选项高亮时触发其唯一的开关信号来确认选择。

扫描速度（Scan Speed）是开关控制的核心参数，通常应允许玩家在 0.5s 到 8s 之间自由调整每个选项的停留时间。扫描模式还分为**自动扫描**（Auto Scanning，无需玩家触发下一项）和**步进扫描**（Step Scanning，玩家主动触发进入下一项）两种，后者赋予玩家更多节奏控制权，适合反应速度较慢但可以精准触发开关的用户。

在游戏引擎中实现开关控制，通常需要在输入系统之上构建一个**动作菜单层（Action Menu Layer）**，将实时游戏动作（移动、攻击、交互）转化为菜单选项的枚举遍历，而非直接映射到模拟轴或即时按键。

---

## 实际应用

**《地平线：西之绝境》（Horizon Forbidden West）**在其无障碍选项中完整实现了上述三类机制：全按键重映射支持导出配置方案并为其命名，允许玩家保存多套方案随时切换；战斗中的瞄准辅助提供了5个强度等级（无、低、中、高、自动锁定），每个等级对应不同的磁吸角度阈值；所有长按交互（如攀爬锁点、拔取草药）均可切换为单次点击的 Toggle 模式。

在 Unity 开发实践中，接入无障碍重映射的典型步骤是：在 `InputActionAsset` 中为每个 `InputAction` 的绑定调用 `ApplyBindingOverride(int bindingIndex, string path)` 方法，其中 `path` 为设备路径字符串（如 `<Gamepad>/buttonSouth`），然后通过 `SaveBindingOverridesAsJson()` 将整个资产的覆写状态序列化存储。加载存档时，调用 `LoadBindingOverridesFromJson(string json)` 即可完整恢复玩家自定义的映射方案。

---

## 常见误区

**误区一：将瞄准辅助与无障碍混为一谈**
标准多人对战中的瞄准辅助（Aim Assist）是为了补偿手柄摇杆精度劣于鼠标的问题，面向的是全体手柄玩家。无障碍输入中的自动瞄准（Auto-Aim 或 Full Aim Assist）更进一步，允许完全锁定目标而无需玩家施加方向输入，两者的实现强度和应用场景有本质区别，不能用同一套参数满足两类需求。

**误区二：按键重映射只需在 UI 层处理**
部分开发者认为重映射只是"显示名称的更改"，实际上必须在输入动作层面完成物理键到动作的重新绑定，否则当游戏内弹出"按 A 键继续"的提示图标时，图标仍会显示原始按键而非玩家重映射后的按键，导致提示与实际操作脱节。正确的做法是在提示系统中通过 `InputBinding` 查询当前有效绑定，动态生成图标。

**误区三：开关控制可以在游戏发布后用系统级工具解决**
iOS 和 Android 的操作系统级开关控制（Switch Access）确实可以在不修改游戏的情况下提供基础扫描功能，但其扫描的目标是 UI 控件树，无法处理游戏主视角中的实时动作（如格挡、闪避的时机性操作）。因此对于动作类游戏，引擎内部的开关控制模式是操作系统工具无法替代的。

---

## 知识关联

无障碍输入建立在输入系统概述所介绍的**设备抽象层**与**动作映射**机制之上。正是因为输入系统将物理按键与游戏逻辑解耦为两个独立层级，按键重映射才得以在不修改游戏逻辑代码的前提下实现。如果一个引擎的输入系统直接在游戏逻辑中硬编码物理键值（如 `if (key == KeyCode.Space)`），则重映射必须逐一修改游戏代码，工程代价极高。

开关控制与 UI 导航系统（Gamepad UI Navigation）共享"焦点遍历"逻辑，理解 UI 系统中的焦点树（Focus Tree）和焦点移动事件（Focus Move Event）有助于更快实现动作菜单扫描层。自动辅助中的瞄准磁吸则涉及角色控制器和摄像机系统的协作，其减速系数的计算通常在摄像机旋转管线的后处理阶段完成，而非在输入采样阶段。