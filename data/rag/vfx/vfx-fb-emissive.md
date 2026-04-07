# 自发光序列帧

## 概述

自发光序列帧（Emissive Flipbook）是序列帧特效技术与HDR自发光材质属性的结合产物，专门用于制作火焰核心、闪电弧、能量爆炸、魔法光球等随时间变化的高亮度发光体视觉效果。其核心技术特征在于：序列帧贴图的RGB颜色值经材质节点放大后超过标准线性空间的1.0上限，输出HDR（High Dynamic Range，高动态范围）亮度信号，进而驱动渲染管线中的Bloom后处理通道向外扩散真实感光晕。

该技术的历史可追溯至Unreal Engine 3时代（约2006年）。开发者最初发现将材质Emissive插槽的RGB值设置为大于1的浮点数时，引擎的Bloom系统会以超出1.0的部分作为"光源种子"向周围像素扩散亮度，形成肉眼可见的辉光。这一偶然发现后来被Epic Games系统化为HDR Emissive工作流，并在Unreal Engine 4发布的《Physically Based Shading on Mobile》技术文档（Karis, 2013）中明确阐述了Emissive输出与Bloom响应的数学关系。

与传统动态点光源方案相比，自发光序列帧的最大优势在于**零运行时光照计算开销**——它不向场景投射真实光照，不产生额外的Shadow Map渲染，仅通过后处理Bloom产生视觉上的"发光"幻觉。在移动平台和主机平台的实时特效中，一个粒子系统用自发光序列帧模拟的火焰爆炸，其GPU开销通常比同等视觉质量的动态光源方案低60%～80%。

---

## 核心原理

### HDR 亮度倍增与 Bloom 驱动机制

自发光序列帧产生辉光的根本原理是：渲染管线在HDR帧缓冲（HDR Framebuffer）阶段将Emissive输出的亮度值原样写入浮点纹理（通常为R11G11B10F或R16G16B16A16F格式），随后Bloom通道对超过亮度阈值（Threshold，默认值通常为1.0）的像素进行高斯模糊（Gaussian Blur）扩散，最终通过色调映射（Tone Mapping）将HDR信号压缩回显示器可呈现的LDR范围，同时保留发光感知。

材质中的最终Emissive输出计算公式为：

$$E_{out} = C_{sample}(u,v,t) \times K_{intensity} \times C_{tint}$$

其中 $C_{sample}(u,v,t)$ 是在时间 $t$ 下从序列帧图集采样的线性空间RGB颜色值（范围0–1），$K_{intensity}$ 是标量发光强度倍数（典型值范围为1.0–20.0），$C_{tint}$ 是美术可调节的色调颜色向量。当 $K_{intensity} \times C_{sample}$ 的任意分量超过1.0时，Bloom系统即被激活。

实际项目中各发光区域的典型参数分布如下：火焰核心 $K_{intensity}$ 取值3.0–10.0，可见辉光范围最大；外焰过渡区取1.2–2.5，仅产生微弱光晕；烟雾拖尾区低于1.0，不触发Bloom但保留色彩叠加感。

### 序列帧 UV 计算与帧率控制

序列帧图集（Flipbook Atlas / Sprite Sheet）将N帧动画排列在一张正方形贴图中，常见规格为 $4\times4$（16帧）、$8\times8$（64帧）、$8\times16$（128帧）。每帧的UV尺寸为：

$$\Delta u = \frac{1}{cols}, \quad \Delta v = \frac{1}{rows}$$

以 $8\times8$ 图集为例，$\Delta u = \Delta v = 0.125$。第 $n$ 帧（从0开始计）的UV左上角坐标为：

$$u_n = \left(\lfloor n \bmod cols \rfloor\right) \times \Delta u, \quad v_n = \left\lfloor \frac{n}{cols} \right\rfloor \times \Delta v$$

在Unreal Engine 5的材质编辑器中，`SubUV`粒子模块和材质内置的`FlipBook`节点已封装上述UV偏移逻辑，并通过`Time`节点配合`Floor`函数实现整数帧跳转——使用`Floor`而非线性插值是关键：线性插值会在相邻帧之间产生半透明重叠（Ghost Frame），对发光帧尤为明显，严重破坏闪光感。

帧率的选择直接影响视觉频率感知：24 fps适合缓慢变化的火焰和烟雾；30–40 fps适合中速爆炸；60 fps以上适合高频电弧和频闪光效。部分特效使用**非线性帧率**——在爆炸的初始膨胀阶段以60 fps播放，在消散尾声阶段降至12 fps，通过材质中的曲线参数（Curve Atlas）控制播放速率，从而在不增加贴图帧数的前提下强化爆炸的冲击感。

### 混合模式选择与 Alpha 通道策略

自发光序列帧的材质混合模式选择直接决定发光效果的质量上限：

**Additive（加法混合）**：粒子颜色直接叠加到场景颜色之上。由于黑色区域（RGB = 0,0,0）加法叠加值为零，自动形成透明效果，无需显式Alpha通道控制。其优势是叠加多层粒子时亮度自然累积，完美契合发光体的物理行为；缺点是遮挡场景亮区时可能导致过曝。

**Translucent（半透明混合）**：需要独立的Opacity输入控制透明度。此时必须注意：若将Opacity值乘以HDR Emissive输出，将会削弱发光强度。正确做法是Opacity仅控制Alpha遮罩形状，Emissive独立输出全值，在材质节点图中二者走不同的数据流路径。

