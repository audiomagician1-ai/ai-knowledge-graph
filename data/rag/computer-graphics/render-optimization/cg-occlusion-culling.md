---
id: "cg-occlusion-culling"
concept: "遮挡剔除"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 遮挡剔除

## 概述

遮挡剔除（Occlusion Culling）是渲染优化管线中继视锥剔除之后的第二道可见性过滤屏障，其目标是在GPU提交光栅化指令之前，识别并丢弃视锥体内被不透明几何体完全遮挡的物体，避免对不可见物体执行顶点着色、三角形组装、光栅化和片元着色等全部管线阶段。

GPU渲染管线本身无法自动跳过被遮挡物体——即便一栋20层的高楼完全阻挡了其后方的整条街道，图形驱动层仍会按提交顺序逐一处理所有Draw Call，每个Draw Call带来顶点变换和着色器调度的固定开销。对于包含10,000+静态物体的城市场景，仅凭视锥剔除通常只能剔除约30%~50%的物体，而叠加遮挡剔除后可将Draw Call总量再压缩60%~90%（Akenine-Möller et al., 《Real-Time Rendering》第4版, CRC Press, 2018）。

遮挡剔除技术的系统性研究始于1990年代中期。1993年，Greene等人提出了基于层次深度缓冲（Hierarchical Z-Buffer）的可见性测试框架，奠定了现代HZB算法的理论基础。此后，Bittner等人于2004年在SIGGRAPH上发表的"Coherent Hierarchical Culling"论文将层次遮挡查询引入实时渲染主流。当前Unreal Engine 5的Nanite虚拟几何体系统和Unity HDRP的GPU Occlusion均以HZB为核心，配合软件光栅化完成CPU侧的早期剔除。

---

## 核心原理

### 层次深度缓冲（Hierarchical Z-Buffer，HZB）

HZB算法的输入是上一帧渲染结束时GPU输出的深度缓冲（Depth Buffer），对其执行逐级降采样，构建一条完整的Mip链。与颜色纹理的Mip不同，HZB每个Mip层级存储其对应4个子像素中的**最大深度值**（即离相机最远的深度，在反转深度约定下为最小浮点值）。对于1920×1080分辨率的视口，完整Mip链共有 $\lceil \log_2(1920) \rceil = 11$ 层，最顶层退化为1×1像素，代表全屏范围内最大的深度极值。

对候选物体执行遮挡测试的步骤如下：

1. 将物体的轴对齐包围盒（AABB）的8个顶点投影到裁剪空间，取投影后屏幕矩形的像素范围 $[x_{\min}, x_{\max}] \times [y_{\min}, y_{\max}]$；
2. 计算覆盖该范围所需的HZB层级：$\text{MipLevel} = \lceil \log_2(\max(x_{\max}-x_{\min},\ y_{\max}-y_{\min})) \rceil$，确保在该层级下包围盒覆盖区域不超过2×2个像素；
3. 从HZB对应层级读取2×2区域内的最大深度 $z_{\text{HZB}}$；
4. 计算包围盒8个顶点中距相机最近的深度 $z_{\text{near}}$；
5. 若 $z_{\text{near}} > z_{\text{HZB}}$（包围盒最近点仍比遮挡物更远），则判定完全遮挡，跳过该物体的Draw Call。

HZB的核心公式可表达为：

$$\text{Occluded} = \begin{cases} \text{true} & \text{if } z_{\text{near}}^{\text{AABB}} > z_{\text{HZB}}^{\text{mip}(k)} \\ \text{false} & \text{otherwise} \end{cases}$$

其中 $k = \lceil \log_2(\max(\Delta x_{\text{screen}},\ \Delta y_{\text{screen}})) \rceil$。

**Ghost Occluder问题**：由于HZB使用上一帧的深度图，当相机快速移动或遮挡物高速位移时，前一帧的遮挡物可能已离开视野，但当前帧仍用其深度数据错误地剔除其后方物体，导致被剔除物体出现一帧"闪烁"。Unreal Engine 5的应对策略是：对被HZB判定为遮挡的物体，将其包围盒在投影空间扩大约2像素的安全边距，同时在Temporal AA阶段对突然出现的新几何体执行reprojection验证，将误剔除率控制在可接受范围内。

### Software Rasterization遮挡剔除（MSOC）

软件光栅化遮挡剔除完全在CPU上运行，无需GPU-CPU回读同步。其流程是：从场景中选取面积较大、剔除收益高的**遮挡体（Occluder）**（通常是建筑外墙、地面、大型地形块），用CPU上的软光栅器将其绘制成一张低分辨率深度图（典型分辨率为512×256或256×128），再用此深度图对其他物体（**Occludee**）做可见性测试，整个过程不产生任何GPU命令。

Intel于2014年开源的**Masked Software Occlusion Culling（MSOC）**库（GitHub: GameTechDev/MashedOcclusionCulling）是该技术的标志性实现。MSOC的核心创新在于将屏幕划分为8×4像素的**Tile**，每个Tile用一个64位掩码（bitmask）表示像素覆盖状态，同时用AVX2 SIMD指令一次处理8个三角形的光栅化运算。在256×128分辨率下，MSOC对包含约200个遮挡体三角形的场景，完整生成一张遮挡深度图的CPU耗时通常低于0.5ms（测试平台：Intel Core i7-6700K）。

与HZB相比，MSOC的遮挡精度略低（受限于低分辨率），但优势在于：
- 零GPU-CPU延迟，适合CPU驱动的多线程剔除管线；
- 遮挡体可由美术手动指定为简化代理网格（Proxy Mesh），而非原始高模；
- 可与任意渲染后端（Vulkan、DX12、Metal）配合使用，不依赖特定图形API。

