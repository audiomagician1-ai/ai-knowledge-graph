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
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

命名规范是指在3D绑定工作中，对骨骼（Joint/Bone）和控制器（Control/Controller）按照统一的字符串格式进行标注的约定体系。这套规范不仅决定骨骼能否被游戏引擎正确识别，还直接影响蒙皮权重的导出、动画重定向（Retargeting）和程序化动画脚本的运行。

命名规范的必要性源于游戏引擎和动画软件的硬编码需求。以虚幻引擎（Unreal Engine）为例，其人形骨架模板（Humanoid Rig）要求脊柱骨骼命名为`spine_01`、`spine_02`等格式，若绑定师将脊柱命名为`Back1`或`척추1`，引擎的IK Rig系统将无法自动完成骨骼匹配，导致动画重定向失败。Unity的Humanoid Avatar配置同样依赖特定骨骼名称，如`LeftUpperArm`、`RightFoot`才能触发自动映射功能。

在团队协作流程中，统一命名规范可以避免绑定师、程序员和动画师因骨骼名称冲突产生的反复修改。一套命名混乱的骨架在FBX导出后会丢失骨骼层级关系，或在Motionbuilder中进行动作捕捉数据对接时出现错误映射，造成大量返工成本。

---

## 核心原理

### 命名结构的三段式规则

绝大多数行业标准命名采用`[位置前缀]_[部位名称]_[编号/后缀]`三段式结构。例如：`L_UpperArm_JNT`表示左侧上臂骨骼，`R_Knee_CTRL`表示右侧膝盖控制器。前缀区分左右（`L_`/`R_`或`Left`/`Right`），中段描述解剖部位，后缀标识节点类型（`_JNT`代表Joint，`_CTRL`代表Controller，`_GRP`代表Group，`_LOC`代表Locator）。

这种三段式结构的优势在于可以通过脚本批量检索特定类型节点。例如在Maya中执行`cmds.ls("*_CTRL")`即可提取场景内所有控制器，配合`"L_*"`前缀过滤则可单独选中左侧所有节点，大幅加速镜像绑定和左右对称操作。

### 大小写与分隔符规则

不同引擎和软件对大小写及分隔符有严格限制：

- **下划线分隔（Snake_Case）**：Maya、Blender及FBX导出格式均支持，是最通用的选择，如`spine_01_JNT`。
- **驼峰命名（CamelCase）**：Unity的Humanoid Avatar要求使用，如`LeftUpperArm`、`RightFoot`，不能含有下划线和空格。
- **空格禁止**：在任何引擎和DCC软件中，骨骼名称中出现空格（如`Left Arm`）会导致FBX解析错误或脚本引用中断，属于硬性禁止项。
- **中文字符禁止**：虚幻引擎5在导入含有中文命名骨骼的FBX时会直接报错崩溃，部分版本的Maya在保存含中文节点名称的场景时也会产生编码异常。

### 引擎特定骨骼名称要求

各引擎存在必须遵守的保留名称（Reserved Name）：

| 引擎 | 必须命名 | 错误命名示例 |
|------|---------|-------------|
| Unreal Engine | `root`（根骨骼）、`pelvis`（骨盆） | `Root`、`Hips`、`Hip` |
| Unity Humanoid | `Hips`（骨盆）、`Spine`（脊柱） | `pelvis`、`spine_01` |
| Spine 2D | `root`（根骨骼） | `ROOT`、`Root` |

注意Unreal要求`root`全小写，而Unity要求`Hips`首字母大写，两者规范互相冲突。因此在同一个角色需要同时支持两套引擎时，必须维护两套命名骨架文件，或在导出管线中加入重命名脚本进行自动转换。

---

## 实际应用

**人形角色绑定完整命名示例（Maya + UE5标准）**：

根骨骼层级从上到下命名为：`root` → `pelvis` → `spine_01` → `spine_02` → `spine_03` → `neck_01` → `head`。四肢左侧为：`clavicle_l` → `upperarm_l` → `lowerarm_l` → `hand_l` → `index_01_l`。UE5要求左右区分使用`_l`/`_r`后缀而非前缀，且全部小写，这与Maya的`L_`前缀传统规范不同，绑定师需要在交付前统一修改。

**控制器命名规范示例（影视级绑定）**：

在影视项目中，控制器通常与骨骼分层命名：骨骼层为`L_UpperArm_JNT`，对应的控制器层为`L_UpperArm_CTRL`，控制器的偏移组（Offset Group）为`L_UpperArm_CTRL_GRP`，约束目标（Constraint Target）为`L_UpperArm_CTRL_TARGET`。这种四层命名结构使得绑定师在大纲视图（Outliner）中能够一眼区分节点职能，避免误操作删除骨骼层。

---

## 常见误区

**误区一：控制器和骨骼使用相同名称**

部分初学者将控制器与骨骼命名为`L_Hand`和`L_Hand`，仅依靠颜色区分。这在导出FBX时会造成节点名称冲突，因为FBX格式要求场景内所有节点名称全局唯一。正确做法是强制加入`_JNT`和`_CTRL`后缀以区分两类节点。

**误区二：编号从0还是1开始无所谓**

UE5的`spine_01`系列骨骼编号必须从`01`开始，而不是`spine_00`。若错误使用`spine_00`作为起始编号，UE5的IK Retargeter在自动骨骼搜索时将无法匹配，导致只有手动指定才能建立关联，影响动画重定向的自动化效率。

**误区三：命名在绑定完成后随时可以修改**

骨骼命名一旦被蒙皮绑定（Skin Binding）引用后，在Maya中重命名骨骼会导致蒙皮权重的`skinCluster`节点失去对应关系，出现权重数据孤立（Orphan Weight）的问题，必须重新绑定蒙皮。正确流程是在蒙皮前完成所有命名审查，而非在交付前临时修改。

---

## 知识关联

命名规范建立在**骨骼系统**的基础上：只有理解骨骼的层级关系（Parent-Child Hierarchy）和节点类型（Root/Intermediate/End Joint），才能正确判断哪个骨骼该使用`_01`编号、哪个该使用`_end`后缀。例如末端骨骼（End Joint）通常命名为`finger_tip_01_end_JNT`，其`_end`后缀标志它不参与蒙皮计算，只作为方向参考。

掌握命名规范后，绑定师能够直接进入蒙皮、IK控制器搭建和表情绑定等进阶工作，因为后续所有Python/MEL自动化脚本和引擎导入管线（Pipeline）都依赖骨骼名称字符串作为唯一识别依据。一套符合规范的命名体系是绑定工作流程可自动化、可批量化的前提条件。