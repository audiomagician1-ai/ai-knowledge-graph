---
id: "fluid-simulation"
concept: "流体模拟"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 3
is_milestone: false
tags: ["流体"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 流体模拟

## 概述

流体模拟是物理引擎中对液体、气体等连续介质的运动行为进行数值计算的技术，其数学基础是纳维-斯托克斯方程（Navier-Stokes Equations，简称N-S方程）。该方程描述不可压缩黏性流体的动量守恒，完整形式为：

$$\rho\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \rho \mathbf{g}$$

其中 $\rho$ 为流体密度（水在20°C时为998 kg/m³），$\mathbf{u}$ 为速度场，$p$ 为压力，$\mu$ 为动态黏度（水约为0.001 Pa·s，蜂蜜约为2~10 Pa·s），$\mathbf{g}$ 为重力加速度（9.8 m/s²）。这个方程的解析解至今只在极少数简化情形下存在，克莱数学研究所甚至将其光滑解的存在性问题列为七大"千禧年难题"之一，悬赏100万美元。游戏引擎必须依赖数值近似方法绕开这一难题。

流体模拟的工程实用化始于20世纪60年代，美国洛斯阿拉莫斯国家实验室将有限差分法用于核武器流体冲击波计算。游戏领域的转折点是1999年：Jos Stam在SIGGRAPH 1999发表的论文《Stable Fluids》提出了无条件稳定的半拉格朗日对流方案，使流体模拟在游戏帧率（30~60fps）下不发散，彻底改变了实时流体的可行性。此后，基于拉格朗日视角的SPH（Smoothed Particle Hydrodynamics，光滑粒子流体动力学）和基于欧拉固定网格的方法成为游戏物理引擎的两大主流技术路线（Müller et al., 2003）。

---

## 核心原理

### 拉格朗日视角：SPH方法

SPH将流体离散为一组携带质量的粒子，每个粒子追踪自身的位置 $\mathbf{x}_i$、速度 $\mathbf{v}_i$、密度 $\rho_i$ 和压力 $p_i$。其核心思想是用核函数 $W(\mathbf{r}, h)$ 对邻域粒子的物理量进行加权平均，其中 $h$ 称为光滑长度（通常设为粒子间距的1.2至1.5倍）。任意物理量 $A$ 在位置 $\mathbf{r}$ 处的SPH插值为：

$$A(\mathbf{r}) = \sum_j m_j \frac{A_j}{\rho_j} W(\mathbf{r} - \mathbf{r}_j, h)$$

游戏引擎中最常用的核函数是Müller等人（2003）提出的多项式核，针对压力计算：

$$W_{\text{pressure}}(r, h) = \frac{15}{\pi h^6}(h - r)^3, \quad 0 \leq r \leq h$$

以及针对黏性项的拉普拉斯核：

$$\nabla^2 W_{\text{viscosity}}(r, h) = \frac{45}{\pi h^6}(h - r), \quad 0 \leq r \leq h$$

压力由弱可压缩状态方程计算：$p_i = k\left(\frac{\rho_i}{\rho_0} - 1\right)$，其中 $k$ 为刚度系数（实际调参中水常取 $k = 1000$ Pa），$\rho_0 = 1000$ kg/m³ 为参考密度。每帧对每个粒子施加压力梯度力、黏性力和重力，再用显式积分（Leap-Frog或Verlet方法，时间步长约 $0.5 \sim 2$ ms）推进位置。

SPH的优势是自然处理自由液面和大变形（飞溅、破碎），无需追踪液面拓扑；缺点是粒子数超过约10万时实时压力计算开始困难，且基础SPH存在密度误差累积导致的流体"穿透"问题，NVIDIA PhysX的FleX模块（2013年发布）通过Position-Based Fluids（PBF，Macklin & Müller, 2013）改进了这一点，将每帧迭代次数控制在2~4次即可收敛，支持GPU上百万粒子规模的实时模拟。

### 欧拉视角：稳定流体与网格方法

欧拉方法在固定笛卡尔网格上描述流体，每个格子存储速度分量、压力、密度等场量。Jos Stam的稳定流体算法（1999）将每帧的计算拆成三个顺序步骤：

1. **对流（Advection）**：将速度场沿流线向后追踪一个时间步 $\Delta t$，即对每个格子的速度 $\mathbf{u}(\mathbf{x})$，追踪到上一帧位置 $\mathbf{x} - \Delta t \cdot \mathbf{u}(\mathbf{x})$，用三线性插值采样旧速度场。这一步无条件稳定，是Stam方法的核心贡献。
2. **扩散（Diffusion）**：隐式求解黏性扩散方程 $(I - \mu \Delta t \nabla^2)\mathbf{u}^{n+1} = \mathbf{u}^*$，用高斯-赛德尔迭代收敛（通常迭代20次以内）。
3. **投影（Projection）**：求解压力泊松方程 $\nabla^2 p = \frac{\rho}{\Delta t} \nabla \cdot \mathbf{u}^*$，然后修正速度场 $\mathbf{u}^{n+1} = \mathbf{u}^* - \frac{\Delta t}{\rho} \nabla p$，使速度场满足无散条件 $\nabla \cdot \mathbf{u} = 0$。

投影步是计算瓶颈：对128³分辨率的3D网格，每帧需要求解约200万个未知量的线性系统，共轭梯度法迭代一次约需数百毫秒，仅适合离线渲染（如电影特效）。实时游戏通常将网格压缩到32³或64³，并限制迭代次数为10~20次，以4~10ms完成单帧。

### 2D高度场近似与浅水方程

游戏中水面最常见的实现是2D高度场近似：将水面建模为一个标量高度图 $h(x, z, t)$，由浅水方程（Shallow Water Equations, SWE）驱动：

$$\frac{\partial h}{\partial t} + \nabla \cdot (h \mathbf{v}) = 0$$
$$\frac{\partial \mathbf{v}}{\partial t} + (\mathbf{v} \cdot \nabla)\mathbf{v} = -g \nabla h$$

忽略对流项后退化为线性波动方程，波速 $c = \sqrt{g H}$（$H$ 为平均水深，例如水深4m时 $c \approx 6.3$ m/s）。这种方法在GPU上用256×256的网格每帧仅需约0.5ms，广泛用于《刺客信条：黑旗》（2013）和《地平线：西部禁地》（2022）等开放世界游戏的海洋渲染，可实时模拟船只尾迹、投石涟漪和岸边碎波。

---

## 关键公式与算法

### PBF（Position-Based Fluids）约束方程

PBF（Macklin & Müller, 2013）将不可压缩约束表达为位置修正问题。对粒子 $i$，定义密度约束：

$$C_i(\mathbf{x}_1, \ldots, \mathbf{x}_n) = \frac{\rho_i}{\rho_0} - 1 = 0$$

每次迭代计算位置修正量：

$$\Delta \mathbf{x}_i = \frac{1}{\rho_0} \sum_j (\lambda_i + \lambda_j) \nabla_{\mathbf{x}_i} W(\mathbf{x}_i - \mathbf{x}_j, h)$$

其中拉格朗日乘子 $\lambda_i = -\frac{C_i}{\sum_k |\nabla_{\mathbf{x}_k} C_i|^2 + \varepsilon}$，松弛参数 $\varepsilon$（通常取 $10^{-6}$）防止分母为零。

### 简易2D流体模拟代码片段（Python伪代码）

```python
# 基于Stam稳定流体的简化2D欧拉网格流体，网格尺寸N=64
import numpy as np

N = 64
dt = 0.1
diff = 0.0001   # 扩散系数（对应水的运动黏度约1e-6 m²/s的简化）
visc = 0.0      # 游戏中水的黏性可设为0简化计算

def diffuse(x, x0, diff, dt):
    a = dt * diff * (N - 2) ** 2
    # 高斯-赛德尔迭代20次
    for _ in range(20):
        x[1:-1, 1:-1] = (x0[1:-1, 1:-1] +
            a * (x[:-2, 1:-1] + x[2:, 1:-1] +
                 x[1:-1, :-2] + x[1:-1, 2:])) / (1 + 4 * a)
    return x

def project(u, v, p, div):
    # 计算散度
    div[1:-1, 1:-1] = -0.5 * (u[2:, 1:-1] - u[:-2, 1:-1] +
                               v[1:-1, 2:] - v[1:-1, :-2]) / N
    p[:] = 0
    # 迭代求解压力泊松方程
    for _ in range(20):
        p[1:-1, 1:-1] = (div[1:-1, 1:-1] +
            p[:-2, 1:-1] + p[2:, 1:-1] +
            p[1:-1, :-2] + p[1:-1, 2:]) / 4
    # 修正速度场，保证无散
    u[1:-1, 1:-1] -= 0.5 * N * (p[2:, 1:-1] - p[:-2, 1:-1])
    v[1:-1, 1:-1] -= 0.5 * N * (p[1:-1, 2:] - p[1:-1, :-2])
    return u, v
```

---

## 实际应用

### 游戏引擎中的流体中间件

NVIDIA PhysX（PhysX 5.0，2022年发布）内置了基于PBF的粒子流体系统，支持GPU加速，在RTX 3080上可实时模拟约100万SPH粒子（帧率30fps，粒子直径约5cm，适合模拟人体尺度的水缸或浴缸场景）。Unity的Visual Effect Graph（VFX Graph）提供了基于Grid方法的烟雾和火焰模拟节点，分辨率上限为128³，适合营地篝火和爆炸冲击波特效。Unreal Engine 5的Chaos Physics模块在5.3版本（2023）中加入了实验性流体解算器，采用FLIP（Fluid-Implicit-Particle）混合方法——粒子负责对流，网格负责压力求解——兼顾了SPH和欧拉方法的优点。

### 案例：《荒野大镖客：救赎2》的河流

Rockstar Games在《荒野大镖客：救赎2》（2018）中的水面使用了多层叠加的2D高度场：底层是FFT驱动的大尺度涌浪（波长10~100m），中层是基于浅水方程的局部涟漪（响应角色涉水和投射物落水），顶层是视差贴图叠加的细节泡沫噪声。三层合计GPU开销约3ms/帧，在PS4（1.84 TFLOPS）上维持了30fps目标帧率。

---

## 常见误区

**误区1：SPH粒子越多越精确**
粒子数量翻倍并不意味着精度线性提升。基础弱可压缩SPH（WCSPH）使用显式时间积分，稳定性要求时间步长满足 $\Delta t \leq 0.4 h / c_s$（$c_s$ 为声速，水中约1500 m/s），粒子间距缩小一半时时间步长必须缩短至少一半，计算量以 $O(N^{4/3})$ 增长。因此在实时场景中盲目增加粒子数量会导致帧率崩溃，正确做法是根据目标帧率预算反推最大粒子数。

**误区2：欧