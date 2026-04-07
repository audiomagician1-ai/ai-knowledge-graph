# PBR纹理工作流

## 概述

PBR（Physically Based Rendering，基于物理的渲染）纹理工作流是一套基于真实世界光照物理规律的贴图制作规范，由迪士尼动画工作室的Brent Burley于2012年在SIGGRAPH发表的论文《Physically-Based Shading at Disney》中正式提出并系统化推广。此前，游戏与影视行业长期使用Blinn-Phong等经验光照模型，其参数（如高光指数Shininess）缺乏物理意义，美术师需要大量"凭感觉"调参，在不同光照环境下材质表现严重失真。PBR工作流通过引入物理约束，彻底改变了这一现状。

该工作流的核心物理约束是**能量守恒定律**：材质反射出的光能总量不能超过入射光能总量。漫反射与镜面反射共同消耗入射光能，两者之和必须小于等于1。这一约束在着色器层面通过菲涅耳方程（Fresnel Equation）和微表面理论（Microfacet Theory）共同保证。

PBR工作流目前存在两大主流分支：**Metallic-Roughness（金属度-粗糙度）**工作流和**Specular-Glossiness（高光-光泽度）**工作流。前者由Allegorithmic（现为Adobe旗下）在Substance系列工具中主推，后者则源自Quixel Suite等工具的传统体系。两者在数学上可以相互转换，但贴图通道的组织方式完全不同，选错工作流会导致材质在引擎中出现明显的物理错误。

对3D美术工作者而言，理解这两种工作流的区别至关重要，因为虚幻引擎（Unreal Engine）默认使用Metallic-Roughness，而许多老项目和部分欧洲工作室的流水线仍沿用Specular-Glossiness，贴图交付前必须明确甲方的引擎需求。

> **思考问题**：如果一张Roughness贴图被错误地以sRGB格式导入引擎（而非线性格式），引擎在伽马校正后会对材质粗糙度产生什么影响？为什么这种错误在明亮场景下比在暗部环境中更难被肉眼察觉？当整个光照环境是HDR天光时，这种错误对IBL（Image-Based Lighting）的漫反射与镜面反射分量各自的影响程度是否相同？

---

## 核心原理

### 微表面理论与菲涅耳方程

PBR的物理基础是微表面理论（Microfacet Theory），最早由Torrance和Sparrow于1967年在光学物理领域建立数学框架，后由Cook和Torrance于1982年引入计算机图形学（Cook & Torrance, 1982）。该理论认为，任何真实表面在微观尺度上都由无数朝向各异的微小平面（微表面法线）构成。Roughness值本质上是描述这些微表面法线分布的统计参数，而非直接描述颜色或反射率。

着色器中用于描述镜面反射的完整微表面BRDF（双向反射分布函数）公式为：

$$f_r(\mathbf{v}, \mathbf{l}) = \frac{D(\mathbf{h}, \alpha) \cdot G(\mathbf{v}, \mathbf{l}, \alpha) \cdot F(\mathbf{v}, \mathbf{h}, F_0)}{4(\mathbf{n} \cdot \mathbf{v})(\mathbf{n} \cdot \mathbf{l})}$$

其中：
- $D(\mathbf{h}, \alpha)$：法线分布函数（NDF），描述微表面法线朝向半程向量 $\mathbf{h}$ 的概率密度，$\alpha = \text{Roughness}^2$（UE5采用此平方关系以使视觉线性化，由Brian Karis在2013年UE4白皮书中确立）
- $G(\mathbf{v}, \mathbf{l}, \alpha)$：几何遮蔽函数，描述微表面的自遮挡与自阴影，UE5采用Smith联合遮蔽-阴影函数
- $F(\mathbf{v}, \mathbf{h}, F_0)$：菲涅耳方程，描述反射率随观察角度增大而增大的现象，$F_0$ 为零度入射角时的基础反射率
- $\mathbf{n}$：宏观表面法线，$\mathbf{v}$：视线方向，$\mathbf{l}$：光线方向，$\mathbf{h} = \frac{\mathbf{v}+\mathbf{l}}{|\mathbf{v}+\mathbf{l}|}$：半程向量

菲涅耳近似公式（Schlick近似，1994年由Christophe Schlick提出）为：

$$F(\theta) = F_0 + (1 - F_0)(1 - \cos\theta)^5$$

其中 $\theta$ 为视线方向与半程向量的夹角，$F_0$ 对于非金属固定约为0.04，对于金属则由BaseColor贴图直接提供彩色反射率值。这解释了为何所有材质在掠射角（grazing angle）下都会产生强烈反射——这是物理规律，而非美术参数可以随意覆盖的。

漫反射部分通常采用Lambertian模型（或迪士尼使用的修正Burley漫反射）：

$$f_d = \frac{\text{BaseColor}}{\pi}$$

此处除以 $\pi$ 是为了保证半球积分后的能量守恒，这是从旧Phong流程迁移到PBR时最容易被忽略的物理细节之一。

### Metallic-Roughness工作流的贴图结构

该工作流由三张核心贴图构成：**BaseColor（基础色）**、**Metallic（金属度）**和**Roughness（粗糙度）**。

