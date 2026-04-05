---
id: "cg-smoke-sim"
concept: "烟雾模拟"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 4
is_milestone: false
tags: ["模拟"]

# Quality Metadata (Schema v2)
content_version: 3
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


# 烟雾模拟

## 概述

烟雾模拟是计算机图形学体积渲染领域的核心技术之一，目标是在数字环境中真实再现烟雾、火焰、云雾等流体现象的运动与外观。烟雾在物理上是悬浮于气体中的微小固体或液体颗粒（直径约0.01μm～10μm）与气体介质的混合物，其宏观运动遵循不可压缩Navier-Stokes方程所描述的流体动力学规律。从图形学角度看，烟雾既是一种参与介质（光在其中发生单次及多重散射与吸收），又是一种随时间演化的动态流体，这使其模拟必须同时处理**流体仿真**与**体积渲染**两个层面。

现代烟雾模拟技术的奠基工作来自Jos Stam于1999年发表的论文《Stable Fluids》（ACM SIGGRAPH 1999），该论文提出了基于半拉格朗日对流和隐式黏性处理的无条件稳定流体求解方案，使得在时间步长 $\Delta t$ 不受CFL条件约束的前提下完成烟雾模拟成为可能。此前显式Euler积分在 $\Delta t > \Delta x / \|\mathbf{u}\|$ 时必然产生数值爆炸，而Stam方案以引入约5%～15%的数值耗散为代价彻底解决了稳定性问题。2003年，Fedkiw等人在《Visual Simulation of Smoke》（Stam & Fedkiw, ACM SIGGRAPH 2001）中引入涡度限制（Vorticity Confinement）方法，将数值耗散造成的涡旋损失以半经验方式补偿回来，成为影视级烟雾的标配技术。2009年前后，Ken Museth主导开发的OpenVDB稀疏体素数据结构（后于2012年开源，并获奥斯卡技术奖）将高分辨率烟雾网格的内存占用从 $O(N^3)$ 降低至仅存储活跃叶节点，使4096³量级的烟雾模拟在工作站上成为现实。

## 核心原理

### Euler方法：基于网格的烟雾模拟

Euler方法将流体域离散为固定的三维交错网格（MAC网格，Marker-and-Cell，由Harlow & Welch于1965年提出）。速度分量 $u, v, w$ 存储在相应面的中心，压力 $p$ 与烟雾密度 $\rho_s$、温度 $T$ 存储在体素中心。不可压缩烟雾的完整求解流程如下：

**第一步：对流（Advection）**

采用半拉格朗日方法，从当前格点 $\mathbf{x}$ 沿速度场反向追踪时间 $\Delta t$，到达位置 $\mathbf{x} - \Delta t \cdot \mathbf{u}(\mathbf{x})$，然后用三线性插值取得该位置的场值作为当前时刻的结果：

$$q^{n+1}(\mathbf{x}) = q^n\!\left(\mathbf{x} - \Delta t \cdot \mathbf{u}^n(\mathbf{x})\right)$$

其中 $q$ 可以是密度场、温度场或速度场中的任一分量。

**第二步：外力（External Forces）**

烟雾受到两类主要体力驱动：
- **重力**：$\mathbf{F}_g = -g\,\hat{\mathbf{z}}$（$g = 9.8\,\text{m/s}^2$）
- **热浮力**：$\mathbf{F}_b = \left(\alpha \rho_s - \beta (T - T_\text{amb})\right)\hat{\mathbf{z}}$

其中 $\alpha$ 为烟雾密度浮力系数（典型值0.1～0.5），$\beta$ 为温度浮力系数（典型值0.1），$T_\text{amb}$ 为环境温度。温度高于环境温度时产生上升驱动力，这正是烟雾自然向上飘散的物理根源。

**第三步：压力投影（Pressure Projection）**

对含散度的速度场求解泊松方程以强制无散度条件 $\nabla \cdot \mathbf{u} = 0$：

$$\nabla^2 p = \frac{\rho_f}{\Delta t} \nabla \cdot \mathbf{u}^*$$

其中 $\mathbf{u}^*$ 是加入外力后尚未投影的速度场，$\rho_f$ 为空气密度（约 $1.2\,\text{kg/m}^3$）。该泊松方程通常用PCG（预条件共轭梯度）迭代求解，收敛阈值取 $10^{-5}$ 量级。求解后更新速度：

$$\mathbf{u}^{n+1} = \mathbf{u}^* - \frac{\Delta t}{\rho_f} \nabla p$$

### Lagrange方法：基于粒子的烟雾模拟

Lagrange方法用大量移动粒子代表烟雾物质，每个粒子 $i$ 携带位置 $\mathbf{x}_i$、速度 $\mathbf{v}_i$、质量 $m_i$、温度 $T_i$、不透明度 $\alpha_i$ 等属性，粒子沿流场轨迹运动：

$$\frac{d\mathbf{x}_i}{dt} = \mathbf{v}_i, \quad \frac{d\mathbf{v}_i}{dt} = \mathbf{F}_i / m_i$$

纯Lagrange框架（如SPH）中粒子通过核函数 $W(r, h)$（支持半径 $h$ 通常取 $2\Delta x$）相互作用估计压力。但由于烟雾对无散度约束要求极为严格，而SPH的无散度执行误差较大，工业界极少将纯Lagrange方法单独用于烟雾求解。更常见的用法是将Lagrange粒子作为**湍流细节载体**，在Euler网格驱动的主流场之外，由粒子携带高频涡旋信息，从而绕过对流数值耗散的限制。

### 混合方法：FLIP与PIC

