---
id: "ta-unity-editor"
concept: "Unity编辑器扩展"
domain: "technical-art"
subdomain: "tool-dev"
subdomain_name: "工具开发"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 52.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Unity编辑器扩展

## 概述

Unity编辑器扩展是指通过继承`Editor`、`EditorWindow`、`PropertyDrawer`等Unity提供的特殊基类，在Unity Inspector面板、Project窗口或Scene视图中添加自定义UI和功能的开发技术。这类脚本必须放置在项目的`Editor`文件夹内，Unity会识别该文件夹并确保其中代码仅在编辑器模式下编译，不会被打包到最终发布版本中，从而避免增加运行时体积。

Unity编辑器扩展功能最早随Unity 3.x版本系统化引入，核心API位于`UnityEditor`命名空间下。技术美术人员使用编辑器扩展的根本动机是消除重复性手工操作——例如批量设置材质参数、自动生成骨骼绑定路径、一键检查贴图格式是否符合项目规范等任务，这些工作若完全依赖手动操作，在大型项目中可能消耗数小时甚至数天。

对技术美术而言，编辑器扩展是连接美术资产与程序逻辑的直接手段。它允许美术同学在不接触运行时代码的前提下，通过可视化按钮和参数调节界面完成复杂操作，同时也使工具开发者能够为非程序同学提供防误操作的友好界面，降低项目中因人为失误产生的资产问题。

---

## 核心原理

### Custom Inspector：重写默认检视面板

Custom Inspector通过继承`Editor`类并标注`[CustomEditor(typeof(YourComponent))]`特性来实现。重写`OnInspectorGUI()`方法后，Unity会用自定义绘制逻辑完全替换目标组件在Inspector中的默认显示。最基础的调用是`DrawDefaultInspector()`，它保留原有字段显示并允许在其前后追加自定义按钮或提示信息。

```csharp
[CustomEditor(typeof(MeshBaker))]
public class MeshBakerEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        if (GUILayout.Button("一键烘焙网格"))
        {
            ((MeshBaker)target).BakeMesh();
        }
    }
}
```

`serializedObject`和`SerializedProperty`是Custom Inspector中操作数据的标准路径。相比直接访问目标对象字段，通过`serializedObject.FindProperty("fieldName")`获取属性再调用`EditorGUILayout.PropertyField()`，可以自动支持撤销（Undo）、Prefab覆写标记（Override）和多对象同时编辑，这三个特性在纯反射访问方式下需要手动实现。

### EditorWindow：独立悬浮工具窗口

`EditorWindow`继承自`ScriptableObject`，通过`EditorWindow.GetWindow<T>()`静态方法创建或激活窗口实例。窗口内的绘制逻辑写在`OnGUI()`方法中，该方法在每次窗口需要重绘时被调用。典型用途包括：批量资产处理工具、动画片段管理器、项目规范检查面板。

EditorWindow的`OnEnable()`和`OnDisable()`生命周期方法分别对应窗口打开和关闭时机，适合在此进行数据加载与状态保存。使用`EditorPrefs.SetString()`可以将窗口的用户配置持久化到本地，使工具在重启Unity后仍能记住上次的设置路径或选项状态。

### PropertyDrawer：自定义序列化字段的绘制

`PropertyDrawer`针对特定类型或特定Attribute修饰的字段，覆盖其在所有Inspector中的显示方式。需重写`OnGUI(Rect position, SerializedProperty property, GUIContent label)`和`GetPropertyHeight()`两个方法，后者决定该字段在Inspector中占用的像素高度（默认单行高度为`EditorGUIUtility.singleLineHeight`，值为18像素）。

自定义Attribute配合PropertyDrawer是常见组合，例如定义`[RangeStep(0f, 1f, 0.1f)]`特性，让float字段在Inspector中显示为步进滑块而非默认滑条，从而约束美术同学只能输入0.1的整数倍值，预防材质参数被设置为不规范的小数。

### GUILayout与EditorGUILayout的区别

