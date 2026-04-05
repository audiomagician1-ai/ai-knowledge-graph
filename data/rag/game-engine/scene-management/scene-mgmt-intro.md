---
id: "scene-mgmt-intro"
concept: "场景管理概述"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
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

# 场景管理概述

## 概述

场景管理（Scene Management）是游戏引擎中负责组织、加载、卸载和维护游戏世界所有对象的子系统。它定义了游戏世界从空白状态到完整运行状态的全过程，包括地形、静态网格、光源、音频触发器、NPC、玩家起始点等所有实体的生命周期控制。没有场景管理系统，游戏引擎将无法确定"什么时候把哪些内容放到内存里"。

场景管理的概念随着游戏复杂度的增长而逐渐成熟。早期游戏（如1993年的《DOOM》）将整个关卡数据一次性加载到内存中，因为关卡体量足够小。随着3D游戏世界的规模从几十个房间扩展到数十平方公里的开放世界，场景管理不得不引入流式加载（Streaming）、层级结构（Hierarchy）和分区（Partition）等机制。现代引擎如Unreal Engine 5引入了World Partition系统，将场景自动划分为若干Cell，按需加载，彻底改变了传统关卡设计的工作流。

理解场景管理对于游戏开发者至关重要，因为它直接影响内存占用峰值、帧率稳定性和迭代开发效率。一个设计不当的场景结构会导致关卡切换时出现几秒甚至十几秒的卡顿，破坏游戏沉浸感；而良好的场景管理能让玩家感受到无缝、连续的世界。

## 核心原理

### 场景的组织结构

游戏场景的底层组织形式通常是一棵**场景图（Scene Graph）**树形结构。每个节点代表一个游戏对象（Game Object 或 Actor），父节点的变换矩阵会传播到所有子节点。例如，一辆汽车是父节点，四个车轮是子节点；移动父节点，子节点随之移动，无需额外计算。节点之间的父子关系在内存中以指针链表或数组索引的形式存储，查询某对象的世界坐标需要从根节点向下乘累积变换矩阵：

**WorldTransform = ParentWorldTransform × LocalTransform**

在 Unreal Engine 中，这套结构对应的是 `UWorld` 包含多个 `ULevel`，每个 `ULevel` 包含若干 `AActor`，每个 `AActor` 挂载若干 `UActorComponent`。

### 场景生命周期阶段

一个游戏场景的生命周期包含以下明确阶段：

1. **创建（Creation）**：引擎分配内存，反序列化场景数据文件（如 Unreal 的 `.umap` 文件或 Unity 的 `.unity` 文件）。
2. **初始化（Initialization）**：所有对象执行 `BeginPlay`（Unreal）或 `Start`（Unity）回调，建立对象间引用，启动物理模拟。
3. **运行（Running）**：每帧调用 `Tick` 或 `Update`，处理游戏逻辑。
4. **暂停（Suspended）**：场景逻辑停止 Tick，但内存中对象仍保留，常用于多场景叠加时的后台场景。
5. **卸载（Unloading）**：调用 `EndPlay`，销毁对象，释放显存和内存，清理引用计数。

跳过任何一个阶段或顺序出错（例如在 `BeginPlay` 之前访问其他对象）是场景管理中崩溃和空指针错误的最常见原因。

### 流式加载与内存预算

现代开放世界游戏不能把整个地图同时放进内存。场景管理系统根据玩家位置和摄像机朝向维护一个**流式距离（Streaming Distance）**，超出距离的场景单元被标记为待卸载，进入视野范围的单元被异步加载。Unreal Engine 5 的 World Partition 中，每个 Cell 的默认大小为 **128m × 128m**（可配置），引擎根据玩家位置动态激活或休眠对应 Cell 内的 Actor。

流式加载必须在后台线程执行，以避免主线程卡顿。这要求场景数据格式支持随机访问，例如 Unreal 将每个 Actor 的数据打包成独立的 Chunk，存储在 `.umap` 的特定偏移地址，加载时直接 seek 到该偏移读取，而不必读取整个文件。

## 实际应用

**多场景叠加加载**：在 Unity 中，可以使用 `LoadSceneAsync(sceneName, LoadSceneMode.Additive)` 将多个场景叠加到同一个 World 中。这种模式常用于在不卸载主场景的前提下，动态加入室内场景或 Boss 战特效场景，避免切换时的黑屏等待。

**关卡流送触发器**：《原神》等开放世界游戏在地图中放置不可见的 Trigger Volume，当角色进入触发器后，场景管理系统开始预加载下一个区域的资产。玩家走过去的那一刻，资产恰好加载完毕，实现"无缝"体验。实际上这是一种隐藏了加载时间的预测性流送策略，而非真正的零加载时间。

**编辑器中的子场景（Sub-Level）**：Unreal Engine 的 World Composition 功能允许多个关卡设计师同时编辑同一个大地图的不同区域，每人负责独立的 `.umap` 子关卡，最终由持久关卡（Persistent Level）统一引用。这种工作流避免了多人同时修改同一个文件时产生的版本冲突，是大型项目场景管理的标准协作模式。

## 常见误区

**误区一：场景等同于关卡文件**
很多初学者认为"一个 `.umap` 文件 = 一个场景"。实际上，Unreal 的一个 World 可以同时包含多个激活的 Level（持久关卡 + 若干子关卡），而 World Partition 模式下甚至没有手动划分的子关卡概念，场景管理完全由运行时坐标驱动。将场景与文件一一对应会导致在大型项目中错误地设计加载边界。

**误区二：场景卸载是即时的**
调用 UnloadLevel 或 LoadScene 并不意味着内存立即释放。Unreal 和 Unity 都依赖垃圾回收（GC）或延迟析构机制，对象引用被清空后，实际内存释放可能延迟数帧甚至更长时间。在内存敏感的平台（如主机或移动端）切换场景后立即申请大量内存，往往会触发内存不足，原因正在于此。

**误区三：场景管理只影响内存，不影响 CPU**
场景中每个激活的 Actor 每帧都会参与 Tick、物理、碰撞和导航查询。即使一个区域在屏幕外不被渲染（Culled），它的逻辑仍在消耗 CPU。正确的做法是通过场景管理将远离玩家的 Actor 设置为休眠（Dormant）或完全卸载，而非仅依赖渲染剔除。

## 知识关联

学习场景管理概述需要具备**游戏引擎概述**的基础，理解引擎各子系统（渲染、物理、脚本）如何协作，以及 **World Partition** 的分区机制是如何作为现代场景管理的基础设施存在的。

在此基础上，场景管理延伸出多个专项主题：**场景图**深入讲解树形层级结构的遍历与变换计算；**世界组合（World Composition）**讲解多子关卡的协作流程；**场景数据层（Data Layers）**讲解如何按逻辑分类管理 Actor（如昼夜切换、任务状态层）；**生成系统（Spawning System）**讲解运行时动态创建和销毁 Actor 的规则；**场景持久状态**讲解存档系统如何记录哪些对象被修改或销毁，从而在玩家下次进入时恢复正确状态。这六个方向共同构成了完整的游戏场景管理知识体系。