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
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 自定义Gizmo

## 概述

自定义Gizmo是指在游戏引擎编辑器的场景视图（Scene View）中，由开发者手动绘制并实现交互逻辑的可视化操控手柄。与引擎内置的位移、旋转、缩放Gizmo不同，自定义Gizmo专门服务于特定组件的参数调整需求，例如用一根可拖动的射线表示探照灯的照射角度，或用一个可缩放的球体表示音频源的衰减半径。其核心价值在于将组件的抽象数值参数转化为场景内可直接操作的三维图形控件，使关卡设计师无需查阅Inspector面板中的数字就能直观地调整组件行为范围。

自定义Gizmo的概念最早在Unity编辑器扩展API中被系统化，通过`OnDrawGizmos`和`OnDrawGizmosSelected`这两个MonoBehaviour回调方法实现基本绘制，而更完整的交互式Gizmo则依赖`Handles`类（Editor专属API）完成。在Unreal Engine中对应功能通过`FComponentVisualizer`类实现，两种引擎的实现路径虽然不同，但核心思想一致：将运行时不可见的编辑辅助图形与鼠标点击、拖拽事件绑定，形成编辑器内的专属交互层。

对游戏工具链而言，自定义Gizmo直接影响关卡设计的迭代效率。一个设计良好的Gizmo可以把原本需要"输入数值→切换视角确认→再次调整"的多步操作压缩为一次鼠标拖拽，对于需要频繁微调碰撞体积、AI感知范围或样条曲线控制点的工作流来说，节省的时间非常可观。

---

## 核心原理

### 绘制层与编辑器事件分离

自定义Gizmo的绘制代码必须置于Editor类或`OnDrawGizmos`回调中，而不能混入运行时逻辑。在Unity中，`Gizmos`类提供的方法（如`Gizmos.DrawWireSphere`、`Gizmos.DrawLine`）仅在编辑器模式下执行，打包后完全剥离，不会产生任何运行时开销。`Handles`类则更进一步，其`Handles.PositionHandle(position, rotation)`方法能返回用户拖拽后的新位置坐标，实现参数的反向写回——这是普通`Gizmos`绘制做不到的。

### HandleUtility与控制ID机制

交互式Gizmo能够正确响应鼠标操作的关键在于控制ID（Control ID）系统。每个可交互的Gizmo元素在绘制前必须通过`GUIUtility.GetControlID(FocusType.Passive)`申请一个唯一ID，系统据此判断当前哪个手柄正在被拖拽。若跳过这一步，多个Gizmo叠加时会出现抢占焦点的混乱行为。`HandleUtility.DistanceToCircle`和`HandleUtility.DistanceToCube`等函数用于计算鼠标与Gizmo几何体的屏幕空间距离，距离阈值通常设定为5像素，低于此值则判定为鼠标悬停。

### 坐标空间变换

Gizmo的绘制坐标默认为世界空间，但组件参数往往储存在局部空间。以一个扇形视野Gizmo为例，AI的视野角度`fieldOfView = 120°`和视野距离`viewDistance = 15f`是局部参数，绘制时需要通过`transform.TransformPoint`将局部坐标转换为世界坐标，而用户拖拽后返回的世界坐标则需要用`transform.InverseTransformPoint`转换回局部坐标才能正确写入组件字段。忽略这一转换会导致当物体发生旋转后，Gizmo的位置与实际参数严重错位。

### Undo/Redo集成

任何会修改组件数据的Gizmo操作必须在赋值前调用`Undo.RecordObject(target, "操作描述字符串")`，否则用户按下Ctrl+Z时无法撤销Gizmo造成的修改。这是自定义Gizmo中最容易被遗漏的步骤，也是导致美术和关卡设计师投诉"撤销不了"的直接原因。

---

## 实际应用

**音频衰减范围Gizmo**：为`AudioSource`组件绘制两个同心球体，内球（黄色）代表`minDistance`，外球（红色渐变）代表`maxDistance`，两个球面均可通过拖拽手柄直接调整对应数值。这是Unity官方Editor扩展文档中的经典示例，用`Handles.RadiusHandle`方法仅需约20行代码即可实现。

**样条曲线控制点编辑**：在赛道编辑工具中，每个样条节点显示为场景内的圆形手柄，切线控制杆以线段延伸显示。设计师可以直接在场景视图中拖动控制点修改曲线形状，而不必在Inspector中手动输入Vector3坐标。Unreal Engine的`FSplineComponentVisualizer`是这一模式的标准实现参考。

**AI感知扇形区域Gizmo**：用`Handles.DrawSolidArc`绘制一个透明扇面，扇面边缘端点配置为可拖拽的方块手柄，分别控制`detectionAngle`和`detectionRange`两个参数。当物体被选中时显示完整扇面（`OnDrawGizmosSelected`），未选中时只显示一条中心轴线（`OnDrawGizmos`），避免场景视图中Gizmo过多导致视觉污染。

---

## 常见误区

**误区一：在`OnDrawGizmos`中直接修改组件数据**  
`OnDrawGizmos`在每次场景视图重绘时都会调用，每秒可能执行数十次。若在此函数中直接对组件字段赋值（而非在检测到拖拽事件后赋值），会导致数据被反复覆盖，Inspector中的手动输入完全失效。正确做法是仅在`EventType.MouseDrag`或`EventType.MouseUp`事件发生时才执行数据写回。

**误区二：混淆`Gizmos`类和`Handles`类的职责**  
`Gizmos`类（命名空间`UnityEngine`）只能绘制，无法获取用户输入，可用于普通MonoBehaviour脚本中；`Handles`类（命名空间`UnityEditor`）既能绘制又能处理交互，但只能在Editor程序集中使用。若在普通MonoBehaviour脚本中引用`Handles`类，打包时会因缺失`UnityEditor`程序集而报错，必须用`#if UNITY_EDITOR`宏包裹相关代码。

**误区三：认为`OnDrawGizmosSelected`只在首次选中时调用一次**  
实际上，只要场景视图处于焦点且对应对象保持选中状态，`OnDrawGizmosSelected`会持续每帧调用。这意味着Gizmo内不应包含任何带副作用的初始化逻辑（如实例化对象、申请资源），所有状态应存储在Editor类的成员字段或序列化组件字段中。

---

## 知识关联

自定义Gizmo建立在编辑器扩展概述所介绍的`Editor`类继承体系之上——只有为组件创建了对应的`[CustomEditor(typeof(MyComponent))]`编辑器类，才能在其中编写`OnSceneGUI`方法来使用`Handles` API实现完整的交互式Gizmo。反过来，Gizmo开发过程中频繁用到的`SerializedObject`/`SerializedProperty`写回机制，也会加深对编辑器序列化系统的理解。

在工具链的更广泛视角下，自定义Gizmo与自定义编辑器窗口（`EditorWindow`）构成两种互补的编辑器扩展形式：前者将交互嵌入场景三维空间，适合需要空间感知的参数；后者提供独立的二维UI面板，适合批量操作和数据概览。掌握自定义Gizmo后，开发者通常会进一步探索Property Drawer（属性抽屉）来完善Inspector端的配套显示，形成"场景内Gizmo + Inspector面板"的完整工具组件。
