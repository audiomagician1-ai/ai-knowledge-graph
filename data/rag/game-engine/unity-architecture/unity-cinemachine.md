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
content_version: 3
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
# Cinemachine

## 概述

Cinemachine 是 Unity 官方开发的程序化摄像机控制系统，于 2017 年作为 Unity Package Manager 的官方包正式发布，并在 Unity 2018.1 版本后成为内置可安装包。它的核心理念是将"摄像机行为"从手动编码脚本中解放出来，通过可配置的组件和参数驱动摄像机运动，从而让开发者无需编写一行 C# 代码就能实现跟随、瞄准、过渡等复杂摄像机效果。

Cinemachine 的设计灵感来源于电影摄影行业，将电影中的"虚拟摄影机"（Virtual Camera）概念引入游戏引擎。系统引入了"大脑（Brain）"与"虚拟摄像机（Virtual Camera）"的分离架构：场景中只有一个真实的 Unity Camera 组件挂载 CinemachineBrain，而多个 CinemachineVirtualCamera 负责描述不同的摄像机行为逻辑，由 Brain 根据优先级和混合规则决定最终输出。

在大型商业游戏中，摄像机行为往往需要根据玩家状态、场景区域、剧情触发等条件动态切换，手写状态机极易产生难以维护的代码。Cinemachine 通过声明式配置替代了这种命令式脚本，同时提供与 Unity Timeline 的深度集成，使过场动画的摄像机调度可在 Timeline 轨道上可视化编辑，大幅降低了动画师与程序员的协作成本。

---

## 核心原理

### Brain 与 Virtual Camera 的分离架构

CinemachineBrain 挂载在场景中唯一的真实 Camera 对象上，它每帧读取当前激活的 Virtual Camera（即 CinemachineVirtualCamera 或其衍生类型）所计算出的位置、旋转和镜头参数，然后将这些数据写入真实 Camera。每个 Virtual Camera 拥有独立的 **Priority（优先级）** 属性，数值越高越优先被 Brain 采用。当多个 Virtual Camera 同时激活时，Brain 不会突然切换，而是按照设定的 **Blend** 规则（如 EaseInOut、Linear、Cut）在指定时间内平滑插值过渡，默认混合时长为 2 秒。

### Body 与 Aim 的双轴解耦

每个 CinemachineVirtualCamera 内部分为 **Body** 和 **Aim** 两个独立算法层：
- **Body** 控制摄像机位置，常用算法包括 `Transposer`（跟随偏移）、`OrbitalTransposer`（轨道跟随）、`FramingTransposer`（2D 框架跟随）、`HardLockToTarget`（硬锁定）。
- **Aim** 控制摄像机朝向，常用算法包括 `Composer`（基于屏幕空间的目标构图）、`HardLookAt`（硬朝向）、`POV`（玩家视角旋转）。

这种解耦意味着可以单独更换某一轴的算法而不影响另一轴。例如，Body 使用 `OrbitalTransposer` 绕角色公转，同时 Aim 使用 `Composer` 并设置 Dead Zone（死区）让目标在屏幕中心区域移动时摄像机不旋转，超出 Soft Zone 才开始追踪，超出 Hard Limit 则硬性对准——这三个区域的百分比参数均可在 Inspector 中精确调节。

### Noise（摄像机抖动）与 Extensions

Cinemachine 提供内置 **Noise** 模块，基于 Perlin Noise 算法生成连续随机抖动，通过指定 `NoiseSettings` 资产（如内置的 `6D Shake` 或 `Handheld_tele_mild`）以及 Amplitude Gain 和 Frequency Gain 参数，可模拟手持摄像机、爆炸震动等效果，无需额外代码。

除 Noise 外，Cinemachine 还支持 **Extensions**（扩展组件），常用扩展包括：
- `CinemachineConfiner`：将摄像机限制在一个 2D 多边形碰撞器或 3D 碰撞体定义的范围内，防止穿墙或越界。
- `CinemachineImpulseSource` + `CinemachineImpulseListener`：通过物理冲量信号系统触发瞬时抖动，例如子弹击中时发射一个 Impulse 信号，所有监听的摄像机自动响应震动。

### Timeline 集成与 CinemachineTrack

