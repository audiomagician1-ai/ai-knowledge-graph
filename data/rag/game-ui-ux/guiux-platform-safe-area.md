---
id: "guiux-platform-safe-area"
concept: "平台安全区域"
domain: "game-ui-ux"
subdomain: "multiplatform"
subdomain_name: "多平台适配"
difficulty: 2
is_milestone: false
tags: ["multiplatform", "平台安全区域"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 平台安全区域

## 概述

平台安全区域（Platform Safe Zone）是指屏幕上能够保证UI元素完整显示、不被物理边框遮挡、传感器凹槽覆盖或曲面畸变干扰的矩形可用渲染区域。游戏开发者必须将血条、小地图、对话框、操作提示等所有关键UI元素限制在这个矩形范围内，才能保证跨平台的可用性。

安全区域问题最早在CRT电视广播时代系统化：1953年NTSC标准制定时，美国广播电视工程师协会（SMPTE）定义了两条安全线——"动作安全区"（Action Safe Area，覆盖屏幕面积的90%）和"字幕安全区"（Title Safe Area，覆盖屏幕面积的80%）。这两条边界的存在，是因为CRT显像管的过扫描（Overscan）电路会将图像四边各约4%至8%的像素推到物理管壳之外，观众根本看不到这部分内容。这一传统直接延续到PlayStation 5和Xbox Series X|S的认证规范中，要求所有游戏至今仍必须实现UI安全区域调节选项。

2017年11月3日，苹果iPhone X发布，刘海屏（Notch）设计让安全区域问题在移动端重新进入开发者视野。苹果同步推出的iOS 11引入了`safeAreaInsets`API，将安全边距的精确像素值直接暴露给开发者，彻底改变了移动游戏UI的适配流程。

参考资料：《移动游戏开发实战》中国铁道出版社（葛燕超，2021），以及苹果官方Human Interface Guidelines（Apple, 2023）。

---

## 核心原理

### 电视过扫描安全区域的计算方法

过扫描（Overscan）源于模拟信号时代CRT显像管的硬件特性：驱动电路故意让电子束的扫描轨迹超出荧光屏可见区域约5%至8%，目的是将模拟信号头尾的时序噪声和行同步脉冲藏在物理边框背后，防止观众看到画面边缘的闪烁杂波。现代平板电视虽然默认关闭过扫描，但**索尼PlayStation 5认证要求（TRC R4112）**和**微软Xbox Series认证要求（XR-019）**均明确规定：游戏必须在设置菜单中提供"安全区域调整"滑块，允许玩家将UI内缩距离设置为屏幕宽高的0%至10%（以5%为默认推荐值）。

**标准1080p分辨率下的安全区域计算公式：**

设屏幕分辨率为 $W \times H$，安全区域内缩比例为 $r$（取值范围0.05至0.10），则安全区域的宽度 $W_s$ 和高度 $H_s$ 分别为：

$$W_s = W \times (1 - 2r), \quad H_s = H \times (1 - 2r)$$

安全区域左上角起始坐标 $(x_0, y_0)$ 为：

$$x_0 = W \times r, \quad y_0 = H \times r$$

**具体数值示例：** 若 $W = 1920$，$H = 1080$，$r = 0.05$，则：
- $W_s = 1920 \times 0.90 = 1728$ 像素
- $H_s = 1080 \times 0.90 = 972$ 像素
- 起始坐标为 $(96, 54)$

这意味着开发者不能将血量条定位在坐标 $(0, 0)$，而必须至少从 $(96, 54)$ 开始布局。若直接在Unreal Engine中使用默认UI摄像机视口而不设置Viewport Padding，则在电视上运行时极有可能导致操作提示被物理边框遮挡。

### 刘海屏与打孔屏安全区域

苹果设备的刘海屏安全边距因机型不同存在显著差异。以竖屏状态为基准，各主要机型的`safeAreaInsets`精确数值如下：

| 机型 | 顶部 (pt) | 底部 (pt) | 左右 (pt) |
|---|---|---|---|
| iPhone SE (第3代，无刘海) | 20 | 0 | 0 |
| iPhone X / XS | 44 | 34 | 0 |
| iPhone 14 Pro (动态岛) | 59 | 34 | 0 |
| iPhone 15 Pro Max (横屏) | 0 | 21 | 59 |

苹果通过`UIView.safeAreaLayoutGuide`在原生层提供这些数值，Unity引擎从2017.2版本起通过`Screen.safeArea`属性（返回`UnityEngine.Rect`结构）将其直接暴露给游戏层，无需开发者手动查询设备型号数据库。

Android阵营则通过`WindowInsetsCompat.getDisplayCutout()`获取异形屏区域数据。由于Android设备碎片化，三星Galaxy S23 Ultra的打孔屏开孔直径约为3.4mm（对应约10像素半径），而小米折叠屏MIX Fold 3在展开状态下屏幕中缝铰链区域宽约2mm，同样需要作为"软性安全区"处理，避免在铰链处放置可交互按钮。

### 曲面屏与折叠屏的特殊处理

三星Galaxy S系列Edge曲面屏在屏幕两侧各约15至20像素区域存在视觉畸变，该区域的触控采样精度也低于屏幕中央，原因是曲面边缘的触控传感器层厚度不均匀，导致电容信号强度偏低约18%（三星内部测试数据，引自Samsung Developer Conference 2019技术分享）。游戏中若将技能按钮或虚拟摇杆边缘放置在曲面区域，玩家误触率会显著上升。建议横屏游戏将左右UI边距设置为不低于屏幕宽度的3%（1080p宽屏下约32像素）。

折叠屏设备在折叠状态与展开状态之间切换时，分辨率和安全区域会动态改变。以三星Galaxy Z Fold 5为例：
- **封面屏（折叠状态）**：分辨率2316×904，宽高比约23:9，横向极窄
- **主屏（展开状态）**：分辨率2176×1812，宽高比约6:5，接近正方形

这意味着游戏UI必须能够响应`onConfigurationChanged`（Android）或`viewSafeAreaInsetsDidChange`（iOS）回调事件，在设备形态改变时实时重新计算锚点位置，而非仅在应用启动时做一次性适配。

---

## 关键实现代码

在Unity中，将Canvas的RectTransform与`Screen.safeArea`动态绑定是处理刘海屏最可靠的方式。以下代码适用于Unity 2021 LTS及以上版本：

```csharp
using UnityEngine;

[RequireComponent(typeof(RectTransform))]
public class SafeAreaAdapter : MonoBehaviour
{
    private RectTransform _rectTransform;
    private Rect _lastSafeArea = Rect.zero;
    private Vector2Int _lastScreenSize = Vector2Int.zero;

    void Awake()
    {
        _rectTransform = GetComponent<RectTransform>();
    }

    void Update()
    {
        // 检测安全区域或分辨率变化（折叠屏切换时触发）
        Rect currentSafe = Screen.safeArea;
        Vector2Int currentSize = new Vector2Int(Screen.width, Screen.height);

        if (currentSafe != _lastSafeArea || currentSize != _lastScreenSize)
        {
            ApplySafeArea(currentSafe);
            _lastSafeArea = currentSafe;
            _lastScreenSize = currentSize;
        }
    }

    void ApplySafeArea(Rect safeArea)
    {
        // 将像素坐标转换为锚点归一化值 (0~1)
        Vector2 anchorMin = safeArea.position;
        Vector2 anchorMax = safeArea.position + safeArea.size;

        anchorMin.x /= Screen.width;
        anchorMin.y /= Screen.height;
        anchorMax.x /= Screen.width;
        anchorMax.y /= Screen.height;

        _rectTransform.anchorMin = anchorMin;
        _rectTransform.anchorMax = anchorMax;
        _rectTransform.offsetMin = Vector2.zero;
        _rectTransform.offsetMax = Vector2.zero;
    }
}
```

将此脚本挂载到UI根Canvas的子Panel上，并将所有HUD元素作为该Panel的子节点，即可自动适配iPhone的刘海区域和电视过扫描偏移，同时兼容Samsung折叠屏的实时形态切换。

---

## 实际应用

### PlayStation与Xbox主机认证的强制要求

索尼和微软的认证规范对安全区域有明确的测试用例。以Xbox Series X|S的XR-019认证为例，测试员会将电视的过扫描调至最大（约10%），然后检查以下三项是否满足：
1. 所有"必读信息"（如弹药数量、生命值、任务目标）必须完整显示在安全区域内；
2. 安全区域调节滑块必须可在设置菜单中访问，且调节范围覆盖0%至10%；
3. 调节滑块实时预览时，屏幕四角必须显示标准的"L形角标"参考标记。

PlayStation 5的TRC R4112规范则额外要求：当玩家通过系统设置的"屏幕尺寸"功能修改安全区域时，游戏必须响应系统事件实时更新UI位置，不得要求重启游戏。

### 移动端横竖屏切换与刘海位置变化

iPhone在横屏状态下，刘海（或动态岛）会移至屏幕左侧，导致`safeAreaInsets.left`从0pt变为59pt（iPhone 14 Pro），而`safeAreaInsets.top`从59pt降至0pt。若游戏中的虚拟摇杆固定锚定在左下角而未响应横屏时左侧安全边距的变化，摇杆的左半部分将被刘海遮挡，玩家向左推摇杆时触控点落在不可响应区域，直接导致操作失灵。

**案例：** 2018年《王者荣耀》在适配iPhone X时，初版更新将摇杆整体向右偏移了固定60像素，但这一硬编码值在iPad横屏下却产生了额外的不必要偏移，后续版本才改为读取`Screen.safeArea`动态计算。

### TV端UI的"L形角标"标定方法

开发TV游戏时，通常在安全区域调节界面的四个角渲染标准的"L形角标"（Corner Bracket），让玩家对照实际电视边框来判断当前偏移量是否合适。角标的线段长度建议为屏幕宽度的3%（1080p下约58像素），线段宽度为4像素，颜色为纯白色或与背景高对比度色。角标的位置应与当前安全区域的四个顶点精确重合，随滑块实时更新。

---

## 常见误区

**误区1：认为现代电视不需要过扫描适配**
许多开发者认为2010年后生产的HDTV默认已关闭过扫描，因此跳过TV安全区域适配。然而，索尼品牌电视的"屏幕尺寸"功能和部分三星电视的"画面尺寸"设置仍可将图像放大约3%至5%。更重要的是，PlayStation 5和Xbox Series X|S的认证规范明确将TV安全区域适配列为"必须通过（Must Pass）"测试项，跳过适配会导致认证失败、游戏无法上架。

**误区2：在iPhone SE上测试通过就认为全系iPhone适配完成**
iPhone SE（第3代）无刘海，`Screen.safeArea`与全屏矩形几乎一致，顶部仅有20pt状态栏偏移。若以SE作为唯一测试机型，代码中的边距硬编码会在iPhone 14 Pro上造成动态岛与UI元素重叠，或在底部Home指示条区域遮挡操作按钮。必须同时覆盖有刘海/动态岛机型和无刘海机型进行测试。

**误区3：将`Screen.safeArea`仅在`Start()`中读取一次**
折叠屏用户在游戏运行过程中展开设备时，屏幕分辨率和安全区域会立即改变。若仅在`Start()`中读取一次`Screen.safeArea`并缓存，展开后的安全区域将继续使用折叠状态的旧数值，导致UI错位。应如上方代码示例所示，在`Update()`中每帧检测变化，或在Android