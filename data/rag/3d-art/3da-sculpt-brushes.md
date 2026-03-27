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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.375
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 雕刻笔刷

## 概述

雕刻笔刷（Sculpt Brush）是数字雕刻软件中用于直接操作网格顶点的工具单元，每种笔刷内置独立的数学算法，决定其对表面法线方向、顶点位移幅度及影响范围的处理方式。以ZBrush为例，该软件目前内置超过60种原生笔刷，而Blender Sculpt Mode则提供约25种核心笔刷类型，两者均将笔刷作为雕刻操作的最小执行单位。

雕刻笔刷的概念随数字雕刻工具的演进逐渐成型。2000年代初期ZBrush 2.0引入"笔刷强度（Intensity）与半径（Radius）可独立控制"的设计范式，确立了现代数字笔刷的基础交互框架。此后Clay Buildup笔刷在ZBrush 3.5版本正式加入，成为角色雕刻有机形态的行业标准工具。

选择正确的笔刷类型直接决定雕刻结果的物理合理性。Standard笔刷产生球形膨胀位移，Clay笔刷模拟黏土堆积产生带平顶的梯形截面，二者在同等设置下作用于相同区域会产生截然不同的表面形态。初学者混用这两类笔刷往往是造成有机体表面"气球感"的主要原因之一。

---

## 核心原理

### Standard笔刷与Clay笔刷的位移算法差异

Standard笔刷沿顶点法线方向施加均匀的球形衰减位移，其影响区域的截面呈高斯曲线形状，中心位移量最大、边缘平滑衰减至零。公式可表示为：**Δv = Intensity × e^(-r²/2σ²) × N**，其中 Δv 为顶点位移向量，r 为顶点到笔刷中心的距离，σ 为衰减系数，N 为顶点法线方向。

Clay笔刷（及其变体Clay Buildup）则在Standard算法基础上增加了一个垂直于绘制平面的截断平面（Clip Plane）计算，使堆积物顶部趋于平坦，从而模拟真实黏土按压后的物理形态。Clay Buildup还默认启用`Accumulate`（积累）模式，同一笔触多次叠加不衰减，这是它比Standard更适合大型体积堆砌的根本原因。

### Flatten与Polish笔刷的表面投影机制

Flatten笔刷计算笔刷影响范围内所有顶点的平均高度，然后将各顶点向该平均平面拉平，强度100%时所有顶点完全投影到该平面上。这使它适合处理盔甲、机械零件的平整面，但在有机曲面上过度使用会破坏曲率连续性。

Polish（ZBrush中的hPolish/TrimDynamic）笔刷在Flatten基础上增加了曲面切线方向的保留权重，能在压平高频凸起的同时保持低频曲率走向。Blender的`Scrape`笔刷与ZBrush的hPolish功能最为接近，均通过"削峰填谷"原理处理表面。

### Smooth笔刷的拉普拉斯平滑计算

Smooth笔刷在几乎所有数字雕刻软件中均通过**拉普拉斯平滑（Laplacian Smoothing）**实现，公式为：**v'ᵢ = vᵢ + λ × Σ(vⱼ - vᵢ)/n**，其中 vᵢ 为当前顶点，vⱼ 为其相邻顶点，n 为相邻顶点数量，λ 为平滑系数（通常取0到1之间）。在ZBrush中，按住`Shift`键可临时切换至Smooth笔刷，这是雕刻流程中频率最高的操作之一。

Smooth笔刷的强度不宜设为100%并反复涂抹，多次完全强度的拉普拉斯计算会导致网格体积收缩，即"体积丢失（Volume Loss）"现象。ZBrush的`Smooth Valleys`与`Smooth Peaks`是Smooth的方向性变体，分别只平滑凹陷区域或凸起区域。

### Inflate、Move与Snake Hook笔刷

Inflate笔刷将每个顶点严格沿其**自身法线**方向外扩，而非笔刷中心的法线，因此适合均匀膨胀薄片结构（如耳廓、眼皮边缘），但在低多边形网格上容易产生爆炸性锯齿。

Move笔刷将影响范围内的顶点作为整体进行刚性平移，不产生相对位移，适合调整大型体块比例。Snake Hook笔刷在Move基础上增加了拖拽方向上的顶点拉伸和末端收缩，是创建触手、卷发、犄角等拉伸形态的专用工具，其`Elastic`变体通过弹性形变算法保持网格均匀分布。

---

## 实际应用

**角色面部雕刻标准流程**中，雕刻师通常遵循以下笔刷顺序：首先使用Move笔刷推动大型体块确定五官位置，接着使用Clay Buildup堆积颧骨、眉弓等骨性结构，再以Standard笔刷在眼眶、鼻翼等区域添加中频细节，最后用Flatten处理眼皮平整部分，并以Smooth笔刷（强度约20-40%）过渡各区域边界。

**硬表面接缝处理**中，Trim Dynamic（ZBrush专有）或Scrape（Blender）笔刷可将两个平面交接处的多余网格直接削平，配合`Mask`遮罩工具保护非工作区域，能高效模拟金属焊缝或机械倒角效果，而这是普通Clay笔刷难以直接实现的几何效果。

**布料褶皱**的快速生成方案依赖Crease（折痕）笔刷与Inflate笔刷的交替使用：Crease笔刷的算法是Inflate的反向，将顶点沿法线向内挤压同时收紧两侧，默认配合`Alpha 22`（线形Alpha）使用，可在2-3次笔触内产生清晰的布料折叠截面。

---

## 常见误区

**误区一：将Clay与Standard混用导致体积混乱。** 许多初学者认为Clay和Standard只是"笔触形状不同"，实际上二者位移截面算法完全不同——Standard堆砌的体积边缘光滑但中心会过度突起形成气球状，而Clay Buildup产生的平顶特性才符合真实体积堆砌的物理逻辑。在有机角色的骨骼或肌肉结构阶段应几乎只使用Clay类笔刷。

**误区二：Smooth笔刷强度越高越好。** Smooth以100%强度反复涂抹同一区域，每次迭代都会触发顶点坐标向周围顶点平均值收缩，累积数十次后网格会出现可见的体积萎缩，即使Undo重做仍会影响感知质量。专业雕刻师通常将Smooth强度控制在15%至35%之间，用多次轻扫代替单次重扫。

**误区三：所有笔刷均可通用于任意细分级别。** Move和Clay笔刷在低细分级别（Subdivision 1-2）操作大型比例最有效，而Crease、Standard等高频细节笔刷需要在较高细分级别（Subdivision 5-7）才能表达足够精度。在低细分级别使用Crease笔刷只会产生扭曲网格，而非清晰的折痕线条。

---

## 知识关联

掌握各类核心笔刷的基础算法差异之后，后续学习**Alpha与笔触纹理**时，理解Alpha图像如何调制笔刷的位移幅度分布（即将灰度图映射到Δv的权重系数上）会更加直观，因为Alpha本质上是对本文所述高斯衰减函数的自定义替换。

进入**雕刻式硬表面**模块后，Trim Dynamic、Flatten和Polish三类笔刷的使用频率将大幅上升，而Clay和Standard笔刷的比重相应降低，掌握Flatten的平面投影计算原理是准确判断何时切换笔刷类型的前提条件。

**Insert Mesh笔刷**建立在Standard笔刷的交互框架之上，但其执行的操作从顶点位移转变为几何体插入与布尔合并，理解普通笔刷的影响半径与笔触方向概念有助于快速适应Insert Mesh的方向控制逻辑。**姿势调整（Pose Brush）**中的骨骼权重区域划分同样继承了笔刷影响范围（Radius/Falloff）的概念体系。