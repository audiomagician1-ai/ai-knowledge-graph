# Agent循环（感知-推理-行动）

## 概述

Agent循环（Perception-Reasoning-Action Loop，简称PRA循环）是自主AI Agent持续运行的基本执行单元，定义了Agent如何从外部环境获取信息、经内部LLM推理后生成决策、再将决策转化为可执行动作的完整一次迭代过程。与单次LLM调用的本质区别在于：PRA循环的每一轮输出会改变环境状态，环境状态的变化又成为下一轮循环的输入，形成真正意义上的闭环控制系统（Closed-Loop Control System）。

PRA循环的理论根源可追溯至Norbert Wiener在1948年出版的《控制论》（*Cybernetics: Or Control and Communication in the Animal and the Machine*）中提出的负反馈回路（Negative Feedback Loop）理论。在认知科学领域，Neisser（1976）在《认知心理学》中进一步将这一思想演化为"感知-行动循环"（Perception-Action Cycle），描述生物智能体如何通过持续的感知与行动交互适应环境。现代AI Agent框架——包括LangChain的`AgentExecutor`、AutoGPT、OpenAI Assistants API的Run循环——均将PRA循环作为运行时调度的核心机制。

该循环解决了LLM"无状态、单轮输出"的根本局限：通过循环迭代，Agent可处理跨步骤依赖的复杂任务，动态响应工具调用结果，并根据中途获取的新信息修正执行路径。以一个调研报告生成任务为例：第1轮循环解析用户需求并调用搜索工具，第2轮循环汇总搜索结果并判断信息充分性，第3轮循环生成最终报告——任何步骤的中间结果均可触发额外的循环次数，这种**动态扩展的执行深度**是静态工作流无法实现的。

---

## 核心原理

### 感知阶段（Perception）：将世界状态序列化为Token序列

感知阶段的本质是将Agent所处的"世界状态"序列化为LLM可消费的Token序列，构建当前循环的完整上下文窗口（Context Window）。输入来源通常包含四类结构化数据：

1. **系统提示词（System Prompt）**：定义Agent的角色、可用工具列表（Tool Schema）及行为约束，在每轮循环中保持不变。
2. **用户消息（User Message）**：原始指令或用户的最新追加输入。
3. **历史对话记录（Conversation History）**：包含之前所有轮次的`assistant`消息和`tool`消息，承载跨轮次的状态信息。
4. **工具返回结果（Tool Message）**：上一轮循环中工具调用（Tool Call）所返回的结构化数据，格式与OpenAI的`tool_call_id`绑定机制对应。

以OpenAI Chat Completions API的消息格式为例，感知阶段输出的消息列表在第2轮循环时形如：

```json
[
  {"role": "system", "content": "你是一个数据分析助手，可以使用以下工具：[get_weather, search_web]"},
  {"role": "user", "content": "查询北京今天的天气并判断是否适合户外活动"},
  {"role": "assistant", "content": null, "tool_calls": [{"id": "call_abc123", "function": {"name": "get_weather", "arguments": "{\"city\": \"北京\"}"}}]},
  {"role": "tool", "tool_call_id": "call_abc123", "content": "晴，气温28°C，湿度40%，风速3级"}
]
```

**感知阶段最关键的工程挑战是上下文窗口溢出**：随着循环轮次增加，历史消息Token数累积，可能超过模型上下文上限（GPT-4o为128K Token，Claude 3.5 Sonnet为200K Token）。常见的缓解策略包括：滑动窗口截断（Sliding Window Truncation）、LLM摘要压缩（Summary Compression）、以及向量化的外部记忆检索（Retrieval-Augmented Memory）。对长期运行的Agent，感知阶段的内存管理策略直接决定了Agent能否在数百轮循环后仍保持对早期关键信息的访问能力。

### 推理阶段（Reasoning）：LLM的决策生成机制

推理阶段将感知阶段构建的上下文输入LLM，模型输出下一步行动计划。LLM的输出在结构上只有两种终态：**终止输出（Final Answer）**——直接生成文本响应，标志任务完成；**工具调用指令（Tool Call）**——生成结构化的函数调用请求，标志任务仍在进行中。

Yao等人（2023）提出的**ReAct框架**（*ReAct: Synergizing Reasoning and Acting in Language Models*，发表于ICLR 2023）在推理阶段引入了显式的"思考链"（Chain-of-Thought, CoT），强制LLM在生成动作前输出推理过程。ReAct的标准输出格式为：

```
Thought: 用户需要判断户外活动的适宜性，我已获取天气数据（28°C，晴，风速3级），
         需要综合分析温度、紫外线和风力因素。
Action: search_web
Action Input: {"query": "北京紫外线指数 2024年今日"}
```

ReAct框架在6个不同基准任务（HotpotQA、Fever、ALFWorld、WebShop等）上的实验表明，相比纯粹的Chain-of-Thought提示，ReAct将任务成功率提升了约34%（Yao et al., 2023）。

推理阶段的另一关键机制是**停止条件判断（Termination Condition）**：LLM必须基于当前上下文判断任务是否已充分完成。若停止条件过于宽松，Agent会在信息不足时提前返回；若停止条件过于严格，Agent会陷入无意义的循环（Loop）。OpenAI Assistants API通过`max_steps`参数（默认值为10）强制终止无限循环。

### 行动阶段（Action）：工具调用与环境交互

行动阶段将推理阶段生成的工具调用指令转化为对实际工具的执行，并将执行结果注入下一轮循环的感知上下文中，这是PRA循环中**唯一与外部世界发生真实交互**的阶段。

