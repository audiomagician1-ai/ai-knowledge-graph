# 运动矢量

## 概述

运动矢量（Motion Vector）是一种将像素或像素块在相邻帧之间的二维位移信息编码为纹理贴图的技术，其每个像素的 R、G 通道分别存储水平（U轴）与垂直（V轴）方向的归一化偏移量。在序列帧特效（Flipbook）系统中，运动矢量贴图使渲染引擎无需额外帧数即可在任意子帧位置合成出"虚拟中间帧"，从而消除低帧率序列帧播放时肉眼可见的跳帧抖动（Judder Artifact）。

运动矢量估计的理论根基来自视频编码领域。Block-matching 运动估计算法在 H.264/AVC（ITU-T Rec. H.264, 2003）中被系统化，通过将每宏块的运动向量记录到码流以消除时间冗余，压缩率相比 MPEG-2 提升约 2 倍。游戏特效领域对这一思路的借鉴发生在 2010 年代中后期：Epic Games 于 Unreal Engine 4.20（2018年）正式在粒子材质编辑器中公开了 Motion Vector 纹理支持，配套 `SubUV_Motion_Vector` 材质节点；Unity 在 2019.3 版本中通过 VFX Graph 提供了等效的 FlipBook with Motion Vectors 模块。

一套典型的 60 帧火焰序列帧若以 30fps 播放，每帧停留约 33.3 毫秒，帧切换间隔感知阈值约为 20 毫秒（Watson, 1986, *Temporal sensitivity* in Handbook of Perception and Human Performance）。通过运动矢量引导的双向插值，渲染引擎可将帧切换的视觉不连续性压缩到感知阈值以下，同时保持原始烘焙帧数不变，节省纹理内存。

---

## 核心原理

### 运动矢量贴图的编码格式

运动矢量贴图通常采用 **RG16F**（16位浮点双通道）或 **RG8**（8位无符号整数双通道）格式。以 RG8 为例，其编解码映射关系如下：

$$
\text{offset} = \left(\frac{\text{texel}}{255.0}\right) \times 2.0 - 1.0
$$

其中 texel 值 0 对应偏移 $-1.0$，texel 值 127 对应偏移 $\approx 0$（无运动），texel 值 255 对应偏移 $+1.0$。偏移量单位为归一化 UV 空间，$\pm1.0$ 代表跨越完整纹理宽度/高度。由于大多数流体特效的帧间局部位移约在纹理尺寸的 1%\~8%，RG8 精度在视觉上通常可接受；但对需要追踪高频细节的液体涟漪或烟雾卷积边缘，量化误差会导致撕裂伪影，此时应使用 RG16F（精度达 $1.5 \times 10^{-5}$，约 RG8 的 700 倍）。

### 帧间双向插值算法

设当前播放时间对应序列帧第 $A$ 帧与第 $B$ 帧之间，混合因子 $t \in [0, 1)$，运动矢量贴图为 $\mathbf{M}$，序列帧贴图为 $\mathbf{S}$，则子帧颜色计算公式为：

$$
\mathbf{m} = \text{decode}(\mathbf{M}(uv)) = \mathbf{M}_{raw}(uv) \times 2.0 - 1.0
$$

$$
C_A = \mathbf{S}_A\!\left(uv - \mathbf{m} \cdot t\right)
$$

$$
C_B = \mathbf{S}_B\!\left(uv + \mathbf{m} \cdot (1 - t)\right)
$$

$$
C_{out} = \text{lerp}(C_A,\; C_B,\; t)
$$

关键逻辑在于：采样 $A$ 帧时沿运动方向**反向**偏移 $t$ 倍，采样 $B$ 帧时沿运动方向**正向**偏移 $(1-t)$ 倍。两帧的像素在子帧位置"相向汇聚"，精确近似该时刻的真实位置，从而消除单向插值或简单 `lerp` 带来的半透明重影（Double-image / Ghost Artifact）。当 $t=0$ 时输出完全等于 $A$ 帧，$t \to 1$ 时完全等于 $B$ 帧，连续性得到保证。

### 光流假设与适用边界

上述插值模型成立的前提是**亮度恒常假设**（Brightness Constancy Constraint），即对应像素在相邻帧间颜色不变，只发生位移：

$$
I(x, y, t) = I(x + u, y + v, t + \Delta t)
$$

这一假设由 Horn & Schunck（1981, *Determining optical flow*, Artificial Intelligence, 17(1-3): 185–203）在光流计算理论中正式提出。对于爆炸、火焰等伴随颜色突变的序列帧，该假设在帧间差异较大处失效，导致运动矢量引导的插值出现色彩偏差。实践中通常限制混合因子 $t$ 的有效范围（如仅在 $t \in [0.1, 0.9]$ 内启用运动矢量插值），在帧切换边缘附近退回简单 lerp 以规避伪影。

---

## 关键方法与生成流程

### 方法一：Houdini 速度场直接导出

在 Houdini 的流体模拟（FLIP Solver）完成后，速度场以点属性 `v`（类型为 `vector`）存储于体积或粒子中。通过 **Velocity to Texture** ROP 节点可将每帧速度场烘焙为 EXR 序列，XY 分量归一化后写入 RG 通道。该方式的优点是矢量与物理模拟完全对应，无光流算法的近似误差，缺点是要求原始 Houdini 工程文件存在，无法对已有视频素材追溯生成。

### 方法二：光流算法离线计算

