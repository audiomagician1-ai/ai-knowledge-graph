---
id: "vehicle-physics"
concept: "载具物理"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 3
is_milestone: false
tags: ["载具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
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

# 载具物理

## 概述

载具物理（Vehicle Physics）是游戏物理引擎中专门处理轮式交通工具运动行为的子系统，通过模拟悬挂弹簧、轮胎摩擦、传动扭矩等机械结构，让赛车、卡车、越野车等在虚拟世界中产生符合直觉的行驶手感。它不同于通用刚体动力学，因为车辆的四个轮子并不是简单的碰撞几何体，而是通过射线检测（Raycast）与地面接触、依靠悬挂弹簧吸收冲击、依靠轮胎侧向力保持转向的复杂约束系统。

该领域的工程实践可追溯至1990年代赛车模拟器的兴起，但游戏引擎层面的标准化方案以2004年PhysX引入`NxWheelShape`为重要里程碑。此后Unity的`WheelCollider`组件和Unreal Engine的`Chaos Vehicle`（UE5时代）都沿用了类似的"射线悬挂+轮胎模型"架构。掌握载具物理，可以直接影响一款驾驶游戏中油门响应、过弯侧滑、颠簸路面跳跃等核心游戏体验，是赛车类和开放世界游戏不可回避的技术课题。

---

## 核心原理

### 悬挂系统（Suspension）

游戏引擎中的悬挂通常以**弹簧-阻尼器（Spring-Damper）** 模型实现，物理公式为：

> **F_suspension = −k·x − c·ẋ**

其中 `k` 是弹簧刚度（Spring Stiffness，单位 N/m），`x` 是悬挂压缩量，`c` 是阻尼系数（Damper），`ẋ` 是压缩速度。Unity的`WheelCollider`将这两个参数分别暴露为`suspensionSpring.spring`和`suspensionSpring.damper`，典型家用轿车的`k`值约为20000–35000 N/m。悬挂射线从车轮中心向下发射，长度等于自然长度加最大压缩量（`suspensionDistance`），射线打到地面时计算压缩量，再将弹力施加到车身刚体上。悬挂阻尼不足会导致车身持续弹跳，阻尼过大则使车辆贴地过死、丧失颠簸感。

### 轮胎摩擦模型

轮胎产生的纵向力（驱动/制动）和横向力（转向）是载具物理中最复杂的部分。大多数引擎采用**Pacejka魔术公式（Magic Formula）**的简化版本：

> **F = D · sin(C · arctan(B·α − E·(B·α − arctan(B·α))))**

其中 `α` 为滑移角（Slip Angle）或纵向滑移率（Slip Ratio），`B/C/D/E`是形状系数。Unity的`WheelFrictionCurve`将其简化为四个关键点（extremumSlip、extremumValue、asymptoteSlip、asymptoteValue）来近似该曲线：在极值滑移率（约0.1–0.2）时摩擦力达到峰值，之后随滑移率上升而下降，模拟真实轮胎的"抓地力打滑"现象。横向力与纵向力存在摩擦椭圆耦合关系：同时全力加速与大角度转弯时，总摩擦力不能超过轮胎极限，否则轮胎会同时横向侧滑。

### 传动系统（Drivetrain）

传动系统决定发动机扭矩如何分配到各驱动轮。发动机扭矩曲线通常以RPM（转/分钟）为横轴，在2000–4500 RPM区间产生峰值扭矩，通过变速箱齿比（Gear Ratio）和最终传动比（Final Drive Ratio）放大后作用于车轮。车轮获得的驱动扭矩为：

> **T_wheel = T_engine × GearRatio × FinalDriveRatio × η**

其中 `η` 是传动效率（一般取0.85–0.95）。多轮驱动分配还涉及差速器（Differential）模拟：开放式差速器允许两轮转速不同但扭矩均分，限滑差速器（LSD）在转速差超过阈值时锁止，避免单轮打滑导致整车失去驱动力。Unreal的Chaos Vehicle系统内置了`DifferentialSetup`，支持Front/Rear/4WD三种模式和LSD参数配置。

---

## 实际应用

**赛车游戏的过弯调校**：在Unity的`WheelCollider`中，将前轮`sidewaysFriction.extremumValue`设置为略高于后轮（如前1.8、后1.5），可以实现转向过度（Oversteer）倾向，让赛车容易漂移，符合赛车竞技游戏的操控风格；反之前后相等或前低后高则产生转向不足（Understeer），感觉更稳健，适合模拟普通民用车。

**越野车的悬挂行程设置**：越野游戏（如模拟越野车攀爬）通常将`suspensionDistance`设置为0.4–0.6米，远高于普通赛车的0.1–0.2米，同时配合较低的弹簧刚度（k约8000 N/m），使车轮在大型障碍物上能保持地面接触，避免车轮腾空后扭矩突然失控导致车辆翻滚。

**摩托车的两轮平衡问题**：两轮载具无法用四点支撑保持静态稳定，需要在物理仿真层叠加一个陀螺力矩（Gyroscopic Torque）或平衡控制器。Unreal Engine的`ChaosWheeledVehicleMovementComponent`对两轮车额外施加一个与车速成正比的扶正力矩，速度高时车辆自然直立，低速时则需要玩家主动修正或引擎强制锁定倾斜角。

---

## 常见误区

**误区一：直接用刚体+球形碰撞体代替WheelCollider**。将轮子设置为普通球体刚体，虽然物理接触更直观，但无法独立控制悬挂弹力和轮胎摩擦，也无法与传动系统解耦，导致车轮在高速时因连续碰撞事件产生抖动（Jitter），而且无法实现Slip Ratio的精确计算。正确做法是始终使用引擎提供的专用轮子组件（如`WheelCollider`），它的射线悬挂比碰撞悬挂稳定性高出一个数量级。

**误区二：认为增大摩擦系数就能提高操控性**。很多初学者将`extremumValue`调到2.5甚至更高，期望车辆更好控制，结果发现车辆在低速转向时过于灵敏、方向盘反应过激。这是因为Pacejka曲线的峰值摩擦力是与法向力（Normal Force）相乘的，法向力本身与车重和重心转移相关；过高的摩擦系数会使横向力在极小滑移角就达到峰值，导致转向阶跃响应而非平滑渐进，破坏手感。

**误区三：忽视物理子步（Physics Substep）对载具稳定性的影响**。载具物理对时间步长极为敏感，在Unity中若将`Fixed Timestep`设置为默认的0.02秒（50Hz），高速行驶的赛车悬挂弹力计算可能出现数值不稳定（发散振荡）。建议将载具所在场景的物理更新频率提升至100–120Hz（即Fixed Timestep改为0.00833秒），或在`WheelCollider`的悬挂参数中确保阻尼比（c / (2√(mk))）大于0.3以保证系统稳定。

---

## 知识关联

载具物理直接建立在**刚体动力学**的基础上：车身本体是一个标准的六自由度刚体，引擎通过`AddForce`和`AddTorque`将悬挂弹力、轮胎摩擦力、空气阻力施加于质心或指定作用点。没有刚体动力学中的惯性张量（Inertia Tensor）概念，就无法理解为何降低车辆质心高度（即调小`centerOfMass.y`）会显著减少翻滚倾向。同时，载具物理的实现也涉及**射线检测（Raycast）** 在碰撞检测中的应用，以及**约束求解器（Constraint Solver）** 中速度投影的原理。在更高阶的赛车模拟领域，Pacejka魔术公式的完整11参数版本和复杂差速器建模是进一步探索的方向，而开放世界游戏还需要将载具物理与**流体浮力模拟**（水中行驶）和**程序化地形**（软体地面的车辙形变）结合，形成完整的载具-环境交互系统。