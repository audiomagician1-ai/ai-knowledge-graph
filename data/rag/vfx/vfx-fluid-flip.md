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
quality_tier: "B"
quality_score: 46.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# FLIP/APIC方法

## 概述

FLIP（Fluid Implicit Particle）方法由Robert Bridson等人在2005年将其引入图形学领域，是一种混合粒子-网格（Particle-in-Cell，PIC）仿真框架的改进版本。其核心思想是将流体速度场分别存储在粒子和背景欧拉网格两种数据结构上，通过在每个时间步内相互传递信息来驱动模拟。与纯粒子方法（如SPH）不同，FLIP借助网格来高效求解压力泊松方程，同时依赖粒子保留拉格朗日运动细节，兼顾了两者的优势。

FLIP本身从等离子体物理中的PIC方法演变而来。PIC方法将粒子速度完整替换为网格速度（混合系数α=1），虽然数值稳定，但存在明显的数值耗散，导致流体运动衰减过快，缺乏细节。FLIP将混合系数设为α接近0，粒子速度通过叠加网格速度变化量（Δu）而非直接赋值来更新，从而几乎消除了数值耗散，使水体能保持长时间的动态细节，如飞溅和旋涡。

APIC（Affine Particle-In-Cell）方法由Jiang等人于2015年在SIGGRAPH上发表，针对FLIP遗留的角动量不守恒和噪声问题提出了改进。APIC在粒子上额外存储一个局部仿射速度矩阵**C**（3×3矩阵），在粒子与网格的信息传递（P2G和G2P）过程中显式地保留了旋转和剪切信息，从而在消除噪声的同时不引入数值耗散。

---

## 核心原理

### PIC/FLIP的基本流程

每个时间步的计算流程分为五个阶段：

1. **P2G（粒子到网格）**：将粒子携带的速度通过权重函数（通常采用二次B样条或三次样条核函数）散布到MAC网格的速度分量节点上。
2. **网格求解**：在欧拉网格上施加重力、求解不可压缩性（压力泊松方程 ∇²p = ρ/Δt · ∇·u），更新网格速度u*。
3. **FLIP速度更新**：粒子速度按公式更新：
   - **PIC**：v_p = 从网格插值的u*（完全替换）
   - **FLIP**：v_p = v_p + (u* − u_old)（叠加增量）
   - **混合**：v_p = α·(FLIP更新) + (1−α)·(PIC更新)，实际生产中α通常取0.95~0.99
4. **粒子平流**：用更新后的粒子速度通过RK2或RK3积分推进粒子位置。
5. **粒子数量管理**：监测每个网格单元的粒子密度，当单元内粒子数少于阈值（典型值为4~8个/格）时补充粒子，过多时删除粒子。

### APIC的仿射速度场保留

APIC在G2P阶段不仅插值速度，还计算粒子局部仿射矩阵**C**：

$$\mathbf{C}_p = \sum_i w_{ip} \, \mathbf{u}_i \, (\mathbf{x}_i - \mathbf{x}_p)^T \cdot \mathbf{D}_p^{-1}$$

其中 **D**_p 是与核函数形状相关的惯性张量。在P2G阶段，粒子向网格贡献速度时加入仿射修正项：

$$m_i \mathbf{u}_i = \sum_p w_{ip} m_p \left(\mathbf{v}_p + \mathbf{C}_p (\mathbf{x}_i - \mathbf{x}_p)\right)$$

这使得旋涡结构在P2G→G2P往返传递中不再丢失，角动量误差从FLIP的O(h)降低到理论上的精确守恒（在无压力求解扰动时）。

### 压力泊松方程求解

FLIP/APIC的压力方程采用有限差分在交错MAC网格（Marker-and-Cell）上离散化：

$$\nabla^2 p = \frac{\rho}{\Delta t} \nabla \cdot \mathbf{u}$$

固体边界以Ghost Fluid Method或直接设置法向速度为零来处理。由于网格节点数远少于SPH的粒子邻域积分，稀疏线性系统通常用预条件共轭梯度（PCG）在O(N)到O(N log N)时间内求解，这是FLIP相较于纯SPH在大规模模拟中更高效的根本原因。

---

## 实际应用

**影视级海洋与瀑布模拟**：Houdini的FLIP Solver（基于Bridson 2005的实现）已成为影视特效中水体模拟的工业标准。《加勒比海盗》系列和《阿凡达》等影片中大规模海浪均采用FLIP框架，典型生产分辨率为256³到512³的网格配合每格8个粒子。

**游戏实时流体**：APIC方法由于角动量守恒特性，在需要展示水轮、旋涡等旋转流体的场景中特别适用。部分次世代游戏的离线预计算流体缓存采用APIC生成，再播放为流体缓存动画。

**MPM弹塑性耦合**：APIC的仿射矩阵**C**被Material Point Method（MPM）直接复用，用于模拟雪、泥浆等弹塑性材料。迪士尼《雪宝奇缘》的雪地模拟即采用了基于APIC思想的MPM方法，由Stomakhin等人于2013年发表。

---

## 常见误区

**误区一：FLIP混合系数α越高越好**  
许多初学者认为α=1（纯FLIP）细节最丰富应该最好，但纯FLIP会积累粒子速度的高频噪声，导致粒子在静止时仍随机抖动（"FLIP noise"）。实际生产通常取α=0.95，用5%的PIC混合来稳定粒子运动，完全消除静止水面的颗粒感。

**误区二：FLIP/APIC中粒子本身携带压力信息**  
FLIP和APIC的粒子只携带速度（APIC还携带仿射矩阵**C**），压力完全在欧拉网格上求解。粒子在这两种方法中仅作为速度场的拉格朗日采样点，不像SPH那样直接通过粒子间相互作用计算压力，混淆这一点会导致对两种方法计算量对比产生错误判断。

**误区三：APIC比FLIP慢很多**  
存储仿射矩阵**C**（每个粒子额外9个浮点数）和在P2G中计算修正项确实增加了内存带宽，但APIC不再需要FLIP中保存上一帧网格速度u_old进行差分，计算开销差异在10%~15%以内，在消除噪声后往往还能减少后期粒子数量，综合性价比优于FLIP。

---

## 知识关联

**与SPH方法的区别**：SPH完全基于粒子计算压力和粘性力，计算复杂度随邻域粒子数增长，适合自由表面小规模模拟；FLIP/APIC将压力求解转移到网格，对封闭流体体积的大规模模拟具有明显优势，但需要额外维护粒子-网格传递步骤，代码实现复杂度更高。

**流体表面重建的前置需求**：FLIP/APIC模拟完成后，粒子的空间分布即代表流体占据的区域，但粒子本身是离散点，需要通过**流体表面重建**（Surface Reconstruction）方法将其转化为可渲染的连续网格。常用的Zhu-Bridson方法（2005年与FLIP同年发表）专门为FLIP粒子设计，通过对粒子半径场进行加权平均并提取等值面（等值为0.5倍平均粒子半径）来生成平滑的水面网格，因此学习FLIP/APIC后自然衔接表面重建的原理与参数调节。