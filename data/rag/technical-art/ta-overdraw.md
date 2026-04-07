# Overdraw控制

## 概述

Overdraw（过度绘制）是指屏幕上同一像素在单帧渲染中被片元着色器（Fragment Shader）写入颜色值超过一次的现象。若某像素在一帧内被写入 $n$ 次，则该像素的 Overdraw 倍率记为 $n\times$。在移动端 GPU（如 ARM Mali-G76、Qualcomm Adreno 640）采用的 Tile-Based Deferred Rendering（TBDR）架构下，帧缓冲存储于片上 SRAM，每次像素写入都消耗带宽预算；当 Overdraw 倍率超过 2.5×，芯片热功耗显著上升，帧率在高通骁龙 855 等主流平台上可下降 15%–30%（Qualcomm Adreno GPU Performance Counters 白皮书，2019）。

透明物体（Alpha Blend）、粒子特效与 UI 控件是产生 Overdraw 的三大来源，其共同机制是**不写入深度缓冲（Depth Write Off）或主动关闭 Early-Z 剔除**，使 GPU 无法在光栅化阶段提前丢弃被遮挡片元。与之对比，不透明物体在开启 Early-Z 后，被遮挡片元在着色器执行前即被硬件丢弃，理想情况下 Overdraw 可接近 1×。

Overdraw 问题因 2012–2014 年间 Adreno 200/300 系列低功耗 GPU 大量搭载廉价 Android 手机而引发行业广泛重视。Unity Technologies 在 2013 年版 Scene 视图中正式引入"Overdraw"可视化着色模式，颜色越趋近亮白表示该像素重绘次数越多；Unreal Engine 4 通过 **Optimization Viewmode → Shader Complexity** 以红色热力图呈现类似信息。业界普遍接受的优化目标是：移动端全帧平均 Overdraw ≤ 2×，局部粒子区域峰值 ≤ 4×。

---

## 核心原理

### 2.1 Early-Z 测试与透明渲染的本质冲突

现代 GPU 渲染管线在顶点着色器之后、片元着色器之前存在一个硬件级 Early-Z（也称 Hi-Z）阶段。其判断逻辑为：

$$
\text{若 } z_{\text{frag}} \geq z_{\text{buffer}} \implies \text{丢弃片元（无需执行 Fragment Shader）}
$$

丢弃操作在着色器启动之前完成，节省的计算量等于：

$$
\text{节省成本} = N_{\text{丢弃}} \times C_{\text{FS}}
$$

其中 $N_{\text{丢弃}}$ 为被 Early-Z 剔除的片元数，$C_{\text{FS}}$ 为单个片元着色器的周期开销。

然而，Alpha Blend 透明渲染依赖混合方程：

$$
C_{\text{out}} = \alpha_{\text{src}} \cdot C_{\text{src}} + (1 - \alpha_{\text{src}}) \cdot C_{\text{dst}}
$$

此方程要求 $C_{\text{dst}}$（已写入帧缓冲的颜色）在当前片元执行时必须已正确存在，因此透明物体必须**从后向前**排序提交（Painter's Algorithm），且不得写入深度缓冲。GPU 无法对透明层启用 Early-Z，每一透明片元必须完整执行着色器，这是透明渲染天然高 Overdraw 的根本原因（Akenine-Möller et al., *Real-Time Rendering*, 4th ed., 2018, Chapter 5.4）。

### 2.2 TBDR 架构下 Overdraw 的放大效应

传统桌面 GPU 采用 Immediate Mode Rendering（IMR），帧缓冲位于显存（DRAM），每次写入产生约 10–50ns 延迟但可被高带宽掩盖。移动端 TBDR 将屏幕分割为 16×16 或 32×32 像素的 Tile，每个 Tile 在片上 SRAM（约 256KB）中完成局部光栅化。当 Overdraw 倍率高时，同一 Tile 内的混合读写次数激增，片上缓存溢出后被迫写回主存，产生额外的主存带宽开销。

具体而言，Arm Mali 架构的 Transaction Elimination（TE）特性可在帧间检测到内容未变化的 Tile 并跳过写回，但透明层的持续变化（如粒子动画）使 TE 命中率接近 0%，意味着每帧都必须完整刷新所有受影响 Tile 到主存（ARM Mali GPU Best Practices Developer Guide，2021，Section 3.2）。

### 2.3 UI 层的 Overdraw 叠加机制

Unity 的 uGUI 系统中，Canvas 在默认"Screen Space - Overlay"模式下于三维场景渲染完成后**额外增加一个全屏渲染 Pass**。若场景本身已产生 2× Overdraw，UI 层的全屏背景图再叠加一次，仅此一项即将覆盖区域的 Overdraw 推至 3×。更危险的是 `Canvas.Mask` 组件：每使用一个 Mask，Unity 会产生两次额外的 Stencil Pass（写入与清除），在 Mask 范围内额外增加 2 次像素写入。一个带有 3 层嵌套 Mask 的背包界面，在其覆盖区域内 Overdraw 贡献可达 +6×，叠加场景基础绘制后轻松超过 8×。

---

## 关键检测方法与量化公式

### 3.1 Overdraw 倍率的量化

设屏幕分辨率为 $W \times H$，帧内所有三角形光栅化产生的总片元数为 $F_{\text{total}}$，则平均 Overdraw 倍率为：

$$
\text{Overdraw}_{\text{avg}} = \frac{F_{\text{total}}}{W \times H}
$$

例如，在 1920×1080（约 207 万像素）的屏幕上，若单帧总片元数为 830 万，则平均 Overdraw = $\frac{8.3 \times 10^6}{2.07 \times 10^6} \approx 4.0\times$，已超出移动端可接受上限。

### 3.2 工具链检测

