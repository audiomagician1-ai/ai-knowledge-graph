---
id: "cg-smaa"
concept: "SMAA"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 40.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# SMAA（基于图案匹配的形态学抗锯齿）

## 概述

SMAA（Subpixel Morphological Antialiasing，子像素形态学抗锯齿）由 Jorge Jimenez 等人于 2012 年在 SIGGRAPH 上正式发表，是对 MLAA（形态学抗锯齿）算法的系统性改进。与 MLAA 的 CPU 实现不同，SMAA 完全运行于 GPU 着色器管线中，同时引入了"图案查找表"机制来识别边缘几何形状，最终在画质和性能之间取得了比 FXAA 更精细的平衡。

SMAA 的核心创新在于其**三阶段处理框架**：边缘检测、面积查找、混合权重计算与最终混合。这四张渲染纹理通过三个后处理 Pass 协作完成抗锯齿，而非像 FXAA 那样仅做一次模糊滤波。这种分阶段设计使 SMAA 能够精确定位锯齿的几何成因，而不仅仅是柔化高频信号。

由于 SMAA 能在不依赖多重采样硬件（MSAA）的情况下达到接近 2× MSAA 的效果，它在延迟渲染（Deferred Rendering）管线中被广泛采用——因为传统 MSAA 在延迟管线中的实现成本极高。《孤岛危机 3》《神秘海域 4》等 AAA 游戏均使用了 SMAA 或其变体。

---

## 核心原理

### 阶段一：边缘检测（Edge Detection）

SMAA 的边缘检测支持三种模式：亮度（Luma）检测、颜色（Color）检测和深度（Depth）检测。其中颜色模式对铬度边缘最敏感，而深度模式适合处理纯几何边缘。边缘判定阈值由常量 `SMAA_THRESHOLD`（默认值 0.1）控制——若相邻像素亮度差超过该阈值，则将该像素标记为边缘像素并写入一张 RG 格式的边缘纹理，R 通道存水平边缘，G 通道存垂直边缘。

### 阶段二：面积查找（Area Calculation via LUT）

这是 SMAA 区别于 FXAA 的最关键步骤。算法会沿水平或垂直方向追踪边缘线段（最长搜索距离由 `SMAA_MAX_SEARCH_STEPS` 决定，默认 16 像素），识别线段两端的"端点图案"——端点可能是平端（flat）、直角端（L形）或对角线端。每种组合对应一种几何形状，共约 **4 个端点类型 × 多种长度**，预计算结果存储在一张 **80×16 像素的面积纹理（AreaTex）** 中。查找该纹理后，算法得到该边缘对应子像素的精确混合权重。

这一步的实质是：将 1D 边缘线段的端点形状映射为对理想锯齿几何的解析估计，而非粗暴地用距离函数推算混合比例。公式上，混合权重 *w* 由面积纹理输出的二维向量 (e₁, e₂) 决定，分别代表上下（或左右）两侧颜色的混合系数。

### 阶段三：对角线边缘处理（Diagonal Detection）

SMAA 1x 版本额外引入了对角线检测模块，使用一张 **20×20 像素的对角线搜索纹理（SearchTex）** 来识别 45° 方向的锯齿。这是 FXAA 完全缺失的能力——FXAA 仅处理水平和垂直方向的混合，对角线锯齿仅被模糊而非正确重建。SMAA 的对角线模式可通过宏 `SMAA_DISABLE_DIAG_DETECTION` 关闭以节省性能。

### 阶段四：邻域混合（Neighborhood Blending）

最终 Pass 使用第二阶段输出的混合权重纹理，对当前像素及其邻域像素执行加权双线性混合。这一步与 FXAA 的最终模糊在数学上形式相似，但混合系数来自精确的几何分析而非启发式梯度，因此能保留更多高频细节（如细纹理、文字边缘）。

---

## 实际应用

**质量等级配置**：SMAA 提供四档预设——SMAA Low、SMAA Medium、SMAA High、SMAA Ultra，主要调整 `SMAA_MAX_SEARCH_STEPS`（分别为 4、8、16、32）和 `SMAA_MAX_SEARCH_STEPS_DIAG`（分别为 0、0、8、16）。Ultra 模式在 GTX 680 上耗时约 **0.9ms**，而 High 模式约 **0.5ms**（1080p 分辨率），可根据平台预算灵活选择。

**与 TAA 结合使用**：现代引擎常将 SMAA T2× 模式与时间性抗锯齿结合。SMAA T2× 通过交替投影两个亚像素抖动帧，利用时间积累将质量提升至接近 4× MSAA。虚幻引擎4 中的 `SMAA 1TX` 模式即是该策略的简化版实现。

**延迟渲染管线集成**：SMAA 以后处理 Pass 形式运行，仅需要颜色缓冲（以及可选的深度/法线缓冲用于边缘检测），因此无需修改 G-buffer 写入阶段，可直接插入 Tone Mapping 之前的后处理链。

---

## 常见误区

**误区一：SMAA 就是"更好的 FXAA"**  
两者的算法本质不同。FXAA 依赖亮度梯度估算混合方向，始终会软化图像；SMAA 通过图案匹配重建几何形状，对非边缘区域的纹理像素完全不修改。因此 SMAA High 的锐度通常明显优于 FXAA，但计算量约为 FXAA 的 2～3 倍。

**误区二：面积纹理可以在运行时动态生成**  
AreaTex 和 SearchTex 均是**预计算的静态纹理资产**，在编译时烘焙完成。试图在 Shader 内用数学公式实时复现这两张纹理的结果会导致精度误差和性能下降，官方实现明确要求将这两张纹理以 DDS/PNG 形式打包进资源库。

**误区三：SMAA 能完全替代 MSAA**  
SMAA 本质是后处理算法，处理的是最终光栅化图像，对**子像素级别的着色走样**（例如高光镜面反射的闪烁）没有改善作用，而硬件 MSAA 可以在着色阶段进行超采样以解决此类问题。在高频镜面反射场景中，单纯使用 SMAA 仍会出现明显的时间性闪烁。

---

## 知识关联

**与 FXAA 的继承关系**：学习 SMAA 需要先理解 FXAA 的边缘方向检测和单 Pass 后处理框架，因为 SMAA 的第一阶段（边缘检测）逻辑与 FXAA 高度相似，均使用亮度差阈值判断。但 SMAA 用面积查找替换了 FXAA 的启发式梯度混合，这是两者最本质的分叉点。

**向上延伸**：掌握 SMAA 后，可进一步研究 SMAA T2×（时间性 SMAA）和 TAA（时间抗锯齿）。SMAA T2× 在 SMAA 的空间混合基础上引入了帧间重投影（Reprojection），需要理解运动向量缓冲（Motion Vector Buffer）的生成与使用，这是现代引擎抗锯齿方案的主流方向，也是 DLSS/FSR 等超分辨率技术的前置概念基础。
