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
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 泛型

## 概述

泛型（Generics）是一种允许在定义函数、类或接口时使用类型参数（Type Parameter）的编程机制，使得同一段代码可以安全地操作多种不同类型的数据，而不牺牲静态类型检查的能力。其本质是"将类型本身作为参数传递"，用尖括号 `<T>` 语法声明类型占位符，在调用时由编译器推断或由程序员显式指定具体类型。

泛型的概念最早由 CLU 语言在1970年代提出，后来在 Ada（1983年）和 C++（1991年模板系统）中得到广泛推广。TypeScript 从1.0版本（2014年发布）起就内置了泛型支持，其设计直接借鉴了 C# 和 Java 的泛型系统，但去掉了 Java 中因类型擦除（Type Erasure）导致的运行时缺失问题。

在 AI 工程的 TypeScript 代码库中，泛型尤为重要：模型推理结果的类型、批处理数据的容器、各类 API 响应的解析器都高度依赖泛型来保持类型安全，同时避免为每种数据结构重复编写逻辑。

---

## 核心原理

### 类型参数声明与替换

泛型的语法核心是类型参数列表 `<T, U, V, ...>`，这些字母本身没有特殊含义，只是占位符（习惯上 `T` 代表 Type，`K` 代表 Key，`V` 代表 Value，`E` 代表 Element）。以下是一个最简单的泛型函数：

```typescript
function identity<T>(arg: T): T {
  return arg;
}
```

调用时，TypeScript 编译器可以自动推断 `T` 的类型：`identity(42)` 中 `T` 被推断为 `number`；`identity("hello")` 中 `T` 被推断为 `string`。也可以显式传入：`identity<boolean>(true)`。关键在于，返回值类型与输入类型被**绑定为同一个 `T`**，这保证了类型层面的一致性——这是 `any` 无法做到的，`any` 会完全放弃类型检查。

### 泛型约束（Generic Constraints）

原始类型参数 `T` 没有任何属性，访问 `arg.length` 会报错，因为编译器不知道 `T` 是否有 `length`。通过 `extends` 关键字可以施加约束：

```typescript
interface HasLength {
  length: number;
}
function logLength<T extends HasLength>(arg: T): T {
  console.log(arg.length);  // 合法，编译器确认 T 有 length
  return arg;
}
```

`T extends HasLength` 的含义是：`T` 必须是 `HasLength` 的子类型，即必须包含 `length: number` 属性。这不是继承关系，而是**结构子类型（Structural Subtyping）**检查：任何含有 `length: number` 的类型，包括 `string`、数组、自定义对象，都满足此约束。

### 泛型类与泛型接口

泛型不仅限于函数，还可以用于类和接口。一个典型的泛型容器类：

```typescript
class DataBatch<T> {
  private items: T[] = [];
  
  add(item: T): void {
    this.items.push(item);
  }
  
  get(index: number): T {
    return this.items[index];
  }
  
  map<U>(transform: (item: T) => U): DataBatch<U> {
    const result = new DataBatch<U>();
    this.items.forEach(item => result.add(transform(item)));
    return result;
  }
}
```

注意 `map` 方法引入了第二个类型参数 `U`，表示转换后的类型与原类型 `T` 可以不同。`DataBatch<ModelInput>` 经过 `map` 后可以变成 `DataBatch<ModelOutput>`，全程保持类型安全。

### 条件类型与内置工具类型

TypeScript 3.0 引入的条件类型 `T extends U ? X : Y` 进一步扩展了泛型的表达力。标准库中大量工具类型基于此实现，例如：

- `Partial<T>`：将 `T` 的所有属性变为可选，实现为 `{ [P in keyof T]?: T[P] }`
- `Record<K, V>`：创建键类型为 `K`、值类型为 `V` 的对象类型
- `ReturnType<T>`：通过 `T extends (...args: any) => infer R ? R : never` 提取函数返回类型

这些工具类型本质上是**高阶泛型**，接受类型作为输入并产生新类型作为输出。

---

## 实际应用

**AI 推理 API 响应解析**：假设调用不同模型 API，响应结构各不相同。可用泛型定义统一的包装器：

```typescript
interface ApiResponse<T> {
  data: T;
  status: number;
  latencyMs: number;
}

interface EmbeddingResult {
  vector: number[];
  model: string;
}

async function callModel<T>(endpoint: string): Promise<ApiResponse<T>> {
  const raw = await fetch(endpoint);
  return raw.json() as ApiResponse<T>;
}

// 调用时指定具体类型
const result = await callModel<EmbeddingResult>("/api/embed");
result.data.vector;  // 编译器知道这是 number[]
```

**批处理流水线**：在数据预处理流水线中，每个处理步骤可以用 `Processor<TInput, TOutput>` 泛型接口表达，强制要求上一步的输出类型必须匹配下一步的输入类型，在编译时而非运行时发现类型不兼容问题。

---

## 常见误区

**误区一：泛型等同于 `any`**。`any` 完全绕过类型检查，`identity<any>(x)` 的返回值类型也是 `any`，后续操作不受保护。而泛型 `identity<T>(x: T): T` 中，输入和输出类型被编译器追踪为同一具体类型，后续代码可以安全地使用该类型的所有方法和属性。两者在运行时都会被 TypeScript 编译为普通 JavaScript，但编译阶段的保护程度完全不同。

**误区二：约束 `T extends SomeClass` 意味着继承**。在泛型约束中，`extends` 不要求 `T` 是 `SomeClass` 的子类，只要求 `T` 的结构上拥有 `SomeClass` 定义的所有属性和方法（结构类型兼容）。一个字面量对象 `{ name: "GPT", predict: () => {} }` 完全可以满足 `extends Model` 的约束，无需使用 `class` 关键字继承。

**误区三：泛型参数越多越灵活**。过多的类型参数（如 `<A, B, C, D>`）会使函数签名难以理解，且约束关系复杂时编译器推断可能失败，需要调用者手动显式传入所有类型参数。实践中，AI 工程代码应优先用1-2个类型参数覆盖主要变化点，对固定的部分直接使用具体类型。

---

## 知识关联

**与类型系统的关系**：泛型的价值完全建立在静态类型系统之上。在动态类型语言（如纯 JavaScript 或 Python）中，不存在泛型的概念，因为类型检查在运行时才发生，编译期不需要提前指定类型。TypeScript 的静态类型系统正是泛型得以发挥作用的基础——类型参数 `T` 在编译期被替换为具体类型，编译后的 JavaScript 中完全不存在 `T`，这也是 TypeScript 泛型与 C++ 模板（模板在编译后生成多份代码）的核心区别。

**与面向对象多态的关系**：泛型提供的是**参数化多态（Parametric Polymorphism）**，与通过继承实现的**子类型多态（Subtype Polymorphism）**是不同的机制。子类型多态通过 `Animal` 基类引用指向 `Dog` 实例来统一处理，而泛型通过类型参数在保留具体类型信息的前提下统一处理。在 AI 工程中，两者常配合使用：用泛型定义数据容器结构，用继承定义模型的行为层次。
