# LLM API调用（OpenAI/Claude）

## 概述

LLM API调用是通过标准化HTTP接口与远端大语言模型服务交互的工程实践，开发者无需部署千亿参数模型即可获得GPT-4o、Claude 3.5 Sonnet等前沿模型的推理能力。OpenAI于2020年6月随GPT-3发布首个商业LLM API（Brown et al., 2020），该论文同期证明了少样本提示（few-shot prompting）在API层面的有效性，彻底改变了NLP应用的开发范式。Anthropic于2023年3月推出Claude API，在接口设计上做出了与OpenAI显著不同的工程决策——将系统提示词从消息数组中独立为顶层`system`参数，这一差异源于Anthropic对"宪法AI"（Constitutional AI）训练方法中系统指令地位的特殊强调（Bai et al., 2022）。

正确调用LLM API涉及认证安全、消息结构设计、采样参数调优、流式处理、错误重试、Token成本管理等六个维度，任何一个维度的失误都会导致功能异常或成本失控。本文系统梳理两大主流API的技术细节与工程陷阱。

## 核心原理

### 请求结构与认证机制

两个API均通过HTTP请求头传递密钥。OpenAI使用`Authorization: Bearer sk-proj-...`格式；Claude则需要同时提供`x-api-key: sk-ant-...`和`anthropic-version: 2023-06-01`两个请求头，后者为**必填项**，缺失时服务器返回400错误而非降级处理，这是初次接入时最常见的失败原因。

消息结构是两者最核心的差异所在。OpenAI的Chat Completions API（`POST /v1/chat/completions`）将系统提示词嵌入消息数组：

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "你是专业的代码审查工程师"},
    {"role": "user", "content": "审查以下Python函数"},
    {"role": "assistant", "content": "好的，请提供代码"},
    {"role": "user", "content": "def add(a,b): return a+b"}
  ],
  "max_tokens": 512,
  "temperature": 0.2
}
```

Claude的Messages API（`POST /v1/messages`）将系统提示词提升为顶层参数，消息数组中不允许出现`system`角色：

```json
{
  "model": "claude-3-5-sonnet-20241022",
  "system": "你是专业的代码审查工程师",
  "messages": [
    {"role": "user", "content": "审查以下Python函数：def add(a,b): return a+b"}
  ],
  "max_tokens": 512,
  "temperature": 0.2
}
```

Claude API还要求消息数组必须以`user`角色开头，且`user`/`assistant`必须交替出现，连续出现同一角色会触发422验证错误——这一强制性的对话结构约束是OpenAI所没有的。

### 采样参数的数学含义

LLM生成文本的过程本质是在词汇表上进行概率采样。设模型对下一个token的logit向量为 $z \in \mathbb{R}^{|V|}$，经过temperature缩放后的概率分布为：

$$p_i = \frac{\exp(z_i / T)}{\sum_{j} \exp(z_j / T)}$$

其中 $T$ 即`temperature`参数。当 $T \to 0$ 时，分布趋向于one-hot（贪心解码，输出极为确定）；当 $T = 1$ 时，使用模型原始概率；当 $T > 1$ 时，分布趋于均匀，随机性增大。

`top_p`（nucleus sampling，Holtzman et al., 2020）则是动态截断：将token按概率降序排列，选取累积概率恰好超过 $p$ 的最小token集合 $V_p$，仅在此集合内采样：

$$V_p = \arg\min_{S \subseteq V} |S| \quad \text{s.t.} \quad \sum_{i \in S} p_i \geq p$$

实践中，OpenAI官方建议**不要同时修改`temperature`和`top_p`**，因为两者叠加会使生成行为难以预测。对于代码生成、数据抽取等需要确定性的任务，建议设置`temperature=0`；对于创意写作，建议`temperature=0.7~1.0`，`top_p=0.9`。

`max_tokens`参数控制最大输出长度，但注意两个API计费均基于**输入+输出**的总token数，而非仅输出。GPT-4o的上下文窗口为128K tokens，`claude-3-5-sonnet-20241022`的上下文窗口为200K tokens，超出上限会触发400错误。

### 响应格式解析

OpenAI的响应体中，生成文本位于`response.choices[0].message.content`，停止原因（`stop`/`length`/`content_filter`）位于`response.choices[0].finish_reason`，Token用量在`response.usage`下包含`prompt_tokens`、`completion_tokens`、`total_tokens`三个字段。

Claude的响应文本位于`response.content[0].text`（注意是数组，因为Claude支持`tool_use`等多类型content block），停止原因在`response.stop_reason`（值为`end_turn`/`max_tokens`/`stop_sequence`），Token统计字段为`input_tokens`和`output_tokens`（命名与OpenAI不同，混用代码时易产生KeyError）。

## 关键方法与工程实践

### 流式输出（Streaming）

对于长文本生成场景，流式输出可将首字节延迟从数十秒降低到毫秒级，显著改善用户体验。两个API均通过Server-Sent Events（SSE）协议实现流式传输，请求时设置`stream=True`即可。

OpenAI Python SDK流式处理示例：
```python
from openai import OpenAI
client = OpenAI()
with client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "写一篇500字的文章"}],
    stream=True
) as stream:
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
```

Anthropic SDK的流式处理语法略有不同，使用`stream()`上下文管理器，且事件类型更为细粒度（`text_delta`、`input_json_delta`等），支持在流中监听tool use的JSON构建过程。

### 错误处理与重试策略

LLM API的常见错误码及处理策略：
- **429 RateLimitError**：触发速率限制，应实施指数退避（exponential backoff）重试，建议初始等待1秒，最大等待60秒，最多重试5次。
- **400 BadRequestError**：请求参数错误（如Claude缺少`anthropic-version`头、消息角色顺序错误），此类错误不应重试。
- **500/529 InternalServerError**：服务端临时故障，可重试。
- **context_length_exceeded**：输入超过模型上下文窗口，需压缩消息历史（如仅保留最近N轮对话或使用摘要压缩）。

例如，使用`tenacity`库实现OpenAI API的健壮重试：
```python
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import RateLimitError

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(5)
)
def call_openai(messages):
    return client.chat.completions.create(
        model="gpt-4o", messages=messages
    )
