---
id: "3da-org-hair-modeling"
concept: "毛发建模"
domain: "3d-art"
subdomain: "organic-modeling"
subdomain_name: "有机建模"
difficulty: 3
is_milestone: true
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 毛发建模

## 概述

毛发建模是三维美术中专门用于创建头发、皮毛、胡须、睫毛等纤维状几何结构的技术分支。与硬表面建模或角色面部建模不同，毛发具有数量庞大（人类头部约有10万根发丝）、每根形态各异、且需要随物理运动而动态变化的特殊属性，因此需要专门的工具和工作流程。

该技术领域大约在2000年代随着电影《指环王》（2001年）中对兽人皮毛的大规模数字处理需求而得到快速发展。现代毛发建模已从早期纯粹的多边形片方案，演进到基于曲线引导（Guide Curves）的程序化生成体系，以及虚幻引擎5引入的Groom系统（基于Alembic毛发标准缓存格式）。

在3D美术管线中，毛发建模的质量直接影响角色最终的真实感，因为人眼对头发轮廓和细节的识别极为敏感，劣质的毛发往往比拙劣的皮肤建模更容易被观众察觉。

---

## 核心原理

### 曲线引导方法（Guide Curve / Spline Hair）

曲线毛发的基本原理是：先创建数量有限的引导曲线（通常50～500根），再通过插值算法在引导曲线之间自动生成数以万计的渲染毛发。每根引导曲线由若干控制点（Control Point）组成，Houdini中通常每根引导毛发使用8～16个控制点以平衡精度与效率。

在Maya的XGen Interactive Grooming、Houdini的Vellum Hair以及Blender的粒子毛发系统中，引导曲线均挂载于头部网格的多边形表面，通过表面法线方向确定初始生长方向。关键参数包括：**密度（Density）**、**长度（Length）**、**噪波（Noise/Clump Noise）**、**卷曲（Curl）**和**蓬松度（Frizz）**。曲线方法的优势在于艺术家可以像梳头一样用笔刷直接对引导曲线进行造型，控制直觉性强。

### 多边形条带方法（Polygon Strip / Card Hair）

多边形条带（Hair Card）是游戏领域最常用的毛发表达形式，原理是用若干张细长的四边形面片（每张通常由2～6个多边形构成），在面片上贴附半透明发束贴图，通过Alpha测试或Alpha混合实现透明度边缘。

一套典型的次世代游戏角色发型通常包含100～500张Hair Card，每张Card宽约0.3～2厘米（基于角色实际体型），配合法线贴图（Normal Map）实现光照响应。制作流程通常是：先用曲线方案在DCC软件中梳理出高质量引导发型，再通过插件（如Ornatrix的Hair Card Baker）将其自动转化为Card并烘焙发束贴图，贴图集（Atlas）中通常包含Diffuse、Alpha、Root-to-Tip渐变和法线共4张通道。

### Groom系统方法

Groom是以根级别数据存储毛发的格式体系，在虚幻引擎5和Houdini中均已标准化。每根Groom发丝包含**位置（Position）**、**颜色（Color）**、**宽度（Width）**和**曲线段数（Segment Count）**等逐根属性，并以Alembic（.abc）或USD格式导出。

UE5的Groom组件支持**Strands模式**（逐根渲染，适合电影级）和**Cards/Meshes回退模式**（适合游戏实时），引擎会根据LOD距离自动切换。Groom系统中的**绑定资产（Groom Binding Asset）**负责将发丝坐标空间绑定到骨骼网格体上，确保角色运动时发根不会出现滑动或分离现象。

---

## 实际应用

**游戏角色发型（Hair Card工作流）**：以《赛博朋克2077》角色为例，制作团队用Autodesk Maya配合Ornatrix插件先梳理出写实引导发型，导出Card后在Marmoset Toolbag中烘焙Atlas贴图，最终每个角色头部发型的面片数控制在约200张Card、总面数不超过3000面，以满足实时渲染预算。

**影视角色皮毛（Houdini Groom工作流）**：动物皮毛通常分为**底毛（Underfur）**、**中间毛（Awn Hair）**和**护毛（Guard Hair）**三层，分别用不同密度的曲线系统独立Groom，再合并为一个Alembic缓存文件交付渲染部门。

**睫毛与眉毛建模**：这两类毛发因生长区域面积极小，通常不用粒子系统，而是直接用4～8排多边形条带手动摆放，贴附含Alpha通道的眉/睫贴图，每排条带约4个面，全套睫毛面数在60～120面之间。

---

## 常见误区

**误区一：引导曲线越多越好**
许多初学者认为增加引导曲线根数就能提升发型质量，但实际上过密的引导曲线会导致曲线之间的插值发生冲突，产生"鸡窝"般的杂乱效果。正确做法是用合理数量的引导曲线配合**成束（Clump）**参数来模拟自然发束的聚合特征，人类头发的自然成束通常是每束5～20根。

**误区二：Hair Card的Alpha边缘不需要特殊处理**
直接使用PNG Alpha通道制作Hair Card会在实时引擎中因深度排序（Depth Sorting）问题产生明显的穿插瑕疵。正确做法是将Hair Card的透明通道渲染模式设置为**Dithered LOD Transition**或启用**Temporal AA**抖动，同时将发束从外层到内层按前到后排列，以减少渲染顺序错误。

**误区三：Groom发根可以直接绑定到任意网格**
Groom绑定要求底层网格的拓扑结构在绑定后不得发生顶点数量或顺序的改变，否则Groom Binding Asset会报错或产生发根位置漂移。头部模型的拓扑在完成毛发Groom之前必须已经是最终版本，这是Groom工作流与头部建模阶段强耦合的根本原因。

---

## 知识关联

毛发建模以**头部建模**为直接前置依赖：Groom曲线的生长点（Root Point）必须精确映射到头部网格的UV坐标与顶点法线上，头顶、发际线处的网格曲率会直接影响发根的生长角度。头部模型上头皮区域的面密度建议不低于每平方厘米2个面，否则发根法线精度不足，会导致发根区域出现光照方向异常。

在渲染层面，毛发建模的成果需要与**毛发着色器**（如UE5的Hair Shading Model或Arnold的aiStandardHair着色器，基于Marschner 1999年提出的R/TT/TRT多次反射模型）配合才能完整表达真实感，但着色器配置属于材质与渲染领域而非建模范畴。完成毛发建模后，通常进入的下游任务是**毛发绑定与模拟**，即为引导曲线添加物理约束以实现动态运动响应。
