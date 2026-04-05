---
id: "vfx-niagara-neighbor-grid"
concept: "邻域网格"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 4
is_milestone: false
tags: ["高级"]

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
updated_at: 2026-04-06
---



# 邻域网格（Neighbor Grid 3D）

## 概述

邻域网格（Neighbor Grid 3D）是Unreal Engine Niagara系统中专用于粒子间空间查询的数据结构模块，通过将三维空间划分为均匀格栅，使每个粒子能够在接近O(k)时间复杂度内（k为平均每格元粒子数）找到其周围指定半径范围内的所有相邻粒子。该模块于UE4.25版本正式稳定化（2020年5月发布），在此之前粒子间的距离检测依赖全体粒子的O(N²)暴力遍历——10,000个粒子每帧产生约5,000万次距离计算，帧率在粒子数超过5,000时通常跌至5fps以下。

邻域网格的设计思想直接来源于计算流体动力学（CFD）领域的空间哈希（Spatial Hashing）技术，该技术由Teschner等人在2003年VMVS会议论文《Optimized Spatial Hashing for Collision Detection of Deformable Objects》中系统化描述，随后被广泛引入实时粒子模拟领域（Teschner et al., 2003）。与纯哈希方案不同，Niagara的邻域网格采用固定尺寸的均匀格栅而非动态哈希桶，牺牲了对稀疏场景的内存效率，换取了GPU上无分支、无原子冲突的并行写入性能。

将同等规模（10,000粒子）的查询代价压缩到每粒子平均约27次格元检索（在3×3×3邻域格元范围内），性能差异达到三到四个数量级。这一特性使Boid群集行为、SPH光滑粒子流体力学近似、粒子间排斥/吸引力场等交互效果从理论变为实时可行。

---

## 核心原理

### 空间分割与格元索引映射

邻域网格将用户定义的世界空间包围盒等分为 $N_x \times N_y \times N_z$ 个格元。每轴格元边长（Cell Size）由总包围盒尺寸除以该轴格元数量得出：

$$
\text{CellSize}_\alpha = \frac{2 \times \text{BoundsExtent}_\alpha}{N_\alpha}, \quad \alpha \in \{x, y, z\}
$$

粒子世界坐标 $\mathbf{P}$ 映射到整数格元坐标的公式为：

$$
\text{CellCoord}_\alpha = \left\lfloor \frac{P_\alpha - \text{BoundsMin}_\alpha}{\text{CellSize}_\alpha} \right\rfloor
$$

当粒子位置超出预设包围盒时，该粒子被邻域网格忽略，不参与任何写入或读取，因此正确设置 **Bounds Extent** 是使用该模块的第一个关键决策。格元数量通常每轴选取8到64之间的2的幂次值（8、16、32、64），便于GPU端的位运算优化。格元边长的经验准则是设为查询半径的1.5倍到2倍：过小（<1倍）会导致单次查询必须遍历5×5×5=125个格元；过大（>3倍）则使单格元粒子数膨胀，链表溢出风险显著上升。

### 写入阶段与读取阶段的Simulation Stage分离

邻域网格**必须配合Simulation Stage使用**，这是该模块与普通粒子Update脚本最根本的区别。整个工作流强制分为两个独立Stage，二者不可合并：

**Stage 1 — Population Stage（填充阶段）**：所有粒子并行执行 `Neighbor Grid 3D → Set Particle Neighbors` 节点，将自身粒子索引写入对应格元的链表槽。此Stage的执行顺序在粒子间是不确定的，但由于每个粒子只写入自身所在格元，不存在读写依赖。

**Stage 2 — Query Stage（查询阶段）**：粒子执行 `Neighbor Grid 3D → Get Particles In Neighborhood` 迭代器，遍历以自身为中心的3×3×3共27个格元，逐一检索邻居粒子索引，再通过 `Direct Read` 节点读取邻居的任意粒子属性（位置、速度、自定义Float属性等），并据此更新自身速度或颜色。

