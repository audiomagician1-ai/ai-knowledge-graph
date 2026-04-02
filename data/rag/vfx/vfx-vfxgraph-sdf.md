---
id: "vfx-vfxgraph-sdf"
concept: "SDF交互"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# SDF交互

## 概述

SDF交互（Signed Distance Field Interaction）是VFX Graph中利用有符号距离场数据驱动粒子行为的技术。有符号距离场是一种三维纹理格式，其中每个体素存储的浮点值代表该点到最近几何表面的有符号距离——正值表示在几何体外部，负值表示在几何体内部，零值精确位于表面上。Unity VFX Graph通过对这种3D纹理的采样，使粒子能够感知场景中的静态几何形状，从而实现碰撞、引导、排斥等复杂的物理交互效果。

从技术历史来看，SDF在图形学中的应用可追溯到1980年Feuerstein等人的工作，但在实时粒子系统中大规模落地是GPU计算能力飞跃之后的事。Unity从VFX Graph正式发布（2019.3版本随Unity 2019.3 LTS稳定推出）起便内置了SDF采样节点，并在后续版本中引入了`SDF Baker`工具，允许美术人员直接将Mesh烘焙为Runtime可用的3D纹理。这一闭环工具链使SDF在游戏特效制作中真正实现了生产可用性。

SDF交互的核心价值在于性能与精度的平衡。传统粒子碰撞依赖物理引擎的Ray Cast或Depth Buffer反查，前者CPU开销巨大，后者存在视角盲区问题。SDF方法将几何信息预烘焙到纹理中，粒子每帧只需执行一次GPU纹理采样即可获得自身到表面的精确距离和梯度方向，这一操作可完全在Compute Shader中并行完成，对百万级粒子规模依然保持线性性能复杂度。

---

## 核心原理

### 距离场采样与梯度计算

VFX Graph中的`Sample SDF`节点接受一个归一化的3D位置坐标（范围0到1，对应SDF纹理的包围盒空间），返回一个浮点型有符号距离值。实际使用时需要将粒子的世界坐标转换到SDF的本地空间，公式为：

```
localPos = (worldPos - sdfOrigin) / sdfExtents
```

其中`sdfOrigin`是SDF包围盒中心的世界坐标，`sdfExtents`是包围盒三个轴向的半边长。转换后的`localPos`输入`Sample SDF`节点，输出的距离值单位为世界空间单位（米）。

梯度方向是SDF交互中同等重要的输出。通过对距离场进行有限差分采样——在X、Y、Z三个轴上分别偏移一个微小量`ε`（通常取纹理分辨率倒数的1到2倍）——可以计算出表面法线方向。VFX Graph提供的`Sample SDF Gradient`节点封装了这一6次采样过程，输出的归一化向量指向距最近表面最短路径的方向，可直接用于粒子的反弹、滑动和沿面流动计算。

### 碰撞与排斥响应

将`Sample SDF`返回的距离值与粒子半径进行比较（通常粒子半径在0.01到0.1米范围），当`distance < radius`时触发碰撞响应。VFX Graph的`Collision`Update Context中内置了基于SDF的碰撞计算模块，其核心逻辑是：

1. 检测粒子是否穿入表面（`distance < 0`）
2. 若穿入，沿梯度方向推出粒子到`distance = 0`位置
3. 对速度向量进行反射：`v_reflect = v - 2 * dot(v, n) * n`，再乘以弹性系数（`Bounciness`，范围0到1）
4. 对切线方向速度乘以摩擦系数（`Friction`，范围0到1）

这一四步流程全部在GPU的Update阶段执行，无需与CPU物理引擎通信。

### SDF烘焙分辨率与精度权衡

Unity的`VFX SDF Bake Tool`（位于`Window > VFX > SDF Bake Tool`菜单）将Mesh烘焙为3D RenderTexture，分辨率选项包括32³、64³、128³和256³，对应的纹理内存占用分别为约0.13MB、1MB、8MB和64MB（以16位浮点精度计算）。分辨率直接决定了可表达的几何细节最小尺寸：64³分辨率下，若SDF包围盒为2m×2m×2m，则最小可分辨特征约为3.1cm（2000mm÷64≈31.25mm）。复杂角色或带有细小几何细节的道具建议使用128³，开阔地形使用64³即可满足粒子交互精度需求。

