---
id: "vfx-fb-vat"
concept: "VAT顶点动画"
domain: "vfx"
subdomain: "flipbook"
subdomain_name: "序列帧特效"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# VAT顶点动画

## 概述

VAT（Vertex Animation Texture，顶点动画纹理）是一种将三维网格的逐顶点位移数据预烘焙至纹理贴图中，在运行时通过顶点着色器读取纹理像素来驱动模型形变的动画技术。与骨骼动画（Skeletal Animation）不同，VAT完全绕过了CPU端的蒙皮矩阵计算，所有动画逻辑在GPU的顶点着色器阶段完成，因此极适合需要同屏渲染数百乃至数千个动画实例的场景。

VAT技术在游戏工业中获得规模化应用约在2015至2016年间。SideFX公司为Houdini软件开发的**GameDev工具包**（前身为SideFX Labs）将其标准化流程化，并发布了专用的VAT Exporter节点，使美术人员能够一键将Houdini布料、刚体破碎、流体模拟结果输出为规格化的浮点纹理。Epic Games在虚幻引擎**4.20版本**（2018年）开始内置对Houdini VAT格式的原生Material Function节点支持，进一步推广了该技术的工业化应用。Unity引擎则通过Shader Graph中的自定义顶点位移节点实现同等功能，部分工作室在URP管线下实测单帧渲染5000个VAT实例，Draw Call维持在个位数。

本技术的核心参考文献为Siggraph 2017演讲《Vertex Animation Textures: Technical Art at Weta Digital》以及SideFX官方文档《Houdini GameDev VAT 3.0 Specification》，后者详细规定了三种VAT模式的纹理打包格式与着色器解码规范。

---

## 核心原理

### 顶点位置数据的纹理编码

VAT的本质是将三维动画数据从时间域展平为二维图像空间。在**标准Houdini VAT格式**中，纹理的**U轴对应时间帧序列**，**V轴对应顶点索引**，每个像素的RGB通道分别存储该顶点在该帧的X、Y、Z位移量（Soft Body模式）或对象空间绝对位置（部分Rigid Body模式）。

由于顶点位移量可远超标准纹理的 $[0,1]$ 归一化范围（例如建筑爆破碎块可能飞出数十米），VAT必须使用**浮点纹理格式**，通常为 `RGBA16F`（半精度浮点，每通道16位）或 `RGBA32F`（单精度，精度更高但内存翻倍）。为了还原真实的世界空间位移值，导出器会将整段动画的包围盒最大值（BoundsMax）与最小值（BoundsMin）写入材质参数或纹理的Alpha通道，着色器按以下公式解码：

$$
P_{world} = P_{encoded} \times (BoundsMax - BoundsMin) + BoundsMin
$$

其中 $P_{encoded}$ 是从纹理中采样到的归一化浮点值（范围 $[0,1]$），$BoundsMax$ 和 $BoundsMin$ 是每个轴向上的真实世界空间极值。若一段破碎动画中碎片最远飞出 $12.5\,\text{m}$，则 $BoundsMax.x = 12.5$，精度损失取决于纹理位深：RGBA16F格式在此范围内的位置精度约为 $12.5 / 2^{10} \approx 0.012\,\text{m}$，对视觉特效通常可接受。

### 顶点着色器的驱动逻辑

材质的**顶点着色器**（Vertex Shader）中，模型的第二套UV通道（UV1或UV2，视引擎约定）预存储了每个顶点在VAT纹理V轴上的归一化坐标（即 $vertexIndex / totalVertexCount$）。动画播放逻辑如下：

```hlsl
// VAT顶点着色器采样伪代码（HLSL）
float totalFrames = 80.0;          // 动画总帧数（由导出器决定）
float fps = 24.0;                  // 回放帧率
float currentTime = _Time.y;      // 引擎运行时间（秒）

// 计算当前帧的U坐标（含小数部分用于插值）
float playbackPos = fmod(currentTime * fps, totalFrames) / totalFrames;
float frame0U = floor(playbackPos * totalFrames) / totalFrames;
float frame1U = frame0U + (1.0 / totalFrames);
float blend   = frac(playbackPos * totalFrames);  // 插值权重

float vertV = uv2.y;  // 顶点的V坐标（预存于第二套UV）

// 采样相邻两帧的位移（线性插值消除帧间跳变）
float3 pos0 = tex2Dlod(VATTex, float4(frame0U, vertV, 0, 0)).rgb;
float3 pos1 = tex2Dlod(VATTex, float4(frame1U, vertV, 0, 0)).rgb;
float3 posEncoded = lerp(pos0, pos1, blend);

// 解码真实位移
float3 posWorld = posEncoded * (BoundsMax - BoundsMin) + BoundsMin;
vertexPosition.xyz += posWorld;  // 叠加到顶点原始位置
```

注意着色器中必须使用 `tex2Dlod`（LOD固定为0）而非 `tex2D`，因为顶点着色器阶段不具备自动计算Mip级别的能力，强制使用LOD=0可避免采样错误帧数据。

### 三种VAT模式的结构差异

SideFX GameDev VAT Exporter 3.0定义了三种主要导出模式，模式选择错误会导致法线错误或存储空间大幅浪费：

- **Soft Body（软体模式）**：适用于顶点数量在所有帧保持固定、仅发生连续形变的网格，例如布料飘动、果冻弹性体。纹理存储逐顶点世界空间位移增量，需配套一张法线VAT（Normal VAT）保存每帧的法线方向以确保光照正确。一段1024顶点、60帧的布料动画，其位置VAT分辨率为 $1024 \times 64$（宽度取最近2的幂次）。

