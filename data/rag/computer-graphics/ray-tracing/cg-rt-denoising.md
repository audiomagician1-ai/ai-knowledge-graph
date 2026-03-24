---
id: "cg-rt-denoising"
concept: "光追降噪"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 3
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 光追降噪

## 概述

光线追踪渲染在物理上正确，但代价极高——实时场景中每像素仅能发射1~4条路径，导致画面充满高频随机噪点（方差极大）。光追降噪（Ray Tracing Denoising）正是针对这一稀疏采样问题设计的后处理管线，其核心目标是：在保留几何细节与光照锐利度的前提下，从极低采样率的噪声图像中重建出收敛质量的最终画面。

该领域的奠基性突破出现在2017年，NVIDIA研究院发表的 **SVGF**（Spatiotemporal Variance-Guided Filtering）论文将实时光追降噪推向工业可用阶段，首次将时域复用与逐像素方差估计结合，使单帧1spp（samples per pixel）的路径追踪画面达到视觉可接受水平。此后AMD、NVIDIA分别推出 NRD（NVIDIA Real-time Denoiser）等SDK级方案，AI降噪路线（DLSS Ray Reconstruction、OptiX AI Denoiser）也于2019—2023年间逐步成熟。

光追降噪之所以不同于传统图像模糊或超分辨率，在于它必须同时处理**时域不稳定性（鬼影/滞留）**与**空间高方差**两类矛盾，且需在渲染管线中融合G-Buffer法线、深度、运动向量等辅助数据，而不是对普通RGB图像做盲处理。

---

## 核心原理

### 1. 时域积累（Temporal Accumulation）

SVGF的第一阶段利用相机运动向量和物体运动向量，将当前帧像素重投影（reproject）到前一帧坐标，提取历史颜色并做指数移动平均（EMA）：

$$\bar{C}_t = \alpha \cdot C_t + (1-\alpha) \cdot \bar{C}_{t-1}$$

其中 $\alpha$ 通常取 **0.1～0.2**（对应历史帧混合比例80%～90%）。当重投影失败（遮挡、disocclusion、反射区域）时，算法通过深度差值 $|z_t - z_{t-1}| / z_t$ 及法线差值 $\cos\theta < 0.906$（约25°阈值）检测到不连续性，将 $\alpha$ 强制提升至1.0以拒绝历史样本，防止鬼影。

### 2. 方差估计与引导滤波（Variance-Guided Spatial Filter）

SVGF在时域积累后计算每像素的**局部时域方差**：统计前7帧的辉度样本，得到 $\sigma^2$，再以此作为空间 à-trous 小波滤波器的权重调制量。à-trous滤波器采用**5级迭代**，卷积核步长指数倍增（1, 2, 4, 8, 16像素），实际有效感受野达33×33像素，但每级仅用5×5稀疏核，复杂度控制在 O(N) 级别。

权重函数综合三个分量：

$$w = w_{\text{lum}} \cdot w_{\text{normal}} \cdot w_{\text{depth}}$$

辉度权重 $w_{\text{lum}} = \exp\left(-\frac{|l_p - l_q|}{\sigma_l \sqrt{\sigma^2} + \varepsilon}\right)$，其中 $\sigma_l=4.0$ 为超参，$\varepsilon=10^{-6}$ 防止除零。方差越大，辉度权重越宽松，允许更大范围的空间模糊；方差收敛时，权重趋于锐利，保留高频细节。

### 3. NRD 的信号分离策略

NRD（NVIDIA Real-time Denoiser，2020年随RTX SDK发布）相比SVGF引入了**Specular/Diffuse信号分离降噪**：漫反射与镜面反射各走独立降噪通道，分别以不同的时域混合权重和空间核处理，最后在合成阶段重组。对于镜面反射，NRD使用**HitT（命中距离）**重投影而非像素空间运动向量，能正确追踪反射物体运动。NRD的REBLUR模式针对球谐函数辐照度和高光波瓣进行自适应模糊半径（与粗糙度挂钩：粗糙度=1.0时核半径约32像素，粗糙度=0.1时约4像素）。

