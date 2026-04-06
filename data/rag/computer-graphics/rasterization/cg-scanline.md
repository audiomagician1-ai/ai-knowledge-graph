---
id: "cg-scanline"
concept: "扫描线转换"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 2
is_milestone: false
tags: ["算法"]

# Quality Metadata (Schema v2)
content_version: 7
quality_tier: "A"
quality_score: 82.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "academic"
    author: "Foley, J.D., van Dam, A., Feiner, S.K., & Hughes, J.F."
    year: 1990
    title: "Computer Graphics: Principles and Practice (2nd ed.)"
    publisher: "Addison-Wesley"
  - type: "academic"
    author: "Sutherland, I.E., Sproull, R.F., & Schumacker, R.A."
    year: 1974
    title: "A Characterization of Ten Hidden-Surface Algorithms"
    journal: "ACM Computing Surveys"
    volume: "6(1)"
    pages: "1–55"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---

# 扫描线转换

## 概述

扫描线转换（Scanline Conversion）是光栅化阶段的核心算法，其任务是将几何图元（通常是三角形）转化为屏幕上的像素集合。算法的基本思路是：对多边形所覆盖的每一条水平扫描线（$y = c$，$c$ 为整数常数），计算出该扫描线与多边形左右边界的交点，然后填充两交点之间所有整数 $x$ 坐标对应的像素。这一"逐行扫描、左右填充"的策略使得算法具有良好的内存访问局部性，与显示设备的行扫描刷新方式天然契合。

扫描线填充算法的理论基础可追溯至1967年Ivan Sutherland等人在哈佛大学开展的早期光栅图形研究。1974年，Sutherland、Sproull与Schumacker在《ACM Computing Surveys》第6卷第1期发表了对十种隐面消除算法的系统性综述，其中对扫描线算法的分析至今仍是该领域的经典参考文献（Sutherland et al., 1974）。1970年代随着帧缓冲显示器的普及，该算法获得广泛工程应用。相比逐像素的点测试（判断像素中心是否在三角形内），扫描线算法在CPU端的传统实现中效率更高，因为它避免了对三角形包围盒内大量非覆盖像素的冗余计算。现代GPU虽采用并行的边函数（edge function）测试替代串行扫描，但理解扫描线算法仍是掌握光栅化工作原理的关键路径。

## 核心公式与数学基础

扫描线算法的效率核心在于**增量式 $x$ 坐标更新**，而非每行重新求解直线方程。对于连接顶点 $(x_1, y_1)$ 与 $(x_2, y_2)$ 的多边形边，其斜率倒数（即每推进一行时 $x$ 的增量）定义为：

$$\Delta x = \frac{x_2 - x_1}{y_2 - y_1}$$

当扫描线从 $y$ 推进到 $y+1$ 时，新的交点 $x$ 坐标直接由递推公式给出：

$$x_{new} = x_{old} + \Delta x$$

这一递推将每行的计算量从一次浮点除法降低为一次浮点加法。对于一条跨越 $h$ 行的多边形边，整体节省了 $h - 1$ 次除法运算。在处理分辨率为 $1920 \times 1080$ 的帧缓冲时，一个覆盖500行的大型三角形可节约约499次除法，在CPU软件光栅化器中这一优化效果显著。

填充判定的奇偶规则可形式化表达为：对于平面上一点 $P$，从 $P$ 出发沿任意方向作射线 $R$，设 $R$ 与多边形边界的交叉次数为 $N$，则：

$$\text{填充}(P) = \begin{cases} \text{填充} & \text{若 } N \bmod 2 = 1 \\ \text{不填充} & \text{若 } N \bmod 2 = 0 \end{cases}$$

## 活性边表（AET）与边表（ET）数据结构

扫描线算法的高效实现依赖两个核心数据结构。**边表（Edge Table，ET）**按多边形各边的最小 $y$ 值分桶存储，每条边的条目包含四个字段：`y_max`（边的最大 $y$ 坐标）、`x_at_ymin`（该边在 $y_{min}$ 处的 $x$ 值）、`Δx`（斜率倒数，即 $\Delta x = (x_2 - x_1)/(y_2 - y_1)$）、以及用于处理浮点精度的分子分母整数对（在定点实现中）。**活性边表（Active Edge Table，AET）**则在当前扫描线处维护所有与该扫描线相交的边，按 $x$ 坐标升序排列，通常以链表实现以支持 $O(1)$ 的插入与删除。

当扫描线从 $y_{min}$ 向 $y_{max}$ 逐行推进时，算法执行三步操作：①将 ET 中 $y$ 值等于当前扫描线的边插入 AET；②从 AET 中移除 `y_max` 等于当前 $y$ 的边（边已离开视野）；③对 AET 中的每对相邻边之间的像素区间执行填充，然后将所有活性边的 $x$ 值更新为 $x \mathrel{+}= \Delta x$。这一增量更新策略使得每行扫描的计算量仅为 $O(\text{活性边数})$，而非重新计算每条交点。整体算法的时间复杂度为 $O(n \log n + \text{总填充像素数})$，其中 $n$ 为多边形顶点数，$\log n$ 来自初始边表排序。

