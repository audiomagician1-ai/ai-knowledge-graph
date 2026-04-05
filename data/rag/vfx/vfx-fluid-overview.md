---
id: "vfx-fluid-overview"
concept: "流体模拟概述"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
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


# 流体模拟概述

## 概述

流体模拟是游戏特效领域中用于模拟液体、气体、烟雾、火焰等流动现象的计算技术总称。其数学基础是纳维-斯托克斯方程（Navier-Stokes Equations），该方程组由法国工程师克劳德-路易·纳维（Claude-Louis Navier）于1822年首次推导，英国数学家乔治·加布里尔·斯托克斯（George Gabriel Stokes）于1845年完善，完整描述了黏性流体运动中动量守恒与质量守恒的耦合关系。时至今日，这组偏微分方程在三维情形下的光滑解存在性问题仍是克雷数学研究所七大"千禧年难题"之一，悬赏奖金100万美元。

游戏特效中的流体模拟从不追求严格的物理精确性，核心约束是计算时间预算：60fps游戏每帧仅有16.67毫秒完成所有逻辑、物理、AI和渲染，分配给单次流体效果的GPU时间通常不超过0.5至2毫秒。相比之下，《阿凡达》的离线流体特效单帧渲染耗时超过47小时。正是这一9个数量级的性能差距，决定了游戏流体算法必须走向极致的近似与简化路线。

《荒野大镖客：救赎2》的水体系统、《战神：诸神黄昏》的冰霜粒子流动、《控制》中超自然力量推动碎片与灰尘的混沌运动，都依赖于不同层次的流体模拟技术。理解流体模拟的核心方法谱系，是游戏特效技术美术（Technical Artist）和图形程序员的必备知识。

---

## 核心原理

### 纳维-斯托克斯方程的游戏简化形式

完整的不可压缩纳维-斯托克斯动量方程为：

$$\rho\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \rho \mathbf{g}$$

其中 $\rho$ 是流体密度（kg/m³），$\mathbf{u}$ 是速度场（m/s），$p$ 是压力（Pa），$\mu$ 是动力黏度（Pa·s），$\mathbf{g}$ 是重力加速度（9.8 m/s²）。连续性方程（质量守恒）要求不可压缩流体满足：

$$\nabla \cdot \mathbf{u} = 0$$

游戏实现中通常做以下三项简化：①忽略黏度扩散项 $\mu \nabla^2 \mathbf{u}$（对烟雾视觉效果影响极小）；②将压力泊松方程的精确求解替换为1至5次雅可比迭代；③将密度 $\rho$ 视为常数而非动态变量。这三项简化可将单帧流体计算量降低约95%，同时保留绝大部分视觉可信度。

参考文献：Jos Stam 于1999年在 SIGGRAPH 发表的论文《Stable Fluids》（Stam, 1999）是游戏实时流体模拟的奠基性工作，提出了半拉格朗日对流方案，从根本上解决了欧拉网格模拟中的数值不稳定问题，使实时流体模拟成为可能。

### 三大主流模拟方法的对比

**粒子系统近似法（Particle System）**是最早被游戏广泛采用的流体视觉近似方案，将流体离散为数千至数百万个独立粒子，每个粒子携带位置 $\mathbf{x}$、速度 $\mathbf{v}$、生命周期 $t_{life}$、颜色和透明度等属性。粒子间通过预设的引力/斥力场（即前置知识"吸引与排斥"所描述的机制）模拟流动感，时间复杂度为 $O(n)$（无粒子间交互）至 $O(n \log n)$（使用空间哈希加速的近邻查询）。粒子系统无法精确模拟流体的压力传播和自由表面，但在视觉上可通过精心设计的速度场驱动实现令人信服的水花、喷泉和尘烟效果。

**基于网格的欧拉法（Eulerian Grid Method）**将模拟空间划分为固定的三维体素网格（voxel grid），每个格子存储速度向量和标量（压强、温度、烟雾密度），流体属性通过对流和扩散在格子间传递。典型游戏实现采用32³至128³的分辨率（即32768至2097152个体素），更高分辨率则借助稀疏数据结构（如OpenVDB的稀疏体素树）按需激活网格。Unity VFX Graph 的 Fluid Simulation 模块和 Houdini 的 Pyro 系统均以此为基础，适合大范围烟雾、火焰和爆炸的模拟。

**光滑粒子流体动力学（Smoothed Particle Hydrodynamics，SPH）**由 Lucy（1977）和 Gingold & Monaghan（1977）独立提出，原为天体物理模拟设计。其核心思想是通过核函数 $W(\mathbf{r}, h)$ 将流体属性从离散粒子平滑插值到连续场：

$$A(\mathbf{r}) = \sum_j m_j \frac{A_j}{\rho_j} W(\mathbf{r} - \mathbf{r}_j, h)$$

其中 $m_j$ 是粒子质量，$\rho_j$ 是粒子密度，$h$ 是核半径（影响平滑范围，通常取粒子间距的1.2至2倍），$W$ 常采用三次样条核或 Poly6 核函数。SPH 同时具备粒子法的几何灵活性和一定的流体连续性，特别适合模拟水花飞溅、流体碰撞和高黏度熔岩，是《马里奥：奥德赛》水帽特效和《荒野大镖客2》浅水踩踏交互的技术基础。

### 不可压缩约束的实时求解策略

满足 $\nabla \cdot \mathbf{u} = 0$ 需要在每帧求解压力泊松方程：

