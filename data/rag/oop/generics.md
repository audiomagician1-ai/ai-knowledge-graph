# 泛型

## 概述

泛型（Generics）是一种在定义类、函数或接口时使用**类型参数**（Type Parameter）作为占位符，从而将具体类型绑定推迟到调用方决定的编程机制。这种机制的学术名称为**参数多态**（Parametric Polymorphism），最早由 Robin Milner 在1973年设计 ML 语言时正式引入（Milner et al., *A Theory of Type Polymorphism in Programming*, 1978）。与之相对的运行时多态依赖虚函数表派发，而泛型的类型检查发生在**编译期**，运行时开销为零（Java 的类型擦除除外）。

Java 在 2004 年 JDK 5.0（JSR-14）中正式引入泛型，设计者 Gilad Bracha 在论文 *Making the Future Safe for the Past: Adding Genericity to the Java Programming Language*（OOPSLA 1998）中详细描述了设计权衡。TypeScript 从1.0版本（2014年10月）起将泛型作为类型系统的一等公民，C++ 则早在1991年通过模板（Template）机制实现了更强大但更复杂的参数多态。

泛型解决的根本矛盾是：**代码复用**与**类型安全**之间的张力。没有泛型之前，要么用 `Object`/`any` 牺牲类型安全，要么为每种类型复写相同逻辑的函数（例如 `sortInts`、`sortStrings`、`sortDates`）。泛型允许编写一个 `sort<T extends Comparable<T>>(arr: T[]): T[]`，既保留了完整的编译期类型约束，又实现了逻辑的唯一定义。

---

## 核心原理

### 类型参数与实例化

泛型的形式语义可以用 System F（二阶 lambda 演算）描述。一个泛型函数 $\Lambda T.\, \lambda x{:}T.\, x$ 表示"对任意类型 $T$，接受一个 $T$ 类型的参数并返回它"。当调用时传入具体类型，即发生**实例化**（Instantiation）：$(\Lambda T.\, \lambda x{:}T.\, x)\ [\text{number}]\ 42$ 得到 $42 : \text{number}$。

在 TypeScript 中，这对应：

```typescript
function identity<T>(value: T): T {
    return value;
}

const n: number = identity<number>(42); // 显式实例化
const s: string = identity("hello");    // 编译器推断 T = string
```

类型推断（Type Inference）的算法基于 Hindley-Milner 类型系统的 Algorithm W（Hindley, 1969；Milner, 1978），通过合一（Unification）将类型变量 $T$ 与实参的静态类型绑定。TypeScript 的推断比标准 HM 更复杂，支持上下文类型（Contextual Typing），能从赋值目标反向推断类型参数。

### 泛型约束（Generic Constraints）

未约束的类型参数 `T` 在函数体内是"透明盒"——编译器仅知道 `T` 是某个类型，不能假设它有任何属性或方法。`extends` 关键字引入**上界约束**（Upper Bound Constraint）：

```typescript
function maxElement<T extends { valueOf(): number }>(arr: T[]): T {
    return arr.reduce((a, b) => a.valueOf() >= b.valueOf() ? a : b);
}
```

此处 `T extends { valueOf(): number }` 是结构子类型约束，TypeScript 的鸭子类型系统（Structural Typing）会在调用点验证传入类型是否满足该结构，而非要求显式继承关系。Java 的等价写法是 `<T extends Comparable<T>>`，采用名义子类型（Nominal Subtyping），需要显式声明 `implements Comparable<T>`。

多重约束可通过交叉类型表达：`<T extends Serializable & Loggable>`，这在 AI 工程中常见于约束张量类型必须同时支持序列化（用于模型持久化）和日志记录（用于调试管道）。

### 协变、逆变与不变

泛型容器在类型系统中存在**型变**（Variance）问题。若 `Cat extends Animal`，那么：

- $\text{ReadonlyArray}<\text{Cat}>$ 是 $\text{ReadonlyArray}<\text{Animal}>$ 的子类型 → **协变**（Covariant）
- $\text{(animal: Animal) => void}$ 是 $\text{(cat: Cat) => void}$ 的子类型 → **逆变**（Contravariant）
- `Array<Cat>` **不是** `Array<Animal>` 的子类型 → **不变**（Invariant）

不变的原因：若允许 `Array<Cat>` 赋给 `Array<Animal>`，则可以向其中 `push(new Dog())`，破坏类型安全。TypeScript 通过 `in`/`out` 型变标注（4.7版本引入）允许开发者显式声明类型参数的型变性：`interface Producer<out T> { produce(): T }`。

Luca Cardelli 和 Peter Wegner 在论文 *On Understanding Types, Data Abstraction, and Polymorphism*（ACM Computing Surveys, 1985）中系统分类了多态类型，其中参数多态（泛型）与包含多态（子类型）、特设多态（重载）、强制多态（类型转换）构成完整的多态分类体系。

### 类型擦除 vs 具现化泛型

Java 采用**类型擦除**（Type Erasure）实现泛型：编译后 `List<String>` 和 `List<Integer>` 都变成原始类型 `List`，类型参数信息在字节码中丢失。这导致无法在运行时通过 `instanceof List<String>` 判断，也无法通过反射获取完整的泛型类型参数（需借助 `TypeToken` 模式绕过）。

C# 采用**具现化泛型**（Reified Generics）：`List<int>` 和 `List<string>` 在 CLR 中是完全独立的类型，运行时可通过 `typeof(List<int>)` 获取完整类型信息，值类型版本（如 `List<int>`）避免了装箱（Boxing）开销，性能优于 Java 的擦除方案。

---

## 关键方法与公式

### 泛型类与泛型接口

