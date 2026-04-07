# 强化学习基础

## 概述

强化学习（Reinforcement Learning, RL）是一种通过**智能体与环境的交互**来学习最优行为策略的机器学习范式。与监督学习不同，强化学习不依赖带标签的训练样本，而是依靠环境返回的**奖励信号（reward）**来指导学习。智能体在每个时间步选择动作，环境返回新状态和标量奖励，智能体的目标是最大化长期累积奖励。

强化学习的理论基础可追溯至1957年Richard Bellman在其著作《Dynamic Programming》中提出的动态规划理论，以及Markov决策过程（MDP）的数学框架。1988年Richard Sutton发表时序差分学习（Temporal Difference Learning）论文，奠定了现代无模型强化学习的基础。现代强化学习的突破性进展包括：1992年Gerald Tesauro开发的TD-Gammon程序通过时序差分学习以2500个神经元掌握西洋双陆棋，达到世界顶级人类水准；2013年DeepMind将深度神经网络与Q-learning结合提出DQN（Mnih et al., 2013），在49款Atari游戏上平均超越人类水平229%；以及2016年AlphaGo结合策略梯度、价值网络与蒙特卡洛树搜索以4:1击败世界围棋冠军李世石。

强化学习在AI工程中的独特价值在于：它能解决**序列决策问题**，即当前动作影响未来状态和奖励的场景——这是监督学习无法直接处理的问题类型。理解强化学习是掌握RLHF（人类反馈强化学习）的先决条件，后者是当前大语言模型（如ChatGPT、Claude）对齐技术的核心机制。

**一个核心问题值得思考**：如果一个智能体在下棋游戏中每步都获得+0.1的小奖励，但只有真正赢棋才有实质意义，这种"密集奖励"的设计是否会帮助学习，还是会导致智能体学会钻空子？这正是奖励设计中最微妙的挑战之一，我们将在常见误区部分深入探讨。

---

## 核心原理

### 马尔可夫决策过程（MDP）

强化学习问题的标准数学描述是**马尔可夫决策过程**，由五元组 $(S, A, P, R, \gamma)$ 定义：

