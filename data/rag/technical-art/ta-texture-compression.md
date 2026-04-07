# 纹理压缩

## 概述

纹理压缩是专为GPU硬件设计的**固定速率有损编码技术**，其核心特性是：GPU在纹理采样阶段能够以硬件电路直接解码压缩块，无需将完整纹理解压至显存后再读取。这一特性与通用压缩算法（ZIP、LZ4）有本质区别——后者必须完全解压才能随机访问任意字节，而纹理压缩格式的每个编码块彼此独立，支持 $O(1)$ 时间内定位并解码任意像素。

纹理压缩技术的历史脉络清晰：1998年，S3 Graphics开发了S3TC（S3 Texture Compression），被微软采纳后以DXT1/3/5命名进入DirectX 6标准，后来被Khronos归一化为BC1–BC5系列（Brownell, 2006）。2004年爱立信提出ETC1并捆绑进OpenGL ES 2.0强制规范，保证了Android早期的基本压缩支持。2012年，ARM与AMD联合向Khronos提交ASTC（Adaptive Scalable Texture Compression）标准，并于OpenGL ES 3.2及Vulkan中成为可选扩展（Nystad et al., 2012）。

一张未压缩的2048×2048 RGBA8纹理在GPU显存中占用 $2048 \times 2048 \times 4 = 16\,\text{MB}$，而同等内容的BC7压缩版本仅占4 MB，压缩比恰好为4:1。在移动端，主流旗舰设备的共享显存预算通常在1–2 GB之间，若项目中100张2K纹理全部以未压缩格式存储，仅纹理一项即消耗1.6 GB，直接触发系统强制回收，导致画面黑块或应用崩溃。

---

## 核心原理

### 块压缩的编码机制

所有主流格式均以**固定尺寸像素块**为编码单元。以BC1为例：纹理被切分为若干4×4像素块，每块存储**两个16位端点颜色**（RGB565格式各占2字节，共4字节）和**16个2位索引**（共4字节），合计**8字节/块**。原始RGBA8的4×4块大小为 $4 \times 4 \times 4 = 64$ 字节，因此BC1的压缩比为：

$$
\text{压缩比} = \frac{64\,\text{字节}}{8\,\text{字节}} = 8:1
$$

GPU采样时，硬件电路通过两个端点颜色 $C_0$、$C_1$ 线性插值生成4色调色板：

$$
C_2 = \frac{2C_0 + C_1}{3}, \quad C_3 = \frac{C_0 + 2C_1}{3}
$$

每个像素通过2位索引从调色板取色，整个解码流程在一个固定延迟的硬件电路中完成，不消耗额外的显存带宽。

这一机制也直接决定了BC1的局限：16个像素仅能表达4种颜色，当块内颜色变化剧烈时（如文字边缘、法线贴图高频区域），调色板无法覆盖真实颜色分布，产生肉眼可见的"块状瑕疵"（block artifacts）。BC7通过将每个4×4块分割为多达3个子集、每子集独立选择端点，将可表达颜色数量提升至数十种，显著改善了高频细节区域的质量，但编码复杂度使BC7的压缩时间比BC1长约100倍。

### ASTC的可变块尺寸原理

ASTC的革命性在于打破了"块固定为4×4"的约束，支持从 $4 \times 4$ 到 $12 \times 12$ 共14种块尺寸，每块统一存储**128位（16字节）**数据。不同块尺寸对应不同压缩比：

$$
\text{位率（bpp）} = \frac{128}{W \times H}
$$

| 块尺寸 | 位率（bpp） | 压缩比（相对RGBA8） |
|--------|------------|------------------|
| 4×4    | 8.00 bpp   | 4:1              |
| 5×5    | 5.12 bpp   | 6.25:1           |
| 6×6    | 3.56 bpp   | 9:1              |
| 8×8    | 2.00 bpp   | 16:1             |
| 10×10  | 1.28 bpp   | 25:1             |
| 12×12  | 0.89 bpp   | ~36:1            |

ASTC还支持HDR模式（FP16端点）和3D纹理块（如 $4\times4\times4$），这是BC和ETC系列完全不具备的能力。Nystad等人在2012年的论文中实测ASTC 4×4的PSNR比ETC2高约1–2 dB，比BC7相当或略低，但ASTC是唯一同时支持LDR/HDR/法线/透明度的统一格式（Nystad et al., 2012）。

### ETC系列的历史演进

ETC1（2004年）编码每个4×4块时将其分为两个2×4或4×2子块，每个子块共享一个基础颜色，通过查找4个预定义的"修饰符表"偏移来还原颜色，存储大小同为8字节，压缩比8:1。ETC1的致命缺陷是**不支持Alpha通道**，导致带透明度的UI纹理在早期Android上必须用两张ETC1纹理（分别存RGB和A）合并采样，消耗双倍内存与采样次数。

ETC2作为ETC1的超集在OpenGL ES 3.0（2012年）中强制支持，新增了RGB8 Punchthrough Alpha（1位透明）和RGBA8两种模式，并对RGB8模式在"溢出区域"（两个端点颜色经线性组合后超出RGB范围的情况）引入了独立的"T型"和"H型"编码，使质量略优于ETC1。EAC（Ericsson Alpha Compression）作为ETC2的Alpha分量扩展，可单独用于R11/RG11单双通道纹理，非常适合灰度遮罩贴图。

---

## 关键方法与平台选择矩阵

### 平台差异与格式兼容性

纹理压缩格式的平台支持碎片化是技术美术最头疼的问题之一：

