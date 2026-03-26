---
id: "3da-sculpt-zbrush-workflow"
concept: "ZBrush工作流"
domain: "3d-art"
subdomain: "sculpting"
subdomain_name: "数字雕刻"
difficulty: 2
is_milestone: true
tags: ["工作流"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.414
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# ZBrush工作流

## 概述

ZBrush工作流是指在Autodesk ZBrush软件中，从模型导入到最终输出的全过程管理方式，其核心特征是以SubTool系统为基础的非破坏性多部件组织体系。与传统三维软件（如Maya或Blender）使用场景层级（Hierarchy）不同，ZBrush将每个独立网格体存储为一个SubTool条目，所有SubTool共同构成一个Tool（工具文件），整体保存为.ZTL格式。

ZBrush的SubTool系统最早在ZBrush 3.1版本（2008年）中得到系统化完善，此后历经多次迭代，至ZBrush 2021版本引入了SubTool文件夹（Folder）功能，允许将多个SubTool分组归类，极大提升了管理复杂角色（动辄拥有50至200个SubTool）时的工作效率。理解这套工作流对于角色艺术家、道具设计师在ZBrush中完成从草稿雕刻到烘焙输出的完整生产链路至关重要。

ZBrush工作流的独特价值在于它的"雕刻优先"逻辑——艺术家可以在极高细节层级（Subdivision Level可达7至8级，面数超过一亿）下工作，而无需顾虑传统建模软件的性能瓶颈，但这也要求艺术家建立一套严格的SubTool命名、合并、细节分配规范，否则项目后期会陷入混乱。

---

## 核心原理

### SubTool的层级结构与命名规范

每个ZBrush Tool文件可容纳最多999个SubTool（官方技术上限），但实际生产中超过100个即会影响操作流畅度。专业工作流通常遵循**类别_部件_版本号**的命名格式，例如`Char_Head_v02`或`Prop_Sword_Guard_v01`，并配合ZBrush 2021引入的Folder功能将"身体"、"服装"、"配件"等拆分为独立文件夹组。

SubTool的排列顺序影响渲染遮挡关系：位于列表上方的SubTool在BPR（Best Preview Render）渲染中优先级更高。因此惯例是将皮肤、身体等基础结构放在列表底部，而将头发、装备、饰品等附加物置于上方，这与Photoshop图层逻辑正好相反，是初学者最容易混淆的地方。

### Subdivision细分级别的管理策略

ZBrush的Subdivision系统（快捷键`Ctrl+D`增加细分，`D`和`Shift+D`在级别间切换）是工作流中最需要计划的部分。专业流程通常遵循"3-3-2"原则：低模阶段保留3级以内用于形体调整，中模阶段3至5级用于肌肉与结构细化，高模阶段6至7级专门用于表面纹理与毛孔雕刻。在高细分级别下对大形体进行调整会导致低细分级别出现不可预期的形变，因此跨级别修改时必须先降回相应级别。

当需要对已有细分层级的SubTool添加新的拓扑循环时，必须使用ZRemesher（快捷键在`Geometry > ZRemesher`面板）重新拓扑，此操作会清除所有现有细分层级，因此正确的工作流是在大形体锁定后再进行ZRemesher，避免重复劳动。

### DynaMesh与传统细分的切换时机

DynaMesh是ZBrush的动态重拓扑功能，通过`Ctrl+拖拽`（在Canvas空白处）触发，适合概念雕刻和布尔运算（Live Boolean）阶段。DynaMesh分辨率数值（Resolution）直接决定网格密度：数值128对应约50万面，数值512对应约800万面。

专业工作流的关键切换节点是：当形体确定、需要保持细节并进入细分雕刻阶段时，必须退出DynaMesh状态，先使用ZRemesher生成均匀四边形网格，再开始添加Subdivision层级。DynaMesh与Subdivision是互斥工作状态，DynaMesh激活时无法添加传统细分层级，这是ZBrush工作流中影响生产节奏的最重要技术约束。

### SubTool的合并与输出规范

ZBrush提供两种SubTool合并操作：`Merge Down`（向下合并相邻SubTool，保留两者网格数据）和`Merge Visible`（合并所有可见SubTool为单一网格）。合并前必须确认所有参与合并的SubTool处于相同Subdivision级别，否则ZBrush会自动将所有对象统一到最高细分级别，可能导致文件体积爆炸式增长。

导出流程方面，ZBrush通过`Export`功能可输出OBJ或FBX格式，但推荐使用GoZ插件（ZBrush与Maya/Blender的桥接通道）进行实时数据传输，GoZ传输时会保留SubTool各自的UV和材质分配信息，而直接Export则需要手动重新分配材质组。

---

## 实际应用

**角色制作完整流程示例：** 在制作一个游戏角色时，典型的ZBrush工作流分为四个阶段。第一阶段使用DynaMesh（分辨率64-128）快速建立头部、身体、四肢的粗模，每个部位独立存为SubTool。第二阶段对身体主体进行ZRemesher（目标面数约5000-8000个四边形），添加至3级Subdivision后雕刻肌肉大形。第三阶段细化至6级Subdivision，使用Standard笔刷（快捷键`B-S-T`）雕刻毛孔和皮肤纹理，此阶段严禁修改低级细分。第四阶段使用Decimation Master（位于`Zplugin`菜单）将高模压缩至低模体积的1/50至1/30，导出供烘焙法线贴图使用。

**遮罩与SubTool联动应用：** 在对角色面部进行局部细节雕刻时，通过`Ctrl+点击`SubTool列表中其他SubTool可以快速遮罩/显示相邻部件，以便检查穿插关系。利用遮罩提取功能（`Tool > SubTool > Extract`）可以直接从现有SubTool表面生成厚度可控的新SubTool，常用于制作紧贴身体的服装部件，Extract Thickness参数通常设置在0.01至0.05之间。

---

## 常见误区

**误区一：在DynaMesh状态下直接开始精细雕刻。** 许多初学者在DynaMesh模式下将分辨率不断提高（512甚至1024），试图在其中完成所有细节。但DynaMesh的三角面网格分布不均匀，笔刷在三角面密集区与稀疏区的表现完全不同，导致细节分布不自然。正确做法是DynaMesh只负责大形体塑造，分辨率控制在256以内，细节雕刻必须在ZRemesher后的四边形网格加细分层级的状态下进行。

**误区二：将所有部件合并为单一SubTool进行雕刻。** 有些艺术家习惯于其他软件中"全选一起操作"的思路，在ZBrush中也倾向于把所有部件合并成一个整体。这会导致无法对单独部件进行Subdivision级别管理，衣物配件与皮肤需要的细分级别不同（配件通常需要4-5级，皮肤需要6-7级），强行合并后任一部件的修改都会影响全局，完全丧失SubTool体系的核心优势。

**误区三：混淆Tool文件与SubTool的保存逻辑。** ZBrush的`Save`功能（`Ctrl+S`）默认保存的是整个程序状态（.ZPR格式，包含所有打开的Tool和界面设置），而非单独的Tool文件。单独保存当前Tool（包含其所有SubTool）必须使用`Tool > Save As`，输出为.ZTL格式。不了解这一区别会导致在不同项目间切换时丢失数据，或在协作时无法正确传递模型文件。

---

## 知识关联

本文档所述工作流以**遮罩与分组**技术作为直接前置基础——遮罩操作（`Ctrl+拖拽`绘制，`Ctrl+点击空白`反转）在SubTool之间的局部保护和提取操作中被高频使用，而PolyGroup分组则是ZRemesher拓扑引导和局部细分（`Geometry > Divide`中的`SDiv by Groups`选项）的依赖条件。没有熟练的遮罩和分组操作，SubTool的精细管理工作流无法有效执行。

在掌握SubTool管理与整体工作流后，艺术家通常进入**ZBrush贴图绘制与Polypaint系统**的学习，或转向**ZBrush到引擎的烘焙导出流程**，二者均以本文所述的SubTool结构、Subdivision级别管理和GoZ/Export输出规范为直接操作基础。