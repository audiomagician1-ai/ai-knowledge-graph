---
id: "cg-fsr"
concept: "FSR"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# FSR（AMD FidelityFX Super Resolution）

## 概述

FSR（FidelityFX Super Resolution）是AMD于2021年6月22日正式发布的开源升采样技术框架，最初版本（FSR 1.0）采用纯空间算法，2022年5月12日发布的FSR 2.0转向时序积累路径，2023年9月发布的FSR 3.0进一步引入帧生成（Frame Generation）模块，将有效帧率提升最高2倍。与NVIDIA DLSS依赖Tensor Core深度学习推理不同，FSR全系列均基于通用计算着色器（Compute Shader）实现，无需专用硬件单元，因此可在AMD Radeon、NVIDIA GeForce、Intel Arc乃至PlayStation 5、Xbox Series X等游戏机GPU上运行。

AMD以MIT许可证将FSR源代码托管于GPUOpen平台（gpuopen.com），开发者可自由修改和集成。截至2024年初，已有超过300款游戏支持FSR技术（AMD官方数据），远超DLSS约150款的覆盖范围，这一差距主要源于FSR的硬件无关性与开放授权策略。

---

## 核心原理

### FSR 1.0：EASU空间升采样滤波器

FSR 1.0的核心是**EASU**（Edge Adaptive Spatial Upsampling）算法。对于每个输出像素，EASU在输入图像上采样一个4×4邻域（共16个纹素），通过计算各方向的亮度梯度（Luma Gradient）识别局部边缘走向——水平、垂直或45°/135°斜向。识别边缘方向后，算法沿垂直于边缘的方向使用拉伸的**Lanczos-2近似核**进行插值，沿平行于边缘的方向则收窄采样范围以保留边缘锐度。

这一设计避免了各向同性插值（如双线性或双三次）在斜向边缘处产生的阶梯感。EASU完全不依赖历史帧、运动向量或深度缓冲区，输入仅为当前帧颜色纹理，这使其集成成本极低——开发者只需在原有后处理链末尾插入两个全屏Pass即可。

**RCAS**（Robust Contrast Adaptive Sharpening）是EASU之后的锐化阶段。它计算每个像素与其4邻域的对比度，对低对比度区域施加更强锐化，对已有高频细节的区域自动抑制锐化量，防止振铃（Ringing）和过曝。RCAS的关键控制参数`rcasAttenuation`取值范围为[0.0, 2.0]，默认0.25；值越大，锐化量越小。两个Pass合计在RX 6800 XT输出4K分辨率下的GPU耗时约为**0.7～1.2毫秒**，比原生4K渲染节省约60%的像素着色带宽。

### FSR 2.0：时序积累与像素锁机制

FSR 2.0的设计目标是在无机器学习推理的前提下复现DLSS 2的时序超分辨率效果。游戏引擎须提供三项额外输入：**运动向量缓冲区**（Motion Vector Buffer，R16G16格式，以像素为单位）、**深度缓冲区**（Depth Buffer）以及每帧的**Halton抖动偏移量**（Jitter Offset），后者用于亚像素级多帧采样覆盖。

算法内部分四个计算阶段（以下以Vulkan/DX12 Compute Shader Pass为单位）：

1. **深度/运动向量扩张（Depth & Motion Dilation）**：在深度不连续边界（前景物体轮廓处）将前景像素的运动向量向外膨胀2个像素，防止背景的错误运动向量渗入前景边缘重投影，这是FSR 2.0相较DLSS早期版本"鬼影"问题更少的关键所在。

2. **历史帧重投影与锁定（Reprojection & Pixel Lock）**：用运动向量将上一帧积累结果映射到当前帧坐标系，对连续3帧以上未发生遮挡或快速运动的像素建立"像素锁"（Pixel Lock）状态。处于锁定状态的像素接受更高权重的历史帧混合（历史权重约0.85～0.92），从而积累更多亚像素信息，实现超分辨率细节重建。

3. **时序合并（Temporal Accumulation）**：对运动区域和遮挡区域动态降低历史帧权重（最低约0.1），并通过**亮度反走样曝光归一化**（Luminance Exposure Normalization）消除高动态范围场景下历史帧与当前帧的亮度不匹配问题。合并后的颜色数据以YCoCg色彩空间存储，以减少色彩通道间的相关性误差。

4. **RCAS锐化**：与FSR 1.0相同的后处理锐化阶段，参数可由开发者独立调节。

FSR 2.0在RX 6700 XT输出1440p（Quality模式，内部960p）下的完整Pass耗时约为**2.0～2.8毫秒**，与TAA的典型耗时（1.5～2.0毫秒）相近，但输出分辨率更高、时序稳定性更好。

### FSR 3.0：帧生成模块（Frame Generation）

FSR 3.0新增的**帧生成**功能通过光流估计（Optical Flow Estimation）在相邻两帧之间插值生成一个完整的中间帧，有效帧率提升幅度在GPU受限场景下可达1.5×～2.0×。其光流场以8×8像素块为单位计算，精度低于专用神经网络方案（如DLSS 3的Optical Flow Accelerator），但完全依赖Compute Shader实现，无需额外硬件支持。帧生成模块与FSR 2.x超分模块独立，可单独启用。

---

## 关键参数与质量模式

FSR定义了四档标准质量预设，以**内部渲染分辨率与目标输出分辨率之比**（Scale Factor）衡量：

| 模式 | 缩放比例 | 1080p内部分辨率 | 1440p内部分辨率 | 4K内部分辨率 |
|------|----------|----------------|----------------|-------------|
| Quality | 1.5× | 720p (1280×720) | 960p (2560×960) | 1440p |
| Balanced | 1.7× | 约635p | 约847p | 约1270p |
| Performance | 2.0× | 540p (960×540) | 720p | 1080p |
| Ultra Performance | 3.0× | 360p (640×360) | 480p | 720p |

