---
id: "cg-taa"
concept: "TAA"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "research"
    title: "High-Quality Temporal Supersampling"
    authors: ["Brian Karis"]
    venue: "SIGGRAPH 2014 (Epic Games)"
    year: 2014
  - type: "research"
    title: "Temporal Reprojection Anti-Aliasing in INSIDE"
    authors: ["Mikkel Gjoel"]
    venue: "GDC 2016"
    year: 2016
  - type: "textbook"
    title: "Real-Time Rendering"
    authors: ["Tomas Akenine-Moller", "Eric Haines", "Naty Hoffman"]
    year: 2018
    isbn: "978-1138627000"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 时间性抗锯齿（TAA）

## 概述

时间性抗锯齿（Temporal Anti-Aliasing，TAA）是一种通过跨多个渲染帧累积亚像素采样信息来消除锯齿的技术。其核心思路是：单帧内只在像素内部的一个偏移位置采样，但通过将当前帧与历史帧混合，等效实现了在同一像素内多点采样的效果。这与MSAA在单帧内同步完成多次采样的方案截然不同。

TAA由Crytek工程师在2011年前后将其引入实时渲染流水线，并于2014年《孤岛危机3》等游戏中大规模普及。传统的SSAA和MSAA的显存与带宽开销随着分辨率增加而线性增长，而TAA的额外开销主要是一张历史帧缓冲，在1080p下仅约8MB（RGBA16F格式），使其成为现代延迟渲染管线中最具性价比的抗锯齿方案。

TAA在游戏引擎中的地位之所以特殊，是因为它既能平滑几何边缘的锯齿，也能改善延迟渲染中难以处理的着色层次锯齿（Shading Aliasing），这是MSAA无法解决的问题。Unreal Engine 4从4.9版本起将TAA设为默认抗锯齿方案，Unity的HDRP渲染管线同样以TAA为首选。

---

## 核心原理

### 亚像素抖动（Subpixel Jitter）

每一帧渲染前，TAA将投影矩阵的平移分量在X和Y方向上施加一个微小偏移，使得观察射线在像素内部的落点发生变化。这个偏移量以像素为单位，范围在 [-0.5, +0.5] 之间，称为**抖动偏移（Jitter Offset）**。常用的采样序列是**Halton序列**（基数2和基数3），因为它的低差异性（Low-Discrepancy）保证了N帧累积后采样点在像素面积内分布均匀，不会出现聚簇。一个标准的8帧Halton序列在X方向的偏移值依次约为：0.5, 0.25, 0.75, 0.125, 0.625, 0.375, 0.875, 0.0625。

投影矩阵偏移的具体做法是在NDC空间中修改矩阵的 `[2][0]` 和 `[2][1]` 分量（OpenGL约定）：

```
P[2][0] += jitterX * (2.0 / screenWidth)
P[2][1] += jitterY * (2.0 / screenHeight)
```

抖动操作发生在投影阶段，对场景中所有物体均匀生效，不需要修改任何几何数据。

### 历史帧重投影（History Reprojection）

当前帧的像素在上一帧中可能对应不同的屏幕坐标，TAA必须将历史帧的颜色"拉回"到正确位置，这一步称为**重投影（Reprojection）**。对于静态场景，重投影可以利用当前帧的深度缓冲重建世界空间位置，再乘以上一帧的视图投影矩阵得到历史UV坐标。对于运动物体，则必须使用**速度缓冲（Velocity Buffer）**直接存储每个像素的屏幕空间运动向量，精度通常为RG16F格式。

重投影误差是历史帧质量的关键瓶颈。若历史UV采样到场景中实际不连续的区域（如遮挡边界），则会引入错误颜色，即**鬼影（Ghosting）**问题。

### 历史帧混合与颜色裁剪（Blending & Color Clipping）

TAA的混合公式为指数移动平均（EMA）：

```
Output = lerp(History, Current, α)
```

其中 α 通常取 **0.05 至 0.1**，对应历史帧权重约为90%~95%。较小的 α 使画面更平滑但响应运动更慢；较大的 α 响应快但累积帧数不足导致锯齿可见。

仅靠重投影无法完全避免颜色错误，因此现代TAA实现均加入**颜色裁剪（Color Clipping / Variance Clipping）**步骤：统计当前像素3×3邻域内的颜色均值 μ 和标准差 σ，将历史颜色裁剪到 [μ - γσ, μ + γσ] 的AABB包围盒内（γ 常取1.0），强制历史帧颜色不偏离当前帧局部颜色统计范围，以此抑制鬼影。颜色空间建议在**YCoCg空间**下执行裁剪，因为该空间的色度分量与亮度分量正交，裁剪效果更加均匀。

---

## 实际应用

**静态场景中的几何边缘抗锯齿**：对于不移动的场景（如室内墙角），TAA在8帧后等效于8倍的亚像素SSAA，边缘质量接近离线渲染效果。Unreal Engine的TAA默认累积8个Halton采样点，正是基于这一原理。

**延迟渲染下的高光锯齿**：金属材质的高频高光在逐像素着色时产生闪烁（Temporal Aliasing），MSAA对此无效，而TAA的历史帧混合能将多帧高光采样平均，显著降低闪烁感。

**与DLSS/FSR的结合**：NVIDIA DLSS 2.0的上采样核心本质上是带学习权重的TAA，它将历史帧重投影和当前帧低分辨率输入送入神经网络，输出超分辨率结果。TAA的抖动模式（Jitter Pattern）必须与DLSS的输入格式匹配，否则网络无法正确解码亚像素信息。

---

## 常见误区

**误区一：TAA只是在帧之间做简单平均**。实际上，TAA的混合权重 α 是固定指数衰减，而非等权平均。若为等权平均（均匀累积），则第N帧的历史权重为 1/N，导致N增大后新信息完全被压制，画面无法响应场景变化。指数移动平均使得有效记忆帧数约为 1/α，当 α=0.1 时有效记忆约10帧，在稳定性与响应速度间取得平衡。

**误区二：TAA的锯齿消除效果与MSAA等价**。TAA消除的锯齿类型包含着色锯齿（MSAA做不到），但TAA对透明物体（如植被、铁丝网）的效果远不如MSAA稳定，因为透明物体的Alpha覆盖信息很难通过运动向量正确重投影，常导致透明边缘出现半透明拖尾。

**误区三：关闭速度缓冲可以节省带宽**。若场景中存在骨骼动画角色或粒子系统，缺少速度缓冲将使这些运动物体的重投影退化为单纯依赖深度的静态重投影，导致运动角色身上产生严重鬼影，α 被迫调大以减少鬼影，反而破坏整体画质。

---

## 知识关联

TAA以**抗锯齿概述**中的采样理论为基础——奈奎斯特定理规定了像素网格对高频信号的采样极限，TAA通过时间维度扩展有效采样率来突破该极限。学习TAA之后，需要重点研究**TAA鬼影**（重投影失败的成因与抑制算法）和**TAA锐度**（EMA导致的低通滤波效应及锐化补偿）这两个TAA特有的质量问题。**速度缓冲**是TAA动态场景支持的必要组件，其填充正确性直接决定运动物体的重投影质量。**抖动模式**的选择（Halton、R2序列、蓝噪声序列）影响TAA在不足帧数时的收敛均匀度，而**DLSS**则是在TAA框架上引入神经网络权重学习后的进化形态，理解TAA是学习DLSS工作原理的前提。