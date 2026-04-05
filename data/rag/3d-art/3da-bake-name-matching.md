---
id: "3da-bake-name-matching"
concept: "名称匹配"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 名称匹配

## 概述

名称匹配（Name Matching）是一种在3D烘焙流程中，通过给高精度模型（High Poly）和低精度模型（Low Poly）的网格命名添加特定后缀，让烘焙软件自动识别并配对两者关系的工作方式。最常见的命名约定使用 `_high` 和 `_low` 后缀：例如将一个齿轮零件命名为 `gear_high` 和 `gear_low`，烘焙软件便能自动将两者绑定，无需手动在界面中拖拽指定烘焙来源和目标。

这一约定最早在Marmoset Toolbag和Substance Painter的工作流中被广泛推广，当前的主流版本（如Substance Painter 2.x起）均将 `_high`/`_low` 作为内置识别规则。在大型游戏项目中，场景内往往有数十乃至数百个需要独立烘焙的物件，若逐一手动配对会耗费大量时间且极易出错，名称匹配机制可将整批物件一次性导入后自动完成配对，显著压缩烘焙准备阶段的工时。

名称匹配的价值不仅在于提升速度，更在于降低人为失误率。当模型由多人协作制作时，只要团队共同遵守同一套命名规范，每位成员交付的资产就能无缝进入同一条烘焙流水线，无需额外沟通每个模型的对应关系。

## 核心原理

### 后缀解析规则

烘焙软件在读取导入的网格文件时，会逐一扫描每个网格对象的名称字符串，将最后一个下划线 `_` 之后的部分识别为类型标签。若标签为 `high`（不区分大小写，`HIGH`、`High` 均有效），则将该网格归入高精度组；若标签为 `low`，则归入低精度组。下划线之前的字符串（称为"基础名称"，Base Name）才是真正用于配对的键值：只有基础名称完全相同的 `_high` 与 `_low` 才会被绑定为一组。例如：

- `door_panel_high` ↔ `door_panel_low` ✅ 成功配对（基础名称均为 `door_panel`）
- `door_panel_high` ↔ `doorpanel_low` ❌ 配对失败（基础名称不一致）

### 一对多配对

一个 `_low` 网格可以对应多个 `_high` 网格，只要它们共享同一基础名称即可。例如一个复杂机械臂的低精度模型 `arm_low`，可以同时对应 `arm_high_001`、`arm_high_002`、`arm_high_003` 三块分开建模的高精度部件——Marmoset Toolbag 4 就支持这种一对多逻辑，烘焙时会将所有 `arm_high_*` 的细节全部投射到 `arm_low` 上。Substance Painter 同样支持此逻辑，它会将同一基础名称下所有高精度网格合并视为一个整体来计算法线等贴图。

### 软件内的具体触发时机

在 Substance Painter 中，名称匹配在"烘焙网格贴图"（Bake Mesh Maps）对话框里的 **Match** 选项控制，默认值即为 **By Mesh Name**。若将此选项切换为 **Always**，则软件会忽略名称规则，将所有高精度网格对所有低精度网格做全局投射，通常只在单物件项目中使用。在 Marmoset Toolbag 中，导入FBX后点击 **Auto Group** 按钮，软件会立刻按 `_high`/`_low` 规则自动创建烘焙组，可在 Baker 面板左侧树状列表中直接核查配对结果。

## 实际应用

**武器道具烘焙场景**：一把步枪通常由枪身、枪管、瞄准镜等多个独立部件组成。美术师在DCC软件（如Maya或Blender）中，将高精度枪身网格命名为 `rifle_body_high`、低精度命名为 `rifle_body_low`，高精度枪管命名为 `rifle_barrel_high`、低精度命名为 `rifle_barrel_low`，其余部件以同样规则命名。将所有网格导出为单一FBX文件后，导入Substance Painter，勾选 By Mesh Name 选项直接烘焙，软件会为每组配对分别生成独立的法线贴图（Normal Map）、环境光遮蔽贴图（AO Map）等，整个流程无需手动操作任何配对步骤。

**场景道具批量烘焙**：在一个包含桌子、椅子、柜子共30件道具的场景中，按照 `_high`/`_low` 规范命名后，可将所有60个网格对象一次性打包进单个FBX，在Marmoset Toolbag中点击Auto Group后立刻得到30个烘焙组，相比手动配对节省约40分钟的重复操作时间。

## 常见误区

**误区一：认为后缀大小写必须严格小写**。部分初学者担心写成 `_High` 或 `_HIGH` 会导致识别失败，实际上Substance Painter和Marmoset Toolbag均对后缀做了大小写不敏感处理，`_HIGH`、`_High`、`_high` 效果完全相同。真正会导致失败的是在后缀与基础名称之间多加了空格，如 `door _low`（下划线前有空格），这会导致软件无法正确切割字符串。

**误区二：基础名称中可以随意包含多余的下划线**。若将模型命名为 `door_left_panel_high`，其基础名称是 `door_left_panel`，对应的低精度模型必须命名为 `door_left_panel_low`，而非 `door_left_panel_low_01`——后者的基础名称变成了 `door_left_panel_low`，与高精度基础名称 `door_left_panel` 不匹配，结果是该 `_low` 网格在烘焙时找不到任何高精度来源，得到空白或错误的法线贴图。

**误区三：以为名称匹配会影响UV信息**。名称匹配仅控制高精度与低精度网格之间的投射配对关系，不会改变低精度模型上的UV布局。如果低精度模型的UV存在重叠或超出0~1 UV空间的问题，名称匹配正确与否不能修复这类错误，烘焙结果依然会出现伪影。

## 知识关联

名称匹配建立在**烘焙概述**所介绍的"高精度投射到低精度"这一基本原理之上：高精度模型提供细节信息源，低精度模型提供目标UV空间，名称匹配解决的正是"软件如何知道哪个高精度对应哪个低精度"这一具体问题。掌握命名规则后，烘焙笼（Cage）的调整技巧与名称匹配直接结合使用——在Marmoset Toolbag中，Auto Group生成的每个烘焙组都包含独立的Cage参数，因此正确的名称匹配是后续针对每组独立调整投射距离的前提条件。若项目进一步涉及多套UV的烘焙或UDIM工作流，命名规范也需要相应扩展（例如Substance Painter中结合UDIM Tiles使用时需确保基础名称与Tile编号的对应关系清晰），但核心的 `_high`/`_low` 逻辑保持不变。