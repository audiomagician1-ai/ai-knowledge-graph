# 伤害模型

## 概述

伤害模型（Damage Model）是特效破碎系统中将外力输入转化为结构破坏输出的核心触发架构，其本质是将**伤害值（Damage Value）**、**伤害区域（Damage Region）**、**伤害类型（Damage Type）**三个独立维度编码为可量化的破碎响应信号。与纯粹依赖刚体碰撞的物理破碎不同，伤害模型在物理层之上构建了一套语义层，使得"一颗子弹打穿玻璃"与"一颗子弹打穿砖墙"在底层能以相同代码路径处理，但产生截然不同的视觉结果。

从工业史角度看，伤害模型的系统化始于 Volition 工作室在 2001 年发布的 *Red Faction* 中所使用的 **GeoMod（Geometry Modification）** 引擎——该引擎首次将地形分割为以体素为单位的伤害接受单元，每个单元维护独立的结构完整性值（Gibson, 2002，GDC Vault: *Destruction and Deformation in Red Faction*）。此后，Epic Games 在 Unreal Engine 4.23（2019年）的预览版中随 **Chaos Physics** 系统正式将伤害模型标准化，通过 `UPhysicsFieldComponent` 和 `ApplyRadialDamage()` 接口将伤害传递抽象为引擎级 API，使破碎行为可在蓝图层无需手写物理代码即可参数化配置（Zafar et al., *Unreal Engine Physics Internals*, Epic GDC 2019）。

伤害模型的工程价值在于实现**物理真实性**与**叙事可控性**的解耦。一根混凝土柱在纯刚体仿真中除非施加精确的弯曲力矩，否则永远不会断裂；但通过伤害模型，技术美术可以设定当该柱累积受到 4200 单位结构伤害后，在距地面三分之一高度处触发沃罗诺伊（Voronoi）模式的层级破碎——这种确定性行为是电影特效镜头分镜预判和游戏关卡设计可行性评估的前提。

---

## 核心原理

### 健康值系统与阈值触发

每个参与破碎逻辑的几何体节点（在 Unreal Engine 的 **Geometry Collection** 架构中称为"Transform Bone"）持有一个浮点型**健康值（Health）**，默认范围由资产定义，通常为 100 至 50000 之间的无量纲正整数。当伤害事件触发时，系统执行以下计算：

$$H_{\text{remaining}} = H_{\text{current}} - D_{\text{applied}} \times R_{\text{mat}}^{-1}$$

其中 $H_{\text{current}}$ 为当前健康值，$D_{\text{applied}}$ 为原始伤害量，$R_{\text{mat}}$ 为材质抗性系数（Material Resistance，典型范围 $0.1 \leq R_{\text{mat}} \leq 2.0$，钢铁约为 1.8，普通玻璃约为 0.3）。当 $H_{\text{remaining}} \leq 0$ 时，该节点解除与父级骨骼的约束（Constraint Release），进入自由刚体模拟阶段。

**累积伤害（Accumulated Damage）**机制允许多次低强度冲击替代单次高强度冲击。这模拟了材料疲劳（Fatigue）行为：一块砖墙承受 10 次各携带 50 单位伤害的子弹冲击，其最终断裂效果与一次 500 单位爆炸冲击在数值上等价，但因伤害区域分布不同，前者在墙体上呈现分散的局部碎坑，后者产生中心化的整体崩塌。

### 伤害区域与局部破碎映射

伤害区域决定"哪些几何体节点接受伤害输入"，其传递形式分为两类：

**点伤害（Point Damage）**：附带世界坐标中的冲击点 $\mathbf{P}_{\text{impact}}$ 和单位冲击法线 $\hat{n}_{\text{impact}}$，仅影响以 $\mathbf{P}_{\text{impact}}$ 为圆心、由 `DamageRadius` 参数定义半径内的破碎簇（Cluster）节点。在 Unreal Engine 实现中，`ApplyPointDamage()` 函数的内部逻辑对每个候选节点执行包围盒（AABB）与冲击点的最近距离测试，仅对距离小于阈值的节点扣除健康值。

**径向伤害（Radial Damage）**：附带一个球心位置 $\mathbf{C}$ 和半径 $r$，在 $\|\mathbf{x}_i - \mathbf{C}\| \leq r$ 范围内的所有节点 $i$ 接受按距离线性衰减的伤害：

$$D_i = D_{\text{base}} \times \left(1 - \frac{\|\mathbf{x}_i - \mathbf{C}\|}{r}\right)$$

爆炸特效通常采用此模式。以一个半径 $r = 300\,\text{cm}$、基础伤害 $D_{\text{base}} = 2000$ 的手榴弹爆炸为例，距爆心 150 cm 处的砖块节点实际接受 1000 单位伤害，而位于边界处的节点仅接受趋近于 0 的象征性伤害，从而形成爆炸中心完全粉碎、边缘轻微受损的自然渐变效果。

局部破碎映射要求破碎网格预先通过 **Chaos Fracture Editor** 划分为层级 Geometry Collection 树状结构。层级 0 为整体，层级 1 为大碎块，层级 2 为小碎块。伤害事件首先作用于层级 1 节点；若该节点健康值清空，则向下解锁层级 2 的子节点，实现**递进式破碎（Progressive Fracture）**——这正是电影级破碎效果中墙体先裂开缝隙、再崩散碎块的视觉逻辑来源。

### 伤害类型与差异化破碎响应

