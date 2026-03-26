---
id: "vfx-niagara-data-interface"
concept: "数据接口"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 数据接口（Niagara Data Interface）

## 概述

Niagara Data Interface（简称NDI）是Unreal Engine Niagara粒子系统中用于连接外部数据源的专用桥梁模块。它允许粒子模拟在运行时读取来自引擎其他子系统的数据，包括静态网格体（Static Mesh）、骨骼网格体（Skeletal Mesh）、2D纹理、体积纹理、音频波形（Audio Oscilloscope/Spectrum）以及场景深度缓冲等。没有Data Interface，Niagara模拟只能在自身的封闭参数空间内运行，无法感知场景中其他资产的实时状态。

Data Interface最早在UE4.20随Niagara系统正式对外公开时引入，取代了旧版Cascade粒子系统中通过材质参数传递采样信息的低效方案。其核心设计理念是将数据提供者（Data Provider）与粒子逻辑解耦：NDI负责封装访问协议，Niagara脚本只需调用标准化的函数节点，无需了解底层的内存布局或GPU资源绑定细节。

NDI在实际项目中解决的典型问题是：让粒子"感知"角色的骨骼位置从而实现毛发模拟，让音频频谱数据驱动粒子爆炸规模，以及让粒子在网格体表面均匀分布而不穿插几何体。这些需求如果没有Data Interface机制，要么需要手动将数据烘焙为纹理再间接采样，要么根本无法实时响应。

---

## 核心原理

### 数据接口的类型与注册方式

UE5中内置的Data Interface类型超过30种，常用的包括：

- **UNiagaraDataInterfaceStaticMesh**：暴露静态网格体的顶点位置、法线、UV、三角形采样等函数。
- **UNiagaraDataInterfaceSkeletalMesh**：提供骨骼变换、蒙皮顶点、骨骼速度等实时数据，支持`Get Bone Position`、`Get Skinned Triangle Data`等节点。
- **UNiagaraDataInterfaceTexture2D** / **UNiagaraDataInterfaceVolumeTexture**：允许粒子在GPU线程直接采样纹理的RGBA值，函数签名为`SampleTexture(UV, OutColor)`。
- **UNiagaraDataInterfaceAudioSpectrum**：将音频频谱的频率幅值（0.0–1.0归一化）映射为粒子参数，精度最高支持512个频率桶（Frequency Bins）。

每种NDI在Niagara System的"用户参数"或"系统参数"面板中注册为一个具名变量（如`MyMesh`、`AudioData`），然后在Emitter Update或Particle Update的HLSL/可视化脚本中通过绑定该变量名来调用其函数。

### CPU端与GPU端的访问差异

Data Interface的函数分为CPU-only和CPU+GPU两类，这是NDI使用中最需要关注的限制。

以`UNiagaraDataInterfaceSkeletalMesh`为例：`Get Bone Position`支持GPU执行，因为骨骼变换矩阵会在每帧提交到GPU的Structured Buffer；而`Get Num Triangles`默认仅在CPU执行，因为读回三角形数量需要同步，代价高昂。若将仅CPU的函数误放入GPU模拟的Particle Update阶段，编译时会产生错误：`Data Interface function 'X' does not support GPU simulation`。

GPU模式下，NDI通过`FNiagaraDataInterfaceProxy`机制在渲染线程维护一个镜像代理对象，每帧将CPU端资源的描述符（如纹理SRV、Buffer SRV）推送至GPU端，供HLSL代码通过`DECLARE_NIAGARA_DI_PARAMETER`宏访问。

### 骨骼网格体Data Interface的采样精度

骨骼网格体NDI提供两种顶点采样模式：
1. **Direct Index**：按顶点索引直接访问，适合确定性粒子附着（如毛囊粒子贴合皮肤）。
2. **Random Triangle**：在三角形面积加权的随机分布上采样，保证粒子在曲面的均匀密度，计算公式为对每个三角面积 $A_i$ 做归一化累积分布，再以均匀随机数 $u \in [0,1)$ 二分查找命中三角形。

