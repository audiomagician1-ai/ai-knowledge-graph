---
id: "3da-env-material-blend"
concept: "材质混合"
domain: "3d-art"
subdomain: "environment-art"
subdomain_name: "环境美术"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "reference"
    citation: "Akenine-Möller, T., Haines, E., & Hoffman, N. (2018). Real-Time Rendering (4th ed.). CRC Press."
  - type: "reference"
    citation: "Wronski, B. (2012). Terrain Shading and Rendering in Assassin's Creed III. SIGGRAPH 2012 Advances in Real-Time Rendering."
  - type: "reference"
    citation: "Tatarchuk, N. (2006). Practical Parallax Occlusion Mapping for Highly Detailed Surface Rendering. GDC 2006, Advanced Real-Time Rendering in 3D Graphics and Games."
  - type: "reference"
    citation: "Burley, B., & Lacewell, D. (2012). Physically-Based Shading at Disney. SIGGRAPH 2012 Course: Practical Physically-Based Shading in Film and Game Production."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 材质混合

## 概述

材质混合（Material Blending）是3D环境美术中将两种或多种材质在同一表面上进行无缝过渡融合的技术。与直接在单一材质中绘制纹理细节不同，材质混合通过控制权重蒙版（weight mask）决定每个像素点上各材质的显示比例，从而在草地与泥土、岩石与沙地等自然边界处产生真实可信的过渡效果。

材质混合技术在游戏行业的系统化应用可追溯至2000年代中期，随着可编程着色器（programmable shader）在DirectX 9.0c（2002年发布）普及后逐渐成熟。早期引擎如Quake III Arena的着色器系统仅支持简单的线性Alpha混合，而Unreal Engine 3（2006年）首次在商业引擎层面引入多层地形材质混合（Terrain Layer Blending），允许最多32个材质层叠加。Unreal Engine 4/5则进一步允许实时计算基于高度图和世界坐标的动态混合，大幅减少了美术资产的重复制作量。

材质混合的核心价值在于将可平铺纹理资产（tileable texture）的重复利用率最大化——同一套512×512至2048×2048分辨率的岩石纹理，既可单独使用，也可通过混合系统与草地纹理自然衔接，使地形表面兼顾细节密度与制作效率。在大型开放世界项目中，合理的材质混合策略可以将地形贴图资产的总体积压缩30%–50%，同时维持相同的视觉品质。

物理正确性是现代材质混合不可忽视的维度：Disney PBR（Physically-Based Rendering）框架（Burley & Lacewell, 2012）要求混合后的基础颜色（Base Color）、金属度（Metallic）和粗糙度（Roughness）通道均需在线性色彩空间（linear color space）中完成加权插值，否则在Gamma校正环节会引入非线性误差，导致混合边界处出现色偏（color banding）。这一要求意味着美术工具链必须在整个流程中保持sRGB解码与线性运算的严格分离。

> **思考问题**：为什么在低多边形地形网格上，顶点颜色混合的边界过渡往往比高度混合更模糊？这两种技术的精度上限分别受什么因素制约？在实际项目中，如何通过组合两种方式的优势来弥补各自的局限性？

---

## 核心原理

### 顶点颜色混合（Vertex Color Blending）

顶点颜色混合利用模型顶点上存储的RGBA四个通道作为混合权重，最多可在一个网格上同时承载4种材质的混合信息。每个通道（R/G/B/A）对应一种材质层，顶点颜色值从0到1代表该材质在该顶点附近的显示权重。在着色器中，最基础的双层线性混合公式为：

$$\text{FinalColor} = \text{MaterialA} \times (1 - V_R) + \text{MaterialB} \times V_R$$

其中 $V_R$ 表示顶点颜色的红色通道采样值（范围0–1）。对于四层混合，需要保证：

$$V_R + V_G + V_B + V_A = 1$$

即所有材质权重之和归一化为1，否则混合结果会出现过曝（权重之和 > 1）或欠曝（权重之和 < 1）的亮度错误。在Unreal Engine 5的材质编辑器中，可通过`VertexColor`节点直接访问这四个通道，并连接至各自的`LinearInterpolate`（Lerp）节点完成多层混合网络的搭建。

顶点颜色的精度受网格拓扑密度限制——低多边形地形网格上顶点间距可达1–2米，顶点之间的双线性插值（bilinear interpolation）过渡往往显得模糊，边界宽度无法精确控制。因此顶点颜色混合更适用于大范围地形上的宏观区域划分，而非石块缝隙级别的精细过渡。在Unreal Engine中，可以使用顶点绘制工具（Mesh Paint Tool）在编辑器视口中直接刷入顶点颜色权重，笔刷半径与强度均可实时调节。

值得注意的是，顶点颜色数据存储于网格的顶点缓冲区（Vertex Buffer），不占用额外的纹理采样器（texture sampler）配额。对于移动平台而言，着色器可用采样器数量通常受OpenGL ES 3.0限制（最多16个），顶点颜色混合因此成为移动端地形着色的常用优化手段。

### 高度混合（Height-Based Blending）

高度混合通过读取各材质自身的高度贴图（heightmap）来锐化混合边界，使材质过渡沿着表面凹凸轮廓分布，从而打破线性混合产生的"油水分离"感。其核心计算公式为：

