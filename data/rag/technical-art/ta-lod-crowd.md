---
id: "ta-lod-crowd"
concept: "人群LOD"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 人群LOD

## 概述

人群LOD（Crowd Level of Detail）是专门针对游戏或实时渲染场景中大量NPC同时出现时的综合性优化技术。不同于单个角色的LOD策略，人群LOD必须同时管理骨骼绑定复杂度、材质批次合并、动画采样频率三条优化轴线，因为单个NPC节省的开销在数百人规模时才会产生乘法效应。典型案例如《刺客信条：大革命》（2014年）曾在街道场景中渲染超过5000个NPC，正是依赖多层人群LOD系统才使PS4平台维持了可用帧率。

人群LOD的工程概念起源于2000年代中期的体育竞技游戏，当时FIFA、NBA 2K系列需要在球场渲染数万名观众。早期方案仅靠平面广告牌（Billboard）替换远距角色，但随着开放世界游戏兴起，NPC需要在近距离内保持真实移动，促使开发者发展出骨骼简化与动画降频并行的多级混合方案。如今Unreal Engine的Massed Character System和Unity的Crowd Simulation均内置了至少3个人群LOD层级。

人群LOD的重要性在于它直接影响CPU的骨骼变换计算量（Skinning Cost）和Draw Call总数两项最容易成为瓶颈的资源。一个全精度NPC可能拥有65根骨骼和4张256×256贴图，而L3级人群LOD角色可压缩至8根骨骼、1张共享图集，Draw Call通过GPU Instancing合并至个位数，使同屏NPC数量扩展空间达到原来的8到10倍。

## 核心原理

### 骨骼LOD分级

人群LOD的骨骼简化遵循"关节保留优先级"原则：脊柱根骨骼、髋部、双肩、头部为L0必须保留的关键骨骼，手指、面部骨骼在L1即可剔除，膝盖和肘部IK骨骼在L2剔除，L3以上仅保留髋-脊-头的5骨极简链条。骨骼数量与Skinning计算量近似线性相关：从65骨降至8骨，GPU Skinning的VS计算量约减少87%。Unreal Engine通过`LODInfo.BonesToRemove`数组精确控制每个LOD层级移除的骨骼列表，被移除骨骼的蒙皮权重在烘焙阶段自动重映射到最近父骨骼。

### 动画采样频率降级

人群LOD中的动画系统不执行完整AnimGraph求值，而改用预烘焙的顶点动画纹理（Vertex Animation Texture，VAT）或动画姿势快照（Pose Snapshot）。具体策略是：L0层级以30fps完整执行状态机；L1层级降至15fps并跳过IK解算；L2层级改为从预烘焙的姿势缓存中每隔2帧采样；L3层级完全使用存储在512×512 RGBAFloat纹理中的VAT，将骨骼动画转为纯GPU计算，彻底绕过CPU动画更新线程。VAT纹理中每一行像素对应一根骨骼在整个动画循环中的旋转四元数序列，着色器通过`uv.y = boneIndex / boneCount`直接采样，无需任何CPU介入。

### 材质与渲染合批策略

人群LOD的材质系统必须配合GPU Instancing才能有效压缩Draw Call。核心做法是为每个LOD层级建立共享图集（Atlas）：将4至8种NPC服装变体的Albedo、Normal、Roughness贴图合并进同一张2048×2048图集，所有同层级NPC共用一个材质实例，仅通过PerInstance的UV偏移参数区分外观。当NPC数量超过某阈值（通常为200人）时，系统自动切换为Impostor（公告板替代物）渲染：每个远距NPC被替换为一张预渲染的8方向×8姿势共64格的精灵图集，以Shader实时插值选择最近方向帧，单Draw Call即可渲染数千个远景NPC。

### LOD切换距离的人群校正

孤立NPC的LOD切换距离公式为 `D = K × √(ScreenHeight / TargetPixels)`，其中K为场景比例系数。但人群LOD需要在此基础上引入密度惩罚因子：当屏幕内NPC密度超过`N_threshold`（典型值为每平方像素0.01个NPC）时，所有NPC的LOD切换距离整体乘以一个0.6至0.8的压缩系数，强制提前降级，防止人群聚集区域突破渲染预算。

## 实际应用

《荣耀战魂》的战场模式在战场边缘部署了约300个AI观战士兵，采用三级人群LOD：0-15米内使用完整32骨架；15-40米退化为12骨架配合Pose Snapshot；40米外切换为仅有躯干和头部运动的VAT角色，Skinning开销从全精度的每帧11ms压缩至0.8ms。

在UE5的示例项目"City Sample"中，人行道NPC系统使用了MassEntity框架，结合人群LOD将同屏行人上限推至18000个，其中距摄像机50米以外的角色全部使用Instanced Static Mesh（ISM）渲染公告板，每帧Draw Call仅增加约40个。

移动端游戏《原神》的人群聚集场景（如璃月港节日活动）通过将NPC共享4套骨架基础变体并为每套独立维护L0/L1/L2三级，将50个同屏NPC的CPU骨骼更新时间控制在2ms以内，在Snapdragon 865平台维持30fps。

## 常见误区

**误区一：骨骼数量越少，视觉退化越小**
实际上骨骼简化对视觉的影响高度依赖角色类型。移除手指骨骼对远景NPC几乎不可感知，但过早移除膝盖骨骼会导致行走动画出现明显的"直腿滑步"，因为膝盖弯曲需要独立关节支撑。正确做法是在目标LOD距离处进行截图对比，而非仅依靠骨骼数量指标判断。

**误区二：人群LOD只需管理渲染，不必管理物理和导航**
大量NPC同时激活完整的物理碰撞和Navmesh寻路会使CPU负载比渲染更先崩溃。人群LOD必须同步实施"行为LOD"：L2以外的NPC停止执行A*路径重算，改为沿预烘焙路径移动；L3以外仅更新位置，不运行任何行为树节点。UE5的MassEntity专门为此提供了`LODCollector` Processor来统一调度行为频率。

**误区三：VAT（顶点动画纹理）可以完全替代骨骼蒙皮**
VAT在极远距离效果优异，但它烘焙的是静态顶点位移序列，无法响应运行时的布料物理、IK目标变化或程序动画叠加。若NPC需要在中等距离响应玩家互动（如躲避、回头），必须保留至少L1级骨骼层级，不能将VAT阈值设得过近。

## 知识关联

人群LOD直接依赖**LOD动画简化**中介绍的骨骼剔除和姿势缓存技术：单角色的AnimLOD确定了每个层级的动画质量基准，人群LOD在此基础上将这套基准扩展为跨数百个实例的批量管理问题，并增加了实例密度感知的切换逻辑。理解骨骼权重重映射原理（来自LOD动画简化）是正确配置`BonesToRemove`列表的前提，否则移除骨骼后会出现蒙皮撕裂。

人群LOD还与**GPU Instancing**和**Impostor烘焙**技术深度耦合：图集UV偏移依赖Instancing的PerInstance参数传递机制，公告板替代方案的质量上限由Impostor的离线渲染精度决定。在技术美术工作流中，人群LOD系统是连接动画技术美术（负责VAT烘焙和骨骼简化）与渲染技术美术（负责材质图集和批次合并）两个专业方向协作的典型交汇点。
