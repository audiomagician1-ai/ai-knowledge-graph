# 载具物理

## 概述

载具物理（Vehicle Physics）是游戏物理引擎中专门处理轮式交通工具运动行为的子系统，其核心任务是通过模拟悬挂弹簧、轮胎摩擦椭圆、差速器扭矩分配等机械结构，让赛车、卡车、越野车等在虚拟世界中产生符合真实驾驶直觉的运动反馈。与通用刚体动力学的本质区别在于：车辆的四个轮子并非简单的碰撞几何体，而是通过射线检测（Raycast）或形状投射（ShapeCast）与地面接触，借助悬挂弹簧吸收冲击、依靠轮胎侧向力维持转向的高度约束系统。

该领域的工程实践可追溯至1990年代专业赛车模拟器（如 Papyrus Design 的 *NASCAR Racing*，1994）的兴起。游戏引擎层面的标准化方案以 2004 年 Ageia PhysX SDK 引入 `NxWheelShape` 为重要里程碑——该组件首次将 Pacejka 轮胎模型与射线悬挂耦合进统一 API，使普通开发者无需从零实现车辆动力学。Unity 3.0（2010）引入的 `WheelCollider` 组件、Unreal Engine 5 的 `Chaos Vehicle`（2021）以及开源方案 *Vehicle Physics Pro*（Angel Garcia-Bellido, 2015）均沿用"射线悬挂 + 参数化轮胎曲线"的核心架构。

理解载具物理对赛车类和开放世界游戏至关重要：错误的悬挂阻尼会导致车辆在跳跃落地后持续弹跳长达数秒；不正确的轮胎侧向刚度会让过弯感受如同在冰面滑行。本文系统性地覆盖悬挂动力学、Pacejka 轮胎模型、传动链扭矩计算、防抱死系统实现及常见调参陷阱。

---

## 核心原理

### 悬挂系统：弹簧-阻尼器动力学

游戏引擎中的悬挂以**弹簧-阻尼器（Spring-Damper）**模型实现，每帧对车身施加垂直力：

$$F_{\text{susp}} = -k \cdot x - c \cdot \dot{x}$$

其中 $k$ 为弹簧刚度（N/m），$x$ 为悬挂当前压缩量（正值表示被压缩），$c$ 为阻尼系数（N·s/m），$\dot{x}$ 为压缩速度。Unity `WheelCollider` 将这两个参数分别暴露为 `suspensionSpring.spring` 和 `suspensionSpring.damper`。典型参考值：家用轿车前悬 $k \approx 20000\text{–}35000\ \text{N/m}$，赛车赛用悬挂 $k \approx 80000\text{–}150000\ \text{N/m}$；阻尼比（Damping Ratio）$\zeta = c / (2\sqrt{mk})$ 通常取 0.3–0.5，低于 0.2 时车身在颠簸后呈现明显欠阻尼振荡。

悬挂射线从车轮中心向车辆本地下方发射，长度等于静止自然长度加最大压缩量（`suspensionDistance`）。射线命中地面时，将接触点到车轮中心的距离换算为压缩量 $x$，代入上式后将力施加到刚体质心处（需乘以力臂转换为扭矩）。PhysX 5.x 的 `PxVehicleSuspensionForce` 函数在此基础上还加入了**防翻车力矩补偿**，通过向车身施加一个微小的横滚恢复扭矩防止低速过弯时内侧车轮抬起过多（Todorov et al., 2012, *PhysX Vehicle SDK White Paper*）。

### 轮胎摩擦模型：Pacejka 魔术公式

轮胎纵向力（驱动/制动）和横向力（转向）是载具物理中数学最复杂的部分。Hans Pacejka 在 1992 年提出的**魔术公式（Magic Formula）**至今仍是赛车工程的行业标准（Pacejka & Bakker, 1992, *Vehicle System Dynamics*）：

$$F = D \cdot \sin\!\left(C \cdot \arctan\!\left(B\alpha - E\left(B\alpha - \arctan(B\alpha)\right)\right)\right)$$

其中 $\alpha$ 为滑移角（Slip Angle，横向）或纵向滑移率（Slip Ratio，$\kappa$），$B$ 为刚度系数，$C$ 为形状系数，$D$ 为峰值因子，$E$ 为曲率因子。对于典型干燥沥青轮胎，纵向参数约为 $B=10,\ C=1.9,\ D=\mu F_z,\ E=0.97$（$\mu\approx1.0$，$F_z$ 为垂直载荷）。

Unity 的 `WheelFrictionCurve` 将完整的 Pacejka 曲线简化为四个关键点近似：

| 参数 | 含义 | 典型值（干沥青） |
|---|---|---|
| `extremumSlip` | 峰值摩擦对应的滑移率 | 0.1–0.2 |
| `extremumValue` | 峰值摩擦系数（相对） | 1.0 |
| `asymptoteSlip` | 渐近线滑移率 | 0.8 |
| `asymptoteValue` | 渐近线摩擦系数 | 0.5 |

**纵横向耦合——摩擦椭圆**：轮胎的总合力不能超过其极限摩擦圆（Friction Circle），设纵向力为 $F_x$、横向力为 $F_y$，摩擦椭圆约束为：

$$\left(\frac{F_x}{\mu_x F_z}\right)^2 + \left(\frac{F_y}{\mu_y F_z}\right)^2 \leq 1$$

