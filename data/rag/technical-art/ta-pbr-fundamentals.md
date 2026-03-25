---
id: "ta-pbr-fundamentals"
concept: "PBR材质基础"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# PBR材质基础

## 概述

PBR（Physically Based Rendering，基于物理的渲染）是一套以现实世界光照物理规律为依据的材质描述体系，其核心目标是让同一套材质参数在任意光照环境下都能产生物理上可信的渲染结果。与传统的Phong或Blinn-Phong光照模型不同，PBR将材质的光学特性抽象为可量化的物理属性，而非依赖美术的经验性调整。

PBR工作流在游戏工业中的广泛普及始于2012年前后，迪士尼研究院发布的"Disney Principled BRDF"论文奠定了实时PBR的理论基础。Epic Games随后在虚幻引擎4（2014年）中将金属度/粗糙度（Metallic/Roughness）工作流正式引入实时渲染管线，成为当前游戏和影视行业最主流的PBR规范。

PBR之所以重要，在于它打破了"为特定灯光调材质"的低效工作模式。一套正确制作的PBR材质放入日光场景与夜晚场景，其金属光泽、漫反射强度和菲涅尔效果都会自动符合物理预期，极大降低了跨场景材质的维护成本。

---

## 核心原理

### 能量守恒与BRDF

PBR的物理基础是能量守恒定律：材质反射的总光能不能超过接收的入射光能。实现这一约束的数学工具是**BRDF**（双向反射分布函数，Bidirectional Reflectance Distribution Function），其公式为：

$$f_r(\omega_i, \omega_o) = \frac{dL_o(\omega_o)}{dE_i(\omega_i)}$$

其中 $\omega_i$ 为入射光方向，$\omega_o$ 为出射（观察）方向，$L_o$ 为出射辐射率，$E_i$ 为入射辐照度。在片元着色器中，Cook-Torrance BRDF将高光反射拆解为法线分布函数（NDF）、几何遮蔽函数（G）和菲涅尔方程（F）三项之积，除以归一化因子 $4(\mathbf{n} \cdot \omega_i)(\mathbf{n} \cdot \omega_o)$。

### 金属度通道（Metallic）

金属度是一个0到1的标量通道，它在物理上区分了**导体**（金属）和**绝缘体**（非金属）两类材料的光学行为差异。绝缘体的F0（垂直入射时的菲涅尔反射率）通常在0.02到0.05之间（对应折射率1.5左右的常见非金属），而金属的F0直接由其BaseColor（基础颜色）决定，且金属几乎不产生漫反射。因此当Metallic=1时，着色器会将漫反射贡献归零，将BaseColor直接作为镜面反射色使用。现实中很少存在纯粹的半金属状态，所以金属度贴图在实践中通常只含有0或1的纯黑/纯白值，过渡灰度仅用于生锈、氧化等混合表面区域。

### 粗糙度通道（Roughness）

粗糙度（0=完全光滑，1=完全粗糙）控制微表面（Microfacet）法线分布的集中程度，直接影响高光的大小与锐度。在UE5的默认着色模型中，粗糙度值会被平方后传入GGX法线分布函数，即实际的 $\alpha = \text{Roughness}^2$，这样做的目的是让粗糙度在感知上呈线性变化。粗糙度为0.1时产生极小且亮的尖锐高光，粗糙度为0.8时高光扩散成大范围漫射，这与磨砂金属或混凝土表面的视觉特征吻合。Unity的HDRP管线中等效参数被称为Smoothness，其值与Roughness互为补集：Smoothness = 1 − Roughness。

### 法线贴图通道（Normal）

法线贴图以切线空间（Tangent Space）存储每个像素的微观法线偏移，RGB三通道分别对应切线方向X、副切线方向Y和法线方向Z的偏移量。标准切线空间法线贴图的Z通道（蓝色分量）始终为正，静止表面的默认值编码为(0.5, 0.5, 1.0)，对应无偏移状态。片元着色器通过TBN矩阵（Tangent-Bitangent-Normal matrix）将切线空间法线转换到世界空间或观察空间，再用于光照计算。注意DirectX（DX）坐标系与OpenGL坐标系在Y轴方向相反，在Substance Painter中导出时需要根据目标引擎选择"DirectX Normal"或"OpenGL Normal"，混用会导致表面凹凸方向全部反转。

