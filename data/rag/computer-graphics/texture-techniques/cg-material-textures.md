---
id: "cg-material-textures"
concept: "材质纹理集"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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


# 材质纹理集

## 概述

材质纹理集（Material Texture Set）是基于物理渲染（PBR，Physically Based Rendering）工作流的核心贴图组合规范，将描述同一物体表面不同物理属性的多张贴图打包为一套协同工作的资产集合。一套标准的材质纹理集通常包含五张核心贴图：漫反射颜色贴图（Albedo）、法线贴图（Normal Map）、粗糙度贴图（Roughness）、金属度贴图（Metallic）以及环境光遮蔽贴图（AO，Ambient Occlusion）。

材质纹理集工作流随着PBR技术在2012年前后被Marmoset Toolbag和Allegorithmic的Substance Designer广泛推广而逐渐成为行业标准，并在游戏引擎领域由迪士尼在其2012年发布的"Principled BRDF"论文中奠定了理论基础。在此之前，美术人员使用漫反射贴图加高光贴图（Specular Map）的传统工作流，无法在不同光照环境下保持材质外观一致。材质纹理集的出现解决了这一问题——基于能量守恒定律的PBR规范确保了同一套贴图无论在室内还是室外光照下都能产生物理正确的渲染结果。

在实际制作中，游戏美术资产通常使用1024×1024至4096×4096像素分辨率的贴图，一套完整的纹理集意味着单个模型可能占用40MB以上的显存空间，因此理解每张贴图的具体作用和数据格式对优化资产成本至关重要。

## 核心原理

### Albedo贴图：纯净的固有色

Albedo贴图存储物体表面的基础颜色信息，与传统漫反射贴图的关键区别在于：Albedo贴图中**不应包含任何光照信息**（阴影、高光或环境光）。在sRGB色彩空间下，非金属材质的Albedo值应保持在50–240之间（0–255范围），过暗的值（低于30）在物理上不可能存在于自然材质中，因为没有任何真实表面能吸收接近100%的光。Albedo贴图通常以RGB三通道格式存储，每通道8位。

### Normal Map：表面细节的几何欺骗

法线贴图通过在切线空间中存储每个像素的法线方向向量，使低面数模型在渲染时表现出高面数模型的光照细节。切线空间法线贴图的RGB三通道分别对应法线向量的X、Y、Z分量，其中Z轴（蓝色通道）始终朝向表面外侧，因此正确的法线贴图整体呈现蓝紫色调——纯平表面对应RGB值（128, 128, 255）。OpenGL与DirectX的法线贴图在Y轴方向（绿色通道）上互为取反，这是跨引擎导入时最常见的翻转错误来源。

### Roughness与Metallic：控制光的行为方式

粗糙度贴图（Roughness）是单通道灰度图，数值范围0.0–1.0，控制镜面反射的模糊程度：值为0表示完全光滑的镜面反射，值为1表示完全漫散射的粗糙表面。金属度贴图（Metallic）同样是单通道灰度图，在实践中通常只使用0（非金属）和1（纯金属）两个端点值，中间值仅用于表示金属表面有污垢覆盖的过渡区域。这两张贴图可以封包进同一张RGBA贴图的不同通道，称为"通道打包"（Channel Packing），例如Unreal Engine的ORM格式将AO存入R通道、Roughness存入G通道、Metallic存入B通道，将三张贴图压缩为一张，节省约66%的采样器资源。

### AO贴图：预计算的遮蔽关系

环境光遮蔽贴图记录模型几何体的缝隙、凹陷处受到环境光遮挡的程度，是一张从模型高模烘焙而来的灰度图。AO值为1（白色）表示该区域完全暴露于环境光中，值为0（黑色）表示完全遮蔽。AO贴图仅影响间接光照的遮蔽，不影响直接光照——在引擎中，AO贴图应与Albedo相乘，而非直接叠加，且绝不应用于影响高光反射部分。

## 实际应用

在Substance Painter中制作角色盔甲时，美术师会为每块不同材质的区域划分独立的纹理集（Texture Set），例如金属护甲板和皮革衬垫各占一套独立贴图，这样可以为不同部位设置不同的Metallic值——护甲板Metallic接近1.0，皮革部分Metallic为0.0，Roughness则根据磨损程度从0.3渐变至0.8。

在Unreal Engine 5中，一套标准的PBR材质节点网络将Albedo连接至Base Color输入，Roughness连接至Roughness输入，Metallic连接至Metallic输入，Normal Map先经过一个"NormalMap"节点解码后连接至Normal输入，AO则乘以Albedo结果再传入Base Color，或直接连接至Ambient Occlusion输入。对于移动端项目，开发者常将Roughness和Metallic两张贴图与AO合并为单张RGB贴图，将整套纹理集从五张减为三张以节省包体。

## 常见误区

**误区一：将含有光照信息的漫反射贴图直接当作Albedo使用。** 从传统渲染工作流迁移过来的美术资产，其漫反射贴图往往烘焙了手绘阴影和高光，直接用作PBR Albedo会导致材质在任何光照角度下都保留"假光影"，在动态光照下显得格外不自然。正确做法是在Photoshop中使用"叠加"或"柔光"混合模式将光照层分离，或重新绘制不含光照信息的固有色。

**误区二：认为Metallic贴图中的中间灰度值代表"半金属"材质。** 现实中不存在物理意义上的"半金属"，Metallic贴图的中间值（0.1–0.9）仅应出现在金属表面边缘有灰尘或污垢覆盖的像素区域，用以模拟该像素内金属与非金属的混合占比。若将金属度统一设为0.5，会产生能量不守恒的不真实反射效果。

**误区三：混淆OpenGL与DirectX法线贴图格式。** 在Unity（默认OpenGL法线格式）中导入为DirectX格式创建的法线贴图，会导致凸起表面在侧面光照下显示为凹陷，即光照方向与法线细节相反。检验方法是观察贴图：OpenGL格式的砖缝等凹陷区域的绿色分量偏暗，而DirectX格式则偏亮。

## 知识关联

学习材质纹理集需要具备纹理映射的基础概念，理解UV坐标如何将二维贴图投影到三维模型表面，以及纹理采样、Mipmap等基本机制——这些知识决定了纹理集中每张贴图如何被正确读取和过滤。

材质纹理集工作流直接引向**纹理烘焙**这一后续技能：五张贴图中，Normal Map和AO贴图都必须从高模向低模烘焙而来，烘焙过程中的笼体（Cage）设置、匹配距离参数以及切线空间基准设置，都与材质纹理集的格式规范紧密对应。此外，掌握材质纹理集还为学习**通道打包优化**和**纹理图集（Texture Atlas）**合并多套纹理集奠定实践基础，这两项技术是移动端和主机端游戏性能优化的关键手段。