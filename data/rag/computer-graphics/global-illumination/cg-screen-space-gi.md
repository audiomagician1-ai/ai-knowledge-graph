---
id: "cg-screen-space-gi"
concept: "屏幕空间GI"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 3
is_milestone: false
tags: ["技术"]

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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 屏幕空间全局光照（SSGI）

## 概述

屏幕空间全局光照（Screen Space Global Illumination，SSGI）是一类完全基于当前帧G-Buffer信息来模拟间接光照的实时渲染技术，其核心约束是：所有光照计算只能使用屏幕上已有的像素数据，而不访问任何三维场景结构。SSGI的直接前身是屏幕空间环境光遮蔽（SSAO，2007年由Crytek的Marcin Iwanicki在《孤岛危机》中引入），而SSGI在此基础上引入了颜色出血（Color Bleeding）计算，使间接光不仅有遮蔽，还能携带邻近表面反射的有色漫反射光。

屏幕空间定向遮蔽（SSDO，Screen Space Directional Occlusion）是SSGI家族中最早将全彩间接反射纳入实时管线的方案，由Tobias Ritschel等人于2009年SIGGRAPH发表。与SSAO只输出灰度遮蔽因子不同，SSDO从被遮挡方向采集实际的屏幕颜色，再按照Lambertian漫反射的余弦权重叠加，从而产生绿色草地对白色墙壁的绿色色溢、红色墙角的红色污染等物理上真实的间接光现象。

现代引擎（UE5、Unity HDRP 12+）均内置了升级版SSGI，以每帧毫秒级的代价在不依赖光线追踪硬件的情况下提供近场间接漫反射。其根本价值在于：相比纯离线的路径追踪，SSGI牺牲了场景完整性换取了确定性的帧时间预算，典型开销约为1–3 ms（1080p，半分辨率）。

---

## 核心原理

### 半球采样与G-Buffer重建

SSGI在着色像素P的切线空间半球内均匀或重要性采样若干方向向量 $\omega_i$（通常16–64个）。对每个方向，算法沿 $\omega_i$ 在屏幕空间做步进：读取深度缓冲计算出采样点的世界坐标 $Q$，若 $Q$ 在P的法线半球内且深度差 $\Delta z$ 落在有效范围 $[z_{\min}, z_{\max}]$（典型值0.01 m–0.5 m）内，则将G-Buffer中 $Q$ 点的辐射度 $L(Q)$ 乘以余弦权重 $\max(0, \omega_i \cdot n_P)$ 累加到P的间接照度：

$$L_{\text{indirect}}(P) = \frac{\pi}{N} \sum_{i=1}^{N} L(Q_i) \cdot \max(0,\, \hat{\omega}_i \cdot \hat{n}_P) \cdot V(P, Q_i)$$

其中 $V(P, Q_i)$ 是可见性项（1表示未遮蔽，0表示遮蔽），$N$ 为采样数。这一公式本质是蒙特卡罗估计半球面上的辐射传输积分。

### 颜色出血的方向性

与SSAO的纯遮蔽不同，SSGI中 $L(Q_i)$ 取自G-Buffer的自发光或已计算好的直接光辐射度纹理（通常是前一帧的HDR颜色缓冲），因此颜色信息得以从发光表面"渗透"到相邻表面。这要求渲染管线存在一张**上一帧的完整光照缓冲**（Previous Frame Lit Buffer），SSGI从中采样邻近像素颜色；Unity HDRP将此缓冲命名为`_ColorPyramidTexture`，并构建MIP链以支持粗糙表面的模糊采样。

### 时域积累与降噪

因采样数受帧时间限制，单帧SSGI原始输出信噪比极低。主流实现采用时域抗锯齿（TAA）风格的历史帧重投影累积：将当前帧结果与历史帧按混合权重 $\alpha \approx 0.1$ 做指数移动平均。当像素被遮挡、移动速度超过重投影误差阈值（典型约2像素/帧）时，历史帧权重降为0以避免拖影。空间降噪（横向双边滤波，核半径通常5–9像素）在时域积累之前或之后执行，利用深度差和法线差控制滤波核权重，防止间接光跨越几何边界渗透。

---

## 实际应用

**游戏角色室内场景**：在走廊、地下室等环境中，SSGI能让角色身上反射地板颜色（如红色地毯对白色靴底产生淡红晕），而无需预计算光照贴图。Unity HDRP中SSGI的典型参数为：最大光线长度2 m，分辨率Half，去噪开启，整体帧时间约1.8 ms（RTX 3070，1440p半分辨率）。

**建筑可视化的快速迭代**：建筑师更改墙漆颜色后，SSGI在下一帧即反映新的色溢效果，而传统光照贴图需要重新烘焙数小时。

**与光线追踪的混合**：UE5在不支持DXR的GPU上回退到SSGI，以屏幕空间算法填补Lumen全局光照方案的空缺，保证跨平台的近场间接光一致性。

---

## 常见误区

**误区一：SSGI能照亮任何被遮蔽的区域**。事实上，凡是未出现在当前屏幕帧内的几何体（如相机背后的红色墙壁）完全不存在于G-Buffer，其反射光照对画面中的物体毫无贡献。这意味着旋转相机时间接光会瞬间改变——屏幕边缘消失的几何体立即失去对场景的间接照明影响，造成闪烁（Light Leaking的逆问题）。

**误区二：增大采样数就能消除所有噪点和伪影**。深度不连续处（前景物体边缘）会产生"光晕泄漏"（Halo Leaking）：采样点 $Q$ 因深度突变而误判为遮挡体，造成轮廓处出现过亮或过暗的光环。这一伪影与采样数无关，根源在于深度缓冲只保存最近表面的信息，无法区分遮挡关系的前后顺序，需要通过厚度偏差参数（Thickness Bias）或深度差阈值剔除大深度跳变的采样点来抑制。

**误区三：SSGI与SSAO可以相互替代**。两者的输出维度完全不同：SSAO输出的是0–1的灰度遮蔽因子，仅调制环境光强度；SSGI输出的是RGB辐射度值，代表来自邻近表面的有方向彩色间接光照。直接用SSGI替代SSAO而不调整光照合成方程，会导致间接光被双重叠加，使画面过亮并引入错误的色彩偏差。

---

## 知识关联

**前置概念——环境光遮蔽（AO）**：SSAO奠定了屏幕空间采样半球的基础流程（随机偏移采样、深度比较、法线偏置），SSGI在这套框架上将灰度遮蔽替换为彩色辐射度积分，学习SSGI前需熟悉SSAO的深度剔除逻辑和法线对齐矩阵构造。

**后续概念——间接高光**：SSGI仅处理粗糙漫反射的半球积分，镜面/光泽表面所需的间接高光由专门的屏幕空间反射（SSR）或近似锥形追踪（SSCRT）负责。两者在合成时共享同一张前帧光照缓冲，但SSR使用反射向量而非随机半球采样，且需要额外的步进精度控制（二进制搜索细化交叉点）。SSGI与SSR的分工界限由材质粗糙度阈值决定，通常粗糙度大于0.5的表面由SSGI主导，小于0.5的表面由SSR主导。