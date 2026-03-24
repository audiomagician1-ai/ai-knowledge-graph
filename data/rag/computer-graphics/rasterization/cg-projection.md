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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 投影变换

## 概述

投影变换是将三维空间中的几何体映射到二维平面的数学操作，在光栅化渲染管线中负责把观察空间（View Space）的顶点坐标转换为裁剪空间（Clip Space）坐标。这一步骤在顶点着色器阶段执行，输出的坐标称为裁剪坐标，之后GPU会自动完成透视除法（除以w分量）得到归一化设备坐标（NDC）。

投影变换分为两大类：**透视投影（Perspective Projection）**和**正交投影（Orthographic Projection）**。透视投影模拟人眼和相机的成像规律，近大远小；正交投影则保持平行线依然平行，不产生近大远小的效果。OpenGL于1992年在其规范中正式确立了基于 $[-1,1]^3$ NDC立方体的投影矩阵标准，Direct3D则采用z方向为 $[0,1]$ 的约定，两者矩阵在z行存在差异。

投影变换的重要性体现在两个方面：一是它定义了**视锥体（Frustum）**的形状，决定哪些几何体会被裁剪掉；二是它将深度信息编码进w分量，透视投影后的w值等于原始z的相反数（$w = -z_{view}$），这为后续的透视校正插值提供了数学基础。

---

## 核心原理

### 透视投影矩阵的推导

透视投影通过一个视锥体来定义可见区域，视锥体由近裁剪面距离 $n$、远裁剪面距离 $f$、垂直视场角 $\text{fovy}$（Field of View Y）以及宽高比 $\text{aspect}$ 四个参数确定。令：

$$
t = n \cdot \tan\left(\frac{\text{fovy}}{2}\right), \quad r = t \cdot \text{aspect}
$$

其中 $t$ 为近裁剪面的半高，$r$ 为半宽。OpenGL约定相机沿 $-z$ 方向看，透视投影矩阵为：

$$
P_{persp} = \begin{pmatrix} \frac{n}{r} & 0 & 0 & 0 \\ 0 & \frac{n}{t} & 0 & 0 \\ 0 & 0 & -\frac{f+n}{f-n} & -\frac{2fn}{f-n} \\ 0 & 0 & -1 & 0 \end{pmatrix}
$$

第四行的 $[0, 0, -1, 0]$ 将观察空间的 $z_{view}$ 存入裁剪坐标的 $w_{clip}$，使得 $w_{clip} = -z_{view}$。透视除法 $x_{ndc} = x_{clip}/w_{clip}$ 正是利用这个w值实现近大远小的效果。

### 正交投影矩阵的推导

正交投影将一个轴对齐包围盒（AABB）映射到NDC立方体，包围盒由六个参数 $l, r, b, t, n, f$（左、右、下、上、近、远）定义。其矩阵为：

$$
P_{ortho} = \begin{pmatrix} \frac{2}{r-l} & 0 & 0 & -\frac{r+l}{r-l} \\ 0 & \frac{2}{t-b} & 0 & -\frac{t+b}{t-b} \\ 0 & 0 & -\frac{2}{f-n} & -\frac{f+n}{f-n} \\ 0 & 0 & 0 & 1 \end{pmatrix}
$$

注意正交投影矩阵的第四行为 $[0,0,0,1]$，输出的 $w_{clip}$ 始终等于1，因此不发生透视除法意义上的缩放，平行关系得以保留。

### 深度非线性与精度问题

透视投影后，NDC中的深度值 $z_{ndc}$ 与观察空间深度 $z_{view}$ 之间呈**非线性关系**：

$$
z_{ndc} = -\frac{f+n}{f-n} - \frac{2fn}{(f-n) \cdot z_{view}}
$$

当 $f/n$ 比值（称为远近比）增大时，深度值在靠近远裁剪面的区域急剧压缩，导致**z-fighting**现象。例如 $n=0.1, f=1000$ 时，远近比为10000，超过99%的深度精度集中在靠近近裁剪面的1%空间内。解决方案包括增大近裁剪面距离、使用**反转深度（Reversed-Z）**技术（将深度范围改为 $[1,0]$），或使用对数深度缓冲。

