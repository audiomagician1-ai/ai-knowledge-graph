---
id: "cg-phase-function"
concept: "相函数"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 3
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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 相函数

## 概述

相函数（Phase Function）是体积渲染中描述光在参与介质内发生散射时，**散射光能量在各个方向上如何分布**的数学函数。给定一束入射光方向 $\omega_i$，相函数 $p(\omega_i, \omega_o)$ 返回光向出射方向 $\omega_o$ 散射的概率密度。与表面BRDF不同，相函数作用于三维体积内部的每个点，并且满足归一化约束：$\int_{4\pi} p(\omega_i, \omega_o)\, d\omega_o = 1$，即所有方向上散射能量之和为单位1（假设无吸收损失）。

相函数的研究最早来源于大气光学与天文学领域。1941年，Ludwig Henyey 和 Jesse Greenstein 在研究星际尘埃对光的散射时提出了后来以他们名字命名的 Henyey-Greenstein 相函数（简称 HG 相函数），这一模型因其数学简洁性和对真实散射行为的良好近似，至今仍是图形学中体积渲染的标准工具。

在云、烟、皮肤次表面散射、参与介质等渲染场景中，相函数直接决定了体积的视觉外观——云朵边缘的"银边"光晕、丁达尔效应（光柱可见性）、烟雾的前向散射特性，均由相函数的形状所控制。选择错误的相函数会导致渲染结果在物理上失真，例如将大气气溶胶误用均匀散射模型会丢失傍晚天空的橙红色渐变细节。

---

## 核心原理

### Henyey-Greenstein 相函数与各向异性参数 g

HG 相函数的解析形式为：

$$p_{HG}(\cos\theta) = \frac{1}{4\pi} \cdot \frac{1 - g^2}{(1 + g^2 - 2g\cos\theta)^{3/2}}$$

其中 $\theta$ 是入射方向与出射方向的夹角，$g \in [-1, 1]$ 是**各向异性参数**（asymmetry parameter），也称为平均余弦值 $g = \langle\cos\theta\rangle$。

- $g = 0$：退化为均匀散射（各向同性），光向所有方向等概率散射；
- $g > 0$（如 $g = 0.8$）：前向散射主导，光倾向于沿原方向继续传播，常见于大气气溶胶、云粒子；
- $g < 0$（如 $g = -0.3$）：后向散射主导，月球表面的逆反射效应可用此建模；
- $g = 0.76$ 是人类皮肤真皮层的经验测量值，在次表面散射模拟中具有重要参考意义。

HG 相函数的最大优点是**可以解析采样**——给定均匀随机数 $\xi \in [0,1]$，可直接求解散射角：

$$\cos\theta = \frac{1}{2g}\left(1 + g^2 - \left(\frac{1-g^2}{1-g+2g\xi}\right)^2\right), \quad g \neq 0$$

这使得蒙特卡洛路径追踪中的散射方向采样极其高效，无需拒绝采样或数值求根。

### Rayleigh 相函数与尺寸依赖性

当散射粒子远小于光的波长（粒子半径 $r \ll \lambda/10$）时，散射由 Rayleigh 理论描述，其相函数为：

$$p_{Rayleigh}(\theta) = \frac{3}{16\pi}(1 + \cos^2\theta)$$

Rayleigh 散射的强度与波长的四次方成反比（$I \propto \lambda^{-4}$），这直接解释了天空为什么是蓝色的——蓝光（450nm）比红光（700nm）的散射强度大约 $(700/450)^4 \approx 5.8$ 倍。在渲染中，Rayleigh 相函数常用于大气层模拟，它具有前后对称的"花生形"分布，无各向异性偏置。

### Mie 散射与双叶瓣模型

当粒子尺寸与光波长接近时（如云滴直径约 10–100μm，远大于可见光波长 400–700nm），需要使用 Mie 散射理论。Mie 散射相函数的精确计算依赖 Lorenz-Mie 理论的级数展开，计算代价极高，实际渲染中常以两个 HG 相函数的线性组合来近似：

$$p_{double}(\theta) = \alpha \cdot p_{HG}(\theta, g_1) + (1-\alpha) \cdot p_{HG}(\theta, g_2)$$

