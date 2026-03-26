---
id: "ta-lod-streaming"
concept: "LOD与流送"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# LOD与流送

## 概述

LOD与流送（LOD with Streaming）是将多细节层次技术与关卡流送机制深度整合的渲染优化策略，专门应对开放世界场景中数以千计的资产在运行时的动态加载与精度管理问题。在Unreal Engine 5的World Partition系统正式引入之前，大型地图依赖手动划分的Level Streaming Cell来控制哪些区域的几何体被加载进内存；World Partition将这一过程自动化，并以64m×64m（可配置）的网格单元为单位进行流送，使得LOD与流送的协同设计从可选优化变为强制性的架构决策。

该技术组合的重要性在于：流送负责控制**资产是否存在于内存**，而LOD负责控制**已存在资产的几何精度**，两者在不同维度上降低GPU和CPU的开销。若仅有流送而无LOD，玩家视野边缘的全精度模型会在单帧内产生巨大渲染负担；若仅有LOD而无流送，即便是LOD3的低精度网格也会在超大地图上累积到数十万个Draw Call。二者缺一不可，且切换时机必须精确配合。

## 核心原理

### World Partition的流送距离与LOD屏幕尺寸的耦合

World Partition通过`Streaming Source`（通常为玩家Pawn）向外扩展加载半径，默认的`Loading Range`约为128m，`Visual Loading Range`可单独设置得更大。关键在于：当一个流送单元进入加载范围时，其中的静态网格Actor会以**LOD0**完整加载进显存；当流送单元处于`Visual`边界（已可见但未完全加载物理）时，同一Actor可配置为仅在内存中保留LOD2或LOD3。这意味着技术美术需要在`StaticMesh`的`LOD Screen Size`阈值与流送单元的半径之间做联合调参——若LOD0切换到LOD1的屏幕尺寸阈值为0.3（约对应100m视距），而流送单元的卸载距离为90m，那么玩家永远不会在LOD0下看到该物体从流送中卸载，从而避免了精度跳变。

### Level Streaming Cell与HLOD的分层替代关系

传统Level Streaming（非World Partition）与LOD配合时，未加载的关卡整体不可见。而World Partition引入了`HLOD Layer`机制，当一个流送单元超出加载范围被卸载后，系统会自动用预烘焙的HLOD代理网格（通常多边形数降至原始LOD0的0.5%~2%）替换该区域。这形成了三层精度架构：**流送单元内LOD0/1/2** → **流送边界处LOD3** → **流送单元外HLOD代理**。技术美术在设置LOD链时，必须保证LOD3的外观与HLOD代理的外观过渡自然，否则在流送边界处会产生视觉跳变（Popping）。HLOD代理的生成参数`Merge Proxy Distance`与LOD3的`Screen Size`之间的差值建议不超过0.05，以控制过渡区间。

### 流送优先级与LOD加载顺序

Unreal Engine的Asset Streaming系统支持`Streaming Priority`，LOD贴图（Mip）和LOD几何体遵循相同的异步加载队列。当玩家快速移动时（如载具速度超过20m/s），新进入流送范围的Actor可能在LOD0几何体完全加载之前就已经出现在屏幕上。引擎通过`r.StaticMesh.LODDistanceScale`全局缩放因子控制LOD切换的保守程度，较大的值（如1.5）会让引擎在更近距离处保持LOD0，但会增加内存压力，需与流送带宽预算（通常设定为200~400MB/s的流送吞吐量）协调取舍。`World Settings`中的`Cell Loading Hysteresis`参数（迟滞范围，默认约32m）可防止在流送边界附近频繁触发加载/卸载，但此迟滞范围与LOD切换距离之间若不协调，会导致短暂的"无HLOD且无流送模型"的穿帮空洞。

## 实际应用

**《黑神话：悟空》大型场景策略**：在山地和寺庙等大型开放区域，制作团队将场景按功能分层配置流送单元，近景建筑使用LOD0（约2万面）至LOD2（约800面）的过渡，而远景山体直接由HLOD代理表示，避免加载整座山的几何数据，整体流送内存预算控制在单帧800MB GPU显存以内。

**赛车游戏的高速流送适配**：在赛道宽度约30m、载具速度达90m/s的场景下，传统128m加载半径不够，需将流送Loading Range扩展至512m以上，同时将LOD0→LOD1的切换屏幕尺寸从0.3下调至0.15，让更远处的物体更早降级，以补偿更大流送范围带来的内存压力。此时技术美术需重新测量每个资产在512m视距处的实际屏幕占比，使用`ProfileGPU`和`Stat Streaming`命令对加载吞吐量实时监测。

**植被系统的LOD与流送整合**：使用`Hierarchical Instanced Static Mesh（HISM）`时，Cull Distance（裁剪距离，通常配置为5000cm）与流送单元半径的关系决定了是否存在"已加载但被Cull的实例"浪费内存的情况。建议Cull Distance不超过流送单元Loading Range的80%，从而确保超出可见范围的实例已被流送系统先行卸载。

## 常见误区

**误区1：LOD切换距离与流送距离可以独立设置**
许多初学者在`StaticMesh Editor`中调整LOD Screen Size时，未考虑该资产所在流送单元的卸载距离。若LOD2的切换距离（如150m）远大于流送单元的卸载距离（如80m），则LOD2从未被玩家看到——引擎在模型降级到LOD2之前就已将整个流送单元卸载，LOD2的制作工时被完全浪费，且HLOD代理接管时因LOD1与HLOD代理面数差距过大而产生明显跳变。

**误区2：启用World Partition后不再需要手动优化LOD**
World Partition的自动流送只解决了"哪些资产需要加载"的问题，并不会自动生成或优化LOD链。引擎内置的`Auto LOD Generation`（基于Simplygon或Nanite Fallback Mesh）只提供几何简化，无法自动判断与流送边界协调的最优Screen Size参数。对于超大地图，技术美术仍需对场景中超过500面的非Nanite静态网格逐类型配置LOD，并在`World Settings > HLOD`面板中手动绑定每一层HLOD与对应LOD层的过渡参数。

**误区3：Nanite网格无需考虑LOD与流送的协同**
Nanite会自动管理三角形的微多边形剔除，但Nanite并不绕过流送系统——Nanite网格的Page数据（每页约128KB）仍然需要通过异步流送加载。在快速移动场景中，Nanite Page的流送延迟（典型值2~4帧）会导致近距离的Nanite资产暂时以低精度渲染，与LOD的屏幕尺寸错误视觉效果相似。监测此问题应使用`r.Nanite.Visualize.OverdrawTiledScaled`和`Stat NaniteStreaming`命令，而非LOD统计命令。

## 知识关联

本文建立在**HLOD系统**的基础上：HLOD代理网格正是LOD链在流送边界之外的延伸，理解HLOD的代理生成参数（如`Merge Distance`、`Proxy LOD Screen Size`）是配置LOD与流送协同过渡的前提条件。没有HLOD的LOD链在流送卸载后会直接消失，产生视觉空洞，因此HLOD充当了LOD3与流送卸载状态之间的缓冲层。

在技术美术的LOD策略体系中，LOD与流送是整个策略链的终端执行层——它将静态LOD参数、动态HLOD代理、流送半径、内存预算四个维度统一纳入一个运行时决策框架。掌握这一协同配置后，技术美术可以在`r.LOD.ForcedLODLevel`、`r.Streaming.PoolSize`和`World Partition Debug`三套工具之间灵活切换，针对不同平台（如PS5的12GB显存预算 vs PC的8GB显存目标）制定差异化的LOD-流送联合参数方案。