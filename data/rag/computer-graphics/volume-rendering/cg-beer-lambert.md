---
id: "cg-beer-lambert"
concept: "Beer-Lambert定律"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 2
is_milestone: false
tags: ["物理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
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



# Beer-Lambert定律

## 概述

Beer-Lambert定律（全称 Beer-Lambert-Bouguer定律）精确描述了准直光束穿过均匀吸收介质时强度随路径长度呈指数衰减的规律。其核心公式为：

$$I = I_0 \cdot e^{-\mu_t \cdot d}$$

其中 $I_0$ 为入射光强度（W/m²），$I$ 为透射光强度，$\mu_t$ 为消光系数（extinction coefficient，单位 m⁻¹），$d$ 为光线穿越介质的路径长度（m）。指数衰减的物理含义是：每增加相同厚度 $\Delta d$ 的介质，光强总以相同比例 $e^{-\mu_t \Delta d}$ 衰减，而非等量减少——这与放射性衰变、RC电路放电共享同一数学结构。

该定律由三位科学家分阶段建立：法国物理学家 Pierre Bouguer 于1729年在其著作《光的衰减论文》(*Essai d'optique sur la gradation de la lumière*) 中最早记录了光在海水与大气中的衰减现象；德国数学家 Johann Heinrich Lambert 于1760年在《光度学》(*Photometria*) 中将其严格数学化，给出透射率与厚度的对数关系；德国化学家 August Beer 于1852年在 *Annalen der Physik* 上进一步将消光系数与溶液摩尔浓度 $c$ 联系起来：$\mu_t = \varepsilon \cdot c$，其中 $\varepsilon$ 为摩尔消光系数（L·mol⁻¹·cm⁻¹）。在体积渲染领域，该定律是描述光在雾、云、烟、皮肤、水体等参与介质中发生消光的基础物理模型，亦是 Physically Based Rendering（PBR）体积光照管线的数学起点，详见 Pharr、Jakob 与 Humphreys 所著《Physically Based Rendering: From Theory to Implementation》（第4版，2023，MIT Press）中第11章对透射率的推导。

---

## 核心原理

### 光学深度（Optical Depth）

光学深度 $\tau$（读作 tau）是 Beer-Lambert 定律在非均匀介质中的推广形式，定义为消光系数沿光线路径的线积分：

$$\tau(0 \to d) = \int_0^d \mu_t(x)\, dx$$

其中 $\mu_t(x)$ 是光线方向上位置 $x$ 处的消光系数，允许随空间任意变化（如密度不均匀的云团）。透射率 $T$ 由光学深度直接给出：

$$T = e^{-\tau}$$

几个关键数值节点对渲染实践有直接指导意义：

| 光学深度 $\tau$ | 透射率 $T = e^{-\tau}$ | 实际含义 |
|---|---|---|
| 0.1 | 90.5% | 薄雾，几乎透明 |
| 1.0 | 36.8% | 中等遮蔽，1/e 特征厚度 |
| 3.0 | 4.98% | 较厚介质 |
| 5.0 | 0.67% | 浓烟，近乎不透明 |
| 10.0 | 0.0045% | 工程上视为完全不透明 |

当介质空间均匀时 $\mu_t(x) = \text{const}$，积分退化为 $\tau = \mu_t \cdot d$，即原始形式。

### 消光系数的物理分解

在体积渲染的物理模型中，消光系数 $\mu_t$ 由两个独立物理过程的系数叠加而成：

$$\mu_t = \mu_a + \mu_s$$

其中 $\mu_a$ 为**吸收系数**（absorption coefficient）：光子被介质分子吸收，能量转化为热能或荧光，光子永久消失；$\mu_s$ 为**散射系数**（scattering coefficient）：光子与介质粒子发生弹性碰撞，改变传播方向但未被消灭。两者之比定义了介质的**单次散射反照率**（single-scattering albedo）：

$$\omega_0 = \frac{\mu_s}{\mu_t} = \frac{\mu_s}{\mu_a + \mu_s}$$

$\omega_0 \in [0, 1]$：纯吸收介质（如铂金染色玻璃）$\omega_0 \approx 0$；积雨云 $\omega_0 \approx 0.999$；人类皮肤真皮层在 633 nm 波长下 $\omega_0 \approx 0.95$（Jacques, 2013, *Physics in Medicine & Biology*）。

**关键限制**：Beer-Lambert 定律仅处理消光（光子从当前光线方向被移除），不包含来自其他方向散射光重新注入当前光线的贡献（即 in-scattering）。因此它描述的是透射率，而非完整的辐射传输方程（Radiative Transfer Equation, RTE）解。完整 RTE 在 Beer-Lambert 的基础上还需加入发射项 $\mu_e \cdot L_e$ 和散射积分项 $\mu_s \int_{4\pi} p(\omega, \omega') L(\omega') d\omega'$。

### 在 Ray Marching 中的离散化实现

实时与离线渲染中无法对任意密度场解析积分 $\tau$，需将光线离散为 $N$ 个步长为 $\Delta x$ 的采样段，透射率以**累积乘积**计算：

$$T_{\text{total}} = \prod_{i=0}^{N-1} e^{-\mu_{t,i} \cdot \Delta x} = \exp\!\left(-\sum_{i=0}^{N-1} \mu_{t,i} \cdot \Delta x\right)$$

其中 $\mu_{t,i}$ 为第 $i$ 段采样点处的消光系数。对应的 GLSL 实现如下：

```glsl
float rayMarchTransmittance(vec3 rayOrigin, vec3 rayDir, float tMax, int numSteps) {
    float stepSize = tMax / float(numSteps);
    float transmittance = 1.0;
    
    for (int i = 0; i < numSteps; i++) {
        float t = (float(i) + 0.5) * stepSize;  // 步段中点采样
        vec3 pos = rayOrigin + t * rayDir;
        
        float density = sampleDensityField(pos);  // 从3D纹理采样密度
        float mu_t = density * extinctionCoeff;    // μt = σ · ρ(x)
        
        transmittance *= exp(-mu_t * stepSize);    // Beer-Lambert离散累乘
        
        // 早期终止：透射率极低时继续步进贡献可忽略不计
        if (transmittance < 0.01) break;
    }
    return transmittance;
}
```

步长 $\Delta x$ 的选择直接影响精度：步长过大会在高密度区域产生"透明漏光"伪影（因为 $e^{-\mu \Delta x}$ 的一阶近似 $1 - \mu \Delta x$ 在 $\mu \Delta x > 0.3$ 时误差超过 15%）；步长过小则导致性能下降。工业实践中常用**自适应步长**，在密度梯度大的区域自动减小 $\Delta x$。

---

## 关键公式汇总

**均匀介质透射率**（最简形式）：
$$T = e^{-\mu_t \cdot d}$$

**非均匀介质透射率**（通用形式）：
$$T(a \to b) = \exp\!\left(-\int_a^b \mu_t\!\left(\mathbf{x}(s)\right) ds\right)$$

**密度场参数化**（渲染管线标准写法）：
$$\mu_t(\mathbf{x}) = \sigma_t \cdot \rho(\mathbf{x})$$

其中 $\sigma_t$ 为材质的消光率（extinction rate，单位 m²/kg），$\rho(\mathbf{x})$ 为体积密度场（kg/m³），由 VDB 或 3D 纹理存储。

**Beer定律的浓度形式**（分析化学场景）：
$$A = \log_{10}\!\frac{I_0}{I} = \varepsilon \cdot c \cdot l$$

其中 $A$ 为吸光度（absorbance，无量纲），$\varepsilon$ 为摩尔消光系数，$c$ 为浓度（mol/L），$l$ 为光程（cm）。注意此处用常用对数而非自然对数，与渲染领域的自然对数形式相差常数因子 $\ln 10 \approx 2.303$。

---

## 实际应用

**云和雾的渲染**：Houdini VDB体积或 Unreal Engine 5 的 Volumetric Fog 系统均以 $\mu_t(\mathbf{x}) = \sigma_t \cdot \rho(\mathbf{x})$ 参数化消光。薄雾场景 $\mu_t$ 典型值为 0.01～0.5 m⁻¹（能见度数百米量级）；积雨云内部 $\mu_t$ 可达 50～200 m⁻¹（光在云中穿透深度仅数厘米至数十厘米）。

例如：在 Unreal Engine 5 的 Exponential Height Fog 中，雾密度随高度按 $\rho(h) = \rho_0 \cdot e^{-H_f \cdot h}$ 衰减（$H_f$ 为高度衰减系数），将其代入光学深度积分后可得解析解，避免了完整 Ray Marching 的性能开销。

**水下渲染**：纯水对不同波长光的吸收系数差异极大：在 440 nm（蓝光）处 $\mu_a \approx 0.006$ m⁻¹，在 680 nm（红光）处 $\mu_a \approx 0.65$ m⁻¹，在 750 nm（近红外）处 $\mu_a \approx 2.7$ m⁻¹。这解释了水下场景随深度迅速变蓝（红光被优先吸收）的视觉现象。实时海洋渲染（如《孤岛危机3》）通过对 R/G/B 三通道分别应用不同 $\mu_a$ 值精确还原这一效果。

**皮肤次表面散射（SSS）的简化**：在实时渲染中，皮肤的多层散射效果有时近似为深度依赖的透射率衰减，其中 Beer-Lambert 提供了各层厚度与透射率的映射基础，再结合漫反射剖面（diffusion profile）叠加散射贡献（Jimenez 等，*GPU Pro 3*，2012）。

---

## 常见误区

**误区1：将 Beer 定律与完整体积光照等价**
Beer-Lambert 定律只计算"光被移除"的过程（消光），不包含 in-scattering（从四面八方散射进入当前光线的光能）。仅用 Beer-Lambert 渲染云层会得到黑色轮廓加衰减的错误结果，而真实云层内部因多重散射呈现明亮的乳白色。完整计算需求解辐射传输方程（RTE），或使用单次散射近似 + 多次散射预计算。

**误区2：步长不变导致的能量不守恒**
在 Ray Marching 中，若直接用 $T \approx 1 - \mu_t \Delta x$（一阶线性近似）代替 $e^{-\mu_t \Delta x}$，当 $\mu_t \Delta x > 0.1$ 时误差显著：$\mu_t \Delta x = 1.0$ 时线性近似给出 $T = 0$（完全不透明），而正确值为 $e^{-1} \approx 0.368$。在高密度区域（如云的核心）这会造成严重的不透明度过估计。

**误区3：混淆吸光度的对数底**
分析化学中 Beer 定律使用常用对数（$\log_{10}$），而渲染/物理领域使用自然对数（$\ln$）。将 $\mu_t$ 值从化学数据库直接移植到渲染引擎时，需乘以 $\ln 10 \approx 2.303$ 进行换算。

**误区4：认为 Beer-Lambert 定律对高浓度介质始终成立**
Beer 定律成立的前提假设包括：光束为准直单色光、溶质分子间无相互作用、无荧光或磷光。在极高浓度下（溶液中溶质摩尔浓度超过约 0.01 mol/L），分子间电磁相互作用改变了等效消光系数，导致线性关系失效（即 $A$-$c$ 曲线向下弯曲）。在渲染中该限制通常不适用，但对于基于物理测量数据建立材质参数的流