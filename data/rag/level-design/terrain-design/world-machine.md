---
id: "world-machine"
concept: "World Machine工具"
domain: "level-design"
subdomain: "terrain-design"
subdomain_name: "地形设计"
difficulty: 3
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# World Machine工具

## 概述

World Machine是由Stephen Schmitt于2003年首次发布的专业程序化地形生成软件，目前由Quadspinner公司持续开发维护。它采用基于节点的工作流程（Node-based Workflow），将地形生成过程拆解为独立的功能模块，用户通过连接"设备（Device）"节点来构建地形生成管线，最终输出高度图（Heightmap）、法线贴图、颜色贴图等多种格式的地形数据。

World Machine的核心价值在于它能够模拟真实地质过程——侵蚀、沉积、河流切割——从而生成具有自然感的地形，而不是依赖手动雕刻。虚幻引擎、Unity等主流游戏引擎均可导入World Machine生成的16位PNG或RAW格式高度图，分辨率最高支持8192×8192像素（专业版）。《地平线：零之曙光》《孤岛惊魂5》等大型游戏项目都曾使用World Machine参与地形资产生产。

对于关卡设计师而言，World Machine解决了手工地形雕刻难以产生宏观地质结构与微观侵蚀细节并存这一矛盾。通过调整少量参数，可以快速生成具有不同地貌特征的多个地形变体，大幅提升地形资产的生产效率与质量。

---

## 核心原理

### 节点系统与设备类型

World Machine的工作区称为"Device Workview（设备工作视图）"，每一个功能单元被称为设备（Device），分为以下几类：

- **生成器（Generator）**：负责创建初始地形数据，最常用的是"Advanced Perlin"噪波生成器和"Voronoi"细胞噪波。"Advanced Perlin"中的Octaves参数控制噪波叠加层数，通常设置为8层，每层频率以Lacunarity值（默认2.0）递增。
- **变换器（Transform）**：对高度数据进行数学运算，例如"Terrace"设备可以将连续坡度转化为阶梯状台地，模拟差异性岩层侵蚀结果。
- **自然过程（Natural Processes）**：最重要的是"Erosion"侵蚀设备，它通过模拟水流颗粒的运动来重塑地形。该设备输出三个通道：高度图、流水图（Flow Map）和磨损图（Wear Map），后两者常用于驱动地形材质混合。
- **组合器（Combiner）**：通过加法、乘法、遮罩等方式合并多个地形数据流，例如"Combiner"设备的"Add"模式可将两个高度场叠加。
- **输出器（Output）**：将处理结果写入磁盘，支持BMP、PNG（16位）、RAW、TIFF等格式。

### 侵蚀模拟的参数控制

Erosion设备中最关键的三个参数是：
- **Duration（持续时长）**：模拟侵蚀持续的"年份"，数值越大地形被磨蚀越深，山脊变得更圆润，默认值为0.2，通常调整范围在0.1至0.6之间。
- **Rock Softness（岩石软度）**：控制岩石被侵蚀的难易程度，硬岩（低值）会保留陡峭悬崖，软岩（高值）会产生更多圆滑丘陵。
- **Sediment Carry Amount（沉积物携带量）**：决定水流能携带多少沉积物，高值会在山谷低地形成明显的冲积扇地貌。

### 地形分辨率与世界尺度设置

在"Project Settings"中，**World Extents（世界范围）**决定地形对应的真实世界尺寸，单位为米。例如设置4096m×4096m意味着输出高度图的每个像素代表1米（当分辨率为4096×4096时）。**Terrain Height（地形高度）**参数设置高度图0~1数值范围对应的实际海拔差，设为2000m时，完全白色（值为1.0）代表海拔2000米，这一数值必须与引擎端导入设置严格对应，否则地形比例会失真。

---

## 实际应用

### 为虚幻引擎生成地形高度图

典型工作流程如下：

1. 在World Machine中新建工程，设置World Extents为8192m×8192m，Terrain Height为1000m，输出分辨率512×512（原型阶段）。
2. 使用"Advanced Perlin"生成基础山脉形状，连接至"Erosion"设备，Duration设0.3，模拟约5000次水流迭代。
3. 将Erosion输出的高度图接入"Clamp"设备，将海平面以下数据截断，再连接到"Height Output"节点，格式选16位PNG。
4. 在虚幻引擎中使用Landscape工具的"Import from File"功能导入，Scale Z值设置为100（对应World Machine中1000m高度，因UE以厘米为单位：1000m÷100cm = 100）。

### 利用Flow Map驱动材质混合

Erosion设备输出的Flow Map（流水图）记录了每个像素上历史水流强度，可在虚幻引擎的Landscape Material中作为混合权重使用：流水值高的区域（峡谷、河道）赋予湿润岩石或沙砾材质，流水值低的山脊顶部赋予裸岩或积雪材质，从而实现与地形生成逻辑高度吻合的自动材质分布，无需手工绘制任何材质权重层。

---

## 常见误区

### 误区一：输出分辨率越高越好

World Machine的Basic版本将输出分辨率限制在512×512，Standard版最高1024×1024，Professional版才支持4096×4096及以上。很多初学者在Basic版中尝试设置更高分辨率后发现输出被自动降采样，误以为是软件Bug。实际上512×512的高度图对应8192m的地形时，每像素代表16米，对于大型开放世界级别的地形精度已经足够，后期可在引擎内通过Landscape雕刻补充细节。

### 误区二：侵蚀Duration值越大地形越真实

将Duration设置为0.8以上时，侵蚀过度会导致所有山脉变成平滑的椭球状丘陵，失去尖锐山脊线，反而不像真实地形。真实山脉的侵蚀程度取决于其地质年龄，年轻山脉（如喜马拉雅）应使用0.1~0.2的低Duration值保留棱角，古老山脉（如阿巴拉契亚）才适合使用0.4~0.6的高值。

### 误区三：World Machine的坐标原点与引擎一致

World Machine的地形数据以左下角为原点输出，而虚幻引擎Landscape的导入原点位于左上角，两者Y轴方向相反。若不在World Machine的"Height Output"设置中勾选"Flip Y Axis"选项，导入引擎后地形会在Y方向产生镜像翻转，导致基于地形预设计的关卡布局与实际地形不符。

---

## 知识关联

### 与程序化地形基础概念的衔接

学习World Machine前需要理解程序化地形的基础概念，包括高度图的数据本质（单通道灰度图，8位或16位精度）、柏林噪波（Perlin Noise）的频率与振幅关系，以及分形叠加（fBm，Fractional Brownian Motion）原理。World Machine的"Advanced Perlin"生成器实质上就是可视化的fBm参数控制界面，其中"Octaves""Lacunarity""Gain"三个参数直接对应fBm公式中的迭代次数、频率倍增系数和振幅衰减系数。

### 向引擎地形工具的延伸

掌握World Machine后，自然过渡到在虚幻引擎Landscape编辑器或Unity Terrain工具中对导入的高度图进行二次精修——World Machine负责宏观地质结构与侵蚀细节，引擎内雕刻工具负责关卡功能性细节（道路切割、战斗平台、遮蔽物放置点）。这种分工使得地形生产流程在艺术质量与设计可控性之间取得平衡，是当前AA至AAA级游戏项目的主流地形制作管线。