---
id: "cg-screen-space-gi"
concept: "屏幕空间GI"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 屏幕空间全局光照（SSGI）

## 概述

屏幕空间全局光照（Screen Space Global Illumination，SSGI）是一类利用当前帧已渲染的屏幕缓冲数据（深度图、法线图、颜色图）来近似计算场景中漫反射间接光照的实时技术。与离线路径追踪不同，SSGI 完全不访问原始场景几何数据，所有采样工作都在二维图像空间内完成，因此其计算量与场景多边形数量无关，仅受分辨率影响。

SSGI 的直接前身是 2007 年 Crytek 提出的屏幕空间环境光遮蔽（SSAO），但 SSAO 只计算可见性遮蔽，不传递实际光照颜色。2010 年前后，Tobias Ritschel 等人提出屏幕空间方向性遮蔽（SSDO，Screen Space Directional Occlusion），将遮蔽过程扩展为同时采集遮挡物表面的出射辐射度，从而实现"颜色渗透"（Color Bleeding）效果——例如红色地板会将粉红色间接光反射到白色墙壁底部。

SSGI 在实时渲染中弥补了光照贴图无法表现动态物体间接光、而完整光线追踪 GI 在 2010 年代前成本过高的空缺。它以极低的硬件门槛（仅需标准延迟渲染 G-Buffer）实现肉眼可辨的色溢和遮蔽，在 Unreal Engine 4 的 SSGI 实现和多款 AAA 游戏中得到广泛应用。

---

## 核心原理

### G-Buffer 重建世界位置与半球采样

SSGI 的计算入口是 G-Buffer 中存储的每个像素的世界空间法线 **N** 和通过深度值反投影得到的世界空间位置 **P**。对像素 **P** 计算间接照度时，算法在以 **N** 为轴的半球范围内随机产生 **N**（通常 16～64）个采样方向，每个采样方向都被重投影回屏幕空间，读取该位置对应像素的颜色（即出射辐射度 $L_o$）和深度，再根据深度差判断该采样是否实际对 **P** 可见。

半球积分近似公式为：

$$L_{indirect}(\mathbf{P}) \approx \frac{1}{N}\sum_{i=1}^{N} L_o(\mathbf{s}_i)\cdot V(\mathbf{P},\mathbf{s}_i)\cdot \frac{\cos\theta_i}{\text{pdf}(\mathbf{s}_i)}$$

其中 $\mathbf{s}_i$ 是第 $i$ 个采样点的屏幕位置，$V$ 是可见性项（0 或 1），$\theta_i$ 是采样方向与法线的夹角，pdf 为采样概率密度函数（余弦加权时 $\text{pdf}=\cos\theta/\pi$）。

### SSDO 对 SSAO 的扩展：辐射度携带

纯 SSAO 在遮蔽检测时只输出一个标量遮蔽因子，而 SSDO 在同一采样循环中额外读取遮挡物像素的 Albedo 与直接光照颜色，将其乘以 Lambert 余弦项后累加为彩色间接光照。这使得 SSDO 能表现"近场色溢"（Near-Field Color Bleeding）：当物体间距小于采样半径时效果最为明显，典型有效范围约为 0.5～2 米世界空间距离。超出此范围的间接光贡献需要依赖光照探针或 Lumen 等宏观方法补充。

### 时间累积降噪（TAA 集成）

由于每像素采样数通常只有 8～16 个，原始 SSGI 输出噪声极大。现代实现（如 UE4/UE5 的 SSGI Pass）采用时间抗锯齿（TAA）框架进行多帧累积：当前帧使用随机旋转的 Halton 序列采样，与历史帧通过指数移动平均混合（混合权重约 0.1 当前帧 + 0.9 历史帧）。摄像机或物体快速移动时，历史帧重投影失效，需要通过运动向量和深度差裁剪（disocclusion mask）来丢弃无效历史样本，防止拖影。

---

## 实际应用

**室内场景色溢**：在走廊类场景中，红砖墙的颜色会经 SSGI 反弹到地面和对面白色墙壁上，消除纯环境光探针方案下墙面过于"干净"的问题，该效果在屏幕内两侧墙面同时可见时表现最佳。

**动态遮蔽补充**：角色站在彩色地面上时，SSGI 可将地面颜色投射到角色鞋底和腿部，这是光照贴图烘焙方案无法动态响应的。SSDO 在角色与地面接触点附近产生的彩色接触阴影，视觉上比单纯 SSAO 灰色遮蔽更真实。

**Unreal Engine 中的配置**：UE4 后期处理体积中的 `Screen Space GI` 选项默认关闭（因为有 Lumen），但在不支持硬件光线追踪的平台（如主机上的低端模式）上仍作为 GI 回退方案使用，其 `Intensity` 乘数控制间接光强度，典型值为 1.0。

---

## 常见误区

**误区一：SSGI 等同于完整 GI，可以替代光照贴图**
SSGI 只能处理屏幕内可见像素之间的一次间接反弹，屏幕外物体（例如被摄像机裁剪的光源反射面）完全无法贡献间接光。这意味着镜头转向时，间接光照会突然消失（称为"Screen Edge Fade"伪影）。真正的全局光照需要屏外信息，SSGI 无法胜任。

**误区二：SSDO 的采样半径越大效果越好**
当采样核半径（Screen Space Radius）过大时，远距离像素的深度差变化剧烈，大量采样点会被错误地判断为遮挡，导致整个画面出现异常暗斑（Over-Occlusion）。实践中采样半径通常限制在屏幕宽度的 5%～15% 之间，过大的半径需要额外的深度范围阈值（Range Check）来剔除不相关遮挡。

**误区三：TAA 累积能完全消除 SSGI 噪点**
历史帧累积在快速移动或场景灯光突变时会失效，产生"鬼影"（Ghosting）而非噪点。这与 TAA 本身的 disocclusion 检测精度密切相关：若运动向量精度不足（如粒子系统缺少单独的运动向量），SSGI 在粒子后方会出现明显的拖影残留。

---

## 知识关联

**前置：环境光遮蔽（AO）**
SSAO 是 SSGI 的直接前身，理解 SSAO 的半球随机采样、深度比较和模糊降噪流程，是理解 SSGI/SSDO 工作机制的必要基础。SSGI 在 SSAO 的可见性检测步骤上增加了辐射度读取和颜色累积，两者共享同一套 G-Buffer 输入管线。

**后续：间接高光（Indirect Specular）**
SSGI 处理的是漫反射（Lambertian）间接光，而材质粗糙度较低时需要额外的间接高光贡献。屏幕空间反射（SSR）与 SSGI 共享相似的屏幕空间光线步进（Ray Marching）结构，但 SSR 沿镜面反射方向采样，而 SSGI 在整个半球范围内余弦加权采样，两者共同构成屏幕空间完整的间接光照方案。
