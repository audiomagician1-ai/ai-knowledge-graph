---
id: "camera-input"
concept: "摄像机输入控制"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["摄像机"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 摄像机输入控制

## 概述

摄像机输入控制是游戏引擎输入系统中专门处理玩家视角操作的模块，负责将鼠标移动量或手柄右摇杆的模拟值转换为摄像机的旋转角度变化。其核心任务是让玩家感到"转头"这个动作既灵敏又顺滑，而不是生硬地跳跃到目标角度。

这一机制最早在1990年代第一人称射击游戏（FPS）兴起时被系统化。Quake（1996）确立了鼠标X轴控制水平旋转（Yaw）、Y轴控制垂直旋转（Pitch）的基本约定，该约定沿用至今。手柄时代到来后，右摇杆以-1.0到+1.0的模拟值替代了鼠标的像素位移量，但旋转逻辑的本质没有改变。

对游戏体验而言，摄像机输入控制直接影响玩家是否感到"晕眩"或"操控迟钝"。一个未经平滑处理的摄像机会在60fps下抖动，而过度平滑又会导致输入延迟感，这两种极端都会破坏沉浸感。因此，正确实现平滑插值是该模块最关键的技术挑战。

---

## 核心原理

### 原始输入读取与灵敏度缩放

鼠标每帧提供的是**像素位移量**（Delta值），例如玩家快速移动鼠标时可能产生`deltaX = 45`（像素/帧）。手柄右摇杆则提供范围在`[-1.0, 1.0]`之间的模拟轴值，两者量纲不同，必须分别配置灵敏度系数。

旋转角度的计算公式为：

```
rotationDelta = inputDelta × sensitivity × deltaTime
```

其中：
- `inputDelta`：本帧鼠标位移量（像素）或摇杆轴值（-1到1）
- `sensitivity`：灵敏度系数，鼠标通常在0.1–2.0范围调节，摇杆通常在60–200度/秒范围设定
- `deltaTime`：帧间时间（秒），用于消除帧率差异对旋转速度的影响

手柄输入**必须乘以`deltaTime`**，因为摇杆值代表"速度"而非"位移"；而鼠标输入是否乘以`deltaTime`则存在争议，不乘以时低帧率下旋转更快，乘以时则帧率独立但手感不同。

### 垂直旋转的俯仰角限制（Pitch Clamp）

不限制垂直旋转会导致摄像机"翻转过头顶"，造成方向感混乱。标准做法是将Pitch角钳制在`[-89°, 89°]`区间（而非正负90°，以避免万向锁问题）：

```
currentPitch = Clamp(currentPitch + pitchDelta, -89.0f, 89.0f)
```

水平旋转（Yaw）通常不需要限制，允许360°自由旋转，但需要对角度值做取模处理（`yaw %= 360`）防止浮点数溢出。

### 平滑插值处理

直接将每帧的`rotationDelta`叠加到摄像机角度上会产生抖动，尤其在摇杆输入存在噪声时明显。常用的平滑方案是**指数平滑（Exponential Smoothing）**：

```
smoothedInput = Lerp(smoothedInput, rawInput, smoothFactor)
```

其中`smoothFactor`是0到1之间的系数，值越小越平滑但延迟越大，值越大越响应迅速但越抖动。典型游戏中`smoothFactor`约设为`0.15–0.3`（每帧更新）。

另一种方案是**基于时间的平滑**，用`1 - exp(-smoothSpeed × deltaTime)`替代固定系数，使平滑效果在不同帧率下表现一致。这在移动端或VR游戏中尤为重要，因为这些平台的帧率波动更大。

---

## 实际应用

**第三人称跟随摄像机**：在Unity或Unreal Engine中，右摇杆的水平输入会围绕角色垂直轴旋转摄像机臂（Spring Arm），同时摄像机本身保持朝向角色。此时`rotationDelta`叠加在摄像机臂的父节点Transform上，而非摄像机自身，以确保旋转中心始终是角色位置。

**FPS视角控制**：鼠标输入直接驱动玩家角色的Yaw旋转（整个角色转向），同时只驱动摄像机节点的Pitch旋转（仅头部上下看）。这意味着Yaw和Pitch分别作用于两个不同的Transform节点，是FPS输入控制与第三人称摄像机最重要的区别。

**摄像机惯性效果**：部分动作游戏（如《战神》系列）在玩家松开摇杆后，摄像机会继续微小惯性旋转后再停下。实现方式是记录上一帧的`smoothedInput`，松开后每帧将其乘以摩擦系数（如0.85）直至趋近于零，而非立即清零。

---

## 常见误区

**误区一：在鼠标输入上乘以`deltaTime`导致高帧率手感变差**

鼠标的`deltaX`已经是帧间累积的位移量，它本身就隐含了时间信息。若再乘以`deltaTime`，则高帧率（如120fps）下`deltaTime`≈0.008秒，相同的物理鼠标移动量产生的旋转角度只有60fps时的一半，导致高帧率反而感觉"迟钝"。摇杆输入必须乘以`deltaTime`，而鼠标输入通常不应该乘以。

**误区二：平滑系数越大越好**

将`smoothFactor`设为接近1的值（如0.95）会引入约3–5帧的输入延迟，在FPS游戏中玩家会明显感到"拖尾"。竞技类FPS游戏（如CS2、Valorant）甚至默认关闭鼠标平滑，因为职业玩家需要精确的即时反馈。平滑主要用于手柄摇杆，因为摇杆的物理阻尼比鼠标少，噪声更大。

**误区三：用`Transform.eulerAngles`直接读写角度**

在Unity中，`eulerAngles`的读取值是引擎从四元数反算的结果，同一旋转状态可能返回不同的欧拉角表示。正确做法是维护一个独立的`float pitchAngle`和`float yawAngle`变量，计算完成后通过`Quaternion.Euler(pitch, yaw, 0)`来设置旋转，避免万向锁和角度跳变问题。

---

## 知识关联

**依赖的前置概念——鼠标光标处理**：摄像机输入控制要求鼠标处于"锁定"状态（`Cursor.lockState = CursorLockMode.Locked`），此时系统不再移动光标图标，而是直接向程序提供原始的Delta位移量。若没有正确处理光标锁定，鼠标移动到屏幕边缘后Delta值会被操作系统截断为零，导致摄像机无法继续旋转。

**与输入轴映射的关系**：摄像机旋转通常不直接读取硬件设备，而是读取引擎输入系统抽象的虚拟轴（如Unity的`Input.GetAxis("Mouse X")`或Unreal的`Axis Mapping`）。这使得同一套旋转代码可以同时响应鼠标和手柄摇杆，输入抽象层负责将两种不同量纲的原始数据统一映射到同一轴值范围。
