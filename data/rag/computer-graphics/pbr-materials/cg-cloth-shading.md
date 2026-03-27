---
id: "cg-cloth-shading"
concept: "布料着色"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 布料着色

## 概述

布料着色是基于物理的渲染（PBR）中专门处理织物类材质光照响应的技术分支。与金属或介质不同，布料由微细纤维交织而成，其表面结构产生独特的光学现象：正向散射（forward scattering）和侧向散射（silhouette scattering），在逆光方向和轮廓边缘会呈现明显的光晕效果。这一特征使得通用的Cook-Torrance BRDF模型在模拟天鹅绒、丝绸、牛仔布等材质时严重失真，必须采用专用模型。

布料BRDF的研究起步于1990年代末。Michael Ashikhmin等人于2000年在SIGGRAPH论文《An Anisotropic Phong BRDF Model》中提出了对各向异性反射的系统化处理，随后在2007年的《Distribution-based BRDFs》中进一步发展出适合布料的微面元模型。Estevez和Kulla在2017年发表的《Production Friendly Microfacet Sheen BRDF》（又称Charlie模型）则将布料着色带入了现代游戏和电影的实时与离线渲染流水线中，成为当前的工业标准之一。

布料着色的重要性在于其覆盖的应用场景极为广泛：角色服装、家具布艺、汽车内饰等场景中布料材质占据主导视觉权重。若用金属粗糙度工作流直接套用，高光会呈现出类似磨砂塑料的错误外观，而正确的布料BRDF能在边缘产生柔和的"sheen"（光泽晕染）效果，这是区分布料与其他材质的关键视觉线索。

## 核心原理

### Ashikhmin-Velvet模型

Ashikhmin为布料提出的近似模型基于逆向反射（retro-reflection）假设：布料纤维倾向于将光线反射回入射方向，而非镜面反射方向。其法线分布函数（NDF）采用倒置的高斯形态：

$$D_{velvet}(\theta_h) = \frac{1}{\pi(1 + 4\alpha^2)} \left(1 + \frac{4\exp\left(\frac{-\cot^2\theta_h}{\alpha^2}\right)}{\sin^4\theta_h}\right)$$

其中 $\theta_h$ 是半程向量与法线的夹角，$\alpha$ 是控制纤维展开程度的粗糙度参数。该函数在 $\theta_h$ 接近90度（掠射角）时取得最大值，这与布料在侧光下更亮的视觉现象完全对应。传统Beckmann或GGX的NDF峰值在0度，而此处峰值移至接近90度，是布料NDF最本质的数学特征。

### Charlie模型与Sheen项

Estevez-Kulla的Charlie模型对Ashikhmin模型进行了工业级改进，核心是引入更稳定的NDF形式：

$$D_{Charlie}(\theta_h) = \frac{(2 + 1/\alpha)}{2\pi} \sin^{1/\alpha}(\theta_h)$$

该公式使用 $\sin^{1/\alpha}$ 替代指数函数，在GPU着色器中计算代价更低，且在极端参数下数值更稳定。Charlie模型配合 $\text{sheen}$ 颜色参数（通常为布料纤维的漫反射色调），在Disney PBR扩展参数体系中以 `sheenColor` 和 `sheenRoughness` 两个独立参数暴露给美术，与基础金属度工作流正交叠加，不破坏原有参数含义。

Charlie模型的遮蔽-阴影函数（Geometry Term）同样经过特殊处理，采用Neubelt等人提出的近似形式：

$$G_{Charlie}(\mathbf{v}, \mathbf{l}) = \frac{1}{4(\mathbf{n}\cdot\mathbf{l} + \mathbf{n}\cdot\mathbf{v} - (\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v}))}$$

这一分母避免了传统Smith遮蔽函数在布料NDF下产生的能量过度消耗问题。

### 布料的漫反射处理

