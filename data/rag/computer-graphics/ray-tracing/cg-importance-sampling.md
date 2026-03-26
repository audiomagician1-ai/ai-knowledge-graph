---
id: "cg-importance-sampling"
concept: "重要性采样"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 4
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 重要性采样

## 概述

重要性采样（Importance Sampling）是蒙特卡洛积分中的一种方差缩减技术，其核心思想是：在估计积分 $\int f(x)\,dx$ 时，不以均匀分布采样，而是按照与被积函数形状相似的概率密度函数（PDF）$p(x)$ 进行采样，从而使估计量 $\hat{I} = \frac{1}{N}\sum_{i=1}^{N}\frac{f(x_i)}{p(x_i)}$ 的方差显著降低。在光线追踪渲染方程中，被积函数为 $L_o = \int_\Omega f_r(\omega_i, \omega_o) \cdot L_i(\omega_i) \cdot \cos\theta_i \,d\omega_i$，该积分包含 BRDF、入射辐照度和余弦项三个因子，若三者之积的形状能被 $p(\omega_i)$ 很好地近似，方差就趋近于零。

重要性采样在图形学中的系统性应用可以追溯到 James Kajiya 1986 年提出渲染方程之后，Lafortune 和 Willems 于 1993 年在其路径追踪实现中明确展示了按 BRDF 采样的方差缩减效果。在此之前，均匀半球采样（cosine-weighted sampling 也需到 1990 年代才被广泛采用）导致渲染高光材质时需要数千个样本才能收敛，而良好的重要性采样可将同等质量所需的样本数降低一到两个数量级。这一特性使重要性采样成为现代物理渲染器（如 Mitsuba、PBRT v4、Cycles）中路径追踪的标配采样策略。

## 核心原理

### 蒙特卡洛估计量与方差公式

给定一维积分 $I = \int_a^b f(x)\,dx$，蒙特卡洛估计量为 $\hat{I} = \frac{1}{N}\sum_{i=1}^N \frac{f(x_i)}{p(x_i)}$，其中 $x_i \sim p(x)$。该估计量的方差为：

$$\mathrm{Var}[\hat{I}] = \frac{1}{N}\int_a^b \left(\frac{f(x)}{p(x)} - I\right)^2 p(x)\,dx$$

当 $p(x) \propto f(x)$（即 $p(x) = f(x)/I$）时，方差恰好为零。实际中无法直接得到这个理想的 PDF（否则积分已知），但选择与 $f(x)$ 形状相近的 $p(x)$ 可使方差大幅降低。在渲染方程中，$f(x)$ 对应 $f_r \cdot L_i \cdot \cos\theta$，由于入射光 $L_i$ 通常未知，实践上常对 BRDF 或余弦项单独构造 PDF。

### 余弦加权半球采样

最简单的重要性采样是余弦加权采样，其 PDF 为 $p(\omega) = \frac{\cos\theta}{\pi}$（对上半球积分验证：$\int_\Omega \frac{\cos\theta}{\pi}\,d\omega = 1$）。对应的采样方法使用 Malley 方法：先在单位圆盘上均匀采样点 $(r, \phi)$，其中 $r = \sqrt{\xi_1}$，$\phi = 2\pi\xi_2$，再投影到半球 $z = \sqrt{1-r^2}$。相比均匀半球采样（PDF $= 1/2\pi$），余弦加权采样消去了渲染方程中的 $\cos\theta$ 因子，对漫反射材质的方差缩减比可达 $\pi$ 倍。

### BRDF 重要性采样

对于镜面反射较强的材质，余弦采样仍会浪费样本到 BRDF 接近零的方向。典型的 GGX 微面元 BRDF 的法线分布函数（NDF）为：

$$D(h) = \frac{\alpha^2}{\pi\left((\alpha^2-1)\cos^2\theta_h + 1\right)^2}$$

其中 $\alpha$ 为粗糙度参数，$\theta_h$ 为半程向量与法线夹角。可以直接对该 NDF 采样半程向量 $h$：

$$\theta_h = \arctan\!\left(\alpha\sqrt{\frac{\xi_1}{1-\xi_1}}\right), \quad \phi_h = 2\pi\xi_2$$

