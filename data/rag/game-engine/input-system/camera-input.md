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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 摄像机输入控制

## 概述

摄像机输入控制是指将玩家的鼠标移动量或手柄右摇杆的偏转值，实时转换为游戏世界中摄像机旋转角度的过程。与普通UI光标控制不同，摄像机控制处理的是**相对输入量**（delta值），而非屏幕上的绝对坐标位置——每帧读取的是鼠标位移了多少像素，而不是鼠标当前在哪里。

这一技术在1992年的《Wolfenstein 3D》时代尚不存在，直到《Quake》（1996年）引入鼠标俯仰控制后，才确立了"鼠标X轴控制水平旋转（Yaw）、Y轴控制垂直旋转（Pitch）"的行业标准。现代引擎如Unity和Unreal Engine均将这一控制模式内置为标准摄像机方案的基础。

摄像机输入控制的核心价值在于**感官沉浸**：若旋转响应存在明显延迟或抖动，玩家会立刻产生晕眩感。因此，这套系统不仅是功能实现，更直接决定游戏的"手感"评价，业界通常要求输入到画面更新的延迟控制在16ms（60fps帧时间）以内。

---

## 核心原理

### 原始输入量的获取与灵敏度缩放

在Unity中，鼠标输入通过`Input.GetAxis("Mouse X")`和`Input.GetAxis("Mouse Y")`获取，返回值是经过Unity内部平滑处理的浮点数。手柄右摇杆则使用`Input.GetAxis("RightStickHorizontal")`，返回范围为`[-1, 1]`。

原始输入量必须乘以灵敏度系数才有实际意义：

```
rotationDelta = rawInputDelta × sensitivity × Time.deltaTime
```

其中`sensitivity`典型值为鼠标3.0～5.0、手柄摇杆100～200（单位：度/秒）。`Time.deltaTime`仅在处理摇杆的**持续偏转**时需要乘入；鼠标的`GetAxis`返回值本身已经是"每帧位移量"，通常**不需要**再乘以`deltaTime`，否则帧率越高摄像机转速越慢，这是初学者最常犯的错误。

### Yaw与Pitch的分离旋转

水平旋转（Yaw）和垂直旋转（Pitch）必须分别施加到不同的GameObject上，才能避免万向锁问题：

- **Yaw旋转**施加在玩家角色或摄像机父节点的**Y轴**上，使整个角色跟随水平视角转动
- **Pitch旋转**施加在摄像机本身的**X轴**上，仅控制上下俯仰

Pitch角度必须做夹值处理：`pitchAngle = Mathf.Clamp(pitchAngle, -89f, 89f)`，上限不设为90度是因为正好90度时会导致万向锁，通常上下限设为±80度到±89度之间。

### 平滑处理：低通滤波的应用

直接将原始鼠标delta应用于摄像机旋转会产生逐帧抖动（尤其是光学鼠标在粗糙桌面上时）。常用的平滑方法是**指数移动平均（EMA）**，也称低通滤波：

```
smoothedInput = smoothedInput × (1 - smoothFactor) + rawInput × smoothFactor
```

`smoothFactor`取值范围0到1，值越小越平滑但响应越迟钝，典型值为0.1～0.3。注意：**过度平滑会让竞技玩家感到"拖拽感"**，因此FPS类游戏默认平滑系数往往为0甚至提供关闭平滑的选项，而第三人称探索游戏则更多使用平滑以增加镜头的电影感。

手柄摇杆还需要引入**死区（Deadzone）**处理，通常将绝对值小于0.15的输入视为0，防止摇杆物理中心偏移造成的摄像机漂移。

---

## 实际应用

### 第一人称射击游戏的摄像机控制

在典型FPS游戏中，摄像机与玩家头部位置绑定，Yaw直接旋转角色的`Transform.eulerAngles.y`，Pitch只旋转摄像机子节点。《CS:GO》等游戏使用原始鼠标输入（smoothFactor=0），并提供`m_yaw`命令（默认值0.022）作为灵敏度参数，这一参数值已成为FPS社区的通用换算标准。

### 第三人称游戏的摄像机绕点旋转

第三人称摄像机需要在旋转的同时维持与角色的固定距离，摄像机位置通过球坐标系计算：

```
cameraPos = targetPos + Vector3(
    distance × cos(pitch) × sin(yaw),
    distance × sin(pitch),
    distance × cos(pitch) × cos(yaw)
)
```

旋转后还需要做碰撞检测（从角色向摄像机发射射线），防止摄像机穿入墙壁。

### 手柄摇杆的非线性映射

竞技游戏常将摇杆输入通过幂函数做非线性映射：`output = sign(input) × |input|^n`，其中n取1.5～2.0，使小偏转时精确微调、大偏转时快速转向。《Halo》系列的摇杆灵敏度曲线正是这种设计的代表。

---

## 常见误区

**误区一：鼠标输入也要乘以Time.deltaTime**
鼠标的`GetAxis`返回值是"本帧内的位移量"，已经是帧间差值，若再乘以`deltaTime`（如0.016秒），旋转速度会变得极慢且随帧率变化。只有摇杆的持续偏转（"每秒旋转N度"语义）才需要乘以`deltaTime`。

**误区二：直接设置eulerAngles的X分量来控制Pitch**
Unity的`eulerAngles`读写均会经过内部四元数转换，直接累加`transform.eulerAngles.x`会导致角度在0、90、270之间跳变。正确做法是在脚本中维护一个独立的`float pitchAngle`变量，每帧累加delta后用`Mathf.Clamp`限幅，再通过`localRotation = Quaternion.Euler(pitchAngle, 0, 0)`统一赋值。

**误区三：平滑越强手感越好**
平滑处理增加的是输入延迟——smoothFactor=0.1时，实际响应延迟约为`1/0.1 = 10帧`才能达到目标值的63%。对需要精准瞄准的游戏，过强平滑会让专业玩家明显感受到"输入滞后"，应将平滑作为可选设置而非强制应用。

---

## 知识关联

**依赖前置概念**：鼠标光标处理解决的是"鼠标在屏幕上的绝对位置"问题，而摄像机输入控制在此基础上要求鼠标光标**不可见且被锁定在屏幕中心**（`Cursor.lockState = CursorLockMode.Locked`）——只有在光标锁定模式下，`Mouse X/Y`的delta值才会持续稳定地返回移动量，否则光标碰到屏幕边缘后delta会被截断为0。

**横向相关系统**：摄像机输入控制产生的旋转角度通常同时输出给角色移动系统，用于计算前进方向向量；还会传递给动画系统，用于控制角色头部朝向的IK（反向动力学）目标点。这两个系统消费的是摄像机控制模块输出的Yaw/Pitch角度值，形成引擎内明确的数据流向。