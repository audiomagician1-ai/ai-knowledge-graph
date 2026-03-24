---
id: "cg-normal-mapping"
concept: "法线贴图"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 法线贴图

## 概述

法线贴图（Normal Mapping）是一种通过在纹理中存储表面法向量信息、从而在不增加几何面数的前提下模拟细节凹凸感的渲染技术。其核心思路是：用一张 RGB 图像的三个颜色通道分别编码法向量的 X、Y、Z 分量，在光照计算阶段将这些"伪造"的法线代入光照方程，使低面数模型呈现出高面数模型才有的细节质感。

该技术由 Jim Blinn 于 1978 年提出的凹凸贴图（Bump Mapping）演化而来。Blinn 的原始方案只存储高度差（单通道），需要在着色阶段通过偏导数计算近似法线，计算开销较高且精度有限。1990 年代末，游戏工业将存储完整法向量的法线贴图方案推向主流，id Software 在《雷神之锤 III》（1999 年）中大规模应用了这一技术，彻底改变了实时渲染对几何细节的处理方式。

法线贴图之所以重要，在于它用一张 24 位 RGB 纹理就能将原本需要数十万三角面才能表达的表面细节压缩进来，极大降低了 GPU 的顶点处理负担，同时保留了逐像素（per-pixel）级别的光照精度。

---

## 核心原理

### 切线空间与 TBN 矩阵

法线贴图最常见的存储格式是**切线空间法线贴图**。切线空间（Tangent Space）是一个依附于每个顶点、随曲面弯曲而变化的局部坐标系，由三个互相正交的向量构成：

- **T（Tangent，切线）**：沿 UV 坐标 U 方向延伸
- **B（Bitangent/Binormal，副切线）**：沿 UV 坐标 V 方向延伸
- **N（Normal，法线）**：垂直于曲面，指向外侧

将这三个向量按列（或按行，取决于约定）排列，即构成 **TBN 矩阵**：

$$
TBN = \begin{bmatrix} T_x & B_x & N_x \\ T_y & B_y & N_y \\ T_z & B_z & N_z \end{bmatrix}
$$

TBN 矩阵是一个从切线空间到世界空间（或视图空间）的变换矩阵。着色时，从法线贴图中采样得到的向量处于切线空间，需要左乘 TBN 矩阵才能转换为世界空间法线，参与后续的光照计算。

### 切线与副切线的计算

T 和 B 向量通过三角形的顶点位置与 UV 坐标联立方程推导。设三角形两条边向量为 $\Delta P_1$、$\Delta P_2$，对应 UV 差值为 $(\Delta u_1, \Delta v_1)$、$(\Delta u_2, \Delta v_2)$，则：

$$
\begin{bmatrix} T \\ B \end{bmatrix} = \frac{1}{\Delta u_1 \Delta v_2 - \Delta u_2 \Delta v_1} \begin{bmatrix} \Delta v_2 & -\Delta v_1 \\ -\Delta u_2 & \Delta u_1 \end{bmatrix} \begin{bmatrix} \Delta P_1 \\ \Delta P_2 \end{bmatrix}
$$

分母 $\Delta u_1 \Delta v_2 - \Delta u_2 \Delta v_1$ 本质上是 UV 空间中该三角形面积的两倍；若其趋近于零（即 UV 展开退化），则 TBN 矩阵数值会发散，这是实践中需要专门处理的退化情况。

### 法线贴图的颜色编码规范

切线空间法线贴图在视觉上呈现为以蓝紫色为主的图像，原因在于未扰动的表面法线在切线空间中为 $(0, 0, 1)$，映射到 $[0, 1]$ 颜色范围后变为 $(0.5, 0.5, 1.0)$，即浅蓝色。解码公式为：

$$
n_{tangent} = \text{textureSample} \times 2.0 - 1.0
$$

其中 X、Y 分量编码切线空间内的横向偏转，Z 分量始终为正（朝向表面外侧），这也意味着切线空间法线贴图可以被**镜像复用**——同一张贴图可以贴在模型左右对称的两侧，节省纹理内存。

---

## 实际应用

**游戏角色皮肤与盔甲制作**：美术人员先用 ZBrush 或 Mudbox 雕刻数百万面的高精度模型，再通过"烘焙"（Baking）工具（如 Marmoset Toolbag、Substance Painter）将高模与低模之间的几何差异投影为法线贴图，存储为 16 位或 8 位 PNG/TGA 文件。低模通常只有 5,000～20,000 个三角面，而烘焙出的法线贴图可令其在光照下呈现出原高模数百万面的凹凸细节。

**OpenGL/GLSL 着色器实现**：在顶点着色器中逐顶点构建 TBN 矩阵并传入片元着色器；在片元着色器中对法线贴图采样，解码后用 TBN 变换到世界空间，再代入 Phong 或 PBR 光照方程计算漫反射和镜面反射。整个流程增加的 GPU 开销主要来自一次矩阵-向量乘法（9 次乘加）以及额外的纹理采样。

**DirectX 与 OpenGL 的 Y 轴差异**：DirectX（DX）使用的 UV 坐标原点在左上角，Y 轴向下；OpenGL 原点在左下角，Y 轴向上。因此同一张法线贴图在两套 API 之间使用时，G 通道（对应 Y/V 方向）需要翻转，否则凹凸方向会反向，表面显得"凹陷"变成"凸起"。

---

## 常见误区

**误区一：法线贴图能改变物体的剪影形状**  
法线贴图只影响着色阶段的光照计算，不修改实际几何体。模型的边缘轮廓（Silhouette）仍由底层低多边形网格决定。当视线角度接近掠射（Grazing Angle）时，边缘处的"假凹凸"会明显穿帮。这是法线贴图与视差贴图、位移贴图之间最本质的区别。

**误区二：直接在 Photoshop 中对法线贴图使用普通叠加混合**  
两张切线空间法线贴图不能用 RGB 加法或标准 Alpha 混合直接合并，因为这样会破坏向量的单位长度。正确方法是使用 **Whiteout 混合公式**：$n = \text{normalize}(n_1.xy + n_2.xy, \ n_1.z \cdot n_2.z)$，或在支持该运算的工具（如 Substance Designer 的"Normal Blend"节点）中操作。

**误区三：TBN 矩阵必须在片元着色器中逐像素重建**  
实际上，若模型曲率变化不剧烈，TBN 可以在顶点着色器中计算并插值传入片元着色器（称为"顶点 TBN"方案）。只有在需要极高精度或处理顶点稀疏的大平面时，才需要逐像素使用 `dFdx`/`dFdy` 导数重建切线（即 MikkTSpace 或屏幕空间 TBN 方法）。

---

## 知识关联

**前置知识——纹理映射概述**：法线贴图本质上是一种特殊的纹理，其采样、Mipmap 生成、UV 寻址方式都遵循普通纹理映射的规则。但法线贴图在生成 Mipmap 时不能简单取平均值——对 RGB 分量直接平均会使低分辨率 Mip 级别的法线长度偏小，需要归一化或使用 LEAN/LEADR 等专用滤波算法。

**后续主题——视差贴图（Parallax Mapping）**：视差贴图在法线贴图的基础上引入额外的高度通道，通过沿视线方向偏移纹理坐标来模拟表面的自遮挡和视角依赖的深度感，弥补了法线贴图无法改变轮廓、掠射角度穿帮的缺陷。理解 TBN 矩阵和切线空间坐标变换，是实现视差贴图中"视线向量转入切线空间"步骤的直接前提。
