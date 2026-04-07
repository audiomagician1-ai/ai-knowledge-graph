---
id: "se-ownership"
concept: "所有权模型"
domain: "software-engineering"
subdomain: "memory-management"
subdomain_name: "内存管理"
difficulty: 3
is_milestone: false
tags: ["安全"]

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


# 所有权模型

## 概述

所有权模型（Ownership Model）是一种在编译期静态追踪内存资源归属的编程语言设计机制，其核心规则是：**每一块内存数据有且仅有一个所有者变量，当该变量离开作用域时，内存自动释放**。这一模型最具代表性的实现是 Rust 语言，自 2015 年 Rust 1.0 发布以来，所有权系统就作为该语言区别于 C/C++ 的根本特征存在，其目标是在不引入垃圾回收（GC）的前提下消除悬空指针、双重释放和数据竞争等内存安全问题。

该模型的起源可追溯至线性类型理论（Linear Type Theory），由逻辑学家 Jean-Yves Girard 于 1987 年在线性逻辑研究中提出。Rust 的设计者 Graydon Hoare 将这一理论与实际系统编程需求结合，形成了今天所看到的三条核心所有权规则。C++ 社区在观察 Rust 的实践成效后，也在 C++23 及相关 Guidelines 中引入了更严格的生命周期标注建议和 `std::unique_ptr` 独占语义的最佳实践，试图在既有语言框架内借鉴同样的思想。

所有权模型的重要性在于：Mozilla 在将 Firefox 浏览器引擎 Servo 用 Rust 重写的过程中，发现原本在 C++ 代码中占比约 70% 的安全漏洞类别（内存越界、Use-After-Free）被所有权检查器在编译期完全拦截。这一数据说明所有权模型并非学术概念，而是能够在工业规模代码库中显著降低安全漏洞密度的工程工具。

---

## 核心原理

### 三条不可违背的所有权规则

Rust 的所有权系统由三条明确规则构成：
1. 每个值有且仅有一个所有者（owner）变量。
2. 当所有者离开其词法作用域（scope）时，该值被立即 drop（释放）。
3. 所有权可以通过**移动（Move）**转移，转移后原变量不再有效。

以字符串为例：`let s1 = String::from("hello"); let s2 = s1;` 执行后，`s1` 立即失效，编译器拒绝任何后续对 `s1` 的访问。这与 C++ 的浅拷贝行为形成鲜明对比——C++ 中相同写法会产生两个指向同一堆内存的指针，导致双重 `free` 风险。

### 借用与引用的生命周期约束

所有权模型通过**借用（Borrowing）**机制允许临时使用数据而不转移所有权。借用规则规定：在同一作用域内，对同一数据要么存在任意数量的**不可变引用**（`&T`），要么存在**恰好一个可变引用**（`&mut T`），两者不能同时存在。这一规则在编译期消除了读写竞争（Write-Read Hazard）。

生命周期标注（Lifetime Annotation）用泛型参数 `'a` 表示引用的有效范围，例如函数签名 `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str` 明确声明返回引用的生命周期不超过输入引用中较短的那个。借用检查器（Borrow Checker）根据这些标注在编译期验证引用不会悬空（Dangling Reference）。

### C++ 智能指针对所有权语义的近似实现

C++ 没有原生的借用检查器，但 `std::unique_ptr<T>`（C++11 引入）提供了与 Rust 移动语义相近的独占所有权语义：`unique_ptr` 不可复制，只能通过 `std::move()` 转移控制权，转移后原指针为 `nullptr`。`std::shared_ptr<T>` 则对应引用计数（Reference Counting）语义，允许多所有者，但需要承担原子操作开销，且无法防止循环引用导致的内存泄漏——这是 Rust 所有权模型在设计上完全规避的问题（Rust 中等价的 `Rc<T>` 同样无法防循环引用，但 `Arc<T>` + `Weak<T>` 组合提供了明确的弱引用解决方案）。

