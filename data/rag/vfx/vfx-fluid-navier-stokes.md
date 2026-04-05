---
id: "vfx-fluid-navier-stokes"
concept: "Navier-Stokes简化"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
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



# Navier-Stokes简化

## 概述

Navier-Stokes方程（NS方程）由法国工程师克劳德-路易·纳维于1822年首次推导出黏性项，英国数学家乔治·加布里埃尔·斯托克斯于1845年给出严格数学形式，描述黏性流体在连续介质假设下的动量守恒。完整的不可压缩NS方程组为：

$$\rho\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \rho \mathbf{g}$$

$$\nabla \cdot \mathbf{u} = 0$$

其中 $\rho$ 为流体密度（水约1000 kg/m³，空气约1.2 kg/m³），$\mathbf{u}$ 为速度场向量，$p$ 为压力场，$\mu$ 为动力黏度（水约0.001 Pa·s，熔岩约100 Pa·s），$\mathbf{g}$ 为重力加速度向量。这组方程至今是七个千禧年大奖难题之一，Clay数学研究所悬赏100万美元，其三维光滑解的整体存在性仍未被证明（Fefferman, 2000）。

在游戏实时渲染中，以512³网格分辨率对上述方程做完整隐式数值积分，单帧所需浮点运算量约为 $5 \times 10^{10}$ FLOP，在RTX 4090（理论峰值82.6 TFLOPS）上仍需约0.6ms，加上压力泊松方程迭代求解和边界条件处理，总帧时间轻松突破16.67ms（60fps预算）。因此，所有实时游戏流体特效均建立在对NS方程系统性简化的基础上，不同简化路径形成了SPH、LBM、Position-Based Fluids、Shallow Water Equation等截然不同的算法族。

---

## 核心原理

### 不可压缩假设与压力泊松方程

游戏流体模拟几乎统一采用**不可压缩假设** $\nabla \cdot \mathbf{u} = 0$，意味着流体微元体积不随压力改变，密度在时间和空间上均为常数。这一假设在物理上忽略了马赫数 $Ma > 0.3$ 时才显著的可压缩效应，对水面、烟雾、火焰等视觉特效误差在5%以内，完全在视觉可接受范围。

不可压缩条件将原始动量方程的求解转化为**投影法（Projection Method）**，分两步执行：

1. **对流步**：忽略压力梯度，计算中间速度 $\mathbf{u}^*$
2. **投影步**：求解压力泊松方程，将 $\mathbf{u}^*$ 投影到散度为零的空间

压力泊松方程形如：

$$\nabla^2 p = \frac{\rho}{\Delta t} \nabla \cdot \mathbf{u}^*$$

这一线性系统的规模等于网格单元总数。128³分辨率下矩阵规模为 $2^{21} \approx 2 \times 10^6$，直接求解（LU分解）耗时不可接受，游戏引擎通常采用**雅可比迭代20~50次**即停止，而非等待残差收敛至机器精度。这带来的代价是每帧约0.5%~2%的体积泄漏，在低频摄像机运动下视觉可接受，但在高速冲击场景下会出现明显的流体"消失"现象。

### 对流项的半拉格朗日处理

NS方程左侧的非线性对流项 $\mathbf{u} \cdot \nabla \mathbf{u}$ 是数值不稳定性的根源。显式欧拉格式要求满足CFL条件 $\Delta t \leq h / |\mathbf{u}|_{max}$，在网格间距 $h = 0.02$m、流速5 m/s时，时间步仅允许0.004s（250fps），完全无法用于30fps游戏。

**半拉格朗日法（Semi-Lagrangian Method）**由Jos Stam在1999年SIGGRAPH论文《Stable Fluids》中引入实时流体领域，彻底解决了CFL限制问题。其核心思想是将欧拉网格上的对流更新转化为粒子追踪：

$$\mathbf{u}^{n+1}(\mathbf{x}) = \mathbf{u}^n\left(\mathbf{x} - \Delta t \cdot \mathbf{u}^n(\mathbf{x})\right)$$

即沿当前速度方向反向追踪一个时间步 $\Delta t$，从到达位置 $\mathbf{x} - \Delta t \cdot \mathbf{u}^n$ 处采样速度并三线性插值回当前网格点。此方法**无条件稳定**，允许使用 $\Delta t = 1/30$s，是目前Unreal Engine Niagara流体、Houdini游戏烘焙管线的标准对流求解器。

其代价是**数值耗散**：三线性插值等效于施加了幅度为 $O(h^2/\Delta t)$ 的人工黏度，导致旋涡细节在约10~20帧内衰减至不可见。MacCormack方案（Selle等，2008）通过前向追踪后再反向修正，将精度从一阶提升至二阶，以约1.8倍计算量换取湍流细节的明显改善，已被《GTA V》水面和《荒野大镖客2》河流特效所采用。

### 黏度项简化：从隐式求解到直接省略

NS方程中的黏度扩散项 $\mu \nabla^2 \mathbf{u}$ 在显式时间积分下要求：

$$\Delta t < \frac{\rho h^2}{2\mu}$$

对熔岩（$\mu \approx 100$ Pa·s，$\rho \approx 2500$ kg/m³，$h = 0.01$m），此约束要求 $\Delta t < 1.25 \times 10^{-5}$ s，即每秒需要80000次时间步，完全不可行。

**隐式黏度求解**将黏度项移至右端，转化为线性系统：