- **BaseColor**：存储材质的固有色。对于非金属，BaseColor代表漫反射颜色，sRGB值通常限制在30–240之间（对应线性空间0.02–0.9），不能出现纯黑或纯白。对于金属材质，BaseColor存储的是金属的F0反射率颜色（即镜面反射颜色），铝的BaseColor约为（0.913, 0.921, 0.925），黄金约为（1.0, 0.766, 0.336），铜约为（0.955, 0.638, 0.538），铁约为（0.562, 0.565, 0.578）。
- **Metallic**：纯灰度贴图，0表示绝缘体，1表示导体（金属），中间值仅用于过渡区域（如生锈金属边缘），不建议大面积使用中间灰值。此贴图应以线性空间导入，切勿勾选sRGB。
- **Roughness**：纯灰度贴图，0代表完美镜面，1代表完全漫反射散射。Roughness在着色器中通常被平方后用于计算GGX微表面分布，因此视觉感受与线性值并不对应——线性值0.5在视觉上对应约0.25的感知粗糙度，这意味着中灰Roughness贴图在渲染结果中实际偏光滑。

### Specular-Glossiness工作流的贴图结构

该工作流同样由三张核心贴图构成：**Diffuse（漫反射色）**、**Specular（高光色）**和**Glossiness（光泽度）**。

- **Diffuse**：仅存储非金属的漫反射颜色。对于金属区域，Diffuse必须填充为纯黑（0,0,0），因为导体没有漫反射分量，这是与Metallic-Roughness工作流最显著的操作差异。
- **Specular**：RGB贴图，直接存储F0（零角度菲涅耳反射率）。非金属的Specular值通常为4%（线性值0.04），对应sRGB约（60,60,60）；金属的Specular值则存储其实际反射颜色，如黄金约为（1.0, 0.766, 0.336）。
- **Glossiness**：与Roughness的关系为：

$$\text{Glossiness} = 1 - \text{Roughness}$$

数值含义与Roughness相反，255表示完全光滑，0表示完全粗糙。制作时需要格外注意两者的方向感，从Roughness习惯切换到Glossiness时极易出现材质感觉"反向"的主观误差。

### 两种工作流的等价转换公式

将Specular-Glossiness转换为Metallic-Roughness时，关键步骤如下：

$$\text{Metallic} = \begin{cases} 1 & \text{if } \text{Specular}_{\text{linear}} > 0.04 \\ 0 & \text{otherwise} \end{cases}$$

$$\text{BaseColor} = \begin{cases} \text{Specular} & \text{if Metallic} = 1 \\ \text{Diffuse} & \text{if Metallic} = 0 \end{cases}$$

$$\text{Roughness} = 1 - \text{Glossiness}$$

反向转换同理，但精度会有损失，因此不建议频繁互转。实际项目中若需批量转换，可使用Substance Alchemist的"Convert Specular/Glossiness to Metal/Roughness"功能，该功能内置了边缘过渡区的插值算法，比手动逐像素转换精度更高。

---

## 关键数值规范与校验方法

Epic Games在其官方PBR校准指南中明确给出了以下非金属BaseColor的线性反射率参考范围（Burley, 2012；Karis, 2013）：

| 材质类型 | 线性反射率 | 对应sRGB近似值 |
|---------|-----------|--------------|
| 木炭 | 2%（0.02） | 约50 |
| 新鲜沥青 | 4%（0.04） | 约60 |
| 干燥混凝土 | 30%（0.30） | 约148 |
| 沙漠沙地 | 36%（0.36） | 约161 |
| 新鲜雪地 | 80%（0.80） | 约230 |

非金属材质的F0固定为4%（线性0.04），这一数值对应折射率（IOR）约为1.5，是绝大多数有机材质和矿物质在可见光下的真实折射率。IOR与F0的换算关系为：

$$F_0 = \left(\frac{n - 1}{n + 1}\right)^2$$

其中 $n$ 为材质折射率。以玻璃（$n \approx 1.5$）为例，代入公式得 $F_0 \approx 0.04$，与PBR规范中非金属4%的默认值完全吻合，这并非巧合，而是PBR系统内部物理一致性的直接体现。

**例如**：在Substance Painter中制作一块"旧铁锈金属"材质时，锈迹区域（非金属）的Metallic应为0，BaseColor的sRGB亮度值应控制在40–160之间（对应锈蚀氧化铁的实测反射率约6%–35%）；金属裸露区域的Metallic应为1，BaseColor应填入铁的F0颜色（约0.562, 0.565, 0.578，对应sRGB约189, 191, 193）。两个区域之间的过渡带，Metallic贴图仅允许1–3像素宽度的灰度渐变，而非大范围模糊。此案例中，如果将锈迹区域的BaseColor sRGB值错误设置为纯黑（0,0,0），PBR验证工具会立即报告"能量吸收超限"警告，因为自然界不存在吸收100%入射光的黑体表面（碳纳米管涂层除外，其反射率约0.045%，远超普通绘制范围）。

使用Marmoset Toolbag 4的**PBR Validator**功能可对贴图进行自动合规检测：将BaseColor和Metallic贴图拖入验证器后，工具会用红色高亮标出线性值低于0.02或高于0.9的非金属像素，以及Metallic值在0.1–0.9之间超过3像素宽度的区域，帮助美术师快速定位违反能量守恒的贴图区域。

---

## 实际应用

### 虚幻引擎5的材质节点接入

UE5的M_Standard材质球直接暴露BaseColor、Metallic、Roughness三个输入槽，对应Metallic-Roughness工作流。若使用Specular-Glossiness的贴图资产直接接入，Specular贴图的RGB值会被引擎误读为高光强度（单通道），导致金属材质出现灰色高光而非彩色金属光泽，这是项目中最常见的