$$\nabla^2 p = \frac{\rho}{\Delta t} \nabla \cdot \mathbf{u}^*$$

其中 $\mathbf{u}^*$ 是对流步骤后的中间速度场。精确求解需要共轭梯度法迭代至收敛（数十至数百次迭代），游戏中通常用固定次数（1至5次）的雅可比迭代替代，接受5%至15%的散度残差。这种"有意为之的不精确"在烟雾和气体效果中几乎不影响视觉结果，但在封闭容器内的液体模拟中可能导致体积轻微膨胀或收缩，实践中通过体积校正补偿项修正。

---

## 关键公式与算法

### 半拉格朗日对流（Semi-Lagrangian Advection）

Stam（1999）提出的半拉格朗日方案是实时流体模拟的核心算法，其思路是：要求网格点 $\mathbf{x}$ 在时刻 $t+\Delta t$ 的速度，等于从 $\mathbf{x}$ 沿速度场反向追踪 $\Delta t$ 时间到达位置 $\mathbf{x} - \mathbf{u}(\mathbf{x}, t)\Delta t$ 处的速度（再通过三线性插值获取）：

$$\mathbf{u}(\mathbf{x}, t+\Delta t) = \mathbf{u}(\mathbf{x} - \mathbf{u}(\mathbf{x}, t)\Delta t, \; t)$$

该方案无条件稳定（任意大时间步长不发散），这正是其革命性所在——此前的前向差分方案要求时间步长满足 CFL 条件 $\Delta t \leq h/|\mathbf{u}|_{max}$（其中 $h$ 为网格间距），严重限制了帧率。半拉格朗日方案的代价是引入数值耗散（artificial diffusion），导致烟雾细节随时间模糊，可通过 MacCormack 方案（Selle et al., 2008）二阶修正来部分补偿。

以下是简化的二维流体模拟对流步骤伪代码：

```python
def semi_lagrangian_advect(u, v, field, dx, dt):
    """
    u, v: 速度场 x/y 分量 (形状: [N, N])
    field: 待对流的标量场，如烟雾密度 (形状: [N, N])
    dx: 网格间距
    dt: 时间步长
    返回: 对流后的新标量场
    """
    N = field.shape[0]
    new_field = np.zeros_like(field)
    for i in range(N):
        for j in range(N):
            # 反向追踪：从当前位置沿速度场逆向一步
            x_prev = i - dt / dx * u[i, j]
            y_prev = j - dt / dx * v[i, j]
            # 双线性插值获取上一时刻该位置的场值
            new_field[i, j] = bilinear_interpolate(field, x_prev, y_prev)
    return new_field
```

实际 GPU 实现中，上述双重循环会替换为并行的 Compute Shader，在 NVIDIA RTX 3080 上处理 64³ 网格的对流步骤仅需约 0.3 毫秒。

---

## 实际应用

### 水面交互：高度场波动方程

《塞尔达传说：旷野之息》和《原神》的水面涟漪效果均采用了二维波方程（高度场简化），将三维流体问题降维为：

$$\frac{\partial^2 h}{\partial t^2} = c^2 \left(\frac{\partial^2 h}{\partial x^2} + \frac{\partial^2 h}{\partial z^2}\right) - d \frac{\partial h}{\partial t}$$

其中 $h(x, z, t)$ 是水面高度偏移，$c$ 是波速（通常设为1至3 m/s模拟平静水面），$d$ 是阻尼系数（控制涟漪消散速度，典型值0.005至0.02）。这一方案将三维流体的体积积分简化为二维网格的差分计算，在256×256分辨率下 GPU 计算耗时不超过0.05毫秒。

### 爆炸烟雾：低分辨率欧拉网格驱动粒子

《使命召唤：现代战争》系列的爆炸烟雾效果使用了32³体素欧拉网格预计算速度场，再用该速度场驱动100,000至500,000个视觉粒子（Velocity Field Driven Particles）。体素网格负责捕捉烟雾的宏观湍流结构（涡旋、膨胀），粒子负责提供视觉细节和透明度混合。这一混合方案（Hybrid Fluid Simulation）将单次爆炸的全部计算控制在1.2至1.8毫秒的 GPU 时间内，同时视觉上比纯粒子系统丰富3至5倍。

### 熔岩与高黏度液体

高黏度流体（如岩浆、史莱姆）的 SPH 模拟中，黏度力项需显式加入粒子间相互作用：

$$\mathbf{f}_i^{viscosity} = \mu \sum_j m_j \frac{\mathbf{u}_j - \mathbf{u}_i}{\rho_j} \nabla^2 W(\mathbf{r}_i - \mathbf{r}_j, h)$$

提高 $\mu$ 值（如从水的0.001 Pa·s增大至岩浆的100至1000 Pa·s等效参数）使粒子速度趋于一致，宏观上表现为缓慢、拉丝的流动行为，无需修改基础 SPH 算法框架。《战神》的熔岩区域和《暗黑破坏神4》的腐蚀黏液特效均采用了此类参数化调整方案。

---

## 常见误区

**误区一：粒子系统等同于流体模拟。** 传统粒子系统中每个粒子完全独立、互不感知，没有压力传播和密度约束，严格来说是"视觉近似"而非物理流体模拟。真正的流体模拟（SPH 或欧拉法）中，粒子或格子间存在基于物理方程的显式耦合。区分标