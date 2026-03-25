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
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 烟雾模拟

## 概述

烟雾模拟是计算机图形学中体积渲染领域的核心技术，通过数值方法求解Navier-Stokes方程组来描述流体运动，再结合光线传播模型生成视觉上逼真的烟雾效果。与固体网格渲染不同，烟雾本质上是密度场随时间变化的连续介质，因此必须在每一帧对整个三维空间中的粒子或网格单元重新求解。

烟雾模拟在学术上的奠基工作可追溯至Jos Stam于1999年发表的论文《Stable Fluids》，该论文引入了半拉格朗日对流方法，使烟雾模拟首次在实时或交互速度下达到无条件稳定。在此之前，显式欧拉积分方法会因时间步长过大而产生数值爆炸，将时间步长限制在毫秒级别，严重制约了实际应用。Stam的方法将这一限制解除，使影视和游戏中的大规模烟雾模拟成为可能。

烟雾模拟的重要性在于它同时涉及物理求解与光学渲染两个层面。物理求解决定密度场、速度场和温度场的时间演化；光学渲染则根据参与介质的散射、吸收和发射特性，将体积密度转化为屏幕上的像素颜色。两个层面的精度共同决定最终画面的可信度。

---

## 核心原理

### 欧拉方法与拉格朗日方法的本质区别

**欧拉方法（Eulerian Method）**将空间划分为固定的三维网格（Voxel Grid），每个网格单元存储速度 $\mathbf{u}$、密度 $\rho$、压力 $p$ 和温度 $T$。模拟时在固定坐标系上对每个单元逐步更新这些场量。欧拉方法的优势是可以直接在网格上施加压力投影（Pressure Projection），确保速度场满足不可压缩条件 $\nabla \cdot \mathbf{u} = 0$。典型网格分辨率从游戏中的 $64^3$ 到影视特效中的 $512^3$ 甚至 $1024^3$ 不等。

**拉格朗日方法（Lagrangian Method）**则追踪离散粒子，每个粒子携带位置 $\mathbf{x}_i$、速度 $\mathbf{v}_i$ 和密度权重 $m_i$。最常见的实现是粒子系统（Particle System），每帧根据力场更新粒子状态，再通过内核函数（Kernel Function）将粒子属性插值回体素空间用于渲染。粒子方法在处理细丝状烟雾和边界拉伸时细节更丰富，但难以精确保证不可压缩性。

**混合方法PIC/FLIP（Particle-in-Cell / Fluid-Implicit-Particle）**将两者结合：用粒子传输信息以减少数值耗散，用网格求解压力。FLIP方法中，粒子到网格的速度转移使用加权平均，而网格到粒子的回传则只添加速度的**增量**，数学上写作：
$$\mathbf{v}_i^{n+1} = \mathbf{v}_i^n + (\mathbf{u}_{grid}^{n+1} - \mathbf{u}_{grid}^n)\big|_{\mathbf{x}_i}$$
这使FLIP方法的数值耗散远低于纯粒子方法，是目前商业流体软件（如Houdini）的主流方案。

### Navier-Stokes方程的离散求解步骤

不可压缩烟雾的Navier-Stokes方程为：
$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{f}$$

其中 $\nu$ 是运动粘度，$\mathbf{f}$ 包含浮力（热烟上升）和外力项。实际求解分为四步：

1. **外力施加**：将重力、浮力 $\mathbf{f}_{buoy} = \alpha \rho_{smoke} \hat{z} - \beta (T - T_{amb})\hat{z}$ 加入速度场，其中 $\alpha$ 和 $\beta$ 分别是密度浮力系数和温度浮力系数。
2. **对流（Advection）**：用半拉格朗日法沿速度场反向追踪，计算 $\mathbf{x}_{prev} = \mathbf{x} - \Delta t \cdot \mathbf{u}(\mathbf{x})$，再在 $\mathbf{x}_{prev}$ 处三线性插值获取新值。
3. **扩散（Diffusion）**：求解隐式热方程 $(I - \nu \Delta t \nabla^2)\mathbf{u}^{n+1} = \mathbf{u}^*$，通常用Gauss-Seidel迭代或共轭梯度法。
4. **压力投影（Pressure Projection）**：求解泊松方程 $\nabla^2 p = \frac{\rho}{\Delta t} \nabla \cdot \mathbf{u}^*$，再减去梯度 $\mathbf{u}^{n+1} = \mathbf{u}^* - \frac{\Delta t}{\rho}\nabla p$，保证散度为零。

