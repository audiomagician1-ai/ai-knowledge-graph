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

UE5关卡编辑器（Level Editor）是Unreal Engine 5中用于构建、编辑和管理游戏世界的主界面工具，开发者通过它完成场景中所有Actor的摆放、变换、属性调节和逻辑连接。与UE4相比，UE5的关卡编辑器在2022年正式发布时引入了Outliner多层级筛选、One File Per Actor（OFPA）默认支持，以及与Lumen全局光照系统和Nanite虚拟化几何体的深度集成，从根本上改变了大型场景的协同编辑流程。

关卡编辑器的操作对象称为**关卡（Level）**，其本质是一个`.umap`后缀的资产文件，存储了所有放置在该关卡中的Actor及其Transform、属性和组件信息。每个UE5项目默认从`/Content/Maps/`目录下的初始关卡启动，编辑器打开后的主窗口由视口（Viewport）、世界大纲视图（World Outliner）、细节面板（Details Panel）、内容浏览器（Content Browser）和工具栏（Toolbar）五大核心区域共同构成。

关卡编辑器对关卡设计师而言是整个创作流程的起点：无论是稍后使用的地形工具、植被工具，还是通过蓝图脚本为对象添加交互逻辑，都必须先在关卡编辑器中完成基础场景的搭建与Actor的放置，理解编辑器各面板的功能分工是高效开发的前提。

---

## 核心原理

### 视口（Viewport）操作与模式切换

UE5关卡编辑器默认提供单视口布局，按下快捷键 **Alt+G/H/J/K** 可分别切换为透视视图（Perspective）、正交俯视图（Top）、正交前视图（Front）和正交侧视图（Side）。透视视口中，按住鼠标右键配合 **W/A/S/D** 键实现摄像机飞行漫游，飞行速度通过视口右上角的速度滑块调节，数值范围为1到8档（对应现实场景中约每秒4cm到4096cm的移动步长）。

视口工具栏的**显示模式（View Mode）**下拉菜单提供了超过20种渲染可视化选项，包括"光照（Lit）"、"无光照（Unlit）"、"线框（Wireframe）"以及UE5特有的"Nanite可视化"和"Lumen场景"模式，后两者允许设计师实时检查虚拟几何体的LOD切换和间接光照缓存状态，这是UE4中不存在的调试手段。

### Actor放置与变换系统

所有可放置对象统一称为**Actor**，通过**放置模式（Place Actors Panel）**或直接从内容浏览器拖拽到视口完成添加。选中Actor后，工具栏提供三种Gizmo工具：**移动（W键）**、**旋转（E键）**、**缩放（R键）**，对应的变换数据存储在Actor的`USceneComponent::RelativeLocation / RelativeRotation / RelativeScale3D`属性中。

按住 **Ctrl+D** 复制Actor时，新Actor保持原始Actor的全部属性并在原位偏移10cm，这一偏移量在`Editor Preferences > Viewports > Grid Snapping`中可自定义。网格对齐（Grid Snapping）默认精度为10单位（1 UE单位 ≈ 1cm），在精密建筑级别场景中可降至1单位。多个Actor可通过先选中再按 **Ctrl+G** 进行**组合（Grouping）**，组合后的Actor集合作为整体进行变换，但组合内各成员仍保持独立属性。

### 世界大纲视图与细节面板

**World Outliner** 以树状层级显示关卡中所有Actor，UE5新增了**文件夹系统**，支持拖拽创建多层嵌套文件夹用于场景组织。Outliner顶部搜索栏支持按类型过滤，例如输入`type:StaticMeshActor`可快速定位场景内所有静态网格体实例。

**Details Panel（细节面板）**在选中Actor时显示该Actor所有组件和属性的可编辑字段，分为变换（Transform）、静态网格（Static Mesh）、材质（Materials）、物理（Physics）、碰撞（Collision）等类别。对于Static Mesh Actor，`Mobility`属性的三个选项——Static、Stationary、Movable——直接决定Lumen和Nanite对该对象的处理方式：设置为Static时Nanite会将其纳入虚拟化几何体系统，设置为Movable时Lumen通过光线追踪实时计算其光照贡献，性能开销相差约3至5倍。

