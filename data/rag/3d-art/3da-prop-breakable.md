---
id: "3da-prop-breakable"
concept: "可破坏道具"
domain: "3d-art"
subdomain: "prop-art"
subdomain_name: "道具美术"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 可破坏道具

## 概述

可破坏道具（Destructible Props）是游戏和影视制作中一类特殊的3D美术资产，指在运行时能够产生碎裂、破损或物理解体效果的场景物件。与普通静态道具不同，可破坏道具需要同时维护"完整状态"与"破坏状态"两套视觉资产，并在触发条件满足时完成视觉切换或物理模拟。常见的可破坏道具包括木箱、陶罐、玻璃窗、石柱等，这类物件在动作类游戏中极大增强了场景交互感。

可破坏道具的制作工艺在游戏行业的发展与实时物理引擎密切相关。早期《毁灭公爵3D》（1996年）等游戏中仅通过贴图替换模拟破坏效果；到2000年代中期，Epic Games在《虚幻引擎3》中引入了Apex Destruction插件，使实时Voronoi破碎首次进入主流工作流；至2020年代，Unreal Engine 5的Chaos Physics系统已能支持数百个破碎碎片的实时刚体模拟。

掌握可破坏道具的制作对3D道具美术师至关重要，因为其资产规格、LOD策略和UV布局规则与普通道具存在本质差异——一个可破坏木箱的最终资产数量可能是同等普通道具的5至10倍，在制作初期若不考虑破坏状态，后期重做成本极高。

## 核心原理

### 预切割碎片（Pre-fractured Fragments）方法

预切割是离线阶段在DCC工具或引擎编辑器中手动或程序性地将完整模型切割为若干碎片的工艺。艺术家在Houdini中使用Voronoi Fracture节点，或在Blender中使用Cell Fracture插件，将模型分割为N个凸多边形碎片（Convex Hulls）。每个碎片需要独立的碰撞体、独立的网格，并在内表面（切割截面）生成新的UV区域以填充内部材质，例如木头的木纹截面、砖块的土芯截面。

预切割的碎片数量对性能影响显著：桌面平台单个可破坏道具通常控制在20至60个碎片，移动平台则压缩至8至16个。切割前需在Houdini中用Paint节点绘制"破碎密度图"，使受力点（如中心区域）的碎片更细碎、边缘区域碎片较大，从而产生自然的应力集中视觉效果。预切割资产在引擎中以静态网格集合形式存储，初始状态由所有碎片拼合还原为完整外形，触发后各碎片获得物理速度向量分裂飞出。

### 实时破碎（Runtime Fracture）方法

实时破碎指在游戏运行时根据撞击位置和力度动态计算切割平面，代表系统为Unreal Engine 5的Chaos Fracture和Houdini Engine的实时程序化破碎。实时破碎的核心算法仍基于Voronoi图，但切割种子点（Seed Points）的位置由撞击点坐标实时生成，因此每次破坏效果不完全相同，视觉多样性高于预切割方案。

实时破碎的主要代价是CPU计算开销，尤其是切割面的网格重建（Mesh Boolean）在运行时极为耗时。Chaos系统采用"几何集合"（Geometry Collection）数据结构预烘焙破碎层级（Fracture Hierarchy），将网格切割工作前置到编辑器，仅在运行时执行刚体分离与物理积分，从而将实时CPU开销控制在可接受范围内。几何集合支持多级破碎：Level 0为完整道具，Level 1为主碎块（约4至8块），Level 2为次碎块（约20至40块），根据撞击能量决定激活到哪一级。

### 内表面与材质处理

可破坏道具的截面（切割面）是制作中最容易被忽视的环节。所有预切割或实时破碎产生的内表面必须分配独立的Material Slot，通常命名为`M_Interior`，并赋予与外表面材质在物理逻辑上一致的内部贴图：石头道具内部使用暗色粗粒岩石纹理，陶器内部使用粗糙陶土纹理，金属容器内部可使用生锈或焊接痕迹贴图。若截面与外表面共用同一材质，破碎后会出现外表面贴图向内延伸的穿帮效果。

