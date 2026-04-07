---
id: "colorblind-design"
concept: "色盲友好设计"
domain: "game-design"
subdomain: "accessibility"
subdomain_name: "可达性设计"
difficulty: 2
is_milestone: false
tags: ["视觉"]

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



# 色盲友好设计

## 概述

色盲友好设计（Color Blind Accessible Design）是游戏可达性设计中针对色觉缺陷玩家群体的专项工程实践，覆盖Protanopia（红色锥细胞缺失）、Deuteranopia（绿色锥细胞缺失）和Tritanopia（蓝色锥细胞缺失）三类主要色觉障碍。根据国际色觉缺陷研究数据（Cole, 2004），全球约8%的欧裔男性和0.5%的欧裔女性存在先天性色觉缺陷，其中Deuteranopia和Protanopia合计占色盲人口的约99%，Tritanopia仅占0.003%。以一款拥有1000万玩家的主机游戏为例，保守估计有超过40万名男性玩家存在红绿色盲，若游戏核心玩法依赖红绿区分（如地图标记、技能状态、队伍识别），这批玩家将直接面临可玩性障碍。

色盲并非单一的"看不见颜色"状态——Protanopia患者对红色的亮度感知显著偏低（红色视亮度约为正常人的10%），而Deuteranopia患者的亮度感知曲线与正常人更接近，两者对红绿混淆的具体表现存在差异。《反恐精英：全球攻势》早期版本因部分血迹效果和雷达颜色对红绿色盲玩家不可辨而受到社区批评，Valve在2014年更新后专门加入色盲辅助选项，分别针对Protanopia、Deuteranopia和Tritanopia提供三套不同的颜色重映射方案。《英雄联盟》2014年引入的色盲模式将敌方小地图标识从红色改为橙色（#FF8C00附近），有效解决了Deuteranopia玩家无法区分红色敌方与绿色草丛的问题。

---

## 核心原理

### 视锥细胞缺失的感知机制

人眼视网膜包含三种视锥细胞：L型（对长波长红光敏感，峰值约564nm）、M型（对中波长绿光敏感，峰值约534nm）和S型（对短波长蓝光敏感，峰值约420nm）。Protanopia是L型视锥细胞先天缺失，导致红色感知被M型曲线替代，红色与深绿色在感知上几乎等价；Deuteranopia是M型缺失，绿色感知被L型替代，同样产生红绿混淆但亮度保留更完整；Tritanopia是S型缺失，蓝色与绿色混淆、黄色与粉红混淆。

从视觉信号处理角度，色觉缺陷者的颜色辨别能力可以用二维色度空间（而非正常人的三维）来建模。Brettel等人在1997年提出了精确的数学模型，将正常三色觉者的LMS色彩空间映射到二色觉者的混淆轴（confusion lines），这是现代色盲模拟工具（如Sim Daltonism、Coblis）的算法基础。设计师理解这一机制后可以预判：红色（#FF0000）在Protanopia视角下呈暗橄榄色，与深绿色（#006400）的感知差异极小，两者在模拟图像中几乎无法区分。

### 多通道信息传递原则

色盲友好设计的根本技术原则来自通用设计准则：**同一关键信息必须通过至少两种独立视觉属性同时编码**，颜色只能作为辅助通道而非唯一通道。具体的双通道策略包括以下几类：

- **颜色 + 形状**：《星际争霸2》为Protoss、Terran、Zerg三个种族的单位设计了完全不同的外形轮廓，玩家即便无法区分队伍颜色也能靠造型识别。
- **颜色 + 图标**：危险区域除红色底色外叠加骷髅或感叹号图标；《暗黑破坏神3》物品品质除颜色区分外还附有不同边框样式。
- **颜色 + 纹理/图案**：战略地图中不同势力领地用不同条纹密度叠加在颜色上；这也是数据可视化中处理色盲问题的标准方案（Tufte, 《The Visual Display of Quantitative Information》, 2001）。
- **颜色 + 亮度差异**：确保不同状态颜色之间存在明显的亮度（Lightness，L值）差距，使黑白打印下依然可辨，这对Protanopia尤其关键，因为该类型患者红色亮度感知异常偏低。

### 色盲安全配色方案与Okabe-Ito调色板

2008年，日本遗传学家Okabe和Ito发表了专为色盲优化的8色调色板（Okabe & Ito, 2008），该方案对Protanopia、Deuteranopia、Tritanopia三种类型均保持高可辨识度，被Nature等科学期刊采纳为推荐配色，也广泛应用于游戏UI领域。8种颜色的十六进制值为：

| 颜色名称 | HEX值   | 典型用途         |
|----------|---------|------------------|
| 黑色     | #000000 | 背景/轮廓        |
| 橙色     | #E69F00 | 警告/高亮        |
| 天蓝色   | #56B4E9 | 友方/信息        |
| 蓝绿色   | #009E73 | 正常/通过状态    |
| 黄色     | #F0E442 | 注意/次要标记    |
| 蓝色     | #0072B2 | 主要队伍标识     |
| 朱红色   | #D55E00 | 危险/敌方        |
| 玫瑰红   | #CC79A7 | 第三队伍/特殊状态|

在游戏实践中，以蓝色（#0072B2）与橙色（#E69F00）或朱红色（#D55E00）作为双方队伍标识，比传统红绿对立配色对红绿色盲玩家友好度提升显著。

---

## 关键公式与实现算法

### 相对亮度与对比度计算

