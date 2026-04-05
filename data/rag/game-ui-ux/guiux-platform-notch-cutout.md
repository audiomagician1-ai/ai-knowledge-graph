---
id: "guiux-platform-notch-cutout"
concept: "异形屏适配"
domain: "game-ui-ux"
subdomain: "multiplatform"
subdomain_name: "多平台适配"
difficulty: 3
is_milestone: false
tags: ["multiplatform", "异形屏适配"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 异形屏适配

## 概述

异形屏适配是指在刘海屏（Notch）、打孔屏（Punch-hole）、折叠屏（Foldable）等非矩形显示区域的设备上，通过专项策略保证游戏UI元素既不被硬件遮挡、又能充分利用延伸显示面积的开发实践。与普通全面屏适配不同，异形屏适配需要精确识别"安全区域"（Safe Area）之外的"危险像素带"，并针对刘海、摄像头打孔的具体坐标位置做出动态规避或主动利用。

这一需求随着2017年9月iPhone X发布而进入主流视野——该设备引入了高度44pt（约132px @ 3x分辨率，物理尺寸约5.9mm）的刘海区域以及底部34pt的Home指示条，迫使开发者第一次系统性地面对非矩形安全区问题。此后Android阵营在2018年8月随Android 9（API Level 28）推出`DisplayCutout` API，正式将异形区域的坐标查询标准化。折叠屏则在2019年2月随三星Galaxy Fold首次商用后带来了铰链遮挡区（Hinge Occlusion Area）这一全新挑战维度，其铰链物理宽度约为6.3mm，折叠展开后在屏幕中央形成不可触控的死区。

对于游戏UI而言，异形屏适配直接影响摇杆、血条、小地图等高频交互控件的可点击性与可读性。若血条恰好落在打孔区后方，玩家在战斗中将无法读取关键信息；若摇杆热区覆盖了Home指示条，系统手势会与游戏操作产生冲突，导致误触返回桌面。根据Google Android兼容性测试数据，2022年市场上搭载异形屏的Android设备占比已超过85%，这意味着异形屏适配已不再是"优化项"而是游戏发行的基本门槛。

参考资料：Android官方文档《Support display cutouts》(Google, 2023)；《移动游戏UI设计实战》，电子工业出版社。

---

## 核心原理

### 安全区域（Safe Area）与环境内嵌量（Environment Insets）

iOS通过`UIView.safeAreaInsets`暴露上下左右四个方向的内嵌量（单位：逻辑点pt）。iPhone X系列设备的典型值为：顶部44pt、底部34pt、左右0pt（竖屏）；横屏时左右各为44pt，底部21pt。iPhone 14 Pro引入的灵动岛（Dynamic Island）将顶部状态栏的安全内嵌量维持在59pt（3x屏下约177px），但由于灵动岛本身是软件可编程的动态组件，其下方区域并非永久遮挡，开发者需额外监听`UIDevice.orientationDidChangeNotification`以在旋转时重新计算布局。

Unity引擎可通过`Screen.safeArea`（返回以像素为单位的`Rect`结构体）直接获取安全矩形，配合以下代码将UI Canvas的RectTransform动态约束到安全区内：

```csharp
// SafeAreaAdapter.cs — Unity 2021+适配脚本
using UnityEngine;

[RequireComponent(typeof(RectTransform))]
public class SafeAreaAdapter : MonoBehaviour
{
    private RectTransform _rt;
    private Rect _lastSafeArea = Rect.zero;

    void Awake() => _rt = GetComponent<RectTransform>();

    void Update()
    {
        var safeArea = Screen.safeArea;
        if (safeArea != _lastSafeArea)
        {
            ApplySafeArea(safeArea);
            _lastSafeArea = safeArea;
        }
    }

    void ApplySafeArea(Rect sa)
    {
        var anchorMin = sa.position;
        var anchorMax = sa.position + sa.size;
        anchorMin.x /= Screen.width;
        anchorMin.y /= Screen.height;
        anchorMax.x /= Screen.width;
        anchorMax.y /= Screen.height;

        _rt.anchorMin = anchorMin;
        _rt.anchorMax = anchorMax;
    }
}
```

Android的`DisplayCutout`对象通过`WindowInsets.getDisplayCutout()`获取，再调用`getSafeInsetTop()`、`getSafeInsetBottom()`、`getSafeInsetLeft()`、`getSafeInsetRight()`分别读取四个方向的像素级内嵌量。与iOS不同，Android设备的打孔位置高度分散——华为Mate 40 Pro的双曲面打孔中心位于顶部约17px处，短轴约14px、长轴约16px；三星Galaxy S22的打孔半径约4.25mm（约42px @ 393ppi）；小米12的打孔半径更小，约3.6mm。这些差异必须通过运行时动态查询而非任何形式的硬编码设备列表来应对。

### 刘海与打孔区域的主动利用策略

避让是消极防御，积极的做法是将刘海/打孔区域两侧的"耳朵"空间（Ear Area）纳入游戏UI布局。以横屏射击游戏为例，iPhone X横屏时左右各有44pt宽、屏幕全高的耳朵区域（面积约44×375pt²），其像素密度与主屏完全相同，可渲染非交互信息层。

标准的耳朵区域利用分级如下：
- **等级A——展示型信息**：金币数量、段位图标、网络延迟数字。这类元素被遮挡1~2帧不影响体验，适合放置于耳朵区。
- **等级B——低频交互**：设置按钮、暂停菜单入口。点击热区须确保完整落在安全区内，仅视觉部分可延伸至耳朵区。
- **等级C——高频精确触控**：摇杆、技能按钮、射击键。严禁放置于耳朵区或Home指示条覆盖范围内。

折叠屏的铰链遮挡区（Hinge Occlusion Rect）在三星设备上通过Jetpack WindowManager库的`FoldingFeature.bounds`获取，返回铰链在窗口坐标系中的精确像素矩形。以Galaxy Z Fold 4为例，展开态内屏分辨率为1812×2176px，铰链遮挡区宽度约为24px（约2.4mm等效），左右各留出约894px的半屏区域。游戏可将左半屏设计为操控面板（虚拟摇杆+技能栏），右半屏渲染主游戏视口，实现类PC双屏体验。

### 动态检测与分级适配逻辑

实用的异形屏适配框架通常分三个层级执行，以减少不必要的布局计算开销：

1. **零适配设备**：`Screen.safeArea`等于`new Rect(0, 0, Screen.width, Screen.height)`，即Insets全为0，按标准布局直接渲染，跳过所有偏移计算。
2. **单边刘海/打孔设备**：仅顶部或单侧存在切口，只需单向偏移对应区域的UI根节点，其余三边保持满屏布局。
3. **多边异形+折叠设备**：需同时处理刘海、打孔、铰链三类异形，且在折叠/展开状态切换时（`FoldingFeature.state == FLAT` 或 `HALF_OPENED`）触发完整的布局重算。三星Galaxy Z Fold系列在半折状态下还会额外限制UI交互区至下半屏，此时顶部折叠角度约为110°~170°，开发者需监听`WindowInfoTracker.windowLayoutInfo`流来响应状态变化。

---

## 关键公式与计算方法

游戏UI中，安全区内嵌量转换为Canvas锚点坐标的通用公式如下。设设备屏幕物理分辨率为 $W \times H$（像素），安全区矩形为 $\text{safeRect} = (x_0, y_0, w_s, h_s)$，则UI根节点的归一化锚点范围为：

$$
\text{anchorMin} = \left(\frac{x_0}{W},\ \frac{y_0}{H}\right), \quad \text{anchorMax} = \left(\frac{x_0 + w_s}{W},\ \frac{y_0 + h_s}{H}\right)
$$

对于打孔屏，需额外判断打孔圆心 $(c_x, c_y)$ 与半径 $r$ 是否与某UI元素的轴对齐包围盒（AABB）相交，相交判断条件为：

$$
\max(|u_x - c_x| - \tfrac{W_{ui}}{2},\ 0)^2 + \max(|u_y - c_y| - \tfrac{H_{ui}}{2},\ 0)^2 \leq r^2
$$

其中 $(u_x, u_y)$ 为UI元素中心像素坐标，$W_{ui}$ 和 $H_{ui}$ 为元素宽高。若满足该不等式，则该UI元素的布局位置须向安全方向偏移至少 $r + 8\text{px}$（8px为视觉缓冲距离，参考Material Design 3规范）。

---

## 实际应用案例

### 案例一：《原神》移动端横屏刘海适配

《原神》在iPhone 13 Pro（2532×1170px，Super Retina XDR，460ppi）横屏模式下，将左侧任务追踪器和右侧小地图分别限制在安全区内边距内约20pt处渲染，同时将角色血条和元素能量条的热区设置为仅响应安全区内的触控输入。刘海左耳区域被用于渲染时间与网络信号的只读状态，不放置任何可交互元素。

### 案例二：折叠屏双屏布局（Galaxy Z Fold系列）

某MOBA手游针对Galaxy Z Fold 4展开态进行专项适配：将1812px宽的内屏按铰链位置划分为左区（894px）和右区（894px），左区渲染技能面板与小地图，右区渲染游戏主视角并保留16:9比例（即实际使用右区中心的约894×503px子区域，其余区域用黑色letterbox填充以避免画面拉伸变形）。铰链24px遮挡带被设计为视觉上的分屏边框装饰，兼顾功能回避与美观。

### 案例三：打孔屏下血量条的动态规避

某RPG游戏在检测到`DisplayCutout.getBoundingRects()`返回非空列表时，将顶部血量HUD向下偏移打孔高度+12dp（12dp的额外间距对应安全触控缓冲区）。若玩家将屏幕旋转为左横屏（打孔移至左侧），系统重新调用适配逻辑，将左侧技能栏整体右移至安全区内，避免技能图标被打孔遮挡。

---

## 常见误区

**误区一：用固定像素值硬编码刘海高度。**  
例如将顶部偏移量写死为88px（iPhone X在3x下刘海的像素值），会导致iPhone 14 Pro（灵动岛高度折算约177px）上UI严重压缩，以及在所有非刘海Android设备上产生不必要的顶部空白带。正确做法是始终从运行时API读取，绝不硬编码。

**误区二：仅适配竖屏，忽略横屏的Insets变化。**  
iPhone X竖屏顶部Insets为44pt，但横屏后变为左右各44pt、顶部0pt（因无状态栏）、底部21pt。若仅在初始化时读取一次Insets而不监听屏幕旋转回调（`Screen.orientation`变化或`onConfigurationChanged`），旋转后UI将出现错位。

**误区三：将折叠屏铰链区误判为"黑边"而不处理。**  
Galaxy Z Fold系列在展开态下铰链区（24px宽）完全透明可见，但触控事件在该区域内不会被系统分发。若将交互按钮放置于铰链正中，按钮视觉可见但完全无法响应点击，导致玩家困惑。必须通过`FoldingFeature.isSeparating`属性判断铰链是否将屏幕分为两个独立逻辑区域，并据此调整布局。

**误区四：忽略灵动岛的动画扩展状态。**  
iPhone 14 Pro的灵动岛在播放音乐或导航时会动态扩展，最大扩展尺寸约为宽390pt、高37pt，覆盖区域远大于静态状态的宽126pt×37pt。若游戏在此时弹出全屏公告等UI，需监听`ActivityKit`通知或在顶部保留足够的动态余量