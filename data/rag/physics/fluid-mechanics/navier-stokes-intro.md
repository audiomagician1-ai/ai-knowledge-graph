---
id: "navier-stokes-intro"
concept: "纳维-斯托克斯方程简介"
domain: "physics"
subdomain: "fluid-mechanics"
subdomain_name: "流体力学"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---

# 纳维-斯托克斯方程

## 概述

纳维-斯托克斯方程（Navier-Stokes Equations，简称NS方程）是描述粘性流体运动的偏微分方程组，由法国工程师克劳德-路易·纳维（Claude-Louis Navier）于1822年首先推导，英国数学家乔治·斯托克斯（George Gabriel Stokes）于1845年在更严格的数学框架下独立完成推导。这组方程本质上是牛顿第二定律（$F = ma$）在连续介质中的具体表达：流体微元的质量乘以加速度，等于作用在其上的所有力之和，包括压力梯度力、粘性力和体积力（如重力）。

NS方程至今仍是千禧年数学难题（Clay Millennium Problems）之一——其三维情形光滑解的存在性与唯一性尚未被证明，悬赏奖金高达100万美元（Clay Mathematics Institute, 2000）。尽管如此，NS方程在工程计算中的应用已经极为成熟，从飞机翼型设计到血管中的血流模拟，均依赖此方程。

---

## 核心原理

### NS方程的完整形式

对于不可压缩牛顿流体，NS方程由两部分组成：

**动量方程（矢量形式）：**

$$\rho \left(\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \rho \mathbf{g}$$

**连续性方程（不可压缩条件）：**

$$\nabla \cdot \mathbf{u} = 0$$

各符号含义如下：

| 符号 | 物理含义 | 量纲 |
|------|----------|------|
| $\rho$ | 流体密度 | kg/m³ |
| $\mathbf{u}$ | 速度场矢量 | m/s |
| $t$ | 时间 | s |
| $p$ | 压力场 | Pa |
| $\mu$ | 动力粘度 | Pa·s |
| $\mathbf{g}$ | 重力加速度矢量（9.8 m/s²） | m/s² |

动量方程左侧的 $(\mathbf{u} \cdot \nabla)\mathbf{u}$ 是**对流加速度项**，这一非线性项正是NS方程难以求解的根本原因，也是湍流产生的数学根源。

### 各力项的物理含义拆解

将动量方程右侧逐项分析：

- $-\nabla p$：**压力梯度力**，流体从高压区向低压区流动的驱动力。例如，心脏收缩产生的血压梯度驱动血液在动脉中流动。
- $\mu \nabla^2 \mathbf{u}$：**粘性扩散项**，描述流体内部因分子间摩擦而产生的动量扩散。动力粘度 $\mu$ 对水（20°C时约为 $1.002 \times 10^{-3}$ Pa·s）和蜂蜜（约2~10 Pa·s）相差约4个数量级，直接决定该项的量级。
- $\rho \mathbf{g}$：**体积力项**，在竖直方向的流动（如烟囱气流、海洋环流）中不可忽略。

### 雷诺数与方程的物理分类

方程中对流项与粘性项之比定义为雷诺数（Reynolds Number）：

$$Re = \frac{\rho U L}{\mu} = \frac{UL}{\nu}$$

其中 $U$ 为特征速度，$L$ 为特征长度，$\nu = \mu/\rho$ 为运动粘度。雷诺数由奥斯本·雷诺（Osborne Reynolds）于1883年通过著名的管道染色实验确定其临界意义：

- $Re < 2300$：层流，粘性力主导，NS方程往往有解析解（如泊肃叶流）
- $2300 < Re < 4000$：过渡流
- $Re > 4000$：湍流，对流项完全主导，只能数值求解

---

## 关键简化情况

### 斯托克斯流（蠕变流）

当 $Re \ll 1$ 时，对流加速度项 $(\mathbf{u} \cdot \nabla)\mathbf{u}$ 相比粘性项可忽略不计，NS方程线性化为**斯托克斯方程**：

$$\nabla p = \mu \nabla^2 \mathbf{u}$$

**典型场景**：微生物游动（细菌鞭毛的 $Re \approx 10^{-4}$）、微流控芯片中的液体输运、地幔对流（粘度高达 $10^{21}$ Pa·s）。

斯托克斯在此简化下推导出著名的**斯托克斯阻力公式**：

$$F_d = 6\pi \mu r v$$

其中 $r$ 为球体半径，$v$ 为球体速度。这一公式被用来测定电子电荷——密立根（Robert Millikan）在1909年的油滴实验中正是利用此公式计算油滴所受粘性阻力。

### 欧拉方程（无粘流）

当 $Re \to \infty$ 时，粘性力相比惯性力可忽略，令 $\mu = 0$，NS方程退化为**欧拉方程**：

$$\rho \left(\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u}\right) = -\nabla p + \rho \mathbf{g}$$

进一步对稳态、不可压缩、沿流线积分，可得**伯努利方程**：

$$p + \frac{1}{2}\rho v^2 + \rho g h = \text{常数}$$

**适用范围**：飞机机翼外部气流（远离边界层区域）、水轮机主流区计算。

### 泊肃叶流（圆管层流精确解）

对于半径为 $R$、沿 $z$ 轴方向的稳态层流，NS方程有精确解析解，速度分布为抛物线型：

$$u_z(r) = \frac{1}{4\mu}\left(-\frac{dp}{dz}\right)(R^2 - r^2)$$

体积流量为：

