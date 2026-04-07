# UI Toolkit（Unity）

## 概述

UI Toolkit 是 Unity Technologies 于 Unity 2019.1 版本中首先面向编辑器扩展工具开发引入、并在 Unity 2021.2 版本中将运行时（Runtime）支持正式提升至生产可用状态的新一代 UI 框架。其架构核心是彻底抛弃 UGUI 沿用至今的"每个控件 = 一个 GameObject + 一个 MonoBehaviour + 一个 RectTransform"的即时合批模型，转向基于 **Retained Mode（保留模式）** 的 Visual Tree 渲染管线。

Unity 此前并行存在两套 UI 系统：运行时使用的 UGUI（始于 Unity 4.6，2014年10月随 Unity 4.6.0 正式发布）依赖 Canvas 的动态合批，任意子节点的顶点变化均可触发整个 Canvas 的 Rebuild，这是业内公认的性能瓶颈；编辑器使用的 IMGUI（Immediate Mode GUI）则在每帧 `OnGUI()` 回调中重新绘制所有控件，无法复用任何帧间状态。UI Toolkit 用统一的 Visual Tree + UXML + USS 体系同时替代这两者，实现编辑器工具 UI 与游戏运行时 UI 的开发范式统一。

根据 Unity 官方 Roadmap（2023年更新），UGUI 自 Unity 2021 LTS 起已进入**维护模式（Maintenance Mode）**，不再接收新特性，所有 UI 领域研发资源均集中于 UI Toolkit。这一战略转向对需要同时维护数百乃至上千个 HUD 元素（血量条、弹药计数、地图标记、任务追踪器）的 AA/AAA 级项目具有实质性工程意义，因为这类项目在 UGUI 架构下每次场景切换时的 Canvas 初始化开销往往超过 20ms。

---

## 核心原理

### Visual Tree 与 VisualElement 节点模型

UI Toolkit 中所有可见与不可见的逻辑节点均继承自 `VisualElement` 基类。运行时，这些节点以有向无环树（DAG）结构组织，称为 **Visual Tree**。与 UGUI 本质不同的是，`VisualElement` 是纯托管 C# 对象，不附着任何 `GameObject` 或 `Transform` 组件，因此不占用 Unity 场景序列化开销，也不出现在 Hierarchy 窗口中。

每个 `VisualElement` 维护一套精细的**脏标记（Dirty Flags）**系统，分为三条独立更新通道：

- **Layout Dirty**：触发 Yoga 引擎对该节点及其子节点重新计算尺寸和位置，仅当 `width`、`margin`、`padding`、`flex-grow` 等影响盒模型的属性变化时置位
- **Style Dirty**：触发 USS 选择器的重新匹配与属性解析，仅当节点的 class 列表、伪类状态（`:hover`、`:checked`）或 USS 资源发生变化时置位
- **Repaint Dirty**：触发该节点的绘制指令（Mesh Generation）重新提交至后端渲染器，仅当背景色、边框、文字内容等视觉属性变化时置位

三通道彼此独立：修改一个 `Label` 的文本内容只置位 Repaint Dirty，不触发任何布局计算。这与 UGUI 的 Canvas Rebuild 形成根本对比——UGUI 中更改任意一个 `Text` 组件的字符串将导致所属 Canvas 所有顶点缓冲区重建。

### Yoga 布局引擎与 Flexbox 盒模型

UI Toolkit 的布局计算由 **Yoga** 引擎驱动。Yoga 是 Meta（前 Facebook）开源的跨平台布局引擎，严格遵循 W3C CSS Flexbox Level 1 规范实现，2016 年由 Schroeder 与 Barahona 在 Meta Engineering Blog 中发表（Schroeder, R. & Barahona, D., *Yoga: A cross-platform layout engine*, Meta Engineering, 2016）。Unity 将 Yoga 编译为原生代码后通过 P/Invoke 与托管层通信，以确保布局计算的高吞吐量。

