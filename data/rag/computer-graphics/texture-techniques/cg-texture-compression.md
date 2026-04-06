---
id: "cg-texture-compression"
concept: "纹理压缩"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 88.5
generation_method: "ai-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v2"
  - type: "academic"
    author: "Nystad, J., Lassen, A., Pomianowski, A., Ellis, S., & Olson, T."
    year: 2012
    title: "Adaptive Scalable Texture Compression"
    venue: "High Performance Graphics (HPG 2012)"
  - type: "academic"
    author: "van Waveren, J.M.P., & Castano, I."
    year: 2006
    title: "Real-Time YCoCg-R Compression"
    venue: "id Software / NVIDIA Technical Report"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---



# 纹理压缩

## 概述

纹理压缩（Texture Compression）是GPU硬件直接支持的有损图像压缩技术，其核心特征是：压缩后的数据**无需解压即可直接被GPU采样**，着色器每次采样时硬件透明地完成解码，这与CPU端的PNG/JPEG压缩有本质区别——JPEG必须先完全解压到内存才能使用。正因如此，纹理压缩能同时降低显存占用和显存带宽消耗，而不会引入额外的解码延迟。

纹理压缩格式的历史可以追溯到1998年，S3公司（Silicon & Software Systems）发布了S3TC（S3 Texture Compression），后被Microsoft DirectX 6.0标准化为DXTC，现代称为BC（Block Compression）系列。同年，OpenGL扩展`EXT_texture_compression_s3tc`将其引入跨平台生态。2004年前后，移动GPU的崛起推动了ETC（Ericsson Texture Compression）的诞生，由爱立信研究院（Ericsson Research）专为嵌入式设备设计，并于2005年发表于《IEEE Transactions on Visualization and Computer Graphics》。2012年，ARM与多家厂商联合推出ASTC（Adaptive Scalable Texture Compression），由Nystad等人在High Performance Graphics会议上正式发表（Nystad et al., 2012），凭借灵活的块尺寸设计成为目前最先进的通用压缩标准，并于2014年被Khronos Group纳入OpenGL ES 3.2核心规范。

选择正确的纹理压缩格式对游戏和实时渲染应用至关重要：一张未压缩的2048×2048 RGBA8纹理占用 $2048 \times 2048 \times 4 = 16\text{ MB}$ 显存，而BC7压缩后仅需4MB，压缩比为4:1；ASTC 4×4块在相同质量下同样实现4:1压缩，但编码灵活性更高。在移动平台上，显存带宽往往是性能瓶颈，合理的纹理压缩可以将带宽消耗降低50%～75%。

---

## 核心原理：块压缩的基本编码机制

所有主流纹理压缩格式均采用**固定块大小编码**策略：将纹理划分为4×4像素的小块（ASTC支持更大块），每块独立编码为固定字节数的压缩数据。BC1格式每块占8字节，BC3/BC7每块占16字节，因此整张纹理的压缩后大小严格可预测，这与JPEG的变长编码截然不同。

对于一张宽 $W$、高 $H$ 像素的纹理，使用块尺寸为 $B_x \times B_y$、每块占 $S$ 字节的格式，压缩后总大小为：

$$\text{CompressedSize} = \left\lceil \frac{W}{B_x} \right\rceil \times \left\lceil \frac{H}{B_y} \right\rceil \times S$$

以BC1为例，其每块存储2个16位基准颜色（color0和color1，RGB565格式）以及16个2位索引（每像素2位）。解码时，GPU用这2个颜色插值出4个颜色端点——当 $\text{color0} > \text{color1}$ 时启用1/3和2/3线性插值；当 $\text{color0} \leq \text{color1}$ 时其中一个端点为透明黑色（punch-through alpha模式）——每个像素的颜色由其2位索引在这4个端点中查表得到。整个解码过程只需少量硬件逻辑，延迟极低，典型GPU上每时钟周期可完成多个4×4块的解码。

**例如**，一张512×512的BC1压缩纹理，块数为 $128 \times 128 = 16384$ 块，每块8字节，总占用 $16384 \times 8 = 128\text{ KB}$，而未压缩RGB8版本需要 $512 \times 512 \times 3 \approx 768\text{ KB}$，节省约83%。

---

## BC格式家族详解（BC1至BC7）

### 各格式特性对比

| 格式  | 每块字节 | 压缩比（vs RGBA8） | 通道支持        | 适用场景                      |
|-------|---------|-----------------|---------------|------------------------------|
| BC1   | 8       | 8:1（无Alpha）    | RGB + 1位Alpha | 不透明漫反射贴图               |
| BC2   | 16      | 4:1             | RGBA（4位Alpha）| 旧式带Alpha贴图（已基本淘汰）   |
| BC3   | 16      | 4:1             | RGBA（8位Alpha）| 带平滑Alpha的漫反射贴图         |
| BC4   | 8       | 8:1（单通道）     | R             | 粗糙度/AO等灰度遮罩图           |
| BC5   | 16      | 4:1（双通道）     | RG            | 法线贴图（XY通道）              |
| BC6H  | 16      | 4:1             | RGB（半精度浮点）| HDR环境贴图、光照贴图           |
| BC7   | 16      | 4:1             | RGBA          | 高质量RGBA，视觉失真最低        |

