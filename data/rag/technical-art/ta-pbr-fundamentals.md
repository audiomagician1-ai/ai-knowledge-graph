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



# PBR材质基础

## 概述

PBR（Physically Based Rendering，基于物理的渲染）是一套以真实光照物理规律为依据的材质描述体系，由迪士尼研究院的Brent Burley在2012年SIGGRAPH演讲《Physically-Based Shading at Disney》中系统化提出，并随后被Unreal Engine 4和Unity 5在2014年前后广泛采用，成为游戏与影视实时渲染的行业标准。

PBR的核心价值在于"光照环境无关性"：一套PBR材质参数在室外日光、室内灯光、黄昏等不同光照条件下均能产生物理正确的外观，彻底解决了传统Phong模型中高光颜色与强度必须针对特定灯光手动调整的问题。这一特性使美术资产可以在任意场景中复用而无需重新调色。

PBR体系建立在两条能量守恒定律之上：一是表面反射光与透射光之和不超过入射光总量；二是粗糙表面的微表面法线分布会扩散高光面积，但不会凭空增加反射总能量。这两条约束从根本上决定了PBR各通道的物理意义与取值范围。

## 核心原理

### 金属度通道（Metallic）

金属度通道是一个0到1的标量蒙版，物理含义是"该像素是导体还是电介质"。金属（导体）的F0反射率通常在70%～100%之间（如金F0≈1.00/0.71/0.29，铁F0≈0.56/0.57/0.58，均为sRGB空间线性值），且反射颜色由BaseColor决定；非金属（电介质）的F0统一近似为0.04（约4%），反射为白色，漫反射颜色来自BaseColor。现实中不存在"半金属"表面，因此金属度在实际使用时应尽量取0或1，中间值仅用于过渡边缘蒙版的抗锯齿处理。

### 粗糙度通道（Roughness）

粗糙度描述微表面法线的统计分布宽度，对应Cook-Torrance BRDF中的分布函数D项与几何遮蔽函数G项。Unreal Engine使用α = Roughness²对roughness值进行感知线性化映射，使艺术家在0.0（镜面反射）到1.0（完全漫反射）之间调整时变化视觉上均匀。粗糙度为0时高光极度集中，为0.5时高光面积大幅扩散但仍可见方向性，为1时高光完全散射等同于朗伯漫反射。注意：Roughness与传统Specular Power（高光指数）是非线性反向关系，不能简单线性转换。

### 法线贴图通道（Normal Map）

法线贴图以切线空间（Tangent Space）存储每个像素的微观法线偏移，RGB三通道分别对应切线空间的X（红）、Y（绿）、Z（蓝）分量，存储格式为线性空间（不可勾选sRGB）。标准切线空间法线贴图的"平坦"像素值为(0.5, 0.5, 1.0)即RGB(128, 128, 255)，显示为淡紫色。法线贴图在片元着色器中通过TBN矩阵（Tangent-Bitangent-Normal）从切线空间变换到世界空间，再参与光照计算——这也是为什么学习PBR材质需要先掌握片元着色器中TBN变换的原因。DirectX与OpenGL的法线贴图在Y轴方向相反，在跨引擎导入时需注意翻转G通道。

### 环境遮蔽通道（Ambient Occlusion / AO）

AO贴图记录的是模型表面接受到环境光的遮蔽程度，取值1.0表示完全暴露，0.0表示完全遮蔽。AO只影响间接漫反射（环境光），不影响直接光照计算，因此正确的PBR管线中AO的乘算位置是在间接漫反射项之后、直接光照叠加之前。将AO错误地乘到最终颜色输出上会导致直接光下凹缝变黑，产生不真实的"脏旧"感。AO通常由Substance Painter或Marmoset Toolbag通过低精度模型烘焙高精度模型获得，烘焙时的Cage偏移设置会直接影响AO精度。

### BaseColor通道

BaseColor（基础色）与传统Diffuse贴图的根本区别在于：BaseColor不应包含任何光照信息（无需手绘高光或阴影），纯粹表达材质的固有色。非金属的BaseColor代表反射后离开表面的漫反射颜色，其值建议控制在sRGB 50～240之间（避免过暗或过亮导致能量不守恒）；金属的BaseColor代表F0镜面反射颜色，铁约为(142, 145, 148)，金约为(255, 181, 74)，均可参考PBR Charts标准值表。

## 实际应用

**金属锈迹材质**：使用一张手绘遮罩将金属度从1.0过渡到0.0模拟锈蚀区域——锈迹区域金属度为0，粗糙度提高至0.85，BaseColor改为红棕色。锈迹凸起部分在法线贴图中叠加高频细节，AO在凹陷处加强遮蔽，整体效果无需任何手绘高光即可在任何光照下自洽。

**Unreal Engine材质节点配置**：BaseColor连接Texture Sample后直接输出到Base Color引脚（注意Texture需为sRGB格式）；Roughness与Metallic贴图需采样自线性空间纹理（关闭sRGB），将R/G通道单独拆出；Normal贴图使用专用的Normal Map引脚，引擎内部自动完成TBN变换。

**皮肤材质的特殊处理**：人类皮肤属于次表面散射（SSS）材质，金属度为0，粗糙度约0.6，但其漫反射不遵循标准朗伯模型——需要额外的Subsurface Color通道模拟红色皮下血液层，Subsurface Radius参数控制光线在皮肤中的散射距离（通常R通道最大约1.2cm，G约0.5cm，B约0.2cm）。

## 常见误区

**误区一：将旧版Diffuse贴图直接当作BaseColor使用**

传统Diffuse贴图通常预先烘焙了环境光遮蔽和手绘高光信息。将其直接插入PBR的BaseColor引脚会导致双重AO叠加（贴图中的AO暗部与引擎计算的AO同时作用），以及在强光下高光区域出现异常亮斑。正确做法是在Substance Painter中重新绘制不含光照的固有色。

**误区二：粗糙度为0等于真实镜面**

粗糙度0在实时PBR中只是数学上的极限情况，反射仍受制于引擎的反射捕获精度（如UE4中的Reflection Capture球半径决定反射分辨率）。如果场景中未放置足够密度的Reflection Capture，即使粗糙度设为0，反射图像也会模糊失真，这是引擎管线限制而非PBR材质参数错误。

**误区三：AO贴图可以替代法线贴图的细节功能**

AO贴图仅影响间接漫反射，不改变表面法线方向，因此不会产生直接光照下的凹凸阴影。若只有AO没有法线贴图，在强方向光下模型表面仍显平坦，凹陷细节仅在间接光下可见。两者服务于不同的光照分量，必须同时使用才能在所有光照条件下呈现立体感。

## 知识关联

**前置依赖**：片元着色器的TBN矩阵变换是理解法线贴图工作原理的直接基础——法线贴图的切线空间到世界空间的转换在片元着色器中以矩阵乘法实现，若不理解这一步骤则无法判断法线贴图方向错误的根本原因。此外，sRGB与线性颜色空间的区别直接决定各通道采样时是否勾选sRGB选项，理解gamma校正流程可避免粗糙度/金属度等线性通道被错误gamma解码。

**后续扩展**：掌握单层PBR材质后，材质分层（Material Layering）在此基础上通过蒙版混合多个PBR参数集，实现如"铁锈覆盖金属"的复合效果；材质实例（Material Instance）将PBR参数暴露为可调变量以复用同一shader；纹理通道打包（Channel Packing）则将AO/Roughness/Metallic压缩进同一张纹理的不同通道，将三次采样优化为一次；Substance工作流在BaseColor/Normal/ORM（Occlusion-Roughness-Metallic）的标准通道命名上与上述概念直接对应。