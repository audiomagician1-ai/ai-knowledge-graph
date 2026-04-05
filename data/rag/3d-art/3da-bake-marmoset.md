---
id: "3da-bake-marmoset"
concept: "Marmoset烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# Marmoset烘焙

## 概述

Marmoset Toolbag 是由 Marmoset LLC 开发的实时渲染与烘焙工具，其烘焙模块（Bake Project）自 Toolbag 3 版本起正式引入，在 Toolbag 4 中得到大幅优化。与 xNormal 或 Substance Painter 内置烘焙不同，Marmoset 烘焙最核心的特点是**实时预览**：调整高模、低模的笼体偏移（Cage Offset）或采样设置后，烘焙结果会在视口中即时更新，无需等待完整烘焙流程结束。

Marmoset 烘焙的另一个显著优势是其**射线投射方式**。它支持逐对象（Per-Object）独立分配高低模配对，这与 xNormal 将所有模型堆叠在同一空间的做法不同，能有效避免不同模型部件互相投影造成的"光线污染"。这一工作流非常适合角色装备、武器道具等由多个独立部件组成的复杂资产。

对于 3D 美术从业者而言，Marmoset 烘焙不仅提升了迭代效率，其输出的切线空间法线贴图质量极高，与 Marmoset 自身的着色器切线计算完全匹配，因此成为游戏角色美术、硬表面道具流程中的主流烘焙选择之一。

---

## 核心原理

### Bake Project 结构与高低模配对

在 Marmoset Toolbag 中，烘焙任务通过 **Bake Project** 面板管理。每个 Bake Project 包含若干"烘焙组"（Bake Group），每个烘焙组内可以分别指定高模（High Poly）和低模（Low Poly）网格。软件沿低模表面法线方向向高模发射射线，射线的最大投射距离由 **Max Frontal Distance** 和 **Max Rear Distance** 两个参数控制，单位为场景世界单位。

将多套高低模分为不同 Bake Group 的原因在于：Marmoset 对每个组单独计算笼体，避免一件盔甲的肩甲部分误采样到头部模型的细节。这是 Marmoset 烘焙与传统单一笼体方案最本质的区别。

### 切线空间与采样设置

Marmoset 使用 **MikkTSpace** 切线空间标准计算法线贴图，这与 Blender、Unreal Engine 5 及 Substance 3D Painter 所用标准一致，确保烘焙出的法线贴图在目标引擎中无需额外转换即可使用。

采样质量由 **Samples** 参数控制，可选 1x、4x、16x、64x 等级别。16x 采样能有效抑制锯齿，64x 适合输出最终高质量贴图但耗时较长。此外，**Soften** 参数（0.0 到 1.0）控制烘焙结果的边缘软化程度，过高会使法线细节模糊，通常保持在 0.1 到 0.3 之间。

### 实时预览机制

Marmoset 烘焙的实时预览依赖 GPU 加速射线投射，在修改笼体偏移时，视口内的低模模型会即刻以烘焙结果着色显示。这意味着美术师能在 **1–5 秒内** 看到当前参数下的烘焙效果，而无需像传统流程那样等待 10–30 秒的完整烘焙渲染。预览模式与最终输出模式共享相同的投射算法，预览结果与导出 PNG/EXR 的质量一致，区别仅在于采样数量。

### 贴图输出类型

单次烘焙任务可同时输出多种贴图类型，包括：
- **Normals**（法线）
- **Height**（高度/置换）
- **Curvature**（曲率，常用于 Substance 中制作磨损效果）
- **Ambient Occlusion**（AO，支持忽略背面与忽略组间遮蔽选项）
- **Thickness**（厚度，用于 SSS 材质）
- **Position**（位置信息）

这些贴图可以选择独立分辨率，例如法线使用 4096×4096，而 AO 使用 2048×2048。

---

## 实际应用

**游戏角色武器烘焙**：制作一把机械手枪时，枪管、枪身、握把分属不同 Bake Group。枪管高模的细节只会投射到枪管低模上，不会污染握把的法线贴图。烘焙完成后，曲率贴图直接导入 Substance 3D Painter，配合 Generator 生成金属边缘磨损效果。

**硬表面道具迭代**：当高模雕刻细节需要多次修改时，美术师每次保存高模 FBX 后，Marmoset 可通过 **Reload** 功能重新加载模型并自动重烘焙，结合实时预览在极短时间内确认投影质量，大幅减少与模型师的来回沟通次数。

**输出 EXR 格式用于引擎**：对于需要高精度数据的 Thickness 或 Position 贴图，输出格式选择 **32-bit EXR** 而非 PNG，以保留完整的浮点精度，避免数据被压缩到 0–255 范围内造成精度损失。

---

## 常见误区

**误区一：认为实时预览就是最终质量**。实时预览使用的采样数通常为 1x 或 4x，而最终导出往往需要设置为 16x 或 64x。如果直接以预览状态满意后不调高 Samples 就导出，最终贴图边缘可能出现明显锯齿，尤其在模型 UV 接缝处体现明显。

**误区二：所有高低模放进同一个 Bake Group**。Marmoset 支持多 Bake Group 正是为了解决复杂资产的投影污染问题。将角色全身所有部件堆入同一组，会导致笼体偏移值难以统一，部分区域过度偏移（法线偏移失真），部分区域投影到错误模型（出现黑色投影错误区域）。

**误区三：混淆 Max Frontal Distance 与笼体膨胀**。Max Frontal Distance 控制射线向高模投射的最远距离，而不是让低模网格膨胀。如果高低模之间距离超过该值，射线就无法抵达高模表面，对应 UV 区域会烘焙出平坦的法线（呈蓝紫色）。正确做法是将该值设置为略大于高低模之间最大间距的数值。

---

## 知识关联

Marmoset 烘焙以**法线烘焙**的基础概念为前提，即理解切线空间法线贴图如何通过射线投射将高模表面信息编码到低模 UV 上。掌握 UV 展开规范（UV 岛屿不重叠、合理利用 UV 空间、接缝位置选择）是确保 Marmoset 烘焙结果无瑕疵的必要条件。

Marmoset 烘焙输出的法线、AO、曲率贴图直接进入 **Substance 3D Painter** 的贴图绘制流程，其中曲率贴图驱动磨损 Generator，AO 贴图用于腔体暗化，两者共同构成 PBR 材质制作流程的数据基础。因此，Marmoset 烘焙的输出质量直接影响后续材质制作的上限。