### AO通道（环境光遮蔽）

AO（Ambient Occlusion）贴图存储的是烘焙阶段预计算的静态遮蔽信息，取值范围0到1，其中0表示完全遮蔽（裂缝、内凹角），1表示完全开阔。在着色器中，AO仅作用于**间接光照**（环境光/IBL贡献）部分，不应与直接光照相乘，否则会造成物理不正确的阴影。在UE5中AO贴图通过乘以间接漫反射项实现：`IndirectDiffuse *= AO`，同时还会影响间接高光的Specular Occlusion计算。

---

## 实际应用

**金属武器材质制作**：一把钢制剑刃的Metallic值设为1.0，BaseColor设为偏冷的浅灰（约#B0B0B0），Roughness设为0.15（锻造抛光面）到0.4（刃口磨损区）的渐变，法线贴图叠加微细划痕以增加表面细节。手柄皮革部分Metallic=0，BaseColor为棕色，Roughness约0.7。两种材质可通过Mask贴图在同一材质实例中区分，这是PBR多材质层混合的标准做法。

**建筑混凝土材质**：混凝土的F0约为0.04，Metallic恒定为0，BaseColor为中灰色（#787878附近），Roughness在0.85至0.95之间，高Roughness导致高光几乎不可见，视觉上完全以漫反射为主。AO贴图在砖缝和内凹处应有明显黑色遮蔽，突出结构感。

**汽车车漆（Clear Coat材质）**：车漆是PBR双层材质的典型案例，UE5的Clear Coat着色模型专门处理这种场景：底层是有颜色的金属漆（Metallic=0.8，Roughness=0.6），上层是透明清漆（Roughness=0.05），两层的高光叠加产生奢华的多层反射效果。

---

## 常见误区

**误区一：BaseColor可以含有光照信息**
传统手绘贴图习惯在Albedo中烘入高光和阴影，但PBR的BaseColor通道只应存储材质的固有色（Albedo），不能包含任何光影信息。将烘焙好AO或高光的手绘图直接作为BaseColor使用，会造成光照计算双重叠加，在强方向光下表面会出现不自然的预烘焙阴影残影。

**误区二：金属度可以随意使用0~1的中间值**
部分初学者将金属度用作"金属感强弱"的调节旋钮，在0.3~0.7范围内大量使用中间值。物理上，绝大多数真实材料非导体即绝缘体，金属度中间值只在锈迹（铁锈本身是绝缘体，但与底层金属共存）、脏污金属等极有限的表面过渡场合才合理。滥用中间值会导致材质在IBL环境中出现物理上无法解释的漫反射与镜面反射混合比例。

**误区三：粗糙度为0等于完美镜面**
Roughness=0在实时渲染中确实趋近镜面，但受制于Mipmap级别和IBL的立方体贴图分辨率（通常最高512×512），极低粗糙度下高光采样仍有精度损失。更重要的是，现实中几乎没有宏观物体具备光学级别的完美光滑度（Roughness<0.05的值在非光学器件表面几乎不存在），过低的粗糙度值会让材质看起来像塑料玩具而非真实金属。

---

## 知识关联

**前置知识**：片元着色器编写是理解PBR的直接基础——PBR材质的金属度、粗糙度等参数最终都以`uniform sampler2D`的形式传入片元着色器，在`gl_FragColor`或`outColor`的计算中被Cook-Torrance BRDF方程消费。不理解Fragment Shader的输入输出机制，就无法定制或调试PBR光照计算。

**后续知识**：掌握各通道的物理含义后，**材质分层**技术允许通过混合权重贴图将多套PBR参数集叠加（如地面泥土与石块的混合），**纹理通道打包**技术（如UE的ORM贴图将AO、Roughness、Metallic分别打包进R、G、B通道）则在此基础上优化显存占用。**Substance工作流**以PBR通道体系为输出目标，Substance Painter