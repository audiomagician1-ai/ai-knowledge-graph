---
id: "gizmo-custom"
concept: "自定义Gizmo"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 3
is_milestone: false
tags: ["交互"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 自定义Gizmo

## 概述

自定义Gizmo（编辑手柄）是游戏引擎编辑器中一种可在场景视口（Scene View）内直接交互的可视化控件，允许开发者为自定义组件绘制专属图形并响应鼠标拖拽、点击等操作，从而在不打开属性面板的情况下直接在3D/2D空间中修改组件数据。与只读的 `OnDrawGizmos` 调试绘制不同，自定义Gizmo同时承担**视觉反馈**与**输入处理**两项职责。

在Unity引擎的历史演进中，早期版本（Unity 4.x 及之前）只提供 `Gizmos` 静态类用于调试绘制，开发者若想实现交互必须手写大量射线检测与句柄变换代码。Unity 5.0 引入 `Handles` API 并将其标准化，使得绘制带交互的手柄成为官方支持的工作流。Unreal Engine 则通过 `FEdMode` 和 `UPrimitiveComponent::GetEditorVisualizationComponent()` 体系实现同等能力。

自定义Gizmo的核心价值在于**减少设计师在属性面板与场景视图之间的上下文切换**。例如，一个自定义的视野角（Field of View）Gizmo可以直接在场景中展示扇形锥体并允许拖拽边缘修改角度，比在Inspector中输入数字直观得多，显著降低关卡设计迭代时间。

---

## 核心原理

### Unity中的 `Handles` API 与编辑器生命周期

自定义Gizmo的代码必须放置在 `Editor` 文件夹内，并通过 `[CustomEditor(typeof(MyComponent))]` 特性绑定目标组件。实际绘制发生在重写的 `OnSceneGUI()` 方法内，该方法在每次场景视口重绘时被调用（帧率与编辑器刷新率一致，通常为每秒数十次）。

```csharp
[CustomEditor(typeof(PatrolAgent))]
public class PatrolAgentEditor : Editor
{
    void OnSceneGUI()
    {
        PatrolAgent agent = (PatrolAgent)target;
        EditorGUI.BeginChangeCheck();
        Vector3 newPos = Handles.PositionHandle(agent.patrolTarget, Quaternion.identity);
        if (EditorGUI.EndChangeCheck())
        {
            Undo.RecordObject(agent, "Move Patrol Target");
            agent.patrolTarget = newPos;
        }
    }
}
```

`EditorGUI.BeginChangeCheck()` / `EndChangeCheck()` 配对检测值是否被用户修改，只有在发生修改时才调用 `Undo.RecordObject`，避免每帧写入撤销历史导致内存膨胀。

### 坐标空间变换：`Handles.matrix`

所有 `Handles` 绘制调用默认在**世界空间**下进行。若需要在对象本地空间绘制（例如绘制相对于骨骼的偏移球体），需在绘制前设置：

```csharp
Handles.matrix = target.transform.localToWorldMatrix;
```

此后所有坐标输入均视为本地空间坐标，`Handles` 内部乘以该矩阵后转换为世界空间绘制。忘记此步骤会导致Gizmo在对象旋转时"飘移"到错误位置——这是初学者最常见的视觉错误之一。

### 控件ID与热控件系统（Hot Control）

Unity的Handles交互依赖`GUIUtility.hotControl`机制。每个可交互手柄通过 `GUIUtility.GetControlID(FocusType.Passive)` 申请唯一ID。当用户按下鼠标时，系统将该ID写入 `GUIUtility.hotControl`，后续的 `MouseDrag` 和 `MouseUp` 事件只会路由给热控件拥有者，防止多个重叠Gizmo同时响应同一次拖拽。自定义交互式Gizmo（非使用内置 `Handles.PositionHandle` 等预制件时）必须手动管理这套ID系统，否则点击穿透问题无法解决。

### 颜色、透明度与深度遮挡

`Handles.color` 接受 `Color` 结构体，Alpha值小于1时Gizmo呈半透明。Unity编辑器中Gizmo绘制**不参与深度缓冲测试**（ZTest Always），这意味着Gizmo会穿透场景几何体显示，这是设计上的有意选择——确保编辑手柄永远可见。如需模拟遮挡效果，开发者需分两次绘制：先用 `Handles.zTest = CompareFunction.LessEqual` 绘制不被遮挡部分（实线），再用 `CompareFunction.Greater` 绘制被遮挡部分（虚线或低饱和度色）。

---

## 实际应用

**AI巡逻路径编辑器**：为 `PatrolAgent` 组件绘制路径折线，每个路径点显示为可拖拽的球形手柄（`Handles.SphereHandleCap`，半径建议取 0.3~0.5 世界单位以便点击），路径线段用 `Handles.DrawAAPolyLine`（线宽2.0f）连接，选中某节点后高亮为黄色，其余保持蓝色。这样关卡设计师无需逐一展开 Inspector 数组元素即可调整全部路径点。

**音频触发区域可视化**：为 `AudioTriggerZone` 绘制一个可缩放的球形范围Gizmo，使用 `Handles.RadiusHandle` 返回新半径值，配合 `Handles.DrawWireArc` 在X/Y/Z三个平面各绘制一圈圆弧表示完整球体。当组件 `enabled` 为false时，将 `Handles.color` 的Alpha设为0.3以示禁用状态。

**摄像机视锥预览**：利用 `Handles.DrawCamera` 或手动计算四个近平面顶点后调用 `Handles.DrawLines`，实时展示当前FOV（如60°）对应的视锥形状，并在顶部放置 `Handles.ScaleValueHandle` 让设计师直接拖拽改变FOV数值。

---

## 常见误区

**误区1：在 `OnDrawGizmos` 中实现交互**
`MonoBehaviour.OnDrawGizmos` 是运行时与编辑器均可调用的方法，仅支持 `Gizmos` 静态类（绘制球、线、图标），**完全不支持 `Handles` API 也不处理鼠标事件**。交互式Gizmo必须且只能在 `Editor` 子类的 `OnSceneGUI()` 中实现。混淆这两个方法会导致编译错误（`Handles` 类在非编辑器程序集中不存在）或功能完全失效。

**误区2：每帧调用 `Undo.RecordObject` 而不判断值是否变化**
不使用 `BeginChangeCheck`/`EndChangeCheck` 包裹，直接在每次 `OnSceneGUI` 调用时记录撤销，会导致撤销栈以60fps速度堆积空记录，按下Ctrl+Z时需要撤销数百步才能回到上一个有意义的状态。正确做法是检测到值真正改变后才调用一次 `RecordObject`。

**误区3：忘记 `serializedObject.ApplyModifiedProperties()` 导致修改不持久化**
当Gizmo通过 `SerializedProperty` 路径修改数据时（而非直接赋值给 `target`），若省略 `ApplyModifiedProperties()` 调用，修改只存在于序列化缓冲区中，保存场景后数据丢失。直接赋值给 `target` 字段时则通过 `Undo.RecordObject` 路径持久化，两种方式不可混用。

---

## 知识关联

**前置概念**：编辑器扩展概述中介绍的 `CustomEditor` 特性、`Editor` 基类生命周期（`OnInspectorGUI`、`OnEnable`）以及 Unity 的编辑器程序集隔离规则（`#if UNITY_EDITOR` 或 `Editor` 文件夹）是实现自定义Gizmo的必要基础——不了解编辑器类只能在编辑器程序集中存在这一规则，将导致发布版本出现编译错误。

**延伸方向**：掌握自定义Gizmo后，可进一步研究 **EditorTool API**（Unity 2019.1引入，`EditorTool` 基类），它将Gizmo逻辑与工具栏按钮集成，支持在不选中对象时激活特定手柄工具，是自定义Gizmo能力的超集。此外，Unreal Engine中与之对应的技术路线是实现 `FEdMode` 并重写 `Render()` 与 `HandleClick()` 方法，核心的坐标空间管理和热控件概念与Unity版本高度相似。