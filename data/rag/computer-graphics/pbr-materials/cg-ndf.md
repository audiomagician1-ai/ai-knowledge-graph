---
id: "cg-ndf"
concept: "法线分布函数"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 法线分布函数

## 概述

法线分布函数（Normal Distribution Function，简称NDF）描述微表面模型中，朝向半程向量 **h** 的微面片在单位面积上的统计密度。具体而言，NDF 的输出是一个无量纲的标量 D(h)，当对整个半球积分时满足：∫D(h)(n·h)dω = 1，保证能量守恒。它控制高光波瓣的形状——峰值越尖锐，材质越像镜面；尾部越厚，材质越显出"光晕"扩散效应。

NDF 的概念随微表面理论发展而来。1967 年 Torrance 和 Sparrow 在物理光学文献中提出微面片模型，1977 年 Blinn 将其引入计算机图形学并给出 Blinn-Phong NDF，1981 年 Beckmann 和 Spizzichino 在电磁散射理论中导出了以高斯分布为基础的 Beckmann NDF。2007 年 Walter 等人在 EGSR 会议上提出 GGX（也称 Trowbridge-Reitz）NDF，因其更重的尾部与真实金属、介质材质吻合度显著优于 Beckmann，成为当代实时渲染的主流选择。

选择何种 NDF 直接影响高光形态。对于粗糙金属、磨砂玻璃等材质，GGX 的重尾特性能够复现光晕（glints）效果；对于光滑涂层表面，Blinn-Phong 的快速衰减更为高效。因此理解三种 NDF 的数学形式和参数含义，是在 PBR 管线中准确匹配真实世界材质外观的基础工作。

---

## 核心原理

### Blinn-Phong NDF

Blinn-Phong NDF 的形式为：

$$D_{Blinn}(\mathbf{h}) = \frac{\alpha_p + 2}{2\pi} (\mathbf{n} \cdot \mathbf{h})^{\alpha_p}$$

其中 αp 是高光指数，取值范围通常为 [1, 数千]，越大越接近镜面。该公式中 (αp+2)/(2π) 是归一化因子，确保半球积分为 1。Blinn-Phong 的高光波瓣以指数衰减，没有重尾，导致其在真实物理材质拟合中偏差较大——它无法呈现当掠射角下高光向外延伸的光晕圆弧。此外，αp 与感知粗糙度的映射是非线性的，引擎中通常用 αp = (1-roughness)^n 近似映射。

### Beckmann NDF

Beckmann NDF 源于高斯随机过程假设，其公式为：

$$D_{Beckmann}(\mathbf{h}) = \frac{1}{\pi \alpha_b^2 (\mathbf{n}\cdot\mathbf{h})^4} \exp\!\left(-\frac{1-(\mathbf{n}\cdot\mathbf{h})^2}{\alpha_b^2 (\mathbf{n}\cdot\mathbf{h})^2}\right)$$

其中 αb 是粗糙度参数（标准差形式，对应斜率的均方根），通常范围 [0.01, 1]。分母的 (n·h)⁴ 项导致当 n·h 趋近于 0（接近掠射角）时，函数值衰减极快，高光尾部较轻。Beckmann 在蒙特卡罗路径追踪中有成熟的重要性采样公式：θh = arctan(√(−αb² ln u))，其中 u 为均匀随机数，采样效率较高。

### GGX（Trowbridge-Reitz）NDF

GGX NDF 的形式为：

$$D_{GGX}(\mathbf{h}) = \frac{\alpha^2}{\pi \left[(\mathbf{n}\cdot\mathbf{h})^2(\alpha^2 - 1) + 1\right]^2}$$

其中 α = roughness²（迪士尼 PBR 中的重映射，使粗糙度感知更线性）。与 Beckmann 相比，分母是有理分式而非指数函数，使得函数在 (n·h) 趋近于 0 时衰减缓慢，形成重尾（heavy tail）。这一重尾在金属、陶瓷等实际测量数据中普遍存在，也是 GGX 从 2012 年前后开始主导游戏引擎（Unreal Engine 4、Unity HDRP 均采用 GGX）的核心原因。GGX 的重要性采样角度为 θh = arctan(α √(u/(1-u)))，同样只需一次反三角运算。

