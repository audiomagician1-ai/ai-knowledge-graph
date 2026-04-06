---
id: "cg-clipping"
concept: "裁剪"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 2
is_milestone: false
tags: ["算法"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
  - type: "academic"
    author: "Sutherland, I. E., & Hodgman, G. W."
    year: 1974
    title: "Reentrant polygon clipping"
    journal: "Communications of the ACM"
    volume: 17
    issue: 1
    pages: "32–42"
  - type: "academic"
    author: "Foley, J. D., van Dam, A., Feiner, S. K., & Hughes, J. F."
    year: 1990
    title: "Computer Graphics: Principles and Practice (2nd ed.)"
    publisher: "Addison-Wesley"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 裁剪

## 概述

裁剪（Clipping）是图形光栅化流程中的一个几何处理步骤，其目标是剔除或截断位于可视区域（视口或裁剪窗口）之外的几何图元，确保只有落在屏幕或视锥体内的部分才会进入后续光栅化计算。如果不执行裁剪而直接将超出范围的图元送入光栅化，会导致错误的像素填充、内存越界写入，乃至硬件渲染错误。

裁剪算法的研究可以追溯到1960至1970年代。Cohen-Sutherland算法由丹·科恩（Dan Cohen）和伊万·萨瑟兰（Ivan Sutherland）在1967年前后提出，专门处理二维线段与矩形窗口的裁剪；Sutherland-Hodgman多边形裁剪算法则于1974年由萨瑟兰与加里·霍德曼（Gary Hodgman）联合发表于《Communications of the ACM》第17卷第1期（页码32–42），将裁剪扩展到任意凸多边形边界（Sutherland & Hodgman, 1974）。这两种算法至今仍是图形学教学和硬件实现的基础参考，在Foley等人1990年出版的权威教材《Computer Graphics: Principles and Practice》中均有详细论述（Foley et al., 1990）。

在现代GPU管线中，裁剪发生在顶点着色器之后、光栅化之前的图元装配阶段。OpenGL 4.6规范（第13.5节）和Vulkan 1.3规范（第24.2节）均明确要求对标准化设备坐标（NDC）立方体 $[-1, 1]^3$ 以外的图元执行裁剪，硬件固定功能单元负责完成这一操作。NVIDIA从Fermi架构（2010年）起，AMD从GCN架构（2012年）起，均在硬件层面实现了完整的齐次裁剪单元，每个时钟周期可处理至少1个三角形的裁剪判断。

---

## 核心原理

### Cohen-Sutherland 线段裁剪

Cohen-Sutherland 算法使用一个4位**区域编码（Outcode）**对线段两端点进行分类。矩形裁剪窗口将平面划分为9个区域，每个端点的编码位定义为：

| 位 | 含义 | 条件 |
|----|------|------|
| Bit 3 (左) | 点在窗口左侧 | $x < x_{\min}$ |
| Bit 2 (右) | 点在窗口右侧 | $x > x_{\max}$ |
| Bit 1 (下) | 点在窗口下方 | $y < y_{\min}$ |
| Bit 0 (上) | 点在窗口上方 | $y > y_{\max}$ |

对两端点编码 $C_1$ 和 $C_2$ 进行如下判断：
- 若 $C_1 \mid C_2 = 0$（两端点均在窗口内），**完全接受（trivially accept）**；
- 若 $C_1 \mathbin{\&} C_2 \neq 0$（两端点在同侧窗口外），**完全拒绝（trivially reject）**；
- 否则，选取窗口外的端点，求其与窗口某条边界的交点，用交点替换该端点，并迭代。

交点计算利用线段参数方程。以线段端点 $(x_1, y_1)$ 与 $(x_2, y_2)$ 和左边界 $x = x_{\min}$ 相交为例，参数 $t$ 及交点纵坐标的计算公式为：

$$t = \frac{x_{\min} - x_1}{x_2 - x_1}, \quad y_{\text{intersect}} = y_1 + t \cdot (y_2 - y_1)$$

其中 $t \in [0, 1]$ 时交点位于线段内部。此算法对大量线段均在窗口外的场景极为高效，因为多数线段可通过位运算在 $O(1)$ 时间内快速拒绝，无需计算浮点交点。在实测基准中，当95%以上的线段完全在窗口外时，Cohen-Sutherland比朴素逐像素裁剪快约40至60倍。

例如，设裁剪窗口为 $[10, 100] \times [10, 100]$，线段端点为 $A=(5, 50)$，$B=(50, 50)$。端点 $A$ 的编码为 `0001`（左侧），$B$ 的编码为 `0000`（内部）。由于 $C_A \mathbin{\&} C_B = 0$ 且 $C_A \mid C_B \neq 0$，需计算 $A$ 与左边界 $x=10$ 的交点：$t = (10-5)/(50-5) \approx 0.111$，$y_{\text{intersect}} = 50$，故裁剪后保留线段从 $(10, 50)$ 到 $(50, 50)$。

### Sutherland-Hodgman 多边形裁剪

Sutherland-Hodgman 算法将凸裁剪区域的每条边界视为一个**半平面**，逐一对输入多边形进行裁剪，每次输出新的顶点列表再送入下一条边界的裁剪。对于矩形窗口，需依次经过4条裁剪边（左、右、上、下）。该算法的时间复杂度为 $O(n \cdot m)$，其中 $n$ 为多边形顶点数，$m$ 为裁剪边界数（Sutherland & Hodgman, 1974）。

针对输入多边形的每条边（顶点 $S$ 到顶点 $P$），算法分四种情况处理：

1. **$S$ 在内，$P$ 在内**：输出 $P$；
2. **$S$ 在内，$P$ 在外**：输出 $S$-$P$ 与裁剪边的交点；
3. **$S$ 在外，$P$ 在外**：不输出任何点；
4. **$S$ 在外，$P$ 在内**：输出交点和 $P$。

该算法要求裁剪区域必须是**凸多边形**，否则会产生多余的连接边。对凹多边形（如自交多边形），需改用Weiler-Atherton算法（1977年）或Greiner-Hormann算法（1998年）。

例如，考虑一个正方形多边形顶点为 $(5,5)$，$(15,5)$，$(15,15)$，$(5,15)$，裁剪窗口为 $[10,20]\times[10,20]$。经左边界（$x=10$）裁剪后，输出顶点变为 $(10,5)$，$(15,5)$，$(15,15)$，$(10,15)$；再经下边界（$y=10$）裁剪后，最终输出四边形 $(10,10)$，$(15,10)$，$(15,15)$，$(10,15)$，即裁剪窗口内的重叠区域。

### 三维视锥体裁剪（齐次坐标裁剪）

在三维图形管线中，裁剪在**裁剪坐标（Clip Space）**中执行，此时顶点坐标仍保留齐次分量 $w$。标准裁剪条件为六个半空间的交集：

$$-w \leq x \leq w, \quad -w \leq y \leq w$$

$$-w \leq z \leq w \;\text{（OpenGL约定）}, \quad 0 \leq z \leq w \;\text{（DirectX/Vulkan约定）}$$

在齐次空间中进行裁剪可以避免透视除法引入的数值不稳定性，特别是当顶点位于观察平面（$w \approx 0$）附近时，直接在NDC空间裁剪会发生除以零的问题。因此现代GPU总是在透视除法之前完成裁剪，这是图形API规范的强制要求。

判断顶点是否在某裁剪平面内侧，可统一表达为点积形式。以左裁剪面为例，设裁剪平面法向量为 $\mathbf{n}_L = (1, 0, 0, 1)^T$，则顶点 $\mathbf{v} = (x, y, z, w)^T$ 在内侧当且仅当：

$$\mathbf{n}_L \cdot \mathbf{v} = x + w \geq 0$$

六个裁剪面均可用类似形式表达，便于硬件并行计算。

---

## 算法复杂度与性能对比

不同裁剪算法在时间复杂度和适用场景上存在显著差异：

| 算法 | 年份 | 类型 | 时间复杂度 | 适用场景 |
|------|------|------|------------|----------|
| Cohen-Sutherland | 1967 | 线段 | $O(1)$（均摊） | 2D线段与矩形窗口 |
| Liang-Barsky | 1984 | 线段 | $O(1)$ | 2D线段，参数更少 |
| Sutherland-Hodgman | 1974 | 多边形 | $O(n \cdot m)$ | 凸裁剪区域多边形 |
| Weiler-Atherton | 1977 | 多边形 | $O(n \log n)$ | 凹裁剪区域多边形 |
| Greiner-Hormann | 1998 | 多边形 | $O(n \cdot m)$ | 任意多边形布尔运算 |

Liang-Barsky算法（1984年）由梁友栋与Barsky提出，通过将线段参数化为 $P(t) = P_1 + t(P_2 - P_1)$，$t \in [0,1]$，将四个裁剪边界转化为参数区间的求交，减少了Cohen-Sutherland中的迭代次数，在线段大量穿越边界的场景下效率提升约15%至25%。

---

## 实际应用

**场景1：2D UI渲染中的滚动列表**
在游戏引擎（如Unity 2022、Unreal Engine 5）或浏览器渲染引擎（如Chromium的Skia图形库）绘制超出控件边界的列表项时，需要对每条文本行或图标矩形执行2D裁剪。利用Cohen-Sutherland的快速拒绝特性，可以在CPU端快速剔除完全不可见的UI元素，避免将其提交给GPU。在Android 13的界面渲染测试中，启用CPU端裁剪剔除可将提交至GPU的UI绘制调用减少约30%至45%。

**场景2：OpenGL近裁剪面精度管理**
当三角形跨越近裁剪面（near plane，$z = -w$ 或 $z = 0$）时，硬件裁剪单元将生成新顶点并拆分图元。若近裁剪面设置过于接近0（如 $z_{\text{near}} = 0.001$），则深度精度丢失和裁剪频率都会显著增加。以32位浮点深度缓冲为例，深度精度 $\epsilon_z$ 近似满足：

$$\epsilon_z \approx \frac{z_{\text{far}}}{z_{\text{far}} - z_{\text{near}}} \cdot 2^{-23}$$

实践中推荐 $z_{\text{far}} / z_{\text{near}} \leq 10000$ 以保持深度缓冲精度，同时避免近裁剪面裁剪频率过高影响GPU吞吐量。

**场景3：软光