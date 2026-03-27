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
quality_tier: "B"
quality_score: 49.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
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

Mesh粒子是Niagara粒子系统中使用3D网格体（Static Mesh或Skeletal Mesh）作为粒子视觉表示的技术方案。与使用Billboard平面图片的Sprite粒子不同，每个Mesh粒子都是一个完整的三维模型，拥有真实的体积感、物理遮挡关系和法线光照响应。这一特性使其成为实现弹壳飞溅、玻璃碎片、飘落树叶、破碎砖块等需要真实立体感特效的首选方式。

Mesh粒子在Unreal Engine 4的Cascade系统中已有原型实现（通过Mesh TypeData模块），但在Niagara系统（随UE4.20正式引入）中得到根本性重构。Niagara将Mesh渲染器抽象为独立的Render模块，允许在同一粒子发射器（Emitter）内混合使用多种渲染器，并通过HLSL自定义表达式精确控制每个Mesh实例的几何变换。这种灵活性是Cascade时代无法实现的。

Mesh粒子的重要性体现在它直接利用GPU Instancing（实例化绘制）技术，将数千个相同网格的绘制合并为单次Draw Call，因此在性能上远优于将同等数量的Static Mesh Actor手动放置于场景。一颗手榴弹爆炸产生500块碎片，若用独立Actor实现会产生500次Draw Call，改用Mesh粒子则仅需1至2次。

## 核心原理

### Mesh Renderer模块配置

在Niagara Emitter的Render栈中添加**Mesh Renderer**时，核心参数包括：
- **Particle Mesh**：指定用于渲染的Static Mesh资产，可同时指定多个Mesh并通过`MeshIndex`粒子属性随机选取
- **Override Materials**：是否覆盖Mesh原有材质，通常需启用以支持粒子颜色参数传递
- **Enable Frustum Culling**：开启视锥剔除，超出摄像机视野的粒子网格停止渲染

粒子的变换由三组专属属性驱动：`Position`控制世界坐标，`Scale`控制三轴缩放（类型为Vector3，而非Sprite粒子的标量Size），`MeshOrientation`使用四元数（Quaternion）存储旋转，这与Sprite粒子依赖`SpriteRotation`标量角度有本质区别。

### 旋转与角速度计算

Mesh粒子的旋转控制是其技术难点核心。`MeshOrientation`为**四元数格式**，不能直接赋值欧拉角，需使用Niagara内置函数`QuatFromAxisAngle(Axis, Angle)`将轴角对转换为四元数，或使用`QuatMul(Q1, Q2)`叠加两个旋转。

实现持续自旋的标准做法是在Particle Update阶段使用以下逻辑：
```
// 每帧增量旋转
DeltaRotation = QuatFromAxisAngle(AngularVelocityAxis, AngularSpeed * DeltaTime)
MeshOrientation = QuatMul(MeshOrientation, DeltaRotation)
```
其中`AngularSpeed`单位为**弧度/秒**，弹壳飞出时的典型自旋速度为10至30弧度/秒（约1.6至4.8圈/秒），落叶飘落通常设为0.5至2弧度/秒。

### 物理碰撞与反弹

Mesh粒子配合**Collision模块**可实现地面碰撞弹跳，关键参数为：
- **Restitution（弹性系数）**：弹壳约0.4至0.6，树叶约0.05至0.1（几乎不反弹）
- **Friction（摩擦系数）**：影响碰撞后的切向速度衰减
- **Collision Radius Scale**：碰撞检测使用的是球形近似，该参数缩放球体半径以匹配Mesh实际尺寸

碰撞后若需触发额外效果（如弹壳落地声音），可通过**Event Handler**接收Collision事件，在碰撞位置生成子发射器粒子。

### LOD与性能管理

