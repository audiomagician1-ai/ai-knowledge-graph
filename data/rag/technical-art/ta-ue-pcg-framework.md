---
id: "ta-ue-pcg-framework"
concept: "UE PCG Framework"
domain: "technical-art"
subdomain: "pcg"
subdomain_name: "程序化生成"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# UE PCG框架：点线面生成与规则

## 概述

UE PCG框架（Procedural Content Generation Framework）是Unreal Engine 5.2版本正式引入的原生程序化内容生成系统，取代了早期依赖蓝图脚本或第三方插件（如Houdini Engine）来完成散点摆放的工作流程。它基于**数据流图（Graph-based Data Flow）**的架构，将场景内容的生成拆解为一系列可组合的节点操作，最终在编辑器内实时预览并烘焙到关卡中。

PCG框架最大的意义在于它将过去需要离线烘焙或运行时大量CPU计算的程序化逻辑，整合进了Unreal的**World Partition**与**HLOD**体系。这意味着开放世界中数百平方公里的植被、建筑废墟、道路碎石等元素，可以在玩家加载地图分块时动态生成，而不必事先手动摆放或预先烘焙静态网格。

对于技术美术而言，PCG框架提供了一套无需编写C++代码的可视化节点系统，同时又比普通蓝图拥有更高的批量处理性能——其底层采用多线程并行处理点集数据，单帧内可稳定处理百万级别的采样点。

---

## 核心原理

### 1. 点集（Point Cloud）作为通用数据载体

PCG框架中所有数据的传递单位是**PCGPoint**。无论是表面上的散布点、样条线上的等距采样点，还是体积内的密度点，最终在节点之间流动的都是PCGPoint的集合（PCGPointData）。每个PCGPoint携带以下属性：

- **Transform**：位置、旋转、缩放（3×4矩阵）
- **Density**：浮点数[0,1]，控制该点被后续节点保留的概率
- **BoundsMin / BoundsMax**：局部包围盒，用于碰撞检测与间距计算
- **Color**：四通道浮点，可存储任意用户自定义属性

技术美术可以通过**Attribute节点**在PCGPoint上附加自定义浮点、向量或整数属性，例如给每棵树附加`tree_type`枚举值，在后续的**Switch/Filter节点**中按类型分流处理。

### 2. 三类基础输入：面、线、体

PCG框架的采样源分三种基础几何类型：

**面（Surface/Landscape）采样**：`Surface Sampler`节点在静态网格或地形表面按泊松圆盘分布（Poisson Disk Distribution）生成点集，参数`Points Per Squared Meter`控制密度，`Point Radius`控制最小间距，两者共同决定最终点数量。对于4km×4km的地形，典型参数设置为0.1点/平方米、半径2m，约生成160万个候选点。

**线（Spline）采样**：`Spline Sampler`节点沿蓝图样条线组件等距采样，`Distance Between Points`参数单位为厘米。若设置为200cm，一条1000m长度的道路样条线将产生500个PCGPoint，每个点的X轴默认对齐样条切线方向，便于后续摆放路灯、护栏等线型资产。

**体（Volume）采样**：`Volume Sampler`节点在PCGVolumeComponent定义的包围盒内按三维网格或随机方式采样，常用于室内散布或悬浮粒子效果。体采样天然携带三维坐标，无需法线投影步骤。

### 3. 规则过滤与属性运算

PCG图的核心逻辑层是各类**Filter与Transform节点**：

- **Density Filter**：按Density阈值剔除点，配合`Self Pruning`节点实现基于距离的稀疏化
- **Projection节点**：将点集投影到地形碰撞上，修正Z轴高度并更新法线旋转——这一步骤对于面采样后需要贴合起伏地形的对象至关重要
- **Point Transform**：对点集施加随机旋转（RandomRotation范围可分轴设置）、随机缩放（支持均匀与非均匀分布），输出仍为PCGPoint集合
- **Grammar节点**（UE5.4新增）：引入L-System风格的字符串重写规则，允许对样条线段按规则替换为不同资产，实现建筑立面或道路节点的语法驱动生成

最终，`Static Mesh Spawner`节点读取PCGPoint的Transform并在关卡中实例化静态网格，底层自动使用**Hierarchical Instanced Static Mesh（HISM）**，保证GPU实例化合批。

---

## 实际应用

**开放世界植被覆盖**：在《Senua's Saga: Hellblade II》的地形制作流程中，PCG框架被用于基于地形材质图层（Landscape Layer Weight）驱动植被密度——`Get Landscape Layer Weight`节点输出[0,1]浮点值直接赋给PCGPoint的Density，配合Density Filter实现草地密集、岩石稀疏的自然过渡。

**道路边缘装饰**：沿公路样条线采样后，使用`Distance To Spline`属性结合`Math Expression`节点计算每个点到样条的垂直偏移量，再通过`Random Select`节点在三种护栏模型间以40%/35%/25%的权重随机选择，形成自然变化的道路边缘。

**建筑废墟散布**：PCGGraph可作为组件挂载到单个Actor上，配合`PCG Component`的`Generate On Volume`选项，在关卡编辑器中拖入一个废墟区域Box即自动在其内部按预定规则摆放碎石、残墙，美术人员修改Box缩放时生成结果实时刷新，迭代效率远超手动摆放。

---

## 常见误区

**误区一：PCGPoint的Density等同于透明度或可见性**
Density是[0,1]范围的浮点权重，它本身不控制任何视觉效果。`Density Filter`节点以Density作为随机保留概率的输入——Density=0.3意味着该点有30%概率通过过滤，而不是该点"半透明"或"半可见"。初学者常误将Density调低期望减少数量，却忘记连接Density Filter节点，导致所有点仍被全量实例化。

**误区二：PCG图等同于蓝图事件图，可以写循环逻辑**
PCG图是纯数据流图，节点之间传递的是点集批次，不存在逐点的For循环控制流。若需要条件分支，必须使用`Branch`或`Switch on Tag`节点将整条点流分叉，而非在单节点内部判断单个点的条件。将蓝图中`ForEach`的思维直接套用到PCG图会导致逻辑结构混乱。

**误区三：勾选"Regenerate on Volume Overlap"会自动处理LOD过渡**
该选项仅控制World Partition分块加载时是否重新触发生成计算，与HLOD或LOD切换无关。PCG生成的HISM实例使用静态网格资产自身的LOD设置，若原始网格未配置LOD，PCG不会自动生成简化模型，远距离仍会全精度渲染。

---

## 知识关联

从**程序化生成概述**过渡到PCG框架时，需要理解泊松圆盘采样（PCG Surface Sampler的底层算法）与纯随机均匀采样的区别：泊松圆盘保证任意两点距离不小于给定半径`r`，而均匀随机采样会产生明显的聚集与空洞，这一差异直接影响植被摆放的自然感。

PCG框架与Unreal的**Houdini Engine插件**形成互补关系：Houdini Engine擅长拓扑级别的网格程序化（建筑墙体生成、管道连接），PCG框架擅长大规模实例化散布与基于属性的过滤规则。实际项目中两者常协同——Houdini输出带有自定义属性的网格，PCG读取这些属性驱动散布逻辑。

随着UE5.4引入**PCG Graph Parameters**（将PCG图参数暴露给关卡编辑器细节面板），技术美术可以进一步开发面向关卡设计师的"黑箱"工具，设计师无需打开PCG图内部即可调节密度、资产列表等关键参数，这是PCG框架向工具化工作流演进的重要方向。