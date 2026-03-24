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
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 载具物理

## 概述

载具物理（Vehicle Physics）是游戏物理引擎中专门模拟轮式交通工具动力学行为的子系统，涵盖车轮与地面的接触力学、悬挂系统的弹簧阻尼响应以及传动链的扭矩传递三大核心模块。与通用刚体模拟不同，载具物理需要将一个整体车身分解为多个相互耦合的约束子系统，并在每帧内以高频率（通常为物理步长的4到10倍细分步）求解这些约束，以防止车轮穿透或悬挂抖振。

该领域的工程实践可追溯至1990年代赛车游戏的兴起。Papyrus Design Group在1993年开发的《NASCAR Racing》中首次引入了基于真实轮胎侧偏刚度的物理模型，奠定了此后PC赛车模拟的技术基准。现代引擎如Unity的WheelCollider和Unreal Engine 5的Chaos Vehicle Plugin均继承并扩展了这一思路，前者将轮胎-地面交互抽象为一个带有悬挂弹簧的射线投射（Raycast）碰撞器，后者则引入了基于Pacejka轮胎模型的侧向力计算。

载具物理之所以在实现上比一般刚体模拟复杂得多，根本原因在于车轮受力具有强烈的速度依赖性与路面接触几何依赖性。一辆普通四轮车至少涉及4套独立的悬挂弹簧-阻尼器、4个轮胎摩擦锥约束以及驱动轴差速器的扭矩分配逻辑，这些子系统之间的耦合导致车身质心产生复杂的六自由度运动响应。

---

## 核心原理

### 轮胎摩擦模型：Pacejka魔法公式

轮胎与地面之间的纵向力（驱动/制动力）和侧向力（转向力）是载具物理的基础。行业标准是Hans Pacejka于1987年提出的半经验公式，通称"Magic Formula"：

$$F = D \cdot \sin\!\bigl(C \cdot \arctan(B\kappa - E(B\kappa - \arctan(B\kappa)))\bigr)$$

其中：
- **F** = 纵向力或侧向力（N）
- **κ (kappa)** = 轮胎滑移率（纵向）或侧偏角（侧向）
- **B** = 刚度因子（Stiffness Factor），控制曲线初始斜率
- **C** = 形状因子（Shape Factor），约为1.3~1.9
- **D** = 峰值因子，与法向载荷 $F_z$ 呈近似线性关系
- **E** = 曲率因子，控制峰值后的衰减形状

纵向滑移率 $\kappa$ 定义为：当车轮角速度产生的线速度 $r\omega$ 与车辆实际速度 $v$ 之差除以较大值，即 $\kappa = (r\omega - v)/\max(r\omega, v)$。$\kappa = 0$ 表示纯滚动，$\kappa = 1$ 表示完全抱死滑行。

### 悬挂系统：弹簧-阻尼-射线投射架构

游戏引擎中的悬挂通常用一根从车轮附着点沿车身局部向下发射的射线来替代真实的多连杆机构。射线命中地面后，计算压缩量 $x = L_{rest} - L_{current}$（其中 $L_{rest}$ 为弹簧自然长度），随后应用弹簧力与阻尼力：

$$F_{suspension} = k \cdot x + d \cdot \dot{x}$$

- **k** = 弹簧刚度（Spring Stiffness，单位 N/m，典型赛车值为 30,000~80,000 N/m）
- **d** = 阻尼系数（Damper Coefficient，典型值为弹簧刚度的 5%~30%）
- **$\dot{x}$** = 弹簧压缩速率（m/s）

该力沿射线方向作用于车身刚体的对应点，同时等量反向施加于虚拟车轮质量上。Unity WheelCollider中的`suspensionSpring.spring`与`suspensionSpring.damper`参数直接对应此处的 $k$ 与 $d$。

### 传动系统：扭矩流与差速器

发动机产生的扭矩经变速箱齿比（Gear Ratio）、主减速比（Final Drive Ratio）后到达驱动轮：

$$T_{wheel} = T_{engine} \times G_{gear} \times G_{final} \times \eta$$

