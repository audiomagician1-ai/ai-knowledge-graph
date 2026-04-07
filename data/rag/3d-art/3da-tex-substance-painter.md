---
id: "3da-tex-substance-painter"
concept: "Substance Painter"
domain: "3d-art"
subdomain: "texturing"
subdomain_name: "纹理绘制"
difficulty: 2
is_milestone: true
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Substance Painter

## 概述

Substance Painter（简称SP）是由Allegorithmic公司于2014年首次发布的专业PBR纹理绘制软件，2019年被Adobe收购后并入Substance 3D系列。SP的核心设计理念是"非破坏性分层绘制"，允许艺术家在三维网格表面直接绘制纹理，同时保留所有编辑历史。与传统的Photoshop平面贴图绘制相比，SP在三维视口中实时预览材质效果，所见即所得地模拟PBR渲染结果。

SP之所以在游戏和影视行业中成为纹理绘制的标准工具，关键在于其将烘焙贴图（如AO、曲率、法线）与程序化生成器深度整合。艺术家导入网格并烘焙完Mesh Maps之后，智能材质和生成器能够自动识别模型的凹凸、边缘和平面区域，在数秒内生成真实的金属划痕、锈蚀和污垢效果。这种工作流大幅缩短了手工绘制磨损细节所需的时间，一个中等复杂度的道具纹理制作时间可从数天压缩至数小时。

## 核心原理

### 图层系统与混合模式

SP的图层系统与Photoshop概念相近但有本质差异：SP中每个图层可以同时携带多个PBR通道的数据，包括Base Color、Roughness、Metallic、Height、Normal等，最多可同时操控8个通道。每个图层还拥有独立的蒙版（Mask）控制该层的显示范围，蒙版本身可以叠加多个生成器效果。

图层叠加遵循从下到上的渲染顺序，底部图层先渲染，上方图层依据混合模式叠加。SP内置了专为PBR设计的混合模式，例如"Normal"模式直接替换下层，"Multiply"模式常用于叠加污垢颜色，而"Height"通道使用的混合模式会影响法线贴图的最终合成结果。图层还可以组合为**图层组（Layer Group/Folder）**，组本身也支持蒙版，实现层级化的非破坏性管理。

### 智能材质（Smart Material）

智能材质是SP的预设材质包，其内部封装了完整的多层图层结构，包含多个依赖烘焙贴图的生成器。例如一个"Worn Metal"智能材质通常包含：底层金属基础色图层、中层使用曲率贴图（Curvature Map）驱动的边缘高光图层、以及顶层使用环境光遮蔽（AO Map）驱动的缝隙污垢图层。智能材质的"智能"体现在其生成器会读取当前模型的Mesh Maps，因此同一个智能材质应用到不同模型上会产生不同的磨损分布，完全贴合模型几何结构。

使用智能材质的前提是必须事先完成Mesh Maps烘焙，至少需要烘焙Normal、World Space Normal、AO、Curvature和Position这五张贴图，否则生成器无法读取到驱动数据，效果会大打折扣。

### 生成器（Generator）与滤镜（Filter）

生成器是SP中程序化生成蒙版的核心机制，本质上是一段参数化的算法，输出0-1的灰度蒙版图像。常用内置生成器包括：**MG Dirt**（利用AO贴图在凹陷区域生成污垢）、**MG Edge Wear**（利用Curvature贴图在凸起边缘生成磨损）、**MG Grunge**（生成随机噪声肌理）。生成器参数通常包括强度（Intensity）、对比度（Contrast）、以及与各Mesh Map的混合权重，这些参数均可在属性面板中实时调整并即时预览。

滤镜（Filter）与生成器的区别在于：生成器作用于**蒙版**，控制图层的显示范围；滤镜作用于**图层通道内容本身**，例如用Blur滤镜模糊Base Color，或用Levels滤镜调整Roughness值的分布范围。两者可以叠加使用，为单一图层构建极其复杂的程序化效果。

### 纹理集（Texture Set）与UDIM

SP以**纹理集（Texture Set）**为单位管理材质，每个纹理集对应模型上一个UV空间和一套输出贴图。一个复杂角色模型可能拆分为"Body"、"Head"、"Armor"等多个纹理集，分别独立绘制。SP 2021版本后加入了完整的UDIM工作流支持，允许单个纹理集使用多张UV Tile（如1001、1002、1003），每个Tile输出独立贴图文件，满足影视级别的高分辨率纹理需求。

## 实际应用

**武器道具纹理制作**是SP最典型的应用场景。以制作一把游戏用步枪为例：首先导入已经完成UV展开的FBX文件，在Texture Set Settings中设置分辨率为2048×2048，然后依次烘焙Normal、AO、Curvature、Position、Thickness贴图；接着拖入"Military Weapon"智能材质作为基础，生成器自动在枪口和握把边缘产生金属磨损，在缝隙处堆积油脂污垢；最后手动添加刮痕、序列号贴花和特定区域的磨损，整个流程可在3-5小时内完成。

**颜色ID驱动的分区绘制**是另一个高频工作流：在建模阶段为不同材质区域指定不同颜色的Material ID贴图，导入SP后使用"Color Selection"蒙版精确隔离每个材质区域，避免笔触溢出到不需要的区域。

SP支持直接导出符合虚幻引擎（Unreal Engine）、Unity、Arnold、V-Ray等渲染器格式的贴图预设，通过内置导出模板一键打包所有PBR贴图通道。

## 常见误区

**误区一：跳过Mesh Maps烘焙直接开始绘制。** 许多初学者在未烘焙任何Mesh Maps的情况下就尝试使用智能材质，发现生成器毫无效果。SP的生成器（如MG Edge Wear）必须读取Curvature Map才能识别模型边缘，没有这张贴图，生成器只会输出均匀的灰色蒙版，无法产生任何与模型几何相关的磨损效果。

**误区二：将所有内容绘制在单一图层上。** 部分初学者习惯在一个Paint图层上叠加所有手绘内容，丧失了SP非破坏性分层的核心优势。正确做法是按材质区域、磨损程度、特殊细节分别建立图层，这样后期修改某个磨损区域时只需调整对应图层，不影响其他内容。

**误区三：混淆Height通道与Normal通道的用途。** SP中Height通道（高度图）与Normal通道分别控制不同的表面细节：Height图存储相对高度位移信息，在SP视口中会被实时转换为屏幕空间法线影响光照表现，但导出时是独立的灰度图；Normal通道直接叠加切线空间法线信息。在SP内通过Height通道绘制的凹凸细节，导出时需要在Export Settings中确认Height和Normal通道的输出格式，否则在引擎端可能出现细节丢失。

## 知识关联

SP的正常使用以**PBR纹理工作流**为基础，艺术家必须理解Base Color、Roughness、Metallic各通道的物理含义才能正确判断材质效果；同时SP的智能材质和生成器功能严重依赖**烘焙最佳实践**——正确的法线方向、无缝的UV接缝处理和准确的Curvature贴图烘焙是生成器效果的质量前提。

从SP出发，自然延伸到更专项的技能：SP内置的法线绘制与叠加功能是学习**法线贴图制作**的实践入口；通过观察SP中AO生成器的参数逻辑可以加深对**AO贴图**原理的理解；**Material ID**工作流直接在SP的Color Selection蒙版中得以应用；SP的智能材质和程序化生成器是**做旧与风化**效果的主要实现手段；而**贴花纹理**功能（Decal投射）在SP中通过专用的Projection模式实现，是角色序列号、标志和特定磨损细节的标准制作手段。