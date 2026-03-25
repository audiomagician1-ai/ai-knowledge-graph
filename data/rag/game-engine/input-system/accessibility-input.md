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
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 无障碍输入

## 概述

无障碍输入（Accessible Input）是游戏引擎输入系统中专门为行动能力受限、视觉障碍或其他身体差异玩家设计的输入处理机制。其核心功能包括三类：按键重映射（Key Remapping）、自动辅助（Auto-Assist）和开关控制（Switch Control），这三种机制可单独启用，也可组合使用。

无障碍输入在游戏行业的系统性普及始于2010年代中期。微软于2018年发布的Xbox Adaptive Controller直接推动了主机平台的无障碍输入标准化，随后Unreal Engine 4.20和Unity 2019.1相继在官方输入模块中增加了无障碍支持接口。2023年索尼的《漫威蜘蛛侠2》将70余项无障碍输入选项直接内置于引擎层，成为行业参考标杆。

从技术层面看，无障碍输入的必要性在于：标准输入系统假设玩家可以同时操作两根摇杆和多个按键，但单手玩家或使用脚踏开关的玩家无法满足这一假设。无障碍输入系统通过在原始输入信号到达游戏逻辑之前插入一个转换层（Input Remapping Layer），在不修改游戏核心逻辑的前提下改变输入的语义映射。

---

## 核心原理

### 按键重映射（Key Remapping）

按键重映射的本质是维护一张运行时可修改的**映射表（Binding Table）**，将物理输入事件（Physical Input Event）转换为逻辑动作（Logical Action）。典型结构如下：

```
PhysicalKey  →  LogicalAction
Button_A     →  Jump
Button_B     →  Attack
```

玩家通过界面重新绑定后，映射表变为：

```
PhysicalKey  →  LogicalAction
Button_X     →  Jump
Button_A     →  Attack
```

游戏逻辑层始终只接收`Jump`和`Attack`这样的逻辑事件，对物理按键变化完全无感知。在Unreal Engine中，这一层由`UInputMappingContext`实现；Unity Input System（Package v1.0+）则通过`InputActionAsset`的运行时覆盖（Override）机制提供相同能力。关键技术要求是映射表必须支持**冲突检测**：当同一物理键被映射到两个逻辑动作时，引擎需要给出警告并拒绝保存，否则输入结果将不可预测。

### 自动辅助（Auto-Assist）

自动辅助包含多个子功能，其中最常实现的两种是：

**连按转保持（Toggle Mode）**：将需要持续按住才能触发的动作（如奔跑`Hold`语义），转换为按一次开启、再按一次关闭的切换语义。实现上，引擎在输入管线中插入一个状态机，状态在`Pressed`事件触发时反转：

```
State=OFF → Pressed → State=ON  → 向游戏层持续发送"按住"信号
State=ON  → Pressed → State=OFF → 停止发送信号
```

**慢速连击辅助（Slow Tap Assist）**：为反应速度较慢的玩家放宽连按判定窗口。标准QTE连按判定窗口通常为80-120毫秒，慢速连击辅助可将窗口扩展至400-600毫秒。此参数在引擎中通常以`TapToleranceMs`浮点变量暴露，设计师可在无需修改代码的情况下调整。

**瞄准辅助（Aim Assist）**严格来说也属于自动辅助范畴。它通过对输入向量施加一个吸附力场，使准星在接近目标时减速，吸附强度由系数`k`（取值0.0–1.0）控制，对使用单摇杆或头部追踪设备的玩家尤为重要。

### 开关控制（Switch Control）

开关控制是为只能操作1至2个输入信号的玩家（例如仅能控制一个按钮或脚踏板）设计的输入模式。其核心机制是**顺序扫描（Sequential Scanning）**：

1. 引擎将所有可用的逻辑动作排成一个有序列表。
2. 系统以固定时间间隔（通常为1.0–2.0秒/项，可调）依次高亮每个动作。
3. 玩家在目标动作高亮时触发开关，该动作被执行。

单开关模式只需1个输入；双开关模式用第一个开关"前进扫描"，第二个开关"确认选择"，响应速度更快。iOS的Switch Control功能和PlayStation的游戏无障碍套件均采用此架构。在引擎实现层面，顺序扫描逻辑独立于正常输入轮询，通常以一个专用的`AccessibilityInputManager`单例组件运行，避免与帧率绑定。

---

## 实际应用

**《最后生还者 第一章》（2022）** 在无障碍输入领域提供了最完整的商业实现参考：其潜行按键原本需要长按L3（约0.5秒），开启切换模式后变为单次点按即可；游泳动作原本需要双手同时操作两根摇杆，开启"单摇杆游泳"辅助后，方向控制被合并至左摇杆，引擎内部通过将右摇杆输入的垂直分量与左摇杆速度绑定来实现。

**《战神：诸神黄昏》（2022）** 的开关控制实现将全部60余个游戏动作整合进扫描列表，扫描间隔可在0.5至3.0秒之间以0.1秒为步长调节，精度远超行业平均水平。

在游戏引擎插件层面，Unity的**Accessibility Plugin（XR Interaction Toolkit v2.3+）** 提供了开箱即用的按键重映射UI组件，可在运行时序列化玩家自定义映射到`PlayerPrefs`，持久化存储格式为JSON，键名规范为`AccessibilityBinding_{ActionName}`。

---

## 常见误区

**误区一：把无障碍输入与"简单模式"等同**
无障碍输入改变的是**输入通道**，而非游戏难度或挑战内容本身。开关控制让单手玩家能够完成所有操作，但游戏的敌人血量、伤害系数、关卡设计与普通模式完全相同。将二者混淆会导致设计师在实现无障碍输入时错误地降低游戏数值，破坏有障碍玩家的完整游戏体验。

**误区二：认为按键重映射只需在UI层保存偏好即可**
实际上，如果重映射仅在UI层处理而未插入输入管线中，游戏内的"按键提示"（Button Prompt）仍会显示默认按键图标（如显示"按A键跳跃"但玩家已将跳跃映射到X键），造成指引错误。正确实现要求提示系统通过查询同一张`Binding Table`动态生成图标，而非使用硬编码资产。这一问题在多语言、多平台项目中尤其容易被忽视。

**误区三：慢速扫描间隔设为固定值就够了**
不同障碍类型对扫描速度的需求差异极大：ALS（肌萎缩侧索硬化症）晚期患者可能需要3.0秒以上的间隔，而轻度运动障碍玩家可能在0.8秒时体验最佳。固定值方案会使部分用户群体完全无法使用开关控制。正确做法是将`ScanIntervalMs`作为可配置参数暴露，最小值不低于500ms，最大值不低于3000ms。

---

## 知识关联

理解无障碍输入需要以**输入系统概述**中的输入管线架构为基础：只有清楚物理输入事件如何经过轮询、映射、分发三个阶段传递到游戏逻辑，才能准确判断转换层应插入哪个阶段（通常在映射阶段与分发阶段之间）。

无障碍输入与**输入重映射（Input Rebinding）** 共享Binding Table数据结构，但后者面向所有玩家的个性化偏好，无障碍输入还额外处理"无法操作某些输入设备"这一约束条件，因此在冲突检测和默认值回退（Fallback）逻辑上有更严格的要求。

从工程实践角度，无障碍输入系统的配置参数应当通过数据驱动（Data-Driven）的方式管理，而非硬编码。这与游戏引擎中配置系统（Config System）的通用设计原则一致，设计师可借助同样的参数暴露机制在编辑器中实时预览不同无障碍设置的效果，缩短迭代周期。
