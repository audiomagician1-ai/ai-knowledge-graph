---
id: "cg-cube-mapping"
concept: "立方体贴图"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 85.2
generation_method: "intranet-llm-rewrite-v3"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v3"
  - type: "academic"
    author: "Greene, Ned"
    year: 1986
    title: "Environment Mapping and Other Applications of World Projections"
    venue: "IEEE Computer Graphics and Applications, Vol. 6, No. 11, pp. 21–29"
  - type: "academic"
    author: "Ramamoorthi, Ravi & Hanrahan, Pat"
    year: 2001
    title: "An Efficient Representation for Irradiance Environment Maps"
    venue: "ACM SIGGRAPH 2001 Proceedings, pp. 497–500"
  - type: "academic"
    author: "Karis, Brian"
    year: 2013
    title: "Real Shading in Unreal Engine 4"
    venue: "ACM SIGGRAPH 2013 Course: Physically Based Shading in Theory and Practice"
  - type: "book"
    author: "Akenine-Möller, Tomas; Haines, Eric; Hoffman, Naty"
    year: 2018
    title: "Real-Time Rendering, 4th Edition"
    venue: "CRC Press, ISBN 978-1138627000, Chapter 10: Local Illumination and Texture"
  - type: "book"
    author: "Pharr, Matt; Jakob, Wenzel; Humphreys, Greg"
    year: 2023
    title: "Physically Based Rendering: From Theory to Implementation, 4th Edition"
    venue: "MIT Press, ISBN 978-0262048026, Chapter 13: Light Transport II: Volume Rendering"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v3
updated_at: 2026-04-06
---

# 立方体贴图

## 概述

立方体贴图（Cubemap）是一种由6张正方形纹理图像组成的特殊纹理类型，这6张图像分别对应一个虚拟立方体的六个面：正X（+X）、负X（−X）、正Y（+Y）、负Y（−Y）、正Z（+Z）、负Z（−Z）。采样时不使用传统的二维UV坐标，而是使用一个从立方体中心出发的三维方向向量，GPU根据该向量的最大分量确定采样哪个面，再将剩余两个分量换算为该面上的二维坐标。这种采样机制使立方体贴图天然适合表达"从某一点向四面八方观察"的全向信息。

立方体贴图最早在1986年由Ned Greene在论文《Environment Mapping and Other Applications of World Projections》（IEEE Computer Graphics and Applications, Vol. 6, No. 11, pp. 21–29）中系统提出，作为球面映射的替代方案。与球面贴图相比，立方体贴图在极点处不存在严重的像素拉伸问题，且可以用标准双线性过滤进行平滑采样。OpenGL在1.3版本（2001年）将立方体贴图纳入核心规范（`GL_TEXTURE_CUBE_MAP`），此后它成为实时渲染中最基础的全向纹理形式。DirectX 8.0同年也将其列为`D3DRTYPE_CUBETEXTURE`类型，进一步确立了其跨API的标准地位。

立方体贴图之所以重要，在于它用6张共计 $6N^2$ 个像素的图像，以较低的存储代价近似编码了场景中某点的完整球面视野，直接支撑了天空盒渲染、实时环境反射和动态漫反射辐照度等多项核心技术。目前主流游戏引擎（Unity 2022 LTS、Unreal Engine 5.3、Godot 4.2）均将立方体贴图作为一等纹理类型原生支持，GPU驱动层（NVIDIA Turing架构及之后）也针对立方体贴图采样路径做了专门的硬件优化。

---

## 核心原理

### 方向向量到面坐标的映射

给定一个三维方向向量 $\mathbf{r} = (r_x, r_y, r_z)$，GPU首先找到绝对值最大的分量，设其绝对值为 $m = \max(|r_x|, |r_y|, |r_z|)$。若 $|r_x|$ 最大且 $r_x > 0$，则采样+X面；以此类推共6种情形。随后，另两个分量被线性映射到 $[0,1]$ 区间，计算公式为：

$$u = \frac{1}{2}\left(\frac{s_c}{m} + 1\right), \quad v = \frac{1}{2}\left(\frac{t_c}{m} + 1\right)$$

其中 $s_c$、$t_c$ 是与该面对应的另两个分量（各面的 $s_c/t_c$ 映射方向在OpenGL规范附录F中有精确定义），$m$ 是最大分量的绝对值，起到归一化分母的作用，确保 $u, v \in [0,1]$。这一步骤完全在硬件纹理单元（TMU，Texture Mapping Unit）中完成，开发者只需向片元着色器传入方向向量即可，无需手动做坐标变换。

**例如**：若方向向量为 $\mathbf{r} = (0.8, 0.3, -0.5)$，则 $|r_x| = 0.8$ 最大，采样+X面，$m = 0.8$。按OpenGL规范，+X面的 $s_c = -r_z = 0.5$，$t_c = -r_y = -0.3$（注意Y轴方向取反，以匹配纹理坐标系原点在左上角的惯例）。代入公式得：

$$u = \frac{1}{2}\left(\frac{0.5}{0.8} + 1\right) = \frac{1}{2}(0.625 + 1) = 0.8125$$

$$v = \frac{1}{2}\left(\frac{-0.3}{0.8} + 1\right) = \frac{1}{2}(-0.375 + 1) = 0.3125$$

