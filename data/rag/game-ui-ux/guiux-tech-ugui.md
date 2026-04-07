# UGUI（Unity）

## 概述

UGUI（Unity GUI）是Unity Technologies于2014年随Unity 4.6版本正式内置的保留模式（Retained Mode）UI框架，用以取代自Unity 3.x时代沿用的即时模式UI系统IMGUI。IMGUI基于`OnGUI()`回调，每帧执行一次完整的布局与绘制过程，无法被美术人员在编辑器内直接操作；UGUI则将每一个UI控件表达为场景中的GameObject，配合专用的`RectTransform`组件实现2D矩形布局，并通过`CanvasRenderer`参与Unity的渲染管线。

UGUI的官方核心文档《Unity Manual: UI System》（Unity Technologies, 2014）将其设计目标定义为：在同一套框架内同时支持**屏幕空间HUD**、**世界空间3D UI**与**编辑器工具UI**三类场景，并通过Canvas的渲染模式切换来统一实现。相比同期竞争方案NGUI（由Tasharen Entertainment开发，2012年发布），UGUI将合批逻辑直接集成进引擎底层，避免了NGUI依赖Atlas手动管理的碎片化工作流。

值得注意的是，UGUI与Unity新一代UI工具包UI Toolkit（原UIElements，Unity 2019.1引入编辑器，Unity 2021.2扩展至运行时）共存于当前Unity生态中。UI Toolkit采用CSS-like的USS样式表与UXML结构描述，更接近Web前端范式；而UGUI在2024年的Unity调查数据中仍占运行时UI使用率的约70%，是绝大多数商业移动游戏项目的首选方案（Unity Technologies, 2024 Unity Gaming Report）。

---

## 核心原理

### Canvas：渲染根节点与批次管理

所有UGUI可见元素必须作为挂载了`Canvas`组件的GameObject的**直接或间接子节点**才能进入渲染流程。Canvas向Unity渲染器提交的并非逐对象DrawCall，而是经过**几何合批（Geometry Batching）**后的顶点缓冲区。Canvas的三种渲染模式在底层实现上存在本质差异：

- **Screen Space - Overlay**：Canvas几何体由专属的Overlay摄像机渲染，永远绘制在所有摄像机输出之上，渲染顺序由`sortingOrder`控制，不参与深度测试。
- **Screen Space - Camera**：Canvas平面被放置于指定摄像机前方的`planeDistance`处，可受摄像机的Projection矩阵影响，支持透视畸变，适合制作3D风格菜单。
- **World Space**：Canvas作为普通3D平面对象存在，可被场景摄像机从任意角度捕捉，常用于血条、NPC头顶对话框等附着于角色的UI元素。

Canvas内部维护一套**Dirty标记机制**：每当子节点的顶点数据（位置、颜色、UV）、材质引用或布局参数发生变化时，受影响的Canvas会被标记为Dirty，并在当前帧的`LateUpdate`阶段由`Canvas.willRenderCanvases`事件触发重建（Rebuild）。重建过程分为**Layout Rebuild**（重新计算RectTransform尺寸位置）与**Graphic Rebuild**（重新生成顶点网格）两个独立阶段，可通过`CanvasUpdateRegistry`的源码观察其调度顺序（Unity Technologies, open source uGUI repository, github.com/Unity-Technologies/uGUI）。

**嵌套子Canvas（Nested Canvas）**是UGUI性能优化的核心手段：在GameObject层级中将频繁动画或持续更新的UI元素（例如每秒刷新的计数器、持续播放的粒子化UI特效）放入独立的子Canvas，可使该子Canvas的Dirty传播被父Canvas隔断，避免静态背景元素被动触发重建。但子Canvas会打断父Canvas的合批，形成额外DrawCall，因此需要在**更新频率**与**DrawCall数量**之间权衡。

### RectTransform：锚点-轴心点双参数布局系统

`RectTransform`继承自`Transform`，在后者的3D变换基础上增加了专门服务于矩形布局的参数集。理解RectTransform的关键在于区分两套坐标参考系：

