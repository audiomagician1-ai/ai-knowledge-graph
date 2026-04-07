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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

SDF（Signed Distance Field，有符号距离场）着色器是一种利用距离函数在片元着色器中实时生成或采样几何形状的技术。与传统基于多边形的渲染不同，SDF着色器通过在每个像素位置计算"距离最近表面的有符号距离"来决定该像素的颜色与透明度——距离为负表示像素在形状内部，为正表示在外部，为零则精确落在边界上。这一特性使得SDF天然支持任意分辨率的锐利边缘渲染，完全消除传统位图放大时的模糊问题。

SDF技术最早由Chris Green于2007年在SIGGRAPH上发表的论文《Improved Alpha-Tested Magnification for Vector Textures and Special Effects》中引入实时图形领域。他提出将字形预先烘焙成低分辨率的SDF纹理（通常64×64像素），在着色器中通过简单的阈值判断即可还原出高质量、无锯齿的字体边缘，即便将该纹理放大8倍仍保持清晰轮廓，这一方案被后来的Unity、Unreal Engine等引擎广泛采用为默认文字渲染方案。

SDF着色器在技术美术领域的价值体现在三个独立方向：UI矢量图形的GPU端实时绘制（无需SVG光栅化CPU开销）、特效中的程序化形状生成与融合、以及三维体积渲染（如云、烟、皮肤次表面散射）中的光线行进（Ray Marching）。掌握SDF着色器意味着能够用极少的顶点数据驱动视觉上复杂的几何效果。

---

## 核心原理

### 1. 有符号距离函数的数学定义

对于场景中的一个形状 $\Omega$，其SDF定义为：

$$
d(\mathbf{p}) = \begin{cases} -\min_{\mathbf{q} \in \partial\Omega} \|\mathbf{p} - \mathbf{q}\| & \mathbf{p} \in \Omega \\ +\min_{\mathbf{q} \in \partial\Omega} \|\mathbf{p} - \mathbf{q}\| & \mathbf{p} \notin \Omega \end{cases}
$$

其中 $\mathbf{p}$ 是当前像素在UV空间中的坐标，$\partial\Omega$ 是形状边界，$d(\mathbf{p})$ 的零等值线即为形状轮廓。在GLSL/HLSL着色器中，圆形的SDF为 `length(uv - center) - radius`，矩形则使用 `length(max(abs(uv - center) - halfSize, 0.0))` 计算角落的精确距离。这些公式具有解析形式，在GPU上每帧计算几乎没有额外开销。

### 2. 抗锯齿与软边缘处理

原始SDF阈值判断（`d < 0.0` 为不透明）会产生硬边，实际应用中使用 `smoothstep` 函数在距离零点附近进行线性混合：

```glsl
float alpha = smoothstep(edge + aaWidth, edge - aaWidth, dist);
```

`aaWidth` 通常设置为 `fwidth(dist) * 0.5`，其中 `fwidth` 返回相邻像素间的距离函数变化量，这样抗锯齿宽度会自动随缩放比例调整，永远保持1像素宽的平滑过渡，无论UI元素被缩放到多大尺寸。通过修改 `edge` 参数还可以在不增加任何纹理采样的情况下为形状添加等距描边（`edge = 0.03`）或内发光效果。

### 3. 形状运算与平滑融合（Smooth Blending）

SDF最强大的特性之一是支持布尔运算的距离场类比：
- **并集**：`min(d1, d2)`
- **交集**：`max(d1, d2)`
- **差集**：`max(d1, -d2)`

更进一步，平滑融合函数（Smooth Union）可以让两个形状在接近时自然融合，公式由Inigo Quilez提出：

```glsl
float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5*(b-a)/k, 0.0, 1.0);
    return mix(b, a, h) - k*h*(1.0-h);
}
```

参数 `k` 控制融合半径，当两个圆形SDF的 `k=0.3` 时，它们在距离0.3个单位内会表现出类似液体水滴合并的视觉效果，这是传统多边形网格极难实现的有机形态。

### 4. 三维Ray Marching中的SDF应用

