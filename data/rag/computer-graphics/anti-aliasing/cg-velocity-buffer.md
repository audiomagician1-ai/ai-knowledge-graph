---
id: "cg-velocity-buffer"
concept: "速度缓冲"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 2
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
  - type: "academic"
    author: "Yang, L., Nehab, D., Sander, P. V., Sitthi-amorn, P., Lawrence, J., & Seitz, S. M."
    year: 2009
    title: "Amortized Supersampling"
    venue: "ACM Transactions on Graphics (SIGGRAPH Asia 2009), 28(5)"
  - type: "technical"
    author: "Karis, B."
    year: 2014
    title: "High Quality Temporal Supersampling"
    venue: "SIGGRAPH 2014 Advances in Real-Time Rendering Course, Epic Games"
  - type: "book"
    author: "Akenine-Möller, T., Haines, E., & Hoffman, N."
    year: 2018
    title: "Real-Time Rendering, 4th Edition"
    venue: "CRC Press"
  - type: "technical"
    author: "Jimenez, J."
    year: 2016
    title: "Filmic SMAA: Sharp Morphological and Temporal Antialiasing"
    venue: "SIGGRAPH 2016 Advances in Real-Time Rendering Course, Activision"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 速度缓冲

## 概述

速度缓冲（Velocity Buffer，也称 Motion Vector Buffer）是一种全屏幕纹理，存储场景中每个像素在屏幕空间的二维运动向量，单位通常为像素/帧或归一化屏幕坐标的位移量。它记录的是从上一帧到当前帧，某个表面点在屏幕上的位置偏移 $(\Delta u, \Delta v)$，而非三维世界中的速度。这一区别至关重要：速度缓冲本质上是一张"屏幕空间位移图"，而非物理意义上的速度场。

该技术的广泛应用始于 2010 年代中期，随着 TAA（时序抗锯齿，Temporal Anti-Aliasing）成为主流而被纳入标准渲染管线。Karis（2014）在 SIGGRAPH 课程中系统阐述了 Velocity Buffer 作为 TAA 基础设施的核心地位，同年 Unreal Engine 4.4 将其作为 TAA 的标准组件正式引入并公开了实现细节。此后几乎所有主流实时渲染引擎都采用相同的 R16G16 半精度浮点格式存储运动向量，以平衡精度与带宽消耗。Unity HDRP 在 2018 年（Unity 2018.1）同样将 Velocity Buffer 纳入其延迟渲染管线的标准 G-Buffer 布局，并将其标记为 RT2 的第四个通道或独立渲染目标，取决于平台带宽预算。

速度缓冲的重要性在于它将"时间信息"以空间化的方式写入 G-Buffer，使得 TAA 的历史帧重投影和运动模糊（Motion Blur）的方向与长度计算都能从同一张纹理中读取数据，避免重复推导，降低 GPU 计算成本。Yang 等人（2009）在时序超采样的早期研究中已指出，逐像素运动向量是实现高质量时序累积的必要条件，这一结论为后续引擎实现提供了重要的理论依据。Akenine-Möller 等人（2018）在《Real-Time Rendering》第四版中将 Velocity Buffer 列为现代延迟渲染管线中继深度缓冲之后最关键的辅助缓冲之一。

---

## 核心数学原理

### Per-Pixel 速度的推导公式

速度向量通过比较当前帧与上一帧的裁剪空间坐标得出。对于静态几何体，只需考虑摄像机运动；对于蒙皮或刚体动画，还需将上一帧的骨骼变换矩阵传入顶点着色器。

具体公式为：

$$\mathbf{v} = \frac{\mathbf{p}_{\text{current}}.xy}{\mathbf{p}_{\text{current}}.w} - \frac{\mathbf{p}_{\text{prev}}.xy}{\mathbf{p}_{\text{prev}}.w}$$

其中 $\mathbf{p}_{\text{current}}$ 由当前帧的 MVP 矩阵（$M_{\text{current}} \times VP_{\text{current}}$）变换顶点得到，$\mathbf{p}_{\text{prev}}$ 由上一帧的 MVP 矩阵（$M_{\text{prev}} \times VP_{\text{prev}}$）变换**同一顶点的世界空间位置**得到。结果从 NDC 的 $[-1, 1]$ 范围转换到 $[0, 1]$ 的 UV 空间后写入 Velocity Buffer：

$$\mathbf{v}_{\text{uv}} = \mathbf{v} \times 0.5$$

TAA 在历史帧重投影阶段利用该向量将采样坐标反推到上一帧位置：

$$\mathbf{uv}_{\text{history}} = \mathbf{uv}_{\text{current}} - \mathbf{v}_{\text{uv}}$$

运动模糊的采样步长则进一步由向量长度与曝光时间系数共同决定，步长为 $|\mathbf{v}_{\text{uv}}| \times k$，其中 $k = 0.5 \times t_{\text{shutter}} / t_{\text{frame}}$，通常在渲染设置中可按需配置。对于 60fps 的游戏，$t_{\text{frame}} \approx 16.67\text{ms}$，若快门时间 $t_{\text{shutter}}$ 设为半帧（约 8.33ms），则 $k = 0.25$，运动模糊强度为速度向量长度的四分之一。

### 精度分析与格式选择