| 平台 | 推荐格式 | 回退格式 | 硬件要求 |
|------|---------|---------|---------|
| PC（DX11+） | BC7 | BC3/BC5 | DirectX 11 Feature Level 11_0 |
| PC（DX10）  | BC5/BC3 | BC1 | DirectX 10 |
| iOS（A8+）  | ASTC 4×4–6×6 | PVRTC 4bpp | iPhone 6 及以上 |
| iOS（A7以下）| PVRTC 4bpp | RGBA8 | A7芯片 |
| Android（高端）| ASTC 4×4 | ETC2 | OpenGL ES 3.2 / Vulkan |
| Android（中端）| ETC2 | ETC1+Alpha | OpenGL ES 3.0 |
| Nintendo Switch | ASTC 4×4–8×8 / BC | — | Tegra X1 支持两者 |
| PlayStation 5 | BC7 / BC6H | BC3 | GCN架构全支持 |

**BC6H**（DirectX 11引入）是唯一专为HDR（FP16）内容设计的BC格式，使用128位/块存储RGB三通道浮点颜色，无Alpha，适合天空盒、IBL光照探针等HDR贴图，在PC和主机上替代RGBA16F可节省50%显存。

### 法线贴图的特殊处理

法线贴图不应使用BC3（DXT5）的RGB通道直接压缩三分量法线，而应使用**BC5**（又称ATI2N或3Dc）：BC5以两个独立的BC4通道分别存储法线的X（R）和Y（G）分量，Z分量在Shader中通过 $Z = \sqrt{1 - X^2 - Y^2}$ 重建，从而避免BC3对三通道联合压缩导致的法线方向偏转误差。

$$
N_z = \sqrt{\max(0,\; 1 - N_x^2 - N_y^2)}
$$

ASTC在法线贴图上可直接使用"法线贴图模式"（`astcenc`工具的`-normal_psnr`标志），该模式优化角度误差而非颜色通道误差，测试表明ASTC 6×6法线贴图的角度RMSE约为0.8°，优于BC5的约1.2°（Nystad et al., 2012）。

### Unity与Unreal中的压缩配置

**Unity**通过Texture Importer的`Compression`和`Format`字段控制每平台格式，支持`Crunch`二次压缩（基于DXT/ETC的有损DCT二次编码，进一步减少磁盘体积约50%，但会略降低GPU端质量）。对于Android构建，Unity 2020+默认使用ASTC作为高端设备格式，ETC2作为回退。

**Unreal Engine 5**的纹理导入系统将纹理按用途自动选择格式：`TC_Default`在PC上映射BC1/BC3，在iOS上映射ASTC 4×4；`TC_Normalmap`映射BC5（PC）或ASTC 4×4（移动端）；`TC_HDR`映射BC6H或RGBA16F。技术美术若手动覆盖为非推荐格式，UE5会在构建时发出警告。

---

## 实际应用案例

### 案例一：移动端UI纹理的内存优化

某手机MMO项目UI图集（4096×4096，含RGBA透明通道）初始以PNG导入且未压缩，占用 $4096 \times 4096 \times 4 = 64\,\text{MB}$。优化流程：

1. 将不透明区域从RGBA分离为独立RGB图集，使用ASTC 6×6（约7 MB）；
2. 透明遮罩单独存为ASTC 8×8单通道（约4 MB）；
3. 含半透明的UI元素使用ASTC 4×4（约16 MB）。

三类分组合计约27 MB，节省约58%显存，帧率从47fps提升至56fps（显存带宽减少导致GPU读取等待时间降低）。

### 案例二：PC端PBR贴图的格式选择

一套标准PBR材质包含BaseColor、Normal、ORM（Occlusion/Roughness/Metallic）三张2K贴图：

- **BaseColor**（sRGB，需感知精度）→ BC7，4 MB，质量最优
- **Normal**（线性，XY双通道）→ BC5，4 MB，Z通道Shader重建
- **ORM**（线性，三通道独立语义）→ BC7，4 MB（或BC3如需节省内存）

三张贴图合计12 MB（BC7方案）。若使用BC3全部替换，降至12 MB不变但BaseColor和ORM质量下降；若使用未压缩RGBA8，合计48 MB，是压缩版的4倍。

---

## 常见误区

**误区一：认为压缩比越高画质损失越严重**
ASTC 8×8（2 bpp，16:1压缩比）用于低频颜色变化的天空渐变贴图时，PSNR可达42 dB以上，肉眼无差异。而BC1（8:1）用于高频法线贴图时PSNR可能只有28 dB，块状瑕疵明显。**压缩质量取决于内容频率与格式的匹配度，而非单一压缩比。**

**误区二：在sRGB纹理上使用BC5**
BC5针对线性空间的双通道数据（法线XY）设计，若对sRGB颜色纹理使用BC5，硬件sRGB解码流程将对只有两个通道的数据解码，导致颜色还原错误。sRGB纹理必须配合支持sRGB标记的格式（BC1_SRGB、BC7_SRGB、ASTC的sRGB模式）。

**误区三：认为ETC1足以覆盖所有Android设备**
ETC1不支持Alpha通道，且自2019年起Google Play要求目标API Level ≥ 29（Android 10），OpenGL ES 3.0（ETC2支持）在2022年的Android设备占有率已超过97%（Google Android Distribution Dashboard, 2022）。继续使用ETC1+RGB+Alpha双纹理方案只会增加Draw Call与内存，无实际兼容收益。

**误区四：Crunch压缩可以无损应用于所有纹理**
Crunch是有损的二次压缩，其DCT编码会在BC/ETC基础上额外引入约0.5–1.5 dB的PSNR损失，且解压CPU开销在