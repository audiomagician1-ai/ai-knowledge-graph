---
id: "cg-sdf-modeling"
concept: "SDF建模"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# SDF建模

## 概述

SDF（Signed Distance Field，有符号距离场）建模是一种将几何形体表示为距离函数的隐式建模方法。对于空间中任意一点 **p**，SDF函数 f(**p**) 返回该点到最近几何表面的有符号距离：若点在形体内部则返回负值，在外部返回正值，恰好位于表面时返回零。这条零等值线（零等值面）即为几何体的边界，与等值面提取技术天然衔接。

SDF建模的现代形态由 John Hart 于1996年在论文《Sphere Tracing》中系统化奠基，他提出了利用SDF值作为步长进行光线行进的球追踪算法，使隐式曲面渲染从理论走向实用。此前，Blinn于1982年已使用隐函数描述"水滴"融合效果（Blobby模型），但彼时尚未标准化符号约定。SDF建模的价值在于：布尔运算退化为简单的数学函数组合，拓扑自动处理，且天然支持平滑过渡与形变，是实时渲染、物理仿真与几何深度学习的共同基础。

## 核心原理

### 基本几何体的精确SDF公式

每种基本形体都有解析SDF表达式。以球体为例，圆心在原点、半径为 r 的球体：

$$f(\mathbf{p}) = |\mathbf{p}| - r$$

对于轴对齐包围盒（AABB），半边长向量为 **b**，则：

$$f(\mathbf{p}) = |\text{max}(|\mathbf{p}| - \mathbf{b},\ \mathbf{0})| + \min(\max(p_x - b_x,\ p_y - b_y,\ p_z - b_z),\ 0)$$

圆环（Torus）的SDF涉及两个半径参数 R（大半径）和 r（管道半径）：

$$f(\mathbf{p}) = \sqrt{(\sqrt{p_x^2 + p_z^2} - R)^2 + p_y^2} - r$$

这些解析公式的关键特性是它们均满足 **Lipschitz常数为1**，即 $|\nabla f| = 1$（几乎处处成立），这一特性称为"精确SDF"或"1-Lipschitz条件"，是球追踪算法收敛性的理论保证。

### 布尔运算的函数组合

SDF最大的建模优势在于布尔运算可直接用数学函数实现，无需处理网格拓扑：

- **并集（Union）**：$f_{A \cup B}(\mathbf{p}) = \min(f_A(\mathbf{p}),\ f_B(\mathbf{p}))$
- **交集（Intersection）**：$f_{A \cap B}(\mathbf{p}) = \max(f_A(\mathbf{p}),\ f_B(\mathbf{p}))$
- **差集（Subtraction）**：$f_{A \setminus B}(\mathbf{p}) = \max(f_A(\mathbf{p}),\ -f_B(\mathbf{p}))$

需要注意的是，min/max操作会**破坏精确SDF特性**——合并后的函数不再满足 $|\nabla f| = 1$，在两个形体的边界交汇处梯度不连续。为解决此问题，Inigo Quilez（shadertoy社区核心贡献者）引入了**平滑并集（Smooth Union）**：

$$f_{\text{smooth}}(\mathbf{p}) = \min(f_A, f_B) - h^2/(4k)$$

其中 $h = \max(k - |f_A - f_B|,\ 0)$，参数 k 控制融合半径，k=0 退化为普通并集。

### 离散化存储与梯度计算

在实时渲染和物理引擎中，SDF常被预计算并存储在三维体素网格（3D Texture）中，典型分辨率为 $128^3$ 至 $512^3$。查询时用三线性插值获得连续值，梯度（即表面法向量）通过中心差分估计：

$$\mathbf{n} \approx \frac{\nabla f}{|\nabla f|}, \quad \frac{\partial f}{\partial x} \approx \frac{f(\mathbf{p} + \epsilon\hat{x}) - f(\mathbf{p} - \epsilon\hat{x})}{2\epsilon}$$

典型 $\epsilon$ 取值为网格间距的0.5倍。离散SDF还可通过**快速行进法（Fast Marching Method）**或 **CUDA并行距离变换**（如 cuSDFGen 工具）从网格直接生成，后者在 $256^3$ 分辨率下可在GPU上50毫秒内完成。

## 实际应用

**实时游戏中的碰撞检测**：Unreal Engine 的 Distance Field Ambient Occlusion（DFAO）功能为场景中每个静态网格预生成体素SDF，在着色器中通过8次球追踪步骤近似计算环境光遮蔽，相比SSAO在大半径遮蔽上表现更准确。每个网格的SDF存储在 $8^3$ 到 $128^3$ 的体素中，引擎默认精度为网格包围盒的 $1/128$。

**程序化建模与Shadertoy**：在片段着色器中，整个场景可由SDF函数树描述，不需要任何网格数据。Inigo Quilez的经典示例"Primitives"展示了如何在100行GLSL中构建含20种基本体的完整场景，球追踪最多迭代100步，步长精度阈值设为 0.001。

**医学影像分割**：将CT/MRI扫描的二值分割掩膜转换为SDF，使得器官边界可用连续函数表示。以肝脏分割为例，将体素标注转为SDF后，网络预测的符号距离可直接施加物理约束（如梯度幅值接近1），比直接预测二值标签的网络泛化性提升约3-5%（基于Medical Image Analysis 2020的报告数据）。

## 常见误区

**误区一：布尔运算后仍是精确SDF**。使用 min/max 进行布尔组合后，结果函数的梯度幅值不再处处等于1，尤其在两个形体距离相近的区域梯度会偏小（小于1）。若此时直接用该函数的值作为球追踪步长，步长会被低估，导致渲染速度降低但不会产生穿透，这是安全失效；但若用于物理碰撞，则距离估计偏保守。区分精确SDF（exact SDF）与有界SDF（bounded SDF）非常重要。

**误区二：SDF的零值面精度与分辨率无关**。对于离散存储的SDF，零等值面的几何精度直接受体素分辨率约束。一个 $64^3$ 的SDF网格，在1米×1米×1米的包围盒内，最小可分辨特征约为 1000/64 ≈ 15.6毫米。通过对存储值做三线性插值后提取等值面（如用Marching Cubes），可以恢复亚体素精度的法向量，但无法恢复被混叠的细节几何。

**误区三：平滑并集在所有形体之间都产生圆滑过渡**。平滑并集的融合效果只在两形体距离小于参数 k 时生效；当两形体相距超过 k 时，行为与普通并集完全一致。若场景中多个形体共用同一 k 值，融合半径是固定的绝对值（如 k=0.1 意味着0.1单位的融合区），因此不同尺寸形体之间的融合视觉效果会显得不一致。

## 知识关联

SDF建模以**等值面提取**为下游可视化工具：通过Marching Cubes或Dual Contouring算法，将SDF的零等值面转换为三角网格，进而可导入传统渲染管线。SDF中的梯度场即为法向量场，等值面提取的质量（尤其是特征边保留）直接依赖SDF的精确程度。

向前延伸，SDF建模是**神经网络几何**（Neural Implicit Representation）的直接前身。DeepSDF（Park et al., CVPR 2019）将SDF解码器设计为8层MLP，输入三维坐标和128维潜在向量，直接回归有符号距离值；NeRF及后续方法中的密度场可看作SDF的软化变体（用密度替代硬边界）。理解精确SDF的Lipschitz约束，有助于理解为何神经SDF训练时需要引入Eikonal损失项 $\mathcal{L}_\text{eikonal} = (|\nabla f| - 1)^2$ 来正则化梯度。