---
id: "agent-frameworks-comparison"
concept: "Agent Frameworks Comparison"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 6
is_milestone: false
tags: ["Agent"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 76.6
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# Agent Frameworks Comparison

## 概述

Agent Frameworks Comparison 是对主流 AI Agent 开发框架的设计哲学、架构差异和适用场景的系统性比较，难度等级 6/9。选择正确的框架直接影响开发效率、系统可维护性和生产可靠性。目前市场上框架众多，各有侧重，理解其核心权衡是工程决策的关键。

本概念建立在 Agent Loop、Tool Use、Multi-Agent 等基础之上，与 Agent 调试和部署实践密切相关。

## 主流框架概览

### 框架对比矩阵

| 框架 | 核心理念 | 抽象层次 | 多 Agent | 生态 | 学习曲线 | 生产就绪 |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **LangChain** | 组件链式编排 | 高 | ✅ (LangGraph) | 最大 | 中 | 🟡 |
| **LlamaIndex** | 数据索引+查询 | 中 | 🟡 | 大 | 低 | ✅ |
| **CrewAI** | 角色扮演协作 | 高 | ✅ (核心) | 中 | 低 | 🟡 |
| **AutoGen** | 对话式多 Agent | 中 | ✅ (核心) | 中 | 中 | 🟡 |
| **Semantic Kernel** | 企业级 SDK | 中 | ✅ | 中 | 高 | ✅ |
| **smolagents** | 极简 Python | 低 | ❌ | 小 | 极低 | 🟡 |
| **OpenAI Agents SDK** | 原生 API | 低 | ✅ | 小 | 低 | ✅ |

### 架构哲学对比

```
LangChain / LangGraph:
  ┌─────────────────────┐
  │   StateGraph (图)    │  ← 显式状态机
  │   Node → Edge → Node│
  │   条件分支/循环      │
  └─────────────────────┘
  哲学: "一切皆为图节点"
  适合: 复杂工作流, 需要精确控制流程

CrewAI:
  ┌─────────────────────┐
  │   Crew              │
  │   ├── Agent (角色)   │  ← 角色 + 目标 + 工具
  │   ├── Task (任务)    │  ← 任务描述 + 预期输出
  │   └── Process        │  ← sequential / hierarchical
  └─────────────────────┘
  哲学: "像管理团队一样管理 Agent"
  适合: 多角色协作, 创意任务

AutoGen:
  ┌─────────────────────┐
  │  ConversableAgent   │
  │   ↕ 对话             │  ← Agent 间通过消息通信
  │  ConversableAgent   │
  │   ↕ 对话             │
  │  ConversableAgent   │
  └─────────────────────┘
  哲学: "Agent 通过对话协作"
  适合: 对话驱动的问题解决, 代码生成
```

## 选型决策树

```
你的需求是什么？
│
├── RAG / 数据查询为主
│   └── ✅ LlamaIndex (最佳数据索引+查询抽象)
│
├── 复杂工作流 + 精确控制
│   └── ✅ LangGraph (显式状态图, 条件分支)
│
├── 多角色协作任务
│   ├── 简单协作 → ✅ CrewAI (最快上手)
│   └── 复杂对话式 → ✅ AutoGen (灵活对话模式)
│
├── 企业级 / .NET 生态
│   └── ✅ Semantic Kernel (微软生态)
│
├── 快速原型 / 学习
│   └── ✅ smolagents (HuggingFace, 极简)
│
└── OpenAI 模型为主 + 最少依赖
    └── ✅ OpenAI Agents SDK (原生 handoff)
```

## 代码风格对比

### 同一任务：Web 搜索 + 总结

```python
# === LangGraph ===
from langgraph.graph import StateGraph
graph = StateGraph(State)
graph.add_node("search", search_node)
graph.add_node("summarize", summarize_node)
graph.add_edge("search", "summarize")
app = graph.compile()

# === CrewAI ===
from crewai import Agent, Task, Crew
researcher = Agent(role="Researcher", tools=[search_tool])
writer = Agent(role="Writer")
task1 = Task(description="搜索相关信息", agent=researcher)
task2 = Task(description="撰写总结", agent=writer)
crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
crew.kickoff()

# === smolagents ===
from smolagents import CodeAgent, DuckDuckGoSearchTool
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)
agent.run("搜索并总结最新AI进展")
```

## 常见误区

1. **选最流行的**: LangChain 最流行但抽象层多，简单任务反而过度工程
2. **忽视锁定风险**: 深度绑定框架后迁移成本高，优先选抽象层薄的
3. **多 Agent = 更好**: 大多数任务单 Agent + 多工具就够了，多 Agent 增加调试复杂度
4. **框架 = 生产就绪**: 框架提供脚手架，生产级可靠性（重试/监控/限流）需自行实现

## 与相邻概念关联

- **前置**: Agent Loop、Tool Use — 理解 Agent 基本工作原理
- **关联**: Multi-Agent — 多 Agent 框架的设计模式
- **关联**: Agent Debugging — 不同框架的调试体验差异显著
- **下游**: Agent Deployment — 框架选型影响部署方案
- **参考**: LangChain Basics、LlamaIndex Basics — 两大主流框架的深入学习
