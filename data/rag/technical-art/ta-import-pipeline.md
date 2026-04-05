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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 导入管线

## 概述

导入管线（Import Pipeline）是指将外部三维资产文件（主要是FBX或glTF格式）读入游戏引擎或DCC工具时，对缩放比例、坐标轴朝向和材质绑定进行标准化处理的一套规则与自动化流程。与手动逐个调整不同，导入管线通过预设的导入配置模板，确保每一个进入项目的模型都遵循统一规范，从源头消除因设置不一致引发的后续返工。

FBX格式由Autodesk于1996年收购Kaydara后逐步标准化，至今仍是游戏工业中最通用的三维资产交换格式；glTF 2.0则由Khronos Group于2017年发布，被称为"三维世界的JPEG"，以JSON+二进制的结构实现了材质参数与几何体的一体化打包。导入管线需要同时处理这两种格式的差异性规范。

在大型项目中，一个场景可能包含数百个来自不同建模师、不同软件版本的FBX文件。若不建立导入管线，仅"单位不统一"一项就能导致模型在引擎中比预期大100倍或缩小到0.01倍，这在Unity（默认1单位=1米）和Unreal Engine（默认1单位=1厘米）之间的迁移场景中尤为常见。

---

## 核心原理

### 缩放标准化

不同DCC软件对"1个单位"的定义存在根本性差异：Maya默认单位是厘米（cm），Blender默认是米（m），3ds Max也是厘米。当Maya中建立的一个身高180cm的角色以FBX导出时，若导入Unity（1单位=1米）且不做缩放修正，角色将显示为身高180米的巨人。

导入管线的标准做法是在FBX导出端统一设置"FBX Scale Factor = 1.0"并勾选"Apply Unit"，然后在引擎导入设置中将"Global Scale"固定为特定值（Unity中通常设为0.01，将Maya的厘米换算为引擎的米）。更规范的做法是制作**导入预设文件**（Unity的`.meta`文件模板，或UE的`Import Options`资产），并通过编辑器脚本批量应用，而不是依赖美术人员手动填写数值。

### 坐标系转换

三大主流软件使用三种不同的坐标系：Maya和3ds Max使用Y轴朝上（Y-up）的右手坐标系，Blender使用Z轴朝上（Z-up）的右手坐标系，而Unreal Engine使用Z轴朝上的**左手坐标系**，Unity使用Y轴朝上的左手坐标系。

坐标系不一致会导致模型在引擎中旋转90°或出现镜像翻转。FBX格式本身存储了坐标轴信息节点（`CoordAxis`、`UpAxis`等），引擎在解析时会尝试自动转换，但自动转换并非总是正确。导入管线的规范做法是：在Maya导出FBX时选择"FBX Export Axis Conversion"选项，在DCC端完成坐标系对齐（即在Maya中将模型沿X轴旋转-90°后Freeze Transforms，再导出），确保导入引擎后根节点旋转值为`(0, 0, 0)`，而不是依赖引擎的自动补偿旋转。

### 材质槽映射标准化

FBX文件内嵌的材质信息仅包含材质名称和少量基础颜色参数，不包含PBR纹理链接；glTF 2.0则原生支持PBR材质参数（`metallicFactor`、`roughnessFactor`、`baseColorTexture`等字段），可以携带完整的材质数据。

导入管线对材质处理的核心任务是**材质槽命名约定**：要求美术人员在建模软件中按固定命名规则创建材质球（例如`MI_Body_01`、`MI_Weapon_Base`），导入脚本根据这些名称自动在引擎中查找或创建对应的材质实例，而不是每次导入都生成一套新的临时材质。在Unity中，可通过`AssetPostprocessor.OnAssignMaterialModel()`回调函数实现材质的自动重映射；在UE5中，则通过配置`FBX Import Options`中的"Material Import Method"为"Do Not Create Material"并配合蓝图脚本完成映射。

---

## 实际应用

**Unity项目的.meta模板复用**：在Unity中，每个导入的FBX文件都有对应的`.meta`文件存储导入设置。团队可以建立一个标准`.meta`模板，其中预设`scaleFactor: 0.01`、`useFileUnits: 0`、`importAnimation: 1`等参数，并通过Python脚本在新资产提交到版本库时自动复制这份模板，从而实现零人工干预的标准化导入。

**glTF工作流中的材质直通**：在使用Blender + Godot 4的独立游戏工作流中，由于两者都原生支持glTF 2.0，材质中的`KHR_materials_pbrMetallicRoughness`扩展参数可以无损传递。导入管线在此场景下的主要工作变为验证纹理路径是否符合项目目录规范（如所有贴图必须存放于`assets/textures/`目录下），并拦截绝对路径引用。

**UE5的批量导入脚本**：Unreal Engine 5的Python脚本API（`unreal.AssetTools.import_asset_tasks()`）允许在CI/CD管线中批量导入FBX文件，并通过`unreal.FbxImportUI`对象程序化设置所有导入参数，彻底替代手动点击导入对话框的操作。

---

## 常见误区

**误区一：认为引擎的"自动坐标系转换"完全可靠**。许多人发现模型导入后位置和旋转都正确，便认为不需要在DCC端做坐标系处理。但自动转换的补偿旋转会被"烘焙"进根节点，导致后续蒙皮动画、程序化旋转时出现累积误差。正确做法是确保模型导入后根节点的Local Rotation显示为`(0, 0, 0)`，若不是，则必须回到DCC软件中修正并重新导出。

**误区二：FBX和glTF的导入设置可以通用**。FBX是二进制/ASCII封装的场景描述格式，材质仅存储名称引用；glTF 2.0是以米为单位的JSON格式，且强制要求Y轴朝上。将FBX的导入预设（含`scaleFactor: 0.01`）直接用于glTF文件导入，会导致glTF模型被额外缩小100倍，因为glTF本身已经是以米为单位的标准格式，不需要单位换算。

**误区三：导入管线只需建立一次**。引擎版本升级（如Unity 2021升级到Unity 6）常常会更改FBX导入器的默认行为（例如Unity 2020.1变更了人形骨骼的坐标系处理方式），导致旧资产在新版本引擎中出现旋转偏移。导入管线必须在引擎升级后进行回归测试，并在版本库中明确记录每次管线配置的变更历史。

---

## 知识关联

**前置概念**：资产管线概述建立了"资产从源文件到引擎内资产"的整体流程框架，导入管线是这个流程中**第一个有实际配置工作的环节**，处理的是原始文件进入引擎的入口规则。

**后续概念**：导出管线与导入管线形成一对：导入管线定义引擎如何接收资产，导出管线定义DCC软件如何输出资产，两者的参数设置必须配套才能保证单位和坐标系的端到端一致。资产烘焙管线在导入管线之后执行，它依赖导入时已经正确设置的缩放和坐标系，才能进行法线烘焙等操作。纹理管线负责纹理的单独导入标准（压缩格式、分辨率规范），与导入管线中的材质槽映射形成互补——导入管线管"材质叫什么名字、绑到哪个槽"，纹理管线管"贴图用什么压缩格式、mip如何生成"。模块化资产系统对导入管线的依赖体现在对齐网格（snap grid）要求上：模块化资产必须在导入时保证缩放为精确的整数或特定倍数，才能在引擎中实现无缝拼接。