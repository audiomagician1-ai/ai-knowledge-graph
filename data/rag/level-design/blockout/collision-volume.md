---
id: "collision-volume"
concept: "碰撞体积设计"
domain: "level-design"
subdomain: "blockout"
subdomain_name: "Blockout"
difficulty: 2
is_milestone: false
tags: ["物理"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.393
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 碰撞体积设计

## 概述

碰撞体积设计（Collision Volume Design）是关卡Blockout阶段中定义玩家角色、敌人AI与环境几何体之间物理边界的技术环节。不同于最终渲染网格，碰撞体积是一套独立的、简化的凸包（Convex Hull）或基元几何体（Primitive Geometry），用于引擎的物理模拟计算。在Unreal Engine中，碰撞体积分为UCX_前缀的自定义凸包网格、基本碰撞基元（Box、Sphere、Capsule）以及逐面碰撞（Per-Face Collision）三类，各有不同的计算开销。

碰撞体积设计的概念随实时3D引擎的物理系统成熟而独立成科。早期游戏（如1996年前的2.5D作品）直接以可见几何体做碰撞，但当多边形数量随次时代引擎增长至数十万面时，用可见网格做碰撞计算导致帧率崩溃，迫使设计师与技术美术将碰撞几何体从渲染几何体中剥离。这一分离催生了今日标准化的碰撞体积设计流程。

对关卡设计师而言，碰撞体积直接决定三件事：玩家能否站上某个台阶、AI导航网格（NavMesh）能否正确烘焙可行走区域、以及是否存在玩家可以意外卡入的"穿模缝隙"。一个Blockout阶段配置错误的碰撞体积，会在后期导航网格烘焙时产生大量错误的不可达区域，修复成本极高。

## 核心原理

### 碰撞基元类型与选择规则

Unreal Engine的碰撞系统提供三种基本基元：**Box Collision**（盒体碰撞）、**Sphere Collision**（球体碰撞）和**Capsule Collision**（胶囊体碰撞）。胶囊体是人形角色的标准碰撞形态——Unreal默认玩家角色胶囊体半径为34 cm、半高为88 cm，这两个数值直接规定了关卡中所有门洞、走廊和台阶的最小尺寸标准。门洞净宽必须大于68 cm（两倍半径），台阶高度一般不超过45 cm以确保角色自动步进（Auto Step Height）能正常触发。

对于Blockout阶段的BSP或静态网格体，应优先使用**简单碰撞（Simple Collision）**而非复杂碰撞（Complex Collision/Use Complex as Simple），因为后者会对每个三角面做碰撞查询，在Blockout的大型几何体上会造成显著性能损耗。通用规则是：**凸形体用单个凸包，凹形体拆分为多个凸包之和**。一个L形走廊应拆为两个Box碰撞体，而非用一个凹形碰撞网格描述。

### 碰撞通道与响应矩阵

Unreal Engine的碰撞系统通过**碰撞通道（Collision Channel）**和**响应类型（Block / Overlap / Ignore）**构成响应矩阵。在Blockout设计中，至少需要正确配置三个通道：`ECC_WorldStatic`（静态世界几何）、`ECC_Pawn`（玩家与NPC）和`ECC_Visibility`（射线检测可见性）。

一个常见配置错误是将Blockout几何体设为`Overlap`而非`Block`，导致玩家直接穿过地板。另一个陷阱是忘记为装饰性小物件（如石块、箱子）设置`ECC_Pawn`为`Block`，导致玩家能穿越这些物件，而`ECC_Visibility`保持`Block`，使这些物件仍遮挡射线检测，造成"看得见却穿得过"的逻辑矛盾。

### 导航阻挡与NavMesh烘焙关系

碰撞体积与导航网格的关系通过**Nav Modifier Volume**和**NavMesh Agent**参数耦合。NavMesh烘焙时，引擎根据`AgentRadius`（通常设为34 cm，与胶囊体半径匹配）和`AgentHeight`（通常设为144 cm，约为胶囊体半高的1.64倍加头顶余量）向碰撞几何体的表面外扩，从而生成可行走的NavMesh多边形。

如果Blockout阶段的碰撞体积比可见几何体**大出超过5 cm**，NavMesh会在该碰撞体周围产生错误的导航排斥区域，AI看起来会绕远路或无法到达视觉上可达的位置。反之，如果碰撞体积比可见几何体**小于可见轮廓2 cm以上**，AI则可能导航至玩家视觉上认为不可达的悬空位置。这种毫米级别的精度要求，使得Blockout阶段的碰撞体积检查成为必要的QA流程。

## 实际应用

**台阶与斜坡的碰撞设计差异**：在Blockout中，楼梯的每一级台阶若都建立独立Box碰撞，AI的NavMesh会在台阶端点产生大量锯齿状多边形，导致NPC行走时产生抖动。标准做法是在楼梯下方铺设一个**斜面碰撞体（Ramp Collision）**，坡度不超过45°，NavMesh会将其识别为连续斜面，AI可平滑移动；而玩家角色由于胶囊体底部的自动步进机制，同样可以正确爬楼梯。这一"双层碰撞"策略（可见几何用台阶，碰撞几何用斜坡）是关卡Blockout中的经典技术方案。

**竞技地图的碰撞对称性验证**：在PVP竞技关卡（如对称地图）的Blockout阶段，设计师需使用Unreal的**Collision Analyzer**工具或控制台命令`show COLLISION`，逐一比对A侧与B侧的碰撞体积，确保双方的可达空间（如掩体后方的站立点、跳跃可达的平台边缘）在碰撞体积层面完全一致。一个边缘差了8 cm的掩体碰撞体，可能使A侧玩家能卡进该掩体边缘，而B侧玩家无法，直接破坏对称性公平。

**不可达区域的主动封堵**：设计师不希望玩家到达的区域（如关卡边界外的"化外之地"）应使用**Blocking Volume**（Unreal中的专用不可见碰撞体）进行封堵，而非依赖视觉上的悬崖。这些Blocking Volume需设置`ECC_Pawn` = Block，同时`ECC_Visibility` = Ignore，确保镜头射线不被这些隐形墙遮挡，避免出现"镜头被空气挡住"的表现问题。

## 常见误区

**误区一：认为碰撞体积越贴合可见几何体越好。** 许多初学设计师会为复杂的岩石、废墟模型启用"Use Complex as Simple Collision"，使碰撞与每个三角面完全吻合。这在Blockout阶段是严重错误：复杂碰撞使NavMesh烘焙时间成倍增加（一个高精度岩石簇可能将局部烘焙时间从2秒延长到40秒），并且会在岩石表面的细小凹陷处生成玩家可以卡入的碰撞缝隙。正确做法是用3-5个凸包Box近似描述岩石外轮廓。

**误区二：将NavMesh Exclusion Volume当作碰撞体积的替代品。** 部分设计师发现AI在某区域导航出错后，直接放置NavMesh Exclusion Volume来"消除"问题区域的NavMesh，却不去修复根本原因——错误的碰撞体积配置。NavMesh Exclusion Volume会将AI完全排除在该区域之外，这意味着如果玩家进入该区域（因为玩家不依赖NavMesh移动），AI永远无法追入，造成战斗AI的逻辑断裂。碰撞问题必须通过修正碰撞体积解决，而非用导航修改器掩盖。

**误区三：忽视碰撞体积的Y轴高度对头顶空间的影响。** 设计师在Blockout阶段经常只关注XZ平面（地面）的碰撞覆盖，而忽略碰撞体的Y轴（高度）上限。如果一个隧道的顶部碰撞体下缘低于玩家胶囊体顶端（即低于176 cm），玩家进入隧道时会触发卡顶反应，表现为玩家角色突然下蹲或被向下推出，但视觉上隧道明明足够高。检查方法是在Unreal中开启`show COLLISION`后，从侧视角验证所有隧道、门洞的碰撞净高是否始终不低于200 cm（含安全余量24 cm）。

## 知识关联

碰撞体积设计直接承接**BSP阻挡体**的知识基础：Blockout阶段的BSP几何体默认具有基于其多边形轮廓生成的碰撞，设计师需要理解BSP碰撞与独立静态网格碰撞的生成逻辑差异，才能在从BSP过渡到Static Mesh时不丢失碰撞配置。具体而言，BSP转换为Static Mesh时（通过"Convert to Static Mesh"操作），原BSP碰撞会被转
