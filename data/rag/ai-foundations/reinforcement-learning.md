---
concept: reinforcement-learning
subdomain: ai-foundations
difficulty: 7
prereqs: [ml-basics, neural-network-basics]
---

# 强化学习基础

## 核心概念

强化学习（Reinforcement Learning, RL）是机器学习的一个分支，研究智能体如何在与环境的交互中通过试错来学习最优行为策略。核心框架：Agent在State下采取Action，环境返回Reward和新State。

## 基本框架

```
Agent ← 观察状态 s ← Environment
Agent → 执行动作 a → Environment
Agent ← 获得奖励 r ← Environment
Agent ← 新状态 s' ← Environment
```

关键要素：
- **状态 (State)**: 环境的描述
- **动作 (Action)**: Agent可以执行的操作
- **奖励 (Reward)**: 环境给Agent的即时反馈
- **策略 (Policy)**: 状态到动作的映射 π(s) → a
- **价值函数**: 从某状态出发的累积奖励期望

## 核心算法

### Q-Learning
学习动作价值函数 Q(s,a)：
```
Q(s,a) ← Q(s,a) + α [r + γ max Q(s',a') - Q(s,a)]
```
- α: 学习率
- γ: 折扣因子（权衡即时奖励和未来奖励）

### Policy Gradient
直接优化策略函数：
- REINFORCE: 蒙特卡洛策略梯度
- Actor-Critic: 结合策略和价值函数

### PPO (Proximal Policy Optimization)
OpenAI 开发的主流RL算法：
- 通过裁剪目标函数限制策略更新幅度
- 训练稳定，调参简单
- RLHF中训练奖励模型的标准算法

## 探索与利用（Exploration vs Exploitation）

RL的核心权衡：
- **探索**: 尝试未知动作，获取新信息
- **利用**: 选择已知最优动作，获取最大奖励
- **ε-greedy**: 以ε概率随机探索，1-ε概率选择最优

## 与LLM的关系

强化学习在LLM领域的关键应用：
- **RLHF**: 使用人类偏好训练奖励模型，再用PPO优化LLM
- **DPO**: 直接偏好优化，跳过显式奖励建模
- **Constitutional AI**: 基于原则的自我改进

## 与ML基础和神经网络的关系

强化学习建立在ML和深度学习基础之上。深度RL（Deep RL）使用神经网络来逼近策略和价值函数，使RL可以处理高维状态空间。
