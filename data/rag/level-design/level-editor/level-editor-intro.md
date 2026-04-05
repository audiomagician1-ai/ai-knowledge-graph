---
id: "level-editor-intro"
concept: "关卡编辑器概述"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 关卡编辑器概述

## 概述

关卡编辑器（Level Editor）是游戏引擎中专门用于构建、摆放和配置游戏场景资产的可视化工具集合。它允许设计师在三维或二维视口中直接拖放几何体、光源、触发器和角色出生点，而无需手动编写场景序列化代码。现代关卡编辑器的直系祖先可追溯到1992年id Software为《德军总部3D》内部开发的地图工具，到1996年《Quake》的QuakeEd编辑器首次以独立工具形式对社区开放，奠定了"刷子几何体（Brush Geometry）"工作流的雏形。

关卡编辑器的核心价值在于将Blockout阶段的灰盒原型快速转化为可测试的游戏场景。设计师在完成空间比例和流线验证之后，需要一个能够同步处理碰撞体积、导航网格（NavMesh）烘焙、光照预计算和资产替换的集成环境。如果缺少关卡编辑器，这些操作将分散在若干独立脚本和外部工具中，迭代周期将从小时级延长到天级。

目前市场占有率最高的三款关卡编辑器分别是：虚幻引擎（Unreal Engine）的内置关卡编辑器、Unity的Scene View编辑环境，以及Godot Engine的Scene Editor。三者在技术架构和设计哲学上存在根本性差异，直接影响团队的工作流选择。

## 核心原理

### 场景层级与Actor/GameObject模型

虚幻引擎的关卡以**World → Level → Actor**三层结构组织。每个放置在关卡中的对象称为Actor，Actor通过Component（组件）挂载网格体、碰撞、逻辑等功能，这种"Actor是容器，Component是功能"的设计使关卡编辑器可以在不修改蓝图类的前提下覆盖单个实例的属性（Instance Override）。Unity的Scene View则采用**Scene → GameObject → Component**结构，逻辑几乎等价，但Unity的预制件（Prefab）系统允许嵌套预制件（Nested Prefab，自2018.3版本引入），解决了大型场景中批量更新资产的痛点。Godot则以**Scene → Node**树的形式统一了关卡与角色的概念，任意节点树都可以作为独立场景保存并实例化，这使关卡本身与角色在编辑器层面没有本质区别。

### 视口操作与坐标系

三款编辑器的视口均提供透视视图（Perspective）和正交三视图（Top/Front/Side），但默认坐标系存在差异：虚幻引擎使用**左手坐标系，Z轴朝上**；Unity使用**左手坐标系，Y轴朝上**；Godot 3.x使用右手坐标系Y轴朝上，而Godot 4.0起切换为右手坐标系Y轴朝上但旋转方向有变化。这一差异导致在不同引擎间导入FBX资产时需要进行-90°或90°的轴旋转补偿，是跨引擎关卡移植时最常见的对齐错误来源。网格对齐（Grid Snapping）是关卡编辑器中保持模块化资产无缝拼接的基础功能，虚幻引擎默认网格步进为10cm，Unity默认为0.25单位（1单位=1米）。

### 光照与烘焙集成

虚幻引擎的关卡编辑器内置**Lightmass全局光照烘焙系统**，设计师可直接在编辑器中设置光照质量预设（Preview/Medium/High/Production）并触发分布式烘焙任务，烘焙结果以Lightmap Atlas的形式保存在关卡的MapBuildData资产中。Unity的关卡编辑器通过**Baked Global Illumination**（Lightmapper后端支持Enlighten和Progressive两种，其中Progressive Lightmapper自Unity 2017.1引入）实现类似功能，但光照数据存储在场景同名文件夹下的独立资产集合中。Godot 4的关卡编辑器集成了**LightmapGI节点**，烘焙数据直接嵌入场景文件，在轻量级项目中维护成本更低，但不支持虚幻Lightmass级别的辐射度计算精度。