### 4. AI降噪（基于卷积神经网络）

OptiX AI Denoiser（2019）和DLSS Ray Reconstruction（DLSS 3.5，2023）采用离线训练的U-Net结构，输入除噪声颜色外还包含法线、反照率、运动向量等辅助通道（G-Buffer）。DLSS Ray Reconstruction专门针对反射、阴影、全局光照的1spp噪声进行联合重建，其时域稳定性依赖DLSS框架内部的帧级特征对齐，而非SVGF式的显式像素重投影，能更好地处理光泽反射（Glossy reflection）中的时域闪烁。

---

## 实际应用

**游戏实时渲染**：《控制》（Control, 2019）是首批使用NRD前身算法的商业游戏，在RTX 2080 Ti上以1080p60fps渲染1spp路径追踪阴影和反射，降噪时间预算约0.8ms。现代游戏引擎（Unreal Engine 5的Lumen）内置了自研的时空滤波器，同样基于方差引导思想，针对Screen Space Radiance Cache做专项降噪。

**离线渲染加速**：Arnold、RenderMan等离线渲染器集成基于CNN的降噪器（如Altus Denoiser），允许将渲染至收敛所需的2048spp压缩至32spp，降噪后SSIM值可达0.97以上，节省90%以上的云渲染费用。

**医疗/工业可视化**：OptiX AI Denoiser被集成进NVIDIA Omniverse，用于实时光追CT/MRI体渲染的降噪，要求保留微小解剖结构（高频边缘），因此在法线权重上比游戏场景更保守（法线阈值缩小到10°以内）。

---

## 常见误区

**误区1：降噪等于高斯模糊**  
初学者常误认为降噪只是对噪声图做一次模糊处理。实际上，SVGF的à-trous权重由逐像素方差动态调制，高方差区域（如直接光照边缘）会触发更大核，而低方差区域（收敛的漫反射面）核宽接近0，完全不模糊。纯高斯模糊会同等地抹去锐利的阴影边界，而SVGF在具有相同法线和深度的连续平面上几乎不产生模糊。

**误区2：时域积累历史比例越高越好**  
将 $\alpha$ 调低至0.05（即保留95%历史）确实能减少噪点，但在镜头快速摇移或快速运动物体旁边，重投影误差会导致历史样本错位，产生明显的色彩滞留（Ghost artifact）。SVGF用帧计数器 $s$ 动态将 $\alpha$ 下限限制为 $\max(0.1, 1/(s+1))$，新出现像素（$s=0$）时强制 $\alpha=1.0$，避免无效历史污染。

**误区3：AI降噪比SVGF在所有场景下更优**  
AI降噪对训练数据分布外的场景（如极端高动态范围的爆炸粒子光源、非真实感风格化渲染）可能产生幻觉伪影（hallucination），错误填充细节。SVGF作为无参数学习的物理滤波器，行为更可预测。在需要严格正确性的工业渲染中，方差引导滤波仍是首选；AI降噪在视觉质量容忍度较高的游戏场景中优势明显。

---

## 知识关联

理解光追降噪需要以**路径追踪**为前提：路径追踪产生的无偏蒙特卡洛估计决定了噪声的统计特性——蒙特卡洛方差与 $1/N$ 成正比，这正是为何1spp的方差是4spp的四倍，也决定了降噪器的设计目标是方差压缩而非均值校正。G-Buffer中的法线、深度、运动向量是SVGF权重函数的直接输入，不理解光栅化G-Buffer结构就无法理解为何降噪器需要辅助通道。

在技术演进方向上，光追降噪与**实时全局光照**（如Lumen、ReSTIR）深度耦合——ReSTIR GI等算法通过时空样本复用在降噪前就提升有效采样率，使降噪器输入的方差从1spp等效提升至数十spp，二者协同才能实现高质量实时光追画面。
