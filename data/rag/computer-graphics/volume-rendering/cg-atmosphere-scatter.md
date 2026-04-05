---
id: "cg-atmosphere-scatter"
concept: "大气散射实现"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 4
is_milestone: false
tags: ["环境"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 大气散射实现

## 概述

大气散射实现是将Rayleigh散射和Mie散射的物理方程转化为实时可用的渲染算法的工程过程。由于大气层厚度约100公里，光线穿越大气时需要在数百个采样点上积分散射贡献，暴力数值积分的计算量在实时场景中完全不可接受。因此，业界发展出以预计算查找表（Look-Up Table，LUT）为核心的方案，将高维积分结果缓存到二维或三维纹理中，使运行时只需几次纹理采样即可重建完整的天空光照。

该技术路线由Bruneton和Neyret在2008年发表于SIGGRAPH的论文《Precomputed Atmospheric Scattering》中系统化奠定。他们将大气光学深度、单次散射、多次散射分别编码到不同维度的纹理中，整套预计算系统的输入只有两个参数：观察者高度 $h$ 和观察方向与天顶角的余弦值 $\mu$。这篇论文成为后续所有主流引擎大气系统的理论基础，包括Epic在UE4中实现的SkyAtmosphere组件（2020年正式发布）。

大气散射实现的工程价值在于将物理上精确但计算极重的路径积分压缩到可在移动端运行的开销内，同时保持日出日落色彩变化、地球曲率阴影、臭氧层蓝移等视觉细节的物理正确性。

## 核心原理

### 光学深度与透射率预计算

透射率 $T(P_a, P_b)$ 描述光线从点 $P_a$ 到 $P_b$ 的衰减，定义为：

$$T(P_a, P_b) = \exp\!\left(-\int_{P_a}^{P_b} \beta_e(h(s))\,ds\right)$$

其中 $\beta_e(h)$ 是高度 $h$ 处的消光系数，对Rayleigh粒子按指数分布 $\beta_R(h) = \beta_{R,0}\,e^{-h/H_R}$（海平面散射系数 $\beta_{R,0} \approx 5.8\times10^{-6}\,\text{m}^{-1}$，标高 $H_R = 8\text{km}$）。透射率只依赖于观察者高度 $h$ 和仰角余弦 $\mu$，因此可以预计算为一张分辨率256×64的二维纹理 `TransmittanceLUT`。在运行时，任意两点间的透射率可用 $T(A,B) = T(A,\text{atm\_top})/T(B,\text{atm\_top})$ 相除得到，避免重复积分。

### 单次散射预计算

单次散射仅考虑光子被大气粒子偏折一次即到达眼睛的贡献。对于观察方向上某采样点 $P$，其Rayleigh散射亮度为：

$$L_1(\mathbf{v}) = \int_0^d T(\text{eye},P)\,\beta_R(h)\,p_R(\theta)\,E_\odot\,T(P,\text{sun})\,ds$$

其中 $p_R(\theta) = \frac{3}{16\pi}(1+\cos^2\theta)$ 是Rayleigh相位函数，$E_\odot$ 是大气顶层太阳辐照度。Bruneton方案将单次散射结果存入四维纹理（$h, \mu, \mu_s, \nu$ 四个参数），其中 $\mu_s$ 是太阳仰角余弦，$\nu$ 是观察方向与太阳方向的夹角余弦。实际实现中常用分辨率为 $256\times128\times32\times8$ 的三维纹理（合并 $\nu$ 维度）存储Rayleigh与Mie分量。

### 多次散射迭代计算

多次散射通过迭代方式求解：第 $n$ 阶散射 $L_n$ 使用第 $n-1$ 阶的结果作为入射光源。Bruneton原方案在CPU上离线迭代4次，每次迭代需要对半球面做蒙特卡洛积分，计算时间约数分钟。

2020年Hillaire在《A Scalable and Production Ready Sky and Atmosphere Rendering Technique》中改进了多次散射的计算方法：将多次散射的总贡献用一个二维纹理 `MultiScatteringLUT`（分辨率仅32×32）近似，利用各向同性假设（均匀相位函数）使积分可分离，把原本数分钟的CPU预计算压缩至GPU上不足1毫秒，且结果与4阶迭代视觉差异极小。该方案已被UE5的SkyAtmosphere直接采用。

### 运行时天空视图重建

在实际渲染帧时，引擎不直接查询高维散射LUT，而是先将天空穹顶渲染到一张分辨率180×180的屏幕空间 `SkyViewLUT` 中。该纹理以经纬度参数化天空半球，每个像素在GPU上查询透射率LUT和多次散射LUT，计算量约等于对大气层做32次体积采样。最终天空渲染只需一次全屏quad并对 `SkyViewLUT` 进行双线性采样，将整帧天空绘制开销压缩到0.2ms以内（1080p，RTX 2060测试数据）。

## 实际应用

**引擎集成示例：UE5的SkyAtmosphere**  
UE5暴露了 `RayleighScattering`（默认值 $0.0331$，对应 $\beta_{R,0}$ 的标准化版本）、`MieScatteringScale`、`OzoneAbsorptionScale` 等参数，均直接映射到上述物理公式的系数。美术通过调整 `AtmosphereHeight`（默认100km）和 `GroundRadius`（默认6371km，即地球半径）可以模拟不同星球的大气效果。

**游戏《荒野大镖客2》中的动态天气**  
Rockstar在GDC 2019分享了其大气系统：他们对Bruneton方案做了定制，额外引入了一个表示云层遮蔽的一维LUT，使阴天条件下的散射计算仍保持物理连贯性，整套系统在PS4 Pro上的帧预算约为0.8ms。

**移动端简化方案**  
对于无法负担多张3D LUT的移动平台，常见做法是仅保留透射率LUT和一张预积分的天空颜色LUT，将Mie散射的前向散射峰（Henyey-Greenstein相位函数，不对称因子 $g\approx0.8$）用解析近似代替，可在Mali G76 GPU上将开销控制在0.3ms以内。

## 常见误区

**误区一：认为提高LUT分辨率就能无限提升精度**  
透射率LUT使用256×64已是精度与内存的平衡点。真正影响精度的是沿视线方向的步进采样数：积分步数不足（如少于16步）会导致日落时地平线附近出现明显色带，而非LUT分辨率问题。增大LUT至512×256仅能改善参数化边界处的插值瑕疵，对渐变误差几乎无帮助。

**误区二：混淆Rayleigh散射与Mie散射的存储方式**  
单次散射LUT中Rayleigh和Mie分量必须分开存储（通常分别存入RGBA纹理的RGB通道和A通道，或独立两张纹理）。原因在于相位函数不同：Rayleigh用 $p_R(\theta)$ 而Mie用Henyey-Greenstein，运行时需要根据观察-太阳夹角 $\theta$ 重新加权。如果预计算时将两者合并，就无法在运行时调整太阳方向，天空颜色将锁死在特定太阳角度下。

**误区三：认为多次散射对视觉效果可以忽略**  
多次散射在正午蓝天的亮度贡献约占总散射亮度的25%至35%。仅实现单次散射的大气系统会呈现出过暗、饱和度过高的天空，在云影交界处尤为明显。Hillaire的32×32 `MultiScatteringLUT` 方案成本极低（GPU计算不足1ms），在任何目标平台上省略多次散射都难以用性能理由来辩护。

## 知识关联

**前置知识衔接**  
天空与大气的物理基础（Rayleigh散射截面、Mie散射参数、大气分层结构）是理解各LUT参数物理含义的必要前提。`TransmittanceLUT` 的参数化依赖对大气几何结构（地球半径、大气顶层高度）的理解，而非通用的渲染管线知识。

**横向关联：体积云与大气散射的耦合**  
体积云渲染需要从大气散射系统获取环境光：云体内部的多次散射（通常用Diffusion Profile近似）的边界条件是大气的 `SkyViewLUT` 所提供的环境辐射。两个系统通过共享透射率LUT的查询接口解耦，在引擎中常用同一套 `AtmosphereParameters` 常量缓冲区绑定。

**延伸方向：行星际尺度大气**  
将地球半径从6371km替换为其他值（如火星3390km、金星6051km），同时调整 $\beta_{R,0}$ 和Mie散射系数，即可用同一套LUT框架渲染外星大气，该方向在科