---
id: "vfx-fb-shader"
concept: "序列帧Shader"
domain: "vfx"
subdomain: "flipbook"
subdomain_name: "序列帧特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 序列帧Shader

## 概述

序列帧Shader是一种通过GPU程序控制单张图集纹理播放动画的着色器技术。其核心思路是将多帧动画帧拼合到一张纹理图集（Sprite Sheet）中，Shader在运行时通过动态偏移UV坐标来依次显示每一帧，从而在不切换纹理资源的前提下实现流畅动画播放。

这一技术最早被广泛应用于早期游戏引擎的粒子系统中。Unity的Shuriken粒子系统从Unity 3.5版本起就内置了Texture Sheet Animation模块，其底层正是通过UV偏移Shader实现的。相比CPU端逐帧切换贴图的方案，序列帧Shader将帧序列控制逻辑完全转移到GPU，大幅减少了DrawCall和纹理绑定开销。

序列帧Shader在特效制作中具有不可替代的地位，因为爆炸、烟雾、火焰等特效往往需要逐帧的精细控制，而纯程序化着色器难以还原预渲染动画的细节质感。掌握序列帧Shader的编写，能让特效美术在保持视觉精度的同时，大幅节省运行时的资源消耗。

---

## 核心原理

### UV偏移计算

序列帧Shader的最核心公式是将归一化UV坐标映射到图集中某一格子的局部UV。假设图集为 `M列 × N行`，当前播放帧索引为 `frameIndex`（从0开始），则：

```
// 每帧的UV尺寸
float2 frameSize = float2(1.0 / M, 1.0 / N);

// 当前帧所在的列与行
float col = frameIndex % M;
float row = floor(frameIndex / M);

// 最终UV偏移
float2 uv = (i.uv + float2(col, N - 1 - row)) * frameSize;
```

注意行方向需要翻转（`N - 1 - row`），因为纹理坐标的V轴原点在左下角，而图集通常从左上角开始排列帧。以一张4×4共16帧的图集为例，frameIndex=5时，col=1，row=1，对应图集第二行第二列的格子。

### 帧索引驱动方式

`frameIndex` 可通过两种方式传入Shader：

**时间驱动**：`frameIndex = floor(_Time.y * _FPS) % totalFrames`，其中 `_FPS` 为目标播放帧率，`_Time.y` 为Unity内置的以秒为单位的全局时间。这种方式适用于粒子系统中所有粒子同步播放的场景。

**粒子自定义数据驱动**：通过Particle System的Custom Data模块将每个粒子的生命周期进度（`0~1`）写入顶点数据，Shader读取后乘以 `totalFrames` 得到帧索引。这样每个粒子可以有独立的动画进度，避免所有粒子"踩踏"同一帧。

### 帧间混合（Frame Blending）

基础UV偏移实现的序列帧在帧率较低（如12帧/秒）时会出现明显的跳帧感。帧间混合技术通过同时采样相邻两帧并线性插值来平滑过渡：

```
float blend = frac(_Time.y * _FPS);  // 当前帧内的小数进度
float4 col0 = tex2D(_MainTex, uvFrame0);  // 第N帧
float4 col1 = tex2D(_MainTex, uvFrame1);  // 第N+1帧
float4 finalColor = lerp(col0, col1, blend);
```

混合权重 `blend` 由 `frac()` 函数提取时间的小数部分得到。代价是每个片元需要两次纹理采样，在移动端需谨慎使用。

### UV裁剪与边界限制

当图集格子排列不满（例如总帧数为14，但4×4图集有16格，末尾两格为空）时，需在Shader中对 `frameIndex` 做截断：`frameIndex = min(frameIndex, totalFrames - 1)`。此外，单帧UV若超出 `[0, frameSize]` 范围会采样到相邻格子，因此必须确保输入UV本身已归一化到 `[0, 1]`，或在偏移前用 `frac(i.uv)` 强制取小数部分。

---

## 实际应用

**爆炸特效**：一张典型的爆炸序列帧图集通常为8×8共64帧，每帧512×512像素，整张图集为4096×4096。Shader以24FPS播放，完整动画持续约2.67秒。通过粒子Custom Data传入 `normalizedAge`（粒子归一化年龄），每个爆炸粒子从诞生到消亡恰好播完全部64帧。

**UI特效循环动画**：技能图标的循环光效通常使用4×4的16帧图集，Shader采用时间驱动方式，`_FPS` 设为8，循环周期为2秒。由于是UI元素，可以启用帧间混合以获得更平滑的视觉效果，移动端性能开销在可接受范围内。

**多通道序列帧**：高品质特效中，图集的RGB通道存储颜色信息，Alpha通道存储透明遮罩。Shader分别对同一UV坐标采样后，将RGB与自发光颜色相乘，Alpha用于控制透明度，实现颜色与形状独立控制的灵活合成效果。

---

## 常见误区

**误区一：忽略行方向翻转**
许多初学者直接用 `row = floor(frameIndex / M)` 而不做翻转，导致动画从图集底部开始播放，画面倒序显示。正确做法是计算 `N - 1 - row` 作为V轴偏移，或者在导出图集时确认第一帧位于左上角并与公式对应。

**误区二：`_Time.y` 在多粒子场景产生同步问题**
使用全局 `_Time.y` 驱动帧索引时，同一时刻生成的所有粒子会完全同步播放，形成"齐步走"的不自然感。修复方案是在Custom Data中注入每个粒子的随机偏移量 `randomOffset`，在Shader中计算 `frameIndex = floor((_Time.y + randomOffset) * _FPS) % totalFrames`。

**误区三：混淆帧数与图集格子数**
当总帧数不等于图集格子总数时（如14帧填入4×4图集），若不做 `min` 截断，Shader会循环采样到空白格子，出现透明帧闪烁。部分开发者错误地将 `M * N` 当做总帧数传入，正确的做法是单独维护 `_TotalFrames` 参数并与实际动画帧数保持一致。

---

## 知识关联

**前置概念——扭曲序列帧**：扭曲序列帧在序列帧Shader的基础上叠加了一张扰动纹理对UV进行偏移，其偏移量公式为 `distortedUV = frameUV + (distortTex.rg * 2 - 1) * _DistortStrength`。学习序列帧Shader的UV偏移计算逻辑，是理解扭曲偏移为何要叠加在"已经偏移后的帧UV"而非原始UV上的关键基础。

**后续概念——序列帧优化**：掌握序列帧Shader的基本编写之后，可进一步学习图集压缩格式选取（ASTC 4×4 vs ETC2对Alpha通道的不同处理）、GPU Instancing与序列帧结合的批处理优化，以及如何利用Mipmap裁剪策略减少图集纹理的内存占用。

**后续概念——UV滚动**：UV滚动是序列帧Shader的降维简化版，适用于流水、岩浆等连续纹理的动画；而序列帧Shader处理的是离散帧跳转。两者的UV操作方式有本质区别：滚动是对整张纹理做连续平移，序列帧是在图集内做离散步进跳转，理解二者的公式差异有助于在项目中准确选型。