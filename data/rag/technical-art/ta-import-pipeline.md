---
id: "ta-import-pipeline"
concept: "导入管线"
domain: "technical-art"
subdomain: "pipeline-build"
subdomain_name: "管线搭建"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 导入管线

## 概述

导入管线（Import Pipeline）是指将外部三维资产文件（如 FBX、glTF）读取进游戏引擎或实时渲染环境时，对缩放比例、坐标系方向、材质槽位映射等属性进行标准化处理的一套规范化流程。其本质是在 DCC 工具（Maya、Blender、3ds Max）产出的文件格式与引擎内部数据结构之间建立可预测的转换规则，确保同一批资产在任意团队成员的机器上导入后得到完全一致的结果。

FBX 格式由 Autodesk 于 1996 年收购 Kaydara 后接管，至今仍是游戏行业最主流的中间格式；glTF 2.0 由 Khronos Group 于 2017 年正式发布，被设计为"三维领域的 JPEG"，内嵌 PBR 材质描述，正在逐步成为实时渲染的首选开放格式。这两种格式在坐标系约定、单位体系和材质表达方式上均存在差异，导入管线必须针对每种格式分别制定处理策略。

在大型项目中，若导入管线缺乏标准化，一个常见后果是模型导入后体积偏差 100 倍（DCC 工具以厘米为单位，而引擎以米为单位时未做换算），或角色骨骼的 Y/Z 轴翻转导致动画整体颠倒。提前制定导入管线规范，可以将此类返工成本从单次数小时压缩至秒级自动修正。

---

## 核心原理

### 单位与缩放标准化

FBX 文件内部存储了一个 `UnitScaleFactor` 属性，常见值为 1.0（厘米）或 100.0（米）。Unreal Engine 5 的内部单位是厘米，而 Unity 的内部单位是米。当一个在 Maya 中以厘米建模、导出时 `UnitScaleFactor=1` 的 FBX 被导入 Unity 时，若未勾选"Convert Units"，模型将缩小为原尺寸的 1/100。

导入管线的标准做法是在导入器脚本中固定一个全局缩放系数。以 Unity 的 ModelImporter API 为例，可通过 `modelImporter.globalScale = 0.01f` 将厘米资产统一换算为米单位，并通过 AssetPostprocessor 的 `OnPreprocessModel()` 回调自动应用，确保所有进入项目的 FBX 都经过相同换算，无需人工每次手动设置。

### 坐标系对齐

三维行业中存在两套主流坐标系约定：Y 轴朝上（Maya、Unity、glTF 2.0）和 Z 轴朝上（Blender 默认、3ds Max、Unreal Engine）。FBX 格式在文件头中使用 `CoordAxisSign` 和 `UpAxis` 字段记录源坐标系，值为 `UpAxis=1` 表示 Y 朝上，`UpAxis=2` 表示 Z 朝上。

当源文件为 Z 朝上（如 Blender 导出的 FBX）导入 Y 朝上引擎时，若引擎未正确读取 `UpAxis` 字段，模型将绕 X 轴旋转 -90°。导入管线应在资产入库脚本中检测该字段，并在必要时注入一个 -90° 的根节点旋转补偿，或在 DCC 工具导出脚本中统一烘焙坐标系旋转至网格顶点数据，以消除运行时的旋转节点开销。glTF 2.0 规范强制要求 Y 轴朝上、右手坐标系，从根源上规避了这一歧义。

### 材质槽位与命名约定

FBX 导入时，引擎会根据网格的 Material Index 自动创建材质槽位，槽位名称来源于 DCC 工具中的材质名称字符串。如果美术在 Maya 中将材质随意命名为 `lambert1` 或 `phong2`，导入引擎后将生成同名的空材质占位符，需要手工重新指定，这在拥有数百个资产的项目中会造成大量重复劳动。

导入管线的材质命名约定通常采用 `M_[AssetType]_[Variant]` 的前缀规则，例如 `M_Prop_Wood_Worn`。在 AssetPostprocessor 的 `OnAssignMaterialModel()` 回调中，可通过字符串匹配将 FBX 材质名映射到项目材质库中的已有实例，实现自动挂载。glTF 2.0 在这方面优于 FBX——它直接在 JSON 结构中内嵌了 `pbrMetallicRoughness` 参数和纹理引用路径，导入时引擎可直接读取金属度、粗糙度、法线贴图等标准通道，减少材质重建步骤。

