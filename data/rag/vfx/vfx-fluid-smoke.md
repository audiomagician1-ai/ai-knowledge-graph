---
id: "vfx-fluid-smoke"
concept: "烟雾模拟"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 烟雾模拟

## 概述

烟雾模拟是一种基于体积（Volumetric）表示的流体仿真技术，通过在三维网格中追踪**密度场**（density field）、**速度场**（velocity field）和**温度场**（temperature field）的演化，再现烟雾的扩散、上升与消散行为。与火焰模拟不同，烟雾不涉及燃烧反应方程，而是将粒子/气体抽象为连续标量场，依赖Navier-Stokes方程的不可压缩形式驱动运动。

烟雾模拟的现代数值框架由Jos Stam于1999年在论文《Stable Fluids》中奠定基础。他提出的**半拉格朗日平流**（Semi-Lagrangian Advection）方案使仿真在大时间步长下仍保持无条件稳定，解决了此前显式方法在烟雾类低雷诺数流体中频繁爆炸的问题，该方法沿用至今，是Houdini、Maya Fluids等主流工具的底层核心。

在电影视觉特效中，烟雾模拟的体素分辨率往往高达512³乃至1024³，单帧体积数据可超过数GB，渲染需要专门的体积光线行进（Volume Ray Marching）管线。正确理解密度场衰减速率、浮力系数与耗散参数之间的耦合关系，是制作自然、可信烟雾效果的技术前提。

---

## 核心原理

### 密度场与标量输运

烟雾的外观由**密度场** ρ(x, t) 决定——它是一个三维标量场，记录每个体素中"烟雾物质"的浓度。密度的演化遵从对流-扩散方程：

$$\frac{\partial \rho}{\partial t} + (\mathbf{u} \cdot \nabla)\rho = \kappa \nabla^2 \rho - d \cdot \rho$$

其中 **u** 为速度场，κ 为扩散系数，**d** 为耗散率（dissipation rate）。耗散项 d·ρ 是一个一阶衰减项，使密度随时间指数级减小，模拟烟雾"消散于空气中"的效果。在Houdini Pyro中，这一参数对应`Dissipation`滑块，典型取值范围为0.01～0.5；过高会让烟雾在数帧内消失，过低则使场景中充满不散的乌云。

### 浮力驱动与温度耦合

烟雾上升的行为来自**热浮力**（Thermal Buoyancy）。在烟雾模拟中，浮力力项通常以以下形式加入动量方程的体力项：

$$\mathbf{f}_{buoy} = \alpha \cdot \rho \cdot \hat{y} - \beta \cdot (T - T_{amb}) \cdot \hat{y}$$

其中 α 为密度浮力系数（正值使浓密烟雾下沉，模拟重烟），β 为温度浮力系数（温度高于环境温度 T_amb 时产生上升力），ŷ 为垂直方向单位向量。

冷烟（如干冰烟雾）α 项主导，β 可设为负值，使烟雾贴地蔓延；热烟（如火焰残余烟柱）β 项主导，产生快速上升的蘑菇云状形态。正确配置这两个系数，是区分不同物理类型烟雾的关键参数操作。

### 压力投影与不可压缩性

烟雾被视为**不可压缩**流体，要求速度场满足散度为零：∇·**u** = 0。在每个时间步的末尾，必须通过求解泊松方程（Poisson Equation）消除速度场中的散度分量，这一步称为**压力投影**（Pressure Projection）。该步骤通常占据整个烟雾仿真计算量的60%～80%，因为它需要在整个仿真域上求解大型稀疏线性方程组，常用PCG（预条件共轭梯度）迭代求解器处理。

### 耗散与湍流细节

单纯的Stam方法由于数值扩散会产生过于光滑的烟雾形态，缺乏自然烟雾中的卷曲细节。现代管线引入**涡旋约束**（Vorticity Confinement，由Fedkiw等人于2001年提出）来补偿被耗散掉的高频旋转结构。涡旋约束强度参数 ε 通常设置在0.1～0.5之间，在Houdini中对应`Confinement`参数，过高会使烟雾形态产生不自然的"蜷曲爆炸"感。

---

## 实际应用

**电影级烟雾柱制作**：在《星球大战：侠盗一号》的特效流程中，大规模爆炸残余烟雾使用Houdini Pyro以256³～512³体素分辨率仿真，随后通过OpenVDB格式存储并传递至Katana/RenderMan进行体积渲染，最终合成时利用密度场直接驱动Z-depth雾化效果。

**干冰贴地烟雾**：将温度浮力系数 β 设为负值（如-2.0），同时将密度浮力系数 α 设为正值（如0.5），加上极低的耗散率（d ≈ 0.005），可以模拟婚礼、演出场景中贴地蔓延的干冰效果。地面碰撞需要额外设置SDF（Signed Distance Field）碰撞体，使烟雾在碰撞边界处正确偏转。

**工业烟囱排烟**：当模拟稳定连续排放的工业烟雾时，通常在发射源设置`Smoke Object`的连续密度注入，同时使用`Wind Field`节点提供横向扰动，配合较高的涡旋约束（ε ≈ 0.3）复现真实烟囱排放时的羽流弯曲与Kelvin-Helmholtz不稳定性卷曲。

---

## 常见误区

**误区一：提高分辨率就能自动获得更多细节**
提高体素分辨率确实增加了可存储的细节空间，但若不同步调整`Substeps`（子步数）和`CFL数`条件，数值平流的误差同样会随之放大，实际可见细节未必显著提升。Houdini Pyro建议在分辨率加倍时将最大时间步长缩短至原来的0.5～0.7倍，以保持平流精度。

**误区二：耗散率控制烟雾"厚度"**
耗散率（dissipation）控制的是密度随时间衰减的速度，而非烟雾的视觉不透明度。烟雾的视觉厚度由渲染时的`Density Scale`（密度缩放比例）参数控制，它在着色/渲染阶段将密度场数值线性映射为消光系数（extinction coefficient）。许多初学者混淆这两个参数，导致调整了仿真参数却看不到预期的渲染变化。

**误区三：烟雾和火焰可以共用同一个仿真对象**
在Houdini中，火焰和烟雾虽然可以在同一个Pyro Solver中共同仿真（通过temperature场驱动combustion，再由燃烧产生密度），但二者遵循不同的物理方程组。将温度场的衰减速率（`Temperature Diffusion`）设置得过快会导致浮力减弱，烟雾柱失去上升动力，这是因为浮力直接由温度超额量（T - T_amb）驱动，并非由密度场独立决定。

---

## 知识关联

烟雾模拟以**火焰模拟**为前导知识，火焰仿真产生的高温气体和燃烧残余物（soot）可直接作为烟雾仿真的密度场输入源，两者在Pyro Solver的`Combustion`模型中通过temperature-to-density映射衔接，燃烧完成后的低温密度场延续受浮力+耗散+平流控制的烟雾物理。

从烟雾模拟向**实时流体策略**推进时，需要理解如何将512³体素的离线仿真结果以烘焙贴图序列（Flipbook）、低精度体积纹理（3D Texture Atlas）或基于神经网络的压缩表示（如NVIDIA的NeuVV格式）转化为游戏引擎可实时渲染的资产，这一转化过程中密度场的LOD（细节层次）降采样策略是关键的技术节点。