---

## 实际应用

**游戏引擎中的透视投影**：Unity默认垂直视场角为60°，宽高比由屏幕分辨率自动计算。在C#中调用 `Camera.projectionMatrix` 可直接获取该4×4透视矩阵；在GLSL顶点着色器中，`gl_Position = projection * view * model * vec4(pos, 1.0)` 这一标准写法的 `projection` 即为透视投影矩阵。

**工程与CAD软件中的正交投影**：AutoCAD、Blender的"顶视图"均使用正交投影，因为正交投影保持了长度和角度的可量测性——平行于投影平面的线段在投影后长度比例不变。建筑图纸的正视图、俯视图本质上都是正交投影的结果。

**VR头显中的非对称视锥体**：HTC Vive等头显为每只眼睛使用不同的 $l, r, t, b$ 参数构建**非对称（Off-Axis）透视矩阵**，而非简单地平移相机。这种做法能更准确地模拟人眼瞳距偏移，减少畸变，技术上通过单独设置四个裁剪面参数（而非使用fovy+aspect）来实现。

---

## 常见误区

**误区1：认为透视除法是投影矩阵本身完成的。**
投影矩阵只负责将坐标变换到裁剪空间，输出的是齐次坐标 $(x_c, y_c, z_c, w_c)$，透视除法 $\mathbf{p}_{ndc} = (x_c/w_c, y_c/w_c, z_c/w_c)$ 是GPU在**光栅化前自动执行**的固定操作，不在着色器内手动完成（除非使用自定义裁剪平面）。混淆这两步会导致对裁剪测试逻辑的误解——裁剪判断是在裁剪空间用 $-w_c \leq x_c \leq w_c$ 等不等式完成的，而非在NDC空间。

**误区2：近裁剪面距离 $n$ 越小越好。**
很多初学者将 $n$ 设置为0.001甚至更小，期望"看到更近的物体"，但这会使远近比 $f/n$ 极大，深度缓冲精度急剧下降。对于float32深度缓冲（24位定点），当 $n=0.001, f=1000$ 时，远近比达到100万，距离相机5米和6米的两个平面在深度缓冲中可能映射到同一个整数值，产生严重的z-fighting。实践中 $n$ 通常设置在0.1到1.0之间。

**误区3：正交投影和透视投影只是视觉风格差异。**
两者在技术上有本质区别：正交投影的 $w_{clip}=1$，透视校正插值退化为线性插值；而透视投影需要透视校正的属性插值（如纹理坐标），公式为 $\phi = \frac{\phi_0/w_0 \cdot (1-t) + \phi_1/w_1 \cdot t}{1/w_0 \cdot (1-t) + 1/w_1 \cdot t}$。在正交模式下误用透视校正公式，或在透视模式下使用简单线性插值，都会导致纹理贴图产生明显错误。

---

## 知识关联

**前置概念——顶点变换**：投影矩阵接收的输入是已经经过模型变换（Model）和视图变换（View）的观察空间坐标，完整变换链为 $M_{clip} = P \cdot V \cdot M$。若视图矩阵将相机对齐到 $-z$ 轴方向不正确，投影矩阵的 $w=-z$ 约定将产生负的w值导致图像翻转，因此两者的坐标系约定必须一致。

**后续概念——视口变换**：投影变换完成并经过透视除法后，NDC坐标范围为 $[-1,1]^3$（OpenGL）。视口变换负责将NDC的xy坐标映射到屏幕像素坐标，变换公式为 $x_{screen} = \frac{w_{viewport}}{2} \cdot (x_{ndc}+1) + x_{origin}$，这一步不再涉及z坐标的缩放，而是直接将 $z_{ndc}$ 重映射到深度缓冲范围 $[z_{near}, z_{far}]$（默认为 $[0,1]$）。