$$Q = \frac{\pi R^4}{8\mu} \left(-\frac{dp}{dz}\right)$$

这就是**哈根-泊肃叶定律**（Hagen-Poiseuille Law），由哈根（Gotthilf Hagen）和泊肃叶（Jean Poiseuille）分别于1839年独立发现。注意流量与半径的**四次方**成正比——动脉狭窄10%会导致流量下降约34%，这正是心血管疾病中血管狭窄危害极大的物理原因。

---

## 实际应用

### 计算流体力学（CFD）数值求解

由于NS方程几乎不存在一般解析解，工程中普遍采用数值离散方法：

```python
# 使用有限差分法求解二维不可压缩NS方程的简化示意
import numpy as np

# 网格参数
nx, ny = 41, 41          # 网格点数
dx = 2 / (nx - 1)        # x方向步长
dy = 2 / (ny - 1)        # y方向步长
dt = 0.001               # 时间步长
nu = 0.1                 # 运动粘度 (m²/s)
rho = 1.0                # 密度 (kg/m³)

# 初始化速度场
u = np.zeros((ny, nx))
v = np.zeros((ny, nx))
p = np.zeros((ny, nx))

# 动量方程（x分量）显式时间推进（简化示意）
def update_u(u, v, p, dx, dy, dt, nu, rho):
    un = u.copy()
    vn = v.copy()
    u[1:-1, 1:-1] = (un[1:-1, 1:-1]
        - un[1:-1, 1:-1] * dt/dx * (un[1:-1, 1:-1] - un[1:-1, :-2])   # 对流项
        - vn[1:-1, 1:-1] * dt/dy * (un[1:-1, 1:-1] - un[:-2, 1:-1])
        - dt/(2*rho*dx) * (p[1:-1, 2:] - p[1:-1, :-2])                 # 压力梯度项
        + nu * dt/dx**2 * (un[1:-1, 2:] - 2*un[1:-1, 1:-1] + un[1:-1, :-2])  # 粘性项
        + nu * dt/dy**2 * (un[2:, 1:-1] - 2*un[1:-1, 1:-1] + un[:-2, 1:-1]))
    return u
```

此类数值方法是现代商业CFD软件（如ANSYS Fluent、OpenFOAM）的计算核心，波音737机翼的气动外形优化、特斯拉电动车的冷却系统设计均依赖此类求解流程。

### 气象预报与海洋模拟

全球大气环流模式（GCM）本质上是在球坐标系下对NS方程的数值积分，时间步长通常为20~30分钟，水平网格分辨率约25 km（ECMWF模式，2023年）。海洋环流模拟（如NEMO模式）则在NS方程中额外加入科氏力项 $-2\rho\boldsymbol{\Omega}\times\mathbf{u}$，以描述地球自转对流体运动的偏转效应。

---

## 常见误区

### 误区一：认为NS方程只适用于液体

NS方程对气体同样适用，前提是气体速度远低于声速（马赫数 $Ma < 0.3$），此时密度变化不超过5%，不可压缩假设成立。超音速流（$Ma > 1$）需要引入可压缩NS方程，连续性方程变为 $\frac{\partial\rho}{\partial t} + \nabla\cdot(\rho\mathbf{u}) = 0$。

### 误区二：将欧拉方程等同于无粘流的完整描述

欧拉方程忽略粘性后，虽然数学上简化，却导致**达朗贝尔悖论（d'Alembert's Paradox, 1752）**：无粘流绕任意物体的阻力为零，与实验严重矛盾。普朗特（Ludwig Prandtl）于1904年提出**边界层理论**，指出即使 $Re$ 很大，物体表面附近极薄的边界层（厚度 $\delta \sim L/\sqrt{Re}$）内粘性仍不可忽略，这才统一了理论与实验。

### 误区三：混淆动力粘度与运动粘度

- 动力粘度 $\mu$（单位：Pa·s）反映流体抵抗剪切变形的能力，空气（20°C）约为 $1.81\times10^{-5}$ Pa·s
- 运动粘度 $\nu = \mu/\rho$（单位：m²/s），空气约为 $1.51\times10^{-5}$ m²/s，水约为 $1.0\times10^{-6}$ m²/s

尽管空气的动力粘度远小于水，但空气的运动粘度（$\nu_{\text{air}}/\nu_{\text{water}} \approx 15$）却比水大约15倍，这意味着在同等速度和尺度下，空气流动比水流动更难达到湍流状态。

### 误区四：认为湍流是NS方程的"失效"

湍流并非NS方程的适用边界，而是方程在高 $Re$ 条件下的正确物理预测——解的混沌敏感性正是湍流的数学本质。当前直接数值模拟（DNS）已能用NS方程精确重现 $Re$ 达数千的湍流结构，只是计算量以 $Re^{9/4}$ 增长极为剧烈（Pope, 2000）。

---

## 知识关联

### 前置知识：粘性

牛顿粘性定律 $\tau = \mu \frac{du}{dy}$ 是NS方程中粘性项 $\mu\nabla^2\mathbf{u}$ 的微观基础。若不理解粘性系数 $\mu$ 的物理意义，NS方程中的粘性扩散项将只是一个符号，无法建立"分子动量交换导致流层间速度均一化"的物理图像。

### 横向联系：热传导方程与扩散方程

NS方程的粘性项 $\mu\nabla^2\mathbf{u}$ 在数学结构上与热传导方程 $\frac{\partial T}{\partial t} = \alpha\nabla^2 T$ 完全类似，热扩散率 $\alpha$ 对应运动粘度 $