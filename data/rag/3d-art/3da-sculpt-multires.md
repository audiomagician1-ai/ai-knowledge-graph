---
id: "3da-sculpt-multires"
concept: "多分辨率雕刻"
domain: "3d-art"
subdomain: "sculpting"
subdomain_name: "数字雕刻"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 多分辨率雕刻

## 概述

多分辨率雕刻（Multiresolution Sculpting）是一种将同一个三维网格同时存储在多个细分层级上的数字雕刻技术。艺术家可以在低分辨率层级调整整体造型，然后切换到高分辨率层级添加细节，而低层级的修改不会破坏高层级已雕刻的细节——这种特性称为**非破坏性工作流**。

该技术最早在Pixologic ZBrush 1.x时代以原型形式出现，并在2005年ZBrush 2.0中以成熟的SDiv（Subdivision Level）系统正式推出。Blender在2.81版本（2019年11月）重写了多分辨率修改器（Multiresolution Modifier），将其整合进雕刻模式，使其成为与ZBrush并列的主流实现方案。

多分辨率雕刻之所以在角色制作流程中不可替代，是因为游戏角色的法线贴图烘焙需要从高模到低模的精确细节映射，而多分辨率系统的层级结构天然提供了"同一拓扑下的高低模对"，省去了重新拓扑后再重新雕刻的大量返工。

---

## 核心原理

### 细分层级（SDiv）的数学基础

每上升一个细分层级，网格面数量乘以4。一个初始有1,000个面的基础网格，在SDiv 1时有4,000面，SDiv 2时有16,000面，SDiv 6时则达到4,096,000面。这是Catmull-Clark细分曲面算法的直接结果：每个四边形面被分成4个子四边形，新生顶点的位置由周围顶点加权平均计算得出，保证曲面在极限状态下光滑连续（G2连续）。

### 置换偏移的分层存储

多分辨率系统并不直接存储每个层级的全量顶点坐标，而是存储**相对于下层细分预测位置的偏移向量（Displacement Offset）**。设某顶点在SDiv N的预测位置为 $\hat{P}_N$，实际雕刻位置为 $P_N$，则系统存储的是差值 $\Delta_N = P_N - \hat{P}_N$。这种存储方式使得修改低层级（如SDiv 2）时，系统能重新计算高层级（如SDiv 5）的预测位置，并将原有的 $\Delta_5$ 偏移叠加回去，从而保留高层级细节。

### 层级传播方向

多分辨率雕刻中存在两个重要的操作方向：
- **向下传播（Propagate Down / Reshape）**：将低层级的形体修改同步更新到高层级，重新计算所有层级的偏移值。在Blender中对应"应用低级别"操作。
- **向上雕刻（Normal Sculpting）**：在当前激活层级直接添加笔刷细节，只修改当前层级及以下的偏移值，不影响更高层级已有内容。

ZBrush中的"Freeze SubDivision Levels"（冻结细分层级）功能允许艺术家在低层级做体块调整时，临时锁定高层级数据，防止意外的向上传播。

---

## 实际应用

### 角色头部雕刻的标准分层策略

在典型的写实角色流程中，头部网格从SDiv 1（约2,000面）到SDiv 6（约128,000面）会按如下方式分配工作内容：
- **SDiv 1–2**：用Move笔刷调整头骨比例、眉弓突出度、颧骨宽度等大型体块
- **SDiv 3–4**：用Clay Buildup笔刷建立眼皮、嘴唇、鼻翼的二级形体
- **SDiv 5–6**：用Damian Standard笔刷（ZBrush）或Crease笔刷雕刻毛孔、细纹、皮肤褶皱

### 法线贴图烘焙的层级对

多分辨率系统的SDiv 1层级直接作为游戏引擎使用的低模，SDiv 5或SDiv 6作为烘焙源。在Blender中，多分辨率修改器可以直接通过"Apply as Shape Key"或通过Bake功能将高低模差值烘焙为法线贴图，无需导出步骤，整个流程在同一文件内完成。

### 从ZBrush导入ZRemesh后的层级重建

当艺术家在ZBrush高层级SDiv 5完成雕刻后，有时需要对网格进行ZRemesh（重拓扑）。此时标准流程是：对ZRemesh后的干净低模重新进行5次细分，然后使用**Project All**（Zplugin > Decimation Master旁边的功能）将原始高模细节投射到新拓扑的对应层级上，从而在新网格上重建多分辨率结构。

---

## 常见误区

### 误区一：在高层级修改体块

许多初学者在SDiv 5上发现比例不对，直接用Move笔刷修改大型体块，结果造成高层级存储了大量本应属于SDiv 2的形体数据。后续想用Smooth笔刷清理时，由于偏移量过大，Smooth会误删精细细节。正确做法是返回SDiv 1或SDiv 2，用Move笔刷修改体块后，再通过Propagate操作更新高层级。

### 误区二：混淆多分辨率雕刻与动态拓扑（DynaMesh/Dyntopo）

动态拓扑（Blender的Dyntopo，ZBrush的DynaMesh）会在雕刻过程中**实时重新三角化网格**，破坏原有拓扑，因此无法维持细分层级结构。激活了DynaMesh的ZBrush SubTool无法切换SDiv层级——这两种系统的使用阶段是互斥的：DynaMesh用于概念探索阶段，多分辨率用于确定拓扑后的精细化阶段。

### 误区三：层级数量越多越好

将SDiv层级设置到8或9并不能比SDiv 6提供更多视觉价值，却会使单次Propagate操作的计算量成指数增长。对于1K分辨率法线贴图，SDiv 5（约500万面，分辨率约2000×2000点密度）已经远超烘焙需求，过高的层级只会延长保存和重新加载文件的时间。

---

## 知识关联

### 前置概念：数字雕刻概述

理解多分辨率雕刻需要掌握数字雕刻的基础笔刷系统，特别是Clay、Move、Smooth三类笔刷对顶点偏移的基本操作方式，因为多分辨率系统只改变了这些操作**作用于哪个层级**，而不改变笔刷本身的计算逻辑。

### 后续概念：雕刻层（Sculpt Layers）

雕刻层（ZBrush中的Layers面板，Blender中的Shape Keys雕刻工作流）是在**固定单一SDiv层级内**叠加可开关的形变偏移，解决同一高分辨率层级下"多套细节方案"的管理问题。它与多分辨率的层级系统形成正交关系：多分辨率管理垂直的精细度维度，雕刻层管理水平的方案变体维度。

### 后续概念：细节投射（Detail Projection）

细节投射技术是多分辨率工作流在网格拓扑变更后的接续手段。ZBrush的Project All和Blender的Multires Reshape操作，都依赖多分辨率系统的逐层偏移结构来确定投射精度：投射只能向已存在的SDiv层级写入偏移量，这是为什么细节投射必须在多分辨率细分完成后才能执行的原因。