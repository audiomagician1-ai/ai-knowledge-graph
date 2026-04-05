---
id: "cg-texture-unit"
concept: "纹理单元"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 2
is_milestone: false
tags: ["硬件"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 纹理单元

## 概述

纹理单元（Texture Mapping Unit，简称 TMU）是 GPU 内部专门负责纹理采样与过滤操作的硬件模块。它的主要职责是：根据片元着色器传入的纹理坐标（UV 坐标），从显存中读取对应的纹理像素（texel），并通过插值或各向异性过滤算法输出最终颜色值。每个 TMU 每个时钟周期最多可处理 4 个 texel 的双线性过滤操作，这一吞吐量指标直接影响渲染管线的填充率上限。

TMU 的硬件化起源于 1996 年 3dfx 推出的 Voodoo Graphics 芯片。在此之前，纹理映射完全由 CPU 软件光栅化完成，速度极慢。Voodoo Graphics 将双线性过滤和透视校正纹理寻址固化进专用硅片电路，使得 640×480 分辨率下的纹理映射速度提升超过 10 倍。现代 GPU 中，每个流式多处理器（SM）通常绑定 4 到 8 个 TMU，NVIDIA RTX 4090 全卡共配置 576 个 TMU。

理解 TMU 的工作原理对优化 GPU 着色器性能至关重要。当着色器的纹理采样调用（`texture()` 或 `tex2D()`）过于密集，或者 UV 坐标访问模式造成缓存缺失时，TMU 会成为渲染管线的瓶颈，导致着色器单元因等待纹理数据而停滞（stall）。

---

## 核心原理

### 纹理寻址与 MIP 级别选择

TMU 处理纹理采样的第一步是计算 MIP 层级（LOD，Level of Detail）。TMU 通过对相邻像素的 UV 偏导数 ∂u/∂x、∂v/∂x、∂u/∂y、∂v/∂y 进行计算，得出 LOD 值：

$$\lambda = \log_2 \left(\max\left(\sqrt{\left(\frac{\partial u}{\partial x}\right)^2+\left(\frac{\partial v}{\partial x}\right)^2},\ \sqrt{\left(\frac{\partial u}{\partial y}\right)^2+\left(\frac{\partial v}{\partial y}\right)^2}\right)\right)$$

当 λ > 0 时，TMU 从更小的 MIP 层读取数据以避免走样；当 λ < 0 时，从原始分辨率层放大采样。这一计算在 2×2 像素的 Quad 粒度上统一进行，因此着色器中若在分支内部调用 `texture()`，整个 Quad 依然会计算所有分支的 LOD。

### 各向异性过滤的硬件实现

各向异性过滤（Anisotropic Filtering，AF）是 TMU 中最耗资源的操作。标准双线性过滤对每个采样点只读取 4 个 texel，而 AF 通过沿纹理空间中最大拉伸方向放置一组各向同性采样探针来近似椭圆形采样区域。以 8× AF 为例，TMU 沿主轴方向最多放置 8 个双线性采样点，意味着单次纹理调用最多需要读取 8×4 = 32 个 texel。NVIDIA 的实现将这些探针的间距和数量动态裁剪，使得对接近正方形映射区域的多边形只触发 1 到 2 个探针，从而在大多数场景下节省带宽。16× AF 的理论带宽消耗是双线性过滤的 4 倍，但由于动态裁剪，实际消耗通常在 2 倍以内。

### TMU 缓存架构与命中优化

每个 TMU 配备一块专用的 L1 纹理缓存，容量通常为 16 KB 至 32 KB（例如 AMD RDNA 2 架构中每个 CU 有 16 KB 纹理 L1 缓存）。纹理数据在缓存中以 Morton 码（Z 曲线）排列，而非行优先顺序，目的是使空间上相邻的 texel 在内存地址上也相邻，从而提升二维局部性。当 UV 坐标呈线性扫描方向访问时，每 16 KB 缓存行可覆盖约 64×64 的 texel 块（4 字节/texel 时），命中率可超过 90%。一旦 UV 坐标随机跳跃（如立方体贴图的六面切换），L1 缺失率将急剧上升，TMU 需要穿透到 L2 或显存，延迟从约 40 个周期增加到 200 个周期以上。

---

## 实际应用

**地形渲染中的各向异性优化**：在第一人称视角的地形场景中，地面多边形对摄像机成极小倾斜角，UV 在屏幕空间被高度拉伸。此时若只使用三线性过滤，地面纹理会出现严重模糊带。开启 4× AF 后，TMU 识别到单方向拉伸比大于 2:1，自动沿地面延伸方向增加采样探针，地面细节清晰度显著提升，GPU 纹理吞吐量指标（TMU Busy%）此时通常从 30% 上升至 60%。

**纹理图集与缓存命中**：游戏引擎（如 Unreal Engine）将数百张小纹理打包为一张 4096×4096 的纹理图集（Texture Atlas），目的之一是减少 TMU 切换不同纹理对象的状态开销，同时使同一帧内大量相近 UV 区域的采样集中在同一块 L1 缓存行内，将平均纹理延迟降低约 20%—40%。

**计算着色器中的显式 LOD 控制**：当在计算着色器中使用 `textureLod()` 替代 `texture()`，手动指定 LOD = 0，可绕过 TMU 对偏导数的自动计算，节省约 8 个周期的 LOD 计算开销，适用于全屏后处理等不需要 MIP 层的场景。

---

## 常见误区

**误区一：更多 TMU 等于更高帧率**。TMU 数量决定纹理吞吐量上限，但如果着色器本身是算术计算瓶颈（ALU bound）而非纹理采样瓶颈，增加 TMU 对帧率没有任何影响。判断是否 TMU bound 需要借助 GPU 性能计数器中的 "Texture Unit Utilization" 指标，该值超过 80% 才意味着 TMU 是实际瓶颈。

**误区二：各向异性过滤开销固定为 N 倍**。由于 TMU 内置了动态各向异性探针裁剪逻辑，8× AF 的实际带宽消耗并非恰好是双线性的 8 倍。对于正视摄像机的正面多边形，AF 的额外开销可能接近于零，因为拉伸比低于触发阈值（通常为 1.5:1）时，AF 退化为标准双线性采样。

**误区三：纹理压缩格式不影响 TMU 性能**。BC7 格式（每像素 1 字节）相比未压缩 RGBA8（每像素 4 字节）可将 L1 纹理缓存有效容量提升 4 倍，使相同访问模式下的缓存命中率显著提高。TMU 硬件原生支持对 BC1—BC7、ASTC 等格式的实时解压，解压延迟约为 2—4 个周期，远低于因缓存缺失造成的 200 个周期延迟。

---

## 知识关联

学习纹理单元需要先掌握 **GPU 硬件管线**中的光栅化阶段：TMU 的工作发生在片元着色器执行期间，片元着色器由 SM（Streaming Multiprocessor）调度，TMU 是 SM 发出纹理采样指令后的专用响应单元。不理解 SM 的 warp 调度模型，就无法解释为何 TMU stall 会触发 warp 切换而非整个 SM 停滞。

纹理单元的下游概念是 **纹理缓存**（Texture Cache）的层次结构细节——包括 L2 共享缓存的分区策略、纹理与渲染目标之间的缓存一致性问题，以及 GDDR/HBM 带宽如何与 TMU 填充率共同决定纹理密集型场景的性能上限。TMU 的 L1 缓存是纹理缓存体系的起点，理解其 Morton 码布局和 16 KB 容量限制，是进一步分析 L2 纹理缓存缺失模式的基础。