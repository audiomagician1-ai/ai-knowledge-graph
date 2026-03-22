from pathlib import Path
ROOT = Path(r"D:\EchoAgent\projects\ai-knowledge-graph\data\rag")
docs = {}

docs["philosophy/logic-reasoning/propositional-logic.md"] = '''---
id: "propositional-logic"
concept: "命题逻辑"
domain: "philosophy"
subdomain: "logic-reasoning"
subdomain_name: "逻辑与推理"
difficulty: 3
is_milestone: false
tags: ["核心"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.94
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Hurley, Patrick J. A Concise Introduction to Logic, 13th Ed., Ch.6-7"
  - type: "textbook"
    ref: "Enderton, Herbert. A Mathematical Introduction to Logic, 2nd Ed., 2001"
  - type: "academic"
    ref: "Boole, George. An Investigation of the Laws of Thought, 1854"
scorer_version: "scorer-v2.0"
---
# 命题逻辑

## 概述

命题逻辑（Propositional Logic, 又称命题演算）是形式逻辑最基础的分支，研究**命题（Proposition）之间通过逻辑联结词组合后的真值关系**。一个命题是一个有确定真假值的陈述句——"地球是圆的"（真）、"2 + 2 = 5"（假）。

George Boole（1854）在《思维法则的探究》中首次将逻辑系统化为代数运算，创立了布尔代数——这一成果在 80 年后被 Claude Shannon 应用于电路设计，直接催生了数字计算机。命题逻辑是整个现代逻辑学、计算机科学（电路设计、编程语言、SAT 求解器）和 AI 推理的基石。

## 核心知识点

### 1. 逻辑联结词（Logical Connectives）

设 p, q 为命题：

| 联结词 | 符号 | 读法 | 真值条件 |
|--------|------|------|---------|
| **否定** | NOT p | "非 p" | p 为真时结果为假，反之亦然 |
| **合取** | p AND q | "p 且 q" | 两者都真时才真 |
| **析取** | p OR q | "p 或 q" | 至少一个为真则真（包容性） |
| **蕴含** | p -> q | "若 p 则 q" | 仅当 p 真 q 假时为假 |
| **双条件** | p <-> q | "p 当且仅当 q" | 两者真值相同时为真 |

**蕴含的反直觉性**：p -> q 在 p 为假时**永远为真**（"空真"）。"如果月亮是方的，那么 2+2=5" 在逻辑上为真。这是因为蕴含只承诺"在前件成立时后件也成立"——前件不成立时，承诺自动满足。

### 2. 真值表方法

真值表穷举所有可能的真值组合来判断复合命题的真假。

**示例**：验证 NOT (p AND q) 等价于 (NOT p) OR (NOT q)（德摩根定律）

| p | q | p AND q | NOT(p AND q) | NOT p | NOT q | (NOT p) OR (NOT q) |
|---|---|---------|--------------|-------|-------|-------------------|
| T | T | T | F | F | F | F |
| T | F | F | T | F | T | T |
| F | T | F | T | T | F | T |
| F | F | F | T | T | T | T |

第 4 列与第 7 列完全相同，证毕。

### 3. 重要逻辑等价与推理规则

**逻辑等价**：
- **德摩根定律**：NOT(p AND q) = (NOT p) OR (NOT q); NOT(p OR q) = (NOT p) AND (NOT q)
- **逆否命题**：p -> q 等价于 NOT q -> NOT p
- **双重否定**：NOT(NOT p) = p
- **分配律**：p AND (q OR r) = (p AND q) OR (p AND r)

**关键推理规则**：
- **肯定前件**（Modus Ponens）：p -> q, p，所以 q
- **否定后件**（Modus Tollens）：p -> q, NOT q，所以 NOT p
- **假言三段论**：p -> q, q -> r，所以 p -> r
- **析取三段论**：p OR q, NOT p，所以 q

### 4. 重言式、矛盾式与可满足式

- **重言式**（Tautology）：在所有真值赋值下都为真。例：p OR (NOT p)
- **矛盾式**（Contradiction）：在所有真值赋值下都为假。例：p AND (NOT p)
- **可满足式**（Satisfiable）：至少存在一种赋值使其为真

**SAT 问题**：判断一个命题公式是否可满足——这是计算机科学中第一个被证明为 NP-Complete 的问题（Cook-Levin 定理，1971）。现代 SAT 求解器可以处理数百万变量的实例，广泛用于芯片验证、AI 规划和密码分析。

## 关键原理分析

### 命题逻辑的完备性与局限

**完备性**：命题逻辑的推理系统是完备的——所有重言式都可以通过形式推导证明（反之亦然）。

**局限性**：命题逻辑无法表达变量和量词。"所有人都会死"和"苏格拉底是人"无法在命题逻辑中推出"苏格拉底会死"——这需要**谓词逻辑**（增加全称量词和存在量词）。

### 与编程的直接关联

编程中的 `if-else`、`&&`、`||`、`!` 就是命题逻辑联结词的直接实现。布尔表达式求值、短路求值（Short-Circuit Evaluation）、条件编译都是命题逻辑的应用。

## 实践练习

**练习 1**：用真值表验证：(p -> q) 等价于 (NOT p) OR q。

**练习 2**：将以下自然语言论证形式化为命题逻辑并验证有效性："如果下雨，地面就会湿。地面没有湿。所以没有下雨。"

## 常见误区

1. **混淆"或"的含义**：逻辑的 OR 是包容性的（两者可以同时为真），日常语言中"茶或咖啡？"通常是排斥性的
2. **否定蕴含的方向**：p -> q 的否定不是 NOT p -> NOT q（否命题），而是 p AND (NOT q)
3. **"蕴含 = 因果"**：逻辑蕴含只是真值关系，不要求 p 与 q 之间有因果联系
'''

