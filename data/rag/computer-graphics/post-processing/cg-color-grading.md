---
id: "cg-color-grading"
concept: "色彩分级"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 2
is_milestone: false
tags: ["艺术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 色彩分级

## 概述

色彩分级（Color Grading）是在图像渲染或拍摄完成后，通过数学变换对每个像素的颜色进行系统性调整的后处理技术。它不同于色彩校正（Color Correction）的目标——色彩校正旨在修复错误（如白平衡偏差），而色彩分级的目的是主动创造视觉风格，例如电影级的青橙色调（Teal & Orange）或复古褪色效果。在实时渲染管线中，色彩分级通常作为色调映射（Tonemapping）之后的最后一道屏幕空间处理步骤。

色彩分级技术在电影工业中有悠久历史，最早以光化学方式在胶片冲洗阶段完成。数字化时代以 DaVinci Resolve（1984年由Resolve Technology推出前身）为代表的调色软件将其推广为标准工作流程。2003年，美国电影摄影师协会（ASC）联合欧洲广播联盟（EBU）制定了 ASC-CDL 规范，将色彩分级中最基础的线性调整操作标准化为跨平台的可交换格式。在游戏引擎领域，Unreal Engine 4 和 Unity 的后处理栈均内置了 LUT 与 CDL 参数支持。

---

## 核心原理

### LUT 色彩查找表

LUT（Look-Up Table，查找表）是色彩分级最主要的实现工具。其原理是将输入颜色空间离散化为一个三维网格，每个格点存储对应的输出颜色值，渲染时对输入像素的 RGB 值进行三线性插值（Trilinear Interpolation）以获取输出颜色。

游戏引擎中最常见的 LUT 格式是 **17³ 或 33³ 的三维纹理**，即沿红、绿、蓝三个轴各分为 17 或 33 个采样点，存储为一张 $N^2 \times N$ 像素的二维图集（Unwrapped 3D LUT）。17³ LUT 仅需一张 $289 \times 17$ 像素的纹理，却能以极低带宽代价覆盖几乎任意复杂的色彩变换，包括无法用解析公式描述的风格化映射。

LUT 的插值公式为：

$$C_{out} = \text{lerp}\left(\text{lerp}\left(\text{lerp}(C_{000}, C_{100}, t_r),\ \text{lerp}(C_{010}, C_{110}, t_r),\ t_g\right),\ \text{lerp}\left(\text{lerp}(C_{001}, C_{101}, t_r),\ \text{lerp}(C_{011}, C_{111}, t_r),\ t_g\right),\ t_b\right)$$

其中 $t_r, t_g, t_b$ 是输入像素颜色在 LUT 网格中的小数坐标，$C_{ijk}$ 是最邻近的 8 个格点颜色值。

### ASC-CDL 色彩校正决策列表

ASC-CDL（Color Decision List）定义了一套标准化的线性色彩调整参数，分三个有序操作：

1. **Slope（斜率）**：乘以 $S$，控制整体亮度和对比度增益
2. **Offset（偏移）**：加上 $O$，提升或压低暗部
3. **Power（幂次）**：取 $P$ 次幂，调整伽马（中间调）

完整的 ASC-CDL 变换公式为：

$$C_{out} = \text{clamp}(C_{in} \times S + O)^P$$

每个参数均独立作用于 R、G、B 三个通道，因此完整的 CDL 参数组由 **9 个浮点数**构成（每通道各一组 $S, O, P$），另加一个可选的 **Saturation（饱和度）** 参数，共 10 个值。CDL 的设计决策是牺牲灵活性换取跨软件一致性——同一组 CDL 参数在达芬奇、Nuke、Premiere 中产生完全相同的结果。

### LUT 与 CDL 的管线组合

在实际渲染管线中，LUT 与 CDL 通常以"CDL 前置 + LUT 后置"的方式组合：先用 CDL 进行场景级的曝光调整（线性空间），再用 LUT 施加整体风格映射（sRGB或伽马空间）。Unreal Engine 的 **Combined LUT** 机制会在运行时将场景中所有后处理体积（Post Process Volume）的 LUT 混合成单张纹理，从而将多次 LUT 采样合并为一次 GPU 采样，节省显存带宽。

---

## 实际应用

**游戏风格化色调**：《赛博朋克 2077》的霓虹色调通过自定义 LUT 实现，将蓝色阴影和品红高光分别映射到特定色相，营造赛博朋克美学；这类非单调的色相偏移无法用 CDL 参数表达，只能依赖 LUT 的任意映射能力。

**跨平台色彩一致性**：在影视与游戏混合制作管线中（如《最后生还者》的电视剧改编素材），调色师使用 ASC-CDL 导出 `.cdl` 或 `.cc` XML 文件，游戏引擎读取同一组参数并直接复现相同的色彩风格，避免手动比对误差。

**LUT 烘焙工作流**：美术人员在 DaVinci Resolve 中调出目标色调，导出 `.cube` 格式的三维 LUT 文件（Cube LUT 格式由 Adobe 于 2013 年规范化），再将其导入 Unreal Engine 或 Unity 的后处理材质，实现所见即所得的调色迁移。33³ 的 `.cube` 文件包含 35937 行颜色数据，精度足以表达细腻的肤色渐变。

---

## 常见误区

**误区一：LUT 应用在线性空间**
许多初学者直接将 LUT 挂在 HDR 渲染缓冲区之后，在线性光照空间采样 LUT。这是错误的——标准 LUT 是在**伽马或 sRGB 空间**（即色调映射之后）设计的，在线性空间中其颜色映射关系完全失效，会产生高光区域颜色失真。正确顺序必须是：HDR → 色调映射 → 色彩分级（LUT）。

**误区二：17³ LUT 精度不足，应一律使用 65³**
17³ LUT 对于大多数平滑渐变的色彩风格完全够用，三线性插值误差通常低于人眼可分辨阈值（低于 1/255 的量化误差）。只有当 LUT 包含**急剧折点**（如选择性色相旋转超过 60°）时，才需要升级到 33³ 或 65³ 以减少插值带状伪影（Banding Artifact）。盲目提高 LUT 分辨率只会增加纹理缓存压力。

**误区三：CDL 的 Power 参数等同于 Gamma 校正**
CDL 的 Power 操作 $C^P$ 作用于经过 Slope 和 Offset 处理后的值，其输入范围可能超出 [0,1]（尤其是 Offset 为正时），此时对负数取非整数幂会产生未定义行为。而标准 Gamma 校正假定输入严格在 [0,1] 范围内。这一差异导致在高对比场景下，CDL Power 与 Gamma 的视觉效果在暗部有明显区别。

---

## 知识关联

**前置依赖——色调映射**：色调映射将 HDR 线性空间压缩至 [0,1] 的显示范围，是色彩分级的必要前提。若跳过色调映射直接分级，LUT 的颜色样本会被 HDR 高光值（如 5.0、20.0）的插值外推破坏，产生颜色溢出。ACES 色调映射流程（Academy Color Encoding System）在输出前已内置部分胶片感色彩偏移，需要与色彩分级的 LUT 区分职责，避免重复施加暖色偏移。

**横向关联——颜色空间转换**：在应用 CDL 参数时，必须明确参数所在的颜色空间（Log C、Rec.709、线性 sRGB），CDL 的设计假定在**线性或 Log 空间**中操作。将针对 Log 素材标定的 CDL 参数直接用于 sRGB 渲染输出，会导致 Offset 偏移量在视觉感知上偏重，因为 sRGB 的暗部编码密度远低于 Log 曲线。