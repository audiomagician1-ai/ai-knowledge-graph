# 动画片段

## 概述

动画片段（Animation Clip）是游戏引擎动画系统中存储骨骼运动数据的原子单元，本质上是一张以时间为索引的多轨道变换数据库。每条轨道记录单根骨骼节点在时间轴上的位置（Translation）、旋转（Rotation）、缩放（Scale）变化，引擎在运行时以固定或可变步长对这些轨道进行采样，从而在任意时刻重建出完整骨骼姿势。

关键帧工作流的数字化起源可追溯到 1981 年 John Lasseter 在 Lucasfilm 将传统手绘"原画—动画"分工迁移至三维计算机图形的实验（Lasseter, 1987, *Principles of Traditional Animation Applied to 3D Computer Animation*, SIGGRAPH '87）。此后，Thomas & Johnston 在《The Illusion of Life: Disney Animation》（1981）中系统归纳的十二条动画原则，直接影响了现代动画片段关键帧密度与曲线形态的设计标准，成为业界制作高质量动画片段的理论依据。

在主流引擎中，Unreal Engine 5 将动画片段实现为 `UAnimSequence` 资产，每条骨骼轨道以 `FRawAnimSequenceTrack` 结构体存储原始关键帧数组，并在烘焙（Cook）阶段压缩为 `FCompressedAnimSequence`；Unity 则以 `AnimationClip` 对象组织，内部以 `AnimationCurve` 数组呈现，每条曲线对应一个属性绑定路径（如 `"Spine/LeftArm.localRotation.x"`）。两者架构殊途同归，均以时间轴索引驱动多骨骼轨道并行采样。

动画片段是所有上层动画逻辑的原始输入：动画状态机（State Machine）的每个状态指向至少一个片段，动画蓝图（AnimGraph）的 Blend Space 节点在二维参数空间中混合多个片段，Root Motion 位移直接从根骨骼轨道提取。因此，片段数据的精度、压缩策略与帧率选择，直接决定了整个角色动画管线的内存占用和 CPU 采样成本。

---

## 核心原理

### 关键帧结构与时间采样

动画片段的时间轴以**关键帧（Keyframe）**为基本粒子，每个关键帧包含：时间戳 $t_i$（单位秒）、变换值 $v_i$（可为向量或四元数），以及可选的入/出切线向量 $\mathbf{m}_i^{\text{in}}, \mathbf{m}_i^{\text{out}}$。引擎以"当前播放时间 $t$"查询轨道时，首先在关键帧时间戳数组中执行二分搜索，定位左右相邻关键帧 $t_l, t_r$，计算局部参数：

$$\alpha = \frac{t - t_l}{t_r - t_l}, \quad \alpha \in [0, 1]$$

随后以 $\alpha$ 为参数代入插值函数，输出该时刻的变换值。采样率与关键帧密度是独立概念：采样率是引擎运行时对片段求值的步长频率（通常锁定为游戏帧率 30/60 Hz），关键帧密度是动画师在 DCC 工具中放置关键帧的疏密程度。稀疏关键帧搭配样条插值可以用极少数据点还原流畅曲线，这是压缩算法的重要利用方向。

### 插值算法详解

**线性插值（LERP）** 是最廉价的插值方式，适用于位置分量：

$$\text{LERP}(\mathbf{p}_0, \mathbf{p}_1, \alpha) = (1-\alpha)\mathbf{p}_0 + \alpha\mathbf{p}_1$$

其缺陷在于经过关键帧时速度突变（一阶不连续），导致运动轨迹出现折线感，仅适合机械物体或调试用途。

**球面线性插值（SLERP）** 专用于单位四元数旋转，确保旋转沿球面最短弧均匀行进，公式为：

$$\text{SLERP}(q_0, q_1, \alpha) = \frac{\sin((1-\alpha)\Omega)}{\sin\Omega}\,q_0 + \frac{\sin(\alpha\Omega)}{\sin\Omega}\,q_1$$

其中 $\Omega = \arccos(q_0 \cdot q_1)$ 为两四元数在四维超球面上的夹角。当 $\Omega$ 接近 0 时需退化为 LERP 以避免数值奇点。SLERP 彻底规避了欧拉角表示法固有的万向锁问题，是现代引擎骨骼旋转插值的工业标准（Shoemake, 1985, *Animating Rotation with Quaternion Curves*, SIGGRAPH '85）。

**Hermite 三次样条** 在插值平滑性和计算效率之间取得最佳平衡。给定相邻关键帧值 $v_0, v_1$ 及其切线 $m_0, m_1$，在参数区间 $\alpha \in [0,1]$ 内的样条值为：

$$H(\alpha) = (2\alpha^3 - 3\alpha^2 + 1)v_0 + (\alpha^3 - 2\alpha^2 + \alpha)m_0 + (-2\alpha^3 + 3\alpha^2)v_1 + (\alpha^3 - \alpha^2)m_1$$

Hermite 样条保证端点一阶导数连续（$C^1$），可产生"缓入缓出"的自然加减速效果，是 Maya、3ds Max 等 DCC 工具曲线编辑器的默认插值模式，也是 Unreal Engine 动画片段烘焙时默认采用的曲线形式。

### 曲线编辑与轨道类型

动画片段支持多种轨道类型并行运行：

