---
id: "ta-translucent-material"
concept: "半透明材质"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 83.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---




# 半透明材质

## 概述

半透明材质（Translucent/Transparent Material）是用于渲染玻璃、水面、薄纱、烟雾、彩色滤镜等物体的材质类型，其核心特征是光线可以穿透物体表面，同时发生折射、散射或颜色过滤。与不透明材质不同，半透明材质的每个像素颜色不仅取决于自身表面属性，还取决于其背后"背景层"的内容，这迫使渲染管线以完全不同于不透明Pass的方式处理它。

半透明渲染的复杂性在1990年代实时图形早期就已被识别。1992年前后，SGI工作站上的OpenGL最早以`GL_BLEND`接口暴露Alpha混合能力。早期游戏（如1996年的《雷神之锤》）通过简单的Alpha混合将前景色与背景色叠加。现代引擎如Unreal Engine 5的Lumen全局光照体系和Unity HDRP均对半透明物体的光照、折射、次表面散射提供了专用渲染通道。

Alpha混合的核心公式为：

$$C_{out} = C_{src} \times \alpha + C_{dst} \times (1 - \alpha)$$

其中 $C_{src}$ 为前景（半透明物体）颜色，$C_{dst}$ 为背景（已渲染场景）颜色，$\alpha \in [0, 1]$ 表示不透明度（0为完全透明，1为完全不透明）。这一公式看似简单，但它引发了整个渲染管线中最棘手的排序问题和性能开销。

参考文献：Foley, van Dam, Feiner, Hughes《Computer Graphics: Principles and Practice》(3rd ed., Addison-Wesley, 2013) 对Alpha混合的物理基础与合成运算有完整的数学推导。

---

## 核心原理

### Alpha混合与Alpha测试的本质区别

**Alpha测试（Alpha Test / Clip）** 通过一个阈值将像素直接裁掉。在Shader中的典型写法：

```hlsl
// Alpha测试：低于阈值的像素直接丢弃，不参与混合
float alpha = tex2D(_MainTex, uv).a;
clip(alpha - 0.333); // 阈值通常取0.333或0.5
```

被`clip`丢弃的像素不执行后续操作，**仍然写入深度缓冲（Depth Write = On）**，因此不需要排序，可与不透明物体共享同一渲染Pass。叶片、铁丝网、树叶等边缘锯齿可接受的物体适合Alpha测试。

**Alpha混合** 保留 $\alpha$ 的连续中间值，不写入深度缓冲，允许背景透过。玻璃、水、烟雾、薄纱等需要平滑半透明过渡的物体必须使用Alpha混合。两者最关键的区别在于：Alpha测试的性能开销接近不透明材质，而Alpha混合的代价远高于此，主要体现在排序与Overdraw两个维度。

### 透明排序问题（Transparency Sorting）

由于Alpha混合不写入深度缓冲，GPU无法通过深度测试自动确定前后关系。若两个半透明物体A（近）和B（远）渲染顺序颠倒，先渲染A时背景色 $C_{dst}$ 中还没有B的贡献，最终合成颜色将完全错误。

标准解法是**画家算法（Painter's Algorithm）**：每帧按物体到摄像机距离由远及近排序后依次绘制。该算法已知的两类失效场景：

1. **交叉网格（Intersecting Meshes）**：两块玻璃板交叉时，无论整体排序顺序如何，总有一部分像素的前后关系是错的。Unreal Engine 5中可通过开启 `Sort Priority` 偏移值或拆分网格来缓解，但无法完全消除。
2. **大规模粒子系统**：数千个烟雾粒子每帧CPU排序的耗时在低端移动设备上可达2–5ms，占据单帧16.7ms预算的30%以上。GPU粒子系统（如Niagara的GPU模拟模式）通过在GPU侧排序来规避此问题，但需要额外的Indirect Draw调用。

更精确的方案是**与顺序无关的透明（Order-Independent Transparency, OIT）**，代表算法包括：
- **Weighted Blended OIT**（McGuire & Bavoil, 2013）：对所有透明片元按深度加权累加颜色和透明度，误差小于精确排序算法，但计算量仅增加约15%，是目前移动端和主机端最实用的OIT方案。
- **Per-Pixel Linked List OIT**：每像素存储所有片元的链表后精确排序，显存占用随屏幕分辨率和层数线性增长，1080p下4层叠加约消耗约33MB额外显存，仅适用于高端PC。

### 深度写入、深度测试与Overdraw性能

半透明材质的标准渲染状态设置：

| 渲染状态 | 不透明材质 | Alpha测试 | Alpha混合（半透明） |
|---|---|---|---|
| Depth Write | On | On | **Off** |
| Depth Test | On | On | On |
| 渲染队列 | Geometry (2000) | AlphaTest (2450) | Transparent (3000) |

**关闭深度写入但保留深度测试**：深度测试确保半透明物体不渲染到被不透明物体完全遮挡的区域（节省像素着色器开销），关闭深度写入则保证同一半透明区域的多层叠加不互相裁切。

**Overdraw** 是半透明材质的主要性能杀手。假设一块粒子特效覆盖屏幕面积的20%，由10层半透明粒子叠加，屏幕分辨率为1920×1080，则该区域实际执行的片元着色器数量为：

$$N_{shading} = 1920 \times 1080 \times 20\% \times 10 = 4{,}147{,}200 \text{ 次}$$

相当于完整绘制整个屏幕4次。移动平台（如Mali-G77、Adreno 650）由于采用Tile-Based Deferred Rendering（TBDR）架构，带宽消耗随Overdraw线性增长，过高的Overdraw会直接触发带宽瓶颈导致帧率骤降。Unity官方建议移动端粒子系统的Overdraw层数控制在3层以内。