### One File Per Actor（OFPA）协同机制

UE5默认启用**One File Per Actor**模式，每个Actor的数据单独存储为`.uasset`文件而非集中写入`.umap`，存放路径为`__ExternalActors__`子目录。这意味着多人团队协作时，不同开发者编辑不同Actor不再产生版本控制冲突，Git或Perforce上的合并代价从整个关卡文件降低到单个Actor文件级别。启用OFPA后，关卡加载时间在大型场景中可能增加10%至20%，但协同收益远超该代价。

---

## 实际应用

**场景原型搭建**：关卡设计师通常使用内置的**几何体笔刷（BSP Brush）**或**Modeling Tools（建模工具）**快速搭建房间、走廊等灰盒结构。在UE5中，`Create > Box Brush`生成的笔刷Actor可直接在Details面板调整X/Y/Z尺寸，完成灰盒验证后再替换为正式静态网格体资产，这是验证关卡动线的标准工作流。

**光源摆放与Lumen配置**：在关卡编辑器中放置`Directional Light`作为主光源，将其`Mobility`设置为Movable后，视口会立即显示Lumen全动态全局光照的效果。通过`Window > Env. Light Mixer`（环境光混合器，UE5.1引入）可在一个面板内同时管理Directional Light、Sky Light和Sky Atmosphere三个光源Actor的参数，避免反复在Outliner中切换选中对象。

**关卡测试与PIE**：点击工具栏的**Play（播放）**按钮进入**Play in Editor（PIE）**模式，角色将从`Player Start` Actor的位置生成并运行完整游戏逻辑。PIE支持**Simulate（模拟）**子模式，该模式下物理和蓝图逻辑运行但不生成玩家，适合调试物体掉落、粒子系统等不需要玩家输入的场景行为。

---

## 常见误区

**误区一：混淆"保存关卡"与"保存所有"的影响范围**
在启用OFPA后，执行`Ctrl+S`只保存`.umap`文件本身，新放置或修改过的Actor的`.uasset`文件需要通过`File > Save All`（`Ctrl+Shift+S`）才能全部写入磁盘。许多初学者在仅按`Ctrl+S`后关闭编辑器，导致部分Actor修改丢失，误以为是软件Bug。

**误区二：认为Outliner文件夹结构影响游戏性能**
World Outliner中的文件夹仅是编辑器组织工具，在打包后的游戏中不产生任何运行时开销，也不会影响Actor的加载顺序或批次。真正影响性能的是Actor的`Mobility`设置、碰撞复杂度和LOD配置，而非Outliner层级深度。

**误区三：关卡编辑器视口中看到的即最终渲染结果**
编辑器视口默认以`Editor Scalability`（编辑器可扩展性）质量级别渲染，该级别通常低于游戏打包后的默认质量。例如Lumen反射在编辑器中可能显示为低分辨率近似值，但执行PIE或打包后会根据`r.Lumen.Reflections.ScreenTraces`等控制台变量显示完整品质。应始终在PIE模式下验证最终视觉效果，而非单纯依赖编辑器视口判断。

---

## 知识关联

**前置概念**：学习UE5关卡编辑器之前需要了解**关卡编辑器概述**中的通用概念——Actor、组件、坐标系和UE单位制度——这些是在UE5编辑器中进行任何操作的语言基础。

**后续扩展**：掌握关卡编辑器的基础操作后，可进入以下几个方向：**蓝图脚本（LD）**在关卡编辑器的基础上为已放置的Actor添加交互逻辑，需要先在关卡中有实体对象才能设置蓝图引用；**关卡流式加载**和**子关卡管理**依赖对`.umap`文件结构和OFPA机制的理解，二者通过`World Composition`或`World Partition`系统将大世界拆分为可动态加载的子关卡；**地形工具**和**植被工具**作为关卡编辑器的专用模式面板，在切换至Landscape模式或Foliage模式后替换主工具栏，本质上仍在关卡编辑器的框架内运行。