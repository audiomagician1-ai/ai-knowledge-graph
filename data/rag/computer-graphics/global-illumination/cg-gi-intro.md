---
id: "cg-gi-intro"
concept: "全局光照概述"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.394
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 全局光照概述

## 概述

全局光照（Global Illumination，简称GI）是指模拟光线在场景中经过多次反射、折射和散射后最终到达观察者眼睛的完整物理过程。与仅计算光源直接照射物体表面的局部光照模型不同，全局光照将整个场景中所有表面之间的光能传递纳入计算范围，因此同一场景中背阴处的墙壁也会被周围彩色墙面的反射光所染色，形成色彩渗色（Color Bleeding）现象。

全局光照的理论基础可以追溯到1984年Cornell大学的研究团队，他们提出了经典的辐射度方法（Radiosity），首次将光能传递方程引入计算机图形学，专门处理漫反射表面之间的光能交换。1986年James Kajiya在SIGGRAPH发表的论文中正式提出了渲染方程（The Rendering Equation），将GI问题统一表达为一个积分方程，为此后所有GI算法奠定了数学基础。

全局光照对最终图像质量的影响体现在两个最直观的视觉线索上：间接光照让暗部细节可见而不是纯黑，以及软阴影和接触阴影让物体显得真实落在场景中。在实时渲染领域，如何以有限的计算预算近似这两个效果，是驱动GI技术不断发展的核心动力。

## 核心原理

### 直接光照与间接光照的区分

直接光照（Direct Illumination）是指光源发出的光子经过零次中间反射，沿直线路径直接打到表面并进入摄像机的光照分量。间接光照（Indirect Illumination）则是光子经过至少一次表面反弹后才贡献到最终像素颜色的分量。GI的核心挑战正是计算这些间接路径：一条光线在到达摄像机之前可能经历1次（单次间接）、2次乃至数十次反射，路径数量随弹射次数呈指数级增长。对于一个典型室内场景，间接光照贡献往往占到最终亮度的30%–70%，忽略它会导致整个场景显得平坦且缺乏色彩联系。

### 渲染方程的结构

渲染方程的标准形式为：

$$L_o(\mathbf{x}, \omega_o) = L_e(\mathbf{x}, \omega_o) + \int_{\Omega} f_r(\mathbf{x}, \omega_i, \omega_o)\, L_i(\mathbf{x}, \omega_i)\, (\omega_i \cdot \mathbf{n})\, d\omega_i$$

其中 $L_o$ 是点 $\mathbf{x}$ 沿方向 $\omega_o$ 的出射辐亮度，$L_e$ 是自发光项，$f_r$ 是双向反射分布函数（BRDF），$L_i$ 是来自方向 $\omega_i$ 的入射辐亮度，$\Omega$ 是法线 $\mathbf{n}$ 所在半球。这个方程的自引用特性（$L_i$ 本身是其他表面的 $L_o$）使其成为递归积分方程，无法解析求解，所有GI算法本质上都是对这个积分的不同近似策略。

### GI方法的主要分类

GI算法按求解策略可分为三大类。**离线精确方法**以路径追踪（Path Tracing）和双向路径追踪（BDPT）为代表，通过蒙特卡洛采样无偏估计渲染方程，收敛结果物理正确，但单帧渲染时间以分钟至小时计，主要用于电影和产品渲染。**预计算方法**包括光照贴图烘焙（Lightmap Baking）和球谐光照（Spherical Harmonics），在运行前将静态GI结果存储到纹理或系数中，运行时查表即可，适合静态场景的实时应用。**实时动态方法**包括屏幕空间全局光照（SSGI）、辐照度探针（Irradiance Probe）网格以及新兴的硬件光线追踪GI（如NVIDIA在2018年随Turing架构引入的RTX管线），这类方法在质量与性能之间取得不同的折中。

## 实际应用

在游戏引擎中，Unreal Engine 5的Lumen系统是当前实时GI的代表性实现，它结合了屏幕空间追踪、有向距离场（SDF）追踪和表面缓存（Surface Cache）三层加速结构，在主机平台（PS5/XSX）上实现30–60fps下的动态多次弹射GI，最高追踪距离约为200米。Unity的自适应探针体积（Adaptive Probe Volumes，APV）则将辐照度探针按场景几何密度自适应分布，解决了传统固定网格探针在薄墙和楼层过渡处的漏光问题。

在电影领域，Pixar自2001年《怪兽公司》起全面使用基于路径追踪的RenderMan渲染器，每帧渲染时间长达数小时，正是完整GI计算使角色毛发在环境色下呈现出可信的颜色渗色效果，这在局部光照模型下完全无法重现。

## 常见误区

**误区一：认为环境光（Ambient Light）等同于间接光照。** 传统实时渲染中常用一个常数环境光项（如 $L_a = 0.1$）来粗略补偿间接光照的缺失，但这个常数对所有表面点和方向一视同仁，既不受场景几何影响也不携带方向信息。真正的间接光照会因遮挡关系在凹陷处更暗（即环境光遮蔽效果），并且会随邻近表面颜色变化而产生色彩渗色，两者在外观上有本质差异。

**误区二：认为GI只影响漫反射表面，镜面反射无需GI。** 事实上镜面反射同样需要GI数据：一个抛光地板反射天花板灯具的高光，就是间接光照中的镜面分量。渲染方程中的 $f_r$ 涵盖BRDF的漫反射和镜面反射两个波瓣，现代基于物理的渲染（PBR）材质两个波瓣都依赖正确的入射辐亮度 $L_i$，而这正是GI所要提供的。

**误区三：认为提高路径追踪的采样数（SPP）就能线性加速收敛。** 蒙特卡洛积分的误差以 $O(1/\sqrt{N})$ 的速率下降，将噪点减少一半需要将SPP提高4倍，而非2倍。这也是为什么工业界大量研究集中在重要性采样（Importance Sampling）、多重重要性采样（MIS）和AI降噪（如NVIDIA的DLSS Ray Reconstruction）上，而非单纯堆叠采样数量。

## 知识关联

学习全局光照概述后，下一步应深入**渲染方程**，将上文提及的积分方程中每个变量（辐亮度、BRDF、立体角微元）进行严格的物理量定义和推导，这是理解所有GI算法正确性的数学前提。在此基础上，**环境光遮蔽（Ambient Occlusion）**可视为对间接漫反射可见性项的独立近似，**辐照度贴图**和**反射探针**则分别是对渲染方程漫反射积分和镜面反射积分的预计算近似，**光传播体积（Light Propagation Volumes，LPV）**是对间接光照体积分布的实时动态近似。这五个后续概念分别对应GI渲染方程中不同分量的不同近似策略，形成完整的实时GI技术图谱。