docs["product-design/data-driven/funnel-analysis.md"] = '''---
id: "funnel-analysis"
concept: "漏斗分析"
domain: "product-design"
subdomain: "data-driven"
subdomain_name: "数据驱动"
difficulty: 3
is_milestone: false
tags: ["分析"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "industry"
    ref: "Croll, Alistair & Yoskovitz, Benjamin. Lean Analytics, O'Reilly, 2013"
  - type: "industry"
    ref: "McClure, Dave. Startup Metrics for Pirates (AARRR), 2007"
  - type: "industry"
    ref: "Amplitude Analytics Documentation: Funnel Analysis, 2024"
  - type: "academic"
    ref: "Kohavi, Ron et al. Trustworthy Online Controlled Experiments, Cambridge UP, 2020"
scorer_version: "scorer-v2.0"
---
# 漏斗分析

## 概述

漏斗分析（Funnel Analysis）是追踪用户在一系列**预定义步骤**中的转化率，定位流失环节的数据分析方法。之所以称为"漏斗"，是因为每一步都会有用户流失，用户数量从上到下逐渐减少，形状如同漏斗。

Dave McClure（2007）提出的 **AARRR 海盗指标**框架将用户生命周期分为五个漏斗层级：**获客（Acquisition）→ 激活（Activation）→ 留存（Retention）→ 收入（Revenue）→ 推荐（Referral）**。每一层的转化率是产品健康度的核心诊断指标。

Croll & Yoskovitz（2013）指出：**产品增长的最大杠杆通常不在漏斗顶部（获取更多用户），而在漏斗中部（提升转化率）**。将注册-激活转化率从 10% 提升到 20%，等效于获客量翻倍，但成本通常低一个数量级。

## 核心知识点

### 1. 漏斗构建方法论

**步骤定义原则**：
1. **关键行为**：每一步必须是用户的明确操作（点击、提交、支付），而非被动状态
2. **顺序性**：步骤之间有合理的时间和逻辑顺序
3. **完整性**：覆盖从首次接触到核心价值实现的全路径
4. **粒度适当**：步骤太多导致每步转化率虚高（看起来都很好），步骤太少无法定位问题

**电商漏斗经典模型**：

| 步骤 | 典型转化率 | 关键指标 |
|------|-----------|---------|
| 访问网站 | 100% (基准) | UV/PV |
| 浏览商品 | 60-80% | 跳出率 |
| 加入购物车 | 8-15% | 加购率 |
| 开始结算 | 40-60% (of加购) | 结算率 |
| 完成支付 | 60-80% (of结算) | 支付成功率 |
| 总转化率 | 2-5% | 端到端 CVR |

### 2. 漏斗诊断框架

**流失归因四步法**：
1. **定量**：找到转化率最低的步骤（最大流失点）
2. **分群**：按用户属性（新/老、渠道、设备）拆分该步骤的转化率
3. **定性**：用户访谈/热力图/会话回放理解为什么流失
4. **验证**：A/B 测试验证改进方案的因果效果

**常见流失原因矩阵**：

| 漏斗位置 | 常见原因 | 诊断信号 |
|---------|---------|---------|
| 顶部（获客->激活） | 价值主张不清晰、首页加载慢 | 高跳出率、首屏停留 < 3s |
| 中部（激活->留存） | 新手引导缺失、核心功能发现困难 | D1 留存低、功能使用率 < 10% |
| 底部（留存->付费） | 定价不匹配、付费价值感不足 | 付费转化率低但使用频率高 |

### 3. 高级漏斗技术

**时间窗口漏斗**：
用户不一定在一次会话中完成所有步骤。设置合理的转化窗口（如 7 天内完成注册->首次购买）比严格的会话内漏斗更真实反映用户行为。

**分支漏斗**：
用户路径不一定线性。例如电商用户可能"浏览->收藏->离开->返回->购买"。分支漏斗追踪多条可能的路径及其各自的转化率。

**漏斗对比**：
- **时间对比**：本周 vs 上周的漏斗变化（feature launch 的效果评估）
- **分群对比**：iOS vs Android 用户的转化差异（平台适配问题）
- **A/B 对比**：实验组 vs 对照组在每一步的转化率差异（Kohavi et al., 2020）

### 4. 漏斗指标体系

| 指标 | 公式 | 用途 |
|------|------|------|
| **步骤转化率** | 完成本步 / 完成上一步 | 定位单步瓶颈 |
| **端到端转化率** | 最终转化 / 漏斗入口 | 整体效率 |
| **流失率** | 1 - 步骤转化率 | 每步损失量 |
| **平均完成时长** | 步骤间的中位时间差 | 发现卡点（时间异常长的步骤） |
| **回访转化率** | 流失后 N 天内返回完成的比例 | 评估召回策略效果 |

## 关键原理分析

### 漏斗分析的局限

漏斗假设用户路径是**线性且单向**的，但现实中用户行为是非线性的——他们会跳步、回退、多设备切换。过度依赖漏斗可能导致"优化局部忽略全局"（如过度优化结算页而忽略了商品页的信息不足才是真正原因）。

### 统计显著性

漏斗对比需要足够的样本量。两个漏斗步骤转化率的差异可能只是随机波动。Kohavi et al.（2020）建议至少 **1000 个样本/组** 才能可靠检测 5% 的相对变化。

## 实践练习

**练习 1**：为一个 SaaS 产品设计注册到付费的 5 步漏斗，定义每步的触发事件和预期转化率。

**练习 2**：给定以下数据（访问 10000, 注册 2000, 激活 800, 付费 120），计算每步转化率和端到端转化率。如果只能优化一步，你会选哪一步？为什么？

## 常见误区

1. **只看端到端转化率**：一个数字无法指导行动，必须拆解到每一步才能定位问题
2. **漏斗步骤过多**：7+ 步的漏斗每步都看似"还行"（80%+），但端到端只有 20%
3. **忽略时间维度**：月度漏斗可能隐藏了某周的急剧变化（如服务器故障）
'''

