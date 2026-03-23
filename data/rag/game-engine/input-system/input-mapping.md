---
id: "input-mapping"
concept: "输入映射"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["映射"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.375
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 输入映射

## 概述

输入映射（Input Mapping）是游戏引擎输入系统中将物理按键/轴信号转换为逻辑游戏动作的中间层机制。它的核心作用是将"玩家按下了键盘空格键"这一硬件事件，解耦成"玩家执行了跳跃动作"这一游戏语义，使游戏逻辑代码无需关心具体是哪个物理按键触发了某行为。

输入映射在1990年代末随主机平台多元化而正式成为引擎标配功能。早期PC游戏直接在代码中硬编码`if (key == VK_SPACE) jump()`，当Xbox控制器普及后，同一游戏需要同时响应空格键和A键，硬编码方式难以维护。虚幻引擎3（2006年）将Action Mapping和Axis Mapping作为两种独立系统引入编辑器，之后Unity的Input System（2019年正式版）也采用了类似的动作映射架构，这两套系统直接影响了当代绝大多数商业引擎的设计。

输入映射之所以不可省略，在于它同时解决了三个具体问题：多平台适配（同一逻辑动作绑定不同设备按键）、运行时重绑定（玩家自定义按键方案）、以及输入值的归一化（不同设备的摇杆范围统一到 \[-1, 1\] 区间）。

---

## 核心原理

### Action Mapping（动作映射）

Action Mapping处理**离散的布尔型输入事件**，对应"按下/松开"这类瞬时状态。其数据结构本质上是一张映射表：

```
ActionName  →  [设备类型, 物理按键, 修饰键]
"Jump"      →  [Keyboard, Space, None]
"Jump"      →  [Gamepad, FaceButtonBottom, None]
"Jump"      →  [Keyboard, Space, Shift]   ← 带修饰键的变体
```

在虚幻引擎5的Enhanced Input系统中，一个Action拥有`Value Type`字段，可选`Bool`、`Axis1D`、`Axis2D`、`Axis3D`四种，纯粹的Action Mapping对应`Bool`类型。当绑定触发时，引擎派发`Started`、`Ongoing`、`Triggered`、`Completed`、`Canceled`五个生命周期事件，而非早期版本只有`Pressed`和`Released`两种。

### Axis Mapping（轴映射）

Axis Mapping处理**连续的模拟值输入**，典型场景是摇杆移动或鼠标位移。每条轴映射记录除物理来源外，还携带一个**Scale（缩放系数）**，公式为：

> **OutputValue = RawInputValue × Scale**

Scale的用途非常具体：将键盘按键（只产生0或1）模拟成轴值时，W键绑定`MoveForward`轴的Scale设为`+1.0`，S键绑定同一轴的Scale设为`-1.0`，这样两个离散按键就能驱动同一个连续轴，游戏逻辑层只需读取`MoveForward`的浮点值即可，无需区分来源。

Unity Input System中对应概念称为**Composite Binding**，其`1D Axis`复合器内置了Positive/Negative两个子绑定，与虚幻的Scale机制在功能上等价。

### 运行时重绑定（Runtime Rebinding）

重绑定允许玩家在游戏运行时将某个逻辑动作的物理来源替换为新按键，而不修改游戏代码。完整的重绑定流程分为以下步骤：

1. **监听模式（Listening）**：引擎暂停正常输入处理，进入"等待任意输入"状态
2. **冲突检测（Conflict Detection）**：新按键若已被其他动作占用，提示冲突
3. **写入映射表**：将原有物理来源替换为新按键
4. **持久化（Serialization）**：将新映射方案写入本地配置文件（如`.ini`或JSON），下次启动时加载

Unity Input System提供`InputActionRebindingExtensions.PerformInteractiveRebinding()`API直接实现第1步，虚幻引擎中则需通过`UInputSettings::AddActionMapping()`手动更新并调用`SaveKeyMappings()`持久化。重绑定数据必须与默认映射分离存储，以便玩家能够执行"恢复默认"操作。

---

## 实际应用

**多平台同一代码库**：一款同时发行于PC和PS5的游戏，"翻滚"动作在PC端绑定`Left Shift`，在PS5端绑定`Circle`键。游戏逻辑层的C++或C#代码只调用`IsActionTriggered("Roll")`，映射表在平台构建时自动选择对应方案，实现零代码差异。

**车辆加减速轴**：赛车游戏中，手柄的`Right Trigger`（值域0到1）映射到`Accelerate`轴，Scale设为`+1.0`；`Left Trigger`同样值域0到1，映射到`Accelerate`轴，Scale设为`-1.0`。两个触发器的输出叠加后，油门/刹车用同一个浮点轴表达，物理引擎只需读取该单一值驱动车辆。

**无障碍辅助（Accessibility）**：通过在映射表中为同一动作绑定多个替代按键，可以低成本实现单手模式支持——将右手常用动作额外绑定到左手可达的按键，无需修改任何游戏逻辑。

---

## 常见误区

**误区一：将轴映射的Scale与灵敏度混淆**
Scale是映射层的固定系数，专门用于方向翻转（负值）和离散键模拟连续轴，**不是**控制灵敏度的参数。灵敏度调节应由输入修饰器（Input Modifier，如`ScalarModifier`）在映射之后处理，两者作用于输入流水线的不同阶段，混用会导致重绑定后灵敏度意外改变。

**误区二：认为Action Mapping只能映射单个按键**
一个Action可以同时绑定任意数量的物理来源（称为Bindings），所有来源采用**OR逻辑**：任意一个物理来源触发即视为Action触发。因此"跳跃"可以同时绑定空格键、手柄A键、触摸屏跳跃区域，三者并列生效，这是映射表的标准功能而非特殊扩展。

**误区三：重绑定保存只需覆盖默认配置**
默认映射配置是只读的引擎资产，重绑定数据必须写入**用户专属的可写路径**（Windows上通常是`%APPDATA%`目录），并在加载时将重绑定数据叠加覆盖在默认配置之上。若直接修改默认资产，多用户账户间会互相污染配置，且无法单独执行"恢复默认"。

---

## 知识关联

输入映射依赖**输入设备抽象层**提供标准化的原始输入值——正是设备抽象层将PS5 DualSense和Xbox Series控制器的物理信号统一为引擎内部格式，映射系统才能用一张设备无关的映射表工作。

掌握输入映射后，下一步学习**输入修饰器**：修饰器作用于映射产生的数值之后，可以对输出值执行归一化、死区过滤、平滑处理等变换，是映射值进入游戏逻辑前的最后加工环节。**输入触发器**则定义动作的激活条件（如长按0.5秒才触发），与映射层共同构成完整的输入处理链。**输入上下文（Input Context）**在映射系统之上增加了"当前哪套映射表生效"的管理能力，使同一物理按键在菜单状态和战斗状态下映射到不同动作。更进一步，**Steam Input** API将映射抽象提升到平台服务层，允许玩家在Steam界面而非游戏内完成重绑定，其Action/ActionSet概念与本文描述的映射结构直接对应。