BC5专为法线贴图设计：法线向量Z分量可从X、Y重建，公式为 $Z = \sqrt{\max(0,\, 1 - X^2 - Y^2)}$，因此只压缩两个通道既节省空间又保留切线空间精度，是BC3存储法线贴图的标准替代方案（van Waveren & Castano, 2006）。BC7于DirectX 11（2009年）随Direct3D 11.0引入，其编码器支持多达8种编码模式（Mode 0～Mode 7），可根据块内色彩复杂度自适应选择最优模式，因此在同等压缩比下画质显著优于BC1/BC3。

---

## ASTC：自适应块尺寸的现代标准

ASTC（Adaptive Scalable Texture Compression）最显著的创新是支持从4×4到12×12的多种块尺寸，全部固定编码为**16字节/块**。块尺寸越大，压缩比越高但质量越低：

| 块尺寸  | 每像素比特数（bpp） | 约等效压缩比（vs RGBA8） | 典型用途              |
|--------|-------------------|----------------------|--------------------|
| 4×4    | 8.00 bpp          | 4:1                  | 高质量漫反射、UI贴图   |
| 5×5    | 5.12 bpp          | 约6.3:1              | 均衡质量场景贴图       |
| 6×6    | 3.56 bpp          | 约9:1                | 地形、远景贴图         |
| 8×8    | 2.00 bpp          | 16:1                 | 低质量需求、粒子贴图   |
| 10×10  | 1.28 bpp          | 约25:1               | 极高压缩比场合         |
| 12×12  | 0.89 bpp          | 约36:1               | 低质量背景纹理         |

此外，ASTC原生支持HDR（高动态范围）和3D纹理压缩，并且支持最多4通道的任意组合，这使得同一种格式能覆盖BC1到BC6H的所有使用场景。ASTC由OpenGL ES 3.2和Vulkan核心规范强制支持，Apple A8芯片（2014年，iPhone 6首发）起全面支持，高通Adreno 400系列（2014年）、ARM Mali-T760（2014年）起也全面支持，现代Android旗舰机已普遍覆盖。

ARM官方开源编码器`astcenc`（GitHub: ARM-software/astc-encoder）支持`-fast`、`-medium`、`-thorough`、`-exhaustive`四个质量级别，对2048×2048纹理的编码时间从约2秒（`-fast`）到超过60秒（`-exhaustive`）不等，项目团队需在构建时间与纹理质量之间权衡。

---

## ETC2与移动端兼容性策略

ETC2是ETC1的超集，强制要求OpenGL ES 3.0（2012年）兼容设备支持，因此在Android生态中具有极广的覆盖率，截至2023年Android设备中约99%支持OpenGL ES 3.0。ETC1只能压缩RGB（无Alpha通道），ETC2新增了`GL_COMPRESSED_RGBA8_ETC2_EAC`格式支持带Alpha的RGBA纹理，以及EAC（Explicit Alpha Compression）用于压缩单通道（`GL_COMPRESSED_R11_EAC`）和双通道（`GL_COMPRESSED_RG11_EAC`）数据，分别对应BC4和BC5的移动端替代方案。

ETC2的块编码精度略低于BC7，主要原因是其编码模式较少（ETC2每块仅有"individual"、"differential"、"T"、"H"、"Planar"五种模式），但在不支持ASTC的老旧设备（如2013年前的中低端Android机型）上是最优选择。

**平台选择决策树**：
- **PC / 主机（PS5、Xbox Series X）**：漫反射贴图用BC7，法线贴图用BC5，HDR环境贴图用BC6H，单通道遮罩用BC4。
- **现代移动端**（Android旗舰2014年后 + iOS A8+）：优先使用ASTC 4×4（高质量）或ASTC 6×6（均衡）。
- **兼容性回退**：不支持ASTC的Android设备降级到ETC2；若需覆盖Android 2.x时代（2010～2012年）极老设备，才考虑ETC1（需另存Alpha通道）。

---

## 实际应用与工程实践

### Unity与Unreal中的实现

**Unity**（2022 LTS及以上）的Texture Importer提供"Override for PC"和"Override for Android"等平台分离设置，可为同一张原始纹理在不同平台输出不同压缩格式，构建时自动打包进对应平台的AssetBundle。Unity的压缩质量选项对应`astcenc`的质量级别，"Best"等级在大型项目中可能显著增加构建时间，建议开发阶段使用"Normal"，发布前切换"Best"。

**Unreal Engine 5**通过"Texture Group"和"Compression Settings"统一管理，选择`TC_Normalmap`时自动在PC上使用BC5、在移动端使用ETC2/ASTC。

### 法线贴图压缩实践

将法线贴图存入BC5（或ASTC双通道模式）后，着色器中**必须**重建Z分量：

```glsl
vec3 normal;
normal.xy = texture(normalMap, uv).rg * 2.0 - 1.0;
normal.z  = sqrt(max(0.0, 1.0 - dot(normal.xy, normal.xy)));
normal    = normalize(normal);
```

这一步骤是使用双通道法线压缩格式的必要配套操作，遗漏会导致法线Z分量始终为0，光照计算完全错误，表面呈现出"扁平化"的高光异常。

**例如**，在UE5的材质编辑器中，若将法线贴图的Compression Settings误设为`TC_Default`（BC7）而非`TC_Normalmap`（BC5），则贴图体积增大不明显，但采样后无需手动重建Z分量，因为BC7已存储完整的三通道数据；而切换为BC5后，材质蓝图中若直接使用RGB输出而不经过"Reconstruct Normal Z"节点，将产生错误的光照结果。

---

## 常见误区与深层辨析

**误区