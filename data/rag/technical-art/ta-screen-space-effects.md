---
id: "ta-screen-space-effects"
concept: "屏幕空间效果"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.8
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

# 屏幕空间效果

## 概述

屏幕空间效果（Screen Space Effects）是一类在光栅化渲染管线的后处理阶段执行的Shader技术，其核心特征是**所有计算仅依赖当前帧的屏幕像素数据**（颜色缓冲、深度缓冲、法线缓冲），而不追溯场景中不可见区域的几何信息。这类技术包括屏幕空间环境光遮蔽（SSAO）、屏幕空间反射（SSR）、屏幕空间次表面散射（SSSSS）等。由于输入数据量恒定为屏幕分辨率×缓冲通道数，这类效果的性能开销与场景复杂度解耦，适合实时渲染。

SSAO由Crytek在2007年随《孤岛危机》首次在商业游戏中落地，是屏幕空间效果普及的起点。其思路借鉴了离线渲染的环境光遮蔽积分，但将射线追踪替换为在深度缓冲中随机采样邻域点，把原本数分钟的计算压缩到单帧16ms预算内。这一取舍思路——用屏幕空间近似换取实时性——成为后续SSR、SSSSS等技术的共同设计哲学。

理解屏幕空间效果对技术美术的意义在于：这类Shader几乎是所有现代AAA游戏视觉质量的"最后一公里"。消除了SSAO的画面会丧失凹陷细节的立体感；缺少SSR的光滑地面会变成哑光材质。同时，屏幕空间效果的共同局限（屏幕边缘失真、运动拖影）决定了美术在资产制作和镜头运动设计上必须与之配合。

---

## 核心原理

### SSAO：基于半球采样的遮蔽估算

SSAO的数学核心是对每个像素点 $p$ 在切线空间半球内采样 $N$（通常16～64）个偏移点，统计其中深度大于深度缓冲值的比例作为遮蔽因子 $A$：

$$A(p) = 1 - \frac{1}{N}\sum_{i=1}^{N} \mathbf{1}[depth(p + r_i) > depth_{buffer}(p + r_i)]$$

其中 $r_i$ 是在半球内随机分布的偏移向量，偏移半径通常设为0.5～2个世界空间单位。为避免大面积均匀噪声，采样向量会与一张4×4的随机旋转纹理（Rotation Noise Texture）进行tile操作，使相邻像素的采样方向不同，再用3×3或5×5的双边模糊（Bilateral Blur）去噪，双边模糊保留深度/法线的不连续边缘，防止遮蔽漏到背景。

### SSR：基于深度缓冲的光线步进

SSR在片元着色器中沿反射方向执行屏幕空间光线步进（Ray Marching）。对于每一步，将世界空间射线转换回NDC坐标，采样深度缓冲判断是否相交。步进方式通常采用**Hierarchical Z（Hi-Z）加速**：预先生成深度缓冲的Mipmap链，粗粒度快速跳过空白区域，在深度变化剧烈处降级到Mip 0精细步进，使步进次数从每像素128步降低到32步左右。

SSR的着色公式需要计算反射射线 $\mathbf{r} = \mathbf{d} - 2(\mathbf{d}\cdot\mathbf{n})\mathbf{n}$（$\mathbf{d}$为视线方向，$\mathbf{n}$为法线），找到交点像素后，将该像素的颜色缓冲值乘以菲涅尔系数（Fresnel）叠加到当前像素的高光层上。粗糙度通过对反射颜色进行模糊（Cone Tracing近似）来模拟非镜面反射。

### SSS（次表面散射）的屏幕空间近似

皮肤、蜡、玉石等材质的次表面散射在屏幕空间的实现称为SSSSS（Separable Subsurface Scattering），由Jorge Jimenez等人在2015年系统化。其思路是将散射剖面（Diffusion Profile）近似为6个高斯核的加权和，在屏幕空间沿水平和垂直方向分两次卷积：

$$I_{sss}(p) = \sum_{k=1}^{6} w_k \cdot \text{GaussianBlur}(I_{diffuse}, \sigma_k)$$

