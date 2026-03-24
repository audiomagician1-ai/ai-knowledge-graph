---
id: "vfx-pp-ao"
concept: "环境光遮蔽"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 环境光遮蔽

## 概述

环境光遮蔽（Ambient Occlusion，简称AO）是一种模拟光线在几何体缝隙、凹陷和接触面处被遮挡衰减的渲染技术。其物理依据来自于漫反射间接光照的可见性积分：在某点处，从半球方向射入的环境光中，被周围几何体遮挡的部分越多，该点接收到的环境光越少，从而呈现出更暗的阴影效果。这种阴影不依赖具体光源方向，而是纯粹由几何形状决定的软阴影效果。

AO的概念最早由工业光魔（ILM）在2002年前后将其引入电影特效流程，随即被Bungie公司在《光晕2》（2004年）的离线烘焙管线中使用。屏幕空间版本（SSAO）由Crytek工程师Vladimir Kajalin在2007年随《孤岛危机》首次在实时渲染中实现，彻底改变了游戏画面的接触阴影表现，此后成为几乎所有3A游戏的标准后处理特效之一。

与传统烘焙AO不同，屏幕空间AO完全在GPU的后处理阶段基于深度缓冲（Depth Buffer）和法线缓冲（Normal Buffer）计算，无需预处理资产，可动态响应场景变化，代价是计算结果只能反映屏幕可见几何体的遮蔽关系，对屏幕外几何体无感知能力。

---

## 核心原理

### SSAO：屏幕空间环境光遮蔽

Kajalin的原始SSAO算法在当前像素周围的半球形采样核（Sample Kernel）内随机采样若干点（通常16～64个），将这些采样点投影回屏幕空间后与深度缓冲比较。若采样点深度大于缓冲中的深度值，则认为该方向被遮挡，遮蔽贡献累加后归一化为0到1的遮蔽系数。SSAO的核心计算公式为：

$$AO = 1 - \frac{1}{N}\sum_{i=1}^{N} \text{occluded}(\mathbf{s}_i)$$

其中 $N$ 为采样数量，$\mathbf{s}_i$ 为第 $i$ 个采样点在世界/视图空间中的偏移向量。为避免自遮蔽伪影，每帧会使用一张小尺寸随机旋转纹理（通常为4×4像素的Noise Texture）对采样核进行旋转，再配合模糊通道消除噪点。SSAO对采样核方向没有法线引导，导致低频噪声和漏光问题较为明显。

### HBAO：基于视界的环境光遮蔽

HBAO（Horizon-Based Ambient Occlusion）由NVIDIA在2008年提出，相较SSAO有本质性改进：它沿着以当前像素为圆心的若干方向射线（通常4～8条），在每条射线上搜索深度缓冲中的"地平线角度"（Horizon Angle），通过积分各方向的遮蔽角度来计算AO值，并引入了像素法线参与计算，使遮蔽结果与表面朝向物理一致。HBAO在同等采样数下比SSAO产生更少的条带噪声，且在狭窄缝隙处遮蔽效果更准确，代价是Shader复杂度提升约30%～50%。

### GTAO：基面真实环境光遮蔽

GTAO（Ground Truth Ambient Occlusion）由Jorge Jimenez等人于2016年在SIGGRAPH上发表，是目前主流引擎（如Unreal Engine 4.26+和Unity HDRP）中最高质量的实时AO方案。GTAO在HBAO的地平线积分基础上，修正了多散射项（Multi-Bounce）近似，将单次遮蔽的假设替换为更完整的漫反射可见性积分，并加入了像素间时域积累（TAA Reprojection）以用极少样本（每帧仅2～4条射线）达到接近离线渲染的效果。Unreal Engine的GTAO实现在4K分辨率下额外消耗约0.8ms的GPU时间。

---

## 实际应用

**角色与场景接触阴影**：AO最典型的视觉贡献是物体与地面接触处的阴影暗化，例如角色脚踩地面时脚底边缘出现的柔和阴影、椅子腿与地板接触点的暗化。若关闭AO，这些接触点会因缺乏阴影而产生"漂浮感"，即使有方向光阴影也无法完全弥补。

**室内场景的角落遮蔽**：墙角、书架内侧、沙发靠垫之间等几何凹陷处，AO能显著增强空间层次感。在《赛博朋克2077》等游戏中，室内环境大量依赖GTAO来区分不同材质平面的空间关系，尤其在无直射光照的区域，AO几乎是唯一的形体信息来源。

**后处理合成顺序**：在标准后处理管线中，AO通常在色调映射（Tonemapping）之前、抗锯齿之后应用，AO纹理以乘法方式叠加到场景颜色的漫反射分量上，不影响高光分量，以避免金属材质表面出现错误的暗化。

---

## 常见误区

**误区一：AO应当应用于所有光照分量**
很多初学者将AO直接乘以最终像素颜色，导致高光和自发光区域也被错误压暗。正确做法是AO只能影响漫反射间接光照分量（Diffuse Indirect），在PBR渲染管线中需要单独乘以Environment Diffuse项，镜面反射（Specular）分量需使用独立的SSAO变种或Specular AO计算。

**误区二：增加SSAO采样数量可以消除光晕伪影（Halo Artifact）**
SSAO的"光晕"问题（大物体边缘出现不合理的AO暗圈）并非采样数不足导致，而是算法本身的深度投影误差造成的结构性缺陷。增加采样数只能减少噪点，无法消除光晕。解决光晕问题需要使用范围检测（Range Check）或改用HBAO/GTAO等更精确的算法。

**误区三：SSAO可以替代光线追踪AO**
屏幕空间AO只能感知当前帧可见像素的深度信息，对于屏幕外的大型遮挡体（如建筑物顶部遮住街道）完全无效。光线追踪AO（RTAO）则通过在场景BVH结构中追踪真实光线获得全局遮蔽信息，效果差异在开阔户外场景中尤为明显。

---

## 知识关联

**与胶片颗粒的关系**：胶片颗粒在后处理管线中的位置通常紧靠最终输出，而AO在管线前段参与光照合成；两者虽然都在后处理阶段执行，但AO输出的遮蔽纹理在被胶片颗粒叠加之前就已融入场景颜色，因此AO的噪点需要通过时域模糊（Temporal Filtering）单独处理，不能依赖胶片颗粒来"掩盖"采样不足的噪声。

**通向屏幕空间反射（SSR）**：AO与SSR同属屏幕空间后处理技术家族，都依赖深度缓冲和法线缓冲作为输入数据，在实现架构上共享GBuffer的读取逻辑。GTAO与SSR合并计算可以共用同一套射线步进框架，理解AO中的视界积分概念是理解SSR中光线步进和反射遮蔽的直接前置知识。