对于直接从渲染序列图像反推运动矢量的场景，常用 **Lucas-Kanade**（Lucas & Kanade, 1981, *An iterative image registration technique with an application to stereo vision*, IJCAI, pp. 674–679）稀疏光流或 **Farnebäck**（Farnebäck, 2003, *Two-Frame Motion Estimation Based on Polynomial Expansion*, SCLDIA, LNCS 2749, pp. 363–370）稠密光流。后者将图像局部区域近似为二次多项式，通过求解多项式系数变化直接得到稠密位移场，在火焰序列帧上的误差（EPE，End-Point Error）约为 0.8\~1.5 像素。

在工具链层面，Adobe After Effects 的 Pixel Motion Blur 效果内部使用稠密光流；Houdini 的 `COP2_MotionBlur`；以及专用工具 **FlowBot3D** 和 Substance Designer 的 Motion Vector Baker 均基于类似原理输出贴图。

### 方法三：程序化向量场生成

对于程序化特效（如旋转的漩涡、径向扩张的冲击波），可直接在 Houdini VEX 或 DCC 工具中手工构建向量场。例如，一个圆形扩张冲击波的运动矢量可定义为：

$$
\mathbf{m}(u, v) = k \cdot \frac{(u - 0.5,\; v - 0.5)}{\|(u - 0.5,\; v - 0.5)\|}
$$

其中 $k$ 为每帧扩张速率（通常为 0.02\~0.05），向量从纹理中心径向向外指。这种方法生成的向量场整洁、无噪声，适合程序化 VFX 资产管线。

---

## 实际应用

### 案例：UE5 烟雾序列帧平滑化

**问题场景**：游戏中使用一套 $8 \times 8$ 布局、64帧、分辨率 4096×4096 的烟雾 Flipbook，以 15fps 驱动，在 60fps 屏幕刷新率下每帧停留 4 个渲染帧，跳帧感强烈。

**解决方案**：在 Houdini 模拟阶段额外输出 2 通道速度场贴图（与 Flipbook 同等布局），导入 UE5 材质后启用 `SubUV_Motion_Vector` 节点，设置 `Blend` 为 `MotionVectors`，`Animation` 设为 `Infinite Loop`。混合因子由粒子 `RelativeTime` 参数驱动，系统自动在 15fps 关键帧间以 60fps 子帧插值。最终视觉评测中，测试人员将帧切换感知分（0-10 主观量表）从平均 7.2 降至 2.1。

**内存代价**：额外增加一张 RG16F 4096×4096 贴图，占用约 32 MB GPU 显存。与直接将原序列帧数加倍至 128 帧（需额外 128 MB 显存）相比，节省约 75% 的纹理内存。

### 案例：Unity VFX Graph 流体环境特效

在 Unity VFX Graph 中，Flipbook Player 块提供了 `Use Motion Vectors` 选项。一个典型的水面波纹特效使用 16×4 布局（64帧）Flipbook，配合 Farnebäck 光流生成的运动矢量贴图，在 RTX 2060 上的帧时间增量约为 0.3ms（相比无运动矢量的裸 lerp 插值额外消耗约 0.08ms），性能代价极低。

---

## 常见误区

### 误区一：运动矢量与屏幕空间运动矢量混淆

游戏渲染管线中存在另一类"运动矢量"（Screen-Space Motion Vector），用于 TAA（Temporal Anti-Aliasing）和 Motion Blur 后处理，记录每个屏幕像素的屏幕空间速度，由顶点着色器根据当前帧与上一帧的 MVP 矩阵差分计算。这与序列帧运动矢量**完全不同**：后者记录的是贴图 UV 空间中序列帧内容的位移，与相机运动、物体变换无关。两者若在材质中混用，会导致运动方向错乱。

### 误区二：所有序列帧都适合运动矢量插值

运动矢量插值对**连续流体运动**（烟雾、火焰、水流）效果显著，但对**不连续跳变**内容（如爆炸的强光帧、闪光特效的亮度骤升）会产生严重的颜色混叠和边缘撕裂。对于每帧间视觉差异超过约 40%（以 SSIM 指标衡量 $< 0.6$）的序列帧，运动矢量收益接近于零，甚至劣于简单 lerp。

### 误区三：运动矢量贴图分辨率越高越好

运动矢量记录的是相邻帧之间的低频位移场，高频细节噪声会导致插值撕裂。将运动矢量贴图分辨率设置为序列帧 Flipbook 的 1/2 甚至 1/4，并配合双线性过滤，通常优于等分辨率的带噪声矢量场。Epic Games 官方文档建议将运动矢量贴图与 Flipbook 保持同尺寸布局但可以使用低精度格式（RG8 而非 RG16F）来节省带宽。

### 误区四：忽略 Tiling 与帧边界的矢量连续性

当序列帧循环播放时（如持续燃烧的火焰），最后一帧与第一帧之间的运动矢量需要特殊处理——否则循环点处会出现明显的方向突变。正确做法是在 Houdini 中使用 Loop 约束将速度场首尾过渡帧的矢量平滑化，或在 Shader 中对循环边界帧主动关闭运动矢量混合（将 $t$ 钳制到 $[0, 0.5]$ 范围）。

---

## 知识关联

### 前置概念

- **序列帧 UV 动画（Flipbook UV Animation）**：运动矢量贴图必须与 Flipbook 的 SubUV 布局严格对应，二者共享相同的行列分割信息。理解 SubUV 索引计算（$\text{index} = \text