`GUILayout`是运行时和编辑器通用的布局API，而`EditorGUILayout`仅在编辑器环境下可用，并提供了`ObjectField`、`ColorField`、`CurveField`等专为Unity资产类型设计的字段控件。在`EditorWindow`和`CustomEditor`中应优先使用`EditorGUILayout`，因为它能正确处理`SerializedProperty`并自动集成Undo系统。

---

## 实际应用

**贴图格式批量检查工具**：技术美术常需确认项目内所有UI贴图的压缩格式是否统一为ASTC 6×6。可创建一个`EditorWindow`，通过`AssetDatabase.FindAssets("t:Texture2D", new[]{"Assets/UI"})`获取所有UI目录下的贴图GUID，再用`AssetImporter.GetAtPath()`取得`TextureImporter`对象，读取`textureCompression`和`androidETC2FallbackOverride`等属性并与预设规范比对，将不合规资产列表显示在窗口中并提供一键修复按钮。

**骨骼路径自动重映射**：当美术同学修改角色骨骼层级名称后，动画片段中存储的骨骼路径字符串会失效。通过`EditorWindow`提供新旧骨骼路径的对照输入界面，调用`AnimationUtility.GetCurveBindings(clip)`遍历所有绑定，用`AnimationUtility.SetEditorCurve()`将路径替换写回片段，实现无需重新制作动画的批量修复。

**材质预设快速应用面板**：为Shader参数繁多的材质创建Custom Inspector，将常用材质预设（如"金属高光"、"皮肤次表面"）以下拉菜单形式列出，点击后通过`material.SetFloat()`、`material.SetTexture()`等API批量设置参数组合，同时调用`Undo.RecordObject(material, "Apply Preset")`确保操作可撤销。

---

## 常见误区

**误区一：将编辑器脚本放在非Editor文件夹**  
`UnityEditor`命名空间中的类不允许被打包进最终构建。若将继承`Editor`的脚本放在普通文件夹中，项目在执行Build时会报编译错误，提示找不到`UnityEditor`引用。正确做法是将所有编辑器扩展脚本放入名为`Editor`的文件夹（可嵌套在任意层级的子目录中，如`Assets/Tools/Editor/`）。

**误区二：在OnGUI中执行高耗时操作**  
`OnInspectorGUI()`和`EditorWindow.OnGUI()`在编辑器每次重绘时都会被调用，触发频率远高于预期（用户每次移动鼠标都可能触发重绘）。将`AssetDatabase.FindAssets()`、文件遍历或网络请求等操作直接写在`OnGUI()`中，会导致编辑器严重卡顿。正确做法是将这类操作移至按钮回调、`OnEnable()`或显式触发的刷新方法中，`OnGUI()`只负责绘制已缓存的数据。

**误区三：混淆target与serializedObject的使用场景**  
直接修改`target`（即`(MyComponent)target`）的字段值虽然语法简单，但这种方式绕过了Unity的序列化系统，导致修改不被Undo系统记录，Prefab的Override标记也不会正确显示。涉及数据修改时应始终通过`serializedObject.Update()`、`property.XXXValue = ...`、`serializedObject.ApplyModifiedProperties()`的三步流程操作。

---

## 知识关联

学习Unity编辑器扩展需要具备技美工具开发的基础认知，了解为什么要开发工具以及工具应服务于哪些美术管线环节，这使得自定义Inspector的功能设计不会脱离实际需求。同时，`OnGUI`的即时模式（Immediate Mode）绘制概念与UGUI的保留模式不同，需要重新建立UI绘制的心智模型。

掌握Unity编辑器扩展后，可以进入C#工具开发的更广泛领域，包括使用`AssetDatabase`进行批量资产导入管线定制（`AssetPostprocessor`）、通过`ScriptableObject`设计数据驱动的工具配置系统，以及结合`UIToolkit`（UIElements）构建比传统IMGUI更复杂的工具界面——后者已是Unity 2021 LTS以后官方推荐的编辑器UI构建方式，其以UXML和USS描述界面的方式与Web前端技术栈高度相似。