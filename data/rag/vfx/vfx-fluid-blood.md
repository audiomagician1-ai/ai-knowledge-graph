---
id: "vfx-fluid-blood"
concept: "血液与液体"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 血液与液体

## 概述

血液与液体特效是游戏特效中专门针对高粘度、非牛顿流体或具有特定颜色与质感的液体所设计的模拟技术，主要处理血液、油漆、毒液、熔岩等与水性液体行为截然不同的材料。血液的动力粘度约为水的3至4倍（约0.003至0.004 Pa·s），剪切稀化特性使其在低剪切速率下表现出高粘度，在高剪切速率（如子弹击穿时）迅速降低至接近水的粘度——这一非牛顿流体特性由Carreau模型描述（Bird et al., 《Transport Phenomena》, Wiley, 2007）。

该类特效的大规模商业应用始于2000年代初期动作游戏的崛起。2001年发布的《Max Payne》率先将程序化血液贴花系统与物理飞溅模拟结合，使玩家首次在实时游戏中看到具有说服力的血液行为。2009年《Left 4 Dead》引入基于曲面细分的动态血液流淌系统，血迹能够沿角色模型的几何曲面向下流动，而非简单地平面贴附。2020年《The Last of Us Part II》进一步加入了表面孔隙吸收模拟，使血液在粗糙布料上的径向扩散速度（约12 cm/s）显著快于光滑金属（约3 cm/s）。掌握这类液体特效的意义在于：其视觉呈现直接影响游戏的ESRB分级（M级与AO级的核心区分指标之一即为血液表现程度），需要技术与美术方向的精准协作。

---

## 核心原理

### 贴花投影与深度偏移（Deferred Decal）

血液落地或溅到墙面时，游戏引擎使用延迟贴花（Deferred Decal）技术将血迹投影到现有几何体表面，无需修改原始网格。投影方向由碰撞时的速度向量决定，贴花UV坐标通过将世界空间坐标除以投影盒尺寸生成。为防止贴花与底层几何体产生Z-Fighting，必须在深度写入时施加深度偏移，在OpenGL中通常写为：

```glsl
// 防止Z-Fighting的深度偏移写法
gl_FragDepth = gl_FragCoord.z - 0.0001;
```

在DirectX 11/12中则通过管线状态对象的 `SlopeScaledDepthBias`（典型值：1.0）与 `DepthBiasClamp`（典型值：0.001）联合控制。血液贴花还需存储法线信息以参与场景光照计算，在Unreal Engine 5中通过DBuffer Decal通道分别写入Albedo（R8G8B8A8）、Normal（R8G8B8）和 Roughness（R8）三个独立缓冲区，确保贴花不影响底层几何体的深度测试。

单帧内同一位置可能叠加多个血液贴花（例如连续射击），因此需要管理贴花池（Decal Pool）：UE5默认贴花池上限为512个，超出时按照LRU（最近最少使用）策略淘汰最早的贴花，开发者可通过 `r.DBuffer.MaxDecals` 控制台变量调整该阈值。

### 流体轨迹与重力流动模拟

血液在竖直或倾斜表面上的流淌依赖流体轨迹算法（Fluid Trail Algorithm）。其核心是在表面切线空间中，沿重力向量在表面上的投影方向计算流动向量：

$$\vec{v}_{flow} = \text{normalize}\left(\vec{g} - (\vec{g} \cdot \hat{n})\hat{n}\right) \times k_{viscosity}$$

其中 $\vec{g}$ 为世界空间重力方向（通常为 $(0, -9.8, 0)$ m/s²），$\hat{n}$ 为表面法线，$k_{viscosity}$ 为粘度系数（血液取0.25，水取1.0，熔岩取0.05）。流淌轨迹以粒子链（Particle Chain）或程序化UV滚动方式渲染，轨迹宽度随累计流量减少线性收窄，末端在低洼处积聚产生积液效果（Pooling）——通过将透明度曲线映射至粒子生命周期的末段85%至100%区间实现渐变堆积。

实际工程中，轨迹采样频率通常为每帧2至4个新节点，每条轨迹链最长保存32至64个节点以平衡内存与表现；超出节点上限时截断尾部并触发积液粒子生成。

### 飞溅形态与碰撞角度映射

高速碰撞（如子弹射入，初速度约900 m/s）产生的血液飞溅具有明确的形态规律：主液滴沿碰撞法线方向喷出，周围伴随卫星液滴（Satellite Droplets），其角度散布近似正态分布，标准差约为15°至25°（由碰撞速度决定）。

实现时预先制作8至16种不同形态的飞溅贴花图集（Splatter Atlas），在运行时依据以下三个变量组合选取：

- **碰撞速度**：低速（<5 m/s）→ 水滴型；中速（5至50 m/s）→ 星形飞溅；高速（>50 m/s）→ 雾化型
- **碰撞角度 θ**：正面碰撞（θ = 90°）→ 对称圆形；斜角碰撞（θ = 15°至30°）→ 带拖尾椭圆形
- **表面材质**：粗糙石材（Roughness > 0.7）→ 锯齿边缘；光滑金属（Roughness < 0.3）→ 光滑圆弧边缘

碰撞角度对贴花形态的影响通过旋转UV矩阵实现：拖尾方向始终沿速度向量在表面的投影方向延伸，拉伸比例为 $s = 1 + \cot(\theta) \times 0.5$，使15°斜角碰撞的血迹长宽比约达3:1至4:1。

---

## 关键公式与着色器实现

