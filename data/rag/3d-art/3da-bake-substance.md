---
id: "3da-bake-substance"
concept: "Substance烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: true
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Substance Painter 内置烘焙器

## 概述

Substance Painter 是由 Allegorithmic 公司（2019年被 Adobe 收购）开发的 PBR 纹理绘制软件，其内置烘焙器自版本 1.x 起便集成在工作流程中，允许美术师在不离开软件的情况下直接完成从高模到低模的多种贴图烘焙。与 Marmoset Toolbag 或 xNormal 等外部烘焙工具相比，Substance Painter 的烘焙结果会直接绑定到当前项目的网格同步（Mesh Sync）系统中，烘焙完成后立即可用于图层和智能材质。

Substance Painter 的烘焙模块支持一次性输出多达 10 余种贴图通道，包括 Normal、World Space Normal、Ambient Occlusion、Curvature、Position、Thickness、ID 等。这一特性使其在影视预渲染外包和游戏资产制作中被广泛采用，因为单次烘焙即可生成 Smart Material（智能材质）所需的全部输入数据，显著减少重复操作。

## 核心原理

### 高低模配对与匹配规则

Substance Painter 使用基于命名后缀的自动配对机制来匹配高模（High Poly）与低模（Low Poly）。默认规则是：低模网格的名称加上 `_high` 后缀即视为其对应的高模部件。例如，低模命名为 `Body`，则高模需命名为 `Body_high` 才能被自动识别。用户也可在烘焙面板的 **Match** 选项中切换为 `Always`（忽略命名直接全部匹配）或 `By Mesh Name`（严格按名称匹配），适应不同的项目命名规范。

### 烘焙分辨率与抗锯齿设置

Substance Painter 烘焙面板提供 **Output Size** 选项，可独立于当前项目纹理分辨率设置烘焙分辨率，最高支持 4096×4096 像素。**Antialiasing** 下拉菜单提供 None、2x、4x、8x 四个超采样级别，其中 4x 是多数游戏资产的推荐默认值，可在烘焙时间和边缘质量之间取得平衡。**Max Frontal / Rear Distance** 两个参数控制射线投射的笼（Cage）前后范围，直接影响投影接触面是否产生浮动或漏穿缺陷，需根据高低模间距手动微调。

### ID 贴图烘焙的颜色生成方式

Substance Painter 的 ID Map 烘焙支持三种颜色来源：**Mesh ID/Polygroup**（按多边形组着色）、**Vertex Color**（读取高模顶点色）和 **Material ID**（读取高模材质槽颜色）。选用 Vertex Color 模式时，软件直接从导入的 FBX 或 OBJ 高模中读取顶点颜色属性，不需要额外的材质设置，是 Blender 到 Substance 工作流中常见的做法。生成的 ID 贴图用于在 **Polygon Fill** 工具中按区域快速蒙版，配合颜色选择器实现一键区域遮罩。

### 环境光遮蔽（AO）的专属参数

Substance Painter AO 烘焙提供 **Quality** 滑块（范围 1–64，代表每像素光线采样数）和 **Max Distance** 参数（单位与场景单位一致）。将 Quality 设为 64 可消除大多数噪点，但烘焙时间会相对线性增加。**Ignore Backface** 选项若开启，会忽略来自模型背面的遮蔽射线，适用于单面植被卡片等特殊资产。

## 实际应用

在游戏角色制作流程中，美术师通常在 ZBrush 完成高模雕刻后导出为 FBX，在 Maya 或 Blender 制作低模并展 UV，将两者一同导入 Substance Painter 项目。在烘焙面板中勾选 Normal、AO、Curvature、Position、Thickness、ID 六个通道，以 2048×2048 分辨率、4x 抗锯齿执行单次烘焙，耗时通常在 30 秒至 3 分钟之间（取决于面数）。烘焙完成后，Curvature 贴图自动驱动智能材质的边缘磨损效果，Position 贴图驱动从上到下的渐变污迹，大幅提升材质细节的自动化程度。

在武器道具制作中，ID 贴图通常通过材质槽方式生成：在 Maya 中为枪托、枪管、金属件分别指定不同颜色的 Lambert 材质，高模导出时保留材质信息，Substance 烘焙时选择 **Material ID** 模式，最终生成区域清晰的色块 ID 图，方便后续对不同金属区域独立调色。

## 常见误区

**误区一：认为 Substance 烘焙的 Normal Map 方向与外部工具完全相同**
Substance Painter 默认输出 **OpenGL 方向**（Y 轴向上为绿色高光）的法线贴图，而 DirectX 方向（Y 轴向上为绿色低谷）在某些引擎（如早期 Unreal Engine 4 项目）中需要翻转 G 通道。若直接将 Substance 烘焙的法线贴图用于 DirectX 工作流却未翻转，模型凹凸关系将整体反转。导出时需在 Substance 的 **Shader Settings** 中切换 Normal Map Format，或在引擎端处理。

**误区二：认为提高 Output Size 就等于提高烘焙精度**
烘焙分辨率影响的是贴图的存储精度，但高低模之间的投影质量由射线数量（AO 的 Quality 参数）和笼距离（Max Frontal/Rear Distance）决定。在 512 分辨率下将 Quality 设为 64 得到的 AO 比在 4096 分辨率下 Quality 为 1 时仍要干净得多，两者作用机制完全不同。

**误区三：认为 `Always` 匹配模式适用于所有场景**
当低模 FBX 文件中包含多个独立零件（如角色身体、头发、装备），使用 `Always` 模式会让所有高模同时向所有低模投影，造成不同部件相互污染，在部件边缘产生明显的投影错误。正确做法是在多零件场景中使用 `By Mesh Name` 并严格遵守 `_high` 后缀命名规范。

## 知识关联

学习 Substance 烘焙需要预先掌握法线烘焙的基础原理，包括切线空间法线贴图的 RGB 通道编码方式（R=X 切线方向，G=Y 副法线方向，B=Z 法线方向）以及高低模拓扑要求。理解了法线烘焙的射线投射原理后，Substance 中 Max Frontal/Rear Distance 参数的含义才能准确把握，否则调参时只能靠试错。

Substance 烘焙生成的 Curvature 和 Position 贴图是后续使用 Smart Material（智能材质）和 Smart Mask（智能遮罩）的数据基础。Curvature 贴图存储每个像素的曲率信息（凸起为白色，凹陷为黑色），Smart Mask 通过对其进行阈值判断自动生成磨损遮罩；Position 贴图存储模型在包围盒内的归一化 XYZ 坐标，驱动方向性污迹效果。掌握烘焙质量控制后，上述所有高级材质技术才能稳定发挥效果。
