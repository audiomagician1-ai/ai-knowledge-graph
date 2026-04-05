---
id: "ta-batch-merge"
concept: "网格合并"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
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



# 网格合并

## 概述

网格合并（Mesh Merging）是技术美术性能优化领域的核心手段之一，通过将场景中多个独立几何体在顶点数据层面物理合并为单一网格对象，从根本上减少 CPU 向 GPU 提交的 Draw Call 数量。其理论依据来自现代图形 API 的工作模式：每次 Draw Call 都涉及状态切换（State Change）、命令缓冲区写入和驱动层验证，在 DirectX 11 / OpenGL 渲染管线下，CPU 每帧能高效处理的 Draw Call 上限约为 2000～3000 次（具体视 CPU 核心数与驱动开销而定）；超出此范围后帧率将因 CPU 瓶颈而显著下滑。

网格合并技术的系统化应用可追溯至 2005 年前后的主机游戏开发实践，并随引擎工具链的成熟而逐步自动化。Unity 在 3.x 时代即暴露 `Mesh.CombineMeshes()` API，允许运行时手动合并；Unreal Engine 于 4.14（2016 年 12 月发布）正式推出图形化 Merge Actors 工具窗口；Epic 进一步在 UE 4.20 中引入 HLOD（Hierarchical Level of Detail）构建管线的稳定版本，并在 UE5 的 World Partition 架构中将 HLOD 提升为大世界流送的基础设施组件。

一个直观案例：某 3A 开放世界关卡包含 15,000 个静态道具（碎石、植被底部、建筑装饰件），合并前 Draw Call 达 12,000～14,000 次（部分物体已被视锥体剔除），合并后降至 800～1,200 次，帧率从 28 FPS 提升至稳定 60 FPS。网格合并与 GPU Instancing、材质合批三者构成静态场景渲染优化的"铁三角"，适用场景和内存代价各有不同，需要结合具体指标选取。

---

## 核心原理

### 静态合批（Static Batching）

静态合批是引擎在构建期（Build Time）或场景加载期自动执行的网格合并策略，仅对标记为 **Static** 的游戏对象生效。在 Unity 中，引擎会将所有参与静态合批的物体顶点数据变换到世界空间后写入一个共享的**大顶点缓冲区（Combined Vertex Buffer）**，运行时 GPU 直接从该缓冲区按子网格的索引范围（Index Range）分批读取，CPU 提交的 Draw Call 数量等于场景中不同材质球的数量，而非物体数量。

**关键限制**：参与合批的所有物体必须引用**完全相同的材质实例（Material Instance）**——即同一个材质资产的同一个引用，而非"参数相同的两个独立实例"。Unity 静态合批不共享顶点数据副本，100 个引用同一 Mesh 的石块合批后，内存中存在 100 份顶点数据的世界空间副本，内存开销与物体数量线性正相关。若原始单个石块顶点数为 500，则合批后 Vertex Buffer 占用为 500 × 100 × 顶点步长（Stride，通常 32～48 字节）约 1.5～2.4 MB，这与 GPU Instancing 仅存储 1 份几何数据的策略形成鲜明对比。

Unity 静态合批的运行时内存上限可通过 `PlayerSettings` 中 `Vertex Compression` 选项压缩位置/法线精度来缓解，但代价是精度损失。

### HLOD（层级细节合并）

HLOD 是专为大型开放世界设计的**空间分层网格合并**方案，其思路是：将地理空间上相邻的一组静态网格体，在编辑器离线构建阶段合并并简化为一个低精度**代理网格（Proxy Mesh）**，当摄像机到该网格簇的距离超过预设阈值时，引擎用代理网格整体替换原始高精度网格组，同时削减 Draw Call 与几何复杂度两个维度。

UE5 中 HLOD 典型分层配置如下：

| 层级 | 触发距离 | 目标面数比例 | Draw Call 变化 |
|------|----------|------------|----------------|
| HLOD0（原始） | 0～5000 cm | 100% | 原始数量 |
| HLOD1 | 5000～20000 cm | 10%～30% | 合并为 1 个 |
| HLOD2 | >20000 cm | 1%～5% | 合并为 1 个 |

HLOD 代理网格的生成使用**屏幕覆盖率（Screen Coverage）**作为简化强度依据，而非固定面数。Epic 官方文档建议将 HLOD1 的屏幕覆盖率目标设为原始组合在触发距离处投影面积的 50%，以保证视觉过渡不产生可感知的突变。UE5 的 Nanite 虚拟几何体系统虽能对 Nanite 网格自动处理 LOD，但透明材质、植被（双面薄片）和骨骼网格体无法启用 Nanite，这些类别的物体在大世界场景中依然强烈依赖 HLOD 管线。

### GPU Instancing 与网格合并的边界

GPU Instancing 和网格合并都能减少 Draw Call，但机制不同：Instancing 在 GPU 端用单次 Draw Call 绘制同一 Mesh 的 N 个实例，每个实例通过实例数据缓冲区（Instance Data Buffer）传递独立的变换矩阵和自定义参数，几何数据仅存储一份；网格合并则是在 CPU/离线阶段将几何数据物理拼接，生成一个包含所有顶点的新 Mesh，适用于**不规则几何体混合**的场景（如一堵由砖块、灰泥、铁扣组成的墙面，每块砖形状略有不同，无法用 Instancing 处理）。两者的选择原则：**高重复率、形状相同 → GPU Instancing；低重复率、形状各异 → 网格合并**。

---

## 关键公式与性能模型

网格合并对 CPU 渲染线程帧时间的收益可用以下简化模型估算：

$$T_{\text{saved}} = (N_{\text{before}} - N_{\text{after}}) \times C_{\text{dc}}$$

