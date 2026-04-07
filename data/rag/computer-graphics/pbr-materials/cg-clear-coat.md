---
id: "cg-clear-coat"
concept: "清漆层"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 清漆层

## 概述

清漆层（Clear Coat Layer）是PBR材质系统中一种专门模拟物体表面额外透明涂层的多层渲染模型。现实中许多物体——汽车车漆、木制家具、指甲油、碳纤维板——都在主材质表面涂有一层光滑透明的保护漆。这层漆折射率通常约为1.5（接近聚氨酯或丙烯酸清漆的物理值），其高光响应与底层材质完全独立，因此单层BRDF无法正确描述这类材质的视觉行为。

清漆层模型由Akenine-Möller等人在早期车漆渲染研究中提出概念原型，后经Karis（2013年SIGGRAPH Unreal Engine 4技术演讲）和Burley（2012年迪士尼PBR论文）系统化落地到实时与离线渲染管线。迪士尼原则性材质将清漆层作为独立参数`clearcoat`和`clearcoatGloss`引入，成为当前行业事实标准。

清漆层之所以不能简单用提高基础层粗糙度来替代，是因为它产生的是叠加在主表面之上的**第二个独立高光波瓣**，而非对原有高光的修改。在掠射角观察汽车时，车身颜色可能是哑光金属漆，但清漆带来的反射依然尖锐明亮——这种双峰高光分布只有多层模型才能正确重现。

---

## 核心原理

### 双层BRDF叠加公式

清漆层的总体BRDF由底层贡献与清漆层贡献线性叠加而成。标准表达式为：

$$f_{total} = f_{base} \cdot (1 - F_{coat}) + f_{coat}$$

其中：
- $f_{base}$ 为底层材质的完整Cook-Torrance BRDF（包含漫反射与金属高光）
- $f_{coat}$ 为清漆层自身的镜面BRDF，通常取 $f_{coat} = \frac{D_{coat} \cdot G_{coat} \cdot F_{coat}}{4(\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v})}$
- $F_{coat}$ 为清漆层Fresnel项，用于能量守恒：清漆反射走的光不再进入底层

清漆层的Fresnel项使用折射率1.5对应的基础反射率 $F_0 = \left(\frac{1.5-1}{1.5+1}\right)^2 \approx 0.04$，恒定不变，不随艺术家调整，因为清漆物理上几乎都是电介质。

### 清漆层的NDF选择

清漆层通常使用粗糙度较低（clearcoatGloss趋近1时粗糙度趋近0.001）的GGX/Trowbridge-Reitz分布函数，且在迪士尼实现中特意选用**各向同性**GGX，不支持各向异性扩展——这是刻意的简化，因为真实清漆涂层的微表面结构本质上是各向同性的。Google Filament引擎文档中明确记录清漆层固定使用 $\alpha_{coat} = (1 - clearcoatGloss \cdot 0.9)^2$ 作为粗糙度映射，不与底层粗糙度联动。

### 几何遮蔽项的独立计算

清漆层的Smith遮蔽函数 $G_{coat}$ 与底层 $G_{base}$ 必须分开计算，使用清漆自身的粗糙度参数。Heitz（2014）的研究表明，若将底层较高粗糙度的 $G$ 项复用于清漆层，会导致掠射角的清漆高光被过度压暗，与真实车漆在大角度仍呈现明亮反射的现象不符。Filament引擎在实现中对清漆 $G$ 项单独使用 `V_Kelemen` 近似：$V_{Kelemen}(l_h) = \frac{0.25}{l_h^2}$，计算量约减少60%但在视觉上与完整Smith误差小于2%。

---

## 实际应用

**汽车车漆渲染**是清漆层最典型的应用场景。车漆通常由三层构成：底漆（颜色层）、金属片（metallic flakes）和顶部清漆。在UE5的材质编辑器中，启用`Clear Coat`着色模型后，暴露出`Clear Coat`（0-1强度）与`Clear Coat Roughness`（0-1粗糙度）两个专用输入插槽，对应迪士尼论文的两个参数，底层金属漆的高光与顶部清漆高光会在光照计算中分别求值后叠加。

**碳纤维材质**是另一重要场景。碳纤维本身呈现强各向异性织物纹理的底层高光，顶部覆盖的环氧树脂清漆则贡献各向同性的平滑反射。两层高光的方向和形状完全不同，若不使用双层模型，无法同时表现织纹的斜向光泽和树脂的圆形高光。

**实时渲染的近似优化**：由于双层BRDF需要额外的IBL（基于图像的光照）查询，Unity HDRP的清漆层实现使用同一张预滤波环境贴图分两次采样（分别传入底层和清漆粗糙度），而非完整重建两张独立贴图，将内存开销控制在可接受范围内。

---

## 常见误区

**误区一：认为清漆层只是提高了基础层的光泽度。**  
清漆层产生的是物理上独立的第二个高光，而非对已有高光的参数调整。将`clearcoat`设为1并同时降低底层粗糙度，会看到两个高光波瓣叠加，而非单一更亮的高光。在正侧光照射下，汽车表面同时可见底层金属漆的散射高光和清漆层的点状镜面高光，二者颜色和大小均不同，这是验证实现是否正确的直观方法。

**误区二：清漆层的$F_0$可以自由调整。**  
清漆几乎恒定为电介质材料，其$F_0 \approx 0.04$是物理约束而非艺术参数。部分引擎提供了可调节的清漆$F_0$参数，但将其设置超过0.08（对应折射率约1.73）已经脱离真实清漆的物理范围。迪士尼论文原版实现中清漆$F_0$是硬编码常量，正是出于这一物理依据。

**误区三：清漆层不需要法线贴图独立通道。**  
真实清漆层与底层表面可能存在不同的微观细节——例如汽车橘皮纹理（orange peel）专属于清漆层，底层金属漆有自己的法线分布。Filament和UE5均支持为清漆层指定独立的`Clear Coat Normal`输入，若共用底层法线，清漆层的橘皮光效果将无法正确模拟。

---

## 知识关联

**前置基础**：清漆层的每一个子项——GGX的NDF、Smith遮蔽项、Schlick Fresnel近似——均直接来自Cook-Torrance模型框架。理解Cook-Torrance中$D$、$G$、$F$三项的物理含义是解读清漆双层叠加公式的必要前提；特别是Fresnel项在清漆模型中承担了能量在两层之间的分配职责，其Schlick近似$F \approx F_0 + (1-F_0)(1-\cos\theta)^5$在清漆$F_0$固定为0.04时退化为极简形式。

**横向关联**：清漆层与**次表面散射（SSS）材质**共同构成了PBR多层材质体系的两个典型范式——清漆层是在表面**叠加**额外反射层，而SSS是在表面**之下**模拟光的穿透与散射。两者均打破了单层BRDF对复杂材质的表达限制，但物理机制和参数化方式完全不同。掌握清漆层的双层叠加思路，有助于理解薄膜干涉（thin-film interference）等更高阶多层材质模型的设计逻辑。