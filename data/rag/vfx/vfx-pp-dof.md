---
id: "vfx-pp-dof"
concept: "景深效果"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

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
updated_at: 2026-04-06
---


# 景深效果

## 概述

景深效果（Depth of Field，DoF）是模拟真实摄影镜头焦点特性的后处理渲染技术，其物理根源是几何光学中的弥散圆（Circle of Confusion，CoC）理论。当镜头焦距固定于某一距离时，该距离之外的点光源无法在传感器平面上汇聚为理想点，而是扩散为一个圆形光斑——其半径正比于物体偏离焦平面的距离与光圈直径的乘积。实时渲染通过逐像素计算 CoC 半径，将其映射为可变模糊核（Variable Blur Kernel），从而在帧缓冲区级别复现镜头的浅景深外观。

景深后处理在游戏引擎中的商业化应用可追溯至 2004 年 Valve 的《半条命 2》与 Epic Games 在 Unreal Engine 3（2006 年）中引入的 BokehDOF Pass。2012 年，Jorge Jimenez 等人在 SIGGRAPH 发表"Practical Post-Process Depth of Field"，系统性地提出了基于半分辨率分层合成的实时 DoF 框架，此后成为主流引擎实现的参考基准（Jimenez et al., 2012）。Unreal Engine 5.0（2022 年）进一步将 DiaphragmDOF 系统迁移至 Temporal Super Resolution 管线，以 TAA 的帧间信息弥补单帧散景采样不足的问题。

景深效果的计算复杂度显著高于 Bloom 泛光：Bloom 仅需对全图做固定方向的高斯分离卷积，而 DoF 的模糊核半径随深度连续变化，每像素的采样半径从 0 到最大 CoC（通常 32–64 像素）不等，这使得朴素实现的 ALU 开销与最大 CoC 的平方成正比。

---

## 核心原理

### 弥散圆（Circle of Confusion）的精确计算

CoC 半径的物理公式源自薄透镜模型，完整形式为：

$$
CoC = \left| \frac{A \cdot f \cdot (d - D)}{d \cdot (D - f)} \right|
$$

其中各变量的物理含义如下：
- $A$：光圈直径（mm），等于焦距除以光圈 F 值，即 $A = f / N$
- $f$：镜头焦距（mm），例如 50mm 标准镜、85mm 人像镜
- $d$：被摄物体到镜头的实际物距（mm）
- $D$：对焦距离，即摄影师主动对焦的锐焦平面距离（mm）

以具体数值为例：焦距 $f = 85\text{mm}$，光圈 $F/1.8$（即 $A \approx 47.2\text{mm}$），对焦距离 $D = 2000\text{mm}$（2 米），当背景物体位于 $d = 5000\text{mm}$（5 米）时：

$$
CoC = \left| \frac{47.2 \times 85 \times (5000 - 2000)}{5000 \times (2000 - 85)} \right| \approx \left| \frac{47.2 \times 85 \times 3000}{5000 \times 1915} \right| \approx 1.26\text{mm}
$$

在 35mm 全幅传感器（36mm × 24mm）、输出分辨率 1920 × 1080 的条件下，1.26mm 传感器尺寸对应约 67 像素的屏幕半径，这正是需要施加的模糊半径。

实时引擎通常以归一化值存储 CoC，将其压缩到 $[-1, 1]$：负值表示近景模糊区（Near Field），正值表示远景模糊区（Far Field），$0$ 表示位于焦内清晰区（In-Focus Zone）。Unreal Engine 的 DiaphragmDOF 使用 R16F 格式缓冲区以物理单位（cm）存储原始 CoC，随后除以屏幕半宽换算为 NDC 空间半径。

### 散景形状与 Bokeh 渲染策略

真实镜头的散景形状由光圈叶片数量与叶片曲率决定：6 叶片产生六边形散景，9 叶片接近圆形，完全开圆光圈产生标准圆形散景。实时渲染中存在两条技术路径：

**Gather（聚合）路径**是主流引擎的默认选择。对于每个输出像素 $p$，在以其为中心、半径为 $r = CoC(p)$ 的区域内，对若干采样点做加权平均：

$$
\text{Color}_{out}(p) = \frac{\sum_{i=1}^{N} w_i \cdot \text{Color}(p + \delta_i)}{\sum_{i=1}^{N} w_i}
$$

其中 $\delta_i$ 是散布在 Bokeh 形状轮廓内的偏移向量，$w_i$ 是权重（通常取 $CoC(p + \delta_i)$ 的函数以减少背景泄漏）。Unity HDRP 默认使用 $N = 42$ 个六边形分布的采样点，最大半径限制为 14 像素（半分辨率下等效 28 像素）。

**Scatter（散射）路径**将每个高亮像素视为一个向外扩散的 Sprite：将屏幕上 CoC 超过阈值（通常 $> 4$ 像素）的像素收集到点列表，以 GPU DrawIndirect 渲染为带透明度的多边形 Sprite，Sprite 的形状与大小由该像素的 CoC 值和预定义的 Bokeh 纹理决定。此方法能正确处理高光散景叠加（如夜晚路灯），但点的数量可能达到数十万，仅适合次世代主机或 PC 高质量模式。

### 近景遮挡与分层合成

景深实现中最难处理的问题是**近景模糊渗透**（Near Field Bleeding）：位于焦内的清晰背景，在其前方存在模糊前景时，模糊会错误地向清晰区域扩散，造成"鬼影"（Ghosting）。标准解决方案是三层分离合成流程：