例如，考虑一个屏幕空间三角形，顶点坐标为 $A=(2, 1)$、$B=(8, 5)$、$C=(1, 5)$（$y$ 轴向下）。边 $AB$ 的 $\Delta x = (8-2)/(5-1) = 1.5$，边 $AC$ 的 $\Delta x = (1-2)/(5-1) = -0.25$。当扫描线从 $y=1$ 推进至 $y=5$ 时，左右边界的 $x$ 值每行分别递增 $-0.25$ 和 $1.5$，无需重复求解直线方程。

## 交点的奇偶规则与非零绕数规则

对于自相交多边形，填充哪些区间需要规则约定。**奇偶规则（Even-Odd Rule）**规定：从任意点向外引射线，若与多边形边界的交叉次数为奇数则填充，偶数则不填充。**非零绕数规则（Non-Zero Winding Rule）**则额外考虑边的方向：向左穿越边计 $+1$，向右穿越边计 $-1$，结果非零则填充。SVG 1.1规范（W3C, 2011）和 PostScript Level 2 均使用非零绕数规则作为默认填充规则，而 CSS 的 `fill-rule` 属性允许在 `nonzero` 与 `evenodd` 之间切换。两种规则在简单（非自交）多边形上产生相同结果，差异仅在复杂自交路径中显现。

值得思考的问题是：**对于一个"五角星"形路径，奇偶规则与非零绕数规则分别会填充哪些区域？为什么中心区域在两种规则下的填充结果不同？** 理解这一问题有助于深入掌握填充规则的实际含义。

## 斜率增量与水平边的特殊处理

$\Delta x = 1/\text{slope}$ 是扫描线算法的核心递推公式，其中 $\text{slope} = (y_2 - y_1)/(x_2 - x_1)$。水平边（$y_1 = y_2$，斜率为零，$\Delta x$ 无穷大）不进入边表，因为水平边不会与水平扫描线产生有意义的单点交叉，其贡献已由相邻两条非水平边的端点隐含处理。对于顶点恰好落在扫描线上的情况，惯例规定：若顶点是两条边的局部最低点（valley 顶点），则计入两次交点；若是局部最高点（peak 顶点），则不计入，从而保证填充的正确性和无重叠性。这一"下闭上开"约定与光栅化的填充惯例（left-inclusive, top-exclusive 规则）一致，也是 Direct3D 光栅化规则（Rasterization Rules, Microsoft DirectX 11 文档）的基础。

在定点数实现（如嵌入式渲染器或早期游戏引擎）中，$\Delta x$ 通常以分数形式 $p/q$ 存储（其中 $p = x_2 - x_1$，$q = y_2 - y_1$），并维护一个余数累加器，每行将余数加 $p$，当余数 $\geq q$ 时令 $x$ 整数部分加 1 并余数减 $q$，从而完全避免浮点运算，实现与 Bresenham 直线算法相同的整数误差累积思路（Foley et al., 1990）。

## 实际应用

**软件光栅化渲染器**：1996年发布的 Quake 引擎由 id Software 开发，其 CPU 端软件光栅化器在 Intel Pentium 处理器上实现了扫描线光栅化。该引擎按多边形的 `y_min` 排序后逐行扫描，同时在 $x$ 方向上插值纹理坐标（$u/v$）和深度值（$z$），实现透视校正纹理映射。在当时主流的 $320 \times 200$ 分辨率下，每帧需处理约 64,000 个像素的扫描线填充，整体帧率可达 30 FPS 以上。

**字体渲染**：FreeType 2 库（首发于2000年）在栅格化 TrueType/OpenType 轮廓时使用扫描线填充，处理二次或三次贝塞尔曲线构成的字形边界。FreeType 的扫描线转换器（`raster` 模块）先将曲线细分为短直线段（细分精度为1/64像素，即26.6定点格式），再用 AET 填充，最终产生8位灰度（0–255）的抗锯齿覆盖值。FreeType 在 Android、iOS 及 Linux 桌面系统中被广泛使用，其扫描线算法每年为数十亿台设备渲染文字。

**多边形裁剪与填充工具**：PostScript Level 2 解释器和 PDF 1.3 及以上规范的渲染引擎在绘制填充路径时直接使用扫描线算法，对复杂路径（含镂空、子路径）应用非零绕数规则决定哪些像素点亮。例如，Adobe Acrobat 在渲染含有透明度混合的 PDF 页面时，扫描线转换是将矢量路径转化为像素覆盖掩码的关键步骤。

## 常见误区

**误区一：认为每次扫描都需要重新计算边与扫描线的交点**。事实上，扫描线算法的精髓在于增量更新：当 $y$ 增加1时，新的 $x$ 交点仅为 $x_{old} + \Delta x$，不需要重新做直线方程求解。忽略这一点会将算法复杂度从 $O(n + \text{总像素数})$ 提升至 $O(n \times \text{行数})$，在处理 $4096 \times 4096$ 的高分辨率离屏渲染时，性能差距可达数十倍。

**误区二：水平边需要像其他边一样插入边表**。水平边的 $\Delta x = (x_2 - x_1)/0$ 为未定义（无穷大），若强行插入 AET 会导致 $x$ 坐标更新溢出或逻辑错误。正确做法是在构建 ET 阶段直接跳过所有满足 $y_1 = y_