即在+X面纹理上的采样坐标为 $(0.8125, 0.3125)$。若该面分辨率为 $512 \times 512$，则实际采样像素位置约为 $(416, 160)$。

### 存储规模与分辨率权衡

设立方体贴图每面分辨率为 $N \times N$，则总像素数为：

$$P_{\text{cube}} = 6N^2$$

与之对比，覆盖相同角分辨率的等距柱状全景图（Equirectangular Panorama）的常用分辨率为 $2N \times N$，总像素数为：

$$P_{\text{equirect}} = 2N^2$$

两者之比 $P_{\text{cube}} / P_{\text{equirect}} = 3$，说明立方体贴图总像素数是等距柱状图的3倍。然而等距柱状图在极点处存在严重冗余（角分辨率极不均匀），有效信息量与立方体贴图相当，这是两种格式各有适用场景的根本原因。在实际工程中，一张每面 $512 \times 512$、RGBA8格式的立方体贴图占用显存为 $6 \times 512^2 \times 4 = 6{,}291{,}456$ 字节（约6 MB）；若启用完整Mipmap链，总显存增量为原始大小的 $1/3$，即额外约2 MB，总共约8 MB。对于HDR格式（RGBA16F），显存占用翻倍，每面 $1024 \times 1024$ 的HDR立方体贴图约占48 MB。

值得注意的是，立方体贴图各面交界处存在接缝（Seam）采样问题：当方向向量非常接近两个面的分界线时，双线性过滤的采样核可能同时跨越两个面，而标准双线性过滤只在单一面内进行，会导致接缝处出现颜色跳变。OpenGL 4.0引入了 `ARB_seamless_cube_map` 扩展（后纳入核心），启用 `GL_TEXTURE_CUBE_MAP_SEAMLESS` 后，GPU会在接缝处自动跨面进行三线性过滤，消除接缝瑕疵，代价是轻微增加带宽压力（需同时访问相邻面的边界像素）。

**思考题**：如果将立方体贴图每面分辨率从 $512 \times 512$ 提升到 $1024 \times 1024$，角分辨率（每像素覆盖的立体角 $\Delta\Omega$）会如何变化？提升分辨率对天空盒渲染与对IBL预过滤贴图的收益是否相同，为什么？在移动端受显存限制时，你会优先压缩哪一类立方体贴图，理由是什么？

### 天空盒渲染原理

天空盒利用立方体贴图模拟无限远的天空背景。实现时，以摄像机位置为中心绘制一个单位立方体，顶点着色器中**去除观察矩阵的平移分量**（只保留旋转部分，即取 `mat4` 的左上 `mat3` 子矩阵），使天空盒始终跟随摄像机旋转而不随平移产生视差。GLSL顶点着色器中的典型写法为：

```glsl
mat4 viewNoTranslation = mat4(mat3(u_view)); // 去除平移
vec4 clipPos = u_proj * viewNoTranslation * vec4(aPos, 1.0);
gl_Position = clipPos.xyww; // 使NDC深度值强制为1.0（w/w = 1）
```

片元着色器将顶点的本地坐标直接作为方向向量采样立方体贴图，即 `texture(u_skybox, vLocalPos)`。深度值强制设为 `gl_FragDepth = 1.0`（或利用 `clipPos.xyww` 使透视除法后深度恒为1.0），确保实体几何体像素始终覆盖天空盒区域，避免过度绘制（Overdraw）带来的额外带宽消耗。

在Unreal Engine 5中，天空盒进一步与大气散射模型（SkyAtmosphere组件，基于Sebastien Hillaire 2020年在EGSR发表的大气渲染论文）结合，将物理精确的大气散射结果实时烘焙入立方体贴图，每帧按需更新受太阳方向影响的面，而非全量更新全部6个面，将动态天空盒的GPU耗时控制在0.3 ms以内（在RTX 3080上测量）。

### 镜面环境反射

对一个反射型表面，片元着色器用入射视线向量 $\mathbf{v}$（指向表面）和表面法线 $\mathbf{n}$ 计算反射向量：

$$\mathbf{r} = \mathbf{v} - 2(\mathbf{v} \cdot \mathbf{n})\,\mathbf{n}$$

即GLSL内置函数 `reflect(v, n)` 的展开形式。其中 $\mathbf{v} \cdot \mathbf{n}$ 为视线与法线的点积，当视线与法线夹角为45°时，$\mathbf{v} \cdot \mathbf{n} = \cos 45° \approx 0.707$。用 $\mathbf{r}$ 采样立方体贴图即得该像素"看到"的环境颜色。该技术称为**环境映射（Environment Mapping）**，单次纹理采样即可近似镜面反射，计算代价远低于光线追踪或屏幕空间反射（SSR）。

代价在于立方体贴图是预烘焙的静态快照，无法反映动态物体，且隐含假设光源无限远（反射向量不随表面位置发生视差偏移）。对于平面反射或近场反射，这一假设会引入明显的视差错误，此时需要局部校正立方体贴图（Localized Cubemap / Box Projection Correction）技术来修正（Akenine-Möller et al., 2018，第10.2章）。Box Projection的核心思路是：将反射向量从表面位置出发，与包围盒的6个平面求交，取最近交点，用交点坐标相对于立方体贴图中心的偏移向量重新构造采样方向，从而引入位置相关的视差修正。

---

## 关键公式与模型

### IBL漫反射辐照度预积分

基于图像的光照（Image-