---
id: "3da-pipe-naming"
concept: "命名规范"
domain: "3d-art"
subdomain: "asset-pipeline"
subdomain_name: "资产管线"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 命名规范

## 概述

命名规范（Naming Convention）是指在3D美术资产管线中，对文件、贴图、材质、模型等所有可交付物采用统一、可预测格式进行命名的约定体系。一套有效的命名规范通常由**前缀（Prefix）、描述符（Descriptor）、变体标识（Variant）、后缀（Suffix）和版本号（Version）**五个结构化字段组成，各字段之间以下划线`_`分隔。

命名规范的标准化需求随游戏工业规模扩大而逐渐成型。早期小型团队（3-5人）依靠口头约定勉强维持秩序，但当项目资产数量超过500个时，非结构化命名会导致资产查找时间显著增加，重复制作现象频发。Unreal Engine于2014年公开其官方资产命名规范文档，将资产类型缩写标准化（如`SM_`表示静态网格体、`T_`表示贴图），这一标准被大量工作室采纳并演化为行业通行做法。

命名规范在资产管线中的核心价值体现在**机器可读性**上：批量处理脚本、自动化导入工具和版本控制系统（如Perforce、Git LFS）均依赖文件名中的结构化信息来执行分类、过滤和冲突检测操作。一个无法被脚本解析的文件名，等同于无法进入自动化流程的孤立资产。

---

## 核心原理

### 字段结构与分隔符规则

行业主流的命名模板通常遵循以下格式：

```
[TypePrefix]_[AssetName]_[Variant]_[Resolution]_[Version].[ext]
```

示例：`SM_PropChair_Broken_v03.fbx` 或 `T_EnvRock_BaseColor_2K_v01.png`

每个字段均有严格的语义约束：
- **TypePrefix（类型前缀）**：2-4个大写字母，标明资产类型。常见前缀包括：`SM_`（Static Mesh静态网格体）、`SK_`（Skeletal Mesh骨骼网格体）、`T_`（Texture贴图）、`M_`（Material材质）、`MI_`（Material Instance材质实例）、`BP_`（Blueprint蓝图）。
- **AssetName（资产描述符）**：采用帕斯卡命名法（PascalCase），即每个单词首字母大写，例如`PropChair`而非`prop_chair`或`propchair`。
- **Variant（变体标识）**：描述破损、颜色或状态差异，如`Broken`、`Red`、`Open`。
- **Version（版本号）**：强制使用零填充整数，格式为`v##`（如`v01`、`v12`），禁止使用`final`、`new`、`fixed`等语义模糊词汇。

### 贴图通道后缀标准

贴图命名中必须包含通道标识符，以区分同一资产的不同PBR贴图文件。标准通道后缀如下：

| 后缀 | 含义 | 示例 |
|------|------|------|
| `_BC` 或 `_BaseColor` | 基础色 | `T_EnvRock_BaseColor_2K.png` |
| `_N` 或 `_Normal` | 法线贴图 | `T_EnvRock_Normal_2K.png` |
| `_R` | 粗糙度（Roughness） | `T_EnvRock_R_2K.png` |
| `_M` | 金属度（Metalness） | `T_PropSword_M_2K.png` |
| `_ORM` | 合并通道（AO+Roughness+Metal） | `T_EnvRock_ORM_2K.png` |
| `_E` | 自发光（Emissive） | `T_PropLamp_E_2K.png` |

分辨率标识（`512`、`1K`、`2K`、`4K`）应出现在通道标识符之后，版本号之前，这样同一资产的多分辨率版本可以按名称排序时自动归组。

### 版本控制与迭代命名

版本字段是命名规范中与版本控制系统（VCS）交互最频繁的部分。正确的版本命名策略需区分两种场景：

1. **工作中间版本**：在本地迭代过程中递增版本号（`v01` → `v02` → `v03`），每次提交至Perforce或SVN时附带变更说明。
2. **正式交付版本**：锁定版本号并在文件名中追加`_Final`标记，例如`SM_PropChair_Broken_v05_Final.fbx`，此后该资产进入只读状态，任何修改必须创建新分支版本。

禁止使用`_FinalFinal`、`_v2_new`、`_fixed_fix`此类累加式命名——这是管线中最常见的版本失控现象，直接原因是缺少强制版本号递增的工具或规范审查流程。

---

## 实际应用

**场景一：UE5项目中的角色资产命名**

一个完整的玩家角色资产组在Unreal Engine 5项目中应命名如下：
```
SK_CharHero_v02.fbx            ← 骨骼网格体
T_CharHero_BaseColor_2K_v02.png
T_CharHero_Normal_2K_v02.png
T_CharHero_ORM_2K_v02.png
M_CharHero_v02.uasset
MI_CharHero_ArmorRed_v01.uasset
```
六个文件通过共同的描述符`CharHero`形成关联，任意一个文件出现版本更新时，仅需递增该文件自身的版本号，不影响其他文件命名。

**场景二：Python批量重命名脚本的依赖性**

在Maya或Houdini的自动化导出管线中，Python脚本通常使用正则表达式解析文件名以提取元数据：

```python
import re
pattern = r'^(SM|SK|T|M|MI)_([A-Z][a-zA-Z]+)_(.+)_(v\d{2})\.(\w+)$'
match = re.match(pattern, filename)
```

若文件名不符合规范，脚本将抛出异常并阻止该文件进入导出队列，从源头拦截不规范资产污染项目目录。

---

## 常见误区

**误区一：使用空格或特殊字符**

Windows、macOS、Linux三大平台对文件名中的空格和特殊字符（`&`、`#`、`(`、`)`、中文字符）的处理方式存在差异。在Perforce中，含空格的路径必须用引号包裹，在Python的`os.path`处理时极易引发路径解析错误。命名规范的首条强制规则通常是：**文件名中只允许使用字母（A-Z、a-z）、数字（0-9）和下划线（\_）**。

**误区二：类型前缀可以省略**

部分美术人员认为，文件扩展名（`.fbx`、`.png`）已经区分了资产类型，前缀是多余的。这一想法忽略了一个事实：在Unreal Engine的内容浏览器中，`.uasset`是所有导入资产的统一扩展名，贴图、材质、静态网格体无法通过扩展名区分。缺少类型前缀将导致搜索结果混乱，且无法被资产验证工具按类型自动分类审查。

**误区三：版本号用于标记质量等级**

在实际项目中常见`_LowPoly`、`_Optimized`、`_ForMobile`被当作版本字段使用。这类标识符属于**变体（Variant）**字段的范畴，应置于资产描述符之后、版本号之前，如`SM_PropChair_LowPoly_v02.fbx`，而非`SM_PropChair_v02_LowPoly.fbx`。字段顺序的错乱会破坏脚本的正则解析逻辑。

---

## 知识关联

命名规范以**资产管线概述**中确立的"资产可追溯性"原则为前提——只有在理解整个资产从建模到引擎的流转过程后，才能明白每个命名字段为何存在。

掌握命名规范后，**目录结构**是其直接延伸：命名规范管理单个文件的标识，目录结构管理文件群组的组织方式，两者共同构成资产管线的寻址体系。**批量处理**脚本的编写高度依赖命名规范的一致性——脚本中的文件过滤逻辑本质上是对命名规范的程序化表达，规范越严格，脚本的适用范围越广、维护成本越低。**资产验证**流程则将命名规范转化为可自动执行的检查规则，对不符合规范的文件生成错误报告，从而形成规范→验证→反馈的闭环管理机制。
