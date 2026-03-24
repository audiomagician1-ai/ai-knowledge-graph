---
id: "3da-pipe-fbx-export"
concept: "FBX导出"
domain: "3d-art"
subdomain: "asset-pipeline"
subdomain_name: "资产管线"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 40.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# FBX导出

## 概述

FBX（Filmbox）格式由Kaydara公司于1996年开发，后被Autodesk收购并持续维护至今。它是3D资产管线中最广泛使用的中间格式，支持几何体、骨骼绑定、动画、材质引用、摄像机和灯光数据的统一封装。与OBJ等纯几何格式不同，FBX使用二进制或ASCII编码存储完整的场景层级，使其成为从DCC软件（如Maya、Blender、3ds Max）向游戏引擎（Unreal、Unity）传递复杂资产的标准桥梁。

FBX格式目前有多个版本，常用的为FBX 2014/2015、FBX 2019和FBX 2020。不同引擎对版本的兼容性存在差异——例如Unreal Engine 5推荐使用FBX 2016至2020，而某些旧版Unity项目在FBX 2013格式下有更好的稳定性。选择错误的FBX版本可能导致动画曲线丢失或多边形法线反转，因此版本选择是导出配置的第一步。

理解FBX导出设置的意义在于：同一套3D资产，若导出参数配置错误，进入引擎后可能出现模型缩放为100倍、骨骼轴向错误、蒙皮变形崩坏等严重问题，这些错误在引擎端难以修复，必须从源头的导出设置介入。

---

## 核心原理

### 轴向（Axis）设置

不同DCC软件使用不同的世界坐标系上方向（Up Axis）：Maya和Unreal Engine默认Y轴朝上，而Blender和3ds Max默认Z轴朝上。FBX导出时若未正确设置轴向，角色进入Unreal后会呈现"侧躺90度"的状态。

解决方案是在导出对话框中明确指定Up Axis为`Y-up`（对应Unreal/Unity）或`Z-up`（对应某些可视化软件）。在Blender中，FBX导出器提供了`Apply Transform`选项，勾选后会将Blender的Z-up坐标系烘焙转换为Y-up，从而保证模型在Unreal中直立。前方向（Forward）通常设置为`-Z Forward`以匹配Unreal的前向定义。

### 单位与缩放（Scale Factor）

FBX内部使用"单位"概念而非固定的物理距离。Maya默认单位为厘米（1单位=1cm），而Unreal Engine以厘米为标准，Unity以米为标准（1单位=1m）。因此，同一个FBX文件导入Unreal时比例正常，导入Unity后可能显示为100倍大小。

FBX导出时的关键参数是`Scale Factor`，Maya导出到Unity时应将此值设为0.01（即将Maya的厘米转换为Unity的米）；导出到Unreal时保持1.0即可。Blender导出FBX时有`Apply Scale`选项，推荐选择`FBX Units Scale`而非`All Local`，前者会将单位差异写入FBX文件头，由接收端引擎自动处理换算，后者则直接修改顶点坐标数值。

### 动画导出设置

动画导出涉及三个关键开关：**Bake Animation**（烘焙动画）、**Resample All**（重采样）和关键帧范围。`Bake Animation`会将驱动节点、表达式、IK等程序化动画逐帧烘焙为显式关键帧，确保引擎端能正确读取。若不勾选此选项，依赖驱动关系的动画在FBX中将丢失。

`Resample All`控制是否以每帧为间隔重采样曲线，会显著增大文件体积，但对于使用Euler角插值的骨骼动画，重采样能防止引擎端发生万向节死锁（Gimbal Lock）导致的骨骼抖动。帧率（FPS）必须与项目设定一致——若Maya动画为30fps导出，但引擎项目设定为60fps，动画时长会被拉伸为双倍，需在导出时确认`Time Mode`设置。

### 嵌入贴图（Embed Textures）

FBX支持将贴图文件以二进制形式嵌入到`.fbx`文件内部（`Embed Media`选项）。嵌入后FBX文件体积大幅增加，但能保证贴图路径不丢失，适合跨团队交付时使用。然而，大多数游戏引擎导入流程会忽略嵌入贴图，将其提取为独立文件，因此在项目内部管线中**不推荐**嵌入贴图，而应将贴图与FBX放在预定目录结构中，使用相对路径引用。Unreal Engine的FBX导入器无法读取嵌入贴图，Unity则能解包但会产生临时文件。

---

## 实际应用

**角色绑定资产导出（Maya → Unreal Engine 5）**：导出选项应设为FBX 2020格式，Up Axis选`Y`，Scale Factor为`1.0`，勾选`Smooth Mesh`（光滑组信息传递法线分裂），勾选`Bake Animation`，取消`Embed Media`。骨骼命名中避免使用非ASCII字符，否则UE5的Skeleton Asset会出现骨骼识别错误。

**静态道具导出（Blender → Unity 2022）**：在Blender FBX导出面板中，Apply Transform勾选，Forward设为`-Z`，Up设为`Y`，Scale设为`1.0`并选`FBX Units Scale`，取消选中`Armature`和`Animation`分类以避免导出空骨架数据，保持文件简洁。Unity会自动将FBX单位系数处理为0.01的缩放修正，不需要手动改顶点数值。

---

## 常见误区

**误区一：认为FBX会保存完整材质**。FBX格式仅能存储材质的**引用路径**和基础Lambert/Phong参数，不能保存PBR材质节点网络或Substance贴图连接。将FBX导入引擎后出现"灰色材质"是正常现象，需要在引擎端重新配置材质，或使用glTF 2.0格式（内置PBR材质规范）替代。

**误区二：以为取消`Apply Transform`在Blender中也能正常导出**。如果不勾选`Apply Transform`，Blender会在FBX中写入原始的Z-up变换矩阵并附带一个旋转修正节点。部分引擎能识别该修正，但在需要根节点归零的动画重定向工作流中，这个隐藏的旋转偏移会导致动画重定向计算出错，难以排查。

**误区三：静态模型也勾选了`Skin`和`Blend Shape`导出选项**。即使模型没有权重和形态键，若导出时这些选项为开启状态，FBX文件中会写入空的蒙皮数据块，导致引擎误将静态网格识别为骨骼网格（Skeletal Mesh），触发不必要的蒙皮运算，浪费GPU性能。

---

## 知识关联

FBX导出是资产管线概述中"格式转换"环节的具体实现，学习者应已了解DCC软件的坐标系概念与资产目录结构后，再配置FBX导出参数。

掌握FBX导出后，可进一步学习**glTF格式**——glTF 2.0是FBX的现代替代方案，原生支持PBR材质且为开放规范，无需Autodesk许可；**引擎导入设置**与FBX导出设置是镜像关系，导出端的轴向、缩放选择直接决定导入端的补偿参数应如何配置。对于需要传递复杂骨骼绑定的项目，**绑定导出**专题会在FBX导出基础上讲解权重阈值、骨骼层级裁剪和shape key精度等进阶参数。对于布料模拟、流体等程序化动画，**Alembic缓存**格式以逐帧顶点位移的方式绕过了FBX动画烘焙的局限性，是FBX动画导出的重要补充方案。
