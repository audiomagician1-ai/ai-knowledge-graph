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
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 纹理压缩

## 概述

纹理压缩（Texture Compression）是GPU硬件直接支持的有损图像压缩技术，其核心特征是：压缩后的数据**无需解压即可直接被GPU采样**，着色器每次采样时硬件透明地完成解码，这与CPU端的PNG/JPEG压缩有本质区别——JPEG必须先完全解压到内存才能使用。正因如此，纹理压缩能同时降低显存占用和显存带宽消耗，而不会引入额外的解码延迟。

纹理压缩格式的历史可以追溯到1998年，S3公司发布了S3TC（S3 Texture Compression），后被DirectX标准化为DXTC，现代称为BC（Block Compression）系列。同年，OpenGL扩展EXT_texture_compression_s3tc将其引入跨平台生态。2004年前后，移动GPU的崛起推动了ETC（Ericsson Texture Compression）的诞生，专为嵌入式设备设计。2012年，ARM与多家厂商联合推出ASTC（Adaptive Scalable Texture Compression），凭借灵活的块尺寸设计成为目前最先进的通用压缩标准。

选择正确的纹理压缩格式对游戏和实时渲染应用至关重要：一张未压缩的2048×2048 RGBA8纹理占用16MB显存，而BC7压缩后仅需4MB，压缩比为4:1；ASTC 4×4块在相同质量下同样实现4:1压缩。在移动平台上，显存带宽往往是性能瓶颈，合理的纹理压缩可以将带宽消耗降低50%～75%。

---

## 核心原理

### 块压缩的基本编码机制

所有主流纹理压缩格式均采用**固定块大小编码**策略：将纹理划分为4×4像素的小块（ASTC支持更大块），每块独立编码为固定字节数的压缩数据。BC1格式每块占8字节，BC3/BC7每块占16字节，因此整张纹理的压缩后大小严格可预测，这与JPEG的变长编码截然不同。

以BC1为例，其每块存储2个16位基准颜色（color0和color1，RGB565格式）以及16个2位索引（每像素2位）。解码时，GPU用这2个颜色插值出4个颜色端点（当color0 > color1时启用1/3和2/3插值；当color0 ≤ color1时其中一个端点为透明黑色），每个像素的颜色由其2位索引在这4个端点中查表得到。整个解码过程只需少量硬件逻辑，延迟极低。

### BC1至BC7各格式特性对比

| 格式 | 每块字节 | 压缩比（RGBA8） | 适用场景 |
|------|---------|--------------|---------|
| BC1  | 8       | 8:1（无Alpha）  | 不透明漫反射贴图 |
| BC3  | 16      | 4:1           | 带Alpha的漫反射贴图 |
| BC4  | 8       | 8:1（单通道）   | 粗糙度/AO等灰度图 |
| BC5  | 16      | 4:1（双通道）   | 法线贴图（XY通道） |
| BC6H | 16      | 4:1           | HDR环境贴图（浮点） |
| BC7  | 16      | 4:1           | 高质量RGBA，失真最低 |

BC5专为法线贴图设计：法线向量Z分量可从X、Y重建（Z = √(1 - X² - Y²)），因此只压缩两个通道既节省空间又保留精度，这是BC3存储法线贴图的典型替代方案。

### ASTC的自适应块尺寸优势

ASTC（Adaptive Scalable Texture Compression）最显著的创新是支持从4×4到12×12的多种块尺寸，全部固定编码为16字节/块。块尺寸越大，压缩比越高但质量越低：
- ASTC 4×4：压缩比8:1（相对RGB8），画质最优
- ASTC 6×6：压缩比约18:1
- ASTC 8×8：压缩比约32:1，适合低质量需求

此外，ASTC原生支持HDR（高动态范围）和3D纹理压缩，并且支持最多4通道的任意组合，这使得同一种格式能覆盖BC1到BC6H的所有使用场景。ASTC由OpenGL ES 3.2和Vulkan核心支持，Apple A8芯片（2014年）起全面支持，现代Android旗舰机也普遍支持。

