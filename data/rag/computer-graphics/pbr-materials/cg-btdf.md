---
id: "cg-btdf"
concept: "透射BRDF"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 透射BRDF（BTDF与BSDF统一框架）

## 概述

透射BRDF在正式术语中称为**BTDF（双向透射分布函数，Bidirectional Transmittance Distribution Function）**，描述光线穿透介质界面后在折射方向上的能量分布。与BRDF描述反射不同，BTDF量化的是入射光从介质一侧穿入另一侧后，沿特定出射方向的辐射率之比。将BRDF与BTDF合并后，得到**BSDF（双向散射分布函数）**，这是处理玻璃、水、皮肤、蜡烛等半透明材质时必须使用的统一框架。

BTDF的正式数学定义由 James Kajiya 在1986年的渲染方程论文中纳入统一散射描述，但微表面透射模型的核心推导来自 Walter 等人2007年发表的论文《Microfacet Models for Refraction through Rough Surfaces》，该论文将Cook-Torrance反射框架扩展至折射域，成为现代PBR透射的基石。

理解BTDF对渲染半透明物体不可或缺：一块磨砂玻璃与光滑玻璃的视觉差异，完全由BTDF的分布形状决定——前者透射波瓣宽而模糊，后者集中在Snell折射角附近。忽略BTDF而仅用透明度Alpha混合，无法正确模拟焦散、色散或粗糙玻璃的模糊透射效果。

---

## 核心原理

### BTDF的数学定义与雅可比变换

BTDF的定义与BRDF形式类似，但涉及跨越介质界面的立体角变换：

$$f_t(\omega_i, \omega_t) = \frac{dL_t(\omega_t)}{L_i(\omega_i)\cos\theta_i \, d\omega_i}$$

其中 $\omega_i$ 为入射方向，$\omega_t$ 为折射出射方向，$\theta_i$ 为入射角。

关键难点在于折射时存在**立体角压缩**。根据Snell定律 $n_i \sin\theta_i = n_t \sin\theta_t$，当光从光疏介质（$n_i$）进入光密介质（$n_t > n_i$）时，折射锥角变小。将入射立体角 $d\omega_i$ 转换为折射侧立体角 $d\omega_t$ 的雅可比行列式为：

$$\frac{d\omega_t}{d\omega_i} = \frac{n_t^2 \cos\theta_t}{n_i^2 \cos\theta_i}$$

这意味着折射光线携带的辐射率要乘以 $(n_t/n_i)^2$ 的比值，这一因子常被初学者遗漏。

### 微表面折射模型（Walter 2007）

Walter模型将Cook-Torrance框架中的半角向量替换为折射半角向量 $\mathbf{h}_t$，其定义为使入射方向折射到 $\omega_t$ 的微表面法线方向：

$$\mathbf{h}_t = -\frac{n_i \omega_i + n_t \omega_t}{|n_i \omega_i + n_t \omega_t|}$$

完整的微表面BTDF公式为：

$$f_t = \frac{|(\omega_i \cdot \mathbf{h}_t)(\omega_t \cdot \mathbf{h}_t)|}{(\omega_i \cdot \mathbf{n})(\omega_t \cdot \mathbf{n})} \cdot \frac{n_t^2 \cdot (1-F) \cdot D(\mathbf{h}_t) \cdot G(\omega_i, \omega_t)}{(n_i(\omega_i \cdot \mathbf{h}_t) + n_t(\omega_t \cdot \mathbf{h}_t))^2}$$

其中：
- $D(\mathbf{h}_t)$：微表面法线分布函数（通常用GGX/Trowbridge-Reitz），与反射侧共用同一粗糙度参数
- $G(\omega_i, \omega_t)$：阴影遮蔽函数，但需特别注意此处 $\omega_t$ 在曲面下方，符号处理与反射情况不同
- $(1-F)$：未被反射（Fresnel反射率为F）的透射能量比例

### BSDF统一框架与能量守恒

BSDF将反射与透射组合为单一框架：

$$f_s(\omega_i, \omega_o) = f_r(\omega_i, \omega_o) \cdot F + f_t(\omega_i, \omega_t) \cdot (1-F)$$

能量守恒要求两者之和满足：

