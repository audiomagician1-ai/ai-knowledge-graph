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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Cinemachine

## 概述

Cinemachine 是 Unity 官方开发的程序化摄像机系统，作为 Package 形式集成于 Unity 引擎中，最早于 2017 年以独立插件形式发布，并在 Unity 2018.1 版本后正式纳入 Package Manager，当前主流版本为 Cinemachine 3.x（随 Unity 2023+ 更新）。它的核心思路是将"摄像机控制逻辑"从脚本编写中抽离出来，通过数据驱动的方式在编辑器内配置摄像机行为，无需手写 `transform.position` 追踪代码。

Cinemachine 的架构将真实的 Unity `Camera` 组件与"虚拟摄像机（Virtual Camera，VCam）"分离开来。场景中可以存在多个 VCam，但只有一个真实摄像机在运行。`CinemachineBrain` 组件挂载在真实摄像机上，负责监听所有 VCam 的优先级（Priority 字段）并决定当前激活哪一个，从而实现多镜头切换和混合过渡。

Cinemachine 在商业项目中被广泛应用的原因在于，它内置了阻尼（Damping）、跟随抖动（Noise）、碰撞避障（Collider）等复杂摄像机行为，这些功能若手写通常需要数百行代码和大量调试时间。对于中小型团队而言，使用 Cinemachine 可将摄像机开发时间缩短约 60%–80%。

---

## 核心原理

### CinemachineBrain 与虚拟摄像机优先级系统

`CinemachineBrain` 每帧读取场景中所有激活的 VCam 的 `Priority` 整数值，选取最高优先级者作为"实时摄像机"来驱动真实 Camera 的 Position 和 Rotation。当两个 VCam 优先级相同时，Brain 采用最近激活的一个。切换时默认使用 **Blend**（混合过渡），在 `Default Blend` 字段可设置过渡时长（秒）和曲线类型，例如 `EaseInOut 2s` 表示 2 秒内以缓入缓出曲线完成镜头切换，避免画面跳跃。

### Follow 与 LookAt 绑定及 Aim/Body 算法

每个 VCam 包含两个核心绑定目标：`Follow`（身体跟随目标）和 `LookAt`（视线目标），两者可独立设置。**Body** 算法决定摄像机如何移动到跟随位置，常见选项包括：
- `Framing Transposer`：用于 2D/2.5D，在屏幕空间中保持目标处于特定比例位置；
- `3rd Person Follow`：自动计算第三人称肩膀偏移和碰撞回退；
- `Orbital Transposer`：允许玩家输入控制环绕角度。

**Aim** 算法决定摄像机如何旋转朝向 LookAt 目标，`Composer` 是最常用的 Aim 算法，通过 `Dead Zone`（死区宽高，0–1 归一化屏幕空间）和 `Soft Zone`（软区）控制目标允许在屏幕内漂移的范围，只有目标超出 Soft Zone 时摄像机才会强制追赶，从而模拟电影摄影师"松散跟随"的手持感。

### Noise 与 Impulse：摄像机震动系统

Cinemachine 提供两套震动机制。**Noise** 模块（`CinemachineBasicMultiChannelPerlin`）通过 Perlin 噪声曲线驱动摄像机的位置和旋转抖动，Asset Store 内置多种预设噪声配置文件（如 `Handheld_tele_mild`），`Amplitude Gain` 和 `Frequency Gain` 两个倍数参数控制抖动强度和频率。

**Impulse** 系统（`CinemachineImpulseSource` + `CinemachineImpulseListener`）专为事件触发的一次性震动设计，例如爆炸或角色落地时调用 `GenerateImpulse(force: Vector3)` 方法，Brain 会将该冲击信号广播到所有监听此信号的 VCam，并支持按距离衰减（`Dissipation Distance` 字段，单位为 Unity 世界单位米）。

### State-Driven Camera 与 Timeline 集成