**Unreal Engine中的Emissive on Translucent最佳实践**（据Epic官方文档建议）：开启材质的`Translucency Lighting Mode`为`Surface TranslucencyVolume`，并勾选`Apply Fogging`以确保HDR发光不会穿透体积雾。

---

## 关键方法与制作流程

### 贴图制作规范：线性空间与色彩编码

自发光序列帧贴图必须存储为**线性空间（Linear Space）RGB**，而非sRGB编码。若贴图以sRGB格式导入（勾选了`sRGB`选项），引擎在采样时会进行Gamma 2.2解码，导致颜色值被非线性压缩，高亮区域的Emissive输出反而降低，严重削弱Bloom响应。

在Houdini或After Effects中输出序列帧时，应将色彩空间设置为**ACEScg**或**Linear Rec.709**，并以**EXR（OpenEXR）**格式导出中间文件以保留完整HDR范围，再在引擎中转换为压缩贴图格式（BC6H用于HDR数据，BC7用于LDR颜色数据）。

贴图分辨率方面，单帧分辨率通常选择64×64到256×256之间，整体图集分辨率控制在2048×2048以内以满足主流平台的纹理采样限制。

### 发光强度的动画化驱动

静态的 $K_{intensity}$ 值只能产生恒定亮度的发光效果。高质量的自发光序列帧会将发光强度本身动画化，使亮度随爆炸过程起伏变化。在Unreal Engine的Cascade或Niagara粒子系统中，可使用`Dynamic Material Parameter`将粒子生命周期曲线的强度值实时传入材质的 $K_{intensity}$ 参数。

例：一个爆炸粒子的生命周期为0.5秒，其发光强度曲线可设计为：0–0.05秒从0快速上升至15.0（闪白峰值），0.05–0.2秒下降至5.0（火焰燃烧阶段），0.2–0.5秒平滑降至0.8（烟雾消散阶段）。这种三段式亮度曲线能精确还原真实爆炸的物理发光规律，仅通过贴图和材质参数即可实现，无需任何动态光源。

### Bloom 参数联调

自发光序列帧的视觉效果与场景Post Process Volume中的Bloom参数高度耦合。关键参数包括：`Bloom Intensity`（光晕整体强度，建议值0.5–1.5）、`Bloom Threshold`（触发Bloom的亮度阈值，降低阈值可使较暗的发光区域也产生光晕）、`Bloom Size Scale`（光晕扩散半径）。美术必须在目标平台的Bloom配置下测试序列帧效果，因为不同平台（PC/主机/移动端）的Bloom实现差异可能导致相同 $K_{intensity}$ 值产生截然不同的光晕半径。

移动平台（iOS/Android）通常使用简化版Bloom，对HDR值的响应范围更窄，因此移动端特效的 $K_{intensity}$ 典型值需要比PC端提高30%–50%才能达到同等视觉强度。

---

## 实际应用案例

**案例一：《原神》的元素爆发特效**

米哈游在《原神》（2020）中大量使用自发光序列帧制作角色元素技能的光爆效果。以雷系角色的爆发为例，核心闪光粒子使用32×32规格的8×8图集序列帧，Additive混合模式，$K_{intensity}$ 在爆发瞬间峰值达到12–15，配合相机Shake和后处理的短暂过曝效果，形成视觉冲击力极强的闪白感。由于游戏需要同时兼容PC和移动端，材质中内置了平台判断分支：移动端路径的 $K_{intensity}$ 乘以1.4的补偿系数以抵消简化Bloom的响应损失。

**案例二：Niagara系统中的电弧特效**

在Unreal Engine 5的Niagara粒子系统中制作电弧序列帧时，典型设置为：使用$4\times8$（32帧）的电弧图集，帧率60 fps，Emissive强度通过`Particle Color`乘以基础强度参数5.0输出。电弧的随机闪烁感通过在Niagara图中对每个粒子个体设置不同的播放起始帧（Random Start Frame）实现，使多条电弧在视觉上形成不同步的频闪，极大增强真实感。

---

## 常见误区

**误区一：认为Emissive值越高效果越好**

无上限地提升 $K_{intensity}$ 不会无限增加光晕面积，当输入亮度超过Bloom的饱和阈值（通常在HDR值20–30以上）时，光晕半径趋于稳定，而过曝的纯白核心反而会消除发光体的形态细节。正确做法是先确定目标光晕半径，反推所需的 $K_{intensity}$ 值范围。

**误区二：将自发光序列帧贴图以sRGB格式导入**

如前文所述，sRGB导入会对颜色值施加Gamma解码，导致原本为2.0的线性亮度值被解码为约0.216，完全无法驱动Bloom。诊断方法：在材质中将Emissive节点接出到Emissive Color的同时接出到BaseColor，观察BaseColor预览中的亮区是否被过度压暗——若压暗明显，则存在sRGB错误导入。

**误区三：在Translucent材质中将Emissive乘以Opacity**

部分新手在Translucent材质中将Opacity值（通常为0–1的遮罩）乘以整个颜色输出再接入Emissive Color，这会导致遮罩边缘的HDR值被Opacity削弱至1.0以下，Bloom响应丢失，发光体边缘没有光晕扩散。正确的节点图结构是：贴图RGB乘以强度参数后直接接Emissive Color输入，贴图Alpha通道独立接Opacity输入，二者完全分离。

**误区四：忽视不同Bloom实现的平台差异**

UE5的Lumen全局光照系统会与Emissive发光发生交互——当材质开启`Cast Ray Traced Shadows`时，高强度Emissive输出可能被Lumen识别为间接光源，向周围场景投射