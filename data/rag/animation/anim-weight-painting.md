---
id: "anim-weight-painting"
concept: "权重绘制"
domain: "animation"
subdomain: "skeletal-rigging"
subdomain_name: "骨骼绑定"
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



# 权重绘制

## 概述

权重绘制（Weight Painting）是骨骼绑定流程中的手动精修步骤，通过类似绘画的交互方式，为网格体上的每个顶点直接指定或修改骨骼影响强度。每个顶点存储一个介于 0.0 到 1.0 之间的浮点数权重值：0.0 表示该骨骼对此顶点完全没有影响，1.0 表示该骨骼完全控制此顶点的位移与旋转，中间值产生多骨骼混合驱动的平滑过渡效果。

权重绘制作为独立工作流出现于 20 世纪 90 年代末三维动画软件的成熟期。早期的《Softimage 3D》3.x 版本和后来的 Maya 5.0（2003年发布）均引入了交互式权重绘制笔刷（Interactive Skin Weight Tool），让美术人员能够以视觉化方式替代手动输入数值来修正自动蒙皮生成的权重表。Blender 在 2.4x 系列（约 2006 年）正式将权重绘制整合为独立编辑模式（Weight Paint Mode），并在 2.80 版本（2019 年）对工具面板进行了全面重构。

权重绘制的核心价值在于修正自动蒙皮算法（如 Blender 的 Envelope Weights 或 Maya 的 Geodesic Voxel Binding）产生的权重瑕疵。自动算法依赖几何距离计算，无法识别肘部内侧、腋下、膝盖弯折等高变形区域的特殊生理需求，只有通过手动绘制才能让这些区域的变形符合真实肌肉与皮肤的运动逻辑。参考资料：《The Animator's Survival Kit》（Richard Williams, 2001, Faber & Faber）对角色关节变形规律的描述，是权重绘制实践的重要理论依据。

---

## 核心原理

### 权重值的颜色映射与归一化规则

在权重绘制模式下，软件以伪彩色热图（Heatmap）显示权重分布：**蓝色代表 0.0，红色代表 1.0**，中间依次经过青色（约 0.25）、绿色（约 0.5）、黄色（约 0.75）过渡。这种可视化设计让美术人员能够直观识别"过渡带"（Transition Zone）是否平滑，以及硬边界是否存在。

多骨骼蒙皮系统遵守**权重归一化（Normalize Weights）规则**：同一顶点所有骨骼权重之和必须等于 1.0。设顶点 $v$ 受 $n$ 根骨骼影响，其权重归一化公式为：

$$w_i' = \frac{w_i}{\sum_{j=1}^{n} w_j}, \quad i = 1, 2, \ldots, n$$

其中 $w_i$ 为第 $i$ 根骨骼的原始权重，$w_i'$ 为归一化后的权重，满足 $\sum_{i=1}^{n} w_i' = 1.0$。例如，当你将 `spine_01` 骨骼的权重提升至 0.8，若 `hip` 骨原为 0.4、`spine_02` 原为 0.2，系统会将剩余两骨按比例压缩：`hip` 变为 $0.4 \times \frac{0.2}{0.6} \approx 0.133$，`spine_02` 变为 $0.2 \times \frac{0.2}{0.6} \approx 0.067$。若关闭归一化，顶点会被多根骨骼的全量权重叠加拉扯，产生"爆炸式"变形崩坏。

### 笔刷参数：半径、强度与衰减曲线

权重绘制的核心工具是笔刷（Brush），关键参数包括：

- **半径（Radius）**：影响范围，Blender 中默认快捷键 `F` 拖拽调节，建议关节区域使用 20–40px，大面积躯干区域使用 80–150px。
- **强度（Weight/Strength）**：每次笔触叠加或削减的权重增量，取值 0.0–1.0。精细过渡区域建议使用 0.05–0.1 的低强度值，反复涂抹累积，避免单次高强度覆盖造成硬边。
- **衰减曲线（Falloff Curve）**：决定笔刷中心到边缘的权重变化形状，常见的有球形（Sphere）、平滑（Smooth）、常数（Constant）三种。球形衰减的权重分布公式为 $w(r) = 1 - r^2$（其中 $r$ 为归一化半径，$r \in [0,1]$），产生最自然的羽化边缘，适合大多数关节绑定场景。

绘制肘关节弯折区域时，推荐将强度设为 0.08，衰减选择球形，配合 **Blur/Smooth 模式**的笔刷对权重边界反复平滑 3–5 次，而非直接以强度 1.0 的大笔触覆盖。

### 镜像权重与顶点组管理

对于左右对称角色，权重绘制支持 **X 轴镜像绘制**（Mirror Vertex Groups），前提是左右骨骼命名严格遵循 `_L / _R` 或 `Left / Right` 的约定。Blender 的镜像权重功能通过查找同名对称顶点组实现实时同步（例如编辑 `upper_arm_L` 时自动同步到 `upper_arm_R`），而 Maya 则依赖"Mirror Skin Weights"工具，通过指定源表面与目标表面的对应轴向（+X 到 -X）完成镜像复制。

每根骨骼对应一个**顶点组（Vertex Group）**，权重绘制的本质是在编辑当前激活顶点组内各顶点的浮点数值。复杂游戏角色的顶点组数量通常在 50–120 个之间，AAA 级影视角色可达 200 个以上。建议在绘制前通过 **Normalize All**（Blender 快捷键：权重菜单 > Normalize All）对全部顶点组执行一次批量归一化，消除自动蒙皮遗留的权重冗余。