**锚点（Anchor）**：`anchorMin`和`anchorMax`均为`Vector2`，取值范围\[0, 1\]，表示相对于**父RectTransform矩形**的归一化比例位置。当`anchorMin == anchorMax`时，锚点退化为单点，此时`anchoredPosition`表示该元素Pivot到锚点的像素偏移，`sizeDelta`直接等于元素的宽高；当`anchorMin != anchorMax`时，锚点展开为一个锚点框（Anchor Box），`sizeDelta`表示元素四边相对于锚点框对应边的**差值**（正值向外扩张，负值向内收缩）。

$$\text{elementWidth} = (\text{anchorMax}.x - \text{anchorMin}.x) \times \text{parentWidth} + \text{sizeDelta}.x$$

$$\text{elementHeight} = (\text{anchorMax}.y - \text{anchorMin}.y) \times \text{parentHeight} + \text{sizeDelta}.y$$

例如：一个设置为全屏拉伸（`anchorMin=(0,0)`，`anchorMax=(1,1)`）、`sizeDelta=(-40, -40)`的Panel，其实际宽度等于父容器宽度减去40像素，高度同理，从而在任意分辨率下保持固定边距——这是移动游戏适配安全区（Safe Area）时常用的参数配置。

**轴心点（Pivot）**同样为`Vector2`，取值范围\[0, 1\]，决定三件事：①旋转与缩放的原点；②`anchoredPosition`偏移的计算起点；③`SetNativeSize()`等API调整尺寸时的固定参考点。将一个血条的Pivot设为`(0, 0.5)`（左侧中点），再通过修改`sizeDelta.x`来改变血条长度，可实现从左向右收缩的效果，无需额外计算位置偏移。

### EventSystem：输入路由与射线检测

`EventSystem`是UGUI输入处理的调度中心，每个场景中有且仅应存在一个EventSystem GameObject。其工作流程为：

1. **Input Module**（`StandaloneInputModule`或`TouchInputModule`）每帧轮询Unity的Input系统，将原始输入（鼠标位置、触摸坐标、手柄轴值）封装为`PointerEventData`。
2. **Raycaster**组件（`GraphicRaycaster`对应Canvas，`PhysicsRaycaster`对应3D碰撞体，`Physics2DRaycaster`对应2D碰撞体）从当前输入坐标向场景发射射线，收集命中结果列表。
3. EventSystem根据`sortingLayer`、`sortingOrder`与`depth`对命中列表排序，找到最优先的接收对象，按照`IPointerDownHandler`、`IDragHandler`、`IPointerClickHandler`等接口协议分发事件。

`GraphicRaycaster`的`Blocking Mask`属性可配置哪些物理层会遮挡UI射线，`Ignore Reversed Graphics`选项决定是否忽略背面朝向摄像机的UI元素——这两个参数在3D World Space Canvas中尤为重要，错误配置会导致UI在角色遮挡后仍可被点击。

---

## 关键方法与公式

### Canvas Scaler的屏幕适配模式

`CanvasScaler`组件是UGUI解决多分辨率适配的核心工具，提供三种缩放模式：

- **Constant Pixel Size**：UI元素保持设计时的像素尺寸不随屏幕分辨率变化，适合PC端以像素密度固定的场景。
- **Scale With Screen Size**：最常用模式。指定一个**Reference Resolution**（如1080×1920），实际缩放因子由以下公式计算：

$$\text{scaleFactor} = \text{lerp}\!\left(\frac{W_{\text{screen}}}{W_{\text{ref}}},\ \frac{H_{\text{screen}}}{H_{\text{ref}}},\ \text{matchWidthOrHeight}\right)$$

其中`matchWidthOrHeight`取值0（以宽度为基准）到1（以高度为基准），0.5表示取宽高缩放比的几何均值。针对竖屏手游通常设置为1（以高度匹配），横屏游戏设置为0（以宽度匹配），从而避免UI在宽高比差异较大的设备上出现裁切或溢出。

