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

引擎导入设置是指在将FBX、OBJ、PNG等资产文件导入Unreal Engine 5或Unity时，用于控制引擎解析、处理和存储资产的参数配置集合。这些设置直接决定了最终资产在引擎内的网格精度、贴图压缩格式、骨骼绑定方式和碰撞体生成规则，是3D美术资产从DCC软件进入实时渲染环境的最后一道关口。

引擎导入设置的概念随着实时渲染引擎的商业化而逐渐成熟。Unity在2005年发布时就提供了模型导入检视器（Model Import Inspector），而Unreal Engine则在UE4时代引入了统一的资产导入流程（Unified Asset Import Pipeline），并在UE5中以FBX导入对话框（FBX Import Options Dialog）的形式进一步细化了超过40个可配置参数。这一演进反映了实时渲染对资产规格化的强烈需求。

对3D美术而言，错误的导入设置会直接造成生产损失：错误的法线切线空间设置会导致法线贴图在引擎中显示黑斑，错误的单位缩放会让角色在场景中尺寸失真，而遗忘勾选"Generate Lightmap UVs"则会让静态光照烘焙完全失败。掌握导入设置能在资产交付阶段提前排除大量视觉错误。

---

## 核心原理

### UE5的FBX导入参数体系

在UE5的FBX Import Options窗口中，网格类选项分为静态网格（Static Mesh）和骨骼网格（Skeletal Mesh）两个分支，各自有独立参数集。对于静态网格，关键参数包括：

- **Import Normals and Tangents**：选择"Import Normals and Tangents"时引擎直接使用FBX文件内存储的法线数据；选择"Calculate Normals"时引擎按照平滑组重新计算，这会覆盖掉Maya/Blender中手动编辑的硬边信息。
- **Generate Lightmap UVs**：勾选后引擎自动在第二UV通道（UV Channel 1，索引从0开始）生成不重叠的展开UV，用于Lumen或Lightmass光照烘焙。未勾选且模型无预制第二UV时，静态光照会产生UV重叠警告。
- **Build Scale**：默认值为(1,1,1)，但若DCC软件导出单位为厘米而引擎默认为厘米时无需更改；若Maya以默认单位（厘米）导出而FBX选项中勾选了"Convert to Centimeters"，可能产生100倍缩放错误。

### Unity的模型导入检视器结构

Unity在Model页签中提供了专门的**Scale Factor**参数，默认值为1，但由于Unity内部单位为米而FBX常以厘米存储，系统会自动设置为0.01以实现单位换算。若手动将此值改为1，一个180cm的角色会在Unity中变成180米高。

Normals页签中的**Normals Mode**有三个选项：Import（直接读取FBX法线）、Calculate（按角度阈值重算）和None（不生成法线缓冲区，适用于点云数据）。**Smoothing Angle**参数仅在Calculate模式下生效，默认值为60度，表示两个面法线夹角超过60度时视为硬边。

Rig页签专为骨骼网格设计，**Animation Type**需设置为Humanoid（使用Avatar重定向系统）或Generic（保留原始骨架层级），Humanoid模式会触发Avatar配置界面，引擎尝试将骨骼自动映射到标准人体骨骼定义（需要至少15根必要骨骼匹配成功）。

### 贴图导入的压缩格式设置

贴图导入时压缩格式的选择直接影响显存占用和画质。在UE5中，Texture的**Compression Settings**默认为`TC_Default`（对应BC1/DXT1用于无Alpha，BC3/DXT5用于有Alpha）。法线贴图必须手动设置为`TC_Normalmap`（对应BC5/ATI2），否则引擎会将其当作颜色贴图压缩，导致法线向量精度损失。遮罩贴图建议设置为`TC_Masks`以禁用sRGB色彩空间转换，因为粗糙度/金属度数据属于线性数据而非颜色数据。

在Unity中，贴图的**Texture Type**设置为Normal Map后会自动切换压缩格式为BC5（PC）或EAC（移动端），并开启法线贴图解码Shader路径，若将法线贴图以Default类型导入则无法触发这一路径。

---

## 实际应用

**角色FBX导入工作流（UE5）**：导入包含骨骼和蒙皮的角色FBX时，需在导入对话框中将Skeleton字段指向已有的同名骨架资产（Skeleton Asset），否则UE5会为每次导入创建新骨架，导致AnimBlueprint无法复用。导入角色动画时同样需要引用相同骨架，Anim Sequence才能正确绑定。

**批量导入自动化（UE5 Python脚本）**：UE5支持通过Python API进行批量导入自动化。使用`unreal.AssetToolsHelpers.get_asset_tools().import_assets_automated(import_data)`可绕过手动对话框，其中`import_data`为`unreal.AutomatedAssetImportData`对象，可预设`FbxImportUI`的所有参数，实现美术流程中一键批量导入数百个静态网格并自动套用统一设置。

**Unity Preset系统**：Unity 2018.3版本引入了Preset（预设）功能，允许将导入设置保存为`.preset`文件并通过AssetPostprocessor脚本自动应用。例如在`OnPreprocessModel()`回调中检测资产路径前缀，对`Characters/`目录下的所有FBX自动应用Humanoid Rig预设，对`Environment/`目录应用Static Mesh预设，实现零手动操作的规范化导入流程。

---

## 常见误区

**误区一：认为FBX导出设置正确就无需关心导入设置**
FBX格式本身支持多种法线存储方式（按顶点或按多边形顶点），UE5的默认导入设置有时会误读多边形顶点法线为顶点法线，导致硬边丢失。FBX导出设置控制数据的写入方式，而引擎导入设置控制数据的读取和转换方式，两者相互独立，必须同时校验。

**误区二：Lightmap UV只要勾选"Generate"就一定可用**
UE5自动生成的Lightmap UV质量取决于网格拓扑的复杂程度。对于有大量细长三角面或多个相互穿插零件的模型，自动生成算法（基于角度和面积的贪心展开）会产生过多UV接缝和浪费的UV空间，导致光照烘焙出现漏光或像素化阴影。高精度静态网格（如建筑主体）应在DCC软件中手动制作第二UV并在导入时关闭自动生成。

**误区三：Unity的Smoothing Angle改大就能减少硬边**
Smoothing Angle仅在Normals Mode为Calculate时起作用。若FBX文件携带了明确的平滑组数据，Unity默认会以Import模式直接读取，此时Smoothing Angle参数完全无效。必须先将Normals Mode切换为Calculate，Smoothing Angle才会参与法线重算。

---

## 知识关联

引擎导入设置以**FBX导出**为直接前提，FBX文件中携带的平滑组、蒙皮权重、UV通道数量和坐标轴朝向（Y-up vs Z-up）都会影响导入设置的选择。UE5导入时的"Convert Scene"选项本质上是对FBX坐标系与引擎坐标系（X前向、Z朝上）之间差异的自动校正，理解FBX导出时的轴向设置才能判断是否需要开启此选项。

从资产管线的角度看，导入设置的规范化是LOD生成、碰撞体设置、材质实例绑定等下游工序的基础。如果导入阶段的单位、法线、UV通道就存在错误，后续所有依赖这些数据的系统（物理碰撞、光照烘焙、材质混合）都会出现难以溯源的错误，因此导入设置往往是项目技术美术（Technical Artist）制定规范文档（Art Bible）时最优先定义的内容之一。