---
id: "cg-anisotropy"
concept: "各向异性"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 各向异性

## 概述

各向异性（Anisotropy）描述材质表面在不同方向上具有不同反射行为的光学性质。当光线照射到拉丝金属、头发、碳纤维或缎面织物时，沿着表面纹理方向与垂直纹理方向观察到的高光形状截然不同——各向同性材质产生圆形高光，而各向异性材质产生沿某一方向拉伸的椭圆形或条带状高光。这一现象的物理根源在于微表面的法线分布函数（NDF）在切线方向和副切线方向上具有不同的粗糙度参数。

这一概念的数学建模由James Blinn于1977年在各向同性Phong模型之后不久提出，但真正被引入PBR管线的各向异性模型由Burley（迪士尼）在2012年SIGGRAPH课程《Physically-Based Shading at Disney》中系统化，其中定义了`anisotropic`参数范围为[-1, 1]，并给出从单一粗糙度值推导出双轴粗糙度的具体公式。

在实时渲染和离线渲染中，各向异性对于准确还原金属加工件、布料和生物材质（如头发）至关重要。忽略各向异性会导致拉丝不锈钢的高光错误地呈圆形，而非沿拉丝方向的横向条带，严重损害材质的视觉真实感。

---

## 核心原理

### 各向异性NDF：双轴粗糙度

各向同性的GGX NDF仅使用单一粗糙度参数 $\alpha$，而各向异性版本引入两个独立参数 $\alpha_x$（沿切线方向 $\mathbf{t}$）和 $\alpha_y$（沿副切线方向 $\mathbf{b}$）。各向异性GGX法线分布函数的完整表达式为：

$$D(\mathbf{h}) = \frac{1}{\pi \alpha_x \alpha_y} \cdot \frac{1}{\left(\dfrac{(\mathbf{h}\cdot\mathbf{t})^2}{\alpha_x^2} + \dfrac{(\mathbf{h}\cdot\mathbf{b})^2}{\alpha_y^2} + (\mathbf{h}\cdot\mathbf{n})^2\right)^2}$$

其中 $\mathbf{h}$ 为半程向量，$\mathbf{t}$ 为切线，$\mathbf{b}$ 为副切线，$\mathbf{n}$ 为法线。当 $\alpha_x = \alpha_y$ 时，公式退化为标准各向同性GGX。$\alpha_x \gg \alpha_y$ 时，高光沿副切线方向被压缩为条带状。

### 迪士尼各向异性参数化

迪士尼模型使用直觉友好的`roughness`（$r$）和`anisotropic`（$k$，范围0到1）两个参数，通过以下公式转换为双轴粗糙度：

$$\alpha_x = r^2 \cdot \frac{1}{\sqrt{1-0.9k}}, \quad \alpha_y = r^2 \cdot \sqrt{1-0.9k}$$

系数0.9的选择保证了当 $k=1$ 时 $\alpha_y$ 不会降为零（避免数值奇点），同时使高光在 $k=1$ 时产生约10:1的长宽比。这是迪士尼材质文档中明确给出的具体数值，而非理论推导的结果。

### 切线空间参数化与切线贴图

各向异性的方向由表面的切线向量 $\mathbf{t}$ 确定。在实际使用中，通常有两种方式控制各向异性方向：其一是使用网格的UV展开切线（由顶点属性提供）；其二是使用专门的**各向异性方向贴图**（Anisotropy Direction Map），贴图的RG通道存储切线空间中的2D方向向量，经过 $[0,1] \to [-1,1]$ 的解码后，与顶点切线叉乘形成最终各向异性主轴。Substance PainterPainter和Filament引擎均采用这种双重机制。注意：切线方向与法线贴图所用的切线空间是同一套空间，因此切线贴图会受到UV接缝和切线一致性的约束，UV展开质量直接影响各向异性高光的连续性。

### 各向异性遮蔽-阴影函数

