---
id: "cg-rtx-hardware"
concept: "RTX硬件加速"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 3
is_milestone: false
tags: ["硬件"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# RTX硬件加速

## 概述

RTX硬件加速是NVIDIA于2018年9月随Turing微架构（GeForce RTX 20系列）正式推出的专用光线追踪硬件技术。其核心创新在于将**RT Core**（Ray Tracing Core）作为独立固定功能单元集成于GPU芯片，使光线-三角形求交运算与BVH节点遍历完全绕过传统CUDA着色器核心的ALU流水线，在专用硬件上并行执行。

在旗舰卡RTX 2080 Ti（TU102芯片）中，RT Core数量为68个，理论光线追踪吞吐量达到**10 Giga Rays/s（每秒100亿条光线求交）**，比同代GTX 1080 Ti使用CUDA软件模拟BVH遍历的速度快约**30倍**。2020年推出的Ampere架构（RTX 30系列）将RT Core升级至第二代，在RTX 3090上部署了**82个RT Core**，吞吐量提升至**80 Giga Rays/s**，并新增对**运动模糊（Motion Blur）的硬件加速支持**——即在BVH遍历阶段直接处理时间维度插值，无需在着色器中手工展开。2022年的Ada Lovelace架构（RTX 40系列）推出第三代RT Core，RTX 4090搭载**128个RT Core**，吞吐量进一步达到**191 Giga Rays/s**，并引入**Opacity Micromap**和**Displaced Micro-Mesh**两项新机制，分别加速透明度测试和微位移几何体的求交。

理解RTX硬件加速的意义在于它重新划分了GPU内部的并行任务：单帧画面渲染可以同时驱动RT Core执行BVH遍历、Tensor Core运行DLSS神经网络降噪、CUDA Core完成着色计算，三类专用单元真正意义上在芯片层面并行工作，而非时间片轮转共享同一组ALU。

---

## 核心原理

### RT Core的固定功能操作

RT Core只执行两类严格限定的操作，不可编程：

1. **Ray-AABB 求交测试**：判断光线是否与轴对齐包围盒（Axis-Aligned Bounding Box）相交，用于BVH内部节点的剔除。
2. **Ray-Triangle 求交测试**：采用硬件实现的Möller-Trumbore算法，计算光线与三角形的精确交点，输出重心坐标 $(u, v)$ 和交点参数 $t$。

Möller-Trumbore算法的核心公式如下。设光线为 $\mathbf{R}(t) = \mathbf{O} + t\mathbf{D}$，三角形三顶点为 $\mathbf{V}_0, \mathbf{V}_1, \mathbf{V}_2$，令：

$$\mathbf{E}_1 = \mathbf{V}_1 - \mathbf{V}_0, \quad \mathbf{E}_2 = \mathbf{V}_2 - \mathbf{V}_0, \quad \mathbf{T} = \mathbf{O} - \mathbf{V}_0$$

则交点参数由Cramer法则求解线性方程组得到：

$$\begin{pmatrix} t \\ u \\ v \end{pmatrix} = \frac{1}{(\mathbf{D} \times \mathbf{E}_2) \cdot \mathbf{E}_1} \begin{pmatrix} (\mathbf{T} \times \mathbf{E}_1) \cdot \mathbf{E}_2 \\ (\mathbf{D} \times \mathbf{E}_2) \cdot \mathbf{T} \\ (\mathbf{T} \times \mathbf{E}_1) \cdot \mathbf{D} \end{pmatrix}$$

当 $u \geq 0,\ v \geq 0,\ u+v \leq 1$ 且 $t$ 在有效范围 $[t_{\min}, t_{\max}]$ 内时，命中成立。整个求解过程在RT Core的专用电路中以一条光线为单位的粒度流水线执行，不消耗任何CUDA着色器周期（参见 Akenine-Möller et al.,《Real-Time Rendering》第4版，2018，第26章）。

### 两级加速结构（TLAS / BLAS）

RT Core遍历的并非单层BVH，而是DXR与Vulkan Ray Tracing规范强制要求的**两级加速结构（Two-Level AS）**：

- **BLAS（Bottom-Level Acceleration Structure）**：存储单个网格的三角形几何体或AABB自定义图元，由应用层在资产加载时构建，可在多个实例间复用。
- **TLAS（Top-Level Acceleration Structure）**：存储场景中所有几何体实例（Instance），每个实例携带一个4×3的仿射变换矩阵，指向对应的BLAS。RT Core从TLAS根节点开始遍历，通过实例变换将光线从世界空间变换到BLAS的对象空间，再继续遍历BLAS内部节点。

这一设计使动态场景能够以极低代价更新：移动一个物体只需更新TLAS中对应实例的变换矩阵并重构TLAS（通常在GPU上耗时不足1 ms），BLAS几何体本身无需重建。BLAS重建（Full Rebuild）代价远高于TLAS，仅在网格拓扑发生改变（如骨骼蒙皮导致顶点大幅位移）时才需触发；轻微形变可使用`ALLOW_UPDATE`标志进行**BLAS Refit**（就地更新包围盒而不改变树结构），代价约为完整重建的1/5。

### DXR / Vulkan RT 着色器阶段划分

DXR（DirectX Raytracing，随DirectX 12 Ultimate发布）与Vulkan Ray Tracing（`VK_KHR_ray_tracing_pipeline`，2020年正式成为Khronos核心扩展）将光线追踪管线拆分为五类专用着色器，每类均有严格的触发条件与硬件调用来源：

| 着色器类型 | 触发方 | 典型用途 |
|---|---|---|
| Ray Generation Shader | CPU DispatchRays / vkCmdTraceRaysKHR | 每像素发射主光线 |
| Intersection Shader | RT Core（自定义图元时）| 球体、SDF等非三角形求交 |
| Any Hit Shader | RT Core（每次候选命中）| 透明度/Alpha Test 裁剪 |
| Closest Hit Shader | RT Core（遍历完成后最近命中）| 光照、反射递归计算 |
| Miss Shader | RT Core（未命中任何几何体）| 采样天空盒、环境光 |

**Any Hit Shader的性能陷阱**：RT Core在遍历过程中每找到一个候选三角形都会中断并等待Any Hit Shader执行完毕，之后才继续遍历。若Any Hit Shader包含纹理采样等高延迟操作，等待时间将完全序列化到遍历流水线中，彻底抵消RT Core的并行优势。实践中应将Any Hit Shader控制在**不超过5条ALU指令**，或使用RTX 40系列的**Opacity Micromap**将透明度信息预烘焙至加速结构，从而在RT Core层面直接跳过对应三角形，无需调用Any Hit Shader。

---

## 关键API用法与代码示例

以下为DXR中构建BLAS的核心代码骨架（HLSL + C++ D3D12），展示从几何体描述到加速结构构建的完整流程：

```cpp
// 1. 描述底层几何体（三角形网格）
D3D12_RAYTRACING_GEOMETRY_DESC geomDesc = {};
geomDesc.Type = D3D12_RAYTRACING_GEOMETRY_TYPE_TRIANGLES;
geomDesc.Triangles.VertexBuffer.StartAddress  = vertexBufferGPUAddress;
geomDesc.Triangles.VertexBuffer.StrideInBytes = sizeof(Vertex);
geomDesc.Triangles.VertexFormat  = DXGI_FORMAT_R32G32B32_FLOAT;
geomDesc.Triangles.VertexCount   = vertexCount;
geomDesc.Triangles.IndexBuffer   = indexBufferGPUAddress;
geomDesc.Triangles.IndexFormat   = DXGI_FORMAT_R32_UINT;
geomDesc.Triangles.IndexCount    = indexCount;
geomDesc.Flags = D3D12_RAYTRACING_GEOMETRY_FLAG_OPAQUE; // 跳过 Any Hit

// 2. 查询BLAS所需显存大小
D3D12_BUILD_RAYTRACING_ACCELERATION_STRUCTURE_INPUTS blasInputs = {};
blasInputs.Type           = D3D12_RAYTRACING_ACCELERATION_STRUCTURE_TYPE_BOTTOM_LEVEL;
blasInputs.DescsLayout    = D3D12_ELEMENTS_LAYOUT_ARRAY;
blasInputs.pGeometryDescs = &geomDesc;
blasInputs.NumDescs       = 1;
blasInputs.Flags          = D3D12_RAYTRACING_ACCELERATION_STRUCTURE_BUILD_FLAG_PREFER_FAST_TRACE;

D3D12_RAYTRACING_ACCELERATION_STRUCTURE_PREBUILD_INFO blasInfo = {};
device->GetRaytracingAccelerationStructurePrebuildInfo(&blasInputs, &blasInfo);

// 3. 分配显存并提交构建命令（在GPU上异步执行）
// blasInfo.ResultDataMaxSizeInBytes  → BLAS存储缓冲区大小
// blasInfo.ScratchDataSizeInBytes    → 临时暂存缓冲区大小
cmdList->BuildRaytracingAccelerationStructure(&blasDesc, 0, nullptr);
cmdList->ResourceBarrier(1, &CD3DX12_RESOURCE_BARRIER::UAV(blasBuffer.Get()));
```

在HLSL的Ray Generation Shader中，发射光线的调用为：

```hlsl
RayDesc ray;
ray.Origin    = cameraPos;
ray.Direction = normalize(pixelWorldPos - cameraPos);
ray.TMin      = 0.001f;  // 避免自相交
ray.TMax      = 10000.0f;

RayPayload payload = { float3(0,0,0), 0 };
TraceRay(
    gSceneTLAS,                          // TLAS资源
    RAY_FLAG_CULL_BACK_FACING_TRIANGLES, // 光线标志
    0xFF,                                // 实例掩码
    0,                                   // Hit Group偏移
    1,                                   // Hit Group步长
    0,                                   // Miss Shader索引
    ray,
    payload
);
```

---

## 实际应用

### 游戏中的混合渲染策略

完全路径追踪（Full Path Tracing）在当前硬件上对于1080p分辨率仍仅能达到每像素1~4条光线，噪声极重，因此商业游戏普遍采用**混合渲染（Hybrid Rendering）**：用光栅化生成G-Buffer（法线、深度、Albedo），再用RTX发射**少量高质量光线**专门计算以下效果：

- **光线追踪阴影（RT Shadows）**：每像素发射1条阴影光线，精确消除漏光和Peter Pan阴影，例如《赛博朋克2077》（2020）。
- **光线追踪反射（RT Reflections）**：对镜面高光像素发射反射光线，替代屏幕空间反射（SSR）在边缘处的失效区域，例如《战地5》（2018，首款使用DXR的商业游戏）。
- **光线追踪环境光遮蔽（RTAO）**：每像素发射2~4条短距离AO光线，替代SSAO的半径限制问题。

以上所有效果最终经过**DLSS（Deep Learning Super Sampling）**的Tensor Core降噪与超分辨率处理，将噪声帧从半分辨率提升到目标分辨率，从而在性能与画质间取得平衡。

### 离线渲染与产品可视化

NVIDIA OptiX 7（2019年发布）是面向科研与影视的光线追踪框架，同样构建于RT Core之上，被DreamWorks、OTOY等影视公司用于制作级路径追踪渲染。相比纯CUDA软件实现，OptiX 7在Ampere架构上的加速比约为**3~5倍**（取决于场景三角形密度与光线发散程度）。

---

## 常见误区

**误区1：RT Core数量越多帧率越高**
RT Core吞吐量是光线追踪性能的必要条件但非充分条件。瓶颈往往出现在命中后的Closest Hit Shader着色阶段（由CUDA Core执行），一条反射光线触发的PBR材质着色可能消耗数百条ALU指令。例如在复杂场景中，将每像素反射光线数从1增加至4，帧时间增加往往超过4倍，因为CUDA Core着色吞吐成为瓶颈，而非RT Core求交。

**误区2：每次渲染帧都需要重建TLAS和BLAS**
正确做法是：静态几何体的BLAS在场景加载时构建一次后不再触碰；