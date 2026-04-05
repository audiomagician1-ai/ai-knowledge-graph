---
id: "ta-impostor"
concept: "Impostor/Billboard"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# Impostor / Billboard（公告牌替代技术）

## 概述

Impostor（冒名顶替体）与 Billboard（公告牌）是 LOD 体系中简化程度最彻底的一级——在极远距离下，用一张带 Alpha 透明通道的 2D 贴图四边形完全取代原始 3D 网格。这张平面由 **2 个三角形（4 个顶点）** 构成，无论原始模型拥有多少多边形，GPU 顶点处理开销都被压缩至理论下限。

该技术的源头可追溯至 id Software 于 **1993 年**发布的《毁灭战士》（*Doom*），游戏中全部敌人角色均以朝向摄像机的 2D 精灵（Sprite）呈现，这一方案本质上就是最原始的球形 Billboard。1998 年，Jakulin 等人在 SIGGRAPH 会议上系统提出"Impostor"概念，将预渲染方向图集与实时视角匹配结合，使非对称物体也能以 2D 卡片近似。2000 年代后，该技术成为大规模植被渲染的标准配置，并在 **SpeedTree SDK**（Interactive Data Visualization 公司，2002 年首发）中获得广泛商业化应用。

关于技术术语区分：**Billboard** 特指实时旋转朝向摄像机的单张贴图平面，适合近似对称物体（树冠、灌木）；**Impostor** 特指预先从多个离散视角烘焙出图像图集、运行时按视角索引显示的方案，能近似非对称形状（建筑、岩石）。两者本质都是"以视图相关的 2D 图像欺骗人眼"，代价是丧失三维视差正确性。

---

## 核心原理

### 朝向对齐的三种模式

Billboard 的视觉质量由顶点着色器中的朝向计算方式决定，共有三种主流模式：

**1. 屏幕对齐（Screen-aligned Billboard）**：四边形始终与视口平面完全平行，法线恒指向 $-\mathbf{z}_{view}$。适合粒子、UI 标注等，但地面植物俯视时贴图倒平，几乎不用于树木。

**2. 摄像机朝向 + 仅 Y 轴旋转（Cylindrical Billboard）**：四边形绕世界空间 Y 轴旋转，使其始终面向摄像机在水平面上的投影方向，根部保持贴地。这是**远景树木 Billboard 最常用方案**，虚幻引擎、Unity 的树木 LOD 末级均默认采用此模式。顶点着色器中只需用摄像机位置与植物根部位置构造水平朝向向量，重建本地 X 轴即可。

**3. 全轴朝向（Spherical Billboard）**：四边形在任意俯仰角下均面向摄像机，需要构造完整的 Look-At 矩阵。适合云朵、远距离爆炸、粒子团。俯视 90° 时会退化为一个点，需特殊处理。

在 GLSL/HLSL 顶点着色器中，Cylindrical Billboard 的核心计算如下：

```hlsl
// Cylindrical Billboard：仅绕 Y 轴朝向摄像机
// _ObjectToWorld[3].xyz = 植物根部世界坐标
// _CameraPos = 摄像机世界坐标

float3 rootWS  = _ObjectToWorld[3].xyz;
float3 toCamera = normalize(_CameraPos - rootWS);

// 在水平面投影，消除 Y 分量
toCamera.y = 0.0;
toCamera   = normalize(toCamera);        // 新的 +Z 轴（朝向摄像机）
float3 up  = float3(0, 1, 0);
float3 right = normalize(cross(up, toCamera)); // 新的 +X 轴

// 用新基向量重建顶点位置
float3 localOffset = input.position.x * right
                   + input.position.y * up;
float4 worldPos = float4(rootWS + localOffset, 1.0);
output.position = mul(_ViewProj, worldPos);
```

### Impostor 图集的烘焙流程

Impostor 的离线烘焙是决定质量的关键环节。主流流程如下：

1. **视角采样**：将虚拟摄像机均匀分布于半球（地面物体）或全球（空中物体）上。常见分辨率为 **8×4=32 方向**（水平 8 档 × 仰角 4 档）或使用八面体映射（Octahedral Impostor）的 **16×16=256 方向**。
2. **离屏渲染（Offscreen Rendering）**：对每个视角渲染 Base Color、World Normal、Depth（可选 PBR 参数）到独立 RT，每帧尺寸通常为 **128×128 或 256×256 像素**。
3. **打包图集**：将所有视角帧拼入同一张图集纹理（典型尺寸 **2048×2048**），并记录每帧 UV 偏移和视角方向向量。
4. **运行时索引**：每帧将视角向量 $\mathbf{v}$ 与图集中存储的所有采样方向 $\mathbf{d}_i$ 做点积，选取 $\arg\max_i (\mathbf{v} \cdot \mathbf{d}_i)$ 对应的帧；更高质量的做法是选最近的两帧做线性混合（Blend Impostor），消除帧切换时的跳变瑕疵。

**Octahedral Impostor**（由 Ryan Brucks 在 2018 年 UE4 博客中推广）是目前最紧凑的方向编码方案：将视角向量通过八面体投影映射到正方形 UV 空间，使图集中每个像素格均匀对应球面方向，一张 2048×2048 的图集可存储 **16×16=256 个视角**的颜色与法线，实现近乎无缝的视角过渡，且法线信息可支持实时光照重计算。

### Alpha Test 与 Alpha Blend 的取舍

Billboard 轮廓裁切依赖透明通道，工程实践中存在两条路径：

