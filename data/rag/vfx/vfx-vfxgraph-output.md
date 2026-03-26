---
id: "vfx-vfxgraph-output"
concept: "输出模式"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 输出模式

## 概述

输出模式（Output Context）是VFX Graph中控制粒子最终如何被渲染为可见几何体的配置层。每个粒子系统必须至少绑定一个Output Context，否则粒子计算虽然在GPU上运行，却不会产生任何画面输出。VFX Graph提供了Quad、Mesh、Line、Point（点云）、Distortion Quad等多种Output类型，每种类型对应不同的顶点结构和渲染管线配置。

这套输出架构起源于Unity在2018年引入VFX Graph时对传统粒子系统的重新设计。传统的Particle System使用CPU端的Billboard渲染，而VFX Graph的Output Context将渲染数据完全保留在GPU显存中，通过`DrawProceduralIndirect`调用实现零CPU开销的几何体生成。这一设计使单帧渲染百万级粒子成为可能。

选择正确的输出模式对性能和视觉质量影响极大。Quad模式每个粒子生成2个三角形（6个顶点索引），而Mesh模式的顶点数取决于所绑定网格的多边形数量——一个100面的网格意味着每粒子消耗100倍于Quad的顶点处理开销。在规划特效时，必须从渲染预算角度权衡视觉细节与粒子数量的关系。

## 核心原理

### Quad输出：Billboard与朝向模式

Quad Output是最常用的输出类型，本质是一个始终面向摄像机或特定方向的平面四边形。在VFX Graph中，Quad的朝向由`Orientation`参数控制，提供以下模式：

- **Camera**：四边形法线始终指向主摄像机，适合烟雾、火花等效果
- **Fixed Axis**：绕固定轴旋转面向摄像机，常用于植被粒子
- **Along Velocity**：四边形沿速度方向拉伸，适合拖尾轨迹
- **Free**：完全由粒子的`Angle`属性决定朝向，适合模拟飘落碎片

Quad Output还内置了`UV Mode`设置，支持`Simple`（整张贴图）、`Flipbook`（序列帧动画，需配置`Flipbook Size`为列数×行数，如4×4=16帧）和`Flipbook Blend`（帧间线性插值，消除序列帧跳帧感）三种UV采样模式。

### Mesh输出：三维网格实例化

Mesh Output允许将任意三维网格作为粒子的渲染形体，其核心是GPU Instancing——所有粒子共享同一份网格数据，每个实例通过粒子属性（位置、旋转、缩放、颜色）进行变换。在Inspector中需要手动指定`Mesh`字段，若留空则不渲染任何内容。

Mesh Output支持`Mesh Count`参数（最大值为4），允许在单个Output中随机选择多个网格变体，通过`Mesh Index`属性控制每粒子使用哪个网格。这一功能常用于碎石、落叶等需要形状多样性的效果，避免重复感。

需要注意的是，Mesh Output默认不支持蒙皮动画（Skinned Mesh）。若需要粒子播放骨骼动画，必须借助烘焙到贴图的顶点动画（VAT，Vertex Animation Texture）技术，将动画数据存储为`Position Map`贴图，再通过`Set Position from Map`Block采样。

### Line输出：连线与轨迹

Line Output每个粒子渲染为一条线段，由`Target Position`属性定义线段终点，粒子自身位置为起点。线段宽度由`Width`属性控制，单位为世界空间米。Line Output不具备朝向属性，其宽度展开方向始终垂直于摄像机视线，本质上是一个沿连线方向拉伸的Quad。

在Lightning（闪电）、粒子轨迹、弹道连线等效果中，Line Output通常搭配`Get Position from Graph`或Strip类型的粒子系统使用。当粒子数量为N时，若要形成连续折线，需使用**Strip Output**（Line的变体），它会按粒子生成顺序依次连接相邻粒子，形成N-1段连续线段。

### 点云输出与Distortion模式

Point Output将每个粒子渲染为屏幕上的单个像素点，无几何体生成，是开销最低的输出模式，适合远景群聚粒子或调试时可视化粒子分布。其`Point Size`参数以像素为单位，在高分辨率屏幕上显示为固定像素大小而非世界空间大小，因此近距离观察时效果较差。

Distortion Quad Output是特殊的折射扭曲模式，它不渲染粒子的颜色，而是采样粒子贴图的RG通道作为屏幕UV偏移量，对背景图像进行扭曲。该模式需要在Project Settings中启用`Distortion`后处理，渲染队列固定为Transparent之前的专用Distortion Pass。

## 实际应用

**爆炸碎片效果**：主体破碎感使用Mesh Output绑定3-4个不规则碎片网格，`Mesh Count`设为3，每粒子随机选择网格变体；同时叠加一个Quad Output渲染烟雾贴图，Quad使用`Flipbook`模式加载8×8=64帧爆炸动画序列。两个Output Context共享同一个Update Context，复用速度、寿命等属性计算，节省GPU资源。

**激光束效果**：使用Line Output，将`Target Position`绑定到Raycast Hit Point属性（由碰撞检测Block输出），`Width`设为0.05米，配合Emission颜色HDR值超过1.0实现Bloom泛光。当碰撞检测未命中时，`Target Position`回退到沿方向向量延伸50米处的默认终点。

**热浪扭曲**：使用Distortion Quad Output，绑定一张噪声法线贴图，`UV Mode`设为`Flipbook`以驱动动态流动感，`Distortion Intensity`值设为0.02-0.05之间以避免过度扭曲破坏画面可读性。

## 常见误区

**误区一：认为多个Output Context会重复计算粒子物理**。实际上，VFX Graph的Spawn→Initialize→Update→Output流水线中，物理计算（碰撞、力场、速度积分）全部在Update Context完成，多个Output Context只是读取粒子属性并生成不同几何体，不会重复执行物理模拟。因此为一个系统添加第二个Output（如同时输出Quad烟雾和Mesh碎片）的额外开销仅为渲染端的顶点处理成本。

**误区二：混淆Quad的`Scale`与粒子的`Size`属性**。Quad Output的最终尺寸由粒子属性`Size`（在Initialize或Update中设置）与Output Context中`Scale`乘数共同决定，最终宽度 = `Size.x × Scale.x`。若直接在Quad Output的Scale中填入绝对尺寸而不修改粒子Size，会导致所有粒子大小相同，无法实现逐粒子的随机尺寸变化。正确做法是在Initialize中用`Random Number`节点驱动`Set Size`，Output的Scale保持为(1,1,1)。

**误区三：Point Output等同于Quad Output的极小尺寸**。Point Output渲染为屏幕空间固定像素，不受摄像机距离影响；而极小尺寸的Quad依然是世界空间几何体，远距离会缩小到亚像素级并被剔除。两者的渲染行为、性能开销以及在不同分辨率下的表现完全不同，不可互替。

## 知识关联

学习输出模式需要先理解碰撞与交互系统——碰撞Block输出的`Hit Position`和`Hit Normal`属性是Line Output中`Target Position`的常见数据来源，碰撞事件也常用于触发从一种输出模式切换粒子的渲染状态（通过Event触发新的Spawn）。

掌握输出模式后，下一步学习SDF交互时会遇到输出模式的进阶应用：SDF场的梯度信息可以驱动Mesh Output中粒子的朝向（让粒子法线沿SDF曲面切线排列），以及通过Distortion Quad与SDF距离场结合实现流体边缘的折射扭曲效果。此外，深入使用Mesh Output的VAT技术也与SDF烘焙流程高度相关。