若将写入与读取混入同一Stage，格元数据在同一帧内处于半填充状态，粒子A可能读到粒子B尚未写入的旧位置，产生依赖执行顺序的竞态错误（Race Condition），表现为粒子交互在不同帧间随机抖动或完全失效。

### 最大邻居数与GPU显存预算

每个格元内部使用**固定容量的环形链表**存储粒子索引，链表容量由参数 `Max Neighbors Per Cell` 控制，默认值仅为2（仅供演示用途），实用场景的推荐值如下表：

| 效果类型 | 推荐 Max Neighbors Per Cell | 原因 |
|---|---|---|
| Boid鸟群（低密度） | 8 | 每格平均粒子数≤5 |
| 粒子排斥力（中密度） | 16 | 局部聚集时需冗余容量 |
| SPH流体（高密度） | 32 | 近邻粒子数可达20+ |

该值与格元总数的乘积直接决定邻域网格消耗的GPU显存：

$$
\text{MemoryBytes} = N_x \times N_y \times N_z \times \text{MaxNeighbors} \times 4
$$

例如，一个 $32 \times 32 \times 32$、每格最多16邻居的网格需要 $32^3 \times 16 \times 4 = 67,108,864$ 字节（约64 MB）。`Max Neighbors Per Cell` 设置过小时，超出容量的粒子将被**静默丢弃**，不触发任何错误提示，造成粒子交互不对称的视觉瑕疵——A粒子感知到B，但B感知不到A——这是邻域网格最常见且最难定位的隐性bug。

### 查询半径与格元遍历范围

`Get Particles In Neighborhood` 节点接受一个 `Query Radius` 参数。在内部实现上，节点以查询粒子所在格元为中心，向外扩展 $\lceil \text{QueryRadius} / \text{CellSize} \rceil$ 层格元进行遍历。当QueryRadius恰好等于CellSize时，遍历范围是3×3×3=27个格元；当QueryRadius=2×CellSize时，遍历扩展到5×5×5=125个格元，单次查询代价提升约4.6倍。因此，**不应通过增大QueryRadius来弥补CellSize过大的问题**，而应首先调整格元尺寸使其与查询半径匹配。

---

## 关键公式与蓝图节点配置

### Niagara脚本节点调用顺序

以下为Population Stage与Query Stage的典型HLSL伪代码逻辑，直接对应Niagara图表中的节点连接顺序：

```hlsl
// === Stage 1: Population Stage ===
// 节点: Neighbor Grid 3D → Set Particle Neighbors
int3 cellCoord = floor((ParticlePosition - BoundsMin) / CellSize);
NeighborGrid.WriteParticle(cellCoord, ParticleIndex);

// === Stage 2: Query Stage ===
// 节点: Neighbor Grid 3D → Get Particles In Neighborhood
int3 myCell = floor((ParticlePosition - BoundsMin) / CellSize);
int searchRadius = ceil(QueryRadius / CellSize);  // 通常为1，即3×3×3遍历

float3 separationForce = float3(0, 0, 0);
for (int dx = -searchRadius; dx <= searchRadius; dx++)
for (int dy = -searchRadius; dy <= searchRadius; dy++)
for (int dz = -searchRadius; dz <= searchRadius; dz++) {
    int3 neighborCell = myCell + int3(dx, dy, dz);
    int neighborCount = NeighborGrid.GetParticleCount(neighborCell);
    for (int i = 0; i < neighborCount; i++) {
        int neighborIdx = NeighborGrid.GetParticle(neighborCell, i);
        float3 delta = ParticlePosition - Particles_Position[neighborIdx];
        float dist = length(delta);
        if (dist > 0 && dist < QueryRadius) {
            // 排斥力：距离越近，力越强
            separationForce += normalize(delta) * (1.0 - dist / QueryRadius);
        }
    }
}
ParticleVelocity += separationForce * SeparationStrength * DeltaTime;
```

