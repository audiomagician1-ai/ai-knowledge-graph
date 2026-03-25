---
id: "undo-redo-serialization"
concept: "Undo/Redo序列化"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 3
is_milestone: false
tags: ["编辑器"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Undo/Redo序列化

## 概述

Undo/Redo序列化是游戏编辑器中将每一次用户操作（如移动物体、修改材质参数、删除节点）封装成可逆事务记录的技术机制。其核心思想是在操作发生时同时捕获"操作前状态"与"操作后状态"（或等价的逆操作描述），并将这些记录以有序序列的形式持久化，从而支持多步撤销与重做。

该机制最早在1974年由Warren Teitelman在Interlisp系统中以"Do What I Mean"理念引入，后来被图形编辑器广泛采用。Unity Editor从2.x版本起引入序列化驱动的Undo系统（`Undo.RecordObject`），Unreal Engine 4则通过`FScopedTransaction`类实现基于事务块的Undo记录。理解这一机制对于开发自定义编辑器工具和避免编辑器数据丢失至关重要。

与运行时序列化（保存游戏存档）不同，Undo/Redo序列化强调的是**操作的可逆性**而非状态的完整性。它不需要序列化整个场景，只需精确记录每次操作所改变的最小数据集，因此其序列化粒度通常精确到单个属性字段级别。

## 核心原理

### 命令模式与事务封装

Undo/Redo序列化在实现上依赖命令模式（Command Pattern）。每个用户操作被封装为一个命令对象，该对象包含三个要素：`Execute()`（执行操作）、`Undo()`（撤销操作）、以及序列化所需的数据载荷。命令对象本身需要实现序列化接口，使得整个Undo栈可以写入磁盘，在编辑器崩溃后恢复。

在Unity的实现中，`Undo.RecordObject(target, "Move Object")`会在操作执行前对目标对象的当前状态拍快照，序列化其所有被`[SerializeField]`标记的字段。快照数据以二进制格式压缩存储于内存中的Undo栈。

### 快照法与差量法

实现Undo序列化有两种主流策略：

**快照法（Snapshot）**：在操作前后各记录一份完整的对象状态序列化数据。撤销时直接反序列化"操作前快照"还原状态。优点是实现简单，缺点是对大型对象（如含有5000个顶点的Mesh）内存开销显著。Unreal中`PreEditChange`/`PostEditChange`回调即采用此模式记录`UObject`属性的前后值。

**差量法（Delta/Diff）**：仅记录发生变更的字段及其新旧值。例如，将一个`Transform`组件的Position从`(0,0,0)`改为`(1,2,3)`，只需记录`{field: "position", old: Vector3(0,0,0), new: Vector3(1,2,3)}`，而非整个组件的序列化数据。差量法在频繁编辑场景下内存效率更高，但需要字段级别的序列化感知能力。

### Undo栈的序列化结构

Undo历史在内存中通常以**双端有界栈（Bounded Deque）**形式管理。Unity默认保留最近200步Undo记录（可通过`Preferences > General > Undo History`调整）。当执行新操作时，栈顶之后的所有Redo记录被丢弃——这一行为本身需要在序列化时被正确处理，避免分支状态泄露。

每条Undo记录（`UndoRecord`）的序列化数据结构通常包含：
- **操作名称**（字符串，显示于Edit菜单）
- **目标对象ID**（GUID或InstanceID，用于反序列化时定位对象）
- **序列化载荷**（操作前/后状态的二进制数据）
- **时间戳**（用于合并短时间内的连续操作，如连续输入文字合并为单一Undo步骤）

### 合并（Merge/Collapse）策略

连续的同类操作若不合并，会导致Undo栈过快膨胀。例如在属性面板中拖动一个浮点数滑杆，若每帧都产生一条记录则毫无意义。Undo序列化系统通过**操作分组Token**解决此问题：`Undo.CollapseUndoOperations(int groupIndex)`（Unity API）可将同一交互手势内的多条记录合并为一个可撤销步骤。合并的判定依据是操作类型相同且目标对象ID一致，且时间间隔小于预设阈值（通常为500毫秒）。

## 实际应用

**地形编辑器的笔刷操作**：用户在地形上涂刷高度时，每帧都会修改大量顶点高度数据。若采用快照法，每帧序列化完整高度图（如512×512的浮点数组）代价极高。实际方案是在笔刷按下时记录被影响区域的初始高度数据快照（差量法只记录笔刷覆盖范围内的Chunk），笔刷释放时提交为单一Undo记录，使内存占用从"每帧×完整地形大小"降为"单次操作×受影响区域"。

**prefab重命名操作**：当用户修改Prefab中某个GameObject的名称时，Undo系统需要序列化的数据仅为`{objectID: "abc123", field: "m_Name", old: "Cube", new: "PlayerBody"}`，整条记录不超过几十字节。这是差量法序列化的典型应用场景。

**多对象批量操作**：在场景中选中100个物体并批量修改其Layer属性时，Undo系统会为每个对象生成独立的差量记录，但将它们绑定在同一个`groupIndex`下，使得一次Ctrl+Z可撤销全部100个修改。

## 常见误区

**误区一：Undo序列化会保存整个场景**。事实上，Undo序列化仅记录操作所影响的最小对象集合的变更数据，而非序列化整个场景树。错误地在每次操作时调用`EditorSceneManager.SaveScene()`来"备份"状态，反而会绕过Undo系统，导致无法撤销。

**误区二：Undo栈在编辑器重启后仍然有效**。Unity和Unreal的Undo栈默认存储在内存中，编辑器关闭即清空。若需要跨会话的操作历史，需要将Undo记录显式序列化到磁盘文件，并在编辑器启动时反序列化恢复——这是一项需要额外实现的高级功能，大多数商业引擎默认不提供。

**误区三：对同一对象调用多次`RecordObject`是安全的**。在Unity中，同一帧内对同一对象重复调用`Undo.RecordObject`会覆盖前一次快照，导致中间状态丢失。正确做法是在操作开始前调用一次，确保捕获完整的初始状态。

## 知识关联

**前置知识**：Undo/Redo序列化建立在通用序列化机制之上，需要了解字段级序列化标记（如`[SerializeField]`）、对象ID系统（InstanceID/GUID用于跨序列化边界引用对象）以及二进制序列化格式的基础概念。没有这些前置知识，将无法理解为何"目标对象定位"在Undo反序列化时是最易出错的环节。

**横向关联**：Undo/Redo序列化与**场景快照序列化**（用于Play Mode进入/退出时还原编辑器状态）共享大量底层机制，但后者序列化的是完整场景而非增量操作。此外，**网络协同编辑**场景下的操作同步（CRDT算法）可视为Undo序列化的分布式扩展，每个操作记录需附加时间戳和用户标识以支持冲突解决。
