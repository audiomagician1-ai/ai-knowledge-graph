---
id: "unity-cinemachine"
concept: "Cinemachine"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 2
is_milestone: false
tags: ["摄像机"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.423
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Cinemachine：Unity程序化摄像机系统

## 概述

Cinemachine 是 Unity 官方开发的程序化摄像机控制包，最初以插件形式在 Unity Asset Store 发布，自 Unity 2018.1 起正式成为 Unity 内置包（Package Manager 中的 `com.unity.cinemachine`）。它的核心设计思想是将"摄像机应该拍什么"与"Unity Camera 组件如何输出画面"分离开来，从而让开发者用数据驱动的方式描述摄像机行为，而无需手写复杂的跟随、平滑、碰撞等逻辑代码。

在 Cinemachine 出现之前，游戏开发者通常需要自行编写 `LateUpdate()` 脚本，手动计算插值、偏移和遮挡处理，容易出现抖动或穿墙等问题。Cinemachine 通过一套分层架构解决了这些痛点：一个真实的 Unity **Brain Camera**（挂载 `CinemachineBrain` 组件）负责最终输出，而一个或多个 **Virtual Camera（虚拟摄像机，`CinemachineVirtualCamera`）** 负责描述具体的拍摄意图。Brain Camera 根据优先级和混合设置在虚拟摄像机之间自动切换和过渡。

Cinemachine 对 2D 游戏（Confiner 边界限制）、3D 第三人称游戏（Freelook Camera）、过场动画（Timeline 集成）和 VR 项目均有专用支持，是 Unity 生态中摄像机开发的事实标准方案。

---

## 核心原理

### 1. Brain-Virtual Camera 架构

场景中只需要**一个**挂载了 `CinemachineBrain` 的真实 Camera GameObject。`CinemachineBrain` 每帧扫描场景中所有激活的 `CinemachineVirtualCamera`，根据它们的 **Priority（优先级，整型数值，默认值为 10）** 决定哪个虚拟摄像机当前"生效"。优先级最高的虚拟摄像机会被选中，Brain 将其计算出的位置和旋转应用到真实 Camera 上。当两个虚拟摄像机发生切换时，Brain 会按照预设的 **Default Blend**（默认为 2 秒的 `EaseInOut` 曲线）在两者之间平滑过渡，开发者无需编写任何插值代码。

### 2. Body 与 Aim 的组件化设计

每个虚拟摄像机通过两个独立模块定义行为：
- **Body（机位控制）**：决定摄像机"站在哪里"。常用算法包括 `Transposer`（跟随目标并保持固定偏移）、`OrbitalTransposer`（绕目标轨道运动）、`FramingTransposer`（2D/俯视图中保持目标在屏幕指定比例位置）。
- **Aim（朝向控制）**：决定摄像机"看向哪里"。常用算法包括 `Composer`（把注视目标保持在屏幕的"Dead Zone + Soft Zone + Hard Limit"三层区域内）、`POV`（玩家鼠标/手柄输入控制旋转）。

`Composer` 的死区（Dead Zone）宽度和高度可设置为 0~1 的归一化屏幕坐标，目标在死区内时摄像机完全不旋转，进入软区（Soft Zone）后以阻尼平滑追踪，超出硬边界（Hard Limit）则立刻夹紧，三层参数共同决定了镜头跟随的手感松紧。

### 3. Noise（摄像机震动）与 Impulse

Cinemachine 提供内置的 **Noise** 模块，通过 `CinemachineBasicMultiChannelPerlin` 算法在 Body 和 Aim 上叠加程序化噪波，实现手持摄感或角色行走的上下起伏。震动强度由 **Amplitude Gain** 和 **Frequency Gain** 两个浮点参数控制。

对于爆炸、碰撞等一次性冲击效果，Cinemachine 提供 `CinemachineImpulse` 系统：在触发源上调用 `CinemachineImpulseSource.GenerateImpulse(force)`，场景内所有订阅了 `CinemachineImpulseListener` 的虚拟摄像机会在物理上模拟冲击波衰减，距离越远震感越弱，无需手动管理多个摄像机的震动状态。

### 4. CinemachineStateDrivenCamera 与 Timeline 集成

`CinemachineStateDrivenCamera` 可将 **Animator 状态机的状态名**映射到不同的子虚拟摄像机，实现角色切换动作时自动换镜（例如攀爬状态切换到仰视镜头）。在 Unity Timeline 中，Cinemachine 提供专用的 **Cinemachine Track**，可在时间轴上精确排列虚拟摄像机的激活片段和混合过渡，配合 Animation Track 制作电影级过场动画，所见即所得地预览最终效果。

---

## 实际应用

**第三人称跑酷游戏**：使用 `CinemachineFreeLook` 摄像机，该预设包含三条轨道（Top Rig、Middle Rig、Bottom Rig），分别对应摄像机在目标角色上方、平齐和下方的环绕轨道。玩家推拉摇杆时 Y 轴在三条轨道间混合，X 轴控制水平环绕角度，配合 `CinemachineCollider` 扩展组件自动检测并推开场景中的遮挡物，防止穿墙。

**2D 横板游戏**：在正交摄像机上使用 `FramingTransposer` + `CinemachineConfiner2D`，将 `Collider2D` 多边形设为关卡边界，摄像机在跟随玩家的同时不会越出关卡边缘，适合《超级马里奥》风格的卷轴关卡。

**过场剧情**：在 Timeline 中创建 Cinemachine Track，将多个虚拟摄像机片段首尾拼接，每段之间设置 0.5 秒 `Cut` 或 1 秒 `EaseIn` 混合，导演式地编排景别切换，最终由同一个 Brain Camera 输出，无需在场景中放置多个真实 Camera。

---

## 常见误区

**误区一：场景中放了多个真实 Camera 来模拟多机位**
Cinemachine 的正确用法是全场景只有一个 Brain Camera，多机位通过多个虚拟摄像机实现。放置多个真实 Camera 会导致渲染冗余，且无法使用 Cinemachine 的混合过渡功能，切换时会直接闪切。

**误区二：直接修改 Brain Camera 的 Transform 来移动镜头**
`CinemachineBrain` 每帧都会用虚拟摄像机的计算结果**覆盖**真实 Camera 的 Transform，所以直接操作 Brain Camera 的位置和旋转是无效的。所有镜头控制必须通过修改虚拟摄像机的参数（Follow 目标、偏移量、Priority 等）来实现。

**误区三：混淆 Follow 和 LookAt 目标的作用**
虚拟摄像机有两个目标槽：`Follow`（给 Body 模块使用，影响机位）和 `LookAt`（给 Aim 模块使用，影响朝向）。两者可以指向不同的 GameObject，例如机位跟随玩家角色，但镜头始终盯着某个 NPC，如果将两者混淆设置会导致摄像机位置正确但朝向错误的问题。

---

## 知识关联

学习 Cinemachine 需要具备 Unity 场景结构的基础知识：理解 GameObject 与 Component 的关系，才能明白为什么 `CinemachineBrain` 挂载在真实 Camera 上而虚拟摄像机是独立的 GameObject。此外，`LateUpdate()` 的执行时机知识有助于理解为何 Cinemachine 在每帧物理模拟之后才更新摄像机位置，从而避免跟随抖动。

Cinemachine 与 **Unity Timeline**（过场动画编排）、**Unity Input System**（POV 摄像机的输入绑定）以及 **Physics/Collider 系统**（`CinemachineCollider` 遮挡处理）均有直接的接口依赖。掌握 Cinemachine 后，可以进一步研究 **Cinemachine 3.x（2023 年随 Unity 6 更新的新版 API）**，该版本将 Body/Aim 重构为更模块化的 `CinemachineComponent` 管线，并提供了 `InputAxis` 系统替代旧版 `CinemachineInputProvider`。
