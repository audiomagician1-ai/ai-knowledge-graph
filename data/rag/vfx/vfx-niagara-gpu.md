---
id: "vfx-niagara-gpu"
concept: "GPU模拟"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# GPU模拟

## 概述

GPU模拟（GPU Compute Sim）是Niagara粒子系统中将粒子运算从CPU迁移到GPU上并行执行的计算模式。与CPU模拟每帧只能串行处理数千至数万个粒子不同，GPU模拟利用显卡的数千个着色器核心同时处理粒子，理论上可在单个发射器中支持超过百万量级的粒子，同时保持可接受的帧率。

GPU模拟对应的底层技术是Unreal Engine的Compute Shader管线。Niagara在UE4.20版本（2018年）正式引入GPU Compute Sim选项，取代了旧Cascade系统中有限的GPU Sprite支持。其核心实现是将每个粒子的Update逻辑编译成HLSL Compute Shader，由GPU的CS阶段并行执行，粒子状态数据全程存储在GPU端的结构化缓冲区（StructuredBuffer）中，无需每帧回传CPU，极大降低了总线带宽压力。

在制作需要大规模粒子的特效时——例如沙尘暴、群体火花、流体泡沫——GPU模拟是性能可行性的关键前提。同样的百万粒子场景，CPU模拟往往导致帧率跌至个位数，而GPU模拟在中端显卡上可维持60fps以上。

## 核心原理

### 执行模型：线程组与粒子并行

GPU模拟将粒子数组切分成固定大小的线程组（Thread Group），每个线程对应一个粒子的计算单元。Niagara默认的线程组大小为 **64**（即`[numthreads(64,1,1)]`），这意味着粒子总数会被填充为64的整数倍进行调度。Spawn和Update模块中编写的所有节点逻辑，均被编译为对应的CS入口函数。粒子属性（位置、速度、颜色等）存储在GPU端的`RWStructuredBuffer<float4>`中，每帧直接在GPU内存中原地更新，避免了CPU→GPU的数据上传开销。

### 数据隔离与CPU交互限制

由于粒子数据驻留在GPU，CPU无法在运行时直接读取单个粒子的位置或状态。这导致以下限制在GPU模拟中**不可用**：
- **碰撞事件（Collision Event）的CPU路径**：GPU粒子碰撞需改用Scene Depth Buffer进行屏幕空间深度碰撞，精度受摄像机视角限制，且无法在被遮挡区域产生碰撞。
- **Spawn On Event（基于事件生成）**：GPU模式下粒子死亡事件无法触发另一CPU发射器的Spawn，若需粒子死亡时产生子粒子，必须将子发射器也设为GPU模拟并使用GPU事件（GPU Event）。
- **获取粒子数量（Get Particle Count）到蓝图**：蓝图无法实时获取GPU粒子数量，因读回操作会引发GPU→CPU同步气泡（Stall）。

### 固定边界（Fixed Bounds）的必要性

CPU模拟的粒子可以动态计算包围盒，而GPU粒子的位置数据无法被CPU实时读取，因此必须手动设置**Fixed Bounds**。在Niagara发射器属性面板中，将`Fixed Bounds`勾选并填写合适的Min/Max坐标范围（单位为本地空间厘米）。若Fixed Bounds设置过小，粒子超出范围时会被视锥剔除（Frustum Culling）错误裁剪，导致粒子凭空消失。建议边界至少比粒子运动范围扩大20%作为安全余量。

### 深度碰撞（Depth Buffer Collision）

GPU模拟的碰撞通过采样场景深度图（Scene Depth Texture，格式为`SceneDepth R32`）近似实现。模块`Collision (GPU)`将粒子的世界坐标投影为屏幕UV，采样深度值还原出碰撞位置，再通过法线偏转速度向量。该方法的计算开销约为每粒子**4次纹理采样**，在粒子数量百万级时仍比物理碰撞快数个数量级。但其本质限制在于：摄像机背面或被遮挡的几何体无法参与碰撞判定。

## 实际应用

**沙漠沙尘暴特效**：在《堡垒之夜》等项目的公开拆解中，沙尘暴使用单个GPU模拟发射器维持约800,000个沙粒粒子，结合Deep Buffer Collision使沙粒贴合地表流动，整体GPU开销控制在1.2ms以内（RTX 2070参考值）。CPU模拟同等粒子量需要约40ms，完全不可行。

**流体泡沫模拟**：水面泡沫效果通常将GPU模拟发射器与Simulation Stage配合，粒子在每帧执行多次迭代（Multi-Iteration）来模拟粒子间的排斥力，实现类流体聚集行为。这种工作流必须在GPU模式下进行，因为Simulation Stage本身依赖Compute Shader的多Pass调度。

**大规模群体火花**：锻造、爆炸等工业特效需要数十万个金属火花粒子，每个粒子具有不同的冷却曲线和颜色变化。GPU模拟中用Curve采样模块结合粒子年龄（Normalized Age）更新颜色，所有计算在GPU内完成，对CPU帧时间贡献几乎为零。

## 常见误区

**误区一：GPU模拟总是比CPU模拟更快**
粒子数量较少时（通常低于5,000个），GPU模拟的Dispatch开销（Compute Shader调度的固定成本约0.05ms）反而使其慢于CPU模拟。GPU模拟的优势在粒子数超过约50,000个后才开始明显体现。盲目将所有发射器切换为GPU模拟会增加低粒子数特效的额外开销。

**误区二：只需切换为GPU模拟，其余设置不变**
将发射器模拟目标从CPU切换为GPU后，所有使用了`Actor`或`Component`引用的模块将失效，因为GPU无法持有对象引用。同时，未设置Fixed Bounds会导致整个粒子系统被剔除或随机闪烁。切换后必须逐一检查模块兼容性并配置Fixed Bounds。

**误区三：GPU粒子数越多越好，可以无限堆砌**
GPU显存（VRAM）对粒子属性缓冲区有硬性上限。每个粒子属性占用4字节（float）至16字节（float4），100万个粒子若有20个float4属性，则需要约**76.3MB VRAM**仅用于粒子数据。移动端显卡的VRAM往往只有1-2GB，大规模粒子会挤占用于贴图和几何体的显存，造成整体性能劣化。

## 知识关联

GPU模拟建立在**Mesh粒子**的基础之上：Mesh粒子阶段已掌握粒子渲染的各种形态（Sprite、Ribbon、Mesh），GPU模拟则是对这些粒子类型的执行后端的替换——Mesh粒子在GPU模式下依然渲染为Mesh，但更新计算迁移到Compute Shader中。理解Mesh粒子的属性系统（位置、方向、缩放分别存于独立Buffer）有助于理解GPU端数据布局。

学习GPU模拟之后，自然引出**Simulation Stage**：Simulation Stage是GPU模拟的扩展功能，允许在单帧内对粒子系统执行多个顺序的Compute Pass，实现粒子间交互（如格网采样、流体模拟）。Simulation Stage只在GPU模拟目标下可用，是构建高级物理特效的前置能力。另一个后续方向是**GPU Profile**：使用Unreal Insights或RenderDoc的Compute Shader时间戳，定位GPU模拟中耗时过高的模块，是性能优化闭环的最终工具。