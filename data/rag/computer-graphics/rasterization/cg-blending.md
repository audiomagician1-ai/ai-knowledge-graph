---
id: "cg-blending"
concept: "Alpha混合"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Alpha混合

## 概述

Alpha混合（Alpha Blending）是光栅化管线中用于模拟透明效果的技术，其核心思想是将新绘制的片元颜色与帧缓冲区中已有的颜色按比例叠加，而非直接覆盖。Alpha值表示不透明度，范围为 [0.0, 1.0]，其中 0.0 表示完全透明，1.0 表示完全不透明。该技术最早在20世纪80年代由 Porter 和 Duff 于1984年在论文《Compositing Digital Images》中正式系统化，提出了"over"操作等经典合成运算。

Alpha混合区别于简单的颜色覆盖：当玻璃、水体、烟雾等半透明物体需要同时显示自身颜色与背后物体时，只有按Alpha权重混合两个颜色才能得到正确结果。在游戏、UI渲染和特效系统中，几乎所有粒子、窗口、HUD元素都依赖Alpha混合实现。

## 核心原理

### 标准混合方程

OpenGL/Vulkan中最常用的混合方程为"over"操作，公式如下：

$$C_{out} = \alpha_s \cdot C_{src} + (1 - \alpha_s) \cdot C_{dst}$$

其中 $C_{src}$ 为源片元颜色（新绘制的透明物体），$C_{dst}$ 为目标颜色（已在帧缓冲区中的颜色），$\alpha_s$ 为源片元的Alpha值。这一公式表达了：透明物体透出的光 = 自身贡献 + 背景透过部分的贡献。

对于Alpha通道本身，叠加后的Alpha值可写为：

$$\alpha_{out} = \alpha_s + (1 - \alpha_s) \cdot \alpha_{dst}$$

在 OpenGL 中，通过 `glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)` 即可配置上述标准混合方式。除"over"之外，Porter-Duff 还定义了 in、out、atop、xor 等12种合成操作，分别对应不同的遮罩逻辑。

### 预乘Alpha（Premultiplied Alpha）

预乘Alpha是指将颜色通道的RGB值预先乘以Alpha，即存储形式变为 $(\alpha R, \alpha G, \alpha B, \alpha)$，而非原始的 $(R, G, B, \alpha)$。在预乘格式下，"over"操作简化为：

$$C_{out} = C_{src}^{pre} + (1 - \alpha_s) \cdot C_{dst}^{pre}$$

预乘Alpha的优势体现在：双线性插值时不会产生"黑边"（Dark Fringe）。未预乘时，透明像素边缘的RGB值往往是不确定的垃圾数据，插值到半透明像素时会被错误地混入计算，导致深色锯齿轮廓；预乘后透明区域的RGB全部为0，插值结果干净。大量纹理贴图工具（如 Unity、Photoshop 的"Generate Mip Maps"选项）默认输出预乘Alpha格式正是出于这一原因。

### 顺序无关透明（Order-Independent Transparency，OIT）

标准Alpha混合要求物体从后到前排序（即"画家算法"），否则混合结果出错。例如两个半透明面片 $A$（$\alpha=0.5$）在 $B$ 前面时，正确顺序为先画 $B$ 再画 $A$；若反转顺序，计算得到的颜色将完全不同。这一约束在实时渲染中代价高昂，三角形级别排序在复杂场景中甚至无解（环形互遮挡）。

为解决顺序依赖问题，业界发展出多种OIT技术：

- **深度剥离（Depth Peeling，2001年 Everitt 提出）**：多Pass渲染，每次剥离最前一层透明面，逐层从前到后合成，结果精确但Pass数量与层数成正比。
- **逐像素链表（Per-Pixel Linked Lists，2010年 DirectX 11 引入）**：利用UAV原子操作将所有片元按像素存入链表，一次全屏Pass完成排序与合成，显存占用较大。
- **加权混合OIT（Weighted Blended OIT，2013年 McGuire & Bavoil）**：使用权重函数近似估计透明度贡献，无需排序，一个Pass完成，精度略有损失但性能极优，被 Filament 等引擎广泛采用。

## 实际应用

**粒子系统**：烟雾、火焰粒子通常使用加法混合（Additive Blending），即 `glBlendFunc(GL_SRC_ALPHA, GL_ONE)`，使粒子叠加处更亮，模拟发光效果。与标准"over"操作不同，加法混合完全忽略目标颜色的遮挡关系，但粒子本身无需排序即可得到视觉合理结果。

**UI渲染**：文字抗锯齿（如 FreeType 输出的灰度位图）依赖Alpha混合将字形平滑地合成到背景上。若UI纹理以预乘Alpha格式存储，在 sRGB 帧缓冲区渲染时需额外注意线性空间与gamma空间的转换顺序，否则边缘颜色偏暗。

**水体与玻璃**：折射效果通常通过在透明物体的Alpha混合阶段采样一张扭曲后的背景纹理实现，此时 $C_{dst}$ 被替换为折射采样颜色，Alpha混合方程在形式上不变，但输入含有屏幕空间信息。

## 常见误区

**误区1：Alpha=0的像素无需处理**  
即使片元完全透明（$\alpha=0$），若启用了深度写入，该片元仍会写入深度缓冲区，导致后续不透明物体被错误遮挡。正确做法是对透明物体关闭深度写入（`glDepthMask(GL_FALSE)`），或在着色器中对 $\alpha < 0.01$ 的片元执行 `discard`。

**误区2：预乘Alpha与非预乘Alpha可以混用**  
若纹理以预乘格式存储，却在混合时使用 `GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA`（非预乘公式），会对Alpha进行二次乘法，导致颜色整体偏暗。预乘纹理的正确混合参数应为 `GL_ONE, GL_ONE_MINUS_SRC_ALPHA`，两者不可混用。

**误区3：画家算法对所有透明物体都有效**  
画家算法仅对凸体或无交叉的面片有效。当两个透明三角形在3D空间中互相穿插时，无论以何种整体顺序排列，都无法通过单一排序获得正确结果——此类场景必须使用OIT技术，或将几何体细分到不再交叉。

## 知识关联

Alpha混合直接依赖属性插值：片元的Alpha值来自顶点Alpha经过重心坐标插值后的结果，插值精度直接影响透明边缘的平滑程度。若顶点着色器输出了 `flat` 修饰的Alpha（不插值），则整个图元使用同一Alpha值，效果截然不同。

Alpha混合与多重采样抗锯齿（MSAA）存在交互问题：MSAA对每个子采样点独立执行覆盖测试，但Alpha混合通常在子采样点合并后的片元级别运行，这导致透明物体的锯齿比不透明物体更难消除。为此，OpenGL 提供了 `GL_SAMPLE_ALPHA_TO_COVERAGE` 模式，将Alpha值转换为覆盖掩码参与MSAA，是连接两个概念的标准桥梁技术。
