# Unity音频系统

## 概述

Unity音频系统是游戏引擎中负责声音采集、处理、混合与空间化输出的完整管线，其三大核心支柱为 **AudioSource**（音频源）、**AudioMixer**（混音器）和 **Audio Spatializer**（空间化插件）。这套系统在 Unity 5.0（2015年3月正式发布）时经历了架构性重构——引入了基于 DSP 总线的 AudioMixer，使得游戏音频工程师第一次可以像使用 Pro Tools 或 Nuendo 那样，在引擎内部完成分组路由、动态压缩和快照切换，而无需依赖外部中间件。

Unity 音频管线在底层使用 FMOD 作为早期版本的音频后端（Unity 4.x 及之前），自 Unity 5 起切换为自研的 UnityAudio 后端，并通过 Native Audio Plugin SDK 开放了 DSP 插件接口（Unity Technologies, 2015）。值得注意的是，尽管 Unity 内置音频系统可满足大多数项目需求，但 Wwise 和 FMOD Studio 等专业音频中间件仍因其更强大的自适应音乐系统和事件驱动架构而被 AAA 项目广泛采用（Collins, 2008）。

从物理声学角度看，Unity 音频系统的 3D 空间音效基于距离衰减与方位角模拟两个维度。正确配置双耳 HRTF 渲染后，玩家对声源方向的判断准确率相较纯立体声可提升约 35%–40%，这对 VR 游戏中的威胁感知与空间导航有直接影响。

---

## 核心原理

### AudioSource 与 AudioListener 的协作机制

每个可发声的 GameObject 需要挂载 **AudioSource** 组件，而整个场景有且仅有一个激活的 **AudioListener**（通常附在 Main Camera 上）。AudioListener 的位置即为"聆听者耳朵"的世界坐标，Unity 引擎每帧根据 AudioSource 与 AudioListener 之间的相对位置和速度，计算以下参数：

- **距离衰减**：依据所选衰减模型削减音量
- **多普勒效应**：根据相对速度改变音调，由 `Doppler Level` 系数控制（默认值 1.0，范围 0–5）
- **声像平移（Panning）**：将信号分配到左右声道

若场景中不存在激活的 AudioListener，所有 AudioSource 均静默，且 Unity 会在 Console 面板输出警告："There are no audio listeners in the scene."

### 距离衰减模型与公式

AudioSource 的 **Spatial Blend** 属性控制 2D/3D 混合比例（0.0 = 纯 2D，1.0 = 纯 3D）。当 Spatial Blend > 0 时，Unity 按照选定的 **Volume Rolloff** 模式计算音量衰减：

**对数衰减（Logarithmic Rolloff，默认）：**

$$
V(d) = \frac{V_0 \cdot d_{min}}{d}, \quad d \geq d_{min}
$$

其中 $V_0$ 为 MinDistance 处的音量，$d$ 为当前距离，$d_{min}$ 为 Min Distance 参数值。超过 Max Distance 后音量强制归零。

**线性衰减（Linear Rolloff）：**

$$
V(d) = V_0 \cdot \left(1 - \frac{d - d_{min}}{d_{max} - d_{min}}\right)
$$

开发者还可通过 **Custom Rolloff** 提供 AnimationCurve，对枪声、音乐环境声等不同素材实现完全差异化的衰减行为。

**例如**：在一款开放世界游戏中，营地篝火的 AudioSource 设置 Min Distance = 2m、Max Distance = 20m、Logarithmic Rolloff，玩家在 2m 内听到满音量，走到 20m 外火焰声消失，符合真实的声学感知。

### AudioMixer 的树状路由结构

AudioMixer 采用 **树形 DSP 图** 组织信号流。每个 Mixer 包含若干 **AudioMixerGroup**（音频混合组），AudioSource 将输出目标设为某个 Group，Group 之间形成父子层级，子 Group 信号向上汇集至 Master Group，再输出到音频设备。典型的分组结构为：

