---
id: "cg-raster-intro"
concept: "光栅化概述"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 82.5
generation_method: "ai-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v2"
  - type: "academic"
    author: "Foley, J. D., van Dam, A., Feiner, S. K., & Hughes, J. F."
    year: 1990
    title: "Computer Graphics: Principles and Practice (2nd ed.)"
    publisher: "Addison-Wesley"
  - type: "academic"
    author: "Shirley, P., & Marschner, S."
    year: 2009
    title: "Fundamentals of Computer Graphics (3rd ed.)"
    publisher: "A K Peters/CRC Press"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 光栅化概述

## 概述

光栅化（Rasterization）是将几何图形（如三角形、直线）转换为屏幕像素网格的过程。具体而言，它解决的问题是：给定一组三维顶点坐标，如何确定最终显示器上哪些像素应该被点亮，以及每个像素应显示什么颜色。现代显示器由数百万个离散的像素点组成，而三维场景中的物体是连续的几何体，光栅化正是连接这两个世界的桥梁算法。

光栅化的历史可追溯到1970年代。1974年，Edwin Catmull（后来成为皮克斯总裁）在其博士论文中提出了Z-buffer（深度缓冲）算法，这是光栅化渲染能够正确处理遮挡关系的关键发明。1980年代，随着SGI（Silicon Graphics Inc.）工作站的普及，硬件加速的光栅化流水线逐渐成型。1992年，OpenGL 1.0正式发布，将光栅化管线标准化并开放给开发者使用。到1999年，NVIDIA发布GeForce 256，将光栅化的顶点变换计算从CPU移入GPU，标志着现代硬件光栅化时代的真正开始。Foley等人（1990）在其经典教材中系统归纳了这一时期光栅化算法的理论基础，至今仍是该领域的权威参考。

光栅化之所以至今仍是实时图形渲染的主流方案，原因在于其极高的计算效率。与光线追踪相比，光栅化的计算复杂度与场景中的三角形数量线性相关，而非与像素和三角形的乘积相关。一块RTX 4090 GPU每秒可处理约1820亿个光栅化操作，使得60帧甚至120帧每秒的实时渲染成为可能。

## 核心原理：从三维到二维的坐标变换链

光栅化渲染管线的起点是三维空间中的顶点坐标。整个变换链称为**MVP变换**（Model-View-Projection），可以用以下矩阵公式表示：

$$\mathbf{p}_{clip} = M_{proj} \cdot M_{view} \cdot M_{model} \cdot \mathbf{p}_{local}$$

其中 $M_{model}$ 将顶点从局部空间变换到世界空间，$M_{view}$ 将世界空间变换到摄像机空间，$M_{proj}$ 将摄像机空间压缩到裁剪空间。经过这三个矩阵的依次变换后，原本分布在三维世界中的几何体被压缩进标准化设备坐标（NDC，Normalized Device Coordinates）空间，其中x、y、z坐标均被映射到 $[-1, 1]$ 范围内。随后，**透视除法**（将x、y、z各分量除以齐次坐标 $w$）和**视口变换**将NDC坐标最终映射到屏幕像素坐标。

例如，一个位于世界坐标 $(3.0,\ 1.5,\ -5.0)$ 的顶点，经过视图矩阵平移和投影矩阵压缩后，可能变换为NDC坐标 $(0.42,\ 0.18,\ 0.87)$，再经过视口变换映射至 $1920 \times 1080$ 分辨率屏幕上的像素位置约为 $(883,\ 637)$。这一过程中，所有数学操作均在GPU的矩阵运算单元（Tensor Core或CUDA Core）上并行完成。

## 三角形遍历：光栅化的核心步骤

GPU确定哪些像素位于三角形内部的方法基于**重心坐标（Barycentric Coordinates）**判断。对于屏幕上的像素点 $P$ 和三角形顶点 $A$、$B$、$C$，若 $P$ 可以表示为：

$$P = \alpha A + \beta B + \gamma C, \quad \alpha + \beta + \gamma = 1$$

且 $\alpha \geq 0,\ \beta \geq 0,\ \gamma \geq 0$，则该像素位于三角形内部，应被渲染。GPU对屏幕上三角形包围盒（Bounding Box）内的每个像素并行执行此判断，这种大规模并行性正是GPU硬件设计的核心优势。重心坐标同时用于在三角形内部插值顶点属性，例如颜色、纹理坐标（UV）和法线向量，插值公式为：

$$\text{attr}(P) = \alpha \cdot \text{attr}(A) + \beta \cdot \text{attr}(B) + \gamma \cdot \text{attr}(C)$$

例如，若三角形三个顶点的UV坐标分别为 $(0,0)$、$(1,0)$、$(0,1)$，则三角形中心点（$\alpha = \beta = \gamma = 1/3$）处的UV值插值结果为 $(1/3,\ 1/3)$，可直接用于采样纹理贴图。Shirley与Marschner（2009）对重心坐标插值的数值稳定性与精度问题有详细讨论，指出在透视投影下需对插值量进行透视矫正（Perspective-Correct Interpolation），以避免纹理扭曲。

## Z-Buffer深度测试与遮挡处理

