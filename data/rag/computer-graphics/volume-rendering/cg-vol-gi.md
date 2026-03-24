---
id: "cg-vol-gi"
concept: "体积全局光照"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 体积全局光照

## 概述

体积全局光照（Volumetric Global Illumination）是体积渲染领域中处理**多重散射**（Multiple Scattering）效果的一类近似计算方法。与表面全局光照只需考虑2D流形上的光能传输不同，体积全局光照必须处理光子在三维参与介质（如雾、云、烟、皮肤次表面）内部连续发生散射、吸收和发射的全程积分问题，计算复杂度本质上高出一个维度。

从历史渊源看，体积全局光照的理论基础源于20世纪50年代辐射传输理论（Radiative Transfer Theory），Chandrasekhar于1950年出版的《辐射传输》奠定了描述介质内光能传输的数学框架。进入图形学领域后，Jensen等人于2001年提出的偶极子扩散近似（Dipole Diffusion Approximation）首次将扩散方程应用于皮肤渲染，标志着实用化体积全局光照方法的成熟。

体积全局光照的重要性在于：仅考虑单次散射（Single Scattering）的介质渲染会产生明显偏暗、缺乏柔和内发光感的结果。真实世界中浓雾、厚云和蜡烛火焰的外观均由多重散射主导——光子平均在介质中散射数十乃至数百次后才逃逸，这种累积效应只有通过全局光照方法才能正确近似。

---

## 核心原理

### 辐射传输方程（RTE）与多重散射项

体积全局光照的出发点是**辐射传输方程**（Radiative Transfer Equation, RTE）：

$$\frac{dL(\mathbf{x}, \omega)}{dt} = -(\sigma_a + \sigma_s)L(\mathbf{x}, \omega) + \sigma_s \int_{4\pi} f_p(\omega', \omega) L(\mathbf{x}, \omega') d\omega' + L_e(\mathbf{x}, \omega)$$

