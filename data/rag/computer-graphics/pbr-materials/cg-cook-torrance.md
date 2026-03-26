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
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.424
last_scored: "2026-03-22"
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

Cook-Torrance模型是由Robert Cook和Kenneth Torrance于1982年在论文《A Reflectance Model for Computer Graphics》中提出的微表面双向反射分布函数（BRDF）。该模型将宏观表面建模为由无数微小完美镜面（microfacets）组成的集合，每个微面的法线方向不同，整体表面的反射特性由这些微面法线的统计分布决定。这一思想直接来源于光学和热辐射领域的物理测量数据，是首个将物理光学引入实时渲染的工业级模型。

Cook-Torrance在发表时解决了Phong模型无法表达金属质感和掠射角高光拉伸等问题。它不依赖经验调参，而是将材质属性分解为可测量的物理量，因此成为现代PBR（基于物理的渲染）工作流的理论基础，被Unreal Engine 4、Unity HDRP等主流引擎直接采用。

## 核心原理

### 完整公式结构

Cook-Torrance镜面反射BRDF的完整形式为：

$$f_r = \frac{D(\mathbf{h}) \cdot F(\mathbf{v}, \mathbf{h}) \cdot G(\mathbf{l}, \mathbf{v}, \mathbf{h})}{4(\mathbf{n} \cdot \mathbf{l})(\mathbf{n} \cdot \mathbf{v})}$$

其中 $\mathbf{h}$ 是半程向量（halfway vector），$\mathbf{l}$ 是光源方向，$\mathbf{v}$ 是视线方向，$\mathbf{n}$ 是宏观法线。分母中的 $4(\mathbf{n} \cdot \mathbf{l})(\mathbf{n} \cdot \mathbf{v})$ 是将微面几何转换到宏观表面积时产生的雅可比修正项，并非经验值。

### D项：法线分布函数（NDF）

D项（Normal Distribution Function）描述了微面法线朝向半程向量 $\mathbf{h}$ 方向的统计概率密度。Cook-Torrance原论文使用Beckmann分布，但现代引擎普遍改用Trowbridge-Reitz GGX分布：

$$D_{GGX}(\mathbf{h}) = \frac{\alpha^2}{\pi\left[(\mathbf{n} \cdot \mathbf{h})^2(\alpha^2 - 1) + 1\right]^2}$$

其中 $\alpha = roughness^2$（粗糙度的平方映射）。GGX相比Beckmann拥有更长的"尾部"，能再现金属表面边缘的光晕扩散，这一差异在掠射角下尤为明显。D项必须满足归一化条件：$\int_\Omega D(\mathbf{h})(\mathbf{n} \cdot \mathbf{h})d\omega_h = 1$。

### F项：菲涅尔方程近似

F项（Fresnel Term）描述光在微面界面处反射与折射的能量分配比例，依赖于视角与法线夹角。Cook-Torrance中常用Schlick近似（1994年由Christophe Schlick提出）：

$$F(\mathbf{v}, \mathbf{h}) = F_0 + (1 - F_0)(1 - \mathbf{v} \cdot \mathbf{h})^5$$

$F_0$ 是垂直入射时的基础反射率，对于非金属材质通常在0.02–0.05之间，对于铜等金属则高达0.95以上且带有色彩偏移。当视线与半程向量夹角趋近90°时，任何材质反射率都趋向1.0，这正是"菲涅尔边缘发光"效果的物理来源。

### G项：几何遮蔽/阴影函数

G项（Geometry Function）统计了因微面之间相互遮挡导致的能量损失，分为"阴影"（shadowing，光线被遮挡）和"遮蔽"（masking，反射光被遮挡）两种情形。Smith分离近似将其拆解为：

$$G(\mathbf{l}, \mathbf{v}) = G_1(\mathbf{l}) \cdot G_1(\mathbf{v})$$

每个 $G_1$ 项通常采用Schlick-GGX形式：$G_1(\mathbf{x}) = \frac{\mathbf{n} \cdot \mathbf{x}}{(\mathbf{n} \cdot \mathbf{x})(1-k) + k}$，其中 $k = \alpha/2$（直接光照）或 $k = (\alpha+1)^2/8$（IBL环境光），粗糙度越高，G项损耗越大，防止了能量不守恒的过亮高光。

## 实际应用

在虚幻引擎4的材质系统中，Cook-Torrance被用于实现"金属度-粗糙度"工作流。美术师设置 Metallic=1.0 时，$F_0$ 直接从BaseColor中读取（彩色反射率）；Metallic=0.0 时，$F_0$ 固定为0.04，BaseColor转为漫反射颜色。这种两分法直接建立在Cook-Torrance的F项物理含义上。

在离线渲染（如Arnold、RenderMan）中，Cook-Torrance通常与多散射微面模型（Multi-scattering BRDF）配合，修正当粗糙度>0.5时能量因G项过度衰减而产生的暗化问题，代表性工作为Heitz等人2016年的"Multiple-Scattering Microfacet BSDFs"。

游戏《荒野大镖客：救赎2》的材质系统通过在Cook-Torrance基础上叠加各向异性NDF（拉伸 $\alpha$ 为椭圆形），还原了皮革纤维和马毛的定向高光效果，这是标准各向同性Cook-Torrance无法实现的。

## 常见误区

**误区一：认为Cook-Torrance天然满足能量守恒**
标准单散射Cook-Torrance实际上不满足能量守恒。当粗糙度增大时，G项会吸收大量能量，但这些能量在现实中应通过微面间多次弹射重新射出。因此粗糙金属球在标准Cook-Torrance下会比真实情况更暗，必须叠加能量补偿项才能物理正确。

**误区二：D项等于高光强度**
D项只是描述微面法线分布的概率密度函数，它可以在某些方向取大于1的值（因为是密度而非概率）。高光的最终亮度是D、F、G三项与分母共同决定的结果，单独调大D项（即降低粗糙度）同时也会因G项变化而改变高光形状。

**误区三：半程向量与法线在任何情况下都可互换**
Cook-Torrance的所有三项都依赖半程向量 $\mathbf{h} = \text{normalize}(\mathbf{l} + \mathbf{v})$，而非宏观表面法线 $\mathbf{n}$。将 $\mathbf{h}$ 替换为 $\mathbf{n}$ 会使模型退化为各向同性Phong反射，失去微表面的物理意义，典型错误出现在初学者手写shader时误用 $(\mathbf{n} \cdot \mathbf{l})$ 代替 $(\mathbf{n} \cdot \mathbf{h})$ 计算D项。

## 知识关联

学习Cook-Torrance需要先掌握BRDF的基本定义（辐射率比辐照度）和Helmholtz互易性原则，这两条性质可以验证Cook-Torrance公式在交换 $\mathbf{l}$ 与 $\mathbf{v}$ 后保持对称。

向上延伸时，D项引出法线分布函数（NDF）的完整理论，包括各向异性GGX与Beckmann之间的差异选择；F项直接连接到菲涅尔效应在导体与电介质中的不同物理机制；G项则展开为Smith联合遮蔽阴影函数的推导细节。

在更复杂的材质建模中，Cook-Torrance作为单层镜面高光层嵌入清漆层（Clearcoat）模型——清漆层实质上是在标准Cook-Torrance基础上叠加第二个低粗糙度、固定 $F_0=0.04$ 的Cook-Torrance镜面瓣。而次表面散射处理的是透射进入材质内部的那部分光，即1减去F项之后的折射份额，两者合并才构成完整的皮肤、蜡烛等半透明材质BSDF。