其中：
- $N_{\text{before}}$：合并前 Draw Call 数量
- $N_{\text{after}}$：合并后 Draw Call 数量（等于合并后使用的独立材质数量）
- $C_{\text{dc}}$：单次 Draw Call 的 CPU 平均开销，在 DX11/PC 平台约为 **0.01～0.05 ms**，在移动端（OpenGL ES 3.x）约为 **0.05～0.2 ms**

例如：移动端场景由 500 次 Draw Call 优化至 50 次，$C_{\text{dc}}$ 取 0.1 ms，则每帧节约 CPU 时间 $= 450 \times 0.1 = 45$ ms，对 30 FPS（帧预算 33.3 ms）的场景而言，此优化具有决定性意义。

Unity 运行时合并的代码接口如下：

```csharp
// Unity 运行时网格合并示例（CombineMeshes API）
MeshFilter[] meshFilters = GetComponentsInChildren<MeshFilter>();
CombineInstance[] combine = new CombineInstance[meshFilters.Length];

for (int i = 0; i < meshFilters.Length; i++)
{
    combine[i].mesh = meshFilters[i].sharedMesh;
    // 将子物体变换转换到父物体本地空间
    combine[i].transform = meshFilters[i].transform.localToWorldMatrix;
    meshFilters[i].gameObject.SetActive(false); // 隐藏原始子物体
}

Mesh mergedMesh = new Mesh();
// 顶点总数超过 65535 时必须使用 IndexFormat.UInt32
mergedMesh.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;
mergedMesh.CombineMeshes(combine, mergeSubMeshes: true, useMatrices: true);

GetComponent<MeshFilter>().sharedMesh = mergedMesh;
GetComponent<MeshRenderer>().enabled = true;
```

`mergeSubMeshes: true` 表示将所有子网格合并为单一 SubMesh（要求所有子物体使用同一材质），设为 `false` 则保留各自 SubMesh 用于多材质物体——但后者并不减少 Draw Call 数量，仅减少游戏对象管理开销。

---

## 实际应用：三种工具流程对比

### Unity：静态合批 + CombineMeshes

**离线静态合批**：在 Inspector 勾选 Static → Batching Static，Build 后自动生效，零代码成本，但无法在运行时动态修改物体位置。适用于永远不移动的场景装饰物（建筑、地面岩石）。

**运行时 CombineMeshes**：适用于程序化生成关卡（Procedural Level Generation），在生成完毕后调用一次合并，代价是合并本身的 CPU 耗时（10,000 个顶点的合并约 2～5 ms，需放在 Loading 阶段执行而非每帧执行）。

Unity 6 中引入的 **GPU Resident Drawer** 可自动对场景中所有使用相同着色器的物体执行 Indirect Rendering，进一步降低驾驭 DrawCall 的门槛，但该功能仅在支持 Compute Shader 的平台（DX12/Vulkan/Metal）上生效。

### Unreal Engine：Merge Actors 工具

UE 的 Merge Actors 工具（Window → Developer Tools → Merge Actors）提供三种合并模式：

- **Merge（完整合并）**：将所选 Actor 的几何体物理合并为一个新 Static Mesh 资产，同时可选择将所有材质的贴图烘焙合并为一张 Atlas 贴图（Material Baking），最终实现"1 个 Mesh + 1 个材质 = 1 次 Draw Call"。贴图 Atlas 分辨率通常设为 2048×2048 或 4096×4096，需根据物体屏幕占比确定，以避免 Texel 密度过低。
- **Batch（批处理合并）**：按材质分组合并，保留不同材质，适用于材质种类少于 4 种的建筑外立面。
- **Approximate（近似合并）**：用于生成 HLOD 代理网格，对原始几何体进行激进简化，面数可控制在原始 1%～20%。

### 贴图 Atlas 烘焙的 UV 重新布局

合并网格时若涉及材质合并，必须对每个子网格执行 **UV 重新布局（UV Repacking）**：将各子网格的 UV 坐标从 [0,1] 范围重新映射到 Atlas 贴图中分配的子区域。例如，16 个物体合并后 Atlas 被均分为 4×4 格，每格占 Atlas 的 1/16 面积，原始 UV 坐标 $(u, v)$ 被变换为 $\left(\dfrac{u + c_x}{4},\ \dfrac{v + c_y}{4}\right)$，其中 $(c_x, c_y)$ 为该物体在 4×4 格中的列行索引。

---

## 常见误区

**误区 1：合并后面数等于子物体面数之和，必然更慢**
合并增加了单个 Mesh 的顶点数，但 GPU 的瓶颈通常是顶点着色器吞吐量和带宽，而非面数的绝对值。在 CPU 绑定（CPU-Bound）的场景中，用 100 次 Draw Call 绘制 10,000 个三角形，远比用 1 次 Draw Call 绘制同等三角形慢；GPU 处理 10,000 个三角形在现代硬件上仅需不到 0.1 ms，但 100 次 Draw Call 的 CPU 开销在移动端可达 10 ms 以上。

**误区 2：网格合并后物体无法单独剔除（Culling）**
合并为单一 Mesh 后，引擎的视锥体剔除（Frustum Culling）和遮挡剔除（Occlusion Culling）以整个合并 Mesh 的 AABB 包围盒为单位执行，确实无法对子区域单独剔除。因此网格合并的**地理范围不宜过大**——通常建议单次合并覆盖范围不超过场景 Tile 的 1/4 面积，或控制合并后 Mesh 的 AABB 对角线长度不超过 50 米（依项目视距而定），以避免摄像机接近时合并 Mesh 整体始终在视锥内，丧失剔除收益。

**