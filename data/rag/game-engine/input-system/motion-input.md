---
id: "motion-input"
concept: "运动输入"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["体感"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 运动输入

## 概述

运动输入（Motion Input）是指游戏引擎通过读取陀螺仪（Gyroscope）、加速度计（Accelerometer）和其他惯性传感器的数据，将物理设备在三维空间中的旋转与位移转换为游戏内可用控制信号的输入机制。与按键或摇杆不同，运动输入捕捉的是设备姿态的连续变化，而非离散按压或轴向偏移，天然适合表达"挥剑""瞄准""倾斜迷宫"等需要空间感的交互。

运动输入在游戏领域的大规模普及始于 2006 年 11 月任天堂 Wii 随主机发售的 Wiimote 遥控器。Wiimote 内置三轴加速度计（±3g 量程），使玩家通过真实挥舞动作打网球或投保龄球，首周北美销量即突破 60 万台，证明了体感交互的商业可行性。2009 年发布的 Wii MotionPlus 配件为 Wiimote 追加了单轴陀螺仪（±8000°/s），弥补了纯加速度计无法检测慢速旋转的先天缺陷，使《塞尔达传说：天空之剑》中 1:1 剑道操作成为可能。此后 2010 年 Sony PlayStation Move、2013 年任天堂 3DS 内置陀螺仪，以及智能手机的全面普及，将两种传感器嵌入数十亿台消费设备，运动输入随之成为移动游戏与主机游戏不可忽视的输入维度。

运动输入提供了一个连续的六自由度（6-DoF）数据流，覆盖线性加速度的 X/Y/Z 三轴与角速度的 Roll/Pitch/Yaw 三轴。这让游戏能实现直觉化的方向瞄准、体感挥击和重力感应解谜等机制——这些体验用传统离散输入极难等价还原。

---

## 核心原理

### 加速度计的工作方式

加速度计测量设备受到的比力（Specific Force），即去除自由落体后的加速度分量，单位为 m/s²，通常以重力加速度 $g$（$1g \approx 9.80665\ \text{m/s}^2$）表示量程。消费级 MEMS 加速度计的典型量程为 ±2g 至 ±16g，分辨率为 12–16 bit，采样率 50–400 Hz。

当设备静止平放时，加速度计三轴读数并非全零，而是会在垂直轴上读到约 $+1g$ 的向上分量，这是地球重力对传感器的反作用力。游戏引擎利用这一特性可在静止状态下直接估算设备的倾斜角（Tilt Angle）：

$$
\text{pitch} = \arctan2\!\left(a_y,\ \sqrt{a_x^2 + a_z^2}\right)
$$

$$
\text{roll} = \arctan2\!\left(-a_x,\ a_z\right)
$$

其中 $a_x, a_y, a_z$ 分别为三轴加速度读数（单位：$g$）。然而，当设备剧烈运动时，运动加速度与重力分量叠加，上述公式将产生严重误差，因此单纯依靠加速度计仅适合静止或低动态场景（如横屏/竖屏切换、缓慢倾斜解谜）。

### 陀螺仪的工作方式

陀螺仪测量角速度（Angular Velocity），单位为 °/s 或 rad/s。消费级 MEMS 陀螺仪的典型量程为 ±250°/s 至 ±2000°/s，采样率一般为 100–1000 Hz。游戏引擎对陀螺仪数据进行时间积分可得当前旋转角度：

$$
\theta_{t} = \theta_{t-1} + \omega \cdot \Delta t
$$

其中 $\omega$ 为当前角速度，$\Delta t$ 为帧间隔时间（秒）。这一方法在短时间（< 5 秒）内精度较高，但 MEMS 陀螺仪存在固有的零偏漂移（Bias Drift），典型值为 0.01°/s 至 0.1°/s。长时间积分后，偏差会线性累积：若零偏为 0.05°/s，10 分钟后累积误差可达 30°，足以使游戏内视角完全偏移——这是单独依赖陀螺仪进行长时姿态追踪的核心技术难题。

### 互补滤波与传感器融合

为兼顾加速度计的长期稳定性（低频重力方向参考）和陀螺仪的短期精度（高频旋转响应），游戏引擎通常采用互补滤波器（Complementary Filter）对两路数据融合。其经典公式为：

$$
\theta_{\text{fused}} = \alpha \cdot \left(\theta_{\text{prev}} + \omega_{\text{gyro}} \cdot \Delta t\right) + (1 - \alpha) \cdot \theta_{\text{accel}}
$$

其中 $\alpha$ 通常取 0.96–0.98，高频分量由陀螺仪积分贡献，低频重力修正由加速度计提供。更精确的方案是 Kalman 滤波器，由 Rudolf Kálmán 于 1960 年在论文 *A New Approach to Linear Filtering and Prediction Problems* 中提出，可在状态估计中同时建模传感器噪声协方差，适用于需要高精度姿态解算的 VR/AR 设备（如 Meta Quest 3 的头部追踪）。

Unity 引擎通过 `Input.gyro.attitude` 直接暴露平台层已融合好的四元数姿态，底层即调用 iOS 的 `CMMotionManager` 或 Android 的 `TYPE_ROTATION_VECTOR` 传感器，后者融合了陀螺仪、加速度计和磁力计三路数据。

---

## 关键公式与 API 用法

下面以 Unity 为例，展示从原始传感器读取到应用旋转的完整流程：

```csharp
using UnityEngine;

public class MotionInputExample : MonoBehaviour
{
    // 互补滤波系数，推荐 0.96–0.98
    [SerializeField] private float alpha = 0.97f;

    private float fusedPitch = 0f;
    private Gyroscope gyro;

    void Start()
    {
        // 启用陀螺仪（默认关闭以省电）
        Input.gyro.enabled = true;
        gyro = Input.gyro;
    }

    void Update()
    {
        // 陀螺仪角速度（rad/s），Unity 坐标系中 x 轴对应 Pitch
        float gyroPitchRate = gyro.rotationRateUnbiased.x; // 已去零偏

        // 加速度计读数（单位 g）
        Vector3 accel = Input.acceleration;

        // 用加速度计估算静态倾斜角（弧度）
        float accelPitch = Mathf.Atan2(accel.y,
                               Mathf.Sqrt(accel.x * accel.x + accel.z * accel.z));

        // 互补滤波融合
        fusedPitch = alpha * (fusedPitch + gyroPitchRate * Time.deltaTime)
                   + (1f - alpha) * accelPitch;

        // 将融合角度应用到摄像机俯仰旋转
        transform.localRotation = Quaternion.Euler(
            fusedPitch * Mathf.Rad2Deg, 0f, 0f);
    }
}
```

注意：`gyro.rotationRateUnbiased` 是 Unity 在 iOS 上调用 `CMMotionManager.deviceMotion.rotationRate` 后减去估算偏置的结果；Android 端对应 `TYPE_GYROSCOPE_UNCALIBRATED` 经系统补偿后的值。若直接使用 `gyro.attitude`（已融合四元数），则上述手动融合步骤可省略，但开发者失去对滤波参数的控制权。

参考文献：Madgwick, S. O. H., Harrison, A. J. L., & Vaidyanathan, R. (2011). *Estimation of IMU and MARG orientation using a gradient descent algorithm*. IEEE International Conference on Rehabilitation Robotics. 该论文提出的 Madgwick 滤波器因计算量极低（单次迭代约 109 次浮点运算），已被 Unity、Unreal 等引擎的移动端姿态解算模块广泛参考。

---

## 实际应用

### 瞄准辅助（Gyro Aiming）

陀螺仪瞄准最典型的工业实现出现在《塞尔达传说：旷野之息》（Nintendo Switch，2017）和《战神》（PS4，2018）中。玩家先用右摇杆粗调方向，再用设备旋转进行精细瞄准，陀螺仪的高分辨率（采样率 200 Hz，角度分辨率 < 0.1°）使其在射击精度上优于纯摇杆。具体映射公式为：

$$
\Delta\text{yaw}_{\text{camera}} = \omega_{\text{gyro\_yaw}} \cdot S \cdot \Delta t
$$

其中 $S$ 为灵敏度系数，典型值 1.0–3.0，由玩家在设置菜单调节。

### 移动端重力感应

iOS 的 `UIInterfaceOrientationMask` 和 Unity 的 `Screen.orientation` 本质上都依赖加速度计的重力方向投票。《神庙逃亡》（Imangi Studios，2011）首月下载量突破 1000 万次，其左右倾斜躲避障碍物的核心机制仅用加速度计 X 轴读数映射角色横向速度，实现简单却高度直觉化。

### VR 头部追踪

Meta Quest 3 头戴设备使用 6-DoF IMU（惯性测量单元），其中旋转追踪（3-DoF）由内置陀螺仪完成，位移追踪（另外 3-DoF）则由外置摄像头的视觉里程计（Visual Odometry）补充。纯 IMU 旋转延迟（Motion-to-Photon Latency）需压缩至 20 ms 以下，否则会引发眩晕（Cybersickness）。

---

## 常见误区

**误区一：陀螺仪能单独实现长时间稳定追踪。**
实际上，MEMS 陀螺仪的零偏漂移（0.01–0.1°/s）决定了纯积分在数分钟内即会累积出不可接受的误差，必须配合加速度计或磁力计的外部参考修正。

**误区二：加速度计可以检测慢速旋转。**
加速度计只能感知比力（重力+运动加速度的合力），无法区分"设备绕竖轴缓慢转动"与"设备保持竖直静止"。Yaw 轴旋转时三轴重力分量几乎不变，因此加速度计对 Yaw 完全盲目，必须借助陀螺仪或磁力计（指南针）。

**误区三：直接使用原始加速度计数据做手势识别。**
未经低通滤波的加速度计数据含有大量高频机械振动噪声（尤其是手持设备），对原始信号直接阈值检测会产生大量误触发。正确做法是先施加截止频率约 5–10 Hz 的低通滤波器，再对平滑后的信号执行峰值检测。

**误区四：所有平台的坐标系一致。**
iOS 的加速度计 Y 轴朝上为正，而 Android 同样 Y 轴朝上为正，但陀螺仪的旋转正方向定义（右手定则 vs 左手定则）在不同厂商 ROM 上存在差异。Unity 的 `Input.gyro` 在内部做了坐标系统一，但若直接调用原生 SDK，需查阅各平台文档并手动转换。

---

## 知识关联

| 相关概念 | 关系说明 |
|---|---|
| **输入设备抽象**（前置） | 运动输入在引擎层被抽象为与按键/摇杆同级的输入通道，`Input.gyro` 和 `Input.acceleration` 就是这一抽象层的具体接口 |
| **四元数与旋转表示** | `gyro.attitude` 返回四元数（Quaternion），避免了欧拉角的万向锁（Gimbal Lock）问题；理解四元数乘法是正确应用运动输入的数学基础 |
| **物理引擎（刚体）** | 体感输入的加速度数据可直接作为 `Rigidbody.AddForce` 的驱动力来源，实现物理模拟下的重力感应滚球等