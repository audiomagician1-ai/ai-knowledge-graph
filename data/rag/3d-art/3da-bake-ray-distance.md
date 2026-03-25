---
id: "3da-bake-ray-distance"
concept: "光线距离"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: false
tags: ["参数"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 光线距离（Max Ray Distance）

## 概述

光线距离（Max Ray Distance）是烘焙系统中控制投射光线最大探测长度的参数，单位通常为场景单位（Scene Units）或厘米。在法线贴图、AO贴图、厚度贴图的烘焙过程中，系统从低模表面法线方向发射射线，Max Ray Distance决定了这条射线在放弃采样之前能够向外延伸的最远距离。若射线在该距离内未命中高模表面，烘焙器将以默认值（通常为中性法线 0,0,1 或黑色）填充该像素，直接影响最终贴图的准确性。

这一参数最早在Substance Painter 1.x版本中作为Cage工作流的补充选项引入，用于处理Cage网格无法覆盖的复杂凹凸区域。相较于完整的Cage设置流程，Max Ray Distance提供了一种更轻量的快速修正手段，适用于形状相对规整、高低模差异不超过场景单位5%的模型。在Marmoset Toolbag、Blender、xNormal等主流烘焙工具中，该参数的实现逻辑基本一致，只是默认值和命名略有差异（Blender中称为"Max Distance"，xNormal中称为"Max frontal ray distance"）。

正确配置Max Ray Distance能消除法线贴图上常见的"漏光"黑斑和错误采样条纹，是在不重新制作Cage的前提下快速提升烘焙质量的关键手段。

---

## 核心原理

### 射线投射的几何逻辑

烘焙时，系统从低模每个表面像素的位置出发，沿该像素法线方向向外（或向内）各发射一条射线。Max Ray Distance = D 时，射线的有效检测区间为从低模表面向外延伸 D 个单位。若高模表面位于 0 到 D 的范围内，射线命中，采样高模的法线/颜色等信息写入贴图；若高模位于 D 之外，射线未命中，该像素写入默认值，贴图上表现为明显的黑色或灰色异常块。

数学上，有效采样要求满足：

```
0 ≤ distance(低模像素, 高模表面) ≤ MaxRayDistance
```

当两模之间的最大偏移量为 Δ_max 时，理论最小安全值为 `MaxRayDistance ≥ Δ_max × 1.05`（留5%余量以应对浮点误差）。

### 数值过小与过大的不同后果

**数值过小**：射线过短，未能触及高模表面，法线贴图出现大面积中性灰色区域（RGB值127,127,255），模型细节完全丢失。在曲率较大的内凹区域（如角色腋窝、铠甲接缝）这种问题尤为突出。

**数值过大**：射线过长，穿透目标高模，命中背面或相邻高模网格的错误面，产生法线方向倒转的黑色条纹（俗称"接缝渗透"）。在Substance Painter 2.6及以后版本中，启用"Average Normals"选项可缓解此问题，但根本解决方式仍是收紧Max Ray Distance。

典型参考值：对于一个高模与低模间距约为0.02米的角色模型，Max Ray Distance设置在0.03至0.05米之间通常是安全区间。

### 与Cage的协同关系

当Cage已配置时，Max Ray Distance的作用被Cage本身限定的包围体积所覆盖，此时修改Max Ray Distance对Cage区域内的烘焙结果几乎没有影响。Max Ray Distance主要作用于**未使用Cage的烘焙工作流**，或Cage与低模重合导致包围体积失效的局部区域。因此，两者不是替代关系，而是互补关系：Cage处理整体形变偏移，Max Ray Distance处理Cage未覆盖的边界溢出问题。

---

## 实际应用

### 场景一：硬表面道具快速烘焙

烘焙一把枪械道具，高模与低模整体偏移约0.5cm，局部螺丝凸起偏移达1.2cm。若不使用Cage，将Max Ray Distance设置为1.5cm（1.2 × 1.25的安全系数），可以确保所有凸起细节被正确采样，同时避免射线穿透枪托另一侧的多边形。

### 场景二：有机角色身体烘焙

角色肌肉高模与低模间距最大约0.8cm（腹肌区域），但手指指缝间距仅0.3cm。此时不能对全身使用统一的Max Ray Distance=0.8cm，否则指缝处射线会命中相邻手指的高模，造成法线贴图花斑。正确做法是将手部拆分为独立烘焙组，手部单独设置Max Ray Distance=0.4cm，躯干设置为1.0cm。

### 场景三：Blender中的AO烘焙

在Blender 3.x的Cycles烘焙面板中，"Max Distance"参数为0时代表无限距离，场景内所有几何体都参与AO遮蔽计算，易在模型背面产生错误暗化。将其设置为模型尺寸的10%（例如角色高1.8m，设置为0.18m）可将AO影响限制在合理的局部遮蔽范围内。

---

## 常见误区

### 误区一：数值越大越安全

许多初学者认为Max Ray Distance设置得越大，就越不会漏掉高模细节。实际上，数值过大会导致射线穿过目标高模，命中场景中其他对象或高模的背面三角形。这种"过采样"会在贴图上产生比"未命中"更难修复的法线反转错误，在薄壁结构（如刀刃、布料边缘）上尤为明显。

### 误区二：Max Ray Distance可以完全替代Cage

Max Ray Distance仅控制射线长度，无法解决低模与高模存在大角度偏转（超过45°法线夹角）时的采样偏移问题。对于高模与低模在法线方向上差异超过模型尺寸15%的情况，必须使用Cage网格进行精确包围，单纯依赖Max Ray Distance会导致烘焙接缝处出现永久性锯齿错误。

### 误区三：该参数在所有软件中含义相同

Substance Painter中的Max Ray Distance是**单向**最大距离（仅向外），而xNormal的"Max frontal ray distance"与"Max rear ray distance"分别控制前向和后向，两者需要同时配置。混淆这一区别会导致使用xNormal时内凹区域始终出现黑斑。

---

## 知识关联

**前置概念——Cage设置**：理解Cage如何通过膨胀低模生成包围网格，是理解Max Ray Distance作用范围的基础。Cage设定的包围体积与Max Ray Distance的探测距离在逻辑上相互补充：Cage控制射线的起始偏移位置，Max Ray Distance控制射线的终止检测距离。熟悉Cage的推拉（Push/Pull）数值后，可以直接将该数值的1.1倍作为Max Ray Distance的初始参考值。

**延伸方向——烘焙组拆分策略**：在掌握Max Ray Distance的数值效果后，自然引出"何时将模型拆分为多个烘焙组并分别配置参数"的工作流问题，这是进阶烘焙流程中处理复杂角色和场景资产的核心操作思路。Max Ray Distance的逐区域精细化配置，正是该工作流的具体执行手段。