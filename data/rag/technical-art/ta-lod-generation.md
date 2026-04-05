---
id: "ta-lod-generation"
concept: "LOD生成方法"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# LOD生成方法

## 概述

LOD（Level of Detail，细节层级）生成方法是指将原始高精度三维网格转换为一系列不同多边形数量版本的具体技术手段。常见的LOD生成方法分为三大类：手动建模减面、第三方自动化工具（以Simplygon为代表）以及引擎内置的自动LOD生成系统。不同方法在质量、效率、控制精度三个维度上各有侧重，技术美术需要根据资产类型和项目预算选择合适方案。

LOD生成作为一种系统性工作流出现在1976年James Clark发表的论文《Hierarchical Geometric Models for Visible Surface Algorithms》中，该论文首次提出用层级几何模型替代单一精度网格来提升渲染效率。从那时起，LOD生成方法经历了从纯手工到算法驱动的演进。现代大型开放世界游戏（如《荒野大镖客2》）中，一个场景资产往往需要4到6个LOD层级，全部手动生成不具备可行性，因此自动化工具成为生产管线的标配。

掌握不同LOD生成方法的原理与局限，能帮助技术美术在角色面部等需要精确控制的资产上选择手动方案，同时在植被、建筑群等批量资产上正确配置自动化工具，避免因盲目使用自动化导致的视觉穿帮或拓扑错误。

---

## 核心原理

### 手动减面（Manual LOD）

手动LOD由艺术家在DCC软件（如Maya、3ds Max、Blender）中直接对原始网格进行减面操作，是质量最高但成本最高的方法。艺术家会保留轮廓关键边缘循环（Edge Loop），手动删除内部细节多边形，并在必要时重新拓扑以保证低面数下的形态正确性。

手动减面遵循的经验规则是每个LOD层级多边形数量缩减约50%~70%。例如一个角色LOD0为8000三角面，LOD1目标为2400~4000三角面，LOD2为700~1200三角面，LOD3为200~350三角面。手动方法的核心优势是艺术家可以主动决定"哪些几何信息可以丢弃"，例如在LOD2层级直接用单块平面替代耳朵的复杂内腔几何体，这是算法难以自动判断的语义层面决策。

### Simplygon自动减面

Simplygon是由瑞典公司Donya Labs开发（后被Microsoft收购）的专业网格简化中间件，广泛集成于Unreal Engine、Unity等主流引擎的编辑器中。其核心算法基于**二次误差度量（Quadric Error Metrics，QEM）**，通过最小化每次边折叠（Edge Collapse）引入的几何误差来决定折叠顺序。

QEM的误差度量公式为：$\Delta(v) = v^T Q v$，其中$v$是顶点位置的齐次坐标，$Q$是该顶点所有关联面的误差矩阵之和。每次折叠选取使$\Delta$最小的边，保证整体形态偏差最小。Simplygon还额外支持**材质边界锁定**（锁定UV接缝处的顶点不参与折叠）和**重要区域加权**（对面部、手部等区域设置更高的保留权重），这两个功能是其区别于基础QEM实现的关键特性。

Simplygon处理一个10万三角面的资产到LOD3通常耗时5~30秒，批量生产效率远高于手动方法，但对于具有细长三角形、重叠UV岛或非流形几何体的"脏网格"，输出质量会明显下降。

### 引擎内置自动LOD

Unreal Engine 5的内置LOD生成（位于Static Mesh Editor → LOD Settings）使用与Simplygon相似的QEM算法，但参数体系更简化，主要暴露**Screen Size（屏幕覆盖率阈值）**和**Reduction Percentage（减面百分比）**两个控制项。Unity的LOD Group组件不直接生成LOD网格，而是让艺术家手动为每个层级指定预先制作好的网格对象，再通过LOD Group统一管理切换逻辑。

Unreal Engine 5还引入了**Nanite**虚拟几何体系统，对于Nanite启用的资产，引擎会自动构建内部微多边形簇（Cluster）层级，在运行时动态流送，从根本上取代传统静态LOD生成流程。但Nanite对蒙皮网格和透明材质的支持截至UE5.3仍不完整，因此角色和植被LOD仍依赖传统方法。

---

## 实际应用

**角色面部资产**：面部表情骨骼绑定区域（眼周、嘴角）的网格拓扑直接影响蒙皮变形质量，此类资产通常选择手动减面生成LOD1，在LOD1中减去约60%面数的同时保留完整的眼眶Edge Loop，避免自动算法破坏蒙皮权重绑定点。

**批量植被资产**：一个场景可能有数千棵同类树木，每棵树的LOD需要在Simplygon中配置树冠的**聚合（Aggregation）**操作——将大量树叶面片在LOD2层级合并为少量Billboard卡片，这是Simplygon的代理LOD（Proxy LOD）功能的典型用法，通过`ProxySettings.ScreenSize=0.05`参数控制代理生成触发的屏幕覆盖率。

**建筑立面资产**：对于砖墙、门窗框架等建筑构件，引擎内置自动LOD在Reduction Percentage设置为50%时往往会在窗洞边缘产生明显的锯齿塌陷，此时需在Simplygon中启用**硬边角度保护**（Shading Importance设为High），专门保护90度硬边不被折叠。

---

## 常见误区

**误区一：自动LOD生成后无需人工检查**。Simplygon和引擎自动LOD均无法识别"语义错误"，例如角色头盔顶部的徽章在LOD2被算法折叠为零面，从远处看徽章消失但头盔整体误差评分仍低。正确做法是对LOD2及以上层级在200~400像素窗口大小下进行目视验收，并为徽章等独立装饰件设置局部权重保护。

**误区二：LOD多边形数量越低越好**。过度减面会导致法线贴图（Normal Map）烘焙的高频细节在低面数载体上产生明显的法线扭曲，因为法线贴图的烘焙误差与基础网格曲率变化量直接相关。通常LOD1的多边形数量不应低于能够支撑法线贴图正确显示的最小曲面分辨率，对于圆柱形资产（如枪管）该下限约为8~12段圆形截面。

**误区三：手动LOD和Simplygon互斥**。实际生产管线中两者常混合使用：LOD0到LOD1使用手动控制，LOD2及以后层级由Simplygon批量生成。Unreal Engine支持在Static Mesh Editor中对单个LOD层级指定"自定义网格"来实现这种混合工作流。

---

## 知识关联

学习本节前需要了解LOD概述中的基本概念：LOD层级命名规则（LOD0为最高精度）、LOD的性能意义以及多边形预算的基本计算方式，这些构成理解减面比例设定的基础。

掌握LOD生成方法后，下一步需要学习**LOD切换策略**，即如何根据摄像机距离或屏幕覆盖率在各LOD层级间触发切换，切换阈值的设定与各层级网格质量直接耦合——质量差的LOD需要设置更远的切换距离以隐藏穿帮。此外，**植被LOD**涉及Billboard技术与Impostor技术，是代理LOD生成方法的进阶应用；**LOD质量测试**则需要在真实目标硬件上对各层级的视觉偏差进行量化评估，形成完整的LOD生产闭环。