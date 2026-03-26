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

ZBrush工作流是指在ZBrush软件中，通过SubTool列表管理多个独立网格对象、配合遮罩与分组功能进行非破坏性雕刻的一套完整操作体系。与Maya或Blender等软件的场景层级管理不同，ZBrush将所有对象存储在单一的Tool文件（.ZTL格式）中，每个SubTool相当于一个独立的3D对象层，可以单独显示、隐藏、合并或分裂。

ZBrush的工作流体系在ZBrush 4R2版本（2011年发布）后随着SubTool数量上限从12个扩展到实际硬件限制而大幅成熟。Pixologic（现已被Maxon收购）设计这套工作流的核心逻辑是"先整体形态，后局部细节"——从低精度的基础型体开始，通过Dynamesh重拓扑、ZRemesher自动减面、再到手动细分（Subdivision Level）逐层叠加细节，最终在最高细分级别雕刻毛孔和微观纹理。

这套工作流之所以受到影视角色艺术家和游戏角色师广泛采用，是因为它允许在不同细分级别之间自由切换而不丢失任何雕刻数据，同时SubTool的分层管理使复杂角色（如含有盔甲、皮肤、头发道具的角色）可以分部件独立作业，大幅降低单次操作的计算压力。

---

## 核心原理

### SubTool层级与文件结构

ZBrush的.ZTL文件本质上是一个容器，其中每个SubTool存储自己独立的：网格数据（含所有细分级别）、多边形分组颜色、顶点色、UV信息以及对应的法线贴图烘焙数据。SubTool列表顶部的对象优先级最高（影响合并顺序），通过"Merge Down"命令可将相邻两个SubTool合并为一个，合并后的对象继承下方SubTool的名称。合并操作会删除上方SubTool的细分历史，因此最佳实践是在确认形态正确后再执行合并，而不是随意整合。

SubTool文件夹（Folder）功能从ZBrush 2020版本正式加入，允许将多个SubTool打包进一个折叠组，例如将"左臂全部骨骼"放入一个文件夹便于批量操作显示状态，而不影响各自的细分数据。

### Dynamesh与ZRemesher的阶段切换逻辑

ZBrush工作流的早期阶段使用**Dynamesh**（动态网格）进行自由造型，其原理是在每次Ctrl+拖拽刷新时将网格体素化重构，分辨率由`Dynamesh Resolution`参数控制（通常设置128到512之间）。Dynamesh的优势是不存在拓扑限制，可以任意增减体积，但它会销毁所有细分历史，因此只适合形态探索阶段。

当主要形态确定后，工作流进入**ZRemesher**阶段：设置目标面数（如5000~15000面），勾选`Keep Groups`选项保留多边形分组颜色作为引导，ZRemesher会按照分组边界生成更规整的四边形拓扑。随后通过`Divide`（细分）将面数倍增（每次×4），在各个细分级别上分别雕刻宏观褶皱（Subdivision Level 2-3）和微观毛孔（Subdivision Level 6-7）。

### 遮罩与多边形分组在工作流中的协同

从上一阶段学习的遮罩与分组技能在ZBrush工作流中承担着**局部变形隔离**的功能。使用`Ctrl+W`将选中区域转为多边形分组后，可通过`Ctrl+Shift+点击`快速隐藏或隔离该分组，在不影响其他区域的情况下对局部进行Dynamesh或细分操作。典型使用场景：将角色面部皮肤设为分组1、眼皮设为分组2，在提高面部细节密度时通过分组隔离避免眼皮网格受到影响。

遮罩的淡化操作（`Ctrl+点击画布空白处`进行模糊，淡化强度通过`Blur`滑块控制，范围0~100）能够生成渐变遮罩边界，配合Move Topological笔刷进行自然过渡的形变——这是纯粹靠SubTool分层无法实现的过渡效果。

---

## 实际应用

**角色脸部雕刻流程**：首先从ZBrush内置的DefaultSphere开始，启用Dynamesh（分辨率128）快速捏出头部基础形态，此阶段约10~15分钟完成头骨比例。接着用ZRemesher生成约8000面的干净拓扑，执行6次Divide使面数达到约512000面，在Level 3雕刻颧骨和下颌骨的宏观形态，在Level 6雕刻眼周纹理和鼻翼细节，在Level 7刻画毛孔（通常使用Noise笔刷配合皮肤Alpha贴图）。

**硬表面盔甲工作流**：创建一个独立SubTool用于每块盔甲板，启用`Crease`（折痕）功能在边缘添加支撑环，再通过`Panel Loops`一键生成厚度，用`Polish By Groups`命令对各多边形分组单独平整表面。最终通过`Merge Visible`将所有盔甲SubTool合并为一个对象导出.OBJ供游戏引擎使用，保留原始.ZTL文件作为可修改的源文件备份。

**使用SubTool文件夹批量操作**：角色包含60个SubTool时，将"头部细节类"15个SubTool放入一个Folder，执行Folder级别的Show/Hide可在半秒内完成视口整理，配合`Solo Mode`（快捷键Alt+点击眼睛图标）快速聚焦到单个SubTool进行精细雕刻。

---

## 常见误区

**误区一：在Dynamesh阶段就急于细分雕刻细节**
许多初学者在Dynamesh形态尚未确定时便执行Divide添加细分，之后发现整体比例有误，再修改时会导致高细分级别的细节数据全部损坏。正确做法是等Dynamesh阶段完全满意后，一次性执行ZRemesher + Divide流程，细节雕刻只在最终拓扑上进行。

**误区二：将所有部件合并进同一SubTool以"减少SubTool数量"**
这会导致无法对单个部件进行细分级别的独立控制。例如角色牙齿不需要Level 7的细节，若与皮肤合并则强制共享相同的细分级别，导致内存浪费（一颗牙在Level 7约有65000面，而实际上Level 3的4000面已足够）。应保持牙齿为独立SubTool，按需单独分配细分资源。

**误区三：混淆ZBrush的"图层"（Layer）与SubTool**
ZBrush中的Layer（通过Layers面板添加）是在同一SubTool上叠加雕刻偏移的不同通道，可独立调整强度（0~1），类似Photoshop的图层混合，与SubTool的对象分离概念完全不同。初学者常误将需要用Layer实现的"表情变体"功能错误地用多个SubTool来实现，导致后期Blend Shape导出困难。

---

## 知识关联

**与前置知识"遮罩与分组"的连接**：遮罩与多边形分组是ZBrush工作流中几乎每一个操作步骤的基础工具。Ctrl+W分组、通过分组颜色引导ZRemesher走线、用遮罩隔离局部进行变形——这三个操作在每个典型ZBrush项目中平均被执行数十次，遮罩技能的熟练程度直接决定工作流的执行效率。

**与3D美术后续管线的衔接**：ZBrush工作流的最终输出分为两条路径——导出高模.OBJ用于法线贴图烘焙（在Marmoset Toolbag或Substance Painter中进行），或通过GoZ功能直接将Low-Poly网格推送至Maya/3ds Max进行绑定。理解.ZTL文件内部的细分层级存储方式（每个Level独立保存顶点偏移量delta值），有助于在跨软件协作时正确判断应在哪个Level导出网格以满足法线烘焙精度要求。