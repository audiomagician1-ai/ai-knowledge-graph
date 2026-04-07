# 金属度工作流

## 概述

金属度工作流（Metallic-Roughness Workflow）是由迪士尼研究院的Brent Burley在2012年SIGGRAPH大会上发布的"迪士尼原则BRDF"（Disney Principled BRDF）中系统推广的一套PBR材质参数化方案。该方案随后被Epic Games的Unreal Engine 4（2012年发布，2014年引擎开源）、Unity的Standard Shader（Unity 5.0，2015年3月正式发布）以及Khronos Group制定的glTF 2.0标准（2017年6月正式发布）所采用，成为实时渲染领域最主流的工作流之一。

其核心思想是用两张（或三张）贴图——基础色（BaseColor）、金属度（Metallic）、粗糙度（Roughness）——来区分金属与非金属材质的渲染行为，并让美术人员无需手动输入折射率（IOR）等物理参数即可获得物理正确的结果。之所以称为"金属度工作流"，是因为它用一个0到1的灰度值来描述材质在金属与绝缘体（非金属）之间的过渡：0代表纯绝缘体，1代表纯金属，中间值通常只用于锈迹、氧化层等混合区域。这种设计大幅降低了美术制作的认知门槛，但要求制作者必须理解参数的物理含义才能避免错误。

从历史背景来看，在金属度工作流普及之前，游戏行业大多沿用Phong或Blinn-Phong着色模型，美术人员通过手工调节高光强度（Specular Power）和高光颜色来模拟材质差异，不同引擎之间参数不通用且缺乏物理依据。迪士尼BRDF的发布，以及随后Epic Games在2013年GDC上展示的"Infiltrator"实时Demo，加速了行业从经验型着色向基于物理的着色的整体迁移，金属度工作流也在这一背景下确立了其行业标准地位。另一个重要里程碑是Allegorithmic公司（现Adobe旗下）于2014年推出的Substance Painter，该工具将金属度工作流内置为默认工作模式，进一步推动了其在影视、游戏和建筑可视化行业的普及。

## 核心原理

### BaseColor贴图的双重语义

在金属度工作流中，BaseColor贴图存储的含义随金属度值的不同而改变：当Metallic=0时，BaseColor代表漫反射反照率（Albedo），即材质的漫射颜色，数值应在sRGB空间下保持在50–240范围（约0.04–1.0线性空间），不应包含光照或AO信息；当Metallic=1时，BaseColor代表金属的F0镜面反射率，即在0度入射角时的反射颜色。以下为常见金属F0参考数值（线性空间RGB），数据来源于Burley（2012）及后续测量研究：

- 铜（Copper）：约 $(0.955,\ 0.638,\ 0.538)$
- 金（Gold）：约 $(1.000,\ 0.766,\ 0.336)$
- 铁（Iron）：约 $(0.560,\ 0.570,\ 0.580)$
- 铝（Aluminum）：约 $(0.913,\ 0.922,\ 0.924)$
- 银（Silver）：约 $(0.972,\ 0.960,\ 0.915)$
- 钛（Titanium）：约 $(0.542,\ 0.497,\ 0.449)$

这种双重语义是金属度工作流与高光工作流（Specular-Glossiness Workflow）最本质的差异——同一张贴图在不同材质区域扮演不同角色。对美术制作人员而言，这意味着在制作金属材质时，BaseColor的颜色选取直接决定了高光颜色，必须参照物理测量值；而在制作非金属材质时，BaseColor才是真正意义上的"颜色贴图"。

值得注意的是，绝缘体（非金属）的BaseColor亮度有严格的物理上下限：线性空间中，最暗的自然材质（如煤炭）约为0.02，最亮的白色物体（如新鲜白雪）约为0.9。超出此范围的BaseColor值通常意味着贴图中混入了光照信息，应当通过"Albedo校验工具"（UE5内置的Validation功能或Marmoset Toolbag 4的PBR Calibration Filter）进行检测。高动态范围HDR贴图除外，此时0.9以上的值可能代表自发光材质，需要配合Emissive通道单独处理。

### 金属度参数的物理意义

金属度（Metallic）参数控制渲染器如何分配漫反射分量与镜面反射分量。对于Metallic=0的绝缘体，渲染器使用BaseColor作为漫反射颜色，同时使用固定的 $F_0 \approx 0.04$（对应折射率约为1.5，覆盖大多数塑料、石材、木材）计算菲涅尔反射；对于Metallic=1的金属，渲染器将漫反射分量归零（金属不存在次表面漫射现象，自由电子会吸收并立即以镜面方式重新辐射光能），完全使用BaseColor作为彩色F0计算镜面高光。

这一物理区别源于材质的能带结构：金属中大量自由电子的存在使得光子在进入材质后被几乎完全吸收，折射光无法传播，因此没有漫射出射；而绝缘体内部的电子束缚于原子轨道，入射光子可以在次表面散射后重新出射，形成漫反射。Burley（2012）正是基于这一物理机制，将Metallic设计为在两种极端物理状态之间进行插值的控制参数。

菲涅尔反射率的近似计算采用Schlick公式（Christophe Schlick，1994年在《Computer Graphics Forum》第13卷第3期发表）：

$$F(\theta) = F_0 + (1 - F_0)(1 - \cos\theta)^5$$

其中 $\theta$ 为入射光线与表面法线的夹角，$F_0$ 为0度入射角时的反射率。对于绝缘体，$F_0 \approx 0.04$；对于金属，$F_0$ 由BaseColor直接提供。Schlick公式相较于精确的Fresnel方程（需要同时知道折射率的实部与虚部）在计算效率上有显著优势，误差在大多数入射角范围内低于0.5%，因此被主流实时渲染管线广泛采用。

