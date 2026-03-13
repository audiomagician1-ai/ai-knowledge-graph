"""
AI知识图谱 — LLM/Agent 前沿知识种子图谱生成器
生成 ~350 个概念节点 + 先修依赖 + 关联关系 + 里程碑节点
输出: JSON 文件 + Neo4j Cypher 导入脚本

知识体系设计 v2:
- 1 个领域 (AI Engineering / AI工程)
- 15 个子域 (CS基础→编程→数据结构→算法→OOP→Web前端→Web后端→数据库→DevOps→系统设计→AI基础→LLM核心→Prompt工程→RAG与知识库→Agent系统)
- ~350 个概念节点，难度 1-10
- 先修依赖关系 (PREREQUISITE)
- 关联关系 (RELATED_TO: analogy/application/contrast)
- 里程碑节点 (is_milestone: True) — 关键成就节点，高亮显示引导用户
"""

import json
import os
from datetime import datetime, timezone

# =============================================
# 知识体系定义
# =============================================

DOMAIN = {
    "id": "ai-engineering",
    "name": "AI工程",
    "description": "从编程基础到大模型与Agent系统的前沿知识体系",
    "icon": "🧠",
    "color": "#8b5cf6",
}

# 子域定义 — v2: 聚焦 LLM/Agent 前沿，保留编程基础作为先修
SUBDOMAINS = [
    {"id": "cs-fundamentals", "name": "计算机基础", "order": 1},
    {"id": "programming-basics", "name": "编程基础", "order": 2},
    {"id": "data-structures", "name": "数据结构", "order": 3},
    {"id": "algorithms", "name": "算法", "order": 4},
    {"id": "oop", "name": "面向对象编程", "order": 5},
    {"id": "web-frontend", "name": "Web前端", "order": 6},
    {"id": "web-backend", "name": "Web后端", "order": 7},
    {"id": "database", "name": "数据库", "order": 8},
    {"id": "devops", "name": "开发运维", "order": 9},
    {"id": "system-design", "name": "系统设计", "order": 10},
    {"id": "ai-foundations", "name": "AI基础", "order": 11},
    {"id": "llm-core", "name": "大模型核心", "order": 12},
    {"id": "prompt-engineering", "name": "Prompt工程", "order": 13},
    {"id": "rag-knowledge", "name": "RAG与知识库", "order": 14},
    {"id": "agent-systems", "name": "Agent系统", "order": 15},
]

# =============================================
# 概念节点定义 — (id, name, subdomain_id, difficulty, est_minutes, content_type, tags)
# =============================================