### GPU遮挡查询（Occlusion Query）

在HZB普及之前，OpenGL和D3D9时代的主流方案是GPU遮挡查询：先提交遮挡体的Draw Call，然后通过`GL_SAMPLES_PASSED`或`D3DISSUE_BEGIN`/`D3DISSUE_END`查询对应物体有多少片元通过深度测试。若通过片元数为0，则下一帧跳过该物体。

此方案的致命缺陷是**CPU-GPU同步气泡**：CPU必须等待GPU完成当前帧的深度查询并将结果回传（`glGetQueryObjectuiv`会阻塞CPU线程），导致CPU-GPU流水线断流。实测在包含500个遮挡查询的场景中，同步回读引入的帧延迟可达3~8ms。现代引擎已基本放弃同步GPU查询，转而采用HZB（异步、无回读）或MSOC（纯CPU）。

---

## 关键公式与算法

### HZB Mip层级选取

$$k = \left\lceil \log_2\left(\max\left(\Delta x_{\text{screen}},\ \Delta y_{\text{screen}}\right)\right) \right\rceil$$

其中 $\Delta x_{\text{screen}} = x_{\max} - x_{\min}$，$\Delta y_{\text{screen}} = y_{\max} - y_{\min}$ 为物体包围盒投影后的屏幕像素尺寸。选取该层级可保证HZB采样区域恰好覆盖包围盒投影范围，避免跨层级采样引入的误判。

### MSOC伪代码流程

```cpp
// MSOC 遮挡测试核心流程（简化版）
struct MaskedOcclusionCulling {
    float depthBuffer[256][128];      // 低分辨率软件深度图
    uint64_t coverageMask[256/8][128/4]; // 每Tile 8x4像素覆盖掩码

    // 阶段1：绘制Occluder，更新软件深度图
    void RasterizeOccluder(const Mesh& occluder) {
        for (Triangle& tri : occluder.triangles) {
            // AVX2: 8条SIMD lane同时处理8个三角形
            __m256 depth = ProjectAndRasterize_AVX2(tri);
            UpdateDepthTile(depth, coverageMask);  // 更新Tile掩码
        }
    }

    // 阶段2：测试Occludee包围盒
    bool IsOccluded(const AABB& bounds) {
        auto [screenRect, zNear] = ProjectBounds(bounds);
        // 在软件深度图中采样包围盒覆盖区域的最大深度
        float zHZB = SampleDepthConservative(screenRect, depthBuffer);
        return zNear > zHZB;  // 包围盒最近点比深度图更远 => 完全遮挡
    }
};
```

---

## 实际应用

**案例1：城市场景（Unreal Engine 5）**
在Epic官方发布的"City Sample"演示（2022年）中，场景包含约80,000个可见物体。HZB遮挡剔除在每帧将需要提交GPU的Draw Call从~18,000条压缩至~3,200条，剔除率约82%。HZB的每帧计算开销约为0.3ms（RTX 3080），相比节省的GPU顶点处理时间（~4.2ms）具有显著的ROI。

**案例2：室内建筑可视化**
对于室内场景，墙壁是天然的高效遮挡体。将每面墙的代理矩形网格注册为MSOC遮挡体后，相机在走廊中移动时，背后房间内的所有物体（家具、灯具等共约2,000个物体）均可在CPU侧被MSOC深度图测试排除，GPU仅处理当前房间可见的约150~300个物体，Draw Call下降约85%。

**案例3：剔除体（Cull Volume）辅助**
Unreal Engine支持在关卡中放置`Cull Distance Volume`，与遮挡剔除联合使用：Cull Distance Volume负责按距离剔除小物体（如距离超过50米剔除路灯），HZB负责剔除距离内但被建筑遮挡的物体，两者协同可将CPU剔除阶段的总负载从~2ms降至~0.4ms。

---

## 常见误区

**误区1：遮挡剔除可以替代LOD**
遮挡剔除只剔除完全不可见的物体，对于视锥体内仅被部分遮挡的物体无能为力。距离相机500米但仍有一个角点可见的高楼，HZB不会将其剔除，此时LOD系统将该物体切换为面数极低的代理才是正确的优化路径。两者的作用域互补，而非替代关系。

**误区2：动态物体无法受益于HZB**
HZB深度图基于上一帧静态和动态物体的混合深度，动态物体同样可以成为Occluder（只要其上一帧深度已写入深度缓冲）。但高速运动的物体作为Occluder时Ghost Occluder风险更高，需要适当扩展包围盒安全边距（Unreal默认扩展8个屏幕像素）。

**误区3：软件光栅化遮挡图分辨率越高越好**
MSOC深度图分辨率从256×128提升至1024×512时，CPU生成耗时从0.5ms上升至约3.5ms，而遮挡精度提升带来的额外剔除收益通常不足5%（因为遮挡判断的瓶颈在于遮挡体的几何完整性，而非深度图分辨率）。Intel官方推荐在大多数场景下使用320×180作为MSOC深度图的上限分辨率以平衡精度与开销。

**误区4：HZB查询结果当帧生效**
HZB必然存在一帧延迟，其结果在下一帧生效。将HZB剔除结果在当前帧立即应用会引入更多Ghost Occluder问题。正确做法是：当前帧用上一帧HZB判定哪些物体不可见，并在当前帧渲染结束后更新HZB供下一帧使用。

---

## 知识关联

**前置概念——视锥剔除**：遮挡剔除的输入是视锥剔除之后仍在视锥体内的物体列表。若视锥剔除已将物体数从100,000减至