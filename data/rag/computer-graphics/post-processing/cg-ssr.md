# 屏幕空间反射

## 概述

屏幕空间反射（Screen-Space Reflection，SSR）是一种利用已渲染帧的深度缓冲（Depth Buffer）和颜色缓冲（Color Buffer）来计算反射效果的实时图形后处理技术。与传统的平面反射（Planar Reflection）或立方体贴图反射（Cubemap Reflection）不同，SSR 能够反映出场景中动态物体、角色和粒子效果，因为其采样来源是当前帧实际渲染的像素内容，而非预烘焙的静态数据。这使得 SSR 在延迟渲染管线（Deferred Rendering Pipeline）中成为金属、湿润石材、水面等高光材质不可或缺的视觉补全手段。

SSR 最早在 2011 年由 Morgan McGuire 和 Michael Mara 在其论文 *Efficient GPU Screen-Space Ray Tracing* 中系统化地提出（后于 2014 年正式发表于 *Journal of Computer Graphics Techniques*，JCGT Vol.3, No.4），随后在 Ubisoft、Epic Games 等公司的商业引擎中得到广泛应用。虚幻引擎 4 在 2014 年将 SSR 作为标准后处理选项正式引入，推动了该技术在次世代游戏开发中的普及。Unity HDRP 则于 2018 年随 Unity 2018.1 版本正式提供生产级 SSR 支持，进一步扩大了该技术的工程受众。

SSR 之所以在工程实践中受到重视，在于它以极低的额外渲染 Pass 代价补全了延迟渲染管线中金属和高光材质的视觉完整性。地板反射、水面倒影、湿润石材等效果均依赖 SSR 才能在不使用光线追踪硬件的条件下实现可信的实时结果。在 GTX 1080 级别硬件上，SSR 的典型帧时预算约为 **1.5～2.5ms**（1080p 半分辨率渲染），相比之下实时光追反射通常消耗 **8～15ms**，性价比差距显著。

> **思考问题：** 为什么 SSR 只能在延迟渲染或带有 Pre-Pass 的正向渲染管线中使用，而无法直接应用于纯正向渲染？这一约束对引擎架构设计有何影响？

---

## 核心原理

### 屏幕空间光线步进（Ray Marching in Screen Space）

SSR 的基础算法是从着色点沿反射向量在屏幕空间内逐步推进。反射向量的计算公式为：

$$\mathbf{R} = \mathbf{V} - 2(\mathbf{V} \cdot \mathbf{N})\mathbf{N}$$

其中 $\mathbf{V}$ 为从着色点指向摄像机的单位视线方向向量，$\mathbf{N}$ 为着色点处的世界空间单位法线向量，$\mathbf{R}$ 为反射光线方向向量。等价地，在 HLSL/GLSL 中可直接写作 `R = reflect(-V, N)`。注意此处 $\mathbf{V}$、$\mathbf{N}$、$\mathbf{R}$ 均须为归一化向量，否则反射方向计算出现偏差，产生视觉拉伸伪影（Stretching Artifact）。

将反射光线从观察空间（View Space）变换到裁剪空间（Clip Space）后，沿像素坐标方向迭代步进，每步采样当前深度缓冲值与步进点深度进行比较。若步进点深度大于缓冲深度（即射线穿入几何体），则认为在该处发生相交（Intersection），并读取对应颜色缓冲作为反射颜色。射线与场景的相交判断本质上是对 NDC 空间中深度不等式 $z_{\text{ray}} \geq z_{\text{buffer}}$ 的逐步检验，其中 $z_{\text{ray}}$ 为当前步进点经投影变换后的深度，$z_{\text{buffer}}$ 为深度缓冲在对应像素处存储的值。

线性步进的致命缺陷是步长均匀，每帧需要 **32～64 次**纹理采样才能保证精度，在 1080p 全分辨率下 GPU 带宽压力极大，通常须降至半分辨率（960×540）执行以维持性能。此外，线性步进在掠射角（Grazing Angle，即反射向量与屏幕平面夹角小于 15°）时最易产生"分层"（Banding）伪影，因为相邻步进点之间深度变化极小，难以精确定位交叉位置。由于深度缓冲存储的是不连续的离散采样，步长选择不当时还会出现"过步"（Overshoot）问题，导致反射图像出现空洞（Missing Region）。

### Hi-Z 加速光线步进（Hierarchical-Z Ray March）

Hi-Z Ray March 是 SSR 的核心优化手段，由 Yasin Uludag 在 *GPU Pro 5*（Uludag, 2014，CRC Press，Chapter 1）中详细描述。其核心思路是为深度缓冲构建一个多层级的深度最大值金字塔（Hierarchical Depth Buffer，Hi-Z），结构类似 MIP Map，但每一层存储的是对应区域像素的**最大深度值**（即最远深度，NDC 空间中数值最大），而非平均值。

Hi-Z 层级总数的计算公式为：

$$L = \lceil \log_2(\max(W, H)) \rceil$$

其中 $W$ 为渲染目标宽度（像素），$H$ 为渲染目标高度（像素），$L$ 为所需金字塔层级总数。

例如，对于分辨率为 1920×1080 的 G-Buffer，$L = \lceil \log_2(1920) \rceil = \lceil 10.9 \rceil = 11$，即需要构建 **11 层**深度金字塔；而在半分辨率（960×540）下执行 SSR 时，$L = \lceil \log_2(960) \rceil = 10$，仅需 **10 层**。构建这 11 层金字塔需要额外 **11 次** Compute Shader 降采样 Dispatch，总内存开销约为全分辨率深度缓冲的 **133%**（由等比级数 $\sum_{k=0}^{L} \frac{1}{4^k} \approx \frac{4}{3}$ 求得）。

