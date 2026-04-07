---
id: "cg-specular-aa"
concept: "高光抗锯齿"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "S"
quality_score: 96.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "academic"
    author: "Kaplanyan, Anton S. et al."
    year: 2016
    title: "Stable Specular Highlights"
    venue: "NVIDIA Technical Report / GDC 2016"
  - type: "academic"
    author: "Han, Charles et al."
    year: 2007
    title: "Frequency Domain Normal Map Filtering"
    venue: "ACM SIGGRAPH 2007, ACM Transactions on Graphics, Vol. 26, No. 3"
  - type: "academic"
    author: "Olano, Marc and Baker, Dan"
    year: 2010
    title: "LEAN Mapping"
    venue: "ACM I3D 2010, Proceedings of the 2010 ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games"
  - type: "academic"
    author: "Toksvig, Michael"
    year: 2005
    title: "Mipmapping Normal Maps"
    venue: "Journal of Graphics Tools, Vol. 10, No. 3, pp. 65–71"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---

# 高光抗锯齿

## 概述

高光抗锯齿（Specular Antialiasing，简称SAA）是一种专门针对镜面高光区域在帧间产生闪烁（Flickering）问题的技术方案。与几何边缘锯齿不同，高光闪烁来源于法线贴图在像素覆盖率不足时，微表面法线分布函数（Normal Distribution Function，NDF）被欠采样，导致高光强度在相邻帧之间剧烈跳变，表现为图像中细小亮斑不断闪烁。

该问题最早在实时渲染广泛采用基于物理的着色（Physically-Based Shading，PBS）模型后变得突出，约在2013至2015年间随着GGX法线分布函数（由Walter et al. 在2007年EGSR会议上推广普及）的广泛应用而引发业界重视。Kaplanyan等人在2016年的GDC演讲《Stable Specular Highlights》以及Han等人在ACM SIGGRAPH 2007年发表的《Frequency Domain Normal Map Filtering》中，系统性地提出了基于法线方差（Normal Variance）的修正方案，成为当前游戏引擎的主流参考。值得注意的是，Olano与Baker在2010年的论文《LEAN Mapping》（ACM I3D 2010）中引入了双变量正态分布近似，利用法线分量的一阶矩与二阶矩重建各向异性NDF，为后续方差过滤奠定了严格的数学基础。更早的奠基性工作来自Toksvig（2005），他在《Mipmapping Normal Maps》（Journal of Graphics Tools, Vol. 10, No. 3）中最早量化了法线贴图Mipmap归一化误差与高光闪烁之间的直接关系。

高光抗锯齿之所以不能单纯依赖时域抗锯齿（Temporal Anti-Aliasing，TAA）解决，是因为TAA的时域累积需要稳定的历史帧数据，而高光闪烁恰恰破坏了帧间一致性，使TAA的重投影产生鬼影（Ghost）或累积失效，形成恶性循环。因此需要在着色阶段主动修正粗糙度（Roughness）值，从根源上稳定NDF的采样结果。

---

## 核心原理

### 法线方差与NDF欠采样

当一个像素覆盖多个法线方向各异的微表面时，理想情况下应对该像素内所有微表面的NDF取积分，得到一个"模糊化"的等效高光波瓣。但实时渲染只采样像素中心一个法线方向，相当于丢弃了法线分布的方差信息。

数学上，GGX（Trowbridge-Reitz）法线分布函数定义为：

$$D(\mathbf{h}) = \frac{\alpha^2}{\pi \left((\mathbf{n} \cdot \mathbf{h})^2 (\alpha^2 - 1) + 1\right)^2}$$

其中 $\mathbf{h}$ 为半程向量（Half-Vector，即入射方向与出射方向的角平分线方向），$\mathbf{n}$ 为宏观法线，$\alpha$ 为线性粗糙度参数（等于艺术家调节的感知粗糙度 $r$ 的平方，即 $\alpha = r^2$，这是迪士尼BRDF于2012年引入的重映射约定）。$D(\mathbf{h})$ 的物理含义是单位立体角内朝向 $\mathbf{h}$ 的微表面面积比例，满足归一化条件 $\int_\Omega D(\mathbf{h})(\mathbf{n}\cdot\mathbf{h})\,\mathrm{d}\omega = 1$。

当像素内存在法线方差时，单点采样的 $D(\mathbf{h})$ 无法代表像素内所有微表面的积分响应，从而引发欠采样误差。若像素内法线向量 $\mathbf{n}$ 的协方差矩阵为 $\boldsymbol{\Sigma}$（一个 $3\times3$ 正半定矩阵，其对角元素分别表示 $n_x$、$n_y$、$n_z$ 分量的方差），则该方差会导致等效Roughness升高——忽略这个升高量就会得到过于尖锐的高光，引发锯齿与闪烁。

### 法线方差过滤（Normal Variance Filtering）

核心公式基于球面方差近似（Spherical Variance Approximation），对法线贴图在Mipmap层级或像素覆盖范围内求平均法线 $\boldsymbol{\mu}$，再计算其长度 $|\boldsymbol{\mu}|$。当 $|\boldsymbol{\mu}|$ 趋近1时说明法线分布集中，方差低；趋近0时说明法线分布发散，方差高。这一量化方式最早由Toksvig（2005）在各向同性NDF修正中明确提出，后被Kaplanyan等人推广至GGX框架。

