---
id: "agent-tool-creation"
concept: "Agent工具创造"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 8
is_milestone: false
tags: ["Agent", "高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# Agent工具创造

## 概述

Agent工具创造（Tool Creation by Agent）是指大语言模型驱动的Agent在执行任务时，不仅能够调用预定义的工具，还能够自主生成、测试和优化新工具代码的能力。与传统的Function Calling仅从固定工具集中选择调用不同，工具创造要求Agent主动识别"当前工具库无法有效解决当前问题"这一缺口，并通过生成可执行的Python函数来填补这一缺口，从而动态扩展自身的行动空间。

这一能力的研究集中爆发于2023年。2023年5月，普林斯顿大学的Cai等人在论文《Large Language Models as Tool Makers》（LATM）中首次系统性地将工具创造任务分离为"制造者（Maker）"和"使用者（User）"两个角色，Maker负责生成Python函数，User负责以自然语言形式调用。同年10月，Wang等人提出的**CREATOR框架**进一步引入四阶段闭环流程（创建→决策→执行→精化），将工具创造与Agent反思机制深度耦合（Wang et al., 2023）。这两个框架共同标志着Agent能力从"工具调用"向"工具制造"的范式转变，将LLM的代码生成能力从一次性答案输出转化为可持久化复用的知识资产。

工具创造解决的核心问题是**静态工具库的覆盖边界**。当任务涉及特定格式转换、领域专用计算（如特殊日历系统的日期换算）或非标准API封装时，预置工具库必然存在盲区。具备工具创造能力的Agent可以在零样本（zero-shot）条件下生成对应工具，并在工具库中持久化存储以供后续任务复用，从而实现跨任务的累积式知识增长。

---

## 核心原理

### LATM框架：分角色协作生成

LATM的核心设计哲学是**利用模型能力差异实现成本-效果平衡**。框架规定：使用高能力模型（论文原版使用GPT-4）作为Tool Maker，使用低成本模型（GPT-3.5-turbo）作为Tool User。Maker接收任务类型描述和3~5个具体示例，生成一个带有完整文档字符串（docstring）的通用Python函数；User则仅接收函数签名与docstring，通过自然语言描述调用该工具完成具体实例。

Maker的提示词结构有严格规范：必须包含函数功能描述、输入输出类型注解（Python typing模块）、以及至少一个可通过`assert`语句自动验证的测试用例。若生成的函数在测试用例上运行失败，则触发自动重生成流程（最多重试3次）。

LATM在**BIG-Bench Hard**测试集（包含23个推理任务类别）上的实验显示，对于适合工具化的任务类别（如日期理解、多步算术），Tool Maker+Tool User组合的推理成本比纯GPT-4方案降低约**10倍**，同时在这些类别上保持相近的准确率（Cai et al., 2023）。这一结果说明：工具一旦生成后，同类型任务的后续推理成本可以大幅压缩。

### CREATOR框架：四阶段闭环反思

CREATOR将工具创造拆解为四个可追踪、可回滚的阶段：

1. **创建（Creation）**：Agent根据任务描述生成一个通用Python工具函数，要求函数参数化程度高，绝不硬编码具体输入值。例如，针对"计算某年是否为闰年"的任务，应生成接受`year: int`参数的函数，而非将具体年份写死。
2. **决策（Decision）**：Agent判断新生成的工具接口是否足以覆盖当前任务的输入输出需求，或需要细化参数设计（如添加可选参数处理边界情况）。
3. **执行（Execution）**：在受控沙箱环境（如`subprocess`隔离进程）中运行工具，同时捕获标准输出（`stdout`）和完整异常栈（`traceback`）。
4. **精化（Rectification）**：若执行结果与预期不符，Agent读取`traceback`中的具体错误行号和异常类型，针对性修改工具代码，形成最多5轮的修复循环。

CREATOR在**MATH数据集**（Hendrycks et al., 2021，包含12500道竞赛级数学题）上的实验表明，四阶段流程相较于直接代码生成方法PAL（Program-Aided Language Models）提升了约**8个百分点**的解题准确率。核心增益来自精化阶段：初版代码中约32%的错误属于可被`traceback`明确定位的边界逻辑错误（如整数除法与浮点除法混用），这类错误通过一次精化即可修复（Wang et al., 2023）。

### 工具持久化与语义检索机制

工具创造的长期价值依赖于**工具库的持久化存储与高效检索**。新生成的工具以Python模块（`.py`文件）形式写入工具库，同时为每个工具的docstring生成向量嵌入（通常使用`text-embedding-ada-002`或本地`all-MiniLM-L6-v2`模型），存入向量数据库（如Chroma或FAISS）。

当新任务到来时，Agent首先用任务描述的嵌入向量在工具库中检索（余弦相似度），若最高相似度得分超过阈值（经验值通常设为**0.78~0.85**），则直接复用已有工具；若低于阈值，则触发新工具创造流程。检索命中时，User仅需接收工具签名和docstring，无需重新调用高成本Maker模型，从而实现跨会话的知识积累。

---

## 关键公式与算法

工具库检索的核心判断逻辑基于余弦相似度阈值决策：

$$
\text{决策}(q, \mathcal{T}) = \begin{cases} \text{复用工具} \ t^* & \text{if} \ \max_{t \in \mathcal{T}} \cos(\vec{q}, \vec{t}) \geq \tau \\ \text{创造新工具} & \text{otherwise} \end{cases}
$$

其中 $\vec{q}$ 为当前任务描述的嵌入向量，$\vec{t}$ 为工具库中各工具docstring的嵌入向量，$\tau$ 为相似度阈值（通常取0.80），$t^* = \arg\max_{t \in \mathcal{T}} \cos(\vec{q}, \vec{t})$。

以下是一个简化的LATM工具生成与验证流程示例（Python伪代码）：

```python
import subprocess, textwrap

def tool_maker(task_description: str, examples: list[dict], llm_maker) -> str:
    """
    调用高能力LLM生成工具函数，并通过assert测试用例自动验证。
    返回通过验证的函数源代码字符串。
    """
    prompt = build_maker_prompt(task_description, examples)
    
    for attempt in range(3):  # 最多重试3次
        code = llm_maker.generate(prompt)
        # 提取函数定义（去除markdown代码块标记）
        func_code = extract_python_code(code)
        
        # 自动运行内嵌的assert测试用例
        test_result = subprocess.run(
            ["python", "-c", func_code],
            capture_output=True, text=True, timeout=10
        )
        if test_result.returncode == 0:
            return func_code  # 验证通过，返回工具代码
        else:
            # 将traceback反馈给LLM进行修复（精化阶段）
            prompt = build_rectification_prompt(func_code, test_result.stderr)
    
    raise RuntimeError(f"工具生成失败，已重试3次。最后错误：{test_result.stderr}")

def tool_user(task_instance: str, tool_code: str, llm_user) -> str:
    """
    调用低成本LLM，仅凭工具签名和docstring完成具体实例。
    """
    # 只向User暴露签名与文档，不暴露实现细节
    tool_signature = extract_signature_and_docstring(tool_code)
    prompt = build_user_prompt(task_instance, tool_signature)
    return llm_user.generate(prompt)
```

**例如**，在处理"将儒略历（Julian Calendar）日期转换为公历日期"这类任务时，预置工具库中通常不包含儒略历转换函数。LATM的Maker（GPT-4）会生成一个接受`year: int, month: int, day: int`参数的`julian_to_gregorian()`函数，内嵌`assert julian_to_gregorian(1582, 10, 4) == (1582, 10, 14)`作为测试用例（1582年10月4日儒略历对应格里历10月14日，即历史上的历法切换点）。User（GPT-3.5-turbo）随后仅调用此函数处理后续的同类型查询，无需重新理解历法转换逻辑。

---

## 实际应用

### 科学计算与数学推理任务

在MATH、GSM8K等数学基准测试中，工具创造框架允许Agent为每类题型（如求多项式根、矩阵行列式计算）生成专用的Sympy封装函数，避免重复在推理链中手工推导。CREATOR在MATH数据集的**代数（Algebra）**子集上，准确率从PAL基线的51.3%提升至59.8%，在**数论（Number Theory）**子集上提升幅度更达**11.2个百分点**，主要原因是数论题对整数溢出和模运算的精度要求高，精化阶段能有效修正初版代码的精度错误。

### 数据处理与格式转换

当Agent面对企业级数据处理任务时，工具创造能力尤其关键。例如，处理非标准日志格式（含自定义时间戳编码）时，Agent可生成专用的正则解析工具，并在工具库中持久化存储。在一次性生成工具后，同类日志文件的后续处理调用成本仅为Tool User的API费用，远低于每次让GPT-4重新解析。

### 多Agent系统中的工具共享

在多Agent协作架构（如AutoGen框架）中，工具创造能力可与工具库共享机制结合：Maker Agent生成的工具可通过共享工具库向同一任务中的其他User Agent开放。这相当于在运行时动态扩展多Agent系统的集体工具集，而无需工程师手动编写和注册新函数。

---

## 常见误区

**误区一：工具创造等同于普通代码生成**
工具创造与一次性代码生成（如PAL、PoT）的本质区别在于**抽象层次**：工具创造要求生成**参数化的通用函数**，而非针对单一输入硬编码的脚本。若Maker生成的函数将具体数值直接写入函数体（而非作为参数传入），则该"工具"无法被Tool User复用，失去工具化意义。判断标准：函数是否能对同类型的不同输入实例都返回正确结果。

**误区二：精化阶段可以无限循环直到成功**
精化循环必须设置最大迭代次数上限（CREATOR原论文设为5轮，LATM设为3轮）。若超过上限仍未成功，应回退到直接推理（chain-of-thought）而非让Agent陷入无限循环。无限精化不仅浪费计算资源，还可能导致代码在修复一个错误的同时引入新的逻辑错误（代码退化现象）。

**误区三：所有任务都适合工具创造**
LATM论文明确指出，工具创造对"**工具适配性（Tool Suitability）**高"的任务类别有效，即任务需要满足：(1) 存在明确的算法解法；(2) 同类任务会反复出现；(3) 工具的输入输出可以被清晰参数化。对于需要主观判断、开放式创作或依赖实时外部状态的任务，强行工具化反而会引入不必要的复杂度。

**误区四：工具库可以无限增长而不影响检索效率**
当工具库规模超过**数千条**时，余弦相似度检索的假阳性率（false positive）显著上升，可能导致Agent错误复用语义相近但功能不同的工具。需要定期对工具库进行聚类去重（如DBSCAN聚类，`eps`参数通常设为0.15~0.25的余弦距离），并为每类工具建立层级标签索引以提升精度。

---

## 知识关联

**前置概念——工具调用（Function Calling）**：工具创造的执行层依赖成熟的Function Calling机制。Maker生成的Python函数最终