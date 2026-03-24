---
id: "cg-anisotropy"
concept: "各向异性"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 各向异性

## 概述

各向异性（Anisotropy）描述材质表面反射行为随观察方向或光照方向不同而呈现差异的物理现象。区别于各向同性材质（BRDF关于方位角旋转对称），各向异性材质的高光形状沿特定切线方向被拉伸或压缩，在参数空间中表现为椭圆形高光而非圆形高光。拉丝金属、丝绸织物、磁盘光碟等都是典型的各向异性材质，其表面存在微观方向性结构。

各向异性BRDF的理论基础可追溯至1984年James Blinn对各向异性高光的早期描述，但现代PBR中广泛使用的模型来自Burley在2012年Disney BRDF报告中提出的参数化方案。该报告引入了单一的各向异性参数 $\alpha_{aniso} \in [-1, 1]$，使艺术家能够直观控制高光形状的拉伸程度与方向，而无需直接操控底层微表面分布函数的两个粗糙度轴。

在实时渲染和离线渲染中，各向异性对金属材质的视觉真实感影响尤为显著。若对拉丝金属使用各向同性BRDF，其圆形高光会与真实的线状高光产生明显差异，即便使用了精确的菲涅耳和几何遮蔽项也无法弥补这一缺陷。因此，各向异性是PBR材质系统中区分不同微观结构的关键物理参数。

## 核心原理

### 各向异性微表面分布函数

标准Cook-Torrance模型使用各向同性GGX分布，其法线分布函数（NDF）形式为 $D(\mathbf{h}) = \frac{\alpha^2}{\pi((\mathbf{n}\cdot\mathbf{h})^2(\alpha^2-1)+1)^2}$，其中 $\alpha$ 为单一粗糙度参数。各向异性GGX（也称为GTR2各向异性变体）将其扩展为双轴形式：

$$D(\mathbf{h}) = \frac{1}{\pi \alpha_x \alpha_y \left(\left(\frac{\mathbf{t}\cdot\mathbf{h}}{\alpha_x}\right)^2 + \left(\frac{\mathbf{b}\cdot\mathbf{h}}{\alpha_y}\right)^2 + (\mathbf{n}\cdot\mathbf{h})^2\right)^2}$$

其中 $\mathbf{t}$ 为切线向量，$\mathbf{b}$ 为副切线向量，$\alpha_x$ 和 $\alpha_y$ 分别为沿切线轴和副切线轴的粗糙度。当 $\alpha_x = \alpha_y$ 时，该公式退化为各向同性GGX分布。

### Disney各向异性参数化

Disney方案使用单一各向异性参数 $anisotropic \in [0, 1]$ 与基础粗糙度 $roughness$ 共同推导双轴粗糙度：

$$\alpha_x = roughness^2 \cdot \frac{1}{\sqrt{1 - 0.9 \cdot anisotropic}}, \quad \alpha_y = roughness^2 \cdot \sqrt{1 - 0.9 \cdot anisotropic}$$

系数0.9是经验值，防止 $\alpha_y$ 趋向于0导致数值奇异性。当 $anisotropic = 0$ 时两轴相等；当 $anisotropic = 1$ 时，$\alpha_x / \alpha_y$ 比值达到约 $\sqrt{10} \approx 3.16$，产生显著的线状高光。

### 各向异性几何遮蔽项

各向同性Smith-GGX几何项同样需要扩展为各向异性版本。对于各向异性Schlick-Smith近似，单方向遮蔽函数变为：

$$G_1(\mathbf{v}) = \frac{2(\mathbf{n}\cdot\mathbf{v})}{\mathbf{n}\cdot\mathbf{v} + \sqrt{\alpha_x^2(\mathbf{t}\cdot\mathbf{v})^2 + \alpha_y^2(\mathbf{b}\cdot\mathbf{v})^2 + (\mathbf{n}\cdot\mathbf{v})^2}}$$

完整几何项 $G = G_1(\mathbf{l}) \cdot G_1(\mathbf{v})$，其中 $\mathbf{l}$ 为光照方向。遗漏各向异性几何项而仅更换NDF，会导致掠射角下能量守恒破坏。

### 切线空间参数化与旋转

