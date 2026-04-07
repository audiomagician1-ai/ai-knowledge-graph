---
id: "cg-rt-intro"
concept: "光线追踪概述"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 93.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 光线追踪概述

## 概述

光线追踪（Ray Tracing）是一种通过模拟光线在三维场景中传播路径来生成图像的渲染算法。其基本思路是从观察者（摄像机）出发，向场景中发射虚拟光线，根据光线与物体的交点计算该像素的颜色值。这种方法与现实物理中光子从光源发出并最终进入眼睛的过程方向相反，因此也被称为"逆向光线追踪"或"眼睛射线追踪"。

光线追踪的数学基础早在16世纪就有雏形，但计算机图形学意义上的里程碑来自1980年。当年，Turner Whitted 在 ACM SIGGRAPH 发表了论文《An Improved Illumination Model for Shaded Display》，正式提出了递归光线追踪模型，后人将其称为 **Whitted-style Ray Tracing**（或经典光线追踪）。这篇论文第一次展示了用软件同时模拟镜面反射、折射和阴影的完整渲染效果，引发了图形学界的广泛关注。

与基于光栅化（Rasterization）的渲染管线相比，光线追踪天然支持全局光照效果：镜面反射、透明折射、软阴影等现象均可通过递归地发射新光线来精确计算，而不依赖任何经验性的近似技巧。这正是光线追踪在电影特效、建筑可视化等对画质要求极高的领域长期占据主导地位的根本原因。

---

## 核心原理

### 光线的数学表示

光线在三维空间中用参数方程描述：

$$\mathbf{r}(t) = \mathbf{o} + t\,\mathbf{d}, \quad t > 0$$

其中 $\mathbf{o}$ 是光线起点（Origin），$\mathbf{d}$ 是归一化方向向量（Direction），参数 $t$ 表示沿光线方向行进的距离。找到光线与场景中物体的最近交点（即最小正值 $t$），是整个光线追踪算法中最频繁执行的操作，也是加速结构（BVH、k-d树等）着力优化的目标。

### Whitted 递归模型

Whitted 模型将一次光线与表面交点处的颜色分解为三个部分：

$$L = L_{\text{local}} + k_r \cdot L_{\text{reflect}} + k_t \cdot L_{\text{refract}}$$

- $L_{\text{local}}$：局部光照（Phong 模型计算的漫反射与镜面高光）
- $k_r$：表面的反射系数，$L_{\text{reflect}}$ 由递归追踪反射光线得到
- $k_t$：表面的透射系数，$L_{\text{refract}}$ 由递归追踪折射光线（Snell 定律）得到

递归终止条件通常是：光线超过预设最大深度（Whitted 1980 年原始实验中使用的递归深度为 **5 层**），或光线对最终颜色的贡献已低于阈值。

### 阴影射线（Shadow Ray）

在每个交点处，Whitted 模型还会向场景中每一个光源各发射一条**阴影射线**（Shadow Ray）。若阴影射线在到达光源之前被其他物体遮挡，则该光源对当前交点不产生直接光照贡献。这是实现硬阴影（Hard Shadow）的直接机制。注意，阴影射线只需判断"是否遮挡"，无需计算完整的交点着色信息，因此可在相交检测一旦命中后立即终止遍历。

### 光线类型层次

在 Whitted 模型及后续扩展中，场景中存在以下几类光线：
- **主光线（Primary Ray / Camera Ray）**：从摄像机出发，每像素至少一条
- **阴影射线（Shadow Ray）**：用于判断直接光照是否被遮挡
- **反射光线（Reflection Ray）**：由镜面反射定律 $\mathbf{d}_r = \mathbf{d} - 2(\mathbf{d}\cdot\mathbf{n})\mathbf{n}$ 计算方向
- **折射光线（Refraction Ray）**：由 Snell 定律 $n_1 \sin\theta_1 = n_2 \sin\theta_2$ 计算方向

---

## 实际应用

**电影特效与离线渲染**：皮克斯的 RenderMan 及迪士尼的 Hyperion 渲染器均以光线追踪或其扩展（路径追踪）为核心。2001年上映的《怪兽电力公司》中，毛发渲染正是借助光线追踪处理复杂的光线散射。

**实时光线追踪**：2018年，NVIDIA 推出 Turing 架构 GPU（RTX 20系列），首次在硬件层面加入专用 RT Core，将光线/三角形求交速度提升约 10 倍。Direct X 12 Ultimate 与 Vulkan Ray Tracing 扩展随之成为实时游戏渲染的新标准，使《赛博朋克 2077》等游戏能够在实时场景中应用光线追踪反射与阴影。

**建筑与工业可视化**：V-Ray、Octane Render 等工具以 Whitted 模型派生的路径追踪为基础，允许建筑师在建模阶段就获得物理准确的日光照射分析结果。

---

## 常见误区

**误区一：光线追踪等同于路径追踪**  
Whitted 式光线追踪对漫反射表面只计算直接光照，不递归追踪漫反射方向的次级光线，因此**无法正确模拟漫反射间接光照（Color Bleeding）**。路径追踪（Path Tracing）在 1986 年由 James Kajiya 提出，通过在半球方向上随机采样来计算完整的渲染方程积分，才实现了真正的全局光照。两者目标不同，不可混用。

**误区二：光线追踪一定比光栅化慢**  
这一结论在 2018 年前主要成立。现代 GPU 上的硬件 BVH 遍历单元（RT Core）与光栅化管线可以**并行执行**，混合渲染管线已经可以将光线追踪阴影和反射以接近帧率的速度合并到光栅化主管线中，二者速度差距大幅缩小。

**误区三：增大递归深度总能提升画质**  
对于 Whitted 模型，递归深度超过 5～8 层后，由于 $k_r < 1$ 和 $k_t < 1$ 的衰减，额外递归带来的亮度贡献往往低于显示设备的精度阈值（通常为 $1/255$），继续增加递归深度只会白白消耗计算资源而肉眼不可见。

---

## 知识关联

**前置知识**：向量点积与叉积、参数方程、Phong 光照模型的基本概念——这些数学工具直接出现在光线与平面/球体的求交公式及反射方向计算中。

**后续概念——光线生成（Ray Generation）**：Whitted 模型中"从摄像机向每个像素发射主光线"这一步骤，在现代渲染系统中发展为独立的光线生成模块，涉及透视投影矩阵的逆变换与采样策略（如多重采样抗锯齿 MSAA 和随机采样）。

**后续概念——路径追踪（Path Tracing）**：Whitted 模型只处理完全镜面与完全透明表面，无法正确积分漫反射材质的半球光照。路径追踪在此基础上引入蒙特卡罗积分，对渲染方程 $L_o = L_e + \int_\Omega f_r \cdot L_i \cdot \cos\theta\, d\omega$ 进行统计估算，从而解决了 Whitted 模型遗留的漫反射间接光问题。