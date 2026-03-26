---
id: "cg-sdf-tracing"
concept: "SDF光线步进"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# SDF光线步进

## 概述

SDF光线步进（Sphere Tracing）是一种利用有符号距离场（Signed Distance Field，SDF）进行光线与隐式曲面求交的算法，由John C. Hart于1996年在论文 *Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces* 中正式提出。与传统光线追踪中解析求交不同，Sphere Tracing不需要代数方程的显式解，而是通过反复查询场景SDF函数来逼近交点位置。

有符号距离场是一个标量函数 `f(p)`，对空间中任意点 `p` 返回该点到场景中最近表面的有符号距离：曲面外部返回正值，内部返回负值，恰好在表面上返回零。正是这个"到最近表面的距离"的语义，使得Sphere Tracing得以安全、高效地推进光线，而不必担心步进过头穿透表面。

Sphere Tracing在实时图形领域（尤其是Shadertoy社区）和光线行进渲染器中极为流行，因为只需一个SDF函数便可定义任意复杂的隐式几何体，并天然支持平滑融合（smooth union）等操作，这是多边形网格难以实现的。

---

## 核心原理

### 安全步长的几何意义

Sphere Tracing的核心思想可以用一句话表达：**当前点处的SDF值即为"安全步长"**。在位置 `p` 处，若 `f(p) = d`，则以 `p` 为球心、`d` 为半径的球体内部不包含任何表面。因此，沿任意方向（包括光线方向）移动最多 `d` 的距离，都不会穿过表面。算法利用这一保证，每步精确地迈出尽可能大的安全步长。

算法的迭代公式为：

```
t_{n+1} = t_n + f(ro + t_n * rd)
```

其中 `ro` 为光线起点（ray origin），`rd` 为单位化的光线方向（ray direction），`t_n` 为第 `n` 步时沿光线的累积距离。当 `f(ro + t_n * rd) < ε`（通常 ε 取 `0.001` 到 `0.0001`）时，认为光线已到达表面，求交成功。

### 收敛条件与终止判断

Sphere Tracing需要两个终止条件：

1. **命中**：`f(p) < ε`，其中 ε 是用户定义的表面厚度阈值。
2. **未命中**：累积步长 `t` 超过最大场景深度（如 `t > 100.0`），或迭代次数超过最大步数限制（常用64至256步）。

迭代步数上限是性能关键。对于光滑的简单SDF，通常64步即可收敛；而细密几何或掠射角（grazing angle）入射时，由于每步SDF值趋近于零（光线几乎与表面相切），步数可能急剧增加，这是Sphere Tracing最主要的性能瓶颈。

### 法线的计算

求交成功后，表面法线可以通过对SDF函数进行数值梯度估计（gradient estimation）得到。最常用的方法是中心差分：

```
n = normalize(vec3(
    f(p + vec3(ε,0,0)) - f(p - vec3(ε,0,0)),
    f(p + vec3(0,ε,0)) - f(p - vec3(0,ε,0)),
    f(p + vec3(0,0,ε)) - f(p - vec3(0,0,ε))
))
```

这需要对SDF额外调用6次，计算代价固定且与几何复杂度无关。另有四面体差分方法（Tetrahedron method，由Inigo Quilez推广）仅需4次SDF调用，且数值稳定性相当。

### SDF的构造与组合

Sphere Tracing的灵活性来自SDF的可组合性。常见基元包括：
- **球体**：`f(p) = length(p - center) - radius`
- **无限平面**：`f(p) = dot(p, normal) + d`
- **长方体**：通过分量最大值构造，形式为 `length(max(abs(p-b)-b, 0.0))`

组合操作包括并集（`min(f1,f2)`）、交集（`max(f1,f2)`）、差集（`max(f1,-f2)`），以及平滑并集（smooth union），其公式为：

```
smin(a, b, k) = -log(exp(-k*a) + exp(-k*b)) / k
```

其中 `k` 控制融合半径，`k` 越大融合越尖锐。

---

## 实际应用

**Shadertoy实时渲染**：Shadertoy平台上大量视觉效果直接基于Sphere Tracing，典型作品如Inigo Quilez的"Slisesix"（2008年）在单个片段着色器中渲染出带阴影、环境光遮蔽的完整三维场景。开发者只需在GPU上并行执行每像素的Sphere Tracing循环即可。

**软阴影（Soft Shadow）**：Sphere Tracing天然支持廉价的软阴影近似。在向光源行进的阴影光线上，记录每步 `f(p)/t` 的最小值（称为"半影因子"），该值趋近于0表示被遮挡，趋近于1表示完全照亮，中间值产生平滑过渡的软阴影，整体代价仅为额外一次光线步进。

**环境光遮蔽（AO）**：由于SDF直接编码了到表面的距离，可以在表面法线方向采样少量（通常5步）固定步长处的SDF值，与期望距离之差即反映遮蔽程度，无需蒙特卡洛采样。

**程序化地形与体积云**：将高度场或密度场包装成SDF后，Sphere Tracing可以渲染地形侵蚀、云层等体积效果，也可与传统光栅化管线混合使用（先光栅化不透明物体，再对深度缓冲可见区域执行光线步进）。

---

## 常见误区

**误区一：SDF必须精确，近似SDF会导致算法失败**

实际上，Sphere Tracing要求的是SDF满足"Lipschitz常数 ≤ 1"的条件（即1-Lipschitz函数），而不要求绝对精确。只要函数值不超过真实距离（即"under-estimated SDF"），算法仍然安全。许多复杂操作（如空间扭曲 `twist`、弯曲 `bend`）会破坏精确距离性质，此时通常通过除以已知的Lipschitz常数进行修正，牺牲一定步进效率但不会穿透表面。

**误区二：步数越多精度越高，应尽量增大最大步数**

最大步数增加并不等比例提升精度，步进精度主要由收敛阈值 ε 决定。增大步数上限主要是为了处理掠射角或深度较大场景中步进速度缓慢的情况。在实践中，128步搭配合理的ε（如 `0.001 * t`，随深度自适应的相对误差）通常优于512步搭配固定ε，且帧率更高。

**误区三：Sphere Tracing等同于Ray Marching**

Ray Marching泛指一切沿光线逐步前进的算法，包括固定步长推进（常用于体积渲染）。Sphere Tracing是Ray Marching的一种特殊形式，其独特之处在于步长由SDF自适应决定，而非固定值。固定步长Ray Marching存在漏洞（可能穿透薄表面），Sphere Tracing则在1-Lipschitz条件下保证不漏洞。

---

## 知识关联

**前置概念——光线求交**：传统光线求交（如光线与三角形的Möller–Trumbore算法）给出了解析精确解，而Sphere Tracing是其在隐式曲面场景下的数值替代方案。理解光线参数化表示 `p = ro + t*rd` 是阅读Sphere Tracing代码的直接前提，两者共享相同的光线数据结构，但求交策略完全不同——前者依赖几何图元的代数性质，后者依赖场景整体的距离场信息。

**隐式曲面建模**：Sphere Tracing是隐式建模工作流的渲染端。SDF的设计（如Inigo Quilez整理的数十种基元SDF公式库）与Sphere Tracing算法解耦，两者共同构成完整的隐式建模渲染管线。掌握Sphere Tracing后，自然引出对更复杂SDF表示（如神经SDF、带符号距离场纹理SDFT）的探索需求。