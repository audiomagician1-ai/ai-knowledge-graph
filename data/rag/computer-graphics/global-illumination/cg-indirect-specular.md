---
id: "cg-indirect-specular"
concept: "间接高光"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 间接高光

## 概述

间接高光（Indirect Specular）是全局光照渲染方程中专门描述镜面反射类光线经过环境间接传播后照射到表面的光照分量。与漫反射间接光照（Indirect Diffuse）不同，间接高光对表面粗糙度（Roughness）极为敏感：当粗糙度接近 0 时，间接高光呈现几乎完美的镜像反射；当粗糙度增大至 0.6 以上时，反射信号逐渐扩散模糊，高光波瓣（Specular Lobe）宽度从近似 delta 函数膨胀为覆盖半球的宽分布，此时与漫反射间接光照在视觉上趋于混合。

物理上，间接高光遵循渲染方程中的镜面 BRDF 项，工业界主流选择 Cook-Torrance 模型，其菲涅尔项 $F$、法线分布函数 $D$（常用 GGX/Trowbridge-Reitz）以及几何遮蔽项 $G$（常用 Smith GGX）共同决定了反射的能量分布。缺失间接高光时，金属材质（metallic = 1）会因漫反射分量趋近于零而呈现"灰塑料感"，这是因为金属的视觉特征几乎完全由镜面反射承载。

早期实时渲染主要依赖预烘焙的反射探针（Reflection Probe）或立方体贴图（Cubemap）来近似间接高光，但这类方案无法反映场景动态变化。2011 年前后，基于屏幕空间的实时技术开始兴起，屏幕空间反射（Screen Space Reflection，SSR）成为主流方案，被广泛应用于《杀戮地带：暗影坠落》（Killzone: Shadow Fall，2013）、《地平线：黎明时分》（Horizon: Zero Dawn，2017）、《赛博朋克 2077》等主机及 PC 游戏中。关于 SSR 技术细节的奠基性介绍可参见 Morgan McGuire 等人的论文 *Efficient GPU Screen-Space Ray Tracing*（McGuire & Mara, 2014），以及 GDC 2015 上 Yasin Uludag 发表的 *Hi-Z Screen-Space Cone-Traced Reflections* 演讲。

---

## 核心原理

### 屏幕空间反射（SSR）的光线步进

SSR 的核心思路是在屏幕空间内对反射光线执行光线步进（Ray Marching）。设 G-Buffer 中存储的世界空间法线为 $\mathbf{N}$，归一化的摄像机观察方向（指向摄像机）为 $\mathbf{V}$，则反射方向为：

$$\mathbf{R} = 2(\mathbf{N} \cdot \mathbf{V})\mathbf{N} - \mathbf{V}$$

将起始点 $\mathbf{P}_0$（当前像素的世界坐标）与方向 $\mathbf{R}$ 构成射线，逐步将射线上的采样点 $\mathbf{P}_i = \mathbf{P}_0 + t_i \mathbf{R}$ 投影回裁剪空间并变换为屏幕 UV 坐标，与深度缓冲（Depth Buffer）中存储的场景深度比较，判断是否命中几何体。

朴素的线性步进实现每条反射射线需要 64～128 次深度采样，在分辨率为 1920×1080 的帧下开销极大。工业实践中普遍采用**分层 Z 步进（Hi-Z Tracing）**策略（Uludag, GDC 2015）：预先构建场景深度的 Mipmap 层级（每层取 2×2 区域的最小深度，即 Min-Z Pyramid），步进时优先在较粗糙的层级上快速跨越空白区域，仅在检测到潜在交叉时才细化到完整精度。该优化将平均步进次数压缩至约 16～32 步，性能提升约 3～5 倍。

命中判定条件：当采样深度值 $d_\text{scene}$ 满足 $d_\text{scene} < d_\text{ray}$ 且深度差 $|d_\text{ray} - d_\text{scene}| < \epsilon_\text{thickness}$（厚度阈值通常取 0.1～0.5 个世界单位）时，判定为有效命中，取该屏幕 UV 处的颜色作为反射结果。若 $|d_\text{ray} - d_\text{scene}|$ 超过厚度阈值，则跳过（避免将薄平面背面误判为反射命中点）。

下面是一段简化的 HLSL 伪代码，展示线性步进的基本结构：

```hlsl
float3 SSR_RayMarch(float3 rayOrigin, float3 rayDir, 
                    Texture2D depthTex, float4x4 projMatrix,
                    int maxSteps, float stepSize, float thickness)
{
    float3 result = float3(0, 0, 0);
    float3 rayPos = rayOrigin;

    for (int i = 0; i < maxSteps; i++)
    {
        rayPos += rayDir * stepSize;

        // 将射线当前点投影到屏幕空间
        float4 clipPos = mul(projMatrix, float4(rayPos, 1.0));
        float2 screenUV = (clipPos.xy / clipPos.w) * 0.5 + 0.5;

        // 超出屏幕范围则终止
        if (any(screenUV < 0.0) || any(screenUV > 1.0)) break;

        float sceneDepth = depthTex.Sample(sampler, screenUV).r;
        float rayDepth   = clipPos.z / clipPos.w;

        if (sceneDepth < rayDepth && (rayDepth - sceneDepth) < thickness)
        {
            result = ColorBuffer.Sample(sampler, screenUV).rgb;
            break;
        }
    }
    return result;
}
```

### SSR 的局限性与边缘消隐

SSR 存在一个根本性限制：**只能反射当前屏幕中可见的像素**。当反射内容位于屏幕视锥之外、被其他物体遮挡，或反射物本身朝向摄像机背面时，SSR 无法提供有效数据。处理缺失区域的标准做法是以低分辨率的反射探针 Cubemap 作为回退（Fallback），并对 SSR 结果的边缘进行基于置信度的淡出（Fade-Out）。

