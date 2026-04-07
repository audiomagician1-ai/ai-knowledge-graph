---
id: "vfx-fluid-flip"
concept: "FLIP/APIC方法"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 5
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
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



# FLIP/APIC方法

## 概述

FLIP（Fluid Implicit Particles）方法由Brackbill和Ruppel于1986年在《Journal of Computational Physics》发表的论文"FLIP: A method for adaptively zoned, particle-in-cell calculations of fluid flows in two dimensions"中首次提出，原始应用场景为等离子体物理中的磁流体动力学模拟。2005年，Zhu和Bridson在SIGGRAPH论文"Animating Sand as a Fluid"中将FLIP引入计算机图形学，证明该方法同样适用于沙粒和液态水的视觉模拟（Zhu & Bridson, 2005）。APIC（Affine Particle-In-Cell）则由Jiang、Schroeder、Selle、Teran和Stomakhin于2015年SIGGRAPH上提出，通过在粒子上存储仿射速度矩阵 $\mathbf{C}_p$ 来修复FLIP长期存在的角动量守恒缺陷（Jiang et al., 2015）。

FLIP/APIC属于混合粒子-网格（Particle-In-Cell, PIC）方法体系。其核心思想是将流体的物质属性（速度、密度、变形梯度）存储在拉格朗日粒子上，而压力求解、粘性扩散等数值运算在欧拉MAC网格（Marker-And-Cell staggered grid）上完成，两种表示方式在每个时间步之间通过加权插值相互转换。这种混合架构使其既能避免纯MAC网格方法因对流项离散化引入的数值耗散导致的涡量细节丢失，又能规避纯SPH方法在维护不可压缩性约束时 $O(N^{1.5})$ 至 $O(N^2)$ 量级的高计算成本。

在影视特效流水线中，Houdini 17+的FLIP Solver、SideFX官方DOP网络、Bifrost（Autodesk）以及Pixar内部水下特效系统均建立在此方法之上。《复仇者联盟：无限战争》（2018）中塔迦朵拉战役的大规模水体、《疯狂动物城》（2016）的雨水效果以及《海洋奇缘》（2016）标志性的翻涌海浪均采用了基于FLIP或APIC的求解器。其单个网格单元内可容纳8至16个粒子（三维标准配置）的特性，使自由液面的薄膜效果和高速飞溅细节远优于纯MAC网格方案。

---

## 核心原理

### P2G与G2P传输机制

FLIP方法每个时间步包含两次核心传输操作，分别称为粒子到网格（Particle-To-Grid, P2G）和网格到粒子（Grid-To-Particle, G2P）。

**P2G阶段**：将粒子携带的速度通过B样条权重函数插值到MAC交错网格的各速度分量节点上。权重核函数通常采用二次B样条（Quadratic B-spline，支撑域半径1.5个网格单元）或三次B样条（Cubic B-spline，支撑域半径2.0个网格单元）。对于网格节点 $i$，其速度由下式加权累积：

$$v_i^{\text{P2G}} = \frac{\sum_p w_{ip} \, v_p}{\sum_p w_{ip}}$$

其中 $w_{ip}$ 为粒子 $p$ 对节点 $i$ 的B样条权重，分母为归一化因子。

**G2P阶段（FLIP更新）**：在网格完成压力投影后，将速度增量（而非绝对速度）传回粒子：

$$v_p^{n+1} = v_p^n + \sum_i w_{ip} \left( v_i^{n+1} - v_i^n \right)$$

这与PIC方法的G2P更新 $v_p^{n+1} = \sum_i w_{ip} \, v_i^{n+1}$ 形成本质区别。PIC每步直接赋值导致速度信息被网格插值平滑，每帧损失约5%至15%的动能；FLIP通过增量更新保留粒子的速度历史，将每帧数值耗散降低至0.1%以下，但代价是高频噪声（撕裂伪影）随时间步累积。实际生产中常使用混合参数 $\alpha$ 将两者加权：

$$v_p^{\text{blend}} = \alpha \cdot v_p^{\text{FLIP}} + (1 - \alpha) \cdot v_p^{\text{PIC}}$$

$\alpha$ 通常取0.95至0.99。Houdini的FLIP Solver中该参数对应`Blend`滑块，默认值为0.95，将其降低至0.85可以在模拟翻腾泡沫时有效抑制粒子穿插噪声。

### APIC的仿射速度矩阵

APIC的核心改进是为每个粒子额外存储一个在二维场景中为 $2\times2$、在三维场景中为 $3\times3$ 的仿射速度矩阵 $\mathbf{C}_p$，用于描述粒子局部速度场的线性变化（包含剪切率、旋转角速度等信息）。G2P阶段同时更新矩阵：

$$\mathbf{C}_p = \frac{4}{\Delta x^2} \sum_i w_{ip} \, v_i \left( \mathbf{x}_i - \mathbf{x}_p \right)^T$$

其中 $\Delta x$ 为均匀网格间距，$\mathbf{x}_i$ 为节点 $i$ 的空间坐标，$\mathbf{x}_p$ 为粒子位置。P2G阶段，节点 $i$ 从粒子 $p$ 接收的速度贡献变为：

$$v_i \mathrel{+}= w_{ip} \left[ v_p + \mathbf{C}_p \left( \mathbf{x}_i - \mathbf{x}_p \right) \right]$$

