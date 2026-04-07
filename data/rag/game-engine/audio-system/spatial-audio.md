# 空间音频

## 概述

空间音频（Spatial Audio）是通过数字信号处理技术模拟声音在三维空间中传播物理规律的音频渲染体系，其核心目标是让听者通过普通耳机或扬声器阵列感知声源的方位角（Azimuth）、仰角（Elevation）和距离（Distance）。与传统双声道立体声仅能提供左右声像定位不同，空间音频可重建完整的球面声场，使玩家能准确辨别背后脚步声的距离、天花板上落下物体的轨迹，以及洞穴环境中多重反射形成的包围感。

空间音频技术的学术根基可追溯至 Blauert（1997）在《Spatial Hearing》一书中对人类双耳听觉定位机制的系统研究——该书至今仍是空间音频领域最重要的参考文献，详细量化了耳廓对 4 kHz～16 kHz 频段的方向性调制规律。游戏工程层面，1998 年 Creative Labs 推出的 EAX（Environmental Audio Extensions）首次将实时环境混响引入 PC 游戏硬件；2015 年 Oculus Audio SDK 将个人化 HRTF 与 VR 头动追踪绑定，标志着空间音频从"音效增强"升级为"感知基础设施"。Unity 引擎自 5.2 版本起开放 Native Audio Spatializer Plugin 接口，Unreal Engine 4.24 起通过 Resonance Audio 插件原生支持 Ambisonics 解码。

---

## 核心原理

### 头部相关传递函数（HRTF）

HRTF（Head-Related Transfer Function）是空间音频的数学核心，描述自由场中声源从方向 $(\theta, \phi)$ 到达左耳或右耳时，受头部绕射、耳廓反射和肩膀遮蔽综合影响所产生的频域滤波特性。设声源信号频谱为 $S(f)$，则到达左耳的频谱为：

$$E_L(f) = H_L(\theta, \phi, f) \cdot S(f)$$

$$E_R(f) = H_R(\theta, \phi, f) \cdot S(f)$$

其中 $H_L$ 和 $H_R$ 分别是左右耳的 HRTF，$\theta \in [0°, 360°)$ 为水平方位角，$\phi \in [-90°, +90°]$ 为仰角。在时域中，HRTF 对应的冲激响应称为 HRIR（Head-Related Impulse Response），游戏引擎通过对音频信号做卷积来施加 HRTF 效果：

$$y(t) = x(t) * h(\theta, \phi, t)$$

人类听觉系统依靠三类物理线索完成声源定位：

**双耳时间差（ITD，Interaural Time Difference）**：声波到达两耳的时间差，当声源位于纯侧方（$\theta = 90°$）时 ITD 达到最大值约 $630\,\mu s$，对应头部半径 $r \approx 8.75\,\text{cm}$ 和音速 $c = 343\,\text{m/s}$。ITD 主导低频（< 1.5 kHz）方向感知，符合 Rayleigh（1907）提出的双工理论（Duplex Theory）。

**双耳声级差（ILD，Interaural Level Difference）**：头部对高频声波（> 1.5 kHz）产生"声影"效应，使远侧耳接收到的声压级显著低于近侧耳，差值可达 20 dB 以上。ILD 主导高频水平定位。

**耳廓频谱线索（Pinna Spectral Cues）**：耳廓的复杂几何形态对 4 kHz～16 kHz 频段形成方向性的谱峰-谱谷图案（Notch Filters），这是区分声源前后方向和判断仰角的唯一单耳线索。Wenzel et al.（1993）的实验表明，若移除耳廓线索，被试对仰角判断的错误率从 15% 上升至 45%，并出现大量"前后混淆"。

游戏引擎中的 HRTF 数据集通常来自公开数据库，如 MIT Media Lab 的 KEMAR 假人测量集（512 个空间采样点，每点 128 抽头 FIR 滤波器）或 CIPIC 数据库（45 名真实被试，包含 1250 个方向采样）。实时卷积使用重叠相加法（Overlap-Add）在频域执行，计算复杂度为 $O(N \log N)$。

### Ambisonics 球谐声场编码

Ambisonics 由 Michael Gerzon 在 1973 年正式提出，以球谐函数（Spherical Harmonics）为基底，将三维声场中任意方向的声压信息无损编码为一组声道信号，解码时再还原至任意扬声器布局或双耳耳机渲染，与录制或混缩时的监听环境完全解耦。

N 阶 Ambisonics 共需 $(N+1)^2$ 个声道。一阶 FOA（First-Order Ambisonics）使用 4 声道（W, X, Y, Z），编码方程为：

$$W = \frac{1}{\sqrt{2}} \cdot p$$

$$X = p \cdot \cos\theta \cos\phi, \quad Y = p \cdot \sin\theta \cos\phi, \quad Z = p \cdot \sin\phi$$

其中 $p$ 为声压，$W$ 是零阶全向分量，X/Y/Z 是一阶偶极分量，分别对应前后、左右、上下三个轴。三阶 HOA（Third-Order Ambisonics）使用 16 声道，空间分辨率约为 $\pm 35°$，是 YouTube 360° 视频和 Google Resonance Audio 采用的标准格式。

Ambisonics 在 VR 内容制作中的优势在于**声场旋转不失真**：当用户转动头部时，只需对 B-Format 矩阵做旋转变换而无需重新采样声场，旋转矩阵 $\mathbf{R}$ 对各阶球谐分量分别作用，计算量远小于重新卷积整套 HRTF。

### 距离衰减与声学环境建模

