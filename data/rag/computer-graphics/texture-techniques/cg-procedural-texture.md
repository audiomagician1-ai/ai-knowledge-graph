---
id: "cg-procedural-texture"
concept: "程序纹理"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 88.5
generation_method: "ai-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v2"
  - type: "academic"
    citation: "Perlin, K. (1985). An image synthesizer. ACM SIGGRAPH Computer Graphics, 19(3), 287–296."
  - type: "academic"
    citation: "Worley, S. (1996). A cellular texture basis function. Proceedings of SIGGRAPH 1996, 291–294."
  - type: "academic"
    citation: "Lagae, A., Lefebvre, S., Cook, R., DeRose, T., Drettakis, G., Ebert, D. S., ... & Zwicker, M. (2010). A survey of procedural noise functions. Computer Graphics Forum, 29(8), 2579–2600."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---



# 程序纹理

## 概述

程序纹理（Procedural Texture）是通过数学函数或算法在运行时动态计算像素颜色值的纹理生成技术，与传统位图纹理不同，它不依赖预先存储的图像文件，而是在着色器代码或CPU程序中实时求解函数 $f(x, y, z) \rightarrow \text{color}$，输入通常是三维空间坐标或纹理坐标，输出为颜色、法线或其他材质属性。

程序纹理的技术根源可追溯至1985年，Ken Perlin在为电影《TRON》（电子世界争霸战）开发视觉效果时提出了Perlin噪声算法（Perlin, 1985），该成果于1997年获得奥斯卡科学技术奖，是计算机图形学领域为数不多荣获该奖项的基础算法之一。同年，Ken Musgrave系统化地将分形几何（源自Mandelbrot 1982年的理论体系）与噪声函数结合，建立了程序纹理的理论框架，使得云层、山脉、大理石等自然材质的计算机模拟成为可能。

程序纹理在现代图形管线中的核心价值体现在三个可量化的优势上：**存储空间接近零**（一个复杂大理石纹理的着色器代码不超过2KB，而对应的4K位图需要约48MB，压缩比约为24000:1）；**支持任意分辨率无损缩放**，无论放大至8K还是缩小至64×64均无质量损失；以及**天然的三维连续性**——切割一个程序纹理木材球体，截面的纹理与外表面完全物理一致，这一特性是任何二维位图贴图技术无法复现的。

> **思考问题**：如果程序纹理在存储和分辨率上如此优越，为何现代游戏引擎仍大量使用位图纹理而非全面转向程序纹理？请从艺术家工作流程、着色器计算成本和内容多样性三个角度分析其局限性。

---

## 核心原理

### Perlin噪声的数学构造

Perlin噪声是绝大多数程序纹理的基础模块，其核心思想是在规则整数网格的每个格点上预先分配一个随机梯度向量，对空间中任意点 $P = (x, y, z)$，找到其所在单元的8个顶角格点，计算每个顶角梯度向量与该顶角到P的偏移向量的点积，再利用**三次平滑插值函数**对8个点积值进行三线性插值，最终得到 $[-1, 1]$ 范围内的连续浮点值。

Ken Perlin最初（1985年）使用的插值多项式为：

$$f(t) = 3t^2 - 2t^3 \quad \text{（smoothstep函数）}$$

但在2002年的改进版本（Improved Noise）中换用五次多项式：

$$f(t) = 6t^5 - 15t^4 + 10t^3$$

改进的原因在于，五次多项式满足 $f'(0) = f'(1) = 0$ 且 $f''(0) = f''(1) = 0$，即在 $t=0$ 和 $t=1$ 处的一阶和二阶导数均为零，消除了格点位置处法线场的不连续伪影。这对需要从程序噪声派生法线贴图的应用场景（如程序地形的光照计算）尤为关键——若使用原始smoothstep，法线贴图在格点边界处会出现肉眼可见的棱角状缝隙。

例如，给定二维坐标 $P = (1.3, 2.7)$，其所在单元的四个格点为 $(1,2), (2,2), (1,3), (2,3)$，分别查表得到梯度向量并计算点积后，以 $f(0.3)$ 和 $f(0.7)$ 作为插值权重进行双线性混合，最终输出约在 $[-0.7, 0.7]$ 范围内的单个浮点值（实际范围因梯度向量选取而略有差异）。

### 分形布朗运动（fBm）

单层Perlin噪声生成的纹理过于平滑，缺乏自然材质的多尺度细节。分形布朗运动（Fractional Brownian Motion，fBm）通过叠加多个不同频率和振幅的噪声层来模拟这种多尺度特征，其公式为：

$$\text{fBm}(P) = \sum_{i=0}^{N-1} \text{amplitude}^i \cdot \text{noise}\!\left(\text{frequency}^i \cdot P\right)$$

其中 $\text{frequency}$（又称**倍频程lacunarity**）通常取 $2.0$（每层频率翻倍），$\text{amplitude}$（又称**增益gain**）通常取 $0.5$（每层振幅减半）。这一参数组合在物理学上对应**赫斯特指数** $H = 0.5$，其分形维数约为 $D = 3 - H = 2.5$，与测量所得的许多自然地形的分形维数吻合。叠加层数 $N$ 一般取4至8层，层数越多细节越丰富，但计算量随 $N$ 线性增长。

