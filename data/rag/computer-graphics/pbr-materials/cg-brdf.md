---
id: "cg-brdf"
concept: "BRDF基础"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# BRDF基础

## 概述

BRDF（Bidirectional Reflectance Distribution Function，双向反射分布函数）由Fred Nicodemus于1965年在美国国家标准局的技术报告中正式定义，是描述不透明表面如何将入射光反射到各个方向的数学函数。它的"双向"特性体现在同时需要指定入射方向和出射方向，缺少任意一个方向信息都无法确定反射量。

从数学角度，BRDF定义为出射辐射率（Radiance）与入射辐照度（Irradiance）之比：

$$f_r(\omega_i, \omega_o) = \frac{dL_o(\omega_o)}{dE_i(\omega_i)} = \frac{dL_o(\omega_o)}{L_i(\omega_i)\cos\theta_i \, d\omega_i}$$

其中 $\omega_i$ 是入射方向，$\omega_o$ 是出射方向，$L_i$ 是入射辐射率，$\theta_i$ 是入射方向与表面法线的夹角，$\cos\theta_i$ 来源于Lambert余弦定律对投影面积的修正。BRDF的单位是 $\text{sr}^{-1}$（每球面度），这一单位常被初学者忽略却至关重要。

BRDF的重要性在于它是渲染方程的核心积分核。James Kajiya于1986年提出的渲染方程将场景中任意点的出射辐射率表达为对所有入射方向上BRDF与入射辐射率乘积的半球积分，物理正确渲染（PBR）的一切材质表现都依赖于为每种材质选用或拟合合适的BRDF模型。

## 核心原理

### 亥姆霍兹互反性（Helmholtz Reciprocity）

BRDF必须满足亥姆霍兹互反性，即交换入射方向与出射方向后函数值不变：

$$f_r(\omega_i, \omega_o) = f_r(\omega_o, \omega_i)$$

这一性质源于光在微观尺度上的时间可逆性。在路径追踪算法中，互反性允许光线从相机出发逆向追踪，其物理正确性正由此性质保证。违反互反性的BRDF（如某些早期游戏引擎使用的经验模型）会导致从不同角度观察同一材质时出现能量不一致的视觉瑕疵。

### 能量守恒

BRDF必须满足能量守恒约束：对任意入射方向，出射辐射率的半球积分不得超过入射辐照度，用数学表达为半球反射率（Hemispherical-Directional Reflectance）须满足：

$$\rho(\omega_i) = \int_{\Omega} f_r(\omega_i, \omega_o) \cos\theta_o \, d\omega_o \leq 1$$

当 $\rho(\omega_i) = 1$ 时表示完全反射（无吸收），小于1则有能量被吸收转化为热能等。Blinn-Phong模型中若高光指数 $n$ 较小但高光强度系数未做归一化处理，$\rho$ 可轻易超过1，这是它不满足能量守恒的根本原因，也是PBR系统放弃直接使用它的关键依据。

### 各向同性与各向异性

当BRDF仅依赖入射和出射方向相对于法线的极角（$\theta_i, \theta_o$）以及两者方位角之差（$\Delta\phi = \phi_o - \phi_i$），而非各自的绝对方位角时，称为各向同性BRDF，参数维度从4维降至3维。拉丝金属、头发横截面等材质则需要各向异性BRDF，其高光拖尾方向与切线方向相关，需要完整的4个方向参数来描述。

### 参数化方式

在实际使用中，方向向量 $\omega$ 常被参数化为球坐标 $(\theta, \phi)$，但Cook-Torrance等微表面模型更多采用**半程向量（Half-vector）** $\mathbf{h} = \text{normalize}(\omega_i + \omega_o)$ 参数化，将BRDF从入射/出射对的函数转写为法线分布函数（NDF）对半程向量的响应，使各向异性材质的描述更直观，计算也更稳定。

## 实际应用

**Lambertian漫反射BRDF**是最简单的满足物理约束的BRDF，其表达式为 $f_r = \frac{\rho_d}{\pi}$，其中 $\rho_d \in [0,1]$ 是漫反射率（albedo）。除以 $\pi$ 是为了在半球积分后精确满足能量守恒，这一归一化系数在早期引擎代码中经常缺失，导致场景整体偏亮。

**测量BRDF数据库**是另一类重要应用。康奈尔大学MERL数据库（2003年由Matusik等人发布）包含100种真实材质的测量数据，以每种材质90×90×180个采样点（约145万个测量值）存储，每条数据文件约33MB。实时引擎通过对测量数据拟合分析模型（如Disney principled BRDF），将100余个采样维度压缩为5至10个艺术家友好的参数，如金属度（metallic）和粗糙度（roughness）。

在**预计算辐射传输（PBR贴图工作流）**中，Substance Painter等工具烘焙的roughness贴图实质上是对底层GGX NDF的宽度参数 $\alpha$ 的空间变化编码，而非直接存储BRDF值，理解这一层映射关系有助于避免贴图数值解读错误。

## 常见误区

**误区一：BRDF可以取负值或任意大值。**
BRDF的值域须满足非负性约束（$f_r \geq 0$），但其上界理论上无限制——镜面反射的BRDF在完美反射方向上趋近于狄拉克 $\delta$ 函数，值为正无穷大，同时被 $\cos\theta$ 和极小的立体角 $d\omega$ 抵消。初学者常因为看到渲染中高光区域"过曝"就认为BRDF违反了能量守恒，实际上能量守恒应通过上节的半球积分不等式来验证，而非直接比较函数值大小。

**误区二：BRDF描述所有表面光照现象。**
BRDF仅描述来自上半球的入射光反射回上半球的不透明表面行为。透射介质（玻璃、皮肤下层）需要BTDF（Bidirectional Transmittance Distribution Function），两者合并为BSDF（S代表Scattering）。皮肤、大理石等材质内部有光线在介质内横向传播后从不同位置出射，这种次表面散射现象既不属于BRDF也不属于BTDF，而需要BSSRDF（双向表面散射反射分布函数）来描述，其比BRDF多两个空间坐标参数。

**误区三：各向同性BRDF只有2个参数。**
各向同性BRDF依赖 $\theta_i$、$\theta_o$ 和相对方位角差 $\Delta\phi$ 共3个参数，减少的是从4维到3维而非到2维。有些教程混淆了"简化"的程度，导致学生误以为各向同性材质可以用一张2D查找表（LUT）精确表达，而实际上需要3D纹理或特殊参数化手段才能无损存储。

## 知识关联

学习BRDF基础需要熟悉PBR材质概述中引入的辐射度量学概念，特别是辐射率（Radiance）和辐照度（Irradiance）的区别——BRDF的定义式中分子分母分别对应这两个不同的物理量，混淆两者会导致渲染方程的积分被错误实现。

BRDF基础直接支撑后续多个方向的学习：Cook-Torrance模型将BRDF分解为菲涅耳项（F）、法线分布函数（D）和几何遮蔽函数（G）三个子项的乘积，是工业界最通用的镜面反射BRDF实现；Disney BRDF在Cook-Torrance框架上添加了清漆（clearcoat）和布料光泽（sheen）等经验参数，覆盖艺术家实际需求；布料着色和毛发着色则是将BRDF推广到纤维几何结构上的特化形式，其中布料常用基于散射体积的经验模型替代标准微表面BRDF；透射BRDF（BTDF）则将互反性和能量守恒的约束延伸到折射现象，需要引入斯涅尔定律对立体角的缩放修正。
