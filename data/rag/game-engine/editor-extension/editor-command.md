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
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 编辑器命令

## 概述

编辑器命令（Editor Commands）是游戏引擎编辑器扩展系统中允许开发者将自定义操作注册为可调用指令的机制。在 Unity 中，编辑器命令通常通过 `MenuItem` 特性（Attribute）注册到菜单栏，而在 Godot 中则通过 `EditorPlugin` 的 `add_tool_menu_item()` 方法注册。每条命令本质上是一个绑定了触发入口（菜单项、快捷键或工具栏按钮）的函数调用链。

这一机制最早在商业级游戏引擎的编辑器工具链中普及，Unity 在 3.x 版本时期引入了基于特性标注的 `MenuItem` API，让开发者无需修改引擎源码就能向编辑器顶部菜单注入自定义功能。这对团队工作流改造至关重要——例如将资产批量命名、场景预处理等重复操作封装成一键命令，可将耗时数分钟的手工操作压缩至毫秒级触发。

编辑器命令区别于运行时代码的关键在于它们只在编辑器环境中编译和执行。Unity 要求所有编辑器命令脚本放置在 `Editor` 文件夹内，否则会被打包进最终构建产物，导致包体冗余甚至运行时报错。

## 核心原理

### 命令注册机制

在 Unity 中，`[MenuItem("Tools/MyCommand")]` 特性将静态方法注册为菜单项。该特性接受三个参数：菜单路径字符串、是否为验证函数的布尔值（`isValidateFunction`），以及控制菜单项显示优先级的整型数（`priority`，默认值为 1000，数值越小越靠上）。以下是一个完整示例：

```csharp
[MenuItem("Tools/Batch Rename", false, 10)]
static void BatchRename() {
    // 执行批量重命名逻辑
}

[MenuItem("Tools/Batch Rename", true)]
static bool BatchRenameValidate() {
    return Selection.gameObjects.Length > 0;
}
```

验证函数（Validate Function）与主函数共享同一菜单路径，但第二个参数传入 `true`。当验证函数返回 `false` 时，对应菜单项会显示为灰色不可点击状态，这是编辑器命令实现"上下文感知"的核心手段。

### 快捷键绑定

Unity 的 `MenuItem` 路径字符串支持在末尾追加快捷键声明，语法为 `%`（Ctrl/Cmd）、`#`（Shift）、`&`（Alt）与字母的组合。例如 `"Tools/Save Layout %#s"` 会将该命令绑定到 `Ctrl+Shift+S`。需要注意的是，快捷键与原生编辑器快捷键冲突时，自定义绑定会被静默忽略而非报错，开发者必须手动测试冲突情况。

在 Unreal Engine 中，命令快捷键通过 `UI_COMMAND` 宏注册，该宏在 `Commands.cpp` 文件中声明，并与 `FUICommandInfo` 结构体绑定。Unreal 的命令系统支持多输入上下文（Input Context），同一快捷键在不同编辑器面板中可触发不同命令。

### 工具栏按钮集成

工具栏按钮是编辑器命令的第三种触发入口，相比菜单项有更高的可见性。在 Unity 中，通过继承 `EditorToolbarElement` 并标注 `[EditorToolbarElement("MyTool/Button")]` 特性可创建自定义工具栏元素（该 API 在 Unity 2021.2 版本引入）。工具栏按钮与菜单命令可以共享同一个底层静态方法，从而实现"一个操作多个入口"的设计。

Godot 4.x 中，`add_control_to_container()` 方法可将自定义 `Button` 控件插入编辑器的 `CONTAINER_TOOLBAR` 区域，按钮的 `pressed` 信号连接到对应命令函数，本质上与 `add_tool_menu_item()` 调用的是同一业务逻辑。

## 实际应用

**资产批处理命令**：美术团队常将贴图压缩格式批量修改封装为编辑器命令。一个典型实现是注册 `"Assets/Force Compress Selected Textures %&t"` 菜单项，配合验证函数检测当前选中对象是否含有 `Texture2D` 类型资产，仅在条件满足时激活命令，避免误操作。

**场景工具命令**：关卡设计师需要频繁对齐物体到地面，可以注册 `"GameObject/Snap To Ground %g"` 命令，在命令内通过 `Physics.Raycast` 向下投射射线并修改选中物体的 `Transform.position.y`，整个操作绑定快捷键后可在不打断鼠标操作的情况下完成。

**CI/CD 流水线命令**：命令行触发编辑器命令是自动化构建的常用手段。Unity 支持通过 `-executeMethod ClassName.MethodName` 参数在无头模式（headless mode）下执行静态编辑器方法，使得打包、资产导出等命令可集成到 Jenkins 或 GitHub Actions 流水线中。

## 常见误区

**误区一：将编辑器命令方法定义为实例方法**。`[MenuItem]` 标注的方法必须是 `static`（静态方法），否则 Unity 会在编译期抛出 `MenuItem method must be static` 错误。初学者常因习惯写实例方法而忽略这一约束，导致菜单项无法显示。

**误区二：忽略验证函数的性能影响**。验证函数在编辑器每次重绘菜单时都会被调用，而不是只在菜单打开时调用一次。如果在验证函数内执行 `FindObjectsOfType<T>()` 等开销较大的操作，会导致编辑器卡顿。正确做法是在验证函数中只检查 `Selection` 或缓存的轻量状态，将重量级查询移入命令主体函数。

**误区三：混淆 `MenuItem` 路径中的分隔符规则**。路径字符串中 `/` 表示子菜单层级，但 Unity 不允许在 `Assets` 和 `GameObject` 之外的顶级菜单直接注册一级菜单项——尝试注册 `"MyMenu"` 而非 `"MyMenu/Command"` 会导致菜单项静默失败不显示。

## 知识关联

编辑器命令是在掌握「编辑器扩展概述」（了解 `Editor` 文件夹隔离原则和 `UnityEditor` 命名空间基础）之后自然延伸的第一个实用工具。命令注册的静态方法写法是后续学习 `EditorWindow`（自定义窗口面板）的前置实践——`EditorWindow.GetWindow<T>()` 通常就是在 `MenuItem` 注册的命令中被调用，作为打开自定义面板的入口。此外，命令的验证函数模式与 `Selection` API 密切配合，为进一步学习基于选中对象的自定义检视面板（Custom Inspector）提供了上下文感知的设计思路。
