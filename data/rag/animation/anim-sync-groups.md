# 同步组（Sync Groups）

## 概述

同步组（Sync Groups）是Unreal Engine动画系统中用于协调多个循环动画播放节奏的机制，专门解决BlendSpace中不同速度档位的行走/奔跑动画在混合过渡时脚步错位的问题。当Walk动画和Run动画的步幅周期（stride cycle）不一致时，混合权重切换瞬间会出现"双脚同时离地"或"踏步相位跳变"的视觉穿帮，同步组通过强制多条动画共享同一个归一化播放位置（normalized position）来消除这种错位。

同步组概念最早随Unreal Engine 4.2版本（2014年8月发布）正式引入动画蓝图系统，由Epic Games动画工程师在官方文档《Animation Sync Groups》中详细阐述，解决了此前开发者必须手动对齐动画帧数或依赖相同帧数限制的痛点。在此之前，BlendSpace用户不得不将Walk和Run动画烘焙成完全相同的帧长度，极大限制了动作捕捉素材的复用灵活性。同步组的出现允许Walk动画保持48帧、Run动画保持32帧，两者仍能在BlendSpace中无缝混合。

同步组的核心价值在于：一旦走路动画的左脚触地帧与奔跑动画的左脚触地帧被强制对齐到同一归一化时间0.0，玩家在操控角色从步行加速到奔跑的全过程中，脚步始终保持自然的相位连续性，而不会产生滑步或抽搐感。这一机制在游戏开发工业中已成为处理运动状态混合的标准手段，Unity引擎的Avatar Mask + Avatar Body Mask方案提供了功能类似但实现路径不同的对应机制，两者均以归一化时间轴为基础。在工业界的大规模项目实践中，同步组已被证明是减少动画程序员与动作设计师之间沟通成本的关键工具，使两个职能岗位能够在帧数完全不同的素材上独立作业（Gregory, 2018）。

值得一提的是，同步组这一思路并非凭空产生——它在概念上源自传统手绘动画中"contact pose对齐"的经验法则，即在循环步行动画中，左脚接触地面的姿势（contact pose）是定义步态相位的黄金标准帧，后续所有混合操作均应以此为锚点展开（Lasseter, 1987）。

## 核心原理

### Leader与Follower角色分配

同步组要求组内每条动画在任意时刻只能扮演两种角色之一：**Leader（主控者）** 或 **Follower（跟随者）**。Leader由当前混合权重最高的动画担任，它的归一化播放位置（范围0.0～1.0）成为本帧的"时间基准"。所有Follower动画放弃自己原本的播放进度，强制跳转到与Leader相同的归一化位置并以对应的实际帧播放。

以一个典型1D BlendSpace为例：输入轴Speed范围0～600（单位：cm/s），Walk动画权重0.3、Run动画权重0.7，此时Run担任Leader，Walk跟随Run的归一化位置0.47播放，即使Walk的原生时长是Run的1.5倍，也必须精确映射到其自身的第0.47×总帧数帧。当Speed提高导致Walk权重降至0.2以下，Leader身份不会立刻切换——UE使用滞后阈值（默认约0.1的权重缓冲区）避免频繁的Leader交接引起抖动。

值得注意的是，Leader切换本身也有内置的平滑机制：当Run的权重从0.69跨越0.70阈值成为新Leader时，引擎不会在单帧内做硬切换，而是在连续2～3帧内完成Leader身份的渐进交接，防止归一化基准位置发生突变。这一设计决策与BlendSpace节点的平滑滤波（smoothing filter）协同工作，共同确保权重曲线在时间轴上的一阶导数连续。

### 归一化位置映射公式

Follower的实际播放帧按以下映射计算：

$$\text{FollowerFrame} = P_{\text{norm}} \times F_{\text{total}}$$

其中：
- $P_{\text{norm}}$（归一化播放位置）$= \dfrac{\text{LeaderCurrentFrame}}{\text{LeaderTotalFrames}}$，取值范围 $[0.0,\ 1.0]$
- $F_{\text{total}}$：Follower动画的总帧数
- $\text{FollowerFrame}$：Follower本帧应渲染的实际帧编号

例如，若Walk共48帧、Run共32帧，当Run（Leader）播放到第16帧时：

$$P_{\text{norm}} = \frac{16}{32} = 0.5 \quad \Rightarrow \quad \text{FollowerFrame} = 0.5 \times 48 = 24$$

即Walk应跳到第24帧。这是同步组与简单"播放速率缩放"方案的根本区别——后者仅改变播放速度（将Walk的播放速率乘以系数 $r = F_{\text{Walk\_total}} / F_{\text{Run\_total}} = 48/32 = 1.5$），无法保证相位对齐，仍会在混合边界处累积相位差。

此外，需要特别注意帧率与动画周期的关系。若Walk动画以30fps采样、Run动画以60fps采样，两者的 $F_{\text{total}}$ 所对应的实际时长（秒数）不同，归一化映射仍然成立，但引擎内部会先将帧编号转换为归一化时间再执行映射，而不是直接做帧号的线性插值。这一细节在混用不同采样率的动捕素材时尤为重要。

### 同步标记（Sync Markers）的精确相位对齐

仅靠归一化位置还不够精确，因为Walk和Run的触地时机在动画曲线上的占比位置可能不同。同步标记允许动画师在Walk动画的左脚触地帧手动插入名为`LeftFootDown`的标记，在Run动画相应位置插入同名标记，同步组随后以标记点为"锚点"进行区间插值而非线性缩放。

