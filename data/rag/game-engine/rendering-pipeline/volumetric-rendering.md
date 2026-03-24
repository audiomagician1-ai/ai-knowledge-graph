---
id: "volumetric-rendering"
concept: "体积渲染"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["特效"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 体积渲染

## 概述

体积渲染（Volumetric Rendering）是一种模拟光线穿越三维空间中非均匀介质（如雾、烟、云、火焰）时发生散射、吸收和自发光现象的渲染技术。与表面渲染只处理几何体表面不同，体积渲染必须对光线在整个三维体积内的传播过程进行积分运算，因此计算代价远高于普通多边形渲染。

体积渲染的理论基础来源于20世纪80年代的科学可视化领域。1984年，Robert Drebin等人提出了基于光线投射（Ray Casting）的体素渲染方法，用于医学CT数据可视化。游戏引擎在2010年代中期开始将体积渲染引入实时渲染管线，代表性里程碑是Guerrilla Games于2015年发布的《地平线：零之曙光》中的大气体积雾系统，以及Epic在Unreal Engine 4.14中正式引入的体积雾（Volumetric Fog）功能。

体积渲染之所以在游戏引擎中受到重视，是因为它能够真实模拟上帝光（God Ray）、丁达尔效应（Tyndall Effect）以及云层内部的多重散射，这些效果单靠屏幕空间后处理无法准确还原体积内的光照遮蔽关系，尤其是当动态光源穿越雾气区域时的阴影正确性。

## 核心原理

### 体积渲染方程（VRE）

体积渲染的数学基础是辐射传输方程（Radiative Transfer Equation），沿光线方向的积分形式为：

$$L(x, \omega) = \int_0^d T(x, x_t) \cdot \sigma_s(x_t) \cdot L_{scat}(x_t, \omega) \, dt + T(x, x_d) \cdot L_{surface}$$

其中：
- $T(a, b) = e^{-\int_a^b \sigma_t(s)ds}$ 为透射率（Transmittance），表示光线未被介质吸收的比例
- $\sigma_t = \sigma_s + \sigma_a$：消光系数，等于散射系数加吸收系数
- $\sigma_s$：散射系数，决定介质将光线向其他方向重新分配的能力
- $L_{scat}$：散射辐亮度，包含来自所有方向的入射光经相位函数加权后的贡献

在实时引擎中，这个积分通常被离散化为沿视线方向采样若干步骤（典型值为64至256步），每步累积散射贡献并衰减透射率，最终合成到屏幕像素。

### 相位函数

相位函数（Phase Function）描述光线碰到介质粒子后向特定方向散射的概率分布。游戏引擎中最常用的是Henyey-Greenstein相位函数（1941年提出）：

$$p(\theta) = \frac{1}{4\pi} \cdot \frac{1 - g^2}{(1 + g^2 - 2g\cos\theta)^{3/2}}$$

参数 $g \in [-1, 1]$ 控制各向异性：$g=0$ 为各向同性散射（均匀雾），$g>0$ 为前向散射（薄雾/云），$g<0$ 为后向散射（特殊介质）。大气雾气通常使用 $g \approx 0.2$，而积云则常用 $g \approx 0.85$ 来产生强烈的银边效果。

### 三维纹理与Froxel体素化

现代实时体积渲染的主流实现方案是将视锥体（Frustum）划分为三维体素网格，称为Froxel（Frustum Voxel）。典型配置如Unreal Engine 4的默认设置为 $160 \times 90 \times 64$ 个Froxel，深度方向采用对数分布以在近处提供更高精度。每个Froxel存储散射系数、吸收系数和自发光颜色，通过Compute Shader在GPU上并行计算光照积分，再将结果写入一张3D LUT纹理，供后续像素着色器查表合成。

### 多重散射近似

真实的云和浓雾中，光子会经历数十次甚至数百次散射，这是实时引擎无法逐次追踪的。Sebastien Hillaire在SIGGRAPH 2015上提出了一种多重散射近似方法：将每次额外的散射贡献乘以一个递减系数（通常为0.5），叠加3到4个八度的散射，能以极低的开销模拟出云层内部的柔和光晕效果。

## 实际应用

**体积雾（Volumetric Fog）**：在游戏场景中，体积雾与阴影贴图结合，使聚光灯能在雾气中投射出体积光锥（VolumetricSpotLight）。《赛博朋克2077》中夜城街道的霓虹光柱即采用此技术，每盏路灯的阴影遮挡关系都被正确传递到体积雾的Froxel数据中。

**实时体积云**：Naughty Dog在《最后生还者：第二章》（2020年，PS4）中使用了基于Worley噪声和Perlin-Worley噪声叠加的三维密度场表示积云形态，在128³分辨率的3D纹理中存储云的低频形状，再用额外一张32³高频噪声纹理叠加细节侵蚀效果。光照部分使用6次步进的锥形采样（Cone Sampling）近似多重散射。

**上帝光（God Ray）**：在Froxel体积雾方案出现之前，许多引擎采用径向模糊（Radial Blur）后处理模拟丁达尔效应。现代Froxel方案的优势在于动态遮挡：当角色或建筑物遮住阳光时，体积光束会实时产生正确的阴影边界，而后处理方法则因缺乏深度信息而产生错误的光线穿透几何体现象。

## 常见误区

**误区一：体积雾和高度雾（Height Fog）是同一种技术**。高度雾是基于解析公式（通常为指数函数）计算从摄像机到表面的积分透射率，它不追踪光线方向，因此无法产生体积阴影和方向性光散射。体积雾通过Froxel采样实际计算每个体素内的光照，能正确处理动态遮挡，代价是比高度雾消耗多出约0.5至2ms的GPU时间（分辨率相关）。

**误区二：增大Froxel分辨率总能提升质量**。Froxel的内存占用随三个维度线性扩展：将 $160 \times 90 \times 64$ 提升到 $320 \times 180 \times 128$ 会使显存占用增加8倍，同时Compute Shader的线程数也随之暴增，往往造成性能骤降且视觉收益有限。实践中应优先优化深度分层策略和每步采样噪声抖动（Temporal Jitter），而非盲目提高网格分辨率。

**误区三：体积云必须使用光线行进（Ray Marching）才能渲染**。确实，体积云的标准实现依赖光线行进，但对于远景云层，引擎可以使用将云密度烘焙到2D Impostor贴图或使用Billboard粒子系统加以代替，在LOD距离以外切换到低开销方案，而玩家几乎无法察觉过渡时的质量差异。

## 知识关联

体积渲染直接依赖渲染管线中的延迟渲染架构（Deferred Rendering）：Froxel系统需要在GBuffer写入完成后才能获取深度信息，以确保体积积分在不透明几何体处正确截断。了解深度缓冲（Depth Buffer）的工作原理是理解体积雾深度采样的前提，而Compute Shader的并行编程模型决定了Froxel更新Pass的效率上限。

在全局光照体系中，体积渲染与光照探针（Light Probe）和级联阴影贴图（Cascaded Shadow Maps，CSM）紧密协作：CSM为Froxel体素提供阴影查询，决定每个体素接收到的直接光照量。学习体积渲染后，可以进一步探索路径追踪中的参与介质（Participating Media）渲染，那是体积渲染在离线渲染领域更精确的理论形式，采用蒙特卡洛积分取代离散步进，从根本上消除了步进走样（Aliasing）问题。
