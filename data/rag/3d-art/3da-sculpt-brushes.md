---
id: "3da-sculpt-brushes"
concept: "雕刻笔刷"
domain: "3d-art"
subdomain: "sculpting"
subdomain_name: "数字雕刻"
difficulty: 1
is_milestone: true
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 92.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "book"
    citation: "Flipped Normals (Henning Sanden & Morten Jaeger, 2019). *Sculpting in ZBrush: The Official Guide*. Pixologic Press."
  - type: "paper"
    citation: "Botsch, M., & Kobbelt, L. (2004). An intuitive framework for real-time freeform modeling. *ACM Transactions on Graphics (SIGGRAPH 2004)*, 23(3), 630–634."
  - type: "book"
    citation: "Kavan, L., & Sorkine, O. (2012). Elasticity-inspired deformations for character articulation. *Proceedings of the ACM SIGGRAPH/Eurographics Symposium on Computer Animation*, 311–320."
  - type: "book"
    citation: "Pixologic Inc. (2021). *ZBrush 2021 Official Reference Manual*. Pixologic Documentation Library. https://docs.pixologic.com"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 雕刻笔刷

## 概述

雕刻笔刷（Sculpt Brush）是数字雕刻软件中用于直接操作网格顶点的工具单元，每种笔刷内置独立的数学算法，决定其对表面法线方向、顶点位移幅度及影响范围的处理方式。以ZBrush为例，该软件目前内置超过60种原生笔刷，而Blender Sculpt Mode则提供约25种核心笔刷类型，两者均将笔刷作为雕刻操作的最小执行单位。

雕刻笔刷的概念随数字雕刻工具的演进逐渐成型。2000年代初期ZBrush 2.0引入"笔刷强度（Intensity）与半径（Radius）可独立控制"的设计范式，确立了现代数字笔刷的基础交互框架。2007年ZBrush 3.1版本进一步引入`BrushModifier`参数，允许艺术家在不更换笔刷的前提下动态偏移算法权重。此后Clay Buildup笔刷在ZBrush 3.5版本正式加入，成为角色雕刻有机形态的行业标准工具，其设计者Pixologic工程师在2009年的GDC技术分享中明确指出，该笔刷的截断平面算法直接参考了Botsch与Kobbelt（2004）关于实时自由形变的研究框架。

选择正确的笔刷类型直接决定雕刻结果的物理合理性。Standard笔刷产生球形膨胀位移，Clay笔刷模拟黏土堆积产生带平顶的梯形截面，二者在同等设置下作用于相同区域会产生截然不同的表面形态。初学者混用这两类笔刷往往是造成有机体表面"气球感"的主要原因之一。

值得注意的是，"笔刷"在数字雕刻中并非单纯的输入设备映射，而是一套由**算法核心（Brush Kernel）**、**衰减曲线（Falloff Curve）**、**Alpha纹理（Alpha Texture）**和**笔触类型（Stroke Type）**四大模块共同定义的可编程工具体系。同一算法核心配合不同的衰减曲线，可生成截然不同的视觉效果。例如，将Standard笔刷的Falloff从默认高斯形状改为"Sphere"形，其影响区域边界会从软过渡变为硬截止，适用于在有机表面上雕刻边缘锐利的机械结构嵌件。

> **思考问题：** 如果一款笔刷的衰减曲线（Falloff Curve）从默认的高斯形状改为线性（Linear），对雕刻结果的边界过渡和体积感会产生哪些具体影响？在需要同时兼顾有机轮廓与硬表面细节的次世代角色雕刻任务中，什么样的衰减曲线组合策略能最大程度地减少补救性Smooth操作？

---

## 核心原理

### Standard笔刷与Clay笔刷的位移算法差异

Standard笔刷沿顶点法线方向施加均匀的球形衰减位移，其影响区域的截面呈高斯曲线形状，中心位移量最大、边缘平滑衰减至零。位移公式为：

$$\Delta \mathbf{v} = I \cdot e^{-r^2 / 2\sigma^2} \cdot \hat{N}$$

其中 $\Delta \mathbf{v}$ 为顶点位移向量，$I$ 为笔刷强度（Intensity，范围0–1），$r$ 为顶点到笔刷中心的世界空间距离，$\sigma$ 为衰减半径系数（由用户设置的Brush Radius派生），$\hat{N}$ 为该顶点的单位法线向量。当 $r = 0$（即笔刷中心正下方顶点）时，位移量为纯 $I \cdot \hat{N}$；当 $r = 2\sigma$ 时，位移量已衰减至约13.5%，这解释了为何Standard笔刷的影响边缘在视觉上远比Radius圆圈更"软"。

Clay笔刷（及其变体Clay Buildup）在Standard算法基础上增加了一个垂直于绘制平面的截断平面（Clip Plane）计算，使堆积物顶部趋于平坦，从而模拟真实黏土按压后的物理形态。Clay Buildup还默认启用`Accumulate`（积累）模式，同一笔触多次叠加不衰减，这是它比Standard更适合大型体积堆砌的根本原因。在截面形态上，Standard笔刷产生的截面近似圆弧，而Clay Buildup产生的截面近似梯形——顶部约60%宽度的区域高度一致，两侧20%以S形曲线收尾。