C++ Core Guidelines 的规则 **R.3** 明确指出："原始指针不应拥有所有权"，这直接借鉴了 Rust 所有权模型中"所有权显式可见"的设计哲学。

---

## 实际应用

**嵌入式系统内存管理**：在无操作系统的裸机（bare-metal）环境中，不能依赖 GC 或 `malloc`/`free` 的正确配对。使用 Rust 所有权模型编写的嵌入式固件，通过栈分配的 `Box<T>` 替代堆分配，或使用静态生命周期 `'static` 的全局变量，可以在编译期保证内存安全，无需运行时检查。Arm Cortex-M 系列微控制器的 Rust 生态（`cortex-m` crate）广泛采用这一模式。

**并发数据结构**：Rust 标准库中的 `Mutex<T>` 将被保护的数据 `T` 直接包裹进锁内，只有调用 `.lock()` 获得 `MutexGuard` 才能访问数据，而 `MutexGuard` 本身是一个独占引用（`&mut T`），离开作用域时自动解锁。这种设计通过所有权和借用规则在类型系统层面强制"持锁访问"，消除了 C++ 中忘记解锁或在持锁状态下发生异常导致死锁的问题。

**C++ 代码迁移审计**：在审计遗留 C++ 代码时，可以将所有权模型作为分析框架——识别每个裸指针的"逻辑所有者"，将其替换为 `unique_ptr` 或 `shared_ptr`，并用 RAII（Resource Acquisition Is Initialization）包装器封装资源。Google 的 C++ 内部代码规范和 Chromium 项目均采用这一策略，将内存安全问题的修复率提高了约 40%。

---

## 常见误区

**误区一：所有权转移等同于深拷贝**。部分初学者认为 `let s2 = s1` 发生了内存复制。实际上，移动语义只转移栈上的元数据（指针、长度、容量），堆数据不复制，原变量直接失效。只有显式调用 `.clone()` 才会触发深拷贝，且实现了 `Copy` trait 的类型（如 `i32`、`bool`）按值复制不涉及所有权转移。

**误区二：借用检查器限制了程序员的表达能力，只能用不安全代码绕过**。事实上，借用检查器拒绝的代码模式中，绝大多数可以通过重构作用域边界、使用 `RefCell<T>` 进行运行时借用检查、或重新设计数据结构来满足编译期要求，而无需 `unsafe` 块。只有与硬件交互或调用 C FFI 等真正需要绕过抽象的场景才应使用 `unsafe`。

**误区三：C++ `unique_ptr` 与 Rust 所有权等价**。`unique_ptr` 仅在堆分配资源上提供独占语义，而 Rust 所有权作用于**所有类型的所有值**，包括栈变量和基本类型。此外，C++ 编译器不会像 Rust 借用检查器那样静态拒绝悬空引用——C++ 中函数返回局部变量的引用只产生警告而非错误，Rust 则是硬性编译错误。

---

## 知识关联

所有权模型建立在**栈与堆的内存布局**概念之上：栈上变量的生命周期由调用帧严格界定，所有权规则本质上是将这一确定性延伸到堆分配的资源上。理解为什么 `String` 需要所有权而 `&str` 不需要，必须先了解前者持有堆指针、后者是固定大小的切片引用这一物理差异。

在并发编程领域，所有权模型直接派生出 `Send` 和 `Sync` 两个 marker trait：`Send` 表示类型的所有权可以跨线程转移，`Sync` 表示类型的共享引用可以跨线程使用。这两个 trait 与所有权规则共同构成 Rust "无畏并发（Fearless Concurrency）"的理论基础，将数据竞争从运行时问题转变为编译期类型错误。

对于学习 C++ 现代化实践的工程师，所有权模型提供了一个评价框架：每当在代码审查中遇到裸指针参数时，应明确该参数传递的是所有权（应改为 `unique_ptr` 值传递）、可变借用（应改为非空引用 `T&`）还是不可变借用（应改为 `const T&`），这一三分法直接来自 Rust 所有权模型对指针语义的精确分类。