```
Master
├── Music
│   └── Adaptive_Layer
├── SFX
│   ├── Weapons
│   ├── Footsteps
│   └── UI
└── Ambience
    ├── Indoor
    └── Outdoor
```

每个 AudioMixerGroup 支持串联多个内置 DSP 效果器：**Equalizer**（均衡器，8段参数EQ）、**Compressor**（压缩器，可设置 Threshold、Ratio、Attack、Release）、**Send/Receive**（支持信号侧链）、**SFX Reverb**（基于 Schroeder 混响算法的混响器）等。

### Snapshot 快照机制

**Snapshot（快照）** 是 AudioMixer 内参数状态的命名预设。例如，可创建 "Outdoor"、"Indoor"、"Underwater" 三个 Snapshot，分别存储不同的 EQ、混响和音量配置。运行时通过以下代码在快照之间平滑过渡：

```csharp
// 在0.5秒内线性过渡到"Underwater"快照
underwaterSnapshot.TransitionTo(0.5f);

// 混合多个快照（权重之和须为1.0）
AudioMixer.TransitionToSnapshots(
    new AudioMixerSnapshot[] { outdoorSnap, indoorSnap },
    new float[] { 0.3f, 0.7f },
    transitionTime: 1.0f
);
```

快照之间的参数插值默认为线性，但 dB 值应使用对数感知插值——这是开发中常被忽略的细节，将在"常见误区"一节详述。

---

## 关键方法与 API

### AudioSource 核心 API

```csharp
// 在 AudioSource 位置播放一次性音效（不需要AudioSource持久引用）
AudioSource.PlayClipAtPoint(clip, transform.position, volume: 0.8f);

// 带随机音调的射击音效，避免重复感
audioSource.pitch = Random.Range(0.9f, 1.1f);
audioSource.PlayOneShot(shootClip, volumeScale: 1.0f);

// 通过代码控制AudioMixer暴露参数（参数名须在Mixer中手动Expose）
audioMixer.SetFloat("MusicVolume", Mathf.Log10(sliderValue) * 20f);
// 注意：sliderValue须>0，建议范围0.0001~1.0
```

`PlayOneShot` 与直接调用 `Play()` 的关键区别在于：`PlayOneShot` 允许同一 AudioSource 同时叠加多个实例，适合高频触发的音效（如快速射击）；而 `Play()` 每次调用都会中断当前正在播放的声音。

### AudioMixer 参数暴露与音量换算

Unity AudioMixer 的音量参数以 **dB（分贝）** 为单位（范围 -80dB 到 +20dB），而 UI 滑动条通常提供 0.0–1.0 的线性值。正确的换算公式为：

$$
\text{dB} = 20 \cdot \log_{10}(\text{linearValue})
$$

```csharp
// 正确写法
float dB = Mathf.Log10(Mathf.Max(linearValue, 0.0001f)) * 20f;
audioMixer.SetFloat("ExposedVolume", dB);
```

若直接将线性值传入 dB 参数，会导致音量滑块在低端极度不灵敏、在高端微小变化就剧烈失真。

### Audio Spatializer 插件接口

Unity 通过 **Native Audio Plugin SDK**（C++ 接口）和 **AudioSpatializerSDK** 支持第三方空间化算法。在 Project Settings → Audio → Spatializer Plugin 中选择插件（如 **Resonance Audio**、**Oculus Spatializer**）后，需在 AudioSource 的 Inspector 中勾选 "Spatialize"，并将 Spatial Blend 设为 1.0。

Resonance Audio（Google, 2017年开源）使用球谐函数（Spherical Harmonics）对房间声学建模，支持高阶环境声（Ambisonics）渲染，在 Oculus Quest 等 6DoF 头显上可实现实时 HRTF 双耳渲染，延迟低于 12ms。

---

## 实际应用

### 案例：自适应音乐系统