```

### Token计算与成本管理

精确的Token计算对于控制API成本至关重要。OpenAI官方提供`tiktoken`库用于离线计算token数：

```python
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")
tokens = enc.encode("你好，世界！Hello World!")
print(len(tokens))  # 输出：9（中文按UTF-8子词分割，效率低于英文）
```

以GPT-4o的定价为例（截至2024年底），输入为$2.50/百万tokens，输出为$10.00/百万tokens。若每次调用消耗500输入tokens + 200输出tokens，则每1000次调用成本为：$0.00125 × 1000 + 0.002 × 1000 = $3.25。Claude 3.5 Sonnet的输入定价为$3.00/百万tokens，输出为$15.00/百万tokens，成本结构与OpenAI相近但输出更贵。

**提示缓存（Prompt Caching）**是两者均支持的重要成本优化手段：Claude API通过在`system`或消息内容中添加`{"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}}`标记，可将缓存命中的输入token成本降低至90%；OpenAI则对超过1024 tokens的重复前缀自动触发缓存，缓存命中价格为标准价格的50%。

## 实际应用

### 案例：多轮对话状态管理

LLM API本身是**无状态**的——每次请求必须携带完整的对话历史，服务端不保存上下文。这意味着随着对话轮次增加，输入token线性增长。

一个实用的滑动窗口对话管理器：
```python
class ConversationManager:
    def __init__(self, system_prompt: str, max_history_tokens: int = 8000):
        self.system_prompt = system_prompt
        self.history = []
        self.max_tokens = max_history_tokens

    def add_turn(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        # 当历史超限时，删除最早的一轮（保留system prompt不计入）
        while self._estimate_tokens() > self.max_tokens and len(self.history) > 2:
            self.history.pop(0)
            self.history.pop(0)

    def get_openai_messages(self):
        return [{"role": "system", "content": self.system_prompt}] + self.history
```

### 案例：Function Calling / Tool Use

OpenAI的Function Calling（2023年6月引入）和Claude的Tool Use（2024年4月引入）是LLM API最重要的能力扩展，允许模型在生成文本时触发外部函数调用，实现真正的AI Agent。

OpenAI定义工具的结构：
```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "获取指定城市的当前天气",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {"type": "string", "description": "城市名称"}
      },
      "required": ["city"]
    }
  }
}
```

当模型决定调用工具时，响应中`finish_reason`为`tool_calls`（OpenAI）或`tool_use`（Claude），开发者解析出函数名和参数后执行本地函数，将结果以`tool`角色（OpenAI）或`tool_result`（Claude）添加回消息列表，再次发起请求，模型据此生成最终回答。

## 常见误区

**误区一：认为`temperature=0`保证完全确定性输出。** 实际上，由于GPU浮点运算的非确定性（不同批次大小、并行度下浮点加法顺序不同），相同参数的多次调用仍可能产生细微差异。OpenAI官方文档明确指出`temperature=0`仅"大体确定"（mostly deterministic），需要`seed`参数配合才能提高复现性（但仍不保证100%确定）。

**误区二：Claude的`system`参数等同于OpenAI消息数组中的system消息。** 两者在模型内部的处理权重不同——Claude在RLHF训练阶段对`system`参数赋予了更高的指令遵循优先级，而OpenAI的system消息与其他消息在技术上处于同等地位，优先级完全依赖提示词措辞。

**误区三：直接将两个API的客户端代码混用。** `openai` Python SDK与`anthropic` Python SDK在异步支持、流式接口、错误类型上均有差异，混用会导致难以调试的运行时错误。建议通过适配器模式（Adapter Pattern）封装统一接口。

**误区四：忽视`max_tokens`对输出截断的影响。** 设置过小的`max_tokens`会导致输出在句子中间被截断，`finish_reason`变为`length`而非`stop`。在解析结构化输出（如JSON）时，截断后的JSON无法被正确解析，应始终检查`finish_reason`。

**误区五：在生产环境中明文存储API密钥。** API密钥一旦泄露将立即被扫描工具发现并滥用，正确做法是通过环境变量（`os.environ["