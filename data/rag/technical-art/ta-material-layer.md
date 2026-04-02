---
id: "ta-material-layer"
concept: "材质分层"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 材质分层

## 概述

材质分层（Material Layering）是指在单一网格体上，通过高度图、遮罩贴图或材质函数叠加等手段，将多种独立材质按顺序混合堆叠的技术。与单层PBR材质不同，材质分层允许一个物体表面同时表现出金属划痕、污垢覆盖、湿润边缘等多种物理层次，每一层都持有自己完整的BaseColor、Roughness、Metallic、Normal等PBR通道数据。

这一技术在2010年代中期随着次世代主机（PS4/Xbox One时代）硬件算力提升而进入实时渲染工业流水线。虚幻引擎4在4.9版本正式引入"材质分层"（Material Layers）节点系统，允许美术师以堆栈方式管理多层材质，而非在一张巨大的材质图中手工连接所有逻辑。Substance Designer同期也通过"层叠栈（Layer Stack）"概念强化了离线分层制作流程。

材质分层的重要性在于它将"材质复用率"与"视觉复杂度"解耦。一套基础钢铁材质函数可以被铠甲、齿轮、武器共用，再通过各自的遮罩叠加锈迹、刮痕层，从而在不膨胀贴图数量的前提下大幅提升资产表现力。

---

## 核心原理

### 高度混合（Height-Based Blending）

高度混合是材质分层中最具物理直觉的过渡方式。其核心公式为：

$$\text{BlendWeight} = \text{clamp}\!\left(\frac{H_A - H_B + \text{Contrast}}{2 \times \text{Contrast}},\ 0,\ 1\right)$$

其中 $H_A$ 是下层材质的高度值，$H_B$ 是上层材质的高度值，Contrast控制两层之间过渡区域的锐利程度（典型值0.1–0.3）。这意味着上层材质只会"积聚"在凸起区域，而凹陷处保留下层材质——例如石头缝隙保留泥土、金属凸起保留光泽、凹坑积累锈斑，所有这些效果都是高度混合公式自动计算的结果，而不需要美术手绘遮罩形状。

### 遮罩层（Mask-Based Layering）

遮罩分层使用一张或多张单通道灰度贴图作为每层材质的可见性权重。一张RGBA遮罩贴图可以携带4个独立层的权重信息，对应4种不同材质（如：R=干净金属，G=锈迹，B=泥垢，A=积雪），这被称为"通道打包（Channel Packing）"策略，在单次纹理采样中节省3次额外采样开销。虚幻引擎中的`BlendMaterialAttributes`节点接受一个0–1的Alpha输入，正是对应这张遮罩的单通道数值。遮罩可以由手绘提供精确的艺术控制，也可以由顶点色（Vertex Color）实时驱动，以支持运行时动态变化（如角色沾上血迹时G通道权重实时增大）。

### 材质函数叠加（Material Function Stacking）

材质函数（Material Function）是虚幻引擎中封装了完整PBR参数输出的可复用节点模块，其输出类型为`MaterialAttributes`结构体，包含全部着色模型所需通道。分层时将多个材质函数的`MaterialAttributes`输出通过`BlendMaterialAttributes`按序叠加，上层函数的输出会覆盖或混合下层输出。关键规则是叠加顺序决定遮挡关系：排列在栈顶的函数优先级最高，但其Alpha（遮罩）为0的区域会完全透出下层，类似Photoshop的图层混合逻辑。在虚幻引擎5中，此系统被进一步封装为"Material Layer"与"Material Layer Blend"两类资产，可在材质实例界面中直接以拖拽方式管理层级。

---

## 实际应用

**角色装备的磨损表现**：以一套板甲为例，底层为镜面抛光金属材质函数，中层为边缘磨损划痕（依赖曲率烘焙贴图作为遮罩，曲率高值区域划痕层权重增大），顶层为污垢/血迹（由顶点色R通道驱动权重，场景触发后实时叠加）。整套甲胄只需一个材质实例即可覆盖全状态，而非为每种磨损程度制作单独贴图集。

**地形过渡混合**：开放世界地形通常使用4–8层地面材质（草地、泥土、砾石、雪地等），每层通过高度混合+手绘权重图共同决定最终混合比例。以虚幻引擎的Landscape材质为例，其`LandscapeLayerBlend`节点本质上就是材质分层系统的地形特化版本，每个Layer Weight对应一个分层遮罩通道。

**建筑外墙分层**：混凝土墙体可以拆分为：基础混凝土层→贴砖层（高度混合，砖块凸出区域权重为1）→水渍层（UV从上方垂直投影，越靠近地面权重越大）→苔藓层（AO值越高的凹陷区域权重越大）。这四层共同工作时，每层的法线贴图通过`BlendAngleCorrectedNormals`函数正确叠加，不会出现法线方向错误的闪烁问题。

---

## 常见误区

**误区一：将所有层直接线性混合**。初学者常用简单的`Lerp`节点以固定比例（如0.5）混合两层材质，结果是每一处表面都呈现两种材质的均匀混合，失去了高度混合应有的物理层次感。正确做法是将高度图信息代入上文公式推导出非线性权重，使过渡区域集中在合理的物理边界位置。

**误区二：遮罩层越多越好**。部分美术师会为一个物件叠加6–8层材质以追求细节丰富，但每新增一层都意味着额外的纹理采样和混合计算。在移动平台上，超过3层的材质分层会导致着色器指令数超过硬件限制（通常为128–256条ALU指令），造成编译失败或性能断崖。合理的做法是在PC平台不超过5层，移动平台不超过3层，并将低贡献度层通过通道打包合并。

**误区三：法线贴图直接用Lerp混合**。法线贴图的分量不能像颜色贴图那样直接线性插值，因为法线向量在插值后长度不再为1，并且切线空间方向会发生错误偏转。正确方法是使用`BlendAngleCorrectedNormals`材质函数（虚幻引擎内置，等效于Reoriented Normal Mapping算法），该函数将下层法线作为"参考切线空间"对上层法线进行重定向后再叠加。

---

## 知识关联

材质分层以PBR材质基础为前提，要求学习者已理解BaseColor、Roughness、Metallic、Normal各通道的物理含义及其取值范围（0–1线性空间或切线空间法线向量），因为分层操作的本质是对这些通道分别执行加权混合，不理解通道语义会导致混合结果出现物理上不合理的表现。

掌握材质分层后，下一步自然延伸到**材质混合技术**，后者关注运行时动态混合的着色器实现细节，包括Dithered LOD过渡、深度偏移混合等进阶算法，是材质分层在时序维度上的扩展。另一个延伸方向是**贴花系统（Decal System）**，贴花可以视为一种在世界空间投影的特殊材质层，与材质分层的UV空间遮罩形成互补：当需要跨多个不同网格体在同一位置叠加同一层材质（如弹孔、积水坑）时，贴花系统比网格内嵌的材质分层更高效。