### ETC2与移动端兼容性

ETC2是ETC1的超集，强制要求OpenGL ES 3.0兼容设备支持，因此在Android生态中具有极广的覆盖率。ETC1只能压缩RGB（无Alpha），ETC2新增了`GL_COMPRESSED_RGBA8_ETC2_EAC`格式支持带Alpha的RGBA纹理，以及`EAC`（Explicit Alpha Compression）用于压缩单通道和双通道数据（类似BC4/BC5的移动端对应物）。ETC2的块编码精度略低于BC7，但在不支持ASTC的老旧设备上是最优选择。

---

## 实际应用

**平台选择策略**：在实际项目中，通常按如下规则选择格式：
- **PC/主机**：漫反射用BC7，法线贴图用BC5，HDR用BC6H，灰度遮罩用BC4。
- **现代移动端**（Android旗舰 + iOS A8+）：优先使用ASTC 4×4（高质量）或ASTC 6×6（均衡）。
- **兼容性回退**：不支持ASTC的Android设备降级到ETC2；若需支持极老旧的Android 2.x设备，才考虑ETC1。

**Unity中的实现**：Unity的Texture Importer提供"Override for PC"和"Override for Android"等平台分离设置，可以为同一张原始纹理在不同平台输出不同压缩格式，构建时自动打包进对应平台的AssetBundle。

**法线贴图压缩实践**：将法线贴图存入BC5（或ASTC双通道模式）后，着色器中必须重建Z分量：
```glsl
vec3 normal;
normal.xy = texture(normalMap, uv).rg * 2.0 - 1.0;
normal.z = sqrt(max(0.0, 1.0 - dot(normal.xy, normal.xy)));
normal = normalize(normal);
```
这一步骤是使用双通道法线压缩格式的必要配套操作，遗漏会导致光照计算完全错误。

---

## 常见误区

**误区一：纹理压缩格式可以随意替换**。BC1和BC3虽然格式相近，但BC1的透明模式（color0 ≤ color1时）会将某些颜色映射为完全透明，若将一张有平滑Alpha过渡的贴图错误地压缩为BC1，会出现大量"像素穿孔"瑕疵（punch-through alpha）。BC3通过独立的8位Alpha通道块避免了这个问题。

**误区二：ASTC质量总是优于BC7**。在相同压缩比（同为4:1）的情况下，ASTC 4×4与BC7画质接近，但ASTC的编码器质量高度依赖于工具链——低质量的ASTC编码往往不如精心调优的BC7编码。ARM官方的`astcenc`工具支持`-medium`、`-thorough`、`-exhaustive`等质量级别，压缩时间从秒级到分钟级不等。

**误区三：压缩格式只影响显存占用**。纹理压缩同时影响显存带宽：GPU采样一个4×4像素块时，未压缩RGBA8需要从显存读取64字节，而BC7仅需读取16字节，带宽节省75%。在移动端统一内存架构（UMA）中，这直接关系到CPU和GPU共享带宽的争抢，对帧率的影响可能超过显存大小本身。

---

## 知识关联

学习纹理压缩需要先理解**纹理映射概述**中的纹理坐标、Mipmap层级、采样器状态等基本概念——Mipmap的每一层都需要独立压缩，且每层的像素尺寸必须是压缩块大小（通常为4）的整数倍，否则需要填充（padding）。若纹理尺寸非2的幂次，不同压缩格式的边缘处理方式也有差异。

掌握纹理压缩后，**虚拟纹理（Virtual Texture / Sparse Texture）**技术将在此基础上进一步处理超大纹理的流式加载问题——虚拟纹理将地形等超大纹理分割为物理页（Physical Page），每页在加载到显存时必须以压缩格式存储（通常BC7或ASTC），以保证物理纹理池（Physical Texture Pool）在有限显存中容纳足够多的页面。此时对纹理压缩格式块对齐要求和解码延迟的深入理解将直接影响虚拟纹理系统的设计决策。