光线步进时采用"升降级"策略：
1. **从高层级（粗粒度）开始**，快速跳过大片无交叉区域；
2. 若当前层级的最大深度小于射线深度，说明该区域无任何几何遮挡，直接跳跃 $2^{\text{level}}$ 个像素；
3. 若存在潜在交叉，则降回更低层级（更细粒度）精确检测，直至第 0 层（像素级精度）。

这使采样次数从线性步进的 64 次降低到通常只需 **16～24 次**，性能提升约 **3 倍**，特别是在反射光线接近水平方向（掠射角）时效果最为显著。

**案例：** 在 Epic Games 于 2014 年 GDC 演讲"Physically Based Shading in Unreal Engine 4"中披露的数据中，Hi-Z 优化使复杂城市场景的 SSR Pass 从线性步进的 4.2ms 降低至 1.4ms（PS4 硬件，1080p 半分辨率），帧时缩减约 67%，在同等视觉质量下为其他渲染特性留出了更多 GPU 预算。

### 反射颜色采样与消隐

确定交叉点后，SSR 需要处理两个关键问题：

**边界消隐（Edge Fade）**：当反射光线超出屏幕边界或指向摄像机背面时，无法获得有效颜色，需要根据光线终点与屏幕边缘的距离进行淡出衰减处理，公式为：

$$\text{fade} = 1 - \text{saturate}\!\left(\frac{|uv - 0.5| \times 2 - t}{1 - t}\right)$$

其中 $uv$ 为反射命中点的屏幕空间归一化坐标（范围 $[0, 1]^2$），$t$ 为淡出起始阈值，通常取 **0.8**，即在屏幕边缘 20% 的区域线性淡出至 0，避免屏幕外反射突然消失产生视觉跳变（Pop Artifact）。$\text{saturate}(\cdot)$ 为将值钳制到 $[0, 1]$ 的操作。

**粗糙度混合（Roughness Blending）**：SSR 反射结果需与材质粗糙度（Roughness）结合，常见做法是根据 Roughness 值在 SSR 颜色与环境球谐/IBL（Image-Based Lighting）之间进行线性混合。当 $\text{Roughness} > 0.5$ 时通常完全回退到 IBL，因为 Hi-Z 步进无法高效模拟散焦模糊（Defocus Blur）反射，此时计算量不成比例地上升而视觉增益极低。部分实现（如 UE5 的 Lumen 兼容模式）引入了"模糊 SSR"模式，对反射命中点邻域进行高斯滤波模拟粗糙散射，但额外带宽开销约为 **0.4ms**，仅在高端配置下启用。

---

## 时序降噪与 TAA 集成

现代引擎中的 SSR 并非孤立的单帧算法，而是深度依赖**时序累积抗锯齿（Temporal Anti-Aliasing，TAA）** 的重建机制。Unity HDRP 技术文档（Unity Technologies, 2021）与 Unreal Engine 源码注释均记载了该设计：将每像素射线数降至 **1 次**，依靠 TAA 的历史帧混合（历史权重通常为 0.9）在时域上重建高质量反射结果。

其混合公式为：

$$C_{\text{out}} = \alpha \cdot C_{\text{history}} + (1 - \alpha) \cdot C_{\text{current}}$$

其中 $\alpha$ 为历史帧权重，典型取值 $\alpha = 0.9$；$C_{\text{current}}$ 为当前帧 SSR 单次采样颜色（RGB 值，HDR 空间）；$C_{\text{history}}$ 为经运动矢量（Motion Vector）重投影后的历史帧结果。当场景静止时，经过约 **10 帧**累积后，信噪比接近每像素 10 次采样的效果（等效于 $1/\sqrt{10} \approx 31.6\%$ 的噪声标准差降低）。

时序重投影的核心挑战在于**鬼影（Ghosting）**：当反射场景快速变化（如爆炸、快速移动的角色）时，历史帧内容已失效，若 $\alpha$ 过高则产生明显拖影。现代实现通常引入**方差裁剪（Variance Clipping）**或**邻域最小最大裁剪（Neighborhood Clamp）**机制，在检测到历史帧与当前帧颜色差异超过阈值（通常为颜色方差的 1.5～2.0 倍标准差）时，将 $\alpha$ 动态调低至 0.5 甚至 0，以牺牲稳定性换取时域响应速度。

这一设计使 Hi-Z SSR 在 1080p 分辨率下的总开销降至约 **0.8ms**（RTX 3060 级别硬件），成为当前引擎工程实践中最常见的 SSR 配置。

**例如**，在 Unity HDRP 的 `HDRenderPipeline.RenderSSR()` 流程中，SSR Trace Pass（Hi-Z 步进）与 SSR Accumulation Pass（TAA 混合）分别作为独立的 Compute Shader 调度，前者耗时约 0.4ms，后者约 0.3ms，合计约 0.7ms（测试平台：RTX 3070，1440p，半分辨率追踪）。值得注意的是，TAA 混合本身还需要一个额外的运动矢量生成 Pass（Motion Vector Pass），若引擎尚未为其他目的生成运动矢量，则 SSR 的实际总开销应加上该 Pass 的约 0.15ms。

---

## 关键公式与模型总结

SSR 涉及多个相互关联的数学公式，以下集中梳理其物理语义与工程取值：

**反射向量（Reflection Vector）**：

$$\mathbf{R} = \mathbf{V} - 2(\mathbf{V} \cdot \mathb