Mesh粒子自动继承Static Mesh资产的**LOD（细节层次）**设置。建议为粒子专用Mesh创建极简LOD1（仅保留轮廓，三角面数降至LOD0的10%至20%），在距离超过500厘米时自动切换。通过**Scalability（可伸缩性）**设置，低端机可将`MaxParticleCount`从PC版的200颗碎片降至移动版的30颗。

## 实际应用

**弹壳抛出特效**：枪械射击时从弹舱位置发射弹壳Mesh粒子，初速度为`{200-400, 50-150, 0}`厘米/秒（侧向+向上分量），叠加每帧自旋更新，设置Restitution=0.5使弹壳在地面多次弹跳，粒子生命周期设为3至5秒后淡出消失。

**爆炸碎片飞溅**：使用Burst发射模式在0.05秒内一次性发射50至200个碎片Mesh，通过`Initial Velocity`模块的Cone形随机分布控制飞散角度（典型锥角120度），配合`Drag`模块模拟空气阻力，使碎片在0.3秒内迅速减速。为增加视觉多样性，可在Particle Mesh处放入3至5种不同形状的破碎块Mesh，通过`UniformRandInt(0,4)`随机选取。

**秋季落叶效果**：将树叶多边形Mesh（约80至120三角面）设置为粒子，在`Wind Force`模块中叠加正弦波侧向扰动（振幅10至30厘米，频率0.3至0.8Hz）模拟风吹效果，同时缓慢更新MeshOrientation实现翻滚，Restitution设为0.02使落地后立即静止。

## 常见误区

**误区一：用欧拉角直接赋值MeshOrientation**
初学者常尝试将`(Roll, Pitch, Yaw)`角度直接写入`MeshOrientation`变量，导致粒子出现异常扭曲或不旋转。正确做法是始终使用`QuatFromAxisAngle`或`RotationFromEuler`转换函数，因为`MeshOrientation`在内存中存储的是四元数的四个分量`(X, Y, Z, W)`，直接赋数值角度会破坏四元数的单位长度约束（|Q|=1）。

**误区二：将高面数模型直接用作粒子Mesh**
将5000+面的角色模型或道具直接指定为Mesh粒子，当粒子数量达到100个时等效于渲染50万面，极易造成GPU过载。粒子专用Mesh应控制在50至300三角面，通过LOD和低精度法线贴图来弥补细节损失，而非依赖高模面数。

**误区三：忽略Mesh的Pivot（轴心点）位置**
粒子的`Position`坐标对应Mesh的Pivot点（原点），若Mesh在建模软件中Pivot位于几何中心，弹壳会以中心为基准旋转；若Pivot偏移到弹壳底部，旋转表现会截然不同。弹壳、碎片类Mesh的Pivot应设在质心位置，落叶类Mesh的Pivot建议设在叶柄根部以获得更真实的翻转效果。

## 知识关联

**与Ribbon特效的对比**：Ribbon粒子生成连续的带状曲面（适合光剑轨迹、烟雾拖尾），Mesh粒子生成离散的独立3D实体（适合固体碎片），两者渲染机制不同——Ribbon通过相邻粒子位置插值构建面片，Mesh直接实例化现有网格体，不存在粒子间连接关系。在同一Emitter中可同时添加两种Renderer叠加效果，例如飞舞的羽毛用Mesh粒子表现翎管，用Ribbon粒子表现羽毛脱落时的轨迹拖尾。

**通向GPU模拟**：Mesh粒子默认在CPU上计算每帧的位置、旋转和缩放更新，当粒子数量超过500至1000个时，CPU计算开销开始成为瓶颈。启用**GPU模拟（GPU Simulation）**后，所有粒子更新逻辑转移至Compute Shader执行，可将Mesh粒子数量提升至数万个而不显著增加CPU开销，这是实现大规模碎石崩落、漫天飞雪等宏观特效的技术基础。GPU模拟对Mesh粒子的主要限制是不支持Collision模块的精确射线检测，需改用深度缓冲近似碰撞方案。