其中：
- $\sigma_a$ 为吸收系数，$\sigma_s$ 为散射系数，二者之和 $\sigma_t = \sigma_a + \sigma_s$ 为消光系数；
- $f_p(\omega', \omega)$ 为相位函数（Phase Function），描述散射方向分布；
- 右侧积分项正是**多重散射的来源**——入射方向 $\omega'$ 的辐射经过散射贡献到方向 $\omega$。

单次散射仅追踪光源到采样点的直接透射，而多重散射要求对上述积分进行无限展开（Neumann级数），实时系统中必须采用近似方法截断此展开。

### 扩散近似（Diffusion Approximation）

当介质的**反照率** $\alpha = \sigma_s / \sigma_t$ 接近1（强散射、弱吸收）时，辐射场趋于**各向同性**，可用扩散方程近似RTE：

$$\nabla^2 \Phi(\mathbf{x}) - \frac{\sigma_a}{D} \Phi(\mathbf{x}) = -Q(\mathbf{x})$$

其中扩散系数 $D = \frac{1}{3(\sigma_a + \sigma_s')}$，$\sigma_s' = \sigma_s(1-g)$ 为**约化散射系数**（$g$ 为Henyey-Greenstein相位函数的各向异性参数，取值范围 $[-1, 1]$），$\Phi$ 为辐照度通量，$Q$ 为光源项。

偶极子扩散近似通过在真实光源上方添加一个虚拟负光源（距介质表面 $2zb$ 处，$zb = 2D \cdot A$，$A$ 由菲涅耳反射率决定）来满足边界条件，使得该方法可直接解析求解，广泛用于皮肤和蜡等半透明材质渲染。

### 体素化辐照度缓存与光子映射

对于不满足扩散近似条件（如 $\alpha < 0.5$ 的烟雾介质）的场景，图形学中常用两类方法：

**体积光子映射**（Volumetric Photon Mapping）：从光源发射光子，在每次散射事件处记录光子位置和能量，最终在渲染时对光子图（Photon Map）进行**核密度估计**（Kernel Density Estimation）。每次散射后光子携带能量乘以反照率 $\alpha$，俄罗斯轮盘赌（Russian Roulette）以 $1-\alpha$ 的概率终止追踪。

**体积辐照度探针**（Volumetric Irradiance Probes）：在三维空间规则或自适应地放置球谐函数（Spherical Harmonics, SH）探针，每个探针存储2阶（9个系数）或3阶（25个系数）SH系数编码的辐照度，渲染时通过三线性插值获取任意位置的多重散射辐照度近似。这是Frostbite、UE5等引擎在实时体积云渲染中的主流方案。

---

## 实际应用

**云与大气散射**：云介质的散射系数极高（$\sigma_s \approx 10\text{--}100 \text{ m}^{-1}$），反照率接近0.999，多重散射主导云的白色外观和内部明亮感。Horizon Zero Dawn（2017）的云渲染系统在体素网格中预计算多重散射贡献，通过将单次散射结果乘以一个由光学厚度参数化的"多重散射近似系数"（约1.2至2.0）来快速近似多重散射，避免完整求解RTE。

**皮肤次表面散射**：偶极子扩散近似在离线渲染器（如RenderMan、Arnold）中被标准化实现。表皮层（$\sigma_s' \approx 2.0 \text{ mm}^{-1}$，$\sigma_a \approx 0.02 \text{ mm}^{-1}$）和真皮层（$\sigma_s' \approx 1.5 \text{ mm}^{-1}$）分别建模，叠加计算形成真实皮肤的宽散射轮廓。

**体积雾中的区域光**：UE5的Lumen系统为体积雾引入了基于**稀疏体素八叉树**（Sparse Voxel Octree）的间接光照注入，将表面反弹的漫反射辐照度写入3D纹理（分辨率通常为 $160 \times 90 \times 64$），以此近似雾中多重散射的二次照明效果。

---

## 常见误区

**误区1：单次散射+透射率等价于全局光照**
许多初学者认为，只要正确计算了透射率（Beer-Lambert定律）和单次散射积分，就完整模拟了介质光照。实际上，这完全忽略了多重散射。对于光学厚度 $\tau > 1$ 的介质，多重散射贡献的能量往往超过单次散射，仅使用单次散射会导致介质内部呈现不真实的深暗色调和边缘过亮现象。

**误区2：扩散近似适用于所有介质**
扩散近似在低反照率介质（$\alpha < 0.5$）或各向异性极强（$g > 0.9$）的介质中会严重失真。例如模拟烟雾（$\alpha \approx 0.3$）时套用扩散近似，所得散射场会因扩散系数过小、方程病态而产生能量不守恒的结果；此时应改用蒙特卡洛路径追踪或VPM方法。

**误区3：体积全局光照必须逐帧完整重算**
由于参与介质（尤其是大气雾和云）的空间变化通常较平滑，且多重散射本身具有低频特性（高阶SH已足够近似），实时系统可以将体积辐照度探针以较低分辨率、时间复用的方式更新（如每帧只更新1/8的探针），借助时间积累稳定结果，无需每帧完整求解。这种时间稳定策略被Frostbite（2015 SIGGRAPH分享）明确记录为有效减少计算开销的关键技术。

---

## 知识关联

**前置概念**：本文档建立在**参与介质**基础模型之上——必须理解消光系数 $\sigma_t$、相位函数 $f_p$、光学厚度 $\tau$ 以及单次散射积分形式，才能理解多重散射"额外贡献了什么"以及扩散近似"近似了什么积分"。

**延伸方向**：体积全局光照的算法选择直接影响体积渲染管线的其他模块——光子映射需要与体积阴影图（Volumetric Shadow Map）协同，SH探针方法需要与体积光照注入阶段（Voxel Light Injection）耦合，而实时扩散近似需要配合屏幕空间滤波（SSSS, Screen-Space Subsurface Scattering）来修正近场精度不足的问题。这些耦合关系在设计体积渲染系统时决定了算法组合的边界条件。