$$B = \text{saturate}\!\left(\frac{H_A + M_A - H_B - M_B}{T_s}\right)$$

其中各变量含义如下：
- $H_A$、$H_B$：分别为材质A与材质B的高度贴图采样值（范围0–1，1代表表面最高处）
- $M_A$、$M_B$：来自顶点颜色或控制贴图的基础权重蒙版，决定哪种材质在该区域"占优"
- $T_s$：过渡锐利度（Transition Sharpness），典型值范围0.05–0.3，值越小边界越锐利
- $\text{saturate}(\cdot)$：将结果钳制至 $[0, 1]$ 区间的饱和函数

最终混合输出使用计算得到的 $B$ 值再次进行 Lerp：

$$\text{FinalColor} = \text{Lerp}(\text{MaterialB},\; \text{MaterialA},\; B)$$

高度混合的视觉效果远优于线性混合：泥土会从岩石表面凸起处向凹陷处自然渗入，雪会在物体高处积聚而在侧面消退。这种效果在《巫师3：狂猎》（2015, CD Projekt Red）、《地平线：零之曙光》（2017, Guerrilla Games）等写实风格游戏的地形中被大量采用，是现代AAA地表材质的标配技术（Akenine-Möller et al., 2018）。高度贴图本身通常被打包至粗糙度贴图的Alpha通道（即RMA贴图格式：R=Roughness, M=Metallic, A=Height），避免额外的采样器消耗，这是Unity HDRP与Unreal Engine 5 Substrate材质系统均推荐的通道打包策略。

### 世界坐标混合（World-Space Position Blending）

世界坐标混合利用片元（fragment）在世界空间中的坐标值驱动混合权重，最常见的应用是基于Z轴（高度轴）实现积雪效果——物体海拔越高，雪材质权重越大：

$$W_{\text{snow}} = \text{saturate}\!\left(\frac{P_Z - H_{\text{start}}}{F_{\text{snow}}}\right)$$

其中 $P_Z$ 为片元世界坐标的Z分量（海拔高度），$H_{\text{start}}$ 为积雪开始的海拔阈值（例如800米），$F_{\text{snow}}$ 为积雪过渡区间长度（例如50米），控制雪线的模糊程度。

除高度外，世界坐标混合还可以利用 $P_{XZ}$ 结合Perlin噪波或Voronoi噪波函数生成宏观地面纹理变化，在不增加任何额外贴图的前提下打破可平铺贴图的重复感。法线方向混合（Normal-Based Blending）是世界坐标混合的衍生形式，通过计算表面法线 $\hat{n}$ 与世界向上向量 $\hat{u} = (0,0,1)$ 的点积（dot product）决定积雪、青苔或灰尘的沉积位置：

$$W_{\text{deposit}} = \text{saturate}\!\left(\frac{\hat{n} \cdot \hat{u} - T_{\text{min}}}{1 - T_{\text{min}}}\right)$$

当 $\hat{n} \cdot \hat{u}$ 接近1.0（水平朝上面）时，沉积材质权重最大；当点积接近0（垂直侧面）时权重归零，精确模拟重力沉积的物理直觉。其中 $T_{\text{min}}$ 为沉积开始的法线角度余弦阈值，典型值为0.5（对应60°倾斜面），可由美术在材质参数集（Material Parameter Collection）中统一调节，一次修改即可全局更新场景内所有使用该材质的网格。

### 控制贴图混合（Control Map Blending）

除以上三种实时计算方式外，美术师也可以预先离线绘制一张专用控制贴图（Control Map），将各材质层的权重信息固定烘焙至2D纹理的各颜色通道中。控制贴图通常采用与地形尺寸匹配的分辨率（如4096×4096像素，对应1公里×1公里地形时每像素约25厘米精度），每个像素精确对应地形表面上的一个采样点，相较顶点颜色混合可提供高出数十倍的空间精度，常用于需要手工精细绘制的城市地表或关卡内部场景（Wronski, 2012）。

控制贴图的缺点在于文件体积较大——一张4096×4096的RGBA控制贴图，在DXT5压缩后约占16 MB显存，但已能覆盖4种材质层的完整权重信息。其次，控制贴图无法动态响应运行时天气或季节变化，通常与高度混合叠加使用：控制贴图提供宏观区域划分精度，高度混合负责材质交界处的微观锐化，二者互补以实现兼顾效率与品质的地形着色方案。在Unreal Engine 5的Landscape系统中，地形层权重图（Layer Weightmap）本质上即是一套自动管理的控制贴图集合，引擎会将权重数据自动打包进多张RGBA贴图并缓存至GPU。

---

## 关键公式与参数速查

以下汇总本文涉及的核心公式及其典型参数范围，供实际开发中快速参考：

| 混合类型 | 核心公式 | 关键参数典型值 |
|---|---|---|
| 线性顶点颜色混合 | $C = A(1-V_R) + BV_R$ | 顶点密度：0.5–2 m/顶点 |
| 高度混合锐利度 | $B = \text{saturate}((H_A+M_A-H_B-M_B)/T_s)$ | $T_s = 0.05$（锐利）至 $0.3$（柔和） |
| 积雪高度阈值 | $W = \text{saturate}((