### 烟雾密度的渲染耦合

模拟得到密度场 $\sigma_s(\mathbf{x})$ 后，需结合参与介质的体积渲染方程：
$$L(\mathbf{x}, \omega) = \int_0^d L_{scatter}(t) \cdot e^{-\int_0^t \sigma_t(s)ds} dt$$

其中消光系数 $\sigma_t = \sigma_s + \sigma_a$（散射系数加吸收系数）。烟雾通常设置高散射低吸收，如 $\sigma_s = 0.8$，$\sigma_a = 0.05$，相比之下火焰则有显著的自发光项。渲染时用光线步进（Ray Marching）沿视线方向采样密度场，步长一般取网格单元大小的 $0.5$ 到 $1.0$ 倍。

---

## 实际应用

**影视特效**中，Houdini的PyroFX模块使用欧拉网格加涡流噪声（Vorticity Confinement）技术增强细节，涡流约束力为 $\mathbf{f}_{vc} = \epsilon \Delta x (\hat{N} \times \boldsymbol{\omega})$，其中 $\epsilon$ 通常取 $0.1$ 到 $2.0$，能有效恢复被数值耗散削弱的旋转细节。《复仇者联盟》系列中的大规模爆炸烟尘即采用此类方案，单帧模拟网格可达 $800^3$。

**游戏引擎**中，UE5的Niagara系统提供GPU粒子烟雾模拟，单个GPU流体网格分辨率通常限制在 $128^3$ 以内以保证帧率。通过预计算流场纹理（Flowmap）或Shader Graph中的噪声扰动，可以在不进行完整物理求解的情况下近似烟雾飘散效果，性能开销仅为完整模拟的 $1/20$ 左右。

**科学可视化**中，烟雾模拟技术被用于流体力学仿真结果的可视化，如CFD软件中气流绕建筑物流动的可视化，此时密度场直接来自仿真数据而非物理求解，渲染管线与艺术类烟雾相同。

---

## 常见误区

**误区一：半拉格朗日对流方法一定无耗散**。实际上半拉格朗日方法因三线性插值引入一阶数值耗散，会使烟雾密度场随时间"模糊化"，细丝结构迅速消失。正确做法是使用BFECC（Back and Forth Error Compensation and Correction）或MacCormack方案提升对流精度，或叠加涡流约束力补偿能量损失。

**误区二：粒子数量越多，拉格朗日模拟越准确**。当粒子密度超过网格分辨率的某一阈值后，继续增加粒子对精度的提升可忽略不计，反而使粒子到网格的插值过程成为性能瓶颈。对于 $64^3$ 的网格，每个单元 $8$ 到 $16$ 个粒子已是合理上限，超过此数量收益递减。

**误区三：烟雾颜色由密度直接决定**。烟雾的最终颜色是密度场、光照方向、散射相函数（如Henyey-Greenstein相函数）以及自阴影（Self-Shadowing）共同作用的结果。同一密度场在不同光照角度下可呈现从白色半透明到深灰色不透明的极大差异，因此调整烟雾外观时不能只修改密度阈值。

---

## 知识关联

烟雾模拟建立在**参与介质**（Participating Media）理论之上。参与介质定义了散射系数 $\sigma_s$、吸收系数 $\sigma_a$ 和相函数 $p(\omega, \omega')$，这三个量直接对应烟雾模拟中渲染步骤所需的输入参数。没有参与介质的光传输模型，密度场只是一组浮点数，无法转化为可见图像。

在前
