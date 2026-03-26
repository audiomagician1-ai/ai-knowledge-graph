---
id: "3da-rig-naming-convention"
concept: "命名规范"
domain: "3d-art"
subdomain: "rigging"
subdomain_name: "绑定"
difficulty: 2
is_milestone: false
tags: ["规范"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 命名规范

## 概述

命名规范是指在3D绑定工作中，对骨骼（Joint）、控制器（Controller）、权重组（Deformer Group）等元素按照统一、可预测的字符串模式进行标注的约定体系。它不仅是团队协作的语言基础，更直接影响骨骼数据能否被Unreal Engine、Unity等游戏引擎正确解析和驱动。

命名规范的历史可追溯到早期游戏动画管线，当时3ds Max与半条命引擎的对接要求骨骼必须以`Bip01`为前缀，否则导出的SMD文件无法识别层级关系。随着FBX格式在2006年前后成为行业标准，跨软件的骨骼命名兼容性问题变得更加突出：Maya的`joint1`默认命名在导入Unreal Engine 5后会因空格或大写规则触发骨骼重新映射错误，导致动画重定向失败。

命名规范的意义不止于整洁。Unreal Engine的IK Retargeter工具依赖骨骼名称字符串进行自动骨骼配对，如果左右腿骨骼没有`_l`/`_r`或`_L`/`_R`后缀，系统无法完成自动映射，绑定师必须手动一一配对，大幅增加工作量。Unity的Humanoid Avatar同样如此：其骨骼自动识别算法扫描名称中的关键词（如`hip`、`spine`、`shoulder`），错误的命名会导致Avatar配置失败。

---

## 核心原理

### 基本命名结构

绑定领域通用的骨骼命名公式为：

```
[前缀]_[部位]_[编号]_[后缀]
```

例如：`DEF_spine_03_L`，其中：
- **DEF**：前缀，表示该骨骼为变形骨（Deform Bone），区别于`MCH`（机制骨/Mechanism）和`ORG`（原始骨/Origin）
- **spine**：部位描述，全小写英文，避免中文或特殊字符
- **03**：编号，使用两位数字（01、02、03）而非单位数字（1、2、3），确保字母序排列正确
- **L**：方向后缀，表示左侧

这套结构直接来源于Blender官方Rigify插件的命名约定，Rigify生成的骨骼层级中`ORG-`、`MCH-`、`DEF-`三类前缀清晰区分骨骼功能，工业管线中也广泛沿用类似逻辑。

### 方向标记的选择

左右方向的标注存在三种主流方案，选择哪种必须在项目开始前确定并严格执行：

| 方案 | 示例 | 常见引擎/工具 |
|------|------|--------------|
| 下划线加大写 | `arm_L` / `arm_R` | Blender Rigify、Unreal Engine MetaHuman |
| 下划线加小写 | `arm_l` / `arm_r` | 部分Maya管线 |
| 单词拼写 | `arm_left` / `arm_right` | Unity Humanoid自动识别 |

Unity的Humanoid骨骼识别器支持`left`/`right`全拼、`l`/`r`缩写以及大写变体，但**不支持中文**（如"左"、"右"），中文字符会导致Avatar骨骼窗口显示乱码，且无法参与动画重定向计算。

### 禁止字符与长度限制

不同引擎和格式对骨骼名称字符串有硬性限制：

- **FBX格式**：骨骼名称不得包含空格、冒号（`:`）、竖线（`|`）。Maya默认的命名空间分隔符`:`在FBX导出时会被截断，造成`character:spine`变成`spine`，与同名骨骼发生冲突。
- **Unreal Engine 5**：骨骼名称区分大小写，`Spine_01`与`spine_01`会被识别为两块不同骨骼，这在动画重定向时会产生哑骨骼（Silent Bone）错误。
- **Unity**：骨骼名称建议不超过64个字符，超长命名在某些版本的Animation窗口中会被截断显示，难以区分。

---

## 实际应用

### 角色标准骨架命名示例

以人形角色脊柱为例，规范命名应为：

```
root
└── pelvis
    ├── spine_01
    ├── spine_02
    ├── spine_03
    │   ├── clavicle_L / clavicle_R
    │   │   └── upperarm_L / upperarm_R
    │   │       └── lowerarm_L / lowerarm_R
    │   │           └── hand_L / hand_R
    └── thigh_L / thigh_R
        └── calf_L / calf_R
            └── foot_L / foot_R
```

这套命名与Unreal Engine 5内置的SK_Mannequin骨架名称一致，使用此命名的角色可以直接复用Epic Games商城中遵循Mannequin规范的动画资产，无需额外重定向配置。

### 控制器命名与骨骼命名的区分

控制器（CTR或CTRL前缀）命名需与驱动骨骼名称建立可读的对应关系，但两者不能完全相同，否则在某些DCC软件中会产生节点名称冲突。规范做法：

- 骨骼：`spine_02`
- 控制器：`CTRL_spine_02`
- IK目标：`IK_foot_L`
- 极向量：`PV_knee_L`

---

## 常见误区

### 误区一：命名在同一软件内部无关紧要，导出时再处理

许多初学者认为命名规范只是导出前的清理工作，这是错误的。Maya的`skinCluster`权重数据以骨骼名称字符串作为索引键值存储，如果在绑定完成后批量重命名骨骼，权重绑定关系会因找不到原始名称而丢失，模型在播放动画时会出现顶点归零（顶点飞到世界原点）的严重问题。骨骼命名必须在蒙皮绑定前完成。

### 误区二：数字编号从0开始还是从1开始无所谓

`spine_00`与`spine_01`作为起始编号看似随意，实则影响引擎行为。Unreal Engine 5的IK Rig自动骨骼链识别器在检测脊柱链时会寻找`_01`作为链的起点标记；若从`_00`开始，自动检测会失败，需要手动指定链起点。统一使用`_01`为起始编号是与Epic官方规范保持一致的标准做法。

### 误区三：中文命名便于沟通，只要在Maya内部使用没有问题

Maya本身支持UTF-8节点名称，中文命名在Maya内部可以正常显示和操作，但当文件通过FBX导出至Unreal Engine或Unity时，非ASCII字符在特定版本的FBX SDK（如FBX SDK 2020.0之前的版本）中会被替换为下划线或问号，导致所有中文骨骼名称变成`___01`等无意义字符串，骨架层级完全错乱。

---

## 知识关联

命名规范建立在**骨骼系统**的基础上：只有理解骨骼层级（父子关系、根骨骼位置、骨骼功能分类）之后，才能明白为何`root`骨骼的命名不可随意更改——它是整个骨架FBX导出时的层级锚点，引擎通过查找名为`root`的节点确定骨骼树的根位置，改名为`ROOT`或`Root`在Unreal Engine中虽然通常兼容，但在某些动画蓝图节点（如`Get Socket Location`按名称查询时）会区分大小写而找不到目标骨骼。

命名规范同时为后续的**动画重定向**（Animation Retargeting）和**IK绑定**工作奠定可操作性基础：规范名称是自动化工具链（如Unreal Engine的IK Retargeter、Blender的Rigify自动绑定）能够减少手动干预的前提条件，规范的命名体系可以将一套动画应用到十几个不同角色时的配置时间从数小时压缩到几分钟。