各向异性NDF必须配合对应的各向异性Smith遮蔽函数，否则能量守恒会被打破。各向异性Smith $G_1$ 的近似形式为：

$$G_1(\mathbf{v}) = \frac{2}{1 + \sqrt{1 + \frac{\alpha_x^2(\mathbf{v}\cdot\mathbf{t})^2 + \alpha_y^2(\mathbf{v}\cdot\mathbf{b})^2}{(\mathbf{v}\cdot\mathbf{n})^2}}}$$

完整遮蔽阴影项 $G = G_1(\mathbf{l}) \cdot G_1(\mathbf{v})$，两轴各自独立参与计算，确保掠射角度下的能量行为与各向同性GGX一致。

---

## 实际应用

**拉丝金属**：不锈钢厨具、铝制外壳的拉丝纹理方向平行于加工方向，$\alpha_x$（顺纹方向）远大于$\alpha_y$，高光呈现横跨高光区域的亮条。虚幻引擎5中Substrate材质的金属层直接暴露 `AnisotropyAngle` 输入，允许以弧度值旋转各向异性主轴。

**头发渲染**：Kajiya-Kay模型是针对头发光纤的各向异性专用模型（1989年），将圆柱形头发纤维的切线方向作为各向异性轴，产生"内高光"（primary specular）和"外高光"（secondary specular）两个错开的条带，这是GGX各向异性无法直接替代的场景。

**碳纤维与编织布料**：碳纤维的编织角度通常为±45°，需要在各向异性方向贴图中烘焙出编织方向的流场（flow map），由Houdini或Substance Designer的"方向流"节点生成，以实现编织纹路之间局部方向变化的各向异性高光。

---

## 常见误区

**误区一：认为各向异性只需修改粗糙度贴图**

部分初学者认为在粗糙度贴图中绘制方向性纹理即可模拟各向异性。实际上，粗糙度贴图只控制高光的整体大小，无法改变高光在两个垂直轴上的拉伸比例。真正的各向异性需要独立的 $\alpha_x$ 和 $\alpha_y$ 参数以及切线方向输入，仅凭单通道粗糙度无法实现椭圆形高光的方向控制。

**误区二：将各向异性角度旋转与法线贴图等同**

各向异性方向贴图工作在切线空间的2D平面内，旋转的是NDF的主轴，与法线贴图对 $\mathbf{n}$ 的扰动完全不同。将法线贴图的G通道误用为各向异性方向会导致高光方向与表面凸起方向错误绑定，在曲面上产生随观察角度变化的方向跳变。

**误区三：各向异性参数 $k=1$ 时会产生完全线性高光**

由于迪士尼公式中0.9系数的存在，$k=1$ 时 $\alpha_y$ 并非零，而是 $r^2 \cdot \sqrt{0.1} \approx 0.316 \cdot r^2$，高光仍有一定宽度，不会退化为一维线段。将 $k$ 暴力设为1并期待得到完美线条高光的做法忽略了这一数值设计，会导致参数与预期不符。

---

## 知识关联

各向异性NDF是对Cook-Torrance模型中各向同性GGX NDF的直接推广：Cook-Torrance框架定义了 $f_r = \frac{D \cdot F \cdot G}{4(\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v})}$，其中菲涅耳项 $F$ 和几何项 $G$ 的基本结构在各向异性情况下保持不变，仅 $D$ 和 $G$ 中的粗糙度由标量替换为双轴参数。这意味着掌握各向同性GGX的能量归一化条件（$\int_\Omega D(\mathbf{h})(\mathbf{n}\cdot\mathbf{h})d\omega_h = 1$）是理解各向异性版本何时成立的必要前提。在迪士尼材质体系中，各向异性与清漆层（Clearcoat）、布料层（Sheen）是并列的独立扩展项，清漆层固定使用各向同性GGX（$\alpha=0.25$），因此为物体同时添加清漆和各向异性时，两层使用不同NDF，需要分别计算再加权叠加。