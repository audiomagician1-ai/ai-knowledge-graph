---
id: "tree-of-thought"
concept: "思维树(ToT)"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 7
is_milestone: false
tags: ["Prompt"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 100.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 思维树（Tree of Thoughts, ToT）

## 概述

思维树（Tree of Thoughts，ToT）由普林斯顿大学的Shunyu Yao、Dian Yu、Jeffrey Zhao等人于2023年5月发表在论文《Tree of Thoughts: Deliberate Problem Solving with Large Language Models》（arXiv:2305.10601）中首次提出，随后被收录于NeurIPS 2023。它将思维链（CoT）的单条线性推理扩展为树状结构：在每个推理步骤，LLM同时生成多个候选"思维节点"，由评估器对各节点打分，再由搜索算法（BFS或DFS）决定哪些节点值得继续展开，从而在解空间中系统性地搜索最优推理路径。

ToT的核心动机来自对CoT局限性的量化观察：在"24点游戏"（Game of 24）基准测试中，标准CoT（gpt-4）成功率仅约 **4%**，思维链自洽（CoT-SC）也只有约 **9%**，而ToT配合BFS策略（每层保留 b=5 个节点）可将成功率提升至 **74%**，是CoT的18倍以上（Yao et al., 2023）。这一差距证明：对于需要多步组合推理的任务，线性推理结构存在根本性的信息瓶颈，而树状搜索可以有效突破这一瓶颈。

ToT设计灵感来源于认知科学中的双系统理论——Kahneman在《Thinking, Fast and Slow》（2011）中将人类思维分为"系统1"（快速直觉）和"系统2"（慢速审慎）。CoT模拟系统1的流畅输出，而ToT通过引入搜索与评估模拟系统2的审慎决策，使LLM具备"尝试—评估—放弃—换路"的认知能力。

---

## 核心原理

### 思维节点的生成（Thought Generation）

ToT在每个推理步骤生成 **T 个**（原论文典型值 T=5）独立候选思维，而非CoT的单一后续步骤。生成策略分两种：

- **采样法（Sample）**：以相同Prompt独立调用LLM共T次，利用温度参数（temperature=0.7~1.0）保证多样性。适合答案空间大、思维形式自由的任务（如创意写作）。
- **提议法（Propose）**：单次调用LLM，在Prompt中明确要求"列出所有可能的下一步操作"，一次性获得多个候选。适合步骤结构明确的任务（如24点游戏中枚举四则运算组合）。

每个节点的状态定义为：$s = (x, z_{1:i})$，其中 $x$ 是原始问题输入，$z_{1:i}$ 是从根节点到当前节点的推理步骤序列。节点 $s$ 的生成可形式化为：

$$
z_{i+1}^{(1)}, z_{i+1}^{(2)}, \ldots, z_{i+1}^{(T)} \sim p_\theta(\cdot \mid x, z_{1:i})
$$

即以当前状态为条件，从LLM的输出分布中采样T个候选下一步思维。

### 思维节点的评估（Thought Evaluation）

每个候选节点必须经过评估才能决定是否继续展开。ToT使用LLM本身作为评估器，通过以下两种方式打分：

**方式一：分类打分**，要求LLM对当前节点输出三档判断：
- `sure`：此路径大概率可达到正确答案
- `likely`：有可能，但需要进一步探索
- `impossible`：此路径已陷入死局，立即剪枝

**方式二：数值打分**，要求LLM给出 0~10 的连续评分，配合贪心策略保留前 b 个节点。

评估Prompt的典型结构为：

```
你是一个推理评估器。给定以下问题和当前推理路径，判断该路径是否值得继续。
问题：使用数字 [3, 9, 7, 13] 和四则运算得到24。
当前路径：3 + 9 = 12，12 × ? 
候选下一步：12 × 2（但2不在剩余数字中）
评估：impossible（剩余数字为 [7, 13]，无法凑出2）
```

这种中间节点剪枝机制是ToT区别于CoT-SC的本质差异：**CoT-SC只在终点投票选最优答案，ToT在每个中间节点就执行淘汰**，避免在无效路径上浪费后续推理资源。

### 搜索算法的选择（Search Strategy）

ToT支持两种主要搜索策略，超参数直接影响API调用总量：

**广度优先搜索（BFS）**：
- 每层展开所有保留节点的全部T个候选，评估后保留得分最高的前 **b** 个节点，再展开下一层
- 原论文24点游戏配置：T=5，b=5，d=4（最多4步运算），总调用次数约为 $5 \times 5^4 = 3125$ 次（含评估调用）
- 适合：推理步骤短（d ≤ 5）、需要找全局最优的任务

**深度优先搜索（DFS）**：
- 优先沿单路径深入，遇到评估分数低于阈值时回溯到最近分支点
- 适合：推理深度大（d > 5）、存在长链推理的任务（如逻辑谜题、多步规划）
- 可设置回溯深度上限 $d_{max}$ 防止过度回溯

整体计算复杂度约为：

$$
C_{\text{ToT}} = O(T \times b^d)
$$

而CoT的复杂度为 $O(1)$（单路径），CoT-SC为 $O(k)$（k条独立路径终点投票）。因此ToT的推理代价远高于CoT，需权衡任务复杂度与API成本。

---

## 关键公式与算法实现

ToT的完整算法流程如下（以BFS为例）：

```python
def tot_bfs(problem: str, llm, T: int = 5, b: int = 5, d: int = 4) -> str:
    """
    ToT广度优先搜索实现
    problem: 原始问题字符串
    T: 每节点生成的候选思维数
    b: 每层保留的最优节点数
    d: 最大搜索深度
    """
    # 初始状态：仅包含问题本身
    current_layer = [{"state": problem, "history": []}]

    for depth in range(d):
        candidates = []

        for node in current_layer:
            # Step 1: 生成T个候选下一步思维
            thoughts = llm.generate_thoughts(
                problem=problem,
                history=node["history"],
                n=T
            )

            for thought in thoughts:
                new_state = {
                    "state": thought,
                    "history": node["history"] + [thought]
                }
                # Step 2: 评估候选节点
                score = llm.evaluate_thought(
                    problem=problem,
                    history=new_state["history"]
                )
                if score != "impossible":
                    candidates.append((new_state, score))

        # Step 3: 保留前b个高分节点
        candidates.sort(key=lambda x: x[1], reverse=True)
        current_layer = [c[0] for c in candidates[:b]]

        # 提前终止：若某节点已得到完整答案
        for node in current_layer:
            if llm.is_terminal(node["state"]):
                return node["state"]

    # 返回最终层得分最高的节点
    return current_layer[0]["state"] if current_layer else "未找到解"
```

以上代码中，`generate_thoughts`、`evaluate_thought`、`is_terminal` 均为对LLM的Prompt调用封装，体现了ToT"用LLM生成 + 用LLM评估"的自洽设计。

---

## 实际应用场景

### 24点游戏（论文基准任务）

原论文使用24点游戏作为核心基准：给定4个1~13的整数，要求用加减乘除恰好得到24。

例如，给定 `[3, 9, 7, 13]`，ToT的BFS推理树可能展开如下：
- 第1步候选：`3+9=12`、`9-3=6`、`13-7=6`、`3×9=27`、`13+7=20`
- 评估后保留：`13-7=6`（剩余[3,9,6]）、`3+9=12`（剩余[7,13,12]）……
- 第4步：`13-9=4, 4×(7-3)=16`（不等于24，剪枝）vs `(9-3)×(13-7)=36`（不等于24，剪枝）vs `13-7=6, 6×(9/3)=18`……
- 最终找到：`(9-3)×(13/13+3) = ?` → `3×(7+1)=24`（需要 `13-13=0`，不合法）…实际路径为 `13-9=4，4×(7-3)=16`（失败）直至找到 `9-7=2，2×3=6，6×(13-9)=24`（成功）

### 创意写作规划

在需要先生成多个故事大纲再精选深化的任务中，ToT可先生成5个不同叙事走向，由评估器依据"情节张力""角色一致性"等维度打分，保留前2个大纲后再展开各自的章节细节。这比单次CoT生成一个大纲后直接写正文，更能系统性地探索创意空间。

### 代码调试与多步推理

针对复杂算法题（如LeetCode Hard难度），ToT可在每一步尝试多种算法策略（动态规划、贪心、回溯），评估器判断每种策略的可行性（如时间复杂度是否满足约束），再沿可行策略展开具体实现，有效避免在不可行算法上浪费实现步骤。

---

## 与CoT系列方法的横向对比

| 维度 | CoT | CoT-SC | ToT |
|------|-----|--------|-----|
| 推理路径数 | 1条线性路径 | k条独立路径（终点投票） | 树状多路径（中间剪枝） |
| 错误可恢复性 | 不可回溯 | 不可回溯 | 支持回溯与剪枝 |
| API调用复杂度 | $O(1)$ | $O(k)$ | $O(T \times b^d)$ |
| 24点游戏成功率 | ~4% | ~9% | ~74% |
| 适用任务类型 | 单步或短链推理 | 答案具有多数一致性的任务 | 多步组合推理、需探索的任务 |
| 代表论文发表年份 | 2022（Wei et al.） | 2022（Wang et al.） | 2023（Yao et al.） |

思考问题：**如果将ToT的评估器替换为外部确定性函数（如数学验证器），而非依赖LLM自评，成功率和成本会如何变化？这种混合架构适合哪类任务？**

---

## 常见误区与使用陷阱

**误区一：将ToT视为万能提升方案**
ToT的API调用量约为CoT的 $T \times b^{d-1}$ 倍（24点游戏配置下约125倍），对于简单问答、文本摘要等任务，CoT的4%→74%这类质变不会出现，而成本却成倍增加。**ToT仅在任务具有明确中间状态、可评估的里程碑式推理步骤时才有显著收益。**

**误区二：忽略评估器本身的误判率**
LLM评估器并非完美：若某个正确路径被错误标记为"impossible"，BFS会永久丢弃该路径（剪枝不可逆）。原论文在mini crosswords任务上观察到，ToT的评估准确率约为60~70%，存在将正确路径误杀的风险。可通过降低剪枝阈值（将"impossible"改为得分低于2分才剪枝）来缓解。

**误区三：混淆ToT与ReAct的适用场景**
ReAct（Yao et al., 2022）将推理与工具调用交替进行，适合需要外部信息检索的任务；ToT是纯粹的多路径推理框架，不涉及外部工具调用。在需要搜索引擎、代码执行等外部反馈的场景下，应优先考虑ReAct或其扩展，而非ToT。

**误区四：忽视Prompt设计对生成多样性的影响**
若生成阶段的Prompt设计不当（如temperature=0），T个候选思维将高度雷同，树的实际有效分支数趋近于1，退化为CoT，完全失去ToT的搜索价