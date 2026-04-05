---
id: "vfx-niagara-mesh"
concept: "Mesh粒子"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Mesh粒子

## 概述

Mesh粒子是Niagara系统中使用静态网格体（Static Mesh）作为粒子单元的渲染方式，区别于Sprite粒子的2D公告板，每个粒子实例都是一个完整的3D几何体，拥有真实的体积感和多角度可见性。碎石崩飞、弹壳弹跳、秋叶飘落这类需要从任意视角观察都保持立体外形的特效，必须使用Mesh粒子才能达到可信的视觉效果。

Mesh粒子在Unreal Engine 4.20随Niagara系统正式引入时便作为核心渲染器类型之一提供，替代了Cascade时代的"Mesh Emitter"。与Cascade相比，Niagara的Mesh粒子将每个网格体实例的Transform、颜色、自定义数据全部打包进GPU实例化绘制调用（Instanced Draw Call），单个发射器支持同时渲染数万个网格体而不成倍增加Draw Call数量。

Mesh粒子的性能表现与所选网格体的多边形密度直接挂钩。一个三角面数超过500的Static Mesh用于需要同时存在2000个实例的弹壳特效，会比同等数量的Sprite特效消耗高出数倍的顶点着色器开销。因此选择专用低面数模型（通常50到200三角面）是Mesh粒子工程化落地的必要前提。

---

## 核心原理

### Mesh渲染器的配置结构

在Niagara发射器中添加**Mesh Renderer**模块后，需要在"Meshes"数组中指定一个或多个Static Mesh资产。当数组包含多个网格体时，Niagara通过`MeshIndex`粒子属性决定每个粒子实例选用哪个网格，这一特性常用于制作碎片种类随机化的岩石爆破效果——同一发射器可以混合三种不同形状的石块模型。

**Override Materials**选项允许用Niagara的动态材质参数覆盖网格体的原始材质，配合`Dynamic Material Parameter`模块，可以让每个叶片粒子携带独立的枯黄程度参数，通过材质中的`DynamicParameter`节点读取并调整颜色偏移。

**Facing Mode**是Mesh渲染器独有的朝向控制参数，提供四种模式：
- `Default`：粒子使用粒子自身的旋转矩阵，适合弹壳翻滚
- `Velocity`：网格体X轴对齐速度方向，适合飞行中的箭矢或螺旋弹
- `Camera`：始终面向摄像机，退化为类Sprite行为，通常不在Mesh粒子中使用
- `Custom Half Vector`：沿自定义向量对齐，用于特殊物理模拟

### 粒子Transform的三重属性

Mesh粒子的空间变换由三个独立的粒子属性控制，与Sprite的二维Scale完全不同：
- `Position`（Vector3）：世界空间或本地空间坐标
- `MeshOrientation`（Quaternion）：四元数旋转，模块`Initial Mesh Orientation`提供随机锥形旋转初始化，`Mesh Rotation Rate`以度/秒为单位持续旋转
- `Scale`（Vector3）：三轴独立缩放，允许在Z轴压扁弹壳

弹壳翻滚的标准做法是：在`Particle Spawn`阶段用`Initial Mesh Orientation`随机化起始角度，在`Particle Update`阶段用`Mesh Rotation Rate`设置每轴50到300度/秒的旋转速率，同时向Z轴施加重力加速度`-980 cm/s²`模拟弹道。

### 碰撞与网格体的配合

Mesh粒子在启用`Collision`模块后，碰撞检测形状始终是**球形包围盒**，半径由`Collision Radius`参数控制，而非实际网格体的精确几何形状。这意味着一个L形弹壳模型的碰撞实际上是一个包裹它的球体——对于快速运动的小型道具特效而言，这种近似在视觉上完全可接受，且GPU计算代价远低于Mesh精确碰撞。碰撞后可通过`Resilience`（弹性系数，取值0到1）控制反弹程度，弹壳落地通常设置为0.3到0.5。

