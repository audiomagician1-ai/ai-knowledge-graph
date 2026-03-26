---
id: "editor-config"
concept: "编辑器配置"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 2
is_milestone: false
tags: ["配置"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
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



# 编辑器配置

## 概述

编辑器配置（Editor Configuration）是虚幻引擎中控制编辑器行为的INI文件系统，其核心文件为 `DefaultEditor.ini`，存放于项目的 `Config/` 目录下。该文件遵循虚幻引擎标准的键值对格式，通过 `[Section]` 段落分隔不同功能模块的设置，并支持 `+`（追加）、`-`（删除）、`.`（清空后追加）等前缀操作符来精确控制数组型配置项的合并行为。

这套配置机制从虚幻引擎3时代延续至今，在UE4和UE5中得到进一步标准化。与运行时配置文件（如 `DefaultGame.ini`）不同，`DefaultEditor.ini` 中的设置仅在编辑器环境中生效，打包后的游戏不会读取该文件，这使得开发团队可以在不影响最终产品的前提下自由调整编辑工具的行为。

编辑器配置的重要性体现在团队协作场景中：将 `DefaultEditor.ini` 纳入版本控制系统（如Git或Perforce）后，所有开发人员打开项目时会自动获得统一的编辑器布局、插件激活状态和工具设置，避免了"在我机器上能运行"的配置漂移问题。

## 核心原理

### INI文件的层级合并机制

虚幻引擎的INI系统采用多层级合并策略，最终生效的配置由以下层级叠加而成（优先级从低到高）：引擎基础配置（`Engine/Config/BaseEditor.ini`）→ 项目配置（`Config/DefaultEditor.ini`）→ 平台专属配置 → 用户本地配置（`Saved/Config/Windows/Editor.ini`）。项目级别的 `DefaultEditor.ini` 是团队共享的关键文件，而 `Saved/` 目录下的本地配置则存储每个开发者的个人偏好，通常应被 `.gitignore` 排除在版本控制之外。

理解这一层级关系后，可以有意识地将配置写入正确的层级。例如，若某项设置写入 `Saved/Config/Windows/Editor.ini`，它会覆盖 `DefaultEditor.ini` 中的同名项，但这种覆盖只在当前开发者的机器上有效。

### 通过C++注册自定义配置项

在扩展编辑器时，开发者可以通过 `UPROPERTY` 宏的 `config` 说明符将自定义设置与INI文件绑定。具体做法是在 `UDeveloperSettings` 的子类中声明属性：

```cpp
UCLASS(config=Editor, defaultconfig)
class UMyEditorSettings : public UDeveloperSettings
{
    GENERATED_BODY()
public:
    UPROPERTY(config, EditAnywhere, Category="My Tool")
    bool bEnableCustomFeature = true;

    UPROPERTY(config, EditAnywhere, Category="My Tool")
    int32 MaxIterationCount = 50;
};
```

其中 `config=Editor` 指定该类的属性序列化到 `DefaultEditor.ini`，`defaultconfig` 说明符确保设置保存到项目的 `Config/` 目录而非 `Saved/` 目录。完成注册后，这些属性会自动出现在编辑器的"项目设置（Project Settings）"面板中，用户的修改会实时写回INI文件。

### 常用配置段落与键值

`DefaultEditor.ini` 中几个高频使用的段落如下：

- **`[/Script/UnrealEd.EditorPerformanceSettings]`**：控制编辑器实时渲染性能，例如 `bShowFrameRateAndMemory=True` 可在视口右上角显示帧率与内存占用。
- **`[/Script/UnrealEd.LevelEditorViewportSettings]`**：存储视口相关设置，如 `bLevelStreamingVolumePrevis=False` 控制关卡流送体积预览。
- **`[CoreRedirects]`**：此段落在 `DefaultEngine.ini` 中更常见，但编辑器相关的类重定向也可写于 `DefaultEditor.ini`，格式为 `+ClassRedirects=(OldName="/Script/OldModule.OldClass", NewName="/Script/NewModule.NewClass")`。

## 实际应用

**统一团队的资产命名验证插件配置**：假设团队开发了一个强制资产命名规范的编辑器插件 `AssetNamingEnforcer`，插件内的设置类继承 `UDeveloperSettings` 并指定 `config=Editor`。将以下内容提交到 `DefaultEditor.ini`：

```ini
[/Script/AssetNamingEnforcer.AssetNamingSettings]
bEnforceNamingOnImport=True
+ForbiddenPrefixes=BP_Bad
+ForbiddenPrefixes=OLD_
```

所有克隆该仓库的开发者打开项目后，插件会自动以这套规则运行，无需每人手动配置。

**禁用编辑器启动时的烦人提示**：在大型团队项目中，某些教程气泡（Tutorial Overlay）会频繁弹出。在 `DefaultEditor.ini` 中添加：

```ini
[/Script/IntroTutorials.TutorialStateSettings]
TutorialsProgress=(Tutorial="/Engine/Tutorial/...", bUserDismissed=True)
```

可以全局关闭指定教程提示，节省每位新成员的配置时间。

## 常见误区

**误区一：将个人偏好写入 `DefaultEditor.ini` 并提交**

部分开发者会直接在编辑器UI中修改设置后提交 `DefaultEditor.ini`，但这往往包含了个人视口布局（`EditorLayout`）或调试窗口位置等个人化配置。正确做法是仅提交团队约定的、对所有人有意义的配置项，个人偏好应留在 `Saved/Config/` 目录中。区分方法是查看修改项所属的配置段落，凡是与 UI布局、窗口位置相关的段落（如 `[MainFrame.MainFrameActions]`）通常不应提交。

**误区二：混淆 `config=Editor` 与 `config=EditorPerProjectUserSettings`**

`config=EditorPerProjectUserSettings` 对应的是 `DefaultEditorPerProjectUserSettings.ini`，该文件专门存储"按项目、按用户"的偏好，例如某个用户在特定项目中选择的默认材质域。若将本应写入此文件的设置错误地指定为 `config=Editor`，设置会被提交到版本控制，强制覆盖其他团队成员的个人选择，造成不必要的冲突。

**误区三：直接手动编辑INI文件后期望热重载**

`DefaultEditor.ini` 的修改通常需要重启编辑器才能完全生效。对于通过 `UDeveloperSettings` 注册的配置项，虽然在"项目设置"面板中修改可以触发 `PostEditChangeProperty` 回调实现部分热更新，但直接修改磁盘上的INI文件后，编辑器不会监听文件变化，需要手动重启。这与蓝图或C++的热重载机制有本质区别。

## 知识关联

学习编辑器配置需要具备编辑器扩展概述中介绍的模块系统知识，特别是了解编辑器模块（`Editor` 模块类型）如何与运行时模块分离，才能理解为何 `DefaultEditor.ini` 中的设置不进入打包产物。

编辑器配置与"细节面板自定义（Detail Panel Customization）"有直接交互：当你通过 `UDeveloperSettings` 暴露配置项到"项目设置"面板时，可以进一步使用 `IDetailCustomization` 为这些属性编写自定义显示逻辑，提供下拉枚举选择器或实时验证反馈等增强体验。此外，编辑器配置中注册的设置值可以在 `FEditorDelegates::OnEditorInitialized` 等编辑器生命周期委托回调中读取，驱动插件的初始化行为。