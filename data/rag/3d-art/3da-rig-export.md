---
id: "3da-rig-export"
concept: "绑定导出"
domain: "3d-art"
subdomain: "rigging"
subdomain_name: "绑定"
difficulty: 2
is_milestone: false
tags: ["流程"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.8
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 绑定导出

## 概述

绑定导出是指将含有骨骼绑定（Rig）的角色或道具模型，以FBX格式从DCC软件（如Maya、3ds Max、Blender）输出，并在游戏引擎（如Unity、Unreal Engine）中正确读取骨骼层级、权重数据与动画曲线的完整流程。这一步骤处于角色制作管线的末端，直接决定骨骼是否能被引擎识别、蒙皮权重是否完整传递，以及动画是否能驱动模型正确形变。

FBX格式由Autodesk开发，最初以Filmbox格式发布，1996年前后开始在游戏行业普及。目前游戏引擎普遍支持FBX 2014/2015及更高版本规范，该规范中定义了`FbxSkin`与`FbxCluster`节点结构，用于存储顶点与骨骼之间的权重绑定关系。若导出时选择的FBX版本过旧（如FBX 6.1），则`FbxSkin`数据可能被截断，导致引擎中出现模型破面。

绑定导出的核心价值在于：骨骼层级命名必须与引擎骨骼映射表（Skeleton Mapping）完全匹配，否则引擎的重定向系统（Retargeting）将无法将通用动画正确驱动到目标角色。因此，掌握绑定导出等同于掌握DCC软件与引擎之间骨骼数据的"翻译协议"。

---

## 核心原理

### FBX导出面板中的关键参数

在Maya的FBX导出插件（FBX Plugin）中，导出绑定角色时有以下必须确认的选项：

- **Smoothing Groups**：须启用，否则法线信息丢失导致光照错误。
- **Skin**（蒙皮）：必须勾选，控制是否导出`FbxSkin`权重数据；取消勾选后引擎将收到无蒙皮的静态网格体。
- **Skeleton Definitions**：控制骨骼节点是否以`FbxSkeleton`类型写入，取消后骨骼节点会退化为普通`FbxNull`节点，Unreal Engine的骨架资产导入向导将无法识别骨骼树。
- **Animation**（动画曲线）：若本次导出仅需骨骼+蒙皮而不含动画，须取消勾选，避免引擎将T-Pose强制识别为一段0帧动画并填满动画时间轴。

Blender的FBX导出器默认将`Armature`节点作为根骨骼父节点导出，这会在骨骼层级顶端插入一个名为`Armature`的额外节点。Unreal Engine 5在导入时会弹出"Convert Scene"警告并自动添加根骨骼，若不手动在导出选项中勾选**Add Leaf Bones = Off**并设置**Primary Bone Axis = Y Axis**，将产生骨骼轴向180°翻转的问题。

### 引擎骨骼映射机制

Unreal Engine使用**骨骼树（Skeleton Asset）**与**骨骼映射表（IK Rig Retargeter）**两套系统管理骨骼识别。导入FBX时，引擎读取所有`FbxSkeleton`节点的名称字符串与父子层级关系，在内部构建一棵骨骼树。若导出时骨骼名称含有空格（如`Left Arm`）或中文字符，引擎会将其替换为下划线（`Left_Arm`），导致后续动画复用时骨骼名无法与原始FBX对应。

Unity的骨骼映射依赖**Humanoid Rig配置**。在Inspector的Rig标签下选择`Humanoid`后，Unity的Mecanim系统会尝试将FBX中的骨骼名称与其内置的56块人形骨骼（包含15块必须骨骼，如Hips、Spine、Head等）进行自动匹配。匹配规则基于名称关键词（如含"hip"、"pelvis"字样的骨骼会被映射到Hips槽位），因此遵循标准命名规范（如UE4骨骼命名或Mixamo命名）能极大提升自动映射成功率。

### 单位与坐标系的导出配置

FBX格式记录场景单位与坐标轴方向，不同DCC软件默认值不同：

| 软件 | 默认单位 | 默认前轴 | 默认上轴 |
|------|---------|---------|---------|
| Maya | cm | Z | Y |
| 3ds Max | inch | Y | Z |
| Blender | m | -Y | Z |

Unreal Engine的内部单位为cm，坐标系为X轴朝前、Z轴朝上。导出时若不在Maya FBX导出选项中勾选**Apply Unit Conversion**并将单位锁定为`Centimeters`，导入UE后角色体型将缩小100倍（因为引擎默认将1单位解释为1cm）。Unity内部单位为m，导入FBX时会自动乘以`Scale Factor`（默认0.01将cm转换为m），但若DCC软件导出时已进行了单位转换，Unity的自动缩放会造成双重缩放，角色最终缩小至1/100。

---

## 实际应用

**场景一：角色首次导入Unreal Engine**
在Maya中完成绑定后，选中角色网格体与根骨骼（`root`节点），执行`File > Export Selection`，格式选`FBX export`，在设置面板中确认：Geometry中勾选Smoothing Groups，Animation取消勾选，Units选择Centimeters，FBX file format选择`FBX 2014/2015 Binary`。导入UE5后，在Skeletal Mesh导入窗口中将`Skeleton`指定为已存在的骨架资产，避免引擎为同一套骨骼创建多个不兼容的Skeleton Asset。

**场景二：Blender导出后骨骼朝向错误**
Blender默认骨骼朝向为头部朝向+Y，导出至UE后骨骼T-Pose呈现全身旋转90°。解决方法：在Blender FBX导出设置中将`Forward`改为`-Z Forward`、`Up`改为`Y Up`，或直接勾选`Apply Transform`（Apply Transform会烘焙变换到顶点，无法还原，需谨慎评估是否为可接受的破坏性操作）。

**场景三：Unity Humanoid自动映射失败**
若角色骨骼命名完全自定义（如`jnt_L_UpperArm`），Unity自动映射可能无法识别Left Upper Arm槽位。此时需要在`Configure Avatar`界面手动将`jnt_L_UpperArm`拖入对应槽位，并点击`Done`保存映射。该映射信息存储在`.meta`文件的`humanDescription`字段中，随项目版本控制提交。

---

## 常见误区

**误区一：导出前未重置骨骼变换**
部分美术在调整绑定过程中会在骨骼节点上累积未冻结的局部旋转值（Non-zero rest pose）。导出后引擎读取的骨骼静置姿势不为零旋转，导致动画混合时出现鬼影偏移。正确做法是在Maya中执行`Modify > Freeze Transformations`（或`makeIdentity -apply true`命令）将静置姿势的局部变换归零，再执行导出。

**误区二：以为只导出蒙皮网格就足够**
许多初学者只选中Mesh导出，忘记同时选中骨骼层级中的根节点。这导致FBX文件只包含`FbxMesh`和`FbxSkin`引用信息，但不包含任何`FbxSkeleton`节点实体，引擎将无法解析蒙皮数据，表现为模型在引擎中显示为一团变形的静态网格。正确导出选择应为：骨骼根节点 + 所有蒙皮网格体，在Maya中可用`Select Hierarchy`命令全选。

**误区三：混淆"绑定导出"与"动画导出"的设置**
绑定导出（仅含骨骼+蒙皮）与动画导出（含关键帧曲线）需使用不同的FBX导出预设。若在导出骨骼绑定时不小心启用了Animation选项，UE5会将T-Pose帧记录为一段名为`Take 001`的动画资产，并在骨架资产的动画列表中生成无效条目，污染项目资产结构。建议在DCC软件中分别保存"绑定导出预设"和"动画导出预设"，避免每次手动调整选项时发生混淆。

---

## 知识关联

**前置概念的承接**：游戏骨骼规范规定了引擎能识别的骨骼命名与层级结构（如UE4的`root > pelvis > spine_01...`链式结构），绑定导出的骨骼名称必须与之一致，否则同一套动画无法跨角色复用。FBX导出的基础操作（选择导出类型、版本、路径）是执行绑定导出的必要前提操作，绑定导出在FBX导出的基础上增加了蒙皮、骨骼映射与单位精度三层专属配置。

**向后延伸**：完成绑定导出并在引擎中成功建立Skeleton Asset之后，后续的动画重定向（Retargeting）、IK绑定（Control Rig）以及布料模拟（Cloth Simulation）组件挂载，都以这棵骨骼树作为数据基础。绑定导出一旦出错（如骨骼数量