---
id: "particle-rendering"
concept: "粒子渲染"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 2
is_milestone: false
tags: ["特效"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 99.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---




# 粒子渲染

## 概述

粒子渲染是游戏引擎渲染管线中专门处理大量细小、短暂视觉元素的技术体系，用于模拟火焰、烟雾、爆炸、魔法特效、雨雪等自然现象。与静态网格体不同，粒子系统需要在单帧内同时渲染数百到数十万个独立的视觉单元，每个单元拥有独立的位置、旋转、缩放、颜色（RGBA各8位）和生命周期属性。

粒子渲染的起源可追溯到1983年William Reeves在Lucasfilm为电影《星际迷航II：可汗之怒》制作"创世纪装置"特效时正式提出并发表的粒子系统理论（Reeves, 1983，《ACM SIGGRAPH Computer Graphics》Vol.17 No.3）。该论文中首次将大量独立运动的微小元素集合定义为"粒子系统"，并描述了随机速度分布、生命周期控制等核心机制。随后，这一概念被游戏业界采用，早期如Amiga平台上的游戏已使用数百个CPU驱动粒子。DirectX 11于2009年正式引入计算着色器（Compute Shader，Shader Model 5.0），使GPU粒子成为主流方案，允许在GPU上并行模拟百万级别粒子而不占用主线程资源。

粒子渲染之所以需要专门的管线处理，是因为粒子数量庞大、生命周期极短（通常0.1秒到10秒之间）、几何形状极简（多为平面四边形，仅4顶点2三角形），且半透明粒子的渲染顺序直接影响Alpha混合结果的正确性。这些特征与常规不透明几何体的渲染策略截然不同，需要单独设计排序、剔除和批处理策略。参考文献：《Real-Time Rendering》第4版（Akenine-Möller et al., 2018，CRC Press）第13章对粒子系统渲染给出了系统性阐述。

---

## 核心原理

### Billboard 粒子

Billboard是最基础也最常见的粒子渲染形式，其本质是一个始终朝向摄像机的四边形（Quad），由2个三角形组成，共4个顶点，UV坐标范围为 $(0,0)$ 到 $(1,1)$。Billboard的朝向分为三种模式：

- **屏幕对齐（Screen-Aligned）**：四边形完全平行于屏幕平面，即使摄像机滚转（Roll）也不影响粒子外观，适用于UI叠加式粒子特效。
- **摄像机朝向（Camera-Facing）**：四边形法线始终指向摄像机位置而非摄像机朝向，当粒子位于视锥边缘时与Screen-Aligned有明显差异，适用于世界空间中有体积感的烟雾球。
- **轴对齐（Axis-Aligned / Velocity-Aligned）**：四边形绕一条固定轴（如Y轴）或沿速度方向旋转，常用于模拟竖直烟柱或子弹拖尾。

Billboard的朝向矩阵直接取自View矩阵中的基向量：粒子局部坐标的右向量 $\mathbf{R}$ 取View矩阵第一列，上向量 $\mathbf{U}$ 取View矩阵第二列，四个顶点的世界空间坐标为：

$$
\mathbf{v}_0 = \mathbf{C} - \frac{W}{2}\mathbf{R} - \frac{H}{2}\mathbf{U}, \quad
\mathbf{v}_1 = \mathbf{C} + \frac{W}{2}\mathbf{R} - \frac{H}{2}\mathbf{U}
$$

$$
\mathbf{v}_2 = \mathbf{C} + \frac{W}{2}\mathbf{R} + \frac{H}{2}\mathbf{U}, \quad
\mathbf{v}_3 = \mathbf{C} - \frac{W}{2}\mathbf{R} + \frac{H}{2}\mathbf{U}
$$

其中 $\mathbf{C}$ 为粒子中心的世界坐标，$W$ 和 $H$ 分别为粒子的宽度和高度（单位：米）。

实现时可在几何着色器（Geometry Shader）中将单个点图元扩展为四顶点四边形，节省顶点缓冲带宽；但几何着色器在某些移动GPU（如高通Adreno 600系列）上存在显著性能开销，现代实践更倾向于在顶点着色器中通过 `gl_VertexID % 4` 直接索引偏移，配合实例化绘制（Instanced Draw）一次调用绘制全部粒子。

### GPU 粒子与 Compute Shader 模拟

GPU粒子将粒子的物理模拟——位置更新、速度积分、碰撞检测、生命周期递减——全部搬到GPU计算着色器中执行。粒子数据存储在两个乒乓（Ping-Pong）结构的结构化缓冲区（`StructuredBuffer<ParticleState>`）中：一帧读取缓冲A并将结果写入缓冲B，下一帧反向操作，避免读写竞争。

位置和速度的更新采用显式欧拉积分：

$$
\mathbf{P}(t+\Delta t) = \mathbf{P}(t) + \mathbf{V}(t)\cdot\Delta t
$$

$$
\mathbf{V}(t+\Delta t) = \mathbf{V}(t) + \mathbf{A}\cdot\Delta t
$$

其中 $\mathbf{A}$ 为合加速度向量（$\mathbf{g} = (0, -9.8, 0)\ \mathrm{m/s^2}$ 叠加风力、湍流等），$\Delta t$ 为帧时间（秒）。对于需要精确物理的场景，可改用二阶 Verlet 积分以减少数值漂移，但计算量增加约40%。

以下为一段简化的 HLSL Compute Shader 核心逻辑示例：

```hlsl
// 每个线程处理一个粒子，线程组大小64
[numthreads(64, 1, 1)]
void CS_SimulateParticles(uint3 id : SV_DispatchThreadID)
{
    uint index = id.x;
    if (index >= g_MaxParticles) return;

    ParticleState p = ReadBuffer[index];

    // 生命周期递减
    p.LifeTime -= g_DeltaTime;
    if (p.LifeTime <= 0.0f)
    {
        // 将索引归还自由列表（原子操作）
        uint freeSlot;
        InterlockedAdd(FreeListCounter[0], 1, freeSlot);
        FreeList[freeSlot] = index;
        p.Active = 0;
    }
    else
    {
        // 欧拉积分更新速度与位置
        p.Velocity += g_Gravity * g_DeltaTime;
        p.Position += p.Velocity * g_DeltaTime;

        // Alpha随生命周期线性衰减
        p.Color.a = p.LifeTime / p.MaxLifeTime;
    }

    WriteBuffer[index] = p;
}
```

GPU粒子的发射与死亡管理通过原子计数器（`InterlockedAdd`）配合"自由列表（Free List）"缓冲实现，完全无需每帧回读数据到CPU。Unreal Engine的**Niagara**系统（UE4.20起引入，2018年）和Unity的**VFX Graph**（Unity 2019.3正式发布）均采用此架构，最大粒子容量可配置到100万个，在RTX 3080上单帧模拟100万粒子约耗时0.8毫秒（不含渲染）。

### Ribbon 粒子

Ribbon（条带）粒子将同一发射器连续发射的粒子点串联成一条光滑曲线几何体，常用于模拟闪电、刀光、剑气、飞行轨迹、魔法圆弧等拖尾效果。Ribbon几何体由相邻粒子点之间的"样条挤出"构成：对于相邻粒子点 $\mathbf{P}_i$ 和 $\mathbf{P}_{i+1}$，沿连线方向的屏幕空间法线方向拉伸宽度 $W_i$，形成一段矩形。

完整的Ribbon由 $N$ 个粒子点生成 $N-1$ 段矩形，共 $2N$ 个顶点、$(N-1)\times2$ 个三角形。为避免相邻段之间的接缝断裂，通常在连接处插入米特（Miter）接头：计算相邻两段切线方向的角平分线，在该方向上延伸宽度除以 $\cos(\theta/2)$（$\theta$ 为夹角）来补偿透视收缩。

Ribbon粒子的顶点数量随活跃粒子点数动态变化，因此需要动态顶点缓冲（Dynamic Vertex Buffer）或GPU端生成几何体，Unreal Engine中每条Ribbon最多支持500个控制点。

### Mesh 粒子

Mesh粒子将一个三维网格体（如石块、树叶、弹壳）作为粒子的渲染单元，每个粒子实例对应一份网格体的独立变换矩阵（位置、旋转、缩放）。Mesh粒子使用GPU实例化（`DrawMeshInstanced`）一次Draw Call渲染数千个实例，每个实例的变换数据存储在实例化数据缓冲（Instance Buffer）中，顶点着色器通过 `SV_InstanceID` 索引读取对应矩阵。

Mesh粒子的碰撞检测比Billboard复杂，因为网格体有实际体积，通常简化为包围球（Bounding Sphere）与场景深度图（Depth Buffer）的离线碰撞，而非精确三角形相交检测。在Unreal Engine中，Mesh粒子模块支持"世界碰撞"开关，开启后每帧额外消耗约0.2ms（以10,000个Mesh粒子为基准，RTX 2080）。

---

## 关键公式与排序算法

半透明粒子必须按照**从后到前（Back-to-Front）**的顺序绘制，才能保证Alpha混合（$\text{dst} = \text{src}\cdot\alpha + \text{dst}\cdot(1-\alpha)$）结果正确。排序以粒子中心到摄像机的距离 $d_i = |\mathbf{P}_i - \mathbf{Eye}|$ 为键值，对所有活跃粒子执行降序排列。

CPU端可使用 `std::sort`（复杂度 $O(N\log N)$），但10万粒子每帧排序约耗时2ms，成为瓶颈。GPU端可使用**Bitonic Sort**（双调排序），其并行复杂度为 $O(\log^2 N)$，在Compute Shader中对65536个粒子排序约耗时0.15ms（RTX 3070）。

实际工程中常用**近似排序**：将粒子按发射时间（粒子越新越靠前绘制）代替距离排序，牺牲少量正确性换取排序开销接近零，Unreal Engine Niagara的默认排序模式即为此策略。

---

## 实际应用案例

**案例：《赛博朋克2077》的雨粒子系统**（CD Projekt Red, 2020）使用约200,000个GPU Billboard粒子模拟降雨，每个粒子为竖直轴对齐的拉伸Billboard（高度约0.3米，宽度0.01米），速度在 $-8$ 到 $-12\ \text{m/s}$ 之间随机分布，与风向场叠加产生斜雨效果。雨滴击打地面时触发Splash子发射器，生成2到5个放射状Billboard，生命周期0.15秒。整个雨效在PS5上占用约1.2ms的GPU时间。

**案例：Unity VFX Graph爆炸效果**：典型配置为5,000个Mesh粒子（低多边形石块，约80三角形/个）与20,000个Billboard烟雾粒子组合。Mesh粒子使用Verlet积分并与深度图碰撞弹跳，Billboard烟雾使用Soft Particle（软粒子）技术避免与场景几何体的硬边相交：在片元着色器中对比粒子深度与场景深度图，差值小于0.5米时线性淡出Alpha。

---

## 常见误区

**误区1：所有粒子都必须排序**。不透明粒子（Additive混合、粒子本身完全不透明）无需排序，加法混合（Additive Blending，$\text{dst} = \text{src}\cdot\alpha + \text{dst}$）结果与绘制顺序无关，可直接跳过排序步