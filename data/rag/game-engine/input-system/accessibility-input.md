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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 无障碍输入

## 概述

无障碍输入（Accessible Input）是游戏引擎输入系统中专门为行动障碍、感知障碍或认知障碍玩家设计的输入适配机制，核心功能分为三个方向：按键重映射（Key Remapping）、自动辅助（Auto-Assist）和开关控制（Switch Control）。这三类机制使得无法使用标准手柄或键鼠方案的玩家，能够通过改装外设或替代控制器参与游戏。

根据世界卫生组织2023年报告，全球约13亿人存在某种形式的残障，其中上肢运动障碍、视觉障碍及认知障碍人群是游戏无障碍设计的主要目标群体。游戏行业对无障碍输入的系统性关注始于2000年代末。微软在2018年9月发布了 Xbox 自适应手柄（Xbox Adaptive Controller，售价99.99美元），这是第一款由主流游戏平台商专门为障碍玩家设计的硬件，其19个3.5mm标准插孔阵列允许接入脚踏板、吹吸管（Sip-and-Puff）、头部追踪等外部开关设备。这一硬件的出现倒逼引擎层的输入系统必须以更灵活的方式支持任意设备-动作映射，而不能假设玩家使用标准输入设备。

游戏引擎的无障碍输入功能直接影响游戏能否通过微软的 Xbox 无障碍指南认证（Xbox Accessibility Guidelines, XAG，当前版本3.4）或 PlayStation 的无障碍自评报告（Accessibility Feature Summary）。XAG 3.4版本中明确要求：游戏必须支持全按键重映射，且所有游戏功能不得强制要求玩家同时按下三个或以上按键（即禁止三键组合 Chord）。

---

## 核心原理

### 按键重映射（Key Remapping）

按键重映射的实现依赖于将物理输入（Physical Input）与游戏动作（Game Action）之间的映射表抽象为可在运行时修改的数据结构。在 Unreal Engine 5 中，这套结构由 `UInputMappingContext` 和 `UInputAction` 承载，可通过 `UEnhancedInputLocalPlayerSubsystem::AddMappingContext()` 在运行时动态切换或叠加映射上下文；在 Unity 的 Input System 包（Package 版本1.7+）中，对应结构是 `InputActionAsset` 与 `InputBinding`，每个 `InputBinding` 持有一个 `path` 字符串（例如 `<Gamepad>/buttonSouth`）指向物理设备路径。

重映射的关键技术点在于**冲突检测**：当玩家将"攻击"重映射到某个按键时，系统必须检查该按键是否已被"移动"或"系统菜单"占用，并给出提示或允许映射交换。XAG 3.4 要求重映射配置必须能够**持久化存储**。Unity Input System 提供 `SaveBindingOverridesAsJson()` 方法将覆写绑定序列化为 JSON 字符串，开发者应将此字符串写入 `PlayerPrefs` 或平台存档系统：

```csharp
// Unity Input System：保存并加载按键重映射
string overridesJson = playerInput.actions.SaveBindingOverridesAsJson();
PlayerPrefs.SetString("InputBindingOverrides", overridesJson);
PlayerPrefs.Save();

// 游戏启动时恢复
string saved = PlayerPrefs.GetString("InputBindingOverrides", string.Empty);
if (!string.IsNullOrEmpty(saved))
    playerInput.actions.LoadBindingOverridesFromJson(saved);
```

对于同时按键（Chord，如 `LT + A`）的无障碍障碍，重映射系统还应支持将组合键拆分为**顺序按键（Sequential Input）**：玩家先按 A 再按 B 等同于同时按下 A+B，容许时间窗口通常设置为500ms 到1000ms。这一参数本身也应作为无障碍选项暴露给玩家。

### 自动辅助（Auto-Assist）

自动辅助指引擎或游戏逻辑对玩家的输入进行补偿，以降低对精准操作的要求。最常见的实现有以下四类：

1. **瞄准辅助（Aim Assist / Magnetism）**：在目标周围设置"吸附区域"，当玩家瞄准方向与目标中心连线的夹角 $\theta$ 小于某阈值（通常为5°到15°）时，摄像机角速度乘以减速系数 $k$（$k \in [0.0,\ 0.7]$），使准星自动向目标靠拢。其补偿量可形式化为：

$$\Delta\omega_{assist} = \omega_{raw} \cdot (1 - k) \cdot \max\!\left(0,\ 1 - \frac{\theta}{\theta_{max}}\right)$$

其中 $\omega_{raw}$ 为原始角速度，$\theta_{max}$ 为吸附区域半角，$k$ 越小辅助力越强。《光环：无限》（Halo Infinite, 2021）在手柄端默认将 $\theta_{max}$ 设为8°、$k$ 设为0.5。

2. **按键保持辅助（Toggle Assist）**：将需要长按的动作（如奔跑、瞄镜）转换为点击切换（Toggle），彻底消除对持续按压能力的要求。《最后生还者 第二部》（The Last of Us Part II, 2020）将此功能单独列为"按钮辅助"选项，允许将全部长按操作一键转为切换模式，并获得2020年游戏无障碍年度大奖（GAconf Awards）。

3. **连击辅助（Button Mashing Assist）**：将需要高频重复按键（如 QTE 连按）替换为单次按下或长按触发，降低对手指重复运动能力的需求。Unity 中可通过 `InputAction.ReadValue<float>()` 配合定时器自动注入重复触发事件模拟连按。

4. **输入缓冲（Input Buffering）**：将玩家的输入指令在时间轴上缓存，允许提前最多200ms或延迟最多300ms执行，容纳反应时间较慢的玩家。这在格斗游戏（如《街霸6》默认缓冲窗口为8帧/133ms @60fps）中尤为重要。

