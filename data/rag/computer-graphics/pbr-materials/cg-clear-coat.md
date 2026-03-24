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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 清漆层

## 概述

清漆层（Clear Coat Layer）是PBR材质中用于模拟汽车漆面、木器清漆、上光蜡等表面的多层材质模型。其物理原型是在有色底漆或粗糙基底之上喷涂的一层透明保护涂层，该涂层本身光滑且折射率约为1.5（接近聚氨酯和聚酯类涂料的真实折射率），导致表面呈现出底层粗糙纹理与顶层镜面高光共存的复合外观。

这一模型的形式化描述最早在 Burley 2012 年发表的迪士尼 PBR 论文《Physically-Based Shading at Disney》中被系统提出，并以独立参数 `clearCoat` 和 `clearCoatRoughness` 的形式纳入 Disney Principled BRDF。Filament（Google 的移动端 PBR 渲染器）也在其材质系统中完整实现了清漆层，并在官方文档中给出了详细的推导与近似公式。

清漆层之所以在实时渲染中有重要价值，是因为仅靠单层 Cook-Torrance 模型无法同时表达两个不同粗糙度的镜面反射叶。汽车车身的外观之所以在强光下兼具底漆的颜色/金属纹理和清晰的天空倒影，正是因为物理上存在两层具有不同粗糙度的介质界面，若将其强行合并为一层则会失去这种分层高光特征。

---

## 核心原理

### 双层 BRDF 叠加结构

清漆层模型的总 BRDF 由底层 BRDF 与清漆层 BRDF 加权叠加而成：

$$f_{\text{total}} = f_{\text{base}} \cdot (1 - F_c) + f_{\text{coat}}$$

其中：
- $f_{\text{base}}$ 为底层材质的完整 Cook-Torrance BRDF（可以是金属或非金属）
- $f_{\text{coat}}$ 为清漆层自身的镜面 BRDF，通常固定为各向同性、无颜色偏移（白色 Fresnel）
- $F_c$ 为清漆层在当前视角下的 Fresnel 反射率，用于对底层贡献进行能量遮蔽

注意 $(1 - F_c)$ 这一乘法因子代表从清漆层透射进入底层并反射出来的能量比例，保证了能量守恒。如果缺少这一衰减，当清漆层反射率很高时，叠加后的出射亮度将超过入射亮度。

### 清漆层自身的 BRDF 参数化

在 Disney BRDF 的实现中，清漆层使用了一个简化的镜面叶：

- **法线分布函数（NDF）**：采用 GTR1（Generalized Trowbridge-Reitz，γ=1）而非底层使用的 GTR2（GGX），GTR1 产生更窄、更尖锐的高光过渡，符合清漆层光滑涂层的特性
- **Fresnel 项**：固定为折射率 $n=1.5$ 对应的 $F_0 = \left(\frac{1.5-1}{1.5+1}\right)^2 = 0.04$，即 4% 的垂直入射反射率，不受底层颜色影响
- **强度参数 `clearCoat`**：范围 \[0, 1\]，在 Filament 中实际将 $F_0$ 缩放到 \[0, 0.04\] 区间，取值 1 代表全强度清漆
- **粗糙度参数 `clearCoatRoughness`**：独立于底层粗糙度，允许在同一材质上定义底层模糊金属光泽 + 顶层高光滑镜面的组合

### 几何遮蔽与折射偏移

严格的清漆层实现还需处理折射率差异带来的折射偏移：光线穿过清漆层折射后打到底层，若清漆层有一定厚度则采样位置会产生横向偏移。在实时渲染中这一效果通常被忽略（厚度视为零），但在离线渲染或路径追踪中，可通过 BTDF 和清漆层厚度参数精确模拟底层细节的横向位移模糊。

清漆层的 Smith 遮蔽函数通常单独计算，不与底层共享，因为两者的粗糙度独立。Filament 文档给出清漆层遮蔽项使用 $\alpha_c = (0.089 + \text{clearCoatRoughness})^2 / 2$ 的近似，与 GGX 遮蔽的 $\alpha^2 = \text{roughness}^4$ 公式有所不同。

---

## 实际应用

**汽车漆面**：这是清漆层最典型的应用场景。底层设置为带金属片的铝粉漆（metallic≈0.8，roughness≈0.4），顶层清漆设置 clearCoat=1.0、clearCoatRoughness≈0.05。渲染结果可以观察到底层弥散的金属光泽与顶层锐利的 IBL（基于图像的光照）反射同时存在，而单层 Cook-Torrance 模型无法复现这种分离的双高光。

**木器清漆与地板**：木纹底层粗糙度约 0.6，清漆层粗糙度约 0.1。在掠射角观察时，清漆层 Fresnel 效应显著，出现强烈的镜面条纹，同时底层木纹颜色仍清晰可见，这与物理测量结果吻合。

**湿润表面模拟**：将 clearCoat=0.5、clearCoatRoughness=0 应用于原本粗糙的地面材质，可以快速近似模拟雨水在地面形成的薄水膜效果，因为水膜的 $n=1.33$ 与清漆层默认 $n=1.5$ 虽有差异，但在视觉效果上已足够接近。

---

## 常见误区

**误区一：认为清漆层会叠加亮度而不衰减底层**  
初学者常直接将 $f_{\text{coat}}$ 相加而遗漏 $(1-F_c)$ 的衰减因子，导致掠射角时材质亮度远超 1.0。正确实现必须用清漆层的 Fresnel 透射率乘以底层贡献，能量才能守恒。在 WebGL/GLSL 实现中这个乘法极易被遗漏。

**误区二：认为清漆层 NDF 与底层相同**  
一些简化实现复用底层的 GGX（GTR2）NDF 来计算清漆层高光，而 Disney 规范明确指出清漆层应使用 GTR1。GTR1 相比 GTR2 高光尾部更短、中心更集中，两者在低粗糙度时差异明显。错误使用 GTR2 会让清漆高光显得过于扩散，失去真实涂层的"尖锐小光点"特征。

**误区三：清漆层粗糙度与底层粗糙度联动**  
某些引擎（如早期 Unity HDRP 版本）将 clearCoatRoughness 直接锁定为底层 roughness 的某个固定比例。这是错误的简化——汽车漆面底漆可以非常粗糙而清漆可以极其光滑，两者没有物理关联，必须作为独立参数暴露给美术人员。

---

## 知识关联

**前置依赖：Cook-Torrance 模型**  
清漆层的每一个子层本质上都是一个独立的 Cook-Torrance 镜面叶，包含 NDF、Fresnel 和几何遮蔽三项。理解清漆层必须已知 $F_0$、GTR 系列 NDF 的公式形式以及 Smith 遮蔽函数的推导，否则无法理解为何清漆层固定 $F_0=0.04$，也无法区分 GTR1 与 GTR2 的高光形状差异。

**延伸方向**  
清漆层是多层材质系统（Multi-Layer Materials）的最简二层特例。更通用的多层框架如 Adobe Substance 的 Stacked Materials 或 NVIDIA 的 MaterialX 标准支持任意层数的 BSDF 叠加，并考虑层间多次散射。掌握清漆层的双层叠加与能量守恒机制，是理解这类通用多层系统的直接基础。
