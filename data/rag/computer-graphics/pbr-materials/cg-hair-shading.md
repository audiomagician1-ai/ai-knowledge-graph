---
id: "cg-hair-shading"
concept: "毛发着色"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
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

# 毛发着色

## 概述

毛发着色是指在计算机图形学中，对单根毛发纤维与光线交互行为的物理模拟技术。与平面材质的BRDF不同，毛发是一种半透明的圆柱体结构，光线可以穿透纤维、在内部发生折射与反射，最终形成多个独立的高光波瓣。正因如此，描述毛发光照的函数被称为BCSDF（Bidirectional Curve Scattering Distribution Function），而非标准BRDF。

2003年，Stephen Marschner等人在SIGGRAPH上发表了论文《Light Scattering from Human Hair Fibers》，首次提出了基于物理的毛发散射模型，即Marschner模型。该模型将毛发内部结构分为表层角质层（Cuticle）、皮质层（Cortex）和髓质层（Medulla），并针对前两者建立了精确的光路追踪方程。这篇论文彻底改变了电影与游戏行业中毛发渲染的技术路线。

毛发渲染的难点在于：单个人类头部约有10万根毛发，每根毛发的直径仅为50至70微米，且毛发表面的角质层鳞片倾角约为2至4度，这一细微的倾角会导致高光位置相对于光源方向产生明显偏移。正确模拟这一偏移是实现真实感毛发的关键。

## 核心原理

### 三条光路：R、TT、TRT

Marschner模型将毛发散射分解为三条主要光路，分别以字母缩写命名：

- **R（Reflection）**：光线直接在毛发表面反射，形成第一个高光波瓣。由于角质层鳞片倾角 α ≈ 2°-4°，R高光相比镜面圆柱体会向发根方向偏移约 2α。
- **TT（Transmission-Transmission）**：光线两次穿透毛发纤维，形成透射分量。这是毛发呈现彩色内透光效果的主要原因，例如金发在逆光下的金黄光晕。
- **TRT（Transmission-Reflection-Transmission）**：光线进入纤维后在内壁反射一次再透射出去，形成第二个高光波瓣。TRT高光比R高光更宽、更亮，并向发梢方向偏移约 4α-2α = 2α（net offset约+2α），且携带了纤维的吸收颜色。

三条光路的能量贡献可分别用方位角函数 N(φ) 和纵向散射函数 M(θ) 的乘积表示，总散射函数为：

$$S(\theta_i, \phi_i, \theta_r, \phi_r) = \sum_{p \in \{R, TT, TRT\}} M_p(\theta_h) \cdot N_p(\phi)$$

其中 θ 为纵向角（沿毛发轴方向），φ 为方位角（垂直截面方向），θ_h 为半角。

### 双高光模型（Kajiya-Kay 简化）

对于实时渲染场景，1989年James Kajiya与Timothy Kay提出了更简单的双高光模型（Two-Highlight Hair Model）。该模型放弃了完整的光路追踪，改用两个各向异性高光层来近似毛发外观：

- **主高光（Primary Specular）**：对应R光路，使用较小的高光指数（Shininess ≈ 80-100），颜色接近光源色，沿切线方向 t 向发根偏移角度 shift1。
- **次高光（Secondary Specular）**：对应TRT光路，使用较大的高光指数（Shininess ≈ 20-40），颜色混合了毛发固有色，向发梢偏移 shift2，约为 shift1 的3倍。

Kajiya-Kay的切线高光公式为：

$$\text{Specular} = (\sin(\mathbf{t} \cdot \mathbf{l}) \cdot \sin(\mathbf{t} \cdot \mathbf{v}) + \cos(\mathbf{t} \cdot \mathbf{l}) \cdot \cos(\mathbf{t} \cdot \mathbf{v}))^n$$

即 $(\mathbf{t} \cdot \mathbf{h})$ 用切线替代法线后展开的形式，其中 t 为毛发切线，h 为半角向量，n 为高光指数。

### 吸收与黑色素参数化

毛发颜色由黑色素（Melanin）含量决定，分为真黑色素（Eumelanin，棕黑色）和褪黑色素（Pheomelanin，红黄色）两种。Marschner模型中，纤维对RGB三通道的吸收系数 σ_a 可由这两种色素的浓度加权求和：

$$\sigma_a = c_e \cdot \sigma_{a,\text{eu}} + c_p \cdot \sigma_{a,\text{ph}}$$

典型金发的 σ_a ≈ (0.06, 0.10, 0.20)（RGB），黑发的 σ_a ≈ (0.50, 0.60, 0.65），通过调整 c_e 和 c_p 可覆盖几乎所有自然发色。

## 实际应用

**电影级渲染**：皮克斯、迪士尼等工作室在其路径追踪渲染器（如RenderMan、Hyperion）中直接实现完整的Marschner模型，并在TRT路径上额外加入TRRT（三次内部反射）来捕获暗发中的彩色内透光。电影《勇敢传说》（2012年）中梅莉达的卷发是首个大规模应用物理毛发着色的代表案例，每根毛发使用约10万个控制曲线段。

**游戏实时渲染**：虚幻引擎5（UE5）的Groom系统采用简化的Marschner模型，将R和TRT合并为两个高光项，并预计算方位角散射函数存入LUT（查找表），将原本需要积分的 N_p(φ) 降为单次纹理采样，在PC平台上将毛发着色耗时控制在0.3ms以内。

**美妆与理发仿真**：Adobe Substance 3D等工具在毛发着色参数中直接暴露黑色素浓度 c_e 和 c_p 滑块，美发师可用这些参数准确预览染发后的外观，而非靠主观调整RGB颜色。

## 常见误区

**误区一：用标准Blinn-Phong法线高光代替切线高光**。许多初学者直接将毛发当作细圆柱体，用法线计算高光，这会导致高光在视角变化时沿毛发截面环形移动，而非沿发丝纵向延伸。正确做法是使用Kajiya-Kay的切线公式，高光应当在纵向散射，在视角绕毛发旋转时保持相对稳定。

**误区二：忽略偏移角导致高光位置错误**。不少实现省略了角质层鳞片倾角 α 引起的高光偏移，将两个高光波瓣对称放置在相同位置。实际上R高光和TRT高光在纵向上的偏移方向相反，差值约为 6α ≈ 12°-24°，缺少这一偏移会使毛发失去立体感，且在梳理方向改变时表现异常。

**误区三：将TT透射分量省略后用漫反射补偿**。某些低成本实现去掉TT路径，改用增大漫反射系数来填补能量。然而TT路径产生的是具有饱和颜色的前向散射亮斑（尤其在逆光时），与漫反射的均匀分布完全不同。省略TT会使金发、红发等高透光率发色在逆光下显得暗淡无光。

## 知识关联

毛发着色建立在**BRDF基础**之上，但将其推广至圆柱体几何的BCSDF框架。理解菲涅耳方程（Fresnel Equations）是计算R路径反射率的前提，毛发与空气界面的折射率通常取 η ≈ 1.55。纵向散射函数 M_p(θ) 本质上是一个以高斯分布近似的卷积核，与微表面模型中的法线分布函数（NDF）在数学形式上有相似之处，但作用域是纵向角而非半球面法线空间。此外，大规模毛发渲染还涉及自阴影计算，常见方案是沿发丝切线方向生成深度图（Strand-Based Shadow Map），这是毛发着色与光线遮挡系统的衔接点。