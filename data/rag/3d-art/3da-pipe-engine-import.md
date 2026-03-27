---
id: "3da-pipe-engine-import"
concept: "引擎导入设置"
domain: "3d-art"
subdomain: "asset-pipeline"
subdomain_name: "资产管线"
difficulty: 2
is_milestone: true
tags: ["引擎"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 引擎导入设置

## 概述

引擎导入设置是指在Unreal Engine 5或Unity等实时渲染引擎中，将FBX等外部资产文件导入项目时所配置的一系列参数选项。这些设置直接决定了网格体的法线计算方式、贴图压缩格式、骨骼绑定的处理方式，以及LOD自动生成的层级数量。一旦资产进入引擎，修改这些设置往往需要重新导入，因此在首次导入时正确配置可以节省大量返工时间。

引擎导入设置的概念随着实时游戏引擎的普及而逐步成熟。Unreal Engine 4时代引入了"Import Settings"面板，UE5进一步将其整合进**Asset Import Data**系统，允许将导入参数作为元数据保存在资产内部，实现一键重新导入（Reimport）而不丢失原有配置。Unity则在2019年引入了**Preset**功能，允许将一组导入设置保存为预设并批量应用。

对3D美术来说，理解引擎导入设置的意义在于：同一个FBX文件，因导入参数不同，可以产生截然不同的渲染结果——例如法线是否翻转、切线空间是否正确、单位比例是否匹配（UE5默认单位为厘米，而Maya默认单位可能为厘米或英寸，需在导入时确认Scale Factor）。

---

## 核心原理

### UE5的静态网格体导入选项

UE5导入FBX静态网格体时，**Import Mesh**面板中最关键的参数包括：

- **Generate Lightmap UVs**：勾选后引擎自动生成第二套UV用于烘焙光照贴图，展开角度阈值默认为45度。如果美术师已在DCC软件中手动制作了第二套UV，应取消此选项以避免覆盖。
- **Build Nanite**（UE5专有）：启用后网格体将使用Nanite虚拟几何体系统，适用于面数超过10万的高精度资产；但启用Nanite的网格体无法使用顶点动画或传统LOD系统。
- **Normal Import Method**：可选`Import Normals`（使用FBX内嵌法线）、`Import Normals and Tangents`（同时导入切线）、`Compute Normals`（引擎重新计算）。使用`Compute Normals`时硬边/软边信息取决于`Normal Generation Method`参数，默认为`Mikk TSpace`算法。

### Unity的模型导入检视器设置

Unity在Inspector面板中将模型导入设置分为三个标签页：**Model、Rig、Animation**。

- **Model标签页**：`Mesh Compression`参数控制网格压缩级别，设为`Off`时保留完整精度，设为`High`时会丢失顶点精度，适合背景装饰物。`Read/Write Enabled`默认关闭以节省内存，但若需要运行时通过脚本读取顶点数据（如程序化变形），必须手动开启，否则运行时会抛出`MeshNotReadableException`错误。
- **Scale Factor**：Unity默认将FBX的1单位视为0.01米（即1cm = 0.01m），`Scale Factor`默认值为**1**，但如果FBX从Maya以厘米导出，而Unity项目使用米制单位，需将Scale Factor调整为**0.01**以保证物体尺寸正确。
- **Rig标签页**：选择`Animation Type`为`Humanoid`时，Unity会自动将骨骼映射到Avatar定义，允许动画重定向；选择`Generic`则保留原始骨骼层级，适合非人形角色或载具。

### 自动化导入：批量设置与脚本化工作流

当项目资产数量超过数百个时，手动逐一设置导入参数效率极低。两款引擎均提供自动化方案：

- **UE5的Python脚本导入**：通过`unreal.AssetImportTask()`类可以批量指定导入参数。例如设置`import_as_skeletal = True`、`automated = True`后调用`unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks()`，可无对话框静默导入数百个FBX文件并统一应用相同设置。
- **Unity的AssetPostprocessor**：在项目的`Editor`文件夹中创建继承自`AssetPostprocessor`的C#脚本，重写`OnPreprocessModel()`方法，可在每次导入模型时自动修改`ModelImporter`的属性，例如强制所有导入到`Assets/Characters/`路径下的FBX开启`importAnimation = false`并设置`meshCompression = ModelImporterMeshCompression.Off`。

---

## 实际应用

**角色骨骼网格体导入**：导入带蒙皮的角色FBX时，UE5中需在导入对话框勾选`Import Mesh`和`Import Animations`，并在`Skeleton`选项中指定已存在的骨架资产，否则引擎会新建骨架，导致同一角色的多个动画FBX无法共用同一套骨架，动画无法正常播放。

**建筑场景道具导入**：大量重复道具（如砖块、路灯）导入Unity时，可创建一个Preset预设，设定`Generate Colliders = false`（手动指定碰撞体）、`Mesh Compression = Medium`，然后将该预设拖拽到`Project Settings > Preset Manager`中，与特定文件夹路径关联，使该文件夹下所有新导入的FBX自动应用此预设。

**贴图导入设置**：UE5导入PNG/TGA贴图时，法线贴图必须将`Texture Type`设为`Normal Map`，引擎会自动将其标记为线性空间（Linear Color Space）而非sRGB。若误将法线贴图设为sRGB，材质中的光照计算将出现明显偏色，高光方向错误。

---

## 常见误区

**误区一：导入后修改设置与重新导入等效**

许多初学者认为导入完成后在Content Browser中修改资产属性与导入时正确设置等效。实际上，部分参数（如UE5的`Generate Lightmap UVs`）只在导入阶段执行计算，导入后修改参数需要点击`Reimport`才能触发重新生成；而骨架绑定一旦建立，即使Reimport也无法更换已关联的骨架资产，必须删除原资产重新导入。

**误区二：Scale Factor只影响显示大小，不影响物理计算**

Scale Factor的错误设置不仅让物体看起来大小不对，还会破坏物理引擎的模拟结果。UE5的Chaos物理系统和Unity的PhysX/Havok系统均基于世界坐标单位进行碰撞检测和重力计算；如果一个角色的碰撞体因Scale Factor错误而实际尺寸为0.01倍，物理引擎会将其视为极小物体，产生穿透或弹飞等异常表现。

**误区三：Unity的`Optimize Mesh`选项总是应有利**

Unity导入设置中`Optimize Mesh`选项会重新排列顶点顺序以优化GPU缓存命中率。但对于需要在运行时通过脚本按索引访问特定顶点的程序化网格（如布料模拟锚点、顶点颜色绘制工具），开启此选项后顶点索引将与DCC软件中的顺序不一致，导致脚本访问错误顶点位置。

---

## 知识关联

**前置概念**：掌握FBX导出设置是正确配置引擎导入的前提。FBX导出时选择的坐标轴方向（Y-up或Z-up）、是否嵌入法线数据、单位设置，直接决定了引擎导入时需要对应调整哪些参数。例如，从Blender以Y-up导出FBX导入UE5时，需在导入设置中将`Transform > Rotation`的X轴旋转修正为-90度，或在Blender导出时勾选`Apply Transform`提前处理坐标轴差异。

**横向关联**：引擎导入设置与材质资产管理密切相关。贴图的导入设置（sRGB/Linear、压缩格式BC1/BC3/BC5）决定了材质节点中采样贴图的正确性；网格体的导入UV布局决定了材质的UV平铺表现。美术规范中通常将FBX导出规范与引擎导入设置写入同一份资产管线文档，作为项目组共同遵守的技术标准。