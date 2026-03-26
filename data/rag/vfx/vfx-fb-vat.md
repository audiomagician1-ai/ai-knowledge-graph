---
id: "vfx-fb-vat"
concept: "VAT顶点动画"
domain: "vfx"
subdomain: "flipbook"
subdomain_name: "序列帧特效"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# VAT顶点动画

## 概述

VAT（Vertex Animation Texture，顶点动画纹理）是一种将3D网格的逐帧顶点位移数据烘焙到2D纹理中，在GPU端以极低的运行时成本重放复杂刚体或软体动画的技术。与传统骨骼蒙皮动画不同，VAT完全绕过CPU端的骨骼矩阵计算，通过在顶点着色器中采样纹理像素来还原每个顶点在特定帧的世界空间位移量，从而实现大规模实例化渲染。

VAT技术的工业化应用兴起于2015年前后的游戏与影视实时渲染领域，Houdini的SideFX Labs工具集（原Game Dev Toolset）在2017年正式发布VAT烘焙插件，使该技术进入主流特效管线。其核心价值在于将拓扑结构固定的复杂动态效果——如大规模布料模拟、破碎碎片、群体流体翻腾——转化为静态资产，在运行时以极少的DrawCall开销驱动数万个动态网格实例。

在序列帧特效体系中，VAT是对传统2D图集序列帧的三维延伸：普通序列帧仅记录颜色外观的逐帧变化，而VAT同时记录几何形状本身的逐顶点空间变化，使特效拥有准确的体积感和视差正确性，不会像Billboard序列帧那样在侧视角出现透视穿帮。

## 核心原理

### 纹理数据编码格式

VAT至少需要两张纹理：**位置纹理（Position Map）**和**法线纹理（Normal Map）**。位置纹理通常使用RGB16F或RGB32F格式，其中每个像素的RGB三个通道分别存储顶点在X、Y、Z轴上相对于绑定姿势的位移量，单位通常经过归一化压缩。具体编码公式为：

```
UV_x = vertex_index / total_vertices
UV_y = frame_index / total_frames
```

即纹理横轴对应顶点序号，纵轴对应帧序号，每个像素精确记录第N帧第M号顶点的三维位移向量。一张512×256的Position Map可存储最多512个顶点、256帧的完整动画数据。

### 顶点着色器中的重建逻辑

在顶点着色器中，重建公式如下：

```
float2 uv = float2(vertexID / totalVertices, currentTime / totalDuration);
float3 displacement = tex2Dlod(PositionMap, float4(uv, 0, 0)).rgb;
float3 finalPos = bindPosePos + displacement * positionRange + positionMin;
```

其中`positionRange`和`positionMin`作为材质参数传入，用于将0~1的归一化像素值反映射回实际的世界空间坐标范围。这意味着VAT资产的包围盒必须在烘焙时确定，运动幅度超出包围盒会导致顶点坐标溢出错误。

### 三种VAT子类型

SideFX Labs定义了三种标准VAT类型，面向不同特效场景：

- **Soft Body（软体类型1）**：每个顶点存储绝对位置与法线，适用于布料、旗帜、肌肉形变，纹理精度要求最高。
- **Rigid Body（刚体类型2）**：以每个破碎块（Piece）为单位存储旋转四元数和平移向量，碎片内部顶点通过同一旋转矩阵变换，大幅节省纹理空间，适用于建筑爆破、陶罐碎裂等特效。
- **Fluid（流体类型3）**：存储粒子/顶点的速度场信息，配合Sprite渲染或体积重建使用，适用于翻腾的水花或气流扰动。

## 实际应用

在虚幻引擎（Unreal Engine 5）中集成VAT特效时，需将Position Map的Compression Settings设置为**HDR（16位浮点）**，并关闭sRGB选项，否则引擎的伽马校正会破坏位移数值的线性精度。材质中使用`VertexInterpolator`节点传递当前帧的UV偏移量，通过`Time`节点驱动纵轴UV的滚动实现动画播放。

在移动端特效（如《原神》风格的大规模场景破坏）中，VAT刚体类型被广泛用于替代实时物理模拟。一个包含200个破碎块、60帧动画的建筑倒塌特效，其Position Map仅需200×60像素（约47KB，使用RGB16F格式），而等效的物理模拟在移动端CPU上需要消耗约8ms的帧时间，VAT方案将其降至不足0.2ms的GPU采样开销。

在Houdini制作流程中，将RBD（Rigid Body Dynamics）模拟输出传入Labs VAT ROP节点，设置导出路径后，工具会自动计算每帧的顶点位移并写入EXR格式的Position Map，同时输出包含`positionMin`、`positionMax`参数的JSON配置文件，供引擎端材质参数绑定使用。

## 常见误区

**误区一：认为VAT可以处理拓扑变化的网格。** VAT严格要求动画序列中每一帧的顶点数量和索引顺序完全一致，因为横轴UV是按顶点序号硬编码的。Houdini的布料模拟或流体Mesh若存在帧间网格重拓扑，必须先使用`Remesh`或`Connectivity`节点将顶点数量锁定为常数，否则导出的Position Map中顶点与像素列的对应关系会完全错乱。

**误区二：认为VAT不支持GPU Instancing。** 恰恰相反，VAT是实现GPU实例化动态网格的利器。通过向每个实例传入不同的`TimeOffset`参数，可以让数千个相同网格的实例在时间轴上错位播放，产生相位随机的自然群体动态效果。实现时需将`TimeOffset`存入实例化数据缓冲区（InstanceData），在顶点着色器中加到UV的纵轴偏移上：`uvY = frac(normalizedTime + instanceTimeOffset)`。

**误区三：误用8位纹理格式存储位置数据。** RGBA8格式仅提供256个离散精度级别，对于顶点位移量来说，若模型运动范围为2米，则位置精度误差约为2/256≈7.8mm，在近景特写镜头中会产生肉眼可见的"跳格"抖动。正确做法是始终使用RGB16F（精度约为0.001mm级别）或在平台限制下改用两张RGBA8纹理分别存储高低位（Pack/Unpack方案）。

## 知识关联

VAT技术建立在**序列帧优化**的基础之上：传统序列帧优化解决了2D图集的采样效率与内存打包问题，VAT将相同的"预烘焙→纹理存储→着色器采样"思路扩展到三维顶点空间，学习者需熟悉UV图集坐标计算和MipMap关闭策略才能正确配置VAT材质（Position Map必须关闭Mipmap，否则采样相邻帧数据时会发生跨帧混合错误）。

VAT的下一个演进方向是**实时捕获**：当VAT的静态预烘焙无法满足玩家交互触发的随机破坏需求时，需要在运行时动态录制物理模拟数据并写入纹理缓冲区，这涉及Render Target的实时写入与格式兼容性问题，是VAT从离线资产向运行时动态资产跨越的关键技术节点。