Ultra Performance模式的3.0×线性缩放意味着每个输出像素对应输入图像中仅约0.11个像素面积（$1/3^2 \approx 0.111$），信息损失极大，画质通常仅作为帧率紧张时的应急选项。

RCAS锐化强度的数学形式可表示为：

$$
\text{output} = \text{input} + \alpha \cdot \left( \text{input} - \frac{1}{4}\sum_{i \in \{N,S,E,W\}} \text{neighbor}_i \right)
$$

其中 $\alpha$ 由`rcasAttenuation`参数控制，$\alpha = 2^{-\text{rcasAttenuation}}$。默认`rcasAttenuation = 0.25`时，$\alpha \approx 0.841$，对局部对比度差值施加约84%强度的锐化补偿。

---

## 集成示例（以FSR 2.0 DX12 API为例）

```cpp
// 初始化FSR 2.0上下文
FfxFsr2ContextDescription contextDesc = {};
contextDesc.flags = FFX_FSR2_ENABLE_HIGH_DYNAMIC_RANGE
                  | FFX_FSR2_ENABLE_DEPTH_INVERTED;
contextDesc.maxRenderSize  = { renderWidth, renderHeight };   // 内部分辨率
contextDesc.displaySize    = { displayWidth, displayHeight }; // 输出分辨率
contextDesc.device         = ffxGetDeviceDX12(d3d12Device);
ffxFsr2ContextCreate(&fsr2Context, &contextDesc);

// 每帧调度升采样
FfxFsr2DispatchDescription dispatchDesc = {};
dispatchDesc.commandList        = ffxGetCommandListDX12(cmdList);
dispatchDesc.color              = ffxGetResourceDX12(colorBuffer);
dispatchDesc.depth              = ffxGetResourceDX12(depthBuffer);
dispatchDesc.motionVectors      = ffxGetResourceDX12(motionVectorBuffer);
dispatchDesc.output             = ffxGetResourceDX12(upscaledBuffer);
dispatchDesc.jitterOffset       = { jitterX, jitterY };  // Halton序列偏移
dispatchDesc.renderSize         = { renderWidth, renderHeight };
dispatchDesc.cameraNear         = 0.1f;
dispatchDesc.cameraFar          = 10000.0f;
dispatchDesc.cameraFovAngleVertical = fovY;
dispatchDesc.frameTimeDelta     = deltaTimeMs;  // 毫秒
dispatchDesc.reset              = cameraJumped; // 场景切换时重置历史帧
ffxFsr2ContextDispatch(&fsr2Context, &dispatchDesc);
```

Halton序列生成Jitter偏移是确保多帧亚像素覆盖均匀分布的关键，FSR 2.0内部默认使用**基数为(2,3)的Halton序列**，序列长度为8（即每8帧循环一次抖动模式）。

---

## 实际应用与性能数据

以《赛博朋克2077》为基准测试场景（GPU：RX 6800 XT，驱动22.11.2）：

- **原生4K**（无任何升采样）：平均49 FPS
- **FSR 1.0 Quality（1440p→4K）**：平均71 FPS，帧率提升约45%，画质评分（Digital Foundry主观评测）约为原生4K的87%
- **FSR 2.0 Quality（1440p→4K）**：平均68 FPS，帧率提升约39%，画质评分约为原生4K的93%，运动稳定性显著优于FSR 1.0
- **FSR 2.0 Performance（1080p→4K）**：平均91 FPS，帧率提升约86%，画质评分约为原生4K的85%

FSR 1.0与FSR 2.0在**静止画面**下画质差距较小，主要差异体现在快速运动物体的边缘稳定性和细发丝、草地等高频细节的时序一致性上。FSR 2.0在持续运动的场景中表现出与DLSS 2.4相近的时序稳定性（参考数字铸造 Digital Foundry 2022年5月的对比测评）。

---

## 常见误区

**误区一：FSR 1.0等同于简单的双三次插值（Bicubic）**
EASU与双三次插值的根本区别在于其边缘方向感知能力。双三次插值使用固定的各向同性核函数，对所有方向等权处理，导致斜向边缘出现阶梯感；EASU通过梯度分析动态旋转插值核，使核函数长轴与边缘方向平行，锯齿感明显减少。直接对比测试中，EASU在45°斜线的SSIM指标上比双三次插值高约0.03～0.06（视场景内容而异）。

**误区二：FSR 2.0不需要运动向量**
FSR 1.0确实无需运动向量，但FSR 2.0强依赖精确的亚像素级运动向量。若游戏引擎提供的运动向量精度不足（如仅输出整数像素精度）或缺少透明物体/粒子的运动向量，FSR 2.0会在这些区域产生明显的时序拖影（Temporal Ghosting）。

**误区三：FSR在所有GPU上性能提升幅度相同**
FSR的性能增益主要来自减少像素着色器调用次数（即降低内部渲染分辨率），因此在**像素着色瓶颈**（Pixel Shader Bound）的场景下收益最大；若游戏瓶颈在CPU或顶点着色阶段，FSR几乎无法提升帧率。

---

## 与TAA及其他升采样技术的关联

FSR 2.0的设计理念直接继承自**TAA（Temporal Anti-Aliasing）**的时序积累框架（详见TAA章节），但在三个方面做了关键扩展：①引入亚像素Jitter以覆盖1倍以上的输出分辨率信息，实现"超分"而非单纯"抗锯齿"；②使用深度扩张替代TAA中的简单运动向量采样，降低边缘鬼影；③以亮度感知混合权重替换TAA的固定α混合，提高高对比度区域的时序稳定