在Persona编辑器的动画时间轴下方有专用的Notifies轨道，同步标记（Sync Marker类型，区别于普通Anim Notify）在此添加。每对同名标记定义了一个循环子区间，组内动画在对应子区间内保持局部归一化对齐，使左脚触地、右脚触地这两个关键相位点精确重合，而不是均匀拉伸整条曲线。

具体而言，若Walk的`LeftFootDown`标记位于归一化位置0.08，而Run的`LeftFootDown`标记位于0.0，引入同步标记后，系统将以标记区间为单位进行分段对齐：Walk的[0.08, 0.58]子区间对应Run的[0.0, 0.5]子区间，两段曲线在各自子区间内独立做归一化映射，从而将原本固有的0.08相位偏差完全消除。

同步标记的命名约定对多角色项目尤为重要。建议在项目早期制定统一的标记命名规范，例如`LF_Down`（左脚触地）、`RF_Down`（右脚触地）、`LF_Up`（左脚离地）、`RF_Up`（右脚离地），并将该规范写入项目动画制作指南（Animation Style Guide）。标记名称的大小写在UE内部区分处理，`LeftFootDown`与`leftfootdown`视为两个不同标记，拼写不一致是同步标记失效最常见的原因之一。

### FAnimSyncContext与底层数据结构

在UE引擎代码层面，同步组的归一化位置状态存储于`FAnimSyncContext`结构体中（位于`AnimationRuntime.h`）。每帧动画更新时，`UAnimInstance::UpdateAnimation()`调用链会收集所有激活动画节点的同步组信息，按照权重排序确定Leader，再将Leader的`FAnimSyncContext::NormalizedTime`广播给所有同组Follower节点。这意味着同步组的计算发生在动画蓝图的Update阶段（早于Evaluate阶段），Follower在Evaluate阶段已持有正确的目标帧号，不存在一帧延迟的问题。

`FAnimSyncContext`还维护一个`MarkerTickRecord`数组，记录上一帧与当前帧之间越过的所有同步标记及其越过方向（正向/反向播放），使引擎在变速或反向播放时也能正确维护标记区间的对齐状态。该设计支持了UE5中运动匹配（Motion Matching）与传统BlendSpace同步组的混合使用场景。

### 同步组与Transition Rule的协同

在动画状态机（State Machine）中，Transition Rule触发时若新状态与旧状态的动画属于不同的同步组，则存在一次相位不连续的潜在风险。处理此类场景的推荐做法是在Transition Rule节点上启用"Sync Group Override"选项，并指定与起始状态相同的同步组名称，这样过渡混合（Cross-fade）期间新状态的动画会临时加入旧同步组，等过渡结束后再切换回自己的常驻同步组。这一技巧在处理"冲刺→急停→走路"连贯动作序列时尤为关键，能避免急停动画结束帧与走路动画起始帧之间的脚步相位跳变。

## 关键公式与模型

### 相位偏差量化模型

在不使用同步组的情况下，两条动画在混合点的相位偏差 $\Delta\phi$ 可以用以下公式估算：

$$\Delta\phi = \left| \frac{t_{\text{elapsed}}}{T_{\text{Walk}}} - \frac{t_{\text{elapsed}}}{T_{\text{Run}}} \right| \mod 1.0$$

其中 $T_{\text{Walk}}$ 和 $T_{\text{Run}}$ 分别为Walk和Run动画的周期时长（秒），$t_{\text{elapsed}}$ 为从上次强制对齐后经过的时间（秒）。

以Walk周期1.6秒、Run周期1.07秒为例，经过1.0秒后：

$$\Delta\phi = \left| \frac{1.0}{1.6} - \frac{1.0}{1.07} \right| = |0.625 - 0.935| = 0.31$$

这意味着仅经过1秒，两条动画的相位差就已达到0.31个完整周期，约相当于半个步幅的错位——这正是不使用同步组时视觉穿帮如此明显的数学原因。以60fps渲染为基准，0.31个周期偏差在Walk动画（48帧）中对应约14.9帧的帧偏移，肉眼极易察觉。

### Leader切换权重阈值

设当前帧各动画权重为 $w_i$（$\sum w_i = 1$），Leader切换规则为：

$$\text{Leader} = \arg\max_i(w_i), \quad \text{当} \max_i(w_i) > w_{\text{prev\_leader}} + \delta_{\text{hysteresis}}$$

其中 $\delta_{\text{hysteresis}}$ 为滞后阈值，UE默认设置约为0.1，防止在权重接近0.5的混合中间区域发生频繁的Leader身份震荡。当组内动画数量为 $n$ 时，最坏情况下需要比较 $n-1$ 次权重大小，算法时间复杂度为 $O(n)$，在动画节点数量较多的复杂Blend Tree中，合理控制单个同步组内的动画条目数（建议不超过8条）可有效降低每帧的同步开销。

### Follower有效播放速率推导

基于归一化映射公式，可以推导Follower在同步组驱动下的有效播放帧率 $fps_{\text{eff}}$：

$$fps_{\text{eff}} = fps_{\text{native}} \times \frac{F_{\text{total\_follower}}}{F_{\text{total\_leader}}} \times \frac{T_{\text{leader}}}{T_{\text{follower}}}$$

当帧率相同（均为30fps）、以帧数替代时长时，上式简化为：

$$fps_{\text{eff}} = 30 \times \frac{48}{32} = 45 \text{ fps（Walk被Run驱动时的有效采样率）}$$

这意味着Walk动画的每一帧在视觉上停留时间约为 $1/45 \approx 22.2$ ms，而非其原生的 $1/30 \approx 33.3$ ms，整体表现为Walk动画以1.5倍速"快进"以追上