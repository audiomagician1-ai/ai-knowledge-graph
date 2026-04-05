---
id: "editor-scripting-py"
concept: "Python编辑器脚本"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 2
is_milestone: false
tags: ["脚本"]

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


# Python编辑器脚本

## 概述

Python编辑器脚本是指在游戏引擎编辑器环境中运行的Python代码，用于自动化资产处理、批量修改场景对象、生成关卡内容等编辑器内任务。与游戏运行时脚本不同，这类代码仅在编辑器打开时执行，不会被打包进最终游戏。Unreal Engine 5通过`unreal` Python模块暴露编辑器API，Unity则通过`UnityEditor`命名空间下的C# API提供类似功能（Unity官方将其称为Editor Script而非Python，但社区工具如Python for Unity也提供了Python绑定）。

UE5的Python编辑器脚本支持正式引入于Unreal Engine 4.20版本（2018年），该版本通过"Python Editor Script Plugin"插件实现了Python 3.x在编辑器中的嵌入运行。开发者需要在插件管理器中手动启用`Python Editor Script Plugin`才能使用相关功能。Unity Editor Script则以C#为主，但借助第三方包`com.unity.scripting.python`（Python for Unity包）可实现类似工作流。

Python编辑器脚本的核心价值在于它能将原本需要数小时手工操作的批量任务压缩至数秒。例如，为一个包含500个静态网格体的项目统一设置LOD参数，手动操作需要逐一打开每个资产，而一段20行的Python脚本可以在不到1分钟内完成同样的工作。

## 核心原理

### UE5 Python模块结构

UE5的Python编辑器脚本通过内置模块`unreal`访问引擎API。该模块在编辑器启动时自动可用，无需`import`额外安装包，只需`import unreal`即可。核心类包括：

- `unreal.EditorAssetLibrary`：负责资产的加载、保存、复制、删除操作
- `unreal.EditorLevelLibrary`：操作当前关卡中的Actor，例如获取所有Actor列表或修改其Transform
- `unreal.AssetToolsHelpers`：执行资产导入流程，配合`unreal.AutomatedAssetImportData`实现批量导入
- `unreal.SystemLibrary`：提供日志输出功能，`unreal.log()`将信息打印到Output Log窗口

脚本的执行方式有三种：通过UE5菜单栏的`File > Execute Python Script`执行外部`.py`文件；在编辑器内置的Python控制台中直接输入命令；或在项目的`Content/Python`目录下放置`init_unreal.py`文件，该文件会在编辑器每次启动时自动运行。

### 批量资产操作的典型模式

UE5 Python批量操作遵循"获取资产列表→遍历处理→保存"的三步模式。以下是批量修改材质参数的核心代码结构：

```python
import unreal

asset_list = unreal.EditorAssetLibrary.list_assets('/Game/Materials', recursive=True)
for asset_path in asset_list:
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if isinstance(asset, unreal.Material):
        # 修改操作
        unreal.EditorAssetLibrary.save_asset(asset_path)
```

其中`list_assets`的第二个参数`recursive=True`表示递归遍历子文件夹，这是处理大型项目时的常用选项。

### Unity Editor Script的执行机制

Unity Editor Script（C#）必须存放在项目的`Assets/Editor`文件夹或任意子文件夹下，Unity编辑器会自动识别该目录下的脚本并将其编译为仅编辑器可用的程序集。与UE5不同，Unity Editor Script通过`[MenuItem("工具/菜单名")]`特性将函数注册为菜单项，而不是直接执行脚本文件。使用Python for Unity包时，Python脚本同样遵循这一机制，通过`PythonRunner.RunFile()`或`PythonRunner.RunString()`在C#桥接层调用Python代码。

## 实际应用

**批量纹理重新导入（UE5）**：当美术团队更新了数十张纹理文件后，可使用`unreal.AssetToolsHelpers.get_asset_tools().import_assets_automated(import_data)`方法一次性重新导入所有修改过的纹理，并统一设置压缩格式为`TC_BC7`，避免手动逐一设置。

**关卡中静态网格体批量替换**：利用`unreal.EditorLevelLibrary.get_all_level_actors()`获取场景中所有Actor，筛选出`StaticMeshActor`类型后，通过`actor.static_mesh_component.set_static_mesh(new_mesh)`替换指定网格体，实现美术资产迭代时的快速全局更新。

**Unity资产后处理**：在Unity中继承`AssetPostprocessor`类并重写`OnPreprocessTexture()`方法，可在每次导入纹理时自动设置`textureImporter.maxTextureSize = 2048`，确保项目纹理规格统一，无需美术人员记住导入规范。

**自动化关卡数据导出**：通过UE5 Python脚本遍历关卡中所有`PointLight` Actor，将其位置、颜色、强度等属性导出为JSON文件，供关卡设计文档或外部工具使用，整个过程无需打开任何界面。

## 常见误区

**误区1：认为UE5 Python脚本可以在运行时（Runtime）使用**
UE5的`unreal` Python模块仅在编辑器环境下可用，`import unreal`在打包后的游戏中会直接抛出`ModuleNotFoundError`。运行时逻辑必须使用蓝图或C++实现，Python只能操作编辑器内的资产和关卡，这是初学者最常犯的概念混淆。

**误区2：修改Actor属性后忘记调用保存函数**
在UE5 Python中通过`set_editor_property()`修改资产属性后，这些修改仅存在于内存中，必须显式调用`unreal.EditorAssetLibrary.save_asset(asset_path)`或`save_loaded_asset(asset)`才能将修改写入`.uasset`文件。不调用保存函数会导致关闭编辑器后修改全部丢失，且系统不会给出任何警告。

**误区3：在Unity中将Editor Script放在错误目录**
Unity Editor Script如果放在`Assets/Editor`以外的目录（如直接放在`Assets/Scripts`），该脚本会被打包进游戏，导致最终构建失败并报错`UnityEditor namespace is not available at runtime`。`Assets/Editor`路径不是建议，而是Unity硬性规定的编辑器代码隔离机制。

## 知识关联

学习Python编辑器脚本需要先掌握**编辑器扩展概述**中关于编辑器与运行时分离的基本概念，特别是UE5插件系统中"Editor模块"与"Runtime模块"的区别——Python脚本本质上属于Editor模块的职责范围。同时需要了解UE5资产路径的命名规范，即以`/Game/`开头的虚拟路径（对应磁盘上的`Content/`目录），错误的路径格式会导致`list_assets`返回空列表而不是报错，造成难以排查的静默失败。

在掌握Python编辑器脚本的基础操作后，自然过渡到**自动化工具**的构建，即将多个Python脚本组合为具有UI界面的工具，使用`unreal.ToolMenus` API在编辑器菜单栏中注册自定义菜单项，或通过`unreal.EditorUtilityWidgetBlueprint`创建带有按钮和参数输入框的可视化自动化面板，从单次执行脚本升级为可复用的流水线工具。