```typescript
interface Repository<T, ID> {
    findById(id: ID): Promise<T | null>;
    findAll(): Promise<T[]>;
    save(entity: T): Promise<T>;
    delete(id: ID): Promise<void>;
}

class InMemoryRepository<T extends { id: string }> 
    implements Repository<T, string> {
    
    private store = new Map<string, T>();
    
    async findById(id: string): Promise<T | null> {
        return this.store.get(id) ?? null;
    }
    async save(entity: T): Promise<T> {
        this.store.set(entity.id, entity);
        return entity;
    }
    // ...
}
```

此模式在 AI 工程中用于构建模型注册中心：`ModelRegistry<M extends BaseModel>` 可统一管理不同架构（BERT、GPT、ViT）的模型实例，同时保留各自的特定方法签名。

### 条件类型（Conditional Types）

TypeScript 2.8 引入条件类型，形式为 $T \text{ extends } U\, ?\, X\, :\, Y$，配合泛型实现类型级别的逻辑分支：

```typescript
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
// UnwrapPromise<Promise<number>> = number
// UnwrapPromise<string>          = string

type DeepReadonly<T> = {
    readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};
```

`infer` 关键字允许在条件类型中**捕获**（Capture）子类型，用于提取嵌套类型信息，无需任何运行时代码。

### 映射类型与类型变换

```typescript
// 将接口所有方法替换为返回 Promise 的异步版本
type Async<T> = {
    [K in keyof T]: T[K] extends (...args: infer A) => infer R 
        ? (...args: A) => Promise<R> 
        : T[K];
};
```

这类类型变换在定义 AI 服务层时极为有用：将同步的模型推理接口 `ModelService` 自动派生出 `Async<ModelService>`，无需手动重复书写所有方法签名。

---

## 实际应用

### 案例一：类型安全的事件系统

```typescript
type EventMap = {
    'model:loaded': { modelId: string; loadTime: number };
    'inference:complete': { input: number[]; output: number[]; latency: number };
    'error': { code: string; message: string };
};

class TypedEventEmitter<Events extends Record<string, unknown>> {
    private listeners = new Map<keyof Events, Set<Function>>();

    on<K extends keyof Events>(
        event: K, 
        listener: (data: Events[K]) => void
    ): void {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event)!.add(listener);
    }

    emit<K extends keyof Events>(event: K, data: Events[K]): void {
        this.listeners.get(event)?.forEach(fn => fn(data));
    }
}

const emitter = new TypedEventEmitter<EventMap>();
emitter.on('inference:complete', ({ latency }) => {
    console.log(`推理耗时 ${latency}ms`);
});
// emitter.emit('inference:complete', { wrong: 'field' }); // 编译错误！
```

这种模式将运行时的事件名称错误和数据结构错误提前到编译期捕获，在大型 AI 系统中减少调试成本。

### 案例二：AI 管道的泛型抽象

```typescript
interface PipelineStep<Input, Output> {
    process(input: Input): Promise<Output>;
}

class Pipeline<T> {
    private steps: PipelineStep<any, any>[] = [];

    pipe<U>(step: PipelineStep<T, U>): Pipeline<U> {
        const next = new Pipeline<U>();
        next.steps = [...this.steps, step];
        return next;
    }

    async run(input: T): Promise<any> {
        return this.steps.reduce(
            async (acc, step) => step.process(await acc),
            Promise.resolve(input)
        );
    }
}

// 使用：文本 → Token → 向量 → 分类结果
const nlpPipeline = new Pipeline<string>()
    .pipe(new TokenizerStep())     // Pipeline<string> → Pipeline<Token[]>
    .pipe(new EmbeddingStep())     // Pipeline<Token[]> → Pipeline<Float32Array>
    .pipe(new ClassifierStep());   // Pipeline<Float32Array> → Pipeline<Label>
```

每个 `.pipe()` 调用都经过编译器验证前一步的输出类型与当前步骤的输入类型是否匹配，在编写管道时即发现类型不兼容问题。

---

## 常见误区

### 误区一：将泛型与 `any` 混用

```typescript
// 错误：用 any 破坏了泛型的意义
function badWrap<T>(value: T): any { return { data: value }; }

// 正确：保持类型信息在整个调用链中传递
function goodWrap<T>(value: T): { data: T } { return { data: value }; }
```

一旦返回类型写成 `any`，调用方获得的结果失去所有类型信息，等同于没有使用泛型。

### 误区二：过度约束导致泛型失去意义

```typescript
// 反例：约束过强，实质上只支持一种类型
function process<T extends SomeVerySpecificClass>(x: T): T { ... }
// 此时直接用 SomeVerySpecificClass 作为参数类型即可，无需泛型
```

泛型的价值在于约束"足够宽松但足以完成操作"的类型范围。若约束到某个具体类或其子类，且不需要在签名中保留"输入类型 = 输出类型"的关联，直接使用具体类更清晰。

### 误区三：误解 Java 类型擦除的影响

```java
// 运行时会抛出 ClassCastException，而非 ClassNotFoundException
List rawList = new ArrayList<String>();
rawList.add(42);               // 编译警告，运行时不报错
String s = (String) rawList.get(0); // 运行时 ClassCastException
```

Java 的类型擦除意味着泛型检查只在编译期有效，若使用原始类型（Raw Type）绕过编译器，运行时安全网消失。这是 Java 泛型与 C# 具现化泛型最显著的行为差异。

### 误区四：混淆协变容器的写操作限制

例如：TypeScript 的 `ReadonlyArray<T>` 是协变的，可以安全地将 `ReadonlyArray<Dog>` 赋给 `ReadonlyArray<Animal>`，但可变 `Array<T>` 是不变的，原因正如前述——允许协变赋值后会破坏写操作的类型安全。

---

## 知识关联

### 与