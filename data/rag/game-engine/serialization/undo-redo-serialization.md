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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Undo/Redo序列化

## 概述

Undo/Redo序列化是游戏编辑器中将每一次用户操作（如移动物体、修改材质参数、删除节点）封装为可逆事务的技术机制。与普通的场景序列化不同，它不仅要保存对象的最终状态，还必须同时记录操作前后的差量数据（Delta），使引擎能够精确地向前或向后重演操作历史。

这一机制最早在桌面图形软件中成熟，Photoshop 4.0（1996年）引入多步历史记录功能后，游戏引擎编辑器（如早期的 UnrealEd）也逐步采用了类似的命令模式（Command Pattern）作为底层架构。现代引擎如 Unity 的 `Undo` 类和 Unreal Engine 的 `FScopedTransaction` 都是这一思想的具体实现。

Undo/Redo序列化的重要性在于：编辑器中的误操作代价极高——一次错误的批量替换可能修改数百个对象属性，若无法回滚，将迫使开发者手动还原，严重破坏工作流。事务化记录将每次改动的成本限制在"一次Ctrl+Z"以内。

---

## 核心原理

### 命令模式与操作封装

Undo/Redo序列化依赖**命令模式（Command Pattern）**，将每个操作封装为一个命令对象，该对象至少包含两个方法：`Execute()`（执行操作）和 `Undo()`（撤销操作）。以 Unity 为例，调用 `Undo.RecordObject(target, "Move Object")` 时，引擎会在执行实际修改之前对 `target` 的序列化字段做一次快照，并将快照与操作名称一起压入撤销栈。

命令对象的最小结构通常如下：

```
Command {
    string  operationName   // 显示在菜单中的名称，如"Move"
    byte[]  beforeSnapshot  // 操作前的序列化数据
    byte[]  afterSnapshot   // 操作后的序列化数据
    GUID    targetObjectID  // 被修改对象的唯一标识
}
```

`targetObjectID` 采用 GUID 而非内存指针，是因为编辑器会话中对象可能被销毁再重建，指针失效会导致撤销时崩溃。

### 撤销栈与重做栈的双栈结构

操作历史由两个栈管理：**撤销栈（Undo Stack）** 和 **重做栈（Redo Stack）**。用户执行新操作时，命令对象被压入撤销栈，重做栈**清空**。用户按 Ctrl+Z 时，栈顶命令从撤销栈弹出、调用 `Undo()` 方法恢复 `beforeSnapshot`，然后将该命令压入重做栈。用户按 Ctrl+Y 时，从重做栈弹出命令、调用 `Execute()` 恢复 `afterSnapshot`，再将其重新压入撤销栈。

为了防止内存无限增长，大多数引擎设置了栈深度上限。Unity 默认的 `Undo` 栈深度为 **200步**，可通过 `Undo.SetCurrentGroupName` 合并相关操作以节省槽位。Unreal Engine 5 中对应的上限由 `ini` 文件中的 `UndoBufferSize` 控制，默认值为 **16 MB**（按内存而非步数限制）。

### 增量序列化与全量序列化的权衡

Undo/Redo序列化存在两种数据保存策略：

- **全量快照（Full Snapshot）**：操作前后各保存目标对象的完整序列化数据。实现简单，但对于含有大量子对象的复杂场景（如一个有 500 个组件的 Prefab），单次操作可能生成数兆字节的快照，导致内存迅速耗尽。

- **增量差量（Delta Recording）**：只记录实际发生变更的字段。例如仅移动了 Transform 的 Position，则只需序列化旧坐标向量 `(1.0, 0.0, 3.5)` 和新坐标向量 `(2.0, 0.0, 3.5)`，数据量缩减至数十字节。Unity 的 `Undo.RecordObject` 在内部使用基于属性路径的差量比对，仅序列化标记了 `[SerializeField]` 且值发生变化的字段。

实际引擎通常将两者结合：对单属性修改使用增量，对对象创建/删除操作使用全量快照，因为创建一个新对象本身就是"从无到有"的变化，无法用差量表达。

