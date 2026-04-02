---
id: "vfx-pp-dof"
concept: "景深效果"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 景深效果

## 概述

景深效果（Depth of Field，简称 DoF）是模拟真实相机镜头焦点特性的后处理技术，通过让焦平面之外的物体产生模糊来营造视觉深度感。其物理基础来自光学原理：当镜头只能将特定距离的光线汇聚到传感器上时，其他距离的点光源会在传感器上形成一个圆形光斑，称为弥散圆（Circle of Confusion，CoC）。实时渲染中的景深效果正是通过计算每个像素的 CoC 半径来决定其模糊程度。

景深作为后处理特效在游戏引擎中的广泛应用始于 2000 年代中期，随着可编程着色器的普及而成熟。相比 Bloom 泛光需要处理整张画面的亮度扩散，景深需要精确的深度信息（来自 G-Buffer 的 Depth Buffer），并对不同区域施以不同程度的模糊，计算量与质量之间的权衡更为复杂。景深效果在电影化叙事场景中尤为重要——它能引导玩家视线聚焦于特定主体，同时以散景（Bokeh）光晕强化画面的电影质感。

## 核心原理

### 弥散圆（Circle of Confusion）的计算

CoC 半径是景深效果的核心量，决定了每个像素需要被模糊多少。其物理公式为：

**CoC = |A × (f × (d - D)) / (d × (D - f))|**

其中：
- **A** = 光圈直径（aperture diameter）
- **f** = 焦距（focal length）
- **d** = 物体到镜头的实际距离
- **D** = 焦距对焦距离（focus distance）

在实时渲染的简化版本中，通常将场景划分为三段：近景虚化区（Near Field）、焦内清晰区（In-Focus Zone）、远景虚化区（Far Field）。CoC 值被映射到 [-1, 1] 范围，负值代表近景模糊，正值代表远景模糊，0 表示完全清晰。Unreal Engine 将 CoC 半径以物理单位（厘米）存储在 R16F 格式的缓冲区中，再除以屏幕分辨率换算为 UV 空间坐标。

### 散景形状与 Bokeh 渲染

真实镜头的光圈叶片数量决定了散景的形状——六叶光圈产生六边形散景，圆形光圈产生圆形散景。实时渲染中有两种主流实现策略：

**基于 Gather（聚合）的方法**：对每个像素，在一定半径内对周围像素做加权平均。这是 Unity HDRP 和 Unreal Engine 的默认方案，半径由该像素的 CoC 值决定，最大采样半径通常限制在 16–32 像素以控制性能开销。

**基于 Scatter（散射）的方法**：将每个高亮像素作为一个 Sprite 向外扩散，能产生正确的前景遮挡和物理准确的散景形状，但需要渲染大量几何体，性能代价更高，通常仅用于离线渲染或高端平台。

### 近景与远景的分层处理

景深效果最棘手的问题是**近景遮挡**（Near Field Bleeding）：当清晰的背景物体靠近模糊的前景物体时，模糊会错误地"渗入"清晰区域。标准解决方案是将近景层和远景层分别渲染到独立的半分辨率缓冲区（Half-Resolution Buffer），远景层只采集 CoC > 0 的像素，近景层只采集 CoC < 0 的像素，再通过 Alpha 混合将两层合成回全分辨率图像。Unreal Engine 5 的 DiaphragmDOF 系统进一步引入了前景层的独立散射通道，将近景误差控制在视觉阈值以下。

## 实际应用

**电影化过场动画**：在对话镜头中，将对焦距离设为角色脸部（约 2–3 米），光圈值设为 f/1.8，背景建筑因 CoC 半径超过 10 像素而产生明显散景，突出人物表情。《赛博朋克 2077》的过场动画广泛使用此策略强化电影感。

**交互式引导视线**：第三人称 RPG 游戏中，当主角拾取道具时，将焦平面锁定在道具距离，使界面外其他场景对象模糊，吸引玩家注意力。这种"程序性对焦"需要在运行时平滑插值 Focus Distance 参数，通常使用线性插值或弹簧阻尼（Spring Damper）以防止突变。

**性能分档实现**：移动端为保持帧率，常用单次 Gaussian Blur 近似 CoC 模糊，仅对画面最远 20% 的像素施以固定半径模糊；PC 高品质模式则启用完整的双层 Bokeh 散射，并使用时域积累（Temporal Accumulation）减少采样数量，将每帧采样数从 64 次降至 16 次。

## 常见误区

**误区一：CoC 越大模糊越好**
许多开发者将光圈值（F-stop）设置过低（如 f/0.8），导致 CoC 半径超出采样内核范围，出现边缘"切割"伪影（Clipping Artifact）。实际上，当 CoC 半径超过最大采样半径（通常 16–32px）时，Gather 方案无法正确采集所有贡献像素，需切换为多次迭代或 Scatter 方案，否则模糊边缘会出现锯齿状硬边。

**误区二：景深只需要简单的 Gaussian Blur**
Gaussian 模糊对所有方向权重相等，无法产生真实镜头的圆形或多边形散景形状，也无法体现光学上亮点对散景形状贡献更大的特性（即亮部散景比暗部更明显）。真实散景需要在 Gather 阶段使用形状掩码（Shape Mask）进行加权采样，或在 Scatter 阶段用带透明度的圆形 Sprite 叠加。

**误区三：前景和背景可以用同一个模糊通道处理**
将近景（负 CoC）与远景（正 CoC）混入同一个模糊 Pass 会导致颜色渗透：清晰中景物体的颜色会被附近的大 CoC 像素"吸走"，产生错误的光晕。这正是分层处理策略存在的原因，必须严格隔离正负 CoC 区域的模糊计算。

## 知识关联

景深效果以 **Bloom 泛光**的管线结构为参照——两者都在 Tone Mapping 之前写入 HDR 缓冲区，且都使用降分辨率通道（Downscale Pass）控制性能。但景深额外依赖 **Depth Buffer** 中的线性深度值，必须在深度重建步骤后才能计算 CoC，这是其在后处理顺序中排在 Bloom 之后的技术原因。

景深与**运动模糊**共同构成相机模拟的两大模糊系统。运动模糊处理的是时间维度的速度向量（来自 Motion Vector Buffer），而景深处理的是空间维度的深度偏差（来自 Depth Buffer）；两者可叠加但计算完全独立，合并时需注意对同一像素的多次模糊会造成过度软化，高端实现会将两者的贡献量化后按权重混合，避免焦外运动物体被双重模糊。