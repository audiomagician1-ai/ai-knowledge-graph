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


# FSR（AMD FidelityFX Super Resolution）

## 概述

FSR（FidelityFX Super Resolution）是AMD于2021年6月推出的开源空间升采样技术，旨在以较低的渲染分辨率生成接近原生高分辨率的画面输出。与NVIDIA DLSS依赖专用张量核心不同，FSR完全基于着色器运算，因此可在AMD、NVIDIA、Intel等多种GPU上运行，甚至支持游戏机平台。

FSR 1.0采用纯空间算法，核心是一个名为EASU（Edge Adaptive Spatial Upsampling）的边缘自适应空间升采样滤波器，结合RCAS（Robust Contrast Adaptive Sharpening）锐化阶段提升细节感知。FSR 2.0于2022年发布，引入时间信息积累机制，技术路径从空间域转向时序域，画质大幅提升，正式与DLSS 2形成直接竞争关系。

FSR的重要性在于其平台无关性与开源策略：AMD将FSR以MIT许可证开放了GPU Open代码库，允许任何开发者集成和修改。这使其在独立游戏和跨平台项目中拥有比DLSS更广泛的覆盖率。

## 核心原理

### FSR 1.0：EASU空间升采样

EASU算法对每个输出像素分析周围12个输入像素，通过检测梯度方向来识别边缘走向，并根据边缘方向选取不同的插值核函数。具体而言，算法将像素邻域分解为水平、垂直和斜向三类边缘模式，再对对应方向施加拉伸的Lanczos-like重采样核，以减少锯齿感。EASU不依赖历史帧、运动向量或深度缓冲区，仅凭当前帧的颜色信息工作，这是其"纯空间"属性的根本原因。

RCAS阶段接收EASU的输出，对局部对比度区域施加自适应锐化，防止升采样引入的模糊感。RCAS的强度参数`rcasAttenuation`控制锐化量，默认值为0.25，值越小锐化越强。两个阶段合计约1毫秒的GPU开销（在RX 6800 XT，4K输出下）。

### FSR 2.0：时序积累机制

FSR 2.0引入了与DLSS 2类似的时序反馈框架，需要游戏提供运动向量（Motion Vectors）和抖动偏移（Jitter Offsets）。算法流程分四步：
1. **深度/运动向量扩张**：对深度不连续区域的运动向量进行膨胀处理，避免背景运动向量污染前景边缘。
2. **颜色重投影与锁定**：用当前帧运动向量将历史帧像素重新投影到当前视角，对静止或缓慢移动的像素建立"像素锁"（Pixel Lock），积累更多历史信息。
3. **时序合并**：通过亮度感知的混合权重将历史样本与当前样本融合，历史帧权重默认约为0.85，但对运动快速或遮挡发生的像素会动态降低。
4. **RCAS锐化**：与FSR 1.0相同的后处理锐化阶段。

### 升采样比率与质量模式

FSR定义了四档质量预设，以内部渲染分辨率与输出分辨率之比衡量：

| 模式 | 缩放比例 | 1080p内部分辨率 | 4K内部分辨率 |
|------|----------|----------------|-------------|
| Quality | 1.5× | 720p | 1440p |
| Balanced | 1.7× | 635p | 1270p |
| Performance | 2.0× | 540p | 1080p |
| Ultra Performance | 3.0× | 360p | 720p |

Ultra Performance模式为FSR 2.0新增，专为低端GPU在4K屏幕上使用设计，但此模式下时序噪声较为明显。

### FSR 3.0：帧生成扩展

FSR 3.0（2023年）在FSR 2.0基础上加入了光流加速的帧插值（Frame Interpolation）模块，通过估算相邻帧之间的像素运动场，合成一帧中间帧，将帧率理论翻倍。帧生成不依赖运动向量API（而是直接分析BackBuffer），这使得集成成本较DLSS 3更低。

## 实际应用

在《赛博朋克2077》中，FSR 2.0的Quality模式（1.5×缩放）被证明在城市街道等几何复杂场景中能有效保留霓虹灯反射细节，但在高速行驶时车窗反射容易出现时序闪烁（Ghosting）伪影。开发者通常需要对反射缓冲区单独提供反射专用运动向量以缓解此问题。

在Unity引擎集成中，FSR 2.0通过替换TAA后处理Pass实现，游戏只需暴露屏幕百分比（RenderScale）和抖动矩阵接口即可。Unity 2022.2 LTS内置了FSR 2.1支持，开发者只需三行API调用切换升采样方式。

在PlayStation 5和Xbox Series X平台上，FSR 2.0被用于原生4K输出的性能保障，如《死亡循环》使用FSR 2.0的Balanced模式，以约588p渲染并输出4K，使帧率保持在60fps以上。

## 常见误区

**误区一：FSR 1.0与FSR 2.0是同一代技术的升级版本**
两者在算法架构上几乎完全不同。FSR 1.0是无状态空间滤波器，不需要运动向量也不积累历史帧，集成极为简单但画质上限低；FSR 2.0是有状态的时序算法，需要游戏引擎提供Jitter、MotionVector和Depth三个额外缓冲区，集成复杂度与TAA相当。将两者混淆会导致错误估计集成工作量。

**误区二：FSR画质低于DLSS因为没有AI**
FSR 2.0与DLSS 2在中等质量档位（如1.5×缩放）的主观画质差距在多项第三方测试（如Digital Foundry 2022年对比测试）中仅为轻微可感知级别，并非决定性差距。FSR 2.0的主要短板是在高速运动或快速旋转镜头时的重影控制能力，而非静态细节还原。DLSS通过神经网络隐式学习了更好的遮挡处理策略，这才是两者差异的根源。

**误区三：FSR可以直接替换TAA**
FSR 2.0虽然内部包含时序抗锯齿效果，但它输出的是升采样后的高分辨率图像，而非原始分辨率的抗锯齿结果。如果游戏引擎在FSR 2.0之前仍然运行独立的TAA Pass，会造成双重时序模糊，必须在启用FSR 2.0时同时禁用引擎原有的TAA。

## 知识关联

FSR 2.0在算法设计上直接继承了TAA的时序积累框架：TAA中用于减少每帧噪声的历史帧混合（blend factor约0.1的当前帧权重）被FSR 2.0重构为升采样驱动的信息积累，历史帧权重比TAA更高（约0.85），以此重建亚像素级别的细节。理解TAA的重影抑制（History Rejection）机制——即检测当前像素是否被历史重投影像素有效覆盖——是理解FSR 2.0时序合并阶段权重调度的前提。

FSR引出了更宏观的**超分辨率技术**课题：包括基于深度学习的DLSS、XeSS，以及软件层面的游戏独立超分（如Lumen的SSGI降噪复用FSR框架）。FSR的开源策略也催生了社区实现如ReShade-FSR，将升采样能力注入不原生支持FSR的旧游戏，拓展了超分辨率在游戏历史内容上的应用边界。