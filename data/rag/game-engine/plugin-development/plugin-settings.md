---
id: "plugin-settings"
concept: "插件设置"
domain: "game-engine"
subdomain: "plugin-development"
subdomain_name: "插件开发"
difficulty: 2
is_milestone: false
tags: ["配置"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 插件设置

## 概述

插件设置（Plugin Settings）是指在 Godot 引擎中，通过 `EditorPlugin` 将自定义配置项注册到编辑器的 **Editor Settings** 或项目级别的 **Project Settings** 中，使插件的参数可被用户持久化保存和修改的机制。与硬编码常量不同，插件设置让最终用户无需修改源码即可调整插件行为，例如调整自动导入的文件路径、切换调试模式开关或设定默认数值阈值。

该机制源自 Godot 3.x 时代对 `EditorPlugin` 类的扩展，在 Godot 4.x 中进一步规范化，分为两个独立的注册接口：面向当前机器上所有项目的 **编辑器设置**（存储在用户数据目录 `editor_settings-4.tres`）和面向单个项目的 **项目设置**（存储在 `project.godot` 文件中）。

理解这两套系统的区别直接影响插件的可移植性。将敏感路径或机器相关配置错误地写入 `project.godot`，会导致团队协作时其他成员打开项目后出现路径失效问题；反之，将项目级参数写入编辑器设置，则无法通过版本控制共享配置。

---

## 核心原理

### 注册到 Project Settings

在 `EditorPlugin` 的 `_enter_tree()` 生命周期方法中，使用 `ProjectSettings.set_setting()` 写入初始值，再用 `add_property_info()` 声明该键的元数据，即可在 **Project > Project Settings** 界面中显示对应控件。

```gdscript
func _enter_tree() -> void:
    # 仅在键不存在时设置默认值，避免覆盖用户已修改的数值
    if not ProjectSettings.has_setting("my_plugin/tile_size"):
        ProjectSettings.set_setting("my_plugin/tile_size", 64)

    ProjectSettings.add_property_info({
        "name": "my_plugin/tile_size",
        "type": TYPE_INT,
        "hint": PROPERTY_HINT_RANGE,
        "hint_string": "8,512,8"
    })
    ProjectSettings.set_initial_value("my_plugin/tile_size", 64)
```

`set_initial_value()` 标记该键的"出厂默认值"，使 Project Settings 界面能以灰色文字显示默认状态，方便用户识别哪些值已被修改。键名必须包含至少一个 `/` 分隔符，否则 Godot 会拒绝注册并抛出错误。

### 注册到 Editor Settings

`EditorSettings` 单例通过 `EditorPlugin.get_editor_interface().get_editor_settings()` 获取。注册流程与 Project Settings 类似，但存储位置是当前用户的编辑器配置文件，不随项目仓库传播。

```gdscript
func _enter_tree() -> void:
    var es := get_editor_interface().get_editor_settings()
    if not es.has_setting("my_plugin/api_endpoint"):
        es.set_setting("my_plugin/api_endpoint", "https://example.com/api")
    es.add_property_info({
        "name": "my_plugin/api_endpoint",
        "type": TYPE_STRING,
        "hint": PROPERTY_HINT_NONE
    })
```

Editor Settings 中的值可通过连接 `settings_changed` 信号实时响应用户修改，而 Project Settings 则需要主动轮询或在工具脚本中监听 `ProjectSettings` 的变更。

### 清理：_exit_tree 中移除设置

插件禁用时若不移除已注册的键，设置条目将永久残留在用户配置中形成"垃圾数据"。Project Settings 中的键应在 `_exit_tree()` 里调用 `ProjectSettings.clear("my_plugin/tile_size")` 删除；Editor Settings 同理调用 `es.erase("my_plugin/api_endpoint")`。但需注意：若用户已修改过该值，调用 `clear()` 会同时丢失用户的自定义内容，因此部分插件选择仅在首次激活时写入、卸载时保留，这取决于插件的使用场景定义。

---

## 实际应用

**地图生成插件** 需要一个控制噪声种子的整数参数。将 `procedural_gen/default_seed` 注册到 Project Settings，并使用 `PROPERTY_HINT_RANGE` 限定范围为 `0,99999,1`，团队成员可在版本控制中共享同一 `project.godot`，保证生成结果一致。

**资产自动导入插件** 需要指定外部工具的可执行文件路径，该路径因开发者机器而异。将 `asset_importer/tool_path` 注册到 Editor Settings，并设置 `PROPERTY_HINT_GLOBAL_FILE` 作为 hint，Godot 会自动在设置界面渲染文件选择按钮，用户可通过 GUI 浏览本机路径，而无需手动输入字符串。

**调试辅助插件** 同时使用两套系统：将"是否在场景树中显示碰撞层可视化"写入 Editor Settings（个人偏好），将"碰撞层颜色映射表"写入 Project Settings（团队共享规范）。

---

## 常见误区

**误区一：把机器相关路径存入 Project Settings**
`project.godot` 通常被纳入 Git 版本控制。若将本机的 Python 解释器路径或 SDK 绝对路径注册到 Project Settings，其他团队成员拉取代码后会立即出现路径不存在的错误。此类路径必须使用 Editor Settings，其存储文件 `editor_settings-4.tres` 默认不应提交到仓库。

**误区二：忘记 `has_setting()` 检查导致覆盖用户设置**
在 `_enter_tree()` 中直接调用 `set_setting("key", default_value)` 而不先检查键是否存在，会在每次插件加载时（包括编辑器重启时）将用户已修改的值重置回默认值。正确做法是用 `if not ProjectSettings.has_setting("key"):` 或 `if not es.has_setting("key"):` 包裹初始化逻辑。

**误区三：键名不使用分类前缀**
直接使用 `"tile_size"` 这样的扁平键名会导致设置项显示在 Project Settings 的根分类下，与引擎内置项混在一起难以区分，且存在键名冲突风险。Godot 要求键名至少含一个 `/`，约定俗成的做法是以插件名称作为前缀，如 `"my_plugin/tile_size"`，这样所有条目会被自动归入名为 `my_plugin` 的分组折叠显示。

---

## 知识关联

本概念建立在 **插件开发概述** 的基础之上，特别依赖对 `EditorPlugin._enter_tree()` / `_exit_tree()` 生命周期的理解——设置的注册与注销必须严格配对在这两个方法中。掌握 `TYPE_INT`、`TYPE_STRING` 等 Godot 内置类型枚举，以及 `PROPERTY_HINT_RANGE`、`PROPERTY_HINT_GLOBAL_FILE` 等属性提示枚举，是正确调用 `add_property_info()` 字典参数的前提。

插件设置机制与 Godot 的 **资源序列化系统** 紧密相关：Project Settings 最终以 `ConfigFile` 格式写入 `project.godot`，Editor Settings 以 `.tres` 格式写入用户数据目录（Windows 下约为 `%APPDATA%\Godot\editor_settings-4.tres`，Linux 下约为 `~/.config/godot/editor_settings-4.tres`）。了解这两个文件的物理位置，有助于在调试时直接检查设置是否被正确写入，以及在必要时手动重置配置。