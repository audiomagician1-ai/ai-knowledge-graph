---
id: "3da-bake-id-map"
concept: "ID贴图烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# ID贴图烘焙

## 概述

ID贴图（ID Map，全称 Material ID Map）是一种将三维模型的材质分区信息编码为纯色色块的特殊烘焙贴图类型。与法线贴图存储法线向量、AO贴图存储环境光遮蔽强度不同，ID贴图的每一个像素仅携带一条信息：**"该像素所在区域属于哪个材质分组编号"**。它本身不参与任何光照计算，是纯粹的分区索引图。

ID贴图的工业化普及时间节点明确：随着 Allegorithmic 公司于2014年正式发布 Substance Painter 1.0，ID贴图与"颜色选择遮罩（Color Selection Mask）"功能的组合被确立为 PBR 工作流的标准组件。在此之前，3A 美术师通常依赖多个 UV 集（Multi-UV Set）或手动框选多边形来区分材质，处理一个含12个材质分区的武器道具往往需要2～4小时。引入 ID 贴图后，同等复杂度的材质分配工作可在5～15分钟内完成，效率提升约10倍。

当前主流工具链（Marmoset Toolbag 4、Substance Painter 9.x、Blender 4.x 的 Cycles 烘焙器）均原生支持 ID 贴图烘焙，使其成为游戏美术和影视道具制作中不可跳过的工序节点。

---

## 核心原理

### ID贴图的两种生成来源

ID贴图的烘焙数据来源分为两类，各有适用场景：

**① 顶点颜色（Vertex Color）方式**

在高模或低模上直接为每组多边形刷上不同的顶点颜色，烘焙器将这些顶点颜色插值后写入贴图。在 Maya 2024 中可通过"网格显示 > 应用颜色"操作，在 Blender 中使用"顶点绘制（Vertex Paint）"模式完成。此方式的**优点**是无需额外创建材质球，流程极简；**缺点**是顶点颜色受顶点密度制约——在面数较少的低模（例如一个仅有48个顶点的子弹夹模型）上，相邻颜色区域交界处会出现插值渐变带，宽度可达2～5个像素，导致 Substance Painter 的颜色选取遮罩出现锯齿或漏选。

**② 多边形材质ID（Polygon Material ID）方式**

在低模上为不同面片分配不同的材质球（Material Slot），每个材质球的 Diffuse/Base Color 设置为一种纯色（如 #FF0000、#00FF00、#0000FF）。烘焙时软件直接将材质颜色写入对应像素，**边缘清晰，无插值渐变**。Marmoset Toolbag 4 的"Bake > Albedo"通道和 Substance Painter 的内置烘焙器"ID"通道均支持此方式，是专业流程中的首选方法。

### 颜色分配规则与RGB距离约束

ID贴图中每种颜色代表一个独立材质分区，颜色之间必须具备足够大的色相差异，以抵抗贴图压缩引入的颜色漂移。两种颜色在 RGB 色彩空间中的欧氏距离定义为：

$$d = \sqrt{(\Delta R)^2 + (\Delta G)^2 + (\Delta B)^2}$$

实践中，相邻两种 ID 颜色的 $d$ 值应不小于 **50**，以防止在 BC1/DXT1 格式压缩后两种颜色在解码端混淆。若项目要求贴图以未压缩 PNG 格式存储（常见于影视离线渲染流程），此约束可放宽至 $d \geq 25$。

六色标准分配方案（适用于最多6个材质分区）如下：

| 分区编号 | 颜色名称 | RGB值         | Hex     |
|----------|----------|---------------|---------|
| 1        | 纯红     | (255, 0, 0)   | #FF0000 |
| 2        | 纯绿     | (0, 255, 0)   | #00FF00 |
| 3        | 纯蓝     | (0, 0, 255)   | #0000FF |
| 4        | 纯黄     | (255, 255, 0) | #FFFF00 |
| 5        | 纯青     | (0, 255, 255) | #00FFFF |
| 6        | 品红     | (255, 0, 255) | #FF00FF |

若材质分区超过6个，可引入中间色（如橙色 #FF8000，$d$ 与纯红的距离 $= \sqrt{0+64^2+0} \approx 128$，安全可用），但需在 Substance Painter 的"颜色选取容差（Tolerance）"滑块中手动调整阈值至 30～60 之间。

### 烘焙设置中的关键参数

**输出格式选择**：ID贴图必须输出为 **PNG（8位或16位）** 格式，严禁使用 JPG。JPG 的 DCT 有损压缩会在颜色边界处产生8×8像素块状噪声（Blocking Artifact），导致 Substance Painter 在颜色选取时沿边缘出现宽达4～12像素的"杂色带"，破坏遮罩精度。

**烘焙分辨率选择**：ID贴图的推荐分辨率与模型在屏幕上的最终尺寸相关。游戏道具通常烘焙至 2048×2048，并以此分辨率直接在 Substance Painter 中使用（ID贴图本身不需要高分辨率来存储表面细节，但与法线贴图保持一致分辨率可简化工作流管理）。

**Marmoset Toolbag 4 烘焙通道设置**：在 Baker 面板中，烘焙类型选择"Albedo"而非"Normal"或"Ambient Occlusion"；勾选"Direct"输出而非"Cage"投影（ID贴图不依赖高低模对应关系，仅读取低模自身颜色）。

---

## 关键操作流程

以 Marmoset Toolbag 4 + Substance Painter 9 为例，完整的 ID 贴图烘焙流程如下：

