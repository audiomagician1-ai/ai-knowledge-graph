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
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 速度缓冲

## 概述

速度缓冲（Velocity Buffer，也称 Motion Vector Buffer）是一种全屏幕纹理，存储场景中每个像素在屏幕空间的二维运动向量，单位通常为像素/帧或归一化屏幕坐标的位移量。它记录的是从上一帧到当前帧，某个表面点在屏幕上的位置偏移 `(Δu, Δv)`，而非三维世界中的速度。

该技术的广泛应用始于 2010 年代中期，随着 TAA（时序抗锯齿）成为主流而被纳入标准渲染管线。Unreal Engine 4 在 2014 年将 Velocity Buffer 作为 TAA 的基础设施正式引入，此后几乎所有主流实时渲染引擎都采用相同的 R16G16 半精度浮点格式存储运动向量，以平衡精度与带宽消耗。

速度缓冲的重要性在于它将"时间信息"以空间化的方式写入 G-Buffer，使得 TAA 的历史帧重投影和运动模糊（Motion Blur）的方向与长度计算都能从同一张纹理中读取数据，避免重复推导，降低 GPU 计算成本。

---

## 核心原理

### Per-Pixel 速度的数学推导

速度向量通过比较当前帧与上一帧的裁剪空间坐标得出。对于静态几何体，只需考虑摄像机运动；对于蒙皮或刚体动画，还需将上一帧的骨骼变换矩阵传入顶点着色器。

具体公式为：

```
velocity = (NDC_current.xy / NDC_current.w) - (NDC_prev.xy / NDC_prev.w)
```

其中 `NDC_current` 由当前帧的 MVP 矩阵变换顶点得到，`NDC_prev` 由上一帧的 MVP 矩阵（`prevModelMatrix × prevViewProjection`）变换**同一顶点的世界空间位置**得到。结果从 NDC 的 `[-1, 1]` 范围转换到 `[0, 1]` 的 UV 空间后写入 Velocity Buffer：

```
uv_velocity = velocity * 0.5
```

### 静态像素的特殊处理

当场景中大多数像素属于静态物体且摄像机也静止时，运动向量全部为零向量。引擎通常会清除 Velocity Buffer 时写入一个"无效标记"（如 `(0.5, 0.5)` 表示零偏移的 UV 编码），TAA 和运动模糊的采样着色器通过判断该标记跳过历史帧重投影，直接使用当前帧数据，节省带宽。

部分引擎（如 Unity HDRP）采用 Stencil 标记静态物体像素，在 Velocity Pass 中仅绘制运动物体的覆盖区域，Velocity Buffer 的其余像素保持摄像机运动产生的统一背景向量，进一步减少不必要的绘制调用。

### 与 TAA 的共享机制

TAA 在历史帧重投影阶段读取当前像素的运动向量，将采样坐标反推到上一帧的位置：

```
uv_history = uv_current - velocity_uv
```

如果不使用 Velocity Buffer 而是仅依赖相机矩阵重投影，则无法处理蒙皮动画角色、粒子系统等动态物体，这类像素会出现"重影"（Ghosting）。Velocity Buffer 正是解决动态物体 TAA 残影的关键数据来源。

运动模糊读取同一张 Velocity Buffer，将向量长度乘以曝光时间系数（通常可配置为 `0.5 × shutter_speed / frame_time`），得出径向模糊的采样步长与方向，完成图像空间的方向性模糊效果。两个效果共享同一次 G-Buffer Pass 的写入成本，是延迟渲染管线中典型的数据复用设计。

---

## 实际应用

**蒙皮角色的运动向量**：角色骨骼动画在每帧顶点着色器中需要同时计算当前帧骨骼矩阵和上一帧骨骼矩阵对顶点的变换结果，分别用于输出当前裁剪坐标和历史裁剪坐标。UE5 的 Nanite 系统对此专门维护了一套"Previous Position Buffer"，以支持百万级几何体的逐像素速度写入。

**粒子系统**：粒子通常在 CPU 或 Compute Shader 上模拟，其上一帧世界坐标可存储在粒子属性中，顶点着色器读取该属性并完成历史裁剪坐标计算，写入 Velocity Buffer。若粒子系统省略此步骤，TAA 会在粒子运动轨迹处产生明显的彩色重影。

**UI 与全屏效果**：HUD 元素不应写入 Velocity Buffer（或写入零向量），否则 TAA 会对 UI 边缘进行错误的历史混合，导致文字发虚。实现上通常将 UI 在 TAA 之后的独立 Pass 中合成。

---

## 常见误区

**误区一：速度缓冲存储的是三维世界空间速度**。实际上 Velocity Buffer 存储的是二维屏幕空间偏移，单位是 UV 坐标差值，不含深度分量。同一个物体在屏幕边缘与屏幕中心产生的屏幕空间向量长度不同，即使其三维速度完全相同，这是透视投影的正常结果。

**误区二：静态物体不需要写入 Velocity Buffer**。当摄像机发生平移或旋转时，静态物体同样有非零的屏幕空间运动向量，此时需要依据摄像机的当前帧与上一帧 ViewProjection 矩阵差异来计算背景运动向量，否则 TAA 会对静态背景产生严重的模糊或重影。通常的做法是全场景统一写入 Velocity Pass，或至少对静态物体写入摄像机运动产生的向量。

**误区三：Velocity Buffer 精度越高越好**。R16G16 半精度（每通道 16 位浮点）在绝大多数场景中已足够，其可表示的最小 UV 偏移约为 `6×10⁻⁵`，对于 1080p 分辨率对应约 0.065 像素的精度，完全满足 TAA 和运动模糊的需求。使用 R32G32 全精度会使带宽翻倍，在移动平台上造成不可忽视的性能损耗。

---

## 知识关联

**前置概念 TAA** 是 Velocity Buffer 最主要的消费者。TAA 的核心算法——历史帧累积与重投影——必须依赖 Velocity Buffer 提供的逐像素运动信息才能正确处理动态物体，否则只能通过相机矩阵估算重投影，无法解决动画角色的重影问题。

Velocity Buffer 生成的 Velocity Pass 通常插入在 G-Buffer Pass 之后、光照计算之前，是延迟渲染管线中除深度缓冲和法线缓冲之外最早生成的全屏数据之一。理解 Velocity Buffer 的写入时机和格式约定，是进一步学习 TAA 调试工具（如在引擎中可视化 Motion Vector 覆盖层）和实现自定义运动模糊算法的直接基础。