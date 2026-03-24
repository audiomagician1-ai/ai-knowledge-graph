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
---
# SDF建模

## 概述

有符号距离场（Signed Distance Field，SDF）是一种将三维空间中每个点映射为该点到最近几何表面距离的标量场表示方法，其中正值表示点位于几何体外部，负值表示点位于几何体内部，零值对应几何表面本身。与体素网格或多边形网格不同，SDF以连续函数 $f: \mathbb{R}^3 \to \mathbb{R}$ 的形式隐式描述几何形状，满足 Eikonal 方程 $|\nabla f(\mathbf{x})| = 1$，即梯度模长处处为1。

SDF建模方法在图形学中的早期系统应用可追溯至1996年Blinn提出的元球（Metaball）概念的延伸，以及2002年Hart对光线步进（Sphere Tracing）算法的形式化描述。Sphere Tracing利用SDF的距离保证特性，允许光线以当前点的SDF值为步长安全前进而不穿透表面，这使得无需三角形网格即可完成精确渲染。

SDF建模的重要性体现在三个方面：其一，布尔运算（并集、交集、差集）可通过简单的 $\min$/$\max$ 操作近似实现，避免了多边形网格布尔运算的拓扑复杂性；其二，SDF天然支持平滑混合（Smooth Blending）操作，能在不同几何体之间生成有机过渡形态；其三，SDF是神经隐式曲面（如DeepSDF、NeRF衍生方法）的核心表示基础。

## 核心原理

### SDF的构建方法

构建SDF有三条主要路径：

**解析构建**适用于基本几何体。例如，球心在原点、半径为 $r$ 的球体SDF为 $f(\mathbf{x}) = |\mathbf{x}| - r$；无限长轴对齐长方体（半尺寸为 $\mathbf{b}$）的SDF为 $f(\mathbf{x}) = |\text{length}(\max(\mathbf{|x|} - \mathbf{b}, \mathbf{0}))| + \min(\max(|x|-b), 0)$。Inigo Quilez维护的SDF公式库收录了超过50种基本形状的解析表达式，是行业标准参考。

**从网格计算**需要对每个离散采样点求最近点距离并附加符号。符号判断通常通过检查点与最近三角面的法线夹角确定：若夹角小于90°则为正（外部），否则为负（内部）。实践中常用的快速算法是基于BVH（包围体层次结构）加速的最近点查询，复杂度约为 $O(\log N)$（$N$为三角面数量）。

**快速行进法（Fast Marching Method）**和**快速扫描法（Fast Sweeping Method）**用于在已知窄带SDF的情况下向外传播距离场。Fast Sweeping在规则网格上的时间复杂度为 $O(N)$，其中 $N$ 为网格点总数，需进行 $2^d$（$d$为维度）次扫描方向的更新。

### 布尔运算与平滑混合

SDF布尔运算的数学表达极为简洁：
- **并集**：$f_{A \cup B}(\mathbf{x}) = \min(f_A(\mathbf{x}), f_B(\mathbf{x}))$
- **交集**：$f_{A \cap B}(\mathbf{x}) = \max(f_A(\mathbf{x}), f_B(\mathbf{x}))$
- **差集**：$f_{A \setminus B}(\mathbf{x}) = \max(f_A(\mathbf{x}), -f_B(\mathbf{x}))$

需要注意的是，上述 $\min$/$\max$ 操作会在结合处产生 $C^0$ 不连续（梯度跳变），严格来说结果不再满足 Eikonal 方程，仅为近似SDF。

为获得有机融合效果，Inigo Quilez提出了基于参数 $k$ 的**平滑最小值函数（smin）**：
$$\text{smin}(a, b, k) = \min(a, b) - \frac{k}{4} \cdot \max\left(k - |a - b|, 0\right)^2 \cdot \frac{1}{k}$$
当 $k$ 趋近0时退化为精确的 $\min$ 操作，$k$ 增大时在结合区域产生宽度约为 $k$ 的平滑过渡带，广泛用于角色建模和生物形态设计。