### 各向异性扩展

GGX 可扩展为各向异性形式：

$$D_{GGX-aniso}(\mathbf{h}) = \frac{1}{\pi \alpha_x \alpha_y \left[\left(\frac{\mathbf{t}\cdot\mathbf{h}}{\alpha_x}\right)^2 + \left(\frac{\mathbf{b}\cdot\mathbf{h}}{\alpha_y}\right)^2 + (\mathbf{n}\cdot\mathbf{h})^2\right]^2}$$

其中 t 和 b 分别是切线与副切线，αx、αy 是两个方向的粗糙度。这使得拉丝金属（brushed metal）和丝绒（satin）等材质的椭圆形高光得以实现。Beckmann 和 Blinn-Phong 也有各向异性变体，但实践中使用远不如各向异性 GGX 普遍。

---

## 实际应用

**游戏引擎默认选择**：Unreal Engine 4 自 2013 年发布以来一直使用 GGX NDF 配合 Smith 遮蔽函数；Unity HDRP 同样默认 GGX，并将 roughness 重映射为 perceptualRoughness² 输入 α。开发者在材质编辑器中调整 Roughness 滑块时，实际修改的就是 GGX 公式中的 α 值。

**离线渲染拟合测量数据**：MERL 材质数据库（100 种各向同性材质）的拟合实验表明，GGX 平均误差约比 Beckmann 低 15%，在黄铜、铝等金属材质上差距尤为明显。这是因为真实金属微表面的法线分布尾部远比 Beckmann 的高斯衰减慢。

**高光抗锯齿**：在实时渲染中，几何法线图中的高频细节会导致 NDF 采样欠缺而产生闪烁。针对 GGX，Toksvig 方法利用法线贴图的 mip 平均长度 |μ| 自动增大 α：α' = α / |μ|^(1/2)，从而在低分辨率 mip 层自动模糊高光，消除次像素闪烁。Beckmann 有类似公式，但 Blinn-Phong 的高光指数形式使等效推导更复杂。

---

## 常见误区

**误区一：认为更高的 α（粗糙度）值会增加总反射能量**。事实上，NDF 本身的归一化约束保证了在任意 α 下积分为 1，粗糙度只改变能量的角度分布而不改变总量。真正影响总能量的是多次散射（multiple scattering）项——粗糙表面中光线在微面片之间多次弹射，如果只用单次散射的 Cook-Torrance 模型，高粗糙度材质会出现能量损失变暗的问题，这与 NDF 本身无关。

**误区二：认为 GGX 在所有场景下都优于 Beckmann**。对于非常光滑（α < 0.1）的涂层或漆面，Beckmann 与 GGX 的视觉差异极小，且 Beckmann 有基于物理的解析 BRDF 积分形式（球面高斯近似），在预积分的环境光照（split-sum 近似）中某些情况下精度略优。另外，学术路径追踪渲染器（如 Mitsuba）历史上以 Beckmann 为默认，积累了更多验证数据。

**误区三：将 NDF 的粗糙度参数 α 直接等同于线性感知粗糙度**。迪士尼 PBR 方案（2012 年 Burley 报告）中明确建议将美术输入的 roughness 通过 α = roughness² 映射后再传入 GGX，原因是线性 α 在低粗糙度区间的视觉变化过于剧烈，平方映射使整个 [0,1] 范围的变化更均匀。若跳过此重映射直接传入 α，高光在低粗糙度端会异常尖锐且对参数变化超敏感。

---

## 知识关联

NDF 是 Cook-Torrance BRDF 中的三个因子之一：f = (D·F·G) / (4(n·l)(n·v))，其中 F 是菲涅耳项，G 是几何遮蔽函数。NDF 的形状选择（GGX vs Beckmann）必须与对应的几何遮蔽函数 G 配套，因为 Smith 方法推导 G 时会使用与 D 相同的分布假设——GGX 的 Smith-G 与 Beckmann 的 Smith-G 公式不同，混用会破坏物理一致性。具体而言，GGX 的 Lambda 函数为 Λ(v) = (√(1 + α²tan²θv) − 1)/2，而 Beckmann 的 Lambda 函数是包含误差函数 erf 的更复杂