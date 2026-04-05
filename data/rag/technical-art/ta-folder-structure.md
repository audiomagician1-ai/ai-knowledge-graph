---
id: "ta-folder-structure"
concept: "目录结构"
domain: "technical-art"
subdomain: "pipeline-build"
subdomain_name: "管线搭建"
difficulty: 1
is_milestone: false
tags: ["规范"]

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
updated_at: 2026-03-25
---

# 目录结构

## 概述

目录结构（Directory Structure）是指在项目文件系统中，将所有资产和文件按照一定逻辑层次组织排列的方式。在技术美术管线中，目录结构定义了美术资产从制作到发布整条链路中的物理存放位置，决定了引擎是否能正确索引资产、版本控制系统（如 Perforce 或 Git LFS）是否能高效追踪变更，以及团队成员是否能在不依赖口头沟通的前提下快速定位文件。

目录结构的标准化实践最早在游戏行业大规模落地，是因为 Unreal Engine 3 时代项目规模扩张导致的"资产失联"问题（即资产脱离场景后无法被重新引用）。从 UE4 开始，引擎强制要求 `Content/` 作为根目录，并在此之下由团队自行约定子目录层级，这使得目录结构规范成为所有美术管线文档的首要章节。好的目录结构能将资产查找时间从数分钟压缩到数秒，并降低合并冲突（Merge Conflict）的发生概率。

在难度分级中，目录结构属于基础约定层（1/9），它本身不涉及技术实现，但作为整条管线的"地基"，一旦项目中期修改目录结构，将导致所有已有引用路径失效，重构成本极高。因此正确理解并在项目第一天就确立合理的目录结构，是技术美术工作的首要任务之一。

---

## 核心原理

### 三种组织维度：按类型、按功能、按模块

目录结构的核心设计决策是选择**主组织维度**。

- **按类型（By Type）**：顶层目录以资产类别命名，例如 `Textures/`、`Meshes/`、`Materials/`、`Blueprints/`。优点是同类资产集中，便于批量处理；缺点是当一个功能模块的资产分散在多个顶层目录时，删除或迁移该功能需要跨目录操作。
- **按功能（By Feature）**：顶层目录以游戏功能命名，例如 `Inventory/`、`Combat/`、`Dialogue/`，每个目录内再细分资产类型。UE5 官方推荐的 `Content/` 结构正是采用此方案，因为功能删除时只需删除对应文件夹，不会影响其他模块。
- **按模块（By Module）**：将项目拆分为可独立交付的制作单元，例如 `Characters/`、`Environments/`、`VFX/`，每个模块下再按功能或类型细分。中大型项目（场景数量超过 20 个关卡）通常采用此方案，结合资产模块化工具（如 UE 的 Asset Manager）实现按需加载。

三种方式并非互斥，实际项目多采用**混合两级策略**：第一层按模块，第二层按类型。例如：

```
Content/
  Characters/
    Textures/
    Meshes/
    Materials/
  Environments/
    Textures/
    Meshes/
    Materials/
  Shared/
    Textures/
    Materials/
```

### 共享资产的隔离原则

跨模块复用的资产（如通用 Trim Sheet 纹理、全局 Post Process Material）必须放入独立的 `Shared/` 或 `Common/` 目录，而非放在任意一个模块目录内。这是因为若将共享纹理放在 `Characters/Textures/` 中，当另一个开发者在 `Environments/` 模块工作时，他无法直觉性地找到该纹理，并可能创建重复文件，导致同一张纹理在项目中出现两份拷贝，造成包体冗余。

Unity 项目中对应的规则是将共享资产置于 `Assets/_Shared/` 目录（以下划线开头使其在字母排序中始终置顶），这是 Unity 社区从 2017 年左右形成的约定。

### 深度控制与路径长度限制

目录嵌套深度建议不超过 **5 层**。Windows 系统的最大路径长度为 260 个字符（MAX_PATH 限制，自 Windows 10 1607 版本起可通过组策略解除，但许多第三方工具仍不支持超长路径），过深的目录结构会直接触发路径溢出错误，导致资产无法导出或打包失败。一条典型安全路径如下：

