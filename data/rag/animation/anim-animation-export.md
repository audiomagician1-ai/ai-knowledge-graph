---
id: "anim-animation-export"
concept: "动画导出"
domain: "animation"
subdomain: "keyframe-animation"
subdomain_name: "关键帧动画"
difficulty: 2
is_milestone: false
tags: ["流程"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 动画导出

## 概述

动画导出是将三维软件（如Blender、Maya、3ds Max）中制作完成的关键帧动画数据打包成通用文件格式的过程，主要输出格式为FBX（Filmbox）和glTF（GL Transmission Format）。这两种格式在导出时需要针对帧率、采样密度、骨骼层级和场景单位进行精确配置，配置不当会导致动画在目标引擎中播放速度错误、骨骼扭曲或缩放异常。

FBX格式由Kaydara公司于1996年开发，后被Autodesk收购，目前版本为FBX 2020，是游戏引擎（Unity、Unreal）与DCC工具之间最常用的交换格式。glTF 2.0由Khronos Group于2017年发布，专为Web和实时渲染设计，内置PBR材质支持，动画数据存储在`.animations`数组中，每个动画通道（channel）对应一根骨骼的平移、旋转或缩放曲线。

正确配置导出参数直接决定动画能否在目标平台正常播放。一段在Blender中以24fps制作的角色行走动画，若导出到Unity（默认30fps项目）时未启用"采样所有帧"选项，贝塞尔切线信息会丢失，插值结果将与原始动画出现明显偏差，尤其在快速旋转的关节处最为突出。

---

## 核心原理

### 帧率设置与转换

导出时的帧率参数（FPS）必须与目标引擎或播放环境的帧率匹配。FBX格式在文件头部的`FBXHeaderExtension`区块中存储帧率值，常见枚举值包括：`24`（电影）、`25`（PAL电视）、`30`（NTSC/游戏）、`60`（高帧率游戏）。

当源帧率与目标帧率不同时，导出器有两种处理策略：**直接重映射**（将关键帧时间戳按比例缩放）和**重新采样**（在目标帧率下逐帧烘焙曲线值）。直接重映射速度快但不改变关键帧数量；重新采样会显著增大文件体积，但能精确保留曲线形态。Blender导出FBX时对应选项为"Force Start/End Keying"和"Sampling Rate"，采样率设为`1`表示每帧都烘焙一个关键帧。

### 采样与曲线烘焙

三维软件中的动画曲线通常以贝塞尔曲线或Hermite样条存储切线信息，而FBX和glTF的大多数接收端（如Unity的Animator）会将这些曲线重新解算。glTF 2.0仅支持三种插值模式：`LINEAR`（线性）、`STEP`（阶跃）和`CUBICSPLINE`（三次样条，使用切线数据）。若导出器不支持`CUBICSPLINE`转换，贝塞尔曲线必须被烘焙为`LINEAR`关键帧序列，此时建议将采样间隔设置为源帧率的倒数（例如30fps下为0.0333秒/帧），以保证曲线还原精度。

Maya的FBX导出器提供"Bake Animation"选项，勾选后会按设定的`Bake Resample All`频率对所有动画层进行合并烘焙，这对含有动画层叠加（Animation Layers）的复杂动画至关重要——不烘焙直接导出时，部分引擎无法识别多层动画数据。

### 骨骼（Armature）导出配置

FBX中骨骼以`LimbNode`或`Root`节点类型存储，骨骼的绑定姿势（Bind Pose）记录在`Pose`区块中。导出时需注意以下三点：

1. **骨骼根节点命名**：Unity要求骨骼根节点必须命名为`Armature`或自定义名称，否则Humanoid重定向会失败；Unreal则建议根骨骼命名为`root`并保持零变换。
2. **Rest Pose vs. Bind Pose**：Blender导出FBX时，"Add Leaf Bones"选项会在每根末端骨骼后附加一个零长度叶骨，用于兼容Maya的骨骼末端节点约定，若目标引擎不需要该兼容性应取消勾选以减少骨骼数量。
3. **骨骼轴向**：FBX规范使用右手坐标系Y轴朝上，而Blender内部使用Z轴朝上；导出时必须启用"Apply Transform"或选择"FBX Units Scale"以正确转换轴向，否则骨骼旋转值会出现-90度偏移。

### 场景单位与缩放

glTF 2.0规范明确规定场景单位为**米（meter）**，1个glTF单位 = 1米。FBX则通过文件头中的`UnitScaleFactor`字段声明单位，常见值为`1.0`（厘米，Maya默认）或`100.0`（表示1单位=1厘米，需乘100才换算为米）。

从Maya（1单位=1厘米）导出FBX到Unity（1单位=1米）时，若不勾选"Automatic Units"，模型会缩小到1/100，角色会变成1厘米高的微型人物。Blender导出到glTF时，若场景单位设置为"厘米"而未勾选"Apply Unit"，输出的glTF文件中所有位移动画的数值都会偏大100倍。

---

## 实际应用

**角色动画导出到Unity**：在Blender中完成一个包含行走、跑步、跳跃三个动画片段的角色时，应在"动画片段管理"阶段用NLA编辑器将三个片段标记为独立的Action，导出FBX时勾选"NLA Strips"选项，Unity会自动将其识别为三个独立的AnimationClip资产。帧率统一设置为30fps，骨骼不添加叶骨，坐标轴选择"-Y Forward, Z Up"以匹配Unity的坐标系。

**Web端glTF动画导出**：使用Three.js播放角色动画时，应从Blender导出glTF 2.0格式（`.glb`二进制封装），勾选"Export Animations"并将插值模式设为支持`CUBICSPLINE`的选项，可将一个800帧的动画文件体积从直接烘焙的线性关键帧版本（约1.2MB）压缩至约150KB。

---

## 常见误区

**误区一：认为帧率不匹配只影响播放速度**
帧率不匹配除了导致速度错误外，还会影响关键帧的时间戳精度。在30fps的项目中导入24fps烘焙的FBX时，每一帧的时间戳（0.0417秒）不能被30fps的帧间隔（0.0333秒）整除，引擎会对关键帧进行额外插值，导致微妙的"抖动"现象在循环动画中尤为明显。

**误区二：导出时"Apply Transform"总是必须勾选**
Blender的"Apply Transform"会在导出时将对象的变换烘焙进顶点数据，对于已绑定蒙皮的骨骼网格体，这一操作会破坏蒙皮权重与骨骼的相对关系，导致角色在T-Pose之外的所有姿势下产生严重形变。正确做法是在建模阶段就应用变换，导出时保持该选项关闭。

**误区三：glTF的CUBICSPLINE插值等同于贝塞尔曲线**
glTF的`CUBICSPLINE`使用的是Hermite样条，切线数据格式为`[inTangent, value, outTangent]`三元组，与Blender贝塞尔曲线的控制点格式不同。Blender的glTF导出插件会自动转换切线格式，但第三方导出工具若直接写入贝塞尔控制点坐标，会导致动画曲线完全错误。

---

## 知识关联

动画导出依赖**动画片段管理**阶段的正确组织：每个片段必须在导出前明确起止帧范围，并在NLA编辑器或时间轴中正确命名，导出时才能生成符合预期的独立AnimationClip资产。若片段管理阶段存在帧范围重叠或命名冲突，FBX导出的`AnimStack`区块会包含错误的时间范围，在引擎中表现为动画片段长度异常。

从技术链路来看，动画导出是整个关键帧动画制作流程的最终输出节点，也是DCC工具与游戏引擎或Web渲染器之间的数据接口。掌握FBX的`UnitScaleFactor`、`LimbNode`层级结构以及glTF的`animations`通道格式，能够在出现导入异常时直接检查文件的二进制或JSON内容定位根本原因，而不必依赖软件界面的反复试错。