---
id: "ta-python-blender"
concept: "Blender Python脚本"
domain: "technical-art"
subdomain: "tool-dev"
subdomain_name: "工具开发"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Blender Python脚本

## 概述

Blender Python脚本是通过Blender内置的`bpy`模块，使用Python语言直接操控Blender软件功能的编程方式。`bpy`模块是Blender暴露给Python的完整API接口，涵盖场景管理、网格操作、材质控制、渲染设置、动画关键帧等几乎所有编辑器功能。自Blender 2.5版本（2010年）起，Blender正式将Python 3作为唯一脚本语言，彻底取代了此前的Blender内部脚本语言，形成了如今稳定的`bpy` API体系。

Blender 2.80版本（2019年）是`bpy` API的重要分水岭，该版本对API进行了大规模重构，引入了`collections`、`eevee`等新模块，同时废弃了大量旧接口。技术美术工程师必须意识到：为Blender 2.79编写的脚本通常无法直接在2.80+版本运行，因为`bpy.context.scene.objects.link(obj)`这类旧式写法已被`bpy.context.collection.objects.link(obj)`所替代。

在技术美术的工具开发场景中，Blender Python脚本的核心价值在于批量处理资产——例如一次性为场景中200个网格对象统一重命名、批量设置UV展开参数或自动化导出FBX文件，将原本数小时的重复操作压缩至数秒完成。

## 核心原理

### bpy模块的三大命名空间

`bpy`模块分为三个最常用的顶层命名空间，各司其职：

- **`bpy.data`**：访问Blender的数据块（Data-Block），包括`bpy.data.meshes`、`bpy.data.materials`、`bpy.data.objects`等。这里存储的是Blender文件（.blend）中的真实数据，与是否在视口中可见无关。
- **`bpy.context`**：访问当前编辑器的上下文状态，如`bpy.context.active_object`获取当前激活物体，`bpy.context.selected_objects`获取所有被选中的物体列表。注意`bpy.context`是只读的反映，不能直接赋值修改。
- **`bpy.ops`**：调用Blender的操作符（Operator），如`bpy.ops.mesh.subdivide(number_cuts=2)`执行细分操作。操作符依赖上下文，在错误的上下文下调用会抛出`RuntimeError: Operator bpy.ops.xxx.poll() failed`错误。

### 物体操作的基本流程

创建并添加一个Cube网格物体的完整代码如下：

```python
import bpy

# 新建网格数据块
mesh = bpy.data.meshes.new("MyCube")
# 新建物体并关联网格
obj = bpy.data.objects.new("MyCube", mesh)
# 将物体链接到当前集合中（2.80+语法）
bpy.context.collection.objects.link(obj)
# 使用bmesh填充几何数据
import bmesh
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=2.0)
bm.to_mesh(mesh)
bm.free()
```

其中`bmesh`是独立于`bpy`的网格编辑模块，专门处理顶点、边、面的几何级操作，拥有`bmesh.ops.create_cube`、`bmesh.ops.extrude_face_region`等专用操作函数。

### 插件的注册机制

Blender插件（Add-on）的本质是一个包含特定元数据字典的Python模块。每个插件文件必须包含名为`bl_info`的字典，以及`register()`和`unregister()`两个函数：

```python
bl_info = {
    "name": "My Tool",
    "author": "Artist",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),  # 最低兼容版本
    "category": "Object",
}

def register():
    bpy.utils.register_class(MyOperator)

def unregister():
    bpy.utils.unregister_class(MyOperator)
```

自定义操作符类必须继承`bpy.types.Operator`，并定义`bl_idname`（格式为`"category.name"`）、`bl_label`和`execute(self, context)`方法。`bl_idname`中的点号分隔了命名空间，例如`"object.my_batch_rename"`将出现在Object分类下。

## 实际应用

**批量重命名材质**：游戏项目中常需将所有材质名称统一添加前缀`M_`，以下代码遍历`.blend`文件中的所有材质并重命名：

```python
import bpy
for mat in bpy.data.materials:
    if not mat.name.startswith("M_"):
        mat.name = "M_" + mat.name
```

**自动化FBX批量导出**：技术美术可以遍历场景中的每个物体，单独选中后调用`bpy.ops.export_scene.fbx()`，并通过`filepath`参数指定以物体名命名的输出路径，实现将100个道具模型一键导出为100个独立FBX文件。

**设置PBR材质节点**：通过`bpy.data.materials["M_Rock"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8`，可以精确控制材质球中Principled BSDF节点的粗糙度参数值为0.8，而无需手动打开材质编辑器。

## 常见误区

**误区一：混淆`bpy.data`与`bpy.context`的用途**。许多初学者尝试用`bpy.context.selected_objects`来处理文件中所有网格，实际上这只返回当前视口中被选中的物体。若需处理.blend文件中的全部物体，应使用`bpy.data.objects`，前者依赖交互状态，后者访问完整数据库。

**误区二：在错误模式下调用操作符**。`bpy.ops.mesh.loop_cut()`必须在编辑模式（Edit Mode）下的活动网格物体上调用，若当前处于物体模式则会报`poll()`失败。正确做法是在调用前使用`bpy.ops.object.mode_set(mode='EDIT')`切换模式，操作完成后再切回`'OBJECT'`模式。

**误区三：直接修改`bpy.context`属性**。`bpy.context.active_object = some_obj`会抛出`AttributeError`，因为`bpy.context`中的大多数属性是只读的运行时映射。要切换激活物体，需使用`bpy.context.view_layer.objects.active = some_obj`，通过`view_layer`层级间接设置。

## 知识关联

学习Blender Python脚本之前，需要掌握技术美术工具开发的基本思维——即识别哪些美术工作流程具有重复性、可参数化，从而确定脚本化的价值目标。没有这一判断能力，编写出的脚本往往解决了不存在的问题。

Blender Python脚本是后续开发完整Blender插件（带UI面板、自定义属性、偏好设置）的直接前置技能。掌握`bpy.types.Panel`面板类的开发后，可在Blender的N面板（侧边栏）中嵌入专属的工具面板，将批量处理功能可视化，供无编程背景的美术人员使用。此外，`bpy`的`bpy.app.handlers`模块提供了事件钩子（如`load_post`、`frame_change_post`），可进一步扩展为响应式的自动化管线工具。