行动阶段的工具类型可分为四大类：
- **信息检索类**（Read-only）：搜索引擎、数据库查询、API读取，不改变外部世界状态。
- **写入执行类**（Write）：发送邮件、创建文件、调用外部服务写接口，会不可逆地改变外部世界状态。
- **子Agent调用类**（Sub-Agent Delegation）：在多Agent系统中，将子任务委托给专门化的子Agent执行。
- **环境控制类**（Environment Control）：如网页浏览器操控（Playwright/Selenium）、代码执行沙箱（Code Interpreter）。

行动阶段的关键工程问题是**工具调用的幂等性（Idempotency）与错误处理**：若工具调用失败（超时、参数错误、权限不足），Agent必须将错误信息作为新的感知输入，在下一轮推理中决定是重试、换用备选工具，还是直接向用户报告失败原因。

---

## 关键公式与形式化描述

PRA循环可以用马尔可夫决策过程（Markov Decision Process, MDP）进行形式化。设：
- $s_t$ 为第 $t$ 轮循环时的环境状态（包含上下文窗口内容）
- $a_t$ 为LLM在状态 $s_t$ 下生成的行动（工具调用指令或终止输出）
- $\mathcal{T}(s_{t+1} | s_t, a_t)$ 为状态转移函数（由工具执行结果决定）
- $r_t$ 为第 $t$ 步的奖励信号（在ReAct等框架中通常为稀疏的任务完成奖励）

则Agent循环的目标可形式化为：

$$\pi^* = \arg\max_{\pi} \mathbb{E}\left[\sum_{t=0}^{T} \gamma^t r_t \,\Big|\, \pi\right]$$

其中 $\pi$ 表示LLM的决策策略（即给定上下文 $s_t$ 输出行动 $a_t$ 的条件分布），$\gamma \in (0,1]$ 为折扣因子，$T$ 为最大循环轮次。

在实际工程中，绝大多数基于LLM的Agent并不显式优化上述目标函数（因为LLM权重通常在推理时固定），而是通过**提示词工程**和**工具设计**来隐式引导策略 $\pi$ 趋近最优。这也是LLM-based Agent与强化学习Agent的根本区别之一。

**循环终止条件**的形式化表达为：

$$\text{Terminate} = \begin{cases} \text{True} & \text{if } a_t = \text{FinalAnswer} \text{ or } t \geq T_{\max} \\ \text{False} & \text{otherwise} \end{cases}$$

其中 $T_{\max}$ 是系统设置的最大步数限制，用于防止无限循环。

---

## 实际应用与典型案例

### 案例一：LangChain AgentExecutor的循环实现

LangChain的`AgentExecutor`是PRA循环最广泛使用的工业实现之一。其`_iter_next_step()`方法精确对应三个阶段：调用`agent.plan()`方法（推理阶段）→ 执行工具（行动阶段）→ 将`ToolMessage`追加至`intermediate_steps`（感知阶段的输入构建）。

`AgentExecutor`通过`max_iterations`参数（默认值15）控制最大循环次数，通过`early_stopping_method`参数（可选`"force"`或`"generate"`）决定达到最大次数时的处理方式：`"force"`直接返回错误信息，`"generate"`则让LLM基于当前上下文强制生成一个最终答案。

### 案例二：OpenAI Assistants API的Run对象

OpenAI Assistants API将PRA循环封装为一个`Run`对象，其状态机（State Machine）精确映射了三个阶段的流转：`queued` → `in_progress`（推理阶段） → `requires_action`（行动阶段等待工具结果提交） → `in_progress`（下一轮感知+推理） → `completed`（循环终止）。

当`Run`进入`requires_action`状态时，开发者需要在规定时间内（默认10分钟超时）通过`submit_tool_outputs`接口提交工具执行结果，否则`Run`将进入`expired`状态并终止循环。这一设计将行动阶段的工具执行控制权完全交还给开发者，体现了OpenAI对工具安全性的考量。

### 案例三：多轮循环的Token成本累积问题

在实际生产部署中，PRA循环的每一轮都会消耗LLM API调用的Token费用，且由于历史消息会随循环积累，**总Token消耗量呈二次方增长**：若每轮新增消息平均为 $k$ Token，第 $t$ 轮循环的总输入Token数为 $\approx t \cdot k$，则 $T$ 轮循环的总Token成本为 $\sum_{t=1}^{T} t \cdot k = \frac{T(T+1)}{2} \cdot k$，复杂度为 $O(T^2 \cdot k)$。

例如：一个执行20轮循环、每轮新增500 Token的任务，总输入Token消耗约为 $\frac{20 \times 21}{2} \times 500 = 105{,}000$ Token，若使用GPT-4o（输入价格$5/1M Token），该单次任务的LLM调用成本约为$0.525，这在高频调用场景下需要重点关注。

---

## 常见误区与反模式

**误区一：将循环次数等同于任务复杂度**

循环次数的增加并不总意味着任务更复杂——更多情况下，它反映的是工具设计不合理或提示词引导不充分。一个设计良好的工具应在单次调用中返回完整信息，而不是强迫Agent通过多轮循环拼凑答案。例如，将"搜索"和"内容提取"拆分为两个独立工具会导致每次信息获取需要2轮循环；将其合并为一个`search_and_extract`工具则可减少一半的循环次数。

**误区二：忽略行动阶段的副作用（Side Effects）**

许多开发者在设计Agent时假设工具调用是纯粹的"查询"操作，但写入类工具（发送邮件、提