---
id: "se-dp-chain"
concept: "责任链模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["行为型"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 责任链模式

## 概述

责任链模式（Chain of Responsibility Pattern）是一种行为型设计模式，其核心机制是将多个处理对象串联成一条链，请求沿着这条链依次传递，直到某个对象决定处理它为止。发出请求的客户端无需知道链上哪个对象最终处理了请求，从而实现了请求发送者与接收者的解耦。

该模式由四人帮（GoF）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式归类。其思想原型来源于操作系统中的事件冒泡机制和Unix管道命令——例如 `cat file.txt | grep "error" | sort` 就是一种典型的链式处理思路，每个命令处理数据后传递给下一个。

责任链模式在实际工程中应用极为广泛：Java的Servlet Filter链、Spring Security的过滤器链、Node.js的Express中间件、Python的Django中间件系统都采用了这一模式。它最重要的工程价值在于：新增或删除一个处理节点，不需要修改请求发送方的代码，也不需要重构其他处理节点，符合开闭原则。

## 核心原理

### 链的基本结构

责任链模式包含三个角色：**抽象处理者（Handler）**、**具体处理者（ConcreteHandler）**和**客户端（Client）**。抽象处理者定义处理请求的接口，并持有指向下一个处理者的引用（通常命名为 `successor` 或 `nextHandler`）。每个具体处理者判断自己是否能处理当前请求：能处理则直接消费，不能处理则调用 `successor.handleRequest()` 将请求向后传递。

```java
abstract class Handler {
    protected Handler successor;
    public void setSuccessor(Handler successor) {
        this.successor = successor;
    }
    public abstract void handleRequest(int level);
}
```

链的末端处理者若无法处理请求，可以选择抛出异常、记录日志或静默丢弃，取决于业务需求。

### 纯责任链与不纯责任链

责任链模式分为**纯**与**不纯**两种变体，这是理解该模式的关键区分点。

**纯责任链**要求每个请求必须被链上恰好一个处理者处理，且该处理者不再向后传递。例如客服工单系统中，级别1处理者能处理金额小于100元的退款，级别2处理1000元以下，级别3处理全部——一旦某级别处理，流程结束。

**不纯责任链**允许一个节点处理请求后继续向后传递，所有满足条件的节点都可以对请求进行操作。Java Servlet Filter链正是不纯责任链的典型：一个请求可能先后经过身份验证Filter、日志Filter、压缩Filter，每个Filter都处理（或装饰）该请求，最终才到达Servlet。

### 中间件管道模型

现代框架将责任链演化为**中间件管道（Middleware Pipeline）**模型，这是责任链模式的工程实践形态。以Express.js为例，中间件函数签名为 `(req, res, next) => {}`，其中 `next()` 调用等价于将请求传递给链上下一个处理者。

```javascript
app.use((req, res, next) => {
    console.log('日志中间件：', req.method, req.url);
    next(); // 显式调用才会传递，否则链断开
});
```

管道模型与经典责任链的差异在于：管道通常要求每个节点**必须显式调用next**才能继续传递，而不是由框架自动传递；且管道中请求返回时还会反向经过中间件，形成"洋葱模型"——Koa.js中的 `await next()` 即是此机制的体现。

### 与命令模式的关联

命令模式将请求封装为对象，而责任链模式定义了这些命令对象的**传递路径**。在实践中两者经常配合：命令对象（如HTTP请求对象）沿责任链传递，链上每个处理者可读取或修改命令对象的内容，再决定是否继续传递。这种组合在Spring MVC的 `HandlerInterceptor` 中体现得尤为明显。

## 实际应用

**审批流系统**：企业报销单审批是最经典的责任链场景。金额≤500元由组长审批，500~5000元由部门经理审批，5000元以上由CFO审批。每个审批节点构成链上一个处理者，新增副总裁审批级别只需插入链中一个节点，不改变任何已有节点逻辑。

**Spring Security过滤器链**：Spring Security内置了约15个安全过滤器（如 `UsernamePasswordAuthenticationFilter`、`BasicAuthenticationFilter`），它们通过 `FilterChainProxy` 串联成责任链。每个请求依次经过这些过滤器，开发者可以通过配置增删过滤器节点而无需修改框架源码。

**前端事件冒泡**：浏览器DOM事件从目标元素向上冒泡到 `document` 的过程，本质上是一条责任链。每个父节点（Handler）可以选择处理该事件（调用 `stopPropagation()` 中断链），或忽略并继续向上冒泡（隐式传递给successor）。

**日志框架分级处理**：Log4j/Logback的日志级别过滤机制也是责任链应用——DEBUG、INFO、WARN、ERROR各级别的Appender构成一条链，低于阈值的日志请求被过滤（丢弃），高于阈值的才被处理并记录。

## 常见误区

**误区一：认为责任链必须有且只有一个节点处理请求**。初学者常将责任链与纯模式混同，认为请求被处理后必须终止传递。实际上，Servlet Filter、Express中间件等工程中最常见的恰恰是不纯责任链，多个节点均会处理同一请求。判断应使用哪种变体，取决于业务是否允许"叠加处理"。

**误区二：将链的构建逻辑放在处理者内部**。常见错误是在每个 `ConcreteHandler` 的构造函数中硬编码 `successor`，导致链结构固化、无法动态调整。正确做法是由客户端或专门的组装类（如Spring的 `SecurityFilterChain`）负责构建链，各处理者只负责"处理或传递"的判断逻辑。

**误区三：忽略链断裂问题**。在管道模型（如Express）中，若中间件忘记调用 `next()`，后续所有处理者都不会执行，且客户端请求会永久挂起（HTTP请求无响应）。这是责任链模式特有的运行时错误，与链式结构的显式传递机制直接相关，调试时需检查每个节点的 `next` 调用路径。

## 知识关联

**前置概念——命令模式**：责任链模式通常与命令模式配合使用。命令模式解决的是"如何封装一个请求"，责任链模式解决的是"封装后的请求由谁处理"。在HTTP请求处理场景中，`HttpServletRequest` 对象是命令，Filter链是责任链。

**设计原则对应**：责任链模式直接体现了**单一职责原则**（每个Handler只处理自己职责范围内的请求）和**开闭原则**（新增处理逻辑只需插入新节点，不修改已有节点）。

**进阶演化方向**：理解责任链模式后，可进一步研究**管道-过滤器架构模式**（Pipeline-Filter Architecture），该模式是责任链在系统架构层面的推广，广泛应用于编译器（词法分析→语法分析→语义分析→代码生成）和数据处理管道（ETL流程）中。责任链处理的是单个请求的路由问题，而管道-过滤器处理的是数据流的批量变换问题，两者在结构上相似但应用粒度不同。
