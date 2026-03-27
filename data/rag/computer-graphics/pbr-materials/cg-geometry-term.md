---
id: "cg-geometry-term"
concept: "几何遮蔽项"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 几何遮蔽项

## 概述

几何遮蔽项（Geometry Term，记作 $G$）是 Cook-Torrance 微表面 BRDF 中专门描述微表面自遮挡现象的因子。在真实材质中，粗糙表面的微小凸起会在入射方向遮挡其他微表面（遮蔽，Shadowing），也会在出射方向遮挡反射光线（掩蔽，Masking），几何遮蔽项将这两种效果合并为一个 $[0,1]$ 范围内的衰减系数。

几何遮蔽项的系统性研究始于 1967 年 Torrance 和 Sparrow 对金属表面光散射的物理分析，他们首次将微几何遮挡写入反射方程。1963 年 Beckmann 分布和后来 1977 年 Cook-Torrance 模型的发表确立了完整框架，但早期的 $G$ 近似方法（如 Schlick-Smith 近似）存在能量不守恒的问题。2014 年 Eric Heitz 在 JCGT 上发表的论文《Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs》系统推导了满足能量守恒的 Height-Correlated Smith 模型，成为现代 PBR 的标准参考。

几何遮蔽项对渲染结果的影响直接体现在掠射角（grazing angle）处的明暗过渡上。若省略该项，粗糙材质在边缘处会出现不真实的过亮现象；若选用不精确的近似，金属、非金属的菲涅耳效果与粗糙度的交互会产生系统性误差，导致整个材质库的色调偏差。

---

## 核心原理

### Smith 遮蔽函数

Smith 几何遮蔽函数将掩蔽函数 $G_1(\mathbf{v}, \mathbf{m})$ 定义为从观察方向 $\mathbf{v}$ 看微表面法线 $\mathbf{m}$ 可见的概率。Smith 的关键假设是：微表面的高度与斜率统计独立，使得 $G_1$ 只依赖于观察方向的仰角而与具体法线方向解耦。对于 GGX（Trowbridge-Reitz）分布，$G_1$ 的解析形式为：

$$G_1(\mathbf{v}) = \frac{2}{1 + \sqrt{1 + \alpha^2 \tan^2\theta_v}}$$

其中 $\alpha$ 是各向同性粗糙度参数（通常由美工输入的粗糙度 $r$ 映射为 $\alpha = r^2$），$\theta_v$ 是观察方向与宏观法线的夹角。当 $\alpha \to 0$（光滑表面）时 $G_1 \to 1$，当 $\theta_v \to 90°$ 时 $G_1 \to 0$，与物理直觉完全吻合。

### Uncorrelated 与 Height-Correlated 模型

朴素的 Smith 联合遮蔽-掩蔽函数将入射方向 $\mathbf{l}$ 和出射方向 $\mathbf{v}$ 的遮蔽视为统计独立事件：

$$G_{\text{uncorr}}(\mathbf{l}, \mathbf{v}) = G_1(\mathbf{l}) \cdot G_1(\mathbf{v})$$

然而 Heitz 2014 年的推导表明，真实微表面上入射和出射路径共享相同的高度分布，二者存在正相关性——位于微表面高处的点同时对入射和出射都更可见。Height-Correlated Smith 模型的联合函数为：

$$G_2(\mathbf{l}, \mathbf{v}) = \frac{1}{1 + \Lambda(\mathbf{l}) + \Lambda(\mathbf{v})}$$

其中 $\Lambda$ 是 Smith 辅助函数（auxiliary function）。对于 GGX 分布：

$$\Lambda(\mathbf{v}) = \frac{-1 + \sqrt{1 + \alpha^2 \tan^2\theta_v}}{2}$$

Height-Correlated 模型的分母是 $1 + \Lambda_l + \Lambda_v$，而非 Uncorrelated 模型的 $(1+\Lambda_l)(1+\Lambda_v)$。这一差异在 $\alpha = 0.5$、$\theta_v = \theta_l = 45°$ 时可产生约 8% 的亮度差距，对高粗糙度金属的外观影响尤为显著。

### 完整几何项在 BRDF 中的位置

在 Cook-Torrance BRDF 的标准形式中：

