---
id: "reinforcement-learning"
concept: "强化学习基础"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 7
is_milestone: false
tags: ["AI", "强化学习"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 强化学习基础

## 概述

强化学习（Reinforcement Learning，RL）是一种让智能体（Agent）通过与环境交互、获取奖励信号来学习最优决策策略的机器学习范式。与监督学习不同，强化学习的训练信号不是标注好的"正确答案"，而是稀疏、延迟的奖励（Reward），智能体必须自主探索才能发现哪些行为序列能够带来最大累积回报。

强化学习的理论根源可追溯至1950年代Bellman提出的动态规划理论，以及心理学中的操作性条件反射。现代强化学习框架由Sutton和Barto在其1998年著作《Reinforcement Learning: An Introduction》中系统化，该书定义了至今仍在使用的核心术语体系。2013年DeepMind发布DQN（Deep Q-Network），首次将深度神经网络与Q-learning结合，在49款Atari游戏上超越人类水平，标志着深度强化学习时代的到来。

强化学习对AI工程师的重要性在于它是目前训练大语言模型"对齐"人类偏好的核心技术路径——RLHF（Reinforcement Learning from Human Feedback）直接依赖本文所述的策略梯度方法。理解MDP框架和值函数估计，是理解PPO算法如何被用于GPT-4、Claude等模型训练的必要前提。

---

## 核心原理

### 马尔可夫决策过程（MDP）

强化学习问题被形式化为马尔可夫决策过程，用五元组 $(S, A, P, R, \gamma)$ 表示：
- $S$：状态空间（State Space）
- $A$：动作空间（Action Space）
- $P(s'|s,a)$：状态转移概率，即在状态 $s$ 执行动作 $a$ 后转移到 $s'$ 的概率
- $R(s,a)$：即时奖励函数
- $\gamma \in [0,1)$：折扣因子，决定未来奖励的衰减速率

MDP的"马尔可夫性质"要求：下一状态 $s'$ 只依赖当前状态 $s$ 和动作 $a$，与历史无关。这一假设简化了问题，但在实际任务（如部分可观测环境）中需要通过状态设计来近似满足。折扣因子 $\gamma=0.99$ 意味着100步后的奖励仅相当于当前的 $0.99^{100} \approx 0.366$ 倍权重。

### 值函数与Bellman方程

智能体的目标是最大化期望累积折扣奖励 $G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$。为此引入两个核心评估函数：

**状态值函数** $V^\pi(s) = \mathbb{E}_\pi[G_t | S_t = s]$，表示从状态 $s$ 出发、按策略 $\pi$ 行动的期望回报。

**动作值函数（Q函数）** $Q^\pi(s,a) = \mathbb{E}_\pi[G_t | S_t = s, A_t = a]$，表示在状态 $s$ 执行动作 $a$ 后再按策略 $\pi$ 行动的期望回报。

Bellman方程建立了当前状态与后续状态值之间的递推关系：
$$V^\pi(s) = \sum_a \pi(a|s) \sum_{s'} P(s'|s,a)[R(s,a) + \gamma V^\pi(s')]$$

最优Bellman方程（Bellman Optimality Equation）将策略优化转为求解：
$$Q^*(s,a) = R(s,a) + \gamma \sum_{s'} P(s'|s,a) \max_{a'} Q^*(s',a')$$

### Q-Learning：无模型价值学习

Q-learning是一种无模型（Model-Free）的时序差分（TD）学习算法，直接通过经验样本逼近最优Q函数，更新规则为：

$$Q(s,a) \leftarrow Q(s,a) + \alpha \left[ R + \gamma \max_{a'} Q(s',a') - Q(s,a) \right]$$

方括号内的项 $\delta = R + \gamma \max_{a'} Q(s',a') - Q(s,a)$ 称为**TD误差**，它度量了当前Q值估计与目标值之间的差距。DQN的关键创新在于用神经网络参数化 $Q(s,a;\theta)$，并引入**经验回放**（Experience Replay）和**目标网络**（Target Network）两项技术来稳定训练——目标网络每隔固定步数（如每1000步）从主网络复制参数，避免训练目标频繁变动。

### 策略梯度方法

与Q-learning学习值函数再间接推导策略不同，策略梯度方法直接参数化策略 $\pi_\theta(a|s)$ 并对期望回报求梯度。**策略梯度定理**给出了梯度计算公式：

$$\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta} \left[ \nabla_\theta \log \pi_\theta(a|s) \cdot Q^{\pi_\theta}(s,a) \right]$$

实践中用蒙特卡洛采样得到的回报 $G_t$ 替代 $Q$ 值，即得REINFORCE算法（Williams，1992）。为减小方差，引入**基线**（Baseline）：用 $G_t - V(s_t)$ 替换 $G_t$，差值 $A(s,a) = Q(s,a) - V(s)$ 称为**优势函数**（Advantage Function）。Actor-Critic架构同时维护策略网络（Actor）和值函数网络（Critic），前者用优势函数指导策略更新，后者降低梯度估计的方差。

---

## 实际应用

**游戏AI**：AlphaGo Zero完全基于自我对弈的强化学习（无监督学习预训练），仅用3天训练便超越了此前借助人类棋谱的AlphaGo版本，Q值被重新定义为落子位置的胜率估计。

**机器人控制**：OpenAI在2019年训练机械手完成魔方复原，使用PPO（Proximal Policy Optimization）算法，在模拟环境中进行约13000年等效训练时长后迁移到真实机械手。PPO的核心约束是裁剪目标函数，限制每次策略更新的幅度不超过 $\epsilon=0.2$。

**大语言模型对齐**：InstructGPT（2022）使用RLHF训练流程：首先通过监督微调得到初始策略，再用人类偏好数据训练奖励模型，最后用PPO优化语言模型，使其生成内容更符合人类偏好。此处语言模型的每个token生成步骤对应MDP中的一个动作。

---

## 常见误区

**误区一：奖励越密集越好**
许多初学者认为给予更频繁的奖励信号能加快学习。实际上，过度的奖励塑造（Reward Shaping）会导致"奖励黑客"问题——智能体找到一种意外的方式最大化所设计的奖励函数，而非完成真正目标。OpenAI的船只赛艇实验中，智能体学会了原地打转收集赛道中的加速道具而不前进，因为这样得分更高。

**误区二：Q-learning和策略梯度可以随意互换**
Q-learning仅适用于离散动作空间（无法对连续动作取argmax），而REINFORCE及Actor-Critic天然支持连续动作空间。在机器人控制（关节角度连续）中必须使用策略梯度或其变体（如DDPG、SAC），而非DQN。两者在样本效率和稳定性上也存在系统性差异。

**误区三：折扣因子只是数学技巧**
$\gamma < 1$ 不只是为了让无限求和收敛。$\gamma$ 的取值直接影响智能体的"短视程度"：$\gamma=0.9$ 时智能体实际只关注约10步以内的奖励（因为 $0.9^{10} \approx 0.35$），而 $\gamma=0.999$ 则需要关注约1000步的长期效果。在稀疏奖励任务中将 $\gamma$ 设得过低会导致智能体根本学不到达成远期目标的行为。

---

## 知识关联

**前置知识**：本文的Q-learning收敛性依赖**机器学习基础**中的随机梯度下降收敛理论；策略梯度方法中的神经网络函数逼近依赖**神经网络基础**中的反向传播算法——策略网络的参数梯度 $\nabla_\theta \log \pi_\theta$ 通过标准自动微分框架（PyTorch/JAX）计算。

**后续方向**：掌握本文的策略梯度和PPO算法后，**RLHF人类反馈强化学习**中的奖励模型训练和语言模型微调流程将直接沿用这些工具——语言模型的token预测策略 $\pi_\theta(\text{token}|\text{context})$ 与MDP中的 $\pi_\theta(a|s)$ 形式完全对应，人类偏好评分充当奖励函数 $R$，只需将动作空间替换为词表（通常为50000+个token）。