- **Constant Physical Size**：以物理尺寸（英寸/厘米）为单位确定UI大小，依赖设备上报的DPI值，适合需要精确控制触控目标物理尺寸（如无障碍设计要求最小44×44 pt触控区）的场景。

### Graphic Rebuild的触发条件

任何对以下属性的修改均会触发`Graphic.SetVerticesDirty()`或`Graphic.SetMaterialDirty()`，进而引发重建：
- `Image.color`（修改顶点颜色，触发顶点重建）
- `Image.sprite`（可能切换材质，触发材质重建）
- `Text.text` / `TextMeshProUGUI.text`（触发完整的字形布局重算）
- `RectTransform`尺寸变化（触发布局重建，进而级联触发子元素重建）

高频修改`Image.fillAmount`（例如圆形冷却图标）仅触发顶点重建，不触发材质重建，是相对轻量的操作；而频繁切换`Image.sprite`且图集不同时，会导致材质切换打断合批，产生额外DrawCall——这是UGUI性能问题中最常见的陷阱之一。

---

## 实际应用

### 案例：移动RPG游戏的主HUD架构

以一款典型的移动端RPG主战斗界面为例，其UGUI层级结构通常组织如下：

```
Canvas (Screen Space - Overlay, CanvasScaler: Scale With Screen Size 1080x1920)
├── Canvas_Static (子Canvas：血条背景、技能图标底图等静态元素)
│   ├── HPBarBackground
│   └── SkillSlotBG (x4)
├── Canvas_Dynamic (子Canvas：数值文字、冷却遮罩等每帧变化元素)
│   ├── HPText (TextMeshProUGUI)
│   ├── CooldownMask_1 (Image, ImageType: Filled, fillMethod: Radial360)
│   └── DamageNumberPool (对象池挂载点)
└── Canvas_Popup (子Canvas：独立sortingOrder，弹窗层)
    └── PopupContainer
```

静态子Canvas与动态子Canvas的分离确保了血条数值每帧更新时，不会触发技能图标底图的重建。`CooldownMask`使用`Image Type: Filled`配合`fillAmount`属性驱动圆形冷却动画，整个冷却效果无需切换Sprite即可实现，避免材质Dirty。

### 案例：TextMeshPro与UGUI的集成

Unity 2018.1起，TextMeshPro（TMP）正式成为UGUI的内置包（Package Manager中的`com.unity.textmeshpro`）。相比`UnityEngine.UI.Text`，`TextMeshProUGUI`使用**SDF（Signed Distance Field）**字体渲染技术，在任意缩放比例下保持字边清晰，并支持富文本标签（`<color>`、`<size>`、`<sprite>`等）。TMP的`TextMeshPro.text`赋值会触发完整的字形Shaping流程，在性能敏感场景应使用`TextMeshProUGUI.SetText(string format, float arg0)`的格式化重载来避免字符串堆分配（GC Alloc）。

---

## 常见误区

**误区一：在Update()中每帧对RectTransform赋值**
即使赋值前后数值相同，部分UGUI属性的setter仍会无条件调用`SetDirty()`，导致每帧触发无效重建。正确做法是在赋值前做值相等判断，或改用`CanvasGroup.alpha`代替逐元素透明度修改（`CanvasGroup`的alpha修改不触发Graphic重建，仅修改渲染状态）。

**误区二：混淆anchoredPosition与localPosition**
`RectTransform.localPosition`与`anchoredPosition`在`anchorMin == anchorMax`且`Pivot == (0.5, 0.5)`时数值相同，但在Pivot偏移或锚点展开时两者存在偏差。通过代码设置UI位置时应优先使用`anchoredPosition`，通过`localPosition`设置可能导致在不同父容器或Pivot设置下产生意料之外的偏移。

**误区三：对World Space Canvas使用GraphicRaycaster而不配置EventCamera**
World Space Canvas的`GraphicRaycaster`需要指定一个`Event Camera`才能正确将屏幕坐标反投影到Canvas平面。未指定时Unity会回退使用`Camera.main`，在多