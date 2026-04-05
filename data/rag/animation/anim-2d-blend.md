---
id: "anim-2d-blend"
concept: "2D BlendSpace"
domain: "animation"
subdomain: "blend-space"
subdomain_name: "BlendSpace"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 2D BlendSpace

## 概述

2D BlendSpace 是 Unreal Engine 动画系统中的一种资产类型，允许动画师在二维参数空间内混合多个动画片段。与 1D BlendSpace 只能沿单一轴插值不同，2D BlendSpace 使用两个独立的浮点参数同时驱动混合结果，最典型的应用是用"速度"（Speed）和"方向"（Direction）这两个轴来驱动角色的八方向移动动画集合。

该功能随 Unreal Engine 4 的早期版本一同发布，并在 UE5 中得到保留和优化。其核心价值在于：单纯的 1D BlendSpace 无法同时表达"角色跑多快"与"角色朝哪走"这两个维度的信息，而 2D BlendSpace 通过在平面网格上布置动画样本点，使引擎能够在任意二维坐标处进行双线性插值，从而产生连续平滑的过渡效果。在第三人称动作游戏中，玩家操控角色进行全向移动时，2D BlendSpace 几乎是不可替代的标准方案。

## 核心原理

### 双轴参数空间与样本点布局

2D BlendSpace 在编辑器中以一个矩形网格呈现。横轴（X 轴）通常映射"方向"，范围设置为 -180° 到 180°；纵轴（Y 轴）通常映射"速度"，范围例如 0 到 600（单位：cm/s）。动画师在这个平面上手动放置动画样本点，例如：

- 坐标 (0, 0)：Idle（站立静止）
- 坐标 (0, 300)：Jog Forward（慢跑向前）
- 坐标 (0, 600)：Run Forward（全速向前）
- 坐标 (90, 300)：Jog Right（慢跑向右）
- 坐标 (-90, 300)：Jog Left（慢跑向左）
- 坐标 (180, 300) / (-180, 300)：Jog Backward（慢跑向后）

以此类推，在方向轴上以 45° 为间隔，可布置前、前右、右、后右、后、后左、左、前左共八个方向，配合速度轴上的层级，构成"八方向移动"的完整动画集。

### 三角剖分插值算法（Delaunay Triangulation）

2D BlendSpace 的混合计算基于 Delaunay 三角剖分。引擎将所有样本点视为平面上的顶点，自动生成一组不重叠的三角形覆盖整个参数空间。当运行时传入参数坐标 (x, y) 时，引擎首先判断该点落在哪个三角形内，然后计算该点相对于三角形三个顶点的重心坐标（Barycentric Coordinates）：

设三角形顶点为 P₁、P₂、P₃，目标点为 P，则：
**P = λ₁·P₁ + λ₂·P₂ + λ₃·P₃**，其中 λ₁ + λ₂ + λ₃ = 1，且每个 λᵢ ≥ 0。

三个 λ 值即为对应三个动画样本的混合权重，引擎据此对骨骼姿势进行加权平均，输出最终的混合姿势。这意味着在任意时刻，最多只有 3 个动画样本参与混合运算，而非全部样本。

### 速度与方向参数的数据来源

在蓝图或 AnimGraph 中，"速度"通常从角色的 `Velocity` 向量的 `VectorLength` 获取；"方向"通常通过计算速度向量与角色朝向之间的有符号偏转角获得，可使用 `CalculateDirection` 节点（输入 Velocity 和角色 Transform）直接输出 -180° 到 180° 范围内的角度值。这两个数值每帧在 AnimInstance 的 `UpdateAnimation` 事件中更新，并传递给 2D BlendSpace 的 X、Y 输入引脚。

### 插值平滑设置

2D BlendSpace 资产内置了独立于动画混合的"参数插值"功能。在资产详情面板中，X 轴和 Y 轴各有独立的 `Interpolation Time`（默认通常为 0）。将速度轴的插值时间设为约 0.1 秒，可防止角色在骤然停步时姿势出现帧间跳变；将方向轴插值时间设为约 0.05 秒，可使转向看起来更自然。这两个参数应分开调整，因为人眼对速度变化和方向变化的敏感程度不同。

