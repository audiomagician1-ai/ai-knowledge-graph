---
id: "ta-texture-compression"
concept: "纹理压缩"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 2
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
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

纹理压缩是一种将纹理图像以有损格式存储在GPU显存中的技术，其核心特征是GPU可以**直接对压缩数据进行采样**，无需在读取前完整解压缩。这与ZIP或PNG的软件压缩有本质区别——后者必须先解压到内存才能使用，而纹理压缩格式（如BC7、ASTC）由GPU硬件解码器实时处理，解码延迟几乎为零。

纹理压缩格式的历史可追溯至1999年NVIDIA发布的S3TC（后标准化为DXT），其中DXT1/DXT5成为PC平台沿用至今的经典格式。2010年前后，移动GPU的崛起催生了ETC（爱立信纹理压缩）和PVRTC格式，分别面向Android和iOS硬件。Khronos Group在2012年提出ASTC（Adaptive Scalable Texture Compression），凭借可变块尺寸设计逐渐成为移动平台的统一标准。

纹理压缩在技术美术工作中意义直接体现在两个数字上：一张2048×2048的RGBA未压缩纹理占用16MB显存，而BC7压缩后仅需4MB，ASTC 4x4压缩后约8MB——在显存预算严格的移动设备上，这往往决定一个场景能容纳多少张纹理资产。

---

## 核心原理

### 块压缩的基本机制

所有主流纹理压缩格式均采用**固定块尺寸编码**：将纹理划分为若干4×4像素块（ASTC支持4×4到12×12的可变块），每块独立编码为固定字节数的数据。以BC1（DXT1）为例，每个4×4像素块（16个像素）被压缩为8字节，存储两个16位端点颜色和16个2-bit索引值，压缩比固定为6:1（相对于RGB8格式）。这种固定压缩比的特性让GPU可以通过简单的地址计算定位任意纹素，实现O(1)随机访问。

### 主流格式对比

**BC系列（Block Compression）** 是DirectX标准格式，广泛用于PC和主机平台：
- **BC1**：RGB无Alpha或1bit Alpha，每像素0.5字节，适合不透明漫反射贴图
- **BC3（DXT5）**：RGBA，每像素1字节，Alpha通道单独用BC4算法压缩，适合带透明度的贴图
- **BC5**：双通道RG，每像素1字节，专为法线贴图设计，分别压缩X/Y分量后Shader中重建Z分量（`z = sqrt(1 - x² - y²)`）
- **BC7**：RGBA高质量，每像素1字节，引入多种编码模式（8种模式自适应选择），画质远优于BC3，是PBR流程中Albedo和Roughness贴图的首选

**ASTC（Adaptive Scalable Texture Compression）** 由ARM主导开发，iOS A8（2014年）及Android OpenGL ES 3.1设备起开始普及：
- 块尺寸从4×4到12×12可调，每块固定16字节，因此4×4时每像素1字节，12×12时每像素约0.11字节
- 支持HDR纹理（LDR/HDR双模式）和3D纹理，是目前移动端功能最全面的压缩格式
- ASTC 6×6（每像素约0.44字节）是移动端画质与内存的常用平衡点

**ETC系列** 是Android的历史标准：
- **ETC1**：仅RGB，不支持Alpha，曾是Android OpenGL ES 2.0的必须支持格式
- **ETC2**：增加Alpha支持，OpenGL ES 3.0强制要求，兼容性覆盖2013年后绝大多数Android设备

### 质量评估指标

纹理压缩的质量损失通常以**PSNR（峰值信噪比）**衡量，单位dB，数值越高失真越小。BC7在典型漫反射贴图上PSNR可达45dB以上，BC1约38dB，而ASTC 4×4与BC7质量相当，ASTC 8×8降至约36dB。法线贴图因其高频细节对压缩伪影更敏感，BC5的双通道独立压缩策略使其PSNR比BC3压缩法线贴图高出约4-6dB。

---

## 实际应用

**PBR材质中的格式分配策略** 是技术美术日常工作的核心决策：

| 贴图类型 | PC/主机推荐 | 移动端推荐 | 原因 |
|---------|-----------|----------|------|
| Albedo（带Alpha） | BC7 | ASTC 4×4 | 需要高颜色精度 |
| 法线贴图 | BC5 | ASTC 4×4 | 保留XY精度 |
| Roughness/Metallic | BC4（单通道）或打包BC7 | ASTC 6×6 | 灰度信息容错性较高 |
| HDR环境贴图 | BC6H | ASTC HDR 6×6 | 专用HDR格式 |

在Unity中，纹理压缩格式通过Texture Importer的`Compression`和`Format`字段手动指定，或使用`Default`让引擎按平台自动选择。Unreal Engine的`LODGroup`预设中内置了不同平台的格式映射，技术美术可通过修改`DefaultDeviceProfiles.ini`统一调整全项目压缩策略。

**ASTC的运行时压缩**在某些移动项目中用于动态生成的纹理（如程序化地形），ARM Mali GPU支持通过计算着色器进行ASTC编码，但编码耗时约为BC7软件编码的5-10倍，仅适合低频更新场景。

---

## 常见误区

**误区一：法线贴图应使用BC3/DXT5压缩**

许多美术会直接将法线贴图以BC3格式导入，因为它"支持四通道"。然而BC3对RGBA四通道均等压缩，而法线贴图的Z通道是冗余信息，真正需要高精度的是X和Y通道。BC5专门对双通道进行高质量独立压缩，同等字节数下法线方向精度显著更高。实际测试中，BC5压缩法线贴图的光照高频细节明显优于BC3，是正确选择。

**误区二：ASTC在所有移动设备上均可用**

ASTC需要OpenGL ES 3.1或Vulkan，部分2013年以前的Android设备（如搭载Mali-400 GPU的设备）不支持。面向广泛Android市场时，仍需提供ETC2作为后备格式，或使用引擎的格式Fallback机制。在Unity中可通过设置"ETC2 fallback"策略处理不支持ASTC的旧设备。

**误区三：压缩格式的选择与原始纹理位深无关**

BC6H专门处理16位浮点HDR数据（每通道16bit），若将HDR环境贴图错误地用BC7（LDR格式，8bit通道）压缩，会导致高亮区域严重过曝截断，损失超出[0,1]范围的光照信息。选择压缩格式前必须确认纹理是否为HDR内容。

---

## 知识关联

**与PBR材质基础的联系**：PBR工作流中Albedo、Normal、Roughness、Metallic等贴图的物理含义直接决定了压缩格式的选择逻辑——法线贴图的XY向量特性对应BC5的双通道设计，Roughness的灰度单调性使其可用BC4单通道压缩以节省内存，这些对应关系是PBR知识在资产管线中的直接延伸。

**与Mipmap生成的关系**：纹理压缩与Mipmap生成的顺序至关重要——应先生成完整Mipmap链（线性空间下，避免Gamma错误），再对每级Mip单独进行块压缩编码。若顺序颠倒，压缩伪影会随Mip降采样逐级放大。在引擎的资产导入管线中，压缩和Mipmap生成通常由同一构建步骤完成，但理解其内部顺序有助于排查远距离纹理出现异常条纹的问题。