1. **远景层（Far Layer）**：仅处理 $CoC > 0$ 的像素，在半分辨率缓冲区做 Gather 模糊，并将 CoC 值本身作为 Alpha 通道写入。
2. **近景层（Near Layer）**：仅处理 $CoC < 0$ 的像素，在独立半分辨率缓冲区做最大化 CoC 膨胀（Max CoC Dilation），再做 Gather 模糊，使近景模糊边界向外扩展约 2–4 像素，从而在合成时遮住背景像素的边缘伪影。
3. **合成**：先将远景层以 $\alpha_{far}$ 混合到原始清晰图像上，再将近景层以 $\alpha_{near}$（通常取 $\max(0, -CoC/CoC_{max})$）叠加到结果上，最终上采样回全分辨率。

Unreal Engine 5 的 DiaphragmDOF 引入了额外的**前景散射通道**（Foreground Scatter Pass）：对 CoC 绝对值 $> 8$ 像素的近景像素，额外执行一次 Scatter 渲染，将其正确地"堆叠"到中景之上，将近景边缘误差控制在 1 像素以内。

---

## 关键公式与实现代码

以下是 GLSL 实现的简化 Gather DoF 核心着色器，展示了 CoC 计算与圆形采样的基本结构：

```glsl
// 输入：深度缓冲（线性化）、颜色缓冲、DoF 参数
uniform float uFocusDist;   // 对焦距离（世界单位）
uniform float uFocalLen;    // 焦距（mm），如 85.0
uniform float uAperture;    // 光圈直径（mm），如 47.2 (f/1.8)
uniform float uSensorHeight;// 传感器高度（mm），如 24.0
uniform vec2  uResolution;  // 屏幕分辨率，如 (1920, 1080)

// 将线性深度转换为 CoC 归一化半径（[-1, 1] 范围）
float computeCoC(float linearDepth) {
    float d = linearDepth;
    float D = uFocusDist;
    float f = uFocalLen;
    float A = uAperture;
    // 薄透镜 CoC（mm）
    float coc_mm = abs(A * f * (d - D) / (d * (D - f)));
    // 转为屏幕像素半径：(coc_mm / sensorHeight) * screenHeight / 2
    float coc_px = (coc_mm / uSensorHeight) * (uResolution.y * 0.5);
    // 归一化到 [-1, 1]，近景取负值
    float sign = (d < D) ? -1.0 : 1.0;
    return sign * clamp(coc_px / 32.0, 0.0, 1.0); // 最大半径 32px
}

// 六边形分布采样（12 点，近似圆形）
const vec2 BOKEH_KERNEL[12] = vec2[](
    vec2( 0.000,  1.000), vec2( 0.500,  0.866),
    vec2( 0.866,  0.500), vec2( 1.000,  0.000),
    vec2( 0.866, -0.500), vec2( 0.500, -0.866),
    vec2( 0.000, -1.000), vec2(-0.500, -0.866),
    vec2(-0.866, -0.500), vec2(-1.000,  0.000),
    vec2(-0.866,  0.500), vec2(-0.500,  0.866)
);

vec4 dofGather(sampler2D colorTex, sampler2D cocTex, vec2 uv) {
    float centerCoC = abs(texture(cocTex, uv).r);
    float radius = centerCoC * 32.0; // 最大 32px 半径
    vec4 acc = vec4(0.0);
    float totalWeight = 0.0;
    for (int i = 0; i < 12; i++) {
        vec2 offset = BOKEH_KERNEL[i] * radius / uResolution;
        vec2 sampleUV = uv + offset;
        vec4 sampleColor = texture(colorTex, sampleUV);
        float sampleCoC = abs(texture(cocTex, sampleUV).r);
        // 权重：远景采样点的 CoC 越大，贡献越可靠
        float w = clamp(sampleCoC / max(centerCoC, 0.001), 0.0, 1.0);
        acc += sampleColor * w;
        totalWeight += w;
    }
    return acc / max(totalWeight, 0.001);
}
```

上述代码中，`BOKEH_KERNEL` 的 12 个点均匀分布于单位圆上，可替换为六边形顶点坐标以模拟 6 叶片光圈散景。生产级实现（如 Unreal 的 DiaphragmDOF）通常使用 32–64 点的随机旋转核（Blue Noise Jitter），配合 TAA 积累多帧样本，以 12 点的采样成本实现等效 128 点的视觉质量。

---

## 实际应用场景

**电影化过场动画**：在双人对话镜头中，将对焦距离设为主角脸部（约 1.8–2.5 米），焦距模拟 85mm 人像镜，光圈 F/1.4–F/2.0，使背景角色与环境陷入明显的圆形散景模糊，迫使玩家视线集中在说话角色上。《最后的生还者 Part II》（2020，Naughty Dog）的过场动画大量采用此技术，其 DoF 参数随摄像机动画关键帧动态切换，焦点转移时间约 0.3–0.5 秒，模仿摄影师手动拉焦的节奏感。

**准星/UI 聚焦效果**：第一人称射击游戏中，当玩家举枪瞄准时，远景和近景同时产生 CoC 约 4–8 像素的轻微模糊，清晰区间压缩至准星前方 10–30 米，强化瞄准准星的视觉突出性。《使命召唤：现代战争》（2019）的 ADS 状态下即采用此策略，CoC 过渡动画时长约 4 帧（66ms @ 60fps），避免产生晕眩感。

**手机游戏的低成本近似**：移动端受限于 ALU 预算，通常以固定半径的高斯模糊（半径 4–8 像素）替代精确 CoC 采样，仅对深度超过阈值（如距摄像机 50 米以上）的远景区域施加模糊，并使用深度测试