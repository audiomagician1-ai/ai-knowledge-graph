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
---
# 强化学习基础

## 概述

强化学习（Reinforcement Learning, RL）是一种通过**智能体（Agent）与环境交互来学习最优行为策略**的机器学习范式。与监督学习不同，强化学习不依赖标注数据集，而是依靠环境反馈的奖励信号（Reward Signal）来驱动学习——智能体执行动作后，环境返回一个标量奖励值，智能体的目标是最大化长期累积奖励。这一框架最早可追溯到1950年代Bellman提出的动态规划理论，1989年Watkins提出Q-learning算法后形成现代体系，2013年DeepMind将深度神经网络与Q-learning结合（DQN），使智能体首次在Atari游戏上超越人类水平。

强化学习之所以在AI工程中至关重要，是因为它是目前唯一能在**序列决策问题**中自主发现最优策略的框架。从游戏AI（AlphaGo）到机器人控制，再到当前大语言模型对齐技术（RLHF），强化学习都是底层机制。掌握其核心概念——MDP、策略、值函数、Q-learning和策略梯度——是理解这些应用的必要前提。

## 核心原理

### 马尔可夫决策过程（MDP）

强化学习问题的数学形式化是**马尔可夫决策过程**，用五元组 $(S, A, P, R, \gamma)$ 表示：
- $S$：状态空间（State Space）
- $A$：动作空间（Action Space）
- $P(s'|s,a)$：状态转移概率，满足马尔可夫性质——下一状态只依赖当前状态和动作，与历史无关
- $R(s,a)$：即时奖励函数
- $\gamma \in [0,1)$：折扣因子，控制未来奖励的权重衰减

累积折扣奖励定义为 $G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$。折扣因子 $\gamma=0.99$ 意味着100步后的奖励仅折算为当前价值的约37%（$0.99^{100} \approx 0.37$）。马尔可夫性质是MDP成立的核心假设：如果环境不满足此性质，需要引入部分可观测MDP（POMDP）处理历史依赖。

### 策略与值函数

**策略（Policy）** $\pi(a|s)$ 定义了智能体在状态 $s$ 下选择动作 $a$ 的概率分布，是强化学习的学习目标。策略分为确定性策略 $\pi(s) \to a$ 和随机策略 $\pi(a|s) \to [0,1]$，随机策略在探索与利用权衡（Exploration-Exploitation Tradeoff）中更具优势。

**值函数**有两种形式，均以策略 $\pi$ 为条件：
- **状态值函数** $V^\pi(s) = \mathbb{E}_\pi[G_t | S_t = s]$：从状态 $s$ 出发遵循策略 $\pi$ 的期望累积奖励
- **动作值函数（Q函数）** $Q^\pi(s,a) = \mathbb{E}_\pi[G_t | S_t=s, A_t=a]$：在状态 $s$ 执行动作 $a$ 后遵循策略 $\pi$ 的期望累积奖励

两者通过**贝尔曼方程**递归关联：$V^\pi(s) = \sum_a \pi(a|s) \sum_{s'} P(s'|s,a)[R(s,a) + \gamma V^\pi(s')]$。最优值函数满足贝尔曼最优方程，此时策略为最优策略 $\pi^*$。

### Q-learning 算法

Q-learning是1989年Watkins提出的**无模型（Model-Free）时序差分（TD）控制**算法，其更新规则为：

$$Q(s,a) \leftarrow Q(s,a) + \alpha \left[ R + \gamma \max_{a'} Q(s',a') - Q(s,a) \right]$$

其中 $\alpha$ 为学习率，方括号内为**TD误差**（目标值与当前估计的差）。Q-learning的关键特性是**离策略（Off-Policy）**学习——行为策略（如ε-贪心探索）和目标策略（贪心选取 $\max_{a'}Q$）可以不同，这使得智能体能利用历史经验池（Replay Buffer）进行批量更新。

DQN（Deep Q-Network）用神经网络 $Q(s,a;\theta)$ 替代Q表，引入**经验回放（Experience Replay）**和**目标网络（Target Network）**两个关键技巧解决训练不稳定问题：目标网络参数每隔固定步数（原论文为10,000步）才从主网络复制，切断了训练中的自举循环。

### 策略梯度方法

与Q-learning间接优化策略不同，**策略梯度（Policy Gradient）**直接对策略参数 $\theta$ 求梯度以最大化期望回报。**策略梯度定理**给出：

$$\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\left[ \nabla_\theta \log \pi_\theta(a|s) \cdot Q^{\pi_\theta}(s,a) \right]$$

直觉上，这等价于增加高回报动作的概率，降低低回报动作的概率。REINFORCE算法用蒙特卡洛采样的 $G_t$ 替代 $Q$ 值，但方差极高。Actor-Critic方法引入Critic网络估计基线（Baseline），将TD误差作为优势函数（Advantage Function）$A(s,a) = Q(s,a) - V(s)$，在降低方差的同时保持无偏性。PPO（Proximal Policy Optimization）通过**裁剪目标函数** $L^{CLIP} = \mathbb{E}[\min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t)]$ 限制每次策略更新幅度，成为目前工程中最常用的策略梯度算法，也是RLHF中的核心优化器。

## 实际应用

**游戏与棋盘博弈**：AlphaGo Zero完全依赖自我对弈的强化学习，使用MCTS结合策略网络和价值网络，在无人类棋谱数据的情况下以100:0击败AlphaGo。

**推荐系统序列优化**：将用户会话建模为MDP，用户点击/停留作为奖励信号，动作为推荐内容。YouTube和Netflix使用Actor-Critic变体优化长期用户留存，而非仅优化单次点击率。

**大语言模型对齐（RLHF预备）**：GPT系列模型的指令跟随能力通过PPO算法优化，将人类偏好评分作为奖励信号。理解Q值代表"当前对话状态下某回复的长期价值期望"是理解RLHF奖励建模的直接前提。

**机器人控制**：连续动作空间（电机扭矩）要求使用策略梯度而非Q-learning，SAC（Soft Actor-Critic）算法通过最大化熵正则化项 $\alpha \mathcal{H}(\pi)$ 实现探索与利用的自动平衡。

## 常见误区

**误区一：奖励越稠密越好**。强化学习中奖励设计（Reward Shaping）是工程难点。为加速训练而设计的稠密中间奖励可能导致**奖励黑客（Reward Hacking）**——智能体找到非预期方式获取高分但不完成真实目标。经典案例：MuJoCo中的爬行机器人学会了翻滚而非行走来最大化前进奖励。稀疏奖励（只在任务完成时给+1）虽训练慢，但目标对齐更可靠。

**误区二：Q-learning和策略梯度可以互换**。Q-learning只适用于**离散动作空间**（Q表或DQN对每个离散动作输出Q值），在连续动作空间（如机械臂的关节角度）中无法直接使用。策略梯度天然支持连续动作空间，但样本效率低于Q-learning（On-Policy方法需丢弃旧数据）。选择算法必须首先考虑动作空间类型。

**误区三：折扣因子 $\gamma$ 是可以随意设置的超参数**。$\gamma$ 不仅影响学习速度，还定义了智能体的"时间视野"。$\gamma=1$（无折扣）在无限时域问题中会导致值函数发散；$\gamma$ 过小使智能体只关注即时奖励，无法学习需要长期规划的策略（如围棋开局布局）。对于需要100步以上长期规划的任务，$\gamma$ 通常需要设置在0.99以上。

## 知识关联

**前置知识连接**：神经网络基础中的反向传播算法直接用于训练DQN和策略网络——Q-learning的TD误差等价于回归损失（MSE），而策略梯度的对数概率梯度需要通过自动微分实现。机器学习基础中的**过拟合与泛化**在强化学习中表现为策略对训练环境的过拟合，经验回放（Replay Buffer）的随机采样机制对应监督学习中的随机批次梯度下降。

**后续概念衔接**：RLHF（人类反馈强化学习）直接使用PPO算法和奖励模型（代替环境