例如，生成一段模拟云层的着色器代码中，取 $N=6$ 层fBm，前3层（低频）决定云团的整体形状和大块结构，后3层（高频）提供卷积边缘的细碎纹理。通过对时间参数做慢速偏移 $\text{noise}(\text{uv} + t \cdot 0.05)$ 即可实现云朵随风流动的动态效果，整个着色器无需任何贴图采样。

### 域扭曲（Domain Warping）

域扭曲是程序纹理中产生湍流流体、岩石纹理等有机形态的关键技术，由图形艺术家兼研究者Inigo Quilez在2002年前后系统整理并通过其个人网站（iquilezles.org）广泛推广。其核心思路是先用一个fBm函数计算坐标的偏移量，再用偏移后的坐标采样另一个fBm，形成自引用结构：

$$\mathbf{q} = \text{fBm}(P), \quad \mathbf{r} = \text{fBm}(P + \mathbf{q}), \quad \text{result} = \text{fBm}(P + \mathbf{r})$$

每级扭曲都会将原始规则网格的格点结构进一步打散，产生类似云朵卷积边缘或岩浆流动的视觉效果。一次域扭曲（只算 $\mathbf{q}$ 层）生成较柔和的变形；二次扭曲（加入 $\mathbf{r}$ 层）则产生明显的漩涡卷曲结构，视觉复杂度远超其代码复杂度所暗示的水平，是程序纹理领域"以极少代码生成极丰富视觉"这一特性的典型体现。

### Worley噪声（细胞噪声）

1996年Steven Worley在SIGGRAPH发表的细胞纹理基函数论文（Worley, 1996）提出了与Perlin噪声梯度机制完全不同的另一套体系。Worley噪声在空间中随机散布**特征点（Feature Points）**，对每个着色点计算其到最近特征点的距离 $F_1$ 和第二近特征点的距离 $F_2$，通过以下组合生成不同视觉效果：

| 组合方式 | 典型视觉效果 |
|----------|-------------|
| $F_1$ | 细胞填充，皮肤/泡沫纹理 |
| $F_2 - F_1$ | Voronoi边界线，龟裂地面 |
| $F_1 / F_2$ | 鳞片、鱼鳞状有机纹理 |
| $F_2$ | 较大圆斑，豹纹类花纹 |

Lagae等人（2010年）在对程序噪声函数的系统综述中，将Worley噪声与Perlin噪声并列为现代程序纹理技术的两大基础支柱，并指出两者在频谱特性上互补：Perlin噪声的功率谱近似带限高斯型，适合模拟连续平滑的自然材质；Worley噪声的功率谱则在低频端集中能量，更适合具有明确边界结构的生物纹理（Lagae et al., 2010）。

---

## 关键公式汇总

程序纹理中最常用的核心公式可归纳如下：

**Perlin噪声插值核函数（改进版，2002）：**
$$f(t) = 6t^5 - 15t^4 + 10t^3, \quad t \in [0, 1]$$

**分形布朗运动（fBm）：**
$$\text{fBm}(P) = \sum_{i=0}^{N-1} g^i \cdot \text{noise}(l^i \cdot P)$$
其中 $l$ 为倍频程（lacunarity，典型值2.0），$g$ 为增益（gain，典型值0.5）。

**大理石程序纹理核心表达式：**
$$c = \sin\!\left(P_x \cdot \omega + \text{fBm}(P) \cdot A\right)$$
其中 $\omega$ 控制条纹密度（典型值5.0），$A$ 控制扰动强度（典型值8.0）；输出 $c \in [-1, 1]$ 经颜色渐变表映射至最终颜色。

**带限噪声截断频率（基于屏幕空间微分）：**
$$N_{\max} = \left\lfloor \log_l \!\left(\frac{1}{\|\nabla_{\text{screen}} P\|}\right) \right\rfloor$$
即当第 $i$ 层噪声频率超过像素可分辨的奈奎斯特频率时，动态截断fBm的叠加层数以防止走样。

---

## 实际应用案例

**实时游戏着色器**：Unreal Engine 5的Lumen全局光照系统和Unity HDRP中，均内置了基于fBm的程序云层着色器。典型实现叠加3至5层噪声，通过对时间参数做偏移 $\text{noise}(\text{uv} + t \cdot 0.1)$ 实现云朵流动，整个着色器代码约50行GLSL/HLSL，无需任何纹理采样带宽，在移动端GPU上单帧开销约0.3ms（1080p分辨率）。

**大理石纹理合成**：经典大理石程序纹理使用公式 $c = \sin(P_x \cdot 5.0 + \text{fBm}(P) \cdot 8.0)$，将fBm结果作为正弦函数的相位扰动，产生不规则弯曲条纹；再通过颜色渐变映射（Color Ramp）将 $[-1, 1]$ 值域映射到白色—灰色—黑色的大理石色带。调整 $P_x$ 系数可从大理石切换至木纹（取值约3.0）或玛瑙（取值约12.0）等不同矿石纹理。

**地形高度图生成**：程序地形生成工具（如World Machine 4.0、Houdini 20