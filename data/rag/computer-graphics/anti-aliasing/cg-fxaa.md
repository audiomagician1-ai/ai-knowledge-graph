---
id: "cg-fxaa"
concept: "FXAA"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# FXAA（快速近似抗锯齿）

## 概述

FXAA（Fast Approximate Anti-Aliasing，快速近似抗锯齿）是由NVIDIA工程师Timothy Lottes于2009年开发、2011年正式发布的后处理抗锯齿算法（Lottes, 2011, *FXAA whitepaper*, NVIDIA）。与传统MSAA（多重采样抗锯齿）在几何光栅化阶段介入不同，FXAA完全工作在屏幕空间的后处理阶段，直接对已完成渲染的颜色缓冲区（Color Buffer）进行操作，既不访问深度缓冲，也不依赖任何几何网格信息。

FXAA的核心思路分为两条并行路径：**局部对比度驱动的混合因子计算**，以及**沿边缘切线方向的端点搜索与亚像素位移**。两条路径的输出结果取最大值后，用于对颜色缓冲执行一次双线性偏移采样，最终输出经过平滑的像素颜色。整个算法仅需一个全屏后处理Pass，在1080p分辨率下GPU耗时约为0.5~1.0ms（GeForce GTX 580基准），远低于4×MSAA的额外带宽开销。

2011年前后，FXAA 3.11（即最终公开版本）被Unreal Engine 3、Unity、CryEngine等主流引擎迅速采用，成为当时PC与主机游戏的默认抗锯齿方案，其意义在于证明：仅凭对颜色缓冲的局部亮度分析，即可在绝大多数场景下消除可见的几何锯齿，代价是牺牲约5%~15%的纹理高频细节清晰度。

---

## 核心原理

### 亮度计算与边缘检测

FXAA放弃直接在RGB空间计算梯度，改用感知亮度（Luma）值，原因是人眼对亮度边缘远比色度边缘敏感。标准亮度转换公式为：

$$L = 0.299R + 0.587G + 0.114B$$

在FXAA 3.11的实际实现中，为了节省一次点积运算，通常要求渲染管线将上述亮度值预先写入颜色缓冲的Alpha通道（即`gl_FragColor.a = sqrt(dot(color.rgb, vec3(0.299, 0.587, 0.114)))`，注意这里取平方根以近似gamma空间亮度），这样在后处理Pass中直接读取`.a`即可。若不具备修改渲染管线的条件，部分实现退而求其次，直接以绿色通道`G`作为亮度近似，因为在上述权重中绿色占比最高（0.587）。

算法对中心像素 $P$ 及其上（N）、下（S）、左（W）、右（E）四邻像素分别采样亮度，计算局部对比度：

$$C_{local} = L_{max} - L_{min}, \quad L_{max} = \max(L_N, L_S, L_W, L_E, L_P)$$

若满足以下两个阈值条件之一，则跳过该像素（不执行任何混合）：

- $C_{local} < 0.0833$（相对阈值，防止对低对比度区域误处理）
- $C_{local} < 0.0625$（绝对阈值，防止在纯暗区产生噪声放大）

这两个数值直接来自Lottes原版白皮书中的推荐默认值，是FXAA对"质量与性能平衡点"的经验性校准结果。

### 边缘方向判断与局部混合因子

通过对比度检测后，FXAA需判断当前边缘是**水平走向**还是**垂直走向**。判断依据是对比水平梯度之和 $H$ 与垂直梯度之和 $V$：

$$H = |L_N + L_S - 2L_P| \cdot 2 + |L_{NE} + L_{SE} - 2L_E| + |L_{NW} + L_{SW} - 2L_W|$$
$$V = |L_W + L_E - 2L_P| \cdot 2 + |L_{NW} + L_{NE} - 2L_N| + |L_{SW} + L_{SE} - 2L_S|$$

若 $H \geq V$，边缘为水平走向，后续混合方向选取垂直（上下偏移）；反之选取水平偏移。注意这里扩展到了8邻域（包含NE、NW、SE、SW四个角），以提高方向判断的鲁棒性。

局部混合因子（Local Blend Factor）由3×3邻域加权亮度均值与中心亮度之差计算得出：

$$\text{BlendLocal} = \text{smoothstep}\!\left(0, 1,\; \frac{|\bar{L}_{3\times3} - L_P|}{C_{local}}\right)$$

其中 $\bar{L}_{3\times3}$ 按中心权重2、上下左右权重2、四角权重1的方式加权（总权重12），再除以12得到均值。`smoothstep`曲线保证混合因子从0到1之间平滑过渡，避免硬边界。

### 沿边缘的端点搜索与亚像素位移

FXAA最具特色的步骤是**沿边缘切线方向的双向迭代搜索**，用于确定当前像素在边缘线段中的相对位置，进而计算亚像素偏移量。

算法从当前像素出发，沿边缘方向（平行于边缘，即垂直于混合方向）向正负两侧各自步进采样。每步采样点位于边缘法线方向偏移0.5个像素处（即采样边缘两侧颜色的平均值），检查该点亮度与**边缘基准亮度**之差是否超过 $0.25 \times C_{local}$。一旦超过，即认为找到了边缘终点，停止该方向的搜索。

在FXAA 3.11中，默认最大搜索步数为**12步**，可覆盖约±8像素范围；高质量模式下可扩展至**32步**，覆盖约±16像素。每步的步长并非均匀，前4步步长为1像素，第5~6步步长为1.5像素，第7~8步步长为2像素，最后几步步长为4~8像素（加速步进），以节省采样次数。