### 导航网格生成

三款编辑器均支持自动导航网格生成，但触发方式不同。虚幻引擎在关卡中放置**Nav Mesh Bounds Volume**后，运行时或编辑器中按P键即可可视化导航网格；Unity需要在窗口菜单中打开**Navigation（Bake）面板**并选择静态障碍物的Navigation Static标记后手动烘焙；Godot 4使用**NavigationRegion3D**节点并调用烘焙功能。关卡编辑器将这些操作统一集成在可视化界面中，是纯代码方案无法替代的效率优势。

## 实际应用

在2020年发布的《赛博朋克2077》开发过程中，CD Projekt Red使用REDengine 4的自研关卡编辑器构建了超过100km²的夜之城地图，其关卡编辑器的流式加载层（Streaming Layer）系统允许设计师在同一视口中同时预览多个流关卡块，这是虚幻World Partition（2021年随UE5正式落地）的早期工程实践参照之一。

对于独立开发团队，Unity的Scene View因其低上手成本被广泛采用：将一个标准的第三人称关卡原型从Blockout阶段推进到美术替换阶段，使用Unity ProBuilder（场景内建模插件）配合Scene View，单人操作可在8小时内完成100m×100m级别的关卡基础搭建，包括碰撞设置和导航烘焙。而相同规模的虚幻引擎项目因为需要额外配置World Settings、Build Lighting等步骤，首次搭建通常需要12-16小时。

## 常见误区

**误区一：关卡编辑器只是"摆东西的地方"**
关卡编辑器同时承担触发器逻辑绑定、关卡流（Level Streaming）配置、LOD组设置和后处理体积（Post Process Volume）调整等工作。以虚幻引擎为例，一个完整的关卡文件（.umap）中通常包含数百个Actor，其中几何体Mesh Actor占比约40-60%，其余均为逻辑组件、光源、触发盒和音效Actor。将编辑器理解为纯粹的摆放工具会导致团队将过多逻辑硬编码进角色蓝图而非关卡层级，造成场景逻辑难以复用。

**误区二：三款主流编辑器可以无缝互换**
虽然三款编辑器在视觉操作上相似，但其场景文件格式存在根本性差异。虚幻的.umap是二进制格式（UE5引入了One File Per Actor以改善版本控制），Unity的.unity场景文件是YAML文本格式，Godot的.tscn是文本格式。这意味着在项目中期切换引擎时，关卡数据几乎无法直接迁移，只有几何体网格（FBX/OBJ）可以跨引擎复用，而触发器、光源参数和导航设置必须重新配置。

**误区三：编辑器内所见即游戏内所见（WYSIWYG）**
关卡编辑器的视口渲染与游戏运行时渲染存在显著差异，尤其体现在光照上。虚幻引擎编辑器默认使用动态天光预览，而最终发布版本往往使用烘焙光照，两者在阴影细节和环境光遮蔽上差异肉眼可见。Unity的Scene View同样不反映最终Post Processing Stack效果，必须通过Game View并开启Play Mode才能看到准确的视觉输出。

## 知识关联

学习关卡编辑器概述的前置概念是**Blockout**：Blockout阶段产生的灰盒几何体和空间比例数据是关卡编辑器处理的第一批输入，理解Blockout中建立的模块网格尺寸（如128cm或256cm的标准单元）有助于在编辑器中正确设置网格吸附步长。

掌握关卡编辑器概述之后，有四个方向可以深入展开：**UE5关卡编辑器**（重点学习World Partition、OFPA和PCG图表）和**Unity场景编辑器**（重点学习Prefab工作流与Addressables集成）属于引擎专项技能；**关卡版本控制**涉及如何在团队协作中处理.umap二进制冲突或.unity YAML合并冲突的具体策略；**PCG关卡生成**则将关卡编辑器从手动摆放工具扩展为程序化规则的可视化调试环境，是关卡编辑器使用方式的重要演进路径。