布料着色不仅修改高光项，其漫反射项也需要特殊处理。标准Lambert漫反射 $f_d = \text{albedo}/\pi$ 对布料仍适用于宏观能量守恒，但在高sheen强度下需乘以一个能量补偿因子 $(1 - \text{sheen})$，防止sheen叠加后总能量超过入射能量。Filament渲染引擎在其开源PBR文档（2019年版）中明确记载了这一处理方式，并提供了对应的预积分DFG查找表（LUT）方案用于IBL（基于图像的照明）中实时计算sheen的环境光贡献。

## 实际应用

在Unreal Engine 5中，布料材质通过"Cloth"着色模型（Shading Model选项中独立列出）激活，内部使用基于Charlie的Sheen BRDF，额外暴露 `Fuzz Color` 参数控制纤维颜色，`Cloth` 参数（0-1）控制布料效果强度与基础PBR层的混合比例。天鹅绒材质通常将 `Cloth` 设为1.0，`Fuzz Color` 设为接近albedo的暖色调，粗糙度保持在0.9以上。

在离线渲染领域，Arnold渲染器自5.3版本起在其Standard Surface材质中加入了 `sheen` 参数组，底层使用的正是Ashikhmin-velvet的NDF变体。制作《蜘蛛侠：平行宇宙》时，Sony Imageworks团队在角色服装上大量使用布料BRDF，通过分层sheen颜色实现了牛仔布的蓝灰色轮廓光晕，区别于同场景金属扣件的高对比度高光。

glTF 2.0的KHR_materials_sheen扩展规范（2020年发布）将Charlie模型标准化为Web端3D内容的布料材质标准，定义了 `sheenColorFactor`（RGB，默认黑色）和 `sheenRoughnessFactor`（0到1，默认0）两个参数，推动了布料着色在WebGL和WebGPU场景中的普及。

## 常见误区

**误区一：用高粗糙度的金属度工作流模拟布料。** 提高GGX粗糙度参数确实能使高光变宽变柔，但GGX的NDF峰值始终在法线方向（$\theta_h=0$），无法产生布料特有的掠射增亮现象。用高粗糙度GGX模拟的"布料"在顺光照明下高光合理，但逆光或侧光时会缺失轮廓光晕，视觉上偏向于磨砂陶瓷而非织物。

**误区二：认为布料不需要菲涅耳（Fresnel）项。** 布料纤维在宏观层面确实没有强烈的折射率差异，但单根纤维在微观层面仍然是介质，存在菲涅耳反射。Charlie模型中 `sheen` 层本身不显式计算菲涅耳，是因为掠射增亮已经由NDF的形状隐式编码，并非完全忽略菲涅耳物理，而是将其折叠入NDF的数学形式中。将sheen项与独立的Schlick菲涅耳相乘会造成双重增强，属于实现错误。

**误区三：将sheen roughness与基础层roughness共用同一参数。** 布料表面存在两个尺度的粗糙度：纤维排列的宏观粗糙度（决定基础漫反射形态）和单根纤维表面的微观粗糙度（决定sheen层宽度）。天鹅绒可以具有宏观平整（基础roughness=0.3）但sheen很宽（sheen roughness=0.9）的特征，两者必须独立控制。

## 知识关联

布料着色以BRDF基础中的NDF、几何衰减函数（G项）和渲染方程为直接前置知识。理解Cook-Torrance框架中三项（D、F、G）的分工，才能理解Charlie模型修改D项形状和G项形式的具体动机——布料的每一处数学改动都对应NDF峰值从0度迁移到90度这一核心决策。

从材质参数化角度，布料着色与Disney PBR扩展参数体系直接相连：sheen参数是Disney Principled BRDF（2012年Burley发表）在原始11参数之外的典型扩展案例，理解这一扩展方式对掌握subsurface、clearcoat等其他特殊层的参数化逻辑有直接参考价值。此外，布料的IBL预积分方案需要为sheen项单独生成DFG查找表，这与标准电介质/金属的DFG纹理不兼容，涉及实时渲染中环境光预计算的具体工程实践。