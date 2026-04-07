---
id: "vfx-fluid-waterfall"
concept: "瀑布与水流"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 瀑布与水流

## 概述

瀑布与水流特效是流体模拟中专门处理**有向流动**（directed flow）场景的技术方案，其根本区别于无固定流向的湖面或海洋模拟：水流沿重力梯度与地形约束形成**可预测的单向路径**，这一特性使路径驱动（path-driven）模拟成为首选方案，而非完整求解 Navier-Stokes 方程组。工业实现中必须同时处理三种视觉现象：水流主体的层流结构（laminar flow）、跌落冲击产生的飞溅粒子，以及底部水潭的白色泡沫与翻腾气泡。

该技术的电影级应用里程碑是2003年《指环王：双塔奇谋》中瑞文戴尔（Rivendell）的多级瀑布场景，由Weta Digital使用其内部流体路径模拟工具完成，首次将分层法线动画与粒子飞溅系统组合输出为电影级画质。游戏实时领域的标志性突破则是顽皮狗（Naughty Dog）2016年发布的《神秘海域4》，其瀑布系统将粒子模拟、三层法线贴图动画与顶点着色器拉伸变形结合，在PS4硬件（1.84 TFLOPS GPU）上实现了每帧预算约0.8ms内的完整瀑布渲染，参见 (Archard & Balestra, 2016, GDC Presentation "Rendering of 'Uncharted 4'")。

---

## 核心原理

### 流速分布与路径驱动模型

河流横截面上的速度分布遵循**抛物线剖面**（parabolic profile），中心流速最大，靠近岸壁处因摩擦力衰减至零。给定截面半宽 $r$，距中心线水平距离 $d$ 处的流速为：

$$v(d) = v_{\max} \times \left(1 - \frac{d^2}{r^2}\right)$$

实现时用一条Catmull-Rom样条曲线定义水流中心线，沿样条方向滚动UV坐标，驱动纹理产生流动视觉。每段样条节点存储三个参数：截面宽度 $w$、水深 $h$、以及该节点处的标量流速 $v_{\max}$（单位 m/s），引擎在运行时插值相邻节点参数以平滑过渡。

瀑布垂直跌落段需要额外处理**重力加速拉伸**：水体在自由落体下速度持续增加，导致视觉上呈现顶部厚、底部薄的水帘形态。顶点着色器中，以瀑布总高度 $H$（米）和当前顶点距顶端的相对高度比 $\tau \in [0,1]$ 为参数，计算垂直方向网格密度压缩系数：

$$\text{scale}(\tau) = \frac{1}{1 + \frac{g \cdot \tau^2 \cdot H}{2v_0^2}}$$

其中 $g = 9.8\ \text{m/s}^2$，$v_0$ 为水流到达瀑布顶端时的初始速度。对于10米高瀑布、$v_0 = 2\ \text{m/s}$ 的典型参数，底部冲击速度约为 $\sqrt{v_0^2 + 2gH} \approx 14.3\ \text{m/s}$，底部网格压缩系数约为顶部的0.28倍，直观再现水帘向下越来越稀薄的视觉特征。

### 泡沫与飞溅的粒子系统设计

瀑布底部飞溅通常分两层独立粒子系统叠加渲染：

**大水珠层**：粒子直径 0.05–0.3m，从冲击点以半球形锥体（锥半角约60°，即整体张角120°）向外喷发，初速度向量从碰撞法线方向随机偏转，初速大小取落差高度决定的冲击速度的15%–40%（模拟非弹性碰撞能量损失）。粒子寿命 0.4–1.2s，受重力影响抛物线下落，落地后触发二级微型溅射。

**雾气层**：Billboard粒子直径等效 < 0.005m，透明度 0.03–0.08，使用加法混合（Additive Blending）堆叠出白色雾气效果。雾气粒子从冲击区域中心以极低初速（0.3–0.8 m/s）向外扩散，并叠加随机布朗运动偏移，有效模拟水雾被气流卷起的飘散感。

河流水面的泡沫分布由**流场散度**（flow divergence）$\nabla \cdot \mathbf{v}$ 驱动：散度为负（流线汇聚）的区域泡沫密度积累，散度为正（流线发散）的区域泡沫消散。以一张 512×512 的 Foam Density Texture 实时存储泡沫密度场，每帧按如下规则更新：

$$\rho_{\text{foam}}^{t+1} = \text{clamp}\left(\rho_{\text{foam}}^{t} + \Delta t \cdot (-\nabla \cdot \mathbf{v}) \cdot k_{\text{accum}} - \Delta t \cdot k_{\text{decay}}, \ 0, \ 1\right)$$

典型参数：$k_{\text{accum}} = 0.5$，$k_{\text{decay}} = 0.1$（单位 s⁻¹），使得泡沫在岩石背流区约2秒内饱和，开阔水面约10秒内消散。

### 法线贴图动画的三层叠加

单层滚动法线贴图无法重现真实水流中湍流、次级涡流与表面微扰同时存在的复杂纹理。工业标准方案叠加**三层法线贴图**：

- **主流层**：沿样条切线方向滚动，速度严格匹配路径样条存储的 $v_{\max}$，贴图分辨率 1024×1024，Tiling 系数约 2×8（横向×纵向）
- **次级涡流层**：偏转主流向约 12°–18°，速度为主层的 0.55–0.65 倍，模拟河流中常见的次级螺旋流（secondary helical flow）
- **高频微扰层**：速度为主层的 0.08–0.12 倍，贴图分辨率 256×256，高 Tiling（16×16），模拟表面张力引起的毛细纹