| 工具 | 平台 | 关键指标 |
|------|------|----------|
| Unity Scene 视图 Overdraw 模式 | Editor | 视觉热力图（亮白 = 高重绘） |
| Unity Frame Debugger | Editor/Device | 逐 Draw Call 片元覆盖范围 |
| Arm Mali Graphics Debugger | Android/Mali | `Fragment Active Cycles`、`Tiles` |
| Qualcomm Snapdragon Profiler | Android/Adreno | `SP ALU Busy`、`Overdraw` 直接计数器 |
| Xcode GPU Frame Capture | iOS/Apple GPU | `Overdraw` 视图（Metal 专属） |
| RenderDoc | 多平台 | 可手动计算层叠片元数 |

Snapdragon Profiler 的 Overdraw 计数器直接输出每帧每像素平均写入次数，是目前针对 Adreno GPU 最精确的量化手段。

---

## 实际优化方法

### 4.1 透明粒子的 Alpha Test 替代方案

对于烟雾、气泡等边缘羽化不严格的粒子，可将 Alpha Blend 替换为 **Alpha Test（cutout）** 模式：设定一个 cutoff 阈值（如 0.5），低于该值的片元直接 discard。Alpha Test 可写入深度缓冲，后续不透明物体对该粒子区域可触发 Early-Z，从而打破透明层必须全量执行的约束。代价是边缘出现锯齿——可结合 **Alpha to Coverage**（需 MSAA 支持）在保留 Early-Z 优势的同时缓解锯齿问题（Persson, *Closer Look at Alpha to Coverage*, GPU Pro, 2012）。

### 4.2 粒子特效的几何压缩

粒子 Billboard 面片普遍使用 Quad（2 个三角形），但大量粒子叠加时，Quad 边角的透明区域仍会光栅化为片元（即便 Alpha 为 0 也会启动着色器）。将 Billboard 改为**八边形或六边形 Mesh**，可将无效透明像素光栅化面积减少约 27%–36%（对比正方形 Quad），直接降低片元生成总量，进而降低 Overdraw。

案例：某移动战斗游戏的中型爆炸特效使用 40 个 Quad 粒子，在 720p 屏幕中央区域产生峰值 12× Overdraw。将 Quad 替换为八边形 Mesh 后，片元数下降 31%，峰值 Overdraw 降至 8.3×，GPU 热功耗下降约 18%。

### 4.3 粒子排序与深度层分离

对于包含不透明粒子（如火星、弹壳）和透明粒子（烟雾、光晕）混合的特效，应将二者拆分为两个 Particle System：不透明粒子使用 Opaque 队列（可触发 Early-Z），透明粒子使用 Transparent 队列。Unity 在同一 Particle System 中无法实现队列分离，强制混用 Transparent 会导致所有粒子丢失 Early-Z 机会。

### 4.4 UI Overdraw 的层级合并策略

- **减少 Canvas 数量**：每个独立 Canvas 是一次独立的渲染 Pass，多 Canvas 嵌套等同于叠加多次全屏绘制。静态 UI 与动态 UI 分离为两个 Canvas（静态 Canvas 触发 Static Batching 只需绘制一次）。
- **避免全屏半透明背景**：将半透明背景图替换为九宫格（9-Slice）边框 + 纯色中心的方案，纯色区域可用一个不透明 Image 覆盖，消除中央大面积的透明层。
- **以 RectMask2D 替代 Mask**：`RectMask2D` 通过裁剪矩形区域（Scissor Rect）实现遮罩，不产生额外 Stencil Pass，Overdraw 贡献为 0，而 `Mask` 组件额外产生 2 次全 Mask 区域片元写入。

### 4.5 不透明物体的渲染排序（Front-to-Back）

不透明队列中，引擎应尽量按**由近及远（Front-to-Back）**顺序提交 Draw Call，使靠近摄像机的物体先写入深度缓冲，后续被遮挡物体的片元在 Early-Z 阶段提前丢弃。Unity 的不透明队列默认已按此原则排序；UE4 通过 Hierarchical-Z（HiZ）缓冲在 GPU 上进行层次深度剔除，可在 GPU 驱动层面进一步减少 Overdraw。

---

## 常见误区

### 5.1 "减少 Draw Call 就能降低 Overdraw"

这是最普遍的误解。Dynamic Batching 将多个 Mesh 合并为一次 Draw Call，降低 CPU 提交开销，但**片元数量完全不变**，被覆盖的像素仍会被写入相同次数。Overdraw 由三角形的屏幕空间覆盖关系决定，与 Draw Call 数量无关。

### 5.2 "粒子数量少所以 Overdraw 不高"

粒子数量与 Overdraw 倍率之间没有线性关系，关键是每个粒子的**屏幕空间投影面积**。10 个铺满半屏的烟雾粒子比 500 个直径 2 像素的火星粒子产生高出数十倍的 Overdraw。

### 5.3 "Alpha Test 比 Alpha Blend 慢"

在桌面 IMR 架构（如 NVIDIA GeForce RTX）上，Alpha Test 中的 `discard` 指令确实会阻止 Early-Z 的 HiZ 更新，有时比 Alpha Blend 更慢。但在移动端 TBDR 架构下，`discard` 不会影响片上 Tile 的排序，而 Alpha Test 可写入深度缓冲从而剔除后续透明片元，**在透明层叠加场景中 Alpha Test 的总体 Overdraw 开销反而更低**（Arm Mali GPU Best Practices，2021，Section 5.1）。

### 5.4 "Overdraw 可视化工具显示绿色就安全"

Unity Overdraw 可视化使用加色混合显示：每层叠加一个半透明白色，颜色越亮 Overdraw 越高。但该工具的颜色对应关系是近似视觉映射，并非精确倍率计数。精确量化必须使用 