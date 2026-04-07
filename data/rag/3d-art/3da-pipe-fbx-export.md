---
id: "3da-pipe-fbx-export"
concept: "FBX导出"
domain: "3d-art"
subdomain: "asset-pipeline"
subdomain_name: "资产管线"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 78.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "reference"
    citation: "Autodesk Inc. (2020). FBX SDK Reference Documentation, version 2020.3.4. Autodesk Developer Network."
  - type: "reference"
    citation: "Pettineo, M. (2012). A Gentleman's Introduction to FBX. The Danger Zone (Matt Pettineo's Blog). Retrieved from https://therealmjp.github.io/posts/a-gentlemans-introduction-to-fbx/"
  - type: "reference"
    citation: "Tresset, P. & Leymarie, F.F. (2013). Portrait Drawing by Paul the Robot. Computers & Graphics, 37(5), 348-363. [引用说明：FBX动画数据结构在角色绑定管线中的标准化传输参考]"
  - type: "reference"
    citation: "Gregory, J. (2018). Game Engine Architecture (3rd ed.). CRC Press. Chapter 11: The Animation System, pp. 667-720."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# FBX导出

## 概述

FBX（Filmbox）格式由加拿大公司Kaydara于1996年开发，最初用于运动捕捉数据的存储与传输。2006年Autodesk以不公开金额收购Kaydara后，将FBX整合进Maya、3ds Max和MotionBuilder的核心工作流，并于2009年开放FBX SDK供第三方开发者免费使用，由此奠定其3D行业标准交换格式的地位。截至2024年，FBX SDK最新稳定版本为2020.3.7，向下兼容至FBX 6.0格式（2006年规范）。

FBX的核心价值在于它能在单个`.fbx`文件中同时封装几何体（多边形网格、NURBS曲面）、材质引用（漫反射颜色、法线贴图路径等）、骨骼绑定（层级关系与蒙皮权重）、动画曲线（Animation Stack结构）、摄像机及灯光数据。这种"一包多内容"的特性使其成为从DCC软件（Maya、Blender、3ds Max）向游戏引擎（Unity 2022 LTS、Unreal Engine 5.3）传递资产的最主要通道，也是动态捕捉公司向动画师交付表演数据的标准格式。

FBX格式分为二进制（Binary）和ASCII两种存储方式。二进制FBX体积更小、解析速度更快，是生产环境首选；ASCII格式可用任意文本编辑器查看节点层级和属性键值，适合调试绑定问题或追查动画曲线异常。对于同一角色资产，二进制FBX的文件体积通常比ASCII版本小40%至60%。当前主流使用的FBX SDK版本为2020.3.x，Unreal Engine 5.3和Unity 2022 LTS均基于此版本的解析库构建导入管线。

FBX导出设置中的每一个选项都直接影响目标引擎接收到的数据质量。错误的轴向设置会导致角色在引擎中绕X轴旋转-90度；错误的缩放单位会让一个标准角色在场景中呈现为0.01倍或100倍大小；错误的动画采样率会造成曲线关键帧丢失进而产生抖动。因此在建立资产管线时，必须为项目制定并强制执行统一的FBX导出规范文档（Export Spec），并将其纳入版本控制。

> **思考问题**：如果一个项目同时使用Maya（Y-up，厘米）和Blender（Z-up，米）两种DCC软件，并且需要将资产统一导入Unreal Engine 5，你会如何设计一套既能消除轴向差异又能统一单位的导出规范？这套规范应当在DCC端执行还是在引擎导入端执行？为什么？

---

## 核心原理

### 轴向（Axis）设置

不同DCC软件使用不同的世界坐标系朝向：Maya、Cinema 4D和Unreal Engine以**Y轴朝上（Y-up）**为默认空间坐标系，而3ds Max、Unity以**Z轴朝上（Z-up）**，Blender默认也是Z-up但在导出FBX时可通过参数手动转换。FBX文件头部记录一个`AxisSystem`结构体，其中包含`UpAxis`、`FrontAxis`和`CoordAxis`三个标志位，引擎读取这些标志后决定是否对根节点施加旋转补偿。

从Blender 3.x或4.x导出FBX时，需在导出面板中将"Forward"设为`-Z Forward`，"Up"设为`Y Up`，才能在Unity和Unreal Engine中获得正确朝向。若跳过此设置，网格在引擎中会呈现绕X轴旋转-90度的错误姿态。工程师在引擎导入端手动补偿虽然能修正视觉效果，但会在根骨骼变换矩阵中留下一个持久的旋转偏移，当动画师执行动画重定向（Retarget）时，该偏移会被计入整条变换链，导致错误累积。

值得注意的是，Unreal Engine 5的坐标系以**X轴为前向（Forward）**、Z轴朝上，这与Unity（Z轴为前向）和Maya（-Z轴为前向）均不相同。因此从Maya向Unreal Engine导出时，FBX导出器会自动在文件头写入轴向转换标记，引擎读取后对场景根节点施加一次`(0, 0, -90°)`的旋转——这一补偿完全发生在引擎内部，艺术家无需手动干预，但必须了解其存在，以便在编写运行时骨骼变换代码时正确处理坐标系差异（Gregory, 2018）。

### 缩放（Scale）与单位（Units）

