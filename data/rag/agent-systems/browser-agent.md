---
id: "browser-agent"
concept: "浏览器Agent"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 7
is_milestone: false
tags: ["Agent", "Web"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 浏览器Agent

## 概述

浏览器Agent是一类能够自主操控Web浏览器完成复杂网络任务的AI系统，其核心能力在于将大语言模型的推理能力与浏览器的DOM操作、页面导航、表单填写等具体动作结合起来。与普通的网页爬虫不同，浏览器Agent能够处理需要多步骤决策的动态任务，例如"在机票预订网站上找到明天北京到上海最便宜的航班并截图"，这类任务要求Agent理解页面语义、处理弹出框、等待异步加载，而非仅仅抓取静态HTML。

浏览器Agent的技术实践在2023年至2024年间快速成熟。2023年3月，OpenAI发布了支持浏览器插件的ChatGPT，同年Anthropic发布了Computer Use功能，使Claude能够直接截图并操作屏幕上的UI元素。2024年初，微软Playwright团队和Google DeepMind分别发布了针对浏览器自动化的Agent框架，将LLM与浏览器控制接口深度整合。

浏览器Agent的价值在于它能突破API限制——大量网站不提供开放API，但其数据和功能可以通过人类正常使用的浏览器界面访问。企业可以用浏览器Agent完成竞品价格监控、自动化报销填写、批量数据采集等任务，而这些任务以往需要专门的RPA（机器人流程自动化）工具或大量人工处理。

## 核心原理

### 浏览器控制接口

浏览器Agent通常依赖两类底层接口操控浏览器。第一类是**CDP（Chrome DevTools Protocol）**，它允许程序级别地控制Chromium内核浏览器，执行JavaScript、监听网络请求、捕获截图等操作；Playwright和Puppeteer都基于CDP实现。第二类是**无障碍访问树（Accessibility Tree）**，浏览器将页面元素组织成一棵语义树，每个节点包含角色（role）、名称（name）、状态（state）等属性，例如 `button[name="提交"][disabled=false]`。相比将整个DOM HTML传给LLM，Accessibility Tree通常能将上下文长度压缩60%-80%，减少Token消耗并提高定位准确性。

### 观察-思考-行动循环（OAT Loop）

浏览器Agent的执行遵循「观察（Observe）→思考（Think）→行动（Act）」的循环结构，与通用ReAct框架在实现细节上有显著差异：
- **观察**：通过截图或Accessibility Tree获取当前页面状态，截图会编码为Base64传入多模态LLM
- **思考**：LLM分析当前状态与目标之间的差距，生成下一步行动计划（Chain-of-Thought）
- **行动**：输出结构化的动作指令，例如 `{"action": "click", "element_id": "btn_search"}` 或 `{"action": "type", "text": "2024-12-01", "element_id": "date_input"}`

每次动作执行后，Agent必须等待页面稳定（通常检测网络请求空闲或DOM变化停止超过500ms）再进行下一轮观察，否则会因为页面仍在加载而产生错误判断。

### 动作空间设计

浏览器Agent的动作空间通常包含约15-25种基本操作：`click`（点击）、`type`（输入文本）、`scroll`（滚动）、`navigate`（导航到URL）、`select`（下拉选择）、`hover`（悬停触发提示）、`wait`（显式等待）、`extract`（提取文本内容）等。WebArena基准测试（2023年发布，包含812个真实任务）中，GPT-4在原始设置下的成功率约为14.9%，而经过专门提示工程优化后可提升到35%-45%，这个数字直接反映了动作空间定义质量对Agent性能的影响。

动作空间设计的关键挑战是**元素定位**——同一个按钮在不同时刻可能有不同的XPath或CSS选择器（例如动态生成的ID如 `btn_12345`），因此健壮的浏览器Agent需要用语义描述（文本内容+上下文位置）而非脆弱的绝对路径来定位元素。

### 记忆与状态管理

跨页面任务要求Agent维护跨步骤的状态。浏览器Agent通常维护三类记忆：
1. **工作记忆**：当前LLM上下文窗口中的对话历史和截图，受Token限制约束
2. **外部存储**：将关键中间结果（如用户名、已找到的价格）存入文件或向量数据库
3. **浏览器状态**：Cookie、Session、localStorage等浏览器原生状态，Agent可以通过CDP直接读写

当任务超过20步时，保留完整的截图历史会消耗大量Token，实践中常用的策略是只保留最近3-5张截图加上文字摘要。

## 实际应用

**自动化表单填写与数据提交**：政府审批系统、报销系统往往只有Web界面，浏览器Agent可以接收结构化的报销数据（如JSON格式的发票信息），自动登录企业OA系统，逐字段填写表单并提交，处理可能出现的验证码（通过第三方OCR服务）或二次确认弹窗。

**竞品价格监控**：电商企业使用浏览器Agent定期访问竞争对手的商品详情页，提取价格、库存和促销信息。与传统爬虫不同，浏览器Agent能处理需要滑动验证、点击"查看更多"按钮或登录才能显示的价格，例如某些B2B平台的报价需要进入询价流程才能获取。

**Web端端到端测试生成**：开发团队用浏览器Agent执行自然语言描述的测试用例（如"以管理员身份登录，创建一个名为'测试项目'的新项目，邀请用户test@example.com"），Agent自动在测试环境执行并记录每步截图作为测试证据，同时生成可重放的Playwright脚本。

**信息聚合与研究辅助**：对于需要综合多个来源信息的研究任务，浏览器Agent可以按顺序访问多个专业数据库（如PubMed、专利数据库、行业报告网站），提取相关段落后汇总成结构化报告。

## 常见误区

**误区一：将浏览器Agent等同于传统爬虫**。传统爬虫通过HTTP请求直接获取HTML，无法执行JavaScript，无法处理需要用户交互才能显示的内容（如AJAX加载、React/Vue渲染的SPA应用）。浏览器Agent在真实浏览器环境中运行，能处理所有人类用户能看到的内容，但代价是速度更慢（每个动作需要等待浏览器渲染，通常比HTTP请求慢5-20倍）且资源消耗更大。选择浏览器Agent而非爬虫应基于目标网站是否有必须交互的动态内容，而非默认使用更复杂的方案。

**误区二：认为截图输入比Accessibility Tree更可靠**。截图看似直观，实际上包含大量与任务无关的视觉噪声（广告横幅、背景图片、颜色主题），且多模态LLM在精确定位坐标时误差较大——GPT-4V在WebArena上的点击坐标误差平均达到页面宽度的8%-15%，容易点错位置。Accessibility Tree虽然不能捕捉纯视觉信息（如图表内容），但在文本为主的操作任务中定位精度更高，Token效率更好。实践中最优方案通常是二者结合：优先使用Accessibility Tree定位元素，仅在遇到纯图片按钮等无文本元素时才依赖视觉坐标。

**误区三：忽视浏览器Agent的安全边界**。与只能读取数据的信息检索Agent不同，浏览器Agent具备写入能力——它能发送邮件、提交表单、进行支付操作。因此必须设计明确的权限边界：例如规定Agent在执行任何涉及金融交易或不可逆操作（如删除账户）的步骤前必须暂停并向人类确认（Human-in-the-Loop）。部分生产系统还会为Agent分配只读角色账号或沙箱账号，从账号权限层面限制其能执行的操作范围。

## 知识关联

浏览器Agent直接依赖**工具调用（Function Calling）**能力：浏览器的每个操作（click、type、navigate）本质上都是工具函数，LLM通过Function Calling格式输出结构化的动作参数，由Python/Node.js层调用Playwright/Selenium实际执行。如果LLM不能可靠地输出符合JSON Schema的工具调用，浏览器Agent将频繁因格式错误导致执行失败。

浏览器Agent还与**代码生成Agent**存在深度关联：当任务的操作步骤高度重复或结构清晰时（如抓取列表页的所有商品），让LLM直接生成完整的Playwright脚本往往比逐步交互式控制更高效——代码生成Agent负责一次性写出完整的浏览器自动化脚本，而浏览器Agent负责处理需要实时判断和条件分支的动态任务。两者的边界在于任务是否需要运行时的页面状态反馈来决策下一步行动：需要则用交互式浏览器Agent，不需要则可以用代码生成一次性解决。

在更大的Agent架构中