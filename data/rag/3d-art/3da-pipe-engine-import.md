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
---
# 引擎导入设置

## 概述

引擎导入设置（Engine Import Settings）是指在将FBX、OBJ、PNG等外部资产文件拖入UE5或Unity时，弹出的参数配置面板所提供的选项集合。这些设置直接决定了资产在引擎内存中的存储格式、压缩方式、网格拓扑处理以及材质绑定行为，错误的导入设置会导致模型法线翻转、纹理色彩空间错误或动画帧率丢失等问题。

该功能在Unity 3.x时代以"Import Settings Inspector"形式出现，UE4则于2014年引入"FBX Import Options"对话框，二者均在后续版本中持续扩展。UE5.1之后加入了"Automated LOD Generation"等自动化选项，Unity 2020.1则引入了Preset系统，允许将一套导入配置保存为.preset文件批量应用给相同类型的资产。

掌握引擎导入设置的意义在于：一个未正确配置的2048×2048纹理，若未勾选"Generate Mip Maps"，在远距离渲染时会出现严重闪烁；而一个多余的"Import Cameras"勾选，会在场景中生成垃圾摄像机节点，污染场景层级结构。

---

## 核心原理

### 网格体（Static/Skeletal Mesh）导入参数

在UE5的FBX Import Options中，**"Normal Import Method"** 提供三个选项：`Compute Normals`（引擎重新计算法线）、`Import Normals`（使用FBX内嵌法线）、`Import Normals and Tangents`（完整导入DCC软件计算的切线空间）。若模型在Maya中使用了"Soften Edge"手动控制硬边，必须选择第三项，否则引擎重新计算的法线会抹平所有硬边效果。

**"Build Scale"** 参数（UE5默认为1.0）与FBX导出时的场景单位密切关联。如果Maya导出时单位为厘米而UE5项目设置为厘米，该值应保持1.0；若Blender导出时单位为米，导入时需将该值设为100，否则模型会缩小至原尺寸的1/100。

Unity的Meshes选项卡下，**"Read/Write Enabled"**（即`isReadable`标志）若勾选，网格数据会在CPU内存中保留一份副本，方便运行时通过`Mesh.vertices`访问，但会使内存占用翻倍，对于静态场景道具应保持关闭。

### 纹理导入参数

UE5纹理导入时，**"Texture Type"** 的选择直接映射到压缩格式：选择`2D Texture`默认使用DXT1/BC1（RGB无透明）或DXT5/BC3（含Alpha），选择`Normal Map`则强制使用BC5（双通道RG法线），比BC3节省约25%显存同时保留法线精度。若将法线贴图误设为`2D Texture`，引擎会用DXT5压缩，导致蓝色通道被错误压缩，模型表面出现"坑洼"假象。

Unity的纹理导入面板中，**"sRGB"** 复选框控制色彩空间解释方式。所有固有色（Albedo/Diffuse）贴图必须勾选sRGB，因为它们存储的是Gamma空间数据；法线贴图、金属度贴图、粗糙度贴图则必须**关闭**sRGB，使引擎以线性空间读取，否则光照计算结果会整体偏亮或偏暗约2.2次方（Gamma值）。

### 动画与骨骼导入参数

UE5导入Skeletal Mesh时，**"Import Animations"** 与 **"Animation Length"** 的组合配置控制动画剪辑范围。选择`Exported Time`使用FBX文件中记录的帧范围；选择`Animated Time`则只截取关键帧实际存在的区间，可自动剔除Maya中时间轴首尾的空白帧。

Unity的Animation选项卡提供**"Anim Compression"**，默认为`Optimal`，引擎会在`Off`（无压缩）、`Keyframe Reduction`（关键帧缩减）、`Optimal`（自动混合算法）之间选择最优方案。对于手部精细动画，建议手动切换为`Keyframe Reduction`并将`Rotation Error`从默认0.5降至0.1度，防止手指关节出现抖动。

---

## 实际应用

**批量导入自动化（UE5）**：在项目的`Content/Editor/ImportData`目录下放置`.ini`配置文件，配合UE5的**"Automatic Import Settings"**（位于Editor Preferences → General → Import Settings），可让特定文件夹内所有新增FBX自动应用预设参数，无需每次手动确认对话框。对于包含100+角色变体的角色包，此方法可将导入耗时从数小时压缩至分钟级。

**Unity的Preset系统**：在Project窗口右键任意资产 → "Create → Preset"，可将当前Inspector中的所有导入参数保存为`.preset`文件。随后在Project Settings → Preset Manager中，可按文件名正则表达式（如`*_NRM`）自动为文件名包含特定后缀的纹理应用对应Preset，实现命名规范驱动的自动导入。

**LOD自动生成**：UE5导入Static Mesh时，勾选**"Generate LODs"**并配置LOD Group（如`LargeProp`），引擎会按照`Engine/Config/BaseEngine.ini`中`[StaticMeshLODSettings]`段落定义的简化百分比自动生成LOD0至LOD3，LOD1默认保留75%三角面，LOD2保留50%，LOD3保留25%。

---

## 常见误区

**误区1：认为导入设置只影响首次导入**
UE5中修改已导入资产的设置后，必须手动点击**"Reimport"**才能重新处理资产。很多初学者修改了导入设置面板中的参数后直接保存项目，但引擎并不会自动重新处理已缓存的资产，导致改动不生效，排查时浪费大量时间。

**误区2：FBX导出设置正确就无需关注引擎导入设置**
这是对两个环节独立性的误解。FBX导出设置控制写入文件的数据，而引擎导入设置控制引擎如何**解读**这些数据。例如FBX中法线数据完整，但若UE5导入时选择了`Compute Normals`，引擎会完全丢弃FBX内嵌法线并重新计算，使DCC软件中的精细法线控制失效。

**误区3：所有纹理用同一套导入设置**
将金属度贴图（灰度图）的Max Size设置与Albedo贴图相同（如2048），会浪费显存。金属度、粗糙度等单通道灰度贴图在`BC4`格式下以512分辨率存储，在PBR管线中视觉损失极小，但相比2048的DXT5节省约94%的显存占用（从约2MB降至约128KB）。

---

## 知识关联

**前置概念——FBX导出**：FBX导出阶段在DCC软件中选择的"Scale Factor"、"Smoothing Groups"等选项，会直接与引擎导入设置中的对应参数形成配对关系。例如Blender中未勾选"Apply Transform"导出的FBX，在UE5导入时需配合调整`Transform Vertex to Absolute`选项才能获得正确的轴向。

**横向关联——材质系统**：导入设置中对纹理`Texture Type`和`Compression`的选择，直接影响材质编辑器中材质球的视觉表现和Shader采样效率。BC5法线贴图需要材质节点使用`Reconstruct Z`节点从RG两通道还原完整法线向量，若纹理格式与材质节点不匹配，光照会出现系统性错误。

**横向关联——LOD系统**：导入时自动生成的LOD数据，构成了引擎距离剔除（Distance Culling）和实例化渲染（HLOD）的基础数据来源，理解导入阶段的LOD参数配置，是后续优化渲染性能的前提工序。