---

## 关键公式与算法

### 线性蒙皮混合（LBS）与权重的数学关系

权重绘制所修改的数值直接驱动线性蒙皮混合（Linear Blend Skinning，LBS）算法。顶点 $v$ 的最终变形位置 $v'$ 由以下公式计算（参见 Sumner & Popović, 2004, SIGGRAPH）：

$$v' = \sum_{i=1}^{n} w_i \cdot M_i \cdot v$$

其中 $M_i$ 为第 $i$ 根骨骼的变换矩阵（包含旋转、位移、缩放），$w_i$ 为该骨骼对顶点的归一化权重，$n$ 为影响该顶点的骨骼总数。这一公式说明，权重值的微小误差会被骨骼变换矩阵放大——当骨骼旋转角度较大（如 90° 弯曲）时，哪怕 0.05 的权重误差也会在网格上产生数毫米的可见偏移。

### 在 Blender Python API 中读取与写入权重

通过 Blender 的 Python API 可以程序化地批量修改权重数据，例如将某顶点组内所有权重低于阈值 0.01 的顶点清零（"清理脏权重"）：

```python
import bpy

obj = bpy.context.active_object
threshold = 0.01
group_name = "upper_arm_L"

vg = obj.vertex_groups.get(group_name)
if vg:
    for v in obj.data.vertices:
        for g in v.groups:
            if g.group == vg.index:
                if g.weight < threshold:
                    # 将微小权重清零，减少顶点组污染
                    vg.add([v.index], 0.0, 'REPLACE')
print(f"已清理 {group_name} 中权重低于 {threshold} 的顶点")
```

这种脚本化清理能有效消除自动蒙皮在远端区域遗留的"幽灵权重"（Ghost Weights），防止手指骨骼微弱影响到肩膀网格顶点。

---

## 实际应用

### 肘关节的双轴变形修正

肘关节是权重绘制中最典型的难点区域。当 `forearm` 骨骼旋转 135° 时，纯 LBS 算法会导致肘部内侧网格发生"糖果纸扭曲"（Candy Wrapper Artifact），表现为体积塌陷约 30–40%。标准修正方案是引入**辅助骨骼（Corrective Bone）**：在 `forearm` 内侧添加一根名为 `elbow_tweak` 的非变形骨骼，为其绘制 0.3–0.5 的过渡权重，使该区域顶点在弯曲时被向外侧轻微推移，补偿体积损失。

例如，针对人体手肘内侧的 20–35 个顶点，建议权重分布如下：`upper_arm` 占 0.15，`forearm` 占 0.55，`elbow_tweak` 占 0.30，三者之和严格等于 1.0。实际绘制时先用强度 0.3 的笔刷确定大范围，再用强度 0.05 的笔刷对边缘 2–3 圈顶点执行 5–8 次 Smooth 操作，最终在绑定测试（Rig Test）中以 90° 和 135° 两个极端姿势验证结果。

### 面部绑定中的精细权重分区

面部表情绑定（Facial Rigging）对权重绘制精度要求极高。眼轮匝肌区域（眼睑周围约 80–120 个顶点）通常需要 4–6 根骨骼协同驱动（`eyelid_upper`、`eyelid_lower`、`eye_corner_L/R`、`cheek_raise`），每根骨骼的权重过渡宽度仅为 2–4mm 的网格间距。在 Blender 中，建议将笔刷半径缩小至 8–12px、强度设为 0.03，并开启"顶点选择遮罩"（Vertex Selection Masking）以防止误涂到相邻区域。

游戏引擎（如 Unreal Engine 5 的 Skeleton Mesh）对单顶点最大影响骨骼数有硬性限制：移动平台为 4 根，PC/主机平台为 8 根。超出限制的权重会在导入时被自动截断，因此在权重绘制完成后必须执行**限制影响数量**（Limit Total，Blender 快捷键：权重菜单 > Limit Total，设置 Maximum = 4 或 8）操作，并再次归一化。

---

## 常见误区

### 误区一：过渡带越宽越好

许多初学者认为权重过渡越平滑、宽度越大，变形越自然。实际上，过宽的过渡带（超过关节长度的 40%）会导致**运动传递滞后**——当手腕骨骼旋转时，前臂中段也会被带动旋转，角色看起来像是"橡皮人"而非有骨骼的生物。腕关节的过渡带宽度建议控制在骨骼长度的 15–25% 范围内。

### 误区二：忽略静止姿势（Rest Pose）的权重验证

权重绘制必须在骨骼的**静止姿势（Rest Pose / Bind Pose）**下进行并验证。部分美术人员习惯在 T-Pose 绑定后立刻切换到 A-Pose 测试，但 A-Pose 下肩部骨骼已产生约 45° 的旋转，此时观察到的权重问题可能是姿势偏移造成的假象，而非真实权重错误。正确流程是：先在 Rest Pose 下确认权重无顶点组缺失或归一化错误，再进入 Pose Mode 以极端旋转角度（90°、-90°、135°）逐一测试每个关节。

### 误区三：依赖自动平滑覆盖手动细节

Blender 的 **Smooth 笔刷**（以及 Maya 的 Smooth Skin Weights）会将相邻顶点的权重取平均值，反复使用会抹去刻意绘制的非对称权重细节。例如，脊椎侧弯时左右两侧应有不同的权重分布来模拟