Yoga 使用**单遍（single-pass）Flexbox 算法**，对一棵深度为 $d$、节点总数为 $n$ 的布局树，其理论时间复杂度为：

$$T_{\text{layout}} = O(n \cdot d)$$

在 UI 树相对扁平（$d \ll n$）的典型游戏 HUD 场景下，接近线性 $O(n)$。对比 UGUI Canvas 在存在动态元素时的合批重建开销 $O(n^2)$，当 $n=500$ 个元素时，理论操作数相差约 250 倍。

USS 中 Flexbox 属性的写法与 Web CSS 几乎完全一致：

```css
.inventory-grid {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: center;
    flex-grow: 1;
    padding: 8px;
    column-gap: 4px;
}
```

### UXML：声明式结构描述

**UXML（Unity XML）** 是基于 XML 的声明式文件格式，用于描述 Visual Tree 的初始层级结构，功能上类比 Web 的 HTML。每个 XML 标签对应一个 `VisualElement` 派生类型，属性（attribute）映射至该类型的公开属性，USS class 通过 `class` 属性赋予。

一个典型的物品栏面板 UXML 结构如下：

```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements">
    <ui:VisualElement name="inventory-root" class="panel-container">
        <ui:Label name="panel-title" text="背包" class="panel-title" />
        <ui:ScrollView name="item-scroll" mode="Vertical">
            <ui:VisualElement name="item-grid" class="inventory-grid" />
        </ui:ScrollView>
        <ui:Button name="close-btn" text="关闭" class="btn-secondary" />
    </ui:VisualElement>
</ui:UXML>
```

UXML 支持 `<ui:Template>` 与 `<ui:Instance>` 机制，允许将可复用的 UXML 片段定义为模板并在其他 UXML 中多次实例化，这是 UGUI Prefab 嵌套之外一种纯声明式的组合方案，且不依赖场景序列化。

### USS：样式系统与选择器

**USS（Unity Style Sheets）** 语法高度参照 W3C CSS Level 2/3 标准子集，支持类型选择器（`Button`）、类选择器（`.btn-primary`）、ID 选择器（`#close-btn`）以及后代选择器（`.panel .label`）。USS 不支持 CSS Grid、CSS Variables 原生语法（Unity 2022.2 后通过 USS 变量 `--custom-property` 部分弥补）及媒体查询。

USS 变量示例（Unity 2022.2+ 语法）：

```css
:root {
    --color-primary: rgb(72, 130, 255);
    --spacing-md: 12px;
}

.btn-primary {
    background-color: var(--color-primary);
    padding: var(--spacing-md);
    border-radius: 6px;
    color: white;
    font-size: 14px;
    -unity-font-style: bold;
}

.btn-primary:hover {
    background-color: rgb(100, 155, 255);
    transition-duration: 0.15s;
    transition-property: background-color;
}
```

USS 选择器匹配在 Visual Tree 构建阶段批量执行，而非逐帧重算，这使得拥有数百个控件的复杂面板在样式应用阶段不产生每帧开销。

### 数据绑定系统（Runtime Data Binding）

Unity 2023.2 正式引入**运行时数据绑定（Runtime Data Binding）**，这是 UI Toolkit 架构成熟的重要里程碑。绑定系统采用 **MVVM（Model-View-ViewModel）** 模式，通过 `INotifyBindablePropertyChanged` 接口或 `[CreateProperty]` 特性标注，将 C# 对象属性与 `VisualElement` 的 USS 属性或自定义属性建立响应式连接。

```csharp
// ViewModel 定义
public class PlayerStatsViewModel : MonoBehaviour, INotifyBindablePropertyChanged
{
    [CreateProperty]
    public float Health
    {
        get => _health;
        set
        {
            if (Mathf.Approximately(_health, value)) return;
            _health = value;
            // 通知绑定系统属性已变化
            Notify(nameof(Health));
        }
    }
    private float _health;

    public event EventHandler<BindablePropertyChangedEventArgs> propertyChanged;
    private void Notify(string property) =>
        propertyChanged?.Invoke(this, new BindablePropertyChangedEventArgs(property));
}
```

