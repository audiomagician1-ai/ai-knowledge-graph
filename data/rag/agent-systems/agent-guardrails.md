---
concept: agent-guardrails
subdomain: agent-systems
difficulty: 7
prereqs: [agent-safety]
---

# Agent安全护栏

## 核心概念

Agent安全护栏（Guardrails）是部署在Agent执行管道中的安全检查和限制机制，确保Agent的行为在预设边界内，防止产生有害、不合规或意外的结果。

## 护栏类型

### 1. 输入护栏（Input Guardrails）
检查和过滤进入Agent的输入：
- **Prompt注入检测**: 识别恶意指令嵌入
- **内容审核**: 过滤有害或不当请求
- **权限验证**: 确认用户有权执行请求的操作

### 2. 输出护栏（Output Guardrails）
验证Agent的输出是否安全合规：
- **毒性检测**: 检查输出是否包含有害内容
- **事实校验**: 验证输出的事实准确性
- **合规检查**: 确认输出符合法规要求（如PII保护）

### 3. 执行护栏（Execution Guardrails）
限制Agent的执行行为：
- **操作白名单**: 限定允许的工具和操作
- **资源配额**: 限制API调用次数、执行时间、成本
- **人工审批**: 高风险操作需人工确认

### 4. 反馈护栏（Feedback Guardrails）
在Agent循环中持续监控：
- **行为异常检测**: 识别Agent行为偏离预期
- **循环检测**: 防止Agent陷入无限循环
- **退化检测**: 发现Agent能力下降趋势

## 实现架构

```
[用户输入] → [输入护栏] → [Agent推理] → [执行护栏] → [工具调用] → [输出护栏] → [返回用户]
                                                ↑                      |
                                                +---- [反馈护栏] ←----+
```

## 关键技术

- **NeMo Guardrails**: NVIDIA开源的对话护栏框架
- **Guardrails AI**: 结构化输出验证框架
- **Constitutional AI**: 基于宪法原则的自我约束
- **Llama Guard**: Meta的安全分类模型

## 护栏的权衡

护栏设计需要在安全性和可用性之间平衡：
- **过严**: Agent能力受限，用户体验差
- **过松**: 安全风险增加
- **误判**: 合法请求被错误拦截

## 与Agent Safety的关系

护栏是Agent安全（Agent Safety）的工程实现层面。安全关注原则和风险评估，护栏是将安全原则转化为可执行代码的实践。