```
Content / Characters / Hero / Textures / T_Hero_Body_D.uasset
  1层       2层          3层    4层          文件（第5层）
```

超过 5 层时，应通过**扩宽同级目录数量**而非继续向下嵌套来容纳更多资产。

---

## 实际应用

**案例一：UE5 第三人称射击游戏项目**

以下为一个约 15 人团队使用的实际目录方案（精简版）：

```
Content/
  _Dev/           ← 个人开发临时文件，不进 Review
  Art/
    Characters/
      Player/
      Enemies/
    Environments/
      Desert/
      Arctic/
    VFX/
    UI/
  Audio/           ← 由音频团队维护，美术不可修改
  Blueprints/
  Maps/
    Levels/
    Sublevels/
  ThirdParty/      ← 外购资产，完整保留原始目录
```

`_Dev/` 目录以下划线开头确保它在 Content Browser 中排在最前，团队约定所有个人实验性资产都放在 `_Dev/[姓名缩写]/` 下，每个 Sprint（通常为 2 周）结束时清理或提升为正式资产。

**案例二：Unity 移动端项目的 `Resources/` 陷阱**

Unity 中 `Resources/` 是特殊目录，其中所有资产在打包时无论是否被引用都会被打入包体。错误地将大量纹理放入 `Resources/` 会导致包体体积暴增。正确做法是仅将运行时需动态加载（`Resources.Load()` 调用）的少量配置文件放入该目录，其余资产一律通过 Addressables 系统管理，并存放在 `Assets/Addressables/` 目录下。

---

## 常见误区

**误区一：按制作者个人习惯建立目录**

部分美术同学会在项目中创建以自己名字或项目代号命名的顶层目录，如 `Content/John_Work/` 或 `Content/ProjectX_Old/`。这类目录在版本控制中会长期残留，无法通过脚本批量处理，且命名无法传达资产类型信息。正确做法是将个人临时目录统一归入 `_Dev/[姓名]/`，并设置 Perforce 权限使其只对本人可写。

**误区二：认为目录结构可以随时重构**

很多初学者认为目录结构是"随时可以调整的配置"。实际上，在 Unreal 中移动一个已被关卡引用的资产目录，即使使用引擎内置的"Fix Up Redirectors"功能，也会在 `.umap` 文件中写入重定向记录，积累过多重定向会显著增加关卡加载时间。Unity 2019 及以前版本中，移动 `Prefab` 目录会直接断开所有场景中的 Prefab 引用（GUID 不变但 meta 文件路径映射失效）。因此**目录结构必须在 Pre-production 阶段锁定核心层级**，后续只允许在既有框架内新增叶子目录。

**误区三：将 ThirdParty 资产直接解压到项目主目录**

购买的外部资产包（如 Quixel Megascans 导入内容、Asset Store 插件）通常自带一套目录结构。将其直接解压到 `Content/` 根目录会使外部文件与自制资产混杂，无法区分所有权，也难以在合规审查时证明哪些资产来自第三方授权。应将所有外购内容集中放在 `Content/ThirdParty/[供应商名称]/` 下，保持原始目录完整性。

---

## 知识关联

**前置：命名规范**
目录名称本身也受命名规范约束。命名规范定义了使用 PascalCase 还是 snake_case 作为目录名格式（多数 Unreal 项目选择 PascalCase，如 `Characters/`），以及特殊前缀（如下划线 `_` 表示全局或临时目录）的语义。没有命名规范作为前提，目录结构中各团队成员会产生大小写不一致的目录名（`Textures/` vs `textures/`），在区分大小写的 Linux 服务器和不区分大小写的 Windows 客户端之间造成路径不匹配错误。

**后续：参考资产库**
建立参考资产库（Reference Asset Library）时，需要在项目目录结构中预留一个稳定的专用路径（如 `Content/Shared/References/`）。参考资产库中的资产必须具有最高路径稳定性保证——一旦目录结构设计时未为参考库预留独立位置，参考资产就会散落在各功能目录下，后续无法被批量脚本识别和保护，丧失参考库的核心价值。