### SDF的可视化与渲染

将SDF可视化为几何表面最常用的方法是**Marching Cubes等值面提取**（等值面取 $f=0$），在分辨率为 $N^3$ 的网格上时间复杂度为 $O(N^3)$。Marching Cubes的256种构型可通过对称性压缩为15种基本情况处理，由Lorensen和Cline于1987年发表于SIGGRAPH。

**Sphere Tracing**是SDF特有的直接光线渲染方式：从相机出发的光线沿方向 $\mathbf{d}$ 步进，每步步长取当前点的SDF值 $t_{n+1} = t_n + f(\mathbf{x}_n)$，当 $f(\mathbf{x}) < \epsilon$（通常取 $10^{-4}$）时判定命中表面。相比传统光线投射无需三角形求交，渲染程序可仅用几百行GLSL代码实现完整的SDF场景渲染。

## 实际应用

**游戏与实时图形**：Epic Games在Unreal Engine 5中引入了基于SDF的全局光照系统（Lumen），使用Mesh Distance Fields为场景中每个静态网格预计算SDF，并在屏幕空间追踪软阴影和间接光，阴影计算的锥体追踪步数通常设置为64步。

**程序化建模工具**：ShaderToy平台上超过10万个项目使用SDF建模技术实时渲染复杂有机形态，开发者在片段着色器中以函数组合方式定义整个场景，代码量通常在50到300行之间。

**医学影像**：CT/MRI体数据处理中，将组织分割结果转化为SDF后可精确测量肿瘤与周围器官的安全间距，用于放射治疗的剂量规划，精度达亚毫米级别。

**字体渲染**：Valve公司于2007年提出将字体轮廓烘焙为低分辨率SDF纹理（通常为64×64像素），在着色器中以 $f \geq 0.5$ 为阈值重建字形边缘，在任意缩放比例下均可获得无锯齿的清晰文字，该技术已被几乎所有主流游戏引擎采用。

## 常见误区

**误区一：SDF布尔运算后仍然是精确距离场**
min/max布尔运算得到的结果仅在两个输入SDF的零等值面附近有效，远离表面的区域距离值可能严重失真。例如两个球体的并集SDF在两球重叠区域以外表现正常，但若对其结果再进行嵌套布尔运算，误差会迅速累积。需要精确SDF时必须在布尔运算后重新执行距离场传播（如Fast Sweeping重算）。

**误区二：Sphere Tracing不会错过细小几何特征**
当场景中存在极细的几何结构（厚度远小于光线初始步长）时，Sphere Tracing可能直接跳过该结构而不命中。这不是光线步长设置问题，而是SDF自身在细薄结构附近的正确值就很小，此时需要限制最大步长或使用增强步进策略（Relaxed Sphere Tracing）。

**误区三：平滑混合smin保持距离场性质**
使用smin进行平滑混合后，结合区域内SDF的梯度模长不再等于1，即结果不再是距离场而是一般标量场。直接在此结果上应用Sphere Tracing会导致步进过量（Over-stepping），可能穿透表面或引发渲染黑斑，需通过缩放修正因子（通常乘以0.8至0.95）或迭代修正来补偿。

## 知识关联

SDF建模以**等值面提取**为可视化出口——Marching Cubes算法正是将SDF的零等值面转化为三角网格的桥梁，理解等值面提取中的歧义情况（Ambiguous Cases）有助于解释SDF建模时某些细薄特征丢失的原因。

SDF建模是**神经网络几何**的直接前驱。DeepSDF（Park等，2019，CVPR）将SDF的解析公式替换为神经网络 $f_\theta(\mathbf{z}, \mathbf{x})$，用潜在向量 $\mathbf{z}$ 编码形状变化，本质上是学习一族SDF函数的参数化表示。理解标准SDF的Eikonal约束和布尔运算局限性，有助于理解为何神经SDF训练需要加入梯度正则化损失项 $\lambda \cdot \mathbb{E}[|\nabla_\mathbf{x} f_\theta - 1|^2]$。
