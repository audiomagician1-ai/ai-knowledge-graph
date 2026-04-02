---
id: "gaea-terrain"
concept: "Gaea地形工具"
domain: "level-design"
subdomain: "terrain-design"
subdomain_name: "地形设计"
difficulty: 3
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Gaea地形工具

## 概述

Gaea（全称 Quadspinner Gaea）是由 Quadspinner 公司开发的专业程序化地形生成软件，于2019年正式发布1.0版本。与同类工具World Machine相比，Gaea采用节点图（Node Graph）架构，允许设计师通过连接不同功能节点来构建完整的地形生成管线，每个节点代表一种地形处理操作，如侵蚀、沉积、噪声生成等。

Gaea的核心优势在于其物理模拟侵蚀系统。该软件内置了水力侵蚀（Hydro Erosion）、热侵蚀（Thermal Erosion）和风蚀（Wind Erosion）三种独立的地质模拟算法，能够在有限的计算时间内生成具有地质真实感的地形特征，例如河谷、冲积扇、崖壁纹理等。这使其成为开放世界关卡设计中生成自然地貌的首选工具之一。

在关卡设计工作流中，Gaea通常承担地形高度图的生成与烘焙任务。设计师在Gaea中完成地形造型后，将结果以16位或32位PNG/EXR格式导出，再导入到Unreal Engine、Unity或Houdini等引擎中进行进一步处理。Gaea本身不包含实时渲染功能，其定位是离线地形制作工具。

---

## 核心原理

### 节点图工作流与数据流向

Gaea使用有向无环图（DAG）结构组织地形操作。每个节点接收一个或多个高度图（Heightmap）或遮罩（Mask）作为输入，输出经处理后的数据传递给下游节点。节点分为三大类：**生成节点**（如Mountain、Voronoi、Gradient）、**处理节点**（如Erosion、Blur、Warp）和**输出节点**（如Export、SatMap、Colorizer）。节点图从左向右读取，最终在Build节点触发完整烘焙。

连接节点时，高度数据以归一化浮点值（0.0–1.0）在节点间传递，代表地形最低点到最高点之间的相对高度。在导出阶段，Gaea会将这个0–1范围映射至实际高度值，具体由"World Scale"参数控制，默认单位为米，典型设置范围为500m至4000m。

### 侵蚀系统参数详解

Gaea的Erosion节点是整套工具中最关键的处理环节。水力侵蚀模拟使用粒子化水流模型，核心参数包括：

- **Duration**：控制侵蚀时间强度，范围0–1，数值越高侵蚀越深，河道越明显
- **Downcutting**：控制水流向下切割的倾向，高值产生深V型峡谷，低值产生宽缓河谷
- **Inhibition**：抑制侵蚀的阻力参数，模拟岩石硬度差异
- **Sediment**：沉积物携带量，影响冲积扇和三角洲的形成程度

热侵蚀（Thermal）节点主要影响坡面崩解，其**Talus Angle**参数（默认33度）决定了碎石堆积的自然休止角，超过此角度的坡面将产生碎石滑落效果。两种侵蚀节点通常配合使用：先运行热侵蚀塑造宏观坡面，再运行水力侵蚀刻画细部水系。

### 遮罩系统与图层控制

Gaea支持通过遮罩（Mask）节点对地形的特定区域施加差异化处理。遮罩本质上是一张灰度图，白色区域代表全强度应用，黑色区域代表不应用。设计师可以使用**SlopeMask**节点根据坡度自动生成遮罩，或使用**HeightMask**节点按高度分层。

例如，若需要山峰区域有雪地效果而山谷保持裸岩，可以将HeightMask节点的输出连接至Colorizer节点的控制端，使颜色图层仅在指定高度区间显示白色雪地纹理。这套遮罩逻辑在Gaea导出的颜色贴图（Color Map）中也会被保留，可直接用于引擎内的材质混合权重图。

---

## 实际应用

**开放世界地形生成流程示例**：在《原神》或Unreal Engine 5开放世界项目中，典型的Gaea工作流程如下：

1. 使用**Mountain**节点或**Voronoi**节点生成基础地形轮廓
2. 通过**Warp**节点添加随机扭曲，破坏噪声的规律性
3. 依次添加Thermal Erosion和Hydro Erosion节点进行地质模拟
4. 使用**Apex**节点（Gaea 1.3版本引入）进行高频细节强化
5. 添加**SatMap**节点生成带有地质色彩的颜色图
6. 在Build Manager中设置分辨率为4096×4096，触发完整烘焙
7. 将输出的16位PNG高度图导入UE5的Landscape系统

Gaea支持**Tiled Export**（切片导出）功能，可将单张地形拆分为最多32×32的切片网格，每块切片对应引擎中的一个Landscape Component，适用于超大地图（如100km²以上）的制作需求。

**与Unreal Engine的桥接**：Gaea 1.3+版本内置了UE5 Landscape的参数预设，导出的高度图分辨率会自动对齐至UE5 Landscape支持的合法分辨率（如505、1009、2017、4033像素），避免导入时出现拉伸变形问题。

---

## 常见误区

**误区一：认为更高的侵蚀Duration值总能产生更真实的效果**
实际上，Duration值过高（接近1.0）会导致地形被过度侵蚀，山峰被削平、河道过深，反而失去地形的宏观轮廓感。专业设计师通常将Hydro Erosion的Duration设置在0.3–0.5之间，并通过多个低强度侵蚀节点的叠加来逐步细化，而非依赖单个高强度侵蚀节点。

**误区二：将Gaea输出的颜色图（Color Map）直接作为地形材质纹理使用**
Gaea的SatMap和Colorizer节点输出的是基于地质高度和坡度的程序化着色图，其分辨率和细节密度不足以作为最终材质纹理。正确用法是将其作为**混合权重图（Blend Weight Map）**导入引擎，驱动多层材质（如岩石、泥土、草地、雪地）之间的混合比例，材质本身的细节纹理仍需在引擎内单独赋予。

**误区三：忽略World Scale参数导致引擎内比例失真**
如果Gaea中World Scale设置为1000m，但在UE5 Landscape导入时Z轴缩放设置不匹配，山脉高度将严重失真。正确做法是：Gaea World Scale（单位m）× 100 = UE5 Landscape的Z Scale参数（单位cm）。例如World Scale=1000m，则UE5中Z Scale应设为100000cm。

---

## 知识关联

学习Gaea地形工具需要具备**程序化地形**的基础认知，包括理解高度图的灰度值与地形高度之间的映射关系，以及噪声函数（Perlin Noise、Voronoi）如何生成初始地形轮廓。没有这些概念的铺垫，初学者难以理解为何同一个Mountain节点在不同Scale参数下会产生截然不同的地貌特征。

Gaea是地形设计流程中从"概念地形"到"可用高度图"的生产工具。完成Gaea制作后，关卡设计师通常需要进一步学习引擎内的**Landscape材质系统**（如UE5的Layer Blend材质节点）以及**植被自动散布工具**（如UE5的Procedural Foliage Volume），才能将裸高度图转化为完整的可游玩关卡场景。Gaea输出的遮罩图在这一阶段可直接复用，作为植被分布的控制依据。