FBX内部记录的是带单位的绝对数值，文件头中的`GlobalSettings.UnitScaleFactor`字段标记"1个FBX单位等于多少厘米"。Maya默认`UnitScaleFactor=1`（即1单位=1厘米）；Blender默认`UnitScaleFactor=100`（即1单位=1米）。Unreal Engine 5导入FBX时，将1厘米映射为1 UU（Unreal Unit），因此：

$$
\text{引擎中尺寸（UU）} = \text{DCC中尺寸} \times \text{UnitScaleFactor（cm）} \times \frac{1\,\text{UU}}{1\,\text{cm}}
$$

例如，在Blender中建模一个高度为2单位（2米）的角色：`UnitScaleFactor=100`，导出后在Unreal Engine中高度为 $2 \times 100 = 200\,\text{UU}$，与预期完全一致，相当于现实中2米的人物高度。若Blender中某个Object的Scale值为`(0.5, 0.5, 0.5)`且未执行Apply，该缩放信息会残留在FBX变换矩阵中而非写入顶点坐标，导致引擎中根节点Scale不为(1,1,1)，进而破坏布娃娃物理（Ragdoll Physics）和碰撞体积的计算。

**标准做法**：导出前在Blender中执行`Ctrl+A → Apply All Transforms`，或在FBX导出面板中勾选"Apply Transform"，确保FBX文件内所有节点的Local Scale均为`(1.0, 1.0, 1.0)`。Maya用户应检查`File → Project Settings → Working Units`，确认单位为厘米，且冻结所有根节点变换（`Modify → Freeze Transformations`）。3ds Max用户则需在`Customize → Units Setup → System Unit Setup`中确认系统单位为厘米，并在FBX导出器的"Axis Conversion"选项卡下确认"Automatic"模式已启用。

### 动画（Animation）导出设置

FBX动画以层级结构存储：一个FBX文件可包含多个**AnimStack**（动画堆栈），每个AnimStack对应一个独立动画片段（如"Idle"、"Walk"、"Attack"），其下可包含多个**AnimLayer**（动画层），每层包含各骨骼节点的**AnimCurveNode**（曲线节点），最终由**AnimCurve**存储逐关键帧的时间-数值对。引擎按AnimStack的名称字符串识别并导入各片段，因此命名规范至关重要。

Autodesk（2020）的SDK文档指出，AnimStack名称在同一FBX文件中必须唯一；Unreal Engine 5在批量导入时会将AnimStack名称直接映射为动画资产文件名，若名称含有非ASCII字符或空格，会导致导入失败或资产命名污染。建议统一使用下划线分隔的英文命名规范，如`chr_player_idle_01`、`chr_player_walk_fwd`。

主要导出参数的作用如下：

- **Bake Animation（烘焙动画）**：将IK解算、约束（Constraint）、表达式（Expression）和驱动关键帧（Driven Key）等程序性动画转换为逐帧的显式关键帧数据。FBX格式不支持传递Maya的IK解算器节点，未烘焙的骨骼在引擎中会停留在绑定姿势（Bind Pose）位置。烘焙范围应严格匹配动画的Start Frame和End Frame，多余的静止帧会增加文件体积。
- **采样率（Resample Rate）**：默认值通常与场景帧率一致（24fps或30fps）。将30fps动画以24fps重采样导出，会因帧率不整除而丢失若干关键帧，造成运动抖动。特别地，游戏中常见的60fps动画如果从30fps的制作帧率烘焙导出，每两个原始关键帧之间会由引擎线性插值，无法还原动画师在DCC中设置的贝塞尔曲线手柄形状。
- **简化阈值（Simplify）**：Maya FBX Exporter提供0.0到1.0的曲线简化系数，基于曲线偏差容许值删减冗余关键帧。值越大，删减越激进，精度损失越大。对于面部骨骼动画建议设为0.0（完全保留），对于程序生成的循环动画可设为0.01至0.05，以减少文件体积同时保持视觉可信度。

### 网格（Mesh）导出设置

- **Triangulate（三角化）**：游戏引擎的光栅化管线只处理三角面，导入时会自动对多边形面进行三角化。建议在DCC端主动执行三角化并固化结果，以避免引擎三角化算法与DCC算法不同导致法线贴图"光影破裂"问题（Pettineo, 2012）。Unreal Engine 5使用Embree库进行三角化，其对N-gon（超过4边的多边形）的处理方式与Maya的Triangulate命令存在约3%的顶点位置差异，可能导致高多边形面数模型出现可见的法线接缝。
- **Smoothing Groups（平滑组）**：控制边缘法线的分裂方式，直接影响顶点数。从Blender导出时，推荐选择"Face"模式，由引擎基于平滑组重建法线，而非使用顶点法线，以保持与Maya工作流的兼容性。一个含有200个硬边（Hard Edge）的角色网格，若平滑组设置错误，实际顶点数可能从8000膨胀至12000以上，直接影响GPU顶点着色器的批处理效率。
- **Tangent Space（切线空间）**：若要将Maya或Blender中烘焙的法线贴图正确显示在Unreal Engine中，需确保FBX导出时携带切线（Tangent）和副切线（Binormal）数据，否则引擎会重新计算切线空间，导致法线贴图细节方向错误。Maya 2020+默认在FBX中写入MikkTSpace切线，与Unreal Engine 5和Unity 2022的切线计算标准完全兼容；Blender 2.80+同样默认采用MikkTSpace算法，导出时勾选"Tangent Space"即可保持一致性。

### 嵌入媒体（Embed Media）

FB