Z-Buffer是光栅化正确处理物体遮挡关系的核心机制。渲染开始时，深度缓冲区被初始化为最大深度值 $1.0$（在NDC空间中远裁剪面处）。每当一个片元（Fragment）通过三角形覆盖测试后，其深度值 $z$ 会与深度缓冲区中对应位置的已存储值进行比较：

$$\text{if } z_{new} < z_{buffer}[x][y]: \quad \text{更新颜色缓冲区及深度缓冲区}$$

若新片元的 $z$ 值更小（更靠近相机），则更新颜色缓冲区和深度缓冲区；否则该片元被丢弃。这一算法的空间复杂度为 $O(W \times H)$（$W$、$H$ 为屏幕分辨率），是与场景复杂度无关的常数级方法，代价是无法直接处理半透明物体的正确排序问题。

深度精度是实践中的重要工程问题。以32位浮点深度缓冲为例，在近裁剪面 $z_{near} = 0.1$ 米、远裁剪面 $z_{far} = 1000$ 米的典型设置下，近处约0.1米范围内的深度精度远高于远处，这会导致远处物体出现**Z-fighting**（深度冲突）伪影。解决方案之一是采用**Reversed-Z**技术，将深度映射区间反转为 $[1, 0]$，充分利用浮点数在接近0时精度更高的特性，显著减少远处深度冲突。

## 着色：片元着色器与光照计算

通过深度测试的片元会进入着色阶段。可编程的**片元着色器（Fragment Shader）**对每个通过测试的像素独立执行一段程序，计算其最终颜色。片元着色器接收由顶点着色器输出并经过重心坐标插值的数据，可访问纹理贴图、光照参数等资源。

以经典Phong光照模型为例，片元着色器计算漫反射分量时使用如下公式：

$$L_d = k_d \cdot I \cdot \max(0,\ \hat{n} \cdot \hat{l})$$

其中 $k_d$ 为漫反射系数，$I$ 为光源强度，$\hat{n}$ 为片元法线单位向量，$\hat{l}$ 为指向光源的单位向量。现代游戏引擎（如Unreal Engine 5、Unity HDRP）已普遍采用**PBR（Physically Based Rendering，基于物理的渲染）**着色模型，使用GGX微表面分布函数替代Phong模型，以获得更真实的金属、粗糙度表现。

例如，渲染一颗金属球体时，PBR着色器需要采样至少三张贴图：albedo贴图（基础色）、metallic贴图（金属度）、roughness贴图（粗糙度），并结合预计算的IBL（Image-Based Lighting）环境贴图，在片元着色器中综合计算镜面反射和漫反射的物理混合比例。

## 实际应用场景

**游戏实时渲染**是光栅化最典型的应用场景。以《赛博朋克2077》为例，其场景中单帧可能包含数千万个三角形，通过LOD（Level of Detail，细节层次）技术动态调整远处物体的三角形数量，配合光栅化管线维持实时帧率。阴影渲染使用**Shadow Mapping**技术，即从光源视角额外执行一次光栅化遍历，生成深度贴图，再在主渲染遍中采样该贴图判断片元是否在阴影中。

**UI渲染框架**如网页浏览器（Chrome、Firefox）的Skia渲染引擎，将网页的矢量图形（CSS样式、SVG路径）通过GPU光栅化转换为屏幕像素。字体渲染也依赖光栅化将TrueType或OpenType格式的矢量字形转换为具体分辨率下的位图像素，并结合次像素渲染（Subpixel Rendering）技术提升文字清晰度。

**科学可视化与工业仿真**领域，光栅化同样广泛应用于医学CT扫描三维重建（体渲染）、有限元分析结果可视化、汽车碰撞仿真动画等场景，这些应用对渲染帧率要求相对宽松，但对几何精度和着色物理准确性要求极高。

## 常见误区与概念辨析

**误区一：认为光栅化只是"截图"操作，而非实时计算过程。** 事实上，即使显示完全静止的画面，GPU每帧（1/60秒内）都在重新执行完整的光栅化管线——执行MVP变换、三角形遍历、深度测试和片元着色。光栅化是一个每帧实时重新计算的过程，而非对存储图像的简单回放。

**误区二：认为光栅化无法实现真实感光影效果，只有光线追踪才能做到。** 实际上，屏幕空间环境光遮蔽（SSAO）、屏幕空间反射（SSR）、级联阴影贴图（CSM）等技术在纯光栅化管线下可以近似实现相当真实的全局光照效果。这些技术是通过在光栅化的屏幕空间进行额外采样计算来模拟光线的间接传播，并非光线追踪。

**误区三：混淆"顶点"与"像素"的处理时机。** 顶点着色器（Vertex Shader）对每个顶点执行一次，而片元着色器对每个通过测试的像素执行一次。一个仅有4个顶点的大四边形，其片元着色器可能被调用数百万次——例如，一个铺满整个 $1920 \times 1080$ 屏幕的全屏四边形，片元着色器将被调用 $1920 \times 1080 = 2{,}073{,}600$ 次。这是光栅化渲染中GPU过载（Overdraw）问题的根本原因，也是为何Early-Z（提前深度测试）优化技术能显著提升渲染性能的原因所在。

> **思考