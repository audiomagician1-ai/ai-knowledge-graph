---
id: "solid-principles"
concept: "SOLID原则"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 6
is_milestone: false
tags: ["设计"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# SOLID原则

## 概述

SOLID原则是面向对象设计中五条具体指导原则的首字母缩写，由Robert C. Martin（"Uncle Bob"）在2000年前后的系列论文中首次系统整理，并在其2002年著作《Agile Software Development: Principles, Patterns, and Practices》中正式成文。这五条原则分别是：单一职责原则（SRP）、开放封闭原则（OCP）、里氏替换原则（LSP）、接口隔离原则（ISP）和依赖倒置原则（DIP）。

在AI工程场景下，SOLID原则的价值尤为突出。AI系统通常包含数据预处理、模型训练、推理服务、评估监控等高度异构的模块，如果各模块职责不清、依赖混乱，任何一次算法迭代都可能引发连锁修改。遵守SOLID原则能让每个模块独立演化，使模型替换（如将XGBoost换成LightGBM）不影响上下游代码。

SOLID并非七条或三条，恰好是五条相互补充的约束，缺少其中任意一条都会导致特定的腐化模式：缺少SRP导致"上帝类"，缺少OCP导致大量if-else分支，缺少LSP导致类型断言陷阱，缺少ISP导致"胖接口"污染，缺少DIP导致高层模块直接依赖具体实现而难以测试。

---

## 核心原理

### 单一职责原则（SRP）

SRP规定：**一个类应该只有一个引起它变化的原因**。"原因"在这里等同于"业务维度"。例如，一个`ModelTrainer`类不应同时负责日志记录和超参数搜索，因为日志格式的变更和搜索策略的变更是两个独立的变化轴。Martin给出的判断标准是：如果你能为一个类写出两个不同部门（如算法团队与运维团队）各自会要求修改的理由，那么这个类就违反了SRP。实践中应将日志、持久化、验证等横切关注点剥离为独立类。

### 开放封闭原则（OCP）

OCP由Bertrand Meyer于1988年首次提出，Martin后来用多态重新诠释：**软件实体应对扩展开放，对修改封闭**。具体做法是将变化点抽象为接口或抽象类，新功能通过新增子类实现，而不修改已有代码。在AI推理服务中，可以定义`Predictor`抽象接口，初期实现`SklearnPredictor`，后续直接新增`OnnxPredictor`或`TorchServingPredictor`，原有调用代码无需改动。衡量代码是否满足OCP的简单标准：添加一种新算法时，改动的文件数是否为1（仅新增实现类）。

### 里氏替换原则（LSP）

LSP由Barbara Liskov于1987年在OOPSLA会议论文《Data Abstraction and Hierarchy》中提出，精确表述为：**若`S`是`T`的子类型，则程序中所有使用`T`的地方，用`S`替换后行为不变**。违反LSP的典型反例是"正方形-矩形悖论"：若`Square`继承`Rectangle`并重写`setWidth`使其同时改变高度，则调用方对`Rectangle`的假设（宽高独立可变）被破坏。在机器学习中，若`BaseClassifier`定义了`predict_proba`方法，子类`SVMClassifier`抛出`NotImplementedError`，则使用`BaseClassifier`类型的代码会因替换而崩溃，违反LSP。

### 接口隔离原则（ISP）

ISP规定：**不应强迫客户端依赖它不使用的方法**。一个包含`train`、`predict`、`explain`、`export_onnx`的"胖接口"会迫使所有实现类提供`explain`和`export_onnx`，即使某些模型（如规则引擎）完全不需要它们。正确做法是将其拆分为`Trainable`、`Predictable`、`Explainable`、`OnnxExportable`四个细粒度接口，具体类按需组合实现。ISP与接口这一前置概念直接相连：只有先理解接口的抽象机制，才能进行有意义的接口拆分。

### 依赖倒置原则（DIP）

DIP包含两层含义：**高层模块不应依赖低层模块，两者都应依赖抽象；抽象不应依赖细节，细节应依赖抽象**。在Python中，违反DIP的代码形如`self.db = MySQLDatabase()`（高层类直接实例化低层具体类）；遵守DIP的形式是构造函数接收`DatabaseInterface`类型参数，由外部传入具体实现。DIP是依赖注入（下一个概念）的理论基础：依赖注入是实现DIP的具体技术手段，DIP描述"应该依赖谁"，依赖注入描述"如何把依赖传进来"。

---

## 实际应用

**AI特征工程流水线**：设计一个特征处理系统时，可以定义`FeatureTransformer`接口，包含`fit(data)`和`transform(data)`两个方法（ISP保证接口精简）。`NumericalScaler`、`CategoricalEncoder`、`EmbeddingLookup`各自实现该接口（OCP），彼此可互相替换且不改变流水线逻辑（LSP）。流水线主类`FeaturePipeline`通过构造函数接收`List[FeatureTransformer]`而不直接实例化具体转换器（DIP）。每个转换器类只负责自身的变换逻辑，日志记录由装饰器单独处理（SRP）。

**模型评估模块**：违反SOLID的写法是一个`Evaluator`类中用`if model_type == 'classification': ... elif model_type == 'regression': ...`分支计算指标。遵守OCP的重构方案是定义`EvaluationStrategy`接口，分别实现`ClassificationEvaluator`和`RegressionEvaluator`，主流程通过接口调用，新增`RankingEvaluator`时不修改任何已有文件。

---

## 常见误区

**误区一：SRP等于"每个类只有一个方法"**。SRP说的是"一个变化原因"，而非"一个方法"。一个`DataPreprocessor`类可以包含`normalize`、`remove_nulls`、`encode_categoricals`多个方法，只要它们都因"数据预处理规则变更"这同一原因而改变，就满足SRP。若该类还包含"将结果写入S3"的方法，则引入了存储策略这一第二变化轴，才真正违反SRP。

**误区二：OCP意味着永远不能修改旧代码**。OCP针对的是已稳定的"完成状态"代码，而非开发中的代码。修复Bug、修正接口定义本身都是合理的修改。OCP要求的是：当新增业务功能时，通过扩展（新增类/模块）而非修改已通过测试的旧类来实现。

**误区三：LSP只是"子类能调用父类方法"**。很多人将LSP误解为语法层面的继承合法性。LSP关注的是行为契约：子类不仅要实现父类的方法签名，还要保持父类方法的前置条件（不能比父类更严格）和后置条件（不能比父类更宽松）。`predict`方法若父类约定返回0到1之间的概率值，子类返回未归一化的logit就违反了LSP的后置条件约束，即使代码能正常编译运行。

---

## 知识关联

SOLID原则以**接口**作为直接的技术支撑。OCP中的"对扩展开放"依赖接口定义变化点；ISP直接操作接口的粒度切分；DIP要求高层模块依赖接口而非具体类。如果不理解接口的抽象与多态机制，OCP和DIP的实践将无法落地。

SOLID原则的直接延伸是**依赖注入**。DIP规定了"应依赖抽象"，但没有规定谁来创建具体对象并将其注入高层模块——这正是依赖注入框架（如Python的`injector`库或Java的Spring IoC容器）解决的问题。掌握SOLID原则后，依赖注入的动机与设计选择将会变得清晰：构造函数注入对应DIP中"通过抽象接收依赖"，容器配置对应"在应用启动时绑定抽象与具体实现"。两者合用才能构建出模块间低耦合、可独立测试的AI系统架构。
