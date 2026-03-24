---
id: "cg-vegetation"
concept: "植被渲染"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 3
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 植被渲染

## 概述

植被渲染是实时图形学中专门针对树木、草地、灌木等自然植物的几何表示与绘制技术体系。与建筑或机械等硬表面物体不同，植被具有数量极多、形态高度随机、叶片半透明且受风力驱动运动等特殊属性，使得直接使用标准网格渲染管线代价极高。一个典型开放世界场景中可能需要同时渲染数十万株草丛和数千棵树木，这迫使图形工程师发展出一套专属的渲染优化策略。

植被渲染技术的奠基性工作可追溯到1985年Loren Carpenter在SIGGRAPH上提出的分形树木渲染，以及1986年Prusinkiewicz基于L-系统的植物形态生成。进入实时渲染领域后，SpeedTree工具库（2002年由IDV公司发布）成为行业标准，其LOD管线与风动画方案被《荒野大镖客2》《地平线：西部禁域》等众多AAA游戏所采用。

植被渲染的核心挑战在于三个相互制约的维度：视觉真实性（叶片的半透明、自遮蔽、色散）、运动真实性（自然风力驱动的分层抖动）和渲染性能（Draw Call压缩、GPU并行化）。这三者的平衡决定了一款游戏在开放世界场景中的帧率表现与画面质量上限。

---

## 核心原理

### LOD策略：从几何体到公告板

植被LOD（细节层次）系统通常设计为3至5个层级，每个层级采用截然不同的几何表示方式。**第0级（近距离，0-10米）**使用完整多边形树冠，每棵树可能包含2000-8000个三角形，叶片为独立双面四边形（Billboard Quad），并绑定完整骨骼或蒙皮数据用于风动画。**第1-2级（中距离，10-50米）**将叶片合并为若干簇状几何体（Cluster Billboard），三角形数降至200-600个。**第3级（远距离，50-200米）**退化为单张或交叉两张公告板（Crossed Billboard），仅用4-8个三角形表示整棵树。**第4级**则完全剔除，仅在深度缓冲中保留，或使用2D远景贴图（Impostor）覆盖地平线。

LOD切换时若直接跳变会产生明显的"弹出"（Popping）瑕疵。解决方案是**LOD渐变融合（LOD Dithering/Crossfade）**：在阈值距离前后约2米范围内，同时渲染相邻两个LOD级别，通过抖动透明度（Dither Alpha）在屏幕空间逐像素交替显示，肉眼感知为平滑过渡。Unity HDRP和Unreal Engine 5均内置此机制，UE5中对应参数为`r.LOD.FadeOutTime`控制融合时间窗口。

### 风动画：顶点着色器中的层级运动

植被风动画的关键思路是**完全在顶点着色器（Vertex Shader）中计算位移**，避免CPU逐帧更新骨骼矩阵的开销。SpeedTree提出的经典三层风模型被行业广泛沿用：

- **主干弯曲（Primary Bending）**：整棵树作为悬臂梁整体摇摆，位移量与顶点高度成正比，公式为 $\Delta pos = A \cdot h \cdot \sin(\omega t + \phi)$，其中 $A$ 为风力振幅，$h$ 为顶点相对根部高度，$\omega$ 为角频率，$\phi$ 为相位偏移（由世界坐标哈希生成，使相邻树木不同步）。
- **枝条摆动（Secondary Bending）**：各主枝条独立振动，频率约为主干的2-4倍，振幅由存储在顶点色（Vertex Color）或UV2通道中的权重蒙版控制。
- **叶片颤动（Leaf Flutter/Turbulence）**：单片叶子的快速随机颤抖，频率约5-15 Hz，通过对叶片中心位置应用Perlin噪声偏移实现，赋予自然感的细节层次。

风场本身通常以一张流动的2D向量纹理（Wind Vector Map）或全局参数形式传入着色器，支持定向风与湍流混合。

### GPU实例化与批次合并