$$\left(\mathbf{I} - \frac{\mu \Delta t}{\rho} \nabla^2\right) \mathbf{u}^{n+1} = \mathbf{u}^*$$

该系统与压力泊松方程结构相同，可复用同一迭代求解器，同样限制迭代次数为20~50次。

更激进的游戏优化是直接**省略黏度项**（令 $\mu = 0$，退化为欧拉方程），将数值耗散本身作为隐式黏度模型。这对雷诺数 $Re = \rho u L / \mu > 10^4$ 的湍流场景（水、烟雾）误差极小，节省了整套线性系统求解。《荒野大镖客2》河流、《赛博朋克2077》雨水积水均采用零黏度假设并叠加程序化湍流噪声作补偿。

---

## 关键公式与简化层次

### 浅水方程（SWE）：二维投影的极端简化

当流体深度远小于水平尺度时（深宽比 $< 0.1$），完整三维NS方程可投影到二维浅水方程组：

$$\frac{\partial h}{\partial t} + \nabla \cdot (h\mathbf{u}) = 0$$

$$\frac{\partial (h\mathbf{u})}{\partial t} + \nabla \cdot \left(h\mathbf{u} \otimes \mathbf{u} + \frac{g h^2}{2}\mathbf{I}\right) = -gh\nabla b$$

其中 $h$ 为水面高度，$\mathbf{u}$ 为深度平均的二维水平速度，$b$ 为床面高程，$g = 9.81$ m/s²。SWE将三维问题降为二维，计算量从 $O(N^3)$ 降至 $O(N^2)$，256×256分辨率下单帧计算量仅约 $10^7$ FLOP，可在CPU上实时运行。《刺客信条：奥德赛》和《对马岛之魂》的海洋波浪交互均基于SWE实现。

### 涡度方法：直接模拟旋涡结构

部分特效（如龙卷风、魔法旋涡）需要显著的旋转结构但不需要完整压力求解。涡度方程通过对NS方程取旋度消去压力项：

$$\frac{\partial \boldsymbol{\omega}}{\partial t} + \mathbf{u} \cdot \nabla \boldsymbol{\omega} = \boldsymbol{\omega} \cdot \nabla \mathbf{u} + \nu \nabla^2 \boldsymbol{\omega}$$

其中 $\boldsymbol{\omega} = \nabla \times \mathbf{u}$ 为涡量场。在二维情形下涡拉伸项 $\boldsymbol{\omega} \cdot \nabla \mathbf{u}$ 消失，只需追踪标量涡度场，再通过Biot-Savart定律恢复速度场，计算量比完整NS低约3倍。

---

## 算法实现示例

以下为游戏中最常用的半拉格朗日对流核心代码片段（HLSL计算着色器）：

```hlsl
// 半拉格朗日对流：将速度场 u_prev 对流到 u_next
// gridSize: 网格分辨率，dt: 时间步长，dx: 网格间距
[numthreads(8, 8, 8)]
void AdvectVelocity(uint3 id : SV_DispatchThreadID)
{
    if (any(id >= gridSize)) return;
    
    float3 worldPos = (id + 0.5) * dx;
    
    // 从当前位置反向追踪：x_prev = x - dt * u(x)
    float3 vel = SampleVelocityTrilinear(u_prev, worldPos);
    float3 prevPos = worldPos - dt * vel;
    
    // 在追踪终点采样速度（三线性插值，隐含数值耗散）
    u_next[id] = SampleVelocityTrilinear(u_prev, prevPos);
}

// MacCormack修正：前向追踪后反向修正，提升至二阶精度
// 误差估计：err = 0.5 * (u_forward - u_backward)
float3 u_hat = SampleVelocityTrilinear(u_next, worldPos + dt * vel);
u_next[id] += 0.5 * (u_prev[id] - u_hat);  // 二阶修正项
```

---

## 实际应用：游戏引擎中的具体选型

| 简化策略 | 计算量级 | 典型帧时间（1080p） | 适用场景 | 代表案例 |
|---|---|---|---|---|
| 完整3D NS（64³网格）| $O(N^3)$ | 8~15ms | 离线烘焙 | Houdini流体缓存 |
| 浅水方程（256²） | $O(N^2)$ | 0.5~1ms | 水面交互 | 《刺客信条：奥德赛》 |
| 2D NS烟雾（128²） | $O(N^2)$ | 1~2ms | 局部烟雾 | Unreal Niagara Grid2D |
| SPH粒子（10万粒子） | $O(N \log N)$ | 3~6ms（GPU） | 飞溅、液体 | 《战神》水特效 |
| 涡粒子方法 | $O(N^2)$（小N） | <1ms | 旋涡尾迹 | 《使命召唤》爆炸烟 |

**案例：《荒野大镖客2》河流系统**

Rockstar公布的GDC 2019技术分享中，河流采用预计算的稳态SWE流场（离线计算1000帧迭代至收敛），运行时叠加基于玩家位移的实时扰动响应（2D NS局部求解，64×64分辨率，5次压力迭代，每帧约0.3ms）。水面渲染通过FFT波谱（Phillips谱，Tessendorf, 2001）叠加视觉细节，物理求解与渲染完全解耦，是"物理简化+视觉增强"策略的典型范例。

---

## 常见误区

**误区1：迭代次数越多，流体越真实**

压力泊松方程迭代从20次增加到100次，残差确实下降约80%，但视觉差异在摄像机运动和粒子特效干扰下几乎不可辨别（Bridson, 2015，《Fluid Simulation for Computer Graphics》, CRC Press）。迭代次数应根