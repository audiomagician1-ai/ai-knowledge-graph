---
id: "editor-command"
concept: "编辑器命令"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 2
is_milestone: false
tags: ["命令"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 76.3
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

# 编辑器命令

## 概述

编辑器命令（Editor Command）是游戏引擎编辑器扩展系统中一种将用户操作封装为可调用单元的机制，允许开发者通过注册函数并绑定快捷键或工具栏按钮来触发自定义逻辑。与运行时游戏代码不同，编辑器命令仅在编辑器进程中执行，不会打包进最终游戏构建。

在 Unity 引擎中，编辑器命令的核心实现依赖于 `MenuItem` 特性（Attribute），该特性于 Unity 3.x 时代引入，允许在 `Tools`、`Assets`、`GameObject` 等顶级菜单下注册自定义菜单项。在 Unreal Engine 中，对应的机制是通过 `FUICommandInfo` 和 `FUICommandList` 注册命令并绑定快捷键映射集（Input Chord）。无论哪种引擎，编辑器命令的本质都是将一段 C# 或 C++ 函数与一个用户可触发的入口点关联起来。

编辑器命令对工作流自动化至关重要——一个批量重命名资源的命令可以将原本需要数小时的手动操作压缩至几秒钟。掌握命令注册机制是编写任何实用编辑器工具的前提条件。

## 核心原理

### 命令注册机制

在 Unity 中，注册编辑器命令的最基础方式是使用 `[MenuItem("路径/命令名")]` 修饰一个 `static` 方法：

```csharp
using UnityEditor;

public class MyTools
{
    [MenuItem("Tools/清理空对象 %#d")]
    static void CleanEmptyObjects()
    {
        // 命令逻辑
    }
}
```

`MenuItem` 路径中使用正斜杠 `/` 分隔菜单层级，最多支持三级嵌套。路径末尾的 `%#d` 是快捷键描述符——`%` 代表 Ctrl（macOS 上为 Cmd），`#` 代表 Shift，`&` 代表 Alt，后跟具体按键字母。这种内联式快捷键声明是 Unity 命令系统的独特写法，与其他工具框架不同。

`MenuItem` 还可接受第二个布尔参数 `isValidateFunction`，当设为 `true` 时，该方法充当验证函数，返回 `false` 会使菜单项呈灰色不可用状态。验证函数必须与命令函数使用完全相同的菜单路径字符串。

### 快捷键绑定规则

Unity 快捷键系统中，全局快捷键（无需选中特定对象即可触发）通过 `MenuItem` 的路径字符串末尾直接声明；而上下文相关快捷键则需要通过 `Shortcuts` 系统（Unity 2019.1 引入）进行注册，使用 `[Shortcut("工具名/命令名", KeyCode.F5)]` 特性绑定。

Unreal Engine 的快捷键绑定更为复杂：需要在 `FUICommandInfo` 中声明命令描述，在 `FUICommandList` 中将命令绑定到具体的 `Execute`、`CanExecute` 和 `IsChecked` 三个代理函数，最后通过 `FInputBindingManager` 注册到全局输入映射。Unreal 的命令还区分 `EUserInterfaceActionType`：`Button`（普通按钮）、`ToggleButton`（切换按钮）、`RadioButton`（单选按钮）和 `Check`（勾选项），这决定了命令在工具栏和菜单中的视觉呈现方式。

### 工具栏扩展与命令关联

在 Unity 中，将命令添加到工具栏需要借助 `EditorToolbarElement` 系统（Unity 2021.2 引入）。通过继承 `VisualElement` 并添加 `[EditorToolbarElement("唯一ID")]` 特性，可以创建自定义工具栏按钮，并在按钮的点击回调中调用与 `MenuItem` 共享的同一静态方法，从而实现命令逻辑的单点维护。

命令的优先级（Priority）参数控制菜单项在同一级别中的排列顺序：`MenuItem` 的第三个参数接受整数优先级，默认值为 1000，数值越小排列越靠前。当两个命令的优先级相差超过 10 时，Unity 会自动在它们之间插入分隔线，这是控制菜单视觉分组的标准做法。

## 实际应用

**批量资源处理命令**：在大型项目中，美术团队常需要对选中的多个纹理统一修改压缩格式。通过注册 `[MenuItem("Assets/批量转换为ASTC格式")]` 命令，配合 `Selection.GetFiltered<Texture2D>(SelectionMode.Assets)` 获取当前选中资源，可以用不到 30 行代码替代手动逐一修改的流程。

**场景操作命令**：关卡设计师需要频繁对齐物体到地面。注册快捷键 `[MenuItem("GameObject/对齐到地面 %g")]` 后，命令内部执行 `Physics.Raycast` 向下检测地面高度并设置 `transform.position`，将操作从选中-拖拽-精确输入三步压缩为单次快捷键触发。

**条件验证实战**：当批量处理命令的验证函数检测到 `Selection.objects.Length == 0` 时返回 `false`，菜单项自动变灰，避免用户在没有选中任何对象时误触发空操作报错，这比在命令主体内部加判断的用户体验更好。

## 常见误区

**误区一：命令方法不必须是静态的**。`[MenuItem]` 修饰的方法必须是 `static`，因为编辑器命令在无实例上下文的情况下通过类型元数据直接调用。尝试在实例方法上添加 `[MenuItem]` 特性会导致编译期警告并且命令不会被注册，这是初学者最常见的报错原因。

**误区二：快捷键冲突时系统会自动提示**。实际上 Unity 不会在编译或运行时报告快捷键冲突——如果两个 `MenuItem` 声明了相同的快捷键组合，其中一个会被静默覆盖（通常是后加载的）。开发者必须主动在 `Edit > Shortcuts` 面板中检查冲突，或在声明前查阅 Unity 内置快捷键列表。

**误区三：验证函数与命令函数路径"大致相同"即可**。验证函数路径必须与命令函数路径**字符完全一致**，包括大小写和空格。哪怕多一个空格，验证函数也无法关联到对应命令，而且不会有任何错误提示，导致菜单项永远可用，验证逻辑完全失效。

## 知识关联

编辑器命令建立在**编辑器扩展概述**所介绍的编辑器脚本编译分离机制之上——所有注册命令的类必须放置在 `Editor` 文件夹内或使用 `#if UNITY_EDITOR` 宏包裹，才能确保其不被打包进游戏构建。理解这一文件夹约定是命令注册能够正确工作的前置条件。

编辑器命令本身不处理复杂的 GUI 布局，其作用范围是触发逻辑和控制可用状态。若需要在命令触发后弹出参数配置界面，需要结合 `EditorWindow` 创建弹出窗口；若需要在 Inspector 中集成按钮式命令，则需要结合自定义 `Editor` 类的 `OnInspectorGUI` 方法。命令机制本身提供的是统一的入口注册能力，复杂交互界面由 `EditorWindow` 和自定义 Inspector 扩展承接。