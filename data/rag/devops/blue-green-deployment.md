# 蓝绿部署

## 概述

蓝绿部署（Blue-Green Deployment）是一种通过同时维护两套完全相同的生产环境来实现零停机发布的策略。其核心机制是：始终保持"蓝色"（Blue）和"绿色"（Green）两个版本的服务同时存在于基础设施中，流量路由器（通常是负载均衡器或反向代理）在任意时刻只将生产流量指向其中一个版本，另一个版本则处于空闲或预热状态。

这一概念由 Jez Humble 和 David Farley 在2010年出版的《Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation》一书中正式系统化描述，成为持续交付实践的经典模式之一（Humble & Farley, 2010）。该书第10章"Deploying and Releasing Applications"首次以"Blue-Green Deployment"命名并完整描述了这一模式的双环境结构与切换机制。在AI推理服务的部署场景中，蓝绿部署尤其关键——一个PyTorch模型从v1升级到v2时，若采用传统停机替换方式，即便仅有30秒中断，也会导致在线推理请求超时失败；蓝绿部署使得切换可以在DNS层面或Kubernetes Service层面完成，切换耗时可压缩至毫秒级。

与简单的滚动更新（Rolling Update）不同，蓝绿部署要求两套环境的资源投入在切换窗口期几乎翻倍，但换来的是极为干净的回滚路径：发现新版本（绿色）存在问题时，仅需将路由切回蓝色环境，回滚时间通常不超过5秒，远快于重新部署所需的几分钟乃至十几分钟。滚动更新则因其逐步替换Pod的方式，回滚时同样需要逐步回替，期间存在新旧版本并行服务的窗口，状态难以精确控制；而蓝绿部署的二元切换特性使得生产环境的版本边界始终清晰。

在云原生架构兴起之前，蓝绿部署主要依赖硬件负载均衡器（如F5 BIG-IP）实现流量切换，成本极高；自2014年Kubernetes开源并于2016年发布1.0稳定版之后，基于Kubernetes Service的蓝绿部署才真正成为中小团队可负担的主流实践（Burns et al., 2016）。与金丝雀发布（Canary Release）相比，蓝绿部署不做流量比例切分，而是以全量方式切换，因此更适合不允许新旧版本并行处理同类请求的强一致性场景，例如有状态的模型推理服务或金融交易系统。

**思考：** 如果你的AI推理服务每次新模型部署都需要重新加载50GB的模型权重（约需4~6分钟），蓝绿部署中的绿色环境应在何时开始预加载权重？若流量切换后30秒内发现新模型输出结果存在系统性偏差，你的回滚决策触发条件应如何量化定义，才能在误报率与漏报率之间取得最优平衡？

## 核心原理

### 双环境镜像与流量切换机制

蓝绿部署的技术实现依赖于一个关键不变量：**两套环境必须在任何时间点都具备独立接收全量生产流量的能力**。在Kubernetes中，这通常通过两个独立的Deployment（如 `model-service-blue` 和 `model-service-green`）加上一个共享的Service资源实现。Service的 `selector` 字段通过标签（Label）决定流量指向哪个Deployment：

```yaml
# 切换到绿色环境只需修改此 selector
selector:
  app: model-service
  slot: green   # 改为 blue 即可回滚
```

流量切换的完整过程分为以下四步：①在绿色环境部署新版模型镜像，并配置与蓝色环境完全相同的副本数（replicas）和资源规格（CPU/内存/GPU）；②执行自动化健康检查和冒烟测试，通常包括：Readiness Probe全部就绪（等待约30~120秒）、关键接口响应时间P99 < 阈值（通常500ms）、至少100次推理请求的错误率 < 0.1%，该阶段耗时通常为2~10分钟；③执行 `kubectl patch service model-service -p '{"spec":{"selector":{"slot":"green"}}}'` 修改Service selector，完成秒级流量切换；④蓝色环境保留至少24~48小时以备回滚，期间蓝色Deployment的Pod保持运行但不接收生产流量。

### 可用性量化公式

蓝绿部署的可用性指标可以用以下公式描述。设 $T_{switch}$ 为流量切换耗时（秒），$T_{detect}$ 为问题检测耗时（秒），$T_{rollback}$ 为回滚完成耗时（秒），则最大故障暴露窗口（Maximum Blast Radius Window）为：

$$W_{blast} = T_{detect} + T_{rollback}$$

进一步地，若定义服务可用性 $A$ 为：

$$A = 1 - \frac{W_{blast}}{T_{total\_observation}}$$

其中 $T_{total\_observation}$ 为观测周期（通常取30天 = 2,592,000秒），则在 Kubernetes Service selector 切换方案中，$T_{rollback} \leq 5s$，假设 $T_{detect} = 300s$（监控告警响应时间），则 $W_{blast} = 305s$，对应可用性 $A = 1 - 305/2592000 \approx 99.9882\%$，优于三个九（99.9%）的SLA目标。

相比之下，在DNS TTL方案中，$T_{rollback}$ 取决于TTL设置，通常为60~300秒，若 $T_{rollback} = 300s$，则 $W_{blast} = 600s$，$A \approx 99.9769\%$，仍满足三个九但余量更小。因此，Kubernetes方案的 $W_{blast}$ 远小于DNS方案，这是云原生场景下优先选用Kubernetes实现蓝绿部署的核心量化依据（Burns et al., 2016）。

此外，变更失败率（Change Failure Rate, CFR）是评估蓝绿部署质量的第二个关键公式：

