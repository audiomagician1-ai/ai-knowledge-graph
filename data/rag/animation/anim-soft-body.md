---
id: "anim-soft-body"
concept: "软体模拟"
domain: "animation"
subdomain: "physics-animation"
subdomain_name: "物理动画"
difficulty: 3
is_milestone: false
tags: ["进阶"]

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



# 软体模拟

## 概述

软体模拟（Soft Body Simulation）是物理动画中专门处理具有弹性形变能力的三维体积物体的技术，涵盖果冻、橡胶球、生物器官、肌肉组织、海绵、充气玩具等材质的动态行为。与布料模拟处理二维薄层结构不同，软体模拟的对象是具有内部体积的三维实体——其所有内部质点之间都存在弹性约束，形变后会产生可观察的侧向膨胀、回弹和振荡效果。

软体模拟的奠基性工作来自 Terzopoulos、Platt、Barr 与 Fleischer 于1987年在 SIGGRAPH 发表的论文《Elastically Deformable Models》，该论文将连续介质弹性力学方程（Continuum Mechanics）首次系统引入计算机图形学，定义了软体物体的应变能（Strain Energy）表达式，奠定了此后三十余年软体动画的数学框架（Terzopoulos et al., 1987）。1998年，Baraff 与 Witkin 在《Large Steps in Cloth Simulation》中提出的隐式积分方法，同样被广泛移植至软体求解器以解决数值稳定性问题。2005年前后，Müller 等人提出的基于位置的动力学（Position-Based Dynamics，PBD）方法将软体求解速度提升至可交互帧率，使实时软体模拟进入游戏引擎成为可能。

从工业应用时间线看：Houdini 在2005年前后的版本中集成了有限元软体求解器（FEM Solver）；Blender 2.40（2005年12月发布）加入了内置软体模块；Maya 的 nCloth/nSolver 系统于2007年随 Maya 8.5 推出，可同时处理布料与软体约束；Unity 和 Unreal Engine 4 分别在2014年后通过 NVIDIA PhysX 提供实时软体支持，但出于性能考量，两者在商业发行版中长期禁用完整软体功能，转而以 PBD 近似替代。

---

## 核心原理

### 质点-弹簧网络（Mass-Spring Network）

软体模拟最直观的实现方式是将网格每个顶点视为有质量的质点，顶点之间通过虚拟弹簧连接。单根弹簧的弹力遵循胡克定律（Hooke's Law）：

$$F = -k \cdot (L - L_0)$$

其中 $k$ 为弹簧刚度系数（单位：N/m），$L$ 为当前长度，$L_0$ 为自然静止长度。三维软体网络中通常同时部署三类弹簧：

- **结构弹簧（Structural Springs）**：连接网格中直接相邻的顶点，维持物体基本形状，$k$ 值最大（如橡胶球约为 500～2000 N/m）。
- **剪切弹簧（Shear Springs）**：连接同一面上的对角顶点，抵抗网格剪切形变，$k$ 值约为结构弹簧的 0.5～0.8 倍。
- **弯曲弹簧（Bend Springs）**：跨越一个中间顶点的"远程"连接，控制整体体积刚性，$k$ 值最小（约为结构弹簧的 0.1～0.3 倍），决定材质"软硬"的感知效果。

仅调节三类弹簧的 $k$ 值比例，即可在同一套算法框架下模拟从软糖（低 $k$）到硬橡皮擦（高 $k$）的全系列材质。

### 体积保存约束（Volume Preservation）

橡胶、凝胶等真实材质的泊松比（Poisson's Ratio）$\nu$ 接近 0.5，意味着近似不可压缩——被竖向压缩时横向膨胀，总体积几乎守恒。若软体求解器不施加体积保存约束，果冻被重力压扁后只会变薄而不会侧向鼓出，视觉上失真明显。

Blender 软体模块通过"Pressure"参数实现体积保存：系统在每帧计算当前网格体积 $V_{current}$ 与目标体积 $V_0$ 之差，并向所有顶点施加等效气压力：

$$F_{pressure} = k_p \cdot \frac{V_0 - V_{current}}{V_0} \cdot \hat{n}$$

其中 $k_p$ 为压力系数（Blender 中默认值为0，设为正值时抵抗压缩；设为负值时模拟真空收缩效果），$\hat{n}$ 为顶点法线方向。该约束每帧需遍历所有表面三角形计算体积积分，是软体求解中计算开销最高的步骤。

### 数值积分方法与时间步长选择

软体系统的运动方程是一组 $3N$ 维耦合常微分方程（$N$ 为质点数），主流求解方法有两类：

**显式欧拉积分（Explicit Euler）**：
$$\mathbf{v}_{t+\Delta t} = \mathbf{v}_t + \frac{\mathbf{F}_t}{m} \Delta t, \quad \mathbf{x}_{t+\Delta t} = \mathbf{x}_t + \mathbf{v}_{t+\Delta t} \Delta t$$

计算简单，但数值稳定性受 $\Delta t < \sqrt{2m/k}$ 约束。对于刚度 $k = 1000$ N/m、质点质量 $m = 0.01$ kg 的橡胶球，稳定时间步长上限约为 $4.5 \times 10^{-3}$ 秒，即每秒至少需要222步计算，远超游戏的60帧/秒预算，因此显式积分仅适用于低刚度软体或离线渲染。

