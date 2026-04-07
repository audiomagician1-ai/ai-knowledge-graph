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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

编辑器模式（Editor Mode）是 Unreal Engine 中一种允许开发者自定义编辑器交互行为的扩展机制，通过继承 `FEdMode` 类（或在 UE5 中继承 `UEdMode`）来实现特定工具集的激活、视口操作拦截和自定义 UI 面板。当某个编辑器模式被激活时，它会接管视口中的鼠标点击、拖拽和键盘事件，使开发者能够构建如地形绘制、植被摆放（Foliage）、样条线编辑等高度专业化的关卡编辑工具。

Unreal Engine 的编辑器模式系统最早在 UE3 时代以 `FEdMode` 形式出现，UE4 延续了这一架构并内置了若干官方模式，包括 `FPlacementMode`（物体摆放）、`FMeshPaintMode`（网格体绘制）和 `FLandscapeEdMode`（地形编辑）。到 UE5，虚幻引擎引入了 `UEdMode` 作为更面向对象的替代方案，同时保留了对旧版 `FEdMode` 的兼容。理解两者的差异对于在正确的版本中选用正确的基类至关重要：`FEdMode` 是纯 C++ 结构体风格，而 `UEdMode` 是 `UObject` 子类，可以被蓝图反射系统识别。

编辑器模式之所以重要，在于它将"工具逻辑"与"普通编辑器插件逻辑"分离开来。植被工具（Foliage Tool）若不以编辑器模式实现，则无法在用户点击视口时自动散布静态网格体实例；物体摆放模式（Placement Mode）若缺少模式框架，则无法在鼠标悬停时实时预览资产投影。

---

## 核心原理

### FEdMode / UEdMode 生命周期

一个自定义编辑器模式的注册依赖于 `FEditorModeRegistry`。在模块启动时，开发者调用：

```cpp
FEditorModeRegistry::Get().RegisterMode<FMyCustomMode>(
    FMyCustomMode::EM_MyCustomModeId,
    LOCTEXT("MyCustomMode", "My Custom Mode"),
    FSlateIcon(),
    true
);
```

其中 `EM_MyCustomModeId` 是一个 `FEditorModeID`（本质为 `FName`），全局唯一标识该模式。激活模式后，引擎依次调用 `Enter()`、若干帧的 `Tick(float DeltaTime)` 以及最终的 `Exit()`。开发者在 `Enter()` 中初始化工具状态，在 `Exit()` 中清理所有临时 Actor 和资源，以避免模式切换后遗留垃圾数据。

### 视口事件拦截

`FEdMode` 提供了一系列可重写的输入回调，最常用的包括：

- `bool InputKey(FEditorViewportClient*, FViewport*, FKey, EInputEvent)`：拦截键盘与鼠标按键，返回 `true` 表示消耗该事件，阻止其传递给普通视口逻辑。
- `bool InputDelta(FEditorViewportClient*, FViewport*, FVector&, FRotator&, FVector&)`：拦截平移/旋转/缩放增量，Foliage 模式用此函数实现画刷大小的实时缩放预览。
- `void Render(const FSceneView*, FViewport*, FPrimitiveDrawInterface*)`：在视口中绘制调试几何体，Placement 模式用此函数渲染资产投影幽灵（Ghost Preview）。

Foliage 编辑器模式（`FoliageEditMode`）的画刷半径默认为 512 cm，通过 `InputDelta` 中检测鼠标滚轮偏移量乘以系数 `10.0f` 来动态调整，这一具体数值可在 `FoliageEditMode.cpp` 源码中查阅。

### 工具包（Toolkit）与 UI 面板

每个编辑器模式通常配套一个 `FModeToolkit` 子类，负责向编辑器左侧模式面板（Mode Panel）注入 Slate UI。`FModeToolkit::GetInlineContent()` 返回一个 `TSharedPtr<SWidget>`，引擎将其嵌入到模式面板的对应插槽中。Placement Mode 的资产浏览网格（Asset Grid）、Foliage Mode 的植被实例列表，均通过各自的 Toolkit 类构建 Slate 控件来呈现，而非使用 Details Panel 反射系统——这是与普通 `UObject` 编辑器扩展的关键区别之一。