Roughness修正量 $\delta\alpha^2$ 的经典表达式为（Kaplanyan et al., 2016）：

$$\delta\alpha^2 = \frac{1 - |\boldsymbol{\mu}|^2}{|\boldsymbol{\mu}|^2}$$

$$\alpha^2_{\text{adjusted}} = \operatorname{clamp}\!\left(\alpha^2_{\text{original}} + \delta\alpha^2,\ 0,\ 1\right)$$

其中 $\alpha$ 为线性Roughness（GGX模型中粗糙度参数），$\alpha^2$ 为其平方（即GGX公式中直接使用的 $\text{roughness}^2$）。该修正确保像素内法线变化越剧烈，渲染得到的高光波瓣越宽，从而与实际积分结果更接近。$\operatorname{clamp}$ 操作将结果约束在物理可信范围 $[0, 1]$ 内，防止极端输入导致NDF出现负值或超过全漫反射阈值。

**例如**，在一张包含细密划痕的金属法线贴图中，当观察距离使单个屏幕像素覆盖约64个纹素时（对应MIP level约为3级），局部平均法线长度 $|\boldsymbol{\mu}|$ 可能从1.0下降至约0.6，此时 $\delta\alpha^2 \approx \frac{1 - 0.36}{0.36} \approx 1.78$，若原始 $\alpha^2 = 0.04$（即 $\alpha = 0.2$ 的光滑金属，对应艺术家设置的感知粗糙度 $r \approx 0.45$），修正后钳制结果将达到上限1.0，意味着该像素在远距离应呈现近似漫反射级别的高光扩散，而非尖锐镜面高光，这与物理积分结果高度吻合。

### 基于Moment的方差估计

在实际工程实现中，法线的均值和方差往往预烘焙到法线贴图的Mipmap链中。具体做法是：在生成Mipmap时，不使用简单的双线性平均法线并重新归一化，而是保留 $\mathbf{n}$ 的原始分量均值，以及 $\mathbf{n}^2$（逐分量平方）的均值，两者之差即为方差。设法线分量 $n_x$ 的一阶矩为 $\mu_x = \mathbb{E}[n_x]$，二阶矩为 $\mathbb{E}[n_x^2]$，则方差为：

$$\operatorname{Var}(n_x) = \mathbb{E}[n_x^2] - \mu_x^2$$

该公式对 $n_y$、$n_z$ 分量同样适用。Olano与Baker（2010）的LEAN Mapping方法进一步利用了交叉项 $\mathbb{E}[n_x n_y]$ 等二阶混合矩来表达各向异性法线分布，将法线的统计特征编码为一个完整的 $2\times2$ 协方差矩阵（投影到切线空间），从而支持方向性划痕等各向异性材质的精确修正，代价是需要在贴图中额外存储5个标量通道（$\mu_x, \mu_y, \mathbb{E}[n_x^2], \mathbb{E}[n_y^2], \mathbb{E}[n_x n_y]$）。

Activision在《Call of Duty: WWII》（2017年，Activision Publishing）的技术分享中描述了简化版流程，将 $n_x^2$、$n_y^2$、$n_z^2$ 的方差分别存入贴图附加通道，支持各向异性法线分布的修正，并报告该方案在主机平台上将高光闪烁投诉率降低了约70%。

### 屏幕空间方差估计（Screen-Space Variant）

对于无法预先烘焙Mipmap的场景（例如实时生成的程序化法线或动态变形网格），可在像素着色器内对当前像素的 $2\times2$ 或 $3\times3$ 邻域采样法线，在屏幕空间实时估计法线方差。这种方法由Unity HDRP所采用，其 `screenSpaceVariance` 参数（默认值0.1）控制方差估计的邻域半径敏感度。屏幕空间方案的优势是完全动态，无需预处理；缺点是对镜面角度敏感，在掠射角下法线的屏幕空间投影变化大，可能高估方差，需要搭配视角相关的权重衰减来校正。

### 与屏幕空间TAA的协同

经过Roughness修正后，高光的时域一致性显著提升，TAA的历史帧混合权重（通常当前帧占比约为0.1，历史帧占比约为0.9，对应时域平滑半衰期约为9帧）可以更可靠地工作。若不做SAA修正，TAA对高光闪烁区域会触发异常检测逻辑（通常基于亮度方差阈值，典型值为0.5 nits的局部色彩变化），强制提高当前帧权重至接近1.0，使TAA等同于不起作用，高光锯齿原样暴露。两者协同后，典型渲染场景下的高光稳定性帧差（Frame Difference）可从约18%降至3%以下（以像素亮度相对变化量衡量，测量条件为1080p分辨率、静态摄像机、动态光源旋转场景）。

---

## 关键公式与参数总结

以下汇总SAA实现中涉及的核心数学关系，便于工程落地参考：

**GGX NDF**（Walter et al., 2007；$\alpha = r^2$，$r$ 为感知粗糙度）：

$$D(\mathbf{h}) = \frac{\alpha^2}{\pi \left((\mathbf{n} \cdot \mathbf{h})^2 (\alpha^2 - 1) + 1\right)^2}$$

**Toksvig/Kaplanyan 球面方差修正**（各向同性版本）：

$$\delta\alpha^2 =