其中 $\eta$ 为传动效率，通常取 0.85~0.95。差速器（Differential）负责在两个驱动轮之间分配该扭矩：开放式差速器允许两轮转速完全解耦，但导致单轮打滑时另一轮失去驱动力；限滑差速器（LSD）通过摩擦片或粘性偶合机构在两轮转速差超过阈值时锁定部分扭矩。在游戏中，LSD通常以一个简单的转速差百分比锁止因子来近似：当 $|\omega_L - \omega_R| > \Delta\omega_{threshold}$ 时，将差值的固定比例（如60%）强制均等化。

---

## 实际应用

**Unity WheelCollider配置示例**：创建一辆基本四驱越野车时，需将`WheelCollider.forwardFriction.stiffness`设为1.5~2.5（控制纵向峰值力），`sidewaysFriction.stiffness`设为1.2~2.0（控制侧向峰值力），再通过`WheelCollider.motorTorque`按帧分配发动机扭矩。若悬挂弹性系数过低（低于10,000 N/m），车身会在崎岖地形上出现穿地问题；过高则导致车身对小凹凸无减振，震荡传递到刚体造成弹飞。

**Unreal Engine 5 Chaos Vehicle**：UE5的Chaos Vehicle以Chaos物理引擎为底层，使用`UChaosWheeledVehicleMovementComponent`。其轮胎模型暴露了`LateralSlipGraph`曲线资产，允许设计师直接编辑侧向力-侧偏角曲线（对应Pacejka的侧向分支），而无需手动填入B/C/D/E参数，降低了调参门槛。

**赛车游戏的防抱死系统（ABS）模拟**：在代码层面，ABS通过检测 $\kappa > 0.15$（滑移率超过15%阈值）时周期性减小`motorTorque`（或增加`brakeTorque`的负反馈），防止轮胎进入完全抱死区间，使纵向力维持在Pacejka曲线的峰值附近而不下滑至滑动摩擦平台。

---

## 常见误区

**误区一：直接用RigidBody摩擦系数模拟轮胎抓地力**。将车轮设为普通球形碰撞器并依赖PhysicsMaterial的`dynamicFriction`来模拟轮胎，会导致侧向力与纵向力无法独立控制，且缺乏速度-滑移率依赖关系。真实轮胎在低速时侧向刚度很高（接近刚性约束），高速漂移时侧向力呈非线性饱和，这两种行为均需专用WheelCollider或自定义Pacejka实现。

**误区二：悬挂弹簧刚度越高越稳定**。提高`spring`值确实能减少车身下沉量，但过高的刚度会让悬挂无法有效吸收高频地形凹凸，射线投射在同一帧内检测到急剧变化的压缩量，导致悬挂力突变并引发刚体角速度的帧间抖振（俗称"弹跳病"）。正确做法是匹配弹簧刚度与阻尼系数，使系统阻尼比 $\zeta = d / (2\sqrt{km})$ 维持在0.3~0.7之间，其中 $m$ 为分配到该车轮的簧载质量。

**误区三：差速器不影响游戏体验可以省略**。在直线加速场景中省略差速器的确影响不大，但在弯道加速或单侧轮悬空（越野场景）时，若两驱动轮直接以相同转速约束绑定，会产生严重的转向抵抗力矩，表现为车辆"拒绝转弯"或在转弯时出现明显的速度损失。即使用最简单的开放式差速器逻辑（两轮扭矩相等、转速独立）也能显著改善此问题。

---

## 知识关联

**前置知识——刚体动力学**：载具物理的整车行为本质上是对一个六自由度刚体施加多点力的结果。理解刚体的惯性张量（Inertia Tensor）对于正确设置车身质心位置至关重要：质心过高会使车辆倾翻临界横向加速度降低（典型SUV约0.7g，F1赛车约4g），质心偏移会导致单侧轮荷转移（Weight Transfer）过大，造成内侧轮胎卸载失去抓地力。这些都需要在刚体层面理解力矩方程 $\tau = I\alpha$ 后才能正确分析。

**横向拓展——轮式机器人与无人机物理**：Pacej