两类笔刷的行为差异还体现在**负向雕刻（按住Alt键）**时：Standard笔刷负向使用时产生对称的球形凹陷，Clay Buildup负向使用时则模拟黏土铲除动作，凹陷底部同样趋于平坦，是雕刻眼眶、鼻孔等内凹结构的更优选择。

### Flatten与Polish笔刷的表面投影机制

Flatten笔刷计算笔刷影响范围内所有顶点的平均高度（即沿笔刷法线方向的加权平均坐标），然后将各顶点向该平均平面拉平，强度100%时所有顶点完全投影到该平面上。其核心计算为：

$$h_{target} = \frac{\sum_{i} w_i \cdot (\mathbf{v}_i \cdot \hat{N}_{brush})}{\sum_{i} w_i}$$

其中 $w_i$ 为各顶点的距离权重，$\hat{N}_{brush}$ 为笔刷中心法线方向。这使Flatten适合处理盔甲、机械零件的平整面，但在有机曲面上过度使用会破坏曲率连续性，表现为平坦区域与周围曲面之间出现生硬折角。

Polish（ZBrush中的hPolish/TrimDynamic）笔刷在Flatten基础上增加了曲面切线方向的保留权重，能在压平高频凸起的同时保持低频曲率走向。Blender的`Scrape`笔刷与ZBrush的hPolish功能最为接近，均通过"削峰填谷"原理处理表面——只对高于平均面的顶点施加向下位移，低于平均面的顶点保持不动，这与完全双向拉平的Flatten有本质区别。

需要特别指出的是，ZBrush 2020版本新增的`TrimDynamic`笔刷相比传统hPolish进一步改进了切线方向权重的计算方式，在弧形表面上表现出更好的各向同性（Isotropy），是目前硬表面流程中平整面处理的首选工具（Pixologic Inc., 2021）。

### Smooth笔刷的拉普拉斯平滑计算

Smooth笔刷在几乎所有数字雕刻软件中均通过**拉普拉斯平滑（Laplacian Smoothing）**实现，其迭代公式为：

$$\mathbf{v}'_i = \mathbf{v}_i + \lambda \cdot \frac{\sum_{j \in \mathcal{N}(i)} (\mathbf{v}_j - \mathbf{v}_i)}{|\mathcal{N}(i)|}$$

其中 $\mathbf{v}_i$ 为当前顶点坐标，$\mathbf{v}_j$ 为其网格邻接顶点，$|\mathcal{N}(i)|$ 为相邻顶点数量，$\lambda$ 为平滑系数（通常取0到1之间，ZBrush默认约为0.5）。在ZBrush中，按住`Shift`键可临时切换至Smooth笔刷，这是雕刻流程中频率最高的操作之一。

Smooth笔刷的强度不宜设为100%并反复涂抹，多次完全强度的拉普拉斯计算会导致网格体积收缩，即"体积丢失（Volume Loss）"现象——这是因为每次迭代都将顶点向其邻居的质心靠拢，整体网格体积单调递减，理论上无限次迭代后网格将退化为单点。ZBrush的`Smooth Valleys`与`Smooth Peaks`是Smooth的方向性变体，分别只平滑凹陷区域或凸起区域，通过在执行平滑前先检测顶点相对于邻域平均面的高度符号来实现方向限制。Blender则提供`Enhance Details`笔刷，其本质是负权重的拉普拉斯平滑（即反平滑/锐化），$\lambda$ 取负值时顶点偏离邻域均值，高频细节得到增强。

为对抗体积丢失问题，研究者提出了**双步拉普拉斯平滑（Taubin平滑，1995）**方法：先以正 $\lambda$ 平滑，再以负 $\mu$（$\mu > \lambda$）反平滑，交替迭代以在保留体积的前提下消除高频噪声。ZBrush的`Relax`笔刷在底层正是采用了类似的双步平滑策略，这使其在均匀化网格密度时体积损失远低于标准Smooth笔刷。

### Inflate、Move与Snake Hook笔刷的向量场差异

Inflate笔刷将每个顶点严格沿其**自身法线**方向外扩，而非笔刷中心的法线，位移方向场在影响范围内是发散的（类似球面向外辐射）。这使Inflate适合均匀膨胀薄片结构（如耳廓、眼皮边缘），但在低多边形网格上因相邻顶点法线差异过大容易产生爆炸性锯齿。与Standard笔刷相比，二者在平坦表面上效果接近，但在高曲率区域（如鼻尖、指节）表现截然不同：Standard使平坦区域隆起，Inflate使高曲率区域均匀膨胀。

Move笔刷将影响范围内的顶点作为整体进行刚性平移，其位移向量场是均匀的（所有受影响顶点位移方向一致），适合调整大型体块比例。Snake Hook笔刷在Move基础上增加了拖拽方向上的顶点拉伸和末端收缩，是创建触手、卷发、犄角等拉伸形态的专用工具，其`Elastic`变体通过弹性形变算法（参考Botsch & Kobbelt, 2004中的ARAP变形框架；Kavan & Sorkine, 2012）保持网格三角形的面积和形状相对均匀，避免拉伸末端出现网格撕裂。

---

## 关键公式汇总与参数速查

为便于实际操作时快速参考，以下整理各核心笔刷的算法关键参数及其对视觉结果的映射关系：

| 笔刷类型 | 位移方向 | 衰减截面 | 关键参数 | 体