CONCEPTS_RAW = [
    # ---- 计算机基础 (difficulty 1-3) ----
    ("binary-system", "二进制与数制", "cs-fundamentals", 1, 20, "theory", ["基础", "数学"]),
    ("boolean-logic", "布尔逻辑", "cs-fundamentals", 1, 15, "theory", ["基础", "逻辑"]),
    ("how-computer-works", "计算机如何工作", "cs-fundamentals", 1, 25, "theory", ["基础", "硬件"]),
    ("memory-model", "内存模型", "cs-fundamentals", 2, 30, "theory", ["基础", "内存"]),
    ("cpu-execution", "CPU执行原理", "cs-fundamentals", 2, 25, "theory", ["基础", "硬件"]),
    ("os-basics", "操作系统基础", "cs-fundamentals", 3, 35, "theory", ["基础", "OS"]),
    ("file-system", "文件系统", "cs-fundamentals", 2, 20, "theory", ["基础", "OS"]),
    ("network-basics", "网络基础", "cs-fundamentals", 3, 30, "theory", ["基础", "网络"]),
    ("tcp-ip", "TCP/IP协议", "cs-fundamentals", 3, 35, "theory", ["网络", "协议"]),
    ("http-protocol", "HTTP协议", "cs-fundamentals", 3, 25, "theory", ["网络", "Web"]),
    ("character-encoding", "字符编码(ASCII/UTF-8)", "cs-fundamentals", 2, 20, "theory", ["基础", "编码"]),
    ("command-line", "命令行基础", "cs-fundamentals", 1, 20, "practice", ["工具", "终端"]),

    # ---- 编程基础 (difficulty 1-4) ----
    ("what-is-programming", "什么是编程", "programming-basics", 1, 15, "theory", ["入门"]),
    ("variables", "变量与数据类型", "programming-basics", 1, 20, "theory", ["基础"]),
    ("operators", "运算符", "programming-basics", 1, 15, "theory", ["基础"]),
    ("conditionals", "条件判断(if/else)", "programming-basics", 1, 20, "practice", ["控制流"]),
    ("loops", "循环(for/while)", "programming-basics", 2, 25, "practice", ["控制流"]),
    ("functions", "函数", "programming-basics", 2, 30, "practice", ["模块化"]),
    ("scope", "作用域", "programming-basics", 2, 20, "theory", ["基础"]),
    ("strings", "字符串操作", "programming-basics", 2, 25, "practice", ["数据类型"]),
    ("arrays-lists", "数组/列表", "programming-basics", 2, 25, "practice", ["数据类型"]),
    ("dictionaries-maps", "字典/映射", "programming-basics", 2, 25, "practice", ["数据类型"]),
    ("input-output", "输入与输出", "programming-basics", 1, 15, "practice", ["基础"]),
    ("error-handling", "错误处理(try/catch)", "programming-basics", 3, 25, "practice", ["鲁棒性"]),
    ("recursion", "递归", "programming-basics", 3, 35, "theory", ["算法思维"]),
    ("modules-imports", "模块与导入", "programming-basics", 2, 20, "practice", ["模块化"]),
    ("type-system", "类型系统(静态vs动态)", "programming-basics", 3, 25, "theory", ["语言设计"]),
    ("debugging-basics", "调试基础", "programming-basics", 2, 20, "practice", ["工具"]),
    ("code-style", "代码规范与风格", "programming-basics", 2, 15, "theory", ["工程"]),
    ("hello-world", "Hello World", "programming-basics", 1, 10, "practice", ["入门"]),
    ("comments", "注释", "programming-basics", 1, 10, "theory", ["基础"]),
    ("iteration-vs-recursion", "迭代vs递归", "programming-basics", 3, 30, "theory", ["算法思维"]),

    # ---- 数据结构 (difficulty 3-7) ----
    ("array-internals", "数组内部原理", "data-structures", 3, 25, "theory", ["线性"]),
    ("linked-list", "链表", "data-structures", 4, 35, "theory", ["线性"]),
    ("stack", "栈", "data-structures", 3, 25, "theory", ["线性", "LIFO"]),
    ("queue", "队列", "data-structures", 3, 25, "theory", ["线性", "FIFO"]),
    ("deque", "双端队列", "data-structures", 4, 20, "theory", ["线性"]),
    ("hash-table", "哈希表", "data-structures", 4, 40, "theory", ["映射"]),
    ("set-data-structure", "集合", "data-structures", 3, 20, "theory", ["集合论"]),
    ("binary-tree", "二叉树", "data-structures", 5, 40, "theory", ["树"]),
    ("bst", "二叉搜索树(BST)", "data-structures", 5, 40, "theory", ["树", "搜索"]),
    ("avl-tree", "AVL树", "data-structures", 6, 45, "theory", ["树", "平衡"]),
    ("red-black-tree", "红黑树", "data-structures", 7, 50, "theory", ["树", "平衡"]),
    ("heap", "堆(优先队列)", "data-structures", 5, 35, "theory", ["树", "排序"]),
    ("trie", "字典树(Trie)", "data-structures", 6, 35, "theory", ["树", "字符串"]),
    ("graph-ds", "图(数据结构)", "data-structures", 5, 40, "theory", ["图"]),
    ("adjacency-matrix", "邻接矩阵", "data-structures", 5, 20, "theory", ["图"]),
    ("adjacency-list", "邻接表", "data-structures", 5, 20, "theory", ["图"]),
    ("disjoint-set", "并查集", "data-structures", 6, 35, "theory", ["图", "集合"]),
    ("bloom-filter", "布隆过滤器", "data-structures", 7, 30, "theory", ["概率"]),
    ("skip-list", "跳表", "data-structures", 7, 35, "theory", ["概率", "线性"]),

    # ---- 算法 (difficulty 3-9) ----
    ("time-complexity", "时间复杂度(Big-O)", "algorithms", 3, 30, "theory", ["分析"]),
    ("space-complexity", "空间复杂度", "algorithms", 3, 25, "theory", ["分析"]),
    ("bubble-sort", "冒泡排序", "algorithms", 3, 20, "practice", ["排序"]),
    ("selection-sort", "选择排序", "algorithms", 3, 20, "practice", ["排序"]),
    ("insertion-sort", "插入排序", "algorithms", 3, 20, "practice", ["排序"]),
    ("merge-sort", "归并排序", "algorithms", 5, 35, "practice", ["排序", "分治"]),
    ("quick-sort", "快速排序", "algorithms", 5, 35, "practice", ["排序", "分治"]),
    ("heap-sort", "堆排序", "algorithms", 5, 30, "practice", ["排序"]),
    ("counting-sort", "计数排序", "algorithms", 4, 20, "practice", ["排序"]),
    ("binary-search", "二分查找", "algorithms", 3, 25, "practice", ["搜索"]),
    ("bfs", "广度优先搜索(BFS)", "algorithms", 4, 30, "practice", ["图", "搜索"]),
    ("dfs", "深度优先搜索(DFS)", "algorithms", 4, 30, "practice", ["图", "搜索"]),
    ("dijkstra", "Dijkstra最短路径", "algorithms", 6, 40, "practice", ["图", "最短路"]),
    ("bellman-ford", "Bellman-Ford算法", "algorithms", 6, 35, "theory", ["图", "最短路"]),
    ("topological-sort", "拓扑排序", "algorithms", 5, 30, "practice", ["图", "DAG"]),
    ("kruskal-mst", "Kruskal最小生成树", "algorithms", 6, 35, "theory", ["图"]),
    ("two-pointers", "双指针", "algorithms", 4, 25, "practice", ["技巧"]),
    ("sliding-window", "滑动窗口", "algorithms", 4, 30, "practice", ["技巧"]),
    ("divide-conquer", "分治法", "algorithms", 5, 35, "theory", ["范式"]),
    ("greedy", "贪心算法", "algorithms", 5, 30, "theory", ["范式"]),
    ("dynamic-programming", "动态规划", "algorithms", 7, 60, "theory", ["范式"]),
    ("dp-memoization", "记忆化搜索", "algorithms", 6, 35, "practice", ["DP"]),
    ("dp-tabulation", "DP表格法", "algorithms", 7, 40, "practice", ["DP"]),
    ("backtracking", "回溯法", "algorithms", 6, 40, "practice", ["范式"]),
    ("bit-manipulation", "位运算技巧", "algorithms", 5, 30, "practice", ["技巧"]),
    ("string-matching", "字符串匹配(KMP)", "algorithms", 7, 45, "theory", ["字符串"]),
    ("graph-coloring", "图着色", "algorithms", 7, 35, "theory", ["图"]),
    ("np-completeness", "NP完全性", "algorithms", 9, 50, "theory", ["理论"]),

    # ---- 面向对象编程 (difficulty 3-7) ----
    ("class-object", "类与对象", "oop", 3, 30, "theory", ["OOP"]),
    ("encapsulation", "封装", "oop", 3, 25, "theory", ["OOP"]),
    ("inheritance", "继承", "oop", 4, 30, "theory", ["OOP"]),
    ("polymorphism", "多态", "oop", 4, 35, "theory", ["OOP"]),
    ("abstraction", "抽象", "oop", 4, 25, "theory", ["OOP"]),
    ("interface", "接口", "oop", 4, 25, "theory", ["OOP"]),
    ("composition-vs-inheritance", "组合优于继承", "oop", 5, 30, "theory", ["设计"]),
    ("design-patterns-intro", "设计模式概述", "oop", 5, 20, "theory", ["设计"]),
    ("singleton", "单例模式", "oop", 5, 20, "practice", ["设计模式"]),
    ("factory-pattern", "工厂模式", "oop", 5, 25, "practice", ["设计模式"]),
    ("observer-pattern", "观察者模式", "oop", 5, 25, "practice", ["设计模式"]),
    ("strategy-pattern", "策略模式", "oop", 5, 25, "practice", ["设计模式"]),
    ("decorator-pattern", "装饰器模式", "oop", 6, 30, "practice", ["设计模式"]),
    ("mvc-pattern", "MVC模式", "oop", 5, 25, "theory", ["架构"]),
    ("solid-principles", "SOLID原则", "oop", 6, 40, "theory", ["设计"]),
    ("dependency-injection", "依赖注入", "oop", 6, 30, "theory", ["设计"]),
    ("generics", "泛型", "oop", 5, 30, "theory", ["类型系统"]),
    ("enum", "枚举类型", "oop", 3, 15, "theory", ["数据类型"]),

    # ---- Web前端 (difficulty 3-7) ----
    ("html-basics", "HTML基础", "web-frontend", 2, 25, "practice", ["Web"]),
    ("css-basics", "CSS基础", "web-frontend", 2, 30, "practice", ["Web", "样式"]),
    ("css-layout", "CSS布局(Flex/Grid)", "web-frontend", 3, 35, "practice", ["布局"]),
    ("css-responsive", "响应式设计", "web-frontend", 4, 30, "practice", ["移动端"]),
    ("javascript-basics", "JavaScript基础", "web-frontend", 3, 40, "practice", ["JS"]),
    ("dom-manipulation", "DOM操作", "web-frontend", 3, 30, "practice", ["JS", "浏览器"]),
    ("event-handling", "事件处理", "web-frontend", 3, 25, "practice", ["JS"]),
    ("async-js", "异步JavaScript(Promise/async)", "web-frontend", 5, 45, "theory", ["JS", "异步"]),
    ("fetch-api", "Fetch API与网络请求", "web-frontend", 4, 25, "practice", ["JS", "网络"]),
    ("react-basics", "React基础", "web-frontend", 4, 40, "practice", ["React"]),
    ("react-hooks", "React Hooks", "web-frontend", 5, 40, "practice", ["React"]),
    ("react-state", "React状态管理", "web-frontend", 5, 35, "theory", ["React"]),
    ("component-lifecycle", "组件生命周期", "web-frontend", 4, 25, "theory", ["React"]),
    ("virtual-dom", "虚拟DOM原理", "web-frontend", 5, 30, "theory", ["React", "性能"]),
    ("spa-routing", "SPA路由", "web-frontend", 4, 25, "practice", ["Web"]),
    ("typescript-basics", "TypeScript基础", "web-frontend", 4, 35, "practice", ["TS"]),
    ("ts-advanced-types", "TypeScript高级类型", "web-frontend", 6, 40, "theory", ["TS"]),
    ("css-in-js", "CSS-in-JS / TailwindCSS", "web-frontend", 4, 25, "practice", ["样式"]),
    ("web-accessibility", "Web无障碍(a11y)", "web-frontend", 4, 25, "theory", ["质量"]),
    ("web-performance", "前端性能优化", "web-frontend", 6, 40, "theory", ["性能"]),
    ("bundler-basics", "打包工具(Webpack/Vite)", "web-frontend", 5, 30, "theory", ["工具链"]),
    ("browser-rendering", "浏览器渲染原理", "web-frontend", 6, 35, "theory", ["浏览器"]),
    ("pwa-basics", "PWA基础", "web-frontend", 5, 30, "theory", ["移动端"]),

    # ---- Web后端 (difficulty 4-8) ----
    ("server-basics", "服务器基础概念", "web-backend", 3, 25, "theory", ["后端"]),
    ("restful-api", "RESTful API设计", "web-backend", 4, 35, "theory", ["API"]),
    ("api-authentication", "API认证(JWT/OAuth)", "web-backend", 5, 40, "theory", ["安全"]),
    ("middleware", "中间件", "web-backend", 4, 25, "theory", ["架构"]),
    ("session-cookie", "Session与Cookie", "web-backend", 4, 25, "theory", ["状态"]),
    ("websocket", "WebSocket实时通信", "web-backend", 5, 30, "theory", ["网络"]),
    ("graphql-basics", "GraphQL基础", "web-backend", 5, 35, "theory", ["API"]),
    ("server-side-rendering", "服务端渲染(SSR)", "web-backend", 6, 35, "theory", ["架构"]),
    ("cors", "CORS跨域", "web-backend", 4, 20, "theory", ["安全"]),
    ("rate-limiting", "限流策略", "web-backend", 5, 25, "theory", ["安全"]),
    ("file-upload", "文件上传处理", "web-backend", 4, 25, "practice", ["API"]),
    ("logging-monitoring", "日志与监控", "web-backend", 5, 30, "theory", ["运维"]),
    ("error-handling-backend", "后端错误处理", "web-backend", 4, 25, "practice", ["鲁棒性"]),
    ("caching-strategies", "缓存策略", "web-backend", 6, 35, "theory", ["性能"]),
    ("message-queue", "消息队列", "web-backend", 6, 35, "theory", ["架构"]),
    ("microservices-intro", "微服务入门", "web-backend", 7, 40, "theory", ["架构"]),
    ("serverless", "Serverless架构", "web-backend", 6, 30, "theory", ["架构"]),

    # ---- 数据库 (difficulty 3-8) ----
    ("db-basics", "数据库基本概念", "database", 3, 25, "theory", ["数据库"]),
    ("sql-basics", "SQL基础(CRUD)", "database", 3, 30, "practice", ["SQL"]),
    ("sql-joins", "SQL JOIN查询", "database", 4, 35, "practice", ["SQL"]),
    ("sql-aggregation", "SQL聚合与分组", "database", 4, 25, "practice", ["SQL"]),
    ("sql-subquery", "SQL子查询", "database", 5, 30, "practice", ["SQL"]),
    ("db-normalization", "数据库范式", "database", 5, 35, "theory", ["设计"]),
    ("db-indexing", "索引原理与优化", "database", 6, 40, "theory", ["性能"]),
    ("db-transactions", "事务(ACID)", "database", 5, 30, "theory", ["一致性"]),
    ("orm-basics", "ORM基础", "database", 4, 25, "practice", ["工具"]),
    ("nosql-intro", "NoSQL概述", "database", 5, 30, "theory", ["数据库"]),
    ("mongodb-basics", "MongoDB基础", "database", 4, 30, "practice", ["NoSQL"]),
    ("redis-basics", "Redis基础", "database", 4, 25, "practice", ["缓存"]),
    ("graph-database", "图数据库(Neo4j)", "database", 6, 35, "theory", ["图"]),
    ("db-replication", "数据库复制", "database", 7, 35, "theory", ["分布式"]),
    ("db-sharding", "分库分表", "database", 8, 40, "theory", ["分布式"]),
    ("db-migration", "数据库迁移", "database", 4, 20, "practice", ["运维"]),

    # ---- 开发运维 (difficulty 3-7) ----
    ("git-basics", "Git基础", "devops", 2, 25, "practice", ["版本控制"]),
    ("git-branching", "Git分支策略", "devops", 3, 25, "practice", ["版本控制"]),
    ("git-workflow", "Git工作流(GitFlow)", "devops", 4, 30, "theory", ["协作"]),
    ("ci-cd", "CI/CD持续集成", "devops", 5, 35, "theory", ["自动化"]),
    ("docker-basics", "Docker基础", "devops", 4, 35, "practice", ["容器"]),
    ("docker-compose-concept", "Docker Compose", "devops", 5, 25, "practice", ["容器"]),
    ("kubernetes-intro", "Kubernetes入门", "devops", 7, 45, "theory", ["编排"]),
    ("linux-basics", "Linux基础命令", "devops", 2, 25, "practice", ["运维"]),
    ("shell-scripting", "Shell脚本", "devops", 4, 30, "practice", ["自动化"]),
    ("cloud-basics", "云服务基础(AWS/GCP)", "devops", 4, 30, "theory", ["云"]),
    ("monitoring-alerting", "监控与告警", "devops", 5, 30, "theory", ["运维"]),
    ("infra-as-code", "基础设施即代码", "devops", 6, 35, "theory", ["自动化"]),
    ("ssl-tls", "SSL/TLS与HTTPS", "devops", 4, 25, "theory", ["安全"]),
    ("environment-variables", "环境变量管理", "devops", 3, 15, "practice", ["配置"]),

    # ---- 系统设计 (difficulty 6-10) ----
    ("system-design-basics", "系统设计入门", "system-design", 6, 40, "theory", ["设计"]),
    ("scalability", "可扩展性", "system-design", 7, 40, "theory", ["架构"]),
    ("load-balancing", "负载均衡", "system-design", 6, 30, "theory", ["架构"]),
    ("cap-theorem", "CAP定理", "system-design", 7, 35, "theory", ["分布式"]),
    ("consistency-patterns", "一致性模型", "system-design", 8, 40, "theory", ["分布式"]),
    ("event-driven-arch", "事件驱动架构", "system-design", 7, 35, "theory", ["架构"]),
    ("api-gateway", "API网关", "system-design", 6, 25, "theory", ["架构"]),
    ("service-discovery", "服务发现", "system-design", 7, 30, "theory", ["微服务"]),
    ("circuit-breaker", "熔断器模式", "system-design", 7, 25, "theory", ["容错"]),
    ("distributed-cache", "分布式缓存", "system-design", 7, 35, "theory", ["性能"]),
    ("cdn", "CDN内容分发", "system-design", 5, 20, "theory", ["性能"]),
    ("design-url-shortener", "设计短链接系统", "system-design", 7, 45, "project", ["实战"]),
    ("design-chat-system", "设计聊天系统", "system-design", 8, 50, "project", ["实战"]),
    ("design-rate-limiter", "设计限流器", "system-design", 7, 40, "project", ["实战"]),
    ("twelve-factor-app", "12-Factor App", "system-design", 6, 30, "theory", ["方法论"]),

    # ---- AI基础 (difficulty 4-7) ----
    ("ai-overview", "人工智能概述", "ai-foundations", 4, 25, "theory", ["AI"]),
    ("ml-basics", "机器学习基础", "ai-foundations", 5, 35, "theory", ["ML"]),
    ("supervised-learning", "监督学习", "ai-foundations", 5, 30, "theory", ["ML"]),
    ("unsupervised-learning", "无监督学习", "ai-foundations", 6, 30, "theory", ["ML"]),
    ("linear-regression", "线性回归", "ai-foundations", 5, 35, "practice", ["ML"]),
    ("logistic-regression", "逻辑回归", "ai-foundations", 5, 30, "practice", ["ML"]),
    ("decision-tree", "决策树", "ai-foundations", 5, 30, "theory", ["ML"]),
    ("neural-network-basics", "神经网络基础", "ai-foundations", 6, 40, "theory", ["DL"]),
    ("deep-learning-intro", "深度学习入门", "ai-foundations", 7, 45, "theory", ["DL"]),
    ("cnn-basics", "卷积神经网络(CNN)", "ai-foundations", 7, 40, "theory", ["DL", "视觉"]),
    ("rnn-basics", "循环神经网络(RNN)", "ai-foundations", 7, 40, "theory", ["DL", "序列"]),
    ("ml-evaluation", "模型评估指标", "ai-foundations", 5, 25, "theory", ["ML"]),
    ("overfitting", "过拟合与正则化", "ai-foundations", 6, 30, "theory", ["ML"]),
    ("feature-engineering", "特征工程", "ai-foundations", 6, 30, "practice", ["ML"]),
    ("gradient-descent", "梯度下降与优化", "ai-foundations", 6, 35, "theory", ["DL"]),
    ("loss-functions", "损失函数", "ai-foundations", 5, 25, "theory", ["DL"]),
    ("backpropagation", "反向传播", "ai-foundations", 7, 40, "theory", ["DL"]),
    ("pytorch-basics", "PyTorch基础", "ai-foundations", 5, 40, "practice", ["工具"]),

    # ---- 大模型核心 (difficulty 5-9) ⭐ 新增重点子域 ----
    ("attention-mechanism", "注意力机制", "llm-core", 7, 45, "theory", ["DL", "NLP"]),
    ("transformer-architecture", "Transformer架构", "llm-core", 8, 50, "theory", ["DL", "NLP"]),
    ("self-attention", "自注意力与多头注意力", "llm-core", 8, 40, "theory", ["Transformer"]),
    ("positional-encoding", "位置编码", "llm-core", 7, 30, "theory", ["Transformer"]),
    ("bert-model", "BERT与编码器模型", "llm-core", 7, 35, "theory", ["NLP"]),
    ("gpt-model", "GPT与解码器模型", "llm-core", 8, 40, "theory", ["LLM"]),
    ("llm-pretraining", "LLM预训练", "llm-core", 8, 45, "theory", ["LLM"]),
    ("tokenization", "分词与Tokenization", "llm-core", 5, 25, "theory", ["NLP"]),
    ("llm-scaling-laws", "LLM缩放定律", "llm-core", 8, 35, "theory", ["LLM"]),
    ("llm-inference", "LLM推理优化", "llm-core", 7, 40, "theory", ["LLM", "性能"]),
    ("quantization", "模型量化(GPTQ/AWQ)", "llm-core", 7, 35, "theory", ["LLM", "部署"]),
    ("fine-tuning-overview", "微调概述(SFT/RLHF)", "llm-core", 7, 40, "theory", ["LLM"]),
    ("lora-peft", "LoRA与参数高效微调", "llm-core", 7, 35, "practice", ["LLM", "微调"]),
    ("rlhf", "RLHF人类反馈强化学习", "llm-core", 9, 50, "theory", ["LLM", "对齐"]),
    ("dpo", "DPO直接偏好优化", "llm-core", 8, 40, "theory", ["LLM", "对齐"]),
    ("multimodal-models", "多模态大模型", "llm-core", 8, 45, "theory", ["LLM", "视觉"]),
    ("llm-evaluation", "LLM评估方法", "llm-core", 6, 30, "theory", ["LLM"]),
    ("open-source-llm", "开源LLM生态(Llama/Qwen/DeepSeek)", "llm-core", 6, 30, "theory", ["LLM"]),
    ("context-window", "上下文窗口与长文本", "llm-core", 7, 35, "theory", ["LLM"]),
    ("mixture-of-experts", "MoE混合专家模型", "llm-core", 8, 40, "theory", ["LLM", "架构"]),

    # ---- Prompt工程 (difficulty 3-8) ⭐ 新增重点子域 ----
    ("prompt-basics", "提示词基础", "prompt-engineering", 3, 20, "practice", ["Prompt"]),
    ("zero-shot", "零样本提示", "prompt-engineering", 3, 15, "practice", ["Prompt"]),
    ("few-shot", "少样本提示", "prompt-engineering", 4, 20, "practice", ["Prompt"]),
    ("chain-of-thought", "思维链(CoT)", "prompt-engineering", 5, 30, "theory", ["Prompt"]),
    ("self-consistency", "自一致性采样", "prompt-engineering", 6, 25, "theory", ["Prompt"]),
    ("tree-of-thought", "思维树(ToT)", "prompt-engineering", 7, 35, "theory", ["Prompt"]),
    ("react-prompting", "ReAct推理+行动", "prompt-engineering", 6, 30, "theory", ["Prompt", "Agent"]),
    ("structured-output", "结构化输出(JSON Mode)", "prompt-engineering", 4, 20, "practice", ["Prompt", "API"]),
    ("system-prompt-design", "System Prompt设计", "prompt-engineering", 5, 30, "practice", ["Prompt"]),
    ("prompt-injection", "提示注入攻防", "prompt-engineering", 6, 30, "theory", ["安全"]),
    ("prompt-optimization", "提示词自动优化(DSPy)", "prompt-engineering", 7, 35, "theory", ["Prompt"]),
    ("llm-api-usage", "LLM API调用(OpenAI/Claude)", "prompt-engineering", 4, 25, "practice", ["API"]),
    ("temperature-sampling", "Temperature与采样策略", "prompt-engineering", 5, 20, "theory", ["LLM"]),
    ("token-economics", "Token经济与成本优化", "prompt-engineering", 4, 20, "theory", ["实践"]),

    # ---- RAG与知识库 (difficulty 5-9) ⭐ 新增重点子域 ----
    ("rag-overview", "RAG检索增强生成概述", "rag-knowledge", 5, 30, "theory", ["RAG"]),
    ("text-embedding", "文本嵌入(Embedding)", "rag-knowledge", 6, 35, "theory", ["NLP", "RAG"]),
    ("vector-database", "向量数据库(Pinecone/Milvus)", "rag-knowledge", 6, 35, "theory", ["数据库", "RAG"]),
    ("chunking-strategies", "文档分块策略", "rag-knowledge", 5, 25, "practice", ["RAG"]),
    ("similarity-search", "相似度搜索与重排", "rag-knowledge", 6, 30, "theory", ["RAG"]),
    ("hybrid-search", "混合检索(向量+关键词)", "rag-knowledge", 6, 30, "theory", ["RAG"]),
    ("rag-pipeline", "RAG管道架构", "rag-knowledge", 7, 40, "theory", ["RAG", "架构"]),
    ("rag-evaluation", "RAG评估(Ragas)", "rag-knowledge", 7, 35, "theory", ["RAG"]),
    ("knowledge-graph-rag", "知识图谱+RAG", "rag-knowledge", 8, 45, "theory", ["RAG", "图"]),
    ("multimodal-rag", "多模态RAG", "rag-knowledge", 8, 40, "theory", ["RAG", "多模态"]),
    ("document-parsing", "文档解析(PDF/HTML/OCR)", "rag-knowledge", 5, 30, "practice", ["RAG"]),
    ("langchain-basics", "LangChain基础", "rag-knowledge", 5, 30, "practice", ["工具"]),
    ("llamaindex-basics", "LlamaIndex基础", "rag-knowledge", 5, 30, "practice", ["工具"]),
    ("graph-database-ai", "图数据库在AI中的应用", "rag-knowledge", 7, 35, "theory", ["图", "RAG"]),
    ("agentic-rag", "Agentic RAG", "rag-knowledge", 8, 40, "theory", ["RAG", "Agent"]),

    # ---- Agent系统 (difficulty 5-10) ⭐ 新增重点子域 ----
    ("agent-overview", "AI Agent概述", "agent-systems", 5, 25, "theory", ["Agent"]),
    ("agent-loop", "Agent循环(感知-推理-行动)", "agent-systems", 6, 30, "theory", ["Agent"]),
    ("tool-use", "工具调用(Function Calling)", "agent-systems", 6, 35, "practice", ["Agent", "API"]),
    ("mcp-protocol", "MCP模型上下文协议", "agent-systems", 7, 40, "theory", ["Agent", "协议"]),
    ("agent-memory", "Agent记忆系统", "agent-systems", 7, 35, "theory", ["Agent"]),
    ("agent-planning", "Agent规划与分解", "agent-systems", 7, 40, "theory", ["Agent"]),
    ("multi-agent", "多Agent协作系统", "agent-systems", 8, 45, "theory", ["Agent"]),
    ("agent-evaluation", "Agent评估与基准测试", "agent-systems", 7, 35, "theory", ["Agent"]),
    ("autogen-framework", "AutoGen框架", "agent-systems", 6, 35, "practice", ["Agent", "工具"]),
    ("crewai-framework", "CrewAI框架", "agent-systems", 6, 35, "practice", ["Agent", "工具"]),
    ("agent-safety", "Agent安全与对齐", "agent-systems", 8, 40, "theory", ["Agent", "安全"]),
    ("code-generation", "代码生成Agent", "agent-systems", 7, 35, "practice", ["Agent", "编程"]),
    ("browser-agent", "浏览器Agent", "agent-systems", 7, 35, "practice", ["Agent", "Web"]),
    ("agent-orchestration", "Agent编排与工作流", "agent-systems", 8, 40, "theory", ["Agent", "架构"]),
    ("human-in-the-loop", "人在回路(HITL)", "agent-systems", 6, 25, "theory", ["Agent", "安全"]),
    ("agent-deployment", "Agent部署与监控", "agent-systems", 7, 35, "practice", ["Agent", "DevOps"]),
    ("ai-application-arch", "AI应用架构设计", "agent-systems", 8, 45, "theory", ["Agent", "架构"]),
    ("autonomous-agents", "自主Agent前沿", "agent-systems", 9, 50, "theory", ["Agent", "前沿"]),
]

