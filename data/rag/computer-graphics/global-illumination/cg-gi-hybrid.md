# 混合GI方案

## 概述

混合GI方案（Hybrid Global Illumination，简称Hybrid GI）是将离线烘焙光照贴图（Baked Lightmap）、实时光照探针（Light Probe）以及屏幕空间全局光照（SSGI，Screen Space Global Illumination）三种技术叠加组合，以覆盖不同空间频率和动态程度光照需求的多层次渲染策略。该方案的核心诉求来自于单一GI技术无法同时满足静态低频环境光、动态物体间接光响应以及近距离高频接触光等三类截然不同的光照现象。

混合GI的系统化实践在2017年前后随Unreal Engine 4.18的"距离场AO + 光照贴图 + 反射捕获"管线组合而广泛普及；Unity的Enlighten Realtime GI（最初集成于Unity 5.0，2015年发布）与烘焙GI共存的双模式架构也在同期形成行业标准。这种分层思想的理论依据是球谐函数（Spherical Harmonics，SH）的频率分离特性：低频项（$L_0$、$L_1$，即直流与偶极项，共4个系数/通道）适合探针存储，中频（$L_2$ 项，9个系数/通道的二阶SH）适合光照贴图，而高频细节则依赖屏幕空间重建。

混合GI方案在实际工程中的价值在于它是目前大型开放世界游戏能够兼顾画质与性能的核心路径。《赛博朋克2077》（CD Projekt Red，2020年）、《荒野大镖客：救赎2》（Rockstar Games，2018年）以及《地平线：零之曙光》（Guerrilla Games，2017年）等AAA作品的GI实现均属于此类混合方案，而非依赖任何单一技术。这三款游戏的GI预算分别约为5ms、4ms和3ms，远低于纯实时路径追踪所需的15–30ms，混合方案正是其在当时硬件条件下实现高质量全局光照的根本原因。

---

## 核心原理

### 分层覆盖模型

混合方案将空间划分为三个作用域，每层负责不同频率的光照贡献，形成互补而非竞争的关系：

- **烘焙层（Baked Layer）**：处理静态几何体之间的低频间接光，典型分辨率为每Texel覆盖10–50 cm的世界空间，存储于Lightmap Atlas中。该层对动态物体完全透明，仅贡献静态表面的漫反射辐照度（Irradiance）。烘焙工具（如UE4的Lightmass，于2008年随UE3引入）通常采用路径追踪或光子映射计算，离线时间从数分钟到数小时不等。
- **探针层（Probe Layer）**：使用三阶球谐（SH9，即每颜色通道9个系数，RGB共27个浮点值）或Irradiance Cubemap捕获动态物体所在位置的环境辐照度。更新频率通常为每帧局部刷新全部探针的1/4体积，或基于物体位移超过阈值（通常为0.5米）时触发局部重烘。
- **屏幕空间层（Screen Space Layer，SSGI）**：以当前帧的GBuffer（深度缓冲、法线缓冲、颜色/反照率缓冲）为输入，利用光线步进（Ray Marching）或随机半球采样（Stochastic Hemisphere Sampling）重建近场间接漫反射。典型参数为：采样半径0.5–3米，每像素8–16条射线，以1/2分辨率渲染后经双边上采样（Bilateral Upsample）恢复全分辨率。

三层按优先级叠加：SSGI结果叠加在探针层之上，探针层填补SSGI的屏幕外信息缺失，烘焙层作为全局基底兜底。混合权重公式写为：

$$L_{\text{final}} = L_{\text{baked}} \cdot w_b + L_{\text{probe}} \cdot (1 - w_{ss}) + L_{\text{ssgi}} \cdot w_{ss}$$

其中 $w_{ss}$ 由SSGI射线命中置信度（Hit Confidence，取值范围0–1）驱动——命中率低于阈值（通常为0.3）时，$w_{ss}$ 自动衰减至0，GI贡献完全退化至探针层，从而保证画面稳定性。能量守恒要求各层有效贡献在像素级归一化，避免叠加后总辐照度超出物理上限。其中 $w_b + (1 - w_{ss}) + w_{ss} \leq 1$ 须在运行时动态约束，否则会出现过曝区域（辐照度超出物理量程，HDR颜色值溢出至16.0以上）。

### 球谐函数的频率分析

球谐函数是定义在单位球面上的一组正交基函数，第 $l$ 阶共有 $2l+1$ 个基函数，前三阶（$l=0,1,2$）合计9个基函数，称为SH9。其辐照度重建公式为：

$$E(\mathbf{n}) = \sum_{l=0}^{2} \sum_{m=-l}^{l} L_{lm} \cdot Y_{lm}(\mathbf{n})$$

其中 $\mathbf{n}$ 为表面法线方向，$L_{lm}$ 为第 $l$ 阶第 $m$ 次谐波系数，$Y_{lm}$ 为对应的实数球谐基函数。SH9可准确重建低频漫反射辐照度，对于Lambertian BRDF而言，$l \geq 3$ 阶的高频项贡献可忽略不计（能量占比不足1%），这正是探针选用SH9而非更高阶的理论依据（Ramamoorthi & Hanrahan，2001年在SIGGRAPH论文"An Efficient Representation for Irradiance Environment Maps"中严格证明）。

每个探针的存储开销为：SH9 × RGB 3通道 × float16 = 9 × 3 × 2 = 54字节。相比之下，一张64×64的HDR Cubemap（6面×64×64×RGB×float16）需要约150KB，SH9在存储效率上具有约2800倍优势，代价是丢失 $l \geq 3$ 阶的高频光照细节。这一权衡决定了探针层只能作为低频辐照度基底，而无法取代Lightmap或SSGI的中高频贡献。