$$f_r = \frac{D(\mathbf{m}) \cdot G_2(\mathbf{l}, \mathbf{v}) \cdot F(\mathbf{v}, \mathbf{m})}{4 (\mathbf{n} \cdot \mathbf{l})(\mathbf{n} \cdot \mathbf{v})}$$

分母中的 $4(\mathbf{n} \cdot \mathbf{l})(\mathbf{n} \cdot \mathbf{v})$ 来自雅可比行列式转换。$G_2$ 的作用是抵消这一分母在掠射角趋于零时的放大效应，保证 BRDF 不发散。部分引擎（如 Unreal Engine 4）将 $G_2$ 与分母合并，定义可见性项 $V = G_2 / (4(\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v}))$，以减少 GPU 浮点运算量。

---

## 实际应用

**实时渲染的近似优化**：完整的 Height-Correlated Smith $G_2$ 包含两次平方根运算，在延迟渲染管线中每像素开销较高。Filament（Google 的移动端 PBR 引擎）采用 Hammon 2017 提出的近似，将 $G_2$ 改写为关于 $(\mathbf{n}\cdot\mathbf{l})$ 和 $(\mathbf{n}\cdot\mathbf{v})$ 的线性插值，误差在 $\alpha \in [0.1, 1.0]$ 范围内不超过 1.5%，同时省去两次 `sqrt` 调用。

**各向异性材质扩展**：对于拉丝金属等各向异性表面，$\alpha$ 被分解为切线方向 $\alpha_t$ 和副切线方向 $\alpha_b$ 两个参数，$\Lambda$ 函数需分别在两个方向上计算，并以方位角加权合并。Blender Cycles 的各向异性 GGX 节点即采用此扩展形式。

**离线渲染的多重散射补偿**：单次散射的 $G_2$ 模型在 $\alpha > 0.5$ 时会丢失微表面间多次弹射的能量，导致高粗糙度材质整体偏暗。Kulla-Conty 2017 提出通过预计算补偿纹理 $E(\mu, \alpha)$ 来恢复这部分能量，Arnold、RenderMan 等离线渲染器已内置此补偿，而实时渲染中 Unreal Engine 5 的 Lumen 也在部分路径上引入了类似修正。

---

## 常见误区

**误区一：把 $G$ 当做简单的 NdotL/NdotV 截断**

初学者有时直接用 $\min(1, 2(\mathbf{n}\cdot\mathbf{h})(\mathbf{n}\cdot\mathbf{v})/(\mathbf{v}\cdot\mathbf{h}))$ 这一几何光学推导的旧式公式代替 Smith 函数。该公式来自 Torrance-Sparrow 1967 年的 V 形槽（V-cavity）假设，与 GGX 等统计分布的微表面模型并不匹配，会在中等粗糙度（$\alpha \approx 0.3$）下产生明显偏亮的高光边缘，与 Smith GGX 的结果偏差可超过 15%。

**误区二：认为 Schlick 的 $k$ 参数对直接光和 IBL 应相同**

Unreal Engine 4 的 PBR 白皮书明确指出，针对直接光照使用 $k = \alpha^2 / 2$，而对 IBL（基于图像的光照）预积分使用 $k = \alpha^2 / 2$ 的不同变体，原因是 IBL 的半球积分覆盖所有入射角，若使用同一 $k$ 会导致材质在从点光源切换到环境光时出现肉眼可见的亮度跳变。这一区别源于 $G_1$ 在不同积分域上的统计行为差异，而非任意的工程 hack。

**误区三：Height-Correlated 模型总优于 Uncorrelated 模型**

Height-Correlated $G_2$ 在物理上更准确，但它假设入射和出射路径沿高度方向完全正相关，这在光线方向差异较大（如后向散射接近 180°）时反而低估了真实遮蔽量。Heitz 论文中提到 Direction-Correlated 模型可进一步修正此问题，但其计算复杂度使其目前只适用于离线路径追踪。

---

## 知识关联

**与 Cook-Torrance 模型的依赖关系**：几何遮蔽项是 Cook-Torrance BRDF 四个因子（$D$、$G$、$F$、归一化分母）之一，必须与 NDF（法线分布函数）配对使用——GGX 的 $D$ 必须搭配 GGX 推导出的 Smith $\Lambda$ 函数，若将 Beckmann 的 $