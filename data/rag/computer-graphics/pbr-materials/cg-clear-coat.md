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
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 清漆层

## 概述

清漆层（Clear Coat Layer）是PBR材质系统中用于模拟汽车喷漆、木质清漆、指甲油等具有半透明保护涂层材质的双层BRDF模型。其物理原理来源于真实世界中的涂层结构：底层为带颜色的漫反射基底（base layer），顶层为一层薄薄的透明高光涂料（clear coat layer），两层之间存在能量守恒关系。Unreal Engine 4在2013年前后将清漆层作为独立着色模型引入其材质系统，随后Filament渲染引擎（Google，2018年）将其数学框架完整公开，成为实时渲染领域的标准参考实现。

清漆层之所以重要，在于用单层Cook-Torrance模型无法同时描述两个不同粗糙度的镜面反射峰。例如汽车车漆往往底层金属粉为中等粗糙度（roughness≈0.4–0.6），而顶层清漆极为光滑（roughness≈0.0–0.1），两者叠加形成一个宽底高峰的双峰高光分布，这是单层模型物理上无法重现的现象。

---

## 核心原理

### 双层BRDF叠加公式

清漆层的完整BRDF为顶层与底层贡献之和，并对底层施加能量衰减：

$$f_r = f_{base}(1 - F_c)^2 + f_{coat}$$

其中：
- $f_{base}$ 为底层Cook-Torrance BRDF（包含漫反射与镜面项）
- $f_{coat}$ 为顶层清漆Cook-Torrance镜面BRDF
- $F_c$ 为清漆层在入射方向上的菲涅尔反射率（Fresnel reflectance of the coat）
- $(1 - F_c)^2$ 表示光线进入和离开清漆层时各损失一次能量，因此平方

这个$(1 - F_c)^2$衰减系数是清漆层公式区别于简单BRDF叠加的关键所在，它保证了整个双层系统满足能量守恒。

### 清漆层的菲涅尔近似

顶层清漆通常被建模为折射率约为**1.5**的无色电介质，其对应的F0（法线方向基础反射率）计算为：

$$F_0^{coat} = \left(\frac{n-1}{n+1}\right)^2 = \left(\frac{1.5-1}{1.5+1}\right)^2 \approx 0.04$$

因此清漆层在法线方向只反射约4%的入射光，而在掠射角（grazing angle）趋近于1。实践中使用Schlick近似来计算任意角度的$F_c$：

$$F_c = F_0^{coat} + (1 - F_0^{coat})(1 - \cos\theta_i)^5$$

顶层清漆的NDF通常使用GGX分布，且其粗糙度参数`clearCoatRoughness`独立于底层`roughness`，在Filament中默认值固定为0.089（对应感知粗糙度perceptualRoughness=0.3）。

### 法线处理与双法线贴图

清漆层引入了一个重要的技术挑战：顶层与底层可以拥有**不同的法线**。例如碳纤维材质，底层显示编织纹理的各向异性法线，顶层则是光滑清漆的宏观法线。在实现上，着色器维护两套法线向量：`baseNormal`（底层）和`clearCoatNormal`（顶层），分别用于各自BRDF的几何遮蔽（G term）和法线分布（D term）的计算。Unreal Engine将顶层法线贴图单独暴露为`ClearCoatBottomNormal`插槽，Google Filament则通过`clearCoatNormalMap`参数实现。

---

## 实际应用

**汽车车漆（Automotive Paint）**：这是清漆层最典型的用例。美术资产通常设置底层为含金属粉的漫反射（metallicness≈0.0，带金属片状高光），顶层clearCoatStrength=1.0，clearCoatRoughness接近0（光亮如镜）。底层通过AlbedoColor呈现车身颜色，顶层只提供无色的镜面峰值，最终渲染出汽车引擎盖上那种"流光溢彩"的效果。

**木质家具清漆**：实木桌面会将底层设为木纹漫反射贴图（高粗糙度，roughness≈0.7），顶层清漆为中等光滑（clearCoatRoughness≈0.2–0.3），clearCoatStrength≈0.5–0.8，产生木纹可见而表面又略有镜面反射的效果，物理上对应了几道薄薄的清漆喷涂。

**指甲油与湿润表面**：湿润岩石、潮湿皮肤等材质，利用clearCoatStrength在0.3–0.6范围内模拟表面水膜的额外高光层，同时水膜（顶层）折射率约1.33，其F0约为0.02，比标准清漆更低，需要修改$F_0^{coat}$参数才能获得准确的物理结果。

---

## 常见误区

**误区一：认为清漆层等同于直接叠加两个独立BRDF**

初学者常写出$f_r = f_{base} + f_{coat}$，忽略了$(1-F_c)^2$的能量损耗系数。这导致在掠射角时材质过亮，底层高光比物理正确值强出约20–30%。正确做法必须对底层整体（包括其漫反射项）乘以$(1-F_c)^2$衰减。

**误区二：认为清漆层只影响镜面高光，不影响漫反射**

实际上底层的漫反射同样被顶层清漆吸收了两次（进出各一次）。在Filament的实现中，底层Lambertian漫反射也需乘以$(1-F_c)^2$，否则会出现漫反射颜色在掠射角偏亮、与真实涂层材质不匹配的问题。

**误区三：清漆层强度clearCoatStrength可以用底层metallic=1.0替代**

金属度为1时底层无漫反射、F0接近反照率颜色，行为与清漆层（无色、F0≈0.04的电介质层）完全不同。用metallic=1不能产生双峰高光分布，也无法在低roughness时重现清漆那种窄锐高光叠加在宽底高光上的层次感。

---

## 知识关联

清漆层以**Cook-Torrance模型**为直接基础：顶层$f_{coat}$本身就是一个标准的Cook-Torrance镜面BRDF，使用GGX-NDF、Smith几何遮蔽函数和Schlick菲涅尔，只是其粗糙度和F0参数被固定为对应清漆折射率的特定值。理解Cook-Torrance中D、G、F三项的物理含义是推导清漆层能量守恒衰减系数$(1-F_c)^2$的先决条件。

在材质系统的横向扩展上，清漆层与**各向异性材质（Anisotropy）**可以组合使用——底层使用各向异性GGX（拉丝金属、碳纤维），顶层清漆保持各向同性，两套法线分别控制，这是Filament 1.4版本后支持的组合。此外，清漆层的双法线机制与**法线贴图叠加（Normal Map Blending）**技术直接相关，顶层法线与底层法线的混合方式（Reoriented Normal Mapping，RNM）影响层间过渡区域的正确性。对于需要更复杂光学现象（如干涉色、衍射）的薄膜材质，则需要进一步扩展为**薄膜干涉（Thin Film Interference）**模型，那是比清漆层更高一层的物理抽象。
