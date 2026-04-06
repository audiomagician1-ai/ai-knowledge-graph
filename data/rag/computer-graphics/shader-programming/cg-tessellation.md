---
id: "cg-tessellation"
concept: "细分着色器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 82.5
generation_method: "ai-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v2"
  - type: "academic"
    author: "Nießner, M., Loop, C., Meyer, M., & DeRose, T."
    year: 2012
    title: "Feature Adaptive Subdivision for Displacement Mapping"
    venue: "ACM SIGGRAPH Asia 2012"
  - type: "academic"
    author: "Vlachos, A., Peters, J., Boyd, C., & Mitchell, J. L."
    year: 2001
    title: "Curved PN Triangles"
    venue: "ACM Symposium on Interactive 3D Graphics"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 细分着色器

## 概述

细分着色器（Tessellation Shader）是Direct3D 11与OpenGL 4.0分别于2009年和2010年正式引入的可编程管线阶段，专门负责在GPU上动态增加几何体的三角形密度。与顶点着色器每次处理一个顶点不同，细分着色器以**图元补丁（Patch）**为操作单位，将一个粗糙的低多边形补丁细分成大量小三角形，实现无需修改CPU端网格数据的动态几何细化。OpenGL 4.0规范于2010年3月由Khronos Group发布，NVIDIA GeForce 400系列（Fermi架构，2010年）是最早全面支持该规范的消费级GPU。

该技术的直接动机是解决3D模型的LOD（Level of Detail）困境：传统做法需要美术预先制作多套精细度不同的模型，而细分着色器允许引擎存储一套低面数基础网格，在渲染时根据相机距离、屏幕投影面积等实时条件自适应地增加三角形数量。Valve的Source 2引擎和Unreal Engine 4均采用该技术实现地形与角色的动态曲面细分，在镜头拉近时自动呈现更丰富的几何细节。

**问题引入**：为什么不直接在CPU端生成高精度网格，而要在GPU上动态细分？在一个包含1000个地形补丁的场景中，若每帧在CPU端根据相机距离重新生成网格，将消耗大量CPU带宽并产生严重的内存分配压力；而细分着色器将这一计算完全卸载到GPU，CPU仅需传递粗糙的控制点数据即可，这是细分着色器设计的根本出发点。

## 核心原理

### 三阶段流水线结构

细分功能由三个连续阶段共同完成，缺一不可：

1. **Hull Shader（外壳着色器）**：每个补丁执行一次，输出**细分因子（Tessellation Factor）**——具体包含外部边因子（决定补丁边缘划分数）和内部因子（决定补丁内部划分数）。以四边形补丁为例，共输出6个浮点数：4个边缘因子 + 2个内部因子。Hull Shader同时透传或修改每个控制点的属性数据供后续阶段使用。

2. **固定功能细分器（Tessellator）**：这一阶段不可编程，由GPU硬件依据Hull Shader输出的因子，在归一化参数空间 $(u, v)$ 中生成均匀或奇偶分布的参数坐标集合，并输出细分后的索引连接关系。细分因子范围通常为1～64的浮点数，等于1时不产生任何新顶点，等于64时单个四边形补丁可细分产生约4096个顶点。

3. **Domain Shader（域着色器）**：对固定功能细分器生成的每个新参数坐标 $(u, v)$ 执行一次，利用重心坐标或双线性插值将参数坐标映射为实际三维世界空间坐标。位移贴图（Displacement Map）的采样通常在此处进行——读取一张高度纹理，将新顶点沿法线方向偏移，从而真正隆起几何细节而非仅靠法线贴图欺骗光照。

### 细分因子的自适应计算

Hull Shader的核心任务是计算**自适应细分因子**，常见策略是基于屏幕空间边长估算。设某条补丁边的世界空间长度为 $L$，屏幕高度像素数为 $H$，垂直视场角为 $\theta$，相机到补丁中心的距离为 $d$，则理想细分因子为：

$$T = \text{clamp}\!\left(\frac{L \cdot H}{2d \cdot \tan(\theta/2)},\ T_{\min},\ T_{\max}\right)$$

此公式保证屏幕上每段边长稳定在约8～16像素左右，镜头近时因子高（最多64），远时因子低（最少1），避免过度绘制造成GPU浪费。另一种策略是球形包围盒视锥体裁剪：若整个补丁在视锥体外，直接将所有细分因子设为0，GPU将丢弃该补丁，无需光栅化任何三角形。

例如，在一个分辨率为1920×1080、垂直FOV为60°的场景中，一条世界空间长度为2米的补丁边，相机距离为5米时，理想细分因子约为：$T \approx 2 \times 1080 / (2 \times 5 \times \tan 30°) \approx 374$，钳制后取最大值64；当相机退至80米时，$T \approx 23$，即细分为约23段，贴近实际渲染需求。

### Phong曲面细分与PN三角形

Domain Shader中最基础的插值是线性插值，但这会保留原网格的锋利折痕。**Phong Tessellation**利用控制点的法线将新顶点向切平面投影再混合（Vlachos et al., 2001），公式为：

$$P_{\text{smooth}} = \text{lerp}\!\left(P_{\text{linear}},\ \text{proj}(P_{\text{linear}},\ P_i,\ N_i),\ \alpha\right)$$

