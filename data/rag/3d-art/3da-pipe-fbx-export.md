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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# FBX导出

## 概述

FBX（Filmbox）格式由Kaydara公司于1996年开发，后被Autodesk收购，目前主流版本为FBX 2020。它是3D美术资产在DCC软件（如Maya、Blender、3ds Max）与游戏引擎（如Unity、Unreal Engine）之间传输的事实标准二进制/ASCII格式。FBX能在单一文件中封装网格体、骨骼、蒙皮权重、动画曲线、材质引用和摄像机数据，使其成为资产管线中跨软件传递复杂资产的首选容器。

FBX的重要性体现在其"有损但通用"的特性：它不保存节点图材质细节，但能可靠传输Mesh拓扑与骨骼层级，因此在资产管线中通常承担"几何体+骨骼+动画"的传输职责，而材质和贴图则由引擎侧单独重建。理解导出设置直接决定资产在引擎中是否出现轴向偏转、单位错误或动画丢帧等问题。

---

## 核心原理

### 轴向（Axis）设置

不同DCC软件使用不同的世界坐标系约定：Maya和3ds Max默认Y轴朝上（Y-Up），而Blender默认Z轴朝上（Z-Up）。Unreal Engine 5内部使用X轴向前、Z轴向上的左手坐标系，Unity则使用Y轴朝上的左手坐标系。

从Blender导出FBX时，若不修正轴向，角色会在Unity中出现倒向侧面的问题。正确做法是在Blender的FBX导出面板中将`Forward`设置为`-Z Forward`，`Up`设置为`Y Up`，这样导出的文件轴向与Unity的期望一致。导入Unreal时则建议直接在引擎导入选项中勾选"Convert Scene"，让引擎自动处理轴向转换，而非在Blender端预旋转。

### 缩放（Scale）设置

FBX内部使用厘米（cm）作为默认单位，Unreal Engine的单位是厘米，Unity的单位是米。若Maya场景以厘米建模但不调整`Scale Factor`，导入Unity后模型会缩小为原来的1/100。

解决方案：在Maya的FBX导出选项中，将`Scale Factor`保持为1.0，同时确认场景工作单位为厘米；在Unity导入设置中将`Scale Factor`设为0.01，由引擎侧统一缩放。若团队选择在Blender中处理，需在导出对话框的`Scale`栏输入`0.01`，确保100 Blender单位（1米）映射为1 Unreal单位（1厘米 × 100 = 1米）的正确比例。缩放问题是管线中最常见且最难排查的错误来源之一。

### 动画（Animation）导出设置

FBX动画分为两种存储模式：**关键帧曲线（Curve）**和**烘焙逐帧采样（Baked）**。曲线模式文件体积小，但跨软件时三次贝塞尔插值可能被错误解读，导致骨骼路径偏差。对于发往引擎的动画资产，推荐启用`Bake Animation`，以场景的原始帧率（通常30fps或60fps）逐帧采样，牺牲文件体积换取确定性。

在Maya中导出带动画的FBX，必须勾选`Animation` → `Bake Animation`，并在`Start/End Frame`中精确填写动画区间，避免导出空白帧。同时关闭`Embed Media`（见下节），否则文件体积会因内嵌贴图而暴增。骨骼动画还需确认`Deformed Models` → `Skins`和`Blend Shapes`选项已勾选，否则蒙皮变形数据会丢失。

### 嵌入媒体（Embed Media）的取舍

FBX提供`Embed Media`选项，可将贴图二进制数据打包进FBX文件本身。此功能适合单文件存档或向客户交付独立资产包，但在引擎导入管线中**强烈不建议开启**：一张2K贴图会让FBX体积增加约8-16MB，版本控制系统（如Git LFS/Perforce）每次修改骨骼后都需要重新提交完整的大文件，严重拖慢协作效率。标准做法是关闭`Embed Media`，让FBX只保存贴图的相对路径引用，贴图以独立`.png`/`.tga`文件管理。

---

## 实际应用

**角色资产从Maya到Unreal的标准导出流程**：在Maya中完成绑定后，选中骨骼根节点及所有Mesh，打开FBX导出对话框，选择FBX 2020版本；轴向保持`Y-Up`（Maya默认，Unreal导入时自动处理）；`Scale Factor`设为1.0；开启`Smooth Mesh`导出高模预览法线；动画Clip按`Bake Animation`逐帧输出，帧率填入场景设置的30fps；关闭`Embed Media`；勾选`Input Connections`以保留Blend Shape名称供引擎读取。完成后文件通常在1-20MB范围，超过50MB则需检查是否意外嵌入了贴图。

**场景道具的静态Mesh导出**：对于没有骨骼的静态Mesh（如武器、家具），应取消勾选`Animation`和`Skeleton`选项，减少无效数据块。Unreal的静态网格体导入器在检测到空骨骼时会报告警告，影响自动化批处理管线的日志清洁度。

---

## 常见误区

**误区一：认为FBX导出设置一次配置永久有效**
不同目标引擎要求不同的导出参数：Unity需要在Blender中预处理Z-Up→Y-Up转换，Unreal则推荐保留原始坐标让引擎自动转换。若美术团队同时向两个引擎交付资产，必须为每个目标维护独立的导出预设（Maya的`.fbxexportpreset`文件），而非使用同一套参数。

**误区二：骨骼Bind Pose破坏导致A-Pose导入为T-Pose**
FBX保存了一个`BindPose`节点，记录骨骼在蒙皮时刻的初始姿态。若在Maya中重新绑定后未更新BindPose（通过`Pose` → `Assume Preferred Angle`），导出的FBX会让引擎读到错误的参考姿态，角色在引擎中静止时会出现扭曲。修复方法是在导出前执行`Reset Bind Pose`命令，确保BindPose与当前骨骼零帧姿态一致。

**误区三：Blender的`Apply Transformations`选项滥用**
Blender导出FBX时提供`Apply Transformations`选项，勾选后会将物体级别的缩放和旋转烘焙进顶点坐标。对于静态Mesh，这通常是正确做法；但对于骨骼动画资产，此选项会破坏骨骼与Mesh之间的相对变换关系，导致引擎中蒙皮结果完全错误。带骨骼的资产必须关闭此选项。

---

## 知识关联

FBX导出是学习**glTF格式**的直接前置：gltF 2.0（2017年发布）在Web和实时渲染领域正逐步替代FBX，两者的轴向约定（glTF强制Y-Up、Z朝屏幕外）与FBX不同，理解FBX的坐标系处理逻辑有助于快速掌握glTF的转换规则。**引擎导入设置**是FBX导出的直接后续环节，Unreal的`FBX Import Options`面板中的`Convert Scene Unit`和`Force Front XAxis`选项与本文描述的导出参数直接对应，两端设置需要联动调试。在**DCC互通**场景（如Maya→Houdini→Unreal管线）中，FBX作为中间格式时的精度损失（尤其是自定义属性和程序节点）会促使团队转向**Alembic缓存**处理复杂模拟数据，而FBX则保留用于传递骨骼动画。