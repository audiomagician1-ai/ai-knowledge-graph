---
id: "cg-projection"
concept: "投影变换"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 2
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 92.4
generation_method: "intranet-llm-rewrite-v3"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v3"
  - type: "textbook"
    citation: "Shirley, P., & Marschner, S. (2009). Fundamentals of Computer Graphics (3rd ed.). A K Peters/CRC Press."
  - type: "textbook"
    citation: "Foley, J. D., van Dam, A., Feiner, S. K., & Hughes, J. F. (1990). Computer Graphics: Principles and Practice (2nd ed.). Addison-Wesley."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v3
updated_at: 2026-04-06
---

# 投影变换

## 概述

投影变换是将三维空间中的几何体映射到二维平面的数学操作，在图形渲染管线中负责将观察空间（View Space）中的顶点坐标转换为裁剪空间（Clip Space）坐标。经过投影变换后，顶点坐标会被存储为齐次坐标形式 $(x, y, z, w)$，其中 $w$ 分量不再为 1，后续通过透视除法（将 $x, y, z$ 各分量除以 $w$）才能得到归一化设备坐标（NDC，Normalized Device Coordinates）。

投影变换的概念最早随着计算机图形学在 1960–1970 年代的形成期确立。Ivan Sutherland 在 1963 年于麻省理工学院完成的博士论文中提出 Sketchpad 系统，奠定了交互式图形学与空间变换流水线的基础；1965 年他在论文《The Ultimate Display》中进一步阐述了沉浸式三维空间的构想。Jim Blinn 在 1977 年的 SIGGRAPH 论文中系统化地整理了齐次坐标在图形变换中的应用，使透视投影矩阵的推导方式沿用至今（Foley et al., 1990）。两种主流的投影类型——**透视投影**与**正交投影**——分别对应人眼感知世界的方式与工程制图的需求，适用于完全不同的应用场景。

投影变换的意义在于它将三维场景的深度信息以特定方式编码进 $z$ 分量，同时定义了可见区域（视锥体 Frustum 或正交盒 Orthographic Box），为后续的视锥体裁剪提供了标准化的坐标系。选择错误的投影类型或设置不当的参数（如近平面 $n$ 过小）会直接导致 z-fighting、深度精度不足等严重渲染问题。

---

## 核心原理：透视投影矩阵

透视投影模拟"近大远小"的视觉效果，其核心思想是：距离相机越远的物体，投影后在屏幕上占据的像素越少。OpenGL 风格的透视投影矩阵由四个参数定义：垂直视野角 $\text{fovy}$（单位：弧度）、宽高比 $\text{aspect}$、近裁剪面 $n$（near）、远裁剪面 $f$（far）。

令 $t = n \cdot \tan\!\left(\dfrac{\text{fovy}}{2}\right)$，$r = t \cdot \text{aspect}$，透视投影矩阵为：

$$
M_{\text{persp}} =
\begin{pmatrix}
n/r & 0 & 0 & 0 \\
0 & n/t & 0 & 0 \\
0 & 0 & -\dfrac{f+n}{f-n} & -\dfrac{2fn}{f-n} \\
0 & 0 & -1 & 0
\end{pmatrix}
$$

第四行中的 $-1$ 使得变换后顶点的 $w$ 分量等于原始的 $-z$（在 OpenGL 右手坐标系中，相机看向 $-z$ 轴）。透视除法后，$z$ 值被压缩到 $[-1, 1]$ 区间，但这一压缩是**非线性的**——靠近 $n$ 平面的区域精度高，靠近 $f$ 平面的区域精度急剧下降。

深度精度的量化分析表明，当使用 $b$ 位整数深度缓冲时，透视投影下两个相邻深度值之间的最小可分辨线性距离 $\Delta z$ 在远处近似为：

$$
\Delta z \approx \frac{2f^2}{n \cdot (2^b - 1)}
$$

这正是为什么 $n$ 与 $f$ 之间的比值 $f/n$ 不应超过 10000（对于 24 位深度缓冲）的实践准则的数学根源。例如，若 $n = 0.01$，$f = 10000$，则 $f/n = 1{,}000{,}000$，远处几乎所有物体的深度值将落在相同的整数区间内，产生严重 z-fighting（Shirley & Marschner, 2009）。

---

## 核心原理：正交投影矩阵

正交投影不产生近大远小的效果，平行线在投影后仍保持平行，常用于 CAD 软件、2D 游戏 UI 层和等距视角游戏。正交投影将一个轴对齐的盒子 $[l, r] \times [b, t] \times [n, f]$ 映射到 NDC 的 $[-1,1]^3$ 立方体，矩阵为：

$$
M_{\text{ortho}} =
\begin{pmatrix}
\dfrac{2}{r-l} & 0 & 0 & -\dfrac{r+l}{r-l} \\[6pt]
0 & \dfrac{2}{t-b} & 0 & -\dfrac{t+b}{t-b} \\[6pt]
0 & 0 & -\dfrac{2}{f-n} & -\dfrac{f+n}{f-n} \\[6pt]
0 & 0 & 0 & 1
\end{pmatrix}
$$

正交投影矩阵的 $w$ 行保持 $(0,0,0,1)$，因此变换后 $w$ 分量始终为 1，透视除法不改变 $x, y, z$ 的值。正交投影的深度误差均匀分布：

