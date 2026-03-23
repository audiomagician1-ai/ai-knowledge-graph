---
id: "cg-ray-intersection"
concept: "光线求交"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 2
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.364
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 光线求交

## 概述

光线求交（Ray Intersection）是光线追踪渲染管线中最基础的几何计算步骤，指的是给定一条参数化射线和场景中的几何体，求出射线与该几何体相交的位置参数 $t$ 值。没有正确的求交结果，光线追踪就无法判断光线击中了哪个物体，后续的着色、阴影、反射计算都无从进行。

光线求交算法的数学基础在20世纪60至70年代随光线追踪技术的奠基性工作逐步成形。1968年 Arthur Appel 的光线投射（Ray Casting）论文和1980年 Turner Whitted 的递归光线追踪论文中，球体和平面的求交是最先被系统描述的几何求解方法。三角形求交则在1997年 Möller-Trumbore 算法发表后才有了目前工业界最广泛使用的高效形式。

光线求交的效率直接影响整体渲染性能，因为对于一帧分辨率 1920×1080、采样数 64 的渲染任务，场景中每个物体都可能被执行数亿次求交测试，因此即使单次求交计算减少几条指令也会带来可测量的帧时间降低。

---

## 核心原理

### 射线的参数化表示

所有光线求交算法共享同一条射线定义：

$$\mathbf{r}(t) = \mathbf{o} + t\,\mathbf{d}, \quad t \geq 0$$

其中 $\mathbf{o}$ 是射线起点（origin），$\mathbf{d}$ 是单位方向向量（direction），$t$ 是无量纲的参数距离。当 $t > 0$ 时点在摄像机前方；$t < 0$ 则在摄像机后方，应予以丢弃。实现中通常同时维护 $t_{\min}$（如 $10^{-4}$，避免自相交）和 $t_{\max}$（当前已知最近交点），每次成功求交后更新 $t_{\max}$，保证只保留最近可见表面。

### 射线与球体求交

设球心为 $\mathbf{c}$、半径为 $r$，将射线方程代入球面方程 $|\mathbf{p} - \mathbf{c}|^2 = r^2$，展开后得到关于 $t$ 的一元二次方程：

$$at^2 + bt + c = 0$$

其中：
- $a = \mathbf{d} \cdot \mathbf{d}$（若 $\mathbf{d}$ 已归一化则 $a=1$）
- $b = 2(\mathbf{d} \cdot (\mathbf{o} - \mathbf{c}))$
- $c = (\mathbf{o}-\mathbf{c})\cdot(\mathbf{o}-\mathbf{c}) - r^2$

判别式 $\Delta = b^2 - 4ac$：当 $\Delta < 0$ 时无交点；$\Delta = 0$ 时射线相切（仅一个交点）；$\Delta > 0$ 时穿透球体，返回较小的正根作为入射点。球体求交是最廉价的求交之一，约需 10–15 次浮点运算。

### 射线与平面求交

设平面由法向量 $\mathbf{n}$ 和平面上一点 $\mathbf{q}$ 定义，满足 $\mathbf{n} \cdot (\mathbf{p} - \mathbf{q}) = 0$，代入射线方程后直接求解：

$$t = \frac{\mathbf{n} \cdot (\mathbf{q} - \mathbf{o})}{\mathbf{n} \cdot \mathbf{d}}$$

当分母 $\mathbf{n} \cdot \mathbf{d} = 0$ 时，射线与平面平行，无交点（或无穷多交点，实际中忽略）。平面求交仅需 1 次除法和两次点积，是所有基本图元中计算量最小的。

### 射线与三角形求交（Möller-Trumbore 算法）

三角形是实时图形学中最常见的图元，Möller-Trumbore（1997）算法利用重心坐标直接求解，避免了先求平面交点再验证内外的两步流程。设三角形顶点为 $\mathbf{v}_0, \mathbf{v}_1, \mathbf{v}_2$，令：

$$\mathbf{e}_1 = \mathbf{v}_1 - \mathbf{v}_0, \quad \mathbf{e}_2 = \mathbf{v}_2 - \mathbf{v}_0, \quad \mathbf{s} = \mathbf{o} - \mathbf{v}_0$$