$$CFR = \frac{N_{failed}}{N_{total}} \times 100\%$$

其中 $N_{failed}$ 指需要回滚或紧急修复的发布次数，$N_{total}$ 指总发布次数。DORA 2023年报告显示，精英团队的CFR中位数低于5%，而采用蓝绿部署的团队因回滚路径清晰，CFR通常可从行业平均值15%~45%压缩至5%以下（Forsgren et al., 2023）。

### 数据库与状态同步的挑战

蓝绿部署最棘手的问题不在计算层，而在数据库Schema兼容性。假设模型服务v2需要新增一张 `inference_cache` 表，并对现有 `model_requests` 表新增 `model_version` 字段：若在切换前执行数据库迁移，蓝色（旧版）服务将遭遇不兼容的Schema写入操作；若切换后再迁移，则绿色服务在迁移期间功能受限。标准解法是**扩展-收缩（Expand-Contract）模式**（Richardson, 2018）：

- **第一阶段（扩展）**：以向后兼容方式扩展Schema——仅执行 `ALTER TABLE model_requests ADD COLUMN model_version VARCHAR(32) DEFAULT NULL`，不删除任何现有列。旧版蓝色服务忽略此新列，新版绿色服务写入此新列，双方共存无冲突。
- **第二阶段（切换）**：完成蓝绿流量切换，待绿色环境稳定运行72小时以上。
- **第三阶段（收缩）**：确认蓝色环境不再需要回滚后，执行第二次迁移，删除废弃字段、添加索引、修改列约束等破坏性变更。

对于AI系统中常见的特征存储（Feature Store）或模型元数据数据库，Expand-Contract模式同样适用，且必须严格遵守——跳过这一步骤是蓝绿部署失败的头号原因。在Pinterest工程团队2023年的内部复盘报告中，约43%的蓝绿回滚事故均与数据库Schema向后兼容性处理不当直接相关。

### 流量预热与连接池建立

新绿色环境在首次接收流量时存在"冷启动"风险：JVM类加载、Python模块导入（如 `import torch` 在某些环境下耗时可达15秒）、GPU显存分配（50GB模型权重的 CUDA 内存映射约需4~6分钟）、KV缓存填充等操作会导致首批请求延迟激增。解决方案是在切换前向绿色环境发送**镜像流量（Traffic Mirroring）**：Nginx 1.13.4+的 `mirror` 指令或Istio `VirtualService` 的 `mirror` 字段可将生产请求同步复制一份发往绿色环境，绿色环境处理这些镜像请求但其响应不返回给用户，对用户完全透明。

经过5~15分钟的镜像流量预热后，绿色环境的缓存命中率和平均延迟已接近稳定状态，此时再切换可将延迟抖动降低约70%。

**案例**：某推理服务（基于vLLM框架部署LLaMA-2-70B模型）在使用 Istio VirtualService 镜像流量预热10分钟后，P99延迟从切换瞬间的3,200ms降低至稳态的480ms，抖动幅度压缩了85%，且GPU显存命中率从冷启动时的12%提升至预热完成后的78%，充分体现了预热机制在大模型推理场景中的工程价值。未经预热的蓝绿切换在该服务中曾导致切换后90秒内P99超时率飙升至23%，触发了SLA违约告警。

## 关键公式与模型

### 三大核心量化指标汇总

蓝绿部署的工程质量可通过以下三个公式体系全面衡量：

**① 故障暴露窗口**（用于评估回滚速度与监控敏锐度的综合效果）：

$$W_{blast} = T_{detect} + T_{rollback}$$

**② 变更失败率**（用于纵向对比引入蓝绿部署前后的部署质量变化）：

$$CFR = \frac{N_{failed}}{N_{total}} \times 100\%$$

**③ 平均恢复时间**（MTTR，Mean Time to Restore，衡量从故障发生到服务完全恢复的时间）：

$$MTTR = \frac{\sum_{i=1}^{N_{failed}} (T_{restore,i} - T_{incident,i})}{N_{failed}}$$

其中 $T_{restore,i}$ 为第 $i$ 次事故的服务恢复时间戳，$T_{incident,i}$ 为事故开始时间戳。采用蓝绿部署后，MTTR 通常从传统部署方式的30分钟~2小时压缩至5~10分钟以内，其中实际回滚操作（修改Kubernetes Service selector）耗时不超过30秒，大部分时间用于问题发现与决策（Forsgren et al., 2023）。

### 资源成本模型

蓝绿部署的主要代价是切换窗口期的资源翻倍成本。设单套生产环境的计算资源成本为 $C_{single}$（包含 $n$ 个GPU节点，每节点每小时费用为 $p_{gpu}$），则双环境并行期间的额外成本为：

$$C_{extra} = C_{single} \times \frac{T_{warmup} + T_{hold}}{T_{billing\_cycle}}$$

其中 $T_{warmup}$ 为绿色环境预热时间（通常10~30分钟），$T_{hold}$ 为切换后蓝色环境保留时间（通常24~48小时）。以AWS p3.8xlarge实例（4×V100 GPU，按需价格约$12.24/小时）为例，若 $T_{hold} = 48h$，则每次蓝绿部署周期的额外GPU成本约为 $12.24 \times 48 \approx \$587.5$。对于发布频率每周一次的团队，月额外成本约 $\$2,350$，这是选择蓝绿方案时必须纳入TCO（总拥有成本）评估的关键数字。

若希望降低成本，可采用**延迟缩容策略**：切换完成后立即将蓝色环境副本