`State-Driven Camera` 是一种特殊 VCam 容器，可将 Animator 的状态机状态映射到不同子 VCam，当角色进入"跑步"状态时自动切换到为跑步设计的镜头，无需任何脚本。在 Unity Timeline 中，Cinemachine Track 允许将 VCam 激活行为作为时间线片段排列，实现电影级过场动画的精确帧级控制。

---

## 实际应用

**第三人称游戏摄像机（如类《塞尔达传说：旷野之息》风格）**：使用 `CinemachineFreeLook` VCam，它内置上中下三条轨道（Top/Middle/Bottom Rig），每条轨道可独立设置半径和高度，形成一个围绕角色的椭球体轨道系统。玩家推动右摇杆时修改 `m_XAxis.Value`（水平角度）和 `m_YAxis.Value`（0–1 纵向混合），摄像机在三条轨道之间平滑插值，自动避免万向锁问题。

**2D 横版过关游戏**：`Cinemachine 2D Confiner` 扩展可将摄像机的移动范围限制在一个 `PolygonCollider2D` 或 `CompositeCollider2D` 定义的区域内，当关卡边界为不规则形状时（如洞穴地图），摄像机会自动计算最近合法位置，使玩家画面不会露出关卡边界外的空白区域。

**过场动画制作**：在 Unity Timeline 中创建 Cinemachine Track，将 4 个不同 VCam 的激活片段顺序排列，每段之间设置 0.5 秒混合过渡，并在最后一个 VCam 上启用 `CinemachineStoryboard` 扩展叠加预渲染图片，即可在运行时实现剧情演出而无需录制视频。

---

## 常见误区

**误区一：认为可以直接移动真实 Camera 的 Transform**  
在使用 Cinemachine 后，直接修改挂有 `CinemachineBrain` 的 Camera GameObject 的 `transform.position` 不会产生预期效果，因为 Brain 每帧 LateUpdate 阶段会用 VCam 计算结果覆盖 Camera 的 Transform。正确做法是修改 VCam 的 `Follow` 目标位置或调整 VCam 自身参数，或临时将 Brain 的 `UpdateMethod` 设为 `ManualUpdate` 并控制调用时机。

**误区二：混淆 Noise 模块与 Impulse 系统的使用场景**  
Noise 模块产生持续的周期性抖动，适合模拟手持摄像机质感或载具震动；Impulse 系统产生由物理冲击触发的瞬态衰减震动，适合爆炸、碰撞等一次性事件。开发者常犯的错误是用 Noise 模拟爆炸震动——这会导致震动无法在时间上精确对齐爆炸事件，且震动不会随距离衰减。

**误区三：Priority 值越高不代表"越重要"一定会被选中**  
VCam 必须处于**激活状态（enabled = true）**才会参与 Brain 的优先级竞选。一个 Priority 为 1000 的 VCam 若其 GameObject 被禁用，Brain 完全不会考虑它。因此切换镜头的标准做法是 `vCam.gameObject.SetActive(true)` 配合优先级，而不是单纯修改 Priority 数值。

---

## 知识关联

学习 Cinemachine 需要掌握 Unity `Camera` 组件的基础属性（FOV、Near/Far Clip Plane、Projection Mode），因为 Cinemachine 最终仍通过这些属性渲染画面，VCam 上的 `Lens` 字段直接映射到真实 Camera 的对应参数。此外，`CinemachineFreeLook` 的纵轴混合权重依赖对 Unity Animator 状态机的理解，若要使用 State-Driven Camera 则需要提前配置好角色的 Animator Controller。

Cinemachine 与 Unity 的 Input System（新版输入系统）配合使用时，`CinemachineInputProvider` 组件作为适配器将 Input Action 的 Vector2 输出绑定到 VCam 的轴控制，这是 Unity 2022+ 项目的推荐集成方式，避免直接使用已被标记为过时的 `Input.GetAxis()` 接口。掌握 Cinemachine 后，开发者在学习 Unity Timeline 制作过场动画时会发现 Cinemachine Track 是其核心功能之一，两者配合构成 Unity 原生过场动画的完整技术栈。