SSR 贡献权重 $w_\text{SSR}$ 通常由三个子权重相乘得到：

$$w_\text{SSR} = w_\text{border} \cdot w_\text{angle} \cdot w_\text{depth}$$

- $w_\text{border}$：反射命中点 UV 与屏幕边界距离的线性衰减，距边缘 5% 时开始淡出；
- $w_\text{angle}$：反射方向 $\mathbf{R}$ 与摄像机朝向夹角的余弦衰减，防止反射朝向摄像机后方产生的错误内容；
- $w_\text{depth}$：命中点深度差 $(d_\text{ray} - d_\text{scene}) / \epsilon_\text{thickness}$ 的反比，量化深度匹配的可信度。

最终合成公式为：

$$L_\text{reflect} = w_\text{SSR} \cdot L_\text{SSR} + (1 - w_\text{SSR}) \cdot L_\text{Cubemap}$$

### 粗糙度对 SSR 的影响与模糊处理

对于粗糙度 $\alpha > 0$ 的表面，反射结果需要进行模糊处理以模拟高光波瓣的扩散。实现上通常有两种路径：

1. **多重随机采样（Stochastic SSR）**：在 GGX 重要性采样分布下对反射方向抖动，每帧发射 1～4 条随机射线，随后通过时序累积（Temporal Accumulation）滤波降噪。《地平线：黎明时分》采用此方案，在 PS4 上以半分辨率（960×540）运行 SSR，再进行时序重投影上采样（Guerrilla Games, GDC 2017）。

2. **采样后模糊（Post-Blur SSR）**：先以单射线执行 SSR，再根据粗糙度 $\alpha$ 对结果图像进行可变半径的高斯模糊或 Cone-Traced Blur（Uludag 提出的圆锥追踪模糊方案），锥体半角 $\theta \approx \arctan(\alpha)$，在屏幕空间中以该角度采样 SSR 结果的 Mipmap 层，实现开销约为 1～2ms（1080p）。

---

## 平面反射（Planar Reflection）

平面反射是间接高光的另一类实现，专门针对地面、水面、光洁地板等接近水平的平坦表面。其原理是将摄像机以反射平面（定义为法线 $\mathbf{n}$ 和平面上一点 $\mathbf{q}$）为基准做镜像翻转，用翻转后的摄像机矩阵完整渲染一遍场景，所得 RT（Render Target）贴回原平面作为反射纹理。

摄像机位置的镜像变换公式为：

$$\mathbf{C'} = \mathbf{C} - 2[(\mathbf{C} - \mathbf{q}) \cdot \mathbf{n}]\mathbf{n}$$

平面反射的主要代价是**额外的完整渲染 Pass**：若场景本身 Draw Call 数量为 $N$，平面反射额外引入约 $N$ 次绘制，GPU 帧时间几乎翻倍。为控制开销，工业实践中通常采用以下优化：

- **分辨率缩减**：以 1/2 或 1/4 分辨率渲染反射 RT，再通过双线性插值上采样，画质损失有限但性能提升明显；
- **裁剪优化**：使用反射平面作为附加裁剪平面（Oblique Near Clip Plane），剔除平面以上的几何体，减少约 30%～50% 的无效绘制；
- **LOD 降级**：反射 Pass 中强制使用更低 LOD 等级的网格，降低顶点处理压力。

平面反射的质量上限远高于 SSR：它能正确反射屏幕外内容、透明物体（如粒子特效），也不存在 SSR 的步进误差问题。然而，它仅适用于单一平坦反射面，对于曲面或多反射面场景则需要多次额外 Pass，成本急剧上升。

---

## 关键公式汇总

间接高光的完整计算建立在分割求和近似（Split-Sum Approximation）之上，该方法由 Brian Karis 在 *Real Shading in Unreal Engine 4*（Karis, SIGGRAPH 2013）中提出，将镜面反射积分拆分为两个预计算项：

$$L_\text{spec} \approx \underbrace{\int_\Omega L_i(\mathbf{l})\, d\mathbf{l}}_{\text{预滤波环境贴图}} \cdot \underbrace{\int_\Omega f_r(\mathbf{l},\mathbf{v}) \cos\theta_l\, d\mathbf{l}}_{\text{BRDF 积分贴图（LUT）}}$$

第一项对环境辐射 $L_i$ 按粗糙度预滤波，存储在 Mipmap 层级不同的 Cubemap 中（粗糙度 0 对应第 0 级，粗糙度 1 对应最粗糙级）；第二项预计算为以粗糙度 $\alpha$ 和 $\cos\theta_v$（$\mathbf{N}\cdot\mathbf{V}$）为索引的二维 LUT 纹理，存储菲涅尔系数的 $R_0$ 缩放量 $A$ 和偏置量 $B$，在运行时通过 $F_0 \cdot A + B$ 即可重建镜面高光强度。

SSR 与分割求和近似的结合方式：SSR 提供的 $L_\text{SSR}$ 替代预滤波 Cubemap 作为 $L_i$ 的高质量来源，但仍复用 BRDF LUT 的第二积分项，避免重新推导 BRDF 权重。

---

## 实际应用

### 游戏引擎中的典型实现

**Unity HDRP**（High Definition Render Pipeline）中，SSR 以半分辨率运行，默认步进 64 步，时序累积使用指数移动平均（EMA）系数 $\alpha_t = 0.1$（即新帧权重 10%，历史帧 90%），在运动较多的场景中自动降低历史