UXML 中通过 `binding-path` 属性声明绑定关系：

```xml
<ui:ProgressBar name="health-bar"
    binding-path="Health"
    low-value="0"
    high-value="100" />
```

相比 UGUI 中需要手写 `OnHealthChanged` 事件订阅与 `UI.Slider.value = newHealth` 的命令式更新，数据绑定机制显著减少了 UI 层与逻辑层之间的耦合代码量，在大型项目中估计可减少 30%-50% 的 UI 同步样板代码。

---

## 关键方法与公式

### 渲染批次计算

UI Toolkit 后端使用独立的 **UIR（UI Renderer）** 渲染器，与 UGUI Canvas 渲染器完全分离。UIR 将 Visual Tree 中连续的、共享同一材质/纹理图集的 `VisualElement` 合并为单一 Draw Call。对于 $m$ 个共享纹理图集的元素组成的 UI 面板，理论最小 Draw Call 数为：

$$DC_{\min} = \lceil m / B \rceil$$

其中 $B$ 为单批次最大顶点数上限（默认约 65536 顶点），在实际游戏 HUD 中通常 $DC_{\min} = 1 \sim 3$。

### 动态元素的更新代价模型

在保留模式下，仅脏节点参与重绘。设某帧中 $k$ 个节点被标记为 Repaint Dirty（$k \ll n$），则该帧的 Mesh 重生成代价近似为：

$$C_{\text{repaint}} = k \cdot C_{\text{meshgen}}$$

其中 $C_{\text{meshgen}}$ 为单节点的 Mesh Generation 平均代价（通常为数微秒量级）。这与 UGUI 中任意节点变化导致整个 Canvas 所有 $n$ 个节点重建（代价 $\propto n$）形成对比，在 $k \ll n$ 时 UI Toolkit 的优势随 $n$ 增大而线性放大。

---

## 实际应用

### 案例：大型 RPG 游戏 HUD 重构

某 Unity 项目拥有约 800 个运行时 HUD 元素（地图标记、状态效果图标、任务追踪等），原 UGUI 实现在场景加载完成后每帧 Canvas Rebuild 耗时约 4.2ms（在目标 16.6ms 帧预算中占比约 25%）。迁移至 UI Toolkit 后，由于 Retained Mode 的脏标记机制，每帧实际触发 Repaint 的节点通常少于 20 个，Rebuild 开销降至 0.3ms 以下，帧预算占比从 25% 降至 1.8%。

### 案例：编辑器扩展工具开发

Unity 官方 Package Manager 窗口、Timeline 编辑器（Unity 2021.2+）均已完全使用 UI Toolkit 重写，告别了 IMGUI 的 `EditorGUILayout.BeginHorizontal()` / `EndHorizontal()` 等嵌套调用地狱。开发者可以使用相同的 UXML/USS 技能栈同时开发游戏内 UI 与编辑器工具面板，技能迁移成本几乎为零。

### 案例：本地化与字体切换

USS 的 `font-size`、`-unity-font`、`-unity-font-definition` 属性支持在运行时通过 USS 变量动态替换，配合 `PanelSettings` 中的 `textSettings` 引用，可实现跨语言字体切换（如中文切换至中文字体资源）而无需修改任何 UXML 结构，仅通过替换一个 USS 文件即可完成全局字体本地化。

---

## 常见误区

### 误区一：UI Toolkit 在所有场景下都比 UGUI 快

UI Toolkit 的性能优势主要体现在**大量静态或低频更新元素**的场景（如背包、技能树、地图等）。对于**高频全局变化**的 UI（如每帧更新全部元素的