则解方程组得到：

$$\begin{pmatrix} t \\ u \\ v \end{pmatrix} = \frac{1}{\mathbf{e}_1 \times \mathbf{e}_2 \cdot \mathbf{d}} \begin{pmatrix} \mathbf{e}_2 \times \mathbf{d} \cdot \mathbf{s} \\ \mathbf{s} \times \mathbf{e}_1 \cdot \mathbf{d} \\ \mathbf{e}_2 \times \mathbf{d} \cdot \mathbf{s} \end{pmatrix}$$

有效交点的条件为：$t > 0$，$u \geq 0$，$v \geq 0$，且 $u + v \leq 1$。重心坐标 $(1-u-v, u, v)$ 还可直接用于插值法线和 UV，使该算法成为"一石二鸟"的实用方案。整个计算大约需要 1 次叉积（6 次乘加）和数次点积，共约 25–30 次浮点运算。

---

## 实际应用

**场景遍历中的最近交点查找**：在最朴素的光线追踪实现中，每条射线需对场景中所有几何体逐一调用求交函数，并以 $t_{\max}$ 过滤更远的交点。Cornell Box 经典测试场景使用了 5 个平面（天花板、地板、左右墙、背墙）加若干长方体（可分解为 12 个三角形），即便如此简单的场景在不使用加速结构时，每条射线仍需执行数十次求交测试。

**阴影射线中的快速拒绝**：在判断某点是否在阴影中时，阴影射线只需知道光源方向上是否存在任意遮挡物，无需找到最近交点。此时可在三角形求交中增加"any-hit"提前退出逻辑，一旦发现 $0 < t < t_{\text{light}}$ 即立即返回，显著减少计算量。

**球形包围体的预筛选**：渲染器常在复杂网格外包裹一个轴对齐包围盒（AABB）或包围球，先执行廉价的球体/盒体求交测试。若未命中则跳过整个网格的三角形列表，这是 BVH 加速结构得以发挥作用的根本前提。

---

## 常见误区

**误区一：忽略 $t_{\min}$ 导致自相交（Self-Intersection）**  
从一个表面上发出反射或阴影射线时，起点 $\mathbf{o}$ 几乎就在物体表面上，浮点精度误差会使射线与起点所在三角形产生 $t \approx 10^{-7}$ 的虚假交点，错误地将物体判定为遮挡自身。正确做法是将 $t_{\min}$ 设为一个小量（通常取 $10^{-3}$ 至 $10^{-4}$，具体值依场景尺度调整），或者沿法线方向将起点偏移一小段距离。

**误区二：混淆单面（One-sided）与双面（Two-sided）三角形**  
Möller-Trumbore 默认通过分母 $(\mathbf{e}_1 \times \mathbf{e}_2) \cdot \mathbf{d}$ 的正负判断正面/背面，若分母为负则可选择剔除（Back-face Culling）。但在光线追踪中，玻璃、水体等透明物体的内外面都需要被击中，此时必须改为双面模式（取绝对值后求解），否则会出现光线"穿透"背面的错误渲染结果。

**误区三：将平面求交的平行判定阈值设置过大**  
有些实现将 $|\mathbf{n} \cdot \mathbf{d}| < \epsilon$ 中的 $\epsilon$ 设为 $10^{-2}$，导致几乎平行的射线（如掠射地面的光线）被错误丢弃，产生地面边缘缺失的渲染瑕疵。合理的阈值通常在 $10^{-6}$ 到 $10^{-8}$ 之间，应根据场景坐标系的单位量级决定。

---

## 知识关联

**前置概念**：光线生成模块负责确定每条射线的起点 $\mathbf{o}$ 和方向 $\mathbf{d}$（包括透视投影或正交投影的计算），光线求交则在此基础上接收该射线并执行几何测试，两者之间通过统一的射线参数结构体（`Ray` struct）传递数据。

**后续加速结构**：当场景三角形数量达到百万级时，逐一遍历所有三角形的暴力求交变得不可接受。BVH（层次包围体）将空间递归地划分为包围盒树，每层节点先做廉价的 AABB 求交测试，命中后才递