---

## 实际应用

### 枪械弹壳抛出特效

第一人称射击游戏中的弹壳抛出是Mesh粒子最典型的应用场景。发射器设置为`Burst`模式，每次开枪触发`Spawn Burst Instantaneous`输出1个粒子。弹壳网格体选用专门制作的约80三角面低模，初始速度设置为`(−50, 80, 120) cm/s`（以武器本地空间计算，向右后方抛出），叠加随机偏移`±20 cm/s`避免每次抛出轨迹完全相同。重力模块使用`Apply External Forces`以`980 cm/s²`向下加速，`Drag`设置为0.05模拟空气阻力。弹壳生命周期设置为3至5秒，配合`Color over Life`在最后0.5秒线性淡出透明度，避免突然消失。

### 秋叶飘落环境特效

场景环境特效中，落叶Mesh粒子通常使用`Box`形状发射器在角色上方10米处持续生成，每秒生成约15到30片。叶片网格体需要在Z轴`Scale`上设置0.05到0.1的随机值使其扁平化，模拟真实叶片厚度。`Curl Noise Force`模块以频率0.3、幅度80的设置为每片叶子施加不同的飘移扰动，使叶片呈现自然随风飘荡而非直线下落的轨迹。每片叶子通过`Dynamic Material Parameter`携带独立的颜色种子值（0.0到1.0），材质中用此值在绿、黄、红三色之间插值。

---

## 常见误区

**误区一：直接使用高精度模型**
新手常将场景中现有的高精度道具模型直接拖入Mesh Renderer的Meshes数组。一个面数为8000的精细弹壳模型，在同时存在50个实例时，其顶点着色器开销等同于渲染400000个顶点。Mesh粒子应始终使用专门制作的特效用低模，并关闭`Cast Shadows`选项——粒子特效级别的网格体开启阴影投射会触发额外的深度Pass，开销可能超过渲染本身。

**误区二：用MeshOrientation的Euler角思维调整旋转**
Niagara的`MeshOrientation`属性存储的是四元数，直接在`Set MeshOrientation`中输入Euler角需要先经过`RotatorToQuaternion`节点转换。初学者跳过此转换直接赋值会导致旋转计算出现万向节锁（Gimbal Lock）现象，表现为某个轴向旋转完全失效。正确做法是使用`Mesh Rotation Rate`模块（内部自动处理四元数积分）而不是手动设置每帧的绝对旋转值。

**误区三：认为Mesh粒子必然比Sprite粒子慢**
在需要真实3D外形的场景下，用3张正交Sprite模拟立体感（Cross Billboard技术）的综合开销——3倍的半透明Overdraw、3倍的Sprite粒子数量——往往高于1个低面数Mesh粒子的开销。当网格体面数控制在150以下且关闭半透明时，Mesh粒子的渲染效率可以优于Cross Billboard方案。

---

## 知识关联

Mesh粒子与**Ribbon特效**共同属于Niagara的几何体渲染器家族，但Ribbon生成连续的带状面片用于拖尾，而Mesh粒子生成离散的独立网格体实例；两者可以在同一个Niagara系统中的不同发射器中协作，例如导弹特效同时使用Ribbon发射器制作烟迹拖尾、Mesh发射器制作碎片喷溅。

进入**GPU模拟**阶段后，Mesh粒子的计算从CPU转移至GPU，粒子数量上限从CPU模式的数千个扩展到数十万个。然而GPU模拟对Mesh粒子有一个关键限制：`Fixed Bounds`必须手动设置（GPU无法向CPU回读包围盒数据），且部分碰撞模式在GPU模式下不可用，需要改用`GPU Depth Buffer Collision`替代普通的场景碰撞查询。掌握Mesh粒子的CPU模式配置是迁移到GPU模拟前必须夯实的基础，因为两种模式共享绝大多数模块逻辑，差异主要集中在边界设置和碰撞接口上。