$$\int_{\Omega^+} f_r \cos\theta_r \, d\omega_r + \int_{\Omega^-} f_t \cos\theta_t \, d\omega_t \leq 1$$

注意积分域不同：反射在上半球 $\Omega^+$，透射在下半球 $\Omega^-$。实践中，UE4和Unity HDRP均在折射通道里单独存储粗糙度，与漫反射粗糙度可以独立控制，允许材质表面反射模糊、背面透射清晰（如汽车前挡风玻璃涂层）。

---

## 实际应用

**磨砂玻璃渲染**：使用GGX分布的BTDF，粗糙度参数设为0.3时，折射图像呈现约15°的模糊扩散角，视觉上产生"磨砂"效果。粗糙度为0时退化为完美折射（Snell折射），此时BTDF退化为Dirac delta函数。

**皮肤与蜡烛（次表面散射的入口）**：BTDF是次表面散射（SSS）的第一步——光线通过BTDF进入介质，在内部经过多次散射后，由另一点的BTDF射出。NVIDIA在GeForce 6系列时代的皮肤渲染中，即将透射入射建模为Walter BTDF + 内部散射剖面的两阶段流程。

**色散模拟**：由于折射率 $n$ 随波长变化（棱镜对红光折射率约1.514，紫光约1.532），可对RGB三通道分别使用不同的 $n_t$ 值计算BTDF，模拟彩虹边缘或钻石火彩。

**实时近似（屏幕空间折射）**：虚幻引擎的Refraction材质节点本质上是对BTDF的屏幕空间近似，通过扰动UV偏移来模拟低粗糙度BTDF的折射效果，但无法处理全内反射（Total Internal Reflection, TIR）等极端角度情况。

---

## 常见误区

**误区一：将BTDF的 $(n_t/n_i)^2$ 因子遗漏**  
许多自己实现BTDF的开发者忘记乘以折射率比值的平方项，导致玻璃材质在 $n=1.5$（标准光学玻璃折射率）时透射能量偏低约44%。这一因子源于立体角压缩的物理现实，不是可以忽略的近似。

**误区二：反射/透射的遮蔽函数共用同一公式**  
GGX的Smith遮蔽函数 $G_1$ 在反射时要求 $\mathbf{v} \cdot \mathbf{n} > 0$，但在BTDF中出射方向 $\omega_t$ 位于下半球，必须改用 $|\omega_t \cdot \mathbf{n}|$ 进行符号修正，否则G项会出现负值或错误截断，造成透射能量异常变暗。

**误区三：用Alpha混合替代BTDF声称实现了"物理透明"**  
Alpha混合（$C = \alpha C_{fg} + (1-\alpha)C_{bg}$）是纯合成操作，不遵循Fresnel定律，不随视角改变透明度（真实玻璃在掠射角接近不透明），也无法产生焦散。只有基于BTDF的积分渲染才能正确重现这些现象。

---

## 知识关联

**前置：BRDF基础**  
BTDF的推导直接复用了Cook-Torrance的微表面框架——法线分布函数D、Smith遮蔽函数G的数学形式完全来自BRDF，但半角向量定义和雅可比因子是BTDF新增的关键差异。已掌握BRDF的学习者只需重点关注折射半角 $\mathbf{h}_t$ 与反射半角的定义区别，以及 $(n_t/n_i)^2$ 因子的来源。

**横向关联：菲涅耳方程**  
BSDF框架中，反射与透射能量的分配比例由菲涅耳方程精确控制。Schlick近似 $F \approx F_0 + (1-F_0)(1-\cos\theta)^5$ 虽然适用于导体反射，但在处理全内反射临界角附近时误差较大，Walter 2007建议在折射材质中直接使用精确的Fresnel-Dielectric公式。

**延伸方向：次表面散射（SSS）与体积渲染**  
BTDF描述的是单次折射界面的透射，当介质厚度增加或散射系数 $\sigma_s$ 非零时，需要进入体积散射方程（Radiative Transfer Equation, RTE）的领域。BTDF是光线穿越界面的"入口函数"，后续的体内传播由相函数（Phase Function）和消光系数共同决定，两者共同构成完整的体积材质描述体系。