```
1. [低模准备 - Maya/Blender]
   - 在低模上为每个材质分区分配独立材质球
   - 材质球 Diffuse 颜色设置为六色方案中的纯色
   - 确认低模 UV 展开完毕（UV无重叠）

2. [烘焙 - Marmoset Toolbag 4]
   - 导入低模 FBX（含材质颜色信息）
   - Baker > Add Bake Project
   - 输出通道: Albedo（烘焙类型选择 Full Color）
   - 格式: PNG, 分辨率: 2048×2048
   - 点击 Bake, 输出文件: mesh_id.png

3. [导入 - Substance Painter 9]
   - 新建项目时导入低模，贴图集尺寸设为 2048
   - Texture Set Settings > Baked Textures
   - 将 mesh_id.png 绑定至 "ID" 通道

4. [使用遮罩 - Substance Painter]
   - 添加 Fill Layer
   - 右键 Layer > Add Mask > Color Selection
   - 在弹出的颜色拾取器中点击 ID 贴图上的目标颜色
   - 遮罩自动生成，覆盖对应材质分区，误差 0 像素
```

---

## 实际应用

### 游戏武器道具的典型案例

以一把含有8个材质分区的现代步枪为例（枪管金属、枪托聚合物、瞄准镜玻璃、皮质护手、布料绑带、橡胶脚垫、铝制导轨、钢制弹匣），美术师在 Maya 中分配8个材质球，颜色分别为6种标准色加上橙色（#FF8000）和紫色（#8000FF）。烘焙输出的 ID 贴图在 Substance Painter 中直接生成8个颜色选取遮罩，对应8套不同的 PBR 材质参数（金属度、粗糙度、颜色变化），整个材质分配操作耗时约8分钟，而传统多边形手选方式处理同等复杂度需要约90分钟。

### 角色皮肤与织物的分区逻辑

角色模型的 ID 贴图分区通常遵循"材质物理属性聚类"原则：皮肤（SSS 材质）分配一种颜色，所有金属配件（扣环、拉链头）共用另一种颜色，布料部分（棉、丝、皮革）各占一种颜色。注意：**同一物理材质的不同颜色变体不需要分配不同的 ID 颜色**，颜色变体可在 Substance Painter 的颜色图层中通过叠加贴图实现，ID 贴图仅用于区分"材质类型"而非"材质颜色"。

### 与Trim Sheet流程的结合

在使用 Trim Sheet（瓷砖化细节贴图）的建筑或载具美术流程中，ID 贴图承担了额外的"表面材质指向"功能：烘焙出的 ID 颜色不仅用于选取遮罩，还可通过 Substance Painter 的"锚点（Anchor Point）"系统驱动不同 Trim 区域调用不同的 Smart Material，使单张 4096×4096 贴图集上最多可管理12种以上的 Trim 材质变体，而无需拆分贴图集。

---

## 常见误区

**误区1：将ID贴图的烘焙分辨率设为512或256**
ID贴图虽然内容简单，但分辨率过低会导致相邻颜色在 UV 边缘处像素级混合，使颜色选取遮罩在对应区域出现单像素宽的"漏色带"。即使最终游戏内使用的贴图是 512 分辨率，烘焙 ID 时也应使用 2048，之后在 Substance Painter 中导出时再降采样。

**误区2：用JPG格式存储ID贴图**
如前所述，JPG 的有损压缩会污染颜色边界。此错误在实践中极为常见，直接表现为 Substance Painter 颜色选取遮罩边缘出现宽达数像素的锯齿状杂色区域，修复方法只有重新以 PNG 格式烘焙。

**误区3：多个材质分区使用接近的颜色（如#FF0000与#CC0000）**
两者的 RGB 欧氏距离 $d = \sqrt{51^2 + 0 + 0} \approx 51$，刚刚达到安全阈值，但一旦经过 BC1 压缩，实际颜色误差可能超过此范围，导致 Substance Painter 误将两个分区识别为同一分区。应始终从六色标准方案出发，确保颜色差异直观可辨。

**误区4：在高模上烘焙ID贴图**
ID贴图的颜色来源于低模的材质球分配，若错误地将高模设为烘焙对象（即把高模的顶点颜色烘焙到贴图），会因高模通常不按材质分区分配颜色而得到纯灰色或错误颜色的输出。正确做法是：ID贴图始终从**低模自身**读取颜色，不涉及高模投影。

---

## 知识关联

**前置概念——烘焙概述**：ID贴图烘焙是所有贴图烘焙类型中最简单的一种，不涉及射线投影（Ray Casting）或光照计算，是理解法线贴图烘焙、AO烘焙的入门跳板。掌握了在 Marmoset Toolbag 中配置烘焙项目、设置输出格式和分辨率的基本操作后，烘焙 ID 贴图的额外学习成本接近零。

**横向关联——顶点颜色（Vertex Color）**：ID贴图的一种生成来源即为顶点颜色。两者在数据层面相同，区别在于顶点颜色存储在网格数据中（随模型文件传递），而 ID 贴图是将顶点颜色"固化"为独立的 2D 图像文件，便于在不携带原始网格的环境中使用（如在 Substance Painter 中工作时，软件不读取顶点颜色，只读取贴图文件）。

**横向关联——遮罩系统（Mask System）**：Substance Painter 的遮罩系统（Color Selection Mask、Black Mask、Smart Mask）是 ID 