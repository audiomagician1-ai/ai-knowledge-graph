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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

自定义编辑器窗口（Custom Editor Window）是指在游戏引擎编辑器环境中，由开发者通过插件或扩展代码自行创建的可停靠、可浮动的 Tab/Panel/Window 界面单元。与引擎内置的"细节面板"或"场景大纲"不同，自定义窗口可以承载完全由开发者定义的 UI 布局、交互逻辑和数据展示，满足项目特定的工作流需求，例如批量资产管理、关卡配置表编辑或角色技能树预览。

在 Unity 编辑器中，`EditorWindow` 类自 Unity 3.x 时代起就是扩展编辑器界面的标准入口；在 Unreal Engine 中，对应机制是基于 Slate UI 框架的 `SDockTab` 注册系统，在 UE4.20 之后还可以通过 `FTabManager` 和 `FGlobalTabmanager` 统一管理标签页的生命周期。两套系统虽然 API 不同，但核心思路一致：先定义窗口类，再向编辑器的标签注册表中登记，最后通过菜单项或快捷键触发打开。

自定义编辑器窗口的价值在于它将重复性手工操作转化为一次性的工具界面。一个典型案例是：美术团队每天需要手动逐一检查数百张贴图的格式合规性，通过自定义窗口可以将这一流程压缩为点击一个按钮并查看结果列表，把原本需要 2 小时的工作缩短至 5 分钟以内。

---

## 核心原理

### 1. 窗口类的声明与生命周期

以 Unity 为例，自定义窗口必须继承自 `UnityEditor.EditorWindow`，并至少实现 `OnGUI()` 方法。窗口的完整生命周期包含以下回调节点：

| 回调方法 | 触发时机 |
|---|---|
| `Awake()` | 窗口对象首次创建时 |
| `OnEnable()` | 窗口变为可见或重新加载时 |
| `OnGUI()` | 每帧绘制 UI 时（与渲染帧同步） |
| `OnDisable()` | 窗口被关闭或隐藏时 |
| `OnDestroy()` | 窗口对象被彻底销毁时 |

`OnGUI()` 基于 Unity 的 **IMGUI（Immediate Mode GUI）**系统工作，每次调用都会重新计算并绘制所有控件，这与 WPF 或 Qt 的保留模式 GUI 不同——窗口内的按钮、标签、滑块等控件没有持久化对象，状态必须由开发者自行维护在字段变量中。

### 2. 窗口的创建与注册

要让窗口出现在编辑器菜单中，需要使用 `MenuItem` 属性标注一个静态工厂方法，并在其中调用 `GetWindow<T>()` 或 `CreateWindow<T>()`：

```csharp
[MenuItem("Tools/我的工具窗口 %#W")]  // Ctrl+Shift+W 快捷键
public static void OpenWindow()
{
    var window = GetWindow<MyToolWindow>("我的工具");
    window.minSize = new Vector2(400, 300);
    window.Show();
}
```

`GetWindow<T>()` 与 `CreateWindow<T>()` 的关键区别在于：前者若已存在同类型窗口则返回已有实例（单例语义），后者每次调用都创建新实例，适合需要同时打开多个独立窗口的场景，例如同时比较两份配置数据。

在 Unreal Engine 中，窗口注册通过 `FTabSpawnerEntry` 完成。开发者需要在模块的 `StartupModule()` 内调用：

```cpp
FGlobalTabManager::Get()->RegisterNomadTabSpawner(
    TabId,
    FOnSpawnTab::CreateRaw(this, &FMyModule::OnSpawnTab)
)
.SetDisplayName(LOCTEXT("TabTitle", "我的工具"))
.SetMenuType(ETabSpawnerMenuType::Hidden);
```

`NomadTab`（游牧标签）表示该窗口不归属于任何特定布局区域，可自由停靠到编辑器的任意 DockArea 中。

### 3. 布局与停靠行为控制

Unity 的 `EditorWindow` 支持通过 `DockArea` 系统实现标签页停靠，但这一行为由用户拖拽控制，代码层面只能通过 `wantsMouseMove`、`autoRepaintOnSceneChange` 等属性影响刷新频率，无法强制指定停靠位置。

Unreal 的 `SDockTab` 提供了更细粒度的控制。`ETabRole` 枚举定义了三种窗口角色：
- `PanelTab`：可停靠到现有标签组，行为类似"细节面板"
- `NomadTab`：独立浮动，不参与布局序列化
- `MajorTab`：顶层窗口，拥有独立标题栏，如"蓝图编辑器"整体窗口

选择错误的 `ETabRole` 会导致窗口在编辑器重启后丢失位置记录，或与其他停靠区域发生布局冲突。

---

## 实际应用

**批量资产重命名工具**：项目组经常需要按命名规范批量重命名模型文件。通过自定义窗口，可以在左侧列表展示当前选中的资产原名，在右侧输入框设置前缀/后缀规则，点击"预览"按钮后在中间区域显示重命名结果对比，确认无误后执行。整个工具的 `OnGUI()` 函数使用 `EditorGUILayout.BeginHorizontal()` 将界面切分为三栏，配合 `GUILayout.Width()` 控制各栏宽度比例。

**关卡事件配置面板**：策划人员需要为关卡内的触发器配置多条事件链，通过继承 `EditorWindow` 并序列化一个 `ScriptableObject` 数据容器，可以将树形结构的事件逻辑可视化地呈现在自定义窗口中，并通过 `AssetDatabase.SaveAssets()` 持久化到磁盘，避免直接操作 YAML 场景文件。

---

## 常见误区

**误区一：在 `OnGUI()` 中执行耗时操作**
`OnGUI()` 在编辑器活跃期间每帧都会调用（通常 60fps），如果在其中直接遍历项目内所有资产文件，会导致编辑器严重卡顿。正确做法是在 `OnEnable()` 或按钮点击回调中一次性缓存数据，`OnGUI()` 只负责读取缓存并绘制。

**误区二：混淆 `GetWindow` 的单例行为**
开发者有时期望每次点击菜单项都弹出一个"新鲜"的窗口，却发现数据残留自上次操作。原因是 `GetWindow<T>()` 默认返回已存在的实例，窗口字段数据未被重置。如果确实需要每次打开时重置状态，应在 `OnEnable()` 中初始化所有字段，而不是依赖 `Awake()`，因为停靠的窗口在编辑器重启后会触发 `OnEnable()` 而不会重新触发 `Awake()`。

**误区三：忽略 `titleContent` 设置导致标签名显示异常**
直接向 `GetWindow()` 传入字符串参数虽然可以设置标题，但无法配置标签图标。Unity 5.1 之后推荐使用 `titleContent = new GUIContent("窗口名", iconTexture)` 进行设置，否则在密集停靠多个标签时，纯文字标签会因宽度不足被截断，降低工具的可用性。

---

## 知识关联

学习自定义编辑器窗口需要先掌握**编辑器扩展概述**中关于 `MenuItem` 属性注册机制和编辑器脚本与运行时脚本隔离（放置在 `Editor` 文件夹内）的规则，否则窗口类会被错误地编译进运行时构建包，导致发布版本体积增大或编译报错。

掌握自定义编辑器窗口之后，下一步学习**内容浏览器扩展**时会更加顺畅：内容浏览器的右键菜单扩展（`AssetTypeActions`）和过滤器扩展都需要通过类似的注册-回调模式接入编辑器，而在右键菜单操作触发后弹出的确认对话框或参数配置界面，正是利用 `EditorWindow.GetWindow<T>()` 或 `ScriptableWizard.DisplayWizard()` 来实现的——后者本质上也是 `EditorWindow` 的一个预制子类。