- **骨骼变换轨道**：每根骨骼独立持有 TRS 三条曲线（位置 3 通道 + 旋转 4 通道四元数 + 缩放 3 通道），是片段的主体数据。
- **浮点曲线轨道（Curve Track）**：以命名字符串绑定任意浮点属性，常用于驱动 Blend Shape 权重（如面部表情的笑容权重 0→1）、材质参数（如受伤时皮肤变红的 Roughness 值）或 IK 链的启用程度。
- **事件轨道（AnimNotify）**：Unreal Engine 特有，在指定时间点或时间窗口触发游戏逻辑回调，例如在跑步片段的第 0.15 秒和第 0.65 秒放置 `Footstep` 通知以精确同步脚步音效。

曲线编辑器中切线类型的选择直接影响最终动画质量：**Auto** 切线由引擎根据相邻关键帧自动计算光滑切线，适合大多数有机运动；**Flat** 切线强制水平（斜率为零），在关键帧前后产生停顿效果，常用于循环动画首尾帧保持姿势的过渡；**Break** 切线允许入切线和出切线独立调节，适合需要急转的非线性运动（如弹跳落地瞬间）。

---

## 关键公式与数据压缩

### 原始数据量估算

未压缩动画片段的存储量可用以下模型估算：设骨骼数为 $B$，采样帧率为 $F$（fps），片段时长为 $T$（秒），每骨骼每帧存储位置（$3 \times 4 = 12$ 字节）、四元数旋转（$4 \times 4 = 16$ 字节）、缩放（$3 \times 4 = 12$ 字节），共 40 字节，则原始数据量为：

$$\text{Size}_{\text{raw}} = B \times F \times T \times 40 \text{ 字节}$$

以一个典型 AAA 游戏角色为例：$B = 150$ 骨骼、$F = 30$ fps、$T = 10$ 秒，则原始大小约为 $150 \times 30 \times 10 \times 40 = 18,000,000$ 字节 $\approx$ **17.2 MB**。一款游戏动辄包含数百条动画片段，若不进行压缩，动画数据将占用数 GB 内存。

### 主流压缩算法

**关键帧简化（Key Reduction）**：对每条曲线单独运行误差阈值比较，若相邻三帧中中间帧的插值误差低于阈值 $\varepsilon$（通常取旋转 0.01°、位置 0.1 mm），则删除中间帧。Unreal Engine 的 `UAnimSequence` 在压缩设置中通过 `MaxPosDiff`、`MaxAngleDiff` 参数控制此阈值，可在不影响视觉的前提下将关键帧数量压缩至原始的 10%–30%。

**量化（Quantization）**：将 32 位浮点值降精度为 16 位或更低。旋转四元数因其约束条件（单位模长、分量范围 $[-1,1]$），可以安全量化至每分量 16 位整型，再配合"最大分量省略"技巧（丢弃绝对值最大的分量，由其余三个分量重建），将四元数存储从 16 字节压缩至 6 字节，压缩比约 2.7×（Unreal Engine 源码 `AnimationCompressionAlgorithm_PerTrackCompression`）。

**基于 ACL 的压缩**：Animation Compression Library（ACL，Valentin, 2019，开源项目 github.com/nfrechette/acl）采用范围归一化（Range Normalization）结合自适应比特率量化，对不同运动幅度的骨骼分配不同存储精度。Unreal Engine 5.0 起将 ACL 作为默认压缩算法，相比旧版 Bitwise 算法在相同视觉质量下内存占用减少 40%–60%，解压 CPU 开销降低约 30%。

---

## 实际应用

### Root Motion 与位移提取

普通动画片段中，根骨骼的位移变化仅影响骨骼局部空间，角色在世界空间中保持原地。启用 **Root Motion** 后，引擎从根骨骼轨道提取每帧位移增量 $\Delta \mathbf{p}$ 和旋转增量 $\Delta q$，直接驱动角色控制器在世界空间中移动：

$$\mathbf{p}_{\text{world}}(t+\Delta t) = \mathbf{p}_{\text{world}}(t) + R_{\text{world}} \cdot \Delta\mathbf{p}_{\text{clip}}$$

这一机制确保动画师在 DCC 中制作的脚步滑动与引擎中的物理位移精确对齐，消除"滑步"伪影。Unreal Engine 通过在 `UAnimSequence` 资产设置中勾选 `Enable Root Motion` 并选择 `Root Motion Root Lock`（固定根骨骼起始位置）实现此功能。

### 动画片段循环与首尾对齐

循环动画片段（如行走、跑步）要求首帧与末帧在骨骼姿势和速度上无缝衔接。常见做法是在 DCC 中将末帧关键帧复制至时长 +1 帧位置（"循环覆盖帧"），使插值曲线在片段边界处切线连续。Unity 的 `AnimationClip.wrapMode = WrapMode.Loop` 及 Unreal Engine 的 `LoopingInterpolation` 均依赖此约定正确工作。若首尾姿势差异过大，需在混合图层（Blend Layer）中添加过渡片段（Transition Clip）进行平滑衔接。

### 案例：《Ori and the Will of the Wisps》的高密度片段管线

Moon Studios 在《Ori and the Will of the Wisps》中为主角 Ori 制作了超过 400 条动画片段，每条片段的平均时长仅 0.4 秒，关键帧密度极高（部分攻击动画在 0.1 秒内包含 4–6 个关键帧）以实现"手绘帧"质感。为控制内存，团队采用 Unity 的 `AnimationClipPlayable` API 在运行时动态流式加载片段资产，避免全部常驻内存。这一案例展示了片段粒度设计与内存管理之间的工程权衡。

---

## 常见误区

**误区一：采样率越高动画越流畅**
采样率决定的是引擎对曲线的求值频率，与关键帧密度无关。将片段的求值频率