---
id: "touch-gesture"
concept: "触屏手势"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["移动端"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 触屏手势

## 概述

触屏手势是游戏引擎输入系统中专门用于识别和处理电容触摸屏多点触控信号的技术模块，负责将原始触摸点坐标序列（TouchPoint 数据流）转换为具有语义意义的交互动作，例如单指轻触（Tap）、单指滑动（Swipe）、双指捏合缩放（Pinch）以及多指旋转（Rotation）。电容屏每帧可同时追踪 2 至 10 个独立触摸点，每个触摸点携带 x/y 坐标、压力值（部分设备）、接触面积（radius）及状态标志（Began/Moved/Ended/Cancelled）四类数据。

触屏手势识别技术随智能手机普及而在 2007 年 iPhone 发布后快速进入游戏引擎领域。Unity 在 2010 年的 Unity 3 中引入 `Input.GetTouch(int index)` API，提供最多 7 个同时触摸点的追踪；Unreal Engine 则在 4.x 版本中通过 `ETouchIndex::Touch1 ~ Touch10` 枚举支持 10 点并发触控。了解触屏手势识别对于移动平台游戏开发至关重要，因为 iOS 和 Android 设备完全依赖触屏作为主要输入方式，不存在物理按键的回退方案。

## 核心原理

### 触摸点生命周期与状态机

每个触摸点从按下到抬起经历严格的状态转换：`Began → Stationary/Moved → Ended`，若系统中断（如来电）则进入 `Cancelled` 状态。游戏引擎为每个活跃触摸点分配唯一的 `fingerId`（整数，通常 0–9），该 ID 在触摸点存活期间保持不变，抬起后可被新触摸复用。手势识别器必须以 `fingerId` 而非数组下标追踪触摸点，否则在多指操作时会因数组重排导致触摸点身份混淆。

### Tap 与 Swipe 的时间空间阈值

Tap（轻触）的识别条件是：同一 `fingerId` 的 Began 到 Ended 时间差小于阈值 T_tap（通常取 **200 毫秒**），且期间最大位移 d < D_tap（通常取 **10–15 像素**，需乘以屏幕 DPI 转换为物理毫米）。满足条件则触发 Tap 事件，否则视为长按或滑动。

Swipe（滑动）除时间判断外，还需计算方向向量：将 Ended 坐标减去 Began 坐标得到位移向量 **Δ = (Δx, Δy)**，通过 `atan2(Δy, Δx)` 计算角度后量化为 4 方向（每象限 90°）或 8 方向（每象限 45°）。最小位移阈值通常设为 **50 像素**，低于此值的短距离滑动不触发 Swipe。

### Pinch 双指捏合缩放

Pinch 手势要求同时存在 2 个活跃触摸点。缩放比例公式为：

**scale = currentDistance / initialDistance**

其中 `currentDistance` = 两触摸点当前帧欧氏距离，`initialDistance` = 两触摸点首次同时出现时的欧氏距离。`scale > 1` 表示展开（zoom in），`scale < 1` 表示捏合（zoom out）。此外，两触摸点中点坐标 **pivot = (p1 + p2) / 2** 给出缩放的锚点位置，摄像机或 UI 元素应围绕该锚点执行变换，而非屏幕中心。双指旋转角度可通过 `atan2` 计算当前帧和上一帧两点连线角度之差得到，范围约束在 (−π, π]。

### 多点触控的帧率一致性问题

触摸事件的采样频率在不同设备上差异显著：iPhone 15 的触摸采样率为 **120 Hz**，而普通 Android 设备通常为 **60 Hz**，部分游戏手机可达 **240 Hz**。当游戏帧率低于触摸采样率时，单帧内可能积累多个触摸事件。Unity 的 `Input.touches` 仅返回当前帧最后一个快照，导致快速 Swipe 在低帧率下被识别为 Tap。解决方案是使用 Unity 新版 `EnhancedTouchSupport`（需调用 `EnhancedTouchSupport.Enable()`）或 Android 原生的 `MotionEvent.getHistoricalX()` 获取帧内历史点。

## 实际应用

在卡牌游戏（如《炉石传说》移动版）中，Swipe 手势用于翻页卡组，Tap 用于选牌，长按（Long Press，持续时间 > 500 毫秒且位移 < 15 像素）触发卡牌详情预览。三种手势共享同一套触摸点，通过时间和位移阈值互斥区分，不会同时触发。

在地图类游戏（如《文明6》移动版）中，单指 Swipe 平移地图，双指 Pinch 缩放，双指旋转（两点连线角度变化 > 15°）旋转视角。为防止缩放与旋转相互干扰，通常引入手势锁定机制：Pinch 开始后若旋转角变化 < 10° 则锁定为纯缩放模式，反之锁定为旋转模式，直至该手势的所有触摸点抬起才解锁。

在 Unity 中实现触屏手势时，推荐将识别逻辑封装为独立的 `GestureDetector` 类，通过 C# 事件（`event Action<GestureEventData>`）向游戏逻辑层广播手势结果，而不是在 `Update()` 中直接操作游戏对象，以便在输入系统抽象层之上保持单一职责。

## 常见误区

**误区一：用 `Input.mousePosition` 在移动端替代触摸输入**
Unity 在移动端会将第一个触摸点模拟为鼠标左键，因此单指 Tap 可被 `Input.GetMouseButtonDown(0)` 捕获。但这种方式完全丢失了 `fingerId` 信息，无法处理多指手势，且在双指操作时 `mousePosition` 会跳变到最新触摸点，导致 Pinch 计算错误。正确做法是始终使用 `Input.GetTouch()` 或 `EnhancedTouch.Touch` API。

**误区二：Tap 识别不考虑位移，只判断时间**
实际使用中，即使非常短暂的触摸也会因手指生理抖动产生 5–8 像素的漂移。若仅以 200 毫秒时间阈值判断 Tap 而忽略位移检查，会导致短距离 Swipe 被错误识别为 Tap，影响卡牌选取、按钮点击等精细操作的准确率。位移阈值需根据屏幕 DPI 换算为物理距离，通常设定为 3–4 毫米。

**误区三：Pinch 的 initialDistance 在每帧重新计算**
部分初学者在每帧用当前距离除以上一帧距离计算增量缩放比（delta scale），而非保存手势开始时的 `initialDistance` 计算累积比例。增量计算在帧率波动时会产生误差累积，且无法支持缩放动画的插值平滑。正确方案是记录手势开始时快照，整个 Pinch 过程始终以该快照作为基准。

## 知识关联

触屏手势识别建立在**输入设备抽象**层之上：输入设备抽象将电容屏的驱动层信号标准化为统一的 TouchPoint 数据结构，触屏手势识别器消费这些标准化数据而无需关心底层操作系统差异（iOS UITouch vs Android MotionEvent）。正因如此，同一套手势识别代码可在不同平台的触摸设备上复用。

触屏手势的识别结果直接驱动**虚拟摇杆**的实现：虚拟摇杆通常将特定屏幕区域的 Tap（激活）和后续 Moved 事件（方向输入）组合为摇杆控制逻辑，其摇杆偏移量计算依赖触摸点的连续坐标追踪，本质上是在触屏手势的基础上构建的专用输入控件。理解触摸点生命周期和 `fingerId` 追踪是实现稳定虚拟摇杆的必要前提。