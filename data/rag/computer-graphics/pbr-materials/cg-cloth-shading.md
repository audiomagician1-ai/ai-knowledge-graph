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

布料着色是物理渲染（PBR）体系中专门针对织物材质的光照计算方法。普通金属或电介质的BRDF以光滑或粗糙的微表面（microfacet）模型为基础，但织物的微观结构是互相缠绕的纤维，而非随机分布的微小镜面。这一本质差异导致棉、丝绸、天鹅绒等面料在现实中呈现出前向散射（forward scattering）和边缘光晕（rim/fringe lighting）两大视觉特征，标准GGX或Beckmann分布无法再现这些效果。

布料BRDF的研究可追溯至1994年Westin等人对编织结构的光学测量，但工程上可实用的解析模型要等到2000年Ashikhmin等人发布各向异性BRDF框架之后才陆续出现。2012年Eric Heitz与Fabrice Neyret在分析天鹅绒时进一步指出，纤维表面的法线分布与传统半球不同，需用倒置的高斯或正弦函数来近似。游戏行业普遍采用的Charlie模型（以Google Filament项目中的实现名称著称）正是在这一基础上简化而来的实时可用版本。

理解布料着色的意义在于：当场景中出现厚重羊毛外套、天鹅绒沙发或丝质礼服时，若仍使用通用PBR着色器，布料表面会显得像塑料或橡胶，失去纤维应有的柔软光泽。正确的布料BRDF能使面料在逆光条件下呈现发光的绒毛轮廓，在正面光照下表现出低饱和度的漫反射，从而还原真实织物的视觉质感。

---

## 核心原理

### Ashikhmin漫反射模型

Ashikhmin-Premoze（2007）针对布料提出了一个修正的朗伯漫反射项，其核心公式为：

$$f_d = \frac{\rho_{ss}}{π} \left(1 - V_1(\mathbf{n}\cdot\mathbf{l})\right)\left(1 - V_1(\mathbf{n}\cdot\mathbf{v})\right)$$

其中 $V_1(\cos\theta) = \left(1 - (1-\cos\theta)^5\right)$ 是基于Schlick近似的单次散射遮挡项，$\rho_{ss}$ 是次表面散射颜色。与Lambertian漫射不同，该公式在掠射角（grazing angle）处刻意降低散射亮度，因为纤维在此角度下更多地产生镜面前向散射而非均匀漫射，从而避免了织物边缘过亮的错误表现。

### Charlie镜面反射与正弦分布NDF

Charlie模型的法线分布函数（NDF）采用的是正弦幂函数形式：

$$D_{Charlie}(\theta_h) = \frac{(2 + \frac{1}{\alpha^2})\sin^{1/\alpha^2}(\theta_h)}{2\pi}$$

其中 $\theta_h$ 是半角向量与法线的夹角，$\alpha$ 是粗糙度参数（取值0到1）。当 $\alpha$ 趋近于1时，NDF在 $\theta_h = 90°$ 附近（即掠射方向）取到极大值，这正好描述了纤维几乎垂直于织物表面站立时的光散射集中区域。相比之下，GGX的NDF在 $\theta_h = 0$ 处（法线正前方）最强，二者的峰值位置恰好相反。

### 遮蔽-阴影函数的选择

在传统微表面理论中，Smith遮蔽函数假设微面元之间相互独立，但纤维的相互缠绕使遮蔽关系更为复杂。Charlie模型通常直接使用一个基于可见性的近似项：

$$V_{Charlie} = \frac{1}{4(\mathbf{n}\cdot\mathbf{l} + \mathbf{n}\cdot\mathbf{v} - (\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v}))}$$

这一表达式由Neubelt和Pettineo（2013）在《Crafting a Next-Gen Material Pipeline》中提出，它放弃了Smith分离假设，改为以几何平均的方式同时压低入射和反射两侧的极端亮度。Google Filament在实现时沿用了这个可见性项，并将整体镜面反射项命名为"Charlie Sheen"，因为该参数特别适合表现天鹅绒（velvet）的丝绒光泽。

