---
id: "anim-notify"
concept: "动画通知"
domain: "game-engine"
subdomain: "animation-system"
subdomain_name: "动画系统"
difficulty: 2
is_milestone: false
tags: ["事件"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 动画通知

## 概述

动画通知（Animation Notify，简称 AnimNotify）是 Unreal Engine 动画系统中嵌入在动画序列时间轴上的事件触发机制。当动画播放到特定帧时，引擎会自动调用预先绑定的函数或广播事件，使动画数据与游戏逻辑产生直接联动。例如，在奔跑动画的第 8 帧脚掌落地瞬间触发脚步音效，或在挥剑动画的第 12–20 帧开启碰撞检测盒，这些都是动画通知的典型用途。

动画通知的概念最早随 Unreal Engine 3 的 UAnimSet 体系引入，并在 UE4 发布时（2014 年）随新的 AnimGraph 与 AnimMontage 系统一并重构，形成了现在的 `UAnimNotify` / `UAnimNotifyState` 两类 C++ 基类。它将"帧级精度的游戏事件"与动画数据绑定在同一个 `.uasset` 文件中，避免了在蓝图或代码里手动轮询播放进度的繁琐写法。

动画通知之所以重要，在于它是让动画驱动游戏世界变化的最低耦合方式：音效设计师可以直接在动画编辑器中放置声音通知，程序员无需改动任何逻辑代码，资产本身携带了触发信息。这种"数据驱动事件"的理念使跨职能团队可以并行迭代。

---

## 核心原理

### Notify 与 NotifyState 的本质区别

`UAnimNotify` 是**单帧点事件**，只在触发帧调用一次 `Notify(USkeletalMeshComponent*, UAnimSequenceBase*)` 函数。`UAnimNotifyState` 是**时间段状态事件**，它携带一个持续区间，在区间开始帧调用 `NotifyBegin`，每个 Tick 内调用 `NotifyTick`，区间结束帧调用 `NotifyEnd`。两者的 C++ 签名不同，不可互换使用：若需在刀光特效持续期间每帧更新粒子位置，必须使用 `NotifyState` 而非多个 `Notify` 点。

### 时间轴编辑与精度

在 Unreal Engine 的动画编辑器（Animation Editor）里，Notify 轨道（Notify Track）位于时间轴底部，默认精度为**每帧一格**。一条动画序列可以添加多条独立的 Notify 轨道，不同职责的通知分开放置，互不干扰。每个通知节点存储的触发时间是以**归一化时间（0.0–1.0）**保存的，引擎运行时会将其乘以序列实际时长（秒）得到绝对触发时间，因此同一资产在不同播放速率下帧精度会发生偏移，这是需要注意的精度陷阱。

### 内置通知类型

引擎预置了若干开箱即用的通知子类：
- **Play Sound**（`UAnimNotify_PlaySound`）：直接在骨骼插槽位置播放 USoundBase，无需额外代码。
- **Play Particle Effect**（`UAnimNotify_PlayParticleEffect`）：在指定骨骼 Socket 生成 Niagara/Cascade 特效。
- **Skeletal Notify**：广播命名事件到 AnimGraph 的 `AnimNotify` 节点，供状态机条件判断使用，不触发蓝图函数。

自定义通知只需在 C++ 中继承 `UAnimNotify` 并重写 `Notify()` 函数，或在蓝图中创建继承自 `AnimNotify` 的蓝图类，在 `Received_Notify` 事件中写逻辑即可，两种方式均支持热重载。

### AnimMontage 中的通知与 Notify Window

在 Montage 系统中，动画通知具有额外的 **Notify Window**（通知窗口）概念：Montage Section 被打断时，引擎会检查当前进度是否处于某个 NotifyState 区间内，若是，则立即调用该 NotifyState 的 `NotifyEnd`，防止状态泄漏（如碰撞检测盒永久开启）。这一机制由 `FAnimNotifyContext::MontageInstance` 指针驱动，Montage 打断时置空该指针并触发清理流程。

---

## 实际应用

**近战攻击的伤害窗口**：在格斗游戏中，剑击动画从第 15 帧到第 28 帧需要开启武器 HitBox。使用 `UAnimNotifyState` 子类 `NS_EnableWeaponTrace`，在 `NotifyBegin` 中将武器组件的 `bGenerateOverlapEvents` 设为 `true`，在 `NotifyEnd` 中关闭，配合 Montage 打断清理，能保证即使连招被格挡打断也不会残留碰撞响应。

**脚步系统**：角色奔跑动画在左脚落地帧放置 `AnimNotify_Footstep`，通知内部根据角色脚下物理材质（`EPhysicalSurface`）选择不同音效和扬尘粒子。这种写法将脚步音效的触发时机完全交由动画师控制，与程序逻辑解耦。

**技能准备反馈**：在蓄力动画的第 0.5 秒处放置 `Notify`，触发 UI 层的充能特效开始计时，使视觉反馈与角色动作帧精度对齐，而非依赖不稳定的 `SetTimer` 延迟。

---

## 常见误区

**误区一：用多个单帧 Notify 模拟持续状态**
一些开发者会在伤害帧区间内密集放置多个 `Notify` 点来"模拟"持续碰撞检测。这种做法无法保证每帧都触发（帧率不固定时某些 Notify 可能被跳过），且在 Montage 打断时没有自动清理机制，必须改用 `NotifyState`。

**误区二：在 AnimNotify 中执行耗时操作**
`Notify()` 函数运行在游戏线程的动画求值阶段，UE5 的多线程动画系统（Threaded Animation Evaluation）默认在工作线程上执行部分求值，直接在通知中调用非线程安全的 Actor 函数（如 `SpawnActor`）会引发崩溃。正确做法是通过 `GetOwningActor()` 获取 Actor 引用后，在下一帧使用 `AsyncTask(ENamedThreads::GameThread, ...)` 调度到主线程执行，或改用蓝图通知（蓝图通知在主线程安全执行）。

**误区三：混淆"Skeletal Notify"与普通自定义 Notify**
Skeletal Notify 仅向 AnimGraph 内的状态机发送信号，**不会**触发角色蓝图中的 `AnimNotify_XXX` 事件函数。若期望在角色蓝图中收到回调，必须使用自定义 `UAnimNotify` 子类；若仅用于驱动状态机跳转，Skeletal Notify 开销更低，因为它跳过了蓝图事件分发流程。

---

## 知识关联

动画通知依赖 **Montage 系统**提供的 Section 与打断机制才能正确清理 NotifyState 状态；若不熟悉 Montage 的 `StopMontage` 流程，无法理解为何打断时 `NotifyEnd` 会被强制调用。反过来，动画通知使 Montage 的每个 Section 可以携带独立的游戏逻辑事件，两者共同构成了 Unreal Engine 中程序化动画驱动游戏事件的完整链路。

在 C++ 扩展方向，掌握动画通知后可进一步研究 **AnimNotify 的网络同步问题**（`AnimNotify` 默认只在本地客户端触发，服务器端需通过 `NetMulticast` 或动画复制额外处理），以及 **Animation Blueprint 中的 Notify State Machine 节点**，利用通知事件直接驱动状态转换而无需额外布尔变量。