### SPH密度估算公式

在流体模拟中，邻域网格常用于计算光滑粒子流体力学（SPH）的局部密度。给定光滑核函数 $W(r, h)$（其中 $h$ 为光滑半径，即QueryRadius），粒子 $i$ 的局部密度为：

$$
\rho_i = \sum_{j \in \mathcal{N}(i)} m_j \cdot W(\|\mathbf{r}_i - \mathbf{r}_j\|, h)
$$

常用的Poly6核函数定义为：

$$
W(r, h) = \frac{315}{64\pi h^9} \cdot \max(h^2 - r^2, 0)^3
$$

此公式直接在Query Stage的HLSL脚本中实现，$\mathcal{N}(i)$ 即由邻域网格检索到的邻居粒子集合。

---

## 实际应用案例

### 案例一：Boid鸟群模拟

Boid算法由Craig Reynolds于1987年提出，包含分离（Separation）、对齐（Alignment）、聚合（Cohesion）三条规则，每条规则均需访问半径R内的邻居速度和位置。在10,000只Boid的场景中，配置参数建议如下：

- **NumCells**：每轴32，包围盒500×500×500 cm，CellSize约15.6 cm
- **QueryRadius**：20 cm（约为CellSize的1.28倍）
- **Max Neighbors Per Cell**：12
- **GPU显存占用**：$32^3 \times 12 \times 4 \approx 50$ MB

使用邻域网格后，该场景在RTX 3080上稳定运行于60fps，而暴力O(N²)方案在相同粒子数下帧时间超过80ms。

### 案例二：粒子碰撞排斥力

在烟花或泡沫粒子效果中，需要防止粒子相互穿插。每帧在Query Stage中对所有距离小于 `MinDistance`（通常为粒子直径，例如5 cm）的邻居施加沿连线方向的冲量：

$$
\Delta \mathbf{v}_i = \sum_{j \in \mathcal{N}(i)} k \cdot \max\left(d_{\min} - \|\mathbf{r}_{ij}\|, 0\right) \cdot \hat{\mathbf{r}}_{ij}
$$

其中 $k$ 为排斥刚度系数，典型值为0.5到2.0（单位：cm⁻¹·s⁻¹）。

### 案例三：粒子间颜色传播（类火焰蔓延）

将一个自定义浮点属性 `HeatValue`（初始值0到1）存入粒子数据集，在Query Stage中让每个粒子从邻居中取平均热值，再施加一个传播速率系数（例如0.1/帧）：

```hlsl
float heatSum = 0.0;
int count = 0;
// ... 遍历邻居（同上方伪代码结构）
    heatSum += Particles_HeatValue[neighborIdx];
    count++;
// ...
if (count > 0) {
    float avgHeat = heatSum / count;
    Particles_HeatValue[ParticleIndex] += (avgHeat - Particles_HeatValue[ParticleIndex]) * 0.1;
}
```

此效果可模拟火焰在粒子群中自然蔓延的视觉现象，无需任何外部纹理驱动。

---

## 常见误区与调试指南

### 误区一：在同一Stage中同时写入和读取

**现象**：粒子交互完全失效，或每帧结果不稳定。  
**根因**：GPU线程并行执行时，写入操作尚未完成就被其他线程读取。  
**修复**：严格保证Population Stage（含`Set Particle Neighbors`节点）的`Stage Order`数值小于Query Stage，且两个Stage属于不同的Simulation Stage节点。

### 误区二：Max Neighbors Per Cell默认值为2未修改

**现象**：粒子效果在低密度时正常，粒子聚集区域交互突然消失或明显不对称。  
**根因**：默认值2仅为模板占位，超出容量的粒子索引被覆盖写入，实际存储的邻居数始终不超过2个。  
**调试方法**：在Query Stage中将每个粒子获取到的