每个高斯核的标准差 $\sigma_k$ 对应不同的散射距离，对皮肤而言典型值范围为0.08～3.0mm（换算到屏幕空间时需除以深度缓冲的线性深度以保持世界空间一致性）。这个方法的Pass数固定为2，性能远优于Ray Marching类SSS方案。

---

## 实际应用

**Unity URP中的SSAO配置**：URP的SSAO Renderer Feature提供Intensity（强度）、Radius（采样半径）、Direct Lighting Strength三个核心参数。将Radius设置过大（超过场景单位的10%）会产生"光晕"（Halo）伪影——在角色头顶出现明显的暗环，这是采样球超出几何体边界采到背景深度的典型错误。美术验收时需在白色背景灯光场景下专门检查此伪影。

**SSR在水面材质中的应用**：水面SSR的步进距离上限通常设置为屏幕宽度的50%（如1920×1080时约960像素步进距离），超出范围的反射用Reflection Probe的Cubemap兜底。SSR Fade参数控制靠近屏幕边缘时反射信息的渐隐距离，建议设为10%～20%屏幕宽度，防止边缘硬切换到Cubemap时产生跳变。

**SSSSS在角色皮肤渲染中的应用**：使用SSSSS时，Diffusion Profile的散射颜色应针对不同种族肤色调整。亚洲肤色皮下血管层的散射颜色偏红（约`#C8402A`），高加索肤色散射更深、偏暗红。散射强度由遮罩贴图控制——鼻翼、耳廓等较薄区域遮罩值应接近1.0，额头等厚实区域降至0.4～0.6，避免全脸均匀散射导致的"蜡感"。

---

## 常见误区

**误区一：SSAO应该叠加到整个光照结果上**
SSAO代表的是间接光（环境光）被遮蔽的程度，只应与间接光照分量相乘，而不应与直接光的漫反射或高光相乘。若直接将AO贴图乘到最终颜色上，会导致凹槽在强直射光下也变黑，产生物理上不正确的脏旧感。正确做法是在光照方程中：`Final = DirectLight + AmbientLight × AO`。

**误区二：SSR能替代所有环境反射**
SSR无法处理屏幕外的内容——当反射物体移出画面或被遮挡时，SSR交点射线无法找到有效像素，必须回退到Reflection Probe或Sky Reflection。许多项目在光滑金属球体上切换镜头时出现反射内容"闪烁消失"的问题，根本原因正是过度依赖SSR而未配置兜底方案。典型的健壮实现是：SSR混合权重 = SSR置信度（命中率），`1 - 置信度`权重分配给Cubemap。

**误区三：屏幕空间效果与TAA（时间抗锯齿）顺序无关**
SSAO、SSR等效果必须在TAA之前执行，或使用TAA专用的时域累积Pass单独处理其噪点。若将含随机噪点的SSAO结果送入TAA，TAA的历史帧混合会引发"鬼影"（Ghosting），在运动物体周围产生持续的暗色拖尾。Unity HDRP通过将SSAO的时域滤波独立出来（GTAO算法的时域累积步骤）解决了这一冲突。

---

## 知识关联

屏幕空间效果的实现入口是**片元着色器**（Fragment Shader）的后处理Pass——从G-Buffer中读取深度纹理、法线纹理和颜色纹理，均使用`tex2D`或`SAMPLE_TEXTURE2D`在片元着色器中完成采样，因此片元着色器的UV坐标变换、纹理采样精度和精度限定符（`mediump`/`highp`）的选择直接影响屏幕空间效果的质量。

与G-Buffer的关系：SSAO和SSR都依赖**重建世界空间位置**，该重建需要深度缓冲值配合逆投影矩阵完成：`worldPos = mul(InvVP, float4(uv * 2 - 1, depth, 1))`。如果项目的深度缓冲精度不足（如使用16位深度格式），远景的SSAO会出现明显的分层带状伪影（Z-fighting-like banding），这是深度缓冲精度与屏幕空间效果之间的直接依赖关系。

屏幕空间效果作为实时渲染中全局光照（GI）的轻量近似方案，其下一阶段的技术演进方向是**光线追踪**（Ray Tracing）——RTX硬件光线追踪RTAO