- **S**：状态空间（State space），可以是离散的（如棋盘格局，共 $3^{9}=19683$ 种井字棋状态）或连续的（如机器人关节角度构成的 $\mathbb{R}^n$ 空间）
- **A**：动作空间（Action space），离散（Atari游戏的18个按键）或连续（机械臂的关节扭矩）
- **P(s'|s,a)**：状态转移概率，给定状态 $s$ 和动作 $a$，转移到 $s'$ 的概率
- **R(s,a,s')**：奖励函数，执行动作后获得的即时标量奖励
- **γ ∈ [0,1)**：折扣因子（discount factor），控制未来奖励的当前价值

MDP的"马尔可夫性"要求：下一状态 $s'$ 仅取决于当前状态 $s$ 和动作 $a$，与历史轨迹无关，即 $P(s_{t+1}|s_t, a_t) = P(s_{t+1}|s_0,a_0,\ldots,s_t,a_t)$。

**累积折扣奖励**定义为：

$$G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$$

其中 $\gamma=0$ 时智能体只关注即时奖励，$\gamma \to 1$ 时等权重考虑所有未来奖励。以自动驾驶为例，若 $\gamma=0.99$，则10秒后的奖励被折扣为当前价值的 $0.99^{10} \approx 0.905$，而100秒后的奖励仅剩 $0.99^{100} \approx 0.366$，这鼓励智能体在保证长远安全的同时也重视近期行为的合理性。

### 策略与值函数

**策略（Policy）** $\pi(a|s)$ 是从状态到动作的映射，可以是确定性的（$\pi(s) = a$）或随机性的（$\pi(a|s)$ 为概率分布）。在探索阶段，随机策略有助于发现更优路径，而部署阶段通常使用确定性策略。

**状态值函数** $V^\pi(s) = \mathbb{E}_\pi[G_t | s_t = s]$ 表示从状态 $s$ 出发，遵循策略 $\pi$ 的期望累积折扣奖励。**动作值函数（Q函数）** $Q^\pi(s,a) = \mathbb{E}_\pi[G_t | s_t=s, a_t=a]$ 表示在状态 $s$ 执行动作 $a$ 后再遵循策略 $\pi$ 的期望回报。两者通过**Bellman方程**联系：

$$V^\pi(s) = \sum_a \pi(a|s) \sum_{s'} P(s'|s,a)\left[R(s,a,s') + \gamma V^\pi(s')\right]$$

**最优Q函数** $Q^*(s,a)$ 满足Bellman最优方程：

$$Q^*(s,a) = \sum_{s'} P(s'|s,a)\left[R + \gamma \max_{a'} Q^*(s',a')\right]$$

最优策略直接取 $\pi^*(s) = \arg\max_a Q^*(s,a)$。Bellman方程揭示了一个深刻的自洽性：最优值函数在其自身上满足递推关系，这是所有基于动态规划的RL算法的根本依据。

### Q-Learning：时序差分方法

Q-Learning是由Watkins（1989年博士论文）提出的一种**无模型（model-free）**的离策略（off-policy）算法，直接从与环境的交互中学习 $Q^*(s,a)$，无需知道转移概率 $P$。其更新规则为：

$$Q(s,a) \leftarrow Q(s,a) + \alpha\left[r + \gamma \max_{a'} Q(s',a') - Q(s,a)\right]$$

其中 $\alpha \in (0,1]$ 是学习率，方括号内的量 $\delta_t = r + \gamma \max_{a'} Q(s',a') - Q(s,a)$ 称为**TD误差（Temporal Difference error）**，衡量当前Q值估计与TD目标之间的差距。

**例如**，在一个简单的迷宫寻宝问题中，智能体在状态 $s_1$ 向右走（动作 $a_1$）获得奖励 $r=0$，到达状态 $s_2$，此时 $\max_{a'} Q(s_2, a') = 10$，若 $\alpha=0.1, \gamma=0.9$，则更新量为 $0.1 \times (0 + 0.9 \times 10 - Q(s_1, a_1))$。若 $Q(s_1,a_1)$ 初始为0，更新后变为0.9，每次交互都会使Q值向真实价值逼近。

DQN（Deep Q-Network）的关键创新是用神经网络 $Q(s,a;\theta)$ 逼近Q函数（Mnih et al., 2015），引入**经验回放（Experience Replay）**——将 $(s,a,r,s')$ 四元组存入容量为100万的缓冲区并随机采样32或64个样本的mini-batch——以及**目标网络（Target Network）**每隔1000步同步一次参数，解决训练不稳定和样本相关性问题。

### 策略梯度方法

策略梯度方法**直接参数化策略** $\pi(a|s;\theta)$，通过梯度上升最大化期望回报 $J(\theta) = \mathbb{E}_\pi[G_0]$。**策略梯度定理**（Sutton et al., 1999）给出：

$$\nabla_\theta J(\theta) = \mathbb{E}_\pi\left[\nabla_\theta \log \pi(a|s;\theta) \cdot Q^\pi(s,a)\right]$$

这个定理的优雅之处在于：即使环境转移概率未知，梯度仍可通过采样计算——$\nabla_\theta \log \pi$ 只需对策略网络求导，与环境动态无关。

REINFORCE算法用采样回报 $G_t$ 替代 $Q^\pi(s,a)$，但方差极高（因为轨迹的随机性累积导致回报估计噪声大）。**Actor-Critic**架构解决这一问题：Actor（策略网络）负责选择动作，Critic（值网络）负责评估动作，用优势函数

$$A(s,a) = Q(s,a) - V(s)$$

替代Q值，大幅降低梯度方差。直觉上，$A(s,a)>0$ 表示该动作比平均水平好，应增加其概率；$A(s,a)<0$ 则应减少。

**PPO（Proximal Policy Optimization）**由Schulman等人（2017年）在OpenAI提出，通过裁剪目标函数限制每次策略更新幅度：

$$L^{\text{CLIP}}(\theta) = \mathbb{E}_t\left[\min\left(r_t(\theta)\hat{A}_t,\ \text{clip}(r_t(\theta), 1-\varepsilon, 1+\varepsilon)\hat{A}_t\right)\right]$$

其中 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$ 为新旧策略的概率比，$\varepsilon$ 通常取0.1或0.2。PPO是目前工业界最广泛使用的策略梯度算法，也是RLHF训练ChatGPT等大语言模型的核心优化算法。

---

## 关键公式与模型总览

强化学习中最核心的公式体系可以归纳如下：

**Bellman期望方程**（用于策略评估）：
$$Q^\pi(s,a) = \mathbb{E}_{s'}\left[R(s,a,s') + \gamma \sum_{a'} \pi(a'|s') Q^\pi(s',a')\right]$$

**TD(λ)回报**（连接MC与TD的统一框架）：
$$G_t^\lambda = (1-\lambda)\sum_{n=1}^{\infty} \lambda^{n-1} G_t^{(n)}$$

其中 $\lambda=0$ 退化为单步TD，$\lambda=1$ 退化为蒙特卡洛回报。$\lambda$ 是Sutton（1988）提出的优雅超参数，允许算法在偏差（bias）和方差（variance）之间平衡。

**SAC（Soft Actor-Critic）最大熵目标**：
$$J(\pi) = \sum_t \mathbb{E}_{(s_t,a_t)\sim\rho_\pi}\left[R(s_t,a_t) + \alpha \mathcal{H}(\pi(\cdot|s_t))\right]$$

其中 $\mathcal{H}(\pi(\cdot|s)) = -\sum_a \pi(a|s)\log\pi(a|s)$ 为策略熵，$\alpha$ 为温度参数，控制探索与利用的平衡。SAC在机器人连续控制任务（如MuJoCo的HalfCheetah-v2）上以约300万步训练达到5000以上得分，远超早期策略梯度方法。

---

## 实际应用

**游戏AI**：DQN在49个Atari游戏中平均超过人类水平229%（Mnih et al., 2015年Nature论文），输入为原始像素帧（84×84灰度图，连续4帧叠加），动作空间为18个离散按键，神经网络包含3层卷积层和2层全连接层，共约180万参数。AlphaGo Zero（Silver et al., 2017）完全不使用人类棋谱，仅通过自博弈和策略梯度，在40天、2900万局自博弈训练后超越所有人类选手，最终版本AlphaZero还将围棋、国际象棋、将棋统一在同一算法框架下。

**机器人控制**：连续动作空间的机器人操控使用SAC算法，Haarnoja等人（2018）在OpenAI Gym的Ant-v2（8自由度四足机器人）任务上，SAC以约300万步交互达到人类设计控制器的性能，而PPO需要约1000万步。这使机器人在抓取任务中对未见过的物体形状有更好的泛化能力，因为最大熵策略天然鼓励探索多样化的抓取