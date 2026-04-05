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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

FBX（Filmbox）格式由Kaydara公司于1996年开发，2006年被Autodesk收购后成为行业标准交换格式。FBX的核心优势在于它能在单个`.fbx`文件中同时封装几何体、材质引用、骨骼绑定、动画曲线、摄像机和灯光数据，这使它成为从DCC软件（Maya、Blender、3ds Max）向游戏引擎（Unity、Unreal Engine）传递资产的主要通道。

FBX格式分为二进制（Binary）和ASCII两种存储方式。二进制FBX体积更小、解析速度更快，是生产环境首选；ASCII格式可用文本编辑器查看内容，适合调试绑定问题或追查动画曲线错误。当前主流使用的FBX SDK版本为2020.x，Unreal Engine 5和Unity 2022均基于此版本的解析库。

FBX导出设置中的每一个选项都直接影响目标引擎接收到的数据质量。错误的轴向设置会导致角色在引擎中旋转90度，错误的缩放单位会让一个标准角色在场景中呈现为0.01倍大小，而错误的动画采样率会造成曲线精度损失。因此在建立资产管线时，必须为项目制定统一的FBX导出规范文档。

---

## 核心原理

### 轴向（Axis）设置

不同DCC软件使用不同的世界坐标系朝向：Maya和Unreal Engine以Y轴朝上（Y-up），而3ds Max和Unity以Z轴朝上（Z-up），Blender默认也是Z-up但导出时可以转换。FBX格式本身记录一个`AxisSystem`标志，引擎读取后决定是否做旋转补偿。

从Blender导出FBX时，需将"Forward"设为`-Z Forward`，"Up"设为`Y Up`，才能在Unity和Unreal Engine中获得正确朝向。如果跳过此设置，网格会在X轴旋转-90度（即绕X轴旋转-90°），工程师需要在引擎端手动补偿，这会积累不必要的旋转偏移并污染动画数据。

### 缩放（Scale）与单位（Units）

FBX记录的是带单位的绝对数值，`ScaleFactor`字段标记1个FBX单位对应多少厘米。Maya默认1单位=1厘米，Unreal Engine导入时将1cm映射为1 UU（Unreal Unit）；Blender默认1单位=1米，导出时若不设置"Apply Scale"，同一个2米高的角色在Unreal中会显示为200单位高——与预期一致。但若在Blender中使用了非1.0的Object Scale且未应用（Apply），FBX中的缩放信息会残留在变换矩阵中而非几何体顶点上，导致引擎中出现缩放不为1的根节点，进而破坏布娃娃物理和碰撞体积。

标准做法：导出前在Blender中执行Ctrl+A → Apply All Transforms，或在导出面板中勾选"Apply Transform"，确保FBX文件内所有节点的Scale值均为(1, 1, 1)。

### 动画（Animation）导出设置

FBX动画以"Animation Stack"和"Animation Layer"结构存储。每个AnimStack对应一个独立动画片段，引擎按名称识别它们。主要参数包括：

- **Bake Animation（烘焙动画）**：将IK、约束、驱动关键帧等程序性动画转换为逐帧关键帧数据。引擎无法解析Maya的IK解算器，必须烘焙后导出。
- **采样率（Resample Rate）**：默认值通常为24fps或30fps，应与项目帧率一致。将30fps动画以24fps导出会导致每隔几帧丢失一个关键帧，造成抖动。
- **简化阈值（Simplify）**：Maya FBX导出器提供0.0到1.0的曲线简化参数，值越大曲线关键帧越少但精度损失越大。对于面部动画建议设为0（不简化），对于程序动画可设为0.01到0.1节省文件体积。

### 嵌入媒体（Embed Media）

FBX支持将贴图文件以二进制形式嵌入`.fbx`文件内部。启用"Embed Media"后，PNG/TGA等贴图会被打包进FBX，文件体积显著增大（一个含4K贴图的角色FBX可达80MB以上）。大多数游戏引擎工作流**不推荐**使用嵌入模式，因为引擎需要解包贴图再重新压缩为DXT/BC格式，且贴图无法独立更新。正确做法是保持贴图外部引用，用相对路径或绝对路径关联，引擎导入时单独处理贴图。

---

## 实际应用

**Blender → Unreal Engine 5角色导出流程**：在Blender中完成角色后，选中角色Mesh和Armature，导出设置如下：Scale=1.0，Forward=-Z，Up=Y，勾选"Armature"和"Mesh"，取消勾选"Embed Textures"，启用"Bake Animation"并设Resample Rate=30。将FBX拖入UE5的Content Browser后，角色朝向正确，骨骼缩放为1.0，动画可在Animation Blueprint中直接使用。

**Maya → Unity静态网格导出**：若场景单位设为厘米，一个标准门（高200cm）导出后在Unity中高度为2单位（Unity默认1单位=1米，FBX导入时自动换算），符合预期。若场景单位误设为毫米，则导入后门高仅0.2单位，需检查Maya的"Working Units"设置。

---

## 常见误区

**误区一：认为FBX导出后轴向可以在引擎端随意修改**。在引擎导入设置中旋转根节点虽然能修正视觉朝向，但会在根骨骼上留下一个额外的旋转偏移。当动画师重定向（Retarget）动画时，这个偏移会被计入变换链，导致动画偏移累积。正确方案是在导出阶段修正轴向，保证FBX文件本身的轴向符合目标引擎标准。

**误区二：认为"Bake Animation"只在有IK时才需要开启**。实际上，任何使用了约束（Constraint）、表达式（Expression）、受驱关键帧（Driven Key）、或父级偏移的骨骼，都必须烘焙才能在引擎中正确回放。FBX格式不支持传递Maya的约束节点，未烘焙的骨骼在引擎中会停留在绑定姿势位置。

**误区三：以为ASCII格式FBX与Binary格式FBX功能等价**。部分旧版FBX插件在写ASCII格式时会省略某些自定义属性（Custom Properties）和用户数据（User Data）字段，导致Unreal Engine无法读取LOD信息或碰撞标记。生产环境统一使用Binary FBX可避免此类兼容性问题。

---

## 知识关联

FBX导出是资产管线中连接内容创作与引擎集成的关键步骤，其上游是**资产管线概述**中建立的目录结构规范和命名约定——FBX文件名与内部节点名必须遵循相同规则，引擎才能正确匹配LOD和碰撞体。

掌握FBX导出后，可进一步学习**glTF格式**，了解glTF 2.0如何用JSON+二进制块替代FBX的专有结构，以及PBR材质定义上的差异。**引擎导入设置**是FBX导出的直接下游，涵盖Unreal Engine的FBX Import Options和Unity的Model Import Settings如何与导出参数对应。对于高面数布料或流体模拟，**Alembic缓存**提供了FBX动画无法替代的逐顶点动画方案。而在多骨骼角色传递方面，**绑定导出**专门处理蒙皮权重、形态键（Blend Shape/Shape Key）和控制器属性的跨软件传递问题。