# =============================================
# 先修依赖关系 (source_id -> target_id, strength)
# 读法: target 需要先学会 source
# =============================================

PREREQUISITES = [
    # 计算机基础 内部
    ("binary-system", "boolean-logic", 0.7),
    ("how-computer-works", "memory-model", 0.8),
    ("how-computer-works", "cpu-execution", 0.8),
    ("memory-model", "os-basics", 0.6),
    ("os-basics", "file-system", 0.5),
    ("network-basics", "tcp-ip", 0.9),
    ("tcp-ip", "http-protocol", 0.8),

    # 编程基础 链
    ("what-is-programming", "hello-world", 0.9),
    ("hello-world", "variables", 0.9),
    ("hello-world", "comments", 0.5),
    ("variables", "operators", 0.9),
    ("variables", "input-output", 0.7),
    ("operators", "conditionals", 0.9),
    ("conditionals", "loops", 0.9),
    ("loops", "functions", 0.8),
    ("functions", "scope", 0.8),
    ("variables", "strings", 0.7),
    ("variables", "arrays-lists", 0.7),
    ("arrays-lists", "dictionaries-maps", 0.7),
    ("functions", "error-handling", 0.6),
    ("functions", "recursion", 0.7),
    ("loops", "recursion", 0.6),
    ("recursion", "iteration-vs-recursion", 0.8),
    ("functions", "modules-imports", 0.6),
    ("variables", "type-system", 0.5),
    ("functions", "debugging-basics", 0.5),
    ("code-style", "debugging-basics", 0.3),

    # 编程基础 → 数据结构
    ("arrays-lists", "array-internals", 0.8),
    ("arrays-lists", "linked-list", 0.7),
    ("arrays-lists", "stack", 0.6),
    ("arrays-lists", "queue", 0.6),
    ("dictionaries-maps", "hash-table", 0.7),
    ("dictionaries-maps", "set-data-structure", 0.5),
    ("recursion", "binary-tree", 0.7),
    ("binary-tree", "bst", 0.9),
    ("bst", "avl-tree", 0.8),
    ("avl-tree", "red-black-tree", 0.7),
    ("binary-tree", "heap", 0.7),
    ("binary-tree", "trie", 0.6),
    ("arrays-lists", "graph-ds", 0.5),
    ("linked-list", "graph-ds", 0.5),
    ("graph-ds", "adjacency-matrix", 0.8),
    ("graph-ds", "adjacency-list", 0.8),
    ("graph-ds", "disjoint-set", 0.6),
    ("hash-table", "bloom-filter", 0.5),
    ("linked-list", "skip-list", 0.6),
    ("queue", "deque", 0.7),

    # 数据结构 → 算法
    ("arrays-lists", "time-complexity", 0.5),
    ("loops", "time-complexity", 0.6),
    ("time-complexity", "space-complexity", 0.8),
    ("arrays-lists", "bubble-sort", 0.6),
    ("arrays-lists", "selection-sort", 0.6),
    ("arrays-lists", "insertion-sort", 0.6),
    ("recursion", "merge-sort", 0.7),
    ("recursion", "quick-sort", 0.7),
    ("divide-conquer", "merge-sort", 0.8),
    ("divide-conquer", "quick-sort", 0.8),
    ("heap", "heap-sort", 0.8),
    ("arrays-lists", "counting-sort", 0.5),
    ("arrays-lists", "binary-search", 0.6),
    ("graph-ds", "bfs", 0.8),
    ("graph-ds", "dfs", 0.8),
    ("queue", "bfs", 0.6),
    ("stack", "dfs", 0.5),
    ("bfs", "dijkstra", 0.7),
    ("dijkstra", "bellman-ford", 0.6),
    ("dfs", "topological-sort", 0.7),
    ("disjoint-set", "kruskal-mst", 0.7),
    ("arrays-lists", "two-pointers", 0.5),
    ("two-pointers", "sliding-window", 0.7),
    ("recursion", "divide-conquer", 0.7),
    ("time-complexity", "greedy", 0.5),
    ("recursion", "dynamic-programming", 0.7),
    ("recursion", "dp-memoization", 0.8),
    ("dynamic-programming", "dp-memoization", 0.9),
    ("dynamic-programming", "dp-tabulation", 0.9),
    ("recursion", "backtracking", 0.7),
    ("dfs", "backtracking", 0.6),
    ("binary-system", "bit-manipulation", 0.7),
    ("strings", "string-matching", 0.6),
    ("graph-ds", "graph-coloring", 0.6),
    ("time-complexity", "np-completeness", 0.6),

    # OOP
    ("functions", "class-object", 0.6),
    ("variables", "class-object", 0.5),
    ("class-object", "encapsulation", 0.8),
    ("class-object", "inheritance", 0.8),
    ("inheritance", "polymorphism", 0.8),
    ("class-object", "abstraction", 0.7),
    ("abstraction", "interface", 0.8),
    ("inheritance", "composition-vs-inheritance", 0.7),
    ("class-object", "design-patterns-intro", 0.5),
    ("design-patterns-intro", "singleton", 0.7),
    ("design-patterns-intro", "factory-pattern", 0.7),
    ("design-patterns-intro", "observer-pattern", 0.7),
    ("design-patterns-intro", "strategy-pattern", 0.7),
    ("design-patterns-intro", "decorator-pattern", 0.6),
    ("design-patterns-intro", "mvc-pattern", 0.6),
    ("interface", "solid-principles", 0.6),
    ("solid-principles", "dependency-injection", 0.7),
    ("type-system", "generics", 0.6),
    ("class-object", "enum", 0.4),

    # Web前端
    ("html-basics", "css-basics", 0.7),
    ("css-basics", "css-layout", 0.8),
    ("css-layout", "css-responsive", 0.7),
    ("html-basics", "javascript-basics", 0.5),
    ("variables", "javascript-basics", 0.6),
    ("javascript-basics", "dom-manipulation", 0.8),
    ("dom-manipulation", "event-handling", 0.8),
    ("functions", "async-js", 0.6),
    ("event-handling", "async-js", 0.5),
    ("async-js", "fetch-api", 0.8),
    ("http-protocol", "fetch-api", 0.5),
    ("javascript-basics", "react-basics", 0.7),
    ("dom-manipulation", "react-basics", 0.5),
    ("react-basics", "react-hooks", 0.9),
    ("react-hooks", "react-state", 0.8),
    ("react-basics", "component-lifecycle", 0.7),
    ("react-basics", "virtual-dom", 0.6),
    ("react-basics", "spa-routing", 0.6),
    ("type-system", "typescript-basics", 0.5),
    ("javascript-basics", "typescript-basics", 0.7),
    ("typescript-basics", "ts-advanced-types", 0.8),
    ("css-basics", "css-in-js", 0.6),
    ("html-basics", "web-accessibility", 0.5),
    ("virtual-dom", "web-performance", 0.5),
    ("browser-rendering", "web-performance", 0.7),
    ("modules-imports", "bundler-basics", 0.5),
    ("dom-manipulation", "browser-rendering", 0.5),
    ("css-responsive", "pwa-basics", 0.4),

    # Web后端
    ("http-protocol", "server-basics", 0.7),
    ("functions", "server-basics", 0.4),
    ("server-basics", "restful-api", 0.8),
    ("restful-api", "api-authentication", 0.7),
    ("server-basics", "middleware", 0.7),
    ("http-protocol", "session-cookie", 0.6),
    ("http-protocol", "cors", 0.5),
    ("restful-api", "graphql-basics", 0.5),
    ("server-basics", "server-side-rendering", 0.5),
    ("virtual-dom", "server-side-rendering", 0.5),
    ("api-authentication", "rate-limiting", 0.5),
    ("restful-api", "file-upload", 0.6),
    ("server-basics", "logging-monitoring", 0.5),
    ("error-handling", "error-handling-backend", 0.6),
    ("server-basics", "caching-strategies", 0.5),
    ("async-js", "websocket", 0.5),
    ("restful-api", "message-queue", 0.5),
    ("restful-api", "microservices-intro", 0.5),
    ("server-basics", "serverless", 0.5),

    # 数据库
    ("variables", "db-basics", 0.3),
    ("db-basics", "sql-basics", 0.9),
    ("sql-basics", "sql-joins", 0.8),
    ("sql-basics", "sql-aggregation", 0.7),
    ("sql-joins", "sql-subquery", 0.7),
    ("db-basics", "db-normalization", 0.7),
    ("db-basics", "db-indexing", 0.6),
    ("db-basics", "db-transactions", 0.7),
    ("sql-basics", "orm-basics", 0.5),
    ("db-basics", "nosql-intro", 0.5),
    ("nosql-intro", "mongodb-basics", 0.7),
    ("nosql-intro", "redis-basics", 0.6),
    ("graph-ds", "graph-database", 0.5),
    ("nosql-intro", "graph-database", 0.5),
    ("db-transactions", "db-replication", 0.6),
    ("db-replication", "db-sharding", 0.7),
    ("sql-basics", "db-migration", 0.5),

    # DevOps
    ("command-line", "git-basics", 0.5),
    ("git-basics", "git-branching", 0.8),
    ("git-branching", "git-workflow", 0.7),
    ("git-workflow", "ci-cd", 0.6),
    ("command-line", "linux-basics", 0.6),
    ("linux-basics", "shell-scripting", 0.7),
    ("linux-basics", "docker-basics", 0.5),
    ("docker-basics", "docker-compose-concept", 0.8),
    ("docker-compose-concept", "kubernetes-intro", 0.6),
    ("server-basics", "cloud-basics", 0.5),
    ("logging-monitoring", "monitoring-alerting", 0.7),
    ("docker-basics", "infra-as-code", 0.5),
    ("http-protocol", "ssl-tls", 0.5),
    ("command-line", "environment-variables", 0.5),

    # 系统设计
    ("restful-api", "system-design-basics", 0.5),
    ("db-basics", "system-design-basics", 0.5),
    ("system-design-basics", "scalability", 0.8),
    ("scalability", "load-balancing", 0.7),
    ("db-transactions", "cap-theorem", 0.6),
    ("cap-theorem", "consistency-patterns", 0.8),
    ("message-queue", "event-driven-arch", 0.6),
    ("microservices-intro", "api-gateway", 0.6),
    ("microservices-intro", "service-discovery", 0.7),
    ("microservices-intro", "circuit-breaker", 0.6),
    ("caching-strategies", "distributed-cache", 0.7),
    ("caching-strategies", "cdn", 0.5),
    ("system-design-basics", "design-url-shortener", 0.7),
    ("system-design-basics", "design-chat-system", 0.7),
    ("websocket", "design-chat-system", 0.5),
    ("system-design-basics", "design-rate-limiter", 0.7),
    ("rate-limiting", "design-rate-limiter", 0.6),
    ("system-design-basics", "twelve-factor-app", 0.5),

    # AI基础
    ("time-complexity", "ai-overview", 0.3),
    ("ai-overview", "ml-basics", 0.8),
    ("ml-basics", "supervised-learning", 0.9),
    ("ml-basics", "unsupervised-learning", 0.8),
    ("supervised-learning", "linear-regression", 0.8),
    ("supervised-learning", "logistic-regression", 0.7),
    ("supervised-learning", "decision-tree", 0.7),
    ("ml-basics", "ml-evaluation", 0.7),
    ("ml-evaluation", "overfitting", 0.7),
    ("ml-basics", "feature-engineering", 0.6),
    ("ml-basics", "loss-functions", 0.7),
    ("loss-functions", "gradient-descent", 0.8),
    ("gradient-descent", "backpropagation", 0.8),
    ("linear-regression", "neural-network-basics", 0.5),
    ("gradient-descent", "neural-network-basics", 0.7),
    ("neural-network-basics", "deep-learning-intro", 0.8),
    ("deep-learning-intro", "cnn-basics", 0.7),
    ("deep-learning-intro", "rnn-basics", 0.7),
    ("functions", "pytorch-basics", 0.4),
    ("neural-network-basics", "pytorch-basics", 0.5),

    # 大模型核心
    ("rnn-basics", "attention-mechanism", 0.7),
    ("attention-mechanism", "transformer-architecture", 0.9),
    ("attention-mechanism", "self-attention", 0.9),
    ("transformer-architecture", "self-attention", 0.6),
    ("transformer-architecture", "positional-encoding", 0.8),
    ("transformer-architecture", "bert-model", 0.7),
    ("transformer-architecture", "gpt-model", 0.8),
    ("gpt-model", "llm-pretraining", 0.8),
    ("transformer-architecture", "tokenization", 0.5),
    ("llm-pretraining", "llm-scaling-laws", 0.7),
    ("llm-pretraining", "llm-inference", 0.6),
    ("llm-inference", "quantization", 0.7),
    ("llm-pretraining", "fine-tuning-overview", 0.7),
    ("fine-tuning-overview", "lora-peft", 0.8),
    ("fine-tuning-overview", "rlhf", 0.7),
    ("rlhf", "dpo", 0.8),
    ("gpt-model", "multimodal-models", 0.5),
    ("cnn-basics", "multimodal-models", 0.5),
    ("llm-pretraining", "llm-evaluation", 0.5),
    ("gpt-model", "open-source-llm", 0.5),
    ("gpt-model", "context-window", 0.6),
    ("transformer-architecture", "mixture-of-experts", 0.6),
    ("llm-scaling-laws", "mixture-of-experts", 0.5),

    # Prompt工程
    ("gpt-model", "prompt-basics", 0.5),
    ("prompt-basics", "zero-shot", 0.8),
    ("prompt-basics", "few-shot", 0.8),
    ("few-shot", "chain-of-thought", 0.7),
    ("chain-of-thought", "self-consistency", 0.7),
    ("chain-of-thought", "tree-of-thought", 0.7),
    ("chain-of-thought", "react-prompting", 0.7),
    ("prompt-basics", "structured-output", 0.6),
    ("prompt-basics", "system-prompt-design", 0.7),
    ("prompt-basics", "prompt-injection", 0.5),
    ("chain-of-thought", "prompt-optimization", 0.6),
    ("prompt-basics", "llm-api-usage", 0.7),
    ("llm-api-usage", "temperature-sampling", 0.6),
    ("llm-api-usage", "token-economics", 0.5),

    # RAG与知识库
    ("gpt-model", "rag-overview", 0.5),
    ("prompt-basics", "rag-overview", 0.5),
    ("rag-overview", "text-embedding", 0.8),
    ("text-embedding", "vector-database", 0.8),
    ("rag-overview", "chunking-strategies", 0.7),
    ("text-embedding", "similarity-search", 0.8),
    ("similarity-search", "hybrid-search", 0.7),
    ("chunking-strategies", "rag-pipeline", 0.7),
    ("similarity-search", "rag-pipeline", 0.7),
    ("rag-pipeline", "rag-evaluation", 0.7),
    ("graph-database-ai", "knowledge-graph-rag", 0.7),
    ("rag-pipeline", "knowledge-graph-rag", 0.6),
    ("multimodal-models", "multimodal-rag", 0.6),
    ("rag-pipeline", "multimodal-rag", 0.6),
    ("rag-overview", "document-parsing", 0.6),
    ("rag-overview", "langchain-basics", 0.5),
    ("rag-overview", "llamaindex-basics", 0.5),
    ("graph-ds", "graph-database-ai", 0.4),
    ("nosql-intro", "graph-database-ai", 0.4),
    ("rag-pipeline", "agentic-rag", 0.7),

    # Agent系统
    ("react-prompting", "agent-overview", 0.6),
    ("llm-api-usage", "agent-overview", 0.5),
    ("agent-overview", "agent-loop", 0.9),
    ("agent-loop", "tool-use", 0.8),
    ("structured-output", "tool-use", 0.6),
    ("tool-use", "mcp-protocol", 0.7),
    ("restful-api", "mcp-protocol", 0.4),
    ("agent-loop", "agent-memory", 0.7),
    ("rag-pipeline", "agent-memory", 0.5),
    ("agent-loop", "agent-planning", 0.8),
    ("tree-of-thought", "agent-planning", 0.5),
    ("agent-loop", "multi-agent", 0.6),
    ("agent-planning", "multi-agent", 0.6),
    ("agent-overview", "agent-evaluation", 0.5),
    ("tool-use", "autogen-framework", 0.5),
    ("multi-agent", "autogen-framework", 0.5),
    ("multi-agent", "crewai-framework", 0.5),
    ("agent-overview", "agent-safety", 0.5),
    ("prompt-injection", "agent-safety", 0.5),
    ("tool-use", "code-generation", 0.6),
    ("tool-use", "browser-agent", 0.6),
    ("multi-agent", "agent-orchestration", 0.7),
    ("agent-overview", "human-in-the-loop", 0.6),
    ("agent-orchestration", "agent-deployment", 0.6),
    ("ci-cd", "agent-deployment", 0.4),
    ("agent-orchestration", "ai-application-arch", 0.7),
    ("system-design-basics", "ai-application-arch", 0.5),
    ("multi-agent", "autonomous-agents", 0.6),
    ("agent-planning", "autonomous-agents", 0.6),
    ("agentic-rag", "autonomous-agents", 0.5),
]