---

## 实际应用

### 仿制植被摆放工具

假设需要为项目构建一个"道路标志自动摆放模式"，步骤如下：

1. 继承 `FEdMode`，在 `Enter()` 中创建一个不可见的球形 `UStaticMeshComponent` 作为预览画刷。
2. 重写 `InputKey`：当检测到 `EKeys::LeftMouseButton` 按下且未按 `Alt` 键时，执行射线检测（`FHitResult`），在命中点以 `GEditor->AddActor()` 生成道路标志 Actor，并返回 `true` 消耗事件。
3. 在 `Render()` 中使用 `PDI->DrawSphere()` 绘制摆放半径预览圆圈，半径与步骤 2 中的碰撞检测范围一致（例如 200 cm）。
4. 在模块 `ShutdownModule()` 中调用 `FEditorModeRegistry::Get().UnregisterMode()` 防止模块卸载后模式残留。

### 物体摆放模式（Placement Mode）扩展

UE4/5 内置的 `FPlacementMode` 通过 `IPlacementModeModule::Get().RegisterPlacementCategory()` 接受外部分类注册，无需修改引擎源码。调用时传入 `FPlacementCategoryInfo` 结构体，指定分类名称、图标和排序优先级（`SortOrder` 整数值，内置"最近放置"分类使用值 `0`，自定义分类通常设置为 `45` 或更高）。

---

## 常见误区

### 误区一：在 Tick 中直接修改关卡数据而不标记脏数据

许多初学者在 `FEdMode::Tick()` 中直接修改 Actor 属性，却忘记调用 `Actor->MarkPackageDirty()` 或使用 `GEditor->BeginTransaction()`/`GEditor->EndTransaction()` 包裹操作。结果是编辑器不提示保存，重启后修改丢失，且撤销（Ctrl+Z）系统无法回滚这些改动。正确的做法是将所有持久性改动包裹在 `FScopedTransaction` 中，并在改动对象前调用 `Object->Modify()`。

### 误区二：混淆 FEdMode 与 EditorUtilityWidget 的职责

编辑器模式专为"视口交互工具"设计，若只需要一个浮动操作面板或批量处理脚本，`EditorUtilityWidget`（蓝图驱动的编辑器工具控件）是更轻量的选择。将简单的资产批量重命名逻辑塞进 `FEdMode` 会引入不必要的视口事件注册开销，且在没有视口焦点时模式可能无法正常触发。

### 误区三：UE5 中仍使用 FEdMode 而非 UEdMode

UE5 引入的 `UEdMode` 支持通过 `UPROPERTY` 暴露属性到 Details Panel，并能在蓝图中调用工具函数；而 `FEdMode` 无法被反射系统感知。若项目为 UE5.0 及以上且需要蓝图调用或在线内容浏览器集成，强制使用 `FEdMode` 会导致大量功能无法使用，例如 `GetToolManager()` 接口仅在 `UEdMode` 中可用。

---

## 知识关联

编辑器模式建立在**编辑器扩展概述**所介绍的模块系统和 `IModuleInterface` 生命周期之上：模式的注册必须在模块的 `StartupModule()` 中完成，注销必须在 `ShutdownModule()` 中完成，这与编辑器扩展的通用插件结构直接对接。

掌握编辑器模式后，可自然延伸至 **Interchange 导入框架**（理解编辑器工具与资产管线如何协作）以及 **Slate UI 框架**（为自定义模式构建更复杂的工具面板）。Foliage 模式与 **HISM（Hierarchical Instanced Static Mesh）**的关系同样值得深入——植被模式在底层通过 `AInstancedFoliageActor` 和 `UHierarchicalInstancedStaticMeshComponent` 管理所有植被实例，理解这一数据结构有助于优化大规模植被场景的运行时性能。