然后由 $h$ 反射入射方向 $\omega_i = 2(h \cdot \omega_o)h - \omega_o$，对应的 PDF 为 $p(\omega_i) = \frac{D(h)\cos\theta_h}{4(\omega_o \cdot h)}$。粗糙度 $\alpha = 0.1$ 的高光材质使用 BRDF 重要性采样相比余弦采样，方差可降低超过 100 倍。

### 逆变换采样与拒绝采样

从非均匀 PDF 生成样本通常使用**逆变换法**：首先计算 CDF $F(x) = \int_{-\infty}^x p(t)\,dt$，再令 $x = F^{-1}(\xi)$，其中 $\xi \sim U[0,1]$。GGX 的 $\theta_h$ 采样公式正是由逆变换法解析推导得到的。对于解析形式复杂的 BRDF（如多层材质），可退而使用拒绝采样，但拒绝率过高会抵消方差收益，实践中需权衡。

## 实际应用

**漫反射场景**：Unity HDRP 和 Unreal Engine 的路径追踪模式对纯漫反射表面均采用余弦加权采样，在 $N=1$ 的单样本路径追踪中，将均匀采样替换为余弦采样后，漫反射区域的噪声在视觉上可减少约 30–40%。

**金属高光材质**：PBRT v4 对 TrowbridgeReitzDistribution（即 GGX）实现了解析逆变换采样，在 $\alpha=0.05$ 的镜面金属球渲染中，10 spp（每像素采样数）下 BRDF 重要性采样的 MSE 约为余弦采样的 1/500。

**环境光贴图采样**：预先对 HDR 环境贴图构建二维分段常数分布，生成对应 PDF，再用逆变换法采样光源方向。Blender Cycles 的 Sky Texture 节点即使用此方案，对太阳盘的强烈高光方向赋予极高采样权重，使户外场景收敛速度提升数倍。

## 常见误区

**误区一：PDF 越"尖"越好**。若 $p(\omega_i)$ 过于集中而 $L_i(\omega_i)$ 在该方向恰好接近零（例如对着墙壁的强高光方向），则商 $f_r \cdot L_i / p$ 中 $L_i \approx 0$ 但 $p$ 极大，其他方向 $L_i$ 很大但几乎不被采样，反而造成方差爆炸（fireflies 萤火虫噪点）。理想 PDF 应正比于完整被积函数 $f_r \cdot L_i \cdot \cos\theta$，仅对 BRDF 采样是局部最优而非全局最优。

**误区二：重要性采样会改变期望值**。只要 $p(x) > 0$ 在 $f(x) \neq 0$ 的所有区域成立（无偏性条件），估计量 $\frac{f(x_i)}{p(x_i)}$ 的期望值与原积分完全相同。重要性采样仅影响方差，不影响无偏性。许多初学者因计算错误的 PDF 导致能量损失，误以为这是重要性采样的固有缺陷。

**误区三：BRDF 采样的 PDF 不需要包含雅可比行列式**。当从半程向量空间 $d\omega_h$ 采样转换到入射方向空间 $d\omega_i$ 时，必须乘以雅可比 $\frac{d\omega_h}{d\omega_i} = \frac{1}{4(\omega_o \cdot h)}$。遗漏此项是 GGX 采样实现中最常见的 bug，表现为高光亮度随粗糙度变化时出现系统性偏差。

## 知识关联

**前置概念——路径追踪**：路径追踪通过递归地估计渲染方程，每次弹射都需要在半球上采样新方向。若使用均匀采样，低粗糙度材质需要极多样本才能命中有效的 BRDF 波瓣；重要性采样正是在此基础上为每次方向采样提供了与 BRDF 形状对齐的 PDF，从而加速路径收敛。

**后续概念——多重重要性采样（MIS）**：单纯的 BRDF 重要性采样对强点光源仍效率低下（BRDF 波瓣未必朝向光源），而纯光源采样对高光材质效率低下。MIS 使用 balance heuristic 公式 $w_s = \frac{n_s p_s}{\sum_k n_k p_k}$ 将多个 PDF 的贡献合并，彻底解决此两难困境，是现代渲染器中重要性采样的实际使用形式。

**后续概念——ReSTIR**：ReSTIR（2020，Bitterli 等）将重要性采样扩展到时序和空间的样本复用，通过带权蓄水池采样（Weighted Reservoir Sampling）