三层法线通过 **UDN 混合**（Unreal Developer Network Normal Blending）而非简单线性插值合并，避免法线向量归一化误差导致的高光异常：

```hlsl
float3 BlendNormals_UDN(float3 n1, float3 n2)
{
    // n1, n2 均为切线空间法线，范围[-1,1]
    return normalize(float3(n1.xy + n2.xy, n1.z));
}

float3 waterNormal = BlendNormals_UDN(
    BlendNormals_UDN(primaryNormal, secondaryNormal),
    detailNormal
);
```

瀑布帘状段还需叠加一张垂直拉伸的"条纹法线"贴图（Tiling 约 1×32），强化水帘纵向折射感，使帘面产生向下流动的光柱高光。

---

## 关键公式与算法

### 折射偏移量计算

水流平面下方内容的折射偏移（Refraction Offset）由法线贴图的 XY 分量直接驱动，偏移量需要根据水深 $d_w$ 进行限幅以避免采样到水面外的错误像素：

$$\text{offset} = n_{xy} \times k_{\text{refract}} \times \text{clamp}\left(\frac{d_w}{d_{\max}}, 0, 1\right)$$

其中 $k_{\text{refract}}$ 通常取 0.05–0.15（无量纲屏幕UV单位），$d_{\max} = 2.0\ \text{m}$ 为折射完全生效的参考水深。浅水区折射幅度受 $d_w$ 线性压制，避免河床纹理出现"穿帮"偏移。

### LOD 切换策略

```
距离 < 8m   : 三层法线 + 泡沫系统 + 粒子飞溅（完整品质）
8m – 40m    : 单层法线 + 泡沫贴图（无粒子）
40m – 120m  : 低分辨率法线 + 漫反射近似（无泡沫）
> 120m      : 静态纯色平面 + 远景雾效遮盖
```

粒子飞溅系统在距离超过 8m 后完全关闭，每个瀑布节省约 2000–5000 粒子的 GPU 粒子模拟开销，是实时场景中包含多处瀑布时的关键性能手段。

---

## 实际应用

### 游戏地图中的河流路径网络

开放世界游戏中的河流系统将整条河流建模为样条网络（Spline Network），相邻样条节点间距离通常为 4–8 米，节点属性包括：中心线位置、截面宽度（0.5–80m）、深度（0.1–10m）、流速（0.2–6 m/s）和材质 ID（用于区分清澈山溪、浑浊泥流等视觉变体）。

《巫师3：狂猎》（2015，CD Projekt Red）中的河流系统使用程序化样条工具生成了超过 60km 的可渡涉河流，每条河流实时计算玩家涉水时的阻力系数——流速超过 3 m/s 的区域会对玩家角色施加横向位移力，流速超过 5 m/s 则触发"被急流冲走"的动画状态机。

### 影视级离线瀑布模拟

电影与动画中使用完整 SPH（Smoothed Particle Hydrodynamics）或 FLIP（Fluid-Implicit-Particle）求解器模拟瀑布，典型分辨率为每立方米约 125,000–1,000,000 个粒子。Houdini 的 FLIP Solver 是目前行业标准工具（参见 SideFX 官方文档《Houdini Fluids》，2023），其 Whitewater Solver 专门处理瀑布底部的泡沫、飞溅与气泡，通过追踪流场中的**速度散度**、**曲率**和**粒子加速度**三个指标来判定白水生成位置，阈值分别约为：散度 > 0.5 s⁻¹、曲率 > 2 m⁻¹、加速度 > 15 m/s²。

### 移动端的降级实现方案

在移动设备（如 iPhone 15 的 Apple A17 Pro，GPU 带宽约 68 GB/s）上，完整三层法线+粒子方案超出预算，通常采用以下降级策略：
1. 将三层法线烘焙为一张 **Flipbook 动画纹理**（16帧，512×512），每帧间隔 0.067s，循环播放模拟流动
2. 飞溅粒子替换为一张垂直 Billboard 的**溅射序列帧纹理**（8×8 Sprite Sheet）
3. 泡沫改为 UV 滚动的静态泡沫贴图，放弃实时散度计算

该方案在 Mali-G715（中端移动 GPU）上瀑布渲染开销约 0.3ms/帧，相比完整方案降低约 73%。

---

## 常见误区

**误区一：用 Alpha 半透明直接渲染水帘导致排序错误**
水帘网格是半透明物体，若使用标准 Alpha Blend 渲染，多个重叠水帘之间会出现深度排序错误（Z-fighting）。正确做法是将水帘拆分为：不透明的深色"阴影"pass（写入深度缓冲）+ 加法混合的白色"高光"pass（不写深度），利用两次 draw call 规避半透明排序问题。

**误区二：法线贴图直接线性插值合并造成高光爆炸**
将两张法线贴图做 `lerp(n1, n2, 0.5)` 再归一化，在两张法线方向差异较大时（超过90°）会产生中间值指向错误方向的问题，导致高光出现黑斑或爆亮。必须使用 UDN 混合或 Reoriented Normal Mapping（RNM）方法（参见 Barré-Brisebois & Hill, 2012, "Blending in Detail"）。

**误区三：忽略瀑布