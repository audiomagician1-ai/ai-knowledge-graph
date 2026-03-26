---
id: "typescript-basics"
concept: "TypeScript基础"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 4
is_milestone: false
tags: ["TS"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# TypeScript基础

## 概述

TypeScript是由微软在2012年10月正式发布的开源编程语言，版本1.0于2014年发布。它是JavaScript的超集，在保留所有JavaScript语法的基础上，增加了静态类型注解系统和编译时类型检查能力。TypeScript代码通过`tsc`（TypeScript Compiler）编译器转译为普通JavaScript，可运行在任何支持JS的环境中。

TypeScript的核心价值在于将运行时错误提前暴露到编译阶段。例如，调用一个可能为`undefined`的对象属性，在JavaScript中要等到浏览器执行时才报错，而TypeScript在编写代码时即可标红提示。对于AI工程前端来说，与后端模型API对接时，请求/响应的数据结构往往复杂（如嵌套的推理结果、流式输出的token对象），TypeScript的接口定义能精确约束这些结构，防止字段名拼写错误或类型不匹配导致的无声bug。

TypeScript在2023年Stack Overflow开发者调查中，以64%的"喜爱度"位列最受欢迎语言第五名。Next.js、React、Vue等主流前端框架均默认提供TypeScript模板，AI工程领域的Vercel AI SDK、LangChain.js也全部使用TypeScript编写。

## 核心原理

### 类型注解与基本类型

TypeScript通过冒号语法为变量、函数参数和返回值添加类型注解：

```typescript
let modelName: string = "gpt-4o";
let temperature: number = 0.7;
let isStreaming: boolean = true;
let tokenCounts: number[] = [128, 256, 512];
```

基本类型包括：`string`、`number`、`boolean`、`null`、`undefined`、`symbol`、`bigint`，以及TypeScript特有的`any`（关闭类型检查）、`unknown`（安全的any）、`never`（永不返回的类型）、`void`（无返回值函数）。

特别需要注意`any`与`unknown`的区别：对`any`类型的值可以直接调用任意方法，而`unknown`类型的值必须经过类型断言或类型守卫才能使用，这使`unknown`在处理来自API的不确定响应时更加安全。

### 接口与类型别名

`interface`用于定义对象的形状，`type`用于定义类型别名，二者在大多数场景下可互换，但存在关键差异：

```typescript
// 定义AI对话消息结构
interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: number; // ?表示可选属性
}

// 类型别名可以表达联合类型
type ModelProvider = "openai" | "anthropic" | "google";
```

`interface`支持声明合并（declaration merging），即同名interface会自动合并字段，而`type`不允许重复声明。在扩展方面，`interface`使用`extends`关键字，`type`使用`&`交叉类型运算符。AI工程实践中，通常用`interface`定义API请求/响应体，用`type`定义联合类型枚举。

### 联合类型、交叉类型与类型守卫

联合类型用`|`表示"或"关系，交叉类型用`&`表示"且"关系：

```typescript
// 流式响应可能是文本块或结束信号
type StreamChunk = TextDelta | FinishReason;

interface TextDelta {
  type: "text_delta";
  text: string;
}
interface FinishReason {
  type: "finish";
  stopReason: "stop" | "length" | "tool_calls";
}
```

类型守卫（Type Guard）是TypeScript在运行时缩窄类型范围的机制，常见方式有`typeof`、`instanceof`、`in`运算符和自定义谓词函数：

```typescript
function handleChunk(chunk: StreamChunk) {
  if (chunk.type === "text_delta") {
    // 此处TypeScript自动将chunk类型缩窄为TextDelta
    console.log(chunk.text);
  }
}
```

### 枚举与字面量类型

TypeScript的`enum`生成真实的JavaScript对象，而字符串字面量联合类型（如`"left" | "right"`）在编译后不产生额外代码，因此在AI工程前端中，通常优先使用字面量类型代替enum以减小打包体积。`const enum`是例外，它在编译时内联数值，不生成对象。

## 实际应用

**封装LLM API调用**：使用TypeScript为大语言模型的请求参数建模，可以防止将`max_tokens`误写为`maxTokens`（OpenAI API使用下划线命名）：

```typescript
interface OpenAIChatRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;      // 0到2之间
  max_tokens?: number;
  stream?: boolean;
}

async function callLLM(request: OpenAIChatRequest): Promise<string> {
  const response = await fetch("/api/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
  const data = await response.json();
  return data.choices[0].message.content;
}
```

**处理流式输出**：AI应用常见的Server-Sent Events（SSE）流式响应，可以用TypeScript的`AsyncGenerator`类型精确描述异步迭代器，使调用方清楚每次迭代产出的是`string`类型的token片段。

**React组件Props类型**：在展示AI生成内容的组件中，使用`interface`定义Props可以在IDE中获得完整的自动补全，例如定义`onMessageUpdate: (message: ChatMessage) => void`回调类型，比JavaScript的注释文档更可靠。

## 常见误区

**误区一：认为`any`是TypeScript的"逃生舱"可以随便使用**。频繁使用`any`会导致类型检查形同虚设，TypeScript社区称这种代码为"AnyScript"。正确做法是：当类型不确定时优先使用`unknown`，配合类型守卫处理；对于第三方库缺少类型定义的情况，应安装`@types/xxx`包或编写`.d.ts`声明文件。

**误区二：混淆类型注解与类型断言**。`const x: string = getValue()` 是编译器对`getValue()`返回值进行检查的注解；而`const x = getValue() as string` 是程序员强制告诉编译器"我比你更清楚"的断言，会跳过类型检查。在AI工程中处理`fetch`返回的`response.json()`时，应使用`unknown`接收再做校验，而不是直接`as MyType`断言，因为网络数据的实际结构可能与预期不符。

**误区三：认为TypeScript类型在运行时依然存在**。TypeScript的类型信息在编译为JavaScript时被完全擦除，接口、类型别名、类型注解在浏览器中无法访问。因此，运行时的数据校验（如验证API响应结构）必须使用`zod`、`io-ts`等运行时校验库，不能依赖TypeScript类型来保证运行时安全。

## 知识关联

**前置知识衔接**：TypeScript的静态类型系统是对"静态vs动态类型"概念的具体实现，`tsc --strict`模式开启后会同时启用`strictNullChecks`（禁止null赋值给非null类型）等7个严格检查项，这是理解TypeScript为什么比"加了注解的JavaScript"更严格的关键。JavaScript的原型链、闭包、异步模型在TypeScript中完全保留，TypeScript只在其上叠加类型层。

**后续学习方向**：掌握基础类型注解后，TypeScript高级类型引入了`Partial<T>`、`Required<T>`、`Pick<T,K>`等内置工具类型，以及条件类型`T extends U ? X : Y`，可以基于现有接口自动派生新类型。泛型`<T>`则允许编写类型安全的复用函数，例如编写一个通用的`parseResponse<T>(raw: unknown): T`函数，让调用方指定期望的返回类型，这在封装多个不同LLM端点时极为实用。