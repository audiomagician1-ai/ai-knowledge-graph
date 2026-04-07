# 同步组（Sync Groups）

## 概述

同步组（Sync Groups）是Unreal Engine动画系统中用于协调多个循环动画播放节奏的机制，专门解决BlendSpace中不同速度档位的行走/奔跑动画在混合过渡时脚步错位的问题。当Walk动画和Run动画的步幅周期（stride cycle）不一致时，混合权重切换瞬间会出现"双脚同时离地"或"踏步相位跳变"的视觉穿帮，同步组通过强制多条动画共享同一个归一化播放位置（normalized position）来消除这种错位。

同步组概念最早随Unreal Engine 4.2版本（2014年发布）正式引入动画蓝图系统，由Epic Games动画工程师在官方文档《Animation Sync Groups》中详细阐述，解决了此前开发者必须手动对齐动画帧数或依赖相同帧数限制的痛点。在此之前，BlendSpace用户不得不将Walk和Run动画烘焙成完全相同的帧长度，极大限制了动作捕捉素材的复用灵活性。同步组的出现允许Walk动画保持48帧、Run动画保持32帧，两者仍能在BlendSpace中无缝混合。

同步组的核心价值在于：一旦走路动画的左脚触地帧与奔跑动画的左脚触地帧被强制对齐到同一归一化时间0.0，玩家在操控角色从步行加速到奔跑的全过程中，脚步始终保持自然的相位连续性，而不会产生滑步或抽搐感。这一机制在游戏开发工业中已成为处理运动状态混合的标准手段，Unity引擎的Avatar Mask + Avatar Body Mask方案提供了功能类似但实现路径不同的对应机制，两者均以归一化时间轴为基础（Canessa等，2019）。

## 核心原理

### Leader与Follower角色分配

同步组要求组内每条动画在任意时刻只能扮演两种角色之一：**Leader（主控者）** 或 **Follower（跟随者）**。Leader由当前混合权重最高的动画担任，它的归一化播放位置（范围0.0～1.0）成为本帧的"时间基准"。所有Follower动画放弃自己原本的播放进度，强制跳转到与Leader相同的归一化位置并以对应的实际帧播放。

以一个典型1D BlendSpace为例：输入轴Speed范围0～600，Walk动画权重0.3、Run动画权重0.7，此时Run担任Leader，Walk跟随Run的归一化位置0.47播放，即使Walk的原生时长是Run的1.5倍，也必须精确映射到其自身的第0.47×总帧数帧。当Speed提高导致Walk权重降至0.2以下，Leader身份不会立刻切换——UE使用滞后阈值（默认约0.1的权重缓冲区）避免频繁的Leader交接引起抖动。

值得注意的是，Leader切换本身也有内置的平滑机制：当Run的权重从0.69跨越0.70阈值成为新Leader时，引擎不会在单帧内做硬切换，而是在连续2～3帧内完成Leader身份的渐进交接，防止归一化基准位置发生突变。

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

### 同步标记（Sync Markers）的精确相位对齐

仅靠归一化位置还不够精确，因为Walk和Run的触地时机在动画曲线上的占比位置可能不同。同步标记允许动画师在Walk动画的左脚触地帧手动插入名为`LeftFootDown`的标记，在Run动画相应位置插入同名标记，同步组随后以标记点为"锚点"进行区间插值而非线性缩放。

在Persona编辑器的动画时间轴下方有专用的Notifies轨道，同步标记（Sync Marker类型，区别于普通Anim Notify）在此添加。每对同名标记定义了一个循环子区间，组内动画在对应子区间内保持局部归一化对齐，使左脚触地、右脚触地这两个关键相位点精确重合，而不是均匀拉伸整条曲线。

具体而言，若Walk的`LeftFootDown`标记位于归一化位置0.08，而Run的`LeftFootDown`标记位于0.0，引入同步标记后，系统将以标记区间为单位进行分段对齐：Walk的[0.08, 0.58]子区间对应Run的[0.0, 0.5]子区间，两段曲线在各自子区间内独立做归一化映射，从而将原本固有的0.08相位偏差完全消除。

### FAnimSyncContext与底层数据结构

在UE引擎代码层面，同步组的归一化位置状态存储于`FAnimSyncContext`结构体中（位于`AnimationRuntime.h`）。每帧动画更新时，`UAnimInstance::UpdateAnimation()`调用链会收集所有激活动画节点的同步组信息，按照权重排序确定Leader，再将Leader的`FAnimSyncContext::NormalizedTime`广播给所有同组Follower节点。这意味着同步组的计算发生在动画蓝图的Update阶段（早于Evaluate阶段），Follower在Evaluate阶段已持有正确的目标帧号，不存在一帧延迟的问题。

## 关键公式与模型

### 相位偏差量化模型

在不使用同步组的情况下，两条动画在混合点的相位偏差 $\Delta\phi$ 可以用以下公式估算：

$$\Delta\phi = \left| \frac{t_{\text{elapsed}}}{T_{\text{Walk}}} - \frac{t_{\text{elapsed}}}{T_{\text{Run}}} \right| \mod 1.0$$