- **Rigid Body（刚体模式）**：适用于破碎特效，网格被预先切分为若干刚体碎块，每块内部顶点相对关系不变。每块的变换以**枢轴位置 + 四元数旋转**的形式打包，而非逐顶点存储，纹理利用率极高。200块碎片、80帧动画，仅需 $256 \times 128$（按碎块数而非顶点数索引）的纹理即可，内存占用约为Soft Body同等规模的1/5。

- **Fluid（流体模式）**：处理顶点数随时间动态变化的情况，例如粒子液体模拟。解决方案为预设最大顶点容量（如4096），当某帧实际顶点数少于最大值时，将多余顶点坐标压缩至网格原点（Vector3.zero）使其不可见。此模式纹理浪费率与顶点数波动幅度正相关，若平均利用率低于60%应考虑重新分段烘焙。

---

## 关键参数与公式

### 纹理分辨率计算

VAT纹理的宽高由顶点数与帧数共同决定，必须为2的幂次（Power of Two）以满足GPU纹理寻址要求：

$$
W = 2^{\lceil \log_2(vertexCount) \rceil}, \quad H = 2^{\lceil \log_2(frameCount) \rceil}
$$

例如，一段角色布料动画含 **1500个顶点、90帧**，则：
- $W = 2^{\lceil \log_2(1500) \rceil} = 2^{11} = 2048$
- $H = 2^{\lceil \log_2(90) \rceil} = 2^7 = 128$

纹理尺寸为 $2048 \times 128$，使用RGBA16F格式时内存占用为 $2048 \times 128 \times 8\,\text{bytes} = 2\,\text{MB}$。

### 实例化时间偏移的随机化

在GPU Instancing场景中，若所有实例共享同一时间轴，动画将完全同步，破坏自然感。常见做法是为每个实例传入一个随机时间偏移量 $\Delta t \in [0, duration]$，在着色器中将当前时间替换为 $t + \Delta t$：

$$
U_{frame} = \frac{\text{fmod}((t + \Delta t) \times fps,\ totalFrames)}{totalFrames}
$$

通过InstanceID驱动伪随机数生成器（如哈希函数 `frac(sin(instanceID * 127.1) * 43758.5)`）即可在零额外Draw Call代价下实现数百实例的相位错开效果。

---

## 实际应用

### 建筑爆破特效

一栋建筑破碎为200个刚体碎块，使用Rigid Body VAT模式在Houdini中烘焙80帧（24fps，约3.3秒）动画，导出位置VAT分辨率为 $256 \times 128$，格式为RGBA16F。在UE5的Niagara粒子系统中，以GPU Instancing方式渲染，单帧同屏50栋建筑同时爆炸（共10000个碎片实例），GPU Draw Call仅为3（位置VAT一次，法线VAT一次，深度Pass一次），在PlayStation 5平台上帧耗时约0.8ms，而同等规模的骨骼动画方案需约14ms（Siggraph 2022, Epic Games技术分享数据）。

### 移动端草地与植被摆动

在移动端（如高通骁龙888平台）渲染10000株草地，每株草含32个顶点，使用Soft Body VAT烘焙30帧风吹循环动画。纹理尺寸为 $32 \times 32$，格式为RGBA16F，内存仅8KB。每株草通过InstanceID生成 $[0, 30]$ 帧范围内的随机相位偏移，GPU侧帧耗时约0.3ms，CPU侧Draw Call为1。相比传统顶点着色器风力公式（需要sin/cos运算），VAT方案在顶点数超过16时GPU计算量更低，因为纹理采样（tex2Dlod）在现代GPU上的吞吐量高于超越函数运算。

### Houdini流体倒水特效

在饮料广告特效中，液体倒入杯子的过程使用Fluid VAT模式烘焙，最大顶点容量设为8192，实际峰值顶点数约6000（利用率73%）。导出纹理 $8192 \times 256$（RGBA16F，32MB），在Unity URP管线中以单个Mesh Renderer渲染，无需粒子系统，支持与场景光照实时交互。由于导出了法线VAT，液面在高光区域的菲涅耳反射随形变实时更新，视觉效果与离线渲染接近。

---

## 常见误区

**误区1：忽略纹理过滤模式导致动画错位**
VAT纹理必须将过滤模式设为 **Point（最近邻采样）** 而非 Bilinear，否则相邻顶点行之间的像素会被混合采样，导致顶点位移值被错误插值。帧间过渡的平滑插值应在着色器中通过 `lerp(frame0Sample, frame1Sample, blend)` 手动实现，而非依赖纹理过滤器。

**误区2：将VAT纹理压缩为DXT/BC格式**
DXT1、DXT5等块压缩格式会对浮点数据引入严重的量化误差（压缩块大小为4×4像素，块内颜色被强制量化至有限色阶），导致顶点位移出现明显的"阶梯"跳变。VAT纹理必须保持 `RGBA16F` 或 `RGBA32F` 无损格式，不可应用任何有损纹理压缩。

**误区3：在Soft Body模式下省略法线VAT**
若仅导出位置VAT而不导出对应的法线VAT，顶点法线将保持网格原始静止状态不变。当网格发生大幅形变（如布料大角度翻折）时，光照方向与实际几何体的夹角严重不符，在高光材质下表现为明显的"塑料感"错误高光。正确做法是始终成对导出Position VAT与Normal VAT，并在材质中用Normal VAT驱动法线输入。

**误区4：误用世界空间坐标而非对象空间坐标**
Houdini导出时若选择"World Space"，VAT存储的是模拟开始时刻的世界空间