其中 $\alpha$ 通常取0.75，$\text{proj}$ 将线性插值点投影到以 $P_i$ 为切点、$N_i$ 为法线的切平面上，具体为：

$$\text{proj}(P, P_i, N_i) = P - \left[(P - P_i) \cdot N_i\right] N_i$$

这使低面数网格在细分后呈现出弯曲圆润的曲面，而非仍然有棱有角的多面体。**PN三角形（Point-Normal Triangles）**是另一种曲面近似方案，由Vlachos等人于2001年在ACM Interactive 3D Graphics会议上提出，通过10个控制点（6个位置控制点 + 6个法线控制点，共享顶点）构造三次贝塞尔曲面，在无需完整细分曲面（Subdivision Surface）数学框架的情况下提供合理的曲面近似质量。Nießner等人（2012）进一步在ACM SIGGRAPH Asia上提出了特征自适应细分（Feature Adaptive Subdivision），结合位移贴图实现了工业级别的曲面细节还原精度。

## 实际应用

**地形渲染**：Unreal Engine的World Composition系统采用细分着色器处理地形Heightmap，基础网格仅需32×32的顶点网格，在摄像机近处细分因子升至64，等效分辨率达2048×2048，而远处保持1:1不增加顶点，极大降低了远距离地形的渲染代价。每帧GPU端自动完成所有细分级别的过渡，无需CPU参与LOD切换逻辑。

**角色皮肤与布料**：DiRT Rally等赛车游戏对赛车车身应用细分着色器结合位移贴图，刮痕与凹陷真实突出于网格表面而非仅是贴图效果。基础车身网格约3000面，细分后局部可达60000面，所有额外几何由GPU实时生成，CPU侧零负担。Codemasters于2015年发布的DiRT Rally明确在技术文档中列出细分着色器为车辆损伤系统的核心渲染技术之一。

**水面模拟**：将水平面划分为64×64的四边形补丁网格，每帧在Hull Shader中根据浪高FFT贴图的能量决定各补丁的细分等级，在浪峰高频区域提升细分因子，在平静水域降低，配合Domain Shader中的Gerstner波方程整体偏移顶点，产生动态起伏的几何波形。例如，Gerstner波的顶点偏移量为：

$$\Delta P = \sum_i A_i \cdot \hat{D}_i \cdot \cos(\vec{k}_i \cdot \vec{x} - \omega_i t + \phi_i)$$

其中 $A_i$ 为波幅，$\hat{D}_i$ 为传播方向，$\omega_i$ 为角频率，$\phi_i$ 为初始相位。

## 性能优化策略

细分着色器在提升视觉质量的同时也带来显著的GPU计算开销，以下三项优化策略在实践中被广泛采用：

**背面剔除（Back-face Culling）**：在Hull Shader中，若补丁的所有控制点法线与视线方向夹角均超过90°（即补丁完全背向相机），将细分因子设为0提前丢弃，可节省约30%～50%的细分计算量（具体比例取决于场景几何分布）。

**视锥裁剪（Frustum Culling）**：计算补丁的轴对齐包围盒（AABB）并与视锥体的6个裁剪平面逐一测试。若AABB完全在视锥体外，同样将细分因子归零。对于包含大量地形补丁的室外场景，视锥裁剪可减少超过60%的无效细分调用。

**LOD过渡平滑（Crack Avoidance）**：相邻补丁若细分因子不同，共享边会因细分数量不一致产生裂缝（T型接缝）。解决方案是在Hull Shader中对每条共享边的因子取相邻两个补丁的最小值，或通过传递相邻补丁的细分因子并取平均来保证边界一致性。Unreal Engine 4的地形系统专门实现了一套"Neighbor LOD"机制以消除此类裂缝。

## 常见误区

**误区一：细分着色器可以替代法线贴图**。细分着色器通过位移贴图增加真实几何，但其成本远高于法线贴图——每个新顶点都要经过Domain Shader计算并送入后续管线。对于纹理内的高频细节（如布料织纹、皮革纹理），仍应使用法线贴图；细分适合中低频的宏观几何变化（岩石块状起伏、角色肌肉凸起，通常波长大于顶点间距的5倍以上）。

**误区二：细分因子设置越高越好**。当细分产生的三角形小于1个像素时，多个三角形会共用同一像素，触发GPU的"过度细分"（Overshading）问题，光栅化效率急剧下降。一般建议以屏幕空间三角形面积不小于4像素为下限动态钳制细分因子，而非写死为最大值64。在GTX 1080上测试表明，细分因子从32提升至64而视觉差异几乎不可见时，帧时间增加约18%，性价比极低。

**误区三：Hull Shader与Domain Shader执行次数相同**。Hull Shader每个补丁只执行一次（或与控制点数相同次数），而Domain Shader对每一个细分后的新顶点执行一次。若细分因子为16的三角形补丁，Domain Shader调用次数约为136次，Hull Shader控制点阶段仅调用3次，两者开销比例约为45:1，差异显著。

## 知识关联

细分着色器在管线中位于顶点着色器之后、几何着色器之前，其输出的顶点最终仍会经过光栅化并触发**片元着色器（Fragment Shader）**计算每像素颜色。理解片元着色器的插值机制有助于正确设置Domain Shader的顶点属性输出——Domain Shader必须为每个新顶点