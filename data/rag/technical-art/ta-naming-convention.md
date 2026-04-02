---
id: "ta-naming-convention"
concept: "命名规范"
domain: "technical-art"
subdomain: "pipeline-build"
subdomain_name: "管线搭建"
difficulty: 1
is_milestone: false
tags: ["规范"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 命名规范

## 概述

命名规范（Naming Convention）是指在游戏开发或影视制作管线中，对所有数字资产——包括纹理贴图、材质实例、静态网格体、骨骼网格体、蓝图类以及动画序列——预先制定统一的字符串格式规则，使每一个文件名都能携带资产类型、所属模块和变体信息，做到"看名知义"。

命名规范的思想早在20世纪80年代的大型软件工程领域就已有雏形，匈牙利命名法（Hungarian Notation）由微软程序员查尔斯·西蒙尼（Charles Simonyi）于1972年前后提出，要求在变量名前缀中编码数据类型。游戏行业在此基础上演化出专门针对资产管线的版本：Epic Games在UE4时代发布的官方风格指南（Gamemakin Style Guide）将资产前缀系统化，例如规定静态网格体使用`SM_`、骨骼网格体使用`SK_`、材质使用`M_`、材质实例使用`MI_`、纹理使用`T_`，这套前缀体系至今仍是行业参考基准。

在多人协作的管线中，命名规范直接决定了自动化工具能否正确识别资产类型。Unreal Engine的资产验证插件、Houdini的PDG节点以及Python批处理脚本，通常依赖文件名前缀或后缀来路由资产到正确的处理流程；一旦某张法线贴图被命名为`texture_01.png`而非`T_Rock_N.png`，自动打包工具就无法将其识别为法线通道，轻则压缩格式错误（应用BC5而非BC7），重则导致整条管线中断。

---

## 核心原理

### 前缀系统（Prefix System）

前缀是命名规范中信息密度最高的部分，其作用是在不打开文件的情况下告知资产类型。常见前缀约定如下：

| 前缀 | 资产类型 |
|------|----------|
| `SM_` | Static Mesh（静态网格体） |
| `SK_` | Skeletal Mesh（骨骼网格体） |
| `M_` | Material（主材质） |
| `MI_` | Material Instance（材质实例） |
| `MF_` | Material Function（材质函数） |
| `T_` | Texture（纹理） |
| `BP_` | Blueprint Class（蓝图类） |
| `ABP_` | Animation Blueprint（动画蓝图） |
| `AM_` | Animation Montage（动画蒙太奇） |
| `PS_` | Particle System（粒子系统，Legacy） |
| `NS_` | Niagara System（Niagara粒子系统） |

前缀必须放置在名称最前端，这是因为内容浏览器（Content Browser）默认按字母升序排列，相同类型的资产会因前缀相同而自动聚集，大幅降低视觉搜索成本。

### 主体命名段（Descriptor Segment）

主体部分描述资产所属对象或功能模块，采用帕斯卡命名法（PascalCase），即每个单词首字母大写、不使用下划线分隔单词内部字母，例如`RockWall`、`HeroCharacter`、`FireEffect`。禁止使用缩写（除非是团队内已书面约定的缩写，如`Env`代表Environment），禁止使用拼音，禁止出现空格，禁止使用特殊字符（`&`、`#`、`%`等在某些引擎路径解析中会引发错误）。

### 后缀系统（Suffix System）

后缀用于描述纹理的通道用途或资产的变体序号，位于名称末尾，用下划线与主体隔开。纹理后缀是后缀系统中规则最为细密的部分：

- `_D` 或 `_BaseColor`：漫反射/基础色贴图  
- `_N`：法线贴图（Normal Map）  
- `_R`：粗糙度贴图（Roughness）  
- `_M`：金属度贴图（Metallic）  
- `_ORM`：将Occlusion、Roughness、Metallic打包进RGB三通道的复合贴图（UE4/UE5常见优化做法）  
- `_E`：自发光贴图（Emissive）  
- `_A`：透明度贴图（Alpha/Opacity）  

变体序号后缀使用两位或三位数字，如`_01`、`_02`，不使用单个数字（避免排序时`_9`排在`_10`之前的问题）。

### 完整命名公式

```
[资产前缀]_[模块名]_[描述词]_[变体/序号]_[纹理通道后缀]
```

示例：
- `SM_Env_RockWall_01`——环境模块第1个岩壁静态网格体  
- `T_Env_RockWall_01_N`——对应的法线贴图  
- `MI_Env_RockWall_Wet_01`——岩壁潮湿变体材质实例  
- `BP_NPC_VillagerA_01`——NPC模块村民A的第1个蓝图变体  

---

## 实际应用

**UE5项目中的自动化验证**：在项目设置中通过Editor Utility Widget或Python脚本遍历Content Browser，检测所有不符合`[前缀]_[模块]_[描述]`格式的资产并输出报告。Epic Games内部项目要求每次提交前运行此脚本，违规资产会被标记为`[NEEDS_RENAME]`并阻止提交。

**Unity项目的Addressables集成**：Unity的Addressable Asset System在构建资产包（Asset Bundle）时，可以用命名中的模块段（如`Env_`、`UI_`、`Char_`）作为Group分组依据，通过正则表达式`^(Env|UI|Char)_.*`自动将资产路由至对应的Bundle，减少手动配置工作量约70%。

**Houdini程序化管线**：在Houdini PDG中，纹理文件名的通道后缀（`_N`、`_ORM`）被TOP节点的File Pattern参数直接读取，用于判断应调用哪条材质连接分支，从而实现数百个资产的无人工干预批处理。

---

## 常见误区

**误区一：认为命名规范可以在项目中途补救**  
许多团队在项目初期忽视命名规范，等到资产数量超过500个时才意识到问题，此时批量重命名会破坏引擎内部的资产引用路径（Reference Path）。在UE5中，资产的路径硬编码在`.uasset`文件内部，使用`Asset Registry`重定向（Redirector）虽可修复引用，但会遗留大量`.uasset`重定向残留文件，且若引用跨越Level Streaming边界，极易出现资产加载失败。正确做法是在**项目第一个资产创建之前**就锁定命名规范文档并纳入版本控制（如写入`CONTRIBUTING.md`）。

**误区二：将纹理通道后缀与主体描述词混淆位置**  
错误写法：`T_N_RockWall_Env_01`（将通道后缀`N`前置），正确写法：`T_Env_RockWall_01_N`。通道后缀必须是名称的**最后一段**，因为自动化脚本通常使用`split('_')[-1]`取最后一个段落来判断通道类型；若通道标识符不在末尾，脚本将无法识别，导致贴图压缩格式被错误设置为`Default（DXT1/BC1）`而非法线贴图专用的`BC5`格式。

**误区三：对蓝图类滥用`BP_`前缀而不区分子类型**  
将所有蓝图一律命名为`BP_`前缀会使蓝图浏览器难以区分Actor类、组件类（`BPC_`）、接口类（`BPI_`）和枚举类（`BE_`）。例如把一个蓝图接口命名为`BP_Interactable`而非`BPI_Interactable`，会导致程序员在搜索接口时与普通Actor类混淆，增加错误引用概率。

---

## 知识关联

**前置概念——资产管线概述**：理解资产管线概述后，学习者已知晓数字资产从DCC软件导出到引擎的完整流动路径；命名规范则是这条路径上的**元数据层**，每个管线节点（导出脚本、验证插件、打包工具）都依赖文件名携带的类型和通道信息来执行正确操作。

**后续概念——目录结构**：命名规范中的**模块名段**（如`Env_`、`Char_`、`UI_`）与目录结构中的顶层文件夹名称直接对应；若两者定义不一致，例如目录结构使用`Environment`而命名规范使用`Env`，自动化路由脚本就会因路径匹配失败而报错。因此通常要求先锁定目录结构的顶层模块定义，再据此书写命名规范文档。

**后续概念——资产审查流程**：资产审查（Asset Review）的第一道检查项即为命名合规性；审查员使用的Linter脚本以命名规范文档为唯一依据，对每个提交的资产执行正则表达式匹配，不合规资产在进入后续LOD生成和碰撞体计算流程之前即被拦截退回，从而避免非法命名污染已发布的Content Build。