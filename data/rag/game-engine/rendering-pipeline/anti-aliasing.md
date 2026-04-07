---
id: "anti-aliasing"
concept: "抗锯齿技术"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 2
is_milestone: false
tags: ["质量"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---




# 抗锯齿技术

## 概述

抗锯齿（Anti-Aliasing）技术是消除三维图形渲染中"锯齿"（Aliasing）伪影的方法集合。锯齿产生的根本原因源自奈奎斯特采样定理（Nyquist Sampling Theorem）：当屏幕像素格栅的采样频率低于图形边缘的信号频率时，高频细节无法被准确重建，几何边缘呈现出阶梯状断裂，在斜线（尤其是接近30°或45°的边缘）和曲线轮廓处最为明显。

抗锯齿技术的演进跨越四十余年。超采样抗锯齿（SSAA）随1980年代光栅化渲染普及，原理直接但性能代价极高。2000年代，MSAA随GPU硬件覆盖测试单元（Coverage Test Unit）的普及进入主流。2009年，NVIDIA工程师Timothy Lottes发布FXAA，将全屏后处理抗锯齿开销压缩至0.5ms以内。2018年起，基于时间累积的TAA成为Unreal Engine与Unity等主流引擎的默认选项。同年NVIDIA发布DLSS 1.0，引入深度学习超采样；AMD则于2021年发布开源方案FSR 1.0，基于Lanczos空间上采样。这一演进轨迹从"多采样几何边缘"到"时间域积分"再到"神经网络图像重建"，彻底改变了渲染分辨率与输出分辨率之间的固定关系。

参考资料：Tomas Akenine-Möller等著《Real-Time Rendering, 4th Edition》(CRC Press, 2018) 第5章对各类采样与重建策略有系统性论述。

---

## 核心原理

### MSAA：多重采样抗锯齿

MSAA（Multisample Anti-Aliasing）在每个像素内设置多个子采样点（Sub-sample），但只为每个像素执行**一次**片元着色器（Fragment Shader）调用。以4×MSAA为例，每个像素含4个子采样点，GPU的覆盖测试单元判断三角形覆盖了哪些采样点，覆盖率（Coverage）决定最终混合权重，着色计算本身仅发生一次。相比于4×SSAA需要4次完整着色调用，MSAA的着色开销接近原生分辨率渲染，但显存带宽需求在4×MSAA时约增加70%（需要存储4份深度与模板缓冲）。

MSAA与延迟渲染（Deferred Rendering）存在根本性不兼容：延迟渲染将法线、反射率等信息写入G-Buffer，若要在G-Buffer阶段支持MSAA，每个子采样点需独立存储一份G-Buffer数据，使显存占用与采样倍率成正比翻倍。这也是为何Unreal Engine 4/5默认禁用MSAA而改用TAA。MSAA对粒子、透明物体（Alpha-Blend模式）、屏幕空间反射等后处理特效完全无效，因为这些效果绕过了几何覆盖测试阶段。

### FXAA：快速近似抗锯齿

FXAA由NVIDIA的Timothy Lottes于2009年设计（发表于NVIDIA白皮书 *FXAA 3.11 White Paper*），以屏幕空间后处理（Screen-Space Post-Process）方式运行，输入为渲染完成后的LDR颜色缓冲（通常是RGB888或R11G11B10格式），不依赖深度缓冲或额外G-Buffer。其算法核心步骤如下：

1. **亮度检测**：将颜色缓冲转换为感知亮度 $L = 0.299R + 0.587G + 0.114B$，计算当前像素与上下左右四邻像素的亮度差 $\Delta L$。
2. **边缘方向判断**：比较水平与垂直方向的亮度梯度，确定边缘走向（水平或垂直）。
3. **端点搜索**：沿边缘方向向两端步进（最多搜索约32像素），寻找亮度反转点，确定边缘在屏幕上的跨度。
4. **亚像素混合**：依据当前像素在边缘长度上的相对位置，对当前像素与相邻像素的颜色进行插值混合。

FXAA的全屏开销在GTX 1080上约为0.3ms（1080p），与渲染管线几乎零耦合。代价是：FXAA无法区分几何边缘与纹理内部的高频细节，对UI文字、细格线纹理等会产生不必要的模糊；同时对着色器内部产生的高频变化（如镜面高光闪烁）完全无能为力。

### TAA：时间性抗锯齿

TAA（Temporal Anti-Aliasing）通过对连续帧的抖动采样结果进行时间域积分来实现超采样效果。每帧渲染时，投影矩阵（Projection Matrix）被施加一个亚像素偏移（Jitter），偏移序列通常采用低差异序列中的**Halton(2,3)序列**，使得多帧的采样点在一个像素内均匀分布。帧混合采用指数移动平均（Exponential Moving Average，EMA）：

$$C_{\text{out}} = \alpha \cdot C_{\text{current}} + (1 - \alpha) \cdot C_{\text{history\_reprojected}}$$

其中 $\alpha$ 通常取 $0.1$（即当前帧权重10%，历史帧权重90%），等效于对约10帧内的采样结果做加权平均，显著压制了时间域内的采样噪声。

历史帧的重投影（Reprojection）通过运动向量（Motion Vector）实现：对于静态物体，依据当前帧与上一帧的摄像机变换矩阵推导像素位移；对于动态物体，渲染阶段需将蒙皮动画的速度信息写入单独的运动向量缓冲（Motion Vector Buffer）。当重投影坐标超出屏幕边界或历史像素被遮挡（Disocclusion）时，TAA需要放弃历史数据（将 $\alpha$ 强制设为1.0），此处理若不当会在快速移动边缘产生明显的"鬼影"（Ghosting）。

TAA的另一核心步骤是**历史颜色裁剪（History Clipping/Clamping）**：将历史颜色值限制在当前像素周围 $3 \times 3$ 邻域的颜色包围盒（Color AABB）内，以减少运动导致的残影，但过于激进的裁剪会重新引入闪烁噪声。

### DLSS 与 FSR：超分辨率重建

DLSS（Deep Learning Super Sampling）由NVIDIA于2018年随RTX 2080系列显卡推出，利用Tensor Core加速的卷积神经网络（CNN）将低分辨率渲染帧上采样至目标分辨率。DLSS 2.0（2020年）引入通用神经网络，输入包括当前低分辨率帧、运动向量和深度缓冲，输出高分辨率重建帧。DLSS 3.0（2022年）进一步加入帧生成（Frame Generation），在两帧之间插入AI合成帧，使帧率几乎翻倍。常见质量档位如下：

| 档位 | 渲染分辨率（输出1080p） | 性能提升（相对原生） |
|------|------------------------|----------------------|
| 质量（Quality） | 720p（1.5× 上采样）    | ~1.5×               |
| 平衡（Balanced）| 640p（约1.7×）          | ~1.7×               |
| 性能（Performance）| 540p（2×）           | ~2.0×               |
| 超性能（Ultra Performance）| 360p（3×）   | ~3.0×               |

FSR（FidelityFX Super Resolution）由AMD于2021年6月发布，FSR 1.0基于空间算法（Lanczos衍生核 EASU + 锐化阶段 RCAS），不依赖运动向量，与GPU型号无关；FSR 2.0（2022年）引入时间反馈，算法逻辑接近DLSS 2.x，质量接近但不依赖专用AI硬件，开源代码托管于GPUOpen平台。

---

## 关键公式与算法

TAA的亚像素抖动采用Halton序列生成。Halton序列基于素数基底的反射小数（Van der Corput序列）：

$$h(i, b) = \sum_{k=0}^{\infty} d_k(i) \cdot b^{-(k+1)}$$

其中 $d_k(i)$ 是 $i$ 在 $b$ 进制下第 $k$ 位的数字。TAA常用 $b=2$（X轴）和 $b=3$（Y轴）的组合，生成8或16个均匀分布于 $[0,1)^2$ 的亚像素偏移点。

以下是Unity HDRP中TAA抖动偏移的核心代码逻辑（简化版）：

```csharp
// 生成第 frameIndex 帧的Halton(2,3)亚像素抖动偏移
float HaltonSequence(int index, int baseValue)
{
    float result = 0f;
    float fraction = 1f / baseValue;
    while (index > 0)
    {
        result += (index % baseValue) * fraction;
        index /= baseValue;
        fraction /= baseValue;
    }
    return result;
}

Vector2 GetJitter(int frameIndex, int sampleCount = 8)
{
    int i = (frameIndex % sampleCount) + 1;
    // 偏移至 [-0.5, 0.5] 范围，以像素为单位
    float jitterX = HaltonSequence(i, 2) - 0.5f;
    float jitterY = HaltonSequence(i, 3) - 0.5f;
    return new Vector2(jitterX / screenWidth, jitterY / screenHeight);
}
```

投影矩阵的 $P_{02}$ 和 $P_{12}$ 分量加上上述偏移后，光栅化阶段每帧的采样点便在亚像素范围内系统性移位，8帧后覆盖一个像素内均匀分布的8个位置，等效于8×SSAA的采样密度——但只需要1倍的渲染开销（代价是引入跨帧的运动依赖）。

---

## 实际应用

**延迟渲染管线中的选择**：Unreal Engine 5默认启用TAA（或其升级版TAAU），在 `r.TemporalAA.Upsampling=1` 时同时执行时间超采样；Epic在内部项目中对静止画面质量要求极高时使用 `r.TemporalAASamples=8` 将TAA累积帧数扩展到8帧。对于移动端（如Mali G78 GPU），受限于带宽，MSAA 4× 仍是前向渲染（Forward Rendering）管线的首选，因为移动GPU的tile-based架构可在片上缓存内完成MSAA解析（Resolve），实际带宽增量接近0。

**案例：《赛博朋克2077》的TAA鬼影问题**：CD Projekt RED在2020年发布时，游戏中的霓虹灯牌、雨滴粒子等高亮动态元素因运动向量精度不足，导致TAA历史帧颜色裁剪失效，产生明显的发光拖影（Bloom Ghosting）。后续补丁通过收紧 AABB 裁剪包围盒边距、强制对高亮像素降低历史帧权重（$\alpha$ 从0.1提升至0.3）修复了该问题。

**DLSS vs FSR 的工程决策**：若目标平台为PC且玩家普遍使用RTX 20系列以上GPU（Steam 2023年硬件调查显示RTX系列占PC游戏玩家约35%），优先集成DLSS 2/3可提供最优画质。若需要覆盖AMD及Intel Arc GPU用户，FSR 2.x或XeSS（Intel，2022年）是兼容性更广的选项，两者均可通过同一套运动向量接口接入。

---

## 常见误区

**误区1：TAA 等同于模糊**。TAA在静止画面或慢速运动场景中，历史帧累积等效于多帧超采样，实际细节密度高于原生分辨率渲染。画面"模糊感"通常来自以下原因：（a）历史颜色裁剪过于激进导致有效累积帧数降低；（b）抖动偏移未配合重建滤波（通常是 Mitchell-Netravali 滤波器）正确补偿，导致频率响应在 Nyquist 频率附近出现衰减。正确配置的TAA应搭配锐化（Sharpening Pass，如RCAS）使