### 双层模型结构

实际渲染中，布料材质往往被分为两层：底层是Ashikhmin漫反射，描述织物基色的均匀散射；顶层是Charlie镜面反射，描述纤维尖端的掠射高光。两层通过一个称为"Sheen"（光泽）的独立颜色参数混合，允许美术人员单独控制轮廓光的色调，例如天鹅绒的红色光晕或丝绸的蓝白色泽，而不影响面料本体颜色。

---

## 实际应用

**天鹅绒（Velvet）**：天鹅绒是布料BRDF最典型的测试用例。其纤维几乎垂直于底层织物，使Charlie NDF的掠射峰值效果最为显著。在Unreal Engine 5的布料着色器中，将Sheen颜色设置为偏暖的橙红色，Roughness设为0.6–0.8，即可再现深色天鹅绒在侧光下的绒毛光晕，这一现象在纯黑天鹅绒上尤为明显，边缘会呈现出一圈有色光晕而非白色高光。

**牛仔布与棉麻**：棉麻纤维较短且卷曲，Sheen强度相对较低，但Ashikhmin漫反射项会在布料拉伸区域（如膝盖、肘部）产生细微亮度变化。在Unity HDRP的Fabric材质类型中，将Thread Map（纱线法线贴图）与布料BRDF结合，可以在无额外光线追踪的情况下还原牛仔布的横纹织造结构。

**丝绸（Silk）**：丝绸兼具各向异性（anisotropy）和布料光泽，通常需要在Charlie模型基础上叠加一个细丝各向异性镜面项（类似Kajiya-Kay发丝模型的切线方向散射），以表现丝绸在不同角度下颜色变化的"shot silk"效应。

---

## 常见误区

**误区一：用高光贴图代替布料BRDF**
部分美术人员试图通过提高GGX材质的粗糙度值并叠加发光贴图来模拟天鹅绒轮廓光。这种方法将轮廓光烘焙进静态贴图，在动态光照环境下轮廓光方向固定不变，无法随光源移动而变化。正确的Charlie模型是基于实时光向量和视角向量计算的，掠射高光会随观察者移动而动态偏移。

**误区二：布料不需要Fresnel项**
有观点认为，纤维材质应完全去掉Fresnel反射（因为织物不像金属有自由电子）。实际上，单根纤维本身是介电质，其折射率约为1.5（棉纤维）到1.56（蚕丝），Fresnel效应确实存在，只是掠射集中的几何效应远强于Fresnel贡献，因此有时被省略，但并非不存在。Charlie Sheen的实现中通常在掠射区域保留一个简化的Fresnel缩放因子。

**误区三：布料BRDF适用于所有织物**
布料BRDF的掠射峰值假设纤维是向上竖立的。对于编织紧密、纤维平躺的缎面（satin），其高光分布更接近经典各向异性微表面，使用Charlie模型反而会使缎面看起来过于"绒感"。缎面应使用Kajiya-Kay或Ward各向异性模型，而天鹅绒、粗纺毛料才是Charlie BRDF的适用对象。

---

## 知识关联

布料着色建立在BRDF基础之上：理解 $f_r(\mathbf{l}, \mathbf{v}) = \frac{D \cdot F \cdot G}{4(\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v})}$ 的DFG三项分解是分析Charlie模型对各项的修改方式的前提。Charlie模型具体改动了D项（正弦NDF代替GGX）和G项（Neubelt可见性代替Smith），而F项（Fresnel）则按材质需求简化或保留。

在材质系统层面，布料着色与毛发渲染（Hair Shading，使用Marschner或d'Eon模型）共享"纤维状微观结构"这一根本出发点。两者都放弃了微平面假设，转而用单根纤维的散射截面来推导BRDF。如果需要实现皮草（fur）或毯子（carpet）等介于布料和毛发之间的材质，可以将Charlie的NDF与Kajiya-Kay的切线分布混合插值，同时控制纤维长度与覆盖密度参数来平滑过渡。