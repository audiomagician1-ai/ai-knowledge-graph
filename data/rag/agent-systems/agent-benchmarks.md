---
id: "agent-benchmarks"
concept: "Agent评测基准"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 6
is_milestone: false
tags: ["Agent", "评测"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Agent评测基准

## 概述

Agent评测基准是专门为测量AI Agent在复杂任务执行能力而设计的标准化测试集合，区别于传统NLP基准（如GLUE/SuperGLUE）只考察单轮问答能力，Agent基准要求被测系统完成多步骤、需使用工具或操作真实环境的序列决策任务。每个基准定义了任务集、执行环境、动作空间和评分标准四个核心要素，缺少任何一项都无法形成完整的Agent评测闭环。

主流Agent基准诞生于2023-2024年这一时间窗口，与大模型能力跃升同步出现。SWE-bench由普林斯顿大学团队于2023年10月发布，专注代码修复任务；WebArena于2023年7月发布，构建了可复现的Web操作环境；AgentBench由清华大学团队于2023年8月发布，提供跨8类任务的统一评测框架。三者的集中涌现反映了社区对"Agent能力标准化度量"需求的迫切性。

使用基准评测Agent的核心价值在于可重复性和横向比较能力。同一套SWE-bench测试实例，GPT-4早期版本解决率约为1.7%，而经过专项优化的Agent系统（如SWE-agent）可达到12.5%以上，这种量化差距为研究方向选择提供了客观依据。没有统一基准，不同论文声称的"性能提升"将无法互相验证。

## 核心原理

### SWE-bench：真实代码仓库修复测试

SWE-bench从GitHub上12个主流Python开源项目（包括Django、scikit-learn、sympy等）中抽取了2294个真实Issue-PR对作为测试实例。每个实例包含：一个描述Bug的Issue文本、对应代码仓库的特定提交版本快照、以及验证修复正确性的测试用例集。评测时Agent需要读取Issue描述、探索代码库、定位问题代码并生成有效补丁（patch文件），最终由原始PR中的测试用例自动判定是否通过（Pass@1指标）。

SWE-bench的难点在于它要求Agent具备"工程师级别"的上下文管理能力——典型仓库有数万行代码，Agent必须通过有策略的文件浏览和搜索来定位相关代码，而非蛮力读取全部内容。SWE-bench Verified是2024年推出的精选子集，包含500个人工验证过问题描述清晰的实例，专为减少测试噪声而设计。

### WebArena：真实Web环境操作评测

WebArena构建了包含电商（基于OpenCart）、社交论坛（基于Reddit）、代码托管（基于GitLab）、地图（基于OpenStreetMap）和内容管理（基于Confluence）在内的五类自托管Web环境，共812个测试任务。Agent通过浏览器操作接口（鼠标点击、键盘输入、页面滚动）完成任务，评测分为三类：字符串精确匹配、程序化验证（如检查数据库状态）和人工判断。

WebArena的关键设计是**功能等价性验证**：同一个"在电商网站搜索价格低于50美元的蓝色运动鞋"任务，接受多种合法完成路径，避免了路径依赖导致的误判。GPT-4+ReAct在WebArena上的基线成功率约为14.9%，当前最优系统已超过36%，但距离人类表现（约78%）仍有显著差距。

### AgentBench：八类任务统一框架

AgentBench将Agent能力分解为操作系统（OS）、数据库（DB）、知识图谱（KG）、数字卡牌游戏（Card）、横向思维谜题（Lateral）、房屋整理（ALFWorld）、Web购物（WebShop）和Web浏览（WebArena子集）八个维度，合计1091个测试实例。统一评测框架使用标准化的任务-环境交互协议，每类任务返回0到1之间的归一化得分，最终汇总为Overall Score。

AgentBench的核心贡献是揭示了**开源模型与商业模型的能力断层**：在2023年8月发布时，GPT-4的Overall Score约为4.21，Claude-2约为3.51，而当时最强的开源模型LLaMA-2-13B仅为0.38，差距超过10倍。这一数据直接推动了开源社区在Agent专项微调方向的投入。

## 实际应用

在实际项目中选择评测基准需匹配Agent的目标任务类型。若构建代码辅助Agent，优先使用SWE-bench评测，具体流程为：用`swebench.harness`工具拉取对应仓库镜像、运行Agent生成patch、通过Docker容器执行测试用例并收集Pass/Fail结果。代码类基准还需注意"测试集污染"问题——部分训练数据已包含SWE-bench实例的解答，需使用SWE-bench Verified并结合训练数据截止日期进行分析。

评测WebArena类Web操作Agent时，推荐在本地使用Docker Compose一键部署五类Web服务（官方提供`docker-compose.yml`），避免依赖公共服务器导致的环境不稳定。评测时应记录每个任务的轨迹（Action Trajectory），通过分析失败轨迹可定位Agent在"元素定位"还是"任务规划"环节的瓶颈，例如某Agent在GitLab任务上失败率高达70%，轨迹分析发现其无法正确解析动态加载的下拉菜单。

使用AgentBench做横向基准时，可将八个维度得分绘制雷达图，快速识别Agent的能力短板。若DB得分低于OS得分50%以上，通常指向Agent的结构化查询生成能力不足，而非通用规划能力问题，从而精准指导改进方向。

## 常见误区

**误区一：在私有任务上微调后声称超越SWE-bench基线**。SWE-bench的评测有效性依赖于测试实例与训练数据的严格隔离。部分团队使用包含相关GitHub PR的数据进行微调，导致模型"记住"了测试答案而非真正具备修复能力。正确做法是使用数据截止日期早于2023年5月（SWE-bench数据收集截止时间）的训练集，并在报告中明确说明训练数据来源。

**误区二：把WebArena成功率当作通用Web Agent能力的绝对度量**。WebArena的812个任务分布不均匀——WebShop子任务有400个而GitLab只有91个，若Agent针对性地优化购物任务，整体成功率可大幅提升，但在代码托管场景下的实际能力并未改善。正确做法是在报告中拆分各子类别成功率，而非只报告加权平均值。

**误区三：认为AgentBench的Overall Score可以直接比较不同版本基准的结果**。AgentBench在2024年进行了任务修订，部分任务难度系数调整导致新旧版本分数不可直接对比。在引用AgentBench数据时必须标注所用的具体版本号（v1.0或v2.0），否则会造成性能误判。

## 知识关联

学习Agent评测基准需要先掌握Agent评估与基准测试的基础概念，尤其是Pass@k指标的计算方式、以及任务成功率（Task Success Rate）与步骤效率（Step Efficiency）这两类评估维度的区别——SWE-bench主要使用前者，而AgentBench在部分任务中同时考量两者。

掌握三大基准后，下一步自然延伸到Agent Debugging and Observability：当Agent在SWE-bench上失败率达85%时，需要通过轨迹追踪工具（如LangSmith Trace或自定义日志）分析Agent在哪一步调用工具失败、哪类文件操作产生了无效输出。评测基准提供了"失败信号"，而可观测性工具提供了"失败原因"，二者共同构成Agent迭代优化的完整闭环。此外，SWE-bench的Docker化评测环境设计思路也直接影响了生产级Agent监控系统的沙箱隔离架构选择。