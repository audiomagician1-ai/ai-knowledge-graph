---
id: "vfx-shader-depth-fade"
concept: "深度渐变"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 深度渐变

## 概述

深度渐变（Depth Fade）是一种基于场景深度缓冲区（Depth Buffer）的粒子透明度控制技术，其核心目的是消除粒子与不透明几何体相交时产生的硬边切割瑕疵。当一个半透明粒子平面插入不透明地面或墙壁时，两者交界处会出现突兀的直线裂缝，深度渐变通过在交叉区域内自动降低粒子的 Alpha 值来柔化这条边界，使粒子看起来自然地融入场景。

该技术最早随着可编程 GPU 管线的普及（约 2003–2005 年，DirectX 9 时代）进入实时渲染工作流。传统的粒子软件相交（Soft Particle）实现依赖逐像素读取深度缓冲区并执行比较运算，在 UE4/Unity HDRP 等现代引擎中，该功能已被封装为单一节点，底层仍调用 `tex2Dproj(depthSampler, screenPos)` 类型的采样指令。

深度渐变在烟雾、火焰、水花、尘土等大面积半透明粒子特效中不可或缺。没有深度渐变的火焰贴图在接触地板时会暴露出四边形（Quad）边界，直接破坏视觉沉浸感；而开启深度渐变后，同一粒子会在距离几何体约 10–50 个世界单位（可调）的范围内线性或指数式衰减至完全透明。

---

## 核心原理

### 深度差值计算

深度渐变的数学基础是逐像素的深度差值（Depth Difference）。设场景深度缓冲中存储的不透明物体深度为 `SceneDepth`，当前像素所在粒子平面的线性深度为 `PixelDepth`，则：

```
DepthDiff = SceneDepth - PixelDepth
```

当粒子完全悬浮在空中时，`DepthDiff` 为较大正值；当粒子平面与不透明表面相交时，`DepthDiff` 趋近于 0 甚至为负。将此差值除以一个"淡出距离"参数 `FadeDistance`，再用 `saturate()` 夹紧至 [0, 1]，即可得到遮罩权重：

```
FadeMask = saturate(DepthDiff / FadeDistance)
```

该值直接乘以粒子原始 Alpha，即完成线性深度渐变。`FadeDistance` 通常取值 50–200（厘米或游戏单位），过小会导致粒子在远离表面时仍过早透明，过大则渐变区域过宽、效果反而不自然。

### 非线性（指数型）渐变

线性渐变在某些材质（如浓烟）上会显得过于机械，改用指数公式可获得更平滑的衰减曲线：

```
FadeMask = saturate(1 - exp(-FadeRate * DepthDiff))
```

其中 `FadeRate` 控制衰减陡峭程度，典型值为 0.02–0.1（单位为 1/游戏单位）。`FadeRate = 0.05` 时，距离不透明表面 20 单位处粒子 Alpha 约为 63%，符合 e 指数的自然衰减特性。UE5 的 `Depth Fade` 节点内部默认使用线性版本，需手动替换为 Power 节点实现指数变体。

### 交叉淡出（Cross Fade）扩展

当两张半透明粒子贴图彼此叠加时，同样会产生硬边——此时可将深度渐变思路扩展为"交叉淡出"：对粒子 A 和粒子 B 分别计算各自与对方深度面的距离差，用该差值混合两者的 Alpha 权重：

```
BlendWeight = saturate((DepthB - DepthA) / CrossFadeRange)
FinalColorA = ColorA * (1 - BlendWeight)
FinalColorB = ColorB * BlendWeight
```

此方法在瀑布水流与水面交接、火焰与地面冲击波叠加等场景中频繁使用，是深度渐变的直接延伸应用。

---

## 实际应用

**营地篝火地面接触**：篝火底部火焰粒子沿 Y 轴扩散，粒子 Quad 不可避免地与地面网格相交。将 `FadeDistance` 设为 30 个单位，可使火焰粒子在接触地面前 30 单位内逐渐消隐，视觉上呈现火焰"燃烧进"地面的效果，而非切穿地面。

**水下泡泡与水面交叉**：泡泡粒子上浮并穿透水面时，需要在水面处执行交叉淡出。将水面深度作为参照，`CrossFadeRange = 15`，泡泡在距离水面 15 单位范围内 Alpha 线性降低，从而模拟泡泡被水面张力破裂吸收的视觉效果。

**沙尘暴贴地烟雾**：沙尘粒子铺满地面时，若不加深度渐变，所有粒子底边会整齐切割地形，暴露出地形高低起伏与粒子平面不吻合的问题。深度渐变会针对每一处高低地形的深度值独立计算 `FadeMask`，自适应地消除地形任意坡度位置的硬边，无需美术手动调整每个发射器高度。

---

## 常见误区

**误区一：认为 FadeDistance 越大越好**。将 `FadeDistance` 设置为 500 甚至更高，会导致即便粒子悬浮于距地面很高处也已大幅透明，粒子整体密度和可见度严重下降。正确做法是根据粒子的物理尺寸设定——一张直径 80 单位的烟雾粒子，其 `FadeDistance` 建议不超过粒子半径的 50%，即约 40 单位。

**误区二：将深度渐变应用于不透明（Opaque）材质**。深度渐变依赖 Alpha 乘法来降低不透明度，若材质混合模式为 Opaque，`FadeMask` 对最终像素颜色毫无影响。该技术仅对 Translucent 或 Additive 混合模式的材质有效，Masked 模式下需额外将 `FadeMask` 接入 Opacity Mask 输入端且阈值须低于 1.0。

**误区三：在移动端直接使用深度渐变而不测试性能**。读取深度缓冲区（`SceneDepth` 节点）在部分 OpenGL ES 3.0 设备上会造成 GPU 管线停顿（Pipeline Stall），因为深度缓冲区在某些 Tile-Based 架构（如 Mali-G76）中并非随时可读。移动端建议使用低频 `CustomDepth` 替代方案，或在 LOD 较远时完全关闭深度渐变节点。

---

## 知识关联

深度渐变建立在**遮罩技术**的基础之上：遮罩技术教会我们如何用一张灰度图控制像素的可见区域，而深度渐变本质上是一张**动态生成的程序化遮罩**——其遮罩值不来自纹理，而是由实时深度比较运算得出的标量。理解 UV 遮罩的乘法合成逻辑，是正确连接深度渐变 `FadeMask` 到 Alpha 输入端的前提。

进入下一阶段的**极坐标变换**学习时，会接触到以像素到中心点距离为变量的径向渐变运算。极坐标变换中的径向距离场与深度渐变中的深度差值场，本质上都是"以某个参照量计算距离并映射为权重"的思路，两者的 `saturate(distance / range)` 模式完全一致，只是参照空间从屏幕空间深度切换到了纹理空间极径。掌握深度渐变中深度差值归一化的推导过程，可以直接加速理解极坐标变换中径向渐变的构造逻辑。