---
id: "cg-mesh-deformation"
concept: "网格变形"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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


# 网格变形

## 概述

网格变形（Mesh Deformation）是几何处理领域中将三角网格或多边形网格从一种形状平滑变换为另一种形状的技术集合。其核心目标是在改变网格顶点位置的同时，尽量保持局部几何特征——例如曲面的光滑度、面积比例或角度关系。网格变形广泛应用于角色动画、医学图像配准、工业设计和游戏引擎中。

自由形变（Free-Form Deformation，FFD）由 Sederberg 和 Parry 于 1986 年在 SIGGRAPH 论文中首次提出，其基本思想是将网格嵌入一个参数化的控制晶格（Lattice）中，通过移动晶格控制点来间接驱动网格顶点位移。骨骼蒙皮绑定（Skeletal Skinning）则起源于 1988 年左右的计算机动画实践，通过为每个网格顶点分配骨骼权重，使顶点跟随骨骼运动而形变。这两种方法分别代表了"空间控制"和"骨骼驱动"两大主流范式，至今仍是实时动画引擎（如 Unreal Engine、Unity）的底层机制。

理解网格变形对几何处理工程师至关重要，因为不合理的变形会导致网格自相交（Self-Intersection）、面积剧烈收缩（Volume Collapse）或三角形翻转（Flipped Triangle），这些缺陷在渲染时会产生明显的视觉撕裂伪影。

---

## 核心原理

### 自由形变（FFD）的数学机制

FFD 将网格顶点坐标 **p** 映射到控制晶格的局部参数坐标 **(s, t, u) ∈ [0,1]³**，再通过三元 Bernstein 多项式重建变形后的位置：

$$\mathbf{p}' = \sum_{i=0}^{l}\sum_{j=0}^{m}\sum_{k=0}^{n} B_i^l(s)\,B_j^m(t)\,B_k^n(u)\,\mathbf{P}_{ijk}$$

其中 $B_i^l(s) = \binom{l}{i}s^i(1-s)^{l-i}$ 为 Bernstein 基函数，$\mathbf{P}_{ijk}$ 是控制晶格的控制点坐标，*l, m, n* 是各方向上的控制点数减一。以 3×3×3 的晶格为例，共有 27 个控制点，每移动一个控制点会以 Bezier 平滑方式影响晶格内所有顶点，而晶格外顶点不受影响。FFD 的关键优势在于：用户只需操控少量控制点（几十个），即可驱动数万个网格顶点产生全局平滑变形，且变形结果具有 C² 连续性保证。

### 骨骼蒙皮绑定（Linear Blend Skinning）

线性混合蒙皮（Linear Blend Skinning，LBS）是当前实时游戏中最普遍的骨骼变形方法，其变形公式为：

$$\mathbf{v}' = \sum_{j=1}^{n} w_j \cdot M_j \cdot \mathbf{v}$$

其中 $\mathbf{v}$ 是顶点在绑定姿态（Bind Pose）下的齐次坐标，$M_j = B_j \cdot B_{j,\text{bind}}^{-1}$ 是第 $j$ 根骨骼的当前变换矩阵乘以绑定逆矩阵，$w_j$ 是该顶点对第 $j$ 根骨骼的蒙皮权重，满足 $\sum w_j = 1$。权重通常由美术师通过权重绘制（Weight Painting）工具手动调整，或由基于距离的热扩散算法（Bounded Biharmonic Weights，Jacobson 2011）自动计算。LBS 的主要缺陷是"糖果纸扭曲"（Candy-Wrapper Artifact）：当关节旋转超过约 90° 时，混合两个旋转矩阵会导致肘部或肩部网格体积塌陷。

### 变形质量的保体积约束

为克服 LBS 的体积塌陷问题，Dual Quaternion Skinning（DQS，Kavan 等 2008）使用对偶四元数替代矩阵进行插值：

$$\mathbf{v}' = \text{DQ}\left(\sum_{j} w_j \hat{q}_j\right) \cdot \mathbf{v}$$

对偶四元数在插值时保持刚体运动的连续性，能有效消除糖果纸扭曲，因此 Unity 和 Blender 均将 DQS 作为默认骨骼蒙皮选项（Unity 自 4.3 版本起支持）。此外，基于 As-Rigid-As-Possible（ARAP）能量最小化的变形方法（Sorkine & Alexa，2007）在每个顶点的局部邻域上施加旋转优先约束，使变形尽量为局部等距变换，有效保持三角面的形状。

---

## 实际应用

**游戏角色动画**：在 Unreal Engine 中，骨骼网格体（Skeletal Mesh）存储每个顶点最多 8 个骨骼权重影响（Influence），引擎在 GPU 顶点着色器阶段实时执行 LBS 或 DQS 运算，使角色在跑步、跳跃等动作中保持平滑的皮肤变形。角色关节处的权重通常需要专门的"矫正形变"（Corrective Blend Shape）来修复 LBS 的扁平化问题。

**工业产品设计**：Autodesk Maya 和 Rhinoceros 软件使用 FFD 晶格让设计师对汽车车身曲面进行整体造型调整，设计师无需逐点编辑数万个控制顶点，只需拖动 4×4×4 共 64 个晶格点即可重塑整体轮廓，同时保持曲面 C² 连续性。

**医学图像配准**：基于 B-Spline FFD 的非刚性图像配准（Rueckert 等，1999）被用于将 CT 扫描的肺部网格模型变形匹配到不同呼吸相位，控制晶格间距通常设置为 5–20mm，以平衡变形自由度与计算效率。

---

## 常见误区

**误区一：蒙皮权重总和必须等于 1 只是一个约定**
权重归一化 $\sum w_j = 1$ 不是任意约定，而是保证刚体骨骼在恒等变换时顶点位置不变的数学必要条件。若权重之和不为 1，即使在绑定姿态下（所有骨骼均为单位变换），顶点也会发生非预期偏移，导致网格在 T-pose 就已经变形。

**误区二：FFD 变形会直接修改网格拓扑**
FFD 仅移动顶点位置，不改变网格的边连接关系（拓扑）。因此 FFD 可以产生自相交（两个面片穿入彼此），但不会合并或分裂顶点。检测 FFD 导致的自相交需要额外的碰撞检测步骤，例如基于 BVH 的三角形对测试，这与 FFD 本身的计算是完全独立的阶段。

**误区三：Linear Blend Skinning 与 Dual Quaternion Skinning 效果差距只在极端角度才体现**
实际测试表明，即使在 45° 的肩关节外展动作下，LBS 也会产生可见的体积减少约 15–20%，而 DQS 在同等角度下几乎无体积损失。这一差距在写实风格渲染中已足够明显，因此高品质影视动画几乎全部采用 DQS 或更高阶方法。

---

## 知识关联

**依赖前置知识——网格表示**：网格变形的操作对象是三角网格的顶点列表和面片索引结构。LBS 公式中的 $\mathbf{v}$ 直接对应网格表示中存储的齐次坐标顶点，而 FFD 的参数化映射需要首先将每个顶点从世界坐标系转换到晶格局部坐标系，这一步骤依赖对网格顶点坐标系和包围盒计算的理解。

**延伸方向**：掌握 FFD 和 LBS 的数学机制后，可进一步研究基于物理的变形仿真（如有限元弹性体模拟）以及神经网络驱动的变形方法（Neural Blend Shapes，Lin 等，2021），后者使用深度学习直接从动作捕捉数据中学习非线性皮肤变形残差，能自动修复 LBS 在复杂动作下的所有伪影。