# =============================================
# 里程碑节点 — 高亮显示引导用户冲刺的关键成就节点
# 设计原则: 每个子域 1-2 个里程碑，前沿子域更多
# =============================================

MILESTONE_NODES = {
    # 编程基础里程碑
    "functions",               # 函数 — 编程核心能力
    "recursion",               # 递归 — 算法思维起点
    # 数据结构里程碑
    "hash-table",              # 哈希表 — 最实用的数据结构
    "binary-tree",             # 二叉树 — 树的基石
    # 算法里程碑
    "dynamic-programming",     # 动态规划 — 算法巅峰
    "binary-search",           # 二分查找 — 分治入门
    # OOP里程碑
    "solid-principles",        # SOLID — 设计能力标志
    # Web里程碑
    "react-hooks",             # React Hooks — 现代前端核心
    "restful-api",             # REST API — 后端核心
    # 数据库里程碑
    "db-indexing",             # 索引 — 性能优化关键
    # 系统设计里程碑
    "system-design-basics",    # 系统设计入门
    # AI基础里程碑
    "deep-learning-intro",     # 深度学习入门 — AI分水岭
    "neural-network-basics",   # 神经网络基础
    # LLM核心里程碑
    "transformer-architecture", # Transformer — LLM的基石
    "gpt-model",              # GPT — 理解生成式AI
    "lora-peft",              # LoRA — 微调实战能力
    "rlhf",                   # RLHF — AI对齐关键技术
    # Prompt工程里程碑
    "chain-of-thought",       # 思维链 — 高级Prompt核心
    "react-prompting",        # ReAct — Agent原型
    # RAG里程碑
    "rag-pipeline",           # RAG管道 — 知识库应用核心
    "knowledge-graph-rag",    # KG+RAG — 高级知识检索
    # Agent里程碑
    "tool-use",               # 工具调用 — Agent基础能力
    "mcp-protocol",           # MCP — 最新Agent协议
    "multi-agent",            # 多Agent — 协作系统
    "agent-orchestration",    # Agent编排 — 生产级能力
    "autonomous-agents",      # 自主Agent — 前沿终极目标
}