在 Unity Timeline 中添加 **Cinemachine Track** 后，可以在轨道上放置多个 CinemachineShot Clip，每个 Clip 绑定一个 Virtual Camera，Timeline 播放到该 Clip 时摄像机即激活并渲染。相邻 Clip 之间可设置混合区域实现过场动画中的摄像机溶解过渡，整个过场动画的摄像机调度完全由 Timeline 时间线驱动，不依赖脚本触发。

---

## 实际应用

**第三人称跟随摄像机**：为 Virtual Camera 的 Body 选择 `Transposer`，将 Follow Target 设为玩家角色，Binding Mode 设为 `Lock To Target With World Up`，X/Y/Z Damping 分别设为 0.5/0.2/0.5 秒，即可实现带惯性缓动的跟随摄像机；Aim 选择 `Composer` 并将 Look At Target 也设为玩家，Dead Zone Width 设为 0.1，这样玩家在屏幕中央小范围移动时画面不晃动。

**多区域摄像机切换**：在关卡中放置多个 Virtual Camera，分别设置不同的 Priority 默认值为 10，当玩家进入特定触发区域时通过脚本调用 `virtualCamera.Priority = 20` 将该区域摄像机提升优先级，Brain 自动触发 EaseInOut 过渡，切换完成后再恢复优先级。这只需两行代码，其余过渡逻辑全由 Cinemachine 处理。

**2D 横版关卡**：Body 选择 `FramingTransposer`，开启 `Dead Zone` 功能，设置 Screen X 为 0.3（玩家偏左三分之一位置）以实现前方视野更开阔的构图，同时配合 `CinemachineConfiner2D` 限制摄像机在关卡边界内移动，当关卡边缘靠近时摄像机自动停止而不会露出场景外的空白区域。

---

## 常见误区

**误区一：Virtual Camera 本身会渲染画面**
初学者常误解 CinemachineVirtualCamera 是一个真正的摄像机，实际上它完全不渲染任何内容，场景中只有挂载 CinemachineBrain 的那一个 Unity Camera 才负责渲染。Virtual Camera 仅是一个"位置与朝向的描述者"，Brain 读取其输出并驱动真实 Camera。如果场景中没有 CinemachineBrain，所有 Virtual Camera 的设置都不会生效。

**误区二：关闭 Virtual Camera GameObject 等同于降低 Priority**
很多开发者通过 `gameObject.SetActive(false)` 来停用摄像机，这在功能上可行，但会触发 GameObject 完整的激活/停用流程，产生额外开销。Cinemachine 官方推荐的做法是保持 GameObject 激活，改为修改 `Priority` 属性或调用 `virtualCamera.enabled = false`（禁用组件而非对象），后者不会销毁 Virtual Camera 的运行状态，重新启用时过渡更平滑。

**误区三：Noise 模块等于实时物理碰撞震动**
Cinemachine 的 Noise 模块基于预设的 Perlin Noise 曲线循环播放，是持续性的随机抖动，适合模拟持续震动（如车辆行驶）；而 `CinemachineImpulse` 系统才是用于一次性冲击事件（如爆炸、落地）的正确工具。混用两者会导致持续抖动与冲击叠加，视觉效果失控。

---

## 知识关联

**前置知识**：理解 Cinemachine 需要熟悉 Unity 中 Camera 组件的基本属性，包括 Field of View、Near/Far Clip Plane 以及 Projection 模式（透视/正交），因为 Cinemachine 的 Lens 设置本质上是在覆写这些 Camera 属性。同时需要了解 Unity 的 Transform 层级和 Follow/LookAt 目标绑定机制，这是 Body 和 Aim 算法的数据来源。

**横向关联**：Cinemachine 与 Unity Timeline 深度集成，过场动画制作需要同时掌握 Timeline 的 Track 与 Clip 概念。在使用 `CinemachineConfiner` 时还涉及 Unity 物理系统中的 Collider 组件，尤其是 `PolygonCollider2D` 用于定义 2D 关卡边界。Cinemachine 3.x 版本（随 Unity 2023 推出）将架构重构为基于 `CinemachineCamera` 的新组件命名体系，与 2.x 版本 API 不完全兼容，升级项目时需注意迁移文档。