内表面UV通常采用Triplanar投影或程序化UV，因为切割面形状不规则，手工展UV效率极低。在Houdini Voronoi Fracture节点中勾选`Create Interior Polygons`并设置`Interior UVs`为`Planar from Axis`，可自动完成截面UV生成，为后续烘焙节省大量时间。

## 实际应用

**《对马岛之魂》风格木质障碍物**：制作时先在Houdini中完成Voronoi切割，碎片数量设为32块，用`Point Relax`节点调整种子点使碎片形状不均匀以避免机械感，导出为FBX后在UE5中建立Geometry Collection资产，为Level 1（8块大碎片）和Level 2（32块细碎片）分别设置`Damage Threshold`参数（分别为200N和500N），低能量撞击仅触发Level 1破碎，高能量爆炸触发完全解体。

**可破坏玻璃窗**：玻璃破碎需要模拟蜘蛛网状裂纹，预切割时在Houdini中使用`Shatter`节点并选择`Radial`模式，以中心为原点向外辐射切割，再叠加`Irregular`随机噪点。玻璃碎片厚度仅约4至6mm，LOD0使用完整几何碎片，LOD1和LOD2替换为Alpha Clip的平面玻璃碎片以降低多边形数量，从而在远处保持视觉效果同时节省显存。

**陶罐破碎粒子联动**：破碎触发瞬间除释放碎片刚体外，还需从撞击点生成粒子效果（灰尘、细碎颗粒）。UE5中在Geometry Collection的`On Break`事件中绑定Niagara特效，传递撞击点`Location`和`Normal`参数，使粒子朝撞击法线反方向喷射，增强视觉冲击感。

## 常见误区

**误区一：用完整道具模型直接破碎**。许多初学者直接对建模时的高面数完整模型执行Voronoi切割，导致每个碎片仍保留大量外表面细节，总面数可能从原始5000面膨胀到单道具80000面以上，在有10至20个同类道具同时破碎的场景中造成严重性能瓶颈。正确做法是为可破坏道具单独制作一套减面优化的"破碎专用低模"，面数控制在普通LOD0的1.5至2倍以内。

**误区二：忽略碎片的凸包限制**。物理引擎对刚体碰撞的计算依赖凸多边形近似（Convex Hull Approximation），若碎片包含明显的凹陷几何（如L形或U形截面），物理引擎会用包围盒近似替代，导致碎片相互穿插或堆叠异常。切割时应在Houdini中勾选`Remove Non-Manifold Geometry`并对每块碎片运行`Convex Decomposition`检查，确保所有碎片满足凸包条件或拆分为多个凸子体。

**误区三：破坏状态与完整状态共用一套UV**。部分美术师为节省时间，让破碎后碎片的外表面UV直接继承完整模型UV，在大多数道具上可行，但对带有完整图案的道具（如绘有花纹的陶罐、有完整标志的木箱）会出现图案在碎片上错位断裂的视觉错误。这类道具应使用`Tileable`平铺纹理而非单幅完整图案纹理，或在破碎节点中设置`Transfer UV`从完整模型向碎片重新映射UV坐标。

## 知识关联

可破坏道具建立在**道具美术概述**的基础上，要求艺术家已掌握普通道具的建模规范、LOD制作流程和材质球设置方式——可破坏道具的完整状态模型制作与普通道具完全一致，差异仅从切割环节开始引入。

在工具链层面，可破坏道具的预切割工作流深度依赖**Houdini程序化建模**知识，Voronoi Fracture、Attribute Transfer和Convex Decomposition节点是核心工具节点；实时破碎方案则需要熟悉**Unreal Engine Chaos Physics**的Geometry Collection编辑器和Field System（力场系统）的配置方式。物理材质参数（如`Damage Threshold`和`Mass`）的调整也与关卡设计团队的数值需求紧密协作，因此可破坏道具往往是3D美术师与关卡设计师跨部门沟通最频繁的资产类型之一。