使用`Get Skinned Vertex Data`时，蒙皮计算在前一帧的GPU Skin Pass结果上进行，存在1帧延迟，需要在设计时通过预测速度（Prev Position + Velocity × DeltaTime）补偿位移。

---

## 实际应用

**角色毛发/布料粒子附着**：在第三人称游戏中，将骨骼网格体（角色Body Mesh）绑定到NDI，使用`Get Skinned Triangle Coordinate`在角色皮肤上生成粒子初始位置，每帧调用`Get Skinned Vertex Velocity`让粒子跟随皮肤运动。《黑神话：悟空》等使用Niagara实现毛发模拟时即采用此类方案。

**音频可视化粒子**：将`AudioSpectrum` Data Interface的频率幅值数组映射到粒子的`Scale`或`Color`参数。例如，将低频段（20–200 Hz对应Bin 0–10）映射到粒子半径，高频段（2 kHz以上）映射到粒子颜色饱和度，实现随音乐律动的粒子效果。

**碰撞数据接口场景深度**：`UNiagaraDataInterfaceSceneDepth`允许粒子读取当前帧的深度缓冲，实现软碰撞：当粒子的投影深度与场景深度之差小于阈值（如5 cm）时，粒子受到排斥力，避免穿插任意几何体，且无需物理碰撞体，GPU开销极低。

---

## 常见误区

**误区一：认为Data Interface可以在任何模拟阶段自由调用**
实际上每个NDI函数都有明确的执行阶段限制。例如`UNiagaraDataInterfaceRenderTarget2D`的写入函数`SetRenderTargetValue`只能在`Emitter Update`或`Simulation Stage`中调用，若放入`Particle Spawn`阶段因执行顺序问题会写入错误帧的数据。必须仔细查阅每个函数节点右键属性中的`Supported Contexts`标注。

**误区二：以为绑定同一个NDI实例会自动共享GPU缓存**
当同一Niagara System中有多个Emitter都绑定了同一个`SkeletalMesh` NDI变量时，每个Emitter的`FNiagaraDataInterfaceProxy`是独立的，蒙皮数据会在GPU端被拷贝多份。正确做法是在System级别声明一个`System Data Interface`变量，由所有Emitter共享同一个代理实例，避免重复的`RHI::CopyBuffer`开销。

**误区三：混淆Data Interface与动态材质参数的适用场景**
Data Interface是在粒子模拟计算阶段（Simulation）读取数据，影响粒子的位置、速度、颜色等属性；动态材质参数是在粒子渲染阶段影响着色结果。若需要纹理颜色影响粒子的运动轨迹，必须用`Texture2D` Data Interface在Particle Update中采样；若只需影响视觉外观而不改变粒子行为，则应通过材质参数集传递，不应滥用NDI增加模拟阶段的采样开销。

---

## 知识关联

**与事件系统的关系**：Niagara事件系统（Event Handler）负责Emitter之间的粒子数据传递，而Data Interface负责Niagara系统与引擎外部资源之间的数据读取。两者互补：事件系统处理"粒子生成粒子"的内部通信，Data Interface处理"粒子读取场景"的外部感知。理解事件系统的执行时序有助于判断在哪个事件阶段调用Data Interface函数最为合适，例如在`OnParticleSpawn`事件处理中调用`Get Skinned Position`初始化粒子位置。

**对渲染器类型的影响**：Data Interface在模拟阶段写入的粒子属性（如`DynamicMaterialParameter`）最终需要被Niagara渲染器消费。不同渲染器类型（Sprite Renderer、Mesh Renderer、Ribbon Renderer）对粒子属性的绑定方式不同，例如Mesh Renderer可以通过`Mesh Orientation`属性直接对接骨骼NDI输出的法线方向，而Sprite Renderer则需要额外的旋转转换节点。选择渲染器类型时必须考虑Data Interface已经提供了哪些几何信息，以最小化重复计算。