这意味着全油门直线加速时横向抓地力下降约 40–60%；赛车游戏中的"油门进弯推头"正是此约束的直接体现。忽略摩擦椭圆耦合，仅用独立的纵/横摩擦系数，会导致车辆在急加速转弯时横向滑移力被高估，手感异常稳定。

### 传动系统：扭矩链与 RPM 计算

传动系统将发动机扭矩经变速箱传递到驱动轮。驱动轮获得的最终扭矩为：

$$T_w = T_e \cdot G_r \cdot G_f \cdot \eta_t$$

其中 $T_e$ 为发动机当前扭矩（N·m），$G_r$ 为当前档位齿比（1档通常 3.5–4.5，6档约 0.6–0.8），$G_f$ 为最终传动比（通常 3.5–4.5），$\eta_t$ 为传动效率（典型值 0.85–0.92）。发动机扭矩曲线以 RPM 为输入，通过动画曲线（AnimationCurve）或查找表实现，峰值扭矩通常出现在 2500–4500 RPM。

RPM 与车速的反向计算：

$$\text{RPM}_e = \frac{v \cdot G_r \cdot G_f \cdot 60}{2\pi r_w}$$

其中 $v$ 为车速（m/s），$r_w$ 为轮胎半径（m）。当 $\text{RPM}_e$ 超过红线时触发限速器；当降档导致 RPM 回落时释放更大扭矩，从而实现"降档超车"的加速感。

差速器（Differential）决定左右驱动轮间的扭矩分配：开放式差速器（Open Diff）总是向阻力更小的车轮输送更多扭矩，导致单轮打滑时另一轮失去驱动力；限滑差速器（LSD）通过预载弹簧和摩擦片限制最大扭矩差值，是赛车游戏中区分"街车"与"赛车"操控感的关键参数之一。

---

## 关键公式与算法实现

### 车轮转速与滑移率

纵向滑移率 $\kappa$ 定义为车轮旋转线速度与车辆实际速度之差的归一化值：

$$\kappa = \frac{\omega r_w - v_x}{\max(|\omega r_w|,\ |v_x|,\ \epsilon)}$$

$\kappa > 0$ 表示驱动打滑（轮速 > 车速），$\kappa < 0$ 表示制动抱死（轮速 < 车速），$\epsilon$ 为防零除小量（典型值 $10^{-3}$）。该公式在 PhysX `PxVehicleWheelsDynData` 中对每个车轮独立计算，每物理步长（通常 1/120 秒）更新一次。

### 防抱死制动系统（ABS）

ABS 的目标是将每个车轮的 $|\kappa|$ 维持在峰值摩擦附近（约 0.1–0.2），防止抱死后摩擦力骤降至渐近线水平。游戏引擎中常用**滑步阈值控制器**：

```
if |κ| > κ_threshold:  // 例如 0.3
    制动扭矩 *= release_factor  // 例如 0.85，逐渐释放
else:
    制动扭矩 = 驾驶员请求制动扭矩
```

更精确的实现参考 Rill（2012, *Road Vehicle Dynamics*）中的 ABS 滑移控制，将减压-保压-增压三相循环的时间常数设为 8–15 ms，与真实 ABS 电磁阀频率（约 10 Hz）对应。

### 空气动力学下压力

高速行驶时，气动下压力（Downforce）显著影响轮胎载荷和极限：

$$F_{\text{downforce}} = \frac{1}{2} \rho v^2 C_d A$$

其中 $\rho=1.225\ \text{kg/m}^3$（标准大气密度），$C_d$ 为阻力/下压系数，$A$ 为参考面积。F1 赛车在 250 km/h 时产生约 2500 N 下压力，使前轮载荷翻倍，进而允许更高的横向摩擦力极限。将此力附加到悬挂垂直载荷 $F_z$ 上，可以正确复现高速弯道"越快越稳"的物理现象。

---

## 实际应用案例

**案例一：Unity WheelCollider 调参实践**

在 Unity 开发一款城市驾驶游戏时，初始参数设置 `suspensionSpring.spring = 35000`，`damper = 4500`，车辆在起伏路面上呈现明显"船摇"感。计算阻尼比 $\zeta = 4500 / (2\sqrt{1500 \times 35000}) \approx 0.31$，属于欠阻尼状态。将 `damper` 调至 8000（$\zeta \approx 0.55$）后，颠簸响应在约 0.8 秒内收敛，油门响应也更线性。此外，将前轮 `WheelFrictionCurve` 的 `stiffness` 从默认 1.0 调低至 0.7，可以模拟湿滑路面的"轻微推头"手感，无需修改摩擦系数即可实现路面差异化。

**案例二：Chaos Vehicle（UE5）赛车项目**

Unreal Engine 5 的 `UChaosWheeledVehicleMovementComponent` 中，通过设置 `WheelSetup.AxleType = Front/Rear` 区分前驱/后驱/四驱布局，`DifferentialSetup.DifferentialType = LimitedSlip_4W` 启用全时四驱限滑。在 GDC 2022 的技术分享中，Epic Games 工程师展示了通过将 `TorqueCombineMethod = Override` 并注入自定义扭矩曲线，使电动赛车在低速时模拟瞬时峰值扭矩（0–60 km/h 加速 < 3 秒），与燃油车的渐进扭矩曲线形成明显对比。

**案例三：越野地形的悬挂行程与车轮贴地**

越野车辆需要较大的 `suspensionDistance`（常见 0.4–0.8 m，路面赛车仅 0.05–0.15 m）以保证四轮在崎岖地形上同时贴地。例如在 *《