粒子与网格结合的FLIP（Fluid-Implicit-Particle）方法由Brackbill & Ruppel于1986年提出，后由Zhu & Bridson于2005年引入图形学液体模拟，随后被推广至烟雾场景。FLIP的核心思路是在网格上完成压力求解，但用粒子携带速度以消除对流数值耗散：

1. **P2G（粒子到网格）**：将粒子速度通过核权重插值到MAC网格面；
2. **网格求解**：在网格上执行外力施加与压力投影，得到速度增量 $\delta \mathbf{u} = \mathbf{u}_\text{grid}^{n+1} - \mathbf{u}_\text{grid}^n$；
3. **G2P（网格到粒子）**：将速度**增量**叠加到粒子速度（FLIP方式），而非直接用网格速度替换粒子速度（PIC方式）；
4. **粒子对流**：粒子用更新后的速度推进位置。

FLIP几乎无数值耗散，但可能引入高频噪声；PIC极度耗散但无噪声。实际应用中常取混合：$\mathbf{v}_i \leftarrow (1-\alpha)\mathbf{v}_\text{PIC} + \alpha\mathbf{v}_\text{FLIP}$，$\alpha$ 通常取0.95～0.99。

## 关键公式与算法

### 涡度限制（Vorticity Confinement）

Stam半拉格朗日方案的数值耗散会导致涡旋结构在数十帧内消失，使烟雾失去蓬松感。Fedkiw等人（2001）提出涡度限制力以补偿这一损失：

$$\boldsymbol{\omega} = \nabla \times \mathbf{u}$$

$$\mathbf{N} = \frac{\nabla |\boldsymbol{\omega}|}{|\nabla |\boldsymbol{\omega}||}, \quad \mathbf{F}_\text{conf} = \varepsilon \Delta x \left(\mathbf{N} \times \boldsymbol{\omega}\right)$$

其中 $\varepsilon$ 为涡度强化系数，典型值为0.1～5.0，$\Delta x$ 为网格间距。该力沿涡旋梯度方向将旋转能量"喂回"速度场，从而在不增加分辨率的前提下恢复视觉上丰富的湍流细节。

### 烟雾密度场的光学传输

烟雾渲染基于体积渲染方程（详见Beer-Lambert定律与参与介质理论）。沿视线 $s$ 方向的透射率为：

$$T(s_1, s_2) = \exp\!\left(-\int_{s_1}^{s_2} \sigma_t(s)\, ds\right)$$

其中消光系数 $\sigma_t = \sigma_a + \sigma_s$（吸收系数加散射系数）与烟雾密度场 $\rho_s$ 成正比，典型比例系数约为 $10\,\text{m}^{-1}$ 每单位密度。离散化后采用光线步进（Ray Marching），步长通常取格点间距的0.5倍以保证精度。

### 基于GPU的简化烟雾实现（伪代码）

```python
# 基于GPU的2D烟雾模拟核心循环（简化版，对应Stam 1999方案）
def simulate_step(u, v, density, dt, dx, viscosity):
    # 1. 对流：半拉格朗日反向追踪
    u_adv = semi_lagrange_advect(u, u, v, dt, dx)
    v_adv = semi_lagrange_advect(v, u, v, dt, dx)
    density_adv = semi_lagrange_advect(density, u, v, dt, dx)

    # 2. 施加浮力外力（alpha=0.25, beta=0.1, T_amb=0）
    alpha, beta = 0.25, 0.1
    buoyancy = alpha * density_adv - beta * temperature
    v_adv += dt * buoyancy  # 只作用于竖直速度分量

    # 3. 隐式黏性扩散（求解 (I - nu*dt*Laplacian) u = u_adv）
    u_diff = solve_implicit_diffusion(u_adv, viscosity, dt, dx)
    v_diff = solve_implicit_diffusion(v_adv, viscosity, dt, dx)

    # 4. 压力投影：强制无散度
    divergence = compute_divergence(u_diff, v_diff, dx)
    pressure = solve_poisson_pcg(divergence, dx, tol=1e-5)
    u_new = u_diff - dt / (rho_f * dx) * grad_x(pressure)
    v_new = v_diff - dt / (rho_f * dx) * grad_y(pressure)

    return u_new, v_new, density_adv
```

## 实际应用

### 影视视觉效果

影视级烟雾模拟通常在128³至512³的网格上运行，单帧求解时间为数分钟至数小时。工业标准工具包括Houdini（SideFX，PyroFX模块）、Autodesk Bifrost和Phoenix FD。以《复仇者联盟4》中的灭霸响指烟化效果为例，每个角色需要约2亿个烟雾粒子，结合Lagrange粒子与Euler网格的混合框架完成模拟，再通过Mantra渲染器的体积路径追踪得到最终画面。OpenVDB格式（.vdb文件）是该流程中烟雾数据交换的行业标准，支持稀疏存储，可将100GB量级的网格数据压缩至数GB。

### 实时游戏烟雾

受限于帧时间预算（16ms @ 60fps），游戏引擎中的烟雾模拟通常在32³至64³的低分辨率网格上运行（Unreal Engine的Fluid Simulation插件默认64³），或采用基于纹理的伪体积方法：将预先模拟的烟雾密度序列存入3D纹理，通过噪声扰动和UV动画模拟视觉上的运动感，计算量仅为真实流体模拟的1%。

**案例：** 在64³ Euler网格烟雾中，以 $\Delta x = 0.1\,\text{m}$、$\Delta t = 1/30\,\text{s}$ 为参数，涡度限制系数 $\varepsilon = 1.5$，一帧的浮力上升速度约为 $0.3\,\text{m/s}$，烟雾柱在约3秒（90帧）内上升约0.9m，与真实燃烧烟雾的视觉运动基本