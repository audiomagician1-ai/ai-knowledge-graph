---
id: "3da-bake-normal"
concept: "法线烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 法线烘焙

## 概述

法线烘焙（Normal Map Baking）是将高多边形模型（High-poly）的表面凹凸细节编码到一张RGB贴图中，再应用到低多边形模型（Low-poly）上，使其在渲染时产生高细节光照效果的技术。贴图中R、G、B三个通道分别对应表面法线的X、Y、Z向量分量，像素颜色值的范围从0到255映射到向量值-1到+1。标准切线空间法线贴图呈现蓝紫色调，是因为大多数表面的Z轴（蓝色通道）趋近于1，即法线朝向屏幕外侧。

法线贴图技术由Krishnamurthy和Levoy于1996年提出，最初以"位移贴图代替"形式出现在论文中，随后由Cg游戏管线在2000年代初期将切线空间（Tangent Space）法线贴图确立为实时渲染的行业标准。切线空间法线贴图相比世界空间法线贴图的核心优势在于：贴图可随模型旋转和UV镜像复用，同一张贴图可应用于镜像的左右对称模型的两侧，节约显存。

在一个典型次世代游戏角色制作流程中，雕刻师会在ZBrush中制作高达2000万面的高模，烘焙后以2048×2048分辨率的法线贴图在低模（约8000面）上还原出几乎相同的光照细节，这是法线烘焙在美术管线中最直接的价值体现。

## 核心原理

### 切线空间的构成

切线空间由三个正交向量组成：法线N（Normal）、切线T（Tangent）和副切线B（Bitangent，有时称Binormal）。这三个向量在每个顶点上由UV展开方向和几何法线共同决定。切线T沿UV的U轴方向，副切线B沿V轴方向，N垂直于表面。烘焙软件将高模在该坐标系下的表面法线向量转换为RGB颜色存储，渲染引擎读取时再将颜色还原为向量，叠加到低模的切线空间中进行光照计算。

### 烘焙流程与关键参数

标准法线烘焙流程分为五个步骤：①准备High-poly与Low-poly的拓扑对应关系；②展开Low-poly的UV（确保无重叠、留有2~4像素的Texel间距防止漏光）；③在软件中设置烘焙参数；④执行烘焙并检查结果；⑤导入引擎进行验证。

关键参数包括：**Ray Distance（射线距离）**控制高模投影的搜索范围，过小会导致区域遗漏，过大会采样到错误的面；**Cage（笼体）**是Low-poly表面向外偏移的包裹体，用于确定射线起始点以避免自交叉问题（详见Cage设置）；**样本数（Samples）**通常设置为4×或16×抗锯齿，16×可消除大多数边缘锯齿但烘焙时间增加约4倍；**Smoothing Groups（平滑组）**必须与UV硬边完全匹配，每条UV缝合线必须对应一条硬边，否则法线贴图在接缝处会出现明显光照断层。

### 坐标系差异：DirectX与OpenGL

法线贴图有两种坐标系标准：DirectX标准（+Y向下，G通道偏暗）和OpenGL标准（+Y向上，G通道偏亮）。Unreal Engine默认使用DirectX（DX）法线，Unity与大多数PBR工具默认使用OpenGL法线。两者G通道（Y轴）方向相反，混用会导致凹凸方向在特定光照角度下反转。将DX法线转换为OpenGL法线只需在Photoshop中将G通道做反相（Ctrl+I）处理即可。Substance Painter支持在导出预设中直接选择DirectX/OpenGL翻转。

### 投影方式

烘焙投影分为两种：**基于射线投影（Ray Casting）**从Low-poly表面沿法线向高模发射射线进行采样，精度高但需正确配置Cage；**基于笼体投影（Cage Projection）**使用自定义的笼体网格代替法线偏移计算射线起始位置，可解决复杂凹凸形状的自遮挡问题。xNormal和Marmoset Toolbag均支持这两种投影模式，而Substance Painter主要使用前者。

## 实际应用

**螺丝、铆钉等小型金属件**：在角色盔甲或道具上，几十颗螺丝无需各自建模，只需在High-poly上雕刻后烘焙到法线贴图。结合一张2048分辨率的法线贴图，可以呈现原本需要额外添加5万面的螺纹和倒角细节。

**砖墙、地面等平铺材质**：在Substance Designer中制作砖墙程序材质时，高度信息通过法线烘焙流程（或法线节点直接生成）编码到法线贴图，可平铺应用于大型场景地面，每一块砖的棱角和缝隙都有正确的光照响应。

**人物面部细节**：ZBrush雕刻的毛孔、皱纹信息通过GoZ插件直接传递到Substance Painter进行烘焙，常见分辨率为4096×4096，确保面部近景下毛孔细节的Texel密度不低于每毫米1像素。

## 常见误区

**误区一：认为High-poly和Low-poly可以随意摆放**
烘焙时High-poly与Low-poly必须完全重叠在同一空间位置，两者的枢轴点（Pivot）必须对齐。若High-poly整体偏移哪怕0.01个单位，射线将无法正确采样，导致整张法线贴图出现错误的黑色投影条纹。Marmoset Toolbag的自动对齐功能可检测到此类偏移并报警。

**误区二：平滑组可以随意设置，烘焙后再调整**
平滑组与UV硬边必须在烘焙前就严格一致。若一条UV缝合线对应的边是软边（未分割平滑组），渲染时引擎会在该位置用错误的切线向量解码法线贴图，产生一条明显的光照缝。正确做法是在3ds Max或Maya中先确认硬边位置，再按硬边分割UV，两者保持一致。

**误区三：法线贴图蓝色纯度越高越好**
纯蓝（RGB 128, 128, 255）代表法线完全垂直于表面，是"无细节"的平坦区域，而不是质量更高的表现。一张细节丰富的法线贴图的非平坦区域R、G通道数值会明显偏离128，若整张图偏蓝说明High-poly细节未被正确采样或射线距离设置过小。

## 知识关联

法线烘焙建立在**烘焙概述**中射线投影基础概念之上，烘焙概述中的坐标系和贴图通道知识是理解RGB=XYZ向量编码的前提。掌握法线烘焙流程后，**Cage设置**专门解决复杂模型中射线起点偏移计算的精细化控制问题；**烘焙瑕疵**则对应本文中提到的接缝断层、投影错误等具体问题的诊断与修复方法。

在工具层面，**Substance烘焙**、**Marmoset烘焙**和**xNormal烘焙**三个概念分别代表行业中三种主流烘焙工具的具体操作差异——例如Marmoset的Full Float精度烘焙、xNormal的命令行批量烘焙，以及Substance Painter与Designer在法线烘焙参数上的不同暴露方式。这些工具均以本文的切线空间法线烘焙原理为共同基础，在具体参数界面和工作流自动化程度上有所区别。