其中 $T_{\text{Walk}}$ 和 $T_{\text{Run}}$ 分别为Walk和Run动画的周期时长（秒），$t_{\text{elapsed}}$ 为从上次强制对齐后经过的时间。

以Walk周期1.6秒、Run周期1.07秒为例，经过1.0秒后：

$$\Delta\phi = \left| \frac{1.0}{1.6} - \frac{1.0}{1.07} \right| = |0.625 - 0.935| = 0.31$$

这意味着仅经过1秒，两条动画的相位差就已达到0.31个完整周期，约相当于半个步幅的错位——这正是不使用同步组时视觉穿帮如此明显的数学原因。

### Leader切换权重阈值

设当前帧各动画权重为 $w_i$（$\sum w_i = 1$），Leader切换规则为：

$$\text{Leader} = \arg\max_i(w_i), \quad \text{当} \max_i(w_i) > w_{\text{prev\_leader}} + \delta_{\text{hysteresis}}$$

其中 $\delta_{\text{hysteresis}}$ 为滞后阈值，UE默认设置约为0.1，防止在权重接近0.5的混合中间区域发生频繁的Leader身份震荡。

## 实际应用

**案例：Walk/Run BlendSpace配置**。在UE5项目中为第三人称角色创建1D BlendSpace，轴范围0～500（单位：cm/s）。将Walk\_Fwd动画（48帧，30fps，步幅周期约1.6秒）与Run\_Fwd动画（32帧，30fps，步幅周期约1.07秒）均加入同一个Sync Group，命名为`LocomotionSyncGroup`。在Walk\_Fwd的第0帧和第24帧分别添加名为`LeftFootDown`和`RightFootDown`的同步标记，在Run\_Fwd的第0帧和第16帧添加相同名称的同步标记。BlendSpace节点在动画蓝图图表中会显示Sync Group名称输入栏，填入同一名称即完成关联。

**Jog→Sprint过渡中的实测差异**：未使用同步组时，Speed从400提升至600的瞬间，两条动画的相位差最大可达半个步幅周期（约0.5归一化单位），角色脚步肉眼可见地"跳"了一步。启用同步组并添加标记后，同一过渡的最大相位偏差降低至约0.04归一化单位（对应约1～2帧），在60fps下基本不可察觉。这一数据与上文相位偏差公式的理论预测高度吻合：标记对齐将残余误差从整体归一化误差压缩至单个标记区间内的局部误差。

**例如，在《堡垒之夜》风格的角色运动系统中**，开发团队通常为走路、小跑、冲刺三个速度档位分别准备32、24、20帧的循环动画，三条动画共享同一个`LocomotionSync`组，并在每条动画的左脚触地、右脚触地位置各插入一个同步标记，总计6个标记点。这样的配置使得角色在0～800 cm/s的速度范围内，脚步相位连续性始终维持在可接受的感知阈值以内。

**Crouch Walk的独立同步组**：蹲伏行走动画不应与直立Walk/Run共享同步组，因为蹲伏步幅节奏（约2.2秒/周期）与直立姿态（约1.6秒/周期）差异约为37%，强制共享会导致蹲伏动画被异常拉伸。正确做法是为`CrouchLocomotion`单独创建一个Sync Group，仅包含CrouchWalk和CrouchRun。

**游泳与攀爬的扩展应用**：同步组不仅限于地面运动。水下游泳动画（慢速划水48帧，快速冲刺24帧）同样可以使用同步组对齐手臂入水时刻；垂直攀爬动画（普通攀爬32帧，快速攀爬20帧）可以对齐右手抓握帧，避免在速度切换时出现手臂悬空的穿帮画面。

## 常见误区

**误区一：同步组等于统一播放速率**。许多初学者认为同步组是让所有动画以相同速度播放，实际上Run（32帧）与Walk（48帧）在同步组中依然保持各自的帧数，只是播放位置被归一化对齐。Walk的实际播放速率会随归一化位置的推进速度自动调整，使其与Leader的步幅节奏匹配——这相当于Walk的有效播放速率从30fps动态变化为 $30 \times (32/48) \approx 20$ fps，而非固定于原始帧率。

**误区二：不添加同步标记也能完美对齐**。纯粹依赖归一化位置的同步组在Walk和Run的触地帧归一化占比相同时效果良好，但大多数动捕数据中左脚触地点并不精确处于0.0和0.5位置。如果Walk的左脚触地在归一化位置0.08而Run在0.0，不加标记的同步将始终保留0.08的相位偏差，仍会导致轻微的踏步错位，必须通过同步标记消除这一残余误差。

**误区三：Sync Group可以跨BlendSpace节点生效**。同步组仅在同一AnimGraph中引用了相同Sync Group名称的节点之间生效。如果Walk/Run BlendSpace节点与一个独立的Idle动画节点均标注了相同的组名，Idle会被错误地拉入同步，导致待机动画的播放速度随角色移动速度异常变化。待机动画应留空Sync