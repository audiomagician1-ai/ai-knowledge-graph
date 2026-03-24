---
id: "3da-bake-cage"
concept: "Cage设置"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Cage设置

## 概述

Cage（烘焙笼）是法线烘焙流程中的一个辅助网格结构，其本质是将低模（Low Poly）的每个顶点沿法线方向向外膨胀一定距离后生成的包裹体。烘焙器在执行光线投射时，不会从低模表面本身发射射线，而是从这个膨胀后的Cage表面向内朝高模方向投射，从而采样到正确的法线信息。

Cage的概念最早随着基于投射的法线烘焙工作流在游戏工业中普及而被引入，xNormal等专用烘焙工具在2005年前后将Cage作为独立可配置选项提供给美术师。在此之前，许多工具只支持简单的"前后搜索距离"（Front/Back Distance）参数，容易在复杂凹凸几何体处产生烘焙错误。Cage的出现使美术师能够对不同区域的射线投射起点进行精细的局部控制。

Cage设置直接决定了法线贴图在凸起、凹陷以及自遮挡区域是否出现黑色阴影瑕疵（俗称"爆点"或"接缝漏光"）。对于一个角色腋下、耳廓内侧或盔甲拼接处等凹入区域，若无正确配置的Cage，投射射线将在到达高模之前撞到低模自身，导致该像素采样失败并呈现错误的紫黑色。

---

## 核心原理

### Cage的生成方式

Cage网格通过将低模的每个顶点沿其**顶点法线**（Vertex Normal）方向位移一个标量距离d来生成，公式为：

> **P_cage = P_lowpoly + d × N_vertex**

其中 `P_lowpoly` 是低模顶点的世界坐标，`N_vertex` 是该顶点的平均法线方向（单位向量），`d` 是偏移量（单位与场景单位一致，常见单位为厘米或Blender中的米）。生成后的Cage是一张独立的网格文件或在工具内部以参数形式存储，它与低模拓扑完全相同，仅顶点位置不同。

在Blender的Cycles烘焙面板中，Cage功能对应"Extrusion（挤出）"数值；在Marmoset Toolbag 4中对应每个Bake Group的"Cage Offset"滑块；在3ds Max的Projection修改器中则称为"Cage"可编辑网格。这三款工具的核心数学逻辑相同，只是界面命名有差异。

### 偏移距离的设定原则

偏移量 d 需要满足一个条件：Cage在所有区域必须完整地包裹住高模，即高模的每一个凸出点必须位于Cage包裹体的**内侧**。偏移量过小时，高模局部突起会刺穿Cage，射线将采集到错误方向的法线，产生黑斑。偏移量过大时，Cage会在凹入区域发生"穿插"——相邻的Cage面彼此交叠，射线可能采集到错误的对面几何体，产生拉伸或镜像瑕疵。

实践中的经验起始值：对于一个约2米高的游戏角色，其整体Cage偏移常设置在 **0.01～0.05单位**（Blender米制）范围内作为初始测试值；对于机械硬表面模型，由于细节较多且凹槽深，往往需要分部件使用 **不同偏移量** 的多组烘焙对。

### 自定义Cage网格

当全局统一偏移无法解决局部问题时，可以手动编辑Cage网格。以3ds Max为例，在Projection修改器中展开Cage子层级后，可以直接拖拽特定顶点，将问题区域的Cage面手动推离高模凸起。这种手动Cage适用于有极端细节落差的区域，例如角色腰带扣件（小型高频细节）与背部大面（低频平坦区域）处于同一烘焙组时：手动把腰带扣处的Cage顶点单独外推，而不影响背部大面的精确投射距离。

---

## 实际应用

**游戏角色头盔烘焙**：头盔顶部铆钉（Rivet）突出低模表面约0.8厘米。若全局Cage偏移设为0.02厘米，铆钉顶端将刺穿Cage，烘焙出黑色区域。正确做法是将Cage偏移设为至少1.0厘米，或在Marmoset中启用"Per-Object Cage"对铆钉单独设置偏移。

**Blender中的Extrusion与Max Distance联动**：Blender烘焙面板中同时存在"Extrusion"（相当于Cage偏移）和"Max Ray Distance"两个参数。Extrusion控制射线起点外推距离，Max Ray Distance控制射线最大投射长度。当低模与高模之间的距离超过Max Ray Distance时，即使Cage设置正确，射线也会因超出最大距离而采样失败。因此两者需要协调配置，常见搭配：Extrusion=0.02m，Max Ray Distance=0.1m。

**硬表面分组烘焙策略**：对于机甲类角色，工业标准做法是按部件将低模/高模分成多个烘焙组（Bake Group），每个组独立设置Cage偏移。躯干大面偏移0.01m，管道细节偏移0.05m，关节嵌套区域偏移0.08m。这种策略在Marmoset Toolbag 4中通过拖拽不同Mesh对象到不同Bake Group来实现。

---

## 常见误区

**误区一：认为Cage偏移越大越安全**
增大Cage偏移在凸面区域确实能消除黑斑，但在凹入区域（如角色腋下、两片几何体相交处）会导致Cage面自交，射线穿过Cage内部的错误空间，采集到完全不相关的高模面，产生拉伸纹理瑕疵。正确做法是用"刚好包裹高模"的最小可用偏移量，而非无限加大。

**误区二：把Cage和光线距离（Ray Distance）当作同一参数**
Cage偏移决定的是**射线起点**的位置，而光线距离（Max Ray Distance / Search Distance）决定的是**射线终点**的最大范围。一些初学者在遇到烘焙黑斑时会错误地调大Ray Distance来解决，这实际上会引入更多错误采样（捡取到不相关的背景几何体法线）。黑斑若是由射线被低模自身遮挡引起，只有增大Cage偏移才能修复。

**误区三：认为不使用Cage就无法烘焙**
不使用Cage时，烘焙器会默认使用低模表面作为射线起点并配合前后搜索距离（Front/Back Distance）进行投射，对平坦或简单几何体完全可行。Cage的必要性随低模几何体的复杂度和自遮挡程度上升，对于一块简单的地面砖块，无Cage的默认烘焙往往已经足够。

---

## 知识关联

**前置概念——法线烘焙**：理解Cage设置的前提是已知法线烘焙中"射线投射"机制——即从低模朝高模发射射线并读取交点处法线的流程。Cage设置本质上是对这个射线发射起点的空间位置做精确控制，没有对法线烘焙投射原理的认识，无法判断何时需要调整Cage。

**后续概念——光线距离（Ray Distance）**：掌握Cage设置后，下一步需要配置光线距离参数，即射线从Cage表面出发后最远可以投射多远。两者共同定义了"射线从哪里出发、走多远停止"这一完整的投射空间范围，是处理低模与高模存在较大位置偏差（如浮动几何体 Floater）时必须联合调校的一对参数。
