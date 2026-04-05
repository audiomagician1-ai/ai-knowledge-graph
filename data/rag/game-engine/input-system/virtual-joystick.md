---
id: "virtual-joystick"
concept: "虚拟摇杆"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["移动端"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
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

# 虚拟摇杆

## 概述

虚拟摇杆（Virtual Joystick）是移动端游戏中用软件模拟物理摇杆操作的触屏UI组件，由一个外圆环（背景盘）和一个可拖拽的内圆点（滑块）构成。玩家用拇指按下内圆点并拖动，系统将拖动偏移量转换为方向向量输出给游戏逻辑，实现角色移动、视角旋转等控制。与实体手柄的弹簧机械结构不同，虚拟摇杆完全依赖触点坐标计算来还原摇杆语义。

虚拟摇杆的概念随智能手机游戏在2008至2010年间普及而出现，早期《Eliminate》《Virtual City》等iOS游戏率先采用此方案。Unity引擎在其Standard Assets中提供了名为`ETCJoystick`的参考实现，后来第三方插件"Easy Touch"将虚拟摇杆的配置能力进一步标准化，成为移动端游戏输入的事实标准组件之一。

虚拟摇杆在移动端游戏中的重要性体现在：它解决了没有物理按键的平板/手机上如何输入连续二维方向信号的问题。不使用虚拟摇杆而改用倾斜（陀螺仪）或点击区域的替代方案，均会在精度或可达输入速度上有明显损失，因此虚拟摇杆至今仍是MOBA、射击、RPG等移动端品类的主流输入方案。

---

## 核心原理

### 坐标偏移量计算

虚拟摇杆的数学核心是将触点坐标转化为归一化二维向量。设外圆半径为 `R`，触点位置为 `P_touch`，摇杆中心为 `P_center`，则原始偏移向量为：

```
delta = P_touch - P_center
```

若 `|delta| > R`，需将其裁剪到半径范围内：

```
clampedDelta = delta.normalized * R
```

最终输出给逻辑层的归一化方向向量为：

```
output = clampedDelta / R    // 值域 [-1, 1] × [-1, 1]
```

这个 `output` 向量的 x 分量对应水平轴，y 分量对应垂直轴，与物理摇杆的 Axis 输入含义完全一致，可直接传入角色控制器。

### 死区（Dead Zone）处理

当玩家手指轻放在摇杆上时，细微抖动会产生非零的 `output` 值，导致角色出现不期望的微小位移。死区（Dead Zone）是一个阈值 `dz`（通常取 0.1 到 0.2），当 `|output| < dz` 时将输出强制归零。Unity的Input系统对实体手柄默认死区为 0.19，虚拟摇杆实现时建议参考同一数值保持行为一致性。超出死区后，可做线性重映射将 `[dz, 1]` 拉伸回 `[0, 1]`，避免因死区导致最大输出值打折：

```
remapped = (|output| - dz) / (1 - dz)
```

### 固定摇杆与浮动摇杆两种模式

**固定模式**：外圆环位置在屏幕上预设固定，玩家必须将拇指放在指定区域才能触发。优点是肌肉记忆稳定，适合需要精确操作的格斗、射击类游戏。

**浮动模式**：玩家在任意区域按下时，摇杆的中心点动态生成在按下位置，手指抬起后摇杆消失。优点是拇指不需要精确对准，适合休闲RPG或探索类游戏。浮动模式需额外维护一个"生成中心"坐标，并在 `TouchPhase.Began` 时记录，在 `TouchPhase.Ended` 时重置并隐藏UI。

---

## 实际应用

### Unity中的基础实现步骤

在Unity中实现虚拟摇杆需要以下关键步骤：
1. 创建两个 UI Image——背景盘（Background）和滑块（Handle），将两者放在 Canvas 下。
2. 编写脚本监听 `Input.GetTouch(0)`，在 `TouchPhase.Moved` 阶段计算偏移向量并更新 Handle 的 `anchoredPosition`。
3. 使用 `RectTransformUtility.ScreenPointToLocalPointInRectangle` 将屏幕触点坐标转换为Canvas本地坐标，避免DPI缩放导致的坐标偏差。
4. 将归一化 output 向量通过公开字段或事件传递给角色的 `CharacterController.Move` 调用。

### 多指支持与触点ID绑定

移动端游戏常需要左手摇杆 + 右手射击按钮同时工作。每个 `Touch` 结构体携带唯一的 `fingerId` 字段。虚拟摇杆组件应在 `TouchPhase.Began` 时记录触发它的 `fingerId`，后续帧只处理同一 `fingerId` 的 Touch 事件，忽略其他手指的触点，从而实现摇杆与其他按钮互不干扰。

### 视觉反馈设计

内圆点的位移应实时跟随手指，但最大偏移量限制在外圆半径内（即上文的 clampedDelta）。许多商业游戏（如《王者荣耀》）还会在摇杆外圆附近显示八个方向的箭头指示，当 output 向量角度落入对应扇区（每扇区45°）时高亮对应箭头，帮助玩家理解当前输入方向。

---

## 常见误区

### 误区一：直接使用屏幕坐标而不做坐标系转换

部分初学者直接用 `Input.GetTouch(0).position`（屏幕像素坐标）减去 UI 元素的 `transform.position`（世界坐标）来计算偏移，在 Canvas 为 Screen Space - Overlay 模式时会得到错误结果。正确做法是先用 `RectTransformUtility.ScreenPointToLocalPointInRectangle` 统一转换到同一坐标系再做减法。

### 误区二：忽略浮动模式的边界限制

浮动摇杆如果允许生成中心出现在屏幕任意位置，则当手指在屏幕边缘按下时，摇杆背景盘会有一半超出屏幕，导致可用方向不足180°（无法向屏幕外拖动）。应将生成中心限制在距屏幕边缘至少一个背景盘半径的安全区内，通常取背景盘半径为屏幕短边的15%左右。

### 误区三：把摇杆归一化向量直接乘以移动速度

虚拟摇杆输出的是方向向量，其模长在 `[0, 1]` 之间，代表"推进量"。如果直接将此向量乘以移速并赋给 `CharacterController.Move`，则没有乘以 `Time.deltaTime`，会导致移动速度与帧率强耦合。正确调用为 `controller.Move(joystickOutput * speed * Time.deltaTime)`。

---

## 知识关联

虚拟摇杆依赖**触屏手势**中的单点触控（`Touch`）数据流：`TouchPhase.Began` 触发摇杆激活、`TouchPhase.Moved` 驱动每帧计算、`TouchPhase.Ended/Canceled` 重置摇杆状态。多指支持则直接使用触屏手势系统提供的 `fingerId` 机制来区分同时存在的多个触点，与多点捏合（Pinch）手势共享同一套 `Input.touches` 数组但通过不同的 ID 分流处理。

在游戏引擎输入系统的更宏观视角下，虚拟摇杆是将触屏原始事件（Raw Touch Event）抽象为逻辑轴（Logical Axis）的典型桥接层，其 output 向量在语义上等价于 Unity Input Manager 中 `Horizontal` / `Vertical` 轴的值域约定，使得为手柄开发的角色控制代码无需修改即可复用于移动端。