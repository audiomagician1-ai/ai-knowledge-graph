---
id: "3da-bake-position-map"
concept: "位置贴图"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 位置贴图

## 概述

位置贴图（Position Map），全称为 World Position Map 或 Object Position Map，是一种将三维空间中顶点或像素的坐标信息直接编码进 RGB 通道的特殊烘焙贴图。贴图中每个像素的 R、G、B 通道分别存储对应表面点的 X、Y、Z 坐标值，使得一张静态的 2D 图像能够携带完整的三维空间位置数据。

位置贴图的概念随着离线渲染和程序化着色器技术的成熟而逐渐普及，在 Houdini、Substance Designer 等工具中被广泛支持。Substance Designer 在 2018 年前后将 World Space Position 和 Object Space Position 作为标准烘焙器正式内置，显著降低了程序化材质工作流中使用位置信息的门槛。

位置贴图的价值在于：它把需要在运行时或渲染时实时计算的空间坐标"预先烘焙"成贴图，让只接受贴图输入的程序化节点（如 Substance 的 Histogram Scan）也能基于真实三维坐标进行遮罩生成，而不必依赖 UV 展开的方式来模拟空间分布规律。

---

## 核心原理

### 坐标空间与通道编码

位置贴图分为两种主要类型：**Object Space Position Map** 以模型自身局部原点为基准，坐标随模型变换而变化；**World Space Position Map** 以场景世界原点为基准，记录的是绝对世界坐标。编码时，浮点坐标值通常被重映射到 [0, 1] 区间后存入 8-bit 或 16-bit 的 RGB 通道。16-bit（半精度浮点，EXR 格式）的位置贴图精度远优于 8-bit，因为 8-bit 仅有 256 级灰阶，在大尺寸模型上会产生明显的色阶断层（Banding）。

对于 Object Space 版本，若模型的包围盒范围为 (−1, −1, −1) 到 (1, 1, 1)，则中心点 (0, 0, 0) 对应 RGB 值 (0.5, 0.5, 0.5)，正 X 轴端点对应 R 通道的最大值 1.0，即纯红色。这一编码规则是读取和调试位置贴图的关键依据。

### 烘焙参数设置

在 Marmoset Toolbag 或 Substance Painter 的烘焙器中烘焙位置贴图时，需要特别注意**归一化范围**的设置。不同工具对坐标归一化的处理方式不同：Substance Painter 的 Position 烘焙器默认以模型的 Object Space 包围盒做自动归一化，而 Marmoset Toolbag 允许手动指定坐标范围的最小值和最大值，以确保不同网格烘焙出的位置贴图具有可比性。当多个 Mesh 组合使用同一张位置贴图时，必须统一归一化范围，否则各部件的颜色梯度含义将不一致。

### 坐标梯度的方向性

位置贴图最直观的特征是其从模型底部到顶部（Y轴方向）会产生一个从黑到绿（或从绿到白）的连续渐变，这个渐变代表了世界/物体空间中的高度信息。正是这种方向性梯度使其在程序化着色中极具价值——通过对 G 通道（Y轴）进行 Levels 或 Histogram Scan 操作，可以精确控制材质效果在高度上的分布起止范围，例如令锈迹只出现在模型底部 30% 的区域，或让苔藓仅生长在水平面以上某个特定高度区间。

---

## 实际应用

**高度驱动的污垢分布**：在 Substance Designer 中，将位置贴图的 G 通道（Y轴坐标）连接到 Histogram Scan 节点，调整 Position 和 Width 参数，即可生成一条沿物体高度分布的水平脏迹遮罩。相较于使用 Curvature 或 AO 贴图来近似高度信息，位置贴图的高度遮罩在视觉上更为准确，尤其适用于垂直细节丰富的道具（如油罐、邮筒）。

**程序化分层材质**：游戏场景中的巨型岩石或建筑构件，往往需要在不同高度呈现不同材质层（底部泥土、中部岩石、顶部积雪）。通过烘焙 World Space Position Map 并在着色器中对 Y 通道进行阈值采样，可以在不手动绘制 Vertex Color 或 Mask 的情况下，自动生成垂直分层遮罩，节省大量手绘时间。

**X/Z 轴方向渐变**：除高度之外，R 通道（X轴）和 B 通道（Z轴）同样可用于生成水平方向的程序化遮罩。例如对一根横向管道，可用 R 通道控制管道两端的锈蚀程度差异，模拟真实管道因液体流向不同而产生的不对称老化效果。

**与法线贴图配合的坡面检测**：将 Object Space Normal Map 的 Y 通道（表面朝上分量）与 Position Map 的 Y 通道相乘，可同时满足"高度够高"且"表面朝上"两个条件，精确定位出模型上最适合积雪或苔藓生长的水平表面区域，这是单独使用任一贴图都难以准确实现的效果。

---

## 常见误区

**误区一：认为位置贴图等同于高度贴图（Height Map）**
高度贴图存储的是单一方向上距离参考面的偏移量，通常用于视差遮蔽或置换，其灰度值对应几何体的法线方向位移。位置贴图存储的是三轴完整坐标，RGB 三通道各自独立携带空间信息，两者用途和数据结构根本不同。将位置贴图的某个单通道误用为高度贴图输入到置换节点，会因值域不匹配而产生错误的几何形变。

**误区二：用 8-bit PNG 格式保存位置贴图**
由于位置坐标是连续的浮点数据，存入 8-bit 格式时会被量化为 0–255 的整数，导致在大范围渐变区域出现明显的色带（Posterization）。正确做法是保存为 16-bit 或 32-bit EXR/TIFF 格式，在 Substance Designer 的工程设置中将位置贴图的格式设为"L16"或"RGBA Float"，才能保留足够的坐标精度。

**误区三：Object Space 与 World Space 位置贴图可以互换使用**
两者的区别不仅在于参考原点不同。当模型在场景中被旋转或缩放后，Object Space 位置贴图的坐标值不变，而 World Space 位置贴图会随变换矩阵改变。若一个道具在游戏引擎中会被动态放置在不同位置，应使用 Object Space 版本；若需要多个不同模型在场景中保持一致的世界坐标高度参考（如地形与建筑的雪线对齐），则应使用 World Space 版本。

---

## 知识关联

位置贴图的烘焙依赖于**烘焙概述**中介绍的光线投射（Ray Casting）机制——烘焙器从低模表面向高模发射射线，命中点的坐标即被记录到对应 UV 像素中。理解 Object Space 与 World Space 的区别，需要掌握变换矩阵（TRS Matrix）的基础知识，因为两种位置贴图本质上是在不同坐标系下采样同一空间点。

在 Substance Designer 的程序化工作流中，位置贴图常与 **Ambient Occlusion 贴图**、**Curvature 贴图**配合使用，三者共同构成程序化遮罩生成的基础信息层。位置贴图负责提供空间分布规律（高度、水平位置），AO 负责凹陷区域识别，Curvature 负责边缘和折痕识别，三者组合可覆盖绝大多数写实材质的程序化需求。