### 开关控制（Switch Control）

开关控制是最极端的无障碍输入模式，面向仅能操作1到5个独立开关（Switch）的玩家——例如只能控制嘴部吹吸、眉毛肌肉或脚趾的重度肢体障碍者。其核心机制是**扫描（Scanning）**：界面或游戏动作列表按固定时间间隔（通常0.5s到3s可调）依次高亮，玩家在目标高亮时触发开关即完成选择。

在游戏引擎中实现开关控制，需要将所有游戏动作组织为一棵**动作树（Action Tree）**，支持深度优先或广度优先扫描顺序。iOS 和 Android 操作系统层面均内置开关控制支持（iOS Switch Control 和 Android Access Switch），引擎需要通过平台无障碍 API 暴露焦点（Focus）节点，使系统级开关控制可以直接驱动游戏 UI。

---

## 关键公式与数据结构

在引擎层，一套完整的无障碍输入映射可以用以下抽象数据模型描述：

```
AccessibleInputProfile
├── remapTable: Map<GameAction, List<PhysicalInput>>
│     GameAction = { "Jump", "Attack", "Pause", ... }
│     PhysicalInput = { device: "Gamepad", path: "/buttonSouth", ... }
├── toggleActions: Set<GameAction>      // 长按→切换的动作集合
├── chordWindow: int (ms)               // 顺序按键容忍窗口，默认700ms
├── inputBufferWindow: int (ms)         // 输入缓冲窗口，默认200ms
├── aimAssistStrength: float [0.0~1.0]  // 瞄准辅助强度
└── scanInterval: float (s)             // 扫描控制间隔，默认1.0s
```

该 Profile 应作为独立 JSON 文件存档，并与游戏存档**分离存储**，以便玩家在不同存档间共享无障碍配置，也便于游戏会话开始前加载（XAG 3.4 第2.6条要求）。

---

## 实际应用

**案例1：《神秘海域4》的全覆盖重映射**  
Naughty Dog 在《神秘海域4》（2016）中率先实现了主机 3A 游戏的全按键重映射，允许将所有功能（包括系统暂停键）映射到任意按键，并支持将任意双摇杆操作替换为单摇杆+按键组合，为后续 PS5 系统级重映射方案（PS5 Accessibility 功能，2021年10月固件引入）提供了先行参考。

**案例2：Unreal Engine 5 增强输入系统的无障碍扩展**  
在 UE5 中，开发者可利用 `UInputModifier` 自定义修改器实现 Toggle Assist。例如，创建一个 `UInputModifierToggle` 子类，在 `ModifyRaw_Implementation()` 中维护一个布尔状态变量，每次收到按下事件时翻转状态，并持续输出对应的激活值，从而将长按"奔跑"转换为单击切换：

```cpp
// UE5 自定义 InputModifier 实现 Toggle Assist
FInputActionValue UInputModifierToggle::ModifyRaw_Implementation(
    const UEnhancedPlayerInput* PlayerInput,
    FInputActionValue CurrentValue,
    float DeltaTime)
{
    if (CurrentValue.Get<bool>()) // 检测到按下事件
    {
        bToggleState = !bToggleState; // 翻转状态
    }
    return FInputActionValue(bToggleState); // 持续输出当前状态
}
```

**案例3：独立游戏 Celeste 的辅助模式**  
2018年发布的平台跳跃游戏《蔚蓝》（Celeste）内置了"辅助模式"（Assist Mode），允许玩家将游戏速度调整为10%到100%（步长10%），将最大跳跃次数从2次增加至无限次，并开启无敌模式。游戏设计师 Maddy Thorson 明确表示这些选项本质上是无障碍工具，此后被广泛引用为独立游戏无障碍设计的标杆案例（参见 Game Developers Conference 2019 演讲"Designing Celeste's Accessibility Features"）。

---

## 常见误区

**误区1：将无障碍选项与"作弊"等同**  
无障碍选项的目标是让玩家"能玩"，而非"更容易赢"。将 Toggle Assist 或瞄准辅助隐藏在"作弊菜单"或加以负面标签，会导致有需求的玩家因污名化而不敢使用。XAG 3.4 第1.1条要求无障碍选项应在独立的无障碍菜单中展示，不得与"简单模式"合并。

**误区2：重映射只需支持面部按键**  
完整的按键重映射必须覆盖**所有**物理输入，包括摇杆（需支持替换为按键）、触摸板（PS5）、陀螺仪以及系统级按键（如截图键、Home 键）。仅允许面部按键重映射不符合 XAG 3.4 要求，且无法覆盖上肢障碍玩家的真实需求。

**误区3：开关控制仅需支持 UI 导航**  
游戏内战斗、探索等核心玩法同样必须可通过开关控制完成。如果游戏存在实时动作操作（如格挡、闪避），应在开关控制模式下提供"自动格挡"或"行动暂停"（如《博德之门3》的回合制切换）等补偿机制，而不是仅保证菜单可操作。

**误区4：无障碍配置随存档绑定**  
将无障碍配置文件嵌入游戏存档会导致：新建存档时需重新配置、其他家庭成员共用设备时无法保留各自的无障碍设置。正确做法是将无障碍配置存储于独立的玩家配置文件（Platform User Profile）层，与游戏进度存档解耦。

---

## 知识关联

无障碍输入与以下输入系统知识点存在直接的技术依赖关系：

- **输入动作映射（Input Action Mapping）**：按键重映射的实现前提是引擎已将物理输入与游戏动作解耦