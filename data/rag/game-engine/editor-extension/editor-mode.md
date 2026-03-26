---
id: "editor-mode"
concept: "编辑器模式"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 3
is_milestone: false
tags: ["模式"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
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


# 编辑器模式

## 概述

编辑器模式（Editor Mode）是 Unreal Engine 提供的一种机制，允许开发者在编辑器视口中注入自定义的输入处理逻辑、鼠标交互行为和可视化反馈，从而创建专属的关卡编辑工作流。与普通的编辑器扩展不同，编辑器模式拥有独立的激活/停用生命周期，并能完全接管视口的鼠标点击、拖拽和键盘事件，而不干扰引擎的其他模块。

该机制在引擎内部已被用于实现 **Placement Mode**（对象放置模式）、**Foliage Mode**（植被绘制模式）、**Landscape Mode**（地形雕刻模式）等内置工具。这些内置模式自 UE4 早期版本起就存在，并随 UE5 在 `UEdMode` 的基础上演变出了新的 `UEdModeInteractive` 和基于 `FEditorModeTools` 的注册接口。理解内置模式的实现方式，是开发自定义编辑器模式的最佳参考路径。

对于需要重复性地在场景中绘制、摆放或标注特定对象的游戏开发场景——例如路点编辑、样条曲线控制点操作、NPC 巡逻区域绘制——自定义编辑器模式能将这些工作从繁琐的手动操作简化为一次性的专用工具，大幅提升关卡设计效率。

---

## 核心原理

### 编辑器模式的类层级与注册

自定义编辑器模式的基类是 `UEdMode`（旧接口）或 `UEdModeInteractive`（UE5 推荐接口）。每个模式必须定义一个唯一的 `FEditorModeID`，通常声明为静态常量字符串，例如：

```cpp
const FEditorModeID FMyCustomMode::EM_MyCustomModeId = TEXT("EM_MyCustomMode");
```

注册通过 `FEditorModeRegistry::Get().RegisterMode<FMyCustomMode>(...)` 完成，通常放在模块的 `StartupModule()` 中，并在 `ShutdownModule()` 中调用 `UnregisterMode` 注销。未正确注销会导致编辑器关闭时出现悬空指针崩溃，这是最常见的开发错误之一。

### 生命周期函数与视口接管

编辑器模式拥有四个关键生命周期回调：

- **`Enter()`**：模式激活时调用，用于初始化工具状态、创建 UI 面板、注册撤销事务。
- **`Exit()`**：模式退出时调用，必须清理所有由 `Enter()` 创建的资源，否则内存泄漏。
- **`Tick(float DeltaTime)`**：每帧调用，可用于更新悬停预览对象的位置。
- **`InputKey / InputDelta`**：处理键盘和鼠标输入，返回 `true` 表示事件已消费，阻止后续默认处理。

Foliage Mode 正是在 `InputDelta` 中监听鼠标左键拖拽，并在每一帧根据鼠标射线投影到地表来决定植被实例的批量生成位置。

### 视口绘制与 HitProxy

编辑器模式可重写 `Render(const FSceneView*, FViewport*, FPrimitiveDrawInterface*)` 和 `DrawHUD(FEditorViewportClient*, FViewport*, const FSceneView*, FCanvas*)` 来绘制自定义调试图形、预览网格或操作手柄。

**HitProxy** 是编辑器模式中实现可点击元素的核心机制。通过为每个可交互元素声明派生自 `HHitProxy` 的结构体，并在渲染时调用 `PDI->SetHitProxy(new HMyProxy(...))` 绑定，即可在 `InputKey` 中通过 `HitResult` 识别用户具体点击了哪个对象。Placement Mode 的预览对象拖放正是依赖该机制实现的。

---

## 实际应用

### 路点编辑器模式

在 AI 导航场景中，可构建一个路点编辑器模式：激活后，每次鼠标左键单击地表时，在射线命中位置生成一个 `AWaypoint` Actor，并自动连接到上一个路点形成序列。利用 `GEditor->BeginTransaction(TEXT("Add Waypoint"))` 与 `GEditor->EndTransaction()` 包裹生成操作，使每次放置都可被 Ctrl+Z 撤销。该模式还可在 `Render()` 中用 `PDI->DrawLine()` 将所有路点连线可视化，无需在场景中创建任何额外的调试 Actor。

### 区域刷子绘制模式

类似 Foliage Mode 的笔刷机制，可实现一个"触发区域绘制模式"：按住鼠标左键拖动时，以笔刷半径（可由编辑器面板 Slate 控件调节，范围建议 100–5000cm）为参数，在地表批量放置触发体积。笔刷预览圆圈通过 `DrawCircle()` 在 `Render()` 中每帧重绘，中心跟随鼠标在地表的投影点实时移动。

---

## 常见误区

### 误区一：认为编辑器模式只能存在一个激活实例

`FEditorModeTools` 实际上维护一个模式栈，允许多个模式同时处于激活状态。默认的 `EEditorModeID::EM_Default`（对象选择模式）几乎始终保持激活，开发者自定义模式会叠加在其上。若在 `InputKey` 中忘记正确返回 `true`（已消费）或 `false`（未消费），可能导致自定义逻辑与默认选择逻辑发生意外冲突，产生双重触发现象。

### 误区二：在 `Tick()` 中直接修改世界对象

编辑器模式的 `Tick()` 在编辑器帧循环中调用，此时场景处于"编辑器世界"上下文。若在 `Tick()` 中直接修改 Actor 属性而不经过事务系统，这些修改将**不可撤销**，且可能绕过属性复制，导致关卡保存时数据不一致。所有对场景的永久修改都应包裹在 `FScopedTransaction` 中，而预览性的临时变化（如悬停预览）应使用独立的预览 Actor 而非修改真实场景对象。

### 误区三：混淆编辑器模式与编辑器工具蓝图（Editor Utility Widget）

Editor Utility Widget 适用于批处理操作和资产管理，其交互入口是面板按钮点击；而编辑器模式的核心价值在于**视口层级的实时交互**——射线检测、拖拽、笔刷绘制。若仅需一个"批量替换选中 Actor"的工具，Editor Utility Widget 更合适；若需要"在视口中交互式绘制样条路径"，则必须使用编辑器模式。二者的选择取决于工具是否需要直接操作视口输入流。

---

## 知识关联

编辑器模式建立在**编辑器扩展概述**中介绍的模块化扩展体系之上，要求开发者已掌握编辑器模块的创建、Slate UI 的基本用法以及 `GEditor` 全局对象的访问方式。在具体实现时，还需理解 `FViewportClient` 的视口渲染管线，以及 UE 的事务撤销系统（`UTransBuffer`）如何追踪对象修改。

掌握编辑器模式后，可进一步探索 **Interactive Tools Framework（ITF）**，这是 UE5 引入的更高层抽象，`UEdModeInteractive` 本身就是基于 ITF 构建的——Modeling Mode（建模模式）完全依赖 ITF 的 `UInteractiveTool` 和 `UInteractiveToolManager` 实现各类网格编辑操作，是编辑器模式与 ITF 结合应用的最完整案例。