伤害类型（Damage Type）在相同伤害值下驱动不同的破碎形态，这是伤害模型三维中最具表现力的一维。在 Unreal Engine 中，`UDamageType` 基类派生出各子类，每个子类可配置独立的**约束冲量乘数（Constraint Impulse Multiplier）**和**传播半径覆盖（Propagation Radius Override）**参数。

典型案例的伤害类型差异：
- **穿刺类（Piercing）**：高穿透、窄区域，$r_{\text{propagation}} = 5\,\text{cm}$，造成线状贯通破口，材质约束沿冲击方向定向断裂；
- **爆炸类（Explosive）**：低穿透、宽区域，$r_{\text{propagation}} = 200\,\text{cm}$，向外施加径向冲量，材质约束从内向外层层解开；
- **钝击类（Blunt）**：中等穿透、中等区域，伴随大幅度初始冲量，模拟锤击后的裂缝扩展，破碎碎片尺寸偏大。

在 Houdini 的 **RBD Material Fracture** 工作流中，伤害类型对应的是不同的约束网络（Constraint Network）断裂条件：穿刺类仅断开胶合约束（Glue Constraint），而爆炸类同时断开胶合约束和弹簧约束，释放更多自由度（SideFX Documentation, *Houdini RBD Constraints*, 2023）。

---

## 关键方法与公式

### 分层阈值设计（Tiered Threshold Design）

工业实践中，单一破碎阈值往往不足以表达丰富的受损状态。常见做法是为同一几何体设置三至四层阈值，分别对应不同的视觉损伤程度：

| 阈值层级 | 健康值区间 | 触发效果 |
|----------|-----------|---------|
| 完好（Intact） | 100% – 70% | 无变形，无粒子 |
| 受损（Damaged） | 70% – 35% | 切换损伤贴图，发射碎屑粒子 |
| 严重受损（Critical） | 35% – 5% | 局部 Geometry 破碎，释放烟尘 Niagara 特效 |
| 摧毁（Destroyed） | < 5% | 完全破碎，触发 Level 1 + Level 2 节点解锁 |

这一设计源自 Dice 工作室在 *Battlefield: Bad Company 2*（2010）中的 **Destruction 2.0** 系统，该系统将建筑结构分为 32 个独立破坏区块，每个区块使用三级阈值驱动渐进式外观替换（Patrick Liu, *Battlefield's Destruction System*, GDC 2010）。

### 伤害衰减曲线（Damage Falloff Curve）

径向伤害的衰减不必是线性的。Unreal Engine 的 `URadialDamageEvent` 支持通过 `FalloffCurve`（类型为 `UCurveFloat`）指定自定义衰减形状。常见的三种衰减曲线及其物理含义：

- **线性衰减**：$D(d) = D_0 \left(1 - d/r\right)$，适合低速钝器冲击波；
- **平方衰减**：$D(d) = D_0 \left(1 - (d/r)^2\right)$，更接近真实爆炸超压的衰减特性（爆炸冲击波超压近似与距离平方成反比）；
- **指数衰减**：$D(d) = D_0 \cdot e^{-\lambda d}$，适合热辐射或能量束类武器效果，其中 $\lambda$ 为介质吸收系数。

在影视级爆破特效制作中，VFX 监制通常要求技术 TD 根据真实爆炸事故调查报告（如 NFPA 921 标准）校准 $\lambda$ 值，以确保破碎范围与能量级别的视觉可信度。

---

## 实际应用

### 游戏引擎中的实时伤害模型

在 Unreal Engine 5 的实时工作流中，伤害模型的典型搭建流程如下：

1. 在 **Fracture Mode** 中对静态网格体执行 Voronoi 或 Cluster 破碎，生成 Geometry Collection 资产；
2. 在每个 Geometry Collection 的 **Damage Thresholds** 面板中为各层级骨骼设置 `External Strain`（外部伤害阈值）和 `Internal Strain`（内部传播阈值）；
3. 在场景中放置 `AGeometryCollectionActor`，绑定 `UPhysicsFieldComponent`；
4. 通过蓝图调用 `ApplyRadialDamage(DamageAmount=1500, Origin=HitLocation, DamageRadius=200.f, DamageTypeClass=BP_ExplosiveDamage)`；
5. Chaos 引擎在每帧 Tick 的 `FChaosSolverActor::UpdateFields()` 阶段遍历场景中所有激活的 Geometry Collection，计算累积伤害并触发约束断裂。

**案例**：以制作一堵可被炮弹击穿的砖墙为例。墙体分为层级 1（16块大砖区）和层级 2（每大区8块小碎片）。设定层级 1 节点 `External Strain = 800`，层级 2 节点 `External Strain = 200`。一枚 `DamageAmount = 1200`、`DamageRadius = 80 cm` 的炮弹命中墙体中心时，命中点半径 80 cm 内的 3 个大砖区节点分别接受 1200、840、400 单位伤害（根据距离衰减）。前两个节点阈值被突破，解锁其下属 16 个小碎片节点；而距爆心最远的第 3 个节点（接受 400 单位 < 800 阈值）保持完整，但其健康值记录为 400/800 = 50%，为后续累积伤害保留状态。

### Houdini 离线破碎中的伤害驱动

在 Houdini 的 **SOP（Surface Operator）** 离线流程中，伤害模型以**属性驱动约束断裂**的形式实现。技术 TD 在约束网络点上写入 `@strength` 属性（默认值代表结构完整性），在 `SOP Solver` 中每帧根据碰撞数据更新 `@strength`：

```vex
// 在 SOP Solver 中执行：
float