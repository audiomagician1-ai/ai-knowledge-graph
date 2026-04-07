---
id: "se-test-before-refactor"
concept: "重构前加测试"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: false
tags: ["测试"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 重构前加测试

## 概述

重构前加测试是指在对遗留代码或未经充分测试的代码进行结构改造之前，先补充编写测试用例以保证重构过程的安全性。这一实践的核心动机来自 Michael Feathers 在其2004年著作《修改代码的艺术》（*Working Effectively with Legacy Code*）中提出的"接缝"（Seam）理论：只有当代码行为被测试"锁定"之后，才能放心地修改其内部结构而不担心引入回归缺陷。

与 TDD（测试驱动开发）的"先写测试再写代码"不同，重构前加测试是"先理解行为再补写测试"。在 TDD 场景下，测试是对意图的描述；而在重构前加测试场景下，测试是对现有行为的**描述性记录**，英文术语称为 Characterization Test（特征测试），目的不是验证行为是否正确，而是确保重构前后行为一致。

这一实践在工程上极为重要：研究表明，超过80%的软件开发时间花在维护和修改已有代码上，而许多遗留系统几乎没有自动化测试覆盖。没有测试保护的重构如同蒙眼拆除承重墙，即使步骤看似合理，任何一个遗漏的细节都可能导致线上故障。

---

## 核心原理

### Characterization Test 的编写方法

Characterization Test 的写法与普通单元测试在结构上相同（Arrange-Act-Assert），但其 Assert 阶段的目的是**记录系统当前实际输出，而非预期的正确输出**。具体步骤为：

1. 调用目标函数，将其实际返回值打印或断言为某个占位值；
2. 运行测试，观察实际输出（无论对错）；
3. 将实际输出写入断言，使测试通过；
4. 该测试从此成为行为"快照"，任何重构导致输出变化时，测试立即失败并报警。

例如，某遗留函数 `calculateDiscount(user, cart)` 对特定输入返回 `42.5`，即便我们不确定这个值是否符合业务规则，也应将 `assertEquals(42.5, calculateDiscount(user, cart))` 写入测试——这把"可能存在的 bug"也一并保留，防止重构意外改变了它（改 bug 应在重构完成后单独处理）。

### 安全网的覆盖度要求

重构前的测试安全网需要达到足够的**分支覆盖率**，而非仅仅行覆盖率。Martin Fowler 在《重构：改善既有代码的设计》第2版中建议，重构前应确保被修改代码路径的**条件分支覆盖率达到100%**，因为行覆盖率为100%的代码仍可能在不同条件组合下表现不一致。

对于含有 `if-else`、`switch` 或循环的函数，需要为每个分支至少准备一个测试用例。若某分支极难构造输入触达（例如依赖外部数据库状态），应使用 Michael Feathers 提出的"接缝"技术：在不修改生产代码逻辑的前提下，通过子类化或参数注入的方式将外部依赖替换为测试替身（Test Double），使分支可被测试触达。

### 黄金主测试（Golden Master Testing）

对于复杂的遗留函数，逐一断言每个输出字段工作量极大。此时可采用 Golden Master（黄金主）技术：将函数在大量典型输入下的**完整序列化输出**存储为参考文件（Golden File），重构后对比输出与参考文件的差异。

黄金主测试的公式可表示为：

```
通过条件：serialize(f_after(input_i)) == golden_file[i]，对所有 i ∈ 测试集
```

其中 `f_after` 为重构后的函数，`golden_file[i]` 为重构前记录的参考输出。该方法在处理报表生成、复杂数据转换等场景下尤为高效，但需注意排除输出中的时间戳、随机数等非确定性内容，否则比对将永远失败。

---

## 实际应用

**场景一：电商订单计算模块重构**  
某电商系统的 `OrderPricingEngine` 类包含1200行无测试遗留代码，需要将其拆分为独立的折扣、税务和运费计算模块。重构前，团队首先针对50个历史真实订单数据编写 Characterization Test，将当前系统对每笔订单的实际计算结果记录为断言。随后执行重构，每次提取方法后立即运行全部50个测试。当某次提取导致其中3个测试失败时，团队立刻回滚该步操作而非继续推进，从而避免了将错误代码带入下一步重构。

**场景二：解耦依赖数据库的计算逻辑**  
某统计函数内部直接调用 `Database.query()` 获取数据，导致测试无法独立运行。使用接缝技术，创建 `StatisticsCalculator(DataSource source)` 构造函数重载（不修改原有单参数构造器），在测试中注入内存数据源，使计算逻辑得以被 Characterization Test 覆盖，整个过程对生产代码的改动量控制在3行以内。

---

## 常见误区

**误区一：认为 Characterization Test 要验证业务逻辑正确性**  
Characterization Test 断言的是当前行为，不是正确行为。遗留代码中存在的历史 bug，在重构阶段应被原样保留在测试断言中。若团队成员发现 `assertEquals(42.5, ...)` 中的 `42.5` 是错误值，应在重构完成后新建专项任务修复，绝不能在补测试阶段"顺手修正"断言值——否则重构与修 bug 同时进行，一旦出现问题将无法区分故障来源。

**误区二：只覆盖主干路径就开始重构**  
许多开发者觉得只要主流程测试通过，就可以开始重构异常处理或边界逻辑。这是危险的。遗留代码中的异常分支往往包含隐式的业务规则（如特定条件下返回0而非抛出异常），这些规则在文档中不存在，只体现在代码行为上。跳过这些分支的 Characterization Test，等于为重构埋下隐患。

**误区三：用 Characterization Test 替代长期单元测试**  
完成重构后，部分团队保留 Characterization Test 作为回归测试。这会导致测试套件中存在"记录错误行为"的测试，污染测试基线。正确做法是：重构完成、代码结构清晰后，用真正描述业务意图的单元测试替换 Characterization Test，后者仅作为重构过渡期的临时安全网。

---

## 知识关联

重构前加测试建立在**重构概述**所定义的"行为保持变换"原则之上：重构的定义本身要求功能不变，而没有测试覆盖就无法客观验证"功能不变"这一承诺是否兑现。Characterization Test 将这一承诺从主观判断转化为可自动验证的机器检查。

与**TDD概述**的关系在于方向相反但工具重叠：TDD 的测试从无到有描述未来行为，重构前加测试从有到有锁定既有行为。两者都使用相同的测试框架（如 JUnit、pytest），但断言的语义完全不同——TDD 的失败断言意味着"功能待实现"，Characterization Test 的失败断言意味着"重构引入了回归"。理解这一语义差异，是正确运用两种测试技术的前提。