## 实际应用

**第三人称射击游戏移动系统**：以《堡垒之夜》类型的全向移动为例，开发者在 2D BlendSpace 中放置 9 个样本点（Idle + 8 方向慢跑），再叠加 9 个样本点（8 方向冲刺 + 中心空位），覆盖速度从 0 到 800 cm/s 的两段区间。运行时通过玩家的摇杆输入实时更新方向和速度参数，引擎自动在前左跑和前跑之间插值，角色移动表现平滑自然。

**NPC 巡逻与追击 AI**：AI 角色由行为树控制速度与方向，2D BlendSpace 同样适用。当 AI 从"慢走巡逻"切换到"快速追击"时，速度参数的连续变化使动画在步行与跑步之间自动过渡，不需要手动编写混合逻辑。

**方向参数归一化问题的解决**：当角色以 (-180°, 300) 慢跑向后时，由于 -180° 和 180° 在现实中表示同一方向，若不特殊处理，插值可能产生"绕远路"的错误结果。解决方法是在 2D BlendSpace 的 X 轴属性中勾选 `Wrap Input`（循环输入），使 -180° 和 180° 被视为连续端点。

## 常见误区

**误区一：样本点越多混合效果越好**

许多初学者在 2D BlendSpace 中放置大量样本点，期望获得更精确的结果。然而，Delaunay 三角剖分的插值原理决定了每帧只使用最近三角形的 3 个顶点，过于密集的样本点会造成三角形面积过小，实际参数在该区域内微小的噪声抖动就会导致权重分配频繁在相邻三角形之间切换，反而引发动画抖动。推荐的做法是以 45° 为方向间隔、以 2~3 档速度为层级，保持样本点数量在 9~18 个之间。

**误区二：2D BlendSpace 可以直接替代 AimOffset**

有开发者认为既然 Aim Offset 也是双轴控制，可以用 2D BlendSpace 代替。实际上两者存在根本区别：2D BlendSpace 输出的是完整骨骼姿势（Full Pose），而 Aim Offset 是专为叠加模式（Additive）设计的特殊资产，它输出的是相对于基础姿势的姿势偏差量。用普通 2D BlendSpace 存放瞄准动画并叠加到移动上，会导致骨骼位置被直接覆盖而非偏移叠加，产生错误的动画表现。

**误区三：方向参数可以直接使用世界空间旋转角**

部分开发者错误地将角色的 `Yaw` 旋转值传入方向轴，而不是使用 `CalculateDirection` 计算出的速度方向与朝向之差。当角色朝东跑步并向北旋转摄像机时，传入世界空间 Yaw 会使方向参数突变，导致动画瞬间跳到错误样本。`CalculateDirection` 的意义正是计算"角色身体朝向与实际移动方向之间的夹角"，这才是 2D BlendSpace 方向轴所需的语义。

## 知识关联

学习 2D BlendSpace 需要先掌握 **1D BlendSpace** 的单轴插值逻辑，因为 2D BlendSpace 在概念上是将 1D 的线性插值扩展到平面上的三角插值，若不理解权重的归一化计算过程，将难以排查混合异常问题。

在 2D BlendSpace 之后，可以进一步学习**混合树（Blend Tree）**，它允许将多个 BlendSpace 与状态机节点组合，实现更复杂的分层动画逻辑，例如在移动 BlendSpace 之上叠加受击反应层。**Aim Offset** 紧接其后，专门解决枪械瞄准、头部追踪等需要叠加式双轴控制的场景。**混合遮罩（Blend Mask）** 则解决上下半身独立驱动不同动画的需求，常与 2D BlendSpace 驱动的下肢移动动画配合使用。**Motion Matching** 作为更高阶的替代技术，其参数数据库在概念上可视为高维度的 BlendSpace 扩展，理解 2D BlendSpace 的样本布局与插值逻辑是学习 Motion Matching 轨迹匹配原理的重要前提。