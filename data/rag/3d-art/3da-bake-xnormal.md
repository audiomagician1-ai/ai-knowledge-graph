---
id: "3da-bake-xnormal"
concept: "xNormal烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# xNormal烘焙

## 概述

xNormal是由西班牙开发者Santiago Orgaz于2005年发布的免费独立烘焙软件，专门针对游戏资产制作中的法线贴图、环境光遮蔽（AO）及其他多种贴图类型的高质量批量烘焙而设计。与Maya、3ds Max或Blender内置的烘焙模块相比，xNormal采用"高模投影低模"的专用工作流，能够以极高精度将高达数百万面的高精度模型细节烘焙到低面数游戏模型上，且不依赖任何宿主DCC软件即可独立运行。

xNormal的核心优势在于其多线程批量烘焙能力——用户可以一次性在队列中加载多组高模/低模配对，软件将按顺序自动处理所有烘焙任务，这对于需要制作数十个角色或道具资产的项目极大节省了人力。截至xNormal 3.19版本，软件支持Windows和Linux平台，输出贴图分辨率最高可达8192×8192像素，并支持16位或32位浮点EXR格式输出，满足影视级别的精度需求。

在游戏行业工作流中，xNormal长期被视为法线烘焙的行业标准工具之一，尤其在虚幻引擎和Unity项目中被广泛采用，因为其烘焙出的切线空间法线贴图与这两个引擎的切线空间计算方式有专门的适配选项。

## 核心原理

### 高模与低模配对机制

xNormal的烘焙流程建立在"高模（High Definition Mesh）"与"低模（Low Definition Mesh）"的明确分工上。用户在左侧面板分别加载高模和低模的OBJ、FBX或其他受支持格式文件，软件通过光线从低模表面向外投射（Raycast）打到高模表面来采样法线信息。投射距离由"Ray Distance"参数控制，该值决定了光线能探测到的最大距离；若设置过小，凸出部分会出现采样遗漏导致黑色噪点；若设置过大，则会误采样到模型内部或反面几何体造成错误。

### 笼（Cage）的作用与调整

xNormal提供两种控制光线投射范围的方式：自动Ray Distance数值调整，以及手动加载"笼网格（Cage Mesh）"。笼是低模表面向外膨胀一定量后生成的包裹性网格，光线从笼的内表面出发投向高模。用户可以在xNormal外部（如Maya或ZBrush）手动编辑笼，对凹陷区域局部收缩笼的膨胀量，从而解决自动Ray Distance无法处理的复杂几何体投影问题，例如角色盔甲的夹角区域或武器的刀刃部分。

### 支持的贴图烘焙类型

xNormal 3.19版可一次性批量烘焙超过12种贴图类型，包括：切线空间法线贴图（Tangent Space Normal）、对象空间法线贴图（Object Space Normal）、环境光遮蔽（Ambient Occlusion，可设置光线数量从8到4096条）、弯曲法线（Bent Normal）、厚度图（Thickness Map）、凹凸贴图（Height Map）、曲率图（Curvature Map）等。其中AO烘焙的质量直接由"Number of Rays"参数决定，通常512条光线已足够游戏资产使用，而影视输出建议使用2048条以上。

### 切线空间兼容性设置

xNormal提供针对不同引擎的切线空间计算选项。在"Tangent Space"设置中，用户需要根据目标引擎选择正确的配置：对于虚幻引擎5，需要勾选"Mikk/xNormal"切线空间模式；对于Unity的标准管线，同样推荐使用MikkTSpace。若切线空间不匹配，烘焙出的法线贴图在引擎内显示会出现明显的光照错误，表现为模型接缝处产生高亮或暗带。

## 实际应用

**武器资产批量烘焙**：在一个包含20把武器的游戏项目中，美术人员可以在xNormal的高模列表中依次添加20个高精度ZBrush雕刻模型，在低模列表中对应添加20个已拓扑的游戏模型，然后在"Baking Options"中同时勾选Normal Map、AO和Curvature Map，点击"Generate Maps"后软件自动按顺序输出60张贴图，无需美术人员值守操作。

**法线贴图接缝处理**：xNormal支持在低模FBX中读取UV分组的硬边信息。美术人员需要确保低模在UV接缝处的边设为硬边（Hard Edge），这样xNormal在烘焙时会按照硬边分割切线空间，烘焙结果在UV接缝处不会产生法线方向突变，这与引擎实时渲染时读取法线贴图的方式保持一致。

**厚度图制作SSS材质**：xNormal的Thickness Map烘焙通过向模型内部投射光线测量穿透厚度，输出0（薄）到1（厚）的灰度图，该图直接用于虚幻引擎5的皮肤着色器中驱动次表面散射（SSS）强度，薄的区域（如耳廓、手指）显示为浅色，呈现透光效果。

## 常见误区

**误区一：Ray Distance设置越大越保险**。许多初学者认为增大Ray Distance可以避免采样遗漏，但当Ray Distance超过模型局部几何体之间的间距时，光线会穿过薄壁结构打到反面或其他部件，导致法线贴图出现大面积错误。正确做法是将Ray Distance设置为恰好能包住高模的最小值，必要时使用Cage文件进行局部精确控制。

**误区二：xNormal烘焙的法线贴图可以在任何软件中通用**。xNormal的切线空间法线贴图在不同引擎和DCC软件中需要不同的Y通道（绿色通道）朝向。DirectX法线贴图（如虚幻引擎使用）的绿色通道朝向与OpenGL法线贴图（如Substance Painter预览使用）相反。xNormal在输出设置中提供了"Flip Y"选项，使用前必须确认目标软件的法线贴图规范。

**误区三：多个高模部件需要合并成一个文件**。xNormal的高模加载列表支持添加多个独立的OBJ文件，软件在烘焙时会将所有高模视为同一场景中的几何体进行光线投射，因此角色的身体、头部、装备等部件可以分别导出为独立文件加载，无需在DCC软件中合并为一个Mesh。

## 知识关联

xNormal烘焙建立在法线烘焙的基础原理之上——理解切线空间法线的RGB分量分别对应XYZ方向偏移是使用xNormal进行参数调整的前提。如果在法线烘焙阶段已经掌握了高模/低模工作流和UV展开规范，那么xNormal中的大多数参数（如Ray Distance、Cage、切线空间选择）都是对这些基础概念的具体操作实现。

在xNormal的实际使用中，低模的UV接缝与硬边的对应关系直接影响烘焙质量，这一规则与Substance Painter、Marmoset Toolbag等其他烘焙工具遵循相同的物理原理，但xNormal因其独立性和免费性，常作为学习和验证烘焙参数的参考工具来与其他软件的烘焙结果进行对比校验。