其中 $\alpha \in [0,1]$ 控制两个叶瓣的权重，$g_1 > 0$ 代表强前向散射叶瓣，$g_2 < 0$ 代表弱后向散射叶瓣。云的渲染中典型参数为 $g_1=0.8,\ g_2=-0.5,\ \alpha=0.7$，可以重现云的银边光晕和内部多重散射的柔和外观。

### 归一化与能量守恒

相函数必须满足归一化条件，这是能量守恒的直接要求。在球坐标系中写作：

$$\int_0^{2\pi}\int_0^{\pi} p(\theta)\sin\theta\, d\theta\, d\phi = 1$$

可以验证，将 $p_{HG}$ 代入上式对任意 $g \in (-1,1)$ 均精确成立，这是 HG 模型被广泛接受的重要数学依据之一。

---

## 实际应用

**云与大气渲染**：Disney 的《无敌破坏王2》（2018）在实时云渲染中使用了双 HG 模型，通过美术调整 $g_1$、$g_2$、$\alpha$ 三个参数来控制云的"蓬松感"与逆光时的光晕强度，避免了全 Mie 计算的性能瓶颈。

**医学体积可视化**：CT/MRI 数据的体积渲染中，皮肤和软组织层的前向散射用 $g \approx 0.9$ 的 HG 相函数建模，可以使半透明皮肤在渲染时呈现符合解剖学观察的蜡质感，而非过于通透的玻璃状外观。

**烟雾与粒子系统**：Houdini 的 Mantra 渲染器在烟雾体积渲染中默认使用 $g=0.0$（各向同性）的 HG 相函数，因为烟雾粒子尺寸分布极宽，各向异性效应相互抵消。用户可将 $g$ 调整至 0.3–0.5 来模拟油烟或特定粒径的气溶胶。

---

## 常见误区

**误区1：认为 $g=0$ 等同于"没有相函数"**  
$g=0$ 的 HG 相函数并非忽略散射，而是各向同性散射——光以等概率散向球面所有方向。不使用相函数（即跳过散射计算）意味着忽略了整个散射事件，二者在物理上有本质区别：前者每个散射事件仍然偏折光线，后者直接令散射系数 $\sigma_s = 0$。

**误区2：用 HG 相函数建模镜面高光**  
当 $g$ 非常接近 1（如 $g=0.99$）时，HG 分布极度集中在前向，但它描述的仍是**体积内部散射**，而非表面反射。将极端前向散射的 HG 相函数误用为替代表面镜面反射项，会导致体积与表面的物理边界模糊，且由于 HG 函数在 $\theta=0$ 处有限（非 delta 函数），仍无法精确复现真实镜面效果。

**误区3：相函数决定散射颜色**  
相函数仅描述散射方向的概率分布，不包含波长依赖的颜色信息。散射颜色由**散射系数** $\sigma_s(\lambda)$ 的波长依赖性决定。例如 Rayleigh 散射呈蓝色，是因为 $\sigma_s \propto \lambda^{-4}$，而非 Rayleigh 相函数本身有颜色偏好——Rayleigh 相函数对所有可见波长形状相同。

---

## 知识关联

相函数建立在**参与介质**的基础概念之上：参与介质定义了散射系数 $\sigma_s$、吸收系数 $\sigma_a$ 和消光系数 $\sigma_t = \sigma_s + \sigma_a$，相函数则进一步精细化散射事件发生后光的重新分布方式。在辐射传输方程（RTE）中，相函数出现在散射项的积分核内：

$$(\omega \cdot \nabla)L = -\sigma_t L + \sigma_s \int_{4\pi} p(\omega', \omega) L(\omega')\, d\omega'$$

对相函数的选择直接影响路径追踪的**重要性采样**效率——可解析采样的 HG 函数相比数值采样的 Mie 函数，在相同样本数下方差更低。掌握相函数后，可进一步研究**多重散射**（Multiple Scattering）算法，如 Woodcock Tracking 和 BSSRDF 近似，这些方法都依赖对单次散射相函数行为的深入理解来设计有效的路