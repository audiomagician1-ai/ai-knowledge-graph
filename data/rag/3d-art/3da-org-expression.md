---
id: "3da-org-expression"
concept: "表情制作"
domain: "3d-art"
subdomain: "organic-modeling"
subdomain_name: "有机建模"
difficulty: 3
is_milestone: true
tags: ["技术"]

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
---
# 表情制作（BlendShape / Morph Target）

## 概述

表情制作是指在3D软件中通过BlendShape（Maya术语）或Morph Target（Unreal Engine / 3ds Max术语）技术，将同一套面部网格变形为不同的表情形态，并在这些形态之间进行权重插值混合的工作流程。其核心机制是：保持顶点数量和顶点索引完全不变，仅移动顶点的空间位置，从而生成目标形态（Target Shape）。这与骨骼蒙皮动画的原理截然不同——骨骼驱动的是顶点权重，而BlendShape驱动的是顶点偏移量（Delta Position）。

该技术的广泛应用可追溯至1990年代的电影级CG制作，皮克斯在《玩具总动员》（1995年）中已大量使用顶点变形技术制作角色面部。现代影视规格的面部绑定系统（如迪士尼的面部动画系统FACS-based rig）通常包含数十乃至数百个BlendShape目标体，覆盖FACS（面部动作编码系统）定义的44个基础动作单元（Action Unit，简称AU）。

理解表情制作的价值在于：它是实时游戏引擎、虚拟直播面捕（如ARKit的52个BlendShape标准）以及影视级表情动画三条技术路线的交汇基础。无论哪条路线，最终都要回归到面部网格上的顶点偏移量管理。

---

## 核心原理

### 顶点偏移量与形态库构建

每一个BlendShape目标体本质上存储的是一张**差值表**：对于网格中的第 $i$ 个顶点，目标体记录的是该顶点相对于基础形态（Base Mesh）的偏移向量 $\Delta P_i = P_i^{target} - P_i^{base}$。最终变形后顶点位置的计算公式为：

$$P_i^{final} = P_i^{base} + \sum_{k=1}^{n} w_k \cdot \Delta P_i^{(k)}$$

其中 $w_k$ 是第 $k$ 个目标体的混合权重（取值范围通常为 $[0, 1]$，部分软件支持负值以实现反向变形），$n$ 为目标体总数。正因为这是线性叠加，多个表情同时激活时，交叉区域可能出现体积塌陷或穿插问题，需要额外的**修正形态（Corrective Shape）**来补偿。

### 表情目标体的雕刻与分层策略

业界标准做法是将表情目标体按照FACS动作单元分层制作。例如：
- **AU1**：内眉上提（Inner Brow Raise）
- **AU6**：颧肌收缩（Cheek Raiser）
- **AU12**：颧大肌收缩，即嘴角上提（Lip Corner Puller）

制作时，每个AU对应一个独立的目标体，艺术家在基础网格的复制体上使用软件的雕刻工具（如ZBrush的Move笔刷或Maya的雕刻工具集）进行精细调整。典型的游戏角色表情库包含20至60个目标体；影视级角色（如《阿凡达》技术路线）可达150个以上。

对称表情（如左右嘴角分别上提）应分为左右两个独立目标体，而不是一个合并目标体，这样绑定师才能分别控制左右面部，实现不对称表情。

### 修正形态（Corrective Blendshape）

当两个目标体权重同时为1时，线性叠加结果往往不满足肌肉体积守恒原则。例如眉头内聚（AU4）与眼皮压低（AU46）同时激活时，眉间区域常出现不自然的塌陷。修正形态的触发权重通常由表达式驱动：

$$w_{corrective} = w_{AU4} \times w_{AU46}$$

这种乘积驱动确保只有两个原始目标体同时激活时，修正形态才以相应比例介入。一套完善的面部绑定的修正形态数量有时超过主表情目标体本身。

---

## 实际应用

**游戏引擎ARKit面捕对接**：苹果ARKit定义了52个标准BlendShape通道（如`jawOpen`、`eyeBlinkLeft`、`mouthSmileLeft`等），Unreal Engine的LiveLink Face插件直接将iPhone面捕数据映射到模型上对应命名的Morph Target。因此，为移动端面捕设计的角色必须按照ARKit的52个命名规范建立目标体，命名一旦偏差就无法自动对应。

**影视面部绑定流程**：制作完成的BlendShape目标体导入Maya后，绑定师使用`blendShape`节点将所有目标体连接到角色的最终形态，再通过驱动关键帧（Driven Key）或表达式将骨骼控制器的旋转/位移值映射为各AU通道的权重，最终交付给动画师。

**写实风格与卡通风格的数量差异**：卡通渲染（Toon Shading）角色因夸张变形较大、可接受的形态跳跃明显，目标体可以较少（20个左右即可覆盖主要情绪）；而写实人脸需要大量细分的目标体来捕捉皮肤微皱纹和肌肉微动态，通常不低于60个。

---

## 常见误区

**误区一：制作表情时直接在Base Mesh上修改**

部分初学者在制作目标体时，直接对场景中的基础网格进行雕刻，导致基础形态被破坏。正确做法是始终对Base Mesh的**复制体**进行雕刻，保持原始基础网格处于中性表情（Neutral Pose）状态不变，否则BlendShape节点的基准偏移量计算将全部出错。

**误区二：认为BlendShape可以改变拓扑**

BlendShape/Morph Target严格要求源网格与目标网格顶点数量一致且顺序相同。若在制作目标体过程中意外执行了合并顶点（Merge Vertex）、删除面（Delete Face）或插入循环边（Insert Edge Loop）等操作，该目标体将无法被软件识别或导入。这也是为何面部拓扑必须在表情制作开始前完全锁定。

**误区三：忽视眼睑与嘴唇的体积守恒**

眼睑闭合和嘴唇开合都涉及皮肤接触面，若仅靠单一目标体线性移动顶点，闭眼时眼睑往往出现穿模或体积压扁。正确做法是在闭眼目标体中同时向内压缩眼球区域周围的顶点，或制作专用的眼睑接触修正形态，确保上下眼睑在权重为1时精确贴合而非相互穿插。

---

## 知识关联

**前置依赖——面部拓扑**：表情制作对面部拓扑有极强的依赖性。眼轮匝肌区域的环形循环边、嘴轮匝肌的放射状布线、额头横向平行线，都是雕刻表情变形时获得干净褶皱走向的前提。若面部拓扑不符合肌肉走向，雕刻表情时顶点会被迫沿着错误的边界移动，产生撕裂感或锯齿状褶皱，无法通过后期修正弥补。因此，面部拓扑的质量直接决定了每一个BlendShape目标体雕刻的可行上限。

**横向关联——面部骨骼绑定**：在生产管线中，BlendShape与骨骼绑定并非互斥关系，而是分工协作：骨骼负责大范围的下颌开合、眼球转动等刚性运动，BlendShape负责皮肤软组织的微变形和褶皱细节。两者叠加驱动同一套面部网格，是当前影视和高品质游戏角色的标准做法。