例如，在一个有红色砖墙和白色天花板的室内场景中，探针捕获的SH9系数的 $L_{00}$（直流项）编码了场景平均亮度约0.4 nit，$L_{11}$（偶极项之一）编码了来自右侧红墙方向的彩色溢色（Color Bleeding），而高频的砖缝阴影细节则完全依赖Lightmap中预计算的遮蔽图来呈现。

### 探针与烘焙的接缝处理

烘焙Lightmap与探针采样之间的颜色不一致（Seam/Leaking）是混合方案最典型的技术挑战。标准做法是在烘焙阶段将探针的SH系数作为约束条件写入，使Lightmap的平均辐照度与探针读数在数值上对齐，误差容忍度通常要求在0.02 nit以内。Unity于2022年（Unity 2022 LTS）引入的Adaptive Probe Volumes（APV）通过体素化探针网格替代传统手动放置，探针密度可根据几何复杂度自适应调整（稀疏区域每3米一个，复杂区域每0.5米一个），使接缝问题从美术手工调整流程转为引擎自动处理，节省了大型场景下约60%的美术调整工时（据Unity 2022技术报告）。

DDGI（Dynamic Diffuse Global Illumination，Majercik et al.，2019）将探针从固定网格拓展为可运行时动态更新的辐照度场（Irradiance Field），每个探针以分辨率8×8的小型Irradiance Atlas存储方向辐照度，并通过Ray Tracing每帧更新256条射线。相比传统静态探针，DDGI能够响应移动光源、开关门窗等动态场景变化，典型帧时间开销约为2–4ms（RTX 2080测试数据），是混合方案探针层在次世代硬件上的主流升级路径。

### 时域稳定性控制

SSGI层对摄像机移动极为敏感，快速移动时会产生"鬼影"（Ghosting）或"萤火虫"噪点（Firefly）。混合方案通常在SSGI之上叠加时域累积滤波（TAA风格的Temporal Reprojection），利用Motion Vector将历史帧混合比例（History Blend Factor）限制在0.85–0.92之间（即当前帧权重为0.08–0.15），并以深度差（$\Delta d > 0.1$ 米）和法线差（$\Delta \theta > 15°$）作为历史拒绝条件，防止遮挡不连续处的历史帧信息污染当前帧。

时域滤波的核心公式为：

$$L_{\text{temporal}}^{(t)} = \alpha \cdot L_{\text{ssgi}}^{(t)} + (1 - \alpha) \cdot \text{Reproject}(L_{\text{temporal}}^{(t-1)})$$

其中 $\alpha \in [0.08, 0.15]$ 为当前帧混合权重，$\text{Reproject}(\cdot)$ 为基于Motion Vector的历史帧重投影函数。时域滤波有效地将8射线/像素的噪声质量提升至等效64射线的视觉效果，是SSGI得以在实时渲染中实用化的关键技术。若历史拒绝触发（$\alpha$ 强制置为1.0），则当前帧仅以8射线质量呈现，噪点短暂可见，通常持续2–4帧后重新收敛。

---

## 关键公式与模型

### 渲染方程的分层离散化

混合GI方案本质上是对完整渲染方程的分层近似。完整渲染方程（Kajiya，1986）为：

$$L_o(\mathbf{x}, \omega_o) = L_e(\mathbf{x}, \omega_o) + \int_{\Omega} f_r(\mathbf{x}, \omega_i, \omega_o) \cdot L_i(\mathbf{x}, \omega_i) \cdot (\omega_i \cdot \mathbf{n}) \, d\omega_i$$

其中 $L_o$ 为出射辐亮度，$L_e$ 为自发光项，$f_r$ 为BRDF，$L_i$ 为入射辐亮度，$\mathbf{n}$ 为表面法线，$\Omega$ 为上半球积分域。混合GI将 $L_i$ 拆分为三个来源：

$$L_i(\mathbf{x}, \omega_i) \approx L_i^{\text{baked}}(\mathbf{x}) + L_i^{\text{probe}}(\mathbf{x}, \omega_i) + L_i^{\text{ssgi}}(\mathbf{x}, \omega_i)$$

对于Lambertian漫反射（$f_r = \rho / \pi$，$\rho$ 为反照率），积分结果简化为辐照度 $E(\mathbf{x})$，三层贡献直接相加后乘以 $\rho / \pi$，即为最终漫反射出射辐亮度。这一分解在数学上的合法性依赖于线性叠加原理，仅在各层能量不重叠（无双重计算）的前提下成立。

### 烘焙Lightmap的辐照度插值

在昼夜循环场景中，多套Lightmap之间的双线性插值模型为：

$$L_{\text{baked}}(t) = (1 - \lambda) \cdot L_{\text{baked}}^{(k)} + \lambda \cdot L_{\text{baked}}^{(k+1)}$$

其中 $t$ 为当前游戏内时间，$k$ 为最近的预烘焙时间段索引，$\lambda = (t - t_k) / (t_{k+1} - t_k) \in [0, 1]$ 为线性插值因子。使用4套Lightmap时内存占用约为单套的4倍；典型1024×1024 Lightmap Atlas（RGB half-float）占用约3MB，4套共约12MB，在主机内存预算中属于可接受范围。

---

## 实际应用案例

**Unreal Engine 5 的 Lumen 降级方案**：Lumen（Epic Games，2021年随UE5发布）在PC和次世代主机端作为全实时GI方案运行，但在移动端或低端硬件上会自动降级