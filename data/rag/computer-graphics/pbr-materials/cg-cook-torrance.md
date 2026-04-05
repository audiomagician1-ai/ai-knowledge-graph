---
id: "cg-cook-torrance"
concept: "Cook-Torrance模型"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Cook-Torrance模型

## 概述

Cook-Torrance模型是由Robert Cook和Kenneth Torrance于1982年在论文《A Reflectance Model for Computer Graphics》中提出的微表面双向反射分布函数（BRDF）。它是第一个将物理光学中的微表面理论系统性地引入计算机图形学的光照模型，将表面视为由无数微小镜面（microfacet）组成的集合，每个微表面仅在其法线方向等于半角向量（half-vector）时才对观察方向产生镜面反射贡献。

该模型的完整公式为：

$$f_r = \frac{D(\mathbf{h}) \cdot F(\mathbf{v}, \mathbf{h}) \cdot G(\mathbf{l}, \mathbf{v}, \mathbf{h})}{4(\mathbf{n} \cdot \mathbf{l})(\mathbf{n} \cdot \mathbf{v})}$$

其中 $D$ 为法线分布函数，$F$ 为菲涅尔项，$G$ 为几何遮蔽项，分母中的 $4(\mathbf{n} \cdot \mathbf{l})(\mathbf{n} \cdot \mathbf{v})$ 是将微表面坐标变换回宏观表面的归一化因子。Cook-Torrance模型之所以重要，在于它替代了此前图形学中广泛使用的Phong模型——后者完全基于经验而非物理，无法正确模拟掠射角下的高光拉伸现象，也不满足能量守恒。

## 核心原理

### D项：法线分布函数（Normal Distribution Function）

D项描述微表面法线在半角向量 $\mathbf{h}$ 方向的统计分布密度，决定高光的形状与尖锐程度。Cook和Torrance在原始论文中使用的是Beckmann分布：

$$D_{Beckmann}(\mathbf{h}) = \frac{1}{\pi \alpha^2 \cos^4\theta_h} \exp\left(-\frac{\tan^2\theta_h}{\alpha^2}\right)$$

其中 $\alpha$ 是表面粗糙度参数，$\theta_h$ 是半角向量与宏观法线的夹角。在现代PBR流程中，Disney于2012年推广的GGX（Trowbridge-Reitz）分布因其更长的高光尾部而取代Beckmann成为主流，但两者都是D项的具体实现。D项必须满足归一化条件：$\int_{\Omega} D(\mathbf{h})(\mathbf{n} \cdot \mathbf{h}) d\omega_h = 1$，即所有微表面面积投影之和等于宏观表面面积。

### F项：菲涅尔方程（Fresnel Equation）

F项计算光在微表面上发生反射的比例，依赖于入射光与微表面法线的夹角 $\theta_d$（即视线与半角向量的夹角）。Cook-Torrance模型中使用精确的Fresnel方程，但1994年Schlick给出了计算成本更低的近似：

$$F_{Schlick}(\mathbf{v}, \mathbf{h}) = F_0 + (1 - F_0)(1 - \mathbf{v} \cdot \mathbf{h})^5$$

$F_0$ 是材质在垂直入射时的基础反射率，对于非金属通常在0.02–0.05之间，对于金属则直接为彩色反射率（如金的 $F_0 \approx (1.0, 0.77, 0.34)$）。F项的物理意义是：即使一块非常粗糙的非金属，在掠射角（$\theta_d \to 90°$）时反射率也趋近于1，这是Phong模型无法解释的现象。

### G项：几何遮蔽函数（Geometry Function）

G项对微表面间的自遮蔽（shadowing）和自遮挡（masking）进行建模，修正那些因被相邻微表面阻挡而无法对出射辐亮度产生贡献的区域。Cook-Torrance原始论文中使用的是基于V形槽假设的几何项：

$$G_{Cook-Torrance} = \min\left(1,\ \frac{2(\mathbf{n}\cdot\mathbf{h})(\mathbf{n}\cdot\mathbf{v})}{\mathbf{v}\cdot\mathbf{h}},\ \frac{2(\mathbf{n}\cdot\mathbf{h})(\mathbf{n}\cdot\mathbf{l})}{\mathbf{v}\cdot\mathbf{h}}\right)$$

