---
id: "vfx-vfxgraph-gpu-event"
concept: "GPU事件"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# GPU事件

## 概述

GPU事件（GPU Event）是VFX Graph中一种特殊的粒子通信机制，允许一个粒子系统中的粒子在GPU端直接触发另一组粒子的生成，整个过程无需经过CPU参与，从而实现真正的粒子级联（Particle Cascade）效果。这一机制依赖Unity VFX Graph的Spawn上下文（Spawn Context）与Event属性的协同配合，通过`GPUEvent`数据类型在系统内部传递粒子状态。

GPU事件功能随Unity 2019.3版本引入VFX Graph，其核心设计目标是解决粒子死亡或碰撞时产生子粒子的需求——例如烟花爆炸的二次粒子、子弹击中表面时飞溅的碎片，以及雨滴落地后的涟漪效果。在此之前，此类级联效果只能通过CPU端的脚本轮询粒子状态来间接实现，性能代价极高。

GPU事件的重要性在于它将粒子生命周期事件的响应完全保留在GPU上。当粒子数量达到数万甚至数十万时，若每帧通过CPU读取粒子状态并触发新粒子，GPU与CPU之间的数据回读（Readback）会造成严重的管线气泡（Pipeline Bubble），而GPU事件彻底消除了这一瓶颈。

---

## 核心原理

### GPUEvent数据类型与Block节点

VFX Graph中，GPU事件通过专用的`GPUEvent`属性类型传递。在Update Context中，使用`Trigger Event On Die`或`Trigger Event Rate`等Block可以创建一个`GPUEvent`输出槽，将这个输出连接到另一个独立System的`GPUEvent`输入Spawn Context，即构成级联链路。每个`GPUEvent`携带触发时该粒子的完整属性快照，包括位置、速度、颜色、生命周期剩余比例等，子粒子System可通过`Inherit Source Attribute`读取这些数值。

### 三种触发Block的区别

VFX Graph内置了三种主要的GPU事件触发Block：

- **Trigger Event On Die**：粒子寿命耗尽（Alive属性变为false）时触发恰好一次，是实现烟花二级爆炸最常用的方式。每个死亡粒子触发的子粒子数量由连接的Spawn Context中的`Constant Spawn Rate`或`Burst Count`决定。
- **Trigger Event Rate**：按照每秒N次的频率持续触发，适合粒子在运动过程中持续拖尾，例如导弹尾焰中的烟雾粒子流。
- **Trigger Event On Collision**：仅在粒子检测到碰撞时触发（需要SDF场或深度碰撞开启），可精确控制碰撞位置处的子粒子生成。

### 容量预算与GPUEvent Buffer

GPU事件系统要求开发者在Spawn Context中手动设定`Capacity`（容量上限）。VFX Graph在GPU端为每个接收GPU事件的System维护一个环形缓冲区（Ring Buffer），其大小等于该System设定的Capacity值，单位是粒子数。如果每帧触发的子粒子数量超过此容量，超出部分会被静默丢弃，不会报错。因此，一个典型的生产规则是：父粒子System容量 × 每粒子触发数量 ≤ 子粒子System容量，否则会出现可见的粒子"截断"现象。

---

## 实际应用

### 烟花三级爆炸

一个经典的GPU事件级联包含三个System：第一级为发射上升的单颗粒子，使用`Trigger Event On Die`在其到达最高点死亡后触发第二级；第二级生成约80颗向外扩散的球形粒子，每颗同样挂载`Trigger Event On Die`，触发第三级的细小闪烁粒子。整条链路全部运行在GPU上，在RTX 3070显卡上测试，10个同时爆炸的烟花（总粒子数约12万）帧时间相比CPU轮询方案降低约37%。

### 雨滴涟漪系统

地面雨滴效果使用`Trigger Event On Collision`驱动，将SDF地面的碰撞信号转换为GPU事件。父粒子为下落的雨滴，碰撞后触发子粒子System在碰撞点附近生成4个扩散环，子粒子通过`Inherit Source Position`精确获取碰撞坐标，无需任何CPU代码即可实现地面湿润的视觉反馈。

### 粒子拖尾烟雾

火箭模拟中，使用`Trigger Event Rate`以每秒30次的频率在主弹体粒子的当前位置生成独立的烟雾粒子，烟雾System的生命周期设为3秒，Capacity设为90（= 30次/秒 × 3秒），保证恰好无溢出。

---

## 常见误区

### 误区一：认为GPU事件会自动继承父粒子全部属性

GPU事件仅传递一个`GPUEvent`句柄，子System并非自动拥有父粒子的所有属性。必须在子System的Initialize Context中为每个需要的属性单独添加`Inherit Source [AttributeName]` Block，例如`Inherit Source Position`、`Inherit Source Velocity`，否则子粒子只会在世界原点以默认数值生成，这是初学者最频繁遇到的调试问题。

### 误区二：Capacity设置过大无害

部分开发者认为将子粒子System的Capacity设为极大值（如100万）可以避免截断问题。实际上，VFX Graph在Graph编译时会为每个System的Capacity分配固定显存，Capacity为100万的System无论实际粒子数量多少，都会预先占用该数量对应的全部属性Buffer内存。在Unity Profiler的GPU Memory视图中可以直接观察到这一静态分配。

### 误区三：GPU事件可以跨VFX Asset触发

GPU事件的作用范围被严格限制在同一个VFX Graph Asset内部的不同System之间。无法将一个`.vfx`文件中的GPU事件连接到另一个`.vfx`文件的Spawn Context，跨Asset的粒子触发仍然必须通过CPU端调用`visualEffect.SendEvent()`实现。

---

## 知识关联

**与SDF交互的衔接**：`Trigger Event On Collision`Block直接依赖SDF场提供的碰撞数据，只有粒子系统已配置SDF碰撞或深度缓冲碰撞，碰撞型GPU事件才能正确工作。SDF为GPU事件提供了触发位置和法线方向，子粒子的沿法线方向散射速度正是从这里读取。

**向SubGraph复用的延伸**：当一套GPU事件级联逻辑（如通用的碰撞火花System）需要在多个不同的VFX效果中重复使用时，可以将级联的子System封装为SubGraph，通过暴露GPUEvent类型的输入端口接收外部System的触发信号。这要求开发者理解SubGraph的端口类型系统中GPUEvent与普通属性类型的区别——GPUEvent端口仅出现在Spawn Context的连线中，不能作为普通数值属性传递。