---

## 关键公式与Shader实现

### 预乘Alpha（Premultiplied Alpha）

标准Alpha混合存在一个细节问题：若 $\alpha = 0.5$，颜色 $C_{src} = (1, 0, 0)$（红色），混合后边缘像素会出现"黑边"（Dark Fringe），因为贴图在打包时 RGB 通道在 $\alpha = 0$ 的区域存储了无意义颜色值。

预乘Alpha将颜色提前乘以Alpha存储：$C'_{src} = C_{src} \times \alpha$，混合公式变为：

$$C_{out} = C'_{src} + C_{dst} \times (1 - \alpha)$$

Photoshop、Spine、Unity UI系统均默认使用预乘Alpha。在Shader中启用预乘Alpha时，混合模式须设置为 `Blend One OneMinusSrcAlpha` 而非标准的 `Blend SrcAlpha OneMinusSrcAlpha`。

### 折射（Refraction）与屏幕空间UV偏移

玻璃和水的真实感不仅来自透明度，还来自折射——光线穿过介质时方向改变，背景图像产生扭曲。实时渲染中常用**屏幕空间折射（Screen-Space Refraction）**：对已渲染完成的场景颜色缓冲（Grab Pass / Scene Color）进行UV偏移采样，偏移量由法线贴图驱动：

```hlsl
// 屏幕空间折射示例（HLSL/Unity URP风格）
float2 screenUV = input.positionNDC.xy / input.positionNDC.w;
float3 normalTS = UnpackNormalScale(SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, uv), _NormalScale);

// 将切线空间法线转换为视空间，取XY分量作为偏移
float2 refractionOffset = normalTS.xy * _RefractionStrength * 0.05;

// 采样场景颜色缓冲，折射偏移后的UV
float2 refractedUV = screenUV + refractionOffset;
float4 refractionColor = SAMPLE_TEXTURE2D(_CameraOpaqueTexture, sampler_CameraOpaqueTexture, refractedUV);
```

折射强度 `_RefractionStrength` 对应斯涅尔定律（Snell's Law）中的折射率差值：水的折射率约为1.333，玻璃约为1.5，空气为1.0。

---

## 实际应用

### 玻璃材质

真实感玻璃需要同时处理三个层次：**反射**（菲涅耳反射，视角越平行反射率越高）、**折射**（背景图像扭曲）、**透射颜色**（有色玻璃的Beer-Lambert吸收）。在Unreal Engine 5中，材质的 `Translucency` 模式选择 `Surface TranslucencyVolume` 可获得体积光照支持；`Refraction` 输入连接法线强度即可驱动屏幕空间折射。

例如，制作蓝色葡萄酒瓶玻璃：设置 `BaseColor = (0.05, 0.1, 0.3)`，`Opacity = 0.15`，`Refraction = 1.5`，法线贴图 `NormalScale = 0.3`（细小表面瑕疵），可在约0.3ms的额外GPU时间内实现令人信服的玻璃效果。

### 薄纱与布料

薄纱（如婚纱、窗帘）的半透明效果与玻璃不同，其透射主要由织物纤维的微观结构决定，不发生明显折射。技术上通常使用 **Dithered Transparency（抖动透明）**：用蓝噪声（Blue Noise）贴图对Alpha值进行阈值化，在屏幕像素级别随机决定该像素是否可见，配合TAA（时间抗锯齿）累积多帧后视觉上近似连续透明，同时避免了Alpha混合的排序问题，深度缓冲可正常写入。

### 水面与海洋

水面材质通常将透明层与不透明层分离：水面以下的场景通过 `Scene Depth` 节点计算水深，深度越大透射颜色越深（Beer-Lambert吸收）；水面本身的泡沫、浪花通过Alpha混合或Alpha测试叠加。Unreal Engine 5的水体插件（Water Plugin）使用单独的 `Water Body` Actor，在渲染时优先渲染水下折射Pass，再合并水面反射，从而规避交叉网格排序问题。

---

## 常见误区

### 误区一：所有透明物体都用Alpha混合

大量开发者对树叶、栅栏、头发等物体使用Alpha混合，实际上这些物体边缘硬切割完全可以接受Alpha测试，后者性能开销低40%–60%，且无排序问题。移动端优化的第一步往往是将能用Alpha测试替换的Alpha混合材质全部替换。

### 误区二：Opacity=0的区域不消耗性能

Alpha混合下，即使 $\alpha = 0$（完全透明），像素着色器仍然执行，仍然产生Overdraw。减少半透明粒子Mesh的顶点数量、裁剪掉贴图中大面积 $\alpha = 0$ 的区域（缩小Sprite的包围盒），才是减少Overdraw的根本手段。

### 误区三：折射率可以随意设置

屏幕空间折射的偏移量过大（`_RefractionStrength > 0.2`）会采样到屏幕外或不透明物体后方的颜色，产生明显的撕裂（Artifact）。物理正确的折射率范围：空气→玻璃约1.0→1.5，偏移量建议限制在屏幕宽度的1%–3%以内。

### 误区四：半透明材质可以接收实时阴影

标准Alpha混合半透明材质**无法写入Shadow Map**，因此无法投射自阴影。如果玻璃需要投影彩色光斑（焦散），必须使用专用的透明阴影（Colored/Translucent Shadows）Pass，Unreal Engine 5的 `Cast Translucent Shadows = On` 选项会额外产生一次阴影Pass渲染，GPU耗时增加约0.5–1.5ms。

---

## 知识关联

### 与PBR材质基础的关系

PBR材质基础中的菲涅耳方程