---
id: "anim-blocking"
concept: "Blocking阶段"
domain: "animation"
subdomain: "animation-principles"
subdomain_name: "动画原理"
difficulty: 2
is_milestone: false
tags: ["流程"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Blocking阶段

## 概述

Blocking阶段是3D动画制作流程中专门用于建立动画"骨架"的工作阶段——动画师仅使用稀疏的关键帧来锁定角色的核心姿势、主要动作节奏和整体计时，而不填充中间帧。这个阶段的英文名称"Blocking"字面意思是"搭积木"，准确描述了其本质：像搭建舞台布景一样，先把最重要的位置和形状确定下来。

Blocking阶段的工作方式直接源于传统手绘动画中的"原画（Key Animation）"概念，但在进入3D软件流程之后，它被系统化为独立的生产阶段。皮克斯、梦工厂等工作室在2000年代初期将Blocking→Spline（曲线）→Polish（精修）的三段式流程标准化，成为业内通用规范。在Blocking阶段，动画曲线通常被设置为**Stepped（阶梯）插值**而非自动平滑曲线，这样每一帧都呈现为静止定格，动画师可以逐帧检查每一个姿势的质量。

Blocking阶段之所以不可跳过，是因为在这个阶段修改姿势或计时的成本极低。一旦进入Spline阶段，大量自动生成的中间帧会让每一次姿势修改都牵一发而动全身，返工代价极高。导演审批、角色姿势调整、节拍重新分配等重大变更，必须在Blocking阶段完成。

---

## 核心原理

### 关键帧的稀疏性与Stepped插值

在Blocking阶段，一段2秒（按24fps计算即48帧）的走路动画，动画师可能只放置6至10个关键帧，每个关键帧对应一个明确的"极端姿势（Extreme Pose）"，例如接触地面帧（Contact）、最低点（Down）、过渡（Pass）、最高点（Up）。通过将所有控制器的插值模式切换为**Stepped**，软件不会在关键帧之间自动生成任何过渡，画面在相邻两帧之间直接跳切，类似于幻灯片播放。这种看似粗糙的显示方式，反而让动画师能清晰地判断每个姿势是否传达了预期的意图和情绪。

### 节奏（Timing）的确立

Blocking阶段最核心的任务之一是确立动画的**Timing**，即每个姿势在时间轴上占据多少帧。例如，一个角色的头部转向动作，如果安排在4帧内完成，传递的是敏锐警觉的感觉；如果安排在12帧内完成，则更接近慵懒或迟钝的状态。动画师在Blocking阶段通过反复播放Stepped关键帧来调整这些时间间隔，确保动作节奏符合角色性格和故事需求，然后才进入Spline阶段。**调整Timing的代价在Blocking阶段不到Spline阶段的1/5**，因此此时做足节奏实验至关重要。

### 姿势的剪影可读性（Silhouette）

Blocking阶段的另一项专项工作是验证每一个极端姿势的**剪影可读性**。动画师会将角色切换为纯黑色实体显示，在全黑剪影状态下检查每个Blocking关键帧——如果观众仅凭剪影无法识别该姿势所代表的动作或情绪，则该姿势需要在进入精修前重新设计。皮克斯内部将这一检查步骤称为"Black Test"，它是Blocking阶段的质量关卡。

### Blocking阶段的常见关键帧类型

- **Extreme Pose（极端姿势）**：动作运动方向改变的端点帧，如跳跃的最高点。
- **Breakdown（分解帧）**：连接两个Extreme之间的关键过渡形态，决定运动弧线的走向。
- **Contact Frame（接触帧）**：四肢或道具与地面/物体发生接触的精确帧，如走路时脚踩地的瞬间。

在Blocking阶段，Extreme通常最先设置，Breakdown在导演确认Extreme之后才加入，这一顺序避免了在未审批的姿势上浪费Breakdown工作量。

---

## 实际应用

在商业3D动画项目中，Blocking阶段的具体产出物是一个**Blocking Pass**文件，由动画师提交给动画监督（Animation Supervisor）审查。以一个10秒的对话镜头为例，动画师通常会为每个主要台词字节（Beat）放置1至3个Blocking关键帧，整段镜头约需要20至40个有效关键帧。审批通过后，文件被锁定不再修改主要姿势，才能进入Spline阶段。

在游戏动画领域，Blocking阶段同样有对应实践。游戏动画师在制作角色攻击动作时，会先用Stepped关键帧确定**预备（Anticipation）帧、出击帧（Strike）和收招帧（Recovery）**三个核心时间点，并由技术设计师检查碰撞帧是否对应到正确的游戏逻辑帧（如Unity中碰撞盒激活的帧）。这种Blocking先行的方式能及早发现游戏逻辑与动画节奏的冲突。

---

## 常见误区

**误区一：Blocking阶段需要做得"好看"**
许多初学者因为Blocking呈现的阶梯式跳切感到不适，急于提前切换到Spline曲线来让动画"流畅"。这实际上跳过了姿势和节奏的独立审查步骤，将Timing问题掩盖在平滑插值之下。专业工作室的规范是：在导演审批通过Blocking之前，**绝对不进入Spline阶段**，否则返工时需要同时处理姿势错误和曲线错误两重问题。

**误区二：Breakdown帧应该放在两个Extreme的时间中点**
初学者常将Breakdown帧机械地放置在两个Extreme的正中间帧。实际上，Breakdown帧的位置决定了运动的**缓入缓出（Ease In/Ease Out）节奏**，偏向前一个Extreme表示动作在前段慢速积蓄、后段快速完成；偏向后一个Extreme则相反。在Blocking阶段有意识地通过Breakdown帧位置来预设运动节奏，能大幅减少后期在曲线编辑器中调整Tangent（切线）的时间。

**误区三：Blocking阶段只处理身体姿势**
部分学习者认为Blocking仅涉及角色肢体，实际上摄像机运动、道具动画和面部主要表情（如眉毛和嘴巴的极端形态）也必须在Blocking阶段同步确立。镜头Blocking与角色Blocking必须协调，若等到Spline阶段才加入摄像机关键帧，摄像机节奏与角色节奏往往无法匹配，需要大幅返工。

---

## 知识关联

**前置概念——逐帧与关键帧法**：Blocking阶段是关键帧工作方式在现代3D流程中的直接延伸。理解关键帧仅记录关键时刻状态、依赖插值填充中间的原理，是理解为何Blocking使用Stepped插值而非Spline的基础。没有关键帧法的概念，无法解释为什么Blocking只需少量关键帧就能定义整个动作的意图。

**后续概念——动画精修（Polish）**：Blocking阶段确立的关键帧是精修阶段所有工作的出发点。精修阶段对次要动作（Secondary Motion）、跟随动画（Follow Through）和曲线形状的调整，都是在不改变Blocking关键帧时间位置的前提下叠加完成的。Blocking质量直接决定精修阶段的工作量：Blocking姿势越清晰，精修时需要校正的姿势偏移越少。

**后续概念——姿势库（Pose Library）**：在Blocking阶段反复使用并得到导演认可的高质量姿势，往往会被提取存入角色的姿势库，供同项目的其他镜头直接调用，减少后续类似镜头的Blocking工作量。