设正方向搜索到终点的距离为 $d_{pos}$，负方向为 $d_{neg}$，则当前像素距最近端点的归一化位置：

$$\text{SubpixelOffset} = 0.5 - \frac{d_{min}}{d_{pos} + d_{neg}}$$

最终像素颜色通过以下偏移UV采样获得：

$$\text{UV}_{final} = \text{UV}_{center} + \text{SubpixelOffset} \times \text{BlendDir} \times \text{TexelSize}$$

其中 `BlendDir` 为法线方向单位向量，`TexelSize` 为单个像素的UV尺寸。这一偏移驱动的双线性采样等价于在亚像素精度上对边缘两侧颜色进行插值，从而消除锯齿台阶感。

---

## 关键公式与代码实现

以下为FXAA核心步骤的GLSL伪代码片段，展示边缘检测与最终混合的完整逻辑：

```glsl
// FXAA 3.11 核心逻辑（简化版，GLSL）
// 假设颜色缓冲Alpha通道已存储亮度值
uniform sampler2D u_colorTex;
uniform vec2 u_rcpFrame; // = vec2(1.0/width, 1.0/height)

vec4 fxaa(vec2 uv) {
    // 1. 采样中心及4邻域亮度
    float lumaN  = texture(u_colorTex, uv + vec2( 0, -1) * u_rcpFrame).a;
    float lumaS  = texture(u_colorTex, uv + vec2( 0,  1) * u_rcpFrame).a;
    float lumaW  = texture(u_colorTex, uv + vec2(-1,  0) * u_rcpFrame).a;
    float lumaE  = texture(u_colorTex, uv + vec2( 1,  0) * u_rcpFrame).a;
    float lumaM  = texture(u_colorTex, uv).a;

    // 2. 计算局部对比度并进行阈值判断
    float lumaMax = max(max(lumaN, lumaS), max(lumaW, max(lumaE, lumaM)));
    float lumaMin = min(min(lumaN, lumaS), min(lumaW, min(lumaE, lumaM)));
    float lumaRange = lumaMax - lumaMin;
    if (lumaRange < max(0.0833, lumaMax * 0.0625))
        return texture(u_colorTex, uv); // 非边缘，直接返回

    // 3. 判断边缘方向（此处省略8邻域扩展，仅示意）
    float gradH = abs(lumaN + lumaS - 2.0 * lumaM) * 2.0;
    float gradV = abs(lumaW + lumaE - 2.0 * lumaM) * 2.0;
    bool isHorizontal = (gradH >= gradV);
    vec2 blendDir = isHorizontal ? vec2(0, 1) : vec2(1, 0);

    // 4. 沿边缘搜索（简化为固定步数示意，实际为变步长12步）
    float stepLen = isHorizontal ? u_rcpFrame.y : u_rcpFrame.x;
    float lumaEdge = (lumaM + (isHorizontal ? lumaN : lumaW)) * 0.5;
    float threshold = lumaRange * 0.25;
    float dPos = 0.0, dNeg = 0.0;
    for (int i = 1; i <= 12; i++) {
        float sPos = texture(u_colorTex,
            uv + blendDir * float(i) * stepLen + vec2(0.5) * u_rcpFrame).a;
        if (abs(sPos - lumaEdge) > threshold) { dPos = float(i); break; }
    }
    // dNeg 方向类似（省略）

    // 5. 计算亚像素偏移并采样
    float subOffset = 0.5 - dPos / max(dPos + dNeg, 1.0);
    vec2 finalUV = uv + blendDir * subOffset * stepLen;
    return texture(u_colorTex, finalUV);
}
```

上述代码展示了FXAA的完整逻辑骨架。真实的FXAA 3.11源码（可从NVIDIA官方SDK或Lottes在GitHub的仓库获取）在此基础上增加了变步长加速、NE/NW/SE/SW角邻域采样、以及局部混合因子与端点混合因子的`max`合并操作。

---

## 实际应用

**游戏引擎集成**：Unity Post Processing Stack v2的FXAA实现（`FastApproximateAntialiasing.shader`）提供Low、Medium、High三档质量预设，分别对应4次、8次、12次迭代搜索。在1080p分辨率下，Low档GPU耗时约为0.3ms，High档约为0.8ms（测试硬件：GeForce GTX 1060）。Unreal Engine 4则将FXAA集成于`PostProcessTonemap` Pass中，通过`r.FXAA 1`控制台命令启用，其质量固定对应Lottes原版的Quality Preset 12。

**移动端适配**：由于FXAA仅需单次全屏纹理读取（约5~9次采样），在移动GPU（如Adreno 640、Mali-G77）上的带宽消耗远低于4×MSAA（后者需要4倍颜色缓冲存储），因此FXAA至今仍是Android/iOS平台实时渲染的主流抗锯齿选择。

例如，《原神》的移动端低画质模式使用FXAA替代TAA，在Snapdragon 865设备上将抗锯齿Pass的耗时从TAA的2.1ms压缩至0.6ms，帧率提升约8%。

**与TAA的协同使用**：在需要高质量输出的场景（如过场动画渲染），FXAA有时被配置在TAA之后作为"收尾"Pass，专门处理TAA因历史帧混合失效（鬼影区域）而残留的锯齿，即"TAA+FXAA"双Pass方案。

---

## 常见误区

**误区1：FXAA会模糊所有纹理细节**。实际上，FXAA的阈值机制（绝对阈值0.0625）会保护低对比度区域不被处理。真正受影响的纹理是那些具有高频亮度交替（如黑白格子纹理）的情况，此类纹理的高频特征与几何锯齿在亮度域上无法区分，FXAA确实会对其产生轻微模糊，损失约半个像