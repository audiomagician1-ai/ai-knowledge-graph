---
id: "ta-sdf-shader"
concept: "SDF着色器"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
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

# SDF着色器

## 概述

SDF着色器（Signed Distance Field Shader）是一类以**有符号距离场**为核心数据结构的着色程序。所谓有符号距离场，指的是空间中每个点存储一个标量值：该值的**绝对值**表示该点到最近几何边界的距离，**正负号**表示该点在几何体内部（负值）还是外部（正值）。在片元着色器中，只需对这个标量执行 `SDF(p) < 0` 或 `SDF(p) < threshold` 的判断，便能以纯数学方式渲染出任意形状，无需三角形网格。

SDF概念最早由Inigo Quilez（网名iq）于2008年前后在demoscene社区中系统化整理并公开，其网站shadertoy.com上的系列教程成为业界标准参考。2015年Valve公司在发表的论文《Improved Alpha-Tested Magnification for Vector Textures and Special Effects》中将SDF预烘焙进纹理，用于字体渲染，彻底解决了低分辨率纹理放大后边缘锯齿的问题——这是SDF在游戏工业界大规模普及的起点。

SDF着色器的重要性体现在三个具体场景：无极缩放的UI矢量图形（只需8×8的SDF纹理即可渲染出清晰的圆形图标）、基于光线步进的体积雾与云渲染、以及实时特效中的软边光晕与描边。这三类需求在传统网格方案中要么消耗大量顶点，要么依赖多张贴图叠加，而SDF着色器用一个函数值即可统一处理。

---

## 核心原理

### 基本SDF函数与符号规则

圆形SDF是最基础的形式，其数学表达式为：

```
float sdCircle(vec2 p, float r) {
    return length(p) - r;
}
```

其中 `p` 是当前片元相对于圆心的坐标，`r` 是圆的半径。返回值 < 0 表示在圆内，= 0 表示在圆边界上，> 0 表示在圆外。矩形SDF则利用分量式最大值计算：

```
float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}
```

这条公式的关键在于 `max(d, 0.0)` 处理外部距离，`min(max(d.x,d.y), 0.0)` 处理内部距离，两段拼接后保证了全域连续且符号正确。

### 抗锯齿与边缘软化

SDF着色器的抗锯齿不依赖MSAA，而是使用 `smoothstep` 在距离场的0值附近做插值。典型写法：

```
float alpha = smoothstep(0.5 + softness, 0.5 - softness, dist);
```

其中 `softness` 取值通常为 `0.02 ~ 0.1`，对应屏幕空间约1~3像素的过渡带。更精确的方案是用 `fwidth(dist)` 自动计算当前像素对应的距离场变化量，从而实现分辨率自适应的抗锯齿：

```
float fw = fwidth(dist);
float alpha = smoothstep(fw, -fw, dist);
```

这一技术使得同一张64×64的SDF纹理在1080p和4K屏幕上都能呈现锐利边缘。

### 布尔运算与形状组合

SDF的最强大特性是可以用简单数学操作实现形状合并、相交、相减：

- **并集（Union）**：`min(sdfA, sdfB)` — 取距离最小值
- **交集（Intersection）**：`max(sdfA, sdfB)` — 取距离最大值
- **差集（Subtraction）**：`max(sdfA, -sdfB)` — 从A中挖去B

平滑融合（Smooth Union）是特效中常用的进阶操作，由Inigo Quilez给出的公式为：

```
float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0) / k;
    return min(a, b) - h * h * k * 0.25;
}
```

参数 `k` 控制融合半径，当 `k=0` 时退化为普通 `min`。这个函数使两个圆在接触时自然"熔合"，常用于粘液特效和变形动画。

### 光线步进与体积渲染

三维SDF着色器通过**Sphere Marching（球形步进）**实现无网格体积渲染。算法步骤如下：从相机发出射线，每步前进距离等于当前点的SDF值（即安全步距），当SDF < 0.001时判定命中表面。典型实现允许最多**64~128步**，超过步数上限视为未命中。

法线计算无需存储任何几何信息，用有限差分数值梯度近似：

```
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.0001, 0.0);
    return normalize(vec3(
        sdf3D(p + e.xyy) - sdf3D(p - e.xyy),
        sdf3D(p + e.yxy) - sdf3D(p - e.yxy),
        sdf3D(p + e.yyx) - sdf3D(p - e.yyx)
    ));
}
```

---

## 实际应用

**UI描边与发光特效**：在Unity的UI系统中，将字体图集替换为SDF纹理（Unity Text Mesh Pro正是基于此原理），可在单次DrawCall中同时渲染描边、投影和外发光——这三种效果只需对同一SDF值做三次不同阈值的采样，无需额外Pass。

**实时水墨/溶解特效**：将噪声函数（如Perlin噪声）叠加到SDF值上，产生不规则边缘，公式为 `dist = sdCircle(p, r) + noise(p * frequency) * amplitude`。调整 `amplitude` 参数从0到1即可驱动圆形向噪声形状溶解的动画，常用于技能消散、燃烧边缘特效。

**软阴影近似**：在光线步进过程中记录每步的 `h = sdf(pos) / t`（t为已行进距离），用 `min` 累积得到软阴影因子 `shadow = min(shadow, k * h)`，`k` 通常取8~32，数值越小阴影越软。这一方法由Inigo Quilez在2010年提出，计算成本仅为额外的一次光线步进循环。

---

## 常见误区

**误区1：SDF值可以直接当作Alpha使用**。直接将SDF返回值作为透明度会得到线性渐变而非清晰边缘。正确做法必须经过 `smoothstep` 或阈值比较才能还原出原始形状的边界，否则渲染结果看起来像一个灰色渐变圆而非填充圆。

**误区2：形状组合后SDF仍是精确距离场**。`min(sdfA, sdfB)` 的结果在两个形状交界处附近**不再是真正的欧氏距离场**，只是近似值。在需要精确法线或精确软阴影的场景下，这种误差会导致法线朝向错误和阴影闪烁。解决方案是在交界区域额外执行梯度重归一化（Gradient Renormalization），或使用 `smin` 代替 `min` 以平滑过渡区。

**误区3：SDF着色器一定比网格渲染性能好**。带64步光线步进的三维SDF着色器在复杂场景下每帧GPU耗时可超过5ms，远高于同等外观的烘焙网格方案。SDF的优势在于**内存占用极低**和**无限分辨率缩放**，而非计算效率。在移动端使用体积SDF前必须先做步数限制和早退优化。

---

## 知识关联

SDF着色器以**噪声函数**为直接前置知识：Perlin噪声、FBM分形噪声的输出值可以直接叠加到距离场上，产生有机边缘；没有噪声函数知识，SDF特效只能生成硬边几何图案，无法实现自然有机形态。具体来说，FBM噪声叠加SDF是实现云层和火焰体积效果的标准管线——噪声提供密度扰动，SDF提供基础体积边界，两者缺一不可。

在实际Shader开发工作流中，SDF着色器技术向上支撑**程序化材质**和**实时光照模型**的实现：掌握三维SDF法线计算后，可以将其接入PBR光照方程；掌握软阴影技术后，可以扩展到全局光照近似（Ambient Occlusion的SDF近似版本，即将步进过程中最小SDF值累积为遮蔽因子）。SDF体积渲染也是理解**光线追踪**管线的重要过渡，两者都基于从相机发射射线并检测命中的核心思路，但光线追踪使用BVH加速结构而SDF使用距离场导向步进。