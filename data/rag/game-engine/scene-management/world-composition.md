---
id: "world-composition"
concept: "世界组合"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 2
is_milestone: false
tags: ["大世界"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 世界组合

## 概述

世界组合（World Composition）是虚幻引擎（Unreal Engine）提供的一套大世界关卡管理系统，允许开发者将一个巨大的游戏世界拆分为多个独立的子关卡（Sub-level），并通过一个持久关卡（Persistent Level）作为容器来统一管理这些子关卡的加载、卸载与位置布局。该系统在UE4.9版本时进入稳定阶段，并延续至UE5中与World Partition系统并列提供。

世界组合的设计初衷是解决超大地形游戏（如开放世界RPG或飞行模拟器）中单一关卡文件过大的问题。传统单一`.umap`文件在团队协作时极易产生版本冲突，而且引擎在编辑器中加载完整地图会消耗大量内存。世界组合通过将地图切割为若干地块（Tile），使美术团队可以并行编辑不同区域，同时运行时只加载玩家附近的地块。

开发者在启用World Composition后，编辑器会在项目的`World Settings`面板中显示专属的图层（Layer）管理界面，每个子关卡可被分配到不同图层，每个图层可以独立配置流送距离（Streaming Distance），这直接决定了玩家在运行时能触发加载的半径范围。

---

## 核心原理

### 持久关卡与子关卡的层级结构

持久关卡（Persistent Level）本身不存放任何地形或静态网格体，它扮演"调度者"角色，记录所有子关卡的相对偏移坐标（Offset）和所属图层信息。每个子关卡是独立的`.umap`文件，存储各自的Actor、地形Actor（Landscape Actor）以及光照数据。子关卡通过`ULevelStreamingDynamic`或`ULevelStreamingKismet`两种C++类来注册，前者用于运行时动态创建，后者通过编辑器预配置引用。

### 基于距离的自动流送

世界组合采用基于玩家位置的球形检测机制来触发流送。每个图层（Layer）有一个`Streaming Distance`整数参数，单位为虚幻引擎单位（1 UU ≈ 1 cm）。当玩家到子关卡中心点的距离小于该值时，引擎将该子关卡标记为待加载；距离超过该值乘以1.25（即卸载缓冲系数）时，标记为待卸载。这套滞后机制（Hysteresis）防止玩家在边界反复横跳时频繁触发I/O操作。

图层可以叠加，例如地形图层的`Streaming Distance`设为500000（约5公里），而放置道具的图层设为150000（1.5公里），二者对同一区域的子关卡独立计算加载条件。

### 关卡偏移与坐标系管理

世界组合在编辑器中提供一个二维拼图视图（Composition View），开发者可以直接拖拽各子关卡的缩略图来设置其在世界中的绝对位置。每个子关卡在本地坐标系中以`(0, 0, 0)`为原点建模，运行时引擎将其平移至`World Settings`中记录的偏移坐标。这个机制与**世界原点偏移（World Origin Shifting）**协同工作，当玩家向远离原点的方向移动时，可以将世界原点重置到玩家附近，以缓解浮点精度误差——在超过100,000 UU（约1公里）时，单精度浮点（float32）的精度损失开始变得肉眼可见。

---

## 实际应用

### 大型开放世界地形切割

《绝地求生》早期版本及众多基于UE4的开放世界游戏采用了类似的Tile切割方案。典型做法是将8km × 8km的地图按照1024m × 1024m切分为64块子关卡，每块对应一个`Landscape`组件。在世界组合视图中，这64个`.umap`文件排列为8×8的网格，持久关卡自动记录每块的`(X, Y)`偏移，无需开发者手动填写坐标。

### 多人协作地图编辑

在5人团队的项目中，可以将64块子关卡按行分配：美术A负责Row0-Row1，美术B负责Row2-Row3，以此类推。每次提交版本控制（如Perforce）时，各人修改的文件互不重叠，彻底消除`.umap`二进制文件合并冲突。持久关卡文件几乎不变动，只在添加新子关卡时由项目负责人更新。

### LOD图层分级流送

可以为同一地理区域建立两个子关卡：一个包含高精度静态网格体，`Streaming Distance`设为50000；另一个包含低精度远景代理网格体，`Streaming Distance`设为300000。玩家在远处只见低精度版本，靠近后自动切换为高精度版本，而无需在同一关卡内手动实现LOD逻辑。

---

## 常见误区

### 误区一：持久关卡可以用来存放游戏逻辑Actor

许多初学者将游戏模式（Game Mode）、玩家出生点（Player Start）以外的Actor也放入持久关卡，认为这样"最安全"。实际上持久关卡的坐标原点会随世界原点偏移而移位，放置在远离原点处的Actor会积累浮点误差。正确做法是持久关卡只保留`Game Mode Override`、全局`Level Blueprint`逻辑和流送控制器，而将具体世界内容放入对应坐标位置的子关卡中。

### 误区二：世界组合等同于关卡流送蓝图节点

`Load Stream Level`蓝图节点是手动触发的关卡流送，开发者需要自行编写触发逻辑；而世界组合是基于玩家位置自动调度的系统，二者底层都使用`ULevelStreaming`，但调度权不同。混用两套机制时，若手动卸载了被世界组合标记为"应加载"的子关卡，引擎会在下一帧重新加载它，导致不断触发磁盘I/O。

### 误区三：World Composition与World Partition可以同时启用

UE5的World Partition是对世界组合的架构性替代，二者在同一项目的同一地图中互斥。启用World Partition后，`World Settings`中的`Enable World Composition`复选框会自动置灰。如果项目从UE4迁移至UE5并希望保留世界组合，必须显式关闭World Partition，否则会出现子关卡偏移数据丢失的问题。

---

## 知识关联

**前置概念：场景管理概述**——理解持久关卡与子关卡的父子关系，需要先掌握UE关卡流送的基本概念：关卡是Actor的容器，多关卡可在同一世界中叠加存在。世界组合在此基础上增加了空间坐标调度层，使关卡不再只是逻辑上的分组，而是拥有明确二维地理位置的地块。

**后续概念：关卡过渡（Level Transition）**——世界组合在单一巨大世界内处理无缝流送，但当玩家需要传送到完全不同的场景（如地下城副本）时，需要使用关卡过渡机制来卸载当前持久关卡并加载目标持久关卡。世界组合的持久关卡设计直接影响过渡时需要卸载的内容范围。

**后续概念：世界原点偏移（World Origin Shifting）**——世界组合本身不解决浮点精度问题，超出约10万UU时必须与世界原点偏移配合使用。原点偏移会通知所有已加载子关卡重新计算其世界坐标，这一通知通过`UWorld::SetNewWorldOrigin()`接口触发，是将世界组合应用于真正超大地图时不可绕过的技术环节。