在体积渲染着色器中，Ray Marching算法从相机出发沿视线方向逐步前进，每步步长等于当前点到最近表面的SDF值（也称Sphere Tracing）。核心循环如下：

```glsl
float t = 0.0;
for(int i = 0; i < 64; i++) {
    vec3 p = rayOrigin + t * rayDir;
    float d = sceneSDF(p); // 场景中所有物体SDF的min
    if(d < 0.001) break;   // 命中阈值
    t += d;                 // 安全步进，不会穿透表面
    if(t > 100.0) break;    // 最大步进距离
}
```

这一算法的理论保证是：当 $d(\mathbf{p})$ 是真正的有符号距离场时，以 $d$ 为步长前进永远不会越过任何表面，最多需要约64到128次迭代即可渲染出包含阴影、环境光遮蔽（AO）的完整三维场景。

---

## 实际应用

**UI圆角矩形**：移动端UI框架（如Flutter的GLSL后端）大量使用矩形SDF代替九宫格拉伸方案。一个半径为 `r` 的圆角矩形SDF为 `length(max(abs(p)-halfSize+r, 0.0)) - r`，单次着色器调用即可渲染任意尺寸的圆角矩形，且描边宽度与圆角半径均可在运行时动态调整，无需重新生成纹理资产。

**特效融合流体**：在游戏特效中，多个球体SDF通过 `smin` 组合后提交给 `smoothstep` 着色，可模拟岩浆灯、史莱姆、血液飞溅等有机流体形态。《文明6》的领土边界特效和《英雄联盟》的部分技能指示器均采用了类似的二维SDF融合方案。

**TextMesh Pro字体渲染**：Unity中的TextMesh Pro将字体字形烘焙为512×512的SDF纹理（每个字形占约32×32像素区域），着色器通过采样该纹理并应用 `smoothstep` 阈值实现在任意分辨率下的清晰渲染，同时支持描边（Outline）、阴影（Shadow Softness）、倒角（Bevel）等多种纯着色器后处理效果，全部基于SDF的距离梯度信息实现。

---

## 常见误区

**误区一：SDF纹理可以表示任意细节**。SDF纹理的分辨率决定了可表示的最小特征尺寸——一张64×64的字形SDF纹理，其内部可以精确表示的最细线条宽度约为字形边界框的1/8。过细的笔画（如中文汉字的细横竖结构）在低分辨率SDF中会发生距离值重叠，导致放大后细节丢失。TextMesh Pro因此对复杂中文字形推荐使用至少64×64像素的独立字形区域，而非默认的32×32。

**误区二：所有形状的SDF都可以解析计算**。圆形、矩形、胶囊体、多边形等规则形状有精确的解析SDF公式，但任意曲线（如贝塞尔曲线）的精确SDF需要求解高次多项式，GPU上代价过高。实际方案是将贝塞尔曲线离散为折线段后逐段取最小距离，或将复杂形状预烘焙为SDF纹理供着色器采样，而非实时计算。

**误区三：Ray Marching的步数固定就足够精确**。当相机极度靠近表面时，SDF值趋近于零，每步前进量极小，固定64步可能不足以追踪完整光线路径，导致接触区域出现噪点。正确做法是在循环中同时检查 `d < 0.001`（命中）和 `t > maxDist`（未命中）两个终止条件，并对掠射角度场景适当增加最大迭代次数至128或256步。

---

## 知识关联

SDF着色器以**噪声函数**作为前置知识，体现在两个具体结合点：其一，将FBM（分形布朗运动）噪声叠加到SDF距离值上（`dist += fbm(uv) * 0.1`）可使形状边界产生有机的扰动效果，常用于火焰、云朵等自然边界特效；其二，噪声函数本身可以作为一种隐式曲面定义方式，通过将三维噪声值作为近似SDF提交给Ray Marching循环，以约128步迭代即可渲染出云体积、地形等噪声驱动的体积形态，但需注意噪声函数不满足真正SDF的Lipschitz条件（梯度模长不恒为1），步进时需额外乘以0.5~0.8的安全系数以避免