docs["software-engineering/architecture-patterns/se-microservices.md"] = '''---
id: "se-microservices"
concept: "微服务架构"
domain: "software-engineering"
subdomain: "architecture-patterns"
subdomain_name: "架构模式"
difficulty: 5
is_milestone: false
tags: ["架构"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "academic"
    ref: "Newman, Sam. Building Microservices, 2nd Ed., O'Reilly, 2021"
  - type: "academic"
    ref: "Richardson, Chris. Microservices Patterns, Manning, 2018"
  - type: "industry"
    ref: "Fowler, Martin. Microservices (martinfowler.com), 2014"
  - type: "industry"
    ref: "Amazon Builder's Library: Avoiding fallback in distributed systems, 2023"
scorer_version: "scorer-v2.0"
---
# 微服务架构

## 概述

微服务架构（Microservices Architecture）是一种将应用程序构建为**一组小型、自治服务**的架构风格，每个服务围绕特定业务能力构建，通过轻量级协议（通常是 HTTP/REST 或 gRPC）通信，可以独立部署和扩展。

Martin Fowler（2014）将微服务定义为"一种将单一应用开发为一套小服务的方法，每个服务运行在自己的进程中"。Sam Newman（2021）进一步强调：微服务的核心价值不是技术上的"拆分"，而是组织上的"自治"——每个团队可以独立决策、独立发布、独立演进。

**关键权衡**：微服务用**运维复杂度**换取了**开发敏捷性**。Netflix、Amazon、Uber 等公司的成功案例表明，当组织规模超过 100+ 工程师时，微服务的收益开始超过成本。但对于小团队（< 20 人），单体架构（Monolith）几乎总是更好的起点。

## 核心知识点

### 1. 微服务 vs 单体 vs SOA

| 特征 | 单体 | SOA | 微服务 |
|------|------|-----|--------|
| **部署单位** | 整个应用 | 服务组 | 单个服务 |
| **数据库** | 共享 | 可共享 | 每服务独享 |
| **通信** | 函数调用 | ESB（企业服务总线） | REST/gRPC/消息队列 |
| **团队结构** | 按技术层分组 | 按项目分组 | 按业务领域分组 |
| **技术栈** | 统一 | 部分灵活 | 完全自主 |
| **复杂度** | 代码复杂 | 中间件复杂 | 运维复杂 |

### 2. 核心设计原则

**单一职责**：每个微服务对应一个**限界上下文**（Bounded Context, DDD 概念）。"订单服务"只管订单，"用户服务"只管用户。跨越两个上下文的功能拆分为两个服务。

**数据库独立**（Database per Service）：
- 每个服务拥有自己的数据库（可以是不同类型——MySQL、MongoDB、Redis）
- 服务之间通过 API 访问数据，不直接查询对方数据库
- 代价：跨服务查询变得复杂（需要 API Composition 或 CQRS）

**可独立部署**：修改服务 A 时不需要重新部署服务 B。这要求严格的 API 版本管理和向后兼容。

### 3. 关键基础设施

| 组件 | 功能 | 工具示例 |
|------|------|---------|
| **API 网关** | 路由、认证、限流、协议转换 | Kong, Envoy, AWS API Gateway |
| **服务发现** | 动态定位服务实例 | Consul, Eureka, K8s DNS |
| **负载均衡** | 分发请求到多个实例 | Nginx, Envoy, K8s Service |
| **配置中心** | 集中管理配置 | Consul KV, Spring Cloud Config |
| **消息队列** | 异步通信、解耦 | Kafka, RabbitMQ, SQS |
| **链路追踪** | 跨服务请求可观测性 | Jaeger, Zipkin, OpenTelemetry |
| **容器编排** | 部署、扩缩容、健康检查 | Kubernetes, Docker Swarm |

### 4. 通信模式

**同步通信**：
- REST/HTTP：最简单、最通用，适合 CRUD 操作
- gRPC：高性能二进制协议，适合内部服务间通信（延迟降低 3-10x vs REST）
- 问题：请求链过长时延迟累积，一个服务超时可能导致级联故障

**异步通信**：
- **事件驱动**：服务发布事件（"订单已创建"），感兴趣的服务订阅处理
- **消息队列**：生产者发送消息到队列，消费者按自己的速度处理
- 优势：服务完全解耦，天然支持最终一致性
- 代价：调试困难、消息顺序和幂等性需要额外处理

### 5. 分布式事务

微服务环境下，跨服务的 ACID 事务不可行（每个服务有独立数据库）。解决方案：

**Saga 模式**（Richardson, 2018）：
将分布式事务拆解为一系列本地事务，每个本地事务有对应的补偿操作：
1. 订单服务：创建订单（补偿：取消订单）
2. 支付服务：扣款（补偿：退款）
3. 库存服务：扣减库存（补偿：恢复库存）

任何一步失败，按反向顺序执行补偿操作。

## 关键原理分析

### Conway 定律

"系统的架构反映组织的沟通结构。"微服务架构成功的前提是组织结构的匹配——如果团队边界不与服务边界对齐，跨团队协调成本会抵消微服务的所有好处。Amazon 的"两个披萨团队"原则（每个团队小到两个披萨能喂饱）就是 Conway 定律的实践。

### 分布式系统的谬误

Peter Deutsch 的"分布式计算的八大谬误"提醒我们：网络是不可靠的、延迟不为零、带宽是有限的。微服务将这些问题从"可能遇到"变成了"必然遇到"——每一个服务间调用都可能失败、超时或返回错误数据。

## 实践练习

**练习 1**：将一个电商单体应用拆分为微服务。画出服务边界、数据库归属和通信协议。至少识别 5 个服务。

**练习 2**：为"用户下单"流程设计一个 Saga，包含订单、支付、库存三个服务，写出正常流程和任意一步失败时的补偿流程。

## 常见误区

1. **"微服务是银弹"**：对于 < 20 人的团队，微服务的运维开销远超其收益。从单体开始，需要时再拆
2. **"服务越小越好"**：过度拆分导致"分布式单体"——每次修改都要改多个服务，还不如单体
3. **忽略可观测性**：没有链路追踪和集中日志，微服务系统出问题时几乎无法调试
'''