《塞尔达传说：荒野之息》（Nintendo, 2017）采用分层音乐架构：安全状态播放低强度主题，战斗状态叠加高能打击层。Unity 中可用 AudioMixer 的 Send/Receive 效果器和 Snapshot 混合复现类似效果：

1. 创建 `Combat_Snapshot`，将战斗音乐组的音量从 -80dB 恢复到 0dB
2. 将环境音乐组的高频 EQ 拉低（模拟"被掩盖"效果）
3. 用 `TransitionToSnapshots` 在 0.3 秒内完成过渡，避免突兀切换

### 案例：水下音效实现

玩家潜入水面时，现实中高频声波被水吸收，音色变得低沉浑浊。在 Unity 中的标准实现方案：

1. 在 AudioMixer 中创建 `Underwater_Snapshot`
2. 将 Master EQ 的高频段（>1kHz）削减 -18dB 至 -24dB
3. 增加 SFX Reverb 的 Decay Time 至 2.5s（模拟水下混响）
4. 降低 Doppler Level 为 0（水中多普勒效应显著减弱）
5. 触发条件：检测摄像机的 Y 坐标低于水面高度时调用 `underwaterSnapshot.TransitionTo(0.3f)`

### 案例：大量音源的性能优化

当场景中同时存在数十个 AudioSource（如 RTS 游戏的单位音效）时，CPU 开销显著上升。Unity 提供以下优化策略：

- **Audio Voice Count**：在 Project Settings → Audio 中限制最大同时播放数（默认 32，移动平台建议降至 16–24）
- **Audio Culling**：距离超过 Max Distance 的 AudioSource 自动停止 DSP 计算
- **Load Type**：频繁播放的短音效使用 `Decompress On Load`（内存换 CPU），背景音乐使用 `Streaming`（磁盘流式解码），偶发长音效使用 `Compressed In Memory`
- **AudioSource Pooling**：通过对象池复用 AudioSource 组件，避免频繁 AddComponent/Destroy

---

## 常见误区

**误区一：线性值直接赋给 dB 参数**
如前所述，`audioMixer.SetFloat("Volume", sliderValue)` 将 0–1 的线性值传给以 dB 为单位的参数，导致音量曲线严重非线性。必须使用 $\text{dB} = 20\log_{10}(\text{value})$ 换算。

**误区二：Snapshot 切换时 dB 参数的插值失真**
AudioMixer 的 Snapshot 对 dB 参数默认使用 **线性插值**，但人耳对响度的感知是对数的。从 -80dB 到 0dB 线性插值时，前 90% 的时间内几乎无法感知音量变化，在最后 10% 突然"冲上来"。解决方案：将音量参数拆成"实际音量"与"fade multiplier"两层控制，或使用 `AudioSource.volume`（线性域）配合 `Mathf.Lerp` 做淡入淡出，再通过 AudioMixer 做频段和效果控制。

**误区三：每帧调用 AudioSource.Play() 重启音效**
在 Update() 中直接调用 `audioSource.Play()` 而不检查 `audioSource.isPlaying`，会导致音效每帧被截断重启，出现"哒哒哒"的噪音。正确做法是先判断：`if (!audioSource.isPlaying) audioSource.Play();`

**误区四：忽略 Audio Spatializer 的 "Spatialize Post Effects" 选项**
Unity 5.5 引入 `Spatialize Post Effects` 选项，控制空间化处理是在 DSP 效果链之前还是之后执行。若混响效果器在空间化之前运行，混响的方位感会丢失；将 `Spatialize Post Effects` 设为 true，混响将在已空间化的双耳信号上叠加，效果更真实。

**误区五：AudioSource.PlayClipAtPoint 的性能陷阱**
该方法每次调用都会创建一个临时 GameObject 并在播放结束后销毁，高频调用（如爆炸、射击）会触发大量 GC，在移动平台上导致明显卡顿。推荐使用自定义的