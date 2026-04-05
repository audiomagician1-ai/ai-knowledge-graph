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
updated_at: 2026-03-26
---





# UE5关卡编辑器

## 概述

UE5关卡编辑器是Unreal Engine 5中用于构建、编排和管理三维游戏世界的主工作界面，集成了视口操作、Actor放置、世界分区管理等功能于单一窗口中。与UE4相比，UE5的关卡编辑器在5.0版本引入了World Partition系统，彻底改变了传统的关卡加载方式，使得开发者能够在单一关卡文件中构建超过数平方公里的开放世界地图，而无需手动切分子关卡。

UE5关卡编辑器的界面由以下固定区域组成：顶部菜单栏与工具栏（包含Play/Simulate按钮）、中央视口（默认为透视视图Perspective）、左侧的放置面板（Place Actors Panel）、右侧的大纲视图（Outliner）与细节面板（Details Panel），以及底部的内容浏览器（Content Browser）。这一布局自UE5.1起支持通过"Window > Load Layout"加载预设布局方案，并允许开发者保存自定义布局。

UE5关卡编辑器的重要性在于它是所有关卡设计工作的起点：地形雕刻、植被绘制、光照设置、蓝图Actor的放置与配置，均通过关卡编辑器完成。Lumen全局光照和Nanite虚拟几何体这两项UE5的标志性技术，也必须在关卡编辑器的视口中通过启用"Show > Lumen"和模型属性中的"Nanite"选项来激活和预览。

## 核心原理

### 视口操作与导航

UE5关卡编辑器的透视视口默认使用WASD键位进行飞行模式导航，鼠标右键按住时激活飞行摄像机，滚轮控制飞行速度倍率（范围1×至8×）。按下F键可将视角聚焦到当前选中的Actor，这在处理大型场景时极为常用。视口右上角的下拉菜单提供了4种标准视角（透视、顶视、前视、侧视）以及光照模式（Lit、Unlit、Wireframe、Detail Lighting等共11种视图模式），其中"Buffer Visualization"模式可单独查看GBuffer的各通道，用于调试Lumen间接光照问题。

### Actor放置与变换工具

在UE5关卡编辑器中，所有可放置的对象统称为Actor，包括StaticMeshActor、Light、Camera、Trigger Volume等。放置Actor有两种方式：从Place Actors面板直接拖拽，或从内容浏览器将资产拖入视口。选中Actor后，工具栏提供了W（移动）、E（旋转）、R（缩放）三种变换工具，配合坐标系切换按钮（世界坐标/本地坐标）和网格吸附设置（Grid Snap，默认值为10cm）进行精确摆放。按住Alt键拖动Actor可快速复制，这是关卡搭建中最高频的操作之一。细节面板中的Transform分组直接显示Location、Rotation、Scale的精确数值，支持手动输入坐标，例如将Z轴设为0以确保Actor贴地。

### 大纲视图与Actor组织管理

UE5关卡编辑器的大纲视图（Outliner）以树形结构列出当前关卡中的所有Actor，支持文件夹分组管理。在启用World Partition的关卡中，大纲视图会显示每个Actor所属的数据层（Data Layer），开发者可以将不同功能的Actor（如敌人、道具、环境）分配到不同的Data Layer，在编辑器中通过勾选来控制其可见性，而不影响运行时的加载逻辑。UE5.1新增的Filter功能允许按Actor类型、Tag或Data Layer快速筛选，当场景中Actor数量超过数千个时，这一功能可将查找时间从分钟级缩短到秒级。

### 编辑器模式切换

UE5关卡编辑器左侧工具栏提供了多种编辑模式：Selection Mode（默认）、Landscape Mode（地形编辑）、Foliage Mode（植被绘制）、Mesh Paint Mode（顶点绘制）以及Modeling Mode（网格建模，UE5新增）。每种模式激活后会在左侧展开对应的专用工具面板，例如Foliage Mode会显示笔刷大小（Brush Size）、密度（Density）等植被绘制参数。这些模式在同一编辑器窗口内无缝切换，无需打开独立的工具窗口。

## 实际应用

**搭建场景原型（Greyboxing）**：关卡设计师通常先在UE5关卡编辑器中使用BSP几何体（通过Place Actors面板 > Geometry分类）或Modeling Mode中的Box工具快速搭建关卡的碰撞体积和空间结构，无需美术资产即可测试玩家动线。BSP体积可直接用于碰撞检测，按下Play按钮即可进入PIE（Play In Editor）模式验证跑跳手感。

**多人协作场景**：在UE5.1及以后版本中，启用了One File Per Actor（OFPA）功能的项目，每个Actor都存储为独立文件，配合版本控制系统（如Perforce或Git LFS），多名关卡设计师可以同时编辑同一关卡的不同区域而不产生文件冲突。激活路径为：Project Settings > World Partition > Enable One File Per Actor。

**光照预览与构建**：关卡编辑器顶部的Build菜单提供了"Build Lighting Only"选项，用于预计算静态光照的Lightmass烘焙。在启用Lumen的项目中，动态全局光照无需烘焙，但仍可通过"Build > Build All Levels"构建导航网格（NavMesh）和预计算可见性（Precomputed Visibility），后者可将运行时的可见性查询性能提升约30%。

## 常见误区

**误区一：直接在默认关卡文件中构建所有内容**。UE5项目默认打开的"ThirdPerson_OverMap"或"Default"关卡是临时测试关卡。正确做法是在内容浏览器中新建专属的关卡文件（.umap格式），通过File > Save Current Level As保存到项目的Maps目录，并在Project Settings > Maps & Modes中将其设置为默认启动关卡。直接在样例关卡中开发会导致资产管理混乱。

**误区二：误认为视口中的实时画面等同于最终游戏画面**。UE5关卡编辑器视口默认以编辑器品质渲染，其Lumen反弹次数、屏幕空间反射质量均低于打包后的游戏。要获得接近发布版本的预览效果，需要在视口右上角点击"▼"展开设置，将"Editor Scalability Settings"调整为Epic级别，或使用File > "Open Editor Preferences" 中的"Use Less CPU when in Background"选项排查帧率干扰因素。

**误区三：混淆Persistent Level与Sublevel的关系**。在未启用World Partition的传统关卡中，UE5关卡编辑器的Levels面板（Window > Levels）允许添加子关卡，但Persistent Level是关卡层级的根节点，GameMode只能在Persistent Level的World Settings中设置，在子关卡中设置的GameMode会被忽略，这是初学者经常遭遇的逻辑失效问题。

## 知识关联

UE5关卡编辑器建立在关卡编辑器概述所讲解的通用编辑器概念之上，将Actor放置、场景层级管理等抽象概念落实为具体的UE5操作流程。掌握了关卡编辑器的基本操作后，下一步自然延伸到**蓝图脚本（LD）**——在关卡编辑器中放置的LevelBlueprint可通过蓝图节点驱动关卡中Actor的行为，入口正是关卡编辑器工具栏上的"Blueprints > Open Level Blueprint"按钮。**关卡流式加载**与**子关卡管理**则是对关卡编辑器中Levels面板和World Partition功能的深化，解决大型世界的内存管理问题。**地形工具**和**植被工具**是关卡编辑器Landscape Mode与Foliage Mode的专项展开，其笔刷系统和参数体系需要在熟悉关卡编辑器整体操作后才能高效使用。