G项取值在 $[0, 1]$ 之间，当光线方向或视线方向趋近于切线平面（掠射）时，G项趋近于0，从而压低掠射角高光，避免物理上不可能的"亮边"伪影。现代实现中，Smith's G函数因与D项在数学上更一致而被优先采用。

### 分母的几何意义

分母 $4(\mathbf{n} \cdot \mathbf{l})(\mathbf{n} \cdot \mathbf{v})$ 并非凑数的经验系数，而是从微表面立体角 $d\omega_h$ 转换到出射方向立体角 $d\omega_o$ 时产生的Jacobian行列式，其推导依赖于 $d\omega_o = 4(\mathbf{v} \cdot \mathbf{h})d\omega_h$ 这一几何关系。这个因子确保了整个BRDF在物理上符合赫姆霍兹互易原理（Helmholtz reciprocity），即交换入射和出射方向后BRDF值不变。

## 实际应用

在Unreal Engine 4的PBR流程中，Cook-Torrance镜面项与Lambert漫反射项共同构成完整的材质响应：引擎默认使用GGX作为D项、Schlick近似作为F项、Smith-GGX Height-Correlated作为G项。Epic Games在2013年SIGGRAPH上的分享表明，这套组合相比原始Cook-Torrance公式在实时渲染中能减少约40%的视觉误差，同时保持实时可计算性。

Unity的HDRP也采用同样的D-F-G分解，但将G项拆分为 $G = G_1(\mathbf{l}) \cdot G_1(\mathbf{v})$（Smith分解），使得遮蔽与阴影两个效果可以独立计算。在离线渲染器（如Arnold、RenderMan）中，Cook-Torrance模型被直接用于路径追踪的重要性采样，采样分布正比于 $D(\mathbf{h}) \cos\theta_h$，以降低渲染方差。

## 常见误区

**误区一：将粗糙度参数 $\alpha$ 与感知粗糙度直接等同。** 在Disney PBR工作流中，美术师使用的roughness滑条值 $r$ 与实际输入D项的 $\alpha$ 是平方关系：$\alpha = r^2$。这种重映射是为了让粗糙度在视觉上呈线性分布，直接将滑条值代入Beckmann或GGX公式会导致粗糙度低端区域高光过于尖锐。

**误区二：认为Cook-Torrance模型是完整的BRDF。** Cook-Torrance公式仅描述镜面反射（specular lobe）部分，完整的PBR材质BRDF还需要加上漫反射项 $f_{diffuse}$，通常写作：$f = f_{diffuse} + f_{specular}$，且漫反射项通过 $(1 - F)$ 进行能量守恒修正，即非金属材质未被反射的光才进入漫反射。

**误区三：G项可以随意省略或用常数1代替。** 在掠射角（$\mathbf{n} \cdot \mathbf{l}$ 或 $\mathbf{n} \cdot \mathbf{v}$ 接近0）时，分母趋近于0，若没有G项的压制，Cook-Torrance公式的值将趋向无穷大，产生严重的高光爆炸（specular blowout）。G项与分母的趋零速度相互抵消，保证了最终结果的有界性。

## 知识关联

学习Cook-Torrance模型需要先掌握BRDF的基本定义——即辐亮度与辐照度之比 $f_r = dL_o / dE_i$，以及能量守恒（反射率积分不超过1）的基本约束，否则无法理解D-F-G各项为何必须存在。

在此基础上，三个子项各自演化为独立的研究方向：法线分布函数方向发展出GGX、Ashikhmin-Shirley各向异性分布等变体；菲涅尔效应连接到薄膜干涉和彩虹色材质的模拟；几何遮蔽项则通向多重散射微表面模型（如Heitz等人2016年提出的将微表面间多次弹射纳入计算的方法）。Cook-Torrance的镜面层结构也直接支撑了清漆层（Clearcoat）材质的实现——清漆层本质上是在基础Cook-Torrance层之上叠加一个低粗糙度、固定 $F_0=0.04$ 的额外Cook-Torrance高光层。