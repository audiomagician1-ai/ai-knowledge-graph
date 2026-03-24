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
---
# 雕刻笔刷

## 概述

雕刻笔刷是数字雕刻软件中模拟现实雕塑工具的功能模块，每种笔刷对网格顶点施加不同类型的数学变换，从而实现堆泥、切割、压平、光滑等效果。以ZBrush为代表的雕刻软件内置超过30种笔刷，Blender的Sculpt Mode同样提供了20余种核心笔刷，初学者最需要掌握的是Clay、Standard、Flatten、Smooth这四种基础笔刷。

数字雕刻笔刷的概念随1999年ZBrush 1.0发布而系统化确立，Pixologic将传统雕塑的"加法"与"减法"概念转化为笔刷的正向（Additive）与反向（Subtractive）模式，通过按住Alt键即可在两种模式间切换。这一设计哲学延续至今，几乎所有主流雕刻软件都沿用了该交互逻辑。

掌握这四种核心笔刷的区别，意味着能够完成角色头部塑造中约80%的工作量。每种笔刷作用于网格的方式根本不同：Standard移动顶点沿法线方向位移，而Clay在此基础上增加了堆积感，Flatten将顶点拉向平均平面，Smooth则对顶点坐标取局部加权平均值。混淆这些原理会导致雕刻表面产生不可控的凹凸噪点。

---

## 核心原理

### Clay 笔刷

Clay笔刷模拟用手指将黏土堆积到模型表面的效果，其核心机制是在法线位移的基础上叠加一个"压平倾向"——笔刷边缘的顶点会被轻微推向笔触中心平面，产生类似泥土层层叠加的台阶感。在ZBrush中，ClayBuildup是Clay的增强版本，每次笔触可叠加更厚的体积，适合快速堆出眉弓、颧骨等大型面部结构。Clay笔刷的Intensity（强度）建议设置在15%–25%之间进行多次叠加，而非一次使用高强度，这样能更好控制形体走向。

### Standard 笔刷

Standard笔刷是最直接的顶点位移工具，顶点严格沿网格法线方向移动，位移量由笔刷Intensity和到笔刷中心的距离共同决定，衰减曲线（Falloff Curve）呈钟形分布。Standard笔刷不修改笔触以外顶点的相对关系，因此适合雕刻毛孔、皱纹等需要精确边界的细节，但在低多边形阶段使用容易产生"气泡"状突起，需配合足够的细分级别（Subdivision Level 4以上）使用。

### Flatten 笔刷

Flatten笔刷将笔触范围内的所有顶点投影到一个由该区域顶点平均位置计算出的平面上，数学表达为：每个顶点新位置 = 顶点原位置 + t × (平面投影点 - 顶点原位置)，其中t由笔刷强度决定（t=1时完全压平）。这一特性使Flatten成为雕刻盔甲护板、机械面板等硬质平面时的首选工具。在Blender中，Flatten笔刷同样拥有对应功能，快捷键为Shift+F调出尺寸控制。使用Flatten时，笔刷尺寸应大于目标压平区域，否则会产生分段的阶梯痕迹。

### Smooth 笔刷

Smooth笔刷对每个顶点取其一环邻居（1-ring neighbors）的坐标加权平均值，本质是对网格做局部拉普拉斯平滑（Laplacian Smoothing）。在ZBrush和Blender中，按住Shift键临时切换为Smooth是最高频的操作之一，每位雕刻师每分钟使用Smooth的次数往往超过10次。Smooth笔刷过度使用会削减已雕刻的细节体积，因此雕刻肌肉过渡时应使用低强度（约10%）的Smooth，而非全力平滑。

---

## 实际应用

**角色头部雕刻流程示例**：在雕刻人脸时，标准工作流是先用ClayBuildup笔刷以强度20%堆出额头、颧骨和下颌的三处主要体积，再用Standard笔刷勾勒眼窝凹陷和鼻梁隆起，Flatten笔刷用于压平鼻尖底部和颧骨外侧平面，最后用Smooth柔化所有过渡区域。整个流程循环往复，Smooth始终作为"橡皮擦"角色穿插其中。

**硬表面与有机体的笔刷选择**：雕刻怪兽皮肤等有机物时，Clay系笔刷使用频率超过60%；雕刻科幻盔甲上的平面分割时，Flatten笔刷应作为主力工具，配合遮罩（Masking）限定作用范围，可精确制造边缘锐利的面板凹槽。

**Blender中的笔刷快捷键**：Blender Sculpt Mode下，按X调出笔刷搜索菜单，Shift+鼠标左键随时激活Smooth，这与ZBrush的操作逻辑一致，方便跨软件工作者快速上手。

---

## 常见误区

**误区一：用Standard笔刷代替Clay做大型塑形**
Standard笔刷缺乏Clay的堆积平面约束，在低细分层级直接使用Standard堆出颧骨体积时，往往产生圆滑气泡而非自然的骨骼突起。正确做法是在前三个细分级别优先使用ClayBuildup或Clay Strips笔刷建立形体，Standard笔刷留到细分级别4–5时处理具体细节。

**误区二：Smooth强度越高越好**
许多初学者习惯用100%强度的Smooth消除所有凹凸，结果将辛苦雕刻的肌肉轮廓一并抹平。Smooth的正确用法是控制在10%–30%强度，在笔触边缘做过渡处理，保留形体中心的体积信息。ZBrush的Smooth笔刷还有Smooth Valleys和Smooth Peaks的细分变体，可选择性只平滑凹谷或凸峰。

**误区三：Flatten等同于平面切割**
Flatten是将顶点投影到动态计算的局部平均平面，而非固定的世界坐标平面，因此在曲面上使用Flatten结果并非绝对水平面。若需要在特定轴向上强制压平，ZBrush应使用TrimDynamic或ClipCurve笔刷，Blender则应使用Scrape笔刷配合法线锁定功能。

---

## 知识关联

学习雕刻笔刷之前，需要了解数字雕刻概述中的细分级别与动态拓扑（DynaMesh/Dyntopo）概念，因为笔刷的表现效果直接依赖网格顶点密度——在面数不足10,000的网格上使用Standard笔刷只会产生硬边锯齿，而非平滑位移。

掌握这四种基础笔刷后，下一步是学习Alpha与笔触纹理，Alpha贴图可以替换笔刷的默认衰减形状，使Clay笔刷产生鳞片、皮革纹等表面细节，将基础笔刷的应用范围从形体塑造扩展到表面肌理。此后进入雕刻式硬表面方向时，Flatten笔刷的遮罩联动技巧将成为制作机甲分模线的核心手段；学习Insert Mesh笔刷时，会发现它本质上是将Standard笔刷的顶点位移逻辑替换为了预制网格插入操作，理解这一区别有助于快速掌握IM笔刷的使用边界。
