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
---
# Gaea地形工具

## 概述

Gaea（发音为"Gee-ah"）是由QuadSpinner公司开发的专业程序化地形生成软件，2019年正式发布1.0版本。它采用节点图（Node Graph）工作流，允许设计师通过连接不同功能节点来构建复杂的地形生成管线，而非直接手绘高度图。Gaea的核心文件格式为`.tor`（Terrain Object Recipe），本质上是一份描述节点连接关系的配方文件，而非地形数据本身。

Gaea在关卡设计领域的重要性体现在它能够生成物理上可信的地形：山脉侵蚀、河流冲刷、岩石风化等自然过程均通过数学模拟实现。其输出的高度图分辨率最高支持8192×8192像素（8K），并可同步输出颜色图、法线图、粗糙度图等PBR贴图通道，直接对接虚幻引擎、Unity或Houdini等主流工具链。

相比World Machine等同类软件，Gaea的侵蚀模拟算法对水力侵蚀（Hydraulic Erosion）和风力侵蚀（Wind Erosion）的精度更高，能够自动生成沉积层（Sediment）数据，这些沉积数据可直接用于驱动材质混合权重，大幅节省手工绘制材质掩码的时间。

---

## 核心原理

### 节点图工作流与数据传递

Gaea的节点系统将地形生成过程拆解为三类节点：**原始体（Primitives）**、**变换器（Transforms）**和**输出器（Output）**。每个节点接收一个或多个高度场（Heightfield）作为输入，处理后输出新的高度场或遮罩（Mask）数据。节点之间的连线代表数据流方向，黄色连线传递高度场，蓝色连线传递遮罩数据。

典型的地形生成管线按顺序为：`Mountain`节点（生成基础山形）→ `Erosion`节点（模拟侵蚀）→ `Apex`节点（增加细节）→ `Colorizer`节点（生成颜色图）→ `Output`节点（导出文件）。任何一个节点的参数修改都会沿数据流方向向下自动重算，这种**非破坏性编辑**特性使设计师可以在任意阶段回溯调整。

### 侵蚀模拟的参数逻辑

Gaea的`Erosion`节点是整个软件最核心的模块，其内部包含水力侵蚀和热力侵蚀（Thermal Erosion）两套独立模拟系统。水力侵蚀的关键参数包括：
- **Duration（持续时间）**：值域0~1，控制侵蚀强度，过高会导致地形细节丢失
- **Downcutting（下切力）**：控制河道下切深度，直接影响峡谷的深度与宽度比
- **Sediment（沉积量）**：0~1范围内，数值越高沉积平原越明显

热力侵蚀的`Talus Angle`参数（休止角，单位为度）模拟碎石堆积角度，大多数岩石材质的自然休止角约为30°~35°，在Gaea中将此参数设置在该范围内可以获得最真实的山麓堆积形态。

### 导出流程与分辨率策略

Gaea的导出系统通过右键点击`Output`节点触发，核心设置包括**分辨率**、**位深**和**文件格式**三项。高度图必须使用**16位（16-bit）PNG或EXR格式**，8位PNG仅有256个高度阶，会在平缓地形上产生明显的阶梯状锯齿（Terracing Artifact）。

Gaea支持**变量分辨率预览**：在节点编辑阶段使用512×512分辨率快速迭代，仅在最终导出时切换到4K/8K。这通过`Build`菜单中的`Resolution`下拉菜单控制，整个导出过程在`Chokehold`模式下会利用CPU多核并行计算，一张8K高度图的完整侵蚀烘焙通常需要5~20分钟不等，具体取决于`Erosion`节点的`Duration`参数和CPU核心数。

导出的多张贴图（高度图、遮罩、颜色图）会自动以节点名称命名，例如`Erosion1_Height.png`和`Erosion1_Flow.png`，其中`Flow`通道记录了水流路径密度，可在虚幻引擎的Landscape Layer中直接用于驱动湿地植被分布。

---

## 实际应用

**对接虚幻引擎5的Landscape系统**：将Gaea导出的16位PNG高度图通过UE5的`Import Landscape`功能导入时，需要注意Gaea默认使用的高度值范围是-32768到32767，对应UE5中Landscape的`Z Scale`应设置为100（即1厘米精度）。若Gaea中设定地形高度为2000米，则UE5中对应的Z Scale = 200000/512 ≈ 390，需根据实际高度反推缩放比例。

**使用Gaea制作雪山关卡**：可在`Erosion`节点后接`Snow`节点，`Snow`节点通过坡度阈值（Slope Threshold）和高度阈值（Altitude Threshold）自动计算积雪覆盖区域，并输出`SnowMask`遮罩。该遮罩在虚幻引擎中可直接驱动材质层混合，实现雪线以上积雪、雪线以下裸岩的自然过渡，省去手工绘制权重图的工作量。

**批量生成地形变体**：Gaea的`Variables`系统允许将任意参数（如随机种子`Seed`）提升为外部变量，配合命令行工具`Gaea.Build.exe`可在CI流水线中批量烘焙数十种不同种子的地形变体，用于关卡设计的早期地形选型阶段。

---

## 常见误区

**误区一：认为8位PNG足以存储地形高度图**。新手常用Photoshop导出8位PNG作为高度图，导致虚幻引擎中出现明显的台阶状地形。Gaea原生导出的16位PNG包含65536个高度阶，能表达约0.15毫米级别的高度差，这在大型地形（如16km×16km）中对于避免视觉瑕疵至关重要。

**误区二：在高分辨率下直接进行全流程迭代**。在8K分辨率下预览节点效果会导致每次参数调整需要等待数分钟重算。正确做法是在Gaea的`Resolution`设置中使用"Preview: 512, Build: 4096"的分级策略——512分辨率下调整所有节点参数，确认效果后一次性执行高分辨率`Build`。

**误区三：将Gaea的颜色图直接用作最终材质**。`Colorizer`节点输出的颜色图是程序化生成的**原型色彩参考**，其目的是帮助设计师快速确认地形分区，而非替代引擎内的PBR材质系统。实际关卡制作中，Gaea的真正价值输出是高度图和各类遮罩（Flow、Wear、Deposit），这些数据才是驱动引擎内材质混合和植被分布的核心资产。

---

## 知识关联

Gaea地形工具建立在**程序化地形**概念的基础之上：理解噪声函数（如Perlin噪声、Worley噪声）如何生成基础高度场，有助于判断Gaea中`Mountain`、`Dunes`、`Badlands`等原始体节点各自适合模拟何种地貌类型——`Mountain`内部基于分形布朗运动（fBm），而`Dunes`则使用双向波动噪声模拟沙丘走向。

掌握Gaea的导出管线后，下一步实践方向是将Gaea与**虚幻引擎Landscape系统**或**Houdini程序化关卡管线**深度集成，利用Gaea输出的多通道遮罩数据自动化驱动植被散布、材质分层和水体放置，构建完整的程序化关卡资产工作流。Gaea的`.tor`文件也可以作为团队共享的"地形配方库"，不同关卡设计师复用同一套节点图但调整不同种子值，快速生成风格统一但形态各异的多块地形资产。