R16G16 半精度浮点格式每通道 16 位，可表示的最小 UV 偏移约为 $6 \times 10^{-5}$。以 1920×1080 分辨率为例，该精度对应约 $6 \times 10^{-5} \times 1920 \approx 0.115$ 像素，完全满足 TAA 和运动模糊的需求。在 4K 分辨率（3840×2160）下，同样的半精度格式对应约 $6 \times 10^{-5} \times 3840 \approx 0.23$ 像素，依然处于亚像素精度范围内，不会引入可见误差。

相比之下，R32G32 全精度格式会使带宽从约 8 MB/帧（1080p，60fps）翻倍至 16 MB/帧，在移动平台上造成不可忽视的功耗与性能损耗。ARM Mali GPU 优化指南明确指出，在 Velocity Buffer 采用 R32G32 格式时，带宽压力会导致 Midgard 及 Bifrost 架构上的帧率下降约 5%~8%，因此在 iOS/Android 的高质量渲染方案中不推荐使用全精度 Velocity Buffer。

### 抖动补偿与子像素修正

TAA 通常配合 Halton 序列抖动（Jitter）使用，在每帧渲染时对投影矩阵施加亚像素偏移，使采样点在 $2 \times 2$、$4 \times 4$ 或 $8 \times 8$ 的模式内逐帧轮换。此时 Velocity Buffer 的写入必须将 Jitter 偏移纳入补偿，否则历史帧重投影坐标会始终偏移半个像素以上，导致 TAA 产生系统性模糊。补偿公式为：

$$\mathbf{v}_{\text{corrected}} = \mathbf{v}_{\text{uv}} + \frac{\mathbf{j}_{\text{current}} - \mathbf{j}_{\text{prev}}}{2}$$

其中 $\mathbf{j}_{\text{current}}$ 和 $\mathbf{j}_{\text{prev}}$ 分别为当前帧和上一帧的 Jitter 偏移量（NDC 单位）。Jimenez（2016）在其 SMAA T2x 方案中对该补偿步骤有详细的数学推导，指出忽略 Jitter 补偿是 TAA 实现中最常见的初级错误之一。

---

## 静态像素的特殊处理

当场景中大多数像素属于静态物体且摄像机也静止时，运动向量全部为零向量。引擎通常在清除 Velocity Buffer 时写入一个"无效标记"（如 $(0.5, 0.5)$ 表示零偏移的 UV 编码），TAA 和运动模糊的采样着色器通过判断该标记跳过历史帧重投影，直接使用当前帧数据，节省带宽。

部分引擎（如 Unity HDRP 2020.2 及以后版本）采用 Stencil 标记静态物体像素，在 Velocity Pass 中仅绘制运动物体的覆盖区域，Velocity Buffer 的其余像素保持摄像机运动产生的统一背景向量，进一步减少不必要的绘制调用。实测数据显示，在静态场景占主体（约 80% 像素为静态）的城市场景中，该优化可将 Velocity Pass 的 GPU 耗时减少约 30%~40%。

摄像机纯旋转（Pan/Tilt）时的背景运动向量可以完全由 CPU 端的矩阵差分计算，并通过一次 Full-Screen Triangle 的 Compute Pass 批量写入，无需为静态网格物体发起任何 Draw Call。UE5 的实现正是采用这一策略：在场景中无动态物体覆盖的区域，完全由 Compute Shader 填充摄像机运动向量，将静态背景的 Velocity Pass CPU 提交开销降至接近零。

---

## 实际应用场景

**蒙皮角色的运动向量**：角色骨骼动画在每帧顶点着色器中需要同时计算当前帧骨骼矩阵和上一帧骨骼矩阵对顶点的变换结果，分别用于输出当前裁剪坐标和历史裁剪坐标。

例如，一个拥有 60 根骨骼的标准人形角色，顶点着色器需要额外传入 60 个 4×4 的上一帧骨骼变换矩阵（或以双四元数压缩传输，每骨骼从 64 字节压缩至 32 字节），以完成逐顶点的历史坐标计算。UE5 的 Nanite 系统对此专门维护了一套"Previous Position Buffer"，以支持百万级几何体的逐像素速度写入，该方案在 2022 年 GDC 的 Nanite 技术分享中有详细说明。在 Nanite 的虚拟几何体管线中，Previous Position Buffer 以顶点索引为键值进行增量更新，每帧只重新上传发生变化的顶点位置，而非全量复制，这使得即使场景中有 1000 万个顶点，Velocity Pass 的内存带宽消耗也能控制在合理范围内。

**粒子系统**：粒子通常在 CPU 或 Compute Shader 上模拟，其上一帧世界坐标可存储在粒子属性中，顶点着色器读取该属性并完成历史裁剪坐标计算，写入 Velocity Buffer。

案例：一个火焰粒子系统若以每帧平均 500 个活跃粒子、每粒子覆盖约 16×16 像素计算，在 1080p 下约有 4% 的屏幕像素受其影响；若粒子系统省略速度写入步骤，TAA 会在这些像素处产生明显的彩色重影（Ghosting），尤其在粒子运动速度超过 10 像素/帧时视觉效果极差。彩色重影的产生机制是：TAA 的历史帧混合权重默认约为 0.9，当无法正确重投影时，历史帧颜色会以 90% 的权重叠加到当前帧，导致残影持续约 10 帧才完全消散（$0.9^{10} \approx 0.35$，即 10 帧后历史帧残余约 35%）。

**UI 与全屏效果**：HUD 元素不应写入 Velocity Buffer（