# =============================================
# 关联关系 (非依赖, 知识互补)
# =============================================

RELATED_EDGES = [
    ("stack", "queue", "contrast", 0.8),
    ("bfs", "dfs", "contrast", 0.9),
    ("merge-sort", "quick-sort", "contrast", 0.8),
    ("sql-basics", "mongodb-basics", "contrast", 0.6),
    ("restful-api", "graphql-basics", "contrast", 0.7),
    ("supervised-learning", "unsupervised-learning", "contrast", 0.8),
    ("cnn-basics", "rnn-basics", "contrast", 0.7),
    ("bert-model", "gpt-model", "contrast", 0.8),
    ("rlhf", "dpo", "contrast", 0.8),
    ("langchain-basics", "llamaindex-basics", "contrast", 0.7),
    ("autogen-framework", "crewai-framework", "contrast", 0.7),
    ("iteration-vs-recursion", "dynamic-programming", "application", 0.6),
    ("hash-table", "bloom-filter", "application", 0.5),
    ("binary-search", "bst", "analogy", 0.7),
    ("react-state", "observer-pattern", "analogy", 0.5),
    ("typescript-basics", "generics", "application", 0.6),
    ("docker-basics", "microservices-intro", "application", 0.6),
    ("redis-basics", "distributed-cache", "application", 0.7),
    ("vector-database", "similarity-search", "application", 0.8),
    ("knowledge-graph-rag", "graph-database-ai", "application", 0.8),
    ("rag-pipeline", "agent-memory", "application", 0.7),
    ("tool-use", "mcp-protocol", "application", 0.8),
    ("react-prompting", "agent-loop", "analogy", 0.8),
    ("chain-of-thought", "agent-planning", "application", 0.7),
    ("multi-agent", "agent-orchestration", "application", 0.8),
    ("code-generation", "browser-agent", "contrast", 0.6),
    ("lora-peft", "rlhf", "contrast", 0.6),
    ("quantization", "llm-inference", "application", 0.7),
    ("web-performance", "caching-strategies", "application", 0.6),
    ("async-js", "websocket", "application", 0.5),
]