### LOD 与网格分组识别

导入管线还负责识别 LOD 层级。FBX 的 LOD 识别通常依赖命名后缀约定：Unreal Engine 识别 `_LOD0`、`_LOD1` 等后缀；Unity 识别 `_LOD0`、`_LOD1` 格式但要求父节点包含 LODGroup 组件。导入脚本需提前与美术团队约定命名规则，并在 PostProcessor 中自动将符合命名规则的子网格组装为 LODGroup，避免美术手动拖拽。

---

## 实际应用

**自动化 FBX 导入规范脚本（Unity）**：在项目 `Editor` 文件夹下建立继承自 `AssetPostprocessor` 的类，在 `OnPreprocessModel()` 中集中设置 `globalScale=0.01`、`importNormals=ModelImporterNormals.Import`、`importTangents=ModelImporterTangents.CalculateMikk`，并将 `importBlendShapes` 按资产类型分支控制（角色开启，道具关闭），从而将导入参数从"人工记忆"变为"代码强制"。

**glTF 导入的 PBR 通道映射**：在 Unreal Engine 5 中使用 glTF Importer 插件导入 glTF 2.0 文件时，`baseColorFactor` 直接映射至材质的 Base Color 引脚，`metallicFactor` 和 `roughnessFactor` 映射至 Metallic 和 Roughness 引脚，`normalTexture.scale` 映射至法线强度乘数。导入管线文档中应明确记录这些映射关系，以便美术在 DCC 工具中导出前校验参数取值范围（金属度和粗糙度均为 0–1 的归一化浮点数）。

**多 DCC 工具混合团队的坐标系策略**：某项目组同时使用 Maya（Y 朝上）和 Blender（Z 朝上），通过在 Blender 的 FBX 导出预设中勾选"Apply Transform"并设置 Forward=-Z、Up=Y，在导出阶段统一将坐标系烘焙为 Y 朝上，使下游导入管线无需区分来源工具，全部以相同参数处理。

---

## 常见误区

**误区一：认为 FBX 导出时"Apply Scale"等同于导入时的单位换算**。在 Blender 中导出 FBX 时勾选"Apply Scale"只是将缩放变换烘焙至顶点坐标，并不修改 FBX 文件头中的 `UnitScaleFactor` 字段。引擎仍然会读取 `UnitScaleFactor` 并再次应用换算，导致二次缩放。正确做法是在 Blender 场景属性中将"Unit Scale"设置为 0.01（等效于在 1 厘米单位下工作），或在导入脚本中显式覆盖 `UnitScaleFactor` 的读取逻辑。

**误区二：glTF 内嵌贴图比外部贴图引用更适合导入管线**。glTF 支持将纹理以 Base64 编码内嵌至 `.glb` 单文件中，看似方便，但这意味着纹理版本与网格版本强耦合——修改一张贴图需要重新导出整个 .glb 文件。在有纹理管线和版本控制需求的项目中，应使用 `.gltf + .bin + 外部纹理文件` 的分离形式，导入管线仅处理网格和材质参数，纹理更新走独立的纹理管线通道。

**误区三：材质自动匹配可以完全取代命名规范**。部分团队依赖引擎的"Search and Remap"功能自动匹配同名材质，认为无需约定命名规范。但当资产库规模超过数百个材质时，同名材质冲突和模糊匹配会导致错误挂载（如将战损木材的材质挂到金属道具上）。自动匹配必须以严格的命名规范为前提，二者缺一不可。

---

## 知识关联

导入管线以**资产管线概述**中确立的资产分类体系和命名约定为输入前提——如果上游没有约定哪类资产存放在哪个目录，导入脚本的 `AssetPostprocessor` 无法依据路径判断资产类型并应用对应的导入参数组。

完成导入标准化后，资产进入**导出管线**时需要对称地处理坐标系和单位问题——导入和导出的坐标系变换必须互为逆操作，否则"导入→修改→导出→再导入"的
