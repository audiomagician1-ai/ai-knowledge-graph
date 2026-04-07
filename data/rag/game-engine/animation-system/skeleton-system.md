# 骨骼系统

## 概述

骨骼系统（Skeleton System）是游戏引擎动画系统的基础架构，由一组具有严格父子关系的骨骼节点（Bone）构成有向树形结构，每根骨骼本质上是三维空间中的一个坐标变换节点，携带位置（Translation）、旋转（Rotation）与缩放（Scale）三种属性，通称 TRS 数据。子骨骼的世界空间变换由其所有祖先骨骼的局部变换矩阵依次右乘累积而得，这使得驱动骨盆骨骼旋转时，大腿、膝盖、小腿与脚踝会自动跟随，无需对每块骨骼单独设置关键帧。

骨骼动画的系统化理论由 Nadia Magnenat-Thalmann 与 Daniel Thalmann 在1988年的论文《Synthetic Actors in Computer-Generated 3D Films》中率先提出，并在此后数年内迅速取代了直接对顶点设置关键帧的变形目标（Morph Target）方案，成为实时角色动画的主流技术路线（Gregory, 2018）。骨骼系统的核心优势在于：一套拥有67根骨骼的人形骨架，即可驱动数十万顶点的网格体变形，存储与运算开销相较逐顶点关键帧减少一至两个数量级。

在工业实践层面，Unreal Engine 5 官方人形角色（UE5 Mannequin）默认拥有约67根骨骼；Unity 的 Humanoid Avatar 规范则强制定义15根必须映射的骨骼（髋、脊柱、胸、颈、头、左右上臂/前臂/手、左右大腿/小腿/脚），其余骨骼视为可选。骨骼数量直接决定 GPU 蒙皮着色器中常量缓冲区（Constant Buffer）的矩阵数组大小，在移动端通常将每角色骨骼数控制在75根以内以兼容低端 GPU 的 Uniform 存储上限。

---

## 核心原理

### 骨骼层级与变换传播

骨骼系统以单根有向树（Rooted Tree）组织所有关节，根节点通常命名为 Root 或 Hips/Pelvis。每根骨骼 $i$ 持有一个**局部变换矩阵** $\mathbf{L}_i \in \mathbb{R}^{4\times4}$，描述其相对父骨骼坐标系的偏移与朝向。**模型空间变换矩阵**（也称世界矩阵，World Matrix）$\mathbf{W}_i$ 通过以下递推式从根到叶依次计算：

$$\mathbf{W}_i = \mathbf{W}_{\text{parent}(i)} \cdot \mathbf{L}_i$$

其中根骨骼满足 $\mathbf{W}_{\text{root}} = \mathbf{L}_{\text{root}}$。对全树求解 $\mathbf{W}_i$ 的过程称为**前向运动学（Forward Kinematics, FK）**，时间复杂度为 $O(n)$，$n$ 为骨骼总数，运算顺序必须保证父骨骼先于子骨骼处理（即拓扑排序）。

局部变换 $\mathbf{L}_i$ 通常不以 $4\times4$ 矩阵存储，而拆分为平移向量 $\mathbf{t} \in \mathbb{R}^3$ 与单位四元数 $\mathbf{q} \in \mathbb{H}$（必要时附加缩放向量 $\mathbf{s}$），以减少浮点精度损失并便于球面线性插值（Slerp）。只有在提交 GPU 蒙皮计算前，才将 TRS 展开为 $4\times3$ 或 $4\times4$ 矩阵（Gregory, 2018）。

### 绑定姿势（Bind Pose）与逆绑定矩阵

绑定姿势（Bind Pose，亦称 T-Pose 或 A-Pose）是骨骼与网格体建立蒙皮权重关联时骨骼所处的参考姿态。在此姿态下，每根骨骼的模型空间变换被记录为**绑定矩阵** $\mathbf{B}_i$，同时预计算其逆矩阵：

$$\mathbf{M}_i^{\text{skin}} = \mathbf{W}_i \cdot \mathbf{B}_i^{-1}$$

$\mathbf{B}_i^{-1}$ 称为**逆绑定矩阵（Inverse Bind Matrix / Offset Matrix）**。蒙皮矩阵 $\mathbf{M}_i^{\text{skin}}$ 的物理含义是：先将顶点从模型空间变换回骨骼 $i$ 的"零姿势局部空间"（乘以 $\mathbf{B}_i^{-1}$），再施加当前帧的骨骼变换（乘以 $\mathbf{W}_i$）。若绑定矩阵不正确（例如在绑定时骨骼已有额外旋转偏移），蒙皮顶点在 Bind Pose 下也会产生错位，这是角色美术制作中最常见的返工原因之一（Parent, 2012）。

逆绑定矩阵在模型导入阶段一次性计算并持久化存储；运行时每帧只需计算 $\mathbf{W}_i$ 并乘以预存的 $\mathbf{B}_i^{-1}$，避免了矩阵求逆的实时开销。

### 骨骼索引与骨骼姿势数组

引擎内部通常以紧凑的**骨骼姿势数组（Pose Array / Bone Transform Array）** 表示一帧的骨骼状态，数组下标即骨骼索引（Bone Index）。例如，UE5 的 `FCompactPoseBoneIndex` 是一种稀疏骨骼集合的紧凑索引，允许动画图（Anim Graph）跳过当前动画不涉及的骨骼，减少无效矩阵乘法。父骨骼索引数组（Parent Index Array）与骨骼姿势数组并行存储，使前向运动学遍历可在连续内存上完成，对 CPU 缓存友好。

