---
id: "generics"
concept: "泛型"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 5
is_milestone: false
tags: ["类型系统"]

# Quality Metadata (Schema v2)
content_version: 5
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
updated_at: 2026-03-31
---

# 泛型

## 概述

泛型（Generics）是一种允许类、函数或接口在定义时不指定具体类型，而在使用时再传入类型参数的编程机制。其核心价值在于：同一段代码逻辑可以安全地作用于多种不同类型，而不必为每种类型重复编写。在 TypeScript 中，泛型语法使用尖括号 `<T>` 表示类型参数，`T` 是约定俗成的占位符名称，全称为 Type Parameter。

泛型的概念最早由 ML 语言在 1973 年引入，称为"参数多态"（Parametric Polymorphism）。Java 在 2004 年的 JDK 5.0 中正式加入泛型支持，TypeScript 则从 1.0 版本（2014 年）起就将泛型作为类型系统的核心特性。与运行时多态（通过继承和接口实现）不同，泛型是一种**编译期多态**——类型检查发生在代码编译阶段，而非程序运行时。

在 AI 工程中，泛型的重要性体现在模型管道（Pipeline）的抽象上。一个数据预处理器可能处理 `string[]`、`number[][]` 或自定义的 `Tensor<Float32>` 类型——泛型让你写一个 `Processor<T>` 类就能覆盖所有情况，而静态类型检查器会保证在传入 `Tensor<Float32>` 时不会意外调用字符串专属方法。

---

## 核心原理

### 类型参数与类型推断

泛型函数的基本形式是在函数名后声明类型参数：

```typescript
function identity<T>(value: T): T {
    return value;
}
```

这里 `T` 是类型参数，函数签名约定了"输入什么类型，就返回什么类型"。调用时可以**显式传入**类型 `identity<number>(42)`，也可以让 TypeScript 编译器通过**类型推断**（Type Inference）自动确定：`identity(42)` 会推断 `T = number`。类型推断依赖于实参的静态类型，而不是运行时值。

### 泛型约束（Generic Constraints）

未加约束的 `T` 在函数体内几乎一无所知——你不能对 `T` 类型的变量调用 `.length`，因为编译器无法保证 `T` 是字符串或数组。泛型约束用 `extends` 关键字解决这个问题：

```typescript
function getLength<T extends { length: number }>(arg: T): number {
    return arg.length;
}
```

`T extends { length: number }` 约定 `T` 必须是拥有 `length` 属性的类型。这不是运行时的类型检查，而是编译期的**结构子类型**约束，TypeScript 的鸭子类型系统会验证传入的类型是否满足该结构。

在 AI 工程场景中，常见约束形式是 `T extends Tensor | NDArray`，用来限定泛型运算函数只接受张量类型，防止意外传入普通对象。

### 泛型类与泛型接口

泛型不仅限于函数，类和接口同样支持类型参数：

```typescript
interface Repository<T> {
    findById(id: string): Promise<T>;
    save(entity: T): Promise<void>;
    findAll(): Promise<T[]>;
}

class ModelRegistry<M extends BaseModel> implements Repository<M> {
    private store = new Map<string, M>();
    
    async findById(id: string): Promise<M> {
        return this.store.get(id)!;
    }
    async save(entity: M): Promise<void> {
        this.store.set(entity.id, entity);
    }
    async findAll(): Promise<M[]> {
        return [...this.store.values()];
    }
}
```

`ModelRegistry<GPTModel>` 和 `ModelRegistry<DiffusionModel>` 是同一段代码产生的两个**具体化类型**（Instantiated Types），它们共享所有方法逻辑，但 TypeScript 会分别为它们进行独立的类型检查。

### 多类型参数与条件类型

泛型可以声明多个类型参数，TypeScript 还支持**条件类型**（Conditional Types，TypeScript 2.8 引入）：

```typescript
type Unwrap<T> = T extends Promise<infer U> ? U : T;
// Unwrap<Promise<number>> → number
// Unwrap<string>          → string
```

`infer` 关键字在条件类型中用于"提取"嵌套类型，这在处理异步 AI 推理结果（如 `Promise<ModelOutput>`）时极为实用。

---

## 实际应用

**AI 推理管道的类型安全封装**：定义泛型 `Pipeline<Input, Output>` 接口，让每个处理步骤都明确声明输入输出类型。当预处理步骤输出 `Tensor<Float32>` 而模型期望 `Tensor<Int8>` 时，编译器会在构建期而非运行期报错，避免线上量化错误。

```typescript
interface Stage<I, O> {
    process(input: I): O;
}

class Pipeline<I, O> {
    constructor(private stage: Stage<I, O>) {}
    run(input: I): O {
        return this.stage.process(input);
    }
}
```

**通用向量存储（Vector Store）**：RAG 系统中的向量数据库客户端可用 `VectorStore<Doc>` 泛型封装，`Doc` 代表存储的文档类型。`VectorStore<PDFDocument>` 和 `VectorStore<CodeSnippet>` 复用同一批查询、插入方法，同时保证返回结果类型正确，不需要类型断言（`as` 强转）。

**批量评估框架**：LLM 评测工具中，`Evaluator<Q, A>` 泛型类可以接受不同格式的问答对（`MCQuestion/MCAnswer` 或 `OpenQuestion/FreeText`），用一套评分逻辑处理多种题型。

---

## 常见误区

**误区一：认为泛型等同于 `any`**  
`any` 完全放弃类型检查，而泛型在类型参数确定后会进行严格检查。`identity<number>` 的返回值是 `number`，可以安全地调用 `toFixed()`；而 `any` 的返回值赋给 `number` 变量不会报错，但也不会保护你免于运行时错误。两者的本质区别：`any` 是**类型逃逸**，泛型是**类型参数化**。

**误区二：在所有地方都用 `T` 作为参数名**  
单字母 `T` 在简单场景可读，但多参数泛型中应使用语义化名称：`<TInput, TOutput>`、`<TEntity, TId>` 等。TypeScript 官方代码库中大量使用 `K`（Key）、`V`（Value）、`E`（Element）等约定名称，盲目使用 `T`、`U`、`V` 会让约束关系难以理解。

**误区三：误以为泛型约束会进行运行时检查**  
`function fn<T extends Animal>(arg: T)` 中的 `extends Animal` **仅在编译期生效**。TypeScript 编译后生成的 JavaScript 不包含任何泛型约束检查代码，类型参数在编译后被完全抹除（Type Erasure）。如果需要运行时验证，必须额外使用 `instanceof` 或 Zod 等运行时验证库。

---

## 知识关联

泛型直接建立在**静态类型系统**的能力之上：只有静态类型语言（或带静态扩展的 TypeScript）才能在编译期对类型参数进行约束检查；Python 的 `TypeVar` 是类似机制但依赖 mypy 等外部工具，运行时行为与 TypeScript 不同。**TypeScript 基础**中的接口（interface）和类型别名（type）是泛型约束的常见约束目标——`T extends SomeInterface` 中的 `SomeInterface` 本身就是 TypeScript 类型系统的产物。

掌握泛型后，面向对象编程中的**设计模式**实现会发生质变：Repository 模式、Strategy 模式、Observer 模式都因泛型而能写出类型安全的通用版本，而非依赖基类引用或类型断言。在 AI 工程的后续实践中，泛型是构建可复用模型服务客户端、类型安全 Prompt 模板系统和多模态数据管道的基础构件。