docs["mathematics/calculus/definite-integrals.md"] = '''---
id: "definite-integrals"
concept: "定积分"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 6
is_milestone: false
tags: ["核心"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.94
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Stewart, James. Calculus: Early Transcendentals, 9th Ed., Ch.5"
  - type: "textbook"
    ref: "Spivak, Michael. Calculus, 4th Ed., Ch.13-14"
  - type: "academic"
    ref: "Bressoud, David. A Radical Approach to Real Analysis, 2nd Ed., MAA, 2007"
scorer_version: "scorer-v2.0"
---
# 定积分

## 概述

定积分（Definite Integral）是微积分两大核心概念之一（另一个是导数），用于计算**曲线下方的有向面积**、物理量的累积（位移、功、电荷）以及无穷多个无穷小量之和。

直觉上，从 a 到 b 对 f(x) 的定积分 = 将区间 [a,b] 分成 n 个极细的矩形条，每个矩形的面积是 f(x_i) * dx，然后将所有矩形面积求和并让宽度趋近于零。这个极限过程——**黎曼和的极限**——就是定积分的严格定义。

微积分基本定理（Newton-Leibniz）建立了定积分与不定积分（反导数）之间的桥梁：Integral from a to b of f(x)dx = F(b) - F(a)，其中 F'(x) = f(x)。这个定理被誉为"人类智慧最伟大的成就之一"（Spivak），因为它将求面积问题（几何/极限）转化为求反导数问题（代数）。

## 核心知识点

### 1. 黎曼和与定积分定义

**分割**：将 [a,b] 分成 n 个子区间 [x_{i-1}, x_i]，宽度 Delta_x_i = x_i - x_{i-1}。

**黎曼和**：S_n = Sum(i=1 to n) f(c_i) * Delta_x_i，其中 c_i 是 [x_{i-1}, x_i] 中任意一点。

**定积分**：当分割越来越细（所有 Delta_x_i -> 0）时，如果 S_n 趋向同一个极限值，则该极限就是定积分：
Integral(a to b) f(x) dx = lim(max Delta_x_i -> 0) S_n

**存在性**：如果 f 在 [a,b] 上连续，则定积分必定存在（Riemann 可积）。

### 2. 定积分的基本性质

| 性质 | 公式 | 直觉 |
|------|------|------|
| **线性** | Integral(af + bg) = a*Integral(f) + b*Integral(g) | 面积的加法和缩放 |
| **区间可加** | Integral(a to b) + Integral(b to c) = Integral(a to c) | 拼接区间 |
| **反向积分** | Integral(b to a) = -Integral(a to b) | 方向反转取负 |
| **保序性** | 若 f(x) >= g(x)，则 Integral(f) >= Integral(g) | 大函数面积更大 |
| **绝对值不等式** | |Integral(f)| <= Integral(|f|) | 有向面积可能相消 |

### 3. 微积分基本定理

**第一部分**（积分的导数）：
如果 F(x) = Integral(a to x) f(t) dt，则 F'(x) = f(x)

意义：积分作为上限的函数，其导数就是被积函数本身。积分与微分互为逆运算。

**第二部分**（Newton-Leibniz 公式）：
如果 F'(x) = f(x) 在 [a,b] 上成立，则
Integral(a to b) f(x) dx = F(b) - F(a)

**计算示例**：
Integral(0 to 1) x^2 dx = [x^3/3] from 0 to 1 = 1/3 - 0 = 1/3

不需要极限过程，只需找到反导数 F(x) = x^3/3 并代入端点。

### 4. 积分计算技巧

**换元法**（Substitution）：
令 u = g(x)，则 Integral f(g(x))*g'(x) dx = Integral f(u) du
- 更换积分上下限：x=a 时 u=g(a)，x=b 时 u=g(b)

**分部积分**（Integration by Parts）：
Integral(a to b) u dv = [uv](a to b) - Integral(a to b) v du
- 选择原则（LIATE）：对数 > 反三角 > 代数 > 三角 > 指数（选前面的做 u）

**特殊技巧**：
- 偶函数在 [-a, a] 上积分 = 2 * Integral(0 to a)
- 奇函数在 [-a, a] 上积分 = 0
- 周期函数在一个完整周期上积分与起点无关

### 5. 定积分的应用

| 应用 | 公式 | 物理含义 |
|------|------|---------|
| **面积** | Integral(a to b) |f(x)| dx | 曲线与 x 轴围成面积 |
| **位移** | Integral(t1 to t2) v(t) dt | 速度对时间的累积 |
| **做功** | Integral(x1 to x2) F(x) dx | 变力沿路径的能量传递 |
| **平均值** | (1/(b-a)) * Integral(a to b) f(x) dx | 函数在区间上的平均高度 |
| **弧长** | Integral(a to b) sqrt(1 + (f'(x))^2) dx | 曲线的总长度 |

## 关键原理分析

### 定积分的本质：无穷小量的求和

莱布尼兹用 Integral 符号（拉长的 S = Summa）和 dx（无穷小量）表达了定积分的核心思想：它是"连续求和"。离散求和 Sum 对应连续的 Integral，增量 Delta x 对应微分 dx。

### 数值积分

当被积函数没有封闭反导数时（如 e^(-x^2)），需要数值方法：
- **梯形法则**：将曲线下方近似为梯形
- **辛普森法则**：用抛物线段近似，精度更高（误差 ~ O(h^4)）
- 现代计算中，高斯求积法和自适应算法可以高效处理几乎所有一维积分

## 实践练习

**练习 1**：计算 Integral(0 to pi) sin(x) dx 的几何含义（面积），并用 Newton-Leibniz 公式验证。

**练习 2**：用分部积分计算 Integral(0 to 1) x * e^x dx。

## 常见误区

1. **"积分 = 面积"**：定积分是**有向面积**，x 轴下方的部分取负值。要求无向面积需加绝对值
2. **忘记换元时更换上下限**：换元后必须将积分上下限从 x 转换为 u
3. **忽略不连续点**：如果 f 在 [a,b] 内有不连续点，需要拆成多个区间分别积分
'''

