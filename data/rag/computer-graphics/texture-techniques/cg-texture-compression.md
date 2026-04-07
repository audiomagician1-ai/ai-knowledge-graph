# 纹理压缩

## 概述

纹理压缩（Texture Compression）是GPU硬件直接支持的有损图像压缩技术，其核心特征是：压缩后的数据**无需解压即可直接被GPU采样**，着色器每次采样时硬件透明地完成解码，这与CPU端的PNG/JPEG压缩有本质区别——JPEG必须先完全解压到内存才能使用。正因如此，纹理压缩能同时降低显存占用和显存带宽消耗，而不会引入额外的解码延迟。

纹理压缩格式的历史可以追溯到1998年，S3公司（Silicon & Software Systems）发布了S3TC（S3 Texture Compression），后被Microsoft DirectX 6.0标准化为DXTC，现代称为BC（Block Compression）系列。同年，OpenGL扩展`EXT_texture_compression_s3tc`将其引入跨平台生态。2004年前后，移动GPU的崛起推动了ETC（Ericsson Texture Compression）的诞生，由爱立信研究院（Ericsson Research）专为嵌入式设备设计，并于2005年发表于《IEEE Transactions on Visualization and Computer Graphics》。2012年，ARM与多家厂商联合推出ASTC（Adaptive Scalable Texture Compression），由Nystad等人在High Performance Graphics会议上正式发表（Nystad et al., 2012），凭借灵活的块尺寸设计成为目前最先进的通用压缩标准，并于2014年被Khronos Group纳入OpenGL ES 3.2核心规范。

选择正确的纹理压缩格式对游戏和实时渲染应用至关重要：一张未压缩的2048×2048 RGBA8纹理占用 $2048 \times 2048 \times 4 = 16\text{ MB}$ 显存，而BC7压缩后仅需4 MB，压缩比为4:1；ASTC 4×4块在相同质量下同样实现4:1压缩，但编码灵活性更高。在移动平台上，显存带宽往往是性能瓶颈，合理的纹理压缩可以将带宽消耗降低50%～75%，对功耗和发热亦有显著改善。据Epic Games公开的《堡垒之夜》移动版优化报告，全面切换ASTC格式后帧率提升约12%，GPU功耗下降约18%，充分说明纹理压缩的实际工程价值远超理论层面的讨论。

---

## 核心原理：块压缩的基本编码机制

所有主流纹理压缩格式均采用**固定块大小编码**策略：将纹理划分为4×4像素的小块（ASTC支持更大块），每块独立编码为固定字节数的压缩数据。BC1格式每块占8字节，BC3/BC7每块占16字节，因此整张纹理的压缩后大小严格可预测，这与JPEG的变长编码截然不同。

对于一张宽 $W$、高 $H$ 像素的纹理，使用块尺寸为 $B_x \times B_y$、每块占 $S$ 字节的格式，压缩后总大小为：

$$\text{CompressedSize} = \left\lceil \frac{W}{B_x} \right\rceil \times \left\lceil \frac{H}{B_y} \right\rceil \times S$$

以BC1为例，其每块存储2个16位基准颜色（color0和color1，RGB565格式）以及16个2位索引（每像素2位）。解码时，GPU用这2个颜色插值出4个颜色端点——当 $\text{color0} > \text{color1}$ 时启用1/3和2/3线性插值；当 $\text{color0} \leq \text{color1}$ 时其中一个端点为透明黑色（punch-through alpha模式）——每个像素的颜色由其2位索引在这4个端点中查表得到。整个解码过程只需少量硬件逻辑，延迟极低，典型GPU上每时钟周期可完成多个4×4块的解码。

每像素所占比特数（bits per pixel，bpp）是评价纹理压缩效率的核心指标：

$$\text{bpp} = \frac{S \times 8}{B_x \times B_y}$$

BC1的 $\text{bpp} = \frac{8 \times 8}{4 \times 4} = 4\text{ bpp}$，而未压缩RGBA8为32 bpp，压缩比恰好为8:1（不含Alpha时）。

**例如**，一张512×512的BC1压缩纹理，块数为 $128 \times 128 = 16384$ 块，每块8字节，总占用 $16384 \times 8 = 128\text{ KB}$，而未压缩RGB8版本需要 $512 \times 512 \times 3 \approx 768\text{ KB}$，节省约83%。如果整个游戏项目有500张同等规模的漫反射贴图，BC1压缩可将纹理总显存从约375 MB降至约62.5 MB，差异在移动端尤为关键。

### 编码质量与率失真权衡

块压缩本质上是一种**矢量量化（Vector Quantization）**问题：在给定比特预算内，寻找使块内像素重建误差最小的端点对。端点优化常用的目标函数是均方误差（MSE），定义如下——设块内有 $N$ 个像素，原始颜色为 $c_i$，重建颜色为 $\hat{c}_i$，则：

$$\text{MSE} = \frac{1}{N} \sum_{i=1}^{N} \|c_i - \hat{c}_i\|^2$$

但人眼对色度误差比亮度误差更不敏感，部分高质量编码器（如`astcenc -exhaustive`）引入感知加权误差，令视觉质量优于纯MSE优化。正因编码复杂度高，离线编码（预计算）是业界标准做法——实时压缩仅在流式传输或程序生成纹理等特定场景下出现，且通常采用精度损失更大的快速算法（Castano, 2020）。

峰值信噪比（PSNR）是衡量压缩质量最常见的客观指标，定义为：

$$\text{PSNR} = 10 \cdot \log_{10}\left(\frac{255^2}{\text{MSE}}\right) \text{ dB}$$

