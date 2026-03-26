---
id: "3da-tex-export-settings"
concept: "纹理导出设置"
domain: "3d-art"
subdomain: "texturing"
subdomain_name: "纹理绘制"
difficulty: 2
is_milestone: false
tags: ["流程"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 纹理导出设置

## 概述

纹理导出设置是指在Substance Painter或类似贴图工具中，将绘制完成的纹理数据从项目文件转换为引擎或渲染器可读文件时，所配置的格式、位深度、通道打包和压缩参数的集合。错误的导出设置会导致纹理在引擎中出现色偏、精度丢失或文件体积异常膨胀等问题，因此导出阶段的参数选择直接影响最终渲染质量。

PNG格式于1996年由PNG开发组作为GIF的无损替代品发布，支持8位和16位通道，被广泛用于漫反射贴图和法线贴图的交付；TGA格式由Truevision公司于1984年推出，支持每通道8/16/32位并携带Alpha通道，是游戏行业长期使用的标准；EXR格式由工业光魔公司（ILM）于2002年开发，支持每通道16位半精度或32位全精度浮点数，专门用于HDR光照贴图和发光贴图等高动态范围内容。

理解纹理导出设置的意义在于，同一张法线贴图若以8位PNG导出，其Z轴方向精度只有256个离散值，而以16位TGA导出则拥有65536个离散值，在曲面细节丰富的角色模型上会产生肉眼可见的阶梯状法线过渡。

---

## 核心原理

### 文件格式的选择依据

**PNG**适合需要无损压缩的颜色贴图（Base Color/Albedo），采用DEFLATE算法压缩，文件体积较TGA小20%–50%，但不支持32位浮点数据。**TGA**支持RLE（行程长度编码）压缩或无压缩存储，是Photoshop和Substance Painter历史上最兼容的中间格式，在需要携带独立Alpha通道的UI纹理中仍被广泛使用。**EXR**通过ZIP或PIZ小波算法实现无损压缩，其16位半精度（Half Float）模式可在4字节中存储一个像素的单通道数据，相比32位全精度节省50%空间，适合烘焙结果和灯光贴图的归档。

### 位深度与精度损失

位深度决定每个颜色通道能表达的离散灰度级数量，公式为：

**灰度级数 = 2^N**（N为每通道位数）

- **8位（uint8）**：256级，适合Albedo、Roughness等感知线性贴图
- **16位（uint16）**：65536级，适合法线贴图、高度贴图，防止阶梯状瑕疵（banding）
- **16位半精度浮点（half float）**：约6.5万个可表示值但分布不均匀，适合HDR光照贴图
- **32位全精度浮点（float32）**：约43亿个可表示值，适合需要后期合成的原始渲染数据

在Substance Painter的导出对话框中，"8 bits per channel"选项对应uint8，"16 bits per channel"对应uint16，"32 bits per channel"则输出float32的EXR或TIF文件。

### 通道打包（Channel Packing）

游戏引擎（如Unreal Engine 5和Unity HDRP）通常要求将Roughness、Metallic、Ambient Occlusion三张灰度贴图打包进一张RGB纹理的R、G、B通道，以减少纹理采样次数。Substance Painter的导出预设（如UE4_Packed或Unity_HDRP）内置了通道打包规则，但美术人员必须核对预设中各通道的赋值顺序——UE5的默认ORM贴图规定R=Occlusion、G=Roughness、B=Metallic，若与引擎材质函数的采样通道不一致，将导致金属感和粗糙度对调显示。

### 色彩空间标记

PNG和TGA文件在导出时需要手动选择是否嵌入sRGB标记。Albedo贴图应以sRGB色彩空间导出，法线贴图和Roughness贴图必须以**线性（Linear）空间**导出，否则引擎在Gamma校正时会对法线数据进行不必要的非线性变换，导致光照方向错误。EXR格式默认存储线性数据，不涉及sRGB标记问题。

---

## 实际应用

**角色皮肤贴图导出**：导出皮肤的Base Color时，选择PNG格式、8位/通道、sRGB色彩空间；导出皮肤厚度贴图（Thickness Map）用于SSS次表面散射时，则改用16位PNG或EXR线性格式，避免薄耳廓区域的梯度信息丢失。

**法线贴图导出**：Substance Painter内置DirectX（Y轴向下）和OpenGL（Y轴向上）两种法线格式，导出时必须根据目标引擎选择正确的翻转方向。Unity使用OpenGL法线，UE5使用DirectX法线；如果导出格式选错，模型表面的高光方向会整体反向。通常选择16位TGA或16位PNG，不建议使用8位，因为法线XY分量的微小差异需要更高精度保留。

**环境贴图导出**：HDRI天空球贴图必须使用EXR格式的32位或16位半精度导出，文件名通常遵循`sky_hdri_4k.exr`的命名规范，分辨率4096×2048是游戏项目的常见标准，更高质量的影视项目使用8192×4096。

---

## 常见误区

**误区一：认为所有贴图都应该用16位以保证质量**。16位PNG的文件体积约是8位的两倍，对于Roughness或Metallic这类肉眼感知不敏感的贴图，16位带来的视觉改善微乎其微，而体积增加会拖慢引擎的流式加载（Streaming）速度。只有法线贴图、高度贴图等需要高梯度精度的贴图才有必要使用16位。

**误区二：TGA和PNG的无损质量相同，随意选择**。尽管两者都支持无损存储，但TGA在导出时默认可能不启用RLE压缩，导致一张2048×2048的TGA文件体积超过12MB，而同等PNG文件通常只有3–6MB。在制作规范中，交付包应优先使用PNG以控制项目仓库体积。

**误区三：导出时不需要区分线性和sRGB，引擎会自动处理**。引擎只有在纹理资产导入设置中被显式标记为"sRGB"时才会进行Gamma矫正，而这依赖美术在导出时正确标记色彩空间。如果法线贴图被错误标记为sRGB并导入引擎，引擎会对其进行0.45次幂的Gamma矫正，法线方向向量模长不再为1，光照计算出现系统性错误。

---

## 知识关联

本概念建立在**Substance Painter**的图层系统和烘焙工作流之上——只有完成了图层绘制和烘焙后，导出设置才能发挥作用。Substance Painter的"导出纹理"对话框（File > Export Textures）是应用这些设置的操作入口，其中的预设模板（Output Template）封装了格式、位深度和通道打包的完整配置。

掌握纹理导出设置后，下一步进入**纹理管线**的学习，将涉及如何在项目工程层面管理从Substance Painter到游戏引擎的自动化导入流程，包括使用Python脚本批量转换格式、通过引擎的资产处理器（Asset Processor）设置纹理压缩格式（如DXT1/BC1、BC7、ASTC）等进阶内容。