与标准FLIP的P2G相比，多了 $\mathbf{C}_p(\mathbf{x}_i - \mathbf{x}_p)$ 这一局部仿射修正项，使粒子能将自身携带的旋转和剪切信息精确传递给相邻网格节点，而不仅仅是平均速度值。这一修改使APIC在数学上严格守恒角动量和线动量，消除了FLIP中由于速度场不连续导致的涡旋耗散。在龙卷风模拟实验中，APIC能持续维持涡旋结构长达500帧以上，而标准FLIP（$\alpha=0.97$）在约80帧后旋转动能即衰减至初始值的50%以下。

### 压力投影与自由液面处理

网格阶段的核心是求解泊松方程，确保速度场满足无散度约束，对应模拟不可压缩流体的物理假设：

$$\nabla \cdot \left( \frac{1}{\rho} \nabla p \right) = \frac{\nabla \cdot \mathbf{u}^*}{\Delta t}$$

其中 $\mathbf{u}^*$ 为对流和外力步骤后的中间速度场，$p$ 为待求压力，$\rho$ 为流体密度，$\Delta t$ 为时间步长。该方程离散化后形成稀疏对称正定线性系统，标准求解器为预条件共轭梯度法（PCG），预条件子通常采用不完全Cholesky分解（IC(0)）。

自由液面（air-water interface）的处理采用Ghost Fluid Method（Fedkiw et al., 1999）：在液面网格单元设置狄利克雷边界条件 $p=0$（大气压），通过Level Set函数 $\phi(\mathbf{x})$ 确定液面位置，液面法线方向的压力梯度经过次网格精度修正以避免界面处的速度不连续。粒子密度不足（少于2个粒子/单元）的网格单元被标记为"空气单元"并从压力求解中排除，这是避免液面区域压力求解发散的关键步骤。

---

## 关键公式与算法流程

完整的APIC时间步迭代伪代码如下：

```python
# APIC单时间步伪代码（三维，均匀网格间距 dx）
def apic_timestep(particles, grid, dt, dx):
    # 1. P2G：粒子属性传输至网格
    grid.reset()  # 清零网格速度和质量
    for p in particles:
        for i in p.neighbor_nodes(dx):  # 遍历支撑域内节点（最多27个）
            w = quadratic_bspline(p.x, grid.node_pos(i), dx)
            # 仿射修正：将C_p的局部速度场贡献加入节点
            v_contrib = p.v + p.C @ (grid.node_pos(i) - p.x)
            grid.v[i] += w * p.mass * v_contrib
            grid.mass[i] += w * p.mass
    grid.v /= grid.mass  # 质量归一化

    # 2. 施加外力（重力等）
    grid.v += dt * gravity

    # 3. 边界条件（固体碰撞、自由液面标记）
    apply_boundary_conditions(grid)

    # 4. 压力投影（PCG求解泊松方程，确保 div(v)=0）
    p_field = solve_pressure_poisson(grid, dt)
    grid.v -= dt / rho * gradient(p_field)

    # 5. G2P：网格速度传回粒子，更新C_p矩阵
    for p in particles:
        p.v = 0.0
        p.C = zeros(3, 3)
        for i in p.neighbor_nodes(dx):
            w = quadratic_bspline(p.x, grid.node_pos(i), dx)
            p.v += w * grid.v[i]
            # APIC核心：更新仿射速度矩阵
            p.C += (4.0 / dx**2) * w * outer(grid.v[i], grid.node_pos(i) - p.x)

    # 6. 粒子对流（半拉格朗日或RK3积分）
    for p in particles:
        p.x += dt * p.v  # 一阶欧拉，生产中常用RK3
```

例如，在Houdini中模拟一个半径0.5m的水球爆裂，典型设置为：网格分辨率128³，粒子数约400万，时间步长 $\Delta t = 0.005\text{s}$（对应CFL数约0.5），压力PCG求解在GTX 4090上耗时约18ms/帧，总模拟时长（250帧）约75分钟。

---

## 实际应用

### 影视特效中的大规模水体

基于APIC的求解器已成为A级制作的标准配置。在Houdini的FLIP Solver工作流中，动力学团队通常先用低分辨率（64³至128³）网格完成动作布局，确认效果后切换至256³或512³进行最终模拟。《海洋奇缘》制作团队（Walt Disney Animation Studios）公开报告其海浪模拟采用了512×256×512的自适应网格，单帧峰值粒子数超过2.5亿，依赖定制的GPU-APIC求解器（Stomakhin et al., 2013的MPM框架延伸）。

### 与MPM方法的结合

APIC的仿射矩阵 $\mathbf{C}_p$ 机制直接催生了物质点法（MPM，Material Point Method）的现代形式——MLS-MPM（Moving Least Squares MPM，Hu et al., 2018）。在弹塑性雪、泥浆、沙的模拟中，MPM在APIC的P2G/G2P框架上增加了变形梯度 $\mathbf{F}_p$ 的更新和本构模型（如Neo-Hookean、Drucker-Prager塑性准则），用同一套代码框架统一处理流体、固体和颗粒物质的耦合模拟，是《冰雪奇缘》雪地效果的技术基础。

### 泡沫与薄膜效果

FLIP特别擅长模拟飞溅液滴和泡沫层，因为孤立粒子在远离液面后可脱离网格求解，转为纯拉格朗日粒子（通常称为"bubble particles"或"foam particles"）继续运动，不再占用压力求解资源。Houdini中通过`whitewater solver`在FLIP模拟完成后提取速度场的散度、曲率和加速度，在超过阈值的区域生成泡沫/浪花粒子，每个泡沫粒子的生命周期、聚合行为和消散均有独立参数控制。

---

## 常见误区

**误区1：认为FLIP总优于PIC**。FLIP在 $\alpha=1.0$ 时确实噪声最小、细节最丰富，但在涉及高速碰撞（流体撞击固体的速度超过10m/s