一般认为PSNR高于40 dB时压缩失真对人眼不可察觉，BC7在典型漫反射贴图上的PSNR通常在44～50 dB之间，而BC1处理含有平滑渐变的纹理时可能低至35 dB，产生明显的色带（color banding）伪影。

### Mipmap与纹理压缩的协同

纹理压缩在Mipmap链中同样适用，每一级Mipmap均独立压缩。值得注意的是，当纹理尺寸小于块尺寸时（如4×4块格式下2×2的Mip层级），GPU实现需要对边界块进行填充（padding），填充像素通常复制边缘像素值。在纹理工具链（如`texturenc`或Unity的Texture Importer）中，对Mipmap启用**Mip淡出（Mip Fade）**功能可以缓解低层级Mipmap上的块状伪影，因为低层级本身已足够模糊，少量的量化误差不会被放大。

---

## BC格式家族详解（BC1至BC7）

### 各格式特性对比

| 格式  | 每块字节 | 每像素比特数 | 通道支持        | 适用场景                      |
|-------|---------|------------|---------------|------------------------------|
| BC1   | 8       | 4 bpp      | RGB + 1位Alpha | 不透明漫反射贴图               |
| BC2   | 16      | 8 bpp      | RGBA（4位Alpha）| 旧式带Alpha贴图（已基本淘汰）   |
| BC3   | 16      | 8 bpp      | RGBA（8位Alpha）| 带平滑Alpha的漫反射贴图         |
| BC4   | 8       | 4 bpp      | R（单通道）     | 粗糙度/AO等灰度遮罩图           |
| BC5   | 16      | 8 bpp      | RG（双通道）    | 法线贴图（XY通道）              |
| BC6H  | 16      | 8 bpp      | RGB（半精度浮点）| HDR环境贴图、光照贴图           |
| BC7   | 16      | 8 bpp      | RGBA          | 高质量RGBA，视觉失真最低        |

BC5专为法线贴图设计：法线向量Z分量可从X、Y重建，公式为

$$Z = \sqrt{\max(0,\; 1 - X^2 - Y^2)}$$

因此只压缩两个通道既节省空间又保留切线空间精度，是BC3存储法线贴图的标准替代方案（van Waveren & Castano, 2006）。BC7于DirectX 11（2009年）随Direct3D 11.0引入，其编码器支持多达8种编码模式（Mode 0～Mode 7），可根据块内色彩复杂度自适应选择最优模式，因此在同等压缩比下画质显著优于BC1/BC3。BC6H专门处理半精度浮点（FP16）HDR数据，其编码范围覆盖 $[0, 65504]$，能无损表达Reinhard色调映射前的原始HDR光照值，是IBL（Image-Based Lighting）管线中存储辐照度图（Irradiance Map）和预过滤环境贴图（Prefiltered Environment Map）的首选格式。

### YCoCg-R色彩空间与压缩质量

van Waveren与Castano（2006）提出将RGB色彩空间先转换为YCoCg-R再进行BC3压缩的技术。YCoCg-R的Y通道（亮度）存入BC3的Alpha通道（独立8位精度），Co和Cg色度分量存入RGB通道，利用人眼对亮度更敏感的特性实现感知上更优的压缩质量。具体转换公式为：

$$\begin{aligned}
Co &= R - B \\
t  &= B + \lfloor Co/2 \rfloor \\
Cg &= G - t \\
Y  &= t + \lfloor Cg/2 \rfloor
\end{aligned}$$

上述变换是无损整数变换，逆变换同样精确，这意味着在BC3的限制下，亮度通道Y可获得完整的8位精度而不受色度量化的影响。这一技术在需要高质量但无法使用BC7（如DirectX 10之前的硬件）的场合被广泛采用，并在《使命召唤：现代战争》等AAA项目中有实际部署记录。

---

## ASTC：自适应块尺寸的现代标准

ASTC（Adaptive Scalable Texture Compression）最显著的创新是支持从4×4到12×12的多种块尺寸，全部固定编码为**16字节/块**。块尺寸越大，压缩比越高但质量越低：

| 块尺寸  | 每像素比特数（bpp） | 约等效压缩比（vs RGBA8） | 典型用途              |
|--------|------------------|----------------------|--------------------|
| 4×4    | 8.00 bpp         | 4:1                  | 高质量漫反射、UI贴图   |
| 5×5    | 5.12 bpp         | 约6.3:1              | 均衡质量场景贴图       |
| 6×6    | 3.56 bpp         | 约9:1                | 地形、远景贴图         |
| 8×8    | 2.00 bpp         | 16:1                 | 低质量需求、粒子贴图   |
| 10×10  | 1.28 bpp         | 约25:1               | 极高压缩比场合         |
| 12×12  | 0.89 bpp         | 约36:1               | 低质量背景纹理         |

此外，ASTC原生支持HDR（高动态范围）和3D纹理压缩，并且支持最多4通道的任意组合，这使得同一种格式能覆盖BC1到BC6H的所有使用场景。ASTC由OpenGL ES 3.2和Vulkan核心规范强制支持，Apple A8芯片（2014年，iPhone 6首发）起全面支持，高通Adreno 400系列（2014年）、ARM Mali-T760（2014年）起也全面支持，现代Android旗舰机已普遍覆盖。

ASTC的16字节块内部结构极为灵活：编码器可以选择1或2个颜色端点对（单/双分区），可以使用高达8位权重格网（weight grid），权重格网的分辨率与块尺寸解耦，这意味着编码器能在块内自适应分配比特预算给颜色端点和权重——这正是ASTC在