---
id: "ue5-level-editor"
concept: "UE5关卡编辑器"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 2
is_milestone: false
tags: ["UE5"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---




# UE5关卡编辑器

## 概述

UE5关卡编辑器（Level Editor）是Unreal Engine 5中用于构建和编辑游戏世界的主工作空间，通过一个统一的视口界面整合了场景摆放、光照设置、碰撞配置与Actor属性编辑等功能。与UE4相比，UE5关卡编辑器在默认布局中新增了Outliner的过滤和搜索增强功能，并将Lumen全局光照和Nanite虚拟几何体的相关开关直接集成到编辑器工具栏，使开发者无需进入Project Settings即可快速切换这两大核心渲染技术。

UE5关卡编辑器于2022年4月随UE5正式版（5.0）发布，继承自UE4的关卡编辑器框架，但新增了One File Per Actor（OFPA）模式，将每个Actor的数据以独立文件存储在`__ExternalActors__`目录下，从根本上解决了大型团队在同一关卡文件上的版本控制冲突问题。

掌握UE5关卡编辑器的意义在于：它是所有关卡设计工作的起点——无论是摆放静态网格体、配置定向光源，还是引用子关卡或触发蓝图逻辑，都必须在关卡编辑器的上下文中完成。理解其界面布局和操作逻辑，是进行高效关卡迭代的前提。

---

## 核心原理

### 界面布局与主要面板

UE5关卡编辑器默认界面由五个区域组成：顶部**菜单栏与工具栏**、中央**主视口（Viewport）**、左侧**放置Actor面板（Place Actors Panel）**、右侧**细节面板（Details Panel）**，以及右上角的**世界大纲视图（World Outliner）**。其中，主视口支持四分屏模式（Top、Front、Side、Perspective），快捷键为键盘数字键`1`至`4`配合`Alt`键切换。工具栏包含Play（`Alt+P`）、Simulate（`Alt+S`）和快速保存按钮，以及Lumen和Nanite的实时开关。

### Actor放置与变换操作

在UE5关卡编辑器中，放置Actor的方式有三种：从Place Actors面板拖入场景、从内容浏览器（Content Browser）拖拽资产至视口、以及使用快捷键`Shift+1`（静态网格体）等快捷放置。选中Actor后，变换操作使用三轴Gizmo，对应快捷键为：`W`平移、`E`旋转、`R`缩放。精确对齐依赖视口右上角的网格吸附（Grid Snap），默认平移吸附单位为10cm，旋转吸附默认5°，可在编辑器设置中自定义。选中多个Actor时，按`Ctrl+G`可将其分组为一个Actor Group，便于整体变换而不改变层级关系。

### World Outliner与One File Per Actor

World Outliner不仅显示关卡内所有Actor的层级树，还支持文件夹分组——右键菜单中选择"Move to Folder"可将Actor归类，该文件夹结构仅存储于关卡元数据中，不影响运行时性能。当项目启用OFPA（One File Per Actor）模式时，World Outliner中每个Actor旁会显示锁定图标，反映该Actor对应外部文件的版本控制状态（已签出、修改、未签出）。这一机制要求配合Perforce或Git LFS等版本控制系统使用，是多人协作关卡制作的核心工作流基础。

### 视口导航与渲染模式

主视口的导航采用"飞行模式"：按住右键的同时使用`W/A/S/D`键飞行，`Q/E`键上下移动，按住右键并滚动鼠标滚轮调整飞行速度（共8个速度档位，默认第4档）。视口左上角的下拉菜单可切换渲染模式，包括：Lit（完全光照，默认）、Unlit（无光照）、Wireframe（线框）、Detail Lighting、Buffer Visualization等约20种模式，其中Buffer Visualization下的BaseColor、Roughness、WorldNormal子模式对材质调试极为重要。

---

## 实际应用

**搭建室外场景的典型工作流**：设计师首先使用快捷键`Shift+3`在视口中放置一盏Directional Light作为主光源，在Details面板中将其Intensity设为10 lux、勾选"Atmosphere Sun Light"使其与Sky Atmosphere组件联动；随后从Content Browser拖入若干静态网格体资产，利用Grid Snap的10cm吸附单位精确拼接地板模块；最后右键点击World Outliner空白处新建文件夹"Architecture"，将所有建筑类Actor拖入分类管理。

**利用Actor Group进行批量调整**：在关卡中摆放了30根路灯后，选中全部并按`Ctrl+G`创建组，此后整组可作为单一对象进行旋转或移动。若需修改组内单个Actor，双击进入组编辑模式（Group Edit Mode），修改完成后再次双击退出，避免意外移动其他组成员。

**OFPA工作流下的团队协作**：在启用了OFPA的项目中，A设计师负责关卡北区，B设计师负责南区。由于每个Actor对应独立文件，两人同时工作时只需在版本控制系统中分别签出各自Actor的外部文件，合并时不会产生关卡主文件的二进制冲突。这在过去的UE4单文件关卡模式下是无法实现的。

---

## 常见误区

**误区1：认为在编辑器中移动Actor等同于修改其碰撞**。在UE5关卡编辑器视口中通过Gizmo改变Actor的位置和旋转，仅修改该Actor的世界变换（World Transform），不会影响其静态网格体资产本身定义的碰撞形状。碰撞的编辑需要在静态网格体编辑器（Static Mesh Editor）中单独操作，或通过Details面板的Collision Preset下拉菜单选择预设碰撞类型。

**误区2：将World Outliner的文件夹与子关卡混淆**。World Outliner中创建的文件夹是纯粹的编辑器组织工具，所有文件夹内的Actor仍属于当前关卡（Persistent Level），在游戏运行时文件夹结构不存在。子关卡（Sub Level）是独立的`.umap`文件，拥有独立的流送状态和内存占用，两者用途完全不同，不可互换。

**误区3：误以为启用Lumen需要重建光照**。在UE5关卡编辑器中，Lumen是完全动态的实时全局光照方案，通过工具栏或`Project Settings > Rendering`启用后立即生效，不依赖Lightmass烘焙流程。若项目中同时存在已烘焙的Lightmap数据，启用Lumen后静态光照贴图数据会被忽略，但不会被自动删除——需手动运行"Build > Delete All Lightmap Data"清理冗余数据以节省包体大小。

---

## 知识关联

学习UE5关卡编辑器需要具备**关卡编辑器概述**的基础认知，即了解什么是Actor、关卡（Level）作为容器的概念，以及视口导航的基本逻辑，这些知识在进入UE5具体界面操作之前提供了认知框架。

在掌握关卡编辑器的界面和基础操作后，下一步自然延伸到**蓝图脚本（LD）**——关卡编辑器中放置的Actor可以承载关卡蓝图（Level Blueprint）逻辑，例如通过Sequencer触发事件或设置Actor引用；进入**地形工具**和**植被工具**时，它们作为关卡编辑器的内置工具模式（Mode）出现在编辑器左侧的模式切换栏中，分别通过`Shift+3`和`Shift+4`激活，理解其与主编辑器视口共享工作空间的关系至关重要。**关卡流式加载**和**子关卡管理**则直接建立在对World Outliner和Persistent Level概念的理解之上——OFPA所建立的多文件结构正是流式加载框架中动态加载子关卡的技术前提。