$$
\Delta z_{\text{ortho}} = \frac{f - n}{2^b - 1}
$$

与透视投影相比，正交投影的 $z$ 缓冲精度是**线性分布**的，深度精度问题远少于透视投影。

---

## 视锥体与裁剪空间的关系

透视投影定义的视锥体是一个四棱锥台（Frustum），由 6 个平面围成：近平面、远平面、左右上下四个侧平面。正交投影定义的则是一个矩形盒子（Orthographic Box）。投影矩阵的作用是将这两种形状分别"压扁"为标准 NDC 立方体，使得裁剪算法只需对 $[-1,1]^3$ 这一统一形状进行判断。

值得注意的是，不同图形 API 对 NDC 的约定存在差异：

- **OpenGL**：NDC 的 $z$ 范围为 $[-1, 1]$，使用右手坐标系，相机朝向 $-z$ 轴。
- **DirectX（D3D11/D3D12）**：NDC 的 $z$ 范围为 $[0, 1]$，使用左手坐标系，对应矩阵第三行系数调整为 $-f/(f-n)$ 和 $-fn/(f-n)$。
- **Vulkan**：NDC 的 $y$ 轴方向与 OpenGL 相反（向下为正），同时 $z$ 范围为 $[0, 1]$。

例如，将 OpenGL 的透视矩阵直接移植到 Vulkan 项目中，会导致画面上下翻转且深度测试完全错误——这是跨平台开发时最常见的矩阵错误之一。

---

## 实际应用

**第一人称 3D 游戏**：使用透视投影，典型 $\text{fovy}$ 设置为 60°–90°（约 $1.047$–$1.571$ 弧度）。$\text{fovy}$ 过小（如 30°）会产生"长焦压缩"感，$\text{fovy}$ 过大（如 120°）则产生鱼眼畸变。Unity 引擎中 Camera 组件的 `Field of View` 属性直接对应此参数，Unreal Engine 中对应 `Camera Field of View`，两者均以角度制（度）为单位输入，引擎内部自动转换为弧度参与矩阵计算。

例如，在 Unity 中创建一个标准第三人称相机：将 `Field of View` 设为 60，`Near Clip Plane` 设为 0.3，`Far Clip Plane` 设为 1000，则 $f/n \approx 3333$，在 24 位深度缓冲下仍可保持良好的深度精度，是工程实践中的推荐配置。

**等距策略游戏（如《文明 VI》2016年，Firaxis Games）**：使用正交投影，确保地图上不同位置的单位图标大小一致，避免透视导致远处单位缩小而影响信息读取。

**深度精度优化——Reversed-Z 技术**：现代渲染器（如 Unreal Engine 4.22 版本之后默认开启，2019年发布）将深度缓冲反转，令 $n$ 对应 $z=1$、$f$ 对应 $z=0$。配合 32 位浮点深度缓冲，这一技术显著改善了透视投影远处的 z-fighting 问题，因为 IEEE 754 浮点数在 $(0, 1]$ 区间内的精度集中在接近 0 的一侧，正好补偿了透视投影 $z$ 值的非线性压缩（Reversed-Z 技术由 Nathan Reed 于 2015 年在其博客文章《Depth Precision Visualized》中系统阐述）。

**UI 渲染**：游戏中的 HUD（抬头显示）元素通常使用正交投影，令 $n=-1$、$f=1$，将屏幕像素坐标直接映射为 NDC，绕过透视计算。以 1920×1080 分辨率为例，正交盒参数设为 $l=0, r=1920, b=0, t=1080$，即可实现"1 单位 = 1 像素"的直接映射。

---

## 常见误区

**误区一：透视除法是投影矩阵完成的**

投影矩阵本身**不执行**透视除法，它只是将顶点从观察空间变换到裁剪空间，输出的是齐次坐标 $(x_c, y_c, z_c, w_c)$。真正的除法 $(x_c/w_c,\ y_c/w_c,\ z_c/w_c)$ 由 GPU 固定管线在视锥体裁剪之后自动完成，称为"透视除法"阶段（Perspective Division）。初学者经常混淆这两个步骤，误以为乘以投影矩阵后就直接得到了 NDC 坐标。

**误区二：正交投影没有 near/far 裁剪面**

正交投影同样有 $n$ 和 $f$ 参数，它们决定了正交盒在深度方向的范围。如果将 $n$ 设为负值（如 Unity 2D 默认的 $n=-10$），超出此范围的物体同样会被裁剪。正交投影的 $n$ 可以设置为负数（物体在相机"后方"也能显示），而透视投影的 $n$ 必须为正值——否则矩阵中的 $2fn/(f-n)$ 项会产生 $z$ 值符号错误，深度测试将完全失效。

**误区三：增大 far 平面可以无限延伸可见范围**

将 $f$ 设置为极大值（如 $1{,}000{,}000$）在透视投影中会导致严重的深度精度损失。以 24 位深度缓冲为例，当 $f/n = 100{,}000$ 时，约 96% 的深度离散值被分配给距相机 $n$ 到 $2n$ 的极小范围内，远处物体的深度几乎无法区分，产生 z-fighting。正确做法是将 $f$ 设置为场景实际所需的最