---

## 关键公式与蒙皮计算

### 线性混合蒙皮（Linear Blend Skinning, LBS）

线性混合蒙皮是游戏引擎中应用最广泛的实时蒙皮算法，其顶点位置更新公式为：

$$\mathbf{v}' = \sum_{j=1}^{k} w_j \cdot \mathbf{M}_j^{\text{skin}} \cdot \mathbf{v}$$

其中 $\mathbf{v}$ 是绑定姿势下的顶点齐次坐标，$w_j$ 是第 $j$ 根骨骼对该顶点的权重（满足 $\sum w_j = 1$），$k$ 通常限制为每顶点最多4根骨骼影响（移动端常压缩至2根）以保证着色器寄存器效率。LBS 存在著名的"糖果包扭曲（Candy-Wrapper Artifact）"问题：当关节旋转接近180°时，混合后的矩阵行列式趋近于零，导致体积塌陷（Parent, 2012）。

### 双四元数蒙皮（Dual Quaternion Skinning, DQS）

为解决 LBS 的体积损失问题，Ladislav Kavan 等人在2008年发表《Skinning with Dual Quaternions》，提出以对偶四元数 $\hat{\mathbf{q}} = \mathbf{q}_0 + \varepsilon \mathbf{q}_\varepsilon$ 编码刚体变换（纯旋转+平移，无缩放），蒙皮公式变为：

$$\hat{\mathbf{q}}' = \frac{\sum_{j} w_j \hat{\mathbf{q}}_j}{\left\|\sum_{j} w_j \hat{\mathbf{q}}_j\right\|}$$

DQS 保持了体积守恒，但引入"膨胀（Bulging）"伪影，且对非均匀缩放的支持有限。UE5 在 `Skinning Mode` 设置中同时提供 LBS 与 DQS 两种选项，开发者可按角色需求切换。

---

## 实际应用

### 动画重定向（Animation Retargeting）

动画重定向是将一套骨骼层级上录制的动画数据迁移至比例或拓扑不同的骨骼上的技术。其前提是两套骨骼共享相同的**语义骨骼映射**（例如将源骨骼"Bip001 L Thigh"映射至目标骨骼"Thigh_L"），并在绑定姿势下对旋转偏移进行补偿。UE5 的 IK Rig Retargeter 工具允许在编辑器内直接拖拽调整每根骨骼的重定向模式（Skeleton / Animation / AnimationScaled），以处理身高、四肢比例差异引起的脚部穿地或手臂过长等问题。

**例如**：将专业动捕演员（身高180 cm、臂展185 cm）的走路动画重定向至游戏内矮人角色（身高120 cm、臂展100 cm）时，若髋骨骨骼采用"AnimationScaled"模式，引擎会按目标骨骼实际骨长比例缩放位移分量，从而保证脚踝落地点贴近地面；若改用"Animation"模式则直接复制原始位移，导致矮人双脚悬空约60 cm。

### 程序化骨骼控制与IK

在运行时，引擎会在完成FK计算后、提交蒙皮矩阵前，插入一个**后处理动画图（Post-Process Anim Graph）**阶段，允许通过逆向运动学（Inverse Kinematics, IK）修正末端执行器位置。例如，UE5 的 Full Body IK（FBIK）节点以角色脚踝为末端执行器，在检测到地面法线倾斜时实时调整整条腿的骨骼链，使角色在崎岖地形上保持脚部贴地效果，而无需为每种地形角度单独制作动画。

### 骨骼插槽（Socket）与附件挂载

骨骼上可定义**插槽（Socket）**——一个带有固定局部偏移（TRS）的虚拟附加点。武器、特效粒子系统、摄像机臂等Actor组件均可Attach至指定骨骼插槽，每帧随骨骼矩阵自动更新其世界变换，无需在蓝图或C++中手动计算附件位置。例如，将手枪Attach至"hand_r"骨骼的"weapon_socket"，枪口朝向在整个射击动画过程中自动跟随右手骨骼旋转，误差来源仅为单次矩阵乘法的浮点精度。

---

## 常见误区

**误区一：将骨骼数量与动画质量直接挂钩。** 骨骼数量增多不必然提升动画表现力，过多的辅助骨骼（如每块布料面片一根骨骼的手工布料骨骼链）会显著增加蒙皮带宽开销，在移动端可能导致DrawCall中骨骼矩阵超出Uniform Buffer限制（通常为75×4×3 = 900个float）。高质量动画更依赖关键帧曲线的精心调整与正确的骨骼权重绘制，而非骨骼数量堆砌。

**误区二：绑定姿势可以任意选取。** Bind Pose 的选择直接影响关节弯曲时的蒙皮质量。T-Pose（双臂水平伸展、手掌朝下）曾是行业标准，但肩部骨骼在此姿势下需旋转约90°才能到达自然下垂位，导致腋下三角区顶点权重难以合理分配。目前业界趋势是改用**A-Pose**（双臂与躯干约成45°夹角），使肩关节处于受力中性位，蒙皮权重绘制更直观，且与运动捕捉的标准参考姿势更接近（Gregory, 2018）。

**误区三：骨骼空间与模型空间等同。** 初学者常混淆局部空间（Local Space，相对父骨骼）与模型空间（Model Space，相对角色根节点原点）。动画曲线存储的是局部空间的 TRS 数据，直接读取动画曲线值不能用于计算顶点的最终位置；必须先执行 FK 遍历，将所有局部变换累乘为模型空间矩阵，再乘以逆绑定矩