---

## 实际应用

**批量操作的事务合并**：在关卡编辑器中，开发者拖动鼠标框选 50 个敌人并统一调整高度，若每帧都产生一条撤销记录，操作历史会被数百条微小变化淹没。Unreal Engine 通过 `FScopedTransaction` 的作用域机制解决这一问题：在鼠标按下时开启事务作用域，鼠标松开时关闭，整个拖拽过程只生成**一条**撤销记录。Unity 对应的方案是 `Undo.CollapseUndoOperations(int groupIndex)`，将指定组号之后的所有操作合并为一步。

**自定义编辑器工具的集成**：开发者用 `EditorWindow` 编写自定义工具时，如果直接修改 `MonoBehaviour` 字段而不调用 `Undo.RecordObject`，该操作将对 Undo 系统不可见，用户按 Ctrl+Z 无效。这是自定义编辑器工具最常见的"漏记"问题。正确做法是在任何赋值语句之前插入记录调用：

```csharp
Undo.RecordObject(myComponent, "Change Health");
myComponent.maxHealth = 200;  // 现在此修改可被撤销
```

**对象创建与销毁的序列化**：删除一个对象时不能仅记录其 GUID——对象已不存在，恢复时需要完整数据。Unity 使用 `Undo.DestroyObjectImmediate` 替代 `GameObject.Destroy`，它会在销毁前序列化对象的全部数据并隐藏对象（而非真正释放内存），直到撤销栈将其彻底清除。

---

## 常见误区

**误区一：认为 Undo/Redo 等同于场景存档读档**

场景存档序列化保存的是完整场景的某一时刻静态状态，文件格式通常为 JSON 或二进制资产文件。Undo/Redo序列化保存的是操作的"变化向量"，其数据在引擎进程退出后**默认不持久化**。关闭 Unity 再重启项目后，Undo 历史归零，这与"读取上一个存档"的行为截然不同。两者的序列化格式、存储位置、生命周期均不相同。

**误区二：增量差量总比全量快照更优**

增量方案在读写单个属性时效率极高，但**重建（Replay）成本随历史深度线性增长**。若需要从第 1 步回放到第 180 步的状态，必须依次应用 180 个增量——全量快照则只需加载一次。因此，部分引擎对每隔 N 步插入一个完整"关键帧快照"，这与视频编解码中的 I 帧（关键帧）/ P 帧（差量帧）策略完全相同。简单地认为"差量一定更好"会导致长历史链下的回退性能急剧下降。

**误区三：只需为可见属性记录 Undo**

开发者有时只对位置、旋转等可见属性调用 `RecordObject`，而忽略内部引用字段（如 `List<GameObject>` 类型的子节点列表）。当用户撤销一次"添加子节点"操作时，位置数据还原了，但子节点列表未还原，场景进入数据不一致的损坏状态。完整的 Undo 记录必须覆盖操作所影响的**所有序列化字段**，包括引用关系。

---

## 知识关联

**前置概念**：理解 Undo/Redo序列化需要先掌握**序列化概述**中的核心概念，特别是字段标注（`[SerializeField]`）和对象图（Object Graph）遍历——因为快照本质上是对对象图的局部序列化，不了解哪些字段会被序列化就无法正确界定记录范围。

**横向关联**：Undo/Redo序列化与**版本控制系统（VCS）**的 diff/patch 机制在数学结构上高度同构，区别在于 VCS 的操作单元是文件行，而此处的操作单元是引擎对象的属性路径。熟悉 Git 的开发者可以将 `beforeSnapshot` 理解为 `git stash`，将增量差量理解为 `git diff` 输出的二进制版本。

**后续扩展方向**：掌握 Undo/Redo序列化后，可进一步探索**协同编辑（Collaborative Editing）**场景，即多人同时编辑同一场景时如何合并来自不同客户端的操作历史，这涉及操作转换（Operational Transformation, OT）算法，是此机制在多用户环境下的直接延伸。