血液材质的次表面散射（Subsurface Scattering, SSS）是使其区别于油漆的核心视觉特征：血液的红细胞对波长620至750 nm的红光散射深度约为2至3 mm，而对蓝光（450 nm）的穿透深度不足0.5 mm，导致薄层血液（<1 mm）呈现鲜红色，厚层血液（>3 mm）转为深红近棕色。在实时渲染中使用预积分SSS近似公式（Penner, 2011）：

$$I_{SSS} = \int_0^d R(r) \cdot L(x - r) \, dr \approx \sum_{i=1}^{N} w_i \cdot \text{GaussianBlur}(L, \sigma_i)$$

其中 $R(r)$ 为散射剖面函数，$w_i$ 和 $\sigma_i$ 为各通道高斯核的权重与标准差。血液的红色通道参数典型值为 $w_R = 0.6,\ \sigma_R = 2.5$ mm，绿色通道为 $w_G = 0.15,\ \sigma_G = 1.0$ mm，蓝色通道为 $w_B = 0.0,\ \sigma_B = 0.0$（几乎不散射）。

以下为血液贴花材质在HLSL中的Roughness与SSS混合伪代码：

```hlsl
// 血液贴花 HLSL 片元着色器核心片段
float4 BloodDecalPS(DecalVSOutput input) : SV_Target
{
    // 从贴花图集采样基础颜色
    float4 baseColor = SplatterAtlas.Sample(LinearSampler, input.uv);
    
    // 厚度图：0=薄层(鲜红), 1=厚层(深红)
    float thickness = ThicknessMap.Sample(LinearSampler, input.uv).r;
    
    // 颜色随厚度从 (0.72, 0.05, 0.05) 变为 (0.28, 0.02, 0.02)
    float3 thinColor  = float3(0.72, 0.05, 0.05);
    float3 thickColor = float3(0.28, 0.02, 0.02);
    float3 bloodColor = lerp(thinColor, thickColor, pow(thickness, 0.45));
    
    // 粗糙度：薄层血液呈湿润光泽(0.15), 厚层/凝固血液粗糙(0.65)
    float roughness = lerp(0.15, 0.65, thickness);
    
    // 写入DBuffer
    return float4(bloodColor * baseColor.rgb, roughness);
}
```

---

## 实际应用

### 游戏引擎中的集成方案

在Unreal Engine 5中，血液贴花系统由 **Niagara粒子系统 + DBuffer Decal材质 + Chaos物理** 三层协同驱动：Niagara负责生成飞溅粒子并在碰撞回调中触发贴花Spawn；DBuffer Decal材质处理贴花投影与深度混合；Chaos物理提供角色布娃娃上的动态血液流淌节点位置。在Unity（HDRP管线）中，等效实现依赖 **Decal Projector组件 + VFX Graph + Custom Pass**，其中Custom Pass负责在GBuffer写入后将贴花法线混入 `_NormalBufferTexture`。

### 平台合规与分级控制

ESRB规范要求AO级（Adults Only）游戏的血液特效不得出现在Teen平台（如任天堂Switch家长控制开启时）。工程实践中通常实现三档血液级别开关：

- **Level 0（无血）**：所有血液粒子替换为金属火花或黑色油污，贴花完全禁用
- **Level 1（减弱）**：血液颜色改为深灰或蓝色（如科幻主题），飞溅粒子数量减少75%
- **Level 2（完整）**：全参数运行，SSS、积液、孔隙吸收全部开启

这一分级参数通常存储在全局GameUserSettings中，并绑定至平台认证的家长控制API。

---

## 常见误区

**误区1：忽略贴花深度排序导致视觉错乱**
多个血液贴花叠加时，若不按照生成时间或深度排序，新贴花可能"浮现"于旧贴花之上，造成不自然的图层闪烁。正确做法是为每个贴花分配单调递增的SortPriority值（UE5中对应 `Decal Sort Order`），确保后生成的贴花在混合时始终覆盖早期贴花。

**误区2：在移动平台直接使用DBuffer Decal**
DBuffer Decal依赖延迟渲染的G-Buffer，而移动平台（iOS Metal / Android Vulkan）多采用Tile-Based Deferred Rendering（TBDR）架构，写入DBuffer的带宽开销极高。移动端应改用前向渲染下的**贴花网格投影（Decal Mesh Projection）**：用一个极薄的四边形Mesh覆盖于地面，配合Alpha混合实现血迹，性能开销约为DBuffer方案的30%。

**误区3：把血液粘度当常数处理**
血液是典型的剪切稀化非牛顿流体。若将粘度设为固定值0.004 Pa·s，则在模拟高速飞溅时会产生不真实的过厚液滴。应使用简化Power-Law粘度模型：$\eta = k \cdot \dot{\gamma}^{n-1}$，其中血液的幂律系数 $n \approx 0.78$，稠度系数 $k \approx 0.014$（Pa·s^n），使高剪切速率下粘度自动降低至约0.001 Pa·s。

**误区4：飞溅贴花未考虑表面法线方向**
斜面上的血液飞溅若仍以世界空间垂直向下作为投影方向，贴花将出现拉伸失真。正确做法是以碰撞点的表面法线为投影轴，并将贴花盒的本地Y轴与重力在表面的投影对齐，从而使拖尾方向始终指向斜面向下方向。

---

## 知识关联

**前置概念——雨滴模拟**：雨滴模拟中建立的表面流动向量计算方法（切线空间重力投影）直接延伸至血液流淌轨迹算法，但血液需额外处理粘度系数（0.25）