游戏引擎中声音的距离感知依赖两个物理规律：

**距离衰减（Inverse Square Law）**：声压级随距离 $d$ 按平方反比衰减，每倍距离衰减约 6 dB：

$$L(d) = L_0 - 20 \log_{10}\!\left(\frac{d}{d_0}\right) \quad \text{(dB)}$$

其中 $L_0$ 为参考距离 $d_0$（通常取 1 米）处的声压级。Unity 的 AudioSource 组件提供 Linear、Logarithmic 和自定义曲线三种衰减模式；Unreal Engine 的 Attenuation Shape 支持球形、胶囊形和锥形衰减区域。

**高频空气吸收（Air Absorption）**：高频声波在空气中的衰减系数大于低频，导致远处声源听起来"发闷"。在标准大气条件下，8 kHz 频段的空气吸收系数约为 $0.17\,\text{dB/m}$，而 1 kHz 仅约 $0.004\,\text{dB/m}$（ISO 9613-1:1993 标准）。Unreal Engine 的 Reverb Distance 功能和 Steam Audio 的 Air Absorption 选项均实现了随距离增强的低通滤波器来模拟此效应。

**遮挡与衍射（Occlusion & Diffraction）**：声音穿过墙体时高频被大幅吸收（典型砖墙对 1 kHz 的隔声量约 45 dB），绕过障碍物边缘时产生衍射使低频声能扩散。Steam Audio 通过基于场景几何的声线投射（Ray Casting）计算遮挡系数，Wwise 的 Spatial Audio 模块使用房间-入口图（Room-Portal Graph）实现门缝透声效果。

---

## 关键方法与实现公式

### 实时双耳渲染流程

游戏引擎中实时 HRTF 双耳渲染的标准流程分为以下步骤：

1. **声源定位变换**：将声源世界坐标转换为以听者头部为原点的极坐标 $(\theta, \phi, d)$，需随头部追踪数据每帧更新。
2. **HRTF 插值**：HRTF 数据集是离散采样的，当声源方向落在两个采样点之间时，使用球面线性插值（SLERP）或双线性插值在相邻采样 HRIR 之间插值，以避免空间定位跳变。
3. **卷积运算**：使用 FFT 卷积对左右声道分别施加对应方向的 HRIR，FFT 帧长通常为 512 或 1024 点（在 48 kHz 采样率下对应约 11～21 ms 延迟）。
4. **距离处理**：根据距离 $d$ 施加幅度衰减、低通滤波（模拟空气吸收）和 ITD 缩放（近场效应下 ITD 随距离变化）。
5. **混响叠加**：将干信号（直达声）与混响尾巴（早期反射 + 混响尾音）以适当比例混合，混响发送量通常随距离增大：$\text{Reverb}_{send} = 1 - e^{-d/d_r}$，其中 $d_r$ 为空间特征衰减距离。

### 多普勒效应

当声源相对听者有速度分量 $v_s$ 时，接收频率按多普勒公式偏移：

$$f' = f_0 \cdot \frac{c + v_l}{c - v_s}$$

其中 $c = 343\,\text{m/s}$，$v_l$ 为听者接近声源的速度，$v_s$ 为声源接近听者的速度。Unity 和 Unreal 均内置多普勒模拟，参数 `Doppler Level`（Unity）或 `Doppler Factor`（Unreal）控制效果强度，取值 0 表示禁用，1 表示物理准确，可大于 1 以夸张效果（常用于赛车游戏）。

---

## 实际应用

### 案例一：第一人称射击游戏中的脚步声定位

在《CS:GO》和《Valorant》等竞技游戏中，脚步声的空间定位直接关系到竞技胜负。这类游戏通常使用双耳 HRTF 渲染（需玩家使用耳机），配合精确的 ITD（±630 μs 范围内）和 ILD 差异，使玩家能在 360° 方位内以约 ±15° 的精度判断脚步方向。Valve 的 Panoramic Spatial Audio 系统（2017 年引入 CS:GO）将声源的仰角信息也纳入渲染，使玩家能区分上下楼梯的脚步声。

### 案例二：VR 游戏中的动态 HRTF 更新

在 Meta Quest 平台的 VR 游戏中，Oculus Audio SDK 将 HRTF 渲染与头部追踪数据以低于 10 ms 的端到端延迟绑定更新。若延迟超过约 40 ms，用户会因头动后声像滞后而产生"声像漂移"（Audio-Visual Mismatch），显著增加眩晕感（Steinicke et al., 2010）。为此，引擎通常采用双缓冲异步音频线程在独立 CPU 核心上运行音频处理，保证帧率无关的低延迟更新。

### 案例三：Unity 中配置 Steam Audio 空间音频

在 Unity 中使用 Steam Audio（Valve, 2017）的典型配置流程：
1. 将场景中所有静态几何体标记为 `Steam Audio Geometry`，用于声线投射；
2. 在 `Steam Audio Listener` 组件上启用 HRTF 双耳渲染（可选 SOFA 格式的自定义 HRTF 文件）；
3. 为每个 `AudioSource` 添加 `Steam Audio Source` 组件，开启 Occlusion（遮挡）、Reflection（反射）和 Transmission（穿透）选项；
4. 烘焙静态场景的 Probe Grid，减少运行时射线计算开销（Baking 后反射精度提升但 CPU 开销从约 8 ms 降至约 0.5 ms/帧）。

---

## 常见误区

**误区一：空间音频等于立体声宽度增强**

将声像左右推宽（例如使用 Haas Effect 将同一信号延迟 1～30 ms 后叠加）与真正的