各向异性BRDF的高光方向由切线向量 $\mathbf{t}$ 决定。切线向量来源于网格UV展开的切线空间，但艺术家通常还需要一个额外的**各向异性旋转角度**参数（$anisotropicAngle \in [0, 1]$，映射到 $[0, 2\pi]$）来旋转高光方向，而不依赖UV展开方式。旋转后的切线为：

$$\mathbf{t}' = \cos(\theta)\mathbf{t} + \sin(\theta)\mathbf{b}$$

其中 $\theta = anisotropicAngle \times 2\pi$。Filament渲染引擎从1.0版本起便在材质系统中暴露该旋转参数，允许在纹理贴图中逐像素编码各向异性旋转方向，实现如流动金属丝线的复杂效果。

## 实际应用

**拉丝不锈钢**是最常见的各向异性材质用例。实现时，将 $anisotropic$ 设为约0.8，$roughness$ 设为0.3–0.5，切线方向沿拉丝方向对齐。高光呈现为垂直于拉丝方向的细长光斑，这与物理上微观沟槽将光散射到垂直于沟槽方向的行为一致。

**丝绸和缎面织物**呈现出特殊的环形高光（Schimmer），其切线方向随纤维编织方向变化。实际制作中会使用各向异性旋转贴图（切线流向图，即Tangent Flow Map）来编码逐像素的纤维方向，再配合各向异性BRDF生成随视角变化的丝光效果。育碧在《刺客信条：奥德赛》的布料着色器中即采用了此类切线流向贴图驱动的各向异性材质。

**光碟（CD/DVD）**表面的彩虹色条纹虽主要来自衍射光栅效应，但其初步近似可以用极高各向异性（$anisotropic \approx 1.0$）且低粗糙度的BRDF模拟环形渐变高光，作为无法使用波动光学模型时的替代方案。

## 常见误区

**误区一：认为各向异性仅影响高光形状，不影响能量守恒。** 实际上，若只替换NDF而保持各向同性几何项，BRDF在掠射角附近会超出能量守恒上限。各向异性NDF和各向异性Smith几何项必须配对使用，才能保证 $\int D(\mathbf{h})(\mathbf{n}\cdot\mathbf{h})\,d\omega_h = 1$ 以及BRDF的能量不增特性。

**误区二：认为切线方向完全由网格UV决定，无法在运行时调整。** 切线空间的UV切线只是默认方向，各向异性旋转参数允许独立旋转高光方向。更进一步，可以使用切线流向图（Tangent Flow Map）将方向编码为纹理的RG通道（存储 $(\cos\theta, \sin\theta)$），实现复杂曲面上逐点各向异性方向控制，这在布料和拉丝金属的细节表现上不可或缺。

**误区三：将各向异性参数的正负号当作纯粹的方向翻转。** 在部分引擎（如Blender的Principled BSDF）中，各向异性参数的符号含义是将高光拉伸方向从沿切线轴切换到沿副切线轴，而不是简单的高光旋转180°。具体来说，$anisotropic = +0.8$ 时高光沿 $\mathbf{t}$ 方向拉伸（即 $\alpha_t < \alpha_b$），$anisotropic = -0.8$ 时高光沿 $\mathbf{b}$ 方向拉伸，两者在视觉上产生90°旋转的效果。

## 知识关联

各向异性BRDF建立在Cook-Torrance微表面框架之上，其核心修改是将单一粗糙度参数 $\alpha$ 拆分为沿切线和副切线的两个独立粗糙度 $(\alpha_x, \alpha_y)$，并将NDF和几何项从各向同性函数扩展为依赖 $\mathbf{t}$、$\mathbf{b}$ 方向的各向异性函数。理解Cook-Torrance中GGX的数学推导是理解各向异性扩展的必要前提，因为各向异性版本的每一项都是对应各向同性项的直接泛化。

各向异性与**切线空间**的关系极为紧密：高光的物理方向完全由切线向量 $\mathbf{t}$ 决定，因此网格的切线生成质量、UV接缝处的切线连续性，以及各向异性旋转贴图的正确编码，都直接影响各向异性效果的视觉质量。在实际项目中，各向异性材质往往需要美术与技术美术密切配合，确