WCAG 2.1标准定义的相对亮度（Relative Luminance）计算公式，是判断游戏HUD元素可读性的量化基准：

$$L = 0.2126 \cdot R_{lin} + 0.7152 \cdot G_{lin} + 0.0722 \cdot B_{lin}$$

其中，线性化RGB分量的转换规则为：

$$C_{lin} = \begin{cases} \dfrac{C_{sRGB}}{12.92} & \text{若 } C_{sRGB} \leq 0.04045 \\ \left(\dfrac{C_{sRGB} + 0.055}{1.055}\right)^{2.4} & \text{若 } C_{sRGB} > 0.04045 \end{cases}$$

两种颜色之间的对比度比值（Contrast Ratio）为：

$$CR = \frac{L_1 + 0.05}{L_2 + 0.05}, \quad L_1 \geq L_2$$

WCAG 2.1要求正文文字的 $CR \geq 4.5:1$，大字体（18pt以上）的 $CR \geq 3:1$。游戏HUD中血条数值、技能冷却读数等关键文字应达到4.5:1标准。以白色文字（L=1.0）叠加纯红色（#FF0000，L≈0.213）背景为例：$CR = (1.0+0.05)/(0.213+0.05) \approx 3.99:1$，未达标准，需将红色背景加深或改用深红（#CC0000）来提高对比度。

### Unity后处理着色器实现（色盲颜色重映射）

在Unity（URP/HDRP管线）中，色盲模式通常通过全屏后处理着色器实现颜色矩阵变换。以下为针对Deuteranopia的简化颜色转换矩阵实现示例：

```hlsl
// ColorBlindFilter.hlsl
// Deuteranopia 颜色重映射矩阵（基于Machado et al., 2009算法简化版）
float3 DeuteranopiaTransform(float3 col)
{
    // 将 Deuteranopia 混淆轴上的红绿混合投影到蓝橙对立轴
    float3x3 deutMat = float3x3(
        0.367, 0.861, -0.228,
        0.280, 0.673,  0.047,
       -0.012, 0.043,  0.969
    );
    return mul(deutMat, col);
}

// 在后处理Pass的Fragment Shader中调用：
float4 Frag(Varyings input) : SV_Target
{
    float4 color = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.texcoord);
    
    #if defined(COLOR_BLIND_DEUTERANOPIA)
        color.rgb = DeuteranopiaTransform(color.rgb);
    #elif defined(COLOR_BLIND_PROTANOPIA)
        color.rgb = ProtanopiaTransform(color.rgb);
    #elif defined(COLOR_BLIND_TRITANOPIA)
        color.rgb = TritanopiaTransform(color.rgb);
    #endif
    
    return color;
}
```

此方案在GPU侧以单个全屏Pass完成，运行时性能开销极小（在1080p分辨率下约0.1ms），适合作为游戏设置中的实时切换选项。需注意矩阵参数应使用Machado等人2009年发表的完整感知模型数据，而非直接使用Brettel 1997年的简化投影矩阵，前者在视觉保真度上有显著提升（Machado, Oliveira & Fernandes, 2009）。

---

## 实际应用

### 游戏行业案例分析

**《守望先锋》（Overwatch，2016）**：Blizzard为该游戏内置了三档色盲模式（Deuteranopia/Protanopia/Tritanopia），对敌我双方的头顶名牌颜色、地图控制区域指示、技能UI加热条分别进行重映射。在Deuteranopia模式下，敌方轮廓颜色从红色（#FF4444）切换为紫色（#9B59B6），避免与绿色植被背景混淆，据Blizzard可达性工程师在2017年GDC演讲中披露，该功能上线后相关的可达性投诉降低了约70%。

**《赛博朋克2077》（2020）**：CD Projekt Red内置了可单独开关的色盲友好UI选项，将小地图任务标记从默认的红/黄/绿三色系统改为蓝/橙/白系统。此外，游戏中物品稀有度除颜色编码（灰/绿/蓝/紫/橙）外，还附有文字标注稀有等级名称（Common/Uncommon/Rare/Epic/Legendary），实现了文字+颜色的双通道传递。

**《蔚蓝》（Celeste，2018）**：独立游戏典范案例。为草莓（收集物）、水晶心（关键道具）等核心物品设计了独特轮廓形状，不依赖颜色辨识；游戏的难度辅助系统（Assist Mode）设计原则记录于Matt Thorson的GDC 2019演讲中，强调可达性不应破坏核心挑战性，为行业提供了重要参考框架。

### 地图与战术UI的特殊处理

RTS和MOBA类游戏的战术地图是色盲问题最密集的区域。《英雄联盟》小地图在色盲模式下除改变敌我颜色外，还将敌方英雄图标加上固定的黑色外框（友方无外框），通过边框存在与否形成形状通道。《文明6》的领土颜色因需显示多达12个文明，在色盲模式下引入了领土边界纹理图案（不同文明使用不同虚线/实线/点线边界），将颜色识别压力分散到纹理通道。

---

## 常见误区

**误区一：提供色盲模式就等于色盲友好**。仅依赖独立色盲模式而非在基础设计中就确保双通道传递，会造成用户必须主动声明自己是色盲才能正常游玩——这本身就是一种体验歧视。正确做法是在默认UI中就做到颜色+形状/图标的双通道，色盲模式作为额外的颜色优化层。

**误区二：只考虑红绿色盲**。虽然Tritanopia（蓝黄色盲）仅占0.003%，但游戏大量使用蓝色作为信息颜