---
id: "custom-editor-window"
concept: "自定义编辑器窗口"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 2
is_milestone: false
tags: ["UI"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 自定义编辑器窗口

## 概述

自定义编辑器窗口（Custom Editor Window）是游戏引擎编辑器扩展中的一种机制，允许开发者创建可停靠（Dockable）、可浮动的独立面板，用于承载工具界面、数据可视化或工作流辅助功能。与仅在 Inspector 中显示的自定义Inspector不同，编辑器窗口拥有独立的生命周期和窗口句柄，可以脱离任何选中对象独立存在。

在 Unity 中，自定义编辑器窗口的历史可追溯到 Unity 3.x 时代的 `EditorWindow` 基类，该类至今仍是 Unity 编辑器扩展的核心 API。Unreal Engine 则通过 Slate UI 框架和 `SDockTab` 体系实现类似功能，两套体系在注册方式和渲染管线上有本质区别。自定义编辑器窗口的价值在于：它能够将重复性的手工操作（如批量资产处理、场景分析报告）封装为一套持久化的工具界面，而不依赖任何特定游戏对象的选中状态。

## 核心原理

### Unity EditorWindow 的创建与注册

在 Unity 中，创建自定义窗口需要继承 `UnityEditor.EditorWindow` 类，并使用静态方法 `GetWindow<T>()` 完成实例化与注册。典型的最小实现如下：

```csharp
using UnityEditor;

public class MyToolWindow : EditorWindow
{
    [MenuItem("Tools/My Tool Window")]
    public static void ShowWindow()
    {
        GetWindow<MyToolWindow>("My Tool");
    }

    private void OnGUI()
    {
        EditorGUILayout.LabelField("窗口内容区域");
    }
}
```

`[MenuItem]` 属性负责在编辑器菜单栏注册入口，路径格式为 `"顶级菜单/子菜单"`。`GetWindow<T>()` 会检查是否已有同类型窗口实例存在——若存在则聚焦，若不存在则新建，从而保证窗口单例行为。若需要允许多实例，应改用 `CreateWindow<T>()`，该方法在 Unity 2019.1 版本起可用。

### 窗口生命周期回调

`EditorWindow` 提供了一套专属于编辑器窗口的生命周期方法，与 `MonoBehaviour` 的运行时生命周期完全分离：

- `OnEnable()`：窗口被创建或重新加载时触发，适合初始化数据和订阅编辑器事件（如 `Selection.selectionChanged`）。
- `OnGUI()`：每帧（或每次重绘请求）调用，所有 UI 绘制代码必须在此方法内执行，不可在其他方法中调用 `GUI.*` 系列函数。
- `OnDisable()`：窗口关闭或编辑器重编译前触发，必须在此处取消订阅所有事件，否则会导致空引用异常。
- `Update()`：以编辑器帧率（非固定60fps，取决于编辑器活跃状态）调用，适合轮询数据变化并调用 `Repaint()` 刷新界面。

若在 `Update()` 中无条件调用 `Repaint()`，会导致编辑器持续重绘，消耗不必要的CPU资源，应加入脏标记（Dirty Flag）判断。

### Unreal Engine 中的 SDockTab 注册

在 Unreal Engine 5 中，自定义编辑器窗口通过 `FGlobalTabmanager::Get()->RegisterNomadTabSpawner()` 注册为一个 **Nomad Tab**（游牧标签页）。Nomad Tab 的特点是全局唯一且不属于任何特定编辑器布局，适合独立工具窗口。注册时需提供 `FTabId`（字符串标识符）和一个返回 `TSharedRef<SDockTab>` 的委托：

```cpp
FGlobalTabmanager::Get()->RegisterNomadTabSpawner(
    FName("MyToolTab"),
    FOnSpawnTab::CreateRaw(this, &FMyToolModule::OnSpawnTab)
).SetDisplayName(LOCTEXT("MyToolTabTitle", "My Tool"));
```

注册通常在模块的 `StartupModule()` 中执行，并在 `ShutdownModule()` 中调用 `UnregisterNomadTabSpawner()` 完成反注册，防止引擎关闭时崩溃。

## 实际应用

**批量资产重命名工具**：一个典型的自定义编辑器窗口用例是资产批量重命名面板。该窗口在 `OnEnable()` 中订阅 `Selection.selectionChanged` 事件，当用户在 Project 面板选中多个资产时，窗口自动列出所选资产的当前名称。用户输入前缀/后缀规则后，点击按钮调用 `AssetDatabase.RenameAsset()` 完成批量操作，最后调用 `AssetDatabase.SaveAssets()` 持久化更改。

**场景对象统计面板**：在大型场景优化阶段，可创建一个编辑器窗口，在 `OnGUI()` 中使用 `EditorGUILayout.BeginScrollView()` 展示场景内所有 MeshRenderer 的面数统计，并按降序排列。此窗口可通过 `SceneView.duringSceneGui` 事件与场景视图联动，在用户点击列表项时自动定位并高亮对应物体。

## 常见误区

**误区一：在 OnGUI 之外调用 GUI 绘制方法**。`EditorGUILayout.TextField()` 等方法依赖 `Event.current` 对象，该对象只在 `OnGUI()` 执行期间有效。如果在 `Update()` 或外部回调中调用这些方法，Unity 会抛出 `ArgumentException: Getting control X's position in a group with only X controls`，且难以追踪根源。所有 UI 状态变量应存储在字段中，在 `OnGUI()` 中统一读写。

**误区二：混淆 GetWindow 与 CreateInstance**。部分开发者习惯用 `ScriptableObject.CreateInstance<T>()` 的思维来理解编辑器窗口创建，直接 `new MyToolWindow()` 或手动调用构造函数。`EditorWindow` 实例必须通过 `GetWindow<T>()` 或 `CreateWindow<T>()` 创建，由编辑器底层管理其与本地窗口句柄的绑定，手动实例化的窗口对象无法正确渲染且会导致编辑器状态异常。

**误区三：忽视编辑器重编译时的状态丢失**。Unity 每次脚本重编译后都会重建 AppDomain，`EditorWindow` 的 C# 字段会丢失。若需要跨编译保留窗口数据（如用户输入的文本），必须使用 `[SerializeField]` 标记字段，或将数据存入 `EditorPrefs`，否则每次修改代码后窗口都会重置为初始状态。

## 知识关联

学习自定义编辑器窗口之前，需要掌握**编辑器扩展概述**中的 `[MenuItem]` 属性用法和 `AssetDatabase` 基本操作，因为这两者构成了编辑器窗口注册入口和数据操作的基础调用方式。

完成本节后，可以进入**内容浏览器扩展**（Content Browser Extension）的学习。内容浏览器扩展在 Unreal Engine 中需要将自定义菜单项和资产操作面板嵌入已有的内容浏览器标签页，其 `FContentBrowserModule` 的委托注册模式与本节的 Tab 注册机制高度相似，但面向的是子面板而非独立 Nomad Tab，理解二者的注册位置差异是进阶的关键。