def build_concepts():
    """构建概念节点列表"""
    concepts = []
    now = datetime.now(timezone.utc).isoformat()
    for raw in CONCEPTS_RAW:
        cid, name, subdomain, diff, est_min, ctype, tags = raw
        concepts.append({
            "id": cid,
            "name": name,
            "description": f"掌握{name}的核心概念和应用",
            "domain_id": "ai-engineering",
            "subdomain_id": subdomain,
            "difficulty": diff,
            "estimated_minutes": est_min,
            "content_type": ctype,
            "tags": tags,
            "is_milestone": cid in MILESTONE_NODES,
            "created_at": now,
        })
    return concepts


def build_edges():
    """构建边列表"""
    prereq_edges = []
    for src, tgt, strength in PREREQUISITES:
        prereq_edges.append({
            "source_id": src,
            "target_id": tgt,
            "relation_type": "prerequisite",
            "strength": strength,
        })

    related_edges = []
    for item in RELATED_EDGES:
        src, tgt, sub_type, strength = item
        related_edges.append({
            "source_id": src,
            "target_id": tgt,
            "relation_type": "related_to",
            "sub_type": sub_type,
            "strength": strength,
        })

    return prereq_edges + related_edges


def validate(concepts, edges):
    """数据校验"""
    concept_ids = {c["id"] for c in concepts}
    errors = []

    # 检查边引用的节点是否都存在
    for e in edges:
        if e["source_id"] not in concept_ids:
            errors.append(f"边引用不存在的source: {e['source_id']}")
        if e["target_id"] not in concept_ids:
            errors.append(f"边引用不存在的target: {e['target_id']}")

    # 检查自环
    for e in edges:
        if e["source_id"] == e["target_id"]:
            errors.append(f"自环: {e['source_id']}")

    # 检查先修依赖无环 (拓扑排序)
    prereqs = [e for e in edges if e["relation_type"] == "prerequisite"]
    in_degree = {c: 0 for c in concept_ids}
    adj = {c: [] for c in concept_ids}
    for e in prereqs:
        adj[e["source_id"]].append(e["target_id"])
        in_degree[e["target_id"]] += 1

    queue = [c for c in concept_ids if in_degree[c] == 0]
    visited = 0
    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited != len(concept_ids):
        errors.append(f"先修依赖存在环! 可达 {visited}/{len(concept_ids)} 节点")

    # 子域覆盖统计
    subdomain_counts = {}
    for c in concepts:
        sd = c["subdomain_id"]
        subdomain_counts[sd] = subdomain_counts.get(sd, 0) + 1

    # 难度分布
    diff_dist = {}
    for c in concepts:
        d = c["difficulty"]
        diff_dist[d] = diff_dist.get(d, 0) + 1

    return errors, subdomain_counts, diff_dist


