---
id: "ta-skin-material"
concept: "皮肤材质"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 皮肤材质

## 概述

皮肤材质是指在实时或离线渲染中，通过模拟皮肤的物理光学特性——包括次表面散射（Subsurface Scattering，SSS）、毛孔微表面结构和皮脂层高光——来还原真实皮肤外观的材质实现方案。皮肤不是一个简单的漫反射表面，光线在进入表皮后会在真皮层与皮下脂肪层之间经历多次散射，最终从入射点附近的不同位置射出，这一现象导致皮肤呈现出独特的半透明蜡质感。

皮肤渲染的学术研究可追溯到2001年Henrik Wann Jensen等人发表的论文《A Practical Model for Subsurface Light Transport》，该论文提出了用偶极子漫射近似（Dipole Diffusion Approximation）计算次表面散射的方法，奠定了此后20年皮肤渲染的理论基础。在实时渲染领域，2007年由Jorge Jimenez推广的预积分皮肤着色（Pre-Integrated Skin Shading）技术将SSS的计算复杂度降低到单Pass可接受的水平，使高质量皮肤渲染进入游戏引擎的实用阶段。

皮肤材质的重要性在于人眼对人脸极为敏感，即所谓"恐怖谷"效应：若人物皮肤缺少SSS导致表面过于"塑料感"，玩家或观众会立即察觉到不真实感，即便模型拓扑和贴图精度都很高也无法弥补。

## 核心原理

### 次表面散射的分层模型

真实皮肤由4层组成，从外至内依次为：角质层（约0.02mm）、表皮层（约0.1–0.2mm）、真皮层（约1–4mm）和皮下组织。光学上，角质层主要负责镜面反射，表皮层含有黑色素，真皮层含有血红素，两者分别控制肤色的黄褐调和红润调。实时渲染中通常将皮肤简化为两层BRDFf+BSSRDF模型：镜面层使用Kelemen-Szirmay-Kalos高光模型，漫反射层使用双极扩散剖面来近似SSS。

双极子扩散剖面的核心公式为：

$$R(r) = \frac{\alpha'}{4\pi} \left[ \frac{z_r(\sigma_{tr} + \frac{1}{d_r})e^{-\sigma_{tr}d_r}}{d_r^2} + \frac{z_v(\sigma_{tr} + \frac{1}{d_v})e^{-\sigma_{tr}d_v}}{d_v^2} \right]$$

其中 $r$ 为入射点到出射点的距离，$\sigma_{tr}$ 为有效传输系数，$z_r$ 和 $z_v$ 分别为真实光源和虚拟光源到表面的距离，$d_r$、$d_v$ 为对应距离。对RGB三个通道分别计算该剖面时，红色通道的散射半径最大（约10mm），绿色次之（约5mm），蓝色最小（约1.5mm），这正是皮肤在强光下呈现红润透光感的物理成因。

### 预积分皮肤着色

在实时管线中，逐像素计算完整BSSRDF代价极高。预积分皮肤着色将散射剖面的积分结果预先存入一张以 $(\mathbf{N}\cdot\mathbf{L}, 1/r)$ 为坐标轴的2D LUT贴图（通常分辨率为512×512），渲染时仅需采样该LUT。曲率半径 $r$ 的倒数 $1/r$ 在实际实现中由顶点法线与像素法线的差异（Curvature Map）近似计算：鼻尖、嘴角等高曲率区域散射更强，前额等平坦区域散射弱。Unity URP和Unreal Engine均内置了此类实现，UE的皮肤Shading Model名称为"Subsurface Profile"，其Profile资产直接存储散射剖面的RGB参数。

### 毛孔与皮脂层的高频细节

毛孔的还原依赖法线贴图与腔体贴图（Cavity Map）的配合。毛孔法线贴图用于打断漫反射的低频变化，腔体贴图（AO的高频版本）用于在毛孔边缘产生细微阴影。皮肤的镜面反射并非均匀分布：T区（额头、鼻子）皮脂腺分泌旺盛，粗糙度值约为0.2–0.3；脸颊区域粗糙度约为0.4–0.5；眼睑皮肤最薄，需叠加额外的透射贡献。使用Disney Principled BRDF时，皮肤材质的`Specular`参数通常设置在0.35–0.5之间（对应折射率约1.4，接近皮肤角质层的实测值1.34–1.55），而非金属材质默认的0.5。

## 实际应用

在游戏角色制作中，皮肤材质工作流通常包含以下贴图通道：Albedo（记录皮肤底色与黑色素分布）、Normal（毛孔法线）、Roughness（分区控制皮脂分布）、Scatter Mask（控制不同区域SSS强度，如耳朵和鼻翼需要更高的透射强度）和Thickness Map（用于透射计算，代表皮肤厚度的近似值）。《战神：诸神黄昏》（2022）中奎托斯的皮肤使用了基于屏幕空间的SSS，并在高频细节上叠加了动态皮脂模拟以表现战斗时的出汗效果。

在UE5的Lumen全局光照下，Subsurface Profile材质的散射剖面参数中，`Scatter Radius`建议设置为1.2cm以内，超出此值在实时渲染下会产生明显的漏光瑕疵。对于离线渲染（如影视VFX），Arnold和RenderMan均直接实现了完整的BSSRDF，散射参数通过测量真实皮肤光谱反射率数据（如Donner & Jensen 2006年测量的8组人体皮肤样本数据）驱动。

## 常见误区

**误区一：将皮肤SSS强度调得越大越好。** 过度的SSS会导致皮肤失去高频明暗对比，面部特征变得模糊，尤其在侧光或强方向光下会出现不自然的光晕。正确做法是用Thickness Map精确控制耳垂、鼻翼等薄处的透射，而非全局提高散射强度。

**误区二：认为皮肤只有一层高光，用单一粗糙度值覆盖全脸。** 皮肤高光实际上是双叶（Dual-lobe）结构：一层来自角质层的介电质反射（窄高光，高亮点），一层来自皮脂的宽散射高光（soft sheen）。仅使用单一GGX BRDF会使皮肤看起来像哑光乳胶。Disney Principled BRDF的`Specular Tint`和UE的`Dual Specular`扩展正是为此设计。

**误区三：认为皮肤Albedo可以直接用拍摄照片。** 相机拍摄的皮肤照片包含了SSS已经贡献的颜色（光已经在皮下散射过），若将其直接用作Albedo输入，再叠加SSS计算，会产生颜色过饱和或过红的问题。正确做法是在交叉极化（Cross-Polarization）拍摄条件下获取去除镜面反射的纯漫反射Albedo，或使用Texturing.xyz等专业皮肤扫描库提供的已校正贴图。

## 知识关联

皮肤材质建立在自定义光照模型的基础上——必须能够在Shader中分离漫反射与镜面反射的计算通道，才能将BSSRDF的散射项插入正确位置替换标准Lambert漫反射。理解皮肤材质后，技术美术可以将同样的次表面散射原理扩展到玉石、大理石、蜡烛等其他半透明材质，这些材质同样使用双极扩散剖面，只是散射颜色和散射半径参数不同。此外，眼球材质（角膜的湿润高光、虹膜的透射深度）和头发材质（Marschner Hair BRDF）通常与皮肤材质配合实现完整的角色头部渲染，三者共同构成写实角色渲染的核心技术栈。