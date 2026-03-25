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

xNormal是由Santiag Orgaz开发的免费独立烘焙工具，专门用于将高精度模型（High Poly）的细节信息投影到低精度模型（Low Poly）上，生成法线贴图、环境光遮蔽（AO）、曲率图等多种烘焙贴图。与Maya、Blender等DCC软件内置的烘焙器相比，xNormal支持在GPU和CPU双模式下运行，并且在处理超百万面数的高模时不容易崩溃，稳定性更高。

xNormal最早发布于2005年前后，最新稳定版本为3.19.3，长期以来是游戏行业法线烘焙的标准工具之一，尤其在次世代游戏角色和道具制作流程中被广泛使用。尽管Marmoset Toolbag和Substance Painter等工具已经提供了集成烘焙功能，xNormal因其批量处理能力和免费授权，至今仍在高校教学和中小型团队中占有重要地位。

xNormal的核心优势在于其高度可配置的烘焙参数和批量导出能力。用户可以一次性设置多个烘焙通道，在单次操作中同时输出法线图、AO图、位移图等，大幅提升大型项目中的资产处理效率。

---

## 核心原理

### 高模与低模的对应关系设置

xNormal的烘焙流程以"笼体（Cage）"机制为核心。低模表面沿法线方向向外膨胀形成一个包裹网格，称为Cage。烘焙时，程序从Cage表面向内发射射线，与高模相交的点即为采样位置。Cage的膨胀量（Cage Offset）直接影响法线烘焙的准确性：数值过小会导致高模的部分几何体被遗漏，数值过大则会采样到错误的面，产生投影错误（Projection Error）。

xNormal支持导入自定义Cage文件（`.obj`格式），允许美术师手动调整Cage形状，解决标准膨胀算法在复杂凹凸区域产生的错误采样问题。这一功能是处理盔甲、武器等复杂硬表面模型时的关键手段。

### 主要烘焙贴图类型与参数

xNormal可一次输出以下多种贴图类型，常用设置如下：

- **法线贴图（Normal Map）**：采样精度建议设置为"Closest Point"或"Interpolated"，对应参数为`Closest Hit`模式。输出空间可选Tangent Space（切线空间，游戏引擎常用）或Object Space（物体空间，特效或程序化使用）。
- **环境光遮蔽图（AO）**：射线数量（Number of Rays）范围为64至512，数值越高噪点越少但计算时间呈线性增长。分布方式（Distribution）可选"Uniform"或"Cosine"，Cosine分布对漫反射材质更准确。
- **曲率图（Curvature Map）**：记录模型表面曲率，常用于Substance Painter中驱动污垢和磨损效果的生成蒙版。
- **位移图（Displacement Map）**：记录高模与低模之间的高度差，以32位EXR格式输出时精度最高。

### 批量烘焙与XML工程文件

xNormal使用`.xnml`格式保存工程配置，该文件本质上是一个XML文档，记录了高模路径、低模路径、输出贴图路径、分辨率和所有参数设置。利用这一特性，用户可以编写脚本批量修改`.xnml`文件中的路径节点，实现对整个角色资产包中数十个模型的自动化批量烘焙，无需逐一手动操作界面。

输出分辨率支持从256×256到4096×4096的标准尺寸，也可设置自定义尺寸。超采样（Supersampling/Antialiasing）选项提供1x、2x、4x三档，4x超采样会将内部渲染尺寸提升为目标分辨率的四倍后再缩小，有效消除法线贴图边缘的锯齿。

---

## 实际应用

**游戏角色武器烘焙**：制作一把游戏用刀具时，高模通常有50万至200万面，低模控制在500至2000面以内。在xNormal中，将高模和低模分别以`.obj`或`.fbx`格式导入对应槽位，设置Cage Offset为0.005至0.02个单位（根据模型尺寸调整），勾选法线图和AO图两个输出通道，设置分辨率为2048×2048，超采样4x，点击Generate Maps即可在数分钟内完成烘焙。

**批量环境道具烘焙**：场景组美术需要烘焙30个石块、木箱等道具的AO图。通过脚本批量生成30个`.xnml`文件，每个文件指向对应的高模和低模路径，再通过命令行调用`xNormal.exe -bna 配置文件.xnml`的方式依次执行，无需打开图形界面，可在离线服务器上完成过夜批量烘焙任务。

**Tangent Space法线贴图的引擎适配**：xNormal默认输出的法线贴图Y轴方向符合DirectX坐标系（绿通道朝下），而OpenGL引擎（如Unity的某些模式、Blender渲染器）要求绿通道朝上。在xNormal的Bake Options中勾选"Flip U"或"Flip V"即可切换，避免导入引擎后出现光照方向反转的问题。

---

## 常见误区

**误区一：Cage Offset越大烘焙结果越安全**

许多初学者认为把Cage设得足够大就能包住所有高模细节。实际上，过大的Cage会导致射线穿越高模后继续前进，采样到模型背面或相邻部件，产生明显的黑色漏光（Shadow Leaking）或法线方向错误。正确做法是将Cage设为刚好完整包裹高模所需的最小值，复杂区域使用手动绘制的自定义Cage文件。

**误区二：xNormal输出的法线图可以直接用于所有引擎**

xNormal输出的是标准切线空间法线贴图，但不同引擎对切线基（Tangent Basis）的计算方式存在差异。Unreal Engine 4使用MikkTSpace算法计算切线空间，若低模导出时未采用MikkTSpace标准（如从旧版Maya导出时未启用对应选项），烘焙结果在引擎中会出现接缝处法线不连续的问题。解决方法是确保导出低模时统一使用MikkTSpace，或改用Marmoset Toolbag进行烘焙以自动对齐切线空间。

**误区三：更高的AO射线数量总是必要的**

512条射线的AO烘焙时间约为64条的8倍，但对于低频、大面积遮蔽区域（如道具底部），128条射线的结果在视觉上与512条几乎无法区分。只有在需要捕捉细小缝隙（宽度小于1mm的刻痕）时，才有必要使用256条以上的射线数量。

---

## 知识关联

学习xNormal烘焙需要先掌握**法线烘焙**的基本原理，包括切线空间的定义、高低模拓扑对应关系以及UV展开规范——xNormal要求低模必须具备无重叠的UV布局，否则多个UV岛共享同一贴图区域会导致烘焙结果相互覆盖。

xNormal输出的贴图类型直接对接**Substance Painter**的纹理绘制工作流：AO图和曲率图可作为Substance中的烘焙资源导入，驱动智能材质中的边缘高光和污垢遮罩生成，无需在Substance内重复烘焙，节省大量计算时间。掌握xNormal的批量烘焙配置后，美术师可以将其整合进Pipeline自动化脚本，与版本控制系统和资产管理平台协同工作，构建完整的游戏资产生产流程。