def generate_cypher(concepts, edges, subdomains):
    """生成 Neo4j Cypher 导入脚本"""
    lines = [
        "// ========================================",
        "// AI Knowledge Graph — Seed Data Import",
        f"// Generated: {datetime.now().isoformat()}",
        f"// Concepts: {len(concepts)}, Edges: {len(edges)}",
        "// ========================================\n",
        "// 清空旧数据 (慎用)",
        "// MATCH (n) DETACH DELETE n;\n",
        "// 创建领域节点",
        f"CREATE (:Domain {{id: 'ai-engineering', name: 'AI工程', description: '从编程基础到大模型与Agent系统的前沿知识体系', icon: '🧠', color: '#8b5cf6'}});\n",
        "// 创建子域节点",
    ]
    for sd in subdomains:
        lines.append(
            f"CREATE (:Subdomain {{id: '{sd['id']}', name: '{sd['name']}', domain_id: 'programming', order: {sd['order']}}});"
        )
    lines.append("")

    # 批量创建概念节点 — 使用 UNWIND
    lines.append("// 批量创建概念节点")
    lines.append("UNWIND [")
    for i, c in enumerate(concepts):
        tags_str = str(c["tags"]).replace("'", '"')
        comma = "," if i < len(concepts) - 1 else ""
        lines.append(
            f"  {{id: '{c['id']}', name: '{c['name']}', domain_id: '{c['domain_id']}', "
            f"subdomain_id: '{c['subdomain_id']}', difficulty: {c['difficulty']}, "
            f"estimated_minutes: {c['estimated_minutes']}, content_type: '{c['content_type']}', "
            f"tags: {tags_str}}}{comma}"
        )
    lines.append("] AS c")
    lines.append("CREATE (:Concept {id: c.id, name: c.name, domain_id: c.domain_id, subdomain_id: c.subdomain_id, difficulty: c.difficulty, estimated_minutes: c.estimated_minutes, content_type: c.content_type, tags: c.tags});")
    lines.append("")

    # 先修依赖
    prereqs = [e for e in edges if e["relation_type"] == "prerequisite"]
    lines.append(f"// 先修依赖 ({len(prereqs)} edges)")
    lines.append("UNWIND [")
    for i, e in enumerate(prereqs):
        comma = "," if i < len(prereqs) - 1 else ""
        lines.append(f"  {{src: '{e['source_id']}', tgt: '{e['target_id']}', str: {e['strength']}}}{comma}")
    lines.append("] AS e")
    lines.append("MATCH (a:Concept {id: e.src}), (b:Concept {id: e.tgt})")
    lines.append("CREATE (a)-[:PREREQUISITE {strength: e.str}]->(b);")
    lines.append("")

    # 关联关系
    related = [e for e in edges if e["relation_type"] == "related_to"]
    if related:
        lines.append(f"// 关联关系 ({len(related)} edges)")
        lines.append("UNWIND [")
        for i, e in enumerate(related):
            comma = "," if i < len(related) - 1 else ""
            lines.append(f"  {{src: '{e['source_id']}', tgt: '{e['target_id']}', type: '{e.get('sub_type', 'related')}', str: {e['strength']}}}{comma}")
        lines.append("] AS e")
        lines.append("MATCH (a:Concept {id: e.src}), (b:Concept {id: e.tgt})")
        lines.append("CREATE (a)-[:RELATED_TO {type: e.type, strength: e.str}]->(b);")

    # 领域包含关系
    lines.append("\n// 领域→概念 包含关系")
    lines.append("MATCH (d:Domain {id: 'ai-engineering'}), (c:Concept {domain_id: 'ai-engineering'})")
    lines.append("CREATE (d)-[:CONTAINS]->(c);")

    # 子域→概念 包含关系
    lines.append("\n// 子域→概念 包含关系")
    lines.append("MATCH (s:Subdomain), (c:Concept)")
    lines.append("WHERE s.id = c.subdomain_id")
    lines.append("CREATE (s)-[:CONTAINS]->(c);")

    # 索引
    lines.append("\n// 创建索引")
    lines.append("CREATE INDEX concept_id IF NOT EXISTS FOR (c:Concept) ON (c.id);")
    lines.append("CREATE INDEX concept_domain IF NOT EXISTS FOR (c:Concept) ON (c.domain_id);")
    lines.append("CREATE INDEX concept_subdomain IF NOT EXISTS FOR (c:Concept) ON (c.subdomain_id);")
    lines.append("CREATE INDEX domain_id IF NOT EXISTS FOR (d:Domain) ON (d.id);")
    lines.append("CREATE INDEX subdomain_id IF NOT EXISTS FOR (s:Subdomain) ON (s.id);")

    return "\n".join(lines)