docs["finance/fixed-income/bond-basics.md"] = '''---
id: "bond-basics"
concept: "债券基础"
domain: "finance"
subdomain: "fixed-income"
subdomain_name: "固定收益"
difficulty: 3
is_milestone: false
tags: ["基础"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Fabozzi, Frank J. Bond Markets, Analysis, and Strategies, 10th Ed., Ch.1-4"
  - type: "textbook"
    ref: "Bodie, Kane & Marcus. Investments, 12th Ed., Ch.14"
  - type: "industry"
    ref: "CFA Institute. Fixed Income Analysis, 4th Ed., CFA Program Curriculum"
scorer_version: "scorer-v2.0"
---
# 债券基础

## 概述

债券（Bond）是发行人向投资者借款的**标准化债务合同**，承诺在约定期限内支付利息，并在到期时偿还本金。它是全球资本市场中规模最大的资产类别——截至 2024 年，全球债券市场规模超过 **130 万亿美元**，是股票市场的约 1.2 倍（SIFMA, 2024）。

Fabozzi（2021）指出，理解债券的核心是理解**时间价值**（Time Value of Money）和**信用风险**（Credit Risk）：债券的价格等于未来所有现金流的**贴现现值之和**，而贴现率反映了投资者要求的风险补偿。

## 核心知识点

### 1. 债券的基本要素

| 要素 | 定义 | 示例 |
|------|------|------|
| **面值**（Face Value/Par） | 到期偿还的金额 | 通常 $1,000 或 RMB 100 |
| **票面利率**（Coupon Rate） | 年利息 / 面值 | 5% 表示每年付 $50 |
| **到期日**（Maturity） | 偿还本金的日期 | 2034年3月22日 |
| **发行人**（Issuer） | 借款方 | 政府、公司、金融机构 |
| **付息频率** | 每年付息次数 | 年付、半年付、季付 |

### 2. 债券定价：贴现现金流模型

债券价格 = 所有未来现金流的现值之和：

P = C/(1+r) + C/(1+r)^2 + ... + C/(1+r)^n + FV/(1+r)^n

其中 C = 每期利息，FV = 面值，r = 每期要求回报率，n = 期数。

**定价示例**：面值 $1000，票面利率 5%（半年付），3 年期，市场利率 6%。
- 每半年利息 = $25，共 6 期，每期贴现率 = 3%
- P = 25/1.03 + 25/1.03^2 + ... + 25/1.03^6 + 1000/1.03^6 = $972.91

### 3. 价格-收益率关系

**核心定律**：债券价格与收益率**反向变动**。

| 市场利率变化 | 债券价格 | 原因 |
|-------------|---------|------|
| 利率上升 | 价格下跌 | 新债券提供更高利息，旧债券相对贬值 |
| 利率下降 | 价格上涨 | 旧债券的高利息更有吸引力 |

**三个关键收益率概念**：
- **当期收益率**（Current Yield）= 年利息 / 当前价格
- **到期收益率**（YTM）= 使债券价格等于所有现金流现值的贴现率（内部收益率）
- **即期收益率**（Spot Rate）= 零息债券的到期收益率

**溢价/折价/平价**：
- 票面利率 > 市场利率 → 价格 > 面值（**溢价**）
- 票面利率 < 市场利率 → 价格 < 面值（**折价**）
- 票面利率 = 市场利率 → 价格 = 面值（**平价**）

### 4. 信用风险与评级

| 评级机构 | 投资级 | 高收益（"垃圾债"） | 含义 |
|---------|--------|------------------|------|
| **S&P/Fitch** | AAA 到 BBB- | BB+ 到 D | D = 违约 |
| **Moody's** | Aaa 到 Baa3 | Ba1 到 C | C = 极高风险 |

**信用利差**（Credit Spread）= 公司债收益率 - 同期限国债收益率。反映市场对违约风险的定价。例：BBB 级公司债利差约 100-200bps（1-2 个百分点）。

**历史违约率**（Moody's 1920-2023 数据）：
- AAA 级：5 年累计违约率 < 0.1%
- BBB 级：5 年累计约 1.5%
- B 级：5 年累计约 20%

### 5. 利率风险与久期

**久期**（Duration）衡量债券价格对利率变动的敏感度：

Delta P / P 约等于 -D * Delta r

其中 D 是修正久期，Delta r 是利率变动。

**久期影响因素**：
- 期限越长，久期越大（利率敏感度越高）
- 票面利率越低，久期越大（更多价值集中在远期本金）
- 零息债券的久期 = 到期时间（最大利率敏感度）

**实际案例**：2022 年美联储加息周期中，长期美国国债（20+ 年）价格下跌超过 **30%**，而短期国债（1-3 年）仅下跌 3-5%——这就是久期差异的直接体现。

## 关键原理分析

### 债券 vs 股票

债券和股票是企业融资的两种基本方式。债券是**固定承诺**（必须还本付息），股票是**剩余索取权**（分红不确定）。从投资者角度：债券风险较低但回报有限，股票风险较高但上不封顶。资产配置的核心就是在两者之间找到与个人风险承受能力匹配的比例。

### 收益率曲线

不同期限的即期收益率绘制成曲线——**正常曲线**（长期利率 > 短期，反映期限溢价）、**倒挂曲线**（短期 > 长期，常预示经济衰退）、**平坦曲线**（各期限相近）。收益率曲线是宏观经济最重要的信号之一。

## 实践练习

**练习 1**：面值 $1000，票面利率 4%（年付），5 年期，市场利率为 3%。计算债券价格。它是溢价还是折价？

**练习 2**：两只债券 A（票面 6%, 10 年期）和 B（票面 2%, 10 年期），哪只的利率敏感度更高？为什么？

## 常见误区

1. **"债券没有风险"**：利率上升时债券价格下跌，长期债券的价格波动可以与股票相当
2. **混淆票面利率与收益率**：票面利率在发行时确定不变，收益率随市场价格变化
3. **"高收益债券更好"**：高收益通常意味着高违约风险。收益是风险的补偿，不是免费的午餐
'''

for rel_path, content in docs.items():
    full = ROOT / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content.strip(), encoding="utf-8")
    print(f"OK {rel_path}")

print("\n8-deps Batch 2 done (10/15)")