草地渲染对Draw Call数量要求极为苛刻。现代引擎使用**GPU Instancing**将同一网格的所有实例合并为单次Draw Call，通过实例缓冲区（Instance Buffer）传递每株草的世界矩阵、随机种子和LOD权重。更激进的方案是**间接绘制（Indirect Draw）**：CPU仅提交一次`DrawMeshInstancedIndirect`命令，由GPU上的Compute Shader执行视锥体剔除（Frustum Culling）和遮挡剔除（Hi-Z Occlusion Culling），将通过测试的实例写入参数缓冲区，完全绕开CPU瓶颈。Unreal Engine 5的Nanite草地插件和Unity的Terrain Detail Instancing均基于此架构，可在单帧内处理百万级草叶实例，GPU负载相比CPU分发方案降低约60-80%。

---

## 实际应用

**《旷野之息》草地系统**：任天堂为Switch有限的GPU带宽设计了极轻量级的草地方案。每株草仅使用3个顶点（单三角形），依靠几何着色器扩展为面向摄像机的扇形，法线经过球形化处理以模拟体积感。整个草地以16×16米的地块为单位批量实例化，超过30米后直接裁剪，牺牲了远景草地但将帧率稳定在30fps。

**《地平线：西部禁域》树木渲染**：Guerrilla Games在GDC 2022演讲中披露，其树木系统在距离摄像机200米以外切换为预渲染的球形谐波（Spherical Harmonics）光照公告板，结合TAA抖动消除边缘锯齿，使远景树林密度提升4倍而不增加额外的几何处理开销。

**草地交互压弯**：当角色走过草地时，需要使草叶产生被踩踏的压弯效果。常见实现是维护一张动态渲染的**交互贴图（Interaction Map）**，跟随角色在草地上滑动，角色位置写入一个移动的圆形压力区域，草地顶点着色器采样此贴图决定额外的弯曲偏移量，过一段时间后恢复弹起。

---

## 常见误区

**误区一：公告板树木在任何视角下都会穿帮**

初学者常认为远距离公告板只能在固定朝向下看起来正确。实际上现代引擎使用**八向（8-way）或十六向Impostor**：在资源预处理阶段从16个水平方向预渲染同一棵树的快照，运行时根据摄像机方位角选择最接近的两张并做插值混合。这种方案在200米以上的距离中视觉欺骗效果良好，玩家几乎无法察觉其为平面贴图。

**误区二：所有叶片都应开启Alpha Test**

Alpha Test（即丢弃透明度低于阈值的像素）是最直接的叶片镂空方案，但它会打断GPU的Early-Z深度测试优化，导致大量过绘制（Overdraw）。对于草地等密集植被，更高效的方案是使用**Alpha To Coverage**配合MSAA：它将透明度信息编码进MSAA的子采样掩码，无需discard指令，既保留半透明边缘的抗锯齿又不破坏Early-Z，性能通常优于Alpha Test约15-30%。

**误区三：风动画的相位偏移靠随机数组**

部分实现将每棵树的风相位存储为CPU端的随机数组，每帧通过Uniform变量上传。这在树木数量超过数千棵时会产生显著的CPU上传开销和着色器状态切换。正确做法是在顶点着色器内部用树木的**世界空间根坐标进行哈希计算**（如 `frac(sin(dot(rootPos.xz, float2(12.9898, 78.233))) * 43758.5453)`），实现零额外数据传输的个体相位差异化。

---

## 知识关联

植被渲染建立在**地形几何**的基础之上：地形的高度图数据为植被密度分布和实例放置提供参照坐标，植被实例通常通过对地形法线采样来对齐倾斜坡面，确保树木沿坡面法线方向生长而非全部垂直向上。植被系统还与地形的纹理混合层（Splat Map）耦合：草地类型纹理区域对应密集草叶生成，岩石区域则抑制植被密度，两者共享同一套UV坐标系。

在渲染管线层面，植被渲染对**剔除系统**（Culling System）和**阴影渲染**提出特殊需求：叶片的半透明性使阴影必须使用Alpha Test Shadow Map或Moment Shadow Map来产生正确的枝叶投影，而非标准的不透明深度写入。这些关联使植被渲染成为连接几何处理、光照计算与GPU性能优化的综合性技术领域。