def main():
    # 构建数据
    concepts = build_concepts()
    edges = build_edges()

    # 校验
    errors, subdomain_counts, diff_dist = validate(concepts, edges)

    print(f"📊 种子图谱统计:")
    print(f"   概念节点: {len(concepts)}")
    print(f"   先修依赖: {len([e for e in edges if e['relation_type'] == 'prerequisite'])}")
    print(f"   关联关系: {len([e for e in edges if e['relation_type'] == 'related_to'])}")
    print(f"   总边数:   {len(edges)}")
    print()

    print(f"📂 子域分布:")
    for sd in SUBDOMAINS:
        count = subdomain_counts.get(sd["id"], 0)
        bar = "█" * count
        print(f"   {sd['name']:12} ({count:2}): {bar}")
    print()

    print(f"📈 难度分布:")
    for d in sorted(diff_dist.keys()):
        bar = "█" * diff_dist[d]
        print(f"   难度 {d:2}: ({diff_dist[d]:2}) {bar}")
    print()

    if errors:
        print(f"❌ 发现 {len(errors)} 个错误:")
        for e in errors:
            print(f"   - {e}")
        return
    else:
        print(f"✅ 数据校验通过: 无错误, DAG无环, 所有引用合法")
    print()

    # 输出目录
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seed", "programming")
    os.makedirs(out_dir, exist_ok=True)

    # 写入 JSON
    graph_data = {
        "domain": DOMAIN,
        "subdomains": SUBDOMAINS,
        "concepts": concepts,
        "edges": edges,
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_concepts": len(concepts),
            "total_edges": len(edges),
            "subdomain_counts": subdomain_counts,
            "difficulty_distribution": diff_dist,
        },
    }

    json_path = os.path.join(out_dir, "seed_graph.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON: {json_path} ({os.path.getsize(json_path) / 1024:.1f} KB)")

    # 写入 Cypher
    cypher = generate_cypher(concepts, edges, SUBDOMAINS)
    cypher_path = os.path.join(out_dir, "import_seed.cypher")
    with open(cypher_path, "w", encoding="utf-8") as f:
        f.write(cypher)
    print(f"💾 Cypher: {cypher_path} ({os.path.getsize(cypher_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