**Alpha Test（硬切）**：着色器中调用 `clip(albedo.a - 0.5)` 丢弃 Alpha 低于阈值的像素，完全不产生混合排序问题，可与深度写入兼容。缺点是轮廓锯齿明显，常配合 **Alpha-to-Coverage**（MSAA 的内置特性，将 Alpha 值映射为 MSAA 覆盖掩码，等效亚像素抗锯齿）或 TAA 的时间抖动来缓解。

**Alpha Blend（软混）**：边缘平滑，但必须关闭深度写入并从后向前排序。数万棵树叠加时排序代价极高，且排序错误会导致 Alpha 版本的 Z-fighting（透明层闪烁）。

**工程主流选择**是：Alpha Test + Dither（屏幕空间抖动透明），结合 TAA 时间累积，既规避排序问题又保持轮廓平滑——Unity HDRP 和 UE5 的默认树木材质均采用此方案。

---

## 关键公式与距离判据

Billboard LOD 切换距离通常基于屏幕上的**投影面积（Projected Screen Area）**，而非简单的世界空间距离。设物体包围球半径为 $r$，摄像机到物体距离为 $d$，屏幕垂直分辨率为 $H$，垂直视野角为 $\theta_{fov}$，则物体在屏幕上占据的近似像素高度为：

$$h_{px} = H \cdot \frac{r}{d \cdot \tan(\theta_{fov}/2)}$$

当 $h_{px}$ 低于设定阈值（典型值：**8~16 像素**）时触发 Billboard LOD 切换。此公式说明：**同一棵树在 1080p 与 4K 屏幕下切换距离不同**，这正是引擎通常将 LOD 偏移暴露为可配置参数（UE5 中的 `LODDistanceScale`）的原因。

UE5 的 Hierarchical Instanced Static Mesh（HISM）系统结合 Billboard LOD，对 **10 万棵**远景树仅生成 **1 次 DrawCall**（GPU Instancing），每帧仅提交 $10^5 \times 2 = 2 \times 10^5$ 个三角形，而同等数量的 LOD2 级别（约 200 面/棵）则需提交 $2 \times 10^7$ 个三角形——降幅达 **100 倍**。

---

## 实际应用案例

**案例 1：《巫师 3》（The Witcher 3，CD Projekt Red，2015）的植被系统**  
游戏中植被总实例数超过 **3500 万**棵（据 CD Projekt Red GDC 2016 分享），其中极远距离层级完全使用 Billboard，中间层级使用简化网格，近距离才渲染完整的树木模型与树皮细节。Billboard 贴图尺寸根据树种分级：高大橡树使用 **512×512**，灌木丛使用 **128×128**，有效控制纹理内存预算。

**案例 2：SpeedTree 8.x 的 Impostor 工作流**  
SpeedTree SDK 在导出时自动执行 Impostor 烘焙，默认生成 **8 方向 × 3 仰角 = 24 帧**图集，并将法线贴图一并烘焙，使 Billboard 在不同光照角度下仍能呈现正确的明暗变化，而非静态颜色卡片。这一特性使 Billboard 与动态天光（Dynamic Sky Light）之间的兼容性大幅提升。

**案例 3：Unity HDRP 的 LOD Billboard**  
Unity 的 SpeedTree 集成在 HDRP 管线中将 Billboard 材质默认配置为 Alpha-to-Coverage + 8×MSAA，并启用抖动透明（Dithered Transparency）来平滑 LOD 切换边界，避免远景树林出现突兀的"几何体消失"闪烁。

---

## 常见误区

**误区 1：Billboard 一定比 LOD2 网格省性能**  
Billboard 节省的是顶点处理和几何带宽，但 **Alpha Test 会破坏 Early-Z 优化**（GPU 在片元着色前无法通过深度测试提前剔除），导致过度绘制（Overdraw）成本上升。在密集树林俯视场景中，大量 Billboard 层叠时 Overdraw 可达 **8~12 层**，片元着色总开销可能反超低面数 3D 模型。正确做法是结合摄像机高度动态调整切换距离，或在 Hi-Z Occlusion Culling 之后再批量绘制 Billboard。

**误区 2：Billboard 朝向计算应在像素着色器中完成**  
部分初学实现将 Look-At 矩阵重建放在像素着色器中，实际上朝向变换只需作用于 **4 个顶点**，放在顶点着色器处理即可，像素着色器中重复运算会造成不必要的 ALU 浪费，在 Tile-based GPU（移动平台）上尤为明显。

**误区 3：Impostor 图集帧数越多越好**  
从 32 方向增加到 256 方向时，视角跳变瑕疵减少，但图集纹理尺寸从约 **512×512** 增至 **2048×2048**，纹理内存增加 **16 倍**，且 GPU 纹理缓存命中率下降。对于距离超过 500 米的极远景物体，8~16 方向通常已足够，仅在中距离（50~200 米）Impostor 才值得使用 32 方向以上。

**误区 4：Billboard 不能接收动态阴影**  
标准 Billboard 的几何深度是平面，投射/接收阴影确实存在误差，但通过在烘焙时同时存储**法线偏移（Normal Bias）**贴图，并在 Shadow Pass 中对 Billboard 使用专用的 alpha clip 材质，可以使其正确投射阴影到地面。UE5 的 Nanite 虚拟几何体系统在 Billboard 层级不适用，因此 Shadow Pass 仍需单独维护 Billboard 的阴影绘制批次。

---

## 知识关联

**与 LOD 切换策略的衔接**：Billboard 是 LOD 链条的终态，切换逻辑与前序 LOD 共用同一套基于屏幕尺寸的判据（$h_{px}$ 公式），但切换距离通常是 LOD2 到 LOD3 距离的 **2~4 倍**，以确保平面欺骗在感知上不可察觉。LOD