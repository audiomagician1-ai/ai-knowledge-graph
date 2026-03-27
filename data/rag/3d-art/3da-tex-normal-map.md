---
id: "3da-tex-normal-map"
concept: "法线贴图制作"
domain: "3d-art"
subdomain: "texturing"
subdomain_name: "纹理绘制"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 法线贴图制作

## 概述

法线贴图（Normal Map）是一种将高面数模型的表面细节信息编码为RGB颜色数据的纹理技术。每个像素的R、G、B通道分别对应法线向量的X、Y、Z分量，使低多边形模型在渲染时能模拟出高模的光照细节，而不增加实际几何复杂度。在游戏引擎中，一张2048×2048的法线贴图可以让仅有几千面的角色模型呈现出拥有数百万面高模同等的凹凸光照效果。

法线贴图技术由Krishnamurthy和Levoy于1996年提出，最早称为"Bump Mapping的向量化扩展"。与前一代的高度图（Height Map）相比，法线贴图直接存储三维法线方向，避免了实时渲染中通过高度差计算法线的额外开销，这是其在游戏行业从2000年代中期开始成为行业标准的根本原因。

制作法线贴图的主流方法有三种：从高低模烘焙（Baking）、在Substance Painter中手工绘制或生成、以及在Substance Designer中通过节点流程过程化生成。三种方法适用场景不同，但底层原理相同——都是在切线空间（Tangent Space）中记录法线偏移量。

---

## 核心原理

### 切线空间与物体空间的区别

法线贴图分为两种坐标空间编码方式：切线空间法线贴图和物体空间法线贴图。切线空间法线贴图的"静止色"为RGB(128, 128, 255)，呈现为大面积偏蓝紫色，这是因为Z轴（蓝色通道）代表法线垂直于表面的默认方向，无偏移时Z值最大。物体空间法线贴图则以模型的世界坐标轴为参考，颜色更鲜艳多样，但不支持UV动画或模型变形，因此游戏资产绝大多数使用切线空间格式。

OpenGL与DirectX对法线贴图的Y轴（绿色通道）方向定义相反。OpenGL格式中绿色通道向上为正，DirectX格式中绿色通道向下为正（即Y轴翻转）。在Substance Painter中可以在项目设置里切换"Normal Map Format"，Unreal Engine默认使用DirectX格式，Unity默认使用OpenGL格式。若格式不匹配，模型在侧光下会出现凹凸关系颠倒的典型错误。

### 从高低模烘焙法线贴图

高低模烘焙是游戏美术中最精确的法线贴图制作方式。核心步骤是：准备同拓扑对应的高模（High Poly，通常数百万面）和低模（Low Poly，通常数千至数万面），使用烘焙软件将高模的表面法线投射到低模的UV展开上。

烘焙时"笼体（Cage）"的设置直接决定烘焙质量。笼体是低模向外膨胀的一个包裹壳，控制射线投射的起始距离。笼体过紧会导致射线从模型内部发出，产生黑色噪点；笼体过松则会采样到错误的高模面，出现"重影（Skewing）"。在Marmoset Toolbag 4（主流烘焙工具）中，每个独立网格区域可以单独调整笼体偏移量，这对处理内凹结构（如螺丝孔、皮带扣）尤为重要。

Substance Painter的烘焙功能（Bake Mesh Maps）使用"By Mesh Name"匹配策略，要求高模命名为`meshname_high`，低模命名为`meshname_low`，软件自动按后缀配对各网格进行烘焙，避免不同部件之间的法线相互干扰。

### 在Substance Painter中手工制作法线细节

当高模不存在或只需添加局部细节（如织物纹理、划痕）时，Substance Painter提供直接在法线通道上绘制的能力。使用"Normal"通道配合高度笔刷（Height Brush），软件实时将笔刷的高度信息转换为切线空间法线偏移并叠加到现有法线贴图上。此外，Substance Painter内置了大量法线/高度的Alpha遮罩（如砖缝、金属压印），配合"Stencil"贴图模式可快速在曲面上贴合复杂图案。

### 在Substance Designer中过程化生成

Substance Designer通过"Normal"节点家族实现过程化法线贴图生成。最常用的流程是：灰度图形 → `Normal`节点（将灰度高度图转为切线空间法线，可调节Intensity参数控制凹凸强度）→ `Normal Blend`节点（叠加多层法线细节）→ 输出。`Normal Combine`节点使用"Whiteout混合算法"而非简单的颜色叠加，该算法公式为：`n = normalize(float3(n1.xy + n2.xy, n1.z * n2.z))`，保证两层法线叠加后结果物理正确，不出现过度压平的问题。

---

## 实际应用

**角色装备烘焙流程**：制作金属护甲时，雕刻师在ZBrush中完成包含铆钉、刻纹的高模（约500万面），拓扑师制作对应低模（约8000面）并展UV。在Marmoset Toolbag中以"Per-Object Cage"模式烘焙，将铆钉部分的笼体偏移单独调高至0.05，避免铆钉内凹阴影区域采样出错。最终导入Substance Painter进行材质绘制。

**场景地面砖块**：在Substance Designer中用`Tile Sampler`节点生成砖块图案，输出灰度高度图后连接`Normal`节点，将Intensity设为0.3（较低值模拟真实砖缝深度），再叠加一层`Grunge Map`噪波的法线层模拟表面磨损，最终输出2048×2048法线贴图，在Unreal Engine 5中赋予Nanite虚拟几何体以外的静态网格。

---

## 常见误区

**误区一：法线贴图可以替代正确的高低模拓扑**。法线贴图只影响像素级光照计算，无法改变模型的轮廓（Silhouette）。从侧面观察时，低模的锯齿状轮廓依然可见，高质量资产仍需要根据轮廓重要性合理分配多边形，法线贴图补充的是光照细节而非几何形状。

**误区二：法线贴图颜色越鲜艳、对比度越高表示细节越多**。过高的法线强度会导致光照下"过锐"（Over-Sharpened），在掠射角（Grazing Angle）处出现不自然的高光噪点。标准做法是在Substance Painter的视口中以多角度、多光源测试法线表现，确保高光平滑过渡，而非追求贴图本身视觉冲击力。

**误区三：OpenGL与DirectX法线贴图可以直接通用**。因绿色通道方向相反，将OpenGL格式的法线贴图直接用于DirectX环境（如直接替换Unreal引擎中的贴图）会导致垂直方向的光照凹凸全部反转，表现为光源在上方时模型表面显示出"向内凹陷"的错误效果。转换时只需在Photoshop或Substance中将绿色通道进行"反相（Invert）"操作即可修正。

---

## 知识关联

学习法线贴图制作需要具备Substance Painter基础操作能力，包括理解纹理通道系统和烘焙工作流中的网格导入规范——这些是正确执行"Bake Mesh Maps"功能的前提，否则无法理解为何需要区分高低模命名规则以及笼体参数的意义。

掌握法线贴图制作后，下一个自然衔接的概念是**曲率贴图（Curvature Map）**。曲率贴图同样来自高低模烘焙流程，记录的是模型表面边缘的凸起与凹陷程度（而非法线方向），在Substance Painter中主要用作遮罩驱动材质磨损效果的分布——例如让金属盔甲的棱角处自动显示出磨损高光。曲率贴图的烘焙设置（如Cage和UV对应关系）与法线贴图共用同一套流程，因此法线贴图烘焙中积累的调试经验可以直接迁移。