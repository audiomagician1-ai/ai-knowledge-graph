---
id: "3da-sculpt-cleanup"
concept: "雕刻清理"
domain: "3d-art"
subdomain: "sculpting"
subdomain_name: "数字雕刻"
difficulty: 2
is_milestone: false
tags: ["流程"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 雕刻清理

## 概述

雕刻清理（Sculpt Cleanup）是指在数字雕刻的细节工作完成之后，对高模网格进行法线修复、多边形噪点消除和表面平滑化的后处理流程。这一步骤的目标不是继续添加细节，而是剔除雕刻过程中产生的伪影（Artifacts）、法线翻转面以及过度密集的局部多边形堆叠，使模型达到可渲染或可用于烘焙的干净状态。

雕刻清理的概念随着ZBrush在2000年代初期的普及而逐渐成型。早期数字雕刻师发现，直接将雕刻完成的高模用于渲染时，往往出现不自然的高光条纹（Shading Seams）和法线插值错误，这些问题在ZBrush 3.0引入DynaMesh工具之后变得更为突出——DynaMesh重拓扑后的网格经常在凹陷区域留下法线方向不一致的三角面，必须通过清理步骤加以修正。

雕刻清理的重要性体现在其位于整个雕刻-烘焙流程的关键节点：一个未经清理的高模，其法线贴图烘焙结果会含有与雕刻噪点同源的黑斑或错误的阴影条纹，即便拓扑重构（Retopology）完成得非常精确，这些错误也会被完整转移到法线贴图中，导致最终游戏或影视资产出现质量缺陷。

---

## 核心原理

### 法线修复（Normal Repair）

高模在多次DynaMesh或ZRemesher操作后，部分三角面的法线方向会因算法误判而指向模型内部，这种现象称为法线翻转（Flipped Normals）。在ZBrush中，可通过 **Tool > Display Properties > Flip** 逐SubTool检测翻转面；在Blender中则使用叠加层（Overlay）中的"面朝向"（Face Orientation）功能，蓝色表示外法线正确，红色表示翻转。翻转面必须在清理阶段全部修正，否则法线贴图烘焙时该区域会产生错误的凹凸反转效果。

修复方法包括：在ZBrush中对整体使用 **Tool > Geometry > Modify Topology > Flip Normals**；在Blender编辑模式中选中所有面后执行 **Mesh > Normals > Recalculate Outside**（快捷键 Shift+N）。对于局部翻转，建议手动选中问题面后单独翻转，避免全局操作误伤正确法线。

### 表面噪点平滑（Surface Noise Smoothing）

数字雕刻中长时间使用Standard笔刷、Clay笔刷或Inflate笔刷，会在网格表面残留肉眼不易察觉的高频噪点——这些噪点在平视观察时隐蔽，但在法线贴图烘焙后会以细小杂点形式暴露。ZBrush的 **Smooth笔刷**（快捷键按住Shift）配合较低的Intensity（建议值10~20）进行多次轻扫，可在保留主要细节的同时消除这类噪点。更精准的方案是使用ZBrush的 **Polish & Relax** 功能（Deformation面板 > Polish值设置为1~3），该功能针对曲率的局部松弛算法能在不破坏锐边的前提下平滑微小不规则性。

### 几何密度均匀化（Polygon Density Equalization）

雕刻过程中，艺术家往往在面部、手部等细节丰富区域反复细分，导致局部多边形密度比其他区域高出数倍——例如一个800万面的角色头部模型，眼角褶皱区域的局部密度可能是颈部的15倍以上。这种密度不均匀会造成法线贴图采样时的精度不一致：高密度区过采样、低密度区欠采样，烘焙结果在两者边界出现明显的精度跳变线（Density Seam）。

ZBrush的 **ZRemesher**（Tool > Geometry > ZRemesher）提供了密度引导绘制功能（ZRemesherGuide笔刷），允许艺术家在清理阶段通过绘制红/蓝色权重来指定目标密度分布，红色区域密度更高，蓝色区域密度更低，最终输出一个密度更均匀的清理版高模，专门用于后续烘焙，而原始雕刻版本则保留存档。

### 孤立面与内部几何清理（Isolated Geometry Cleanup）

DynaMesh在处理模型穿插区域（如衣物与皮肤的接触面）时，有时会在内部生成不可见的孤立多边形岛（Isolated Polygon Islands）。这些内部几何体不影响外观，但会增大文件体积，并可能在烘焙时被射线检测到而产生错误黑斑。在ZBrush中，可通过 **Tool > Geometry > Modify Topology > Del Hidden** 删除隐藏面；在Blender中，通过 **Select > Select All by Trait > Interior Faces** 选中并删除内部面。

---

## 实际应用

**游戏角色高模清理流程**：以一个用于次世代手游的战士角色为例，雕刻完成后其ZBrush文件包含约1200万面。清理步骤如下：首先在Display Properties中全局检测法线，发现腰带扣处有约30个翻转面，手动修正；随后对皮肤区域以Intensity 15的Smooth笔刷轻扫三遍，消除Clay笔刷遗留的横向条纹噪点；使用ZRemesherGuide在手指关节绘制红色高密度区、背部大面积区域绘制蓝色低密度区，执行ZRemesher后输出800万面的清理版高模，密度分布均匀度提升约40%；最后在Blender中执行Interior Faces检测，删除腋窝内部的17个孤立面。经过以上清理，最终烘焙出的2K法线贴图中噪点数量从清理前的可见杂点完全消除。

**影视资产清理与游戏资产清理的差异**：影视高模通常不需要烘焙法线贴图，其清理重点在于表面一致性和渲染可见面的法线正确性，对多边形密度均匀性要求相对宽松；而游戏资产的清理必须为后续烘焙服务，密度均匀化是最优先的清理目标。

---

## 常见误区

**误区一：清理等同于再次雕刻细节**
许多初学者在清理阶段继续使用Clay或Standard笔刷添加细节，导致清理后的模型产生新的表面噪点，陷入"雕刻—清理—再雕刻"的死循环。雕刻清理的核心准则是**只减不增**：Smooth笔刷、Relax算法是主要工具，任何添加性笔刷都不应在此阶段出现，除非是修补法线翻转面附近的明显凹陷。

**误区二：全局Smooth会破坏所有细节**
部分初学者因担心Smooth破坏细节而完全跳过表面平滑步骤，或使用过高的Intensity值（50以上）一次性平滑，结果要么是保留了所有噪点，要么是丢失了精细的皮肤纹理。正确做法是将Smooth笔刷的Intensity设置在10~20之间，配合较大的笔刷半径进行轻扫，高频噪点（波长小于笔刷半径1/10）会被消除，而波长接近或大于笔刷半径的主要细节（如毛孔、皱纹）则得以保留。

**误区三：ZRemesher清理版可以替代原始雕刻存档**
ZRemesher在重新拓扑过程中会对顶点位置进行轻微位移，导致清理版高模与原始版高模存在约0.1%~0.3%的几何误差。若仅保留清理版，原始雕刻的精确细节已不可逆地丢失。正确做法是将原始雕刻版（作为存档）与清理版（用于烘焙）分开保存为两个ZTool文件，文件命名建议加上`_raw`和`_clean`后缀以区分。

---

## 知识关联

**与细节雕刻的衔接**：细节雕刻阶段产生的高频笔刷噪点和DynaMesh重拓扑残留是雕刻清理需要处理的直接来源。理解细节雕刻中不同笔刷（Clay Buildup、Dam Standard、Alpha笔刷）在网格上留下的噪点特征，有助于在清理阶段针对性地选择Smooth还是Relax工具。

**对雕刻展示的影响**：清理后的模型表面法线一致性直接决定了在KeyShot、Marmoset Toolbag或ZBrush BPR渲染器中的高光表现质量。法线翻转和表面噪点在渲染灯光下会被放大为明显的黑斑或条纹，因此雕刻清理是实现高质量雕刻展示作品（Portfolio Render）的必要前提。

**为拓扑重构奠定基础**：拓扑重构（Retopology）中常用的投影烘焙（Project）和法线贴图烘焙均以高模作为参考源，若高模存在翻转法线或密度极度不均匀，投影精度会大幅下降，低模表面会出现与高模雕