在实际工作流中，一些引擎（如UE5的Substrate材质框架，2023年随UE5.3正式发布）已经开始引入更细粒度的电介质F0控制，允许美术人员为高折射率材质（如钻石IOR=2.42、玻璃IOR=1.5到1.9之间的品种）指定精确的F0值而非固定0.04，这是对经典金属度工作流的一次重要扩展。对于有此需求的项目，可以通过以下公式将折射率IOR转换为F0标量值：

$$F_0 = \left(\frac{n - 1}{n + 1}\right)^2$$

例如，玻璃的典型折射率 $n=1.5$ 代入公式得 $F_0 = (0.5/2.5)^2 = 0.04$，恰好与绝缘体默认值吻合；而钻石 $n=2.42$ 则得 $F_0 \approx 0.172$，与常见的0.04差距显著，需要单独指定。

### 粗糙度参数与微表面模型

粗糙度（Roughness）直接映射到Cook-Torrance微表面BRDF中的 $\alpha$ 参数（Cook & Torrance，1982年提出微表面框架，由Burley等人在2012年重新参数化推广）。UE4采用平方映射以使感知线性化，即：

$$\alpha = \text{Roughness}^2$$

NDF（法线分布函数，Normal Distribution Function）常用GGX/Trowbridge-Reitz模型（Walter等人，2007年在EGSR会议上正式引入图形学渲染领域），其公式为：

$$D(\mathbf{h}) = \frac{\alpha^2}{\pi \cdot \left[(\mathbf{n} \cdot \mathbf{h})^2(\alpha^2 - 1) + 1\right]^2}$$

其中 $\mathbf{h}$ 为半向量（Half Vector，即入射方向与出射方向的角平分线方向），$\mathbf{n}$ 为表面法线，$\alpha$ 为经过平方映射后的粗糙度。Roughness=0时表面为完美镜面，Roughness=1时高光完全扩散。

GGX模型相较于之前广泛使用的Beckmann NDF（1963年提出），最关键的改进在于其"长尾"特性：GGX在高角度时法线分布衰减更慢，这使得材质高光边缘产生更自然的光晕渐变，而非Beckmann模型下生硬的截断效果。这一特性在抛光金属、湿润表面等材质上的表现尤为明显，也是现代渲染引擎几乎全面迁移至GGX的核心原因。

一张8位灰度的Roughness贴图即可描述从抛光金属（0.0–0.1）到粗糙混凝土（0.8–0.95）的全范围变化。结合 $\alpha = \text{Roughness}^2$ 的平方映射，Roughness=0.1对应 $\alpha=0.01$（极光滑），Roughness=0.5对应 $\alpha=0.25$（中等粗糙），感知上的线性分布使得美术调节具有良好的直觉性，这也是Karis（2013）在UE4实现文档中特别强调选用此映射的原因。

### 几何遮蔽函数与完整渲染方程

完整的Cook-Torrance BRDF不仅包含NDF项，还包含几何遮蔽函数（Geometry Function）$G$ 和菲涅尔项 $F$：

$$f_r(\mathbf{v}, \mathbf{l}) = \frac{D(\mathbf{h}) \cdot F(\mathbf{v}, \mathbf{h}) \cdot G(\mathbf{v}, \mathbf{l}, \mathbf{h})}{4(\mathbf{n} \cdot \mathbf{v})(\mathbf{n} \cdot \mathbf{l})}$$

其中 $\mathbf{v}$ 为视线方向，$\mathbf{l}$ 为光线方向，分母中的 $4(\mathbf{n} \cdot \mathbf{v})(\mathbf{n} \cdot \mathbf{l})$ 为归一化因子，确保BRDF在能量上的守恒性。UE4使用Schlick-GGX近似的Smith几何函数：

$$G_{\text{Schlick-GGX}}(\mathbf{n}, \mathbf{v}, k) = \frac{\mathbf{n} \cdot \mathbf{v}}{(\mathbf{n} \cdot \mathbf{v})(1-k) + k}, \quad k = \frac{(\text{Roughness}+1)^2}{8}$$

其中 $k$ 的计算方式针对直接光照进行了优化；在IBL（Image-Based Lighting）环境光照情形下，$k$ 改写为 $k_{\text{IBL}} = \text{Roughness}^2 / 2$，以减少在粗糙材质上的过暗偏差。完整的Smith几何函数同时考虑视线方向遮蔽（Shadowing）和光线方向遮蔽（Masking），实际使用 $G = G_1(\mathbf{v}) \cdot G_1(\mathbf{l})$ 的乘积形式。

理解这一完整公式有助于解释为什么在掠射角（Grazing Angle）处即使是纯黑色非金属也会产生明亮的白色高光——这是Schlick菲涅尔公式中 $(1-\cos\theta)^5$ 在 $\theta \to 90°$ 时趋近于1的物理必然结果，而非渲染器的错误。正因如此，在暗场景下观察磨砂塑料球，边缘仍会出现清晰的菲涅尔光环，这是物理正确渲染的标志之一。

## 关键公式汇总与参数映射

金属度工作流中各参数对渲染方程的映射关系可以整理如下：

| 参数 | 范围 | 映射到BRDF中的角色 | 典型物理值 |
|------|------|-------------------|-----------|
| BaseColor（绝缘体）| 线性0.02–0.9 |