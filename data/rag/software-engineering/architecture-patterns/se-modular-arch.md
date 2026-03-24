---
id: "se-modular-arch"
concept: "模块化架构"
domain: "software-engineering"
subdomain: "architecture-patterns"
subdomain_name: "架构模式"
difficulty: 2
is_milestone: false
tags: ["原则"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 模块化架构

## 概述

模块化架构是一种将软件系统分解为独立、可替换的功能单元（模块）的设计方法，每个模块封装特定的业务逻辑或技术能力，并通过明确定义的接口与其他模块交互。模块的边界由"高内聚、低耦合"原则决定——模块内部的元素紧密协作完成单一职责（高内聚），而模块之间的依赖关系尽可能少且稳定（低耦合）。

模块化思想最早可追溯至1972年David Parnas在论文《On the Criteria To Be Used in Decomposing Systems into Modules》中提出的信息隐藏（Information Hiding）原则。Parnas指出，模块分解的标准不应是执行步骤，而应是"可能发生变化的设计决策"——将每个易变决策封装在一个模块中，使变化不扩散到系统其他部分。这篇论文奠定了现代模块化架构理论的基础。

模块化架构在软件工程中的价值体现在两个可量化维度：一是并行开发效率——不同团队可同时开发不相互依赖的模块；二是变更影响范围——理想情况下修改一个模块只需回归测试该模块及其直接调用者，而非整个系统。

## 核心原理

### 内聚度量：LCOM指标

模块内聚性可用LCOM（Lack of Cohesion of Methods）指标衡量。以LCOM4版本为例，其值等于模块内方法与属性构成的连通图中不相连的子图数量。LCOM4 = 1 表示该模块所有方法共享数据关联，内聚性最高；LCOM4 > 1 则提示该模块实际承担了多个独立职责，应拆分为多个模块。例如一个同时处理用户认证和用户资料展示的`UserModule`，其认证方法组与展示方法组通常不共享字段，LCOM4 = 2，说明应拆分为`AuthModule`和`UserProfileModule`。

### 耦合类型与强度排序

模块间耦合按强度从高到低分为七级：内容耦合（一个模块直接修改另一个模块的内部数据）、公共耦合（多个模块共享全局变量）、外部耦合（依赖外部I/O格式）、控制耦合（传递控制标志位）、标记耦合（传递数据结构但只使用部分字段）、数据耦合（仅传递必要的基本数据）、无耦合。架构设计的目标是将模块间耦合降至数据耦合级别，彻底消除内容耦合和公共耦合。

### 模块接口契约

模块间通信必须通过显式接口进行，接口定义包含三个要素：签名（方法名、参数类型、返回类型）、前置条件（调用方在调用前需满足的约束）、后置条件（模块承诺在调用后保证的结果）。以支付模块为例，`processPayment(orderId: String, amount: Decimal): PaymentResult`的后置条件可定义为"若返回SUCCESS，则订单金额已从账户扣除且交易记录已持久化"。这种契约设计使模块可以独立测试，无需依赖其他模块的真实实现。

### 扇入与扇出控制

扇入（Fan-in）指调用某模块的其他模块数量，扇出（Fan-out）指某模块调用的其他模块数量。高扇入模块（如通用工具模块）说明复用性好；高扇出模块则意味着该模块职责过重、依赖过多，是架构的脆弱点。经验法则建议单个模块的扇出不超过7，超过时应引入中间模块或将部分职责下移。

## 实际应用

**Java包结构中的模块化**：在Spring Boot项目中，典型的模块化结构按业务域划分包，例如`com.example.order`、`com.example.inventory`、`com.example.payment`，每个包内包含该业务域的Controller、Service、Repository和领域对象。包之间的依赖通过Service接口而非实现类引用，这样替换`PaymentService`的实现不影响`OrderService`的编译。

**JavaScript的ES Module系统**：ES2015引入的`import/export`语法强制模块显式声明依赖和导出内容，取代了CommonJS的`require`全局函数。这种设计使构建工具（如Webpack、Rollup）可以通过树摇（Tree Shaking）分析模块依赖图，剔除未被任何模块导入的导出，减少最终打包体积。

**Android的多模块工程**：大型Android应用采用Gradle多模块结构，将`:feature:login`、`:feature:payment`、`:core:network`等模块分离编译。增量编译只重新编译变更模块及其下游依赖，在拥有数百个模块的工程中，全量构建时间可从30分钟缩短至3分钟以内。

## 常见误区

**误区一：按技术层而非业务域分模块**。许多项目将所有Controller放入`web`模块、所有Service放入`service`模块、所有Repository放入`dao`模块。这种分法导致添加一个新业务功能（如"优惠券"）时需要同时修改三个模块，违背了模块化"变化局部化"的初衷。正确做法是按业务域（订单、库存、优惠券）划分模块，每个模块自包含其Web层、业务层和数据层。

**误区二：将"模块化"等同于"文件拆分"**。仅仅将代码分散到多个文件或类并不是模块化。若这些文件之间存在大量双向依赖（A调用B，B又调用A），模块间出现循环依赖，则整个系统实际上仍是一个紧耦合的整体。模块化架构要求依赖关系是有向无环图（DAG），可通过`mvn dependency:analyze`或`ArchUnit`等工具检测循环依赖。

**误区三：过度模块化导致碎片化**。将每个函数或每个数据对象都拆分为独立模块，会使模块间通信开销超过其带来的隔离收益。当一个功能点的修改需要同时改动5个以上小模块时，说明模块粒度过细，应按内聚原则重新合并相关模块。

## 知识关联

模块化架构以软件架构概述中的关注点分离（Separation of Concerns）原则为基础——模块化是该原则在代码组织层面的具体实现手段。理解模块化架构中的接口契约和依赖倒置规则，是学习微服务架构的必要准备：微服务可理解为将模块化架构中的物理模块边界扩展为独立部署的网络服务边界，两者共享相同的高内聚低耦合设计目标，但微服务额外引入了网络延迟、分布式事务和服务发现等复杂性，这些复杂性在单体模块化系统中不会出现。