---

## 实际应用

**雨水打湿表面效果**：将角色Mesh烘焙为128³分辨率的SDF，将雨滴粒子系统的碰撞源设为该SDF。粒子下落时采样SDF距离，当距离小于0.02m时触发碰撞，沿SDF梯度（即表面法线）反弹，同时生成一个次级粒子（水花溅射）。因为SDF包含了角色肩膀、帽沿、手臂等所有朝上表面的几何信息，雨水会在这些位置自然堆积流淌，而不会穿透衣物。

**熔岩绕障流动**：在洞穴关卡中，将岩石几何体烘焙为64³ SDF，熔岩粒子的速度场中叠加SDF梯度的反向量（即指向表面内部的方向乘以一个负权重），使粒子在接近岩石时产生切线方向的偏转，模拟液体绕过障碍物的流动行为。配合`Turbulence`扰动节点，最终效果在静态SDF的基础上呈现出动态的有机流动感。

**粒子沿表面吸附**：设定粒子的目标位置为在SDF梯度方向上偏移一个固定距离（如0.05m）的点，通过每帧向该目标位置插值移动，使粒子如同吸附在几何体表面滑行。这种技术常用于能量护盾特效——大量发光粒子沿盾牌表面流动，遮罩在角色和装备的轮廓上。

---

## 常见误区

**误区一：SDF交互可以替代动态物体碰撞**。SDF在VFX Graph中通常是预烘焙的静态数据，无法实时跟随骨骼动画的角色变形。若将一个静态烘焙的人物SDF用于运动中的角色，粒子碰撞参考的形状是T-Pose或初始姿态，与实际动画位置完全不符。Unity在实验性功能中提供了基于Mesh Skinning的运行时SDF更新，但性能开销显著。生产中的常见解法是用简化代理Mesh（Collision Proxy）烘焙SDF，确保静态状态下的合理精度。

**误区二：SDF梯度等于几何法线**。SDF梯度（∇SDF）在表面处确实等于表面法线，但在离表面有一定距离的空间中，梯度方向指向"最近表面点的方向"，并非粒子当前位置所对应三角面的法线。在复杂凹槽几何中，两者方向差异可达90度以上，直接将远离表面的粒子的SDF梯度用作法线进行光照计算会产生错误的高光响应。SDF梯度只适合用于接近表面（距离小于约两个体素尺寸）的粒子的碰撞响应计算。

**误区三：更高分辨率SDF总是更好**。256³的SDF对于一个覆盖范围仅0.5m的小道具来说确实能提供毫米级精度，但在VFX Graph运行时，GPU需要对这个64MB纹理进行三线性插值采样，L2缓存命中率会因纹理体积过大而大幅下降，反而导致采样延迟增加。实践建议是根据SDF包围盒尺寸和所需最小碰撞精度反推所需分辨率，而不是盲目选择最高值。

---

## 知识关联

SDF交互建立在**输出模式**的认知基础上：理解VFX Graph将逻辑分为Initialize、Update、Output三个阶段，才能准确定位SDF碰撞检测应写入Update Context而非Output Context——在Output阶段修改粒子属性不会持久化到下一帧，碰撞反弹的速度修改必须在Update中完成。若将SDF采样节点误放入Output Context，会看到粒子视觉上"接触"表面时没有任何反弹，因为速度数据从未被更新。

学习SDF交互后，下一个进阶概念是**GPU事件**（GPU Event）。SDF碰撞检测是GPU事件最经典的触发源：当粒子通过SDF判断检测到碰撞（`distance < threshold`），可以在同一Update块中触发`Trigger Event On Die`或`Trigger Event Rate`，生成子粒子系统（如水花、火星）。这一机制完全在GPU上完成父子粒子的生灭通信，是VFX Graph相较于传统CPU粒子系统的核心性能优势之一，SDF交互提供了理解GPU事件触发条件的最直观实践场景。