**隐式欧拉积分（Implicit Euler）**：由 Baraff & Witkin（1998）引入图形学，每步需求解线性方程组 $(M - \Delta t^2 K)\Delta v = \Delta t \cdot F$，其中 $K$ 为系统刚度矩阵。隐式方法允许 $\Delta t$ 取至 1/30 秒，代价是每帧需要一次稀疏矩阵求解（通常采用共轭梯度法），适合 Houdini FEM 等高精度离线管线。

阻尼力叠加在弹力之上：

$$F_{damp} = -d \cdot \mathbf{v}$$

果冻的阻尼系数 $d$ 约为 0.05～0.2（低阻尼，长时间振荡），橡胶球约为 0.3～0.6，超过临界阻尼值 $d_c = 2\sqrt{km}$ 时物体不再振荡，形变后缓慢归位，呈现类黏土效果。

---

## 关键公式与代码示例

以下为 Python 伪代码，展示单根弹簧在每帧更新中的受力计算逻辑：

```python
import numpy as np

def spring_force(pos_a, pos_b, vel_a, vel_b, k, L0, d):
    """
    计算弹簧对质点 A 施加的合力（弹力 + 阻尼力）
    pos_a, pos_b: 两端质点位置 (3D向量)
    vel_a, vel_b: 两端质点速度 (3D向量)
    k   : 刚度系数 (N/m)
    L0  : 自然长度 (m)
    d   : 阻尼系数
    """
    delta = pos_b - pos_a                     # 方向向量
    L = np.linalg.norm(delta)                 # 当前长度
    if L < 1e-8:
        return np.zeros(3)
    
    direction = delta / L                     # 单位方向向量
    # 胡克弹力：F = -k * (L - L0) * 方向
    F_spring = k * (L - L0) * direction

    # 沿弹簧方向的相对速度分量（用于阻尼）
    rel_vel = np.dot(vel_b - vel_a, direction)
    F_damp = d * rel_vel * direction

    return F_spring + F_damp                  # 对 A 的合力（方向指向 B）

# 示例：果冻材质参数
k_structural = 80.0    # 结构弹簧刚度 (N/m)
k_shear      = 50.0    # 剪切弹簧刚度
k_bend       = 10.0    # 弯曲弹簧刚度
damping      = 0.08    # 果冻低阻尼系数
```

上述代码中，将 `k_structural` 调至 500 以上、`damping` 调至 0.4 以上，输出行为即接近橡皮擦；将 `k_structural` 降至 20 以下、`damping` 降至 0.02，则呈现水母般的极软振荡效果。

---

## 实际应用

**电影特效**：皮克斯动画《怪兽公司》（2001年）中蓝色独眼怪兰道的眼球滚动，以及《冰川时代》系列中松鼠追逐的橡果弹跳，均使用基于质点-弹簧的软体系统制作。DreamWorks 的 Premo 动画平台（2013年随《驯龙高手2》正式投入使用）整合了实时软体反馈，允许动画师用手柄直接"捏"角色脸部并预览弹性形变。

**游戏引擎**：《蜘蛛侠：迈尔斯·莫拉莱斯》（2020年，Insomniac Games）中的史莱姆怪物采用 PBD 软体模拟，在 PS5 上以 60 帧/秒运行，每帧约有 2000 个软体约束被实时求解。《糖豆人》（Fall Guys，2020年，Mediatonic）的角色"豆人"身体在碰撞时的压扁效果，同样依赖基于 Unity 的 PBD 软体系统，开发团队公开表示每只豆人含约 120 个软体质点。

**医学可视化**：手术模拟软件（如 3D Systems 的 Touch Surgery Simulator）使用有限元软体模型模拟器官组织在手术器械压力下的形变，要求实时帧率（>30帧/秒）且形变误差小于 1 mm，通常采用线性有限元方法（Linear FEM）结合 GPU 并行加速实现。

**程序化角色动画**：在骨骼蒙皮动画之上叠加软体"二次运动"（Secondary Motion）是提升角色真实感的常用技术。Houdini 的 Vellum 求解器允许将角色面部皮肤网格设为软体层，使眼皮、脸颊、耳垂在快速运动时产生延迟与微振荡，这一效果在《蜘蛛侠：英雄远征》（2019年）的面部捕捉处理中有明确的技术披露。

---

## 常见误区

**误区1：弹簧刚度越高，软体越"真实"**
提高 $k$ 值并不直接等于更真实的橡胶效果，反而会逼近刚体行为并引发数值不稳定。真实橡胶的杨氏模量（Young's Modulus）约为 0.01～0.1 GPa，而硅胶果冻约为 0.001～0.01 GPa。在质点-弹簧系统中，$k$ 值需与网格分辨率（弹簧自然长度 $L_0$）匹配换算，不能直接使用物理单位中的材料参数。

**误区2：忽略碰撞检测中的内部穿透**
软体物体被尖锐物刺穿时，若只做表面碰撞检测，内部质点仍会穿越碰撞体，导致视觉上正确但物理上错误（软体"套在"碰撞体外而内部穿模）。正确做法是同时对软体的内部体素或四面体单元做碰撞检测，Houdini Vellum 默认启用此选项，但会使碰撞计算时间增加约3～5倍。

**误区3：将布料参数直接复用于软体**
布料的弯曲弹簧针对薄层结构设计，其 $k_{bend}$ 极低（薄布不抵抗弯曲）。若将布料参数复用于体积软体，会导致物体中心区域无法维持体积，像"空气球"一样瘪塌。软